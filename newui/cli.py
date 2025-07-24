"""
NewUI CLI - Command line interface for NewUI framework
"""

import argparse
import sys
from typing import List, Optional


def create_project(name: str, template: Optional[str] = None) -> None:
    """Create a new NewUI project"""
    print(f"Creating new NewUI project: {name}")
    # TODO: Implement project scaffolding
    print("Project creation not yet implemented. Please refer to documentation for manual setup.")


def version() -> str:
    """Get NewUI version"""
    try:
        from importlib.metadata import version as get_version
        return get_version("flask-newui")
    except Exception:
        # Fallback when package not found
        try:
            # Try pkg_resources fallback for Python < 3.8
            import pkg_resources
            return pkg_resources.get_distribution("flask-newui").version
        except Exception:
            # Final fallback when package not installed (e.g., during development/testing)
            from newui import __version__
            return __version__


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="newui",
        description="NewUI Framework - A modern frontend framework for Flask/Jinja2"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"NewUI {version()}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new NewUI project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument(
        "--template", "-t",
        help="Project template (basic, full, websocket)",
        choices=["basic", "full", "websocket"],
        default="basic"
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show NewUI information")
    
    args = parser.parse_args(argv)
    
    if args.command == "create":
        create_project(args.name, args.template)
    elif args.command == "info":
        print(f"NewUI Framework v{version()}")
        print("A modern reactive frontend framework for Flask/Jinja2")
        print("\nDocumentation: https://flask-newui.dev/docs")
        print("GitHub: https://github.com/smbrandonjr/flask-newui")
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())