#!/usr/bin/env python3
"""
Path Utilities for Client-Server Encrypted Backup Framework
Provides standardized path management and import path setup.

This module eliminates the 25+ scattered sys.path.insert() calls across the codebase
by providing a centralized, reliable way to handle Python import paths.
"""

import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    Get the project root directory reliably from any location in the codebase.

    Returns:
        Path object pointing to the project root directory
    """
    # Start from this file's location and search upward for project markers
    current_path = Path(__file__).resolve().parent

    # Look for project markers that indicate the root directory
    project_markers = [
        "CLAUDE.md",  # Project instructions file
        "requirements.txt",  # Python dependencies
        "build",  # C++ build directory
        "vcpkg",  # C++ package manager
        "Client",  # C++ client source
        "python_server",  # Python server directory
    ]

    # Search upward from current directory
    while current_path != current_path.parent:
        # Check if current directory has any project markers
        if any((current_path / marker).exists() for marker in project_markers):
            return current_path
        current_path = current_path.parent

    # Fallback: assume we're already in project root or nearby
    fallback = Path(__file__).resolve().parent.parent
    return fallback


def ensure_imports() -> None:
    """
    Ensure all critical import paths are available.
    Call this at the top of any module that needs framework imports.

    This replaces all scattered sys.path.insert() calls with a single standardized approach.
    """
    project_root = get_project_root()

    # Critical paths that need to be in sys.path for imports
    critical_paths = [
        project_root,  # Project root for Shared, etc.
        project_root / "python_server" / "server",  # Server modules
        project_root / "api_server",  # API server modules
        project_root / "Shared",  # Shared utilities
        project_root / "Database",  # Database modules
        project_root / "src" / "api",  # API implementation
        project_root / "Client" / "wrappers",  # C++ wrapper modules
    ]

    # Add paths to sys.path if not already present
    for path in critical_paths:
        path_str = str(path.resolve())
        if path.exists() and path_str not in sys.path:
            sys.path.insert(0, path_str)


def get_server_directory() -> Path:
    """Get the python_server/server directory path."""
    return get_project_root() / "python_server" / "server"


def get_api_directory() -> Path:
    """Get the api_server directory path."""
    return get_project_root() / "api_server"


def get_shared_directory() -> Path:
    """Get the Shared directory path."""
    return get_project_root() / "Shared"


def get_database_directory() -> Path:
    """Get the Database directory path."""
    return get_project_root() / "Database"


def get_received_files_directory() -> Path:
    """Get the received_files directory path."""
    return get_project_root() / "received_files"


def get_config_directory() -> Path:
    """Get the config directory path."""
    return get_project_root() / "config"


def validate_project_structure() -> list[str]:
    """
    Validate that the project structure is intact.

    Returns:
        List of validation errors (empty if all good)
    """
    errors: list[str] = []
    project_root = get_project_root()

    # Check for essential directories
    essential_dirs = ["python_server/server", "api_server", "Shared", "Client", "scripts"]

    for dir_path in essential_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            errors.append(f"Missing essential directory: {dir_path}")

    # Check for essential files
    essential_files = [
        "CLAUDE.md",
        "requirements.txt",
        "python_server/server/server.py",
        "api_server/cyberbackup_api_server.py",
    ]

    for file_path in essential_files:
        full_path = project_root / file_path
        if not full_path.exists():
            errors.append(f"Missing essential file: {file_path}")

    return errors


# Convenience function for quick setup at module import
def setup_imports():
    """
    Quick setup function to call at the top of any module.

    Usage:
        from Shared.path_utils import setup_imports
        setup_imports()

        # Now all imports work reliably
        from server import ServerManager
        from database import DatabaseManager
    """
    ensure_imports()


if __name__ == "__main__":
    # Test the path utilities
    print("Testing Path Utilities...")

    root = get_project_root()
    print(f"Project root: {root}")
    print(f"Project root exists: {root.exists()}")

    print(f"Server directory: {get_server_directory()}")
    print(f"API directory: {get_api_directory()}")
    print(f"Shared directory: {get_shared_directory()}")

    # Validate structure
    errors = validate_project_structure()
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Project structure validation passed!")

    # Test import setup
    print("Setting up imports...")
    ensure_imports()
    print(f"sys.path now has {len(sys.path)} entries")

    print("Path utilities test completed!")
