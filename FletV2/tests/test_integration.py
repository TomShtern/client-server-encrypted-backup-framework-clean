"""
Integration tests for FletV2 experimental views.

This module tests the integration between experimental views and the broader system,
including server bridge integration, state management, and UI functionality.
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Add the FletV2 directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from views.enhanced_logs_exp import create_enhanced_logs_view
from views.database_pro_exp import create_database_view
from views.dashboard_exp import create_dashboard_view
from utils.async_helpers_exp import run_sync_in_executor, fetch_with_loading


def test_enhanced_logs_view_integration():
    """Test that enhanced logs view integrates properly with page and bridge."""
    # Create mock page and bridge
    mock_page = Mock()
    mock_bridge = Mock()
    
    # Mock the bridge methods
    mock_bridge.get_logs = Mock(return_value={'success': True, 'data': {'logs': []}})
    
    # Create the view
    main_control, dispose_func, setup_func = create_enhanced_logs_view(mock_page, mock_bridge)
    
    # Verify that the function returns the expected tuple structure
    assert main_control is not None
    assert callable(dispose_func)
    assert callable(setup_func)
    
    print("Enhanced logs view integration test passed!")


def test_database_view_integration():
    """Test that database pro view integrates properly with page and bridge."""
    # Create mock page and bridge
    mock_page = Mock()
    mock_bridge = Mock()
    
    # Mock the bridge methods
    mock_bridge.get_database_info = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_table_names = Mock(return_value={'success': True, 'data': ['clients', 'files']})
    mock_bridge.get_table_data = Mock(return_value={'success': True, 'data': {'columns': [], 'rows': []}})
    
    # Create the view
    main_control, dispose_func, setup_func = create_database_view(mock_page, mock_bridge)
    
    # Verify that the function returns the expected tuple structure
    assert main_control is not None
    assert callable(dispose_func)
    assert callable(setup_func)
    
    print("Database pro view integration test passed!")


def test_dashboard_view_integration():
    """Test that dashboard view integrates properly with page and bridge."""
    # Create mock page and bridge
    mock_page = Mock()
    mock_bridge = Mock()
    
    # Mock the bridge methods
    mock_bridge.get_dashboard_summary = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_system_status = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_performance_metrics = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_server_statistics = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_recent_activity = Mock(return_value={'success': True, 'data': []})
    
    # Create the view
    main_control, dispose_func, setup_func = create_dashboard_view(mock_page, mock_bridge)
    
    # Verify that the function returns the expected tuple structure
    assert main_control is not None
    assert callable(dispose_func)
    assert callable(setup_func)
    
    print("Dashboard view integration test passed!")


def test_async_helpers_integration():
    """Test that async helpers work properly with mock functions."""
    
    # Test run_sync_in_executor with a mock synchronous function
    def mock_sync_func(x, y):
        return x + y
    
    # Since run_sync_in_executor requires an event loop, we'll test it inside an async context
    async def run_test():
        result = await run_sync_in_executor(mock_sync_func, 5, 3)
        assert result == 8
        return True
    
    # Run the async test
    result = asyncio.run(run_test())
    assert result
    
    print("Async helpers integration test passed!")


def test_fetch_with_loading_integration():
    """Test that fetch_with_loading works properly."""
    
    # Create a mock bridge method
    def mock_bridge_method():
        return {'success': True, 'data': 'test_data'}
    
    # Mock the loading and error controls
    mock_loading_control = Mock()
    mock_error_control = Mock()
    
    # Track if success callback was called
    success_called = False
    def on_success(data):
        nonlocal success_called
        success_called = True
        assert data == 'test_data'
    
    # Since fetch_with_loading is async, test within an async context
    async def run_test():
        result = await fetch_with_loading(
            mock_bridge_method,
            loading_control=mock_loading_control,
            error_control=mock_error_control,
            on_success=on_success,
            on_error=None
        )
        
        assert result == 'test_data'
        assert success_called
        return True
    
    # Run the async test
    result = asyncio.run(run_test())
    assert result
    
    print("Fetch with loading integration test passed!")


if __name__ == "__main__":
    # Run all integration tests
    test_enhanced_logs_view_integration()
    test_database_view_integration()
    test_dashboard_view_integration()
    test_async_helpers_integration()
    test_fetch_with_loading_integration()
    
    print("All integration tests passed!")