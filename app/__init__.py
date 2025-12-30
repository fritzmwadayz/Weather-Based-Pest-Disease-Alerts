from flask import Flask, request, make_response
from .extensions import db, migrate, socketio, login_manager, cors, mail
from celery import Celery
from celeryconf import celery
from config import CeleryConfig
import redis, os
from dotenv import load_dotenv
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    verify_jwt_in_request
)

load_dotenv()

def validate_user_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        # Check for user_id in URL or body
        requested_id = kwargs.get('user_id') or request.json.get('user_id')
        
        if requested_id and current_user['id'] != requested_id:
            return jsonify({"error": "Unauthorized access"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

protected_endpoints = {
    '/farm-settings',
    '/login',
    '/forgot-password',
    '/reset-password',
    '/auth/me',
    '/auth/valdate',
    '/auth/refresh'
}

def create_app():
    app = Flask(__name__)
    @app.before_request
    def prevent_json_validation_for_gets():
        if request.method == 'GET':
            request._cached_json = {}  # Trick Flask into thinking JSON was parsed
            request._parsed_content_type = ['application/json']  # Fake content type
    
    # Basic configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SQLITE_SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    cors.init_app(
        app,
        resources={
            r"/farm-settings*": {
                "origins": "http://localhost:5173",
                "methods": ["GET", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            },
            r"/*": {
                "origins": "http://localhost:5173",
                "supports_credentials": True
            },
            r"/api/*": {
                "origins": "http://localhost:5173",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type"],
                "expose_headers": ["Authorization"],
                "supports_credentials": True,
                "max_age": 600  # Cache OPTIONS responses for 10 minutes
            },
            r"/auth/*": {
                "origins": "http://localhost:5173",
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type"],
                "supports_credentials": True
            },
            r"/get-settings/*": {
                "origins": "http://localhost:5173",
                "methods": ["GET", "OPTIONS"],
                "allow_headers": ["Authorization"]
            }
        },
        supports_credentials=True,  # If you need cookies/auth headers
        allow_headers=["Content-Type", "Authorization"],  # Optional
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # Optional
    )
    
    # CORS handlers
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            return response

    @app.before_request
    def verify_jwt():
        if request.endpoint in protected_endpoints:
            try:
                jwt_data = get_jwt_identity()
                # Ensure token contains email that matches request path
                if '/farm-settings/' in request.path:
                    user_id = int(request.path.split('/')[-1])
                    if jwt_data['id'] != user_id:
                        return jsonify({"error": "Unauthorized access"}), 403
            except Exception as e:
                return jsonify({"error": "Invalid token"}), 401

    #'''
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    #'''

    #JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    jwt = JWTManager(app)
    
    # Celery configuration
    app.config.from_object(CeleryConfig)
    celery.conf.update(
        result_backend=CeleryConfig.result_backend,
        broker_url=CeleryConfig.broker_url,
    )

    # Redis configuration
    global redis_client
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    try:
        redis_client.ping()
        app.logger.info("Redis connection established successfully")
    except redis.ConnectionError:
        app.logger.error("Failed to connect to Redis")
        raise

    # User loader
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    #Add mailing
    app.config.update({
        'MAIL_SERVER': 'smtp.yandex.com',
        'MAIL_PORT': 465,
        'MAIL_USE_TLS': False,  # Must be True for STARTTLS
        'MAIL_USE_SSL': True,  # Must be False for port 587
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
    })
    
    mail.init_app(app)

    from .services import email_service

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.predictor import predictor_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(predictor_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # Initialize SocketIO (but don't return it)
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins=["http://localhost:5173"])
    
    
    return app