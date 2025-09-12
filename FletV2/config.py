#!/usr/bin/env python3
"""
Configuration and Constants for FletV2.
"""

import os
from pathlib import Path
from contextlib import suppress

# Load environment variables from .env file if it exists
with suppress(ImportError):
    from dotenv import load_dotenv
    load_dotenv()

# Debug mode - controls visibility of mock data and debug features
DEBUG_MODE = os.environ.get('FLET_V2_DEBUG', 'false').lower() == 'true'

# Secure secret handling from environment variables
GITHUB_PERSONAL_ACCESS_TOKEN = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
SERVER_API_KEY = os.environ.get('SERVER_API_KEY')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

# Optional: Validate critical secrets in debug mode
if DEBUG_MODE:
    if not GITHUB_PERSONAL_ACCESS_TOKEN:
        print("Warning: GITHUB_PERSONAL_ACCESS_TOKEN not set")
    if not SERVER_API_KEY:
        print("Warning: SERVER_API_KEY not set")
    if not DATABASE_PASSWORD:
        print("Warning: DATABASE_PASSWORD not set")

# Mock data visibility - when False, mock data is only used when server is unavailable
SHOW_MOCK_DATA = DEBUG_MODE

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
SETTINGS_FILE = "flet_server_gui_settings.json"

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

def is_debug_mode():
    """Check if debug mode is enabled."""
    return DEBUG_MODE

def show_mock_data():
    """Check if mock data should be shown."""
    return SHOW_MOCK_DATA

def get_status_color(status):
    """Get color for status."""
    return STATUS_COLORS.get(status, "ON_SURFACE")