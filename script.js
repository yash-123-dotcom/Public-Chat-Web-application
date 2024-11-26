const socket = io();
let username = '';

socket.on('connect', () => {
    console.log('Connected to server');
});

function joinChat() {
    username = document.getElementById('username').value.trim();
    if (username) {
        socket.emit('user_connect', { username: username });
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('chat-container').style.display = 'block';
    }
}

function sendMessage() {
    const messageInput = document.getElementById('message');
    const message = messageInput.value.trim();
    
    if (message) {
        socket.emit('send_message', { message: message });
        messageInput.value = '';
    }
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

document.getElementById('message').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

socket.on('new_message', (data) => {
    const messagesDiv = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${data.sender === username ? 'own' : 'other'}`;
    messageElement.innerHTML = `
        <strong>${data.sender}</strong><br>
        ${data.message}
        <div class="timestamp">${formatTime(data.timestamp)}</div>
    `;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});

socket.on('user_joined', (data) => {
    const messagesDiv = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'message system';
    messageElement.innerHTML = data.message;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});

socket.on('user_left', (data) => {
    const messagesDiv = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'message system';
    messageElement.innerHTML = data.message;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});

socket.on('update_users', (users) => {
    const usersDiv = document.getElementById('users');
    usersDiv.innerHTML = users
        .map(user => `
            <div class="user-item">
                <span class="user-status"></span>
                ${user.username}
            </div>
        `)
        .join('');
});

document.getElementById('username').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        joinChat();
    }
});
