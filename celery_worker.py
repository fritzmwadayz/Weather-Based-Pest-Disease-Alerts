from celeryconf import celery  #Celery instance
from app import create_app

#Flask context
app = create_app()
app.app_context().push()

if __name__ == '__main__':
    celery.start()