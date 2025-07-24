"""
Example application demonstrating NewUI route-based code splitting
"""

from flask import Flask, render_template_string, request, jsonify
from newui import NewUI
from newui import components as ui
from newui.routing import *
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'
newui = NewUI(app)

# Initialize routing system
chunk_manager = init_routing(app)
router = RouterComponent(chunk_manager)

# Create example JavaScript content for different routes
DASHBOARD_JS = """
// Dashboard specific functionality
window.DashboardComponents = {
    StatsWidget: function(element, state) {
        console.log('Stats widget initialized');
        
        // Simulate loading stats
        setTimeout(() => {
            const stats = {
                users: Math.floor(Math.random() * 1000) + 500,
                orders: Math.floor(Math.random() * 500) + 200,
                revenue: Math.floor(Math.random() * 50000) + 25000
            };
            
            element.querySelector('.users-count').textContent = stats.users;
            element.querySelector('.orders-count').textContent = stats.orders;
            element.querySelector('.revenue-count').textContent = '$' + stats.revenue.toLocaleString();
        }, 1000);
    },
    
    RecentActivity: function(element, state) {
        console.log('Recent activity widget initialized');
        
        const activities = [
            'User John Doe registered',
            'Order #1234 completed',
            'New product "Widget" added',
            'Customer service ticket #567 resolved'
        ];
        
        const list = element.querySelector('.activity-list');
        list.innerHTML = activities.map(activity => 
            `<li class="list-group-item">${activity}</li>`
        ).join('');
    }
};

// Dashboard event handlers
NewUI.registerHandler('refreshDashboard', function(element, event) {
    const widgets = document.querySelectorAll('[data-ui-component="StatsWidget"]');
    widgets.forEach(widget => {
        NewUI.components.StatsWidget(widget, {});
    });
});
"""

PRODUCTS_JS = """
// Products page functionality
window.ProductsComponents = {
    ProductGrid: function(element, state) {
        console.log('Product grid initialized');
        
        const products = [
            {id: 1, name: 'Laptop Pro', price: 1299.99, category: 'Electronics'},
            {id: 2, name: 'Wireless Mouse', price: 29.99, category: 'Electronics'},
            {id: 3, name: 'Coffee Mug', price: 12.99, category: 'Home'},
            {id: 4, name: 'Notebook', price: 8.99, category: 'Office'},
            {id: 5, name: 'USB Cable', price: 15.99, category: 'Electronics'},
            {id: 6, name: 'Desk Lamp', price: 45.99, category: 'Home'}
        ];
        
        const grid = element.querySelector('.product-grid');
        grid.innerHTML = products.map(product => `
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text">
                            <strong>$${product.price}</strong><br>
                            <small class="text-muted">${product.category}</small>
                        </p>
                        <button class="btn btn-primary btn-sm" onclick="addToCart(${product.id})">
                            Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    },
    
    ProductFilter: function(element, state) {
        console.log('Product filter initialized');
        
        const categories = ['All', 'Electronics', 'Home', 'Office'];
        const select = element.querySelector('select');
        
        select.innerHTML = categories.map(cat => 
            `<option value="${cat.toLowerCase()}">${cat}</option>`
        ).join('');
        
        select.addEventListener('change', function() {
            // Filter products based on selection
            console.log('Filter changed to:', this.value);
        });
    }
};

// Product page handlers
NewUI.registerHandler('addToCart', function(element, event) {
    const productId = element.getAttribute('data-product-id');
    console.log('Adding product to cart:', productId);
    
    // Show notification
    showNotification('Product added to cart!');
});

function addToCart(productId) {
    console.log('Adding product to cart:', productId);
    showNotification('Product added to cart!');
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 1000;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
"""

ANALYTICS_JS = """
// Analytics page functionality
window.AnalyticsComponents = {
    ChartWidget: function(element, state) {
        console.log('Chart widget initialized');
        
        // Simulate chart data
        const canvas = element.querySelector('canvas');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            
            // Simple bar chart simulation
            ctx.fillStyle = '#007bff';
            const data = [30, 45, 25, 60, 35, 50, 40];
            const barWidth = canvas.width / data.length;
            
            data.forEach((value, index) => {
                const barHeight = (value / 60) * canvas.height;
                ctx.fillRect(
                    index * barWidth, 
                    canvas.height - barHeight, 
                    barWidth - 2, 
                    barHeight
                );
            });
        }
    },
    
    MetricsTable: function(element, state) {
        console.log('Metrics table initialized');
        
        const metrics = [
            {metric: 'Page Views', value: '12,345', change: '+5.2%'},
            {metric: 'Unique Visitors', value: '3,456', change: '+2.1%'},
            {metric: 'Bounce Rate', value: '42.3%', change: '-1.5%'},
            {metric: 'Avg Session Duration', value: '3m 45s', change: '+8.7%'}
        ];
        
        const tbody = element.querySelector('tbody');
        tbody.innerHTML = metrics.map(metric => `
            <tr>
                <td>${metric.metric}</td>
                <td><strong>${metric.value}</strong></td>
                <td class="${metric.change.startsWith('+') ? 'text-success' : 'text-danger'}">
                    ${metric.change}
                </td>
            </tr>
        `).join('');
    }
};

// Analytics handlers
NewUI.registerHandler('exportData', function(element, event) {
    console.log('Exporting analytics data...');
    showNotification('Analytics data exported successfully!');
});

NewUI.registerHandler('refreshMetrics', function(element, event) {
    console.log('Refreshing metrics...');
    const tables = document.querySelectorAll('[data-ui-component="MetricsTable"]');
    tables.forEach(table => {
        NewUI.components.MetricsTable(table, {});
    });
});
"""

SETTINGS_JS = """
// Settings page functionality
window.SettingsComponents = {
    SettingsForm: function(element, state) {
        console.log('Settings form initialized');
        
        // Load saved settings
        const savedSettings = localStorage.getItem('app-settings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            
            Object.keys(settings).forEach(key => {
                const input = element.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = settings[key];
                    } else {
                        input.value = settings[key];
                    }
                }
            });
        }
    },
    
    ThemeSelector: function(element, state) {
        console.log('Theme selector initialized');
        
        const themes = ['light', 'dark', 'auto'];
        const select = element.querySelector('select');
        
        select.innerHTML = themes.map(theme => 
            `<option value="${theme}">${theme.charAt(0).toUpperCase() + theme.slice(1)}</option>`
        ).join('');
        
        select.addEventListener('change', function() {
            document.body.setAttribute('data-theme', this.value);
            console.log('Theme changed to:', this.value);
        });
    }
};

// Settings handlers
NewUI.registerHandler('saveSettings', function(element, event) {
    const form = element.closest('form');
    const formData = new FormData(form);
    const settings = {};
    
    for (let [key, value] of formData.entries()) {
        const input = form.querySelector(`[name="${key}"]`);
        if (input && input.type === 'checkbox') {
            settings[key] = input.checked;
        } else {
            settings[key] = value;
        }
    }
    
    localStorage.setItem('app-settings', JSON.stringify(settings));
    console.log('Settings saved:', settings);
    showNotification('Settings saved successfully!');
});

NewUI.registerHandler('resetSettings', function(element, event) {
    if (confirm('Are you sure you want to reset all settings?')) {
        localStorage.removeItem('app-settings');
        location.reload();
    }
});
"""

# CSS for different routes
DASHBOARD_CSS = """
.stats-widget {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.stats-widget h3 {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 5px;
}

.activity-widget {
    background: #f8f9fa;
    border-left: 4px solid #007bff;
    padding: 15px;
    border-radius: 4px;
}
"""

PRODUCTS_CSS = """
.product-grid .card {
    transition: transform 0.2s ease;
    border: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.product-grid .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.product-filter {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}
"""

ANALYTICS_CSS = """
.chart-widget {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-widget canvas {
    width: 100%;
    height: 200px;
}

.metrics-table {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
"""

# Write JavaScript files to temporary location for chunks
os.makedirs('temp_chunks', exist_ok=True)

with open('temp_chunks/dashboard.js', 'w') as f:
    f.write(DASHBOARD_JS)

with open('temp_chunks/products.js', 'w') as f:
    f.write(PRODUCTS_JS)

with open('temp_chunks/analytics.js', 'w') as f:
    f.write(ANALYTICS_JS)

with open('temp_chunks/settings.js', 'w') as f:
    f.write(SETTINGS_JS)

with open('temp_chunks/dashboard.css', 'w') as f:
    f.write(DASHBOARD_CSS)

with open('temp_chunks/products.css', 'w') as f:
    f.write(PRODUCTS_CSS)

with open('temp_chunks/analytics.css', 'w') as f:
    f.write(ANALYTICS_CSS)

# Register route chunks
register_route_chunk(
    name="dashboard",
    route_pattern="/dashboard",
    js_files=["temp_chunks/dashboard.js"],
    css_files=["temp_chunks/dashboard.css"],
    components=["StatsWidget", "RecentActivity"],
    preload=True  # Preload dashboard since it's commonly accessed
)

register_route_chunk(
    name="products",
    route_pattern="/products",
    js_files=["temp_chunks/products.js"],
    css_files=["temp_chunks/products.css"],
    components=["ProductGrid", "ProductFilter"],
    lazy=True
)

register_route_chunk(
    name="analytics",
    route_pattern="/analytics",
    js_files=["temp_chunks/analytics.js"],
    css_files=["temp_chunks/analytics.css"],
    components=["ChartWidget", "MetricsTable"],
    dependencies=["dashboard"],  # Analytics depends on dashboard components
    lazy=True
)

register_route_chunk(
    name="settings",
    route_pattern="/settings",
    js_files=["temp_chunks/settings.js"],
    components=["SettingsForm", "ThemeSelector"],
    lazy=True
)

# Register some component chunks
register_component_chunk(
    name="modal-component",
    component_name="Modal",
    js_content="""
// Modal component
window.ModalComponent = {
    show: function(title, content) {
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div class="modal fade show" style="display: block;" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                        </div>
                        <div class="modal-body">
                            ${content}
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show"></div>
        `;
        document.body.appendChild(modal);
    }
};
""",
    css_content="""
.modal {
    background: rgba(0,0,0,0.5);
}
""",
    dependencies=[]
)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Route-based Code Splitting Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    <style>
        .nav-tabs .nav-link {
            cursor: pointer;
        }
        .nav-tabs .nav-link.active {
            background: #007bff;
            color: white;
            border-color: #007bff;
        }
        .route-content {
            min-height: 400px;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-top: none;
            border-radius: 0 0 8px 8px;
        }
        .chunk-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 12px;
        }
        .demo-section {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            background: white;
        }
        
        /* Route-specific styles loaded dynamically */
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1>Route-based Code Splitting Demo</h1>
        <p class="text-muted">Dynamic loading of route-specific JavaScript and CSS</p>
        
        <div class="row">
            <div class="col-md-8">
                <div class="demo-section">
                    <h3>Single Page Application with Code Splitting</h3>
                    
                    <!-- Navigation Tabs -->
                    <ul class="nav nav-tabs" role="tablist">
                        <li class="nav-item">
                            <a class="nav-link active" data-route="/dashboard" onclick="navigateToRoute('/dashboard')">
                                Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-route="/products" onclick="navigateToRoute('/products')">
                                Products
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-route="/analytics" onclick="navigateToRoute('/analytics')">
                                Analytics
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-route="/settings" onclick="navigateToRoute('/settings')">
                                Settings
                            </a>
                        </li>
                    </ul>
                    
                    <!-- Route Content -->
                    <div class="route-content" id="route-content">
                        <!-- Content will be loaded here based on route -->
                        <div id="dashboard-content">
                            <h4>Dashboard</h4>
                            <p>Welcome to the dashboard! This content is loaded with route-specific code.</p>
                            
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="stats-widget" data-ui-component="StatsWidget">
                                        <h6>Users</h6>
                                        <h3 class="users-count">Loading...</h3>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="stats-widget" data-ui-component="StatsWidget">
                                        <h6>Orders</h6>
                                        <h3 class="orders-count">Loading...</h3>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="stats-widget" data-ui-component="StatsWidget">
                                        <h6>Revenue</h6>
                                        <h3 class="revenue-count">Loading...</h3>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <div class="activity-widget" data-ui-component="RecentActivity">
                                    <h5>Recent Activity</h5>
                                    <ul class="list-group activity-list">
                                        <li class="list-group-item">Loading...</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <button class="btn btn-primary mt-3" data-ui-click="refreshDashboard">
                                Refresh Dashboard
                            </button>
                        </div>
                        
                        <div id="products-content" style="display: none;">
                            <h4>Products</h4>
                            <p>Browse our product catalog with dynamic filtering.</p>
                            
                            <div class="product-filter" data-ui-component="ProductFilter">
                                <label for="category-filter">Filter by Category:</label>
                                <select id="category-filter" class="form-control">
                                    <option>Loading...</option>
                                </select>
                            </div>
                            
                            <div class="product-grid" data-ui-component="ProductGrid">
                                <div class="row">
                                    <div class="col-12 text-center">
                                        <p>Loading products...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div id="analytics-content" style="display: none;">
                            <h4>Analytics</h4>
                            <p>View detailed analytics and reports.</p>
                            
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="chart-widget" data-ui-component="ChartWidget">
                                        <h5>Traffic Overview</h5>
                                        <canvas width="400" height="200"></canvas>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="metrics-table" data-ui-component="MetricsTable">
                                        <h5>Key Metrics</h5>
                                        <table class="table table-sm">
                                            <thead>
                                                <tr>
                                                    <th>Metric</th>
                                                    <th>Value</th>
                                                    <th>Change</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr><td colspan="3">Loading...</td></tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-3">
                                <button class="btn btn-primary" data-ui-click="refreshMetrics">Refresh</button>
                                <button class="btn btn-success ms-2" data-ui-click="exportData">Export Data</button>
                            </div>
                        </div>
                        
                        <div id="settings-content" style="display: none;">
                            <h4>Settings</h4>
                            <p>Configure your application preferences.</p>
                            
                            <form data-ui-component="SettingsForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="app-name" class="form-label">Application Name</label>
                                            <input type="text" class="form-control" id="app-name" name="app_name" value="My App">
                                        </div>
                                        
                                        <div class="mb-3">
                                            <label for="email" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="email" name="email" value="user@example.com">
                                        </div>
                                        
                                        <div class="mb-3 form-check">
                                            <input type="checkbox" class="form-check-input" id="notifications" name="notifications" checked>
                                            <label class="form-check-label" for="notifications">
                                                Enable Notifications
                                            </label>
                                        </div>
                                    </div>
                                    
                                    <div class="col-md-6">
                                        <div class="mb-3" data-ui-component="ThemeSelector">
                                            <label for="theme" class="form-label">Theme</label>
                                            <select class="form-control" id="theme" name="theme">
                                                <option>Loading...</option>
                                            </select>
                                        </div>
                                        
                                        <div class="mb-3">
                                            <label for="language" class="form-label">Language</label>
                                            <select class="form-control" id="language" name="language">
                                                <option value="en">English</option>
                                                <option value="es">Spanish</option>
                                                <option value="fr">French</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mt-3">
                                    <button type="button" class="btn btn-primary" data-ui-click="saveSettings">Save Settings</button>
                                    <button type="button" class="btn btn-secondary ms-2" data-ui-click="resetSettings">Reset</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="demo-section">
                    <h3>Chunk Information</h3>
                    <p>Monitor code chunk loading and performance</p>
                    
                    <div>
                        <h5>Current Route</h5>
                        <div class="chunk-info">
                            <strong>Route:</strong> <span id="current-route">/dashboard</span><br>
                            <strong>Chunks:</strong> <span id="current-chunks">dashboard</span>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <h5>Loaded Chunks</h5>
                        <div class="chunk-info" id="loaded-chunks-list">
                            Loading...
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <h5>Chunk Manifest</h5>
                        <div class="chunk-info">
                            <small>
                                <strong>Available Routes:</strong><br>
                                • /dashboard (preload: true)<br>
                                • /products (lazy: true)<br>
                                • /analytics (lazy: true, deps: dashboard)<br>
                                • /settings (lazy: true)
                            </small>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <h5>Actions</h5>
                        <button class="btn btn-sm btn-outline-primary" onclick="preloadAllChunks()">
                            Preload All Chunks
                        </button>
                        <button class="btn btn-sm btn-outline-info ms-2" onclick="showChunkManifest()">
                            Show Manifest
                        </button>
                        <button class="btn btn-sm btn-outline-success mt-2" onclick="loadModalComponent()">
                            Load Modal Component
                        </button>
                    </div>
                </div>
                
                <div class="demo-section">
                    <h3>Performance Info</h3>
                    <div class="chunk-info" id="performance-info">
                        <strong>Page Load:</strong> <span id="page-load-time">-</span>ms<br>
                        <strong>Chunk Loads:</strong> <span id="chunk-load-count">0</span><br>
                        <strong>Total Size:</strong> <span id="total-size">-</span>KB
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <!-- Router code will be injected here -->
    <script>
        {{ router_code | safe }}
    </script>
    
    <script>
        let currentRoute = '/dashboard';
        let chunkLoadTimes = {};
        let startTime = performance.now();
        
        // Update performance info
        document.getElementById('page-load-time').textContent = Math.round(performance.now());
        
        function navigateToRoute(route) {
            console.log('Navigating to:', route);
            
            const startTime = performance.now();
            
            // Update active tab
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            document.querySelector(`[data-route="${route}"]`).classList.add('active');
            
            // Hide all content
            document.querySelectorAll('[id$="-content"]').forEach(content => {
                content.style.display = 'none';
            });
            
            // Show target content
            const contentId = route.substring(1) + '-content';
            const targetContent = document.getElementById(contentId);
            if (targetContent) {
                targetContent.style.display = 'block';
            }
            
            // Update route info
            currentRoute = route;
            document.getElementById('current-route').textContent = route;
            
            // Use NewUI router if available
            if (window.NewUIRouter) {
                window.NewUIRouter.navigateTo(route).then(() => {
                    const loadTime = Math.round(performance.now() - startTime);
                    chunkLoadTimes[route] = loadTime;
                    console.log(`Route ${route} loaded in ${loadTime}ms`);
                    updateChunkInfo();
                });
            } else {
                updateChunkInfo();
            }
        }
        
        function updateChunkInfo() {
            if (window.NewUIRouter) {
                const loadedChunks = window.NewUIRouter.getLoadedChunks();
                const chunksList = document.getElementById('loaded-chunks-list');
                
                chunksList.innerHTML = loadedChunks.map(chunk => 
                    `<div><strong>${chunk}</strong> ${chunkLoadTimes[chunk] ? `(${chunkLoadTimes[chunk]}ms)` : ''}</div>`
                ).join('') || 'None loaded yet';
                
                document.getElementById('chunk-load-count').textContent = loadedChunks.length;
                document.getElementById('current-chunks').textContent = 
                    window.NewUIRouter.getChunksForRoute ? 
                    window.NewUIRouter.getChunksForRoute(currentRoute).join(', ') : 
                    'Unknown';
            }
        }
        
        function preloadAllChunks() {
            if (window.NewUIChunks) {
                console.log('Preloading all chunks...');
                window.NewUIChunks.preload('products');
                window.NewUIChunks.preload('analytics');
                window.NewUIChunks.preload('settings');
                
                setTimeout(updateChunkInfo, 1000);
            }
        }
        
        function showChunkManifest() {
            fetch('/api/chunks/manifest')
                .then(response => response.json())
                .then(manifest => {
                    if (window.ModalComponent) {
                        window.ModalComponent.show('Chunk Manifest', 
                            `<pre>${JSON.stringify(manifest, null, 2)}</pre>`);
                    } else {
                        alert('Chunk Manifest:\\n' + JSON.stringify(manifest, null, 2));
                    }
                })
                .catch(error => {
                    console.error('Failed to load manifest:', error);
                });
        }
        
        function loadModalComponent() {
            if (window.NewUIChunks) {
                console.log('Loading modal component chunk...');
                window.NewUIChunks.loadComponent('Modal').then(() => {
                    console.log('Modal component loaded!');
                    if (window.ModalComponent) {
                        window.ModalComponent.show('Component Loaded!', 
                            'The modal component was loaded dynamically!');
                    }
                });
            }
        }
        
        // Listen for route changes
        window.addEventListener('routechange', function(event) {
            console.log('Route changed:', event.detail);
            updateChunkInfo();
        });
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateChunkInfo();
            
            // Simulate some size calculations
            setTimeout(() => {
                document.getElementById('total-size').textContent = 
                    Math.round(Math.random() * 100 + 50);
            }, 2000);
            
            console.log('Route-based code splitting demo initialized');
        });
        
        // Helper function for notifications (available globally)
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show position-fixed" 
                     style="top: 20px; right: 20px; z-index: 1000;" role="alert">
                    ${message}
                    <button type="button" class="btn-close" onclick="this.closest('.alert').remove()"></button>
                </div>
            `;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 3000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, router_code=router.generate_client_code())

if __name__ == '__main__':
    print("\\n" + "="*50)
    print("Route-based Code Splitting Demo")
    print("="*50)
    print("Open http://localhost:5011")
    print("Features:")
    print("- Dynamic loading of route-specific JavaScript and CSS")
    print("- Code chunk management with dependencies")
    print("- Client-side routing with lazy loading")
    print("- Component-based code splitting")
    print("- Chunk manifest and debugging tools")
    print("- Performance monitoring")
    print("- Preloading and caching strategies")
    print("="*50 + "\\n")
    app.run(debug=True, port=5011)