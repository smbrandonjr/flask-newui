"""
State stores for complex NewUI applications
"""

from typing import Dict, List, Any, Optional, Callable, Set
import json
import copy
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from threading import Lock
import time


@dataclass
class StateAction:
    """Represents a state change action"""
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    component_id: Optional[str] = None


class StateSubscriber:
    """Subscriber interface for state changes"""
    
    def __init__(self, callback: Callable, selector: Optional[Callable] = None):
        self.callback = callback
        self.selector = selector  # Optional function to select specific state slice
        self.last_selected_state = None
    
    def notify(self, state: Dict[str, Any], action: StateAction):
        """Notify subscriber of state change"""
        try:
            if self.selector:
                selected_state = self.selector(state)
                # Only notify if selected state has changed
                if selected_state != self.last_selected_state:
                    self.last_selected_state = copy.deepcopy(selected_state)
                    self.callback(selected_state, action)
            else:
                self.callback(state, action)
        except Exception as e:
            print(f"Error in state subscriber: {e}")


class Store(ABC):
    """Abstract base class for state stores"""
    
    def __init__(self, initial_state: Dict[str, Any] = None):
        self._state = initial_state or {}
        self._subscribers: List[StateSubscriber] = []
        self._middleware: List[Callable] = []
        self._lock = Lock()
        self._history: List[StateAction] = []
        self._max_history = 100
    
    @abstractmethod
    def reduce(self, state: Dict[str, Any], action: StateAction) -> Dict[str, Any]:
        """Reduce function to handle state changes"""
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state (read-only copy)"""
        with self._lock:
            return copy.deepcopy(self._state)
    
    def get_state_slice(self, path: str) -> Any:
        """Get a specific slice of state using dot notation"""
        parts = path.split('.')
        value = self._state
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return copy.deepcopy(value)
    
    def dispatch(self, action: StateAction) -> Dict[str, Any]:
        """Dispatch an action to update state"""
        with self._lock:
            # Apply middleware
            for middleware in self._middleware:
                action = middleware(self._state, action) or action
            
            # Reduce state
            new_state = self.reduce(copy.deepcopy(self._state), action)
            
            # Update state
            self._state = new_state
            
            # Add to history
            self._history.append(action)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]
            
            # Notify subscribers
            self._notify_subscribers(action)
            
            return copy.deepcopy(new_state)
    
    def subscribe(self, callback: Callable, selector: Optional[Callable] = None) -> Callable:
        """Subscribe to state changes. Returns unsubscribe function."""
        subscriber = StateSubscriber(callback, selector)
        self._subscribers.append(subscriber)
        
        # Immediately notify with current state
        subscriber.notify(self._state, StateAction("@@INIT"))
        
        def unsubscribe():
            if subscriber in self._subscribers:
                self._subscribers.remove(subscriber)
        
        return unsubscribe
    
    def add_middleware(self, middleware: Callable):
        """Add middleware function"""
        self._middleware.append(middleware)
    
    def _notify_subscribers(self, action: StateAction):
        """Notify all subscribers of state change"""
        for subscriber in self._subscribers[:]:  # Copy list to avoid modification during iteration
            subscriber.notify(self._state, action)
    
    def get_history(self) -> List[StateAction]:
        """Get action history"""
        with self._lock:
            return copy.deepcopy(self._history)
    
    def clear_history(self):
        """Clear action history"""
        with self._lock:
            self._history.clear()


class SimpleStore(Store):
    """Simple store with basic reducers"""
    
    def reduce(self, state: Dict[str, Any], action: StateAction) -> Dict[str, Any]:
        """Simple reducer that handles basic actions"""
        action_type = action.type
        payload = action.payload
        
        if action_type == "SET_STATE":
            # Merge payload into state
            return {**state, **payload}
        
        elif action_type == "SET_VALUE":
            # Set a specific value using path
            path = payload.get('path', '')
            value = payload.get('value')
            
            if path:
                new_state = copy.deepcopy(state)
                self._set_value_by_path(new_state, path, value)
                return new_state
        
        elif action_type == "APPEND_TO_LIST":
            # Append item to a list
            path = payload.get('path', '')
            item = payload.get('item')
            
            if path:
                new_state = copy.deepcopy(state)
                list_value = self._get_value_by_path(new_state, path)
                if isinstance(list_value, list):
                    list_value.append(item)
                else:
                    self._set_value_by_path(new_state, path, [item])
                return new_state
        
        elif action_type == "REMOVE_FROM_LIST":
            # Remove item from list by index or value
            path = payload.get('path', '')
            index = payload.get('index')
            value = payload.get('value')
            
            if path:
                new_state = copy.deepcopy(state)
                list_value = self._get_value_by_path(new_state, path)
                if isinstance(list_value, list):
                    if index is not None and 0 <= index < len(list_value):
                        list_value.pop(index)
                    elif value is not None and value in list_value:
                        list_value.remove(value)
                return new_state
        
        elif action_type == "TOGGLE_BOOLEAN":
            # Toggle a boolean value
            path = payload.get('path', '')
            if path:
                new_state = copy.deepcopy(state)
                current_value = self._get_value_by_path(new_state, path)
                self._set_value_by_path(new_state, path, not bool(current_value))
                return new_state
        
        elif action_type == "INCREMENT":
            # Increment a numeric value
            path = payload.get('path', '')
            amount = payload.get('amount', 1)
            if path:
                new_state = copy.deepcopy(state)
                current_value = self._get_value_by_path(new_state, path) or 0
                self._set_value_by_path(new_state, path, current_value + amount)
                return new_state
        
        elif action_type == "RESET":
            # Reset to initial state or provided state
            return payload.get('state', {})
        
        return state
    
    def _get_value_by_path(self, obj: Dict[str, Any], path: str) -> Any:
        """Get value by dot notation path"""
        parts = path.split('.')
        value = obj
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _set_value_by_path(self, obj: Dict[str, Any], path: str, value: Any):
        """Set value by dot notation path"""
        parts = path.split('.')
        current = obj
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value


class ComponentStore(SimpleStore):
    """Store specifically designed for component state management"""
    
    def __init__(self, initial_state: Dict[str, Any] = None):
        super().__init__(initial_state)
        self.component_subscriptions: Dict[str, Set[str]] = {}  # component_id -> set of paths
    
    def connect_component(self, component_id: str, paths: List[str] = None):
        """Connect a component to specific state paths"""
        if component_id not in self.component_subscriptions:
            self.component_subscriptions[component_id] = set()
        
        if paths:
            self.component_subscriptions[component_id].update(paths)
    
    def disconnect_component(self, component_id: str):
        """Disconnect a component from the store"""
        if component_id in self.component_subscriptions:
            del self.component_subscriptions[component_id]
    
    def get_component_state(self, component_id: str) -> Dict[str, Any]:
        """Get state relevant to a specific component"""
        if component_id not in self.component_subscriptions:
            return {}
        
        component_state = {}
        for path in self.component_subscriptions[component_id]:
            value = self.get_state_slice(path)
            if value is not None:
                # Build nested object structure
                self._set_value_by_path(component_state, path, value)
        
        return component_state


class StoreManager:
    """Manages multiple stores and provides global access"""
    
    def __init__(self):
        self.stores: Dict[str, Store] = {}
        self._default_store: Optional[Store] = None
    
    def create_store(self, name: str, store_class: type = SimpleStore, 
                    initial_state: Dict[str, Any] = None) -> Store:
        """Create and register a new store"""
        store = store_class(initial_state)
        self.stores[name] = store
        
        if self._default_store is None:
            self._default_store = store
        
        return store
    
    def get_store(self, name: str = None) -> Optional[Store]:
        """Get a store by name, or default store if no name provided"""
        if name is None:
            return self._default_store
        return self.stores.get(name)
    
    def remove_store(self, name: str):
        """Remove a store"""
        if name in self.stores:
            del self.stores[name]
            
            # Update default store if needed
            if self._default_store == self.stores.get(name):
                self._default_store = next(iter(self.stores.values())) if self.stores else None
    
    def dispatch_to_all(self, action: StateAction):
        """Dispatch action to all stores"""
        for store in self.stores.values():
            store.dispatch(action)
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get state from all stores"""
        return {name: store.get_state() for name, store in self.stores.items()}


# Middleware functions
def logging_middleware(state: Dict[str, Any], action: StateAction) -> StateAction:
    """Middleware that logs all actions"""
    print(f"[Store] Action: {action.type}, Payload: {action.payload}")
    return action

def validation_middleware(state: Dict[str, Any], action: StateAction) -> StateAction:
    """Middleware that validates actions"""
    # Example validation - you can customize this
    if action.type == "SET_VALUE":
        path = action.payload.get('path')
        if not path:
            print(f"[Store] Warning: SET_VALUE action missing path")
    
    return action

def persistence_middleware(persistence_key: str):
    """Middleware factory for state persistence"""
    def middleware(state: Dict[str, Any], action: StateAction) -> StateAction:
        # In a real implementation, you might save to localStorage, database, etc.
        print(f"[Store] Persisting state for key: {persistence_key}")
        return action
    return middleware


# Helper functions for common patterns
def create_action(action_type: str, payload: Dict[str, Any] = None, 
                 component_id: str = None) -> StateAction:
    """Helper to create state actions"""
    return StateAction(
        type=action_type,
        payload=payload or {},
        component_id=component_id
    )

def set_value_action(path: str, value: Any, component_id: str = None) -> StateAction:
    """Helper to create SET_VALUE action"""
    return create_action("SET_VALUE", {"path": path, "value": value}, component_id)

def append_to_list_action(path: str, item: Any, component_id: str = None) -> StateAction:
    """Helper to create APPEND_TO_LIST action"""
    return create_action("APPEND_TO_LIST", {"path": path, "item": item}, component_id)

def toggle_boolean_action(path: str, component_id: str = None) -> StateAction:
    """Helper to create TOGGLE_BOOLEAN action"""
    return create_action("TOGGLE_BOOLEAN", {"path": path}, component_id)

def increment_action(path: str, amount: int = 1, component_id: str = None) -> StateAction:
    """Helper to create INCREMENT action"""
    return create_action("INCREMENT", {"path": path, "amount": amount}, component_id)


# Global store manager instance
store_manager = StoreManager()

# Convenience functions for global access
def create_store(name: str, store_class: type = SimpleStore, 
                initial_state: Dict[str, Any] = None) -> Store:
    """Create a global store"""
    return store_manager.create_store(name, store_class, initial_state)

def get_store(name: str = None) -> Optional[Store]:
    """Get a global store"""
    return store_manager.get_store(name)

def dispatch(action: StateAction, store_name: str = None):
    """Dispatch action to a store"""
    store = get_store(store_name)
    if store:
        return store.dispatch(action)
    else:
        print(f"Store '{store_name}' not found")

def get_state(store_name: str = None) -> Dict[str, Any]:
    """Get state from a store"""
    store = get_store(store_name)
    return store.get_state() if store else {}

def subscribe(callback: Callable, selector: Optional[Callable] = None, 
             store_name: str = None) -> Optional[Callable]:
    """Subscribe to state changes"""
    store = get_store(store_name)
    return store.subscribe(callback, selector) if store else None