"""
Example application demonstrating NewUI WebSocket real-time updates
"""

from flask import Flask, render_template_string, request, jsonify
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    print("Warning: Flask-SocketIO not installed. Install with: pip install flask-socketio")
    SocketIO = None
    SOCKETIO_AVAILABLE = False

from newui import NewUI
from newui import components as ui
import time
import json
import threading
import random

if SOCKETIO_AVAILABLE:
    from newui.websocket import NewUIWebSocket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
newui = NewUI(app)

# Initialize SocketIO if available
if SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*")
    # Initialize NewUI WebSocket support
    ws = NewUIWebSocket(app, socketio)
else:
    socketio = None
    ws = None

# Shared application state
app_state = {
    'users_online': 0,
    'chat_messages': [],
    'live_counter': 0,
    'system_stats': {
        'cpu': 45,
        'memory': 67,
        'disk': 23
    }
}

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI WebSocket Real-time Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel=\"stylesheet\">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    <style>
        .demo-section {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            background: white;
        }
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
        }
        .connected { background-color: #28a745; }
        .disconnected { background-color: #dc3545; }
        .reconnecting { background-color: #ffc107; color: #000; }
        
        .chat-messages {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
            padding: 10px;
            background: #f8f9fa;
        }
        .chat-message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 5px;
            background: white;
        }
        .system-message {
            background: #e9ecef !important;
            font-style: italic;
            color: #6c757d;
        }
        
        .stats-card {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            margin: 10px;
        }
        .stats-value {
            font-size: 2rem;
            font-weight: bold;
            color: #007bff;
        }
        
        .live-counter {
            font-size: 4rem;
            font-weight: bold;
            text-align: center;
            color: #28a745;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .progress-animated {
            transition: width 0.5s ease;
        }
    </style>
</head>
<body>
    <div class="connection-status disconnected" id="connection-status">
        Disconnected
    </div>
    
    <div class="container mt-5">
        <h1>Real-time WebSocket Demo</h1>
        <p class="text-muted">This demo shows real-time updates using WebSocket connections</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>Live Statistics</h3>
                    <p>Real-time system monitoring</p>
                    
                    <div data-ui-component="system-stats" 
                         data-ui-state='{{ stats_state | tojson }}'>
                        <div class="row">
                            <div class="col-4">
                                <div class="stats-card bg-primary text-white">
                                    <div>CPU Usage</div>
                                    <div class="stats-value" data-ui-bind="cpu">{{ stats_state.cpu }}%</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stats-card bg-success text-white">
                                    <div>Memory</div>
                                    <div class="stats-value" data-ui-bind="memory">{{ stats_state.memory }}%</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stats-card bg-info text-white">
                                    <div>Disk</div>
                                    <div class="stats-value" data-ui-bind="disk">{{ stats_state.disk }}%</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Progress bars -->
                        <div class="mt-3">
                            <div class="mb-2">
                                <label>CPU</label>
                                <div class="progress">
                                    <div class="progress-bar progress-animated" role="progressbar" 
                                         style="width: {{ stats_state.cpu }}%" 
                                         data-ui-bind="cpu" data-ui-bind-attr="style.width">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-2">
                                <label>Memory</label>
                                <div class="progress">
                                    <div class="progress-bar bg-success progress-animated" role="progressbar" 
                                         style="width: {{ stats_state.memory }}%" 
                                         data-ui-bind="memory" data-ui-bind-attr="style.width">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-2">  
                                <label>Disk</label>
                                <div class="progress">
                                    <div class="progress-bar bg-info progress-animated" role="progressbar" 
                                         style="width: {{ stats_state.disk }}%" 
                                         data-ui-bind="disk" data-ui-bind-attr="style.width">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="demo-section">
                    <h3>Live Counter</h3>
                    <p>Synchronized counter across all clients</p>
                    
                    <div data-ui-component="live-counter" 
                         data-ui-state='{"count": {{ counter_state }}}'>
                        <div class="live-counter" data-ui-bind="count">{{ counter_state }}</div>
                        <div class="text-center mt-3">
                            <button class="btn btn-success btn-lg" data-ui-click="incrementCounter">
                                +1
                            </button>
                            <button class="btn btn-warning btn-lg ms-2" data-ui-click="resetCounter">
                                Reset
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>Real-time Chat</h3>
                    <p>Live chat with all connected users</p>
                    
                    <div data-ui-component="chat-room" 
                         data-ui-state='{"messages": {{ chat_messages | tojson }}, "users_online": {{ users_online }}}'>
                        
                        <div class="mb-3">
                            <strong>Users Online: <span data-ui-bind="users_online">{{ users_online }}</span></strong>
                        </div>
                        
                        <div class="chat-messages" id="chat-messages">
                            {% for message in chat_messages %}
                            <div class="chat-message {{ 'system-message' if message.type == 'system' else '' }}">
                                {% if message.type == 'system' %}
                                    <em>{{ message.text }}</em>
                                {% else %}
                                    <strong>{{ message.user }}:</strong> {{ message.text }}
                                    <small class="text-muted">({{ message.time }})</small>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        
                        <form data-ui-submit="sendMessage" class="mt-3">
                            <div class="input-group">
                                {{ ui.input("message", placeholder="Type your message...", class_="", required=True) }}
                                <button class="btn btn-primary" type="submit">Send</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div class="demo-section">
                    <h3>Connection Info</h3>
                    <div data-ui-component="connection-info" 
                         data-ui-state='{"info": {}}'>
                        <pre id="connection-info" class="bg-light p-3"></pre>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>WebSocket Controls</h3>
                    <div class="btn-group" role="group">
                        <button class="btn btn-success" onclick="connectWebSocket()">Connect</button>
                        <button class="btn btn-danger" onclick="disconnectWebSocket()">Disconnect</button>
                        <button class="btn btn-info" onclick="subscribeToStats()">Subscribe to Stats</button>
                        <button class="btn btn-warning" onclick="unsubscribeFromStats()">Unsubscribe from Stats</button>
                        <button class="btn btn-secondary" onclick="joinChatRoom()">Join Chat Room</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        let socket = null;
        
        function updateConnectionStatus(status) {
            const statusEl = document.getElementById('connection-status');
            statusEl.className = `connection-status ${status}`;
            statusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
        
        function connectWebSocket() {
            if (socket && socket.connected) {
                console.log('Already connected');
                return;
            }
            
            socket = io();
            
            socket.on('connect', function() {
                updateConnectionStatus('connected');
                console.log('Socket.IO connected');
                
                // Auto-subscribe to components
                subscribeToStats();
                joinChatRoom();
                
                // Update connection info
                updateConnectionInfo();
            });
            
            socket.on('disconnect', function() {
                updateConnectionStatus('disconnected');
                console.log('Socket.IO disconnected');
            });
            
            socket.on('message', function(data) {
                console.log('Received WebSocket message:', data);
                
                switch(data.type) {
                    case 'state_update':
                        handleStateUpdate(data);
                        break;
                    case 'component_update':
                        handleComponentUpdate(data);
                        break;
                    case 'broadcast':
                        handleBroadcast(data);
                        break;
                    case 'custom':
                        handleCustomMessage(data);
                        break;
                }
            });
            
            socket.on('error', function(error) {
                console.error('Socket.IO error:', error);
            });
        }
        
        function disconnectWebSocket() {
            if (socket) {
                socket.disconnect();
                socket = null;
                updateConnectionStatus('disconnected');
            }
        }
        
        function subscribeToStats() {
            if (socket && socket.connected) {
                socket.emit('subscribe', { componentId: 'system-stats' });
                socket.emit('subscribe', { componentId: 'live-counter' });
            }
        }
        
        function unsubscribeFromStats() {
            if (socket && socket.connected) {
                socket.emit('unsubscribe', { componentId: 'system-stats' });
                socket.emit('unsubscribe', { componentId: 'live-counter' });
            }
        }
        
        function joinChatRoom() {
            if (socket && socket.connected) {
                socket.emit('join_room', { room: 'chat' });
            }
        }
        
        function handleStateUpdate(data) {
            const { componentId, data: stateData } = data;
            
            // Find the component and update its state
            const component = document.querySelector(`[data-ui-component="${componentId}"]`);
            if (component) {
                const componentIdAttr = component.getAttribute('data-ui-id');
                if (componentIdAttr) {
                    // Update NewUI state
                    for (const [key, value] of Object.entries(stateData)) {
                        NewUI.setStateValue(componentIdAttr, key, value);
                    }
                    
                    // Special handling for progress bars
                    if (componentId === 'system-stats') {
                        updateProgressBars(stateData);
                    }
                }
            }
        }
        
        function updateProgressBars(stats) {
            const progressBars = document.querySelectorAll('.progress-bar');
            progressBars.forEach(bar => {
                const bindAttr = bar.getAttribute('data-ui-bind');
                if (bindAttr && stats[bindAttr] !== undefined) {
                    bar.style.width = `${stats[bindAttr]}%`;
                }
            });
        }
        
        function handleComponentUpdate(data) {
            const { componentId, data: htmlData } = data;
            
            const component = document.querySelector(`[data-ui-component="${componentId}"]`);
            if (component) {
                component.outerHTML = htmlData;
                NewUI.initializeComponents();
            }
        }
        
        function handleBroadcast(data) {
            console.log('Broadcast message:', data.data);
            
            // Handle chat messages
            if (data.data.type === 'chat_message') {
                appendChatMessage(data.data.message);
            }
        }
        
        function handleCustomMessage(data) {
            console.log('Custom message:', data.data);
        }
        
        function appendChatMessage(message) {
            const chatMessages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${message.type === 'system' ? 'system-message' : ''}`;
            
            if (message.type === 'system') {
                messageDiv.innerHTML = `<em>${message.text}</em>`;
            } else {
                messageDiv.innerHTML = `
                    <strong>${message.user}:</strong> ${message.text}
                    <small class="text-muted">(${message.time})</small>
                `;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function updateConnectionInfo() {
            if (socket && socket.connected) {
                fetch('/api/connection-info')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('connection-info').textContent = JSON.stringify(data, null, 2);
                    });
            }
        }
        
        // Register NewUI handlers
        NewUI.registerHandler('incrementCounter', function(element, event) {
            if (socket && socket.connected) {
                socket.emit('component_action', {
                    componentId: 'live-counter',
                    action: 'increment',
                    payload: {}
                });
            }
        });
        
        NewUI.registerHandler('resetCounter', function(element, event) {
            if (socket && socket.connected) {
                socket.emit('component_action', {
                    componentId: 'live-counter',
                    action: 'reset',
                    payload: {}
                });
            }
        });
        
        NewUI.registerHandler('sendMessage', function(element, event) {
            const form = element;
            const messageInput = form.querySelector('input[name="message"]');
            const message = messageInput.value.trim();
            
            if (message && socket && socket.connected) {
                socket.emit('component_action', {
                    componentId: 'chat-room',
                    action: 'send_message',
                    payload: { message: message }
                });
                
                messageInput.value = '';
            }
        });
        
        // Auto-connect on page load
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(connectWebSocket, 1000);
            
            // Update connection info periodically
            setInterval(updateConnectionInfo, 5000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, 
                                ui=ui,
                                stats_state=app_state['system_stats'],
                                counter_state=app_state['live_counter'],
                                chat_messages=app_state['chat_messages'],
                                users_online=app_state['users_online'])

@app.route('/api/connection-info')
def connection_info():
    if ws:
        return jsonify(ws.get_connection_info())
    else:
        return jsonify({'error': 'WebSocket not available', 'total_connections': 0})

# WebSocket event handlers for application logic (only if SocketIO is available)
if SOCKETIO_AVAILABLE:
    @socketio.on('component_action')
    def handle_component_action(data):
        component_id = data.get('componentId')
        action = data.get('action')
        payload = data.get('payload', {})
        
        if component_id == 'live-counter':
            if action == 'increment':
                app_state['live_counter'] += 1
                # Broadcast to all subscribers
                ws.update_component_state('live-counter', {'count': app_state['live_counter']})
            elif action == 'reset':
                app_state['live_counter'] = 0
                ws.update_component_state('live-counter', {'count': app_state['live_counter']})
        
        elif component_id == 'chat-room':
            if action == 'send_message':
                message = payload.get('message', '').strip()
                if message:
                    chat_message = {
                        'user': f'User-{request.sid[:8]}',  # Simple user identification
                        'text': message,
                        'time': time.strftime('%H:%M:%S'),
                        'type': 'user'
                    }
                    app_state['chat_messages'].append(chat_message)
                    
                    # Keep only last 50 messages
                    if len(app_state['chat_messages']) > 50:
                        app_state['chat_messages'] = app_state['chat_messages'][-50:]
                    
                    # Broadcast to chat room
                    ws.broadcast_message({'type': 'chat_message', 'message': chat_message}, room='chat')

    @socketio.on('connect')
    def handle_connect(auth=None):
        app_state['users_online'] += 1
        ws.update_component_state('chat-room', {'users_online': app_state['users_online']})
        
        # Send welcome message
        welcome_message = {
            'text': f'User-{request.sid[:8]} joined the chat',
            'time': time.strftime('%H:%M:%S'),
            'type': 'system'
        }
        app_state['chat_messages'].append(welcome_message)
        ws.broadcast_message({'type': 'chat_message', 'message': welcome_message}, room='chat')

    @socketio.on('disconnect')
    def handle_disconnect():
        app_state['users_online'] = max(0, app_state['users_online'] - 1)
        ws.update_component_state('chat-room', {'users_online': app_state['users_online']})
        
        # Send goodbye message
        goodbye_message = {
            'text': f'User-{request.sid[:8]} left the chat',
            'time': time.strftime('%H:%M:%S'),
            'type': 'system'
        }
        app_state['chat_messages'].append(goodbye_message)
        ws.broadcast_message({'type': 'chat_message', 'message': goodbye_message}, room='chat')

def simulate_system_stats():
    """Background thread to simulate changing system stats"""
    while True:
        time.sleep(3)  # Update every 3 seconds
        
        # Simulate changing stats
        app_state['system_stats']['cpu'] = max(0, min(100, app_state['system_stats']['cpu'] + random.randint(-10, 10)))
        app_state['system_stats']['memory'] = max(0, min(100, app_state['system_stats']['memory'] + random.randint(-5, 5)))
        app_state['system_stats']['disk'] = max(0, min(100, app_state['system_stats']['disk'] + random.randint(-2, 2)))
        
        # Broadcast updates if WebSocket is available
        if ws:
            ws.update_component_state('system-stats', app_state['system_stats'])

if __name__ == '__main__':
    print("\\n" + "="*50)
    print("WebSocket Real-time Demo")
    print("="*50)
    print("Open http://localhost:5008")
    
    if SOCKETIO_AVAILABLE:
        print("Features:")
        print("- Real-time system stats with progress bars")
        print("- Live synchronized counter across all clients")
        print("- Real-time chat room")
        print("- WebSocket connection management")
        print("- Component subscriptions and room-based messaging")
        print("="*50 + "\\n")
        
        # Start background stats simulation
        stats_thread = threading.Thread(target=simulate_system_stats, daemon=True)
        stats_thread.start()
        
        socketio.run(app, debug=True, port=5008, allow_unsafe_werkzeug=True)
    else:
        print("WARNING: Flask-SocketIO not installed!")
        print("Install with: pip install flask-socketio")
        print("Running in basic Flask mode without WebSocket features.")
        print("="*50 + "\\n")
        
        # Start background stats simulation (without WebSocket updates)
        stats_thread = threading.Thread(target=simulate_system_stats, daemon=True)
        stats_thread.start()
        
        app.run(debug=True, port=5008)