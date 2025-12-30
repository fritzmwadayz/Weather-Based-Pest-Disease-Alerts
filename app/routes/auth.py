from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.models import db, User
import jwt, smtplib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from functools import wraps
from app.services.email_service import send_reset_email
from app.extensions import mail
from flask_mail import Message
from app.utils.validation import validate_password
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app import validate_user_access
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt
)
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

# Helper function to generate JWT tokens
def generate_token(user_id, role):
    return jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=48)
    }, SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = {
                "id": data['user_id'],
                "role": data['role']
            }
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("15 per hour")
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate required fields
    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Add password validation
    is_valid, message = validate_password(data.get('password', ''))
    if not is_valid:
        return jsonify({'success': False, 'message': message}), 400

    # Check if username or email already exists
    existing_user_by_username = User.query.filter_by(username=username).first()
    existing_user_by_email = User.query.filter_by(email=email).first()

    if existing_user_by_username:
        return jsonify({'success': False, 'message': 'Username already registered.'}), 400
    if existing_user_by_email:
        return jsonify({'success': False, 'message': 'Email already registered.'}), 400

    try:
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='farmer'  # Default role
        )
        db.session.add(new_user)
        db.session.commit()

        # Return success response
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error creating user',
            'error': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email').lower().strip()
    password = data.get('password')

    user = User.query.filter(func.lower(User.email) == email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT token with string subject
    access_token = create_access_token(
        identity=str(user.id),  # Convert to string
        additional_claims={
            'email': user.email,
            'role': user.role
        }
    )
    
    return jsonify({
        'token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'role': user.role
        }
    })

@auth_bp.route('/auth/validate', methods=['GET'])
@jwt_required()
def validate_token():
    current_user = get_jwt_identity()
    return jsonify({"valid": True, "user": current_user}), 200

@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200

@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        # Get the user ID from the token identity
        user_id = get_jwt_identity()
        
        # Get additional claims if needed
        claims = get_jwt()
        
        # Fetch user from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({
            "id": user.id,
            "email": user.email,
            "role": user.role
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("5 per hour")
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # Security: Don't reveal whether email exists
        return jsonify({"success": True, "message": "If this email exists, a reset link has been sent"})

    try:
        reset_token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=30),
            'purpose': 'password_reset',}, 
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    

        user.reset_token = reset_token
        db.session.commit()

        if send_reset_email(user.email, reset_token):
            return jsonify({"success": True, "message": "Reset email sent"})
        return jsonify({"success": False, "message": "Failed to send email"}), 500
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({"success": False, "message": "Server error"}), 500

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    data = request.get_json()
    
    # Input validation
    if not data or 'token' not in data or 'new_password' not in data:
        return jsonify({
            'success': False,
            'message': 'Token and new password are required'
        }), 400

    is_valid, message = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'success': False, 'message': message}), 400

    token = data['token']
    new_password = data['new_password']

    try:
        # Verify and decode token
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        # Find user
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Password reset successful'
        })

    except jwt.ExpiredSignatureError:
        return jsonify({
            'success': False,
            'message': 'Token expired'
        }), 400
        
    except jwt.InvalidTokenError:
        return jsonify({
            'success': False,
            'message': 'Invalid token'
        }), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('auth.login'))
