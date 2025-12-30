from celeryconf import celery
from app.models import  db, Farm, Crop
from datetime import timedelta
import logging
import time
from app import redis_client

@celery.task(bind=True)
def update_weather_data(self, location):
    """Example background task"""
    weather = WeatherData.query.filter_by(location=location).first()
    # Your update logic here
    db.session.commit()
    return f"Weather updated for {location}"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task(bind=True)
def example_task(self, duration):
    logger.info(f"Task {self.request.id} started")
    for i in range(duration):
        time.sleep(1)
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": duration})
        logger.info(f"Task {self.request.id} progress: {i + 1}/{duration}")
    logger.info(f"Task {self.request.id} completed")
    return {"status": "Task completed!"}

'''
@celery.task(bind=True)
def select_model_task(self, farm_id):
    """
    Celery task to select the best model based on the farm's crops.
    """
    try:
        farm = Farm.query.get(farm_id)
        if not farm:
            logger.error(f"Farm {farm_id} not found")
            return {"status": "error", "message": "Farm not found"}

        if not farm.crops:
            logger.error(f"No crops configured for farm {farm_id}")
            # Set default model when no crops specified
            redis_client.set(f"selected_model:{farm_id}", "default_model")
            return {
                "status": "success",
                "selected_model": "default_model",
                "message": "Used default model (no crops specified)"
            }

        # Select model based on primary crop (or implement more complex logic)
        primary_crop = farm.crops[0].name
        selected_model = select_best_model(primary_crop)

        # Store with expiration (1 week) to ensure periodic refresh
        redis_client.setex(
            f"selected_model:{farm_id}",
            timedelta(weeks=1),
            selected_model
        )

        logger.info(f"Selected model {selected_model} for farm {farm_id}")
        return {
            "status": "success",
            "selected_model": selected_model,
            "crop_used": primary_crop
        }
    except Exception as e:
        logger.error(f"Model selection failed for farm {farm_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Model selection failed: {str(e)}"
        }
'''

@celery.task(bind=True)
def select_model_task(self, farm_id):
    """
    Celery task to select the best model based on the farm's crops.
    """
    try:
        logger.debug(f"Starting model selection for farm {farm_id}")
        
        # Verify Redis connection
        try:
            redis_client.ping()
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            return {
                "status": "error",
                "message": "Redis connection failed",
                "detail": str(e)
            }

        # Verify database connection
        try:
            farm = Farm.query.get(farm_id)
            if not farm:
                logger.error(f"Farm {farm_id} not found in database")
                return {
                    "status": "error",
                    "message": f"Farm {farm_id} not found"
                }
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            return {
                "status": "error",
                "message": "Database operation failed",
                "detail": str(e)
            }

        # Rest of your existing task logic...
        if not farm.crops:
            logger.warning(f"No crops configured for farm {farm_id}")
            try:
                redis_client.setex(
                    f"selected_model:{farm_id}",
                    timedelta(weeks=1),
                    "default_model"
                )
                logger.info(f"Set default model for farm {farm_id}")
                return {
                    "status": "success",
                    "selected_model": "default_model"
                }
            except Exception as e:
                logger.error(f"Failed to set default model: {str(e)}")
                return {
                    "status": "error",
                    "message": "Failed to set default model",
                    "detail": str(e)
                }

        primary_crop = farm.crops[0].name
        selected_model = select_best_model(primary_crop)
        
        try:
            redis_client.setex(
                f"selected_model:{farm_id}",
                timedelta(weeks=1).total_seconds(),
                selected_model
            )
            logger.info(f"Successfully stored model {selected_model} for farm {farm_id}")
            return {
                "status": "success",
                "selected_model": selected_model
            }
        except Exception as e:
            logger.error(f"Failed to store model in Redis: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to store model",
                "detail": str(e)
            }

    except Exception as e:
        logger.error(f"Unexpected error in model selection: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Unexpected error in model selection",
            "detail": str(e)
        }

def select_best_model(crop_type):
    """
    Select the best model based on the given crop type.
    """
    model_mapping = {
        "Maize": "maize_model_v1",
        "Wheat": "wheat_model_v2",
        "Rice": "rice_model_v3"
    }

    return model_mapping.get(crop_type, "default_model")