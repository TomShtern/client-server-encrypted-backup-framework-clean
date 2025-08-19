# -*- coding: utf-8 -*-
"""
custom_theme.py - Material Design 3 theme configuration for Encrypted Backup Server
Implements dynamic theming with Material You color system
"""

from kivymd.theming import ThemeManager
from typing import Dict, Any


class CustomTheme:
    """Custom Material Design 3 theme settings"""
    
    # Material Design 3 Color Schemes
    THEMES = {
        "Blue": {
            "primary": "#1976D2",
            "on_primary": "#FFFFFF",
            "primary_container": "#D1E4FF",
            "on_primary_container": "#001D36",
            "secondary": "#535F70",
            "on_secondary": "#FFFFFF",
            "secondary_container": "#D7E3F7",
            "on_secondary_container": "#101C2B",
            "tertiary": "#6B5778",
            "on_tertiary": "#FFFFFF",
            "tertiary_container": "#F2DAFF",
            "on_tertiary_container": "#251432",
            "error": "#BA1A1A",
            "on_error": "#FFFFFF",
            "error_container": "#FFDAD6",
            "on_error_container": "#410002",
            "surface": "#0F1419",
            "on_surface": "#E1E2E8",
            "surface_variant": "#42474E",
            "on_surface_variant": "#C2C7CF",
            "outline": "#8C9199",
            "outline_variant": "#42474E",
            "background": "#0F1419",
            "on_background": "#E1E2E8"
        },
        "Green": {
            "primary": "#2E7D32",
            "on_primary": "#FFFFFF",
            "primary_container": "#A8F5A8",
            "on_primary_container": "#002106",
            "secondary": "#52634F",
            "on_secondary": "#FFFFFF",
            "secondary_container": "#D4E8CF",
            "on_secondary_container": "#101F0F",
            "tertiary": "#39656B",
            "on_tertiary": "#FFFFFF",
            "tertiary_container": "#BCEAF2",
            "on_tertiary_container": "#001F23",
            "error": "#BA1A1A",
            "on_error": "#FFFFFF",
            "error_container": "#FFDAD6",
            "on_error_container": "#410002",
            "surface": "#0F1512",
            "on_surface": "#E0E3DD",
            "surface_variant": "#414941",
            "on_surface_variant": "#C1C9BE",
            "outline": "#8B9389",
            "outline_variant": "#414941",
            "background": "#0F1512",
            "on_background": "#E0E3DD"
        },
        "Purple": {
            "primary": "#6A1B9A",
            "on_primary": "#FFFFFF",
            "primary_container": "#EADDFF",
            "on_primary_container": "#21005D",
            "secondary": "#625B71",
            "on_secondary": "#FFFFFF",
            "secondary_container": "#E8DEF8",
            "on_secondary_container": "#1D192B",
            "tertiary": "#7D5260",
            "on_tertiary": "#FFFFFF",
            "tertiary_container": "#FFD8E4",
            "on_tertiary_container": "#31111D",
            "error": "#BA1A1A",
            "on_error": "#FFFFFF",
            "error_container": "#FFDAD6",
            "on_error_container": "#410002",
            "surface": "#141218",
            "on_surface": "#E6E0E9",
            "surface_variant": "#49454F",
            "on_surface_variant": "#CAC4D0",
            "outline": "#938F99",
            "outline_variant": "#49454F",
            "background": "#141218",
            "on_background": "#E6E0E9"
        }
    }
    
    # Server-specific status colors
    STATUS_COLORS = {
        "online": "#4CAF50",
        "offline": "#F44336",
        "warning": "#FF9800",
        "processing": "#2196F3",
        "success": "#8BC34A",
        "error": "#E91E63"
    }
    
    # Typography scale (Material Design 3)
    TYPOGRAPHY = {
        "display_large": {"size": 57, "line_height": 64, "weight": "regular"},
        "display_medium": {"size": 45, "line_height": 52, "weight": "regular"},
        "display_small": {"size": 36, "line_height": 44, "weight": "regular"},
        "headline_large": {"size": 32, "line_height": 40, "weight": "regular"},
        "headline_medium": {"size": 28, "line_height": 36, "weight": "regular"},
        "headline_small": {"size": 24, "line_height": 32, "weight": "regular"},
        "title_large": {"size": 22, "line_height": 28, "weight": "medium"},
        "title_medium": {"size": 16, "line_height": 24, "weight": "medium"},
        "title_small": {"size": 14, "line_height": 20, "weight": "medium"},
        "body_large": {"size": 16, "line_height": 24, "weight": "regular"},
        "body_medium": {"size": 14, "line_height": 20, "weight": "regular"},
        "body_small": {"size": 12, "line_height": 16, "weight": "regular"},
        "label_large": {"size": 14, "line_height": 20, "weight": "medium"},
        "label_medium": {"size": 12, "line_height": 16, "weight": "medium"},
        "label_small": {"size": 11, "line_height": 16, "weight": "medium"}
    }
    
    # Component styling constants
    CARD_ELEVATION = 1
    CARD_RADIUS = 12
    BUTTON_RADIUS = 20
    FAB_RADIUS = 16
    DIALOG_RADIUS = 28
    
    # Animation durations (in seconds)
    ANIMATIONS = {
        "short": 0.15,
        "medium": 0.25,
        "long": 0.35,
        "extra_long": 0.5
    }
    
    @classmethod
    def apply_theme(cls, theme_manager: ThemeManager, theme_name: str = "Blue", style: str = "Dark"):
        """
        Apply custom theme to the KivyMD app
        
        Args:
            theme_manager: KivyMD ThemeManager instance
            theme_name: Color scheme name (Blue, Green, Purple)
            style: Theme style (Dark, Light)
        """
        # Set basic theme properties
        theme_manager.theme_style = style
        theme_manager.primary_palette = theme_name
        theme_manager.material_style = "M3"
        
        # Apply custom colors if available
        if theme_name in cls.THEMES:
            colors = cls.THEMES[theme_name]
            # Note: In KivyMD 2.0.0, custom color setting may require different approach
            # This is a placeholder for color customization
            try:
                # Custom color application (API may vary)
                for color_key, color_value in colors.items():
                    if hasattr(theme_manager, color_key):
                        setattr(theme_manager, color_key, color_value)
            except Exception as e:
                print(f"[WARNING] Could not apply custom colors: {e}")
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Get color for server status indicators"""
        return cls.STATUS_COLORS.get(status.lower(), cls.STATUS_COLORS["offline"])
    
    @classmethod
    def get_theme_config(cls, theme_name: str = "Blue") -> Dict[str, Any]:
        """Get complete theme configuration"""
        return {
            "colors": cls.THEMES.get(theme_name, cls.THEMES["Blue"]),
            "status_colors": cls.STATUS_COLORS,
            "typography": cls.TYPOGRAPHY,
            "component_styles": {
                "card_elevation": cls.CARD_ELEVATION,
                "card_radius": cls.CARD_RADIUS,
                "button_radius": cls.BUTTON_RADIUS,
                "fab_radius": cls.FAB_RADIUS,
                "dialog_radius": cls.DIALOG_RADIUS
            },
            "animations": cls.ANIMATIONS
        }


class ThemeConfig:
    """Theme configuration management utility"""
    
    def __init__(self, config_data: Dict[str, Any]):
        self.config = config_data
        self.current_theme = config_data.get("app", {}).get("primary_color", "Blue")
        self.current_style = config_data.get("app", {}).get("theme", "Dark")
    
    def apply_to_app(self, theme_manager: ThemeManager):
        """Apply configuration to KivyMD app"""
        CustomTheme.apply_theme(
            theme_manager,
            self.current_theme,
            self.current_style
        )
    
    def get_server_colors(self) -> Dict[str, str]:
        """Get colors for server status indicators"""
        return CustomTheme.STATUS_COLORS
    
    def get_chart_colors(self) -> Dict[str, str]:
        """Get colors for chart elements"""
        chart_config = self.config.get("charts", {})
        return chart_config.get("colors", {
            "cpu": "#1976D2",
            "memory": "#7C4DFF",
            "network": "#00897B"
        })
    
    def update_theme(self, theme_name: str, style: str = None):
        """Update current theme settings"""
        self.current_theme = theme_name
        if style:
            self.current_style = style
        
        # Update config
        if "app" not in self.config:
            self.config["app"] = {}
        self.config["app"]["primary_color"] = theme_name
        if style:
            self.config["app"]["theme"] = style