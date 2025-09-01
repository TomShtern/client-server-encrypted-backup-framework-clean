"""
Theme Compatibility Layer
Provides backward compatibility for existing theme usage while transitioning to clean system.

This module serves as a bridge between the old unified_theme_system imports and 
Flet's native color system, ensuring all existing components continue to work
without modification while we transition to a cleaner architecture.
"""

import flet as ft
from typing import Dict, Any, Optional

# Compatibility TOKENS dictionary using verified Flet colors
TOKENS = {
    # Primary colors - core Material Design colors
    'primary': ft.Colors.PRIMARY,
    'on_primary': ft.Colors.ON_PRIMARY,
    'primary_container': ft.Colors.PRIMARY_CONTAINER,
    'on_primary_container': ft.Colors.ON_PRIMARY_CONTAINER,
    
    # Secondary colors
    'secondary': ft.Colors.SECONDARY,
    'on_secondary': ft.Colors.ON_SECONDARY,
    'secondary_container': ft.Colors.SECONDARY_CONTAINER,
    'on_secondary_container': ft.Colors.ON_SECONDARY_CONTAINER,
    
    # Tertiary colors
    'tertiary': ft.Colors.TERTIARY,
    'on_tertiary': ft.Colors.ON_TERTIARY,
    'tertiary_container': ft.Colors.TERTIARY_CONTAINER,
    'on_tertiary_container': ft.Colors.ON_TERTIARY_CONTAINER,
    
    # Surface colors - use basic ones that definitely exist
    'surface': ft.Colors.SURFACE,
    'on_surface': ft.Colors.ON_SURFACE,
    'surface_variant': ft.Colors.SURFACE_TINT,  # Use SURFACE_TINT as fallback
    'on_surface_variant': ft.Colors.ON_SURFACE_VARIANT,
    
    # Error colors
    'error': ft.Colors.ERROR,
    'on_error': ft.Colors.ON_ERROR,
    'error_container': ft.Colors.ERROR_CONTAINER,
    'on_error_container': ft.Colors.ON_ERROR_CONTAINER,
    
    # Other semantic colors - using safe fallbacks
    'outline': ft.Colors.OUTLINE,
    'outline_variant': ft.Colors.OUTLINE_VARIANT,
    'background': ft.Colors.SURFACE,  # Use surface as background
    'on_background': ft.Colors.ON_SURFACE,
    'inverse_surface': ft.Colors.INVERSE_SURFACE,
    'inverse_on_surface': ft.Colors.ON_SURFACE,  # Safe fallback
    'inverse_primary': ft.Colors.INVERSE_PRIMARY,
    'shadow': ft.Colors.BLACK12,  # Safe fallback
    'scrim': ft.Colors.BLACK54,  # Safe fallback
    
    # Common UI colors for compatibility
    'success': ft.Colors.GREEN,
    'warning': ft.Colors.ORANGE,
    'info': ft.Colors.BLUE,
    
    # Additional surface variants using safe fallbacks
    'surface_dim': ft.Colors.SURFACE,
    'surface_bright': ft.Colors.SURFACE,
    'surface_container_lowest': ft.Colors.SURFACE,
    'surface_container_low': ft.Colors.SURFACE,
    'surface_container': ft.Colors.SURFACE,
    'surface_container_high': ft.Colors.SURFACE,
    'surface_container_highest': ft.Colors.SURFACE,
}

class ThemeManager:
    """
    Compatibility wrapper for theme management.
    Provides the same interface as the original ThemeManager while using Flet's native theming.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self._tokens = TOKENS.copy()
    
    def get_tokens(self) -> Dict[str, str]:
        """Return the color tokens dictionary"""
        return self._tokens
    
    def apply_theme(self) -> None:
        """
        Apply theme to the page.
        Flet handles this automatically, but we maintain the interface for compatibility.
        """
        # Flet's native theme handling is automatic
        if hasattr(self.page, 'update'):
            self.page.update()
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark theme"""
        current_theme = getattr(self.page, 'theme_mode', ft.ThemeMode.SYSTEM)
        
        if current_theme == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
        elif current_theme == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            # If system theme, default to light
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        if hasattr(self.page, 'update'):
            self.page.update()
    
    def get_theme_mode(self) -> str:
        """Get current theme mode as string"""
        theme_mode = getattr(self.page, 'theme_mode', ft.ThemeMode.SYSTEM)
        if theme_mode == ft.ThemeMode.LIGHT:
            return 'light'
        elif theme_mode == ft.ThemeMode.DARK:
            return 'dark'
        else:
            return 'system'

class ThemeConsistencyManager:
    """
    Compatibility wrapper for theme consistency management.
    Maintains the same interface while using Flet's native system.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.theme_manager = ThemeManager(page)
    
    def ensure_consistency(self) -> None:
        """Ensure theme consistency across components"""
        # Flet handles this natively
        pass
    
    def get_tokens(self) -> Dict[str, str]:
        """Get theme tokens"""
        return self.theme_manager.get_tokens()

def apply_theme_consistency(page: ft.Page, *args, **kwargs) -> None:
    """
    No-op function for compatibility.
    Flet handles theme consistency automatically.
    """
    pass

def linear_gradient(
    colors: Optional[list] = None,
    begin: Optional[ft.Alignment] = None,
    end: Optional[ft.Alignment] = None,
    **kwargs
) -> ft.LinearGradient:
    """
    Compatibility wrapper for gradients using Flet's native LinearGradient.
    """
    if colors is None:
        colors = [ft.Colors.PRIMARY, ft.Colors.SECONDARY]
    
    if begin is None:
        begin = ft.alignment.top_left
    
    if end is None:
        end = ft.alignment.bottom_right
    
    return ft.LinearGradient(
        colors=colors,
        begin=begin,
        end=end
    )

def gradient_button(
    text: str = "Button",
    on_click=None,
    colors: Optional[list] = None,
    **kwargs
) -> ft.Container:
    """
    Compatibility wrapper for gradient buttons.
    Creates a Container with gradient background and button-like behavior.
    """
    if colors is None:
        colors = [ft.Colors.PRIMARY, ft.Colors.SECONDARY]
    
    gradient = linear_gradient(colors=colors)
    
    return ft.Container(
        content=ft.Text(
            text,
            color=ft.Colors.ON_PRIMARY,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER
        ),
        gradient=gradient,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        on_click=on_click,
        ink=True,
        **kwargs
    )

def get_semantic_color(color_name: str, fallback: str = ft.Colors.PRIMARY) -> str:
    """
    Get a semantic color by name with fallback.
    
    Args:
        color_name: Name of the color (e.g., 'primary', 'error', 'success')
        fallback: Fallback color if the requested color is not found
    
    Returns:
        Color string suitable for Flet components
    """
    return TOKENS.get(color_name, fallback)

def create_themed_container(
    content: ft.Control,
    background_color: str = 'surface',
    border_color: str = 'outline_variant',
    **kwargs
) -> ft.Container:
    """
    Create a themed container with semantic colors.
    
    Args:
        content: The content to place in the container
        background_color: Background color key from TOKENS
        border_color: Border color key from TOKENS
        **kwargs: Additional Container properties
    
    Returns:
        Configured Container with themed colors
    """
    return ft.Container(
        content=content,
        bgcolor=get_semantic_color(background_color),
        border=ft.border.all(1, get_semantic_color(border_color)),
        border_radius=12,
        padding=ft.padding.all(16),
        **kwargs
    )

# Legacy compatibility functions
def get_theme_colors() -> Dict[str, str]:
    """Legacy function - returns TOKENS"""
    return TOKENS

def apply_material_theme(page: ft.Page) -> None:
    """Legacy function - no-op as Flet handles this natively"""
    pass

def setup_theme_system(page: ft.Page) -> ThemeManager:
    """Setup and return a ThemeManager for the given page"""
    return ThemeManager(page)

# Export commonly used items for backward compatibility
__all__ = [
    'TOKENS',
    'ThemeManager', 
    'ThemeConsistencyManager',
    'apply_theme_consistency',
    'linear_gradient',
    'gradient_button',
    'get_semantic_color',
    'create_themed_container',
    'get_theme_colors',
    'apply_material_theme',
    'setup_theme_system'
]