"""
Example application demonstrating NewUI component composition patterns
"""

from flask import Flask, render_template_string, request, jsonify
from newui import NewUI
from newui import components as ui
from newui.composition import *
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key'
newui = NewUI(app)

# Sample data for demonstrations
SAMPLE_PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Coffee Mug", "price": 12.99, "category": "Home", "in_stock": True},
    {"id": 3, "name": "Book", "price": 24.99, "category": "Education", "in_stock": False},
    {"id": 4, "name": "Headphones", "price": 89.99, "category": "Electronics", "in_stock": True},
]

SAMPLE_USERS = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "Admin", "active": True},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "User", "active": True},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "role": "User", "active": False},
]

class ProductCardComponent(Component):
    """Custom product card component"""
    
    def __init__(self, product: dict, props: ComponentProps = None):
        super().__init__("product-card", props)
        self.product = product
        self.set_state('product', product)
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        product = self.product
        
        stock_badge = "In Stock" if product['in_stock'] else "Out of Stock"
        stock_class = "success" if product['in_stock'] else "danger"
        
        return Markup(f'''
            <div class="card h-100" {attrs}>
                <div class="card-body">
                    <h5 class="card-title">{product['name']}</h5>
                    <p class="card-text">
                        <span class="badge bg-secondary">{product['category']}</span>
                        <span class="badge bg-{stock_class} ms-2">{stock_badge}</span>
                    </p>
                    <p class="card-text">
                        <strong>${product['price']:.2f}</strong>
                    </p>
                    {self.render_children()}
                </div>
                <div class="card-footer">
                    <small class="text-muted">Product ID: {product['id']}</small>
                </div>
            </div>
        ''')

class UserRowComponent(Component):
    """Custom user row component for tables"""
    
    def __init__(self, user: dict, props: ComponentProps = None):
        super().__init__("user-row", props)
        self.user = user
        self.set_state('user', user)
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        user = self.user
        
        status_badge = "Active" if user['active'] else "Inactive"
        status_class = "success" if user['active'] else "secondary"
        
        return Markup(f'''
            <tr {attrs}>
                <td>{user['id']}</td>
                <td>{user['name']}</td>
                <td>{user['email']}</td>
                <td><span class="badge bg-primary">{user['role']}</span></td>
                <td><span class="badge bg-{status_class}">{status_badge}</span></td>
                <td>
                    {self.render_children()}
                </td>
            </tr>
        ''')

class DashboardLayoutComponent(Component):
    """Custom dashboard layout with sidebar and main content"""
    
    def __init__(self, title: str = "Dashboard", props: ComponentProps = None):
        super().__init__("dashboard-layout", props)
        self.title = title
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        
        sidebar = self.get_slot('sidebar', '<p>No sidebar content</p>')
        main_content = self.get_slot('main', self.render_children())
        header = self.get_slot('header', f'<h1>{self.title}</h1>')
        
        return Markup(f'''
            <div class="dashboard-layout" {attrs}>
                <div class="row">
                    <div class="col-md-3">
                        <div class="sidebar bg-light p-3 rounded">
                            <h5>Navigation</h5>
                            {sidebar}
                        </div>
                    </div>
                    <div class="col-md-9">
                        <div class="main-content">
                            <div class="header mb-4">
                                {header}
                            </div>
                            <div class="content">
                                {main_content}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        ''')

# Register custom components
registry.register_template('product-card', lambda product, **kwargs: ProductCardComponent(product, **kwargs))
registry.register_template('user-row', lambda user, **kwargs: UserRowComponent(user, **kwargs))
registry.register_template('dashboard-layout', lambda title="Dashboard", **kwargs: DashboardLayoutComponent(title, **kwargs))

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Component Composition Demo</title>
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
        .composition-example {
            border: 2px dashed #007bff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background: #f8f9fa;
        }
        .component-source {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 3px;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
            margin: 10px 0;
        }
        .sidebar {
            min-height: 400px;
        }
        .dashboard-layout {
            min-height: 500px;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>Component Composition Patterns</h1>
        <p class="text-muted">Explore reusable, composable components in NewUI</p>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>1. Custom Component Classes</h3>
                    <p>Create reusable components with custom logic and rendering</p>
                    
                    <div class="composition-example">
                        <h5>Product Cards</h5>
                        <div class="row">
                            {% for product in products %}
                            {{ product_cards[loop.index0] }}
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="component-source">
                        <strong>Component Definition:</strong><br>
                        class ProductCardComponent(Component):<br>
                        &nbsp;&nbsp;def render(self) -> Markup:<br>
                        &nbsp;&nbsp;&nbsp;&nbsp;return Markup(f'&lt;div class="card"&gt;...&lt;/div&gt;')
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>2. Component Builder Pattern</h3>
                    <p>Use fluent API to build complex components</p>
                    
                    <div class="composition-example">
                        {{ builder_card }}
                    </div>
                    
                    <div class="component-source">
                        <strong>Builder Usage:</strong><br>
                        card("User Profile")<br>
                        &nbsp;&nbsp;.with_css_class("border-primary")<br>
                        &nbsp;&nbsp;.with_slot("body", user_content)<br>
                        &nbsp;&nbsp;.build().render()
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>3. Layout Components with Slots</h3>
                    <p>Create flexible layouts using named slots</p>
                    
                    <div class="composition-example">
                        {{ dashboard_layout }}
                    </div>
                    
                    <div class="component-source">
                        <strong>Layout with Slots:</strong><br>
                        layout = DashboardLayoutComponent("My Dashboard")<br>
                        layout.add_slot("sidebar", navigation_component)<br>
                        layout.add_slot("main", main_content_component)
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>4. List Components with Templates</h3>
                    <p>Render lists using component templates</p>
                    
                    <div class="composition-example">
                        <h5>User Management Table</h5>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for user_row in user_rows %}
                                {{ user_row }}
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="demo-section">
                    <h3>5. Conditional Components</h3>
                    <p>Components that render based on conditions</p>
                    
                    <div class="composition-example" data-ui-component="conditional-demo" 
                         data-ui-state='{"show_advanced": false, "user_role": "admin"}'>
                        <div class="mb-3">
                            {{ ui.checkbox("show_advanced", "Show Advanced Options", 
                                         bind="show_advanced", id="show-advanced") }}
                        </div>
                        
                        {{ conditional_content }}
                        
                        <hr>
                        
                        {{ role_based_content }}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>6. Nested Component Composition</h3>
                    <p>Complex UIs built from nested, reusable components</p>
                    
                    <div class="composition-example">
                        {{ nested_composition }}
                    </div>
                    
                    <div class="component-source">
                        <strong>Nested Structure:</strong><br>
                        layout("two-column")<br>
                        &nbsp;&nbsp;.with_slot("left", product_list)<br>
                        &nbsp;&nbsp;.with_slot("right", user_profile_card)<br>
                        &nbsp;&nbsp;.build()
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>7. Component Registry</h3>
                    <p>Register and reuse components across your application</p>
                    
                    <div class="composition-example">
                        <h5>Registered Components:</h5>
                        <ul class="list-group">
                            {% for component_name in registered_components %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span><code>{{ component_name }}</code></span>
                                <span class="badge bg-primary rounded-pill">Available</span>
                            </li>
                            {% endfor %}
                        </ul>
                        
                        <div class="mt-3">
                            <button class="btn btn-primary" data-ui-click="createRegistryComponent">
                                Create Component from Registry
                            </button>
                            <div id="registry-output" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>8. Interactive Component Communication</h3>
                    <p>Components that communicate with parent/child relationships</p>
                    
                    <div class="composition-example" data-ui-component="component-communication" 
                         data-ui-state='{"message": "", "child_count": 0}'>
                        
                        <div class="alert alert-info">
                            <strong>Parent Message:</strong> 
                            <span data-ui-bind="message">No message yet</span>
                        </div>
                        
                        <div class="alert alert-success">
                            <strong>Child Components Count:</strong> 
                            <span data-ui-bind="child_count">0</span>
                        </div>
                        
                        <div class="mb-3">
                            <button class="btn btn-primary" data-ui-click="addChild">Add Child Component</button>
                            <button class="btn btn-warning" data-ui-click="removeChild">Remove Child</button>
                            <button class="btn btn-info" data-ui-click="broadcastMessage">Broadcast Message</button>
                        </div>
                        
                        <div id="dynamic-children" class="border p-3 rounded">
                            <!-- Dynamic child components will appear here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Component communication handlers
        NewUI.registerHandler('addChild', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            const newCount = (state.child_count || 0) + 1;
            
            NewUI.setStateValue(componentId, 'child_count', newCount);
            
            // Add new child component
            const container = document.getElementById('dynamic-children');
            const childDiv = document.createElement('div');
            childDiv.className = 'child-component alert alert-secondary mt-2';
            childDiv.innerHTML = `
                <strong>Child Component #${newCount}</strong>
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="removeThisChild(this)">Remove</button>
                <button class="btn btn-sm btn-outline-info ms-2" onclick="sendMessageToParent(this, ${newCount})">Send Message</button>
            `;
            container.appendChild(childDiv);
        });
        
        NewUI.registerHandler('removeChild', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            const currentCount = state.child_count || 0;
            
            if (currentCount > 0) {
                NewUI.setStateValue(componentId, 'child_count', currentCount - 1);
                
                // Remove last child
                const container = document.getElementById('dynamic-children');
                const children = container.querySelectorAll('.child-component');
                if (children.length > 0) {
                    children[children.length - 1].remove();
                }
            }
        });
        
        NewUI.registerHandler('broadcastMessage', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const message = `Broadcast from parent at ${new Date().toLocaleTimeString()}`;
            
            NewUI.setStateValue(componentId, 'message', message);
            
            // Update all child components
            const children = document.querySelectorAll('.child-component');
            children.forEach((child, index) => {
                const messageSpan = document.createElement('small');
                messageSpan.className = 'text-muted d-block';
                messageSpan.textContent = `Received: ${message}`;
                
                // Remove old messages
                const oldMessages = child.querySelectorAll('small.text-muted');
                oldMessages.forEach(msg => msg.remove());
                
                child.appendChild(messageSpan);
            });
        });
        
        // Registry demo
        NewUI.registerHandler('createRegistryComponent', function(element, event) {
            const output = document.getElementById('registry-output');
            
            // Create a component dynamically from registry
            const cardHtml = `
                <div class="card mt-3">
                    <div class="card-header">
                        <h5>Dynamically Created Component</h5>
                    </div>
                    <div class="card-body">
                        <p>This card was created using the component registry at runtime!</p>
                        <small class="text-muted">Created at: ${new Date().toLocaleString()}</small>
                    </div>
                </div>
            `;
            
            output.innerHTML = cardHtml;
        });
        
        // Helper functions for dynamic children
        function removeThisChild(button) {
            button.closest('.child-component').remove();
            
            // Update parent count
            const parentComponent = document.querySelector('[data-ui-component="component-communication"]');
            const componentId = parentComponent.getAttribute('data-ui-id');
            const currentCount = NewUI.state[componentId].child_count || 0;
            NewUI.setStateValue(componentId, 'child_count', Math.max(0, currentCount - 1));
        }
        
        function sendMessageToParent(button, childNumber) {
            const message = `Message from Child #${childNumber} at ${new Date().toLocaleTimeString()}`;
            
            const parentComponent = document.querySelector('[data-ui-component="component-communication"]');
            const componentId = parentComponent.getAttribute('data-ui-id');
            NewUI.setStateValue(componentId, 'message', message);
        }
        
        console.log('Component composition demo initialized');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Create product cards using custom components
    product_cards = []
    for product in SAMPLE_PRODUCTS:
        card_component = ProductCardComponent(product)
        
        # Add action buttons as children
        if product['in_stock']:
            card_component.add_child(HTMLComponent("button", "Add to Cart", 
                ComponentProps(css_classes=["btn", "btn-primary", "btn-sm"], 
                              attributes={"data-ui-click": "addToCart"})))
        else:
            card_component.add_child(HTMLComponent("button", "Notify Me", 
                ComponentProps(css_classes=["btn", "btn-outline-secondary", "btn-sm"], 
                              attributes={"disabled": True})))
        
        product_cards.append(card_component.render())
    
    # Create user rows
    user_rows = []
    for user in SAMPLE_USERS:
        row_component = UserRowComponent(user)
        
        # Add action buttons
        actions_html = f'''
            <button class="btn btn-sm btn-outline-primary" data-ui-click="editUser" data-user-id="{user['id']}">Edit</button>
            <button class="btn btn-sm btn-outline-danger ms-1" data-ui-click="deleteUser" data-user-id="{user['id']}">Delete</button>
        '''
        row_component.add_child(HTMLComponent("div", actions_html))
        user_rows.append(row_component.render())
    
    # Create builder pattern example
    user_profile_content = HTMLComponent("div", '''
        <p><strong>Name:</strong> John Doe</p>
        <p><strong>Email:</strong> john@example.com</p>
        <p><strong>Role:</strong> Administrator</p>
    ''')
    
    builder_card = (card("User Profile")
                   .with_css_class("border-primary")
                   .with_slot("body", user_profile_content)
                   .with_attribute("id", "user-profile-card")
                   .build().render())
    
    # Create dashboard layout
    sidebar_content = HTMLComponent("div", '''
        <ul class="nav nav-pills flex-column">
            <li class="nav-item"><a class="nav-link active" href="#">Dashboard</a></li>
            <li class="nav-item"><a class="nav-link" href="#">Users</a></li>
            <li class="nav-item"><a class="nav-link" href="#">Products</a></li>
            <li class="nav-item"><a class="nav-link" href="#">Settings</a></li>
        </ul>
    ''')
    
    main_content = HTMLComponent("div", '''
        <div class="row">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Users</h5>
                        <h2 class="text-primary">1,234</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Products</h5>
                        <h2 class="text-success">567</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Orders</h5>
                        <h2 class="text-warning">890</h2>
                    </div>
                </div>
            </div>
        </div>
    ''')
    
    dashboard = DashboardLayoutComponent("Analytics Dashboard")
    dashboard.add_slot("sidebar", sidebar_content)
    dashboard.add_slot("main", main_content)
    dashboard_layout = dashboard.render()
    
    # Create conditional content
    advanced_options = HTMLComponent("div", '''
        <div class="alert alert-warning">
            <h6>Advanced Options</h6>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="debug-mode">
                <label class="form-check-label" for="debug-mode">Enable Debug Mode</label>
            </div>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="beta-features">
                <label class="form-check-label" for="beta-features">Enable Beta Features</label>
            </div>
        </div>
    ''')
    
    conditional_content = ui.show_if("show_advanced", advanced_options.render())
    
    # Role-based content
    admin_content = HTMLComponent("div", '''
        <div class="alert alert-info">
            <h6>Administrator Panel</h6>
            <p>You have administrative privileges.</p>
            <button class="btn btn-sm btn-primary">Manage System</button>
        </div>
    ''')
    
    user_content = HTMLComponent("div", '''
        <div class="alert alert-secondary">
            <h6>User Panel</h6>
            <p>Standard user access.</p>
        </div>
    ''')
    
    role_based_content = ui.toggle('user_role === "admin"', 
                                  admin_content.render(), 
                                  user_content.render())
    
    # Create nested composition
    product_summary = HTMLComponent("div", '''
        <h5>Product Summary</h5>
        <ul class="list-group">
            <li class="list-group-item d-flex justify-content-between">
                Electronics <span class="badge bg-primary">2 items</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
                Home <span class="badge bg-success">1 item</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
                Education <span class="badge bg-info">1 item</span>
            </li>
        </ul>
    ''')
    
    user_summary = HTMLComponent("div", '''
        <h5>User Summary</h5>
        <div class="card">
            <div class="card-body">
                <p><strong>Total Users:</strong> 3</p>
                <p><strong>Active:</strong> 2</p>
                <p><strong>Inactive:</strong> 1</p>
                <p><strong>Admins:</strong> 1</p>
            </div>
        </div>
    ''')
    
    nested_layout = (layout("two-column")
                    .with_slot("left", product_summary)
                    .with_slot("right", user_summary)
                    .with_css_class("border", "rounded", "p-3")
                    .build().render())
    
    return render_template_string(TEMPLATE, 
                                ui=ui,
                                products=SAMPLE_PRODUCTS,
                                users=SAMPLE_USERS,
                                product_cards=product_cards,
                                user_rows=user_rows,
                                builder_card=builder_card,
                                dashboard_layout=dashboard_layout,
                                conditional_content=conditional_content,
                                role_based_content=role_based_content,
                                nested_composition=nested_layout,
                                registered_components=registry.list_components())

if __name__ == '__main__':
    print("\\n" + "="*50)
    print("Component Composition Demo")
    print("="*50)
    print("Open http://localhost:5009")
    print("Features:")
    print("- Custom component classes with reusable logic")
    print("- Builder pattern for fluent component creation")
    print("- Layout components with named slots")
    print("- List components with item templates")
    print("- Conditional rendering components")
    print("- Nested component composition")
    print("- Component registry for reusable templates")
    print("- Interactive component communication")
    print("="*50 + "\\n")
    app.run(debug=True, port=5009)