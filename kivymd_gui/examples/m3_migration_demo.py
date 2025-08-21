"""
Material Design 3 Migration Demonstration
Shows before/after examples of migrating KivyMD components to M3 adapters
"""

import sys
import os

# Add project root to path  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    # Import M3 adapters
    from kivymd_gui.components import (
        create_md3_button, create_md3_card, create_md3_textfield,
        get_token_value, MD3Button, MD3Card
    )
    
    # Import KivyMD for comparison
    from kivymd.uix.button import MDIconButton, MDButton
    from kivymd.uix.card import MDCard as OriginalMDCard
    from kivymd.uix.textfield import MDTextField
    
    print("SUCCESS: All imports loaded successfully")
    
    # Demonstrate token access
    primary_color = get_token_value('palette.primary')
    corner_radius = get_token_value('shape.corner_medium')
    button_height = get_token_value('component_tokens.button.height')
    
    print(f"Token Values:")
    print(f"  Primary Color: {primary_color}")
    print(f"  Corner Radius: {corner_radius}dp")
    print(f"  Button Height: {button_height}dp")
    print()
    
    # Example 1: Button Migration
    print("BEFORE (Raw KivyMD):")
    print("  button = MDButton(text='Save')")
    print("  # Manual styling required")
    print()
    
    print("AFTER (M3 Adapter):")
    print("  button = create_md3_button('Save', variant='filled', tone='primary')")
    print("  # Automatic token styling applied")
    print()
    
    # Example 2: Card Migration  
    print("BEFORE (Raw KivyMD):")
    print("  card = MDCard(radius=[12], padding=[16])")
    print("  # Hardcoded values")
    print()
    
    print("AFTER (M3 Adapter):")
    print("  card = create_md3_card(variant='elevated')")
    print("  # Token-driven styling")
    print()
    
    # Example 3: Component Factory Usage
    print("Component Factory Usage:")
    print("  from kivymd_gui.components import get_component_factory")
    print("  button_factory = get_component_factory('button')")
    print("  card_factory = get_component_factory('card')")
    print()
    
    # Migration Statistics
    print("MIGRATION BENEFITS:")
    print("  * Token-driven styling (consistent design)")
    print("  * WCAG accessibility compliance")
    print("  * Responsive design (automatic scaling)")
    print("  * Semantic component variants")
    print("  * Reduced maintenance overhead")
    print("  * Professional M3 compliance")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the correct virtual environment")

if __name__ == "__main__":
    print("Material Design 3 Migration Demo")
    print("=" * 50)