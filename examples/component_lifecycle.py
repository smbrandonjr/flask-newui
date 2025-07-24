"""
Example application demonstrating NewUI component lifecycle hooks
"""

from flask import Flask, render_template_string, jsonify
from newui import NewUI
from newui import components as ui

app = Flask(__name__)
app.secret_key = 'your-secret-key'
newui = NewUI(app)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Component Lifecycle Hooks Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    <style>
        .lifecycle-log {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        .log-entry {
            padding: 2px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .log-init { color: #28a745; }
        .log-mounted { color: #007bff; }
        .log-update { color: #ffc107; }
        .log-destroy { color: #dc3545; }
        .timer-display {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>Component Lifecycle Hooks Demo</h1>
        
        <div class="row">
            <div class="col-md-6">
                <h3>Timer Component</h3>
                <p>This component demonstrates all lifecycle hooks.</p>
                
                <div data-ui-component="timer" 
                     data-ui-state='{"count": 0, "interval": null, "running": false}'
                     data-ui-hooks="init,mounted,beforeUpdate,updated,beforeDestroy,destroyed">
                    <div class="timer-display">
                        <span data-ui-bind="count">0</span>
                    </div>
                    <div class="text-center">
                        <button class="btn btn-success" data-ui-click="startTimer">Start</button>
                        <button class="btn btn-warning" data-ui-click="stopTimer">Stop</button>
                        <button class="btn btn-primary" data-ui-click="resetTimer">Reset</button>
                        <button class="btn btn-danger" data-ui-click="destroyTimer">Destroy Component</button>
                    </div>
                </div>
                
                <hr>
                
                <h3>Dynamic Components</h3>
                <button class="btn btn-primary mb-3" data-ui-click="addComponent">Add Component</button>
                
                <div id="dynamic-components"></div>
            </div>
            
            <div class="col-md-6">
                <h3>Lifecycle Event Log</h3>
                <button class="btn btn-sm btn-secondary mb-2" onclick="clearLog()">Clear Log</button>
                <div id="lifecycle-log" class="lifecycle-log"></div>
                
                <hr>
                
                <h3>State Monitor</h3>
                <div data-ui-component="monitor" 
                     data-ui-state='{"watching": "timer"}'>
                    <p>Monitoring component: <strong data-ui-bind="watching"></strong></p>
                    <pre id="state-display" class="bg-light p-3"></pre>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Lifecycle log helper
        function logLifecycle(componentName, hookName, details = '') {
            const log = document.getElementById('lifecycle-log');
            const entry = document.createElement('div');
            entry.className = 'log-entry log-' + hookName.toLowerCase();
            const timestamp = new Date().toLocaleTimeString();
            entry.textContent = `[${timestamp}] ${componentName}.${hookName}() ${details}`;
            log.insertBefore(entry, log.firstChild);
        }
        
        function clearLog() {
            document.getElementById('lifecycle-log').innerHTML = '';
        }
        
        // Register lifecycle hooks for timer component
        NewUI.registerLifecycle('timer', {
            init: function(element, state) {
                logLifecycle('timer', 'init', '- Component initializing');
                // Set up any initial data
            },
            
            mounted: function(element, state) {
                logLifecycle('timer', 'mounted', '- Component mounted to DOM');
                // Component is now in the DOM
            },
            
            beforeUpdate: function(element, data) {
                logLifecycle('timer', 'beforeUpdate', 
                    `- ${data.changedPath}: ${data.oldValue} → ${data.newValue}`);
                // Can return false to prevent update
            },
            
            updated: function(element, data) {
                logLifecycle('timer', 'updated', 
                    `- ${data.changedPath} updated`);
                // DOM has been updated
                updateStateDisplay();
            },
            
            beforeDestroy: function(element, state) {
                logLifecycle('timer', 'beforeDestroy', '- Cleaning up...');
                // Clean up intervals
                if (state.interval) {
                    clearInterval(state.interval);
                }
            },
            
            destroyed: function(element, state) {
                logLifecycle('timer', 'destroyed', '- Component removed');
            }
        });
        
        // Timer handlers
        NewUI.registerHandler('startTimer', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            
            if (!state.running) {
                const interval = setInterval(() => {
                    NewUI.setStateValue(componentId, 'count', state.count + 1);
                }, 1000);
                
                NewUI.setStateValue(componentId, 'interval', interval);
                NewUI.setStateValue(componentId, 'running', true);
            }
        });
        
        NewUI.registerHandler('stopTimer', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            
            if (state.interval) {
                clearInterval(state.interval);
                NewUI.setStateValue(componentId, 'interval', null);
                NewUI.setStateValue(componentId, 'running', false);
            }
        });
        
        NewUI.registerHandler('resetTimer', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.setStateValue(componentId, 'count', 0);
        });
        
        NewUI.registerHandler('destroyTimer', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.destroyComponent(componentId);
        });
        
        // Dynamic component management
        let componentCounter = 0;
        
        NewUI.registerHandler('addComponent', function(element, event) {
            componentCounter++;
            const container = document.getElementById('dynamic-components');
            const componentId = 'dynamic-' + componentCounter;
            
            const componentHtml = `
                <div data-ui-component="dynamic" 
                     data-ui-id="${componentId}"
                     data-ui-state='{"id": ${componentCounter}, "value": 0}'
                     class="card mb-2">
                    <div class="card-body">
                        <h5>Component #<span data-ui-bind="id"></span></h5>
                        <p>Value: <span data-ui-bind="value"></span></p>
                        <button class="btn btn-sm btn-primary" data-ui-click="increment">+1</button>
                        <button class="btn btn-sm btn-danger" data-ui-click="removeComponent">Remove</button>
                    </div>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', componentHtml);
            
            // Initialize the new component
            const newElement = container.lastElementChild;
            NewUI.initializeComponents();
            
            // Register lifecycle for dynamic components
            NewUI.registerLifecycle('dynamic', {
                init: function(element, state) {
                    logLifecycle('dynamic', 'init', `- Component #${state.id}`);
                },
                mounted: function(element, state) {
                    logLifecycle('dynamic', 'mounted', `- Component #${state.id}`);
                },
                beforeDestroy: function(element, state) {
                    logLifecycle('dynamic', 'beforeDestroy', `- Component #${state.id}`);
                },
                destroyed: function(element, state) {
                    logLifecycle('dynamic', 'destroyed', `- Component #${state.id}`);
                }
            });
        });
        
        NewUI.registerHandler('increment', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            NewUI.setStateValue(componentId, 'value', state.value + 1);
        });
        
        NewUI.registerHandler('removeComponent', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            NewUI.destroyComponent(componentId);
        });
        
        // State display update
        function updateStateDisplay() {
            const timerState = NewUI.state[Object.keys(NewUI.state).find(key => key.includes('timer'))] || {};
            document.getElementById('state-display').textContent = JSON.stringify(timerState, null, 2);
        }
        
        // Initial state display
        setTimeout(updateStateDisplay, 100);
        
        // Log initial page load
        logLifecycle('page', 'load', '- Demo started');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Component Lifecycle Hooks Demo")
    print("="*50)
    print("Open http://localhost:5006")
    print("Features:")
    print("- Timer component with all lifecycle hooks")
    print("- Dynamic component creation/destruction")
    print("- Lifecycle event logging")
    print("- State monitoring")
    print("="*50 + "\n")
    app.run(debug=True, port=5006)