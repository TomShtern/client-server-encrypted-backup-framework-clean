#!/usr/bin/env python3
"""
Test script to verify button functionality and action system
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

from flet_server_gui.actions.base_action import ActionResult
from flet_server_gui.actions.client_actions import ClientActions
from flet_server_gui.actions.file_actions import FileActions
from flet_server_gui.actions.server_actions import ServerActions


def test_action_result_creation():
    """Test ActionResult creation methods"""
    print("Testing ActionResult creation...")
    
    # Test success result
    success_result = ActionResult.success_result(
        data={"test": "data"},
        metadata={"operation": "test"}
    )
    assert success_result.success == True
    assert success_result.data == {"test": "data"}
    assert success_result.metadata == {"operation": "test"}
    print("  [PASS] Success result creation")
    
    # Test error result
    error_result = ActionResult.error_result(
        error_message="Test error",
        error_code="TEST_ERROR",
        metadata={"operation": "test"}
    )
    assert error_result.success == False
    assert error_result.error_message == "Test error"
    assert error_result.error_code == "TEST_ERROR"
    assert error_result.metadata == {"operation": "test"}
    print("  [PASS] Error result creation")
    
    # Test combining results
    results = [success_result, error_result]
    combined = ActionResult.from_results(results)
    assert combined.success == False  # Should be False when any result fails
    assert combined.error_code == "PARTIAL_FAILURE"
    print("  [PASS] Result combination")


def test_button_configurations():
    """Test that all button configurations are properly defined"""
    print("Testing button configurations...")
    
    from flet_server_gui.components.button_factory import ActionButtonFactory
    
    # Check that all configurations exist
    required_configs = [
        'client_export',
        'client_import',
        'client_disconnect_bulk',
        'client_delete_bulk',
        'file_download_bulk',
        'file_verify_bulk',
        'file_export_list',
        'file_upload',
        'file_cleanup',
        'server_health_check'
    ]
    
    for config_key in required_configs:
        assert config_key in ActionButtonFactory.BUTTON_CONFIGS, f"Missing config: {config_key}"
        config = ActionButtonFactory.BUTTON_CONFIGS[config_key]
        assert hasattr(config, 'text'), f"Config {config_key} missing text"
        assert hasattr(config, 'icon'), f"Config {config_key} missing icon"
        assert hasattr(config, 'action_class'), f"Config {config_key} missing action_class"
        assert hasattr(config, 'action_method'), f"Config {config_key} missing action_method"
        print(f"  [PASS] {config_key} configuration")
    
    print("  [PASS] All button configurations verified")


def test_action_classes():
    """Test that action classes can be instantiated"""
    print("Testing action class instantiation...")
    
    # Create mock server bridge
    class MockServerBridge:
        pass
    
    server_bridge = MockServerBridge()
    
    # Test ClientActions
    client_actions = ClientActions(server_bridge)
    assert client_actions.server_bridge == server_bridge
    print("  [PASS] ClientActions instantiation")
    
    # Test FileActions
    file_actions = FileActions(server_bridge)
    assert file_actions.server_bridge == server_bridge
    print("  [PASS] FileActions instantiation")
    
    # Test ServerActions
    server_actions = ServerActions(server_bridge)
    assert server_actions.server_bridge == server_bridge
    print("  [PASS] ServerActions instantiation")


def test_action_methods_exist():
    """Test that required action methods exist"""
    print("Testing action method existence...")
    
    # ClientActions methods
    client_methods = [
        'disconnect_client',
        'disconnect_multiple_clients',
        'delete_client',
        'delete_multiple_clients',
        'export_clients',
        'get_client_stats'
    ]
    
    for method in client_methods:
        assert hasattr(ClientActions, method), f"ClientActions missing method: {method}"
    print("  [PASS] ClientActions methods")
    
    # FileActions methods
    file_methods = [
        'delete_file',
        'delete_multiple_files',
        'download_file',
        'download_multiple_files',
        'verify_file_integrity',
        'verify_multiple_files',
        'export_file_list',
        'cleanup_old_files'
    ]
    
    for method in file_methods:
        assert hasattr(FileActions, method), f"FileActions missing method: {method}"
    print("  [PASS] FileActions methods")
    
    # ServerActions methods
    server_methods = [
        'start_server',
        'stop_server',
        'restart_server',
        'get_server_status',
        'get_server_health'
    ]
    
    for method in server_methods:
        assert hasattr(ServerActions, method), f"ServerActions missing method: {method}"
    print("  [PASS] ServerActions methods")


if __name__ == "__main__":
    print("Running button functionality tests...")
    test_action_result_creation()
    test_button_configurations()
    test_action_classes()
    test_action_methods_exist()
    print("[SUCCESS] All button functionality tests passed!")