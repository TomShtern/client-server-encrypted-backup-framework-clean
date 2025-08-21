"""
Material Design 3 TextField Adapter
Token-driven text field implementation enforcing M3 specifications
"""

from typing import Optional
from kivy.metrics import dp
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, BooleanProperty

from .token_loader import TokenLoader, hex_to_rgba, get_token_value


class MD3TextField(MDTextField):
    """
    Material Design 3 TextField adapter enforcing design tokens
    
    Modes:
    - outlined (default): Outlined text field
    - filled: Filled text field with background
    """
    
    field_mode = StringProperty("outlined")
    error_state = BooleanProperty(False)
    
    def __init__(self, field_mode: str = "outlined", helper_text: str = "", 
                 error_text: str = "", **kwargs):
        
        # Load tokens first
        self.tokens = TokenLoader().tokens
        self.field_mode = field_mode
        self.helper_text = helper_text
        self.error_text = error_text
        
        # Initialize with token-derived properties
        super().__init__(**kwargs)
        
        # Apply M3 specifications from tokens
        self._apply_token_styling()
        
        # Bind property changes
        self.bind(field_mode=lambda x, y: self._apply_token_styling())
        self.bind(error_state=lambda x, y: self._apply_error_styling())
    
    def _apply_token_styling(self):
        """Apply Material Design 3 text field styling from design tokens"""
        # Text field geometry from tokens
        textfield_tokens = get_token_value('component_tokens.text_field', {})
        palette = get_token_value('palette', {})
        typography = get_token_value('typography', {})
        
        # Apply dimensions from tokens
        self.size_hint_y = None
        self.height = dp(get_token_value('component_tokens.text_field.height', 56))
        
        # Apply padding from tokens
        padding_h = get_token_value('component_tokens.text_field.padding_horizontal', 16)
        padding_v = get_token_value('component_tokens.text_field.padding_vertical', 8)
        
        # Apply radius based on mode
        if self.field_mode == "outlined":
            self.mode = "outlined"
            self.radius = [get_token_value('component_tokens.text_field.radius', 4)]
        else:  # filled
            self.mode = "filled"
            self.radius = [
                get_token_value('component_tokens.text_field.radius', 4),
                get_token_value('component_tokens.text_field.radius', 4),
                0, 0  # Bottom corners square for filled mode
            ]
        
        # Apply typography from tokens
        body_large = typography.get('body_large', {})
        self.font_size = f"{body_large.get('size', 16)}sp"
        
        # Apply colors from design tokens
        self._apply_color_scheme()
    
    def _apply_color_scheme(self):
        """Apply color scheme from design tokens"""
        palette = get_token_value('palette', {})
        
        # Text colors
        self.theme_text_color = "Custom"
        self.text_color_normal = hex_to_rgba(palette.get('on_surface', '#E1E2E8'))
        self.text_color_focus = hex_to_rgba(palette.get('on_surface', '#E1E2E8'))
        
        # Hint text color
        self.hint_text_color_normal = hex_to_rgba(palette.get('on_surface_variant', '#C2C7CF'))
        self.hint_text_color_focus = hex_to_rgba(palette.get('on_surface_variant', '#C2C7CF'))
        
        # Line colors for outlined mode
        if self.field_mode == "outlined":
            self.line_color_normal = hex_to_rgba(palette.get('outline', '#8C9199'))
            self.line_color_focus = hex_to_rgba(palette.get('primary', '#1976D2'))
        else:  # filled mode
            self.fill_color_normal = hex_to_rgba(palette.get('surface_variant', '#42474E'), 0.12)
            self.fill_color_focus = hex_to_rgba(palette.get('surface_variant', '#42474E'), 0.16)
            self.line_color_focus = hex_to_rgba(palette.get('primary', '#1976D2'))
    
    def _apply_error_styling(self):
        """Apply error state styling"""
        if self.error_state:
            palette = get_token_value('palette', {})
            error_color = palette.get('error', '#BA1A1A')
            
            self.error = True
            self.line_color_focus = hex_to_rgba(error_color)
            self.hint_text_color_focus = hex_to_rgba(error_color)
            
            if self.error_text:
                self.helper_text = self.error_text
                self.helper_text_mode = "on_error"
        else:
            self.error = False
            self._apply_color_scheme()  # Reset to normal colors
            if hasattr(self, 'original_helper_text'):
                self.helper_text = self.original_helper_text
    
    def set_error(self, error_message: str = ""):
        """Set error state with optional error message"""
        self.error_state = True
        if error_message:
            if not hasattr(self, 'original_helper_text'):
                self.original_helper_text = self.helper_text
            self.error_text = error_message
            self._apply_error_styling()
    
    def clear_error(self):
        """Clear error state"""
        self.error_state = False
        self._apply_error_styling()


class MD3SearchField(MD3TextField):
    """Material Design 3 Search Field with search-specific styling"""
    
    def __init__(self, **kwargs):
        super().__init__(
            field_mode="filled",
            hint_text="Search...",
            **kwargs
        )
        
        # Search field specific styling
        self.radius = [dp(get_token_value('shape.corner_extra_large', 28))]  # Fully rounded
        self.size_hint_y = None
        self.height = dp(48)  # Slightly smaller than standard text field


class MD3NumberField(MD3TextField):
    """Material Design 3 Number Field with numeric input validation"""
    
    def __init__(self, min_value: Optional[float] = None, 
                 max_value: Optional[float] = None, **kwargs):
        
        self.min_value = min_value
        self.max_value = max_value
        
        super().__init__(
            input_filter="float",
            **kwargs
        )
        
        # Bind text changes for validation
        self.bind(text=self._validate_number)
    
    def _validate_number(self, instance, value):
        """Validate numeric input against min/max constraints"""
        if not value:
            return
        
        try:
            num_value = float(value)
            
            # Check min/max constraints
            if self.min_value is not None and num_value < self.min_value:
                self.set_error(f"Value must be at least {self.min_value}")
                return
            
            if self.max_value is not None and num_value > self.max_value:
                self.set_error(f"Value must be at most {self.max_value}")
                return
            
            # Clear error if validation passes
            self.clear_error()
            
        except ValueError:
            self.set_error("Please enter a valid number")


# Factory functions
def create_md3_textfield(hint_text: str = "", field_mode: str = "outlined", 
                        helper_text: str = "", **kwargs) -> MD3TextField:
    """Factory function to create M3-compliant text fields"""
    return MD3TextField(
        hint_text=hint_text,
        field_mode=field_mode,
        helper_text=helper_text,
        **kwargs
    )


def create_search_field(hint_text: str = "Search...", **kwargs) -> MD3SearchField:
    """Factory function to create M3-compliant search fields"""
    return MD3SearchField(hint_text=hint_text, **kwargs)


def create_number_field(hint_text: str = "", min_value: Optional[float] = None,
                       max_value: Optional[float] = None, **kwargs) -> MD3NumberField:
    """Factory function to create M3-compliant number fields"""
    return MD3NumberField(
        hint_text=hint_text,
        min_value=min_value,
        max_value=max_value,
        **kwargs
    )