"""
Design Tokens - Phase 4 Material Design 3 Consolidation
======================================================

This file defines all Material Design 3 design tokens for the Flet Server GUI.
Design tokens provide the foundation for consistent theming across all components.

CONSOLIDATION TARGET:
- Extract design tokens from scattered theme files
- Provide single source of truth for design values
- Enable easy theme customization and maintenance
"""

import flet as ft
from typing import Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum


class ColorRole(Enum):
    """Material Design 3 color role definitions"""
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
    SURFACE = "surface"
    ON_SURFACE = "on_surface"
    SURFACE_VARIANT = "surface_variant"
    ON_SURFACE_VARIANT = "on_surface_variant"
    OUTLINE = "outline"
    OUTLINE_VARIANT = "outline_variant"


class TypographyRole(Enum):
    """Material Design 3 typography role definitions"""
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


@dataclass
class DesignToken:
    """Base class for design tokens"""
    name: str
    value: Any
    category: str
    description: str = ""


# Color Design Tokens
# TODO: Consolidate these values from existing theme files

LIGHT_COLOR_TOKENS: Dict[ColorRole, str] = {
    ColorRole.PRIMARY: ft.Colors.BLUE,
    ColorRole.ON_PRIMARY: ft.Colors.WHITE,
    ColorRole.PRIMARY_CONTAINER: ft.Colors.BLUE_100,
    ColorRole.ON_PRIMARY_CONTAINER: ft.Colors.BLUE_900,
    
    ColorRole.SECONDARY: ft.Colors.GREEN,
    ColorRole.ON_SECONDARY: ft.Colors.WHITE,
    ColorRole.SECONDARY_CONTAINER: ft.Colors.GREEN_100,
    ColorRole.ON_SECONDARY_CONTAINER: ft.Colors.GREEN_900,
    
    ColorRole.TERTIARY: ft.Colors.ORANGE,
    ColorRole.ON_TERTIARY: ft.Colors.WHITE,
    ColorRole.TERTIARY_CONTAINER: ft.Colors.ORANGE_100,
    ColorRole.ON_TERTIARY_CONTAINER: ft.Colors.ORANGE_900,
    
    ColorRole.ERROR: ft.Colors.RED,
    ColorRole.ON_ERROR: ft.Colors.WHITE,
    ColorRole.ERROR_CONTAINER: ft.Colors.RED_100,
    ColorRole.ON_ERROR_CONTAINER: ft.Colors.RED_900,
    
    ColorRole.SURFACE: ft.Colors.WHITE,
    ColorRole.ON_SURFACE: ft.Colors.BLACK87,
    ColorRole.SURFACE_VARIANT: ft.Colors.GREY_100,
    ColorRole.ON_SURFACE_VARIANT: ft.Colors.GREY_700,
    
    ColorRole.OUTLINE: ft.Colors.GREY_400,
    ColorRole.OUTLINE_VARIANT: ft.Colors.GREY_200,
}

DARK_COLOR_TOKENS: Dict[ColorRole, str] = {
    ColorRole.PRIMARY: ft.Colors.BLUE_200,
    ColorRole.ON_PRIMARY: ft.Colors.BLUE_900,
    ColorRole.PRIMARY_CONTAINER: ft.Colors.BLUE_800,
    ColorRole.ON_PRIMARY_CONTAINER: ft.Colors.BLUE_100,
    
    ColorRole.SECONDARY: ft.Colors.GREEN_200,
    ColorRole.ON_SECONDARY: ft.Colors.GREEN_900,
    ColorRole.SECONDARY_CONTAINER: ft.Colors.GREEN_800,
    ColorRole.ON_SECONDARY_CONTAINER: ft.Colors.GREEN_100,
    
    ColorRole.TERTIARY: ft.Colors.ORANGE_200,
    ColorRole.ON_TERTIARY: ft.Colors.ORANGE_900,
    ColorRole.TERTIARY_CONTAINER: ft.Colors.ORANGE_800,
    ColorRole.ON_TERTIARY_CONTAINER: ft.Colors.ORANGE_100,
    
    ColorRole.ERROR: ft.Colors.RED_200,
    ColorRole.ON_ERROR: ft.Colors.RED_900,
    ColorRole.ERROR_CONTAINER: ft.Colors.RED_800,
    ColorRole.ON_ERROR_CONTAINER: ft.Colors.RED_100,
    
    ColorRole.SURFACE: ft.Colors.GREY_900,
    ColorRole.ON_SURFACE: ft.Colors.WHITE,
    ColorRole.SURFACE_VARIANT: ft.Colors.GREY_800,
    ColorRole.ON_SURFACE_VARIANT: ft.Colors.GREY_300,
    
    ColorRole.OUTLINE: ft.Colors.GREY_600,
    ColorRole.OUTLINE_VARIANT: ft.Colors.GREY_700,
}

# Typography Design Tokens
# TODO: Consolidate from existing typography definitions

TYPOGRAPHY_TOKENS: Dict[TypographyRole, Dict[str, Any]] = {
    TypographyRole.DISPLAY_LARGE: {
        "font_family": "Roboto",
        "font_size": 57,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 64,
        "letter_spacing": -0.25,
    },
    TypographyRole.DISPLAY_MEDIUM: {
        "font_family": "Roboto",
        "font_size": 45,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 52,
        "letter_spacing": 0,
    },
    TypographyRole.DISPLAY_SMALL: {
        "font_family": "Roboto",
        "font_size": 36,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 44,
        "letter_spacing": 0,
    },
    TypographyRole.HEADLINE_LARGE: {
        "font_family": "Roboto",
        "font_size": 32,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 40,
        "letter_spacing": 0,
    },
    TypographyRole.HEADLINE_MEDIUM: {
        "font_family": "Roboto",
        "font_size": 28,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 36,
        "letter_spacing": 0,
    },
    TypographyRole.HEADLINE_SMALL: {
        "font_family": "Roboto",
        "font_size": 24,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 32,
        "letter_spacing": 0,
    },
    TypographyRole.TITLE_LARGE: {
        "font_family": "Roboto",
        "font_size": 22,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 28,
        "letter_spacing": 0,
    },
    TypographyRole.TITLE_MEDIUM: {
        "font_family": "Roboto",
        "font_size": 16,
        "font_weight": ft.FontWeight.W_500,
        "line_height": 24,
        "letter_spacing": 0.15,
    },
    TypographyRole.TITLE_SMALL: {
        "font_family": "Roboto",
        "font_size": 14,
        "font_weight": ft.FontWeight.W_500,
        "line_height": 20,
        "letter_spacing": 0.1,
    },
    TypographyRole.BODY_LARGE: {
        "font_family": "Roboto",
        "font_size": 16,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 24,
        "letter_spacing": 0.15,
    },
    TypographyRole.BODY_MEDIUM: {
        "font_family": "Roboto",
        "font_size": 14,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 20,
        "letter_spacing": 0.25,
    },
    TypographyRole.BODY_SMALL: {
        "font_family": "Roboto",
        "font_size": 12,
        "font_weight": ft.FontWeight.NORMAL,
        "line_height": 16,
        "letter_spacing": 0.4,
    },
    TypographyRole.LABEL_LARGE: {
        "font_family": "Roboto",
        "font_size": 14,
        "font_weight": ft.FontWeight.W_500,
        "line_height": 20,
        "letter_spacing": 0.1,
    },
    TypographyRole.LABEL_MEDIUM: {
        "font_family": "Roboto",
        "font_size": 12,
        "font_weight": ft.FontWeight.W_500,
        "line_height": 16,
        "letter_spacing": 0.5,
    },
    TypographyRole.LABEL_SMALL: {
        "font_family": "Roboto",
        "font_size": 11,
        "font_weight": ft.FontWeight.W_500,
        "line_height": 16,
        "letter_spacing": 0.5,
    },
}

# Spacing Design Tokens
SPACING_TOKENS: Dict[str, int] = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48,
    "xxxl": 64,
}

# Elevation Design Tokens  
ELEVATION_TOKENS: Dict[str, int] = {
    "level0": 0,
    "level1": 1,
    "level2": 3,
    "level3": 6,
    "level4": 8,
    "level5": 12,
}

# Border Radius Design Tokens
BORDER_RADIUS_TOKENS: Dict[str, int] = {
    "none": 0,
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
    "xxl": 28,
    "full": 999,
}

# Component-Specific Design Tokens
# TODO: Add component-specific tokens from existing components

BUTTON_TOKENS: Dict[str, Any] = {
    "height": 40,
    "padding_horizontal": 24,
    "padding_vertical": 10,
    "border_radius": BORDER_RADIUS_TOKENS["md"],
}

CARD_TOKENS: Dict[str, Any] = {
    "elevation": ELEVATION_TOKENS["level1"],
    "border_radius": BORDER_RADIUS_TOKENS["md"],
    "padding": SPACING_TOKENS["md"],
}

DIALOG_TOKENS: Dict[str, Any] = {
    "elevation": ELEVATION_TOKENS["level3"],
    "border_radius": BORDER_RADIUS_TOKENS["lg"],
    "padding": SPACING_TOKENS["lg"],
    "max_width": 560,
}

# Animation Design Tokens
ANIMATION_TOKENS: Dict[str, Union[int, str]] = {
    "duration_short": 150,
    "duration_medium": 250,
    "duration_long": 300,
    "easing_standard": "cubic-bezier(0.2, 0.0, 0, 1.0)",
    "easing_decelerate": "cubic-bezier(0.0, 0.0, 0.2, 1.0)",
    "easing_accelerate": "cubic-bezier(0.4, 0.0, 1.0, 1.0)",
}


# Helper Functions
def get_color_token(role: ColorRole, is_dark: bool = False) -> str:
    """Get color token by role and theme"""
    tokens = DARK_COLOR_TOKENS if is_dark else LIGHT_COLOR_TOKENS
    return tokens.get(role, ft.Colors.PRIMARY)


def get_typography_token(role: TypographyRole) -> Dict[str, Any]:
    """Get typography token by role"""
    return TYPOGRAPHY_TOKENS.get(role, TYPOGRAPHY_TOKENS[TypographyRole.BODY_MEDIUM])


def get_spacing_token(size: str) -> int:
    """Get spacing token by size"""
    return SPACING_TOKENS.get(size, SPACING_TOKENS["md"])


def get_elevation_token(level: str) -> int:
    """Get elevation token by level"""
    return ELEVATION_TOKENS.get(level, ELEVATION_TOKENS["level1"])


# Export all design tokens
__all__ = [
    'ColorRole',
    'TypographyRole',
    'DesignToken',
    'LIGHT_COLOR_TOKENS',
    'DARK_COLOR_TOKENS',
    'TYPOGRAPHY_TOKENS',
    'SPACING_TOKENS',
    'ELEVATION_TOKENS',
    'BORDER_RADIUS_TOKENS',
    'BUTTON_TOKENS',
    'CARD_TOKENS',
    'DIALOG_TOKENS',
    'ANIMATION_TOKENS',
    'get_color_token',
    'get_typography_token', 
    'get_spacing_token',
    'get_elevation_token',
]