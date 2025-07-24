"""
Example application demonstrating NewUI development tools - debugger and component inspector
"""

from flask import Flask, render_template_string, request, jsonify
from newui import NewUI
from newui import components as ui
from newui.devtools import init_debugger
import time
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.debug = True  # Enable debug mode to show debug tools
newui = NewUI(app)

# Initialize debugger
debugger = init_debugger(app, enabled=True)

# Sample data for the demo
SAMPLE_TASKS = [
    {'id': 1, 'title': 'Design new homepage', 'completed': False, 'priority': 'high', 'assigned_to': 'Alice'},
    {'id': 2, 'title': 'Fix login bug', 'completed': True, 'priority': 'urgent', 'assigned_to': 'Bob'},
    {'id': 3, 'title': 'Update documentation', 'completed': False, 'priority': 'medium', 'assigned_to': 'Charlie'},
    {'id': 4, 'title': 'Code review', 'completed': False, 'priority': 'low', 'assigned_to': 'Alice'},
]

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Development Tools Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    <style>
        .demo-section {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            background: white;
        }
        .component-demo {
            border: 2px dashed #007bff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background: #f8f9fa;
            position: relative;
        }
        .component-demo::before {
            content: attr(data-demo-name);
            position: absolute;
            top: -10px;
            left: 10px;
            background: #007bff;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }
        .task-item {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
            background: white;
            transition: all 0.2s ease;
        }
        .task-item:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .task-item.completed {
            background: #f8f9fa;
            opacity: 0.7;
        }
        .priority-badge {
            font-size: 11px;
            padding: 2px 6px;
        }
        .priority-urgent { background: #dc3545; }
        .priority-high { background: #fd7e14; }
        .priority-medium { background: #ffc107; color: #000; }
        .priority-low { background: #6c757d; }
        
        .stats-widget {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 10px 0;
        }
        .stats-number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1001;
            min-width: 300px;
        }
        
        .debug-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 12px;
        }
        
        .performance-test {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }
        
        .slow-component {
            /* Intentionally slow animation for performance testing */
            animation: slowPulse 3s infinite;
        }
        
        @keyframes slowPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-md-8">
                <h1>Development Tools Demo</h1>
                <p class="text-muted">Interactive debugging and component inspection</p>
                
                <div class="alert alert-info">
                    <strong>🐛 Debug Mode Active!</strong> 
                    Look for the debug button in the bottom-right corner to open the debug panel.
                    All component interactions are being monitored and logged.
                </div>
            </div>
            <div class="col-md-4">
                <div class="stats-widget" data-ui-component="StatsWidget" 
                     data-ui-state='{"active_tasks": 3, "completed_tasks": 1, "total_users": 3}'>
                    <div class="stats-number" data-ui-bind="active_tasks">3</div>
                    <div>Active Tasks</div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>Task Manager Component</h3>
                    <p>A complex component with state management and user interactions</p>
                    
                    <div class="component-demo" data-demo-name="TaskManager">
                        <div data-ui-component="TaskManager" 
                             data-ui-state='{"tasks": {{ tasks | tojson }}, "filter": "all", "new_task_title": ""}'>
                            
                            <!-- Task Creation Form -->
                            <form data-ui-submit="addTask" class="mb-4">
                                <div class="input-group">
                                    {{ ui.input("new_task", placeholder="Enter new task...", 
                                              bind="new_task_title", required=True) }}
                                    <select name="priority" class="form-select">
                                        <option value="low">Low</option>
                                        <option value="medium" selected>Medium</option>
                                        <option value="high">High</option>
                                        <option value="urgent">Urgent</option>
                                    </select>
                                    <button class="btn btn-primary" type="submit">Add Task</button>
                                </div>
                            </form>
                            
                            <!-- Task Filters -->
                            <div class="mb-3">
                                <div class="btn-group" role="group">
                                    <button class="btn btn-outline-secondary" data-ui-click="setFilter" data-filter="all">
                                        All (<span id="count-all">4</span>)
                                    </button>
                                    <button class="btn btn-outline-success" data-ui-click="setFilter" data-filter="active">
                                        Active (<span id="count-active">3</span>)
                                    </button>
                                    <button class="btn btn-outline-primary" data-ui-click="setFilter" data-filter="completed">
                                        Completed (<span id="count-completed">1</span>)
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Task List -->
                            <div id="task-list">
                                <!-- Tasks will be rendered here by JavaScript -->
                            </div>
                            
                            <!-- Bulk Actions -->
                            <div class="mt-3">
                                <button class="btn btn-success btn-sm" data-ui-click="completeAllTasks">
                                    Complete All
                                </button>
                                <button class="btn btn-warning btn-sm ms-2" data-ui-click="clearCompleted">
                                    Clear Completed
                                </button>
                                <button class="btn btn-info btn-sm ms-2" data-ui-click="shuffleTasks">
                                    Shuffle Tasks
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>Performance Test Components</h3>
                    <p>Components designed to test performance monitoring</p>
                    
                    <div class="component-demo" data-demo-name="PerformanceTest">
                        <!-- Counter Component -->
                        <div data-ui-component="CounterComponent" 
                             data-ui-state='{"count": 0, "auto_increment": false}'>
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="display-4" data-ui-bind="count">0</h2>
                                    <div class="btn-group">
                                        <button class="btn btn-danger" data-ui-click="decrementCounter">-</button>
                                        <button class="btn btn-success" data-ui-click="incrementCounter">+</button>
                                        <button class="btn btn-info" data-ui-click="toggleAutoIncrement">Auto</button>
                                        <button class="btn btn-warning" data-ui-click="resetCounter">Reset</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Slow Component (for performance testing) -->
                        <div class="mt-3">
                            <div data-ui-component="SlowComponent" 
                                 data-ui-state='{"render_delay": 100, "enabled": false}'
                                 class="performance-test">
                                <h5>Slow Rendering Component</h5>
                                <p>This component intentionally has slow render times for debugging.</p>
                                <div class="form-check">
                                    {{ ui.checkbox("slow_enabled", "Enable Slow Rendering", 
                                                 bind="enabled", id="slow-checkbox") }}
                                </div>
                                <div class="mt-2">
                                    <label>Render Delay: <span data-ui-bind="render_delay">100</span>ms</label>
                                    <input type="range" class="form-range" min="50" max="500" step="50" 
                                           data-ui-bind="render_delay" data-ui-change="updateDelay">
                                </div>
                                <div class="slow-component mt-2" data-ui-show="enabled">
                                    <div class="alert alert-warning">
                                        ⚠️ Slow rendering is active! Check the performance tab in debug tools.
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="demo-section">
                    <h3>Error Testing</h3>
                    <p>Test error handling and logging</p>
                    
                    <div class="component-demo" data-demo-name="ErrorTesting">
                        <div data-ui-component="ErrorComponent" data-ui-state='{}'>
                            <div class="btn-group-vertical w-100">
                                <button class="btn btn-outline-danger" data-ui-click="triggerError">
                                    Trigger JavaScript Error
                                </button>
                                <button class="btn btn-outline-warning" data-ui-click="triggerWarning">
                                    Trigger Warning
                                </button>
                                <button class="btn btn-outline-info" data-ui-click="triggerLongTask">
                                    Trigger Long Task (Performance)
                                </button>
                                <button class="btn btn-outline-secondary" data-ui-click="triggerMemoryLeak">
                                    Simulate Memory Issues
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>Debug Information</h3>
                    <p>Real-time debug information and component state</p>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <h5>Component Registry</h5>
                            <div class="debug-info" id="component-registry">
                                Loading...
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5>Performance Metrics</h5>
                            <div class="debug-info" id="performance-metrics">
                                Loading...
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5>Recent State Changes</h5>
                            <div class="debug-info" id="state-changes">
                                Loading...
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <h5>Debug Tools</h5>
                        <div class="btn-group">
                            <button class="btn btn-primary" onclick="openDebugPanel()">
                                🐛 Open Debug Panel
                            </button>
                            <button class="btn btn-info" onclick="exportDebugData()">
                                📊 Export Debug Data
                            </button>
                            <button class="btn btn-success" onclick="runPerformanceTest()">
                                🚀 Run Performance Test
                            </button>
                            <button class="btn btn-warning" onclick="clearDebugData()">
                                🗑️ Clear Debug Data
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Notification Area -->
    <div class="notification" id="notification" style="display: none;">
        <div class="alert alert-info alert-dismissible fade show" role="alert">
            <span id="notification-text"></span>
            <button type="button" class="btn-close" onclick="hideNotification()"></button>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <!-- Debug client code -->
    <script>
        {{ debug_code | safe }}
    </script>
    
    <script>
        // Application state
        let appState = {
            tasks: {{ tasks | tojson }},
            nextTaskId: 5,
            autoIncrementInterval: null
        };
        
        // Task Manager Handlers
        NewUI.registerHandler('addTask', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            const form = element;
            const formData = new FormData(form);
            
            const title = formData.get('new_task').trim();
            const priority = formData.get('priority');
            
            if (!title) {
                showNotification('Please enter a task title', 'warning');
                return;
            }
            
            const newTask = {
                id: appState.nextTaskId++,
                title: title,
                completed: false,
                priority: priority,
                assigned_to: 'Current User'
            };
            
            appState.tasks.push(newTask);
            NewUI.setStateValue(componentId, 'tasks', appState.tasks);
            NewUI.setStateValue(componentId, 'new_task_title', '');
            
            form.reset();
            renderTasks();
            updateTaskCounts();
            showNotification('Task added successfully!');
        });
        
        NewUI.registerHandler('setFilter', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const filter = element.getAttribute('data-filter');
            
            NewUI.setStateValue(componentId, 'filter', filter);
            
            // Update active button
            document.querySelectorAll('[data-ui-click="setFilter"]').forEach(btn => {
                btn.classList.remove('btn-outline-secondary', 'btn-secondary');
                btn.classList.add('btn-outline-secondary');
            });
            element.classList.remove('btn-outline-secondary');
            element.classList.add('btn-secondary');
            
            renderTasks();
        });
        
        NewUI.registerHandler('completeAllTasks', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            
            appState.tasks.forEach(task => task.completed = true);
            NewUI.setStateValue(componentId, 'tasks', appState.tasks);
            
            renderTasks();
            updateTaskCounts();
            showNotification('All tasks completed!');
        });
        
        NewUI.registerHandler('clearCompleted', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            
            const incompleteTasks = appState.tasks.filter(task => !task.completed);
            appState.tasks = incompleteTasks;
            NewUI.setStateValue(componentId, 'tasks', incompleteTasks);
            
            renderTasks();
            updateTaskCounts();
            showNotification('Completed tasks cleared!');
        });
        
        NewUI.registerHandler('shuffleTasks', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            
            // Shuffle array
            for (let i = appState.tasks.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [appState.tasks[i], appState.tasks[j]] = [appState.tasks[j], appState.tasks[i]];
            }
            
            NewUI.setStateValue(componentId, 'tasks', appState.tasks);
            renderTasks();
            showNotification('Tasks shuffled!');
        });
        
        // Counter Component Handlers
        NewUI.registerHandler('incrementCounter', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            
            NewUI.setStateValue(componentId, 'count', (state.count || 0) + 1);
        });
        
        NewUI.registerHandler('decrementCounter', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            
            NewUI.setStateValue(componentId, 'count', Math.max(0, (state.count || 0) - 1));
        });
        
        NewUI.registerHandler('resetCounter', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.setStateValue(componentId, 'count', 0);
        });
        
        NewUI.registerHandler('toggleAutoIncrement', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            const newAutoState = !state.auto_increment;
            
            NewUI.setStateValue(componentId, 'auto_increment', newAutoState);
            
            if (newAutoState) {
                appState.autoIncrementInterval = setInterval(() => {
                    const currentState = NewUI.state[componentId];
                    if (currentState.auto_increment) {
                        NewUI.setStateValue(componentId, 'count', (currentState.count || 0) + 1);
                    }
                }, 500);
                element.textContent = 'Stop';
                element.classList.remove('btn-info');
                element.classList.add('btn-danger');
            } else {
                if (appState.autoIncrementInterval) {
                    clearInterval(appState.autoIncrementInterval);
                    appState.autoIncrementInterval = null;
                }
                element.textContent = 'Auto';
                element.classList.remove('btn-danger');
                element.classList.add('btn-info');
            }
        });
        
        // Slow Component Handlers
        NewUI.registerHandler('updateDelay', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const delay = parseInt(element.value);
            
            // Simulate slow update
            setTimeout(() => {
                NewUI.setStateValue(componentId, 'render_delay', delay);
            }, delay);
        });
        
        // Error Testing Handlers
        NewUI.registerHandler('triggerError', function(element, event) {
            // Intentionally cause an error for testing
            throw new Error('Test error for debugging purposes');
        });
        
        NewUI.registerHandler('triggerWarning', function(element, event) {
            console.warn('Test warning message for debugging');
            showNotification('Warning logged to console', 'warning');
        });
        
        NewUI.registerHandler('triggerLongTask', function(element, event) {
            // Simulate a long-running task
            const start = performance.now();
            showNotification('Starting long task...', 'info');
            
            // Block the main thread for testing
            setTimeout(() => {
                let sum = 0;
                for (let i = 0; i < 10000000; i++) {
                    sum += Math.random();
                }
                const duration = performance.now() - start;
                console.log('Long task completed in', duration, 'ms, result:', sum);
                showNotification(`Long task completed in ${duration.toFixed(2)}ms`, 'success');
            }, 10);
        });
        
        NewUI.registerHandler('triggerMemoryLeak', function(element, event) {
            // Simulate memory allocation for testing
            const largeArray = new Array(100000).fill(0).map(() => ({
                id: Math.random(),
                data: new Array(100).fill('memory test data')
            }));
            
            console.log('Allocated large array with', largeArray.length, 'items');
            showNotification('Memory allocation test completed', 'info');
            
            // Don't clean up to simulate a "leak" for testing
            window.testMemoryData = largeArray;
        });
        
        // Task rendering functions
        function renderTasks() {
            const taskList = document.getElementById('task-list');
            const componentElement = document.querySelector('[data-ui-component="TaskManager"]');
            const componentId = componentElement.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            const filter = state ? state.filter : 'all';
            
            let filteredTasks = appState.tasks;
            if (filter === 'active') {
                filteredTasks = appState.tasks.filter(task => !task.completed);
            } else if (filter === 'completed') {
                filteredTasks = appState.tasks.filter(task => task.completed);
            }
            
            taskList.innerHTML = filteredTasks.map(task => `
                <div class="task-item ${task.completed ? 'completed' : ''}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="flex-grow-1">
                            <div class="form-check d-inline-block">
                                <input class="form-check-input" type="checkbox" 
                                       id="task-${task.id}" 
                                       ${task.completed ? 'checked' : ''}
                                       onchange="toggleTask(${task.id})">
                                <label class="form-check-label" for="task-${task.id}">
                                    <strong>${task.title}</strong>
                                </label>
                            </div>
                            <br>
                            <small class="text-muted">
                                Assigned to: ${task.assigned_to}
                                <span class="badge priority-badge priority-${task.priority} ms-2">${task.priority.toUpperCase()}</span>
                            </small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-primary" onclick="editTask(${task.id})">Edit</button>
                            <button class="btn btn-sm btn-outline-danger ms-1" onclick="deleteTask(${task.id})">Delete</button>
                        </div>
                    </div>
                </div>
            `).join('');
            
            if (filteredTasks.length === 0) {
                taskList.innerHTML = '<div class="text-center text-muted py-4">No tasks to display</div>';
            }
        }
        
        function toggleTask(taskId) {
            const task = appState.tasks.find(t => t.id === taskId);
            if (task) {
                task.completed = !task.completed;
                
                const componentElement = document.querySelector('[data-ui-component="TaskManager"]');
                const componentId = componentElement.getAttribute('data-ui-id');
                NewUI.setStateValue(componentId, 'tasks', appState.tasks);
                
                renderTasks();
                updateTaskCounts();
                
                const action = task.completed ? 'completed' : 'reopened';
                showNotification(`Task "${task.title}" ${action}!`);
            }
        }
        
        function editTask(taskId) {
            const task = appState.tasks.find(t => t.id === taskId);
            if (task) {
                const newTitle = prompt('Edit task title:', task.title);
                if (newTitle && newTitle.trim()) {
                    task.title = newTitle.trim();
                    
                    const componentElement = document.querySelector('[data-ui-component="TaskManager"]');
                    const componentId = componentElement.getAttribute('data-ui-id');
                    NewUI.setStateValue(componentId, 'tasks', appState.tasks);
                    
                    renderTasks();
                    showNotification('Task updated!');
                }
            }
        }
        
        function deleteTask(taskId) {
            if (confirm('Are you sure you want to delete this task?')) {
                appState.tasks = appState.tasks.filter(t => t.id !== taskId);
                
                const componentElement = document.querySelector('[data-ui-component="TaskManager"]');
                const componentId = componentElement.getAttribute('data-ui-id');
                NewUI.setStateValue(componentId, 'tasks', appState.tasks);
                
                renderTasks();
                updateTaskCounts();
                showNotification('Task deleted!');
            }
        }
        
        function updateTaskCounts() {
            const total = appState.tasks.length;
            const completed = appState.tasks.filter(t => t.completed).length;
            const active = total - completed;
            
            document.getElementById('count-all').textContent = total;
            document.getElementById('count-active').textContent = active;
            document.getElementById('count-completed').textContent = completed;
            
            // Update stats widget
            const statsWidget = document.querySelector('[data-ui-component="StatsWidget"]');
            if (statsWidget) {
                const componentId = statsWidget.getAttribute('data-ui-id');
                NewUI.setStateValue(componentId, 'active_tasks', active);
                NewUI.setStateValue(componentId, 'completed_tasks', completed);
            }
        }
        
        // Debug utility functions
        function openDebugPanel() {
            if (window.NewUIDebug) {
                window.NewUIDebug.openDebugPanel();
            } else {
                alert('Debug tools not available');
            }
        }
        
        function exportDebugData() {
            if (window.NewUIDebug) {
                Promise.all([
                    window.NewUIDebug.getPerformanceData(),
                    fetch('/debug/components').then(r => r.json()),
                    fetch('/debug/state-history').then(r => r.json())
                ]).then(([performance, components, stateHistory]) => {
                    const debugData = {
                        timestamp: new Date().toISOString(),
                        performance,
                        components,
                        stateHistory
                    };
                    
                    const blob = new Blob([JSON.stringify(debugData, null, 2)], {
                        type: 'application/json'
                    });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `newui-debug-${Date.now()}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                    
                    showNotification('Debug data exported!', 'success');
                });
            }
        }
        
        function runPerformanceTest() {
            showNotification('Running performance test...', 'info');
            
            const startTime = performance.now();
            
            // Trigger multiple state updates
            for (let i = 0; i < 50; i++) {
                setTimeout(() => {
                    const counterElement = document.querySelector('[data-ui-component="CounterComponent"]');
                    if (counterElement) {
                        const componentId = counterElement.getAttribute('data-ui-id');
                        const state = NewUI.state[componentId];
                        NewUI.setStateValue(componentId, 'count', (state.count || 0) + 1);
                    }
                }, i * 10);
            }
            
            setTimeout(() => {
                const duration = performance.now() - startTime;
                showNotification(`Performance test completed in ${duration.toFixed(2)}ms`, 'success');
            }, 600);
        }
        
        function clearDebugData() {
            if (confirm('Clear all debug data? This cannot be undone.')) {
                // In a real implementation, this would call an API endpoint
                showNotification('Debug data cleared!', 'warning');
            }
        }
        
        // Update debug information displays
        function updateDebugInfo() {
            // Component Registry
            fetch('/debug/components')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('component-registry').innerHTML = 
                        `Components: ${data.total_components}<br>` +
                        `State Updates: ${data.total_state_updates}<br>` +
                        `Types: ${[...new Set(data.components.map(c => c.type))].join(', ')}`;
                })
                .catch(() => {
                    document.getElementById('component-registry').innerHTML = 'Error loading data';
                });
            
            // Performance Metrics
            fetch('/debug/performance')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('performance-metrics').innerHTML = 
                        `Total Renders: ${data.total_renders}<br>` +
                        `Avg Render Time: ${data.avg_render_time.toFixed(2)}ms<br>` +
                        `Memory Usage: ~${data.memory_usage.estimated_kb}KB`;
                })
                .catch(() => {
                    document.getElementById('performance-metrics').innerHTML = 'Error loading data';
                });
            
            // State Changes
            fetch('/debug/state-history')
                .then(r => r.json())
                .then(data => {
                    const recent = data.history.slice(-3);
                    document.getElementById('state-changes').innerHTML = 
                        recent.map(change => 
                            `${new Date(change.timestamp * 1000).toLocaleTimeString()}: ${change.component_id}`
                        ).join('<br>') || 'No recent changes';
                })
                .catch(() => {
                    document.getElementById('state-changes').innerHTML = 'Error loading data';
                });
        }
        
        // Notification functions
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            const alert = notification.querySelector('.alert');
            const text = document.getElementById('notification-text');
            
            alert.className = `alert alert-${type} alert-dismissible fade show`;
            text.textContent = message;
            notification.style.display = 'block';
            
            setTimeout(() => {
                hideNotification();
            }, 3000);
        }
        
        function hideNotification() {
            document.getElementById('notification').style.display = 'none';
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            renderTasks();
            updateTaskCounts();
            updateDebugInfo();
            
            // Update debug info periodically
            setInterval(updateDebugInfo, 5000);
            
            console.log('Development tools demo initialized');
            console.log('🐛 Debug tools are active - check the debug panel!');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE,
                                ui=ui,
                                tasks=SAMPLE_TASKS,
                                debug_code=debugger.generate_client_debug_code())

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'POST':
        # Add new task
        data = request.json
        new_task = {
            'id': len(SAMPLE_TASKS) + 1,
            'title': data.get('title', ''),
            'completed': False,
            'priority': data.get('priority', 'medium'),
            'assigned_to': data.get('assigned_to', 'Current User')
        }
        SAMPLE_TASKS.append(new_task)
        return jsonify(new_task)
    
    return jsonify(SAMPLE_TASKS)

if __name__ == '__main__':
    print("\\n" + "="*50)
    print("Development Tools Demo")
    print("="*50)
    print("Open http://localhost:5012")
    print("Features:")
    print("- Component inspector with real-time state monitoring")
    print("- Performance profiling and render time analysis")
    print("- Error logging and debugging tools")
    print("- State change history and debugging")
    print("- Interactive debug panel with component tree")
    print("- Client-side debugging with automatic instrumentation")
    print("- Memory usage estimation and leak detection")
    print("- Long task detection and performance warnings")
    print("")
    print("🐛 Look for the debug button in the bottom-right corner!")
    print("="*50 + "\\n")
    app.run(debug=True, port=5012)