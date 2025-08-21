"""
Material Design 3 Button Adapter
Token-driven button implementation enforcing M3 specifications
"""

from typing import Dict, Any, Optional
from kivy.metrics import dp
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivy.properties import StringProperty, NumericProperty

from .token_loader import TokenLoader, hex_to_rgba, get_token_value


class MD3Button(MDButton):
    """
    Material Design 3 Button adapter enforcing design tokens
    
    Variants:
    - filled (default): Filled button with primary color
    - tonal: Filled button with secondary color container
    - outlined: Outlined button with border
    - text: Text-only button
    - elevated: Elevated filled button
    """
    
    variant = StringProperty("filled")
    tone = StringProperty("primary")  # primary, secondary, tertiary, error
    
    def __init__(self, text: str = "", variant: str = "filled", tone: str = "primary", **kwargs):
        # Load tokens first
        self.tokens = TokenLoader().tokens
        
        # Set variant and tone
        self.variant = variant
        self.tone = tone
        
        # Initialize with token-derived properties (no text parameter for MDButton)
        text_content = kwargs.pop('text', text)
        super().__init__(**kwargs)
        
        # Add text component using KivyMD 2.0.x pattern
        if text_content:
            button_text = MDButtonText(text=text_content)
            self.add_widget(button_text)
        
        # Apply M3 specifications from tokens
        self._apply_token_styling()
        
        # Bind property changes to update styling
        self.bind(variant=lambda x, y: self._apply_token_styling())
        self.bind(tone=lambda x, y: self._apply_token_styling())
    
    def _apply_token_styling(self):
        """Apply Material Design 3 styling from design tokens"""
        # Button geometry from tokens
        button_tokens = get_token_value('component_tokens.button', {})
        
        self.radius = [get_token_value('component_tokens.button.radius', 20)]
        self.size_hint_y = None
        self.height = dp(get_token_value('component_tokens.button.height', 40))
        
        # Apply padding from tokens
        padding_h = get_token_value('component_tokens.button.padding_horizontal', 24)
        padding_v = get_token_value('component_tokens.button.padding_vertical', 8)
        
        # Apply minimum width
        min_width = get_token_value('component_tokens.button.min_width', 64)
        if self.size_hint_x is None:
            self.width = max(self.width, dp(min_width))
        
        # Apply elevation from tokens
        elevation_tokens = get_token_value('elevation', {})
        
        # Apply color scheme based on variant and tone
        self._apply_color_scheme()
        
        # Apply elevation based on variant
        if self.variant == "elevated":
            self.elevation = elevation_tokens.get('level1', 1)
        elif self.variant in ["filled", "tonal"]:
            self.elevation = 0
        else:  # outlined, text
            self.elevation = 0
    
    def _apply_color_scheme(self):
        """Apply color scheme based on variant and tone using design tokens"""
        palette = get_token_value('palette', {})
        
        # Determine base colors from tone
        if self.tone == "primary":
            main_color = palette.get('primary', '#1976D2')
            on_color = palette.get('on_primary', '#FFFFFF')
            container_color = palette.get('primary_container', '#D1E4FF')
            on_container = palette.get('on_primary_container', '#001D36')
        elif self.tone == "secondary":
            main_color = palette.get('secondary', '#535F70')
            on_color = palette.get('on_secondary', '#FFFFFF')
            container_color = palette.get('secondary_container', '#D7E3F7')
            on_container = palette.get('on_secondary_container', '#101C2B')
        elif self.tone == "error":
            main_color = palette.get('error', '#BA1A1A')
            on_color = palette.get('on_error', '#FFFFFF')
            container_color = palette.get('error_container', '#FFDAD6')
            on_container = palette.get('on_error_container', '#410002')
        else:  # tertiary or fallback
            main_color = palette.get('tertiary', '#6B5778')
            on_color = palette.get('on_tertiary', '#FFFFFF')
            container_color = palette.get('tertiary_container', '#F2DAFF')
            on_container = palette.get('on_tertiary_container', '#251432')
        
        # Apply colors based on variant
        if self.variant == "filled":
            self.md_bg_color = hex_to_rgba(main_color)
            self._apply_text_color(hex_to_rgba(on_color))
            
        elif self.variant == "tonal":
            self.md_bg_color = hex_to_rgba(container_color)
            self._apply_text_color(hex_to_rgba(on_container))
            
        elif self.variant == "outlined":
            self.md_bg_color = (0, 0, 0, 0)  # Transparent
            self._apply_text_color(hex_to_rgba(main_color))
            # Note: KivyMD button border would need custom implementation
            
        elif self.variant == "text":
            self.md_bg_color = (0, 0, 0, 0)  # Transparent
            self._apply_text_color(hex_to_rgba(main_color))
            
        elif self.variant == "elevated":
            self.md_bg_color = hex_to_rgba(container_color)
            self._apply_text_color(hex_to_rgba(on_container))
    
    def _apply_text_color(self, color):
        """Apply text color to MDButtonText component"""
        # Find MDButtonText child and set its color
        for child in self.children:
            if isinstance(child, MDButtonText):
                child.theme_text_color = "Custom"
                child.text_color = color
                break


class MD3IconButton(MDIconButton):
    """Material Design 3 Icon Button adapter"""
    
    tone = StringProperty("primary")
    
    def __init__(self, tone: str = "primary", **kwargs):
        self.tokens = TokenLoader().tokens
        self.tone = tone
        
        super().__init__(**kwargs)
        
        # Apply M3 icon button specifications
        self.size_hint = (None, None)
        self.size = (dp(48), dp(48))  # M3 touch target minimum
        self.radius = [dp(24)]  # Fully rounded
        
        self._apply_color_scheme()
    
    def _apply_color_scheme(self):
        """Apply color scheme from design tokens"""
        palette = get_token_value('palette', {})
        
        if self.tone == "primary":
            icon_color = palette.get('primary', '#1976D2')
        elif self.tone == "secondary":
            icon_color = palette.get('secondary', '#535F70')
        elif self.tone == "error":
            icon_color = palette.get('error', '#BA1A1A')
        else:
            icon_color = palette.get('on_surface', '#E1E2E8')
        
        self.theme_icon_color = "Custom"
        self.icon_color = hex_to_rgba(icon_color)


# Factory function for creating buttons with proper typing
def create_md3_button(text: str = "", variant: str = "filled", tone: str = "primary", **kwargs) -> MD3Button:
    """
    Factory function to create M3-compliant buttons
    
    Args:
        text: Button text
        variant: Button variant (filled, tonal, outlined, text, elevated)
        tone: Color tone (primary, secondary, tertiary, error)
        **kwargs: Additional KivyMD button properties
        
    Returns:
        Configured MD3Button instance
    """
    return MD3Button(
        text=text,
        variant=variant,
        tone=tone,
        **kwargs
    )