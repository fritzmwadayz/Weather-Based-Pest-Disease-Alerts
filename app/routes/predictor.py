from flask import Blueprint, request, jsonify
import pickle
import numpy as np
from app import redis_client
from app.models import Farm, Crop
from datetime import datetime
from app.services.weather_service import WeatherService

predictor_bp = Blueprint('predictor', __name__)

# Load models
MODELS = {
    "maize": pickle.load(open('app/ml_models/maize_model.pkl', 'rb')),
    "wheat": pickle.load(open('app/ml_models/wheat_pest_model.pkl', 'rb')),
    "rice": pickle.load(open('app/ml_models/rice_pest_model.pkl', 'rb'))
}

PEST_LABELS = {
    "maize": ["Armyworms", "Stalk_Borers", "Aphids"],
    "wheat": ["Rust", "Aphids", "Fusarium_Head_Blight"],
    "rice": ["Blast", "Brown_Spot", "Stem_Borers"]
}

def get_model_for_farm(farm_id):
    """Get the appropriate model for a farm's primary crop"""
    # Try Redis cache first
    cached_model = redis_client.get(f"model:{farm_id}")
    if cached_model:
        return cached_model.decode()
    
    # Get from database
    farm = Farm.query.get(farm_id)
    if not farm or not farm.crops:
        return None
    
    primary_crop = farm.crops[0].name.lower() if farm.crops else None
    return primary_crop if primary_crop in MODELS else None

@predictor_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        farm_id = data.get('farm_id')
        
        if not farm_id:
            return jsonify({'error': 'Farm ID is required'}), 400

        # Get farm data
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({'error': 'Farm not found'}), 404

        # Get weather for farm's location
        weather_data = WeatherService.get_current_weather(farm.location)

        # Get model based on farm's crops
        crop_type = get_model_for_farm(farm_id)
        if not crop_type:
            return jsonify({'error': 'No model available for this farm'}), 400

        # Validate weather data
        required_fields = ['temperature', 'humidity', 'rainfall', 'wind_speed']
        if not all(field in weather_data for field in required_fields):
            return jsonify({'error': 'Incomplete weather data'}), 400

        # Prepare features
        features = np.array([[
            float(weather_data['temperature']),
            float(weather_data['humidity']),
            float(weather_data['rainfall']),
            float(weather_data['wind_speed'])
        ]])

        # Make prediction
        prediction = MODELS[crop_type].predict(features)[0]
        probabilities = MODELS[crop_type].predict_proba(features)[0] if hasattr(MODELS[crop_type], 'predict_proba') else None

        # Format results
        result = {
            "pests": {
                pest: {
                    "present": bool(prediction[i]),
                    "probability": float(probabilities[i][1]) if probabilities is not None else None
                } for i, pest in enumerate(PEST_LABELS[crop_type])
            },
            "model_used": crop_type,
            "timestamp": datetime.utcnow().isoformat()
        }

        return jsonify({
            "status": "success",
            "prediction": result
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@predictor_bp.route('/models', methods=['GET'])
def list_models():
    """List available crop models"""
    return jsonify({
        "status": "success",
        "models": list(MODELS.keys()),
        "pest_labels": PEST_LABELS
    })