# -*- coding: utf-8 -*-
"""
custom_theme.py - Material Design 3 Expressive theme configuration for Encrypted Backup Server
Implements dynamic theming with Material You color system and adaptive personalization
"""

from kivymd.theming import ThemeManager
from typing import Dict, Any, Optional, Tuple
import random
import math


class CustomTheme:
    """Material Design 3 Expressive theme settings with dynamic color generation"""
    
    # Material Design 3 Expressive Style Constants
    EXPRESSIVE_STYLES = {
        "baseline": {
            "corner_radius": 4,
            "emphasis_scale": 1.0,
            "motion_curve": "standard"
        },
        "expressive": {
            "corner_radius": 28,
            "emphasis_scale": 1.2,
            "motion_curve": "emphasized"
        }
    }
    
    # Dynamic Color Harmonies for Expressive Theming
    COLOR_HARMONIES = {
        "monochromatic": {"hue_shift": 0, "saturation_variance": 0.1},
        "analogous": {"hue_shift": 30, "saturation_variance": 0.15},
        "complementary": {"hue_shift": 180, "saturation_variance": 0.2},
        "triadic": {"hue_shift": 120, "saturation_variance": 0.25},
        "split_complementary": {"hue_shift": 150, "saturation_variance": 0.2}
    }
    
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
    def _rgb_to_hsl(cls, r: float, g: float, b: float) -> Tuple[float, float, float]:
        """Convert RGB to HSL color space"""
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Lightness
        l = (max_val + min_val) / 2
        
        if diff == 0:
            h = s = 0  # achromatic
        else:
            # Saturation
            s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)
            
            # Hue
            if max_val == r:
                h = (g - b) / diff + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            h /= 6
        
        return h * 360, s, l
    
    @classmethod
    def _hsl_to_hex(cls, h: float, s: float, l: float) -> str:
        """Convert HSL to hex color"""
        def hue_to_rgb(p: float, q: float, t: float) -> float:
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        h = h / 360  # Convert to 0-1 range
        
        if s == 0:
            r = g = b = l  # achromatic
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}".upper()
    
    @classmethod
    def _get_timestamp(cls) -> str:
        """Get current timestamp for theme generation tracking"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @classmethod
    def generate_expressive_theme_from_seed(cls, seed_color: str, harmony: str = "analogous", style: str = "expressive") -> Dict[str, Any]:
        """Generate a dynamic Material Design 3 Expressive theme from a seed color"""
        try:
            # Convert hex to HSL for better color manipulation
            r, g, b = int(seed_color[1:3], 16), int(seed_color[3:5], 16), int(seed_color[5:7], 16)
            h, s, l = cls._rgb_to_hsl(r/255, g/255, b/255)
            
            # Get harmony configuration
            harmony_config = cls.COLOR_HARMONIES.get(harmony, cls.COLOR_HARMONIES["analogous"])
            hue_shift = harmony_config["hue_shift"]
            sat_variance = harmony_config["saturation_variance"]
            
            # Generate harmonious color palette
            primary_hue = h
            secondary_hue = (h + hue_shift) % 360
            tertiary_hue = (h + hue_shift * 0.67) % 360
            
            # Create adaptive saturation and lightness values
            base_saturation = max(0.3, min(0.9, s + random.uniform(-sat_variance, sat_variance)))
            
            # Generate expressive theme with enhanced contrast and vibrancy
            expressive_theme = {
                "primary": cls._hsl_to_hex(primary_hue, base_saturation, 0.5),
                "on_primary": "#FFFFFF" if l < 0.5 else "#000000",
                "primary_container": cls._hsl_to_hex(primary_hue, base_saturation * 0.4, 0.85),
                "on_primary_container": cls._hsl_to_hex(primary_hue, base_saturation * 0.8, 0.15),
                
                "secondary": cls._hsl_to_hex(secondary_hue, base_saturation * 0.7, 0.45),
                "on_secondary": "#FFFFFF",
                "secondary_container": cls._hsl_to_hex(secondary_hue, base_saturation * 0.3, 0.8),
                "on_secondary_container": cls._hsl_to_hex(secondary_hue, base_saturation * 0.8, 0.2),
                
                "tertiary": cls._hsl_to_hex(tertiary_hue, base_saturation * 0.6, 0.4),
                "on_tertiary": "#FFFFFF",
                "tertiary_container": cls._hsl_to_hex(tertiary_hue, base_saturation * 0.25, 0.75),
                "on_tertiary_container": cls._hsl_to_hex(tertiary_hue, base_saturation * 0.7, 0.25),
                
                "error": "#BA1A1A",
                "on_error": "#FFFFFF",
                "error_container": "#FFDAD6",
                "on_error_container": "#410002",
                
                "surface": "#0F1419" if style == "Dark" else "#FEFBFF",
                "on_surface": "#E1E2E8" if style == "Dark" else "#1C1B1F",
                "surface_variant": cls._hsl_to_hex(primary_hue, 0.1, 0.25 if style == "Dark" else 0.9),
                "on_surface_variant": cls._hsl_to_hex(primary_hue, 0.15, 0.75 if style == "Dark" else 0.3),
                
                "outline": cls._hsl_to_hex(primary_hue, 0.1, 0.55),
                "outline_variant": cls._hsl_to_hex(primary_hue, 0.08, 0.35 if style == "Dark" else 0.8),
                "background": "#0F1419" if style == "Dark" else "#FEFBFF",
                "on_background": "#E1E2E8" if style == "Dark" else "#1C1B1F",
                
                # Expressive-specific enhancements
                "_expressive_style": style,
                "_harmony_type": harmony,
                "_seed_color": seed_color,
                "_generation_timestamp": cls._get_timestamp()
            }
            
            return expressive_theme
            
        except Exception as e:
            print(f"[WARNING] Failed to generate expressive theme: {e}")
            return cls.THEMES["Blue"]  # Fallback to default
    
    @classmethod
    def apply_theme(cls, theme_manager: ThemeManager, theme_name: str = "Blue", style: str = "Dark", expressive_config: Optional[Dict[str, Any]] = None):
        """
        Apply Material Design 3 Expressive theme to the KivyMD app
        
        Args:
            theme_manager: KivyMD ThemeManager instance
            theme_name: Color scheme name (Blue, Green, Purple) or dynamic theme
            style: Theme style (Dark, Light)
            expressive_config: Optional expressive theming configuration
                - enable_dynamic: bool - Enable dynamic theme generation
                - seed_color: str - Hex color for dynamic generation
                - harmony: str - Color harmony type
                - expressive_style: str - baseline/expressive styling
        """
        try:
            # Check if we should generate a dynamic expressive theme
            if expressive_config and expressive_config.get("enable_dynamic", False):
                seed_color = expressive_config.get("seed_color", "#1976D2")
                harmony = expressive_config.get("harmony", "analogous")
                expressive_style = expressive_config.get("expressive_style", "expressive")
                
                # Generate dynamic theme
                theme_data = cls.generate_expressive_theme_from_seed(seed_color, harmony, expressive_style)
                print(f"[INFO] Applied dynamic MD3 Expressive theme with {harmony} harmony")
            else:
                # Use predefined theme
                theme_data = cls.THEMES.get(theme_name, cls.THEMES["Blue"])
                print(f"[INFO] Applied predefined MD3 theme: {theme_name}")
            
            # Set basic theme properties
            theme_manager.theme_style = style
            theme_manager.primary_palette = theme_name if not expressive_config else "Blue"
            
            # Set Material Design 3 Expressive style
            theme_manager.material_style = "M3"
            
            # Apply expressive design tokens if available
            if expressive_config:
                expressive_style = expressive_config.get("expressive_style", "baseline")
                style_config = cls.EXPRESSIVE_STYLES.get(expressive_style, cls.EXPRESSIVE_STYLES["baseline"])
                
                # Apply expressive styling (these would be used by components)
                theme_manager._expressive_corner_radius = style_config["corner_radius"]
                theme_manager._expressive_emphasis_scale = style_config["emphasis_scale"]
                theme_manager._expressive_motion_curve = style_config["motion_curve"]
                
                print(f"[INFO] Applied MD3 Expressive style: {expressive_style}")
            
            # Apply custom colors if available
            if expressive_config and expressive_config.get("enable_dynamic", False):
                # For dynamic themes, apply the generated theme data
                try:
                    for color_key, color_value in theme_data.items():
                        if not color_key.startswith('_') and hasattr(theme_manager, color_key):
                            setattr(theme_manager, color_key, color_value)
                except Exception as e:
                    print(f"[WARNING] Could not apply dynamic colors: {e}")
            else:
                # Apply predefined custom colors if available
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
                
        except Exception as e:
            print(f"[ERROR] Failed to apply theme: {e}")
            # Fallback to basic theme application
            theme_manager.theme_style = style
            theme_manager.primary_palette = "Blue"
            theme_manager.material_style = "M3"
    
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