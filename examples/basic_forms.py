"""
Simple example to demonstrate and debug two-way data binding
"""

from flask import Flask, render_template_string
from newui import NewUI
from newui import components as ui

app = Flask(__name__)
app.secret_key = 'test-key'
newui = NewUI(app)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Data Binding Test</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Two-Way Data Binding Test</h1>
        
        <div class="alert alert-info">
            <strong>How it works:</strong> Type in any input field and watch all bound elements update in real-time.
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <!-- Component with initial state -->
                <div data-ui-component="demo" data-ui-id="demo1" 
                     data-ui-state='{"user": {"name": "John Doe", "email": "john@example.com"}}'>
                    
                    <h3>Input Fields</h3>
                    
                    <div class="mb-3">
                        <label>Name Input 1:</label>
                        <input type="text" class="form-control" data-ui-model="user.name">
                    </div>
                    
                    <div class="mb-3">
                        <label>Name Input 2 (same binding):</label>
                        <input type="text" class="form-control" data-ui-model="user.name">
                    </div>
                    
                    <div class="mb-3">
                        <label>Email:</label>
                        <input type="email" class="form-control" data-ui-model="user.email">
                    </div>
                    
                    <hr>
                    
                    <h3>Display Bindings</h3>
                    <p>Name: <strong data-ui-bind="user.name" style="color: blue;"></strong></p>
                    <p>Email: <strong data-ui-bind="user.email" style="color: green;"></strong></p>
                    
                    <hr>
                    
                    <h3>Another Name Display:</h3>
                    <div class="alert alert-secondary">
                        Hello, <span data-ui-bind="user.name"></span>!
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <h3>Debug Info</h3>
                <div class="bg-light p-3 rounded">
                    <h5>Component State:</h5>
                    <pre id="state-debug" style="font-size: 12px;"></pre>
                    
                    <h5>Events Log:</h5>
                    <div id="events-log" style="max-height: 200px; overflow-y: auto; font-size: 12px;">
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Debug helpers
        function updateDebug() {
            const state = NewUI.state['demo1'];
            document.getElementById('state-debug').textContent = JSON.stringify(state, null, 2);
        }
        
        function logEvent(msg) {
            const log = document.getElementById('events-log');
            const entry = document.createElement('div');
            entry.textContent = new Date().toISOString().substr(11, 12) + ' - ' + msg;
            log.insertBefore(entry, log.firstChild);
        }
        
        // Initial state display
        setTimeout(() => {
            updateDebug();
            logEvent('Initial state loaded');
        }, 100);
        
        // Log all binding events
        document.addEventListener('input', (e) => {
            if (e.target.hasAttribute('data-ui-model') || e.target.hasAttribute('data-ui-bind')) {
                const binding = e.target.getAttribute('data-ui-model') || e.target.getAttribute('data-ui-bind');
                logEvent(`Input event on ${binding}: "${e.target.value}"`);
                setTimeout(updateDebug, 0);
            }
        });
        
        // Also check NewUI state directly
        setInterval(() => {
            const currentState = NewUI.state['demo1'];
            if (currentState && JSON.stringify(currentState) !== document.getElementById('state-debug').textContent) {
                updateDebug();
            }
        }, 100);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Two-Way Data Binding Test")
    print("="*50)
    print("Open http://localhost:5003 and type in the input fields")
    print("All bound elements should update immediately")
    print("="*50 + "\n")
    app.run(debug=True, port=5003)