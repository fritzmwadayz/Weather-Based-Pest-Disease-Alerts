from celeryconf import celery
from app.services.weather_service import WeatherService
from app.models import db

@celery.task(bind=True)
def update_all_weather_data(self):
    """Periodically update all weather locations"""
    locations = ["Nairobi", "Taita Hills", "Kisumu", "Mombasa"]
    results = []
    
    for location in locations:
        try:
            weather = WeatherService.get_current_weather(location)
            results.append(f"Updated {location}: {weather.temperature}°C")
        except Exception as e:
            results.append(f"Failed {location}: {str(e)}")
    
    db.session.commit()
    return results