"""
Component registration and handling system
"""

from typing import Dict, Any, Callable, Optional
from functools import wraps
from flask import render_template_string
import json


class ComponentRegistry:
    """Registry for NewUI components"""
    
    def __init__(self):
        self._components: Dict[str, Callable] = {}
        self._component_templates: Dict[str, str] = {}
    
    def register(self, name: str, template: Optional[str] = None):
        """Register a component with the system"""
        def decorator(func):
            @wraps(func)
            def wrapper(**kwargs):
                # Extract and set component metadata
                ui_component = name
                ui_state = kwargs.pop('ui_state', {})
                
                # Remove internal parameters before passing to user function
                kwargs.pop('_ui_component', None)
                kwargs.pop('_ui_state', None)
                
                # Validate required parameters
                if hasattr(func, '_required_params'):
                    for param in func._required_params:
                        if param not in kwargs:
                            raise ValueError(f"Component {name} requires parameter '{param}'")
                
                # Process the component
                result = func(**kwargs)
                
                # If template is provided, render it
                if template:
                    return render_template_string(template, **kwargs)
                
                return result
            
            self._components[name] = wrapper
            if template:
                self._component_templates[name] = template
            
            return wrapper
        
        return decorator
    
    def get(self, name: str) -> Optional[Callable]:
        """Get a registered component"""
        return self._components.get(name)
    
    def render(self, name: str, **kwargs) -> str:
        """Render a component"""
        component = self.get(name)
        if not component:
            raise ValueError(f"Component '{name}' not found")
        
        return component(**kwargs)
    
    def list_components(self) -> list:
        """List all registered components"""
        return list(self._components.keys())


def required_params(*params):
    """Decorator to mark required parameters for a component"""
    def decorator(func):
        func._required_params = params
        return func
    return decorator