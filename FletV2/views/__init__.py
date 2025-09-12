#!/usr/bin/env python3
"""
Views Package Init
Initialization file for views package.
"""
# Import all view modules to make them available when importing the views package
from . import analytics
from . import clients
from . import dashboard
from . import database
from . import files
from . import logs
from . import settings

# Define what should be imported with "from views import *"
__all__ = [
    "analytics",
    "clients", 
    "dashboard",
    "database",
    "files",
    "logs",
    "settings"
]