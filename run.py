from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Development settings
    socketio.run(app, 
                host='localhost', 
                port=5000, 
                debug=True,
                use_reloader=True)