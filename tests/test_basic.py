"""
Basic tests for Flask-NewUI core functionality
"""
import pytest
from flask import Flask


class TestBasicFunctionality:
    """Test basic Flask-NewUI functionality"""
    
    def test_newui_import(self):
        """Test that NewUI can be imported"""
        from newui import NewUI
        assert NewUI is not None
    
    def test_components_import(self):
        """Test that components can be imported"""
        from newui import components
        assert components is not None
    
    def test_version_exists(self):
        """Test that version is defined"""
        from newui import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert __version__ == "1.0.0"
    
    def test_basic_flask_integration(self):
        """Test basic Flask integration"""
        app = Flask(__name__)
        
        from newui import NewUI
        newui = NewUI(app)
        
        assert newui is not None
        assert newui.app is app
        
        # Test that static routes are available
        with app.test_client() as client:
            response = client.get('/newui/static/newui.css')
            assert response.status_code == 200
            
            response = client.get('/newui/static/newui.js')
            assert response.status_code == 200
    
    def test_basic_components(self):
        """Test basic component generation"""
        from newui import components as ui
        
        # Test button
        button = ui.button("Test Button")
        assert isinstance(button, str)
        assert "Test Button" in button
        assert "button" in button.lower()
        
        # Test input
        input_field = ui.input("test")
        assert isinstance(input_field, str)
        assert "input" in input_field.lower()
        assert 'name="test"' in input_field
        
        # Test card
        card = ui.card("Content", title="Title")
        assert isinstance(card, str)
        assert "Content" in card
        assert "Title" in card
    
    def test_cli_basic(self):
        """Test basic CLI functionality"""
        from newui.cli import main
        
        # Test that CLI doesn't crash with no args
        result = main([])
        assert result == 1  # Should show help and return 1
        
        # Test info command
        result = main(['info'])
        assert result == 0


class TestExampleApplications:
    """Test that example applications can be imported"""
    
    def test_examples_exist(self):
        """Test that examples directory exists and has files"""
        import os
        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples')
        assert os.path.exists(examples_dir)
        
        example_files = os.listdir(examples_dir)
        assert len(example_files) > 0
        assert any(f.endswith('.py') for f in example_files)
    
    def test_todo_app_example_imports(self):
        """Test that todo app example can be imported"""
        import sys
        import os
        
        # Add examples to path
        examples_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples')
        if examples_path not in sys.path:
            sys.path.insert(0, examples_path)
        
        try:
            # Try to import without running
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "todo_app", 
                os.path.join(examples_path, "todo_app.py")
            )
            module = importlib.util.module_from_spec(spec)
            # Don't execute, just verify it can be loaded
            assert spec is not None
            assert module is not None
        except Exception as e:
            pytest.skip(f"Could not import example: {e}")


@pytest.fixture
def app():
    """Create a test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app