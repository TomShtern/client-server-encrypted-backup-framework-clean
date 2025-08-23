#!/usr/bin/env python3
"""
Test script to verify custom theme colors are applied correctly
"""
import sys
import os

# Add project root to path
sys.path.insert(0, '.')

try:
    from flet_server_gui.ui.theme_m3 import TOKENS, create_theme
    import flet as ft
    
    print("Custom theme tokens:")
    print(f"  Primary: {TOKENS.get('primary', 'Not found')}")  # Should be purple #7C5CD9
    print(f"  Secondary: {TOKENS.get('secondary', 'Not found')}")  # Should be orange #FCA651
    print(f"  Tertiary: {TOKENS.get('tertiary', 'Not found')}")  # Should be pinkish-red #AB6DA4
    print(f"  Container: {TOKENS.get('container', 'Not found')}")  # Should be teal #38A298
    
    # Test creating themes
    light_theme = create_theme(use_material3=True, dark=False)
    
    print("\nCreated light theme successfully")
    if hasattr(light_theme, 'color_scheme') and light_theme.color_scheme:
        print("Applied color scheme:")
        print(f"  Primary: {getattr(light_theme.color_scheme, 'primary', 'Not set')}")
        print(f"  Secondary: {getattr(light_theme.color_scheme, 'secondary', 'Not set')}")
        print(f"  Tertiary: {getattr(light_theme.color_scheme, 'tertiary', 'Not set')}")
        print(f"  Primary Container: {getattr(light_theme.color_scheme, 'primary_container', 'Not set')}")
        print(f"  Surface: {getattr(light_theme.color_scheme, 'surface', 'Not set')}")
    else:
        print("No color scheme found in theme")
        
    # Test if we can access the tokens directly
    print(f"\nDirect token access test:")
    print(f"  TOKENS['secondary']: {TOKENS.get('secondary', 'Not found')}")
    print(f"  TOKENS['tertiary']: {TOKENS.get('tertiary', 'Not found')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()