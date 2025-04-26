from app import socketio
from flask_socketio import emit
import json
import time 
print("---------------")
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'WebSocket connection established'})

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    emit('response', {'data': f'Server received: {data}'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    
@socketio.on('get_data')
def handle_get_data(request):
    print('Data request:', request)
    
    # Example: Send some data
    data = {
        'status': 'success',
        'message': 'Here is your data',
        'payload': {
            'items': [1, 2, 3],
            'timestamp': time.time()
        }
    }
    emit('data_response', data)
    
def send_update_to_all(message):
    socketio.emit('update', {'data': message}, broadcast=True)