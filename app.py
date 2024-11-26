from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store online users
online_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"New connection established: {request.sid}")
    emit('update_users', [
        {
            'username': user['username'],
            'status': user['status'],
            'last_seen': user['last_seen']
        } for user in online_users.values()
    ], broadcast=True)

@socketio.on('user_connect')
def handle_user_connect(data):
    try:
        username = data.get('username')
        if not username:
            return
            
        online_users[request.sid] = {
            'username': username,
            'status': 'online',
            'last_seen': datetime.now().isoformat()
        }
        
        # Broadcast user joined message
        emit('user_joined', {
            'username': username,
            'message': f'{username} has joined the chat!'
        }, broadcast=True)
        
        # Update online users list for all clients
        emit('update_users', [
            {
                'username': user['username'],
                'status': user['status'],
                'last_seen': user['last_seen']
            } for user in online_users.values()
        ], broadcast=True)
    except Exception as e:
        print(f"Error in handle_user_connect: {str(e)}")

@socketio.on('send_message')
def handle_message(data):
    try:
        if request.sid not in online_users:
            return
            
        message = data.get('message')
        if not message:
            return
            
        sender = online_users[request.sid]['username']
        timestamp = datetime.now().isoformat()
        
        # Broadcast message to all connected users
        emit('new_message', {
            'messageId': str(datetime.now().timestamp()),
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        }, broadcast=True)
        
    except Exception as e:
        print(f"Error in handle_message: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in online_users:
        username = online_users[request.sid]['username']
        
        # Remove user from online users
        del online_users[request.sid]
        
        # Broadcast user left message
        emit('user_left', {
            'username': username,
            'message': f'{username} has left the chat!'
        }, broadcast=True)
        
        # Update online users list for all clients
        emit('update_users', [
            {
                'username': user['username'],
                'status': user['status'],
                'last_seen': user['last_seen']
            } for user in online_users.values()
        ], broadcast=True)

if __name__ == '__main__':
    print("Server is running on http://127.0.0.1:5000")
    socketio.run(app, debug=True)
