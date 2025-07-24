"""
Enhanced Jinja2 rendering with NewUI capabilities
"""

from flask import Flask, render_template, render_template_string
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from typing import Dict, Any, Optional
import os


class EnhancedRenderer:
    """Enhanced Jinja2 renderer with NewUI extensions"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self._setup_filters()
        self._setup_globals()
    
    def init_app(self, app: Flask):
        """Initialize with Flask app"""
        self.app = app
        self._setup_filters()
        self._setup_globals()
    
    def _setup_filters(self):
        """Add custom Jinja2 filters"""
        if not self.app:
            return
            
        # Add state serialization filter
        self.app.jinja_env.filters['ui_state'] = self._serialize_state
        
        # Add data attribute builder
        self.app.jinja_env.filters['ui_attrs'] = self._build_ui_attrs
    
    def _setup_globals(self):
        """Add global functions to Jinja2"""
        if not self.app:
            return
            
        # Add component helper
        self.app.jinja_env.globals['ui_component'] = self._component_helper
        
        # Add event binding helper
        self.app.jinja_env.globals['ui_bind'] = self._bind_helper
    
    def _serialize_state(self, state: Dict[str, Any]) -> str:
        """Serialize component state for data attributes"""
        return json.dumps(state, separators=(',', ':'))
    
    def _build_ui_attrs(self, component_name: str, state: Dict[str, Any] = None, 
                        events: Dict[str, str] = None) -> str:
        """Build data attributes for a component"""
        attrs = [f'data-ui-component="{component_name}"']
        
        if state:
            attrs.append(f'data-ui-state=\'{self._serialize_state(state)}\'')
        
        if events:
            for event, handler in events.items():
                attrs.append(f'data-ui-{event}="{handler}"')
        
        return ' '.join(attrs)
    
    def _component_helper(self, name: str, **kwargs) -> str:
        """Helper to render components in templates"""
        # This will be connected to ComponentRegistry
        return f'<!-- Component: {name} -->'
    
    def _bind_helper(self, field: str, value: Any = None) -> str:
        """Helper for two-way data binding"""
        attrs = [f'data-ui-bind="{field}"']
        if value is not None:
            attrs.append(f'value="{value}"')
        return ' '.join(attrs)
    
    def render_partial(self, template: str, **kwargs) -> str:
        """Render a partial template for AJAX updates"""
        # Add UI context
        kwargs['_ui_partial'] = True
        
        if template.endswith('.html'):
            return render_template(template, **kwargs)
        else:
            return render_template_string(template, **kwargs)