from datetime import datetime, timedelta
import random

class WeatherService:
    # Predefined base weather data
    LOCATION_WEATHER = {
        "Nairobi": {"temperature": 25, "humidity": 70, "rainfall": 120, "wind_speed": 10},
        "Taita Hills": {"temperature": 22, "humidity": 75, "rainfall": 200, "wind_speed": 8},
        "Kisumu": {"temperature": 28, "humidity": 80, "rainfall": 180, "wind_speed": 12},
        "Mombasa": {"temperature": 30, "humidity": 85, "rainfall": 220, "wind_speed": 15},
    }

    # Cache for generated weather data
    _weather_cache = {}

    @classmethod
    def get_current_weather(cls, location):
        """Get current weather with realistic variations (cached for 1 hour)"""
        cached = cls._weather_cache.get(location)
        
        if cached and cached['expires'] > datetime.utcnow():
            return cached['data']
        
        # Get base weather or defaults
        base = cls.LOCATION_WEATHER.get(location, {
            "temperature": 25, 
            "humidity": 70, 
            "rainfall": 120, 
            "wind_speed": 10
        })
        
        # Generate with variations
        weather_data = {
            "temperature": round(base['temperature'] + random.uniform(-2, 2), 1),
            "humidity": int(base['humidity'] + random.uniform(-5, 5)),
            "rainfall": round(base['rainfall'] * random.uniform(0.8, 1.2), 1),
            "wind_speed": round(base['wind_speed'] * random.uniform(0.7, 1.3), 1),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Cache for 1 hour
        cls._weather_cache[location] = {
            'data': weather_data,
            'expires': datetime.utcnow() + timedelta(hours=1)
        }
        
        return weather_data

    @classmethod
    def generate_forecast(cls, location, days=3):
        """Generate a weather forecast"""
        current = cls.get_current_weather(location)
        base = cls.LOCATION_WEATHER.get(location, current)
        
        forecast = []
        for day in range(1, days + 1):
            forecast.append({
                "date": (datetime.utcnow() + timedelta(days=day)).strftime('%Y-%m-%d'),
                "temperature": round(current['temperature'] + random.uniform(-2, 2), 1),
                "humidity": max(40, min(100, current['humidity'] + random.uniform(-10, 10))),
                "rain_chance": min(100, round(base['rainfall']/3 * random.uniform(0.5, 1.5))),
                "wind_speed": round(current['wind_speed'] * random.uniform(0.8, 1.2), 1),
                "condition": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"])
            })
        
        return {
            "current": current,
            "forecast": forecast
        }