"""
Setup file for NewUI - A modern frontend framework for Flask/Jinja2
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flask-newui",
    version="1.0.0",
    author="NewUI Contributors",
    author_email="contact@flask-newui.dev",
    description="A modern reactive frontend framework that bridges Flask/Jinja2 with modern UI capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smbrandonjr/flask-newui",
    project_urls={
        "Bug Reports": "https://github.com/smbrandonjr/flask-newui/issues",
        "Documentation": "https://flask-newui.dev/docs",
        "Source": "https://github.com/smbrandonjr/flask-newui",
    },
    packages=find_packages(exclude=["examples", "docs", "tests"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
    ],
    keywords="flask jinja2 frontend framework reactive ui components",
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "websocket": [
            "Flask-SocketIO>=5.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-flask>=1.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
            "pre-commit>=2.0",
        ],
        "examples": [
            "Flask-SocketIO>=5.0.0",
        ],
        "all": [
            "Flask-SocketIO>=5.0.0",
            "pytest>=6.0",
            "pytest-flask>=1.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
            "pre-commit>=2.0",
        ],
    },
    include_package_data=True,
    package_data={
        "newui": [
            "static/*.js",
            "static/*.css",
        ],
    },
    entry_points={
        "console_scripts": [
            "newui=newui.cli:main",
        ],
    },
    zip_safe=False,
)