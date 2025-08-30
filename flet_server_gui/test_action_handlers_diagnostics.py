#!/usr/bin/env python3
"""
Test script for action handlers diagnostics
Tests the diagnostic logging and fallback behavior we just implemented.
"""

import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import directly to avoid relative import issues
sys.path.append(os.path.join(os.path.dirname(__file__), "components"))

# Mock the server bridge import before importing the handlers
class MockServerBridge:
    """Mock server bridge for testing"""
    async def get_client_details(self, client_id):
        return {"id": client_id, "status": "connected", "files_count": 5}
    
    async def get_client_files(self, client_id):
        return [
            {"filename": "test1.txt", "size": 1024},
            {"filename": "test2.txt", "size": 2048}
        ]
    
    async def get_file_details(self, filename):
        return {"filename": filename, "size": 1024, "created": "2025-08-30"}

class MockActions:
    """Mock actions class"""
    def __init__(self, server_bridge):
        self.server_bridge = server_bridge
    
    async def get_client_details(self, client_id):
        return await self.server_bridge.get_client_details(client_id)
    
    async def get_client_files(self, client_id):
        return await self.server_bridge.get_client_files(client_id)
    
    async def get_file_details(self, filename):
        return await self.server_bridge.get_file_details(filename)
    
    async def disconnect_client(self, client_id):
        return True
    
    async def download_file(self, filename, destination):
        return True
    
    async def get_file_content(self, filename):
        class Result:
            success = True
            data = f"Mock content for {filename}"
            error_message = None
        return Result()

# Mock the modules before import
import types
utils_module = types.ModuleType('utils')
utils_module.server_bridge = types.ModuleType('server_bridge')
utils_module.server_bridge.ServerBridge = MockServerBridge

actions_module = types.ModuleType('actions')
actions_module.ClientActions = MockActions
actions_module.FileActions = MockActions

sys.modules['flet_server_gui.utils'] = utils_module
sys.modules['flet_server_gui.utils.server_bridge'] = utils_module.server_bridge
sys.modules['flet_server_gui.actions'] = actions_module

# Now import the actual handlers
import importlib.util
import flet as ft

# Import the handlers manually
client_handler_path = os.path.join(os.path.dirname(__file__), "components", "client_action_handlers.py")
file_handler_path = os.path.join(os.path.dirname(__file__), "components", "file_action_handlers.py")

spec_client = importlib.util.spec_from_file_location("client_action_handlers", client_handler_path)
client_handler_module = importlib.util.module_from_spec(spec_client)
spec_client.loader.exec_module(client_handler_module)

spec_file = importlib.util.spec_from_file_location("file_action_handlers", file_handler_path)
file_handler_module = importlib.util.module_from_spec(spec_file)
spec_file.loader.exec_module(file_handler_module)

ClientActionHandlers = client_handler_module.ClientActionHandlers
FileActionHandlers = file_handler_module.FileActionHandlers

class MockToastManager:
    """Mock toast manager for testing"""
    def show_success(self, message):
        print(f"[TOAST SUCCESS] {message}")
    
    def show_error(self, message):
        print(f"[TOAST ERROR] {message}")
    
    def show_info(self, message):
        print(f"[TOAST INFO] {message}")
    
    def show_warning(self, message):
        print(f"[TOAST WARNING] {message}")

class MockPage:
    """Mock page for testing"""
    def update(self):
        print("[PAGE] Update called")
    
    def run_task(self, coro):
        print(f"[PAGE] run_task called with: {coro}")
        asyncio.create_task(coro)

async def test_client_actions_with_none_dialog():
    """Test client action handlers with None dialog system"""
    print("=" * 60)
    print("TESTING CLIENT ACTION HANDLERS WITH None DIALOG SYSTEM")
    print("=" * 60)
    
    # Create mock objects
    server_bridge = MockServerBridge()
    toast_manager = MockToastManager()
    page = MockPage()
    dialog_system = None  # This is the key test - no dialog system
    
    # Create action handler
    client_handler = ClientActionHandlers(server_bridge, dialog_system, toast_manager, page)
    
    print("\n1. Testing view_client_details with client_id 'test_client_123'")
    await client_handler.view_client_details("test_client_123")
    
    print("\n2. Testing view_client_files with client_id 'test_client_123'")
    await client_handler.view_client_files("test_client_123")
    
    print("\n3. Testing disconnect_client with client_id 'test_client_123'")
    await client_handler.disconnect_client("test_client_123")

async def test_file_actions_with_none_dialog():
    """Test file action handlers with None dialog system"""
    print("\n" + "=" * 60)
    print("TESTING FILE ACTION HANDLERS WITH None DIALOG SYSTEM")
    print("=" * 60)
    
    # Create mock objects
    server_bridge = MockServerBridge()
    toast_manager = MockToastManager()
    page = MockPage()
    dialog_system = None  # This is the key test - no dialog system
    
    # Create action handler
    file_handler = FileActionHandlers(server_bridge, dialog_system, toast_manager, page)
    
    print("\n1. Testing view_file_details with filename='test_file.txt'")
    await file_handler.view_file_details(filename="test_file.txt")
    
    print("\n2. Testing view_file_details with file_id='test_file_id.txt' (button factory param)")
    await file_handler.view_file_details(file_id="test_file_id.txt")
    
    print("\n3. Testing preview_file with filename='test_preview.txt'")
    await file_handler.preview_file(filename="test_preview.txt")
    
    print("\n4. Testing preview_file with file_id='test_preview_id.txt' (button factory param)")
    await file_handler.preview_file(file_id="test_preview_id.txt")
    
    print("\n5. Testing download_file with filename='test_download.txt'")
    await file_handler.download_file("test_download.txt")

async def test_file_action_signature_issues():
    """Test the specific signature issues we're fixing"""
    print("\n" + "=" * 60)
    print("TESTING SIGNATURE COMPATIBILITY FIXES")
    print("=" * 60)
    
    # Create mock objects
    server_bridge = MockServerBridge()
    toast_manager = MockToastManager()
    page = MockPage()
    dialog_system = None
    
    # Create action handler
    file_handler = FileActionHandlers(server_bridge, dialog_system, toast_manager, page)
    
    print("\n1. Testing old signature issue: view_file_details(file_id='test.txt')")
    try:
        await file_handler.view_file_details(file_id='test.txt')
        print("[SUCCESS] Method accepted file_id parameter")
    except TypeError as e:
        print(f"[ERROR] TypeError: {e}")
    
    print("\n2. Testing old signature issue: preview_file(file_id='test.txt')")
    try:
        await file_handler.preview_file(file_id='test.txt')
        print("[SUCCESS] Method accepted file_id parameter")
    except TypeError as e:
        print(f"[ERROR] TypeError: {e}")

async def main():
    """Run all diagnostic tests"""
    print("STARTING ACTION HANDLER DIAGNOSTICS TEST")
    print("This will help identify why dialog system isn't working")
    print("Look for [DEBUG], [ERROR], [FALLBACK] messages")
    
    await test_client_actions_with_none_dialog()
    await test_file_actions_with_none_dialog()
    await test_file_action_signature_issues()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC TESTS COMPLETE")
    print("=" * 60)
    print("Check the output above for:")
    print("- [DEBUG] messages showing what parameters are received")
    print("- [ERROR] messages showing missing dialog_system")
    print("- [FALLBACK] messages showing console output when dialogs fail")
    print("- [TOAST] messages showing toast notifications")
    print("- [SUCCESS] messages confirming signature fixes work")

if __name__ == "__main__":
    asyncio.run(main())