#!/usr/bin/env python3
"""
Simple debug script to check button structure
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def debug_button_structure():
    """Debug button structure"""
    print("Debugging button structure...")
    
    try:
        import flet as ft
        
        # Create a simple button
        button = ft.ElevatedButton(
            text="Test Button",
            icon=ft.Icons.INFO,
            tooltip="Test tooltip"
        )
        
        print(f"Button type: {type(button)}")
        print(f"Button attributes: {dir(button)}")
        print(f"Button on_click: {button.on_click}")
        
        # Test setting on_click
        def test_click(e):
            print("Button clicked!")
            
        button.on_click = test_click
        print(f"Button on_click after setting: {button.on_click}")
        
        # Test button factory
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
        from flet_server_gui.components.base_component import BaseComponent
        
        class MockPage:
            pass
            
        class MockBaseComponent(BaseComponent):
            def __init__(self):
                pass
                
        class MockServerBridge:
            pass
            
        mock_page = MockPage()
        mock_component = MockBaseComponent()
        mock_server_bridge = MockServerBridge()
        
        button_factory = ActionButtonFactory(mock_component, mock_server_bridge, mock_page)
        
        def get_selected_items():
            return ["item1"]
            
        # Create action button
        action_button = button_factory.create_action_button(
            "client_view_details",
            get_selected_items
        )
        
        print(f"Action button type: {type(action_button)}")
        print(f"Action button on_click: {action_button.on_click}")
        
    except Exception as e:
        print(f"[FAIL] Button structure debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_button_structure()