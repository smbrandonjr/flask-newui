"""
State management utilities for NewUI
"""

import json
from typing import Dict, Any, Optional
from flask import session, request
import hashlib


class StateManager:
    """Manages component state between server and client"""
    
    def __init__(self):
        self._states: Dict[str, Dict[str, Any]] = {}
    
    def get_state(self, component_id: str) -> Dict[str, Any]:
        """Get state for a component"""
        # Check session first
        session_key = f'ui_state_{component_id}'
        if session_key in session:
            return session[session_key]
        
        # Check in-memory states
        return self._states.get(component_id, {})
    
    def set_state(self, component_id: str, state: Dict[str, Any], 
                  persist: bool = False):
        """Set state for a component"""
        self._states[component_id] = state
        
        if persist:
            session[f'ui_state_{component_id}'] = state
    
    def update_state(self, component_id: str, updates: Dict[str, Any], 
                     persist: bool = False):
        """Update specific state values"""
        current = self.get_state(component_id)
        current.update(updates)
        self.set_state(component_id, current, persist)
    
    def clear_state(self, component_id: str):
        """Clear state for a component"""
        self._states.pop(component_id, None)
        session.pop(f'ui_state_{component_id}', None)
    
    def generate_component_id(self, component_name: str, 
                            props: Dict[str, Any]) -> str:
        """Generate a unique ID for a component instance"""
        # Create hash from component name and props
        data = f"{component_name}:{json.dumps(props, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()[:8]
    
    def sync_from_client(self, component_id: str, client_state: Dict[str, Any]):
        """Sync state from client-side updates"""
        # Validate and merge client state
        current = self.get_state(component_id)
        
        # Only update allowed fields
        allowed_updates = client_state.get('_allowed_updates', [])
        if allowed_updates:
            updates = {k: v for k, v in client_state.items() 
                      if k in allowed_updates}
        else:
            updates = client_state
        
        self.update_state(component_id, updates)
    
    def to_json(self, component_id: str) -> str:
        """Convert component state to JSON"""
        return json.dumps(self.get_state(component_id))
    
    def from_json(self, component_id: str, json_str: str):
        """Load component state from JSON"""
        try:
            state = json.loads(json_str)
            self.set_state(component_id, state)
        except json.JSONDecodeError:
            pass