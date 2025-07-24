"""
Tests for NewUI core functionality
"""
import pytest
from flask import Flask
from newui import NewUI


class TestNewUICore:
    """Test NewUI core functionality"""
    
    def test_newui_import(self):
        """Test that NewUI can be imported"""
        from newui import NewUI
        assert NewUI is not None
    
    def test_newui_initialization(self):
        """Test NewUI initialization with Flask app"""
        app = Flask(__name__)
        newui = NewUI(app)
        assert newui is not None
        assert newui.app is app
    
    def test_newui_init_app(self):
        """Test NewUI init_app pattern"""
        app = Flask(__name__)
        newui = NewUI()
        newui.init_app(app)
        assert newui.app is app
    
    def test_newui_version(self):
        """Test that version is defined"""
        from newui import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0


class TestNewUIFlaskIntegration:
    """Test Flask integration"""
    
    def test_blueprint_registration(self):
        """Test that NewUI blueprint is registered"""
        app = Flask(__name__)
        newui = NewUI(app)
        
        # Check that newui blueprint is registered
        assert 'newui' in app.blueprints
    
    def test_static_route_available(self):
        """Test that static routes are available"""
        app = Flask(__name__)
        newui = NewUI(app)
        
        with app.test_client() as client:
            # Test CSS file
            response = client.get('/newui/static/newui.css')
            assert response.status_code == 200
            assert 'text/css' in response.content_type
            
            # Test JS file
            response = client.get('/newui/static/newui.js')
            assert response.status_code == 200
            assert 'javascript' in response.content_type or 'text/plain' in response.content_type


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


@pytest.fixture
def client(newui_app):
    """Create a test client"""
    app, _ = newui_app
    return app.test_client()