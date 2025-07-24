# Getting Started with NewUI Framework

## Installation

### Basic Installation

```bash
pip install flask-newui
```

### Installation with Optional Features

```bash
# WebSocket support
pip install flask-newui[websocket]

# Development tools
pip install flask-newui[dev]

# All features
pip install flask-newui[all]
```

## Your First NewUI Application

### 1. Basic Setup

Create a new Python file `app.py`:

```python
from flask import Flask, render_template_string
from newui import NewUI
from newui import components as ui

app = Flask(__name__)
newui = NewUI(app)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>My NewUI App</title>
        <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Welcome to NewUI!</h1>
            {{ ui.button("Click Me!", onclick="sayHello", class_="btn btn-primary") }}
        </div>
        
        <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
        <script>
            NewUI.registerHandler('sayHello', function(element, event) {
                alert('Hello from NewUI!');
            });
        </script>
    </body>
    </html>
    ''', ui=ui)

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. Run Your Application

```bash
python app.py
```

Visit `http://localhost:5000` to see your NewUI application!

## Core Concepts

### Components

NewUI provides built-in components that generate HTML with reactive capabilities:

```python
# Import components
from newui import components as ui

# Use in templates
{{ ui.button("Save", onclick="save") }}
{{ ui.input("email", type="email", placeholder="Enter email") }}
{{ ui.card("Content here", title="My Card") }}
```

### State Management

Components can maintain state that automatically syncs between client and server:

```html
<!-- Component with state -->
<div data-ui-component="counter" data-ui-state='{"count": 0}'>
    <p>Count: <span data-ui-bind="count">0</span></p>
    {{ ui.button("Increment", onclick="increment") }}
</div>

<script>
NewUI.registerHandler('increment', function(element, event) {
    const componentId = NewUI.getComponentId(element);
    const state = NewUI.state[componentId];
    NewUI.setStateValue(componentId, 'count', (state.count || 0) + 1);
});
</script>
```

### Event Handling

Register JavaScript handlers for UI interactions:

```javascript
// Register handler
NewUI.registerHandler('myHandler', function(element, event) {
    // Your code here
});

// Use in HTML
{{ ui.button("Click", onclick="myHandler") }}
```

### AJAX Integration

NewUI automatically handles AJAX requests and partial page updates:

```html
<!-- AJAX form -->
<form data-ui-submit="ajax:/api/save">
    {{ ui.input("name", placeholder="Name") }}
    {{ ui.button("Save", type="submit") }}
</form>
```

```python
@app.route('/api/save', methods=['POST'])
def save():
    # Process form data
    name = request.form.get('name')
    # Return JSON or partial HTML
    return jsonify({'status': 'success', 'message': f'Hello {name}!'})
```

## Building a Todo Application

Let's build a complete todo application to demonstrate NewUI's capabilities:

### Step 1: Application Structure

```python
from flask import Flask, render_template_string, request, jsonify
from newui import NewUI
from newui import components as ui

app = Flask(__name__)
newui = NewUI(app)

# In-memory storage (use database in production)
todos = [
    {'id': 1, 'text': 'Learn NewUI', 'completed': False},
    {'id': 2, 'text': 'Build awesome app', 'completed': False}
]
next_id = 3
```

### Step 2: Main Route

```python
@app.route('/')
def index():
    return render_template_string(TODO_TEMPLATE, ui=ui, todos=todos)
```

### Step 3: Template with Reactive Components

```python
TODO_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Todo App</title>
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Todo Application</h1>
        
        <!-- Todo Form -->
        <div data-ui-component="todo-form" data-ui-state='{"text": ""}'>
            <form data-ui-submit="addTodo" class="mb-4">
                <div class="input-group">
                    {{ ui.input("text", placeholder="Add new todo...", bind="text", required=True) }}
                    {{ ui.button("Add Todo", type="submit", class_="btn btn-primary") }}
                </div>
            </form>
        </div>
        
        <!-- Todo List -->
        <div data-ui-component="todo-list" data-ui-state='{"todos": {{ todos | tojson }}}'>
            <div id="todo-items">
                <!-- Todos will be rendered here -->
            </div>
            
            <div class="mt-3">
                <small class="text-muted">
                    Total: <span data-ui-bind="todos.length">{{ todos | length }}</span> items
                </small>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Add todo handler
        NewUI.registerHandler('addTodo', function(element, event) {
            const formData = new FormData(element);
            const text = formData.get('text').trim();
            
            if (!text) return;
            
            fetch('/api/todos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            })
            .then(response => response.json())
            .then(todo => {
                // Add to state
                const listComponent = document.querySelector('[data-ui-component="todo-list"]');
                const componentId = listComponent.getAttribute('data-ui-id');
                const state = NewUI.state[componentId];
                
                NewUI.setStateValue(componentId, 'todos', [...state.todos, todo]);
                
                // Clear form
                const formComponent = document.querySelector('[data-ui-component="todo-form"]');
                const formId = formComponent.getAttribute('data-ui-id');
                NewUI.setStateValue(formId, 'text', '');
                element.reset();
                
                renderTodos();
            });
        });
        
        // Toggle todo completion
        function toggleTodo(id) {
            fetch(`/api/todos/${id}/toggle`, {method: 'PUT'})
            .then(response => response.json())
            .then(todo => {
                const listComponent = document.querySelector('[data-ui-component="todo-list"]');
                const componentId = listComponent.getAttribute('data-ui-id');
                const state = NewUI.state[componentId];
                
                const newTodos = state.todos.map(t => 
                    t.id === id ? {...t, completed: todo.completed} : t
                );
                
                NewUI.setStateValue(componentId, 'todos', newTodos);
                renderTodos();
            });
        }
        
        // Delete todo
        function deleteTodo(id) {
            fetch(`/api/todos/${id}`, {method: 'DELETE'})
            .then(() => {
                const listComponent = document.querySelector('[data-ui-component="todo-list"]');
                const componentId = listComponent.getAttribute('data-ui-id');
                const state = NewUI.state[componentId];
                
                const newTodos = state.todos.filter(t => t.id !== id);
                NewUI.setStateValue(componentId, 'todos', newTodos);
                renderTodos();
            });
        }
        
        // Render todos
        function renderTodos() {
            const listComponent = document.querySelector('[data-ui-component="todo-list"]');
            const componentId = listComponent.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            const container = document.getElementById('todo-items');
            
            container.innerHTML = state.todos.map(todo => `
                <div class="card mb-2">
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" 
                                   ${todo.completed ? 'checked' : ''}
                                   onchange="toggleTodo(${todo.id})">
                            <label class="form-check-label ${todo.completed ? 'text-decoration-line-through text-muted' : ''}">
                                ${todo.text}
                            </label>
                        </div>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTodo(${todo.id})">
                            Delete
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', renderTodos);
    </script>
</body>
</html>
'''
```

### Step 4: API Routes

```python
@app.route('/api/todos', methods=['POST'])
def add_todo():
    global next_id
    data = request.json
    todo = {
        'id': next_id,
        'text': data['text'],
        'completed': False
    }
    todos.append(todo)
    next_id += 1
    return jsonify(todo)

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PUT'])
def toggle_todo(todo_id):
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo:
        todo['completed'] = not todo['completed']
        return jsonify(todo)
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [t for t in todos if t['id'] != todo_id]
    return jsonify({'status': 'deleted'})

if __name__ == '__main__':
    app.run(debug=True)
```

This complete todo application demonstrates:

- **Component-based architecture** with separate form and list components
- **State management** with automatic UI updates
- **AJAX integration** for seamless user experience
- **Event handling** with NewUI's declarative approach
- **Progressive enhancement** - works without JavaScript for basic functionality

## Next Steps

1. **Explore Examples**: Check out the `examples/` directory for more advanced patterns
2. **Read the Documentation**: Dive deeper into specific features
3. **Add Real-time Features**: Integrate WebSockets for live updates
4. **Build Complex UIs**: Use state stores and component composition
5. **Debug and Optimize**: Use NewUI's development tools

## Common Patterns

### Form Handling with Validation

```python
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Validate and process form
        errors = validate_contact_form(request.form)
        if not errors:
            # Save and redirect
            return jsonify({'status': 'success', 'redirect': '/thank-you'})
        else:
            return jsonify({'status': 'error', 'errors': errors})
    
    return render_template('contact.html')
```

### Modal Components

```html
<!-- Modal trigger -->
{{ ui.button("Open Modal", onclick="openModal", data_target="#my-modal") }}

<!-- Modal -->
{{ ui.modal(
    content="<p>Modal content here</p>",
    title="My Modal",
    id="my-modal"
) }}
```

### List Updates with Animations

```javascript
NewUI.registerHandler('updateList', function(element, event) {
    const componentId = NewUI.getComponentId(element);
    
    // Add CSS transition classes before updating
    const items = document.querySelectorAll('.list-item');
    items.forEach(item => item.classList.add('fade-out'));
    
    setTimeout(() => {
        NewUI.setStateValue(componentId, 'items', newItems);
        renderList();
        
        // Add fade-in animation
        requestAnimationFrame(() => {
            document.querySelectorAll('.list-item').forEach(item => {
                item.classList.add('fade-in');
            });
        });
    }, 200);
});
```

Start building with NewUI and experience the power of reactive Flask development!