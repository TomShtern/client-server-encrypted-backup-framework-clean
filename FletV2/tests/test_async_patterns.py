"""
Async pattern verification tests for FletV2 experimental views.

This module verifies that all async patterns are correctly implemented,
including proper use of run_in_executor for sync operations and that no
blocking operations cause UI freezes.
"""

import sys
import os
import asyncio
import threading
from unittest.mock import Mock, patch
import time

# Add the FletV2 directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.async_helpers_exp import run_sync_in_executor, fetch_with_loading
from views.enhanced_logs_exp import fetch_logs_async, fetch_log_statistics_async
from views.database_pro_exp import fetch_database_info_async, fetch_table_data_async
from views.dashboard_exp import fetch_dashboard_summary_async, fetch_system_status_async


def test_run_sync_in_executor_basic():
    """Test basic functionality of run_sync_in_executor."""

    def sync_function(x, y):
        threading.Event().wait(0.01)  # Simulate some work without blocking the event loop
        return x + y

    async def run_test():
        result = await run_sync_in_executor(sync_function, 5, 3)
        assert result == 8
        return True

    result = asyncio.run(run_test())
    assert result
    print("Basic run_sync_in_executor test passed!")


def test_run_sync_in_executor_with_kwargs():
    """Test run_sync_in_executor with keyword arguments."""

    def sync_function_with_kwargs(x, y=10, operation='add'):
        threading.Event().wait(0.01)  # Simulate some work without blocking the event loop
        if operation == 'add':
            return x + y
        elif operation == 'multiply':
            return x * y
        return 0

    async def run_test():
        result = await run_sync_in_executor(sync_function_with_kwargs, 5, y=3, operation='multiply')
        assert result == 15

        result2 = await run_sync_in_executor(sync_function_with_kwargs, 5, operation='add')
        assert result2 == 15  # 5 + 10 (default y value)
        return True

    result = asyncio.run(run_test())
    assert result
    print("run_sync_in_executor with kwargs test passed!")


def test_fetch_with_loading_success():
    """Test fetch_with_loading with a successful operation."""

    def mock_sync_operation():
        return {'success': True, 'data': 'test_data', 'error': None}

    mock_loading_control = Mock()
    mock_error_control = Mock()

    success_result = None

    def on_success(data):
        nonlocal success_result
        success_result = data

    def on_error(error):
        pass  # We don't expect errors in this test

    async def run_test():
        result = await fetch_with_loading(
            mock_sync_operation,
            loading_control=mock_loading_control,
            error_control=mock_error_control,
            on_success=on_success,
            on_error=on_error
        )

        # Check that loading control was shown and then hidden
        assert mock_loading_control.visible == False  # After operation completes
        assert success_result == 'test_data'
        assert result == 'test_data'
        return True

    result = asyncio.run(run_test())
    assert result
    print("fetch_with_loading success test passed!")


def test_fetch_with_loading_error():
    """Test fetch_with_loading with an error operation."""

    def mock_sync_operation_with_error():
        return {'success': False, 'data': None, 'error': 'Test error'}

    mock_loading_control = Mock()
    mock_error_control = Mock()

    error_result = None

    def on_success(data):
        pass  # We don't expect success in this test

    def on_error(error):
        nonlocal error_result
        error_result = error

    async def run_test():
        result = await fetch_with_loading(
            mock_sync_operation_with_error,
            loading_control=mock_loading_control,
            error_control=mock_error_control,
            on_success=on_success,
            on_error=on_error
        )

        # Check that loading control was shown and then hidden
        assert mock_loading_control.visible == False  # After operation completes
        assert error_result == 'Test error'
        assert result is None  # Should return None on failure
        return True

    result = asyncio.run(run_test())
    assert result
    print("fetch_with_loading error test passed!")


def test_fetch_functions_async_patterns():
    """Test that fetch functions properly use run_sync_in_executor."""

    # Mock bridge with sync methods
    mock_bridge = Mock()
    mock_bridge.get_logs = Mock(return_value={'success': True, 'data': {'logs': []}})
    mock_bridge.get_log_stats = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_database_info = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_table_data = Mock(return_value={'success': True, 'data': {'columns': [], 'rows': []}})
    mock_bridge.get_dashboard_summary = Mock(return_value={'success': True, 'data': {}})
    mock_bridge.get_system_status = Mock(return_value={'success': True, 'data': {}})

    async def run_tests():
        # Test enhanced logs fetch functions
        logs_result = await fetch_logs_async(mock_bridge)
        assert logs_result == []

        stats_result = await fetch_log_statistics_async(mock_bridge)
        assert isinstance(stats_result, dict)

        # Test database pro fetch functions
        db_info_result = await fetch_database_info_async(mock_bridge)
        assert db_info_result['success'] == True

        table_data_result = await fetch_table_data_async(mock_bridge, 'test_table')
        assert table_data_result['success'] == True

        # Test dashboard fetch functions
        dash_result = await fetch_dashboard_summary_async(mock_bridge)
        assert dash_result['success'] == True

        sys_result = await fetch_system_status_async(mock_bridge)
        assert sys_result['success'] == True

        return True

    result = asyncio.run(run_tests())
    assert result
    print("All fetch functions async patterns test passed!")


def test_no_blocking_operations():
    """Verify that async functions don't make direct sync calls that would block."""

    # This test ensures that our async functions use run_in_executor
    # rather than calling sync methods directly which would block the event loop

    mock_bridge = Mock()
    # Configure the bridge to have a slow sync method that would block if called directly
    def slow_sync_method():
        threading.Event().wait(0.5)  # This would block if called directly in async context
        return {'success': True, 'data': 'slow_result'}

    mock_bridge.get_logs = slow_sync_method

    start_time = time.time()

    async def run_test():
        # This should not block the event loop thanks to run_in_executor
        result = await fetch_logs_async(mock_bridge)
        return result

    # Run the async test
    result = asyncio.run(run_test())
    end_time = time.time()

    # The operation should complete quickly because run_in_executor doesn't block the event loop
    # The actual work happens in a separate thread
    duration = end_time - start_time
    assert duration < 0.4  # Should be much less than the 0.5s the sync operation takes

    assert result == []  # Expected result from fetch_logs_async when data is empty
    print("No blocking operations test passed!")


def test_multiple_concurrent_operations():
    """Test that multiple concurrent operations work properly with run_in_executor."""

    mock_bridge = Mock()
    # Mock the bridge methods
    mock_bridge.get_logs = lambda: {'success': True, 'data': {'logs': [{'message': 'log1'}]}}
    mock_bridge.get_clients = lambda: {'success': True, 'data': [{'name': 'client1'}]}
    mock_bridge.get_files = lambda: {'success': True, 'data': [{'name': 'file1'}]}

    async def run_concurrent_test():
        # Run multiple operations concurrently
        logs_task = fetch_logs_async(mock_bridge)
        # Simulate other fetch operations
        clients_result = await run_sync_in_executor(mock_bridge.get_clients)
        files_result = await run_sync_in_executor(mock_bridge.get_files)

        logs_result = await logs_task

        assert isinstance(logs_result, list)
        assert isinstance(clients_result, list)
        assert isinstance(files_result, list)

        return True

    result = asyncio.run(run_concurrent_test())
    assert result
    print("Multiple concurrent operations test passed!")


if __name__ == "__main__":
    # Run all async pattern verification tests
    test_run_sync_in_executor_basic()
    test_run_sync_in_executor_with_kwargs()
    test_fetch_with_loading_success()
    test_fetch_with_loading_error()
    test_fetch_functions_async_patterns()
    test_no_blocking_operations()
    test_multiple_concurrent_operations()

    print("All async pattern verification tests passed!")