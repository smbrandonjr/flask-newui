"""
Example application demonstrating NewUI list rendering with efficient updates
"""

from flask import Flask, render_template_string, jsonify, request
from newui import NewUI
from newui import components as ui
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'
newui = NewUI(app)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI List Rendering Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    <style>
        .todo-item {
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .todo-item[data-completed="true"] {
            opacity: 0.6;
        }
        .todo-item[data-completed="true"] span {
            text-decoration: line-through;
        }
        .user-card {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background: white;
        }
        .ui-list-empty {
            text-align: center;
            color: #6c757d;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>List Rendering Demo</h1>
        
        <div data-ui-component="demo" id="main-component" data-ui-id="list-demo" 
             data-ui-state='{{ initial_state | tojson }}'>
            
            <div class="row">
                <div class="col-md-6">
                    <h3>Todo List Example</h3>
                    
                    <div class="mb-3">
                        <div class="input-group">
                            {{ ui.input(name="new_todo", model="newTodo", 
                                      placeholder="Enter new todo...", class_="form-control") }}
                            <button class="btn btn-primary" data-ui-click="addTodo">Add Todo</button>
                        </div>
                    </div>
                    
                    <h5>Filter:</h5>
                    <div class="btn-group mb-3" role="group">
                        <button class="btn btn-outline-secondary" data-ui-click="filterAll">All</button>
                        <button class="btn btn-outline-secondary" data-ui-click="filterActive">Active</button>
                        <button class="btn btn-outline-secondary" data-ui-click="filterCompleted">Completed</button>
                    </div>
                    
                    <!-- List rendering with template -->
                    {% set todo_template = '''
                        <div class="todo-item" data-completed="{completed}">
                            <div>
                                <input type="checkbox" 
                                       data-checked="{completed}"
                                       data-ui-click="toggleTodo" data-todo-id="{id}">
                                <span>{text}</span>
                            </div>
                            <button class="btn btn-sm btn-danger" 
                                    data-ui-click="removeTodo" data-todo-id="{id}">
                                Remove
                            </button>
                        </div>
                    ''' %}
                    <div id="todo-list-container">
                        {{ ui.for_each("filteredTodos", 
                            template=todo_template,
                            key="id",
                            empty_message="No todos match the current filter."
                        ) }}
                    </div>
                    
                    <div class="mt-3">
                        <small class="text-muted">
                            <span data-ui-bind="todoStats.active"></span> active, 
                            <span data-ui-bind="todoStats.completed"></span> completed
                        </small>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <h3>Dynamic User List</h3>
                    
                    <div class="mb-3">
                        <button class="btn btn-success" data-ui-click="addUser">Add Random User</button>
                        <button class="btn btn-warning" data-ui-click="shuffleUsers">Shuffle Users</button>
                        <button class="btn btn-danger" data-ui-click="clearUsers">Clear All</button>
                    </div>
                    
                    <!-- List with more complex template -->
                    {% set user_template = '''
                        <div class="user-card">
                            <h5>{name}</h5>
                            <p class="mb-1">Email: {email}</p>
                            <p class="mb-1">Role: {role}</p>
                            <p class="mb-0">
                                <small class="text-muted">ID: {id}</small>
                            </p>
                            <button class="btn btn-sm btn-outline-danger mt-2" 
                                    data-ui-click="removeUser" data-user-id="{id}">
                                Remove
                            </button>
                        </div>
                    ''' %}
                    {{ ui.for_each("users",
                        template=user_template,
                        key="id",
                        empty_message="No users in the list."
                    ) }}
                </div>
            </div>
            
            <hr>
            
            <div class="row">
                <div class="col-12">
                    <h3>Nested Lists Example</h3>
                    
                    {% set category_template = '''
                        <div class="mb-4">
                            <h4>{name}</h4>
                            <div class="ms-3">
                                <ul>
                                    <!-- Items would be rendered here in a real nested list -->
                                    <li>Items count: {items.length}</li>
                                </ul>
                            </div>
                        </div>
                    ''' %}
                    {{ ui.for_each("categories",
                        template=category_template,
                        key="id"
                    ) }}
                </div>
            </div>
            
            <hr>
            
            <div class="row">
                <div class="col-12">
                    <h4>State Debug</h4>
                    <pre class="bg-light p-3" id="state-debug"></pre>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Register event handlers
        NewUI.registerHandler('addTodo', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            const newTodo = state.newTodo?.trim();
            
            if (newTodo) {
                if (!state.todos) state.todos = [];
                state.todos.push({
                    id: Date.now(),
                    text: newTodo,
                    completed: false
                });
                NewUI.setStateValue(componentId, 'newTodo', '');
                updateTodoStats(componentId);
            }
        });
        
        NewUI.registerHandler('removeTodo', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const todoId = parseInt(element.getAttribute('data-todo-id'));
            const state = NewUI.state[componentId];
            
            if (state && state.todos && !isNaN(todoId)) {
                const index = state.todos.findIndex(t => t.id === todoId);
                if (index !== -1) {
                    state.todos.splice(index, 1);
                    updateTodoStats(componentId);
                }
            }
        });
        
        NewUI.registerHandler('toggleTodo', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const todoId = parseInt(element.getAttribute('data-todo-id'));
            const state = NewUI.state[componentId];
            
            if (state && state.todos && !isNaN(todoId)) {
                const todo = state.todos.find(t => t.id === todoId);
                if (todo) {
                    todo.completed = !todo.completed;
                    updateTodoStats(componentId);
                }
            }
        });
        
        NewUI.registerHandler('filterAll', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.setStateValue(componentId, 'filter', 'all');
            applyTodoFilter(componentId);
        });
        
        NewUI.registerHandler('filterActive', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.setStateValue(componentId, 'filter', 'active');
            applyTodoFilter(componentId);
        });
        
        NewUI.registerHandler('filterCompleted', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.setStateValue(componentId, 'filter', 'completed');
            applyTodoFilter(componentId);
        });
        
        // User handlers
        NewUI.registerHandler('addUser', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            
            if (!state.users) state.users = [];
            
            const names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'];
            const roles = ['Admin', 'User', 'Guest', 'Moderator'];
            const randomName = names[Math.floor(Math.random() * names.length)];
            const randomRole = roles[Math.floor(Math.random() * roles.length)];
            
            state.users.push({
                id: Date.now() + Math.random(),
                name: randomName + ' ' + (state.users.length + 1),
                email: randomName.toLowerCase() + state.users.length + '@example.com',
                role: randomRole
            });
            
            NewUI.updateLists(componentId, 'users');
        });
        
        NewUI.registerHandler('removeUser', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const userId = parseFloat(element.getAttribute('data-user-id'));
            const state = NewUI.state[componentId];
            
            if (state && state.users) {
                const index = state.users.findIndex(u => u.id === userId);
                if (index !== -1) {
                    state.users.splice(index, 1);
                    NewUI.updateLists(componentId, 'users');
                }
            }
        });
        
        NewUI.registerHandler('shuffleUsers', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            
            if (state.users && state.users.length > 0) {
                // Fisher-Yates shuffle
                for (let i = state.users.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [state.users[i], state.users[j]] = [state.users[j], state.users[i]];
                }
                NewUI.updateLists(componentId, 'users');
            }
        });
        
        NewUI.registerHandler('clearUsers', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.setStateValue(componentId, 'users', []);
        });
        
        // Helper functions
        function updateTodoStats(componentId) {
            const state = NewUI.state[componentId];
            const todos = state.todos || [];
            const active = todos.filter(t => !t.completed).length;
            const completed = todos.filter(t => t.completed).length;
            
            NewUI.setStateValue(componentId, 'todoStats', { active, completed });
            
            // Also update filtered todos
            applyTodoFilter(componentId);
        }
        
        function applyTodoFilter(componentId) {
            const state = NewUI.state[componentId];
            const todos = state.todos || [];
            const filter = state.filter || 'all';
            
            let filtered = todos;
            if (filter === 'active') {
                filtered = todos.filter(t => !t.completed);
            } else if (filter === 'completed') {
                filtered = todos.filter(t => t.completed);
            }
            
            NewUI.setStateValue(componentId, 'filteredTodos', filtered);
        }
        
        // Update debug view
        function updateDebug() {
            const state = NewUI.state['list-demo'] || {};
            document.getElementById('state-debug').textContent = JSON.stringify(state, null, 2);
        }
        
        // Initial setup
        setTimeout(() => {
            updateTodoStats('list-demo');
            updateDebug();
        }, 100);
        
        // Update debug on any change
        setInterval(updateDebug, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    todos = [
        {'id': 1, 'text': 'Learn NewUI', 'completed': True},
        {'id': 2, 'text': 'Build an app', 'completed': False},
        {'id': 3, 'text': 'Deploy to production', 'completed': False}
    ]
    
    initial_state = {
        'newTodo': '',
        'filter': 'all',
        'todos': todos,
        'filteredTodos': todos,  # Initially show all todos
        'todoStats': {'active': 2, 'completed': 1},
        'users': [
            {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'role': 'Admin'},
            {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'role': 'User'}
        ],
        'categories': [
            {
                'id': 1,
                'name': 'Electronics',
                'items': [
                    {'name': 'Laptop', 'price': 999},
                    {'name': 'Phone', 'price': 699}
                ]
            },
            {
                'id': 2,
                'name': 'Books',
                'items': [
                    {'name': 'Python Guide', 'price': 29},
                    {'name': 'Web Development', 'price': 39}
                ]
            }
        ]
    }
    
    return render_template_string(TEMPLATE, 
                                initial_state=initial_state,
                                ui=ui)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("List Rendering Demo")
    print("="*50)
    print("Open http://localhost:5005")
    print("Features:")
    print("- Add/remove todos with keyed updates")
    print("- Dynamic user list with shuffle")
    print("- Nested lists demonstration")
    print("="*50 + "\n")
    app.run(debug=True, port=5005)