"""
Example application demonstrating NewUI state stores for complex applications
"""

from flask import Flask, render_template_string, request, jsonify
from newui import NewUI
from newui import components as ui
from newui.stores import *
import json
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'
newui = NewUI(app)

# Initialize stores for different parts of the application
user_store = create_store('users', ComponentStore, {
    'users': [
        {'id': 1, 'name': 'Alice Johnson', 'email': 'alice@example.com', 'role': 'admin', 'active': True},
        {'id': 2, 'name': 'Bob Smith', 'email': 'bob@example.com', 'role': 'user', 'active': True},
        {'id': 3, 'name': 'Charlie Brown', 'email': 'charlie@example.com', 'role': 'user', 'active': False},
    ],
    'current_user': None,
    'filter': 'all',  # all, active, inactive
    'search_term': '',
    'loading': False,
    'error': None
})

shopping_store = create_store('shopping', ComponentStore, {
    'products': [
        {'id': 1, 'name': 'Laptop', 'price': 999.99, 'category': 'Electronics', 'stock': 5},
        {'id': 2, 'name': 'Coffee Mug', 'price': 12.99, 'category': 'Home', 'stock': 50},
        {'id': 3, 'name': 'Book', 'price': 24.99, 'category': 'Education', 'stock': 0},
        {'id': 4, 'name': 'Headphones', 'price': 89.99, 'category': 'Electronics', 'stock': 12},
    ],
    'cart': {
        'items': [],
        'total': 0.0,
        'discount': 0.0,
        'tax_rate': 0.08
    },
    'ui': {
        'cart_open': False,
        'loading_product': None,
        'notification': None
    }
})

analytics_store = create_store('analytics', SimpleStore, {
    'stats': {
        'page_views': 1250,
        'unique_visitors': 340,
        'bounce_rate': 0.42,
        'avg_session_duration': 245
    },
    'real_time': {
        'active_users': 23,
        'current_page_views': 8,
        'events_last_hour': 156
    },
    'history': [],
    'auto_update': True
})

# Add middleware to stores
user_store.add_middleware(logging_middleware)
shopping_store.add_middleware(logging_middleware)
analytics_store.add_middleware(validation_middleware)

# Custom middleware for shopping cart calculations
def cart_calculation_middleware(state, action):
    """Automatically recalculate cart totals when items change"""
    if action.type in ['ADD_TO_CART', 'REMOVE_FROM_CART', 'UPDATE_QUANTITY']:
        # This will be applied after the reducer runs
        return action
    return action

shopping_store.add_middleware(cart_calculation_middleware)

# Custom reducer for shopping store
class ShoppingStore(ComponentStore):
    def reduce(self, state, action):
        if action.type == 'ADD_TO_CART':
            product_id = action.payload.get('product_id')
            quantity = action.payload.get('quantity', 1)
            
            # Find product
            product = next((p for p in state['products'] if p['id'] == product_id), None)
            if not product or product['stock'] < quantity:
                return state
            
            # Add to cart
            new_state = copy.deepcopy(state)
            cart_item = next((item for item in new_state['cart']['items'] if item['product_id'] == product_id), None)
            
            if cart_item:
                cart_item['quantity'] += quantity
            else:
                new_state['cart']['items'].append({
                    'product_id': product_id,
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity
                })
            
            # Update product stock
            product_in_state = next(p for p in new_state['products'] if p['id'] == product_id)
            product_in_state['stock'] -= quantity
            
            # Recalculate total
            new_state['cart']['total'] = sum(item['price'] * item['quantity'] for item in new_state['cart']['items'])
            
            # Show notification
            new_state['ui']['notification'] = f"Added {product['name']} to cart"
            
            return new_state
        
        elif action.type == 'REMOVE_FROM_CART':
            product_id = action.payload.get('product_id')
            
            new_state = copy.deepcopy(state)
            cart_items = new_state['cart']['items']
            
            # Find and remove item
            item_to_remove = next((item for item in cart_items if item['product_id'] == product_id), None)
            if item_to_remove:
                # Restore stock
                product = next(p for p in new_state['products'] if p['id'] == product_id)
                product['stock'] += item_to_remove['quantity']
                
                # Remove from cart
                cart_items.remove(item_to_remove)
                
                # Recalculate total
                new_state['cart']['total'] = sum(item['price'] * item['quantity'] for item in cart_items)
                
                # Show notification
                new_state['ui']['notification'] = f"Removed {item_to_remove['name']} from cart"
            
            return new_state
        
        elif action.type == 'CLEAR_CART':
            new_state = copy.deepcopy(state)
            
            # Restore all stock
            for item in new_state['cart']['items']:
                product = next(p for p in new_state['products'] if p['id'] == item['product_id'])
                product['stock'] += item['quantity']
            
            # Clear cart
            new_state['cart']['items'] = []
            new_state['cart']['total'] = 0.0
            new_state['ui']['notification'] = "Cart cleared"
            
            return new_state
        
        elif action.type == 'TOGGLE_CART':
            new_state = copy.deepcopy(state)
            new_state['ui']['cart_open'] = not new_state['ui']['cart_open']
            return new_state
        
        elif action.type == 'CLEAR_NOTIFICATION':
            new_state = copy.deepcopy(state)
            new_state['ui']['notification'] = None
            return new_state
        
        # Fall back to parent reducer
        return super().reduce(state, action)

# Replace shopping store with custom implementation
store_manager.stores['shopping'] = ShoppingStore(shopping_store.get_state())

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI State Stores Demo</title>
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
        .store-monitor {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
        }
        .cart-sidebar {
            position: fixed;
            right: -400px;
            top: 0;
            width: 400px;
            height: 100vh;
            background: white;
            box-shadow: -2px 0 5px rgba(0,0,0,0.1);
            transition: right 0.3s ease;
            z-index: 1000;
            overflow-y: auto;
        }
        .cart-sidebar.open {
            right: 0;
        }
        .cart-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.5);
            z-index: 999;
            display: none;
        }
        .cart-overlay.show {
            display: block;
        }
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1001;
            min-width: 300px;
        }
        .stats-card {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .stats-value {
            font-size: 2rem;
            font-weight: bold;
        }
        .real-time-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .action-log {
            max-height: 200px;
            overflow-y: auto;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 10px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <div class="container-fluid mt-3">
        <h1>State Stores Demo</h1>
        <p class="text-muted">Centralized state management for complex applications</p>
        
        <div class="row">
            <!-- User Management Store -->
            <div class="col-lg-4">
                <div class="demo-section">
                    <h3>User Management Store</h3>
                    <p>Centralized user state with filtering and search</p>
                    
                    <div data-ui-component="user-manager" 
                         data-ui-state='{"filter": "all", "search_term": "", "loading": false}'>
                        
                        <div class="mb-3">
                            <div class="row">
                                <div class="col-8">
                                    {{ ui.input("search", placeholder="Search users...", 
                                              bind="search_term", class_="form-control-sm") }}
                                </div>
                                <div class="col-4">
                                    {{ ui.select("filter", 
                                               [{"value": "all", "text": "All"},
                                                {"value": "active", "text": "Active"},
                                                {"value": "inactive", "text": "Inactive"}],
                                               bind="filter", class_="form-control-sm") }}
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <button class="btn btn-primary btn-sm" data-ui-click="addUser">Add User</button>
                            <button class="btn btn-secondary btn-sm ms-2" data-ui-click="refreshUsers">Refresh</button>
                        </div>
                        
                        <div id="user-list">
                            <!-- Users will be populated here by JavaScript -->
                        </div>
                        
                        <div class="mt-3">
                            <small class="text-muted">
                                Store State: <span id="user-store-info"></span>
                            </small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Shopping Cart Store -->
            <div class="col-lg-4">
                <div class="demo-section">
                    <h3>Shopping Cart Store</h3>
                    <p>E-commerce state with automatic calculations</p>
                    
                    <div data-ui-component="product-catalog" data-ui-state='{}'>
                        <div class="mb-3">
                            <button class="btn btn-outline-primary btn-sm" data-ui-click="toggleCart">
                                Cart (<span id="cart-count">0</span>) - $<span id="cart-total">0.00</span>
                            </button>
                        </div>
                        
                        <div id="product-list" class="row">
                            <!-- Products will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Analytics Store -->
            <div class="col-lg-4">
                <div class="demo-section">
                    <h3>Analytics Store</h3>
                    <p>Real-time analytics with automatic updates</p>
                    
                    <div data-ui-component="analytics-dashboard" 
                         data-ui-state='{"auto_update": true}'>
                        
                        <div class="mb-3">
                            <span class="real-time-indicator"></span>
                            <small class="ms-2">Live Data</small>
                            <button class="btn btn-sm btn-outline-secondary ms-2" 
                                    data-ui-click="toggleAutoUpdate">
                                Toggle Auto-Update
                            </button>
                        </div>
                        
                        <div id="analytics-stats">
                            <!-- Stats will be populated here -->
                        </div>
                        
                        <div class="mt-3">
                            <h6>Real-time Metrics</h6>
                            <div id="realtime-stats">
                                <!-- Real-time stats here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="demo-section">
                    <h3>Store Monitoring & Debugging</h3>
                    <p>Monitor all stores and their state changes</p>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <h5>User Store State</h5>
                            <div class="store-monitor" id="user-store-monitor"></div>
                        </div>
                        <div class="col-md-4">
                            <h5>Shopping Store State</h5>
                            <div class="store-monitor" id="shopping-store-monitor"></div>
                        </div>
                        <div class="col-md-4">
                            <h5>Analytics Store State</h5>
                            <div class="store-monitor" id="analytics-store-monitor"></div>
                        </div>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-12">
                            <h5>Action Log</h5>
                            <button class="btn btn-sm btn-secondary mb-2" onclick="clearActionLog()">Clear Log</button>
                            <div class="action-log" id="action-log"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Shopping Cart Sidebar -->
    <div class="cart-overlay" id="cart-overlay" onclick="closeCart()"></div>
    <div class="cart-sidebar" id="cart-sidebar">
        <div class="p-3">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Shopping Cart</h4>
                <button class="btn-close" onclick="closeCart()"></button>
            </div>
            
            <div id="cart-items">
                <!-- Cart items populated by JavaScript -->
            </div>
            
            <div class="mt-3 pt-3 border-top">
                <div class="d-flex justify-content-between">
                    <strong>Total: $<span id="cart-sidebar-total">0.00</span></strong>
                </div>
                <button class="btn btn-success w-100 mt-2" data-ui-click="checkout">Checkout</button>
                <button class="btn btn-outline-danger w-100 mt-2" data-ui-click="clearCart">Clear Cart</button>
            </div>
        </div>
    </div>
    
    <!-- Notification Toast -->
    <div class="notification" id="notification" style="display: none;">
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <span id="notification-text"></span>
            <button type="button" class="btn-close" onclick="hideNotification()"></button>
        </div>
    </div>
    
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Store state management
        let stores = {
            users: {{ user_state | tojson }},
            shopping: {{ shopping_state | tojson }},
            analytics: {{ analytics_state | tojson }}
        };
        
        let actionLog = [];
        
        // Store subscriptions and updates
        function subscribeToStores() {
            // Subscribe to store changes via polling (in real app, use WebSocket)
            setInterval(updateStoresFromServer, 2000);
        }
        
        function updateStoresFromServer() {
            fetch('/api/stores')
                .then(response => response.json())
                .then(data => {
                    stores = data;
                    updateAllComponents();
                    updateStoreMonitors();
                });
        }
        
        function dispatchAction(storeName, actionType, payload = {}) {
            const action = {
                type: actionType,
                payload: payload,
                timestamp: Date.now()
            };
            
            logAction(storeName, action);
            
            return fetch('/api/stores/dispatch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    store: storeName,
                    action: action
                })
            })
            .then(response => response.json())
            .then(data => {
                stores[storeName] = data;
                updateComponentsForStore(storeName);
                updateStoreMonitors();
                return data;
            })
            .catch(error => {
                console.error('Store dispatch error:', error);
            });
        }
        
        function logAction(storeName, action) {
            actionLog.unshift({
                store: storeName,
                action: action,
                timestamp: new Date().toLocaleTimeString()
            });
            
            // Keep only last 50 actions
            if (actionLog.length > 50) {
                actionLog = actionLog.slice(0, 50);
            }
            
            updateActionLog();
        }
        
        function updateActionLog() {
            const logEl = document.getElementById('action-log');
            logEl.innerHTML = actionLog.map(entry => 
                `<div>[${entry.timestamp}] ${entry.store}/${entry.action.type}: ${JSON.stringify(entry.action.payload)}</div>`
            ).join('');
        }
        
        function clearActionLog() {
            actionLog = [];
            updateActionLog();
        }
        
        function updateStoreMonitors() {
            document.getElementById('user-store-monitor').textContent = JSON.stringify(stores.users, null, 2);
            document.getElementById('shopping-store-monitor').textContent = JSON.stringify(stores.shopping, null, 2);
            document.getElementById('analytics-store-monitor').textContent = JSON.stringify(stores.analytics, null, 2);
        }
        
        function updateAllComponents() {
            updateUserList();
            updateProductList();
            updateAnalytics();
            updateCart();
        }
        
        function updateComponentsForStore(storeName) {
            switch(storeName) {
                case 'users':
                    updateUserList();
                    break;
                case 'shopping':
                    updateProductList();
                    updateCart();
                    break;
                case 'analytics':
                    updateAnalytics();
                    break;
            }
        }
        
        function updateUserList() {
            const userList = document.getElementById('user-list');
            const users = stores.users.users || [];
            const filter = stores.users.filter || 'all';
            const searchTerm = stores.users.search_term || '';
            
            let filteredUsers = users;
            
            // Apply filter
            if (filter !== 'all') {
                filteredUsers = users.filter(user => 
                    filter === 'active' ? user.active : !user.active
                );
            }
            
            // Apply search
            if (searchTerm) {
                filteredUsers = filteredUsers.filter(user =>
                    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    user.email.toLowerCase().includes(searchTerm.toLowerCase())
                );
            }
            
            userList.innerHTML = filteredUsers.map(user => `
                <div class="card card-body mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${user.name}</strong><br>
                            <small class="text-muted">${user.email}</small><br>
                            <span class="badge bg-${user.active ? 'success' : 'secondary'}">${user.active ? 'Active' : 'Inactive'}</span>
                            <span class="badge bg-primary ms-1">${user.role}</span>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-primary" onclick="editUser(${user.id})">Edit</button>
                            <button class="btn btn-sm btn-outline-danger ms-1" onclick="deleteUser(${user.id})">Delete</button>
                        </div>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('user-store-info').textContent = `${filteredUsers.length} of ${users.length} users`;
        }
        
        function updateProductList() {
            const productList = document.getElementById('product-list');
            const products = stores.shopping.products || [];
            
            productList.innerHTML = products.map(product => `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${product.name}</h6>
                            <p class="card-text">
                                <strong>$${product.price.toFixed(2)}</strong><br>
                                <small class="text-muted">${product.category}</small><br>
                                <span class="badge bg-${product.stock > 0 ? 'success' : 'danger'}">
                                    ${product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                                </span>
                            </p>
                            <button class="btn btn-primary btn-sm" 
                                    onclick="addToCart(${product.id})" 
                                    ${product.stock === 0 ? 'disabled' : ''}>
                                Add to Cart
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateCart() {
            const cart = stores.shopping.cart || {items: [], total: 0};
            const notification = stores.shopping.ui?.notification;
            
            // Update cart count and total
            const itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cart-count').textContent = itemCount;
            document.getElementById('cart-total').textContent = cart.total.toFixed(2);
            document.getElementById('cart-sidebar-total').textContent = cart.total.toFixed(2);
            
            // Update cart items in sidebar
            const cartItems = document.getElementById('cart-items');
            cartItems.innerHTML = cart.items.map(item => `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                    <div>
                        <strong>${item.name}</strong><br>
                        <small>$${item.price.toFixed(2)} × ${item.quantity}</small>
                    </div>
                    <div>
                        <strong>$${(item.price * item.quantity).toFixed(2)}</strong>
                        <button class="btn btn-sm btn-outline-danger ms-2" onclick="removeFromCart(${item.product_id})">×</button>
                    </div>
                </div>
            `).join('');
            
            // Show notification if present
            if (notification) {
                showNotification(notification);
                // Clear notification after showing
                setTimeout(() => {
                    dispatchAction('shopping', 'CLEAR_NOTIFICATION');
                }, 3000);
            }
        }
        
        function updateAnalytics() {
            const stats = stores.analytics.stats || {};
            const realTime = stores.analytics.real_time || {};
            
            // Update main stats
            document.getElementById('analytics-stats').innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <div class="stats-card bg-primary text-white">
                            <div>Page Views</div>
                            <div class="stats-value">${stats.page_views || 0}</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="stats-card bg-success text-white">
                            <div>Unique Visitors</div>
                            <div class="stats-value">${stats.unique_visitors || 0}</div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-6">
                        <div class="stats-card bg-warning text-dark">
                            <div>Bounce Rate</div>
                            <div class="stats-value">${Math.round((stats.bounce_rate || 0) * 100)}%</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="stats-card bg-info text-white">
                            <div>Avg Session</div>
                            <div class="stats-value">${Math.round((stats.avg_session_duration || 0) / 60)}m</div>
                        </div>
                    </div>
                </div>
            `;
            
            // Update real-time stats
            document.getElementById('realtime-stats').innerHTML = `
                <div class="row">
                    <div class="col-4">
                        <strong>${realTime.active_users || 0}</strong><br>
                        <small>Active Users</small>
                    </div>
                    <div class="col-4">
                        <strong>${realTime.current_page_views || 0}</strong><br>
                        <small>Page Views</small>
                    </div>
                    <div class="col-4">
                        <strong>${realTime.events_last_hour || 0}</strong><br>
                        <small>Events/Hour</small>
                    </div>
                </div>
            `;
        }
        
        // Event handlers
        NewUI.registerHandler('addUser', function() {
            const name = prompt('Enter user name:');
            const email = prompt('Enter user email:');
            if (name && email) {
                const newUser = {
                    id: Date.now(),
                    name: name,
                    email: email,
                    role: 'user',
                    active: true
                };
                dispatchAction('users', 'APPEND_TO_LIST', {path: 'users', item: newUser});
            }
        });
        
        NewUI.registerHandler('refreshUsers', function() {
            dispatchAction('users', 'SET_VALUE', {path: 'loading', value: true});
            setTimeout(() => {
                dispatchAction('users', 'SET_VALUE', {path: 'loading', value: false});
            }, 1000);
        });
        
        NewUI.registerHandler('toggleCart', function() {
            dispatchAction('shopping', 'TOGGLE_CART');
            const cart = stores.shopping.ui?.cart_open;
            document.getElementById('cart-sidebar').classList.toggle('open', cart);
            document.getElementById('cart-overlay').classList.toggle('show', cart);
        });
        
        NewUI.registerHandler('clearCart', function() {
            dispatchAction('shopping', 'CLEAR_CART');
        });
        
        NewUI.registerHandler('checkout', function() {
            alert('Checkout functionality would be implemented here!');
            dispatchAction('shopping', 'CLEAR_CART');
            closeCart();
        });
        
        NewUI.registerHandler('toggleAutoUpdate', function() {
            const current = stores.analytics.auto_update;
            dispatchAction('analytics', 'TOGGLE_BOOLEAN', {path: 'auto_update'});
        });
        
        // Utility functions
        function addToCart(productId) {
            dispatchAction('shopping', 'ADD_TO_CART', {product_id: productId, quantity: 1});
        }
        
        function removeFromCart(productId) {
            dispatchAction('shopping', 'REMOVE_FROM_CART', {product_id: productId});
        }
        
        function editUser(userId) {
            alert(`Edit user ${userId} functionality would be implemented here!`);
        }
        
        function deleteUser(userId) {
            if (confirm('Are you sure you want to delete this user?')) {
                const userIndex = stores.users.users.findIndex(u => u.id === userId);
                if (userIndex !== -1) {
                    dispatchAction('users', 'REMOVE_FROM_LIST', {path: 'users', index: userIndex});
                }
            }
        }
        
        function closeCart() {
            document.getElementById('cart-sidebar').classList.remove('open');
            document.getElementById('cart-overlay').classList.remove('show');
            dispatchAction('shopping', 'SET_VALUE', {path: 'ui.cart_open', value: false});
        }
        
        function showNotification(message) {
            document.getElementById('notification-text').textContent = message;
            document.getElementById('notification').style.display = 'block';
        }
        
        function hideNotification() {
            document.getElementById('notification').style.display = 'none';
        }
        
        // Data binding handlers
        document.addEventListener('input', function(e) {
            if (e.target.name === 'search') {
                dispatchAction('users', 'SET_VALUE', {path: 'search_term', value: e.target.value});
            }
        });
        
        document.addEventListener('change', function(e) {
            if (e.target.name === 'filter') {
                dispatchAction('users', 'SET_VALUE', {path: 'filter', value: e.target.value});
            }
        });
        
        // Simulate real-time analytics updates
        function simulateAnalyticsUpdates() {
            if (stores.analytics.auto_update) {
                // Randomly update some stats
                const updates = {
                    'real_time.active_users': Math.floor(Math.random() * 50) + 10,
                    'real_time.current_page_views': Math.floor(Math.random() * 20) + 1,
                    'real_time.events_last_hour': Math.floor(Math.random() * 200) + 100
                };
                
                Object.entries(updates).forEach(([path, value]) => {
                    dispatchAction('analytics', 'SET_VALUE', {path, value});
                });
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            subscribeToStores();
            updateAllComponents();
            updateStoreMonitors();
            
            // Start analytics simulation
            setInterval(simulateAnalyticsUpdates, 5000);
            
            console.log('State stores demo initialized');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE,
                                ui=ui,
                                user_state=user_store.get_state(),
                                shopping_state=shopping_store.get_state(),
                                analytics_state=analytics_store.get_state())

@app.route('/api/stores')
def get_all_stores():
    return jsonify({
        'users': user_store.get_state(),
        'shopping': shopping_store.get_state(),
        'analytics': analytics_store.get_state()
    })

@app.route('/api/stores/dispatch', methods=['POST'])
def dispatch_to_store():
    data = request.json
    store_name = data.get('store')
    action_data = data.get('action')
    
    store = get_store(store_name)
    if not store:
        return jsonify({'error': 'Store not found'}), 404
    
    action = StateAction(
        type=action_data['type'],
        payload=action_data.get('payload', {}),
        timestamp=action_data.get('timestamp', time.time())
    )
    
    new_state = store.dispatch(action)
    return jsonify(new_state)

if __name__ == '__main__':
    print("\\n" + "="*50)
    print("State Stores Demo")
    print("="*50)
    print("Open http://localhost:5010")
    print("Features:")
    print("- Centralized state management with multiple stores")
    print("- User management store with filtering and search")
    print("- Shopping cart store with automatic calculations")
    print("- Analytics store with real-time updates")
    print("- Store monitoring and debugging tools")
    print("- Action logging and state inspection")
    print("- Middleware for logging, validation, and custom logic")
    print("="*50 + "\\n")
    app.run(debug=True, port=5010)