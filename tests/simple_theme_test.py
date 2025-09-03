#!/usr/bin/env python3
"""
Simple Theme Test
Basic test to verify theme loading.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '.')

try:
    # Import the custom theme
    from flet_server_gui.ui.theme_m3 import TOKENS
    print("Theme loaded successfully!")
    print(f"Primary color: {TOKENS.get('primary')}")
    print(f"Secondary color (should be orange): {TOKENS.get('secondary')}")
    print(f"Tertiary color: {TOKENS.get('tertiary')}")
    print("\nAll theme tokens:")
    for key, value in TOKENS.items():
        print(f"  {key}: {value}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()