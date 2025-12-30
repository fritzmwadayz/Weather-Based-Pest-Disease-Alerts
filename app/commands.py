@app.cli.command('init-weather')
def init_weather():
    """Initialize weather data for all locations"""
    from app.services.weather_service import WeatherService
    locations = ["Nairobi", "Taita Hills", "Kisumu", "Mombasa"]
    
    for loc in locations:
        WeatherService.get_current_weather(loc)
    
    db.session.commit()
    print(f"Initialized weather for {len(locations)} locations")