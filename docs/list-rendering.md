# List Rendering in NewUI

NewUI provides efficient list rendering with automatic DOM updates, keyed elements for optimal performance, and seamless integration with the state management system.

## Features

- **Efficient DOM updates**: Only changed elements are updated
- **Keyed rendering**: Use unique keys for optimal performance
- **Template-based**: Simple template syntax with variable substitution
- **Empty state handling**: Show custom messages for empty lists
- **Reactive updates**: Lists automatically update when state changes
- **Nested data support**: Access nested properties in templates

## Basic Usage

### Simple List

```python
{{ ui.for_each("items", 
    template='<div class="item">{name} - ${price}</div>',
    key="id"
) }}
```

### With Custom Variables

```python
{{ ui.for_each("users",
    item_var="user",
    index_var="idx",
    template='''
        <div class="user-card">
            <h5>{idx + 1}. {user.name}</h5>
            <p>{user.email}</p>
        </div>
    ''',
    key="id"
) }}
```

### Empty State

```python
{{ ui.for_each("notifications",
    template='<div class="notification">{message}</div>',
    empty_message="No new notifications"
) }}
```

## Template Syntax

### Variable Substitution

Use curly braces to insert values:

```html
{name}           <!-- Direct property -->
{user.email}     <!-- Nested property -->
{index}          <!-- Current index -->
{item.price}     <!-- Item property -->
```

### Template Examples

```python
# Simple item
template='<li>{text}</li>'

# Card layout
template='''
    <div class="card">
        <h4>{title}</h4>
        <p>{description}</p>
        <span class="price">${price}</span>
    </div>
'''

# With conditional classes
template='''
    <div class="todo {completed ? 'done' : 'pending'}">
        <input type="checkbox" data-ui-model="completed">
        <span>{text}</span>
    </div>
'''
```

## State Integration

Lists automatically update when the bound array changes:

```python
<div data-ui-component="todo-app" data-ui-state='{"todos": []}'>
    {{ ui.input(model="newTodo", placeholder="Add todo...") }}
    <button data-ui-click="addTodo">Add</button>
    
    {{ ui.for_each("todos",
        template='''
            <div class="todo-item">
                <span>{text}</span>
                <button data-ui-click="removeTodo" data-id="{id}">×</button>
            </div>
        ''',
        key="id"
    ) }}
</div>
```

JavaScript handlers:
```javascript
NewUI.registerHandler('addTodo', function(element) {
    const componentId = NewUI.getComponentId(element);
    const state = NewUI.state[componentId];
    
    if (state.newTodo) {
        if (!state.todos) state.todos = [];
        state.todos.push({
            id: Date.now(),
            text: state.newTodo
        });
        NewUI.setStateValue(componentId, 'newTodo', '');
    }
});
```

## Keyed Updates

Using keys enables efficient DOM updates:

```python
{{ ui.for_each("items", template="...", key="id") }}
```

Benefits of keyed rendering:
- Preserves element state (input values, focus)
- Enables smooth animations
- Optimizes performance for large lists
- Maintains correct element associations

## Data Binding in Lists

Elements within lists can use data binding:

```python
{{ ui.for_each("tasks",
    template='''
        <div class="task">
            <input type="checkbox" data-ui-model="completed">
            <input type="text" data-ui-model="title" class="form-control">
        </div>
    ''',
    key="id"
) }}
```

The bindings automatically adjust to the correct array index.

## Dynamic List Operations

### Adding Items

```javascript
const state = NewUI.state[componentId];
if (!state.items) state.items = [];
state.items.push({ id: Date.now(), name: 'New Item' });
// List updates automatically
```

### Removing Items

```javascript
const index = state.items.findIndex(item => item.id === itemId);
if (index !== -1) {
    state.items.splice(index, 1);
    NewUI.updateLists(componentId, 'items');
}
```

### Updating Items

```javascript
const item = state.items.find(item => item.id === itemId);
if (item) {
    item.name = 'Updated Name';
    NewUI.updateLists(componentId, 'items');
}
```

### Sorting/Filtering

```javascript
// Sort
state.items.sort((a, b) => a.name.localeCompare(b.name));
NewUI.updateLists(componentId, 'items');

// Filter (create derived list)
state.filteredItems = state.items.filter(item => item.active);
NewUI.updateLists(componentId, 'filteredItems');
```

## API Reference

### for_each(items_path, template, **options)

Parameters:
- `items_path` (required): Path to array in state (e.g., "todos", "user.items")
- `template` (required): HTML template string with variable substitutions
- `key`: Property name for unique keys (recommended for performance)
- `item_var`: Variable name for items (default: "item")
- `index_var`: Variable name for index (default: "index")
- `empty_message`: Message when list is empty
- `class_`: CSS classes for container
- `id`: ID for container element

### Template Variables

Available in templates:
- `{item}` or custom item variable: Current item object
- `{index}` or custom index variable: Current item index (0-based)
- `{item.property}`: Any property of the item
- Direct properties when using spread

## Performance Tips

1. **Always use keys** when items have unique IDs
2. **Avoid inline functions** in templates
3. **Batch updates** when modifying multiple items
4. **Use efficient data structures** (objects with IDs vs arrays)
5. **Debounce rapid updates** for better performance

## Common Patterns

### Todo List

```python
{{ ui.for_each("todos",
    template='''
        <div class="todo {completed ? 'completed' : ''}">
            <input type="checkbox" data-ui-model="completed">
            <span>{text}</span>
            <button data-ui-click="deleteTodo" data-id="{id}">Delete</button>
        </div>
    ''',
    key="id",
    empty_message="No todos yet!"
) }}
```

### User Cards

```python
{{ ui.for_each("users",
    template='''
        <div class="user-card">
            <img src="{avatar}" alt="{name}">
            <h4>{name}</h4>
            <p>{role}</p>
            <a href="mailto:{email}">{email}</a>
        </div>
    ''',
    key="id"
) }}
```

### Data Table

```python
<table class="table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {{ ui.for_each("users",
            template='''
                <tr>
                    <td>{name}</td>
                    <td>{email}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" 
                                data-ui-click="editUser" data-id="{id}">
                            Edit
                        </button>
                    </td>
                </tr>
            ''',
            key="id"
        ) }}
    </tbody>
</table>
```

## Limitations

1. Templates don't support nested NewUI components (use JavaScript for complex cases)
2. No built-in virtualization for very large lists (10,000+ items)
3. Template syntax is simple string replacement (no expressions)

For complex rendering needs, consider using JavaScript to manually render items with full NewUI component support.