"""
Example application demonstrating NewUI conditional rendering
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
    <title>NewUI Conditional Rendering Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    <style>
        .demo-section {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
        }
        .state-debug {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>Conditional Rendering Demo</h1>
        
        <div data-ui-component="demo" data-ui-id="demo1" 
             data-ui-state='{{ initial_state | tojson }}'>
            
            <div class="row">
                <div class="col-md-6">
                    <h3>Controls</h3>
                    
                    <div class="demo-section">
                        <h5>Toggle Visibility</h5>
                        {{ ui.checkbox(name="show_message", model="showMessage", 
                                     label="Show welcome message") }}
                        {{ ui.checkbox(name="is_premium", model="user.isPremium", 
                                     label="Premium user") }}
                        {{ ui.checkbox(name="has_notifications", model="hasNotifications", 
                                     label="Has notifications") }}
                    </div>
                    
                    <div class="demo-section">
                        <h5>User Settings</h5>
                        {{ ui.input(name="username", model="user.name", 
                                  label="Username", placeholder="Enter name...") }}
                        {{ ui.input(name="age", type="number", model="user.age", 
                                  label="Age", placeholder="Enter age...") }}
                        {{ ui.select(name="role", model="user.role", label="Role",
                                   options=[
                                       {'value': '', 'text': 'Select role...'},
                                       {'value': 'admin', 'text': 'Administrator'},
                                       {'value': 'user', 'text': 'Regular User'},
                                       {'value': 'guest', 'text': 'Guest'}
                                   ]) }}
                    </div>
                    
                    <div class="demo-section">
                        <h5>Notification Count</h5>
                        {{ ui.input(name="count", type="number", model="notificationCount", 
                                  label="Number of notifications", value="0") }}
                    </div>
                </div>
                
                <div class="col-md-6">
                    <h3>Conditional Content</h3>
                    
                    <!-- Simple show/hide -->
                    {{ ui.show_if("showMessage", '''
                        <div class="alert alert-info">
                            <h5>Welcome!</h5>
                            <p>This message is shown when checkbox is checked.</p>
                        </div>
                    ''') }}
                    
                    <!-- Hide if condition -->
                    {{ ui.hide_if("user.isPremium", '''
                        <div class="alert alert-warning">
                            <strong>Upgrade to Premium!</strong>
                            <p>Get access to exclusive features.</p>
                        </div>
                    ''') }}
                    
                    <!-- Show based on user input -->
                    {{ ui.show_if("user.name", '''
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5>Hello, <span data-ui-bind="user.name"></span>!</h5>
                                <p>Nice to meet you.</p>
                            </div>
                        </div>
                    ''') }}
                    
                    <!-- Complex conditions -->
                    {{ ui.show_if("user.age >= 18", '''
                        <div class="alert alert-success">
                            You are an adult (18 or older).
                        </div>
                    ''') }}
                    
                    {{ ui.show_if("user.age > 0 && user.age < 18", '''
                        <div class="alert alert-info">
                            You are a minor (under 18).
                        </div>
                    ''') }}
                    
                    <!-- Role-based visibility -->
                    {{ ui.show_if('user.role === "admin"', '''
                        <div class="card border-danger mb-3">
                            <div class="card-header bg-danger text-white">Admin Panel</div>
                            <div class="card-body">
                                <p>Administrator tools and settings.</p>
                            </div>
                        </div>
                    ''') }}
                    
                    <!-- Toggle between two states -->
                    {{ ui.toggle("hasNotifications", 
                        true_content='''
                            <div class="alert alert-primary">
                                <strong>You have <span data-ui-bind="notificationCount"></span> notifications!</strong>
                            </div>
                        ''',
                        false_content='''
                            <div class="alert alert-secondary">
                                No new notifications.
                            </div>
                        '''
                    ) }}
                    
                    <!-- Multiple conditions -->
                    {{ ui.show_if('user.isPremium && user.role === "admin"', '''
                        <div class="card border-gold mb-3" style="border-color: gold;">
                            <div class="card-body">
                                <h5>Premium Admin Features</h5>
                                <p>Exclusive access to advanced admin tools.</p>
                            </div>
                        </div>
                    ''') }}
                    
                    <!-- Numeric comparisons -->
                    {{ ui.show_if("notificationCount > 5", '''
                        <div class="alert alert-danger">
                            Too many notifications! Please check them.
                        </div>
                    ''') }}
                </div>
            </div>
            
            <hr>
            
            <div class="row">
                <div class="col-12">
                    <h4>State Debug</h4>
                    <div class="state-debug" id="state-debug"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Update state debug view
        function updateDebug() {
            const state = NewUI.state['demo1'] || {};
            document.getElementById('state-debug').textContent = JSON.stringify(state, null, 2);
        }
        
        // Initial update
        setTimeout(updateDebug, 100);
        
        // Update on any change
        document.addEventListener('input', updateDebug);
        document.addEventListener('change', updateDebug);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    initial_state = {
        'showMessage': True,
        'hasNotifications': False,
        'notificationCount': 0,
        'user': {
            'name': '',
            'age': 0,
            'isPremium': False,
            'role': ''
        }
    }
    
    return render_template_string(TEMPLATE, 
                                initial_state=initial_state,
                                ui=ui)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Conditional Rendering Demo")
    print("="*50)
    print("Open http://localhost:5004")
    print("Try toggling checkboxes and changing values!")
    print("="*50 + "\n")
    app.run(debug=True, port=5004)