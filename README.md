# NewUI Framework

[![PyPI version](https://badge.fury.io/py/flask-newui.svg)](https://badge.fury.io/py/flask-newui)
[![Python Support](https://img.shields.io/pypi/pyversions/flask-newui.svg)](https://pypi.org/project/flask-newui/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Framework Schema](https://img.shields.io/badge/AI%20Framework%20Schema-Available-brightgreen.svg)](#🤖-ai-assisted-development)

**A modern reactive frontend framework that bridges Flask/Jinja2 with modern UI capabilities**

NewUI transforms traditional Flask/Jinja2 development by adding reactive capabilities while maintaining the simplicity and server-side rendering benefits that make Flask development straightforward. Build sleek, intuitive frontends that rival modern frameworks without leaving the Flask ecosystem.

> **🤖 NEW: AI-Powered Development**  
> Flask-NewUI includes the world's first **AI Framework Schema (AFS)** - making AI tools instant experts in Flask-NewUI development. Get framework-specific code generation, smart recommendations, and expert debugging assistance. [Learn more ↓](#🤖-ai-assisted-development)

## ✨ Features

**🎯 Core Capabilities**
- **Zero Build Step**: Works without webpack or compilation
- **Progressive Enhancement**: Full functionality without JavaScript, enhanced with it
- **Flask-Native**: Seamless integration with Flask's request/response cycle
- **CSS Framework Agnostic**: Works with Tailwind, Bootstrap, or custom CSS
- **Jinja2-First**: All components leverage Jinja2's existing capabilities

**🤖 AI-Optimized Development**
- **AI Framework Schema (AFS)**: Comprehensive machine-readable documentation
- **Instant AI Expertise**: AI tools become Flask-NewUI experts immediately
- **Better Code Generation**: AI generates idiomatic Flask-NewUI code
- **Smart Recommendations**: AI knows when to use Flask-NewUI vs other solutions

**🚀 Phase 1: Foundation**
- ✅ Component macro system with parameter validation
- ✅ Automatic AJAX partial rendering
- ✅ Basic event handling (click, submit, change)
- ✅ State persistence via data attributes
- ✅ Flask extension for easy integration

**⚡ Phase 2: Enhanced Interactivity**
- ✅ Two-way data binding for forms
- ✅ Conditional rendering helpers
- ✅ List rendering with efficient updates
- ✅ Component lifecycle hooks
- ✅ Built-in loading states

**🔥 Phase 3: Advanced Features**
- ✅ WebSocket support for real-time updates
- ✅ Component composition patterns
- ✅ State stores for complex apps
- ✅ Route-based code splitting
- ✅ Development tools (debugger, component inspector)

## 🚀 Quick Start

### Installation

```bash
pip install flask-newui

# For WebSocket support
pip install flask-newui[websocket]

# For development
pip install flask-newui[dev]
```

### Basic Usage

```python
from flask import Flask, render_template_string
from newui import NewUI
from newui import components as ui

app = Flask(__name__)
newui = NewUI(app)

# Simple reactive page
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NewUI Demo</title>
        <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    </head>
    <body>
        <div class="container">
            <h1>Welcome to NewUI!</h1>
            
            <!-- Reactive Counter -->
            <div data-ui-component="counter" data-ui-state='{"count": 0}'>
                <p>Count: <span data-ui-bind="count">0</span></p>
                {{ ui.button("Increment", onclick="increment") }}
                {{ ui.button("Reset", onclick="reset") }}
            </div>
            
            <!-- AJAX Form -->
            <form data-ui-submit="ajax:/api/save">
                {{ ui.input("name", placeholder="Enter your name") }}
                {{ ui.button("Save", type="submit") }}
            </form>
        </div>
        
        <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
        <script>
            NewUI.registerHandler('increment', function(element, event) {
                const componentId = NewUI.getComponentId(element);
                const state = NewUI.state[componentId];
                NewUI.setStateValue(componentId, 'count', (state.count || 0) + 1);
            });
            
            NewUI.registerHandler('reset', function(element, event) {
                const componentId = NewUI.getComponentId(element);
                NewUI.setStateValue(componentId, 'count', 0);
            });
        </script>
    </body>
    </html>
    ''', ui=ui)

if __name__ == '__main__':
    app.run(debug=True)
```

### 5-Minute Tutorial

**1. Create a Flask app with NewUI:**

```python
from flask import Flask
from newui import NewUI

app = Flask(__name__)
newui = NewUI(app)
```

**2. Use built-in components:**

```python
from newui import components as ui

# In your template
{{ ui.button("Click Me", onclick="handleClick") }}
{{ ui.input("email", type="email", placeholder="Enter email") }}
{{ ui.card("Card content", title="My Card") }}
```

**3. Add reactivity:**

```html
<!-- State-aware component -->
<div data-ui-component="todo-list" data-ui-state='{"items": []}'>
    <!-- Component content with data binding -->
    <span data-ui-bind="items.length">0</span> items
</div>
```

**4. Handle events:**

```javascript
NewUI.registerHandler('addTodo', function(element, event) {
    const componentId = NewUI.getComponentId(element);
    const state = NewUI.state[componentId];
    // Update state and UI automatically updates
    NewUI.setStateValue(componentId, 'items', [...state.items, newItem]);
});
```

## 🤖 AI-Assisted Development

**Developing with AI tools? Flask-NewUI includes the world's first AI Framework Schema (AFS) to make AI your expert coding partner.**

### What is AI Framework Schema?

The AI Framework Schema is a revolutionary machine-readable documentation format that makes AI models instantly expert in Flask-NewUI. Instead of generic suggestions, AI tools provide:

✅ **Framework-specific code generation**  
✅ **Contextual recommendations** (when to use Flask-NewUI vs alternatives)  
✅ **Idiomatic patterns** and best practices  
✅ **Targeted debugging assistance**  

### Using AFS with AI Tools

**1. Include the schema in your AI conversations:**
```
Please reference the Flask-NewUI AI Framework Schema when helping me:
[Paste contents of flask-newui.afs.json]
```

**2. Or reference it from the repository:**
```
Use the AI Framework Schema at: /flask-newui.afs.json
to understand Flask-NewUI capabilities and provide expert assistance.
```

**3. Example AI-powered development:**
```
Human: "Create a todo app with real-time updates"
AI: [With AFS] "Perfect! Flask-NewUI is ideal for this. Use WebSocket 
integration with component state management..."
```

### AFS Files in This Repository

- **`flask-newui.afs.json`** - Complete schema making AI an instant expert
- **`afs-spec.md`** - Full specification for the AFS standard  
- **`validate_afs.py`** - Tool to validate schema files
- **`AFS-README.md`** - Comprehensive AFS documentation

**Try it yourself:** Ask your AI assistant about Flask-NewUI while providing the AFS file. Watch it become an instant expert! 🚀

## Component System

### Built-in Components

All components are available via the `ui` global in templates:

- **Button**: `ui.button(text, type, variant, onclick, disabled, class_)`
- **Form**: `ui.form(content, action, method, ajax, csrf_token)`
- **Input**: `ui.input(name, type, value, placeholder, label, bind)`
- **Select**: `ui.select(name, options, selected, label, bind)`
- **Card**: `ui.card(content, title, footer, class_)`
- **Alert**: `ui.alert(message, type, dismissible, class_)`

### Custom Components

```python
@ui.component('my_component')
def my_component(title, content):
    return render_template('components/my_component.html', 
                         title=title, content=content)
```

## Event Handling

### Declarative Events

```html
<!-- Click handler -->
<button data-ui-click="handleClick">Click me</button>

<!-- AJAX handler -->
<button data-ui-click="ajax:/api/save">Save</button>

<!-- Form submission -->
<form data-ui-submit="ajax:/api/submit">
```

### JavaScript Integration

```javascript
// Register custom handler
NewUI.registerHandler('handleClick', function(element, event) {
    console.log('Button clicked!');
});

// Update component via AJAX
NewUI.updateComponent('component_id', data);
```

## State Management

### Server-Side State

```python
# In your route
ui.state.set_state('component_id', {'count': 0})
state = ui.state.get_state('component_id')
```

### Client-Side Binding

```html
<!-- Two-way data binding -->
<input data-ui-bind="user.name" value="{{ user.name }}">

<!-- State persistence -->
<div data-ui-component="counter" data-ui-state='{"count": 0}'>
```

## AJAX Partial Rendering

### Reactive Routes

```python
@app.route('/dashboard')
@ui.reactive
def dashboard():
    # Automatically handles partial updates
    return render_template('dashboard.html', data=get_data())
```

### Manual Partial Updates

```python
@app.route('/update/<component>')
def update_component(component):
    return ui.ajax.component_response(component, data=new_data)
```

## CSS Framework Integration

NewUI works seamlessly with any CSS framework:

### Tailwind CSS v4.0
```html
{{ ui.button("Save", class_="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600") }}
{{ ui.input("email", class_="rounded-lg border-gray-300 shadow-sm focus:ring-blue-500") }}
```

**See the complete example:** `examples/tailwind_modern_ui.py` - A modern dashboard with dark mode, animations, and responsive design.

### Bootstrap
```html
{{ ui.button("Save", class="btn btn-primary") }}
{{ ui.input("email", class="form-control") }}
```

## 📚 Examples

Comprehensive examples are included in the `examples/` directory:

### Basic Examples
- **`todo_app.py`** - Complete todo application with AJAX forms
- **`form_binding.py`** - Two-way data binding demonstration
- **`basic_forms.py`** - Simple form handling and validation
- **`dynamic_content.py`** - Dynamic conditional content rendering
- **`dynamic_lists.py`** - Efficient list updates and rendering
- **`ajax_loading.py`** - Loading states and progress indicators
- **`component_lifecycle.py`** - Component lifecycle hooks demo
- **`tailwind_modern_ui.py`** - Modern dashboard with Tailwind CSS v4.0 and dark mode

### Advanced Examples  
- **`realtime_chat.py`** - Real-time chat with WebSocket integration
- **`state_management.py`** - Redux-like state management patterns
- **`nested_components.py`** - Component composition and nesting
- **`spa_routing.py`** - Single-page application routing
- **`debug_tools.py`** - Development tools and debugging helpers

### Quick Examples

**Todo List with Real-time Updates:**
```python
from flask import Flask
from newui import NewUI
from newui import components as ui

app = Flask(__name__)
newui = NewUI(app)

todos = []

@app.route('/')
def index():
    return render_template_string('''
    <div data-ui-component="todo-app" data-ui-state='{"todos": {{ todos | tojson }}}'>
        <form data-ui-submit="addTodo">
            {{ ui.input("todo", placeholder="Add new todo...") }}
            {{ ui.button("Add", type="submit") }}
        </form>
        <div data-ui-list="todos" data-ui-list-item="todo">
            <div class="todo-item">
                <span data-ui-bind="todo.text"></span>
                {{ ui.button("Delete", onclick="deleteTodo", data_todo_id="todo.id") }}
            </div>
        </div>
    </div>
    ''', ui=ui, todos=todos)
```

**Real-time Chat:**
```python
# With WebSocket support
from newui.websocket import NewUIWebSocket

socketio = SocketIO(app)
ws = NewUIWebSocket(app, socketio)

@socketio.on('send_message')
def handle_message(data):
    # Broadcast to all connected clients
    ws.broadcast_message({'type': 'new_message', 'message': data})
```

## 🔧 API Reference

### Core Classes

#### `NewUI(app=None)`
Main framework class for Flask integration.

```python
from newui import NewUI

newui = NewUI(app)  # or newui.init_app(app)
```

**Methods:**
- `init_app(app)` - Initialize with Flask app
- `reactive(func)` - Decorator for reactive routes
- `component(name)` - Decorator for custom components

#### `components` Module
Built-in UI components.

```python
from newui import components as ui

# Basic components
ui.button(text, onclick=None, type="button", variant="primary", disabled=False, class_="")
ui.input(name, type="text", value="", placeholder="", label=None, bind=None, required=False)
ui.form(action="", method="POST", ajax=False, csrf_token=None, class_="")
ui.select(name, options=[], selected=None, label=None, bind=None, class_="")

# Layout components  
ui.card(content, title=None, footer=None, class_="")
ui.alert(message, type="info", dismissible=False, class_="")
ui.modal(content, title=None, id=None, size="md", class_="")

# Advanced components
ui.list_render(items, item_template, bind=None, class_="")
ui.conditional(condition, content, else_content=None)
ui.loading_state(content, loading_text="Loading...", class_="")
```

### State Management

#### Client-Side State
```javascript
// Get component state
const state = NewUI.getState(componentId);

// Set single value
NewUI.setStateValue(componentId, 'key', value);

// Update multiple values
NewUI.updateState(componentId, {key1: value1, key2: value2});

// Subscribe to state changes
NewUI.onStateChange(componentId, callback);
```

#### Server-Side State
```python
from newui.stores import Store

# Create store
store = Store('myStore', initial_state={'count': 0})

# Dispatch actions
store.dispatch('increment', payload={'amount': 1})

# Subscribe to changes
store.subscribe(lambda state: print(f"New state: {state}"))
```

### WebSocket Integration

```python
from newui.websocket import NewUIWebSocket

ws = NewUIWebSocket(app, socketio)

# Update component state in real-time
ws.update_component_state('component-id', {'count': 42})

# Broadcast to all clients
ws.broadcast_message({'type': 'notification', 'message': 'Hello!'})

# Send to specific room
ws.broadcast_message({'type': 'update'}, room='chat-room')
```

### Development Tools

```python
from newui.devtools import init_debugger

# Enable debugging
debugger = init_debugger(app, enabled=True)

# In templates
{{ debug_code | safe }}  # Inject debug client code
```

## 🛠️ Development

### Project Structure
```
flask-newui/
├── newui/                 # Core framework
│   ├── __init__.py       # Main NewUI class
│   ├── components.py     # Built-in components
│   ├── composition.py    # Component composition
│   ├── devtools.py       # Development tools
│   ├── routing.py        # Route-based code splitting
│   ├── stores.py         # State management
│   ├── websocket.py      # WebSocket support
│   ├── cli.py           # Command line interface
│   ├── core/            # Core modules
│   │   ├── ajax.py      # AJAX handling
│   │   ├── components.py # Component system
│   │   ├── renderer.py   # Template rendering
│   │   └── state.py     # State management
│   └── static/          # Static assets
│       ├── newui.js     # Core JavaScript
│       └── newui.css    # Default styles
├── examples/             # Example applications
├── docs/                # Documentation
├── tests/               # Test suite
└── setup.py            # Package configuration
```

### Running Examples

```bash
# Install with examples
pip install flask-newui[examples]

# Run todo application
python examples/todo_app.py

# Run modern Tailwind CSS dashboard
python examples/tailwind_modern_ui.py

# Run real-time chat example
python examples/realtime_chat.py

# Run development tools demo
python examples/debug_tools.py
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python -m pytest tests/ -v`
5. Submit a pull request

## 📖 Documentation

- **[Getting Started Guide](docs/getting-started.md)** - Detailed setup and usage
- **[Component Reference](docs/components.md)** - Complete component documentation  
- **[State Management](docs/state-management.md)** - Advanced state patterns
- **[WebSocket Guide](docs/websockets.md)** - Real-time features
- **[Migration Guide](docs/migration.md)** - Moving from vanilla Flask
- **[Best Practices](docs/best-practices.md)** - Recommended patterns

## 🤝 Community

- **GitHub**: [smbrandonjr/flask-newui](https://github.com/smbrandonjr/flask-newui)
- **Issues**: [Report bugs or request features](https://github.com/smbrandonjr/flask-newui/issues)
- **Discussions**: [Community discussions](https://github.com/smbrandonjr/flask-newui/discussions)

## 💝 Support the Project

If Flask-NewUI has helped you build amazing applications, consider supporting its continued development:

**Bitcoin**: `3DEMZi7sx1ZJWwGi8jzq3yqevGoyczFn9X`

Your contributions help maintain and improve this open-source project. Thank you for your support! 🙏

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⭐ Why NewUI?

**For Flask Developers:**
- Familiar Jinja2 syntax with reactive enhancements
- No need to learn a completely new framework
- Gradual adoption - use as much or as little as needed
- Maintains Flask's simplicity and patterns

**For Modern Development:**
- Component-based architecture
- Real-time updates with WebSockets
- State management for complex UIs
- Development tools for debugging
- AI Framework Schema for expert AI assistance

**For Production:**
- Progressive enhancement ensures accessibility
- Server-side rendering for SEO
- Works without JavaScript for core functionality
- Easy deployment with existing Flask infrastructure

---

**Get started today and transform your Flask applications with modern UI capabilities!**