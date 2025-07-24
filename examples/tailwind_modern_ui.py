"""
Modern UI with Tailwind CSS v4.0 and Flask-NewUI

This example demonstrates how to build a beautiful, modern interface using
Tailwind CSS v4.0 with Flask-NewUI's reactive components.

Features:
- Tailwind CSS v4.0 with CDN setup
- Dark mode support
- Responsive design
- Modern UI components (cards, modals, notifications)
- Smooth animations and transitions
- Interactive dashboard layout
"""

from flask import Flask, render_template_string, request, jsonify
from newui import NewUI
from newui import components as ui
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tailwind-demo-secret-key'
newui = NewUI(app)

# Sample data for dashboard
dashboard_data = {
    'stats': [
        {'label': 'Total Users', 'value': '12,543', 'change': '+12%', 'trend': 'up'},
        {'label': 'Revenue', 'value': '$54,321', 'change': '+23%', 'trend': 'up'},
        {'label': 'Active Projects', 'value': '89', 'change': '-5%', 'trend': 'down'},
        {'label': 'Performance', 'value': '98.5%', 'change': '+2%', 'trend': 'up'},
    ],
    'notifications': [],
    'tasks': [
        {'id': 1, 'title': 'Review pull requests', 'completed': False, 'priority': 'high'},
        {'id': 2, 'title': 'Update documentation', 'completed': True, 'priority': 'medium'},
        {'id': 3, 'title': 'Deploy to production', 'completed': False, 'priority': 'high'},
        {'id': 4, 'title': 'Team meeting', 'completed': False, 'priority': 'low'},
    ]
}

TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Dashboard - Tailwind CSS v4.0 + Flask-NewUI</title>
    
    <!-- Tailwind CSS v4.0 -->
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    
    <!-- NewUI CSS -->
    <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    
    <!-- Tailwind v4.0 Custom Styles -->
    <style>
        @import "tailwindcss";
        
        /* Custom theme configuration for v4.0 */
        @theme {
            --color-primary-50: #eff6ff;
            --color-primary-500: #3b82f6;
            --color-primary-600: #2563eb;
            --color-primary-700: #1d4ed8;
            
            --animate-fade-in: fadeIn 0.5s ease-in-out;
            --animate-slide-up: slideUp 0.3s ease-out;
        }
        
        /* Custom animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in {
            animation: var(--animate-fade-in);
        }
        
        .animate-slide-up {
            animation: var(--animate-slide-up);
        }
        
        /* Smooth transitions for all interactive elements */
        * {
            transition: all 0.2s ease;
        }
    </style>
</head>
<body class="h-full bg-gray-50 dark:bg-gray-900">
    <!-- Main Container -->
    <div class="min-h-full">
        <!-- Navigation -->
        <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
            <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div class="flex h-16 justify-between items-center">
                    <div class="flex items-center">
                        <h1 class="text-xl font-semibold text-gray-900 dark:text-white">
                            Flask-NewUI + Tailwind v4.0
                        </h1>
                    </div>
                    
                    <!-- Dark mode toggle -->
                    <div class="flex items-center space-x-4">
                        <button onclick="toggleDarkMode()" 
                                class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                                id="theme-toggle">
                            <!-- Sun icon (for dark mode) -->
                            <svg id="sun-icon" class="w-5 h-5 text-gray-600 dark:text-gray-400 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                            <!-- Moon icon (for light mode) -->
                            <svg id="moon-icon" class="w-5 h-5 text-gray-600 dark:text-gray-400 block dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                            </svg>
                        </button>
                        
                        <!-- Notification bell -->
                        <div class="relative" data-ui-component="notifications" 
                             data-ui-state='{"count": {{ notifications | length }}, "open": false}'>
                            <button data-ui-click="toggleNotifications"
                                    class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 relative">
                                <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                                </svg>
                                <span data-ui-show="count > 0" 
                                      class="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center"
                                      data-ui-bind="count">{{ notifications | length }}</span>
                            </button>
                            
                            <!-- Notification dropdown -->
                            <div data-ui-show="open" 
                                 class="absolute right-0 mt-2 w-80 rounded-lg bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                                <div class="p-4">
                                    <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Notifications</h3>
                                    <div id="notification-list" class="space-y-2">
                                        <!-- Notifications will be rendered here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
        
        <!-- Main Content -->
        <main class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
            <!-- Stats Grid -->
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                {% for stat in stats %}
                <div class="bg-white dark:bg-gray-800 overflow-hidden rounded-lg shadow animate-fade-in"
                     style="animation-delay: {{ loop.index0 * 100 }}ms">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-1">
                                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    {{ stat.label }}
                                </p>
                                <p class="mt-1 text-3xl font-semibold text-gray-900 dark:text-white">
                                    {{ stat.value }}
                                </p>
                            </div>
                            <div class="ml-5">
                                <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium
                                           {% if stat.trend == 'up' %}bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200
                                           {% else %}bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200{% endif %}">
                                    {{ stat.change }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Main Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Task List -->
                <div class="lg:col-span-2">
                    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
                        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h2 class="text-lg font-medium text-gray-900 dark:text-white">Tasks</h2>
                        </div>
                        
                        <div class="p-6" data-ui-component="task-manager" 
                             data-ui-state='{"tasks": {{ tasks | tojson }}, "filter": "all"}'>
                            
                            <!-- Filter Tabs -->
                            <div class="flex space-x-1 mb-4">
                                <button data-ui-click="filterTasks" data-filter="all"
                                        class="px-4 py-2 rounded-lg text-sm font-medium 
                                               bg-primary-500 text-white">
                                    All Tasks
                                </button>
                                <button data-ui-click="filterTasks" data-filter="active"
                                        class="px-4 py-2 rounded-lg text-sm font-medium 
                                               text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                                    Active
                                </button>
                                <button data-ui-click="filterTasks" data-filter="completed"
                                        class="px-4 py-2 rounded-lg text-sm font-medium 
                                               text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                                    Completed
                                </button>
                            </div>
                            
                            <!-- Task Input -->
                            <form data-ui-submit="addTask" class="mb-4">
                                <div class="flex space-x-2">
                                    <input name="title" 
                                           type="text" 
                                           placeholder="Add a new task..."
                                           required
                                           class="flex-1 rounded-lg border-gray-300 dark:border-gray-600 
                                                  dark:bg-gray-700 dark:text-white shadow-sm 
                                                  focus:border-primary-500 focus:ring-primary-500">
                                    <select name="priority" 
                                            class="rounded-lg border-gray-300 dark:border-gray-600 
                                                   dark:bg-gray-700 dark:text-white shadow-sm">
                                        <option value="low">Low</option>
                                        <option value="medium" selected>Medium</option>
                                        <option value="high">High</option>
                                    </select>
                                    {{ ui.button("Add Task", type="submit", 
                                               class_="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500") }}
                                </div>
                            </form>
                            
                            <!-- Task List -->
                            <div id="task-list" class="space-y-2">
                                <!-- Tasks will be rendered here -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Activity Feed -->
                <div class="lg:col-span-1">
                    <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
                        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h2 class="text-lg font-medium text-gray-900 dark:text-white">Recent Activity</h2>
                        </div>
                        
                        <div class="p-6" data-ui-component="activity-feed" 
                             data-ui-state='{"activities": []}'>
                            <div id="activity-list" class="space-y-4">
                                <p class="text-sm text-gray-500 dark:text-gray-400">No recent activity</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Actions -->
                    <div class="mt-8 bg-white dark:bg-gray-800 shadow rounded-lg">
                        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                            <h2 class="text-lg font-medium text-gray-900 dark:text-white">Quick Actions</h2>
                        </div>
                        
                        <div class="p-6 space-y-3">
                            <button data-ui-click="showModal" 
                                    class="w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500">
                                Create New Project
                            </button>
                            <button data-ui-click="exportData"
                                    class="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600">
                                Export Data
                            </button>
                            <button data-ui-click="showNotification"
                                    class="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                                Test Notification
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <!-- Modal Template -->
    <div id="modal" class="hidden fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-center justify-center min-h-screen px-4">
            <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
            
            <div class="relative bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6 animate-fade-in">
                <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    Create New Project
                </h3>
                
                <form data-ui-submit="createProject">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Project Name
                            </label>
                            <input type="text" name="name" required
                                   class="mt-1 block w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Description
                            </label>
                            <textarea name="description" rows="3"
                                      class="mt-1 block w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm"></textarea>
                        </div>
                    </div>
                    
                    <div class="mt-6 flex space-x-3">
                        <button type="submit"
                                class="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
                            Create Project
                        </button>
                        <button type="button" onclick="hideModal()"
                                class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Toast Notification Container -->
    <div id="toast-container" class="fixed bottom-4 right-4 z-50 space-y-2">
        <!-- Toasts will be added here -->
    </div>
    
    <!-- Scripts -->
    <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
    <script>
        // Dark mode toggle
        function toggleDarkMode() {
            const html = document.documentElement;
            const isDark = html.classList.contains('dark');
            
            if (isDark) {
                html.classList.remove('dark');
                localStorage.setItem('darkMode', 'false');
            } else {
                html.classList.add('dark');
                localStorage.setItem('darkMode', 'true');
            }
            
            updateThemeIcon();
        }
        
        function updateThemeIcon() {
            const isDark = document.documentElement.classList.contains('dark');
            const sunIcon = document.getElementById('sun-icon');
            const moonIcon = document.getElementById('moon-icon');
            
            if (isDark) {
                sunIcon.classList.remove('hidden');
                sunIcon.classList.add('block');
                moonIcon.classList.remove('block');
                moonIcon.classList.add('hidden');
            } else {
                sunIcon.classList.remove('block');
                sunIcon.classList.add('hidden');
                moonIcon.classList.remove('hidden');
                moonIcon.classList.add('block');
            }
        }
        
        // Initialize theme on page load
        function initializeTheme() {
            const savedTheme = localStorage.getItem('darkMode');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            // Use saved preference, or system preference, or default to light
            const shouldBeDark = savedTheme === 'true' || (savedTheme === null && prefersDark);
            
            if (shouldBeDark) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
            
            updateThemeIcon();
        }
        
        // Modal functions
        function showModal() {
            document.getElementById('modal').classList.remove('hidden');
        }
        
        function hideModal() {
            document.getElementById('modal').classList.add('hidden');
        }
        
        // Toast notification
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            const bgColor = type === 'success' ? 'bg-green-500' : 
                           type === 'error' ? 'bg-red-500' : 'bg-blue-500';
            
            toast.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-lg animate-fade-in`;
            toast.textContent = message;
            
            document.getElementById('toast-container').appendChild(toast);
            
            setTimeout(() => {
                toast.classList.add('opacity-0');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
        
        // Task rendering
        function renderTasks() {
            const taskManager = document.querySelector('[data-ui-component="task-manager"]');
            const componentId = taskManager.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            const taskList = document.getElementById('task-list');
            
            let tasks = state.tasks || [];
            const filter = state.filter || 'all';
            
            if (filter === 'active') {
                tasks = tasks.filter(t => !t.completed);
            } else if (filter === 'completed') {
                tasks = tasks.filter(t => t.completed);
            }
            
            taskList.innerHTML = tasks.map(task => `
                <div class="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 
                            hover:bg-gray-50 dark:hover:bg-gray-700 animate-fade-in">
                    <input type="checkbox" 
                           ${task.completed ? 'checked' : ''}
                           onchange="toggleTask(${task.id})"
                           class="h-4 w-4 text-primary-600 rounded focus:ring-primary-500">
                    <div class="ml-3 flex-1">
                        <p class="text-sm font-medium text-gray-900 dark:text-white 
                                  ${task.completed ? 'line-through opacity-50' : ''}">
                            ${task.title}
                        </p>
                    </div>
                    <span class="px-2 py-1 text-xs rounded-full
                               ${task.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                                 task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                                 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'}">
                        ${task.priority}
                    </span>
                    <button onclick="deleteTask(${task.id})" 
                            class="ml-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            `).join('');
        }
        
        // NewUI Handlers
        NewUI.registerHandler('toggleNotifications', function(element, event) {
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            NewUI.setStateValue(componentId, 'open', !state.open);
        });
        
        NewUI.registerHandler('filterTasks', function(element, event) {
            const filter = element.getAttribute('data-filter');
            const componentId = NewUI.getComponentId(element);
            
            // Update button styles
            element.parentElement.querySelectorAll('button').forEach(btn => {
                btn.classList.remove('bg-primary-500', 'text-white');
                btn.classList.add('text-gray-700', 'dark:text-gray-300', 'hover:bg-gray-100', 'dark:hover:bg-gray-700');
            });
            element.classList.remove('text-gray-700', 'dark:text-gray-300', 'hover:bg-gray-100', 'dark:hover:bg-gray-700');
            element.classList.add('bg-primary-500', 'text-white');
            
            NewUI.setStateValue(componentId, 'filter', filter);
            renderTasks();
        });
        
        NewUI.registerHandler('addTask', function(element, event) {
            const formData = new FormData(element);
            const componentId = NewUI.getComponentId(element);
            const state = NewUI.state[componentId];
            
            const newTask = {
                id: Date.now(),
                title: formData.get('title'),
                priority: formData.get('priority'),
                completed: false
            };
            
            fetch('/api/tasks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(newTask)
            })
            .then(response => response.json())
            .then(data => {
                const tasks = [...(state.tasks || []), data.task];
                NewUI.setStateValue(componentId, 'tasks', tasks);
                renderTasks();
                element.reset();
                showToast('Task added successfully!', 'success');
                
                // Add activity
                addActivity(`Created task: ${newTask.title}`);
            });
        });
        
        NewUI.registerHandler('showModal', function() {
            showModal();
        });
        
        NewUI.registerHandler('createProject', function(element, event) {
            const formData = new FormData(element);
            hideModal();
            showToast(`Project "${formData.get('name')}" created!`, 'success');
            addActivity(`Created project: ${formData.get('name')}`);
            element.reset();
        });
        
        NewUI.registerHandler('exportData', function() {
            showToast('Exporting data...', 'info');
            setTimeout(() => {
                showToast('Data exported successfully!', 'success');
                addActivity('Exported dashboard data');
            }, 1500);
        });
        
        NewUI.registerHandler('showNotification', function() {
            const notifComponent = document.querySelector('[data-ui-component="notifications"]');
            const componentId = notifComponent.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            
            const newNotification = {
                id: Date.now(),
                message: 'This is a test notification!',
                time: new Date().toLocaleTimeString()
            };
            
            // Add notification
            fetch('/api/notifications', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(newNotification)
            })
            .then(() => {
                NewUI.setStateValue(componentId, 'count', (state.count || 0) + 1);
                showToast('New notification added!', 'success');
                renderNotifications();
            });
        });
        
        // Helper functions
        function toggleTask(taskId) {
            const taskManager = document.querySelector('[data-ui-component="task-manager"]');
            const componentId = taskManager.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            
            const tasks = state.tasks.map(t => 
                t.id === taskId ? {...t, completed: !t.completed} : t
            );
            
            NewUI.setStateValue(componentId, 'tasks', tasks);
            renderTasks();
            
            const task = tasks.find(t => t.id === taskId);
            addActivity(`${task.completed ? 'Completed' : 'Reopened'} task: ${task.title}`);
        }
        
        function deleteTask(taskId) {
            const taskManager = document.querySelector('[data-ui-component="task-manager"]');
            const componentId = taskManager.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            
            const task = state.tasks.find(t => t.id === taskId);
            const tasks = state.tasks.filter(t => t.id !== taskId);
            
            NewUI.setStateValue(componentId, 'tasks', tasks);
            renderTasks();
            showToast('Task deleted', 'info');
            addActivity(`Deleted task: ${task.title}`);
        }
        
        function addActivity(message) {
            const activityFeed = document.querySelector('[data-ui-component="activity-feed"]');
            const componentId = activityFeed.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            
            const activity = {
                id: Date.now(),
                message: message,
                time: new Date().toLocaleTimeString()
            };
            
            const activities = [activity, ...(state.activities || [])].slice(0, 5);
            NewUI.setStateValue(componentId, 'activities', activities);
            renderActivities();
        }
        
        function renderActivities() {
            const activityFeed = document.querySelector('[data-ui-component="activity-feed"]');
            const componentId = activityFeed.getAttribute('data-ui-id');
            const state = NewUI.state[componentId];
            const activityList = document.getElementById('activity-list');
            
            const activities = state.activities || [];
            
            if (activities.length === 0) {
                activityList.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No recent activity</p>';
                return;
            }
            
            activityList.innerHTML = activities.map(activity => `
                <div class="flex items-start space-x-3 animate-fade-in">
                    <div class="flex-shrink-0">
                        <div class="h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                            <svg class="h-4 w-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm text-gray-900 dark:text-white">${activity.message}</p>
                        <p class="text-xs text-gray-500 dark:text-gray-400">${activity.time}</p>
                    </div>
                </div>
            `).join('');
        }
        
        function renderNotifications() {
            // This would fetch and render notifications in the dropdown
            console.log('Rendering notifications...');
        }
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize theme first (before rendering to avoid flash)
            initializeTheme();
            
            // Then initialize components
            renderTasks();
            renderActivities();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE, 
                                ui=ui,
                                stats=dashboard_data['stats'],
                                tasks=dashboard_data['tasks'],
                                notifications=dashboard_data['notifications'])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    task = request.json
    task['id'] = len(dashboard_data['tasks']) + 1
    dashboard_data['tasks'].append(task)
    return jsonify({'status': 'success', 'task': task})

@app.route('/api/notifications', methods=['POST'])
def add_notification():
    notification = request.json
    dashboard_data['notifications'].append(notification)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Modern UI with Tailwind CSS v4.0")
    print("="*50)
    print("Open http://localhost:5015")
    print("Features:")
    print("- Modern dashboard with Tailwind CSS v4.0")
    print("- Dark mode support (toggle in top-right)")
    print("- Responsive design")
    print("- Interactive components with smooth animations")
    print("- Task management with filters")
    print("- Real-time notifications")
    print("- Activity feed")
    print("- Modal dialogs")
    print("- Toast notifications")
    print("="*50 + "\n")
    app.run(debug=True, port=5015)