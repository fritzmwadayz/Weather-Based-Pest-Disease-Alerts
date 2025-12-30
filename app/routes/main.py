from flask import Blueprint, render_template, current_app, make_response
from flask import jsonify, request
from app.tasks import select_model_task
import time
from datetime import datetime
from app import celery
from app import db
from app.models import Farm, User, Crop, Alert
from celery.result import AsyncResult
from app import redis_client
from app import socketio
from app.services.weather_service import WeatherService
from app import validate_user_access
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity
)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return jsonify({"message": "Welcome to the API!"})  # Return JSON instead of rendering a template

@main_bp.route("/get_selected_model/<farm_id>")
def get_selected_model(farm_id):
    """
    Fetch the selected model from Redis with detailed status information.
    """
    try:
        # Check if farm exists
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({
                "status": "error",
                "message": "Farm not found",
                "action_required": "create_farm_settings"
            }), 404

        selected_model = redis_client.get(f"selected_model:{farm_id}")

        if not selected_model:
            # If no model selected but farm exists with crops, trigger selection
            if farm.crops:
                select_model_task.delay(farm_id)
                return jsonify({
                    "status": "pending",
                    "message": "Model selection in progress",
                    "action_taken": "triggered_model_selection"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "No crops configured for model selection",
                    "action_required": "update_farm_settings"
                })

        return jsonify({
            "status": "success",
            "selected_model": selected_model,
            "last_updated": redis_client.ttl(f"selected_model:{farm_id}"),  # Time remaining
            "farm_id": farm_id
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get selected model: {str(e)}"
        }), 500

@main_bp.route('/farm-settings', methods=['GET', 'POST','PUT'])
@jwt_required()
def handle_farm_settings():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required"}), 400

    try:
        farm = Farm.query.filter_by(user_id=user_id).first()
        if not farm:
            farm = Farm(user_id=user_id)
            db.session.add(farm)

        # Track if crops changed (which affects model selection)
        crops_changed = False
        if 'crops' in data:
            current_crops = {c.name for c in farm.crops}
            new_crops = set(data['crops'])
            crops_changed = current_crops != new_crops
            
            farm.crops = []
            for crop_name in data['crops']:
                crop = Crop.query.filter_by(name=crop_name).first()
                if not crop:
                    crop = Crop(name=crop_name)
                    db.session.add(crop)
                farm.crops.append(crop)

        # Update other fields
        if 'location' in data:
            farm.location = data['location']
        if 'temperature' in data:
            farm.temperature = data['temperature']
        
        db.session.commit()

        # Trigger model selection if crops changed or farm is new
        if crops_changed or not redis_client.exists(f"selected_model:{farm.id}"):
            select_model_task.delay(farm.id)

        # Update farm properties
        if 'location' in data:
            farm.location = data['location']
        if 'temperature' in data:
            farm.temperature = data['temperature']
            
        # Update crops
        if 'crops' in data:
            farm.crops = []
            for crop_name in data['crops']:
                crop = Crop.query.filter_by(name=crop_name).first()
                if not crop:
                    crop = Crop(name=crop_name)
                    db.session.add(crop)
                farm.crops.append(crop)
            
            farm.updated_at = datetime.utcnow()
            db.session.commit()

            socketio.emit('settings_updated', {
                'user_id': user_id,
                'farm_settings': {
                    'location': farm.location,
                    'crops': [crop.name for crop in farm.crops],
                    'temperature': farm.temperature,
                    'updated_at': farm.updated_at.isoformat()
                }
            })

            return jsonify({
                "status": "success",
                "message": "Farm settings updated successfully",
                "data": {
                    "location": farm.location,
                    "crops": [crop.name for crop in farm.crops],
                    "temperature": farm.temperature,
                    "updated_at": farm.updated_at.isoformat()
                }
            })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Failed to update farm settings: {str(e)}"
        }), 500

    else:  # GET request
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"status": "error", "message": "User ID is required"}), 400

        farm = Farm.query.filter_by(user_id=user_id).first()
        if not farm:
            return jsonify({"status": "error", "message": "Farm not found"}), 404

        return jsonify({
            "status": "success",
            "data": {
                "location": farm.location,
                "crops": [crop.name for crop in farm.crops],
                "temperature": farm.temperature,
                "updated_at": farm.updated_at.isoformat() if farm.updated_at else None
            }
        })

@main_bp.route("/model_selection_status/<farm_id>")
def model_selection_status(farm_id):
    """
    Check if model selection is complete and valid.
    """
    model_exists = redis_client.exists(f"selected_model:{farm_id}")
    ttl = redis_client.ttl(f"selected_model:{farm_id}") if model_exists else -1
    
    return jsonify({
        "model_exists": bool(model_exists),
        "ttl_seconds": ttl,
        "is_expired": ttl < 0 if model_exists else None,
        "farm_id": farm_id
    })

@main_bp.route("/refresh_model/<farm_id>", methods=["POST"])
def refresh_model(farm_id):
    """
    Force refresh of the selected model.
    """
    farm = Farm.query.get(farm_id)
    if not farm:
        return jsonify({
            "status": "error",
            "message": "Farm not found"
        }), 404
    
    select_model_task.delay(farm_id)
    return jsonify({
        "status": "success",
        "message": "Model refresh initiated",
        "farm_id": farm_id
    })

@main_bp.route('/weather-data')
def get_weather_endpoint():
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location parameter required"}), 400
    
    try:
        weather = WeatherService.get_current_weather(location)
        return jsonify({
            "status": "success",
            "data": {
                "current": weather,
                "forecast": WeatherService.generate_forecast(location)['forecast']
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get weather data: {str(e)}"
        }), 500

@main_bp.route('/general-settings', methods=['GET', 'POST'])
def handle_general_settings():
    if request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"status": "error", "message": "User ID is required"}), 400

        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404

            # Initialize settings if not exists
            if not user.settings:
                user.settings = {}

            # Update with new settings
            user.settings.update(data.get('settings', {}))
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "General settings updated successfully",
                "data": user.settings
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": f"Failed to update general settings: {str(e)}"
            }), 500

    else:  # GET request
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"status": "error", "message": "User ID is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        return jsonify({
            "status": "success",
            "data": user.settings if user.settings else {}
        })

@main_bp.route('/get-settings/<int:user_id>', methods=['GET'])
@jwt_required()
def get_settings(user_id):
    try:
        # Verify the requesting user matches the user_id
        current_user_id = get_jwt_identity()
        if int(current_user_id) != user_id:
            return jsonify({
                "status": "error",
                "message": "Unauthorized access"
            }), 403

        # Get farm data with error handling
        farm = Farm.query.filter_by(user_id=user_id).first()
        if not farm:
            return jsonify({
                "status": "success",
                "message": "No farm data found",
                "data": None
            }), 200

        # Prepare response data
        response_data = {
            "location": farm.location,
            "crops": [crop.name for crop in farm.crops],
            "updated_at": farm.updated_at.isoformat() if farm.updated_at else None
        }

        # Add weather data if location exists
        if farm.location:
            try:
                response_data['weather'] = get_weather_data(farm.location)
            except Exception as e:
                current_app.logger.error(f"Weather data error: {str(e)}")

        return jsonify({
            "status": "success",
            "data": response_data
        })

    except Exception as e:
        current_app.logger.error(f"Settings error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)  # More detailed error message
        }), 500

@main_bp.route('/recommended-articles')
def get_articles():
    pest_name = request.args.get('pest')
    articles = BlogPost.query.filter(BlogPost.tags.contains([pest_name]))\
                           .order_by(BlogPost.created_at.desc())\
                           .limit(3).all()
    return jsonify([a.to_dict() for a in articles])

@main_bp.route('/farm-settings/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_farm_settings(user_id):
    """Handle only path parameter version"""
    try:
        return jsonify({
            "location": "Test Location",
            "crops": ["Corn", "Wheat"],
            "user_id": user_id  # Now guaranteed to be an integer
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/recommendations/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_recommendations(user_id):
    return jsonify({
        "posts": [
            {
                "title": "Summer Crop Tips",
                "url": "/blog/summer-tips"
            }
        ]
    })

@main_bp.route('/alerts/<int:farm_id>', methods=['GET', 'OPTIONS'])
def get_alerts(farm_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({
                "status": "error",
                "message": "Farm not found"
            }), 404
            
        active_alerts = Alert.query.filter_by(farm_id=farm_id, is_active=True).all()
        
        pests = [alert.serialize() for alert in active_alerts if alert.type == 'pest']
        diseases = [alert.serialize() for alert in active_alerts if alert.type == 'disease']
        
        return jsonify({
            "status": "success",
            "pests": pests or [],
            "diseases": diseases or [],
            "last_updated": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@main_bp.route('/weather-data', methods=['GET'])
def get_weather():
    location = request.args.get('location')
    if not location:
        return jsonify({"status": "error", "message": "Location required"}), 400
    
    weather = WeatherData.get_for_location(location)
    if not weather:
        return jsonify({"status": "error", "message": "Weather data not found"}), 404
    
    return jsonify({
        "status": "success",
        "data": weather.serialize()
    })

@main_bp.route('/debug-request')
def debug_request():
    import inspect
    from flask import request
    
    # Get all frames in the call stack
    frames = inspect.stack()
    flask_internals = []
    
    for frame in frames:
        if 'flask/' in frame.filename.lower():
            flask_internals.append({
                'file': frame.filename,
                'line': frame.lineno,
                'function': frame.function
            })
    
    return jsonify({
        'request_processing': {
            'content_type': request.content_type,
            'is_json': request.is_json,
            'headers': dict(request.headers)
        },
        'flask_stack': flask_internals
    })

@main_bp.route('/api/farms/<int:user_id>', methods=['GET', 'OPTIONS'])
def get_farm_data(user_id):
    """Clean, focused endpoint for farm data"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        farm = Farm.query.filter_by(user_id=user_id).first()
        if not farm:
            return jsonify({
                "status": "error",
                "message": "Farm not found"
            }), 404

        # Get current weather if location exists
        weather = None
        if farm.location:
            weather = WeatherService.get_current_weather(farm.location)

        return jsonify({
            "status": "success",
            "data": {
                "location": farm.location,
                "crops": [crop.name for crop in farm.crops],
                "weather": weather,
                "last_updated": farm.updated_at.isoformat() if farm.updated_at else None
            }
        })

    except Exception as e:
        current_app.logger.error(f"Farm data error for user {user_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch farm data"
        }), 500

@main_bp.route('/api/farms/<int:user_id>', methods=['OPTIONS'])
def options_farms(user_id):
    response = jsonify({'status': 'preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
    response.headers.add('Access-Control-Max-Age', '600')
    return response

@main_bp.before_request
def before_request():
    current_app.logger.info(f"Incoming request: {request.method} {request.path}")
    current_app.logger.info(f"Headers: {dict(request.headers)}")
    current_app.logger.info(f"Token: {request.headers.get('Authorization')}")

def _build_cors_preflight_response():
    response = jsonify({"status": "preflight"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response