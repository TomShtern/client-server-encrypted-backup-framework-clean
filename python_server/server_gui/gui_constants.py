# -*- coding: utf-8 -*-
"""
gui_constants.py - Centralized constants for the GUI's design system.

This module acts as a "single source of truth" for all visual styling,
including colors, fonts, dimensions, and custom style names. This approach
promotes a consistent, professional aesthetic and makes future theming or
rebranding efforts trivial.
"""

from typing import Dict, Tuple

class Fonts:
    """Defines the typographic scale for the application."""
    UI_FONT = "Segoe UI"
    CODE_FONT = "Consolas"
    
    # --- Semantic Font Sizes ---
    Display = (UI_FONT, 18, "bold")
    Headline = (UI_FONT, 16, "bold")
    Title = (UI_FONT, 12, "bold")
    BODY = (UI_FONT, 10)
    BODY_BOLD = (UI_FONT, 10, "bold")
    SMALL = (UI_FONT, 9, "italic")
    CODE = (CODE_FONT, 10)

class Dimensions:
    """Defines standard sizes and padding for UI elements."""
    PADDING_SM = 5
    PADDING_MD = 10
    PADDING_LG = 20
    
    CORNER_RADIUS = 8
    
    SCROLLBAR_WIDTH = 10

class CustomStyles:
    """Defines custom ttkstyle names used throughout the application."""
    
    # --- Custom Style Names ---
    # These names are used in code, e.g., style='Pill.TEntry'
    PILL_ENTRY = "Pill.TEntry"
    STATUS_CARD_FRAME = "StatusCard.TFrame"
    NAV_BUTTON = "Nav.TButton"
    NAV_BUTTON_ACTIVE = "NavActive.TButton"

class Icons:
    """Maps conceptual icon names to their asset file names."""
    # This abstraction allows us to change the icon set without changing UI code.
    MAP: Dict[str, str] = {
        # Navigation
        "DASHBOARD": "house-door-fill",
        "CLIENTS": "people-fill",
        "FILES": "file-earmark-zip-fill",
        "ANALYTICS": "graph-up-arrow",
        "DATABASE": "database-fill",
        "LOGS": "file-text-fill",
        "SETTINGS": "gear-fill",
        
        # Actions
        "START": "play-circle-fill",
        "STOP": "stop-circle-fill",
        "RESTART": "arrow-clockwise",
        "SAVE": "check-circle-fill",
        "REFRESH": "arrow-clockwise",
        "DISCONNECT": "power",
        "COPY": "clipboard",
        "BROWSE": "folder2-open",
        "SEARCH": "search",
        
        # Indicators & Placeholders
        "SERVER_STATUS": "power",
        "UPTIME": "clock-history",
        "DATA_RATE": "arrow-repeat",
        "INFO": "info-circle",
        "PLACEHOLDER_CLIENT": "person-badge",
        "PLACEHOLDER_FILE": "file-earmark-text",
        "PLACEHOLDER_TABLE": "table",
        "PLACEHOLDER_CHART": "graph-up-arrow",
        "VERIFIED": "check-circle-fill",
        "NOT_VERIFIED": "x-circle-fill",
    }    C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\kivy_venv_new\Scripts\activate.bat