"""
Route-based code splitting for NewUI applications
"""

from typing import Dict, List, Any, Optional, Callable, Union
from flask import Flask, request, jsonify, send_from_directory
import os
import json
import hashlib
from pathlib import Path
import importlib.util
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class RouteChunk:
    """Represents a code chunk for a specific route"""
    name: str
    route_pattern: str
    js_files: List[str]
    css_files: List[str]
    dependencies: List[str]
    components: List[str]
    preload: bool = False
    lazy: bool = True


@dataclass  
class ComponentChunk:
    """Represents a code chunk for a specific component"""
    name: str
    component_name: str
    js_content: str
    css_content: str = ""
    dependencies: List[str] = None
    

class ChunkManager:
    """Manages code chunks and lazy loading"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.chunks: Dict[str, RouteChunk] = {}
        self.component_chunks: Dict[str, ComponentChunk] = {}
        self.loaded_chunks: set = set()
        self.chunk_manifest: Dict[str, Any] = {}
        self.output_dir = "static/chunks"
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize with Flask app"""
        self.app = app
        
        # Ensure chunks directory exists
        chunk_path = os.path.join(app.static_folder or 'static', 'chunks')
        os.makedirs(chunk_path, exist_ok=True)
        
        # Register routes for serving chunks
        app.add_url_rule('/chunks/<path:filename>', 'serve_chunk', self.serve_chunk)
        app.add_url_rule('/api/chunks/manifest', 'chunk_manifest', self.get_manifest)
        app.add_url_rule('/api/chunks/load/<chunk_name>', 'load_chunk', self.load_chunk_api)
        
        print("NewUI code splitting initialized")
    
    def register_route_chunk(self, chunk: RouteChunk):
        """Register a route-based chunk"""
        self.chunks[chunk.name] = chunk
        self._generate_chunk_files(chunk)
        self._update_manifest()
    
    def register_component_chunk(self, chunk: ComponentChunk):
        """Register a component-based chunk"""
        self.component_chunks[chunk.name] = chunk
        self._generate_component_files(chunk)
        self._update_manifest()
    
    def _generate_chunk_files(self, chunk: RouteChunk):
        """Generate physical chunk files"""
        if not self.app:
            return
            
        chunk_dir = os.path.join(self.app.static_folder or 'static', 'chunks')
        
        # Generate JavaScript chunk
        js_content = self._build_js_chunk(chunk)
        js_filename = f"{chunk.name}.js"
        js_path = os.path.join(chunk_dir, js_filename)
        
        with open(js_path, 'w') as f:
            f.write(js_content)
        
        # Generate CSS chunk if needed
        if chunk.css_files:
            css_content = self._build_css_chunk(chunk)
            css_filename = f"{chunk.name}.css"
            css_path = os.path.join(chunk_dir, css_filename)
            
            with open(css_path, 'w') as f:
                f.write(css_content)
    
    def _generate_component_files(self, chunk: ComponentChunk):
        """Generate component chunk files"""
        if not self.app:
            return
            
        chunk_dir = os.path.join(self.app.static_folder or 'static', 'chunks')
        
        # Generate component JavaScript
        js_filename = f"component-{chunk.name}.js"
        js_path = os.path.join(chunk_dir, js_filename)
        
        with open(js_path, 'w') as f:
            f.write(chunk.js_content)
        
        # Generate component CSS if provided
        if chunk.css_content:
            css_filename = f"component-{chunk.name}.css"
            css_path = os.path.join(chunk_dir, css_filename)
            
            with open(css_path, 'w') as f:
                f.write(chunk.css_content)
    
    def _build_js_chunk(self, chunk: RouteChunk) -> str:
        """Build JavaScript chunk content"""
        content_parts = [
            f"// Route chunk: {chunk.name}",
            f"// Route pattern: {chunk.route_pattern}",
            "",
            "(function(window, NewUI) {",
            "  'use strict';",
            "",
            f"  // Chunk: {chunk.name}",
            f"  const chunkName = '{chunk.name}';",
            "",
        ]
        
        # Add component registrations
        for component in chunk.components:
            content_parts.extend([
                f"  // Component: {component}",
                f"  if (window.{component}Components) {{",
                f"    Object.keys(window.{component}Components).forEach(name => {{",
                f"      NewUI.registerComponent(name, window.{component}Components[name]);",
                f"    }});",
                f"  }}",
                "",
            ])
        
        # Add JavaScript files content
        for js_file in chunk.js_files:
            if os.path.exists(js_file):
                with open(js_file, 'r') as f:
                    file_content = f.read()
                    content_parts.extend([
                        f"  // File: {js_file}",
                        f"  {file_content}",
                        "",
                    ])
        
        content_parts.extend([
            f"  // Mark chunk as loaded",
            f"  if (window.NewUIChunks) {{",
            f"    window.NewUIChunks.markLoaded('{chunk.name}');",
            f"  }}",
            "",
            f"  console.log('Loaded route chunk: {chunk.name}');",
            "",
            "})(window, window.NewUI);",
        ])
        
        return "\n".join(content_parts)
    
    def _build_css_chunk(self, chunk: RouteChunk) -> str:
        """Build CSS chunk content"""
        content_parts = [
            f"/* Route chunk CSS: {chunk.name} */",
            f"/* Route pattern: {chunk.route_pattern} */",
            "",
        ]
        
        for css_file in chunk.css_files:
            if os.path.exists(css_file):
                with open(css_file, 'r') as f:
                    file_content = f.read()
                    content_parts.extend([
                        f"/* File: {css_file} */",
                        file_content,
                        "",
                    ])
        
        return "\n".join(content_parts)
    
    def _update_manifest(self):
        """Update chunk manifest"""
        self.chunk_manifest = {
            'routes': {
                name: {
                    'name': chunk.name,
                    'route_pattern': chunk.route_pattern,
                    'js_url': f"/chunks/{chunk.name}.js",
                    'css_url': f"/chunks/{chunk.name}.css" if chunk.css_files else None,
                    'dependencies': chunk.dependencies,
                    'components': chunk.components,
                    'preload': chunk.preload,
                    'lazy': chunk.lazy,
                    'hash': self._get_chunk_hash(chunk.name)
                }
                for name, chunk in self.chunks.items()
            },
            'components': {
                name: {
                    'name': chunk.name,
                    'component_name': chunk.component_name,
                    'js_url': f"/chunks/component-{chunk.name}.js",
                    'css_url': f"/chunks/component-{chunk.name}.css" if chunk.css_content else None,
                    'dependencies': chunk.dependencies or [],
                    'hash': self._get_component_hash(chunk.name)
                }
                for name, chunk in self.component_chunks.items()
            },
            'version': self._get_manifest_version()
        }
    
    def _get_chunk_hash(self, chunk_name: str) -> str:
        """Get hash of chunk file for cache busting"""
        if not self.app:
            return "dev"
            
        js_path = os.path.join(self.app.static_folder or 'static', 'chunks', f"{chunk_name}.js")
        if os.path.exists(js_path):
            with open(js_path, 'r') as f:
                content = f.read()
                return hashlib.md5(content.encode()).hexdigest()[:8]
        return "unknown"
    
    def _get_component_hash(self, chunk_name: str) -> str:
        """Get hash of component chunk file"""
        if not self.app:
            return "dev"
            
        js_path = os.path.join(self.app.static_folder or 'static', 'chunks', f"component-{chunk_name}.js")
        if os.path.exists(js_path):
            with open(js_path, 'r') as f:
                content = f.read()
                return hashlib.md5(content.encode()).hexdigest()[:8]
        return "unknown"
    
    def _get_manifest_version(self) -> str:
        """Get manifest version"""
        manifest_str = json.dumps(self.chunk_manifest, sort_keys=True)
        return hashlib.md5(manifest_str.encode()).hexdigest()[:8]
    
    def serve_chunk(self, filename: str):
        """Serve chunk files"""
        if not self.app:
            return "Not found", 404
            
        chunk_dir = os.path.join(self.app.static_folder or 'static', 'chunks')
        return send_from_directory(chunk_dir, filename)
    
    def get_manifest(self):
        """API endpoint to get chunk manifest"""
        return jsonify(self.chunk_manifest)
    
    def load_chunk_api(self, chunk_name: str):
        """API endpoint to mark chunk as loaded"""
        self.loaded_chunks.add(chunk_name)
        return jsonify({'status': 'loaded', 'chunk': chunk_name})
    
    def get_chunks_for_route(self, route_pattern: str) -> List[str]:
        """Get chunk names for a specific route"""
        matching_chunks = []
        for chunk in self.chunks.values():
            if self._route_matches(route_pattern, chunk.route_pattern):
                matching_chunks.append(chunk.name)
        return matching_chunks
    
    def _route_matches(self, current_route: str, chunk_pattern: str) -> bool:
        """Check if current route matches chunk pattern"""
        # Simple pattern matching - in a full implementation,
        # you'd want more sophisticated pattern matching
        if chunk_pattern == current_route:
            return True
        
        # Handle wildcards
        if '*' in chunk_pattern:
            pattern_parts = chunk_pattern.split('*')
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                return current_route.startswith(prefix) and current_route.endswith(suffix)
        
        return False


class RouterComponent:
    """Client-side router with code splitting support"""
    
    def __init__(self, chunk_manager: ChunkManager):
        self.chunk_manager = chunk_manager
        self.current_route = None
        self.loaded_chunks = set()
    
    def generate_client_code(self) -> str:
        """Generate client-side router JavaScript"""
        return f"""
// NewUI Router with Code Splitting
(function(window, NewUI) {{
    'use strict';
    
    class NewUIRouter {{
        constructor() {{
            this.currentRoute = null;
            this.loadedChunks = new Set();
            this.routeChunks = new Map();
            this.componentChunks = new Map();
            this.manifest = null;
            
            this.init();
        }}
        
        async init() {{
            // Load chunk manifest
            await this.loadManifest();
            
            // Set up client-side routing
            this.setupRouting();
            
            // Handle initial route
            this.handleRoute(window.location.pathname);
        }}
        
        async loadManifest() {{
            try {{
                const response = await fetch('/api/chunks/manifest');
                this.manifest = await response.json();
                
                // Build route chunk map
                Object.values(this.manifest.routes || {{}}).forEach(chunk => {{
                    this.routeChunks.set(chunk.route_pattern, chunk);
                }});
                
                // Build component chunk map
                Object.values(this.manifest.components || {{}}).forEach(chunk => {{
                    this.componentChunks.set(chunk.component_name, chunk);
                }});
                
                console.log('Chunk manifest loaded:', this.manifest);
            }} catch (error) {{
                console.error('Failed to load chunk manifest:', error);
            }}
        }}
        
        setupRouting() {{
            // Handle popstate for back/forward buttons
            window.addEventListener('popstate', (event) => {{
                this.handleRoute(window.location.pathname);
            }});
            
            // Intercept link clicks for SPA navigation
            document.addEventListener('click', (event) => {{
                const link = event.target.closest('a[data-route]');
                if (link && !event.ctrlKey && !event.metaKey) {{
                    event.preventDefault();
                    this.navigateTo(link.getAttribute('href') || link.getAttribute('data-route'));
                }}
            }});
        }}
        
        async navigateTo(path) {{
            if (path === this.currentRoute) {{
                return;
            }}
            
            // Update browser history
            history.pushState(null, '', path);
            
            // Handle the route
            await this.handleRoute(path);
        }}
        
        async handleRoute(path) {{
            console.log('Handling route:', path);
            
            this.currentRoute = path;
            
            // Find matching chunks
            const requiredChunks = this.getChunksForRoute(path);
            
            // Load chunks if not already loaded
            for (const chunkName of requiredChunks) {{
                if (!this.loadedChunks.has(chunkName)) {{
                    await this.loadChunk(chunkName);
                }}
            }}
            
            // Fire route change event
            window.dispatchEvent(new CustomEvent('routechange', {{
                detail: {{ path, chunks: requiredChunks }}
            }}));
        }}
        
        getChunksForRoute(path) {{
            const matchingChunks = [];
            
            this.routeChunks.forEach((chunk, pattern) => {{
                if (this.routeMatches(path, pattern)) {{
                    matchingChunks.push(chunk.name);
                }}
            }});
            
            return matchingChunks;
        }}
        
        routeMatches(currentPath, pattern) {{
            if (pattern === currentPath) {{
                return true;
            }}
            
            // Handle wildcards
            if (pattern.includes('*')) {{
                const parts = pattern.split('*');
                if (parts.length === 2) {{
                    const [prefix, suffix] = parts;
                    return currentPath.startsWith(prefix) && currentPath.endsWith(suffix);
                }}
            }}
            
            return false;
        }}
        
        async loadChunk(chunkName) {{
            if (this.loadedChunks.has(chunkName)) {{
                return;
            }}
            
            const chunk = this.manifest.routes[chunkName];
            if (!chunk) {{
                console.warn('Chunk not found:', chunkName);
                return;
            }}
            
            console.log('Loading chunk:', chunkName);
            
            try {{
                // Show loading indicator
                this.showLoadingIndicator(chunkName);
                
                // Load dependencies first
                for (const dep of chunk.dependencies || []) {{
                    if (!this.loadedChunks.has(dep)) {{
                        await this.loadChunk(dep);
                    }}
                }}
                
                // Load CSS if present
                if (chunk.css_url) {{
                    await this.loadCSS(chunk.css_url);
                }}
                
                // Load JavaScript
                await this.loadJS(chunk.js_url);
                
                // Mark as loaded
                this.markLoaded(chunkName);
                
                // Hide loading indicator
                this.hideLoadingIndicator(chunkName);
                
                console.log('Chunk loaded successfully:', chunkName);
                
            }} catch (error) {{
                console.error('Failed to load chunk:', chunkName, error);
                this.hideLoadingIndicator(chunkName);
            }}
        }}
        
        async loadComponent(componentName) {{
            const chunk = this.componentChunks.get(componentName);
            if (!chunk || this.loadedChunks.has(chunk.name)) {{
                return;
            }}
            
            console.log('Loading component chunk:', chunk.name);
            
            try {{
                // Load dependencies first
                for (const dep of chunk.dependencies || []) {{
                    if (!this.loadedChunks.has(dep)) {{
                        await this.loadComponent(dep);
                    }}
                }}
                
                // Load CSS if present
                if (chunk.css_url) {{
                    await this.loadCSS(chunk.css_url);
                }}
                
                // Load JavaScript
                await this.loadJS(chunk.js_url);
                
                // Mark as loaded
                this.markLoaded(chunk.name);
                
                console.log('Component chunk loaded:', chunk.name);
                
            }} catch (error) {{
                console.error('Failed to load component chunk:', error);
            }}
        }}
        
        loadJS(url) {{
            return new Promise((resolve, reject) => {{
                const script = document.createElement('script');
                script.src = url;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            }});
        }}
        
        loadCSS(url) {{
            return new Promise((resolve, reject) => {{
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = url;
                link.onload = resolve;
                link.onerror = reject;
                document.head.appendChild(link);
            }});
        }}
        
        markLoaded(chunkName) {{
            this.loadedChunks.add(chunkName);
            
            // Notify server
            fetch(`/api/chunks/load/${{chunkName}}`, {{ method: 'POST' }})
                .catch(error => console.warn('Failed to notify server:', error));
        }}
        
        showLoadingIndicator(chunkName) {{
            // Create or show loading indicator
            let indicator = document.getElementById('chunk-loading-indicator');
            if (!indicator) {{
                indicator = document.createElement('div');
                indicator.id = 'chunk-loading-indicator';
                indicator.className = 'chunk-loading-indicator';
                indicator.innerHTML = `
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    <span>Loading...</span>
                `;
                document.body.appendChild(indicator);
            }}
            
            indicator.style.display = 'flex';
            indicator.querySelector('span').textContent = `Loading ${{chunkName}}...`;
        }}
        
        hideLoadingIndicator(chunkName) {{
            const indicator = document.getElementById('chunk-loading-indicator');
            if (indicator) {{
                indicator.style.display = 'none';
            }}
        }}
        
        // Public API
        preloadChunk(chunkName) {{
            if (!this.loadedChunks.has(chunkName)) {{
                this.loadChunk(chunkName);
            }}
        }}
        
        preloadRoute(path) {{
            const chunks = this.getChunksForRoute(path);
            chunks.forEach(chunk => this.preloadChunk(chunk));
        }}
        
        getCurrentRoute() {{
            return this.currentRoute;
        }}
        
        getLoadedChunks() {{
            return Array.from(this.loadedChunks);
        }}
    }}
    
    // Initialize router
    const router = new NewUIRouter();
    
    // Expose router globally
    window.NewUIRouter = router;
    window.NewUIChunks = {{
        markLoaded: (chunkName) => router.markLoaded(chunkName),
        preload: (chunkName) => router.preloadChunk(chunkName),
        preloadRoute: (path) => router.preloadRoute(path),
        loadComponent: (componentName) => router.loadComponent(componentName)
    }};
    
    // Expose to NewUI
    if (NewUI) {{
        NewUI.router = router;
        NewUI.preloadChunk = (chunkName) => router.preloadChunk(chunkName);
        NewUI.preloadRoute = (path) => router.preloadRoute(path);
        NewUI.navigateTo = (path) => router.navigateTo(path);
        NewUI.loadComponent = (componentName) => router.loadComponent(componentName);
    }}
    
}})(window, window.NewUI);

// Add CSS for loading indicator
if (!document.getElementById('chunk-loading-styles')) {{
    const style = document.createElement('style');
    style.id = 'chunk-loading-styles';
    style.textContent = `
        .chunk-loading-indicator {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: #007bff;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            display: none;
            align-items: center;
            z-index: 10000;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
    `;
    document.head.appendChild(style);
}}
"""


# Global chunk manager instance
chunk_manager = ChunkManager()

# Convenience functions
def register_route_chunk(name: str, route_pattern: str, js_files: List[str] = None,
                        css_files: List[str] = None, components: List[str] = None,
                        dependencies: List[str] = None, preload: bool = False,
                        lazy: bool = True) -> RouteChunk:
    """Register a route-based code chunk"""
    chunk = RouteChunk(
        name=name,
        route_pattern=route_pattern,
        js_files=js_files or [],
        css_files=css_files or [],
        dependencies=dependencies or [],
        components=components or [],
        preload=preload,
        lazy=lazy
    )
    
    chunk_manager.register_route_chunk(chunk)
    return chunk

def register_component_chunk(name: str, component_name: str, js_content: str,
                           css_content: str = "", dependencies: List[str] = None) -> ComponentChunk:
    """Register a component-based code chunk"""
    chunk = ComponentChunk(
        name=name,
        component_name=component_name,
        js_content=js_content,
        css_content=css_content,
        dependencies=dependencies or []
    )
    
    chunk_manager.register_component_chunk(chunk)
    return chunk

def init_routing(app: Flask) -> ChunkManager:
    """Initialize routing system with Flask app"""
    chunk_manager.init_app(app)
    return chunk_manager