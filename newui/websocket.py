"""
WebSocket support for NewUI real-time updates
"""

import json
import time
from typing import Dict, List, Set, Any, Optional, Callable
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from threading import Lock
import uuid


class NewUIWebSocket:
    """WebSocket manager for NewUI real-time updates"""
    
    def __init__(self, app: Flask = None, socketio: SocketIO = None):
        self.app = app
        self.socketio = socketio
        self.connections: Dict[str, Dict] = {}  # session_id -> connection info
        self.component_subscribers: Dict[str, Set[str]] = {}  # component_id -> set of session_ids
        self.rooms: Dict[str, Set[str]] = {}  # room_name -> set of session_ids
        self.lock = Lock()
        
        if app and socketio:
            self.init_app(app, socketio)
    
    def init_app(self, app: Flask, socketio: SocketIO):
        """Initialize WebSocket support with Flask-SocketIO"""
        self.app = app
        self.socketio = socketio
        
        # Register WebSocket event handlers
        self.socketio.on_event('connect', self._handle_connect)
        self.socketio.on_event('disconnect', self._handle_disconnect)
        self.socketio.on_event('subscribe', self._handle_subscribe)
        self.socketio.on_event('unsubscribe', self._handle_unsubscribe)
        self.socketio.on_event('join_room', self._handle_join_room)
        self.socketio.on_event('leave_room', self._handle_leave_room)
        self.socketio.on_event('component_action', self._handle_component_action)
        
        print("NewUI WebSocket support initialized")
    
    def _handle_connect(self, auth=None):
        """Handle new WebSocket connection"""
        session_id = self._get_session_id()
        
        with self.lock:
            self.connections[session_id] = {
                'connected_at': time.time(),
                'subscriptions': set(),
                'rooms': set(),
                'user_data': auth or {}
            }
        
        emit('connected', {'session_id': session_id, 'status': 'connected'})
        print(f"WebSocket client connected: {session_id}")
    
    def _handle_disconnect(self):
        """Handle WebSocket disconnection"""
        session_id = self._get_session_id()
        
        with self.lock:
            if session_id in self.connections:
                # Clean up subscriptions
                for component_id in self.connections[session_id]['subscriptions']:
                    if component_id in self.component_subscribers:
                        self.component_subscribers[component_id].discard(session_id)
                        if not self.component_subscribers[component_id]:
                            del self.component_subscribers[component_id]
                
                # Clean up rooms
                for room_name in self.connections[session_id]['rooms']:
                    if room_name in self.rooms:
                        self.rooms[room_name].discard(session_id)
                        if not self.rooms[room_name]:
                            del self.rooms[room_name]
                
                del self.connections[session_id]
        
        print(f"WebSocket client disconnected: {session_id}")
    
    def _handle_subscribe(self, data):
        """Handle component subscription"""
        session_id = self._get_session_id()
        component_id = data.get('componentId')
        
        if not component_id:
            emit('error', {'message': 'Component ID required for subscription'})
            return
        
        with self.lock:
            if session_id in self.connections:
                self.connections[session_id]['subscriptions'].add(component_id)
                
                if component_id not in self.component_subscribers:
                    self.component_subscribers[component_id] = set()
                self.component_subscribers[component_id].add(session_id)
        
        emit('subscribed', {'componentId': component_id})
        print(f"Client {session_id} subscribed to component {component_id}")
    
    def _handle_unsubscribe(self, data):
        """Handle component unsubscription"""
        session_id = self._get_session_id()
        component_id = data.get('componentId')
        
        if not component_id:
            emit('error', {'message': 'Component ID required for unsubscription'})
            return
        
        with self.lock:
            if session_id in self.connections:
                self.connections[session_id]['subscriptions'].discard(component_id)
                
                if component_id in self.component_subscribers:
                    self.component_subscribers[component_id].discard(session_id)
                    if not self.component_subscribers[component_id]:
                        del self.component_subscribers[component_id]
        
        emit('unsubscribed', {'componentId': component_id})
        print(f"Client {session_id} unsubscribed from component {component_id}")
    
    def _handle_join_room(self, data):
        """Handle room joining"""
        session_id = self._get_session_id()
        room_name = data.get('room')
        
        if not room_name:
            emit('error', {'message': 'Room name required'})
            return
        
        join_room(room_name)
        
        with self.lock:
            if session_id in self.connections:
                self.connections[session_id]['rooms'].add(room_name)
                
                if room_name not in self.rooms:
                    self.rooms[room_name] = set()
                self.rooms[room_name].add(session_id)
        
        emit('room_joined', {'room': room_name})
        print(f"Client {session_id} joined room {room_name}")
    
    def _handle_leave_room(self, data):
        """Handle room leaving"""
        session_id = self._get_session_id()
        room_name = data.get('room')
        
        if not room_name:
            emit('error', {'message': 'Room name required'})
            return
        
        leave_room(room_name)
        
        with self.lock:
            if session_id in self.connections:
                self.connections[session_id]['rooms'].discard(room_name)
                
                if room_name in self.rooms:
                    self.rooms[room_name].discard(session_id)
                    if not self.rooms[room_name]:
                        del self.rooms[room_name]
        
        emit('room_left', {'room': room_name})
        print(f"Client {session_id} left room {room_name}")
    
    def _handle_component_action(self, data):
        """Handle component actions from client"""
        session_id = self._get_session_id()
        component_id = data.get('componentId')
        action = data.get('action')
        payload = data.get('payload', {})
        
        if not component_id or not action:
            emit('error', {'message': 'Component ID and action required'})
            return
        
        # Fire custom action handlers if registered
        # This could be extended to handle application-specific actions
        emit('action_received', {
            'componentId': component_id,
            'action': action,
            'payload': payload
        })
        
        print(f"Component action from {session_id}: {component_id}.{action}")
    
    def _get_session_id(self) -> str:
        """Get session ID for current request"""
        from flask import request
        return request.sid if hasattr(request, 'sid') else str(uuid.uuid4())
    
    def update_component_state(self, component_id: str, state_data: Dict[str, Any], 
                              room: Optional[str] = None):
        """Send state update to subscribers"""
        if not self.socketio:
            return
        
        message = {
            'type': 'state_update',
            'componentId': component_id,
            'data': state_data,
            'timestamp': time.time()
        }
        
        if room:
            # Send to all clients in room
            self.socketio.emit('message', message, room=room)
            print(f"Sent state update to room {room} for component {component_id}")
        else:
            # Send to component subscribers
            with self.lock:
                if component_id in self.component_subscribers:
                    for session_id in self.component_subscribers[component_id]:
                        self.socketio.emit('message', message, room=session_id)
                    print(f"Sent state update to {len(self.component_subscribers[component_id])} subscribers for component {component_id}")
    
    def update_component_html(self, component_id: str, html_data: str, 
                             room: Optional[str] = None):
        """Send HTML update to subscribers"""
        if not self.socketio:
            return
        
        message = {
            'type': 'component_update',
            'componentId': component_id,
            'data': html_data,
            'timestamp': time.time()
        }
        
        if room:
            self.socketio.emit('message', message, room=room)
            print(f"Sent HTML update to room {room} for component {component_id}")
        else:
            with self.lock:
                if component_id in self.component_subscribers:
                    for session_id in self.component_subscribers[component_id]:
                        self.socketio.emit('message', message, room=session_id)
                    print(f"Sent HTML update to {len(self.component_subscribers[component_id])} subscribers for component {component_id}")
    
    def broadcast_message(self, data: Dict[str, Any], room: Optional[str] = None):
        """Broadcast message to all clients or specific room"""
        if not self.socketio:
            return
        
        message = {
            'type': 'broadcast',
            'data': data,
            'timestamp': time.time()
        }
        
        if room:
            self.socketio.emit('message', message, room=room)
            print(f"Broadcast message to room {room}")
        else:
            self.socketio.emit('message', message)
            print("Broadcast message to all clients")
    
    def send_custom_message(self, data: Dict[str, Any], room: Optional[str] = None,
                           session_id: Optional[str] = None):
        """Send custom message"""
        if not self.socketio:
            return
        
        message = {
            'type': 'custom',
            'data': data,
            'timestamp': time.time()
        }
        
        if session_id:
            self.socketio.emit('message', message, room=session_id)
            print(f"Sent custom message to session {session_id}")
        elif room:
            self.socketio.emit('message', message, room=room)
            print(f"Sent custom message to room {room}")
        else:
            self.socketio.emit('message', message)
            print("Sent custom message to all clients")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about current connections"""
        with self.lock:
            return {
                'total_connections': len(self.connections),
                'component_subscriptions': {
                    comp_id: len(subscribers) 
                    for comp_id, subscribers in self.component_subscribers.items()
                },
                'active_rooms': {
                    room: len(members) 
                    for room, members in self.rooms.items()
                }
            }
    
    def cleanup_stale_connections(self, max_age_seconds: int = 3600):
        """Clean up stale connections (optional maintenance)"""
        current_time = time.time()
        stale_sessions = []
        
        with self.lock:
            for session_id, info in self.connections.items():
                if current_time - info.get('connected_at', 0) > max_age_seconds:
                    stale_sessions.append(session_id)
            
            for session_id in stale_sessions:
                # This would need to be coordinated with actual socket disconnection
                print(f"Marking session {session_id} as stale")