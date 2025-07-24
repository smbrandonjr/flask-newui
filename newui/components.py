"""
Built-in NewUI components as Python functions
"""

from markupsafe import Markup
from typing import Optional, List, Dict, Any, Union, Callable
import json
import html


class UIComponent:
    """Base class for UI components"""
    
    @staticmethod
    def _attrs(**kwargs) -> str:
        """Convert kwargs to HTML attributes"""
        attrs = []
        for key, value in kwargs.items():
            if value is None or value is False:
                continue
            if value is True:
                attrs.append(key)
            else:
                # Convert underscores to hyphens for data attributes
                key = key.replace('_', '-')
                attrs.append(f'{key}="{value}"')
        return ' '.join(attrs)
    
    @staticmethod
    def _data_attrs(**kwargs) -> str:
        """Convert kwargs to data-* attributes"""
        import html
        attrs = []
        for key, value in kwargs.items():
            if value is not None:
                key = key.replace('_', '-')
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                # HTML escape the value to handle quotes properly
                value = html.escape(str(value))
                attrs.append(f'data-{key}="{value}"')
        return ' '.join(attrs)


class Button(UIComponent):
    """Button component"""
    
    @staticmethod
    def render(text: str = "Click me", type: str = "button", variant: str = "primary",
               onclick: str = "", disabled: bool = False, class_: str = "", 
               ui_state: Dict = None, **kwargs) -> Markup:
        """Render a button component"""
        
        attrs = {
            'type': type,
            'class': f"btn btn-{variant} {class_}".strip(),
            'disabled': disabled
        }
        
        data_attrs = {
            'ui-component': 'button'
        }
        
        if ui_state:
            data_attrs['ui-state'] = json.dumps(ui_state)
        
        if onclick:
            data_attrs['ui-click'] = onclick
        
        # Merge any additional kwargs
        attrs.update(kwargs)
        
        return Markup(
            f'<button {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'{text}'
            f'</button>'
        )


class Form(UIComponent):
    """Form component with AJAX support"""
    
    @staticmethod
    def render(content: str, action: str = "", method: str = "post", 
               ajax: bool = False, onsubmit: str = "", class_: str = "", 
               id: str = "", csrf_token: str = None) -> Markup:
        """Render a form component"""
        
        attrs = {
            'action': action,
            'method': method,
            'class': class_,
            'id': id
        }
        
        data_attrs = {}
        
        if ajax:
            data_attrs['ui-submit'] = f"ajax:{action}"
        elif onsubmit:
            data_attrs['ui-submit'] = onsubmit
        
        csrf_input = ""
        if method.lower() == "post" and csrf_token:
            csrf_input = f'<input type="hidden" name="csrf_token" value="{csrf_token}"/>'
        
        return Markup(
            f'<form {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'{csrf_input}'
            f'{content}'
            f'</form>'
        )


class Input(UIComponent):
    """Input component with data binding"""
    
    @staticmethod
    def render(name: str, type: str = "text", value: str = "", 
               placeholder: str = "", label: str = "", required: bool = False,
               bind: str = "", model: str = "", sync: bool = False,
               class_: str = "", id: str = "") -> Markup:
        """Render an input component"""
        
        if not id:
            id = name
        
        attrs = {
            'type': type,
            'name': name,
            'id': id,
            'value': value,
            'placeholder': placeholder,
            'required': required,
            'class': f"form-control {class_}".strip()
        }
        
        data_attrs = {}
        # Support both bind and model attributes
        if model:
            data_attrs['ui-model'] = model
        elif bind:
            data_attrs['ui-bind'] = bind
        
        if sync:
            data_attrs['ui-sync'] = "true"
        
        input_html = f'<input {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}/>'
        
        if label:
            return Markup(
                f'<div class="form-group">'
                f'<label for="{id}">{label}</label>'
                f'{input_html}'
                f'</div>'
            )
        
        return Markup(input_html)


class Select(UIComponent):
    """Select component"""
    
    @staticmethod
    def render(name: str, options: List[Union[str, Dict[str, str]]] = None,
               selected: str = "", label: str = "", required: bool = False,
               bind: str = "", model: str = "", sync: bool = False,
               multiple: bool = False, class_: str = "", id: str = "") -> Markup:
        """Render a select component"""
        
        if not id:
            id = name
        
        if options is None:
            options = []
        
        attrs = {
            'name': name,
            'id': id,
            'required': required,
            'multiple': multiple,
            'class': f"form-control {class_}".strip()
        }
        
        data_attrs = {}
        # Support both bind and model attributes
        if model:
            data_attrs['ui-model'] = model
        elif bind:
            data_attrs['ui-bind'] = bind
        
        if sync:
            data_attrs['ui-sync'] = "true"
        
        options_html = []
        for option in options:
            if isinstance(option, dict):
                value = option.get('value', '')
                text = option.get('text', value)
            else:
                value = text = str(option)
            
            selected_attr = 'selected' if value == selected else ''
            options_html.append(f'<option value="{value}" {selected_attr}>{text}</option>')
        
        select_html = (
            f'<select {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'{"".join(options_html)}'
            f'</select>'
        )
        
        if label:
            return Markup(
                f'<div class="form-group">'
                f'<label for="{id}">{label}</label>'
                f'{select_html}'
                f'</div>'
            )
        
        return Markup(select_html)


class Textarea(UIComponent):
    """Textarea component with data binding"""
    
    @staticmethod
    def render(name: str, value: str = "", rows: int = 3,
               placeholder: str = "", label: str = "", required: bool = False,
               bind: str = "", model: str = "", sync: bool = False,
               class_: str = "", id: str = "") -> Markup:
        """Render a textarea component"""
        
        if not id:
            id = name
        
        attrs = {
            'name': name,
            'id': id,
            'rows': rows,
            'placeholder': placeholder,
            'required': required,
            'class': f"form-control {class_}".strip()
        }
        
        data_attrs = {}
        # Support both bind and model attributes
        if model:
            data_attrs['ui-model'] = model
        elif bind:
            data_attrs['ui-bind'] = bind
        
        if sync:
            data_attrs['ui-sync'] = "true"
        
        textarea_html = f'<textarea {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>{value}</textarea>'
        
        if label:
            return Markup(
                f'<div class="form-group">'
                f'<label for="{id}">{label}</label>'
                f'{textarea_html}'
                f'</div>'
            )
        
        return Markup(textarea_html)


class Checkbox(UIComponent):
    """Checkbox component with data binding"""
    
    @staticmethod
    def render(name: str, label: str = "", checked: bool = False,
               bind: str = "", model: str = "", sync: bool = False,
               class_: str = "", id: str = "") -> Markup:
        """Render a checkbox component"""
        
        if not id:
            id = name
        
        attrs = {
            'type': 'checkbox',
            'name': name,
            'id': id,
            'checked': checked,
            'class': f"form-check-input {class_}".strip()
        }
        
        data_attrs = {}
        # Support both bind and model attributes
        if model:
            data_attrs['ui-model'] = model
        elif bind:
            data_attrs['ui-bind'] = bind
        
        if sync:
            data_attrs['ui-sync'] = "true"
        
        checkbox_html = f'<input {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}/>'
        
        if label:
            return Markup(
                f'<div class="form-check">'
                f'{checkbox_html}'
                f'<label class="form-check-label" for="{id}">{label}</label>'
                f'</div>'
            )
        
        return Markup(checkbox_html)


class Card(UIComponent):
    """Card component"""
    
    @staticmethod
    def render(content: str, title: str = "", class_: str = "", 
               footer: str = "") -> Markup:
        """Render a card component"""
        
        header_html = ""
        if title:
            header_html = f'<div class="card-header">{title}</div>'
        
        footer_html = ""
        if footer:
            footer_html = f'<div class="card-footer">{footer}</div>'
        
        return Markup(
            f'<div class="card {class_}" data-ui-component="card">'
            f'{header_html}'
            f'<div class="card-body">{content}</div>'
            f'{footer_html}'
            f'</div>'
        )


class ConditionalWrapper(UIComponent):
    """Base class for conditional rendering"""
    
    @staticmethod
    def show_if(condition: str, content: str, class_: str = "", id: str = "") -> Markup:
        """Render content only if condition is true"""
        attrs = {
            'class': class_,
            'id': id
        }
        
        data_attrs = {
            'ui-show': condition
        }
        
        # Remove empty attributes
        attrs = {k: v for k, v in attrs.items() if v}
        
        return Markup(
            f'<div {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'{content}'
            f'</div>'
        )
    
    @staticmethod
    def hide_if(condition: str, content: str, class_: str = "", id: str = "") -> Markup:
        """Hide content if condition is true"""
        attrs = {
            'class': class_,
            'id': id
        }
        
        data_attrs = {
            'ui-hide': condition
        }
        
        # Remove empty attributes
        attrs = {k: v for k, v in attrs.items() if v}
        
        return Markup(
            f'<div {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'{content}'
            f'</div>'
        )
    
    @staticmethod
    def show_unless(condition: str, content: str, class_: str = "", id: str = "") -> Markup:
        """Show content unless condition is true (opposite of hide_if)"""
        return ConditionalWrapper.hide_if(condition, content, class_, id)
    
    @staticmethod
    def toggle(condition: str, true_content: str, false_content: str = "", 
               class_: str = "", id: str = "") -> Markup:
        """Toggle between two contents based on condition"""
        attrs = {
            'class': class_,
            'id': id
        }
        
        data_attrs = {
            'ui-toggle': condition
        }
        
        # Remove empty attributes
        attrs = {k: v for k, v in attrs.items() if v}
        
        return Markup(
            f'<div {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'<div data-ui-when="true">{true_content}</div>'
            f'<div data-ui-when="false">{false_content}</div>'
            f'</div>'
        )


class ListRenderer(UIComponent):
    """List rendering component with efficient updates"""
    
    @staticmethod
    def for_each(items_path: str, item_var: str = "item", index_var: str = "index",
                 template: str = "", key: str = "", class_: str = "", id: str = "",
                 empty_message: str = "No items to display") -> Markup:
        """
        Render a list of items with efficient updates
        
        Args:
            items_path: Path to the items array in state (e.g., "todos", "user.items")
            item_var: Variable name for each item in the template (default: "item")
            index_var: Variable name for the index (default: "index")
            template: HTML template for each item (can use {item} and {index} placeholders)
            key: Property name to use as unique key (e.g., "id")
            class_: CSS classes for the container
            id: ID for the container
            empty_message: Message to show when list is empty
        """
        attrs = {
            'class': f"ui-list {class_}".strip(),
            'id': id
        }
        
        data_attrs = {
            'ui-list': items_path,
            'ui-item-var': item_var,
            'ui-index-var': index_var,
            'ui-key': key,
            'ui-empty': empty_message
        }
        
        # Remove empty attributes
        attrs = {k: v for k, v in attrs.items() if v}
        
        # Process template to create the item template
        if template:
            # Store the template as a data attribute
            data_attrs['ui-template'] = html.escape(template)
        
        return Markup(
            f'<div {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'<!-- List items will be rendered here -->'
            f'</div>'
        )
    
    @staticmethod
    def list_item(content: str, key: str = "", class_: str = "") -> Markup:
        """
        Wrap content as a list item for better structure
        
        Args:
            content: The item content
            key: Unique key for the item
            class_: CSS classes
        """
        attrs = {
            'class': f"ui-list-item {class_}".strip()
        }
        
        data_attrs = {}
        if key:
            data_attrs['ui-key'] = key
        
        return Markup(
            f'<div {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'{content}'
            f'</div>'
        )


class LifecycleComponent(UIComponent):
    """Component with lifecycle hooks support"""
    
    @staticmethod
    def component(name: str, template: str = "", 
                  init: Callable = None,
                  mounted: Callable = None,
                  before_update: Callable = None,
                  updated: Callable = None,
                  before_destroy: Callable = None,
                  destroyed: Callable = None,
                  class_: str = "", id: str = "",
                  **data_attrs) -> Markup:
        """
        Create a component with lifecycle hooks
        
        Args:
            name: Component name
            template: HTML template/content
            init: Called when component is initialized
            mounted: Called after component is mounted to DOM
            before_update: Called before state update
            updated: Called after state update
            before_destroy: Called before component removal
            destroyed: Called after component removal
            class_: CSS classes
            id: Component ID
            **data_attrs: Additional data attributes
        """
        attrs = {
            'class': class_,
            'id': id
        }
        
        # Set up data attributes
        component_attrs = {
            'ui-component': name,
            'ui-lifecycle': 'true'
        }
        component_attrs.update(data_attrs)
        
        # Remove empty attributes
        attrs = {k: v for k, v in attrs.items() if v}
        
        # Register lifecycle hooks via script if provided
        lifecycle_script = ""
        hooks = {}
        if init: hooks['init'] = 'init'
        if mounted: hooks['mounted'] = 'mounted'
        if before_update: hooks['beforeUpdate'] = 'beforeUpdate'
        if updated: hooks['updated'] = 'updated'
        if before_destroy: hooks['beforeDestroy'] = 'beforeDestroy'
        if destroyed: hooks['destroyed'] = 'destroyed'
        
        if hooks:
            # We'll use data attributes to indicate which hooks are available
            component_attrs['ui-hooks'] = ','.join(hooks.keys())
        
        return Markup(
            f'<div {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**component_attrs)}>'
            f'{template}'
            f'</div>'
        )


class Alert(UIComponent):
    """Alert component"""
    
    @staticmethod
    def render(message: str, type: str = "info", dismissible: bool = False,
               class_: str = "") -> Markup:
        """Render an alert component"""
        
        dismiss_class = "alert-dismissible" if dismissible else ""
        dismiss_button = ""
        
        if dismissible:
            dismiss_button = (
                '<button type="button" class="close" data-ui-click="dismiss">'
                '<span aria-hidden="true">&times;</span>'
                '</button>'
            )
        
        return Markup(
            f'<div class="alert alert-{type} {dismiss_class} {class_}" '
            f'role="alert" data-ui-component="alert">'
            f'{message}'
            f'{dismiss_button}'
            f'</div>'
        )


class LoadingState(UIComponent):
    """Loading state component"""
    
    @staticmethod
    def spinner(size: str = "md", variant: str = "primary", text: str = "", 
                inline: bool = False, class_: str = "") -> Markup:
        """Render a loading spinner"""
        
        size_class = {
            "sm": "spinner-border-sm",
            "md": "",
            "lg": "spinner-lg"
        }.get(size, "")
        
        container_class = "d-inline-flex align-items-center" if inline else "text-center"
        
        spinner_html = (
            f'<div class="spinner-border text-{variant} {size_class}" role="status">'
            f'<span class="visually-hidden">Loading...</span>'
            f'</div>'
        )
        
        if text:
            if inline:
                spinner_html += f'<span class="ms-2">{text}</span>'
            else:
                spinner_html += f'<div class="mt-2">{text}</div>'
        
        return Markup(
            f'<div class="{container_class} {class_}" data-ui-component="loading">'
            f'{spinner_html}'
            f'</div>'
        )
    
    @staticmethod
    def skeleton(lines: int = 3, width: str = "100%", class_: str = "") -> Markup:
        """Render skeleton loading placeholder"""
        
        lines_html = []
        for i in range(lines):
            line_width = width
            # Vary width for last line to look more natural
            if i == lines - 1 and lines > 1:
                line_width = "75%"
            
            lines_html.append(
                f'<div class="skeleton-line" style="width: {line_width}"></div>'
            )
        
        return Markup(
            f'<div class="skeleton {class_}" data-ui-component="skeleton">'
            f'{"".join(lines_html)}'
            f'</div>'
        )
    
    @staticmethod
    def overlay(content: str = "", spinner: bool = True, class_: str = "") -> Markup:
        """Render loading overlay"""
        
        spinner_html = ""
        if spinner:
            spinner_html = (
                '<div class="spinner-border text-primary mb-3" role="status">'
                '<span class="visually-hidden">Loading...</span>'
                '</div>'
            )
        
        return Markup(
            f'<div class="loading-overlay {class_}" data-ui-component="loading-overlay">'
            f'<div class="loading-content">'
            f'{spinner_html}'
            f'{content}'
            f'</div>'
            f'</div>'
        )
    
    @staticmethod
    def button_loading(text: str = "Loading...", variant: str = "primary", 
                      disabled: bool = True, class_: str = "") -> Markup:
        """Render a loading button state"""
        
        return Markup(
            f'<button class="btn btn-{variant} {class_}" disabled="{disabled}" '
            f'data-ui-component="loading-button">'
            f'<span class="spinner-border spinner-border-sm me-2" role="status"></span>'
            f'{text}'
            f'</button>'
        )


class LoadingWrapper(UIComponent):
    """Wrapper for content with loading states"""
    
    @staticmethod
    def wrap(content: str, loading_text: str = "Loading...", 
             loading_type: str = "spinner", show_loading: bool = False,
             class_: str = "", id: str = "") -> Markup:
        """Wrap content with loading state capability"""
        
        attrs = {
            'class': f"loading-wrapper {class_}".strip(),
            'id': id
        }
        
        data_attrs = {
            'ui-loading-text': loading_text,
            'ui-loading-type': loading_type
        }
        
        # Remove empty attributes
        attrs = {k: v for k, v in attrs.items() if v}
        
        # Loading overlay (hidden by default)
        loading_overlay = ""
        if loading_type == "spinner":
            loading_overlay = LoadingState.spinner(text=loading_text)
        elif loading_type == "skeleton":
            loading_overlay = LoadingState.skeleton()
        elif loading_type == "overlay":
            loading_overlay = LoadingState.overlay(loading_text)
        
        display_style = "" if show_loading else "display: none;"
        
        return Markup(
            f'<div {UIComponent._attrs(**attrs)} {UIComponent._data_attrs(**data_attrs)}>'
            f'<div class="loading-state" style="{display_style}">{loading_overlay}</div>'
            f'<div class="content-state" style="{"display: none;" if show_loading else ""}">{content}</div>'
            f'</div>'
        )


# Create singleton instances for cleaner API
button = Button.render
form = Form.render
input = Input.render
select = Select.render
textarea = Textarea.render
checkbox = Checkbox.render
card = Card.render
alert = Alert.render

# Conditional rendering
show_if = ConditionalWrapper.show_if
hide_if = ConditionalWrapper.hide_if
show_unless = ConditionalWrapper.show_unless
toggle = ConditionalWrapper.toggle

# List rendering
for_each = ListRenderer.for_each
list_item = ListRenderer.list_item

# Lifecycle component
component = LifecycleComponent.component

# Loading states
spinner = LoadingState.spinner
skeleton = LoadingState.skeleton
loading_overlay = LoadingState.overlay
loading_button = LoadingState.button_loading
loading_wrapper = LoadingWrapper.wrap