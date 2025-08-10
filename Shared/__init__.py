"""
Shared module for the Client-Server Encrypted Backup Framework.

This module contains shared utilities, configuration management,
logging utilities, observability features, and other common functionality
used across the client and server components.
"""

# Make commonly used modules easily accessible
from . import config
from . import logging_utils
from . import observability
from . import crc
from . import filename_validator

__all__ = [
    'config',
    'logging_utils', 
    'observability',
    'crc',
    'filename_validator'
]