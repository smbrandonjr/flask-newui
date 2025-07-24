# Two-Way Data Binding in NewUI

NewUI provides seamless two-way data binding between form inputs and component state, making it easy to build reactive forms while maintaining server-side control.

## Features

- **Automatic Synchronization**: Form inputs automatically sync with component state
- **Multiple Binding Syntax**: Use either `data-ui-bind` or `data-ui-model` attributes
- **Server Sync**: Optional real-time synchronization with server state
- **Display Binding**: Bind text content to state values for live previews
- **Debounced Updates**: Text inputs use debounced updates to reduce server calls

## Basic Usage

### Form Input Binding

```python
# In your template
{{ ui.input(name="username", model="user.name", sync=True, label="Username") }}
{{ ui.input(name="email", type="email", model="user.email", label="Email") }}
{{ ui.textarea(name="bio", model="user.bio", rows=3, label="Bio") }}
```

### Display Binding

```html
<!-- Display bound values -->
<span data-ui-bind="user.name">Initial Name</span>
<p data-ui-bind="user.bio">Initial Bio</p>
```

### Component State

```python
@app.route('/')
def index():
    initial_state = {
        'user': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'bio': 'Developer'
        }
    }
    return render_template('form.html', initial_state=initial_state)
```

### Template Setup

```html
<div data-ui-component="user-form" 
     data-ui-id="form1" 
     data-ui-state='{{ initial_state | tojson }}'>
    
    <!-- Your form inputs here -->
    
</div>
```

## Supported Form Elements

### Text Input
```python
{{ ui.input(name="field", model="path.to.value", sync=True) }}
```

### Email Input
```python
{{ ui.input(name="email", type="email", model="user.email") }}
```

### Textarea
```python
{{ ui.textarea(name="description", model="item.description", rows=5) }}
```

### Select
```python
{{ ui.select(
    name="country",
    model="user.country",
    options=[
        {'value': 'us', 'text': 'United States'},
        {'value': 'ca', 'text': 'Canada'}
    ]
) }}
```

### Checkbox
```python
{{ ui.checkbox(name="subscribe", model="user.newsletter", label="Subscribe") }}
```

## Synchronization Options

### Local Only (Default)
Updates happen only in the browser:
```python
{{ ui.input(name="field", model="data.field") }}
```

### Server Sync
Enable real-time server synchronization:
```python
{{ ui.input(name="field", model="data.field", sync=True) }}
```

## Advanced Features

### Nested Object Paths
Bind to nested properties using dot notation:
```python
{{ ui.input(model="user.profile.settings.theme") }}
```

### Multiple Bindings
Multiple elements can bind to the same state value:
```python
{{ ui.input(name="name1", model="user.name") }}
{{ ui.input(name="name2", model="user.name") }}
<span data-ui-bind="user.name"></span>
```

### Custom State Handling

Handle state changes in JavaScript:
```javascript
// Listen for state changes
document.addEventListener('input', (e) => {
    if (e.target.hasAttribute('data-ui-model')) {
        const componentId = NewUI.getComponentId(e.target);
        const state = NewUI.state[componentId];
        console.log('State updated:', state);
    }
});
```

## Server-Side State Management

### Accessing State
```python
@app.route('/api/state/<component_id>')
def get_state(component_id):
    state = ui.state.get_state(component_id)
    return jsonify(state)
```

### Updating State
```python
@app.route('/api/update', methods=['POST'])
def update_state():
    component_id = request.json.get('component_id')
    updates = request.json.get('updates')
    ui.state.update_state(component_id, updates)
    return jsonify({'success': True})
```

## Best Practices

1. **Initialize State**: Always provide initial state for bound components
2. **Use Sync Sparingly**: Enable server sync only when needed to reduce server load
3. **Validate Server-Side**: Always validate data on the server, even with client-side binding
4. **Graceful Degradation**: Forms should work without JavaScript enabled

## Example: Complete Form

```python
from flask import Flask, render_template_string
from newui import NewUI

app = Flask(__name__)
ui = NewUI(app)

@app.route('/')
def form():
    template = '''
    <div data-ui-component="contact-form" 
         data-ui-state='{"contact": {"name": "", "email": "", "message": ""}}'>
        
        {{ ui.form(content=form_fields, action="/submit", ajax=True) }}
        
        <div class="preview">
            <h3>Preview</h3>
            <p>Name: <span data-ui-bind="contact.name">-</span></p>
            <p>Email: <span data-ui-bind="contact.email">-</span></p>
            <p>Message: <span data-ui-bind="contact.message">-</span></p>
        </div>
    </div>
    '''
    
    form_fields = f'''
        {ui.input(name="name", model="contact.name", label="Name", sync=True)}
        {ui.input(name="email", type="email", model="contact.email", label="Email")}
        {ui.textarea(name="message", model="contact.message", label="Message", rows=4)}
        {ui.button("Send", type="submit")}
    '''
    
    return render_template_string(template, form_fields=form_fields, ui=ui.components)
```

## Troubleshooting

### State Not Updating
- Ensure the component has a `data-ui-component` and `data-ui-id` attribute
- Check that the initial state includes the property path you're binding to
- Verify the `model` or `bind` attribute uses the correct path

### Server Sync Not Working
- Check that `sync=True` is set on the input
- Ensure the `/ui/state/<component_id>` endpoint is accessible
- Check browser console for any AJAX errors

### Values Not Displaying
- For display elements, use `data-ui-bind` not `data-ui-model`
- Ensure the element is inside a component with proper state initialization