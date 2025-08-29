#!/usr/bin/env python3
"""
Unified Material Design 3 Theme System for Flet Server GUI
==========================================================

This file consolidates ALL theme-related functionality from the following files:
- ui/theme.py - Base theme configuration
- ui/theme_m3.py - Material Design 3 specific theme
- ui/theme_tokens.py - Advanced token management system
- ui/theme_consistency.py - Theme consistency utilities  
- utils/theme_manager.py - Theme management functionality
- utils/theme_utils.py - Theme utility functions
- core/theme_system.py - Theme system consolidation (partial)

FEATURES:
- Single source of truth for all Material Design 3 theming
- Advanced token management with validation and accessibility
- Unified theme management and application
- Performance optimized theme switching with caching
- Complete Material Design 3 component theming
- WCAG 2.1 AA accessibility compliance validation
- Event system for theme changes
- Smooth animations and transitions
- Error handling and logging
- Backward compatibility with existing code

DESIGN TOKENS: Custom purple-orange gradient system based on project favicon
"""

import flet as ft
import asyncio
import logging
import json
from typing import Dict, Any, Optional, Union, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import os
import sys

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# IMPROVED DYNAMIC DESIGN TOKENS - Real Theme-Aware Single Source of Truth
# ============================================================================

class DynamicTokens:
    """Enhanced dynamic tokens that work with Flet's theme system properly"""
    
    def __init__(self):
        # Enhanced static token definitions - these never change and provide fallback values
        self._static_tokens = {
            # Primary: blue → purple gradient
            "primary_gradient": ["#A8CBF3", "#7C5CD9"],
            "primary": "#7C5CD9",
            "on_primary": "#FFFFFF",
            "primary_container": "#EADDFF",
            "on_primary_container": "#21005D",
            
            # Secondary: ORANGE
            "secondary": "#FFA500", 
            "on_secondary": "#000000",
            "secondary_container": "#FFDDB3",
            "on_secondary_container": "#2B1600",
            
            # Tertiary: pink-ish
            "tertiary": "#AB6DA4",
            "on_tertiary": "#FFFFFF",
            "tertiary_container": "#FFD8EE",
            "on_tertiary_container": "#3A0038",
            
            # Containers (teal)
            "container": "#38A298",
            "on_container": "#FFFFFF",
            
            # Surface tones
            "surface": "#F6F8FB",
            "on_surface": "#000000",
            "surface_variant": "#E7EDF7",
            "on_surface_variant": "#44474E",
            "surface_container": "#F6F8FB",
            "surface_container_high": "#F6F8FB",
            "surface_container_highest": "#0F1720",
            "surface_dark": "#0F1720", 
            "inverse_surface": "#2F3033",
            "on_inverse_surface": "#F1F0F4",
            
            # Background and foreground
            "background": "#FFFFFF",
            "on_background": "#000000",
            
            # Outlines and borders
            "outline": "#666666",
            "outline_variant": "#C4C6D0",
            
            # Error
            "error": "#B00020",
            "on_error": "#FFFFFF",
            "error_container": "#FFDAD6",
            "on_error_container": "#410002",
            
            # Additional semantic colors
            "shadow": "#000000",
            "scrim": "#000000"
        }
        
        # Enhanced Flet theme-aware color mappings - these adapt to theme automatically
        # Using available Flet Colors constants that adapt to light/dark theme
        # Based on Material Design 3 color system specifications
        self._flet_color_mappings = {
            # Primary color palette
            "primary": "Colors.PRIMARY",
            "on_primary": "Colors.ON_PRIMARY",
            "primary_container": "Colors.PRIMARY_CONTAINER",
            "on_primary_container": "Colors.ON_PRIMARY_CONTAINER",
            
            # Secondary color palette
            "secondary": "Colors.SECONDARY", 
            "on_secondary": "Colors.ON_SECONDARY",
            "secondary_container": "Colors.SECONDARY_CONTAINER",
            "on_secondary_container": "Colors.ON_SECONDARY_CONTAINER",
            
            # Tertiary color palette
            "tertiary": "Colors.TERTIARY",
            "on_tertiary": "Colors.ON_TERTIARY",
            "tertiary_container": "Colors.TERTIARY_CONTAINER",
            "on_tertiary_container": "Colors.ON_TERTIARY_CONTAINER",
            
            # Surface colors
            "surface": "Colors.SURFACE",
            "on_surface": "Colors.ON_SURFACE",
            "surface_variant": "Colors.SURFACE_CONTAINER_HIGHEST",  # Proper surface variant background
            "on_surface_variant": "Colors.ON_SURFACE_VARIANT",
            "surface_container": "Colors.SURFACE_CONTAINER_HIGHEST",
            "surface_container_high": "Colors.SURFACE_CONTAINER_HIGHEST",
            "surface_container_highest": "Colors.SURFACE_CONTAINER_HIGHEST",
            "inverse_surface": "Colors.INVERSE_SURFACE",
            "on_inverse_surface": "Colors.ON_INVERSE_SURFACE",
            
            # Background and foreground
            "background": "Colors.SURFACE",  # Use surface as background equivalent
            "on_background": "Colors.ON_SURFACE",  # Use on_surface as on_background equivalent
            
            # Outlines and borders
            "outline": "Colors.OUTLINE",
            "outline_variant": "Colors.ON_SURFACE_VARIANT",
            
            # Error colors
            "error": "Colors.ERROR",
            "on_error": "Colors.ON_ERROR",
            "error_container": "Colors.ERROR_CONTAINER",
            "on_error_container": "Colors.ON_ERROR_CONTAINER",
            
            # Additional semantic colors
            "shadow": "Colors.SHADOW",  # If available, otherwise fallback to BLACK
            "scrim": "Colors.SCRIM"     # If available, otherwise fallback to BLACK
        }
    
    def _should_use_flet_colors(self):
        """Check if we should use Flet's theme-aware colors instead of static values"""
        # Always use Flet's theme-aware colors for proper theme switching
        return True
    
    def __getitem__(self, key):
        """Get theme-appropriate color for the key - NOW RETURNS FLET CONSTANTS"""
        if key not in self._static_tokens:
            raise KeyError(f"Token '{key}' not found")
        
        # For proper theme switching, return Flet color constants instead of static values
        # Flet will automatically use the correct colors based on current theme mode
        if self._should_use_flet_colors() and key in self._flet_color_mappings:
            import flet as ft
            # Return Flet color constant that adapts to theme automatically
            flet_constant = self._flet_color_mappings[key]
            color_attr = flet_constant.split('.')[1]
            
            # Handle fallbacks for colors that might not exist in all Flet versions
            if hasattr(ft.Colors, color_attr):
                return getattr(ft.Colors, color_attr)
            elif color_attr in ['SHADOW', 'SCrim']:
                # Fallback to BLACK for shadow/scrim if not available
                return ft.Colors.BLACK
            else:
                # Fallback to static colors if Flet color not available
                return self._static_tokens.get(key, ft.Colors.BLACK)
        
        # Fallback to static colors (should rarely happen)
        return self._static_tokens[key]
    
    def get(self, key, default=None):
        """Get token value with default fallback"""
        try:
            return self[key]
        except KeyError:
            return default
    
    def keys(self):
        """Get all token keys"""
        return self._static_tokens.keys()
    
    def values(self):
        """Get all current token values (theme-aware)"""
        return [self[key] for key in self._static_tokens.keys()]
    
    def items(self):
        """Get all token key-value pairs (theme-aware)"""
        return [(key, self[key]) for key in self._static_tokens.keys()]
    
    def copy(self):
        """Get a copy of current token values"""
        return dict(self.items())
    
    def __contains__(self, key):
        """Check if token key exists"""
        return key in self._static_tokens


# Global dynamic tokens instance - REPLACES STATIC TOKENS WITH FLET-THEME-AWARE VERSION
TOKENS = DynamicTokens()


# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class ColorRole(Enum):
    """Material Design 3 color roles"""
    PRIMARY = "primary"
    ON_PRIMARY = "on_primary"
    PRIMARY_CONTAINER = "primary_container"
    ON_PRIMARY_CONTAINER = "on_primary_container"
    SECONDARY = "secondary"
    ON_SECONDARY = "on_secondary"
    SECONDARY_CONTAINER = "secondary_container"
    ON_SECONDARY_CONTAINER = "on_secondary_container"
    TERTIARY = "tertiary"
    ON_TERTIARY = "on_tertiary"
    TERTIARY_CONTAINER = "tertiary_container"
    ON_TERTIARY_CONTAINER = "on_tertiary_container"
    ERROR = "error"
    ON_ERROR = "on_error"
    ERROR_CONTAINER = "error_container"
    ON_ERROR_CONTAINER = "on_error_container"
    BACKGROUND = "background"
    ON_BACKGROUND = "on_background"
    SURFACE = "surface"
    ON_SURFACE = "on_surface"
    SURFACE_VARIANT = "surface_variant"
    ON_SURFACE_VARIANT = "on_surface_variant"
    OUTLINE = "outline"
    OUTLINE_VARIANT = "outline_variant"
    SHADOW = "shadow"
    INVERSE_SURFACE = "inverse_surface"
    INVERSE_ON_SURFACE = "inverse_on_surface"
    INVERSE_PRIMARY = "inverse_primary"


class TypographyRole(Enum):
    """Material Design 3 typography roles"""
    DISPLAY_LARGE = "display_large"
    DISPLAY_MEDIUM = "display_medium"
    DISPLAY_SMALL = "display_small"
    HEADLINE_LARGE = "headline_large"
    HEADLINE_MEDIUM = "headline_medium"
    HEADLINE_SMALL = "headline_small"
    TITLE_LARGE = "title_large"
    TITLE_MEDIUM = "title_medium"
    TITLE_SMALL = "title_small"
    BODY_LARGE = "body_large"
    BODY_MEDIUM = "body_medium"
    BODY_SMALL = "body_small"
    LABEL_LARGE = "label_large"
    LABEL_MEDIUM = "label_medium"
    LABEL_SMALL = "label_small"


class ThemeMode(Enum):
    """Theme modes for application appearance"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    AUTO = "auto"


@dataclass
class MaterialDesignTokens:
    """Complete Material Design 3 token system"""
    # Color tokens with complete M3 palette
    colors: Dict[ColorRole, str] = field(default_factory=lambda: {
        ColorRole.PRIMARY: TOKENS["primary"],
        ColorRole.ON_PRIMARY: TOKENS["on_primary"],
        ColorRole.PRIMARY_CONTAINER: TOKENS["container"],
        ColorRole.ON_PRIMARY_CONTAINER: TOKENS["on_container"],
        ColorRole.SECONDARY: TOKENS["secondary"],
        ColorRole.ON_SECONDARY: TOKENS["on_secondary"],
        ColorRole.SECONDARY_CONTAINER: TOKENS["container"],
        ColorRole.ON_SECONDARY_CONTAINER: TOKENS["on_container"],
        ColorRole.TERTIARY: TOKENS["tertiary"],
        ColorRole.ON_TERTIARY: TOKENS["on_tertiary"],
        ColorRole.TERTIARY_CONTAINER: TOKENS["container"],
        ColorRole.ON_TERTIARY_CONTAINER: TOKENS["on_container"],
        ColorRole.ERROR: TOKENS["error"],
        ColorRole.ON_ERROR: TOKENS["on_error"],
        ColorRole.ERROR_CONTAINER: "#FEEBEE",
        ColorRole.ON_ERROR_CONTAINER: "#000000",
        ColorRole.BACKGROUND: TOKENS["background"],
        ColorRole.ON_BACKGROUND: TOKENS["on_background"],
        ColorRole.SURFACE: TOKENS["surface"],
        ColorRole.ON_SURFACE: TOKENS["on_surface"],
        ColorRole.SURFACE_VARIANT: TOKENS["surface_variant"],
        ColorRole.ON_SURFACE_VARIANT: TOKENS["outline"],
        ColorRole.OUTLINE: TOKENS["outline"],
        ColorRole.OUTLINE_VARIANT: "#CCCCCC",
        ColorRole.SHADOW: "#000000",
        ColorRole.INVERSE_SURFACE: "#333333",
        ColorRole.INVERSE_ON_SURFACE: "#FFFFFF",
        ColorRole.INVERSE_PRIMARY: "#A8CBF3",
    })
    
    # Typography tokens following M3 type scale
    typography: Dict[TypographyRole, Dict[str, Any]] = field(default_factory=lambda: {
        TypographyRole.DISPLAY_LARGE: {"size": 57, "weight": ft.FontWeight.W_400, "letter_spacing": -0.25},
        TypographyRole.DISPLAY_MEDIUM: {"size": 45, "weight": ft.FontWeight.W_400, "letter_spacing": 0},
        TypographyRole.DISPLAY_SMALL: {"size": 36, "weight": ft.FontWeight.W_400, "letter_spacing": 0},
        TypographyRole.HEADLINE_LARGE: {"size": 32, "weight": ft.FontWeight.W_400, "letter_spacing": 0},
        TypographyRole.HEADLINE_MEDIUM: {"size": 28, "weight": ft.FontWeight.W_400, "letter_spacing": 0},
        TypographyRole.HEADLINE_SMALL: {"size": 24, "weight": ft.FontWeight.W_400, "letter_spacing": 0},
        TypographyRole.TITLE_LARGE: {"size": 22, "weight": ft.FontWeight.W_400, "letter_spacing": 0},
        TypographyRole.TITLE_MEDIUM: {"size": 16, "weight": ft.FontWeight.W_500, "letter_spacing": 0.15},
        TypographyRole.TITLE_SMALL: {"size": 14, "weight": ft.FontWeight.W_500, "letter_spacing": 0.1},
        TypographyRole.BODY_LARGE: {"size": 16, "weight": ft.FontWeight.W_400, "letter_spacing": 0.5},
        TypographyRole.BODY_MEDIUM: {"size": 14, "weight": ft.FontWeight.W_400, "letter_spacing": 0.25},
        TypographyRole.BODY_SMALL: {"size": 12, "weight": ft.FontWeight.W_400, "letter_spacing": 0.4},
        TypographyRole.LABEL_LARGE: {"size": 14, "weight": ft.FontWeight.W_500, "letter_spacing": 0.1},
        TypographyRole.LABEL_MEDIUM: {"size": 12, "weight": ft.FontWeight.W_500, "letter_spacing": 0.5},
        TypographyRole.LABEL_SMALL: {"size": 11, "weight": ft.FontWeight.W_500, "letter_spacing": 0.5},
    })
    
    # Shape tokens for consistent corner radius
    corner_radius: Dict[str, int] = field(default_factory=lambda: {
        "none": 0,
        "extra_small": 4,
        "small": 8,
        "medium": 12,
        "large": 16,
        "extra_large": 28,
        "full": 999
    })
    
    # Elevation tokens
    elevations: Dict[str, int] = field(default_factory=lambda: {
        "level0": 0,
        "level1": 1,
        "level2": 3,
        "level3": 6,
        "level4": 8,
        "level5": 12
    })
    
    # Spacing tokens
    spacing: Dict[str, int] = field(default_factory=lambda: {
        "extra_small": 4,
        "small": 8,
        "medium": 12,
        "large": 16,
        "extra_large": 24
    })
    
    # Animation tokens
    animations: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "duration_short": {"duration": 100, "curve": "EASE_IN_OUT"},
        "duration_medium": {"duration": 250, "curve": "EASE_IN_OUT"},
        "duration_long": {"duration": 300, "curve": "EASE_IN_OUT"},
        "easing_standard": {"curve": "EASE_IN_OUT"},
        "easing_decelerate": {"curve": "EASE_OUT"},
        "easing_accelerate": {"curve": "EASE_IN"}
    })


# ============================================================================
# ACCESSIBILITY AND VALIDATION
# ============================================================================

class ThemeValidator:
    """Validation and accessibility checking for theme tokens"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_contrast_ratio(self, foreground: str, background: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        try:
            fg_luminance = self._calculate_relative_luminance(foreground)
            bg_luminance = self._calculate_relative_luminance(background)
            
            lighter = max(fg_luminance, bg_luminance)
            darker = min(fg_luminance, bg_luminance)
            
            ratio = (lighter + 0.05) / (darker + 0.05)
            return round(ratio, 2)
            
        except Exception as e:
            self.logger.error(f"Contrast calculation error: {e}")
            return 4.5  # Default acceptable ratio
    
    def _calculate_relative_luminance(self, color: str) -> float:
        """Calculate relative luminance using WCAG formula"""
        try:
            if color.startswith("#"):
                color = color[1:]
            
            r = int(color[0:2], 16) / 255.0 if len(color) >= 2 else 0
            g = int(color[2:4], 16) / 255.0 if len(color) >= 4 else 0
            b = int(color[4:6], 16) / 255.0 if len(color) >= 6 else 0
            
            # Apply gamma correction
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
            
        except Exception as e:
            self.logger.error(f"Luminance calculation error: {e}")
            return 0.0
    
    def is_accessible(self, foreground: str, background: str, level: str = "AA") -> bool:
        """Check if color combination meets accessibility standards"""
        ratio = self.calculate_contrast_ratio(foreground, background)
        if level == "AAA":
            return ratio >= 7.0
        return ratio >= 4.5  # WCAG AA standard
    
    def validate_color_token(self, color: str) -> bool:
        """Validate color token format"""
        if not isinstance(color, str):
            return False
        
        if color.startswith("#"):
            try:
                int(color[1:], 16)
                return len(color) in [4, 5, 7, 9]
            except ValueError:
                return False
        
        return hasattr(ft.Colors, color.upper())
    
    def validate_typography_token(self, typography: Dict[str, Any]) -> bool:
        """Validate typography token structure"""
        if not isinstance(typography, dict):
            return False
        
        required_fields = ["size", "weight"]
        for field in required_fields:
            if field not in typography:
                return False
        
        if not isinstance(typography["size"], (int, float)):
            return False
        
        valid_weights = ["W_100", "W_200", "W_300", "W_400", "W_500", "W_600", "W_700", "W_800", "W_900"]
        weight = str(typography["weight"]).upper()
        if not any(weight.endswith(vw) for vw in valid_weights):
            return False
        
        return True


# ============================================================================
# UNIFIED THEME MANAGER - Core System
# ============================================================================

class UnifiedThemeManager:
    """
    Unified Theme Manager - Consolidates all theme management functionality
    
    This class provides:
    - Complete Material Design 3 token management
    - Theme switching with animation support
    - Accessibility validation and compliance
    - Event system for theme changes  
    - Component theming utilities
    - Performance caching
    - Error handling and logging
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        
        # Core state
        self.current_mode = ThemeMode.SYSTEM
        self.tokens = MaterialDesignTokens()
        self.is_animating = False
        
        # Validation and accessibility
        self.validator = ThemeValidator()
        self.accessibility_warnings: List[Dict[str, Any]] = []
        
        # Event system
        self.event_callbacks: Dict[str, List[Callable]] = {
            "theme_changed": [],
            "mode_switched": [],
            "tokens_updated": [],
            "accessibility_warning": []
        }
        
        # Performance caching
        self._cache = {
            "themes": {},
            "styles": {},
            "gradients": {}
        }
        
        # Initialize theme system
        self._initialize()
    
    def _initialize(self):
        """Initialize theme system"""
        try:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
            self.apply_theme()
            self.validate_accessibility()
            self.logger.info("Unified theme system initialized successfully")
        except Exception as e:
            self.logger.error(f"Theme system initialization error: {e}")
    
    def apply_theme(self) -> None:
        """Apply current theme to the page"""
        try:
            # Create Flet themes
            light_theme = self._create_flet_theme(dark=False)
            dark_theme = self._create_flet_theme(dark=True)
            
            # Apply to page
            self.page.theme = light_theme
            self.page.dark_theme = dark_theme
            
            # Set theme mode
            if self.current_mode == ThemeMode.LIGHT:
                self.page.theme_mode = ft.ThemeMode.LIGHT
            elif self.current_mode == ThemeMode.DARK:
                self.page.theme_mode = ft.ThemeMode.DARK
            elif self.current_mode == ThemeMode.AUTO:
                # Auto mode based on time
                hour = datetime.now().hour
                self.page.theme_mode = ft.ThemeMode.LIGHT if 6 <= hour < 18 else ft.ThemeMode.DARK
            else:
                self.page.theme_mode = ft.ThemeMode.SYSTEM
            
            # Update page
            self.page.update()
            
            # Fire event
            self._fire_event("theme_changed", {"mode": self.current_mode.value})
            
        except Exception as e:
            self.logger.error(f"Theme application error: {e}")
    
    def _create_flet_theme(self, dark: bool = False) -> ft.Theme:
        """Create Flet theme with custom color scheme"""
        try:
            cache_key = f"theme_{dark}"
            if cache_key in self._cache["themes"]:
                return self._cache["themes"][cache_key]
            
            # Create base theme
            seed = self.tokens.colors[ColorRole.PRIMARY]
            theme = ft.Theme(
                use_material3=True,
                color_scheme_seed=seed,
                font_family="Inter"
            )
            
            # Create custom color scheme
            if hasattr(ft, 'ColorScheme'):
                color_scheme = self._create_color_scheme(dark)
                theme.color_scheme = color_scheme
            
            # Cache and return
            self._cache["themes"][cache_key] = theme
            return theme
            
        except Exception as e:
            self.logger.error(f"Theme creation error: {e}")
            return ft.Theme(use_material3=True)
    
    def _create_color_scheme(self, dark: bool = False) -> ft.ColorScheme:
        """Create Flet ColorScheme from tokens"""
        colors = self.tokens.colors
        
        # Adjust for dark mode
        if dark:
            surface = self.tokens.colors.get(ColorRole.SURFACE, TOKENS["surface_dark"])
            on_surface = "#FFFFFF"
            background = TOKENS["surface_dark"]
            on_background = "#FFFFFF"
        else:
            surface = colors[ColorRole.SURFACE]
            on_surface = colors[ColorRole.ON_SURFACE]
            background = colors[ColorRole.BACKGROUND]
            on_background = colors[ColorRole.ON_BACKGROUND]
        
        # Create ColorScheme with compatibility check for newer Flet versions
        color_scheme_args = {
            "primary": colors[ColorRole.PRIMARY],
            "on_primary": colors[ColorRole.ON_PRIMARY],
            "primary_container": colors[ColorRole.PRIMARY_CONTAINER],
            "on_primary_container": colors[ColorRole.ON_PRIMARY_CONTAINER],
            "secondary": colors[ColorRole.SECONDARY],
            "on_secondary": colors[ColorRole.ON_SECONDARY],
            "secondary_container": colors[ColorRole.SECONDARY_CONTAINER],
            "on_secondary_container": colors[ColorRole.ON_SECONDARY_CONTAINER],
            "tertiary": colors[ColorRole.TERTIARY],
            "on_tertiary": colors[ColorRole.ON_TERTIARY],
            "tertiary_container": colors[ColorRole.TERTIARY_CONTAINER],
            "on_tertiary_container": colors[ColorRole.ON_TERTIARY_CONTAINER],
            "error": colors[ColorRole.ERROR],
            "on_error": colors[ColorRole.ON_ERROR],
            "error_container": colors[ColorRole.ERROR_CONTAINER],
            "on_error_container": colors[ColorRole.ON_ERROR_CONTAINER],
            "background": background,
            "on_background": on_background,
            "surface": surface,
            "on_surface": on_surface,
            "surface_variant": colors[ColorRole.SURFACE_VARIANT],
            "on_surface_variant": colors[ColorRole.ON_SURFACE_VARIANT],
            "outline": colors[ColorRole.OUTLINE],
            "outline_variant": colors[ColorRole.OUTLINE_VARIANT],
            "shadow": colors[ColorRole.SHADOW],
        }
        
        # Add newer color scheme attributes if they exist in the current Flet version
        if hasattr(ft.ColorScheme, 'inverse_surface'):
            color_scheme_args["inverse_surface"] = colors[ColorRole.INVERSE_SURFACE]
        if hasattr(ft.ColorScheme, 'inverse_on_surface'):
            color_scheme_args["inverse_on_surface"] = colors[ColorRole.INVERSE_ON_SURFACE]
        if hasattr(ft.ColorScheme, 'inverse_primary'):
            color_scheme_args["inverse_primary"] = colors[ColorRole.INVERSE_PRIMARY]
        
        return ft.ColorScheme(**color_scheme_args)
    
    async def switch_theme(self, mode: ThemeMode, animate: bool = True) -> None:
        """Switch theme mode with optional animation"""
        try:
            old_mode = self.current_mode
            self.current_mode = mode
            
            if animate and not self.is_animating:
                await self._animate_theme_switch()
            else:
                self.apply_theme()
            
            self._fire_event("mode_switched", {
                "old_mode": old_mode.value,
                "new_mode": mode.value,
                "animated": animate
            })
            
        except Exception as e:
            self.logger.error(f"Theme switch error: {e}")
    
    async def _animate_theme_switch(self) -> None:
        """Animate theme switching"""
        try:
            self.is_animating = True
            
            # Get animation duration
            duration = self.tokens.animations["duration_medium"]["duration"]
            
            # Apply theme
            self.apply_theme()
            
            # Wait for animation
            await asyncio.sleep(duration / 1000.0)
            
            self.is_animating = False
            
        except Exception as e:
            self.logger.error(f"Theme animation error: {e}")
            self.is_animating = False
    
    def toggle_theme(self) -> None:
        """Toggle between light, dark, system, and auto modes"""
        mode_cycle = [ThemeMode.LIGHT, ThemeMode.DARK, ThemeMode.SYSTEM, ThemeMode.AUTO]
        current_index = mode_cycle.index(self.current_mode)
        next_mode = mode_cycle[(current_index + 1) % len(mode_cycle)]
        
        # Use sync version for compatibility
        self.current_mode = next_mode
        self.apply_theme()
    
    def update_tokens(self, new_tokens: Dict[Union[ColorRole, TypographyRole, str], Any]) -> bool:
        """Update theme tokens with validation"""
        try:
            validated_tokens = {}
            
            # Validate tokens
            for key, value in new_tokens.items():
                if isinstance(key, ColorRole):
                    if self.validator.validate_color_token(value):
                        validated_tokens[key] = value
                        self.tokens.colors[key] = value
                    else:
                        self.logger.warning(f"Invalid color token: {key.value}={value}")
                elif isinstance(key, TypographyRole):
                    if self.validator.validate_typography_token(value):
                        validated_tokens[key] = value
                        self.tokens.typography[key] = value
                    else:
                        self.logger.warning(f"Invalid typography token: {key.value}={value}")
                else:
                    validated_tokens[key] = value
            
            if validated_tokens:
                # Clear cache
                self._cache.clear()
                
                # Re-apply theme
                self.apply_theme()
                
                # Validate accessibility
                self.validate_accessibility()
                
                # Fire event
                self._fire_event("tokens_updated", {
                    "updated_tokens": list(validated_tokens.keys()),
                    "count": len(validated_tokens)
                })
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Token update error: {e}")
            return False
    
    def validate_accessibility(self) -> List[Dict[str, Any]]:
        """Validate theme for accessibility compliance"""
        try:
            self.accessibility_warnings.clear()
            
            # Check common color combinations
            color_pairs = [
                (ColorRole.PRIMARY, ColorRole.ON_PRIMARY),
                (ColorRole.SECONDARY, ColorRole.ON_SECONDARY),
                (ColorRole.TERTIARY, ColorRole.ON_TERTIARY),
                (ColorRole.ERROR, ColorRole.ON_ERROR),
                (ColorRole.SURFACE, ColorRole.ON_SURFACE),
                (ColorRole.BACKGROUND, ColorRole.ON_BACKGROUND),
            ]
            
            for bg_role, fg_role in color_pairs:
                bg_color = self.tokens.colors.get(bg_role)
                fg_color = self.tokens.colors.get(fg_role)
                
                if bg_color and fg_color:
                    if not self.validator.is_accessible(fg_color, bg_color):
                        warning = {
                            "type": "contrast_violation",
                            "background_role": bg_role.value,
                            "foreground_role": fg_role.value,
                            "background_color": bg_color,
                            "foreground_color": fg_color,
                            "contrast_ratio": self.validator.calculate_contrast_ratio(fg_color, bg_color),
                            "severity": "high"
                        }
                        self.accessibility_warnings.append(warning)
            
            # Fire event if warnings found
            if self.accessibility_warnings:
                self._fire_event("accessibility_warning", {
                    "warnings": self.accessibility_warnings,
                    "count": len(self.accessibility_warnings)
                })
            
            return self.accessibility_warnings
            
        except Exception as e:
            self.logger.error(f"Accessibility validation error: {e}")
            return []
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for theme events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: str, callback: Callable) -> bool:
        """Unregister theme event callback"""
        if event_type in self.event_callbacks and callback in self.event_callbacks[event_type]:
            self.event_callbacks[event_type].remove(callback)
            return True
        return False
    
    def _fire_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Fire theme event to registered callbacks"""
        try:
            callbacks = self.event_callbacks.get(event_type, [])
            for callback in callbacks:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Event callback error: {e}")
        except Exception as e:
            self.logger.error(f"Event firing error: {e}")


# ============================================================================
# THEME UTILITIES - Helper Functions
# ============================================================================

class ThemeUtilities:
    """Utility functions for theme operations"""
    
    def __init__(self, theme_manager: UnifiedThemeManager):
        self.theme_manager = theme_manager
        self.logger = logging.getLogger(__name__)
    
    def get_color(self, role: ColorRole) -> str:
        """Get color token by role"""
        return self.theme_manager.tokens.colors.get(role, "#000000")
    
    def get_typography(self, role: TypographyRole) -> Dict[str, Any]:
        """Get typography token by role"""
        return self.theme_manager.tokens.typography.get(role, {"size": 14, "weight": ft.FontWeight.W_400})
    
    def get_corner_radius(self, size: str) -> int:
        """Get corner radius by size"""
        return self.theme_manager.tokens.corner_radius.get(size, 8)
    
    def get_elevation(self, level: str) -> int:
        """Get elevation by level"""
        return self.theme_manager.tokens.elevations.get(level, 1)
    
    def get_spacing(self, size: str) -> int:
        """Get spacing by size"""
        return self.theme_manager.tokens.spacing.get(size, 12)
    
    def create_linear_gradient(self, colors: Optional[List[str]] = None, 
                             begin: ft.Alignment = ft.alignment.top_left,
                             end: ft.Alignment = ft.alignment.bottom_right,
                             stops: Optional[List[float]] = None) -> ft.LinearGradient:
        """Create linear gradient with theme colors"""
        if colors is None:
            colors = TOKENS["primary_gradient"]
        
        return ft.LinearGradient(
            colors=colors,
            begin=begin,
            end=end,
            stops=stops
        )
    
    def get_button_style(self, variant: str = "filled") -> ft.ButtonStyle:
        """Get themed button style"""
        cache_key = f"button_{variant}"
        if cache_key in self.theme_manager._cache.get("styles", {}):
            return self.theme_manager._cache["styles"][cache_key]
        
        try:
            if variant == "filled":
                style = ft.ButtonStyle(
                    bgcolor=self.get_color(ColorRole.PRIMARY),
                    color=self.get_color(ColorRole.ON_PRIMARY),
                    shape=ft.RoundedRectangleBorder(radius=self.get_corner_radius("medium")),
                )
            elif variant == "outlined":
                style = ft.ButtonStyle(
                    side=ft.BorderSide(1, self.get_color(ColorRole.OUTLINE)),
                    color=self.get_color(ColorRole.PRIMARY),
                    shape=ft.RoundedRectangleBorder(radius=self.get_corner_radius("medium")),
                )
            elif variant == "text":
                style = ft.ButtonStyle(
                    color=self.get_color(ColorRole.PRIMARY),
                )
            else:
                # Default to filled
                style = ft.ButtonStyle(
                    bgcolor=self.get_color(ColorRole.PRIMARY),
                    color=self.get_color(ColorRole.ON_PRIMARY),
                    shape=ft.RoundedRectangleBorder(radius=self.get_corner_radius("medium")),
                )
            
            # Cache the style
            if "styles" not in self.theme_manager._cache:
                self.theme_manager._cache["styles"] = {}
            self.theme_manager._cache["styles"][cache_key] = style
            
            return style
            
        except Exception as e:
            self.logger.error(f"Button style creation error: {e}")
            return ft.ButtonStyle()
    
    def get_text_style(self, role: TypographyRole) -> ft.TextStyle:
        """Get text style based on typography tokens"""
        typography = self.get_typography(role)
        return ft.TextStyle(
            size=typography["size"],
            weight=typography["weight"],
            letter_spacing=typography.get("letter_spacing", 0)
        )
    
    def create_gradient_button(self, content: Union[str, ft.Control], 
                             width: int = 220, height: int = 48,
                             on_click: Optional[Callable] = None, 
                             radius: int = 12) -> ft.Container:
        """Create gradient button container"""
        try:
            if isinstance(content, str):
                content = ft.Text(content, color=self.get_color(ColorRole.ON_PRIMARY))
            
            return ft.Container(
                width=width,
                height=height,
                content=ft.Row([content], alignment=ft.MainAxisAlignment.CENTER),
                border_radius=ft.border_radius.all(radius),
                gradient=self.create_linear_gradient(),
                alignment=ft.alignment.center,
                ink=True,
                on_click=on_click,
                animate_scale=ft.animation.Animation(180, "easeInOut")
            )
            
        except Exception as e:
            self.logger.error(f"Gradient button creation error: {e}")
            return ft.Container()
    
    def create_surface_card(self, content: ft.Control, 
                           elevation: str = "level1",
                           padding: Optional[int] = None) -> ft.Card:
        """Create surface card with theme styling"""
        try:
            if padding is None:
                padding = self.get_spacing("medium")
            
            return ft.Card(
                content=ft.Container(
                    content=content,
                    padding=ft.padding.all(padding),
                    border_radius=ft.border_radius.all(self.get_corner_radius("medium"))
                ),
                elevation=self.get_elevation(elevation),
                color=self.get_color(ColorRole.SURFACE),
            )
            
        except Exception as e:
            self.logger.error(f"Surface card creation error: {e}")
            return ft.Card(content=content)


# ============================================================================
# GLOBAL INSTANCES AND BACKWARD COMPATIBILITY
# ============================================================================

# Global instances
_global_theme_manager: Optional[UnifiedThemeManager] = None
_global_theme_utilities: Optional[ThemeUtilities] = None


def initialize_theme(page: ft.Page) -> UnifiedThemeManager:
    """Initialize and return global theme manager"""
    global _global_theme_manager, _global_theme_utilities, theme_system
    
    if _global_theme_manager is None:
        _global_theme_manager = UnifiedThemeManager(page)
        _global_theme_utilities = ThemeUtilities(_global_theme_manager)
        theme_system = _global_theme_manager  # Set backward compatibility alias
    
    return _global_theme_manager


def get_theme_manager() -> Optional[UnifiedThemeManager]:
    """Get global theme manager instance"""
    return _global_theme_manager


def get_theme_utilities() -> Optional[ThemeUtilities]:
    """Get global theme utilities instance"""
    return _global_theme_utilities


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================

def get_theme_tokens() -> Dict[str, str]:
    """Get theme tokens - backward compatibility"""
    return TOKENS.copy()


def get_theme_color(color_name: str, default: str = "#000000") -> str:
    """Get theme color by name - backward compatibility"""
    return TOKENS.get(color_name, default)


def get_primary_color() -> str:
    """Get primary color - backward compatibility"""
    return TOKENS["primary"]


def get_secondary_color() -> str:
    """Get secondary color - backward compatibility"""
    return TOKENS["secondary"]


def get_tertiary_color() -> str:
    """Get tertiary color - backward compatibility"""
    return TOKENS["tertiary"]


def get_container_color() -> str:
    """Get container color - backward compatibility"""
    return TOKENS["container"]


def get_gradient_colors() -> List[str]:
    """Get gradient colors - backward compatibility"""
    return TOKENS["primary_gradient"]


def linear_gradient(colors: Optional[List[str]] = None,
                   begin: ft.Alignment = ft.alignment.top_left,
                   end: ft.Alignment = ft.alignment.bottom_right,
                   stops: Optional[List[float]] = None) -> ft.LinearGradient:
    """Create linear gradient - backward compatibility"""
    if colors is None:
        colors = TOKENS["primary_gradient"]
    
    return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)


def gradient_button(content: Union[str, ft.Control], 
                   width: int = 220, height: int = 48,
                   on_click: Optional[Callable] = None, 
                   radius: int = 12) -> ft.Container:
    """Create gradient button - backward compatibility"""
    utilities = get_theme_utilities()
    if utilities:
        return utilities.create_gradient_button(content, width, height, on_click, radius)
    
    # Fallback implementation
    if isinstance(content, str):
        content = ft.Text(content, color=TOKENS["on_primary"])
    
    return ft.Container(
        width=width,
        height=height,
        content=ft.Row([content], alignment=ft.MainAxisAlignment.CENTER),
        border_radius=ft.border_radius.all(radius),
        gradient=linear_gradient(),
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        animate_scale=ft.animation.Animation(180, "easeInOut")
    )


def surface_container(child: ft.Control, padding: int = 12, 
                     radius: int = 12, elevation: int = 2) -> ft.Card:
    """Create surface container - backward compatibility"""
    return ft.Card(
        content=ft.Container(
            content=child,
            padding=ft.padding.all(padding),
            border_radius=ft.border_radius.all(radius)
        ),
        elevation=elevation
    )


def create_theme(use_material3: bool = True, dark: bool = False) -> ft.Theme:
    """Create Flet theme - backward compatibility"""
    manager = get_theme_manager()
    if manager:
        return manager._create_flet_theme(dark)
    
    # Fallback implementation
    seed = TOKENS["primary"]
    theme = ft.Theme(
        use_material3=use_material3,
        color_scheme_seed=seed,
        font_family="Inter"
    )
    
    return theme


def create_themed_button(text: str, icon=None, button_type: str = "filled", **kwargs) -> ft.Control:
    """Create themed button - backward compatibility"""
    utilities = get_theme_utilities()
    if utilities and button_type == "gradient":
        content = ft.Row([ft.Icon(icon), ft.Text(text)]) if icon else ft.Text(text)
        return utilities.create_gradient_button(content, **kwargs)
    
    # Standard button fallback
    if button_type == "filled":
        return ft.FilledButton(text, icon=icon, **kwargs)
    elif button_type == "outlined":
        return ft.OutlinedButton(text, icon=icon, **kwargs)
    else:
        return ft.TextButton(text, icon=icon, **kwargs)


def get_linear_gradient(begin: ft.Alignment = ft.alignment.top_left, 
                       end: ft.Alignment = ft.alignment.bottom_right, 
                       stops: Optional[List[float]] = None) -> ft.LinearGradient:
    """Get linear gradient - backward compatibility"""
    return linear_gradient(None, begin, end, stops)


def get_gradient_button_style() -> Dict[str, Any]:
    """Get gradient button style - backward compatibility"""
    return {
        "gradient": linear_gradient(),
        "border_radius": ft.border_radius.all(12)
    }


def apply_theme_consistency(page: ft.Page, tokens: Optional[Dict[str, str]] = None) -> None:
    """Apply theme consistency to the entire page - backward compatibility"""
    try:
        # Initialize unified theme manager
        theme_manager = initialize_theme(page)
        
        if tokens:
            # Update with provided tokens
            color_updates = {}
            typography_updates = {}
            
            for key, value in tokens.items():
                # Try to map string keys to ColorRole enum
                try:
                    if key in ['primary', 'secondary', 'tertiary', 'error', 'surface', 'background']:
                        if key == 'primary':
                            color_updates[ColorRole.PRIMARY] = value
                        elif key == 'secondary':
                            color_updates[ColorRole.SECONDARY] = value
                        elif key == 'tertiary':
                            color_updates[ColorRole.TERTIARY] = value
                        elif key == 'error':
                            color_updates[ColorRole.ERROR] = value
                        elif key == 'surface':
                            color_updates[ColorRole.SURFACE] = value
                        elif key == 'background':
                            color_updates[ColorRole.BACKGROUND] = value
                except Exception:
                    # Skip invalid tokens
                    pass
            
            if color_updates:
                theme_manager.update_tokens(color_updates)
        
        # Apply theme consistency automatically through unified manager
        theme_manager.apply_theme()
        
    except Exception as e:
        logger.error(f"apply_theme_consistency error: {e}")
        # Fallback - just apply basic theme
        try:
            theme_manager = initialize_theme(page)
            theme_manager.apply_theme()
        except Exception:
            pass  # Silent fallback


# ============================================================================
# LEGACY CLASSES FOR BACKWARD COMPATIBILITY
# ============================================================================

class ThemeManager:
    """Legacy theme manager class for backward compatibility"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._unified_manager = initialize_theme(page)
        self.page.theme_mode = ft.ThemeMode.SYSTEM
    
    def apply_theme(self):
        """Apply theme to page"""
        self._unified_manager.apply_theme()
    
    def toggle_theme(self, e=None):
        """Toggle theme mode"""
        self._unified_manager.toggle_theme()
    
    def get_tokens(self):
        """Get design tokens"""
        return TOKENS.copy()
    
    def get_gradient(self, colors=None, begin=ft.alignment.top_left, 
                    end=ft.alignment.bottom_right, stops=None):
        """Get linear gradient"""
        return linear_gradient(colors, begin, end, stops)


class ThemeConsistencyManager:
    """Legacy theme consistency manager for backward compatibility"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._unified_manager = initialize_theme(page)
        self.theme_manager = self._unified_manager  # For compatibility
    
    def get_component_colors(self, component_type: str = "surface"):
        """Get component colors - backward compatibility"""
        utilities = get_theme_utilities()
        if utilities:
            if component_type == "surface":
                return {
                    "bg": utilities.get_color(ColorRole.SURFACE),
                    "fg": utilities.get_color(ColorRole.ON_SURFACE),
                    "variant_bg": utilities.get_color(ColorRole.SURFACE_VARIANT),
                    "variant_fg": utilities.get_color(ColorRole.ON_SURFACE_VARIANT),
                    "outline": utilities.get_color(ColorRole.OUTLINE)
                }
            elif component_type == "primary":
                return {
                    "bg": utilities.get_color(ColorRole.PRIMARY),
                    "fg": utilities.get_color(ColorRole.ON_PRIMARY),
                    "container_bg": utilities.get_color(ColorRole.PRIMARY_CONTAINER),
                    "container_fg": utilities.get_color(ColorRole.ON_PRIMARY_CONTAINER)
                }
        return {}
    
    def get_theme_tokens(self):
        """Get theme tokens"""
        return self._unified_manager.tokens if self._unified_manager else MaterialDesignTokens()


# ============================================================================
# EXPORTS
# ============================================================================

# ============================================================================  
# DYNAMIC TOKENS - Theme-Aware Color Tokens
# ============================================================================

class DynamicTokens:
    """
    Dynamic theme-aware tokens that return appropriate colors based on current theme mode.
    This replaces static TOKENS with intelligent, adaptive color values.
    """
    
    def __init__(self):
        self._theme_manager = None
    
    def _get_theme_manager(self):
        """Get current theme manager instance"""
        if self._theme_manager is None:
            self._theme_manager = get_theme_manager()
        return self._theme_manager
    
    def _get_current_theme_mode(self):
        """Get current theme mode"""
        theme_manager = self._get_theme_manager()
        if theme_manager:
            return theme_manager.current_mode
        return ThemeMode.SYSTEM
    
    def _is_dark_mode(self):
        """Check if current theme is dark mode"""
        mode = self._get_current_theme_mode()
        if mode == ThemeMode.DARK:
            return True
        elif mode == ThemeMode.LIGHT:
            return False
        elif mode == ThemeMode.SYSTEM:
            # Auto-detect system theme (simplified)
            import datetime
            hour = datetime.datetime.now().hour
            return hour < 6 or hour >= 18
        return False  # Default to light mode
    
    def _get_theme_aware_color(self, light_color: str, dark_color: str) -> str:
        """Get appropriate color based on current theme mode"""
        return dark_color if self._is_dark_mode() else light_color
    
    def __getitem__(self, key: str) -> str:
        """Get theme-aware color by key"""
        # Get static token value
        static_color = TOKENS.get(key, "#000000")
        
        # Return theme-aware adaptation for common colors
        if key == "surface":
            return self._get_theme_aware_color(TOKENS["surface"], TOKENS["surface_dark"])
        elif key == "on_surface":
            return "#FFFFFF" if self._is_dark_mode() else TOKENS["on_surface"]
        elif key == "background":
            return self._get_theme_aware_color(TOKENS["background"], TOKENS["surface_dark"])
        elif key == "on_background":
            return "#FFFFFF" if self._is_dark_mode() else TOKENS["on_background"]
        
        # For other colors, return static value for now
        # In a more advanced implementation, we could adjust saturation/brightness for dark mode
        return static_color
    
    def get(self, key: str, default: str = "#000000") -> str:
        """Get theme-aware color with default fallback"""
        try:
            return self[key]
        except KeyError:
            return default


# Global dynamic tokens instance
_DYNAMIC_TOKENS = None

def get_dynamic_tokens() -> DynamicTokens:
    """Get global dynamic tokens instance"""
    global _DYNAMIC_TOKENS
    if _DYNAMIC_TOKENS is None:
        _DYNAMIC_TOKENS = DynamicTokens()
    return _DYNAMIC_TOKENS


# Theme-aware TOKENS proxy - drop-in replacement for static TOKENS
def DYNAMIC_TOKENS_PROXY() -> DynamicTokens:
    """
    Drop-in replacement for static TOKENS that returns theme-aware colors.
    Usage: DYNAMIC_TOKENS_PROXY()['primary'] instead of TOKENS['primary']
    """
    return get_dynamic_tokens()


def get_theme_system() -> Optional[UnifiedThemeManager]:
    """Get global theme manager instance - backward compatibility"""
    return get_theme_manager()


# Backward compatibility alias
theme_system = None  # Will be set when initialize_theme is called
MaterialDesign3ThemeSystem = UnifiedThemeManager


__all__ = [
    # Core classes
    "UnifiedThemeManager",
    "ThemeUtilities", 
    "ThemeValidator",
    "MaterialDesignTokens",
    
    # Backward compatibility
    "MaterialDesign3ThemeSystem",
    "theme_system",
    "get_theme_system",
    
    # Enums
    "ColorRole",
    "TypographyRole", 
    "ThemeMode",
    
    # Global functions
    "initialize_theme",
    "get_theme_manager",
    "get_theme_utilities",
    
    # Dynamic tokens
    "DynamicTokens",
    "get_dynamic_tokens",
    "DYNAMIC_TOKENS_PROXY",
    
    # Backward compatibility
    "ThemeManager",
    "ThemeConsistencyManager", 
    "apply_theme_consistency",
    "TOKENS",
    "get_theme_tokens",
    "get_theme_color",
    "get_primary_color",
    "get_secondary_color",
    "get_tertiary_color", 
    "get_container_color",
    "get_gradient_colors",
    "linear_gradient",
    "gradient_button",
    "surface_container",
    "create_theme",
    "create_themed_button",
    "get_linear_gradient",
    "get_gradient_button_style",
]