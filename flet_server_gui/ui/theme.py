#!/usr/bin/env python3
"""
Purpose: Material Design 3 theme and styling system
Logic: Theme configuration, color schemes, typography
UI: Theme application and style utilities
"""

import flet as ft
from typing import Optional, Dict, Any, Union
from enum import Enum

# ============================================================================
# DESIGN TOKENS (from theme_m3.py)
# ============================================================================

TOKENS = {
    # Primary: blue → purple gradient (use these colors for gradients, accents, icons)
    "primary_gradient": ["#A8CBF3", "#7C5CD9"],  # light blue to purple
    "primary": "#7C5CD9",  # fallback solid primary (purple)
    "on_primary": "#FFFFFF",
    # Secondary: ORANGE (as requested)
    "secondary": "#FFA500",  # Pure orange
    "on_secondary": "#000000",
    # Tertiary: pink-ish (bottom arrow) — distinct from error red
    "tertiary": "#AB6DA4",
    "on_tertiary": "#FFFFFF",
    # Containers (teal for the "file page" background)
    "container": "#38A298",
    "on_container": "#FFFFFF",
    # Surface tones (suggested): neutral surfaces compatible with M3
    "surface": "#F6F8FB",            # main surface (light)
    "surface_variant": "#E7EDF7",    # subtle variant
    "surface_dark": "#0F1720",       # main dark surface suggestion
    "background": "#FFFFFF",
    "on_background": "#000000",
    "outline": "#666666",
    # Error
    "error": "#B00020",
    "on_error": "#FFFFFF"
}

# ============================================================================
# THEME MANAGER (consolidated from theme_manager.py and theme_utils.py)
# ============================================================================

class ThemeManager:
    """Manages Material Design 3 themes and styling using custom design tokens."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        # Set the default theme mode. SYSTEM is a good choice.
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self._cached_tokens = None

    def apply_theme(self):
        """
        Applies light and dark themes to the page using custom design tokens.
        Falls back to default M3 theme if custom theme is not available.
        """
        try:
            # Use custom theme with design tokens
            self.page.theme = self.create_theme(use_material3=True, dark=False)
            self.page.dark_theme = self.create_theme(use_material3=True, dark=True)
            
            # Apply custom font if available
            if hasattr(self.page.theme, 'font_family'):
                self.page.theme.font_family = "Inter"
                self.page.dark_theme.font_family = "Inter"
        except Exception as e:
            print(f"[WARNING] Failed to apply custom theme: {e}")
            # Fallback to default M3 theme
            self.page.theme = ft.Theme(
                color_scheme_seed=TOKENS.get("primary", "blue"),
                use_material3=True
            )
            self.page.dark_theme = ft.Theme(
                color_scheme_seed=TOKENS.get("primary", "indigo"),
                use_material3=True
            )
        
        self.page.update()
    
    def apply_consistency(self):
        """
        Apply theme consistency across the application.
        Temporarily disabled to prevent async/threading issues.
        """
        try:
            from flet_server_gui.ui.theme_consistency import apply_theme_consistency
            # Temporarily disabled to fix async/threading issues
            # apply_theme_consistency(self.page, TOKENS)
            print("[INFO] Theme consistency disabled to prevent async errors")
        except Exception as e:
            print(f"[WARNING] Theme consistency not available: {e}")

    def create_theme(self, use_material3: bool = True, dark: bool = False) -> ft.Theme:
        """Return a Flet Theme using the tokens above.
        This creates a full Material color scheme using all custom tokens.
        We also expose the token palette for direct use."""
        
        # Create base theme with primary color as seed
        seed = TOKENS.get("primary") or TOKENS["primary_gradient"][0]
        theme = ft.Theme(
            use_material3=use_material3,
            color_scheme_seed=seed,
            font_family="Inter"
        )
        
        # Override with custom color scheme if available
        if hasattr(ft, 'ColorScheme'):
            try:
                # Create a custom color scheme using all the defined tokens
                custom_scheme = ft.ColorScheme(
                    primary=TOKENS.get("primary", "#7C5CD9"),
                    on_primary=TOKENS.get("on_primary", "#FFFFFF"),
                    secondary=TOKENS.get("secondary", "#FFA500"),
                    on_secondary=TOKENS.get("on_secondary", "#000000"),
                    tertiary=TOKENS.get("tertiary", "#AB6DA4"),
                    on_tertiary=TOKENS.get("on_tertiary", "#FFFFFF"),
                    primary_container=TOKENS.get("container", "#38A298"),
                    on_primary_container=TOKENS.get("on_container", "#FFFFFF"),
                    secondary_container=TOKENS.get("container", "#38A298"),
                    on_secondary_container=TOKENS.get("on_container", "#FFFFFF"),
                    tertiary_container=TOKENS.get("container", "#38A298"),
                    on_tertiary_container=TOKENS.get("on_container", "#FFFFFF"),
                    surface=TOKENS.get("surface", "#F6F8FB") if not dark else TOKENS.get("surface_dark", "#0F1720"),
                    on_surface=TOKENS.get("on_background", "#000000") if not dark else "#FFFFFF",
                    surface_variant=TOKENS.get("surface_variant", "#E7EDF7"),
                    on_surface_variant=TOKENS.get("outline", "#666666"),
                    outline=TOKENS.get("outline", "#666666"),
                    error=TOKENS.get("error", "#B00020"),
                    on_error=TOKENS.get("on_error", "#FFFFFF"),
                )
                
                # Apply the custom color scheme
                theme.color_scheme = custom_scheme
                
                # For dark theme, adjust some colors
                if dark:
                    dark_scheme = ft.ColorScheme(
                        primary=TOKENS.get("primary", "#7C5CD9"),
                        on_primary=TOKENS.get("on_primary", "#FFFFFF"),
                        secondary=TOKENS.get("secondary", "#FFA500"),
                        on_secondary=TOKENS.get("on_secondary", "#000000"),
                        tertiary=TOKENS.get("tertiary", "#AB6DA4"),
                        on_tertiary=TOKENS.get("on_tertiary", "#FFFFFF"),
                        primary_container=TOKENS.get("container", "#38A298"),
                        on_primary_container=TOKENS.get("on_container", "#FFFFFF"),
                        secondary_container=TOKENS.get("container", "#38A298"),
                        on_secondary_container=TOKENS.get("on_container", "#FFFFFF"),
                        tertiary_container=TOKENS.get("container", "#38A298"),
                        on_tertiary_container=TOKENS.get("on_container", "#FFFFFF"),
                        surface=TOKENS.get("surface_dark", "#0F1720"),
                        on_surface="#FFFFFF",
                        surface_variant=TOKENS.get("surface_variant", "#E7EDF7"),
                        on_surface_variant=TOKENS.get("outline", "#666666"),
                        outline=TOKENS.get("outline", "#666666"),
                        error=TOKENS.get("error", "#B00020"),
                        on_error=TOKENS.get("on_error", "#FFFFFF"),
                    )
                    theme.color_scheme = dark_scheme
            except Exception as e:
                print(f"[WARNING] Failed to create custom color scheme: {e}")
        
        return theme

    def toggle_theme(self, e=None):
        """Toggle between light, dark, and system theme modes."""
        current_mode = self.page.theme_mode
        if current_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
        elif current_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.page.update()

    def get_tokens(self) -> Dict[str, str]:
        """Return the design tokens for direct use in components."""
        return TOKENS.copy()

    def get_gradient(self, colors=None, begin=ft.alignment.top_left, end=ft.alignment.bottom_right, stops=None):
        """Return a linear gradient using the custom theme."""
        try:
            return linear_gradient(colors, begin, end, stops)
        except Exception:
            # Fallback gradient
            if colors is None:
                colors = TOKENS.get("primary_gradient", ["#2196F3", "#3F51B5"])
            return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)

# ============================================================================
# THEME UTILITIES (consolidated from theme_utils.py)
# ============================================================================

def get_theme_tokens() -> Dict[str, str]:
    """Get theme tokens with caching for performance."""
    return TOKENS.copy()

def get_theme_color(color_name: str, default: str = "#000000") -> str:
    """Get a specific theme color by name."""
    return TOKENS.get(color_name, default)

def get_primary_color() -> str:
    """Get the primary color."""
    return get_theme_color("primary", "#7C5CD9")

def get_secondary_color() -> str:
    """Get the secondary color."""
    return get_theme_color("secondary", "#FFA500")

def get_tertiary_color() -> str:
    """Get the tertiary color."""
    return get_theme_color("tertiary", "#AB6DA4")

def get_container_color() -> str:
    """Get the container color."""
    return get_theme_color("container", "#38A298")

def get_gradient_colors() -> list:
    """Get the primary gradient colors."""
    return TOKENS.get("primary_gradient", ["#A8CBF3", "#7C5CD9"])

def get_linear_gradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, stops=None) -> ft.LinearGradient:
    """Create a linear gradient using theme colors."""
    try:
        return linear_gradient(begin=begin, end=end, stops=stops)
    except Exception:
        # Fallback gradient
        colors = get_gradient_colors()
        return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)

def get_gradient_button_style() -> Dict[str, Any]:
    """Get style dictionary for gradient buttons."""
    return {
        "gradient": get_linear_gradient(),
        "border_radius": ft.border_radius.all(12)
    }

def apply_theme_to_component(component: ft.Control, page: ft.Page) -> None:
    """Apply theme colors to a component based on its type and purpose."""
    # This function can be extended to automatically style components
    # based on theme tokens
    pass

def create_themed_button(text: str, icon=None, button_type: str = "filled", **kwargs) -> ft.Control:
    """Create a themed button using the appropriate theme colors."""
    try:
        if button_type == "gradient":
            return gradient_button(ft.Row([ft.Icon(icon), ft.Text(text)]) if icon else ft.Text(text), **kwargs)
    except Exception:
        pass
    
    # Fallback to standard buttons
    if button_type == "filled":
        return ft.FilledButton(text, icon=icon, **kwargs)
    elif button_type == "outlined":
        return ft.OutlinedButton(text, icon=icon, **kwargs)
    else:
        return ft.TextButton(text, icon=icon, **kwargs)

# ============================================================================
# HELPER FUNCTIONS (from theme_m3.py)
# ============================================================================

def linear_gradient(colors=None, begin=ft.alignment.top_left, end=ft.alignment.bottom_right, stops=None):
    """Make linear gradient for containers/buttons"""
    if colors is None:
        colors = TOKENS["primary_gradient"]
    return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)

def gradient_button(content, width=220, height=48, on_click=None, radius=12):
    """Return a Container that behaves like a Filled/Gradient button."""
    c = ft.Container(
        width=width,
        height=height,
        content=ft.Row([content], alignment=ft.MainAxisAlignment.CENTER),
        border_radius=ft.border_radius.all(radius),
        gradient=linear_gradient(),
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        animate_scale=180
    )
    return c

def surface_container(child, padding=12, radius=12, elevation=2):
    """Create a surface container with Material Design 3 styling."""
    return ft.Card(content=child, elevation=elevation, border_radius=ft.border_radius.all(radius))

# ============================================================================
# STYLE PRESETS
# ============================================================================

class StylePresets:
    """Pre-defined style configurations for common UI patterns."""
    
    @staticmethod
    def get_card_style(elevated: bool = True) -> Dict[str, Any]:
        """Get card styling configuration."""
        return {
            "elevation": 2 if elevated else 0,
            "border_radius": ft.border_radius.all(12),
            "padding": 16,
        }
    
    @staticmethod
    def get_button_style(style_type: str = "filled") -> Dict[str, Any]:
        """Get button styling configuration."""
        styles = {
            "filled": {
                "style": ft.ButtonStyle(
                    bgcolor=get_primary_color(),
                    color=get_theme_color("on_primary")
                )
            },
            "outlined": {
                "style": ft.ButtonStyle(
                    side=ft.BorderSide(1, get_primary_color())
                )
            },
            "text": {
                "style": ft.ButtonStyle(
                    color=get_primary_color()
                )
            }
        }
        return styles.get(style_type, styles["filled"])
    
    @staticmethod
    def get_text_style(variant: str = "body") -> ft.TextStyle:
        """Get text styling configuration."""
        styles = {
            "headline": ft.TextStyle(size=24, weight=ft.FontWeight.BOLD),
            "title": ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
            "body": ft.TextStyle(size=14),
            "caption": ft.TextStyle(size=12, color=get_theme_color("outline"))
        }
        return styles.get(variant, styles["body"])

# ============================================================================
# INITIALIZATION HELPERS
# ============================================================================

def initialize_theme(page: ft.Page) -> ThemeManager:
    """Initialize and apply theme to a page."""
    theme_manager = ThemeManager(page)
    theme_manager.apply_theme()
    return theme_manager