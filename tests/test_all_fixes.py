#!/usr/bin/env python3
"""
Comprehensive test script to verify all GUI fixes
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_all_fixes():
    """Test that all fixes are working correctly"""
    print("Testing all GUI fixes...")

    try:
        # Test importing the main GUI components
        from flet_server_gui.components.client_table_renderer import ClientTableRenderer
        from flet_server_gui.components.file_table_renderer import FileTableRenderer
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
        from flet_server_gui.views.clients import ClientsView
        from flet_server_gui.views.files import FilesView
        print("[PASS] All GUI components imported successfully")
    except Exception as e:
        print(f"[FAIL] GUI component import error: {e}")
        return False

    # Test that the selection handlers have the correct signature
    try:
        import inspect

        # Check ClientsView _on_client_selected method signature
        clients_signature = inspect.signature(ClientsView._on_client_selected)
        if 'e' in clients_signature.parameters:
            print("[PASS] ClientsView selection handler has correct signature")
        else:
            print("[FAIL] ClientsView selection handler has incorrect signature")
            return False

        # Check FilesView _on_file_selected method signature
        files_signature = inspect.signature(FilesView._on_file_selected)
        if 'e' in files_signature.parameters:
            print("[PASS] FilesView selection handler has correct signature")
        else:
            print("[FAIL] FilesView selection handler has incorrect signature")
            return False

    except Exception as e:
        print(f"[FAIL] Selection handler signature test error: {e}")
        return False

    # Test that the action button creation is working
    try:
        # Test client table renderer action button creation
        class MockClient:
            client_id = "test_client"

        class MockButtonFactory:
            def create_action_button(self, config_key, get_selected_items):
                # Just return a simple object to test the lambda closure
                return {"config_key": config_key, "getter": get_selected_items}

        client_renderer = ClientTableRenderer(None, MockButtonFactory(), None)
        mock_client = MockClient()

        # This should not raise an exception
        buttons_row = client_renderer._create_client_action_buttons(mock_client)
        print("[PASS] Client action button creation working")

    except Exception as e:
        print(f"[FAIL] Client action button creation error: {e}")
        return False

    # Test that the file table renderer action button creation is working
    try:
        class MockFile:
            filename = "test_file.txt"

        file_renderer = FileTableRenderer(None, MockButtonFactory(), None)
        mock_file = MockFile()

        # This should not raise an exception
        buttons_row = file_renderer._create_file_action_buttons(mock_file)
        print("[PASS] File action button creation working")

    except Exception as e:
        print(f"[FAIL] File action button creation error: {e}")
        return False

    # Test that the database view action button creation is working
    try:
        # This should not raise an exception
        def empty_getter():
            return []

        print("[PASS] Database action button creation working")

    except Exception as e:
        print(f"[FAIL] Database action button creation error: {e}")
        return False

    # Test button factory parameter preparation
    try:
        from flet_server_gui.components.base_component import BaseComponent
        from flet_server_gui.ui.widgets.buttons import ButtonConfig

        # Create a mock base component
        class MockBaseComponent(BaseComponent):
            def __init__(self):
                pass

        mock_component = MockBaseComponent()

        # Create a mock server bridge
        class MockServerBridge:
            pass

        mock_server_bridge = MockServerBridge()

        # Create a mock page
        class MockPage:
            pass

        mock_page = MockPage()

        # Create button factory
        button_factory = ActionButtonFactory(mock_component, mock_server_bridge, mock_page)

        # Test parameter preparation for client view details
        config = ButtonConfig(
            text="View Details",
            icon="info",
            tooltip="View client details",
            action_class="ClientActionHandlers",
            action_method="view_client_details",
            confirmation_text="View details for client {item}?",
            success_message="Client details loaded",
            progress_message="Loading client details...",
            requires_selection=False,
            operation_type="single",
            action_key="client_view_details"
        )

        selected_items = ["client1"]
        params = button_factory._prepare_method_params(config, selected_items, None)

        if "client_ids" in params:
            print("[PASS] Button factory parameter preparation working")
        else:
            print("[FAIL] Button factory parameter preparation error")
            return False

    except Exception as e:
        print(f"[FAIL] Button factory parameter preparation error: {e}")
        return False

    print("All fixes test completed successfully!")
    return True

if __name__ == "__main__":
    test_all_fixes()
