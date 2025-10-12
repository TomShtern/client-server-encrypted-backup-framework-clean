#!/usr/bin/env python3
"""
Configuration and Constants for FletV2.
"""

import os
from contextlib import suppress
from pathlib import Path
from typing import Any

# Load environment variables from .env file if it exists
with suppress(ImportError):
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()

# Debug mode - controls visibility of mock data and debug features
DEBUG_MODE = os.environ.get('FLET_V2_DEBUG', 'false').lower() == 'true'

# Secure secret handling from environment variables
GITHUB_PERSONAL_ACCESS_TOKEN = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
SERVER_API_KEY = os.environ.get('SERVER_API_KEY')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

# Real server configuration
REAL_SERVER_URL = os.environ.get('REAL_SERVER_URL')  # e.g., https://backup.example.com/api
BACKUP_SERVER_TOKEN = os.environ.get('BACKUP_SERVER_TOKEN') or os.environ.get('BACKUP_SERVER_API_KEY')
REQUEST_TIMEOUT = float(os.environ.get('REQUEST_TIMEOUT', '10'))
VERIFY_TLS = os.environ.get('VERIFY_TLS', 'true').lower() == 'true'

# Optional: Validate critical secrets in debug mode
if DEBUG_MODE:
    if not GITHUB_PERSONAL_ACCESS_TOKEN:
        print("Warning: GITHUB_PERSONAL_ACCESS_TOKEN not set")
    if not SERVER_API_KEY:
        print("Warning: SERVER_API_KEY not set")
    if not DATABASE_PASSWORD:
        print("Warning: DATABASE_PASSWORD not set")
    if not REAL_SERVER_URL:
        print("Info: REAL_SERVER_URL not set - running in mock mode unless a real server is injected")
    if REAL_SERVER_URL and not REAL_SERVER_URL.startswith(('https://', 'http://')):
        print("Warning: REAL_SERVER_URL should start with https:// or http://")
    if not BACKUP_SERVER_TOKEN:
        print("Info: BACKUP_SERVER_TOKEN not set - endpoints requiring auth will fail in real mode")

# Mock data visibility - when False, mock data is only used when server is unavailable
SHOW_MOCK_DATA = os.environ.get('FLET_V2_SHOW_MOCK_DATA', 'false').lower() == 'true'

# Async operation delays for simulation
ASYNC_DELAY = 0.5  # seconds

# Server connection timeout
SERVER_TIMEOUT = 5  # seconds

# File scan timeout
FILE_SCAN_TIMEOUT = 10  # seconds

# Pagination settings
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Refresh intervals
DEFAULT_REFRESH_INTERVAL = 5  # seconds
MIN_REFRESH_INTERVAL = 1  # seconds
MAX_REFRESH_INTERVAL = 300  # seconds (5 minutes)

# Validation settings
MIN_PORT = 1024
MAX_PORT = 65535
MIN_MAX_CLIENTS = 1
MAX_MAX_CLIENTS = 1000

# Paths
PROJECT_ROOT = Path(__file__).parent
RECEIVED_FILES_DIR = PROJECT_ROOT.parent / "received_files"

# Database Configuration - Points to BackupServer's database
# This ensures FletV2 GUI uses the same database as the production server
BACKUP_SERVER_ROOT = PROJECT_ROOT.parent / "python_server"
DATABASE_PATH = PROJECT_ROOT.parent / "defensive.db"  # Database is in project root, not python_server subdirectory
DATABASE_NAME = "defensive.db"  # For compatibility with BackupServer config
FILE_STORAGE_DIR = PROJECT_ROOT.parent / "received_files"  # Shared file storage

# Database connection settings (matching BackupServer defaults)
DATABASE_CONNECTION_POOL_ENABLED = True
DATABASE_CONNECTION_POOL_SIZE = 5
DATABASE_TIMEOUT = 10.0
DATABASE_MAX_CONNECTION_AGE = 3600.0  # 1 hour
DATABASE_CLEANUP_INTERVAL = 300.0     # 5 minutes

# Settings persistence path with proper directory structure
CONFIG_DIR = PROJECT_ROOT / "data"
CONFIG_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = CONFIG_DIR / "fletv2_settings.json"

# Status colors
STATUS_COLORS = {
    "Connected": "GREEN",
    "Registered": "ORANGE",
    "Offline": "RED",
    "Verified": "GREEN",
    "Pending": "ORANGE",
    "Received": "BLUE",
    "Unverified": "RED",
    "Active": "GREEN",
    "Inactive": "ORANGE",
    "Error": "RED",
    "Success": "GREEN",
    "Warning": "ORANGE",
    "Info": "BLUE"
}

# Log levels
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]

# File types
FILE_TYPES = {
    "docx": "WORD",
    "xlsx": "EXCEL",
    "pdf": "PDF",
    "jpg": "IMAGE",
    "png": "IMAGE",
    "txt": "TEXT",
    "py": "CODE",
    "zip": "ARCHIVE"
}

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return DEBUG_MODE

def show_mock_data() -> bool:
    """Check if mock data should be shown."""
    return SHOW_MOCK_DATA

def get_status_color(status: str) -> str:
    """Get color for status."""
    return STATUS_COLORS.get(status, "ON_SURFACE")

def get_database_path() -> Path:
    """Get the path to the BackupServer database."""
    return DATABASE_PATH

def get_database_name() -> str:
    """Get the database filename for compatibility."""
    return DATABASE_NAME

def get_file_storage_dir() -> Path:
    """Get the shared file storage directory."""
    return FILE_STORAGE_DIR

def is_database_available() -> bool:
    """Check if the BackupServer database file exists."""
    return DATABASE_PATH.exists()

def get_database_config() -> dict[str, Any]:
    """Get complete database configuration for ServerBridge."""
    return {
        'database_path': str(DATABASE_PATH),
        'database_name': DATABASE_NAME,
        'file_storage_dir': str(FILE_STORAGE_DIR),
        'connection_pool_enabled': DATABASE_CONNECTION_POOL_ENABLED,
        'connection_pool_size': DATABASE_CONNECTION_POOL_SIZE,
        'timeout': DATABASE_TIMEOUT,
        'max_connection_age': DATABASE_MAX_CONNECTION_AGE,
        'cleanup_interval': DATABASE_CLEANUP_INTERVAL
    }
