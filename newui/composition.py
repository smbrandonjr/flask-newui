"""
Component composition patterns for NewUI
"""

from typing import Dict, List, Any, Optional, Callable, Union
from markupsafe import Markup
import json
import html
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class ComponentProps:
    """Properties passed to a component"""
    data: Dict[str, Any] = field(default_factory=dict)
    children: List['Component'] = field(default_factory=list)
    slots: Dict[str, 'Component'] = field(default_factory=dict)
    events: Dict[str, str] = field(default_factory=dict)
    css_classes: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


class Component(ABC):
    """Base class for composable components"""
    
    def __init__(self, name: str, props: ComponentProps = None):
        self.name = name
        self.props = props or ComponentProps()
        self.state: Dict[str, Any] = {}
        self.children: List['Component'] = []
        self.parent: Optional['Component'] = None
        self.component_id: Optional[str] = None
    
    @abstractmethod
    def render(self) -> Markup:
        """Render the component to HTML"""
        pass
    
    def add_child(self, child: 'Component'):
        """Add a child component"""
        child.parent = self
        self.children.append(child)
    
    def add_slot(self, name: str, component: 'Component'):
        """Add a named slot component"""
        self.props.slots[name] = component
        component.parent = self
    
    def get_slot(self, name: str, default: str = "") -> Markup:
        """Render a named slot"""
        if name in self.props.slots:
            return self.props.slots[name].render()
        return Markup(default)
    
    def render_children(self) -> Markup:
        """Render all child components"""
        return Markup(''.join(child.render() for child in self.children))
    
    def set_state(self, key: str, value: Any):
        """Set component state"""
        self.state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get component state"""
        return self.state.get(key, default)
    
    def emit_event(self, event_name: str, data: Any = None):
        """Emit an event to parent component"""
        if self.parent and hasattr(self.parent, 'handle_event'):
            self.parent.handle_event(event_name, data, self)
    
    def handle_event(self, event_name: str, data: Any, source: 'Component'):
        """Handle events from child components"""
        pass
    
    def _render_attributes(self) -> str:
        """Render HTML attributes"""
        attrs = []
        
        # CSS classes
        if self.props.css_classes:
            attrs.append(f'class="{" ".join(self.props.css_classes)}"')
        
        # Component attributes
        for key, value in self.props.attributes.items():
            if value is not None:
                key = key.replace('_', '-')
                attrs.append(f'{key}="{html.escape(str(value))}"')
        
        # Data attributes
        if self.state:
            attrs.append(f'data-ui-state="{html.escape(json.dumps(self.state))}"')
        
        if self.component_id:
            attrs.append(f'data-ui-id="{self.component_id}"')
        
        attrs.append(f'data-ui-component="{self.name}"')
        
        return ' '.join(attrs)


class HTMLComponent(Component):
    """Simple HTML wrapper component"""
    
    def __init__(self, tag: str, content: str = "", props: ComponentProps = None):
        super().__init__(f"html-{tag}", props)
        self.tag = tag
        self.content = content
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        children_html = self.render_children()
        
        return Markup(
            f'<{self.tag} {attrs}>'
            f'{self.content}'
            f'{children_html}'
            f'</{self.tag}>'
        )


class CardComponent(Component):
    """Reusable card component with slots"""
    
    def __init__(self, title: str = "", props: ComponentProps = None):
        super().__init__("card", props)
        self.title = title
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        
        header_content = self.get_slot('header', self.title)
        body_content = self.get_slot('body', self.render_children())
        footer_content = self.get_slot('footer')
        
        header_html = f'<div class="card-header">{header_content}</div>' if header_content else ''
        footer_html = f'<div class="card-footer">{footer_content}</div>' if footer_content else ''
        
        return Markup(
            f'<div class="card" {attrs}>'
            f'{header_html}'
            f'<div class="card-body">{body_content}</div>'
            f'{footer_html}'
            f'</div>'
        )


class FormComponent(Component):
    """Composable form component"""
    
    def __init__(self, action: str = "", method: str = "post", props: ComponentProps = None):
        super().__init__("form", props)
        self.action = action
        self.method = method
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        
        form_attrs = []
        if self.action:
            form_attrs.append(f'action="{self.action}"')
        if self.method:
            form_attrs.append(f'method="{self.method}"')
        
        # Handle form events
        if 'submit' in self.props.events:
            form_attrs.append(f'data-ui-submit="{self.props.events["submit"]}"')
        
        form_attrs_str = ' '.join(form_attrs)
        
        return Markup(
            f'<form {form_attrs_str} {attrs}>'
            f'{self.render_children()}'
            f'</form>'
        )


class ListComponent(Component):
    """Composable list component with item templates"""
    
    def __init__(self, items: List[Any] = None, item_template: 'Component' = None, props: ComponentProps = None):
        super().__init__("list", props)
        self.items = items or []
        self.item_template = item_template
        self.set_state('items', self.items)
    
    def set_items(self, items: List[Any]):
        """Update list items"""
        self.items = items
        self.set_state('items', items)
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        
        if not self.items and not self.item_template:
            return Markup(f'<div {attrs}>{self.render_children()}</div>')
        
        # Render items using template
        items_html = []
        for index, item in enumerate(self.items):
            if self.item_template:
                # Clone template and set item data
                item_component = self._clone_template(self.item_template, item, index)
                items_html.append(item_component.render())
        
        return Markup(
            f'<div {attrs}>'
            f'{"".join(items_html)}'
            f'{self.render_children()}'
            f'</div>'
        )
    
    def _clone_template(self, template: Component, item: Any, index: int) -> Component:
        """Clone template component with item data"""
        # This is a simplified clone - in a full implementation,
        # you'd want deep cloning of the component tree
        cloned = template.__class__(template.name, template.props)
        cloned.set_state('item', item)
        cloned.set_state('index', index)
        return cloned


class ConditionalComponent(Component):
    """Component for conditional rendering"""
    
    def __init__(self, condition: Union[bool, Callable], props: ComponentProps = None):
        super().__init__("conditional", props)
        self.condition = condition
    
    def render(self) -> Markup:
        # Evaluate condition
        should_render = self.condition
        if callable(self.condition):
            should_render = self.condition(self.state, self.props.data)
        
        if should_render:
            true_content = self.get_slot('true', self.render_children())
            return Markup(f'<div style="display: block;">{true_content}</div>')
        else:
            false_content = self.get_slot('false')
            return Markup(f'<div style="display: block;">{false_content}</div>')


class LayoutComponent(Component):
    """Layout component with multiple slots"""
    
    def __init__(self, layout_type: str = "default", props: ComponentProps = None):
        super().__init__(f"layout-{layout_type}", props)
        self.layout_type = layout_type
    
    def render(self) -> Markup:
        attrs = self._render_attributes()
        
        if self.layout_type == "two-column":
            return self._render_two_column(attrs)
        elif self.layout_type == "three-column":
            return self._render_three_column(attrs)
        elif self.layout_type == "header-main-footer":
            return self._render_header_main_footer(attrs)
        else:
            return self._render_default(attrs)
    
    def _render_two_column(self, attrs: str) -> Markup:
        left = self.get_slot('left')
        right = self.get_slot('right')
        
        return Markup(
            f'<div class="row" {attrs}>'
            f'<div class="col-md-6">{left}</div>'
            f'<div class="col-md-6">{right}</div>'
            f'</div>'
        )
    
    def _render_three_column(self, attrs: str) -> Markup:
        left = self.get_slot('left')
        center = self.get_slot('center')
        right = self.get_slot('right')
        
        return Markup(
            f'<div class="row" {attrs}>'
            f'<div class="col-md-4">{left}</div>'
            f'<div class="col-md-4">{center}</div>'
            f'<div class="col-md-4">{right}</div>'
            f'</div>'
        )
    
    def _render_header_main_footer(self, attrs: str) -> Markup:
        header = self.get_slot('header')
        main = self.get_slot('main', self.render_children())
        footer = self.get_slot('footer')
        
        return Markup(
            f'<div class="layout-container" {attrs}>'
            f'<header class="layout-header">{header}</header>'
            f'<main class="layout-main">{main}</main>'
            f'<footer class="layout-footer">{footer}</footer>'
            f'</div>'
        )
    
    def _render_default(self, attrs: str) -> Markup:
        return Markup(
            f'<div {attrs}>'
            f'{self.render_children()}'
            f'</div>'
        )


class ComponentBuilder:
    """Builder pattern for creating complex components"""
    
    def __init__(self, component_class: type, *args, **kwargs):
        self.component = component_class(*args, **kwargs)
    
    def with_props(self, **props) -> 'ComponentBuilder':
        """Set component properties"""
        for key, value in props.items():
            setattr(self.component.props, key, value)
        return self
    
    def with_state(self, **state) -> 'ComponentBuilder':
        """Set component state"""
        for key, value in state.items():
            self.component.set_state(key, value)
        return self
    
    def with_children(self, *children) -> 'ComponentBuilder':
        """Add child components"""
        for child in children:
            self.component.add_child(child)
        return self
    
    def with_slot(self, name: str, component: Component) -> 'ComponentBuilder':
        """Add a named slot"""
        self.component.add_slot(name, component)
        return self
    
    def with_css_class(self, *classes) -> 'ComponentBuilder':
        """Add CSS classes"""
        self.component.props.css_classes.extend(classes)
        return self
    
    def with_event(self, event_name: str, handler: str) -> 'ComponentBuilder':
        """Add event handler"""
        self.component.props.events[event_name] = handler
        return self
    
    def with_attribute(self, name: str, value: Any) -> 'ComponentBuilder':
        """Add HTML attribute"""
        self.component.props.attributes[name] = value
        return self
    
    def build(self) -> Component:
        """Build and return the component"""
        return self.component


# Factory functions for common components
def card(title: str = "", **kwargs) -> ComponentBuilder:
    """Create a card component"""
    return ComponentBuilder(CardComponent, title, **kwargs)

def form(action: str = "", method: str = "post", **kwargs) -> ComponentBuilder:
    """Create a form component"""
    return ComponentBuilder(FormComponent, action, method, **kwargs)

def div(content: str = "", **kwargs) -> ComponentBuilder:
    """Create a div component"""
    return ComponentBuilder(HTMLComponent, "div", content, **kwargs)

def span(content: str = "", **kwargs) -> ComponentBuilder:
    """Create a span component"""
    return ComponentBuilder(HTMLComponent, "span", content, **kwargs)

def list_view(items: List[Any] = None, **kwargs) -> ComponentBuilder:
    """Create a list component"""
    return ComponentBuilder(ListComponent, items, **kwargs)

def layout(layout_type: str = "default", **kwargs) -> ComponentBuilder:
    """Create a layout component"""
    return ComponentBuilder(LayoutComponent, layout_type, **kwargs)

def conditional(condition: Union[bool, Callable], **kwargs) -> ComponentBuilder:
    """Create a conditional component"""
    return ComponentBuilder(ConditionalComponent, condition, **kwargs)


class ComponentRegistry:
    """Registry for reusable components"""
    
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.templates: Dict[str, Callable] = {}
    
    def register(self, name: str, component: Component):
        """Register a component template"""
        self.components[name] = component
    
    def register_template(self, name: str, factory: Callable):
        """Register a component factory function"""
        self.templates[name] = factory
    
    def create(self, name: str, *args, **kwargs) -> Optional[Component]:
        """Create a component instance"""
        if name in self.templates:
            return self.templates[name](*args, **kwargs)
        elif name in self.components:
            # Return a copy of the registered component
            return self._clone_component(self.components[name])
        return None
    
    def _clone_component(self, component: Component) -> Component:
        """Clone a component (simplified implementation)"""
        # In a full implementation, this would do deep cloning
        cloned = component.__class__(component.name, component.props)
        cloned.state = component.state.copy()
        return cloned
    
    def list_components(self) -> List[str]:
        """List all registered components"""
        return list(self.components.keys()) + list(self.templates.keys())


# Global component registry
registry = ComponentRegistry()

# Register common component factories
registry.register_template('card', lambda title="", **kwargs: card(title, **kwargs).build())
registry.register_template('form', lambda action="", method="post", **kwargs: form(action, method, **kwargs).build())
registry.register_template('div', lambda content="", **kwargs: div(content, **kwargs).build())
registry.register_template('list', lambda items=None, **kwargs: list_view(items, **kwargs).build())
registry.register_template('layout', lambda layout_type="default", **kwargs: layout(layout_type, **kwargs).build())