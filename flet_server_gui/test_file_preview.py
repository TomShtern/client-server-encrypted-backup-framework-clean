#!/usr/bin/env python3
"""
Test script to verify file preview functionality
"""
import sys
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Import utf8_solution to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "..", "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        print("[WARNING] utf8_solution import failed, continuing without it")
        print(f"[DEBUG] Import error: {e}")

from flet_server_gui.components.file_action_handlers import FileActionHandlers
from flet_server_gui.ui.widgets.file_preview import FilePreviewManager
from flet_server_gui.actions.file_actions import FileActions
from flet_server_gui.utils.server_bridge import ServerBridge


class MockDialogSystem:
    """Mock dialog system for testing"""
    def __init__(self):
        self.current_dialog = None
        self.messages = []
    
    def show_info_dialog(self, title, message):
        self.messages.append(f"INFO: {title} - {message}")
        print(f"[DIALOG] {title}: {message}")
    
    def show_error_dialog(self, title, message):
        self.messages.append(f"ERROR: {title} - {message}")
        print(f"[DIALOG ERROR] {title}: {message}")
    
    def show_custom_dialog(self, title, content, actions=None):
        self.messages.append(f"CUSTOM: {title}")
        print(f"[DIALOG CUSTOM] {title}")
    
    def show_confirmation_dialog(self, title, message, on_confirm=None, on_cancel=None):
        self.messages.append(f"CONFIRM: {title} - {message}")
        print(f"[DIALOG CONFIRM] {title}: {message}")
        if on_confirm:
            on_confirm()


class MockToastManager:
    """Mock toast manager for testing"""
    def __init__(self):
        self.messages = []
    
    def show_success(self, message):
        self.messages.append(f"SUCCESS: {message}")
        print(f"[TOAST SUCCESS] {message}")
    
    def show_error(self, message):
        self.messages.append(f"ERROR: {message}")
        print(f"[TOAST ERROR] {message}")
    
    def show_warning(self, message):
        self.messages.append(f"WARNING: {message}")
        print(f"[TOAST WARNING] {message}")


class MockPage:
    """Mock Flet page for testing"""
    def __init__(self):
        self.dialog = None
        self.overlay = []
    
    def update(self):
        print("[PAGE] Updated")
    
    def run_task(self, func, *args):
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return asyncio.create_task(func(*args))
        else:
            return asyncio.create_task(asyncio.sleep(0, result=func(*args)))


def test_file_preview_functionality():
    """Test file preview functionality"""
    print("Testing file preview functionality...")
    
    # Create mock components
    mock_page = MockPage()
    mock_dialog_system = MockDialogSystem()
    mock_toast_manager = MockToastManager()
    mock_server_bridge = ServerBridge()
    
    # Create FileActionHandlers
    file_action_handlers = FileActionHandlers(
        mock_server_bridge, 
        mock_dialog_system, 
        mock_toast_manager, 
        mock_page
    )
    
    # Create FilePreviewManager
    preview_manager = FilePreviewManager(
        mock_server_bridge,
        mock_dialog_system,
        mock_page
    )
    
    # Connect preview manager to action handlers
    file_action_handlers.preview_manager = preview_manager
    
    print("[PASS] FileActionHandlers and FilePreviewManager created successfully")
    print("[PASS] Components connected successfully")
    print("[INFO] File preview functionality test completed")


if __name__ == "__main__":
    test_file_preview_functionality()