"""
Example application demonstrating NewUI built-in loading states
"""

from flask import Flask, render_template_string, jsonify, request
from newui import NewUI
from newui import components as ui
import time
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'
newui = NewUI(app)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Loading States Demo</title>
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
        .demo-content {
            min-height: 150px;
            background: #f8f9fa;
            border-radius: 5px;
            padding: 20px;
            margin: 10px 0;
        }
        .action-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>Loading States Demo</h1>
        <p class="text-muted">Explore different loading states and patterns in NewUI</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>Basic Spinners</h3>
                    <p>Different spinner variations</p>
                    
                    <div class="mb-3">
                        <h5>Sizes:</h5>
                        {{ ui.spinner(size="sm", text="Small", inline=True) }}
                        {{ ui.spinner(size="md", text="Medium", inline=True, class_="ms-3") }}
                        {{ ui.spinner(size="lg", text="Large", inline=True, class_="ms-3") }}
                    </div>
                    
                    <div class="mb-3">
                        <h5>Colors:</h5>
                        {{ ui.spinner(variant="primary", text="Primary", inline=True) }}
                        {{ ui.spinner(variant="success", text="Success", inline=True, class_="ms-3") }}
                        {{ ui.spinner(variant="warning", text="Warning", inline=True, class_="ms-3") }}
                        {{ ui.spinner(variant="danger", text="Error", inline=True, class_="ms-3") }}
                    </div>
                    
                    <div class="mb-3">
                        <h5>Centered:</h5>
                        {{ ui.spinner(text="Loading data...") }}
                    </div>
                </div>
                
                <div class="demo-section">
                    <h3>Skeleton Loading</h3>
                    <p>Placeholder content while loading</p>
                    
                    <div class="row">
                        <div class="col-6">
                            <h5>Text Lines:</h5>
                            {{ ui.skeleton(lines=3) }}
                        </div>
                        <div class="col-6">
                            <h5>Variable Width:</h5>
                            {{ ui.skeleton(lines=4, width="90%") }}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>Interactive Loading</h3>
                    <p>Control loading states with buttons</p>
                    
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="showOverlayDemo()">Show Overlay</button>
                        <button class="btn btn-success" onclick="showWrapperDemo()">Show Wrapper</button>
                        <button class="btn btn-warning" onclick="showTimedDemo()">Timed Loading</button>
                        <button class="btn btn-info" onclick="showButtonDemo()">Button Loading</button>
                    </div>
                    
                    <div id="demo-content" class="demo-content">
                        <h5>Demo Content Area</h5>
                        <p>This content will be covered by loading states when you click the buttons above.</p>
                        <ul>
                            <li>Item one</li>
                            <li>Item two</li>
                            <li>Item three</li>
                        </ul>
                    </div>
                </div>
                
                <div class="demo-section">
                    <h3>Form Loading</h3>
                    
                    <form data-ui-component="demo-form" data-ui-state='{"submitting": false}'>
                        <div class="mb-3">
                            {{ ui.input("email", type="email", label="Email Address", 
                                      placeholder="Enter your email", required=True) }}
                        </div>
                        <div class="mb-3">
                            {{ ui.textarea("message", label="Message", 
                                         placeholder="Enter your message...", rows=3) }}
                        </div>
                        <button type="button" class="btn btn-primary" id="submit-btn" 
                                onclick="simulateFormSubmit()">
                            Submit Form
                        </button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>Loading Wrapper Component</h3>
                    <p>Wrap content with built-in loading capability</p>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <h5>Spinner Type:</h5>
                            {{ ui.loading_wrapper(
                                '<div class="p-3"><h6>User Profile</h6><p>John Doe<br>john@example.com<br>Admin Role</p></div>',
                                loading_text="Loading profile...",
                                loading_type="spinner",
                                id="wrapper-spinner"
                            ) }}
                            <button class="btn btn-sm btn-outline-primary mt-2" 
                                    onclick="toggleWrapper('wrapper-spinner')">
                                Toggle Loading
                            </button>
                        </div>
                        
                        <div class="col-md-4">
                            <h5>Skeleton Type:</h5>
                            {{ ui.loading_wrapper(
                                '<div class="p-3"><h6>Article Content</h6><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore.</p></div>',
                                loading_text="Loading article...",
                                loading_type="skeleton",
                                id="wrapper-skeleton"
                            ) }}
                            <button class="btn btn-sm btn-outline-primary mt-2" 
                                    onclick="toggleWrapper('wrapper-skeleton')">
                                Toggle Loading
                            </button>
                        </div>
                        
                        <div class="col-md-4">
                            <h5>Overlay Type:</h5>
                            {{ ui.loading_wrapper(
                                '<div class="p-3"><h6>Dashboard</h6><div class="row"><div class="col-6">Charts</div><div class="col-6">Stats</div></div></div>',
                                loading_text="Loading dashboard...",
                                loading_type="overlay",
                                id="wrapper-overlay"
                            ) }}
                            <button class="btn btn-sm btn-outline-primary mt-2" 
                                    onclick="toggleWrapper('wrapper-overlay')">
                                Toggle Loading
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>AJAX Loading</h3>
                    <p>Simulate real async operations</p>
                    
                    <div data-ui-component="ajax-demo" data-ui-state='{"data": null, "loading": false}'>
                        <div class="action-buttons">
                            <button class="btn btn-primary" data-ui-click="loadUserData">Load Users</button>
                            <button class="btn btn-success" data-ui-click="loadPostData">Load Posts</button>
                            <button class="btn btn-warning" data-ui-click="simulateError">Simulate Error</button>
                            <button class="btn btn-secondary" data-ui-click="clearData">Clear</button>
                        </div>
                        
                        <div id="ajax-content" class="demo-content mt-3">
                            <div data-ui-show="!data && !loading">
                                <p class="text-muted text-center">Click a button above to load data</p>
                            </div>
                            
                            <div data-ui-show="loading">
                                {{ ui.spinner(text="Loading data from server...") }}
                            </div>
                            
                            <div data-ui-show="data && !loading">
                                <pre id="data-display" class="bg-light p-3"></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Demo functions for interactive loading
        function showOverlayDemo() {
            NewUI.showLoading('demo-content', { overlay: true, text: 'Loading with overlay...' });
            setTimeout(() => NewUI.hideLoading('demo-content'), 3000);
        }
        
        function showWrapperDemo() {
            NewUI.showLoading('demo-content', { text: 'Wrapper loading...' });
            setTimeout(() => NewUI.hideLoading('demo-content'), 2500);
        }
        
        function showTimedDemo() {
            NewUI.showLoadingFor('demo-content', 2000, { 
                overlay: true, 
                text: 'This will hide automatically in 2 seconds' 
            });
        }
        
        function showButtonDemo() {
            const btn = event.target;
            NewUI.setButtonLoading(btn, true, 'Processing...');
            setTimeout(() => NewUI.setButtonLoading(btn, false), 3000);
        }
        
        function simulateFormSubmit() {
            const btn = document.getElementById('submit-btn');
            NewUI.setButtonLoading(btn, true, 'Submitting...');
            
            // Simulate network delay
            setTimeout(() => {
                NewUI.setButtonLoading(btn, false);
                alert('Form submitted successfully!');
            }, 2500);
        }
        
        function toggleWrapper(wrapperId) {
            const wrapper = document.getElementById(wrapperId);
            const isLoading = wrapper.classList.contains('ui-loading');
            
            if (isLoading) {
                NewUI.hideLoading(wrapper);
            } else {
                NewUI.showLoading(wrapper);
            }
        }
        
        // AJAX Demo handlers
        NewUI.registerHandler('loadUserData', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            
            NewUI.setStateValue(componentId, 'loading', true);
            NewUI.setStateValue(componentId, 'data', null);
            
            // Simulate API call
            setTimeout(() => {
                const userData = {
                    users: [
                        { id: 1, name: 'Alice Johnson', email: 'alice@example.com' },
                        { id: 2, name: 'Bob Smith', email: 'bob@example.com' },
                        { id: 3, name: 'Charlie Brown', email: 'charlie@example.com' }
                    ],
                    meta: { total: 3, loaded_at: new Date().toISOString() }
                };
                
                NewUI.setStateValue(componentId, 'data', userData);
                NewUI.setStateValue(componentId, 'loading', false);
                
                document.getElementById('data-display').textContent = JSON.stringify(userData, null, 2);
            }, 1500);
        });
        
        NewUI.registerHandler('loadPostData', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            
            NewUI.setStateValue(componentId, 'loading', true);
            NewUI.setStateValue(componentId, 'data', null);
            
            setTimeout(() => {
                const postData = {
                    posts: [
                        { id: 1, title: 'First Post', content: 'Hello world!' },
                        { id: 2, title: 'Second Post', content: 'Another post here' }
                    ],
                    meta: { count: 2, loaded_at: new Date().toISOString() }
                };
                
                NewUI.setStateValue(componentId, 'data', postData);
                NewUI.setStateValue(componentId, 'loading', false);
                
                document.getElementById('data-display').textContent = JSON.stringify(postData, null, 2);
            }, 2000);
        });
        
        NewUI.registerHandler('simulateError', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            
            NewUI.setStateValue(componentId, 'loading', true);
            NewUI.setStateValue(componentId, 'data', null);
            
            setTimeout(() => {
                const errorData = {
                    error: 'Failed to load data',
                    message: 'The server returned a 500 error',
                    timestamp: new Date().toISOString()
                };
                
                NewUI.setStateValue(componentId, 'data', errorData);
                NewUI.setStateValue(componentId, 'loading', false);
                
                document.getElementById('data-display').textContent = JSON.stringify(errorData, null, 2);
            }, 1000);
        });
        
        NewUI.registerHandler('clearData', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            
            NewUI.setStateValue(componentId, 'data', null);
            NewUI.setStateValue(componentId, 'loading', false);
            
            document.getElementById('data-display').textContent = '';
        });
        
        console.log('Loading states demo initialized');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, ui=ui)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Loading States Demo")
    print("="*50)
    print("Open http://localhost:5007")
    print("Features:")
    print("- Spinner components (different sizes and colors)")
    print("- Skeleton loading placeholders")
    print("- Loading overlays and wrappers")
    print("- Button loading states")
    print("- Form submission loading")
    print("- AJAX loading simulation")
    print("="*50 + "\n")
    app.run(debug=True, port=5007)