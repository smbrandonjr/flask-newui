# Flask-NewUI - Pip Distribution Runbook

This guide provides step-by-step instructions for publishing Flask-NewUI to PyPI.

## Prerequisites

### 1. Install Required Tools

```bash
# Install build tools
pip install --upgrade pip setuptools wheel twine build

# Install development dependencies
pip install -e .[dev]
```

### 2. Create PyPI Accounts

1. **Create accounts on both PyPI and TestPyPI:**
   - PyPI (production): https://pypi.org/account/register/
   - TestPyPI (testing): https://test.pypi.org/account/register/

2. **Enable 2FA** on both accounts for security

3. **Create API tokens:**
   - Go to Account Settings → API Tokens
   - Create tokens for both PyPI and TestPyPI
   - Store tokens securely (you'll need them for `.pypirc`)

### 3. Configure Authentication

Create `~/.pypirc` file:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

**Security Note:** Keep your tokens secure and never commit them to version control.

## Pre-Release Checklist

### 1. Code Quality Checks

```bash
# Run basic tests
python -m pytest tests/ -v

# Run tests with coverage (requires pytest-cov)
# pip install pytest-cov
# python -m pytest tests/ -v --cov=newui --cov-report=html

# Check code formatting (if using development tools)
# pip install black flake8
# black --check newui/
# flake8 newui/

# Note: The package includes a basic test suite that validates core functionality
# For development, install the dev dependencies: pip install flask-newui[dev]
```

### 2. Version Management

1. **Update version in key files:**
   - `newui/__init__.py` → `__version__ = "1.0.0"`
   - `setup.py` → `version="1.0.0"`
   - `pyproject.toml` → uses setuptools_scm (automatic)

2. **Update CHANGELOG.md** with new features and fixes

3. **Verify all examples work:**
   ```bash
   python examples/todo_app.py
   python examples/realtime_chat.py
   python examples/debug_tools.py
   ```

### 3. Documentation Review

- [ ] README.md is comprehensive and up-to-date
- [ ] All code examples work
- [ ] Links are valid
- [ ] Installation instructions are correct
- [ ] API documentation matches actual code

### 4. Package Structure Verification

```bash
# Verify package structure
find newui/ -name "*.py" | head -20
ls -la newui/static/
ls -la examples/
```

Expected structure:
```
newui/
├── __init__.py           # Main module with version
├── cli.py               # Command line interface
├── components.py        # Built-in components
├── composition.py       # Component composition
├── devtools.py          # Development tools
├── routing.py           # Route-based code splitting
├── stores.py            # State management
├── websocket.py         # WebSocket support
├── core/               # Core modules
│   ├── __init__.py
│   ├── ajax.py
│   ├── components.py
│   ├── renderer.py
│   └── state.py
└── static/             # Static assets
    ├── newui.js
    └── newui.css
```

## Build Process

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info/
find . -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

### 2. Build the Package

```bash
# Build both wheel and source distribution
python -m build

# Verify the build
ls -la dist/
```

You should see files like:
- `flask_newui-1.0.0-py3-none-any.whl`
- `flask-newui-1.0.0.tar.gz`

### 3. Verify Build Contents

```bash
# Check wheel contents
python -m zipfile -l dist/flask_newui-1.0.0-py3-none-any.whl

# Check source distribution
tar -tzf dist/flask-newui-1.0.0.tar.gz
```

## Testing on TestPyPI

### 1. Upload to TestPyPI

```bash
# Upload to test repository
python -m twine upload --repository testpypi dist/*
```

### 2. Test Installation from TestPyPI

```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ flask-newui

# Test basic functionality
python -c "from newui import NewUI; print('Import successful!')"
python -c "from newui import components; print('Components import successful!')"

# Test CLI
newui --version
newui info

# Cleanup
deactivate
rm -rf test_env/
```

### 3. Test with Example Project

Create a test Flask app:

```python
# test_install.py
from flask import Flask, render_template_string
from newui import NewUI
from newui import components as ui

app = Flask(__name__)
newui = NewUI(app)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test NewUI</title>
        <link href="{{ url_for('newui.static', filename='newui.css') }}" rel="stylesheet">
    </head>
    <body>
        <h1>NewUI Test</h1>
        {{ ui.button("Test Button", onclick="test") }}
        <script src="{{ url_for('newui.static', filename='newui.js') }}"></script>
        <script>
            NewUI.registerHandler('test', function() { alert('Works!'); });
        </script>
    </body>
    </html>
    ''', ui=ui)

if __name__ == '__main__':
    app.run(debug=True)
```

Run and verify it works:
```bash
python test_install.py
# Visit http://localhost:5000 and test
```

## Production Release

### 1. Final Checks

- [ ] All tests pass on TestPyPI installation
- [ ] Documentation is complete and accurate
- [ ] Version numbers are consistent
- [ ] CHANGELOG.md is updated
- [ ] No sensitive information in package

### 2. Create Git Tag

```bash
# Create and push git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 3. Upload to Production PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*
```

### 4. Verify Production Installation

```bash
# Test production installation
pip install flask-newui

# Verify
python -c "from newui import NewUI; print(f'NewUI v{NewUI.__version__} installed successfully!')"
```

## Post-Release

### 1. Update Documentation

- [ ] Update website (if applicable)
- [ ] Update GitHub repository description
- [ ] Create GitHub release with CHANGELOG
- [ ] Announce on relevant channels

### 2. Monitor Initial Adoption

- [ ] Check PyPI download statistics
- [ ] Monitor GitHub issues for problems
- [ ] Respond to community feedback

### 3. Plan Next Release

- [ ] Create development branch for next version
- [ ] Update version to next development version (e.g., "1.1.0-dev")
- [ ] Start planning next features

## Troubleshooting

### Common Issues

**1. Build Failures:**
```bash
# Check setup.py syntax
python setup.py check

# Validate package metadata
python -m twine check dist/*
```

**2. Upload Authentication Issues:**
```bash
# Re-configure authentication
twine configure

# Use explicit repository
twine upload --repository pypi dist/*
```

**3. Missing Dependencies:**
```bash
# Verify all dependencies are listed
pip-compile requirements.txt
```

**4. Static Files Not Included:**
```bash
# Check MANIFEST.in
python setup.py sdist
tar -tzf dist/flask-newui-*.tar.gz | grep static
```

### Emergency Procedures

**If you need to yank a release:**
```bash
# Yank specific version (keeps it installed but hides from new installs)
twine yank flask-newui 1.0.0 "Reason for yanking"
```

**If you need to delete a release entirely:**
- Contact PyPI administrators (only in extreme cases)
- Document the issue and resolution

## Security Considerations

1. **Never commit secrets:**
   - API tokens
   - Passwords
   - Private keys

2. **Review package contents:**
   ```bash
   # Check for sensitive files before upload
   tar -tzf dist/flask-newui-*.tar.gz | grep -E '\.(key|pem|env)$'
   ```

3. **Use secure development practices:**
   - Enable 2FA on PyPI
   - Use API tokens instead of passwords
   - Regularly rotate credentials

4. **Monitor for security issues:**
   - Set up GitHub security alerts
   - Monitor PyPI security advisories
   - Keep dependencies updated

## Automated Release (Future Enhancement)

Consider setting up GitHub Actions for automated releases:

```yaml
# .github/workflows/release.yml
name: Release to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@master
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Checklist Summary

**Pre-Release:**
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run all tests
- [ ] Verify examples work
- [ ] Review documentation

**Build & Test:**
- [ ] Clean build artifacts
- [ ] Build package
- [ ] Upload to TestPyPI
- [ ] Test installation from TestPyPI
- [ ] Verify functionality

**Release:**
- [ ] Create git tag
- [ ] Upload to production PyPI
- [ ] Test production installation
- [ ] Create GitHub release

**Post-Release:**
- [ ] Update documentation
- [ ] Monitor adoption
- [ ] Plan next release

---

**Ready to publish NewUI Framework to PyPI? Follow this runbook step by step!**