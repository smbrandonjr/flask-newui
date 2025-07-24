"""
Example application demonstrating NewUI two-way data binding
"""

from flask import Flask, render_template_string, jsonify
from newui import NewUI

app = Flask(__name__)
app.secret_key = 'your-secret-key'
ui = NewUI(app)

# Example template with two-way data binding
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Data Binding Example</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Two-Way Data Binding Demo</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div data-ui-component="form-demo" data-ui-id="demo-form" 
                     data-ui-state='{{ initial_state | tojson }}'>
                    
                    <h3>Form Inputs</h3>
                    
                    {% set form_html = ui_components.form(content=form_content, ajax=True, action="/submit") %}
                    {{ form_html }}
                    
                    <hr>
                    
                    <h3>Live Preview</h3>
                    <div class="card">
                        <div class="card-body">
                            <p><strong>Name:</strong> <span data-ui-bind="user.name">{{ initial_state.user.name }}</span></p>
                            <p><strong>Email:</strong> <span data-ui-bind="user.email">{{ initial_state.user.email }}</span></p>
                            <p><strong>Bio:</strong> <span data-ui-bind="user.bio">{{ initial_state.user.bio }}</span></p>
                            <p><strong>Country:</strong> <span data-ui-bind="user.country">{{ initial_state.user.country }}</span></p>
                            <p><strong>Newsletter:</strong> <span data-ui-bind="user.newsletter">{{ initial_state.user.newsletter }}</span></p>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <h3>Synchronized Input</h3>
                    <p>This input is synchronized with the name field above:</p>
                    {% set sync_input = ui_components.input(name="sync_name", model="user.name", sync=True, placeholder="Type here...") %}
                    {{ sync_input }}
                    
                </div>
            </div>
            
            <div class="col-md-6">
                <h3>State Debug View</h3>
                <pre id="state-debug" class="bg-light p-3"></pre>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Update debug view when state changes
        NewUI.registerHandler('updateDebug', function() {
            // Find the actual component ID
            const component = document.querySelector('[data-ui-component="form-demo"]');
            if (!component) return;
            
            const componentId = component.getAttribute('data-ui-id');
            const state = NewUI.state[componentId] || {};
            document.getElementById('state-debug').textContent = JSON.stringify(state, null, 2);
        });
        
        // Initial debug update
        setTimeout(() => {
            NewUI.handlers.updateDebug();
        }, 100);
        
        // Update debug on any input change
        document.addEventListener('input', () => {
            NewUI.handlers.updateDebug();
        });
        document.addEventListener('change', () => {
            NewUI.handlers.updateDebug();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Initial state for the form
    initial_state = {
        'user': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'bio': 'A passionate developer',
            'country': 'us',
            'newsletter': True
        }
    }
    
    # Import components
    from newui import components as ui_components
    
    # Form content with data binding
    form_content = f"""
        {ui_components.input(name="name", label="Name", model="user.name", sync=True)}
        {ui_components.input(name="email", type="email", label="Email", model="user.email", sync=True)}
        {ui_components.textarea(name="bio", label="Bio", model="user.bio", sync=True, rows=3)}
        {ui_components.select(
            name="country", 
            label="Country",
            model="user.country",
            sync=True,
            options=[
                {'value': 'us', 'text': 'United States'},
                {'value': 'ca', 'text': 'Canada'},
                {'value': 'uk', 'text': 'United Kingdom'},
                {'value': 'au', 'text': 'Australia'}
            ]
        )}
        {ui_components.checkbox(name="newsletter", label="Subscribe to newsletter", model="user.newsletter", sync=True)}
        {ui_components.button("Submit", type="submit", variant="primary")}
    """
    
    return render_template_string(TEMPLATE, 
                                initial_state=initial_state,
                                form_content=form_content,
                                ui_components=ui_components)

@app.route('/submit', methods=['POST'])
def submit():
    # In a real app, you would process the form data here
    return jsonify({'success': True, 'message': 'Form submitted successfully!'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)