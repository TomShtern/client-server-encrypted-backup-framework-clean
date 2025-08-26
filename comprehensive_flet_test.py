#!/usr/bin/env python3
"""
Comprehensive Flet GUI Test - Isolate and Fix Issues
This script will run through all GUI components to identify specific problems.
"""

import sys
import os
import traceback
import asyncio

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import UTF-8 solution with safe printing
safe_print = print  # Default to regular print
try:
    import Shared.utils.utf8_solution
    from Shared.utils.utf8_solution import safe_print
    safe_print("[OK] UTF-8 solution imported")
except ImportError:
    safe_print("[!] UTF-8 solution import failed - continuing anyway")

import flet as ft

def test_imports():
    """Test all critical imports for the Flet GUI."""
    safe_print("\n=== Testing Imports ===")
    
    # Test core components
    try:
        from flet_server_gui.ui.theme import ThemeManager
        safe_print("[OK] ThemeManager import successful")
    except ImportError as e:
        safe_print(f"[ERROR] ThemeManager import failed: {e}")
        return False
    
    try:
        from flet_server_gui.ui.dialogs import DialogSystem, ToastManager
        safe_print("[OK] Dialog systems import successful")
    except ImportError as e:
        safe_print(f"[ERROR] Dialog systems import failed: {e}")
        return False
    
    try:
        from flet_server_gui.ui.navigation import NavigationManager
        safe_print("[OK] NavigationManager import successful")
    except ImportError as e:
        safe_print(f"[ERROR] NavigationManager import failed: {e}")
        return False
    
    try:
        from flet_server_gui.utils.server_bridge import ServerBridge
        safe_print("[OK] ServerBridge import successful")
    except ImportError as e:
        safe_print(f"[ERROR] ServerBridge import failed: {e}")
        return False
    
    try:
        from flet_server_gui.components.control_panel_card import ControlPanelCard
        safe_print("[OK] ControlPanelCard import successful")
    except ImportError as e:
        safe_print(f"[ERROR] ControlPanelCard import failed: {e}")
        return False
    
    try:
        from flet_server_gui.views.dashboard import DashboardView
        safe_print("[OK] DashboardView import successful")
    except ImportError as e:
        safe_print(f"[ERROR] DashboardView import failed: {e}")
        return False
    
    return True

def test_server_bridge():
    """Test ServerBridge initialization in isolation."""
    safe_print("\n=== Testing ServerBridge ===")
    
    try:
        from flet_server_gui.utils.server_bridge import ServerBridge
        
        # Try to create ServerBridge without server instance (mock mode)
        try:
            bridge = ServerBridge(server_instance=None)
            safe_print("[OK] ServerBridge created in mock mode")
            return bridge
        except Exception as e:
            safe_print(f"[ERROR] ServerBridge creation failed: {e}")
            
            # Try creating a minimal mock instead
            class MockServerBridge:
                def __init__(self):
                    self.mock_mode = True
                    
                async def get_server_status(self):
                    return type('ServerInfo', (), {
                        'running': False,
                        'host': 'localhost',
                        'port': 1256,
                        'connected_clients': 0,
                        'total_clients': 0
                    })()
                
                async def start_server(self):
                    return True
                    
                async def stop_server(self):
                    return True
                    
                async def restart_server(self):
                    return True
            
            bridge = MockServerBridge()
            safe_print("[OK] Mock ServerBridge created as fallback")
            return bridge
            
    except ImportError as e:
        safe_print(f"[ERROR] ServerBridge import failed: {e}")
        return None

def test_dashboard_creation(bridge):
    """Test dashboard creation with mock bridge."""
    safe_print("\n=== Testing Dashboard Creation ===")
    
    try:
        from flet_server_gui.views.dashboard import DashboardView
        
        class MockPage:
            def __init__(self):
                self.theme_mode = ft.ThemeMode.DARK
                
            def update(self):
                pass
        
        page = MockPage()
        dashboard = DashboardView(page, bridge)
        safe_print("[OK] Dashboard view created successfully")
        
        # Test building dashboard
        dashboard_content = dashboard.build()
        if dashboard_content:
            safe_print("[OK] Dashboard content built successfully")
            return dashboard
        else:
            safe_print("[ERROR] Dashboard content is None")
            return None
            
    except Exception as e:
        safe_print(f"[ERROR] Dashboard creation failed: {e}")
        traceback.print_exc()
        return None

def comprehensive_gui_test(page: ft.Page):
    """Comprehensive test of the full GUI."""
    safe_print("\n=== Starting Comprehensive GUI Test ===")
    
    # Basic page setup
    page.title = "Comprehensive Flet Test"
    page.window_width = 1200
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    
    # Test theme manager
    try:
        from flet_server_gui.ui.theme import ThemeManager
        theme_manager = ThemeManager(page)
        theme_manager.apply_theme()
        safe_print("[OK] Theme applied successfully")
    except Exception as e:
        safe_print(f"[ERROR] Theme application failed: {e}")
        return
    
    # Test server bridge
    server_bridge = test_server_bridge()
    if not server_bridge:
        safe_print("[ERROR] Cannot proceed without server bridge")
        return
    
    # Test dashboard creation
    dashboard = test_dashboard_creation(server_bridge)
    if not dashboard:
        safe_print("[ERROR] Cannot proceed without dashboard")
        return
    
    # Test dialog systems
    try:
        from flet_server_gui.ui.dialogs import DialogSystem, ToastManager
        dialog_system = DialogSystem(page)
        toast_manager = ToastManager(page)
        safe_print("[OK] Dialog systems created successfully")
    except Exception as e:
        safe_print(f"[ERROR] Dialog systems creation failed: {e}")
        return
    
    # Create test UI
    def test_button_click(e):
        safe_print("[OK] Test button clicked!")
        toast_manager.show_success("Button click test successful!")
    
    def test_dialog_click(e):
        safe_print("[OK] Dialog button clicked!")
        dialog_system.show_info_dialog("Test Dialog", "This dialog test was successful!")
    
    # Test control panel
    try:
        from flet_server_gui.components.control_panel_card import ControlPanelCard
        
        async def mock_show_notification(message, is_error=False):
            safe_print(f"[NOTIFICATION] {message}")
            if is_error:
                toast_manager.show_error(message)
            else:
                toast_manager.show_success(message)
        
        def mock_add_log_entry(source, message, level):
            safe_print(f"[LOG] {source}: {message} ({level})")
        
        control_panel = ControlPanelCard(
            server_bridge=server_bridge,
            page=page,
            show_notification=mock_show_notification,
            add_log_entry=mock_add_log_entry
        )
        control_panel_card = control_panel.build()
        safe_print("[OK] Control panel card created successfully")
        
    except Exception as e:
        safe_print(f"[ERROR] Control panel creation failed: {e}")
        traceback.print_exc()
        control_panel_card = ft.Card(
            content=ft.Container(
                content=ft.Text("Control panel failed to load"),
                padding=20
            )
        )
    
    # Create main layout
    main_content = ft.Container(
        content=ft.Column([
            ft.Text(
                "Comprehensive Flet GUI Test Results",
                style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(),
            
            # Test buttons
            ft.ResponsiveRow([
                ft.Container(
                    content=ft.FilledButton(
                        "Test Button Click",
                        icon=ft.Icons.CHECK_CIRCLE,
                        on_click=test_button_click
                    ),
                    col={"sm": 12, "md": 6}
                ),
                ft.Container(
                    content=ft.OutlinedButton(
                        "Test Dialog",
                        icon=ft.Icons.CHAT,
                        on_click=test_dialog_click
                    ),
                    col={"sm": 12, "md": 6}
                )
            ]),
            
            ft.Divider(),
            
            # Control panel test
            ft.ResponsiveRow([
                ft.Container(
                    content=control_panel_card,
                    col={"sm": 12, "md": 12}
                )
            ])
        ], spacing=20, scroll=ft.ScrollMode.AUTO),
        padding=20,
        expand=True
    )
    
    # Add app bar
    page.appbar = ft.AppBar(
        title=ft.Text("Comprehensive Test"),
        center_title=True
    )
    
    page.add(main_content)
    safe_print("[OK] GUI test layout completed successfully")

def main():
    """Main entry point for comprehensive testing."""
    safe_print("=" * 60)
    safe_print("COMPREHENSIVE FLET GUI TEST")
    safe_print("=" * 60)
    
    # Test imports first
    if not test_imports():
        safe_print("[ERROR] Critical imports failed, cannot continue")
        return False
    
    safe_print("\n[INFO] All imports successful, starting GUI test...")
    
    try:
        ft.app(target=comprehensive_gui_test)
        safe_print("[OK] Comprehensive test completed successfully")
    except Exception as e:
        safe_print(f"[ERROR] Test failed: {e}")
        safe_print("\nFull traceback:")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)