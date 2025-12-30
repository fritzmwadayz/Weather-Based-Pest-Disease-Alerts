from celery import Celery
from config import CeleryConfig
import logging
from celery.schedules import crontab

# Single Celery instance with all config
celery = Celery(
    __name__,
    broker=CeleryConfig.broker_url,
    backend=CeleryConfig.result_backend,
    include=['app.tasks']  # Add your tasks module here
)

# Apply configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('celery.log')]
)

celery.conf.beat_schedule = {
    'update-weather-every-hour': {
        'task': 'app.tasks.weather_tasks.update_all_weather_data',
        'schedule': crontab(minute=0),  # Every hour
    },
}
