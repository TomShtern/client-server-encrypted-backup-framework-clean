#!/usr/bin/env python3
"""
Material Design 3 Component Factory
==================================

A comprehensive factory for creating Material Design 3 compliant components
with proper theme integration, state layers, and responsive design.

This factory provides:
- M3 compliant buttons (Filled, Outlined, Text, Elevated, Tonal) 
- M3 cards (Elevated, Filled, Outlined)
- M3 navigation components (NavigationRail, NavigationDrawer)
- M3 input components (TextField, DropDown, Checkbox, Switch)
- M3 data display components (DataTable, List items)
- State layers for interactive feedback
- Proper elevation system
- M3 color roles integration
- Typography scale compliance
- Corner radius specifications
"""

import flet as ft
from typing import Dict, List, Callable, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from flet_server_gui.core.theme_compatibility import TOKENS

# Configure logging first
logger = logging.getLogger(__name__)

# Import existing theme and design token systems with comprehensive fallbacks
THEME_SYSTEM_AVAILABLE = False
DESIGN_TOKENS_AVAILABLE = False

# Define classes that are always needed at module level
class ThemeMode:
    LIGHT = "light"
    DARK = "dark"

class ColorRole:
    PRIMARY = "primary"
    ON_PRIMARY = "on_primary"
    SECONDARY = "secondary"
    ON_SECONDARY = "on_secondary"
    PRIMARY_CONTAINER = "primary_container"
    ON_PRIMARY_CONTAINER = "on_primary_container"
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
    SHADOW = "shadow"
    SCRIM = "scrim"

class TypographyRole:
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

try:
    from ..core.theme_compatibility import (
        TOKENS, ThemeManager, get_semantic_color, setup_theme_system
    )
    THEME_SYSTEM_AVAILABLE = True
    DESIGN_TOKENS_AVAILABLE = True
    
    # Compatibility functions
    def get_theme_system():
        return None  # Use Flet's native theming
    
    def get_color_token(role):
        return TOKENS.get(role, ft.Colors.PRIMARY)
    
    def get_typography_token(role):
        return "14"  # Default font size
    
    def get_spacing_token(role):
        return 8  # Default spacing
    
    def get_elevation_token(role):
        return 2  # Default elevation
        
except ImportError:
    THEME_SYSTEM_AVAILABLE = False
    DESIGN_TOKENS_AVAILABLE = False
    # Final fallback - create basic implementations
    logger.warning("Could not import theme system, using fallbacks")
    
    # Use basic fallback colors when theme system is not available
    TOKENS = {
        'primary': ft.Colors.BLUE,
        'on_primary': ft.Colors.WHITE,
        'surface': ft.Colors.WHITE,
        'on_background': ft.Colors.BLACK,
        'error': ft.Colors.RED,
        'outline': ft.Colors.GREY_400,
    }
    
    class FallbackThemeSystem:
        def __init__(self):
            self.current_mode = ThemeMode.DARK
        
        def switch_theme(self, mode):
            self.current_mode = mode
            return None
    
    def get_theme_system():
        return FallbackThemeSystem()
    
    def get_color_token(role, is_dark=False):
        # Basic color mapping for fallback
        color_map = {
            ColorRole.PRIMARY: TOKENS['primary'],
            ColorRole.ON_PRIMARY: TOKENS['on_primary'],
            ColorRole.SURFACE: TOKENS['surface'],
            ColorRole.ON_SURFACE: TOKENS['on_background'],
            ColorRole.ERROR: TOKENS['error'],
            ColorRole.OUTLINE: TOKENS['outline'],
        }
        return color_map.get(role, TOKENS['primary'])
        
    def get_typography_token(role):
        # Basic typography mapping for fallback
        typography_map = {
            TypographyRole.TITLE_LARGE: {"font_size": 22, "font_weight": ft.FontWeight.NORMAL},
            TypographyRole.BODY_LARGE: {"font_size": 16, "font_weight": ft.FontWeight.NORMAL},
            TypographyRole.BODY_MEDIUM: {"font_size": 14, "font_weight": ft.FontWeight.NORMAL},
        }
        return typography_map.get(role, {"font_size": 14, "font_weight": ft.FontWeight.NORMAL})
    
    def get_spacing_token(size):
        spacing_map = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32}
        return spacing_map.get(size, 16)
        
    def get_elevation_token(level):
        elevation_map = {"level0": 0, "level1": 1, "level2": 3, "level3": 6}
        return elevation_map.get(level, 1)
    
    BUTTON_TOKENS = {"height": 40, "border_radius": 12}
    CARD_TOKENS = {"border_radius": 12, "padding": 16}
    BORDER_RADIUS_TOKENS = {"none": 0, "xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20}
    ANIMATION_TOKENS = {"duration_medium": 250}


class ComponentStyle(Enum):
    """Material Design 3 component style variants"""
    # Button styles
    FILLED = "filled"
    OUTLINED = "outlined"
    TEXT = "text"
    ELEVATED = "elevated"
    TONAL = "tonal"
    
    # Card styles  
    ELEVATED_CARD = "elevated"
    FILLED_CARD = "filled"
    OUTLINED_CARD = "outlined"
    
    # Navigation styles
    NAVIGATION_RAIL = "rail"
    NAVIGATION_DRAWER = "drawer"
    NAVIGATION_BAR = "bar"


class StateLayer(Enum):
    """Material Design 3 state layer definitions"""
    HOVER = "hover"
    FOCUS = "focus"
    PRESSED = "pressed"
    DRAGGED = "dragged"
    DISABLED = "disabled"


@dataclass
class M3ComponentConfig:
    """Configuration for M3 component creation"""
    # Core properties
    style: ComponentStyle
    theme_mode: Optional[ThemeMode] = None
    
    # Visual properties
    elevation: Optional[int] = None
    border_radius: Optional[int] = None
    state_layers: List[StateLayer] = field(default_factory=list)
    
    # Typography
    typography_role: Optional[TypographyRole] = None
    
    # Colors (will be resolved from theme)
    primary_color_role: Optional[ColorRole] = None
    surface_color_role: Optional[ColorRole] = None
    
    # Responsive properties
    responsive: bool = True
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    
    # Animation
    animation_duration: int = 250
    enable_animations: bool = True


@dataclass
class M3ButtonConfig(M3ComponentConfig):
    """Extended configuration for M3 buttons"""
    # Button-specific properties
    text: str = ""
    icon: Optional[str] = None
    icon_placement: str = "leading"  # leading, trailing
    size: str = "medium"  # small, medium, large
    full_width: bool = False
    
    # Interaction
    on_click: Optional[Callable] = None
    disabled: bool = False
    loading: bool = False
    
    # Advanced styling
    custom_colors: Optional[Dict[str, str]] = None


@dataclass  
class M3CardConfig(M3ComponentConfig):
    """Extended configuration for M3 cards"""
    # Card-specific properties
    content: Optional[ft.Control] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    actions: Optional[List[ft.Control]] = None
    
    # Layout
    padding: Optional[int] = None
    content_padding: Optional[int] = None
    
    # Interaction
    clickable: bool = False
    on_click: Optional[Callable] = None


class M3ComponentFactory:
    """
    Material Design 3 Component Factory
    
    Provides a unified interface for creating M3-compliant components
    that integrate seamlessly with the existing theme system.
    """
    
    def __init__(self, theme_system=None):
        """Initialize the component factory"""
        self.theme_system = theme_system or get_theme_system()
        self._state_layer_opacity = {
            StateLayer.HOVER: 0.08,
            StateLayer.FOCUS: 0.12,
            StateLayer.PRESSED: 0.16,
            StateLayer.DRAGGED: 0.16,
            StateLayer.DISABLED: 0.12,
        }
    
    def _resolve_color(self, color_role: ColorRole, is_dark: Optional[bool] = None) -> str:
        """Resolve color from theme system"""
        if is_dark is None:
            is_dark = self.theme_system.current_mode == ThemeMode.DARK
        return get_color_token(color_role, is_dark)
    
    def _apply_typography(self, control: ft.Control, typography_role: TypographyRole) -> ft.Control:
        """Apply typography styling to a control"""
        typography = get_typography_token(typography_role)
        
        if hasattr(control, 'size'):
            control.size = typography.get("font_size")
        if hasattr(control, 'weight'):
            control.weight = typography.get("font_weight")
        if hasattr(control, 'font_family'):
            control.font_family = typography.get("font_family")
            
        return control
    
    def _create_state_layer(self, base_color: str, state: StateLayer) -> str:
        """Create state layer color with proper opacity"""
        opacity = self._state_layer_opacity.get(state, 0.08)
        # This is a simplified implementation - in a full implementation
        # you would blend the colors properly
        return base_color
    
    # ========== Button Components ==========
    
    def create_button(
        self, 
        style: Union[str, ComponentStyle], 
        text: str = "",
        icon: Optional[str] = None,
        on_click: Optional[Callable] = None,
        config: Optional[M3ButtonConfig] = None,
        **kwargs
    ) -> ft.Control:
        """
        Create a Material Design 3 button
        
        Args:
            style: Button style (filled, outlined, text, elevated, tonal)
            text: Button text
            icon: Button icon (ft.Icons)
            on_click: Click event handler
            config: Advanced button configuration
            **kwargs: Additional Flet button properties
        
        Returns:
            ft.Control: M3 compliant button
        """
        if isinstance(style, str):
            style = ComponentStyle(style)
        
        # Merge configuration
        if config is None:
            config = M3ButtonConfig(style=style, text=text, icon=icon, on_click=on_click)
        
        # Determine button type and styling based on M3 spec
        is_dark = self.theme_system.current_mode == ThemeMode.DARK if self.theme_system else False
        
        if style == ComponentStyle.FILLED:
            return self._create_filled_button(config, is_dark, **kwargs)
        elif style == ComponentStyle.OUTLINED:
            return self._create_outlined_button(config, is_dark, **kwargs)
        elif style == ComponentStyle.TEXT:
            return self._create_text_button(config, is_dark, **kwargs)
        elif style == ComponentStyle.ELEVATED:
            return self._create_elevated_button(config, is_dark, **kwargs)
        elif style == ComponentStyle.TONAL:
            return self._create_tonal_button(config, is_dark, **kwargs)
        else:
            logger.warning(f"Unknown button style: {style}, falling back to filled")
            return self._create_filled_button(config, is_dark, **kwargs)
    
    def _create_filled_button(self, config: M3ButtonConfig, is_dark: bool, **kwargs) -> ft.FilledButton:
        """Create M3 filled button"""
        button = ft.FilledButton(
            text=config.text,
            icon=config.icon,
            on_click=config.on_click,
            disabled=config.disabled,
            **kwargs
        )
        
        # Apply M3 styling (compatible with current Flet version)
        if not config.custom_colors:
            button.style = ft.ButtonStyle(
                bgcolor=self._resolve_color(ColorRole.PRIMARY, is_dark),
                color=self._resolve_color(ColorRole.ON_PRIMARY, is_dark),
                shape=ft.RoundedRectangleBorder(radius=BUTTON_TOKENS["border_radius"])
            )
        
        return self._apply_responsive_sizing(button, config)
    
    def _create_outlined_button(self, config: M3ButtonConfig, is_dark: bool, **kwargs) -> ft.OutlinedButton:
        """Create M3 outlined button"""
        button = ft.OutlinedButton(
            text=config.text,
            icon=config.icon,
            on_click=config.on_click,
            disabled=config.disabled,
            **kwargs
        )
        
        # Apply M3 styling (compatible with current Flet version)
        button.style = ft.ButtonStyle(
            bgcolor=None,
            color=self._resolve_color(ColorRole.PRIMARY, is_dark),
            side=ft.BorderSide(
                width=1, 
                color=self._resolve_color(ColorRole.OUTLINE, is_dark)
            ),
            shape=ft.RoundedRectangleBorder(radius=BUTTON_TOKENS["border_radius"])
        )
        
        return self._apply_responsive_sizing(button, config)
    
    def _create_text_button(self, config: M3ButtonConfig, is_dark: bool, **kwargs) -> ft.TextButton:
        """Create M3 text button"""
        button = ft.TextButton(
            text=config.text,
            icon=config.icon,
            on_click=config.on_click,
            disabled=config.disabled,
            **kwargs
        )
        
        # Apply M3 styling (compatible with current Flet version)
        button.style = ft.ButtonStyle(
            color=self._resolve_color(ColorRole.PRIMARY, is_dark),
            shape=ft.RoundedRectangleBorder(radius=BUTTON_TOKENS["border_radius"])
        )
        
        return self._apply_responsive_sizing(button, config)
    
    def _create_elevated_button(self, config: M3ButtonConfig, is_dark: bool, **kwargs) -> ft.ElevatedButton:
        """Create M3 elevated button"""
        button = ft.ElevatedButton(
            text=config.text,
            icon=config.icon,
            on_click=config.on_click,
            disabled=config.disabled,
            **kwargs
        )
        
        # Apply M3 styling (compatible with current Flet version)
        button.style = ft.ButtonStyle(
            bgcolor=self._resolve_color(ColorRole.SURFACE, is_dark),
            color=self._resolve_color(ColorRole.PRIMARY, is_dark),
            elevation=1,
            shadow_color=self._resolve_color(ColorRole.SHADOW, is_dark),
            shape=ft.RoundedRectangleBorder(radius=BUTTON_TOKENS["border_radius"])
        )
        
        return self._apply_responsive_sizing(button, config)
    
    def _create_tonal_button(self, config: M3ButtonConfig, is_dark: bool, **kwargs) -> ft.FilledButton:
        """Create M3 filled tonal button (using FilledTonalButton when available)"""
        # Note: Flet may not have FilledTonalButton yet, so we simulate with FilledButton
        button = ft.FilledButton(
            text=config.text,
            icon=config.icon,
            on_click=config.on_click,
            disabled=config.disabled,
            **kwargs
        )
        
        # Apply M3 tonal styling (secondary container colors)
        button.style = ft.ButtonStyle(
            bgcolor=self._resolve_color(ColorRole.SECONDARY_CONTAINER, is_dark),
            color=self._resolve_color(ColorRole.ON_SECONDARY_CONTAINER, is_dark),
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=BUTTON_TOKENS["border_radius"])
        )
        
        return self._apply_responsive_sizing(button, config)
    
    def _apply_responsive_sizing(self, button: ft.Control, config: M3ButtonConfig) -> ft.Control:
        """Apply responsive sizing to button"""
        if not config.responsive:
            return button
        
        # Apply size-based styling
        if config.size == "small":
            button.height = 32
        elif config.size == "large":
            button.height = 48
        else:  # medium (default)
            button.height = BUTTON_TOKENS["height"]
        
        if config.full_width:
            button.expand = True
        
        if config.min_width:
            button.width = max(button.width or 0, config.min_width)
        
        return button
    
    # ========== Card Components ==========
    
    def create_card(
        self,
        style: Union[str, ComponentStyle],
        content: Optional[ft.Control] = None,
        title: Optional[str] = None,
        config: Optional[M3CardConfig] = None,
        **kwargs
    ) -> ft.Card:
        """
        Create a Material Design 3 card
        
        Args:
            style: Card style (elevated, filled, outlined)
            content: Card content control
            title: Optional card title
            config: Advanced card configuration
            **kwargs: Additional Flet card properties
        
        Returns:
            ft.Card: M3 compliant card
        """
        # Handle string conversion for cards
        if isinstance(style, str):
            if style == "elevated" or style not in ["filled", "outlined"]:
                style = ComponentStyle.ELEVATED_CARD
            elif style == "filled":
                style = ComponentStyle.FILLED_CARD
            else:
                style = ComponentStyle.OUTLINED_CARD
        if config is None:
            config = M3CardConfig(style=style, content=content, title=title)

        is_dark = self.theme_system.current_mode == ThemeMode.DARK if self.theme_system else False

        if style == ComponentStyle.ELEVATED_CARD:
            return self._create_elevated_card(config, is_dark, **kwargs)
        elif style == ComponentStyle.FILLED_CARD:
            return self._create_filled_card(config, is_dark, **kwargs)
        elif style == ComponentStyle.OUTLINED_CARD:
            return self._create_outlined_card(config, is_dark, **kwargs)
        else:
            logger.warning(f"Unknown card style: {style}, falling back to elevated")
            return self._create_elevated_card(config, is_dark, **kwargs)
    
    def _create_elevated_card(self, config: M3CardConfig, is_dark: bool, **kwargs) -> ft.Card:
        """Create M3 elevated card"""
        # Build card content
        content = self._build_card_content(config)
        
        card = ft.Card(
            content=content,
            elevation=config.elevation or get_elevation_token("level1"),
            color=self._resolve_color(ColorRole.SURFACE, is_dark),
            **kwargs
        )
        
        # Apply M3 styling
        card.surface_tint_color = self._resolve_color(ColorRole.PRIMARY, is_dark)
        
        return self._apply_card_responsiveness(card, config)
    
    def _create_filled_card(self, config: M3CardConfig, is_dark: bool, **kwargs) -> ft.Card:
        """Create M3 filled card"""
        content = self._build_card_content(config)
        
        card = ft.Card(
            content=content,
            elevation=0,
            color=self._resolve_color(ColorRole.SURFACE_VARIANT, is_dark),
            **kwargs
        )
        
        return self._apply_card_responsiveness(card, config)
    
    def _create_outlined_card(self, config: M3CardConfig, is_dark: bool, **kwargs) -> ft.Container:
        """Create M3 outlined card (using Container with border)"""
        content = self._build_card_content(config)
        
        # Wrap in container to provide border
        card = ft.Container(
            content=content,
            bgcolor=self._resolve_color(ColorRole.SURFACE, is_dark),
            border=ft.border.all(
                1, self._resolve_color(ColorRole.OUTLINE_VARIANT, is_dark)
            ),
            border_radius=CARD_TOKENS["border_radius"],
            padding=config.padding or CARD_TOKENS["padding"],
            **kwargs
        )
        
        return self._apply_card_responsiveness(card, config)
    
    def _build_card_content(self, config: M3CardConfig) -> ft.Control:
        """Build card content with title, subtitle, and actions"""
        elements = []
        
        # Add title if provided
        if config.title:
            title_text = ft.Text(
                config.title,
                size=get_typography_token(TypographyRole.TITLE_LARGE)["font_size"],
                weight=get_typography_token(TypographyRole.TITLE_LARGE)["font_weight"]
            )
            elements.append(title_text)
        
        # Add subtitle if provided  
        if config.subtitle:
            subtitle_text = ft.Text(
                config.subtitle,
                size=get_typography_token(TypographyRole.BODY_MEDIUM)["font_size"],
                weight=get_typography_token(TypographyRole.BODY_MEDIUM)["font_weight"]
            )
            elements.append(subtitle_text)
        
        # Add main content
        if config.content:
            elements.append(config.content)
        
        # Add actions if provided
        if config.actions:
            action_row = ft.Row(
                controls=config.actions,
                alignment=ft.MainAxisAlignment.END,
                spacing=get_spacing_token("sm")
            )
            elements.append(action_row)
        
        # Return content in a column
        if len(elements) == 1:
            return elements[0]
        
        return ft.Column(
            controls=elements,
            spacing=get_spacing_token("md"),
            expand=True
        )
    
    def _apply_card_responsiveness(self, card: ft.Control, config: M3CardConfig) -> ft.Control:
        """Apply responsive design to card"""
        if config.responsive:
            card.expand = True
        
        if config.min_width and hasattr(card, 'width'):
            card.width = max(card.width or 0, config.min_width)
        
        if config.max_width and hasattr(card, 'width'):
            card.width = min(card.width or config.max_width, config.max_width)
        
        return card
    
    # ========== Input Components ==========
    
    def create_text_field(
        self,
        label: str,
        hint_text: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs
    ) -> ft.TextField:
        """Create M3 compliant text field"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK
        
        field = ft.TextField(
            label=label,
            hint_text=hint_text,
            value=value,
            border_radius=BORDER_RADIUS_TOKENS["sm"],
            **kwargs
        )
        
        # Apply M3 styling
        field.bgcolor = self._resolve_color(ColorRole.SURFACE_VARIANT, is_dark)
        field.border_color = self._resolve_color(ColorRole.OUTLINE, is_dark)
        field.focused_border_color = self._resolve_color(ColorRole.PRIMARY, is_dark)
        
        return field
    
    def create_dropdown(
        self,
        label: str,
        options: List[ft.dropdown.Option],
        value: Optional[str] = None,
        **kwargs
    ) -> ft.Dropdown:
        """Create M3 compliant dropdown"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK
        
        dropdown = ft.Dropdown(
            label=label,
            options=options,
            value=value,
            border_radius=BORDER_RADIUS_TOKENS["sm"],
            **kwargs
        )
        
        # Apply M3 styling
        dropdown.bgcolor = self._resolve_color(ColorRole.SURFACE_VARIANT, is_dark)
        dropdown.border_color = self._resolve_color(ColorRole.OUTLINE, is_dark)
        dropdown.focused_border_color = self._resolve_color(ColorRole.PRIMARY, is_dark)
        
        return dropdown
    
    def create_checkbox(
        self,
        label: Optional[str] = None,
        value: Optional[bool] = None,
        **kwargs
    ) -> ft.Control:
        """Create M3 compliant checkbox"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK
        
        checkbox = ft.Checkbox(
            value=value,
            **kwargs
        )
        
        # Apply M3 styling
        checkbox.fill_color = self._resolve_color(ColorRole.PRIMARY, is_dark)
        checkbox.check_color = self._resolve_color(ColorRole.ON_PRIMARY, is_dark)
        
        if label:
            return ft.Row([
                checkbox,
                ft.Text(
                    label,
                    size=get_typography_token(TypographyRole.BODY_MEDIUM)["font_size"]
                )
            ], spacing=get_spacing_token("sm"))
        
        return checkbox
    
    def create_switch(
        self,
        label: Optional[str] = None,
        value: Optional[bool] = None,
        **kwargs
    ) -> ft.Control:
        """Create M3 compliant switch"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK
        
        switch = ft.Switch(
            value=value,
            **kwargs
        )
        
        # Apply M3 styling (when Flet supports it)
        switch.active_color = self._resolve_color(ColorRole.PRIMARY, is_dark)
        if hasattr(switch, 'inactive_color'):
            switch.inactive_color = self._resolve_color(ColorRole.OUTLINE, is_dark)
        
        if label:
            return ft.Row([
                ft.Text(
                    label,
                    size=get_typography_token(TypographyRole.BODY_MEDIUM)["font_size"]
                ),
                switch
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        return switch
    
    # ========== Data Display Components ==========
    
    def create_data_table(
        self,
        columns: List[ft.DataColumn],
        rows: List[ft.DataRow],
        **kwargs
    ) -> ft.DataTable:
        """Create M3 compliant data table"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK
        
        table = ft.DataTable(
            columns=columns,
            rows=rows,
            border_radius=BORDER_RADIUS_TOKENS["md"],
            **kwargs
        )
        
        # Apply M3 styling
        table.bgcolor = self._resolve_color(ColorRole.SURFACE, is_dark)
        table.border = ft.border.all(
            1, self._resolve_color(ColorRole.OUTLINE_VARIANT, is_dark)
        )
        table.heading_row_color = self._resolve_color(ColorRole.SURFACE_VARIANT, is_dark)
        
        return table
    
    def create_list_tile(
        self,
        title: str,
        subtitle: Optional[str] = None,
        leading: Optional[ft.Control] = None,
        trailing: Optional[ft.Control] = None,
        **kwargs
    ) -> ft.ListTile:
        """Create M3 compliant list tile"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK

        return ft.ListTile(
            title=ft.Text(
                title,
                size=get_typography_token(TypographyRole.BODY_LARGE)["font_size"],
            ),
            subtitle=(
                ft.Text(
                    subtitle,
                    size=get_typography_token(TypographyRole.BODY_MEDIUM)[
                        "font_size"
                    ],
                )
                if subtitle
                else None
            ),
            leading=leading,
            trailing=trailing,
            **kwargs
        )
    
    # ========== Navigation Components ==========
    
    def create_navigation_rail(
        self,
        destinations: List[ft.NavigationRailDestination],
        selected_index: int = 0,
        **kwargs
    ) -> ft.NavigationRail:
        """Create M3 compliant navigation rail"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK

        return ft.NavigationRail(
            destinations=destinations,
            selected_index=selected_index,
            bgcolor=self._resolve_color(ColorRole.SURFACE, is_dark),
            **kwargs
        )
    
    # ========== Utility Methods ==========
    
    def create_component_theme(self, base_color: str = None) -> Dict[str, Any]:
        """Create a component theme configuration"""
        is_dark = self.theme_system.current_mode == ThemeMode.DARK
        
        return {
            "primary": base_color or self._resolve_color(ColorRole.PRIMARY, is_dark),
            "surface": self._resolve_color(ColorRole.SURFACE, is_dark),
            "background": self._resolve_color(ColorRole.SURFACE, is_dark),
            "error": self._resolve_color(ColorRole.ERROR, is_dark),
        }
    
    def apply_m3_elevation(self, control: ft.Control, level: str = "level1") -> ft.Control:
        """Apply M3 elevation to any control that supports it"""
        if hasattr(control, 'elevation'):
            control.elevation = get_elevation_token(level)
        
        if hasattr(control, 'shadow_color'):
            is_dark = self.theme_system.current_mode == ThemeMode.DARK
            control.shadow_color = self._resolve_color(ColorRole.SHADOW, is_dark)
        
        return control
    
    def apply_m3_shape(self, control: ft.Control, corner_radius: str = "md") -> ft.Control:
        """Apply M3 shape system to any control"""
        radius = BORDER_RADIUS_TOKENS.get(corner_radius, BORDER_RADIUS_TOKENS["md"])
        
        if hasattr(control, 'border_radius'):
            control.border_radius = radius
        elif hasattr(control, 'shape'):
            control.shape = ft.RoundedRectangleBorder(radius=radius)
        
        return control


# Global component factory instance
_component_factory = None

def get_m3_factory() -> M3ComponentFactory:
    """Get the global M3 component factory instance"""
    global _component_factory
    if _component_factory is None:
        _component_factory = M3ComponentFactory()
    return _component_factory


# Convenience functions for easy component creation
def create_m3_button(style: str, text: str = "", **kwargs) -> ft.Control:
    """Convenience function for creating M3 buttons"""
    return get_m3_factory().create_button(style, text, **kwargs)

def create_m3_card(style: str, content: ft.Control = None, **kwargs) -> ft.Control:
    """Convenience function for creating M3 cards"""
    return get_m3_factory().create_card(style, content, **kwargs)

def create_m3_text_field(label: str, **kwargs) -> ft.TextField:
    """Convenience function for creating M3 text fields"""
    return get_m3_factory().create_text_field(label, **kwargs)

def create_m3_data_table(columns: List[ft.DataColumn], rows: List[ft.DataRow], **kwargs) -> ft.DataTable:
    """Convenience function for creating M3 data tables"""
    return get_m3_factory().create_data_table(columns, rows, **kwargs)


# Export all public components and functions
__all__ = [
    'M3ComponentFactory',
    'ComponentStyle',
    'StateLayer',
    'M3ComponentConfig',
    'M3ButtonConfig',
    'M3CardConfig',
    'get_m3_factory',
    'create_m3_button',
    'create_m3_card', 
    'create_m3_text_field',
    'create_m3_data_table',
]