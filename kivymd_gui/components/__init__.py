"""
Material Design 3 Component Adapters
Token-driven KivyMD component wrappers enforcing M3 design specifications
"""

# Core token system
from .token_loader import TokenLoader, token_loader, get_token_value, hex_to_rgba

# M3 Component adapters
from .md3_button import MD3Button, MD3IconButton, create_md3_button
from .md3_card import MD3Card, MD3StatusCard, create_md3_card, create_status_card
from .md3_textfield import (
    MD3TextField, MD3SearchField, MD3NumberField,
    create_md3_textfield, create_search_field, create_number_field
)

# Legacy components (for backward compatibility)  
try:
    from .status_card import MDStatusCard, StatusCard
except ImportError:
    pass  # Skip if not available
try:
    from .charts import *
except ImportError:
    pass  # Skip if not available

__all__ = [
    # Token system
    'TokenLoader', 'token_loader', 'get_token_value', 'hex_to_rgba',
    
    # M3 Adapters
    'MD3Button', 'MD3IconButton', 'create_md3_button',
    'MD3Card', 'MD3StatusCard', 'create_md3_card', 'create_status_card',
    'MD3TextField', 'MD3SearchField', 'MD3NumberField',
    'create_md3_textfield', 'create_search_field', 'create_number_field',
    
    # Legacy components (temporarily disabled)
    # 'MDStatusCard', 'StatusCard'
]


def validate_token_system():
    """Validate that the token system is properly loaded and functional"""
    try:
        loader = TokenLoader()
        tokens = loader.tokens
        
        # Check essential token categories
        required_categories = ['palette', 'shape', 'elevation', 'typography', 'motion', 'spacing']
        missing_categories = [cat for cat in required_categories if cat not in tokens]
        
        if missing_categories:
            print(f"[WARNING] Missing token categories: {missing_categories}")
            return False
        
        # Validate essential color tokens
        palette = tokens.get('palette', {})
        essential_colors = ['primary', 'on_primary', 'surface', 'on_surface']
        missing_colors = [color for color in essential_colors if color not in palette]
        
        if missing_colors:
            print(f"[WARNING] Missing essential color tokens: {missing_colors}")
            return False
        
        print("[INFO] Token system validation passed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Token system validation failed: {e}")
        return False


def get_component_factory(component_type: str):
    """
    Get factory function for creating M3 components
    
    Args:
        component_type: Type of component ('button', 'card', 'textfield', etc.)
        
    Returns:
        Factory function for the component type
    """
    factories = {
        'button': create_md3_button,
        'card': create_md3_card,
        'status_card': create_status_card,
        'textfield': create_md3_textfield,
        'search_field': create_search_field,
        'number_field': create_number_field,
    }
    
    return factories.get(component_type)


# Auto-validate token system on import
validate_token_system()