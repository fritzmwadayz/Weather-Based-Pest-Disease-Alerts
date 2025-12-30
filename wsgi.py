'''from app import create_app
from app.extensions import socketio

app = create_app()

@socketio.on('connect')
def handle_connect():
    socketio.emit('connection_response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)'''

#from app import create_app, socketio

#app = create_app()
#socketio_app = socketio.WSGIApp(socketio, app)  # Special WSGI wrapper

#if __name__ == '__main__':
    # Can still run directly if needed
#    socketio.run(app)

print(f"wsgi.py imported by: {__name__}")
from app import create_app
app = create_app()  # Production configuration happens here

# This file should ONLY be used by WSGI servers like gunicorn
application = app  # For WSGI servers expecting 'application'