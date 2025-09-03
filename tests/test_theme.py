#!/usr/bin/env python3
"""
Test script to verify custom theme colors
"""
import sys
import os

# Add project root to path
sys.path.insert(0, '.')

try:
    from flet_server_gui.ui.theme_m3 import TOKENS, create_theme
    print("Custom theme loaded successfully")
    print("Theme tokens:")
    for key, value in TOKENS.items():
        print(f"  {key}: {value}")
    
    # Test creating themes
    light_theme = create_theme(use_material3=True, dark=False)
    dark_theme = create_theme(use_material3=True, dark=True)
    
    print("\nLight theme color scheme:")
    if hasattr(light_theme, 'color_scheme') and light_theme.color_scheme:
        print(f"  Primary: {getattr(light_theme.color_scheme, 'primary', 'Not set')}")
        print(f"  Secondary: {getattr(light_theme.color_scheme, 'secondary', 'Not set')}")
        print(f"  Tertiary: {getattr(light_theme.color_scheme, 'tertiary', 'Not set')}")
        print(f"  Surface: {getattr(light_theme.color_scheme, 'surface', 'Not set')}")
    
    print("\nDark theme color scheme:")
    if hasattr(dark_theme, 'color_scheme') and dark_theme.color_scheme:
        print(f"  Primary: {getattr(dark_theme.color_scheme, 'primary', 'Not set')}")
        print(f"  Secondary: {getattr(dark_theme.color_scheme, 'secondary', 'Not set')}")
        print(f"  Tertiary: {getattr(dark_theme.color_scheme, 'tertiary', 'Not set')}")
        print(f"  Surface: {getattr(dark_theme.color_scheme, 'surface', 'Not set')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()