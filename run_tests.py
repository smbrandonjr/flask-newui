#!/usr/bin/env python
"""
Simple test runner for Flask-NewUI
Runs tests with or without coverage depending on what's installed
"""
import subprocess
import sys

def main():
    """Run tests with appropriate configuration"""
    # Basic pytest command
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    # Try to import pytest-cov to see if coverage is available
    try:
        import pytest_cov
        print("pytest-cov found, running with coverage...")
        cmd.extend(["--cov=newui", "--cov-report=html", "--cov-report=term"])
    except ImportError:
        print("Running tests without coverage (install pytest-cov for coverage reports)")
    
    # Run the tests
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())