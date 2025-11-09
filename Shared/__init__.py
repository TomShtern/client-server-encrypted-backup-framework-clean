"""
Shared module for the Client-Server Encrypted Backup Framework.

This module contains shared utilities, configuration management,
logging utilities, observability features, and other common functionality
used across the client and server components.
"""

import os
import sys

# Enable global UTF-8 support automatically (replaces all manual UTF-8 setup)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import Shared.utils.utf8_solution

# Make commonly used modules easily accessible
from . import config, crc, filename_validator, logging_utils, observability

__all__ = ["config", "crc", "filename_validator", "logging_utils", "observability"]
