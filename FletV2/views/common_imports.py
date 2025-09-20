#!/usr/bin/env python3
"""
Common Imports Module for FletV2 Views
Eliminates import duplication across view files.

Only includes imports that appear in 3+ view files for focused, maintainable design.
Following the Flet Simplicity Principle: Don't over-engineer.
"""

# Core Flet framework
import flet as ft

# Standard library imports (appear in 3+ view files)
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import asyncio
import aiofiles

# FletV2 utility imports (appear in all 7 view files)
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button
from utils.user_feedback import show_success_message, show_error_message

# Convenience logger setup
logger = get_logger(__name__)