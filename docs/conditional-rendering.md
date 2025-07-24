# Conditional Rendering in NewUI

NewUI provides powerful conditional rendering helpers that work seamlessly between server and client, allowing you to show or hide content based on component state.

## Features

- **Server-side and client-side rendering**: Works with or without JavaScript
- **Reactive updates**: Automatically updates when state changes
- **Complex conditions**: Supports expressions, comparisons, and logical operators
- **Multiple helpers**: `show_if`, `hide_if`, `show_unless`, and `toggle`
- **State integration**: Works with NewUI's state management system

## Basic Usage

### show_if - Show content when condition is true

```python
{{ ui.show_if("user.isLoggedIn", '''
    <div class="welcome-message">
        Welcome back!
    </div>
''') }}
```

### hide_if - Hide content when condition is true

```python
{{ ui.hide_if("user.isGuest", '''
    <div class="member-content">
        Exclusive member content here.
    </div>
''') }}
```

### show_unless - Show content unless condition is true (opposite of hide_if)

```python
{{ ui.show_unless("form.isSubmitting", '''
    <button type="submit">Submit Form</button>
''') }}
```

### toggle - Switch between two contents

```python
{{ ui.toggle("isDarkMode", 
    true_content='<span>🌙 Dark Mode</span>',
    false_content='<span>☀️ Light Mode</span>'
) }}
```

## Condition Syntax

### Simple Property Access

Access state properties using dot notation:

```python
{{ ui.show_if("showPanel", "...") }}              # Direct property
{{ ui.show_if("user.isActive", "...") }}          # Nested property
{{ ui.show_if("settings.theme.isDark", "...") }}  # Deep nesting
```

### Comparisons

Use standard JavaScript comparison operators:

```python
{{ ui.show_if("count > 0", "...") }}              # Greater than
{{ ui.show_if("age >= 18", "...") }}              # Greater or equal
{{ ui.show_if("status === 'active'", "...") }}    # Equality
{{ ui.show_if("role !== 'guest'", "...") }}       # Not equal
```

### Logical Operators

Combine conditions with AND/OR:

```python
{{ ui.show_if("user.isPremium && user.isActive", "...") }}   # AND
{{ ui.show_if("isAdmin || isModerator", "...") }}            # OR
{{ ui.show_if("!isDisabled", "...") }}                       # NOT
```

### Complex Expressions

```python
{{ ui.show_if("items.length > 0 && !isLoading", "...") }}
{{ ui.show_if("(role === 'admin' || role === 'mod') && isActive", "...") }}
{{ ui.show_if("price > 100 && price < 500", "...") }}
```

## Integration with Data Binding

Conditional rendering works seamlessly with data binding:

```python
<div data-ui-component="demo" data-ui-state='{"showDetails": false}'>
    {{ ui.checkbox(model="showDetails", label="Show details") }}
    
    {{ ui.show_if("showDetails", '''
        <div class="details">
            <h4>Additional Information</h4>
            <p>These details are shown when the checkbox is checked.</p>
        </div>
    ''') }}
</div>
```

## Dynamic Content Updates

Content inside conditionals can use data binding:

```python
{{ ui.show_if("user.name", '''
    <div class="greeting">
        Hello, <span data-ui-bind="user.name"></span>!
        You have <span data-ui-bind="user.messageCount"></span> messages.
    </div>
''') }}
```

## Common Patterns

### Loading States

```python
{{ ui.toggle("isLoading",
    true_content='<div class="spinner">Loading...</div>',
    false_content='<div class="content">{{ content }}</div>'
) }}
```

### Permission-based UI

```python
{{ ui.show_if('user.role === "admin"', '''
    <button class="btn btn-danger">Delete Item</button>
''') }}

{{ ui.hide_if('user.role === "guest"', '''
    <button class="btn btn-primary">Edit Profile</button>
''') }}
```

### Form Validation Feedback

```python
{{ ui.show_if("errors.email", '''
    <div class="error-message">
        <span data-ui-bind="errors.email"></span>
    </div>
''') }}
```

### Progressive Disclosure

```python
{{ ui.checkbox(model="showAdvanced", label="Show advanced options") }}

{{ ui.show_if("showAdvanced", '''
    <div class="advanced-options">
        <!-- Advanced form fields here -->
    </div>
''') }}
```

## Server-Side Rendering

When JavaScript is disabled, the initial visibility is determined server-side based on the initial state. The content is still rendered but hidden with CSS.

## Performance Considerations

1. **Conditions are re-evaluated** when any bound state changes
2. **Use simple conditions** when possible for better performance
3. **Hidden content is still in the DOM** (display: none), not removed
4. **Complex expressions** are evaluated safely without eval()

## API Reference

### show_if(condition, content, class_="", id="")
- `condition`: String expression to evaluate
- `content`: HTML content to conditionally show
- `class_`: Optional CSS classes
- `id`: Optional element ID

### hide_if(condition, content, class_="", id="")
- Same parameters as show_if, but hides when condition is true

### show_unless(condition, content, class_="", id="")
- Same as hide_if (alias for clarity)

### toggle(condition, true_content, false_content="", class_="", id="")
- `condition`: String expression to evaluate
- `true_content`: Content to show when true
- `false_content`: Content to show when false
- `class_`: Optional CSS classes
- `id`: Optional element ID

## Best Practices

1. **Keep conditions simple** for readability and performance
2. **Use meaningful variable names** in your state
3. **Validate conditions server-side** for security-critical UI
4. **Consider accessibility** - hidden content should not break screen reader flow
5. **Test without JavaScript** to ensure graceful degradation