# CLAUDE.md - NewUI Framework Development Guide

## Project Overview

**Project Name**: NewUI  
**Purpose**: A modern frontend framework that bridges the gap between traditional Flask/Jinja2 development and modern reactive frameworks like Vue.js

## Core Philosophy

NewUI is designed to enhance Jinja2 templating with reactive capabilities while maintaining the simplicity and server-side rendering benefits that make Flask development straightforward. It should feel familiar to Flask developers while providing modern UI capabilities.

## Technical Requirements

### Foundation
- **Built on**: Jinja2 templating engine
- **Backend**: Flask (with flask_login and flask_sqlalchemy)
- **Frontend**: Vanilla JavaScript, CSS, HTML

### Key Design Principles
1. **Jinja2-First**: All components should leverage Jinja2's existing capabilities
2. **Progressive Enhancement**: Works without JavaScript, enhanced with it
3. **Flask-Native**: Seamless integration with Flask's request/response cycle
4. **Zero Build Step**: No webpack, no compilation required for basic usage
5. **CSS Framework Agnostic**: Easy integration with Tailwind, Bootstrap, or custom CSS

## Framework Architecture

### Component System
- Components should be Jinja2 macros with enhanced capabilities
- Support for props/parameters passed from parent templates
- Automatic state management through data attributes
- Event handling via declarative attributes

### Reactivity Model
- Server-side state management with client-side updates
- AJAX-powered partial template rendering
- WebSocket support for real-time updates (optional)
- Declarative data binding syntax that extends Jinja2

### File Structure
```
newui/
├── core/
│   ├── __init__.py
│   ├── components.py      # Component registration and handling
│   ├── renderer.py        # Enhanced Jinja2 rendering
│   ├── state.py          # State management utilities
│   └── ajax.py           # AJAX/partial rendering handlers
├── static/
│   ├── newui.js          # Core JavaScript library
│   └── newui.css         # Minimal default styles
├── templates/
│   ├── components/       # Built-in component templates
│   └── layouts/          # Base layouts
└── newui.py    # Flask integration
```

## Implementation Guidelines

### Component Example
```jinja2
{# Define a reactive component #}
{% macro Button(text="Click me", onclick="", variant="primary", ui_state={}) %}
  <button 
    class="btn btn-{{ variant }}" 
    data-ui-component="Button"
    data-ui-state="{{ ui_state | tojson }}"
    {% if onclick %}data-ui-action="{{ onclick }}"{% endif %}
  >
    {{ text }}
  </button>
{% endmacro %}

{# Usage #}
{{ Button("Save", onclick="save_form", variant="success") }}
```

### State Management
- Server maintains authoritative state
- Client-side state for UI interactions only
- Automatic syncing via AJAX calls
- Form submissions should work without JavaScript

### Event Handling
```javascript
// Declarative event syntax
<div data-ui-click="toggleMenu" data-ui-hover="showTooltip">

// Should translate to proper event listeners
// No inline JavaScript in templates
```

### Partial Rendering
```python
# Flask route for partial updates
@app.route('/ui/partial/<component>')
def render_partial(component):
    # Return just the component HTML
    return render_template(f'components/{component}.html', **request.args)
```

## Features to Implement

### Phase 1: Core
1. Component macro system with parameter validation
2. Automatic AJAX partial rendering
3. Basic event handling (click, submit, change)
4. State persistence via data attributes
5. Flask extension for easy integration

### Phase 2: Enhanced Interactivity
1. Two-way data binding for forms
2. Conditional rendering helpers
3. List rendering with efficient updates
4. Component lifecycle hooks
5. Built-in loading states

### Phase 3: Advanced Features
1. WebSocket support for real-time updates
2. Component composition patterns
3. State stores for complex apps
4. Route-based code splitting
5. Development tools (debugger, component inspector)

## API Design

### Python API
```python
from flask import Flask
from newui import NewUI

app = Flask(__name__)
ui = NewUI(app)

# Register custom components
@ui.component
def Card(title, content, **kwargs):
    return render_template('components/card.html', 
                         title=title, content=content, **kwargs)

# Reactive route
@app.route('/dashboard')
@ui.reactive  # Enables partial rendering
def dashboard():
    return render_template('dashboard.html', data=get_dashboard_data())
```

### Template API
```jinja2
{# Import NewUI #}
{% import 'newui/core.html' as ui %}

{# Reactive form #}
{% call ui.form(action="/save", reactive=true) %}
  {{ ui.input("name", value=user.name, bind="user.name") }}
  {{ ui.button("Save", type="submit") }}
{% endcall %}

{# Conditional rendering #}
{{ ui.show_if("user.is_premium") }}
  <div>Premium content here</div>
{{ ui.end_if() }}

{# List rendering #}
{{ ui.for_each(items, "item") }}
  <li>{{ item.name }} - {{ item.price }}</li>
{{ ui.end_for() }}
```

## Development Constraints

1. **No Build Tools Required**: Should work with simple file includes
2. **Graceful Degradation**: Full functionality without JavaScript
3. **Minimal Dependencies**: Only Flask and Jinja2 as hard requirements
4. **Performance First**: Leverage server-side rendering, minimize client work
5. **Developer Experience**: Clear error messages, good debugging tools

## Integration Examples

### With Tailwind CSS
```html
<!-- Just include Tailwind normally -->
<link href="https://cdn.tailwindcss.com" rel="stylesheet">

<!-- Components use Tailwind classes -->
{{ ui.button("Click me", class="bg-blue-500 hover:bg-blue-700") }}
```

### With Bootstrap
```html
<!-- Include Bootstrap -->
<link href="bootstrap.min.css" rel="stylesheet">

<!-- Components adapt to Bootstrap -->
{{ ui.button("Click me", class="btn btn-primary") }}
```

## Testing Strategy

1. **Unit Tests**: Test component rendering and state management
2. **Integration Tests**: Test Flask integration and AJAX endpoints
3. **E2E Tests**: Test full user flows with and without JavaScript
4. **Performance Tests**: Ensure minimal overhead vs vanilla Flask

## Documentation Requirements

1. **Getting Started**: 5-minute quick start guide
2. **Component Library**: Catalog of built-in components
3. **Migration Guide**: Converting existing Jinja2 templates
4. **Best Practices**: Patterns for common use cases
5. **API Reference**: Complete API documentation

## Success Criteria

1. A Flask developer can adopt NewUI without learning new concepts
2. Pages work without JavaScript but are enhanced with it
3. Performance is within 10% of vanilla Flask/Jinja2
4. Compatible with existing Flask extensions
5. Supports modern UI patterns (modals, notifications, live updates)

## Example Application

Create a todo list app that demonstrates:
- CRUD operations with partial updates
- Real-time updates via WebSocket (optional)
- Form validation with and without JS
- Responsive design with chosen CSS framework
- State management across page refreshes

## Development Philosophy

When implementing features, always ask:
1. Does this maintain Jinja2's simplicity?
2. Will this work without JavaScript?
3. Is this familiar to Flask developers?
4. Does this add meaningful value over vanilla Jinja2?
5. Can this integrate with existing Flask patterns?

Remember: NewUI should feel like a natural evolution of Flask/Jinja2 development, not a completely new paradigm.