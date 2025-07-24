"""
Tests for NewUI components
"""
import pytest
from flask import Flask
from newui import NewUI
from newui import components as ui


class TestBuiltinComponents:
    """Test built-in UI components"""
    
    def test_components_import(self):
        """Test that components can be imported"""
        from newui import components
        assert components is not None
    
    def test_button_component(self):
        """Test button component generation"""
        button_html = ui.button("Test Button")
        assert isinstance(button_html, str)
        assert "Test Button" in button_html
        assert "button" in button_html.lower()
    
    def test_button_with_onclick(self):
        """Test button with onclick handler"""
        button_html = ui.button("Click Me", onclick="testHandler")
        assert "testHandler" in button_html
        assert "data-ui-click" in button_html
    
    def test_input_component(self):
        """Test input component generation"""
        input_html = ui.input("test_input")
        assert isinstance(input_html, str)
        assert "input" in input_html.lower()
        assert 'name="test_input"' in input_html
    
    def test_input_with_type(self):
        """Test input with different types"""
        email_input = ui.input("email", type="email")
        assert 'type="email"' in email_input
        
        password_input = ui.input("password", type="password")
        assert 'type="password"' in password_input
    
    def test_form_component(self):
        """Test form component generation"""
        form_html = ui.form("Form content")
        assert isinstance(form_html, str)
        assert "form" in form_html.lower()
        assert "Form content" in form_html
    
    def test_card_component(self):
        """Test card component generation"""
        card_html = ui.card("Card content", title="Test Card")
        assert isinstance(card_html, str)
        assert "Card content" in card_html
        assert "Test Card" in card_html
    
    def test_alert_component(self):
        """Test alert component generation"""
        alert_html = ui.alert("Test message", type="success")
        assert isinstance(alert_html, str)
        assert "Test message" in alert_html
        assert "success" in alert_html.lower()
    
    def test_select_component(self):
        """Test select component generation"""
        options = [("value1", "Label 1"), ("value2", "Label 2")]
        select_html = ui.select("test_select", options=options)
        assert isinstance(select_html, str)
        assert "select" in select_html.lower()
        assert "value1" in select_html
        assert "Label 1" in select_html


class TestComponentParameters:
    """Test component parameter handling"""
    
    def test_button_with_all_params(self):
        """Test button with all parameters"""
        button_html = ui.button(
            text="Complete Button",
            onclick="handler",
            type="submit",
            variant="primary",
            disabled=True,
            class_="custom-class"
        )
        assert "Complete Button" in button_html
        assert "handler" in button_html
        assert 'type="submit"' in button_html
        assert "primary" in button_html
        assert "disabled" in button_html
        assert "custom-class" in button_html
    
    def test_input_with_all_params(self):
        """Test input with all parameters"""
        input_html = ui.input(
            name="complete_input",
            type="text",
            value="default_value",
            placeholder="Enter text...",
            required=True,
            class_="form-control"
        )
        assert 'name="complete_input"' in input_html
        assert 'type="text"' in input_html
        assert 'value="default_value"' in input_html
        assert 'placeholder="Enter text..."' in input_html
        assert "required" in input_html
        assert "form-control" in input_html
    
    def test_component_class_parameter(self):
        """Test that components accept class parameters"""
        button_html = ui.button("Test", class_="custom-class")
        assert "custom-class" in button_html


@pytest.fixture
def app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def newui_app(app):
    """Create a Flask app with NewUI initialized"""
    newui = NewUI(app)
    return app, newui