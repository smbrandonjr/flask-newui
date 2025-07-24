"""
Pytest configuration and shared fixtures for Flask-NewUI tests
"""
import pytest
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask for testing
try:
    from flask import Flask
except ImportError:
    pytest.skip("Flask not available", allow_module_level=True)

# Import NewUI
try:
    from newui import NewUI
except ImportError:
    pytest.skip("NewUI not available", allow_module_level=True)


@pytest.fixture(scope="session")
def app_config():
    """Configuration for test Flask app"""
    return {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
    }


@pytest.fixture
def app(app_config):
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config.update(app_config)
    
    # Create application context
    with app.app_context():
        yield app


@pytest.fixture
def newui_app(app):
    """Create a Flask app with NewUI initialized"""
    newui = NewUI(app)
    return app, newui


@pytest.fixture
def client(newui_app):
    """Create a test client"""
    app, _ = newui_app
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


# Add markers for different test categories
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "websocket: WebSocket related tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Mark WebSocket tests
        if "websocket" in item.nodeid:
            item.add_marker(pytest.mark.websocket)
        
        # Mark integration tests
        if "test_integration" in item.nodeid or "integration" in item.name:
            item.add_marker(pytest.mark.integration)
        else:
            # Default to unit tests
            item.add_marker(pytest.mark.unit)