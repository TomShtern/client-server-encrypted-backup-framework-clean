"""
Material Design 3 Card Adapter
Token-driven card implementation enforcing M3 specifications
"""

from typing import Optional, Union
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, NumericProperty

from .token_loader import TokenLoader, hex_to_rgba, get_token_value, apply_responsive_tokens


class MD3Card(MDCard):
    """
    Material Design 3 Card adapter enforcing design tokens
    
    Variants:
    - surface (default): Standard surface card
    - elevated: Card with elevation shadow
    - outlined: Card with outline border
    - filled: Card with filled background
    """
    
    variant = StringProperty("surface")
    
    def __init__(self, variant: str = "surface", **kwargs):
        # Load tokens first
        self.tokens = TokenLoader().tokens
        self.variant = variant
        
        # Initialize with token-derived properties
        super().__init__(**kwargs)
        
        # Apply M3 specifications from tokens
        self._apply_token_styling()
        
        # Bind property changes to update styling
        self.bind(variant=lambda x, y: self._apply_token_styling())
    
    def _apply_token_styling(self):
        """Apply Material Design 3 card styling from design tokens"""
        # Card geometry from tokens
        card_tokens = get_token_value('component_tokens.card', {})
        palette = get_token_value('palette', {})
        elevation_tokens = get_token_value('elevation', {})
        
        # Apply radius from tokens
        self.radius = [dp(get_token_value('component_tokens.card.radius', 12))]
        
        # Apply padding from tokens  
        card_padding = get_token_value('component_tokens.card.padding', 24)
        self.padding = [dp(card_padding)] * 4
        
        # Apply elevation and colors based on variant
        if self.variant == "surface":
            self.elevation = 0
            self.theme_bg_color = "Custom"
            self.md_bg_color = hex_to_rgba(palette.get('surface', '#0F1419'))
            
        elif self.variant == "elevated":
            self.elevation = elevation_tokens.get('level1', 1)
            self.theme_bg_color = "Custom" 
            self.md_bg_color = hex_to_rgba(palette.get('surface', '#0F1419'))
            
        elif self.variant == "outlined":
            self.elevation = 0
            self.theme_bg_color = "Custom"
            self.md_bg_color = hex_to_rgba(palette.get('surface', '#0F1419'))
            # Note: Outline would require custom canvas implementation
            
        elif self.variant == "filled":
            self.elevation = 0
            self.theme_bg_color = "Custom"
            self.md_bg_color = hex_to_rgba(palette.get('surface_variant', '#42474E'))
        
        # Apply responsive adjustments
        self._apply_responsive_adjustments()
    
    def _apply_responsive_adjustments(self):
        """Apply responsive token adjustments based on screen size"""
        # Get screen width (this would ideally come from app context)
        # For now, using window size or a reasonable default
        from kivy.core.window import Window
        screen_width = Window.width if Window else 1200
        
        base_tokens = {
            'radius': get_token_value('component_tokens.card.radius', 12),
            'padding': get_token_value('component_tokens.card.padding', 24)
        }
        
        apply_responsive_tokens(self, base_tokens, screen_width)
    
    def update_content_padding(self, content_type: str = "default"):
        """
        Update padding based on content type for optimal M3 layout
        
        Args:
            content_type: Type of content ('default', 'dense', 'media', 'action')
        """
        spacing_tokens = get_token_value('spacing', {})
        
        if content_type == "dense":
            # Reduced padding for dense content
            self.padding = [dp(spacing_tokens.get('md', 16))] * 4
        elif content_type == "media":
            # No padding for media content (full bleed)
            self.padding = [0, 0, 0, 0]
        elif content_type == "action":
            # Action cards get standard padding with bottom margin for buttons
            base_padding = dp(spacing_tokens.get('lg', 24))
            self.padding = [base_padding, base_padding, base_padding, base_padding]
        else:
            # Default M3 card padding
            self.padding = [dp(get_token_value('component_tokens.card.padding', 24))] * 4


class MD3StatusCard(MD3Card):
    """Enhanced Material Design 3 Status Card with semantic content structure"""
    
    status_color = StringProperty("primary")
    
    def __init__(self, title: str = "", primary_text: str = "", 
                 secondary_text: str = "", icon: str = "information",
                 status_color: str = "primary", **kwargs):
        
        self.title = title
        self.primary_text = primary_text  
        self.secondary_text = secondary_text
        self.icon = icon
        self.status_color = status_color
        
        super().__init__(variant="elevated", **kwargs)
        
        # Apply status-specific styling
        self._apply_status_styling()
        self._setup_content_layout()
    
    def _apply_status_styling(self):
        """Apply status-specific styling based on status_color"""
        palette = get_token_value('palette', {})
        
        # Status indicator colors
        if self.status_color == "primary":
            accent_color = palette.get('primary', '#1976D2')
        elif self.status_color == "error":
            accent_color = palette.get('error', '#BA1A1A')
        elif self.status_color == "success":
            accent_color = palette.get('tertiary', '#6B5778')  # Using tertiary for success
        else:
            accent_color = palette.get('secondary', '#535F70')
        
        # Store accent color for use in content layout
        self.accent_color = accent_color
    
    def _setup_content_layout(self):
        """Setup the content layout with proper M3 typography"""
        # This would create the internal layout structure
        # For now, storing the content properties for external layout creation
        self.content_config = {
            'title': self.title,
            'primary_text': self.primary_text,
            'secondary_text': self.secondary_text,
            'icon': self.icon,
            'accent_color': self.accent_color
        }


# Factory functions for common card types
def create_md3_card(variant: str = "surface", **kwargs) -> MD3Card:
    """Factory function to create M3-compliant cards"""
    return MD3Card(variant=variant, **kwargs)


def create_status_card(title: str = "", primary_text: str = "", 
                      secondary_text: str = "", icon: str = "information",
                      status_color: str = "primary", **kwargs) -> MD3StatusCard:
    """Factory function to create M3-compliant status cards"""
    return MD3StatusCard(
        title=title,
        primary_text=primary_text,
        secondary_text=secondary_text,
        icon=icon,
        status_color=status_color,
        **kwargs
    )