"""
Main NewUI Flask extension
"""

from flask import Flask, Blueprint, url_for, session
from .core.components import ComponentRegistry
from .core.renderer import EnhancedRenderer
from .core.state import StateManager
from .core.ajax import AjaxHandler
import os
from typing import Optional, Callable


class NewUI:
    """Flask extension for NewUI framework"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.components = ComponentRegistry()
        self.renderer = EnhancedRenderer()
        self.state = StateManager()
        self.ajax = AjaxHandler()
        
        # Configuration defaults
        self._config = {
            'NEWUI_STATIC_FOLDER': 'static',
            'NEWUI_TEMPLATE_FOLDER': 'templates',
            'NEWUI_COMPONENT_FOLDER': 'components',
            'NEWUI_AUTO_RELOAD': True,
            'NEWUI_ENABLE_WEBSOCKET': False
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize NewUI with Flask app"""
        self.app = app
        
        # Update configuration from app config
        for key, default in self._config.items():
            self._config[key] = app.config.get(key, default)
        
        # Initialize submodules
        self.renderer.init_app(app)
        self.ajax.init_app(app)
        
        # Register static blueprint
        self._register_static_blueprint(app)
        
        # Add template functions
        self._register_template_functions(app)
        
        # Store reference in app extensions
        app.extensions['newui'] = self
    
    def _register_static_blueprint(self, app: Flask):
        """Register blueprint for static files"""
        newui_bp = Blueprint(
            'newui',
            __name__,
            static_folder='static',
            static_url_path='/newui/static'
        )
        app.register_blueprint(newui_bp)
    
    def _register_template_functions(self, app: Flask):
        """Register template functions and filters"""
        # Import built-in components
        from . import components as ui_components
        
        # Register components in Jinja globals
        app.jinja_env.globals['ui'] = ui_components
        
        # Connect renderer to component registry
        def render_component(name: str, **kwargs):
            return self.components.render(name, **kwargs)
        
        app.jinja_env.globals['ui_component'] = render_component
        
        # Add state management functions
        app.jinja_env.globals['ui_get_state'] = self.state.get_state
        app.jinja_env.globals['ui_set_state'] = self.state.set_state
        
        # Add CSRF token function if not already present
        if 'csrf_token' not in app.jinja_env.globals:
            def generate_csrf_token():
                # Simple CSRF token generation
                import secrets
                if '_csrf_token' not in session:
                    session['_csrf_token'] = secrets.token_hex(16)
                return session['_csrf_token']
            
            app.jinja_env.globals['csrf_token'] = generate_csrf_token
    
    def component(self, name: Optional[str] = None, template: Optional[str] = None):
        """Decorator to register a component"""
        def decorator(func):
            component_name = name or func.__name__
            return self.components.register(component_name, template)(func)
        return decorator
    
    def reactive(self, func):
        """Decorator to make routes reactive"""
        return self.ajax.reactive(func)
    
    def partial(self, component: str, handler: Callable):
        """Register a partial update handler"""
        self.ajax.register_handler(component, handler)
    
    def get_component_url(self, component: str) -> str:
        """Get URL for component partial updates"""
        return url_for('newui_partial', component=component)
    
    def render(self, template: str, **kwargs):
        """Enhanced render with NewUI context"""
        # Add NewUI context
        kwargs['_newui'] = {
            'components': self.components.list_components(),
            'version': '0.1.0'
        }
        
        return self.renderer.render_partial(template, **kwargs)