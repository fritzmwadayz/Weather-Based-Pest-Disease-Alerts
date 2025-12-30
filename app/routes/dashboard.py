from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import User, Alert, Farm
from app import db

dashboard_bp = Blueprint('dashboard', __name__)

# Admin Dashboard View
@dashboard_bp.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    return render_template('dashboard/admin.html')

# Admin Dashboard Data
@dashboard_bp.route('/admin/data')
@login_required
def admin_data():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    total_users = User.query.count()
    total_predictions = Alert.query.count()
    active_farms = Farm.query.filter(Farm.is_active == True).count()

    # Get predictions over time
    predictions = db.session.query(
        db.func.date(Alert.created_at),
        db.func.count(Alert.id)
    ).group_by(db.func.date(Alert.created_at)).all()

    prediction_dates = [p[0].strftime('%Y-%m-%d') for p in predictions]
    prediction_counts = [p[1] for p in predictions]

    return jsonify({
        "total_users": total_users,
        "total_predictions": total_predictions,
        "active_farms": active_farms,
        "prediction_dates": prediction_dates,
        "prediction_counts": prediction_counts
    })

# Farmer Dashboard View
@dashboard_bp.route('/farmer')
@login_required
def farmer():
    if current_user.role != 'farmer':
        return "Unauthorized", 403
    return render_template('dashboard/farmer.html')

# Farmer Dashboard Data
@dashboard_bp.route('/farmer/data')
@login_required
def farmer_data():
    if current_user.role != 'farmer':
        return jsonify({"error": "Unauthorized"}), 403

    your_predictions = Alert.query.filter_by(user_id=current_user.id).count()

    # Get high-risk pests for this farmer
    high_risk_pests = (
        db.session.query(Alert.pest_name)
        .filter(Alert.user_id == current_user.id, Alert.risk_level == "high")
        .distinct()
        .all()
    )
    high_risk_pests = [p[0] for p in high_risk_pests]

    # Pest type distribution
    pest_data = (
        db.session.query(Alert.pest_name, db.func.count(Alert.id))
        .filter(Alert.user_id == current_user.id)
        .group_by(Alert.pest_name)
        .all()
    )
    pest_types = [p[0] for p in pest_data]
    pest_counts = [p[1] for p in pest_data]

    return jsonify({
        "your_predictions": your_predictions,
        "high_risk_pests": high_risk_pests,
        "pest_types": pest_types,
        "pest_counts": pest_counts
    })
