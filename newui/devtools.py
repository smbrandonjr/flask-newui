"""
Development tools for NewUI - debugger and component inspector
"""

from typing import Dict, List, Any, Optional, Callable
from flask import Flask, render_template_string, request, jsonify
import json
import time
from datetime import datetime
import traceback
import sys
import os


class ComponentInspector:
    """Component inspection and debugging tools"""
    
    def __init__(self):
        self.components_registry: Dict[str, Dict] = {}
        self.component_instances: Dict[str, Dict] = {}
        self.state_history: List[Dict] = []
        self.performance_data: Dict[str, List] = {}
        self.enabled = True
    
    def register_component(self, component_id: str, component_type: str, 
                          initial_state: Dict = None, element_info: Dict = None):
        """Register a component instance for inspection"""
        if not self.enabled:
            return
            
        self.component_instances[component_id] = {
            'id': component_id,
            'type': component_type,
            'state': initial_state or {},
            'element_info': element_info or {},
            'created_at': time.time(),
            'updated_at': time.time(),
            'render_count': 0,
            'lifecycle_events': [],
            'performance': {
                'render_times': [],
                'state_updates': 0,
                'event_handlers': 0
            }
        }
    
    def update_component_state(self, component_id: str, new_state: Dict, 
                              source: str = 'unknown'):
        """Record component state update"""
        if not self.enabled or component_id not in self.component_instances:
            return
            
        component = self.component_instances[component_id]
        old_state = component['state'].copy()
        
        # Update state
        component['state'] = new_state
        component['updated_at'] = time.time()
        component['performance']['state_updates'] += 1
        
        # Record state history
        self.state_history.append({
            'component_id': component_id,
            'timestamp': time.time(),
            'source': source,
            'old_state': old_state,
            'new_state': new_state,
            'diff': self._calculate_state_diff(old_state, new_state)
        })
        
        # Keep only last 100 state changes
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    def record_lifecycle_event(self, component_id: str, event: str, 
                              data: Dict = None):
        """Record component lifecycle event"""
        if not self.enabled or component_id not in self.component_instances:
            return
            
        component = self.component_instances[component_id]
        component['lifecycle_events'].append({
            'event': event,
            'timestamp': time.time(),
            'data': data or {}
        })
        
        # Keep only last 20 events per component
        if len(component['lifecycle_events']) > 20:
            component['lifecycle_events'] = component['lifecycle_events'][-20:]
    
    def record_render_time(self, component_id: str, duration: float):
        """Record component render performance"""
        if not self.enabled or component_id not in self.component_instances:
            return
            
        component = self.component_instances[component_id]
        component['render_count'] += 1
        component['performance']['render_times'].append({
            'duration': duration,
            'timestamp': time.time()
        })
        
        # Keep only last 50 render times
        if len(component['performance']['render_times']) > 50:
            component['performance']['render_times'] = component['performance']['render_times'][-50:]
    
    def record_event_handler(self, component_id: str, event_type: str, 
                           handler_name: str, duration: float = None):
        """Record event handler execution"""
        if not self.enabled:
            return
            
        if component_id in self.component_instances:
            self.component_instances[component_id]['performance']['event_handlers'] += 1
        
        # Record in performance data
        if 'event_handlers' not in self.performance_data:
            self.performance_data['event_handlers'] = []
        
        self.performance_data['event_handlers'].append({
            'component_id': component_id,
            'event_type': event_type,
            'handler_name': handler_name,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def _calculate_state_diff(self, old_state: Dict, new_state: Dict) -> Dict:
        """Calculate differences between old and new state"""
        diff = {
            'added': {},
            'removed': {},
            'changed': {}
        }
        
        # Find added and changed keys
        for key, value in new_state.items():
            if key not in old_state:
                diff['added'][key] = value
            elif old_state[key] != value:
                diff['changed'][key] = {
                    'old': old_state[key],
                    'new': value
                }
        
        # Find removed keys
        for key in old_state:
            if key not in new_state:
                diff['removed'][key] = old_state[key]
        
        return diff
    
    def get_component_tree(self) -> Dict:
        """Get hierarchical component tree"""
        # In a full implementation, this would build a proper tree
        # based on DOM hierarchy and component relationships
        components = []
        for component_id, component in self.component_instances.items():
            components.append({
                'id': component_id,
                'type': component['type'],
                'state_keys': list(component['state'].keys()),
                'render_count': component['render_count'],
                'last_updated': component['updated_at'],
                'performance_summary': {
                    'avg_render_time': self._calculate_avg_render_time(component_id),
                    'state_updates': component['performance']['state_updates'],
                    'event_handlers': component['performance']['event_handlers']
                }
            })
        
        return {
            'components': components,
            'total_components': len(components),
            'total_state_updates': len(self.state_history)
        }
    
    def _calculate_avg_render_time(self, component_id: str) -> float:
        """Calculate average render time for component"""
        if component_id not in self.component_instances:
            return 0.0
            
        render_times = self.component_instances[component_id]['performance']['render_times']
        if not render_times:
            return 0.0
        
        total_time = sum(rt['duration'] for rt in render_times)
        return total_time / len(render_times)
    
    def get_component_details(self, component_id: str) -> Optional[Dict]:
        """Get detailed information about a specific component"""
        if component_id not in self.component_instances:
            return None
        
        component = self.component_instances[component_id]
        
        # Get recent state history for this component
        recent_history = [
            h for h in self.state_history[-20:]
            if h['component_id'] == component_id
        ]
        
        return {
            **component,
            'state_history': recent_history,
            'performance_details': {
                'avg_render_time': self._calculate_avg_render_time(component_id),
                'render_time_trend': component['performance']['render_times'][-10:],
                'total_renders': component['render_count']
            }
        }
    
    def get_global_performance(self) -> Dict:
        """Get global performance statistics"""
        total_components = len(self.component_instances)
        total_renders = sum(c['render_count'] for c in self.component_instances.values())
        total_state_updates = sum(c['performance']['state_updates'] for c in self.component_instances.values())
        
        # Calculate average render times
        all_render_times = []
        for component in self.component_instances.values():
            all_render_times.extend([rt['duration'] for rt in component['performance']['render_times']])
        
        avg_render_time = sum(all_render_times) / len(all_render_times) if all_render_times else 0
        
        return {
            'total_components': total_components,
            'total_renders': total_renders,
            'total_state_updates': total_state_updates,
            'avg_render_time': avg_render_time,
            'slowest_components': self._get_slowest_components(),
            'most_active_components': self._get_most_active_components(),
            'memory_usage': self._estimate_memory_usage()
        }
    
    def _get_slowest_components(self) -> List[Dict]:
        """Get components with slowest average render times"""
        components_with_times = []
        for component_id, component in self.component_instances.items():
            avg_time = self._calculate_avg_render_time(component_id)
            if avg_time > 0:
                components_with_times.append({
                    'id': component_id,
                    'type': component['type'],
                    'avg_render_time': avg_time
                })
        
        return sorted(components_with_times, 
                     key=lambda x: x['avg_render_time'], 
                     reverse=True)[:5]
    
    def _get_most_active_components(self) -> List[Dict]:
        """Get components with most state updates"""
        components_with_updates = []
        for component_id, component in self.component_instances.items():
            updates = component['performance']['state_updates']
            if updates > 0:
                components_with_updates.append({
                    'id': component_id,
                    'type': component['type'],
                    'state_updates': updates,
                    'render_count': component['render_count']
                })
        
        return sorted(components_with_updates, 
                     key=lambda x: x['state_updates'], 
                     reverse=True)[:5]
    
    def _estimate_memory_usage(self) -> Dict:
        """Estimate memory usage of component data"""
        # Rough estimation based on serialized JSON size
        total_size = 0
        
        try:
            # Component instances
            instances_json = json.dumps(self.component_instances)
            total_size += len(instances_json.encode('utf-8'))
            
            # State history
            history_json = json.dumps(self.state_history)
            total_size += len(history_json.encode('utf-8'))
            
            # Performance data
            perf_json = json.dumps(self.performance_data)
            total_size += len(perf_json.encode('utf-8'))
        except:
            total_size = 0
        
        return {
            'estimated_bytes': total_size,
            'estimated_kb': round(total_size / 1024, 2),
            'component_count': len(self.component_instances),
            'history_entries': len(self.state_history)
        }


class NewUIDebugger:
    """Main debugger class with Flask integration"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.inspector = ComponentInspector()
        self.enabled = True
        self.debug_mode = False
        self.console_logs: List[Dict] = []
        self.error_logs: List[Dict] = []
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize debugger with Flask app"""
        self.app = app
        self.debug_mode = app.debug
        
        # Register debug routes
        app.add_url_rule('/debug/components', 'debug_components', self.get_components_api)
        app.add_url_rule('/debug/component/<component_id>', 'debug_component_detail', self.get_component_detail_api)
        app.add_url_rule('/debug/performance', 'debug_performance', self.get_performance_api)
        app.add_url_rule('/debug/state-history', 'debug_state_history', self.get_state_history_api)
        app.add_url_rule('/debug/console', 'debug_console', self.get_console_logs_api)
        app.add_url_rule('/debug/panel', 'debug_panel', self.render_debug_panel)
        
        # Debug endpoints for receiving client data
        app.add_url_rule('/debug/log', 'debug_log', self.receive_log, methods=['POST'])
        app.add_url_rule('/debug/error', 'debug_error', self.receive_error, methods=['POST'])
        app.add_url_rule('/debug/performance-data', 'debug_perf_data', self.receive_performance_data, methods=['POST'])
        
        print("NewUI Debugger initialized")
    
    def get_components_api(self):
        """API endpoint for component tree"""
        return jsonify(self.inspector.get_component_tree())
    
    def get_component_detail_api(self, component_id: str):
        """API endpoint for component details"""
        details = self.inspector.get_component_details(component_id)
        if details:
            return jsonify(details)
        return jsonify({'error': 'Component not found'}), 404
    
    def get_performance_api(self):
        """API endpoint for performance data"""
        return jsonify(self.inspector.get_global_performance())
    
    def get_state_history_api(self):
        """API endpoint for state history"""
        return jsonify({
            'history': self.inspector.state_history[-50:],  # Last 50 entries
            'total_entries': len(self.inspector.state_history)
        })
    
    def get_console_logs_api(self):
        """API endpoint for console logs"""
        return jsonify({
            'logs': self.console_logs[-100:],  # Last 100 logs
            'errors': self.error_logs[-50:],   # Last 50 errors
            'total_logs': len(self.console_logs),
            'total_errors': len(self.error_logs)
        })
    
    def receive_log(self):
        """Receive log data from client"""
        data = request.json
        self.console_logs.append({
            'timestamp': time.time(),
            'level': data.get('level', 'info'),
            'message': data.get('message', ''),
            'component_id': data.get('component_id'),
            'source': 'client'
        })
        
        # Keep only last 200 logs
        if len(self.console_logs) > 200:
            self.console_logs = self.console_logs[-200:]
        
        return jsonify({'status': 'logged'})
    
    def receive_error(self):
        """Receive error data from client"""
        data = request.json
        self.error_logs.append({
            'timestamp': time.time(),
            'message': data.get('message', ''),
            'stack': data.get('stack', ''),
            'component_id': data.get('component_id'),
            'source': 'client'
        })
        
        # Keep only last 100 errors
        if len(self.error_logs) > 100:
            self.error_logs = self.error_logs[-100:]
        
        return jsonify({'status': 'logged'})
    
    def receive_performance_data(self):
        """Receive performance data from client"""
        data = request.json
        
        # Record component registration
        if data.get('type') == 'component_registered':
            self.inspector.register_component(
                data.get('component_id'),
                data.get('component_type'),
                data.get('initial_state'),
                data.get('element_info')
            )
        
        # Record state updates
        elif data.get('type') == 'state_updated':
            self.inspector.update_component_state(
                data.get('component_id'),
                data.get('new_state'),
                data.get('source', 'client')
            )
        
        # Record lifecycle events
        elif data.get('type') == 'lifecycle_event':
            self.inspector.record_lifecycle_event(
                data.get('component_id'),
                data.get('event'),
                data.get('data')
            )
        
        # Record render performance
        elif data.get('type') == 'render_performance':
            self.inspector.record_render_time(
                data.get('component_id'),
                data.get('duration')
            )
        
        # Record event handler performance
        elif data.get('type') == 'event_handler':
            self.inspector.record_event_handler(
                data.get('component_id'),
                data.get('event_type'),
                data.get('handler_name'),
                data.get('duration')
            )
        
        return jsonify({'status': 'recorded'})
    
    def render_debug_panel(self):
        """Render the debug panel UI"""
        return render_template_string(self.get_debug_panel_template())
    
    def get_debug_panel_template(self) -> str:
        """Get the debug panel HTML template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>NewUI Debug Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .debug-panel {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
        }
        .debug-sidebar {
            background: #f8f9fa;
            border-right: 1px solid #dee2e6;
            height: 100vh;
            overflow-y: auto;
        }
        .debug-content {
            height: 100vh;
            overflow-y: auto;
        }
        .component-tree-item {
            padding: 5px 10px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
        }
        .component-tree-item:hover {
            background: #e9ecef;
        }
        .component-tree-item.active {
            background: #007bff;
            color: white;
        }
        .json-viewer {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
        .performance-metric {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #007bff;
        }
        .log-entry {
            padding: 5px;
            border-bottom: 1px solid #eee;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-info { color: #17a2b8; }
        .log-warn { color: #ffc107; }
        .log-error { color: #dc3545; }
        .state-diff {
            background: #f8f9fa;
            border-left: 3px solid #28a745;
            padding: 10px;
            margin: 5px 0;
            font-family: monospace;
            font-size: 12px;
        }
        .diff-added { color: #28a745; }
        .diff-removed { color: #dc3545; }
        .diff-changed { color: #ffc107; }
    </style>
</head>
<body class="debug-panel">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-3 debug-sidebar p-0">
                <div class="p-3 border-bottom">
                    <h5>NewUI Debugger</h5>
                    <div class="btn-group-vertical w-100">
                        <button class="btn btn-outline-primary btn-sm" onclick="switchTab('components')">Components</button>
                        <button class="btn btn-outline-primary btn-sm" onclick="switchTab('performance')">Performance</button>
                        <button class="btn btn-outline-primary btn-sm" onclick="switchTab('state')">State History</button>
                        <button class="btn btn-outline-primary btn-sm" onclick="switchTab('console')">Console</button>
                    </div>
                </div>
                
                <div id="sidebar-content">
                    <!-- Sidebar content will be populated here -->
                </div>
            </div>
            
            <div class="col-md-9 debug-content p-3">
                <div id="main-content">
                    <h4>Select a tab to view debug information</h4>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentTab = 'components';
        let selectedComponent = null;
        let debugData = {
            components: null,
            performance: null,
            stateHistory: null,
            console: null
        };
        
        function switchTab(tab) {
            currentTab = tab;
            
            // Update active button
            document.querySelectorAll('.btn-outline-primary').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Load tab data
            loadTabData(tab);
        }
        
        async function loadTabData(tab) {
            try {
                let data;
                switch(tab) {
                    case 'components':
                        data = await fetch('/debug/components').then(r => r.json());
                        debugData.components = data;
                        renderComponentsTab(data);
                        break;
                    case 'performance':
                        data = await fetch('/debug/performance').then(r => r.json());
                        debugData.performance = data;
                        renderPerformanceTab(data);
                        break;
                    case 'state':
                        data = await fetch('/debug/state-history').then(r => r.json());
                        debugData.stateHistory = data;
                        renderStateTab(data);
                        break;
                    case 'console':
                        data = await fetch('/debug/console').then(r => r.json());
                        debugData.console = data;
                        renderConsoleTab(data);
                        break;
                }
            } catch (error) {
                document.getElementById('main-content').innerHTML = 
                    '<div class="alert alert-danger">Error loading debug data: ' + error.message + '</div>';
            }
        }
        
        function renderComponentsTab(data) {
            const sidebar = document.getElementById('sidebar-content');
            const main = document.getElementById('main-content');
            
            // Render component list in sidebar
            sidebar.innerHTML = `
                <div class="p-2">
                    <h6>Components (${data.total_components})</h6>
                    <div>
                        ${data.components.map(component => `
                            <div class="component-tree-item" onclick="selectComponent('${component.id}')">
                                <strong>${component.type}</strong><br>
                                <small>${component.id}</small><br>
                                <small class="text-muted">${component.render_count} renders</small>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            // Render overview in main content
            main.innerHTML = `
                <h4>Component Overview</h4>
                <div class="row">
                    <div class="col-md-4">
                        <div class="performance-metric">
                            <div class="metric-value">${data.total_components}</div>
                            <div>Total Components</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="performance-metric">
                            <div class="metric-value">${data.total_state_updates}</div>
                            <div>State Updates</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="performance-metric">
                            <div class="metric-value">${data.components.reduce((sum, c) => sum + c.render_count, 0)}</div>
                            <div>Total Renders</div>
                        </div>
                    </div>
                </div>
                <p class="mt-3">Select a component from the sidebar to view detailed information.</p>
            `;
        }
        
        async function selectComponent(componentId) {
            selectedComponent = componentId;
            
            // Update active item
            document.querySelectorAll('.component-tree-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Load component details
            try {
                const data = await fetch(`/debug/component/${componentId}`).then(r => r.json());
                renderComponentDetails(data);
            } catch (error) {
                document.getElementById('main-content').innerHTML = 
                    '<div class="alert alert-danger">Error loading component details: ' + error.message + '</div>';
            }
        }
        
        function renderComponentDetails(component) {
            const main = document.getElementById('main-content');
            
            main.innerHTML = `
                <h4>Component: ${component.type}</h4>
                <p><strong>ID:</strong> ${component.id}</p>
                
                <div class="row">
                    <div class="col-md-6">
                        <h5>Current State</h5>
                        <div class="json-viewer">${JSON.stringify(component.state, null, 2)}</div>
                        
                        <h5 class="mt-3">Performance</h5>
                        <div class="performance-metric">
                            <div class="metric-value">${component.render_count}</div>
                            <div>Total Renders</div>
                        </div>
                        <div class="performance-metric">
                            <div class="metric-value">${component.performance_details.avg_render_time.toFixed(2)}ms</div>
                            <div>Avg Render Time</div>
                        </div>
                        <div class="performance-metric">
                            <div class="metric-value">${component.performance.state_updates}</div>
                            <div>State Updates</div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <h5>Recent State History</h5>
                        <div style="max-height: 300px; overflow-y: auto;">
                            ${component.state_history.map(change => `
                                <div class="state-diff">
                                    <strong>${new Date(change.timestamp * 1000).toLocaleTimeString()}</strong> (${change.source})<br>
                                    ${renderStateDiff(change.diff)}
                                </div>
                            `).join('')}
                        </div>
                        
                        <h5 class="mt-3">Lifecycle Events</h5>
                        <div style="max-height: 200px; overflow-y: auto;">
                            ${component.lifecycle_events.map(event => `
                                <div class="log-entry">
                                    <strong>${event.event}</strong> - ${new Date(event.timestamp * 1000).toLocaleTimeString()}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }
        
        function renderStateDiff(diff) {
            let html = '';
            
            Object.keys(diff.added).forEach(key => {
                html += `<div class="diff-added">+ ${key}: ${JSON.stringify(diff.added[key])}</div>`;
            });
            
            Object.keys(diff.removed).forEach(key => {
                html += `<div class="diff-removed">- ${key}: ${JSON.stringify(diff.removed[key])}</div>`;
            });
            
            Object.keys(diff.changed).forEach(key => {
                const change = diff.changed[key];
                html += `<div class="diff-changed">~ ${key}: ${JSON.stringify(change.old)} → ${JSON.stringify(change.new)}</div>`;
            });
            
            return html || '<small class="text-muted">No changes</small>';
        }
        
        function renderPerformanceTab(data) {
            const sidebar = document.getElementById('sidebar-content');
            const main = document.getElementById('main-content');
            
            sidebar.innerHTML = `
                <div class="p-2">
                    <h6>Performance Metrics</h6>
                    <div class="list-group">
                        <div class="list-group-item">
                            <strong>Components:</strong> ${data.total_components}
                        </div>
                        <div class="list-group-item">
                            <strong>Renders:</strong> ${data.total_renders}
                        </div>
                        <div class="list-group-item">
                            <strong>Avg Render:</strong> ${data.avg_render_time.toFixed(2)}ms
                        </div>
                        <div class="list-group-item">
                            <strong>Memory:</strong> ${data.memory_usage.estimated_kb}KB
                        </div>
                    </div>
                </div>
            `;
            
            main.innerHTML = `
                <h4>Performance Analysis</h4>
                
                <div class="row">
                    <div class="col-md-6">
                        <h5>Slowest Components</h5>
                        <div class="list-group">
                            ${data.slowest_components.map(comp => `
                                <div class="list-group-item">
                                    <strong>${comp.type}</strong> (${comp.id})<br>
                                    <small>Avg: ${comp.avg_render_time.toFixed(2)}ms</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <h5>Most Active Components</h5>
                        <div class="list-group">
                            ${data.most_active_components.map(comp => `
                                <div class="list-group-item">
                                    <strong>${comp.type}</strong> (${comp.id})<br>
                                    <small>${comp.state_updates} updates, ${comp.render_count} renders</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <h5>Memory Usage Estimate</h5>
                    <div class="performance-metric">
                        <div class="metric-value">${data.memory_usage.estimated_kb} KB</div>
                        <div>${data.memory_usage.component_count} components, ${data.memory_usage.history_entries} history entries</div>
                    </div>
                </div>
            `;
        }
        
        function renderStateTab(data) {
            const sidebar = document.getElementById('sidebar-content');
            const main = document.getElementById('main-content');
            
            sidebar.innerHTML = `
                <div class="p-2">
                    <h6>State History</h6>
                    <div class="list-group-item">
                        <strong>Total Entries:</strong> ${data.total_entries}
                    </div>
                    <div class="list-group-item">
                        <strong>Showing:</strong> Last ${data.history.length}
                    </div>
                </div>
            `;
            
            main.innerHTML = `
                <h4>State Change History</h4>
                <div style="max-height: 600px; overflow-y: auto;">
                    ${data.history.reverse().map(change => `
                        <div class="state-diff">
                            <strong>${new Date(change.timestamp * 1000).toLocaleString()}</strong><br>
                            <strong>Component:</strong> ${change.component_id} (${change.source})<br>
                            ${renderStateDiff(change.diff)}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function renderConsoleTab(data) {
            const sidebar = document.getElementById('sidebar-content');
            const main = document.getElementById('main-content');
            
            sidebar.innerHTML = `
                <div class="p-2">
                    <h6>Console Logs</h6>
                    <div class="list-group-item">
                        <strong>Total Logs:</strong> ${data.total_logs}
                    </div>
                    <div class="list-group-item">
                        <strong>Total Errors:</strong> ${data.total_errors}
                    </div>
                    <button class="btn btn-sm btn-outline-danger mt-2" onclick="clearLogs()">Clear Logs</button>
                </div>
            `;
            
            const allEntries = [...data.logs, ...data.errors].sort((a, b) => b.timestamp - a.timestamp);
            
            main.innerHTML = `
                <h4>Console Output</h4>
                <div style="max-height: 600px; overflow-y: auto; font-family: monospace;">
                    ${allEntries.map(entry => `
                        <div class="log-entry log-${entry.level || 'info'}">
                            [${new Date(entry.timestamp * 1000).toLocaleTimeString()}] 
                            ${entry.level ? entry.level.toUpperCase() : 'INFO'}: 
                            ${entry.message}
                            ${entry.component_id ? ` (${entry.component_id})` : ''}
                            ${entry.stack ? `<br><small class="text-muted">${entry.stack}</small>` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function clearLogs() {
            // In a real implementation, this would make an API call to clear logs
            alert('Clear logs functionality would be implemented here');
        }
        
        // Auto-refresh data every 5 seconds
        setInterval(() => {
            if (currentTab) {
                loadTabData(currentTab);
            }
        }, 5000);
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            switchTab('components');
        });
    </script>
</body>
</html>
        """
    
    def generate_client_debug_code(self) -> str:
        """Generate client-side debugging code"""
        return f"""
// NewUI Debug Client
(function(window, NewUI) {{
    'use strict';
    
    if (!NewUI || !{str(self.enabled).lower()}) {{
        return; // Debugging disabled
    }}
    
    const NewUIDebug = {{
        enabled: true,
        apiBase: '/debug',
        
        init: function() {{
            this.instrumentNewUI();
            this.setupErrorHandling();
            this.startPerformanceMonitoring();
            console.log('NewUI Debug client initialized');
        }},
        
        instrumentNewUI: function() {{
            // Instrument component initialization
            const originalInitializeComponents = NewUI.initializeComponents;
            NewUI.initializeComponents = function() {{
                const startTime = performance.now();
                const result = originalInitializeComponents.call(this);
                const duration = performance.now() - startTime;
                
                // Report performance
                NewUIDebug.reportPerformance({{
                    type: 'initialization',
                    duration: duration,
                    timestamp: Date.now()
                }});
                
                // Register all components
                document.querySelectorAll('[data-ui-component]').forEach(element => {{
                    const componentType = element.getAttribute('data-ui-component');
                    const componentId = element.getAttribute('data-ui-id');
                    const stateData = element.getAttribute('data-ui-state');
                    
                    let initialState = {{}};
                    if (stateData) {{
                        try {{
                            initialState = JSON.parse(stateData);
                        }} catch (e) {{
                            console.warn('Failed to parse component state:', e);
                        }}
                    }}
                    
                    NewUIDebug.reportPerformance({{
                        type: 'component_registered',
                        component_id: componentId,
                        component_type: componentType,
                        initial_state: initialState,
                        element_info: {{
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id
                        }}
                    }});
                }});
                
                return result;
            }};
            
            // Instrument state changes
            const originalSetStateValue = NewUI.setStateValue;
            NewUI.setStateValue = function(componentId, path, value) {{
                const oldState = NewUI.state[componentId] || {{}};
                const result = originalSetStateValue.call(this, componentId, path, value);
                const newState = NewUI.state[componentId] || {{}};
                
                NewUIDebug.reportPerformance({{
                    type: 'state_updated',
                    component_id: componentId,
                    path: path,
                    old_state: oldState,
                    new_state: newState,
                    source: 'client'
                }});
                
                return result;
            }};
            
            // Instrument event handlers
            const originalHandleEvent = NewUI.handleEvent;
            NewUI.handleEvent = function(eventType, element, event) {{
                const startTime = performance.now();
                const componentId = NewUI.getComponentId(element);
                const handlerName = element.getAttribute(`data-ui-${{eventType}}`);
                
                try {{
                    const result = originalHandleEvent.call(this, eventType, element, event);
                    const duration = performance.now() - startTime;
                    
                    NewUIDebug.reportPerformance({{
                        type: 'event_handler',
                        component_id: componentId,
                        event_type: eventType,
                        handler_name: handlerName,
                        duration: duration
                    }});
                    
                    return result;
                }} catch (error) {{
                    NewUIDebug.logError(error, componentId, `Event handler: ${{handlerName}}`);
                    throw error;
                }}
            }};
            
            // Instrument lifecycle hooks
            const originalFireLifecycleHook = NewUI.fireLifecycleHook;
            NewUI.fireLifecycleHook = function(componentName, hookName, element, state) {{
                const componentId = element ? element.getAttribute('data-ui-id') : null;
                
                NewUIDebug.reportPerformance({{
                    type: 'lifecycle_event',
                    component_id: componentId,
                    event: hookName,
                    data: {{ componentName, state }}
                }});
                
                return originalFireLifecycleHook.call(this, componentName, hookName, element, state);
            }};
        }},
        
        setupErrorHandling: function() {{
            // Global error handler
            window.addEventListener('error', (event) => {{
                this.logError(event.error || new Error(event.message), null, event.filename + ':' + event.lineno);
            }});
            
            // Unhandled promise rejection handler
            window.addEventListener('unhandledrejection', (event) => {{
                this.logError(event.reason, null, 'Unhandled Promise Rejection');
            }});
        }},
        
        startPerformanceMonitoring: function() {{
            // Monitor page performance
            if (window.PerformanceObserver) {{
                // Monitor long tasks
                try {{
                    const longTaskObserver = new PerformanceObserver(list => {{
                        list.getEntries().forEach(entry => {{
                            if (entry.duration > 50) {{ // Tasks longer than 50ms
                                this.log('warn', `Long task detected: ${{entry.duration.toFixed(2)}}ms`);
                            }}
                        }});
                    }});
                    longTaskObserver.observe({{ entryTypes: ['longtask'] }});
                }} catch (e) {{
                    // Long task API not supported
                }}
                
                // Monitor layout shifts
                try {{
                    const clsObserver = new PerformanceObserver(list => {{
                        list.getEntries().forEach(entry => {{
                            if (entry.value > 0.1) {{ // Significant layout shift
                                this.log('warn', `Layout shift detected: ${{entry.value.toFixed(3)}}`);
                            }}
                        }});
                    }});
                    clsObserver.observe({{ entryTypes: ['layout-shift'] }});
                }} catch (e) {{
                    // Layout shift API not supported
                }}
            }}
        }},
        
        reportPerformance: function(data) {{
            if (!this.enabled) return;
            
            fetch(this.apiBase + '/performance-data', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(data)
            }}).catch(error => {{
                console.warn('Failed to report performance data:', error);
            }});
        }},
        
        log: function(level, message, componentId) {{
            console[level] && console[level](message);
            
            if (!this.enabled) return;
            
            fetch(this.apiBase + '/log', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    level: level,
                    message: message,
                    component_id: componentId,
                    timestamp: Date.now()
                }})
            }}).catch(error => {{
                console.warn('Failed to send log:', error);
            }});
        }},
        
        logError: function(error, componentId, context) {{
            console.error(error);
            
            if (!this.enabled) return;
            
            fetch(this.apiBase + '/error', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    message: error.message || String(error),
                    stack: error.stack || '',
                    component_id: componentId,
                    context: context,
                    timestamp: Date.now()
                }})
            }}).catch(err => {{
                console.warn('Failed to send error log:', err);
            }});
        }},
        
        // Public API
        openDebugPanel: function() {{
            window.open('/debug/panel', 'newui-debug', 'width=1200,height=800,scrollbars=yes');
        }},
        
        getComponentInfo: function(componentId) {{
            return fetch(`${{this.apiBase}}/component/${{componentId}}`)
                .then(response => response.json());
        }},
        
        getPerformanceData: function() {{
            return fetch(`${{this.apiBase}}/performance`)
                .then(response => response.json());
        }}
    }};
    
    // Initialize debug client
    NewUIDebug.init();
    
    // Expose globally
    window.NewUIDebug = NewUIDebug;
    
    // Add debug panel toggle
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', addDebugToggle);
    }} else {{
        addDebugToggle();
    }}
    
    function addDebugToggle() {{
        // Add debug panel toggle button (only in debug mode)
        if ({str(self.debug_mode).lower()}) {{
            const debugToggle = document.createElement('div');
            debugToggle.innerHTML = `
                <div style="position: fixed; bottom: 20px; right: 20px; z-index: 10000;">
                    <button onclick="NewUIDebug.openDebugPanel()" 
                            style="background: #007bff; color: white; border: none; padding: 10px; border-radius: 50%; font-size: 16px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.2);"
                            title="Open NewUI Debug Panel">
                        🐛
                    </button>
                </div>
            `;
            document.body.appendChild(debugToggle);
        }}
    }}
    
}})(window, window.NewUI);
"""


# Global debugger instance
debugger = NewUIDebugger()

# Convenience functions
def init_debugger(app: Flask, enabled: bool = True) -> NewUIDebugger:
    """Initialize debugger with Flask app"""
    debugger.enabled = enabled
    if enabled:
        debugger.init_app(app)
    return debugger