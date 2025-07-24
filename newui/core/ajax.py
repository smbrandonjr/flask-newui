"""
AJAX/partial rendering handlers for NewUI
"""

from flask import request, jsonify, render_template, make_response
from typing import Dict, Any, Optional, Callable
import json
from functools import wraps


class AjaxHandler:
    """Handles AJAX requests for partial rendering"""
    
    def __init__(self, app=None):
        self.app = app
        self._handlers: Dict[str, Callable] = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Register AJAX endpoint
        app.add_url_rule(
            '/ui/partial/<component>',
            'newui_partial',
            self._handle_partial_request,
            methods=['GET', 'POST']
        )
        
        # Register state sync endpoint
        app.add_url_rule(
            '/ui/state/<component_id>',
            'newui_state',
            self._handle_state_sync,
            methods=['POST']
        )
    
    def _handle_partial_request(self, component: str):
        """Handle partial component rendering requests"""
        # Get component data from request
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        # Check for custom handler
        if component in self._handlers:
            result = self._handlers[component](**data)
            if isinstance(result, dict):
                # Render template with data
                template = f"components/{component}.html"
                return render_template(template, **result)
            return result
        
        # Default rendering
        template = f"components/{component}.html"
        return render_template(template, **data)
    
    def _handle_state_sync(self, component_id: str):
        """Handle state synchronization from client"""
        if request.method != 'POST':
            return jsonify({'error': 'Method not allowed'}), 405
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get state manager from app extensions
        if 'newui' in self.app.extensions:
            state_manager = self.app.extensions['newui'].state
            state_manager.sync_from_client(component_id, data)
            
            # Return updated state
            return jsonify({
                'success': True,
                'component_id': component_id,
                'state': state_manager.get_state(component_id)
            })
        
        return jsonify({
            'success': True,
            'component_id': component_id,
            'state': data
        })
    
    def register_handler(self, component: str, handler: Callable):
        """Register a custom handler for a component"""
        self._handlers[component] = handler
    
    def reactive(self, func):
        """Decorator to make routes reactive (support partial rendering)"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if this is an AJAX request for partial update
            if request.headers.get('X-NewUI-Partial'):
                # Extract component to update
                component = request.headers.get('X-NewUI-Component')
                if component:
                    # Render only the requested component
                    result = func(*args, **kwargs)
                    if isinstance(result, tuple):
                        # Handle (template, context) return
                        template, context = result
                        return render_template(
                            f"components/{component}.html", 
                            **context
                        )
                    elif isinstance(result, dict):
                        # Handle dict context return
                        return render_template(
                            f"components/{component}.html",
                            **result
                        )
            
            # Normal full-page render
            return func(*args, **kwargs)
        
        return wrapper
    
    def component_response(self, component: str, **kwargs):
        """Create a response for a component update"""
        html = render_template(f"components/{component}.html", **kwargs)
        
        response = make_response(html)
        response.headers['X-NewUI-Component'] = component
        
        # Include state updates if any
        if '_state' in kwargs:
            response.headers['X-NewUI-State'] = json.dumps(kwargs['_state'])
        
        return response