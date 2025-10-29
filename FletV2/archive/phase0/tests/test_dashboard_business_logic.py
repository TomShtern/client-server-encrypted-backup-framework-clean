"""
Unit tests for dashboard.py business logic functions.

This module tests the pure functions in the dashboard.py_exp file
that perform metric calculations and data processing.
"""

import sys
import os

# Add the FletV2 directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from views.dashboard_exp import (
    calculate_metrics_summary,
    format_storage_value,
    format_duration,
    get_status_color,
    process_activity_logs
)

import flet as ft


def test_calculate_metrics_summary():
    """Test calculating and combining dashboard metrics."""
    dashboard_data = {'data': {'clients_count': 10, 'files_count': 100, 'total_storage': 1024000}}
    system_data = {'data': {'uptime': 3600, 'server_status': 'Connected'}}
    performance_data = {'data': {'cpu_usage': 50.5, 'memory_usage': 60.2, 'network_usage': 10.1}}
    stats_data = {'data': {'backup_success_rate': 95.5, 'active_sessions': 5, 'pending_operations': 2}}
    
    summary = calculate_metrics_summary(dashboard_data, system_data, performance_data, stats_data)
    
    assert summary['clients_count'] == 10
    assert summary['files_count'] == 100
    assert summary['total_storage'] == 1024000
    assert summary['uptime'] == 3600
    assert summary['server_status'] == 'Connected'
    assert summary['cpu_usage'] == 50.5
    assert summary['memory_usage'] == 60.2
    assert summary['network_usage'] == 10.1
    assert summary['backup_success_rate'] == 95.5
    assert summary['active_sessions'] == 5
    assert summary['pending_operations'] == 2
    
    # Test with empty data
    summary = calculate_metrics_summary({}, {}, {}, {})
    assert summary['clients_count'] == 0
    assert summary['files_count'] == 0
    assert summary['total_storage'] == 0
    assert summary['uptime'] == 'Unknown'
    assert summary['server_status'] == 'Unknown'
    assert summary['cpu_usage'] == 0
    assert summary['backup_success_rate'] == 0


def test_format_storage_value():
    """Test formatting storage values in human-readable format."""
    # Test bytes
    assert format_storage_value(512) == "512.00 B"
    
    # Test KB
    assert format_storage_value(1024) == "1.00 KB"
    assert format_storage_value(2048) == "2.00 KB"
    
    # Test MB
    assert format_storage_value(1024*1024) == "1.00 MB"
    assert format_storage_value(5*1024*1024) == "5.00 MB"
    
    # Test GB
    assert format_storage_value(1024*1024*1024) == "1.00 GB"
    
    # Test TB
    assert format_storage_value(1024*1024*1024*1024) == "1.00 TB"
    
    # Test None value
    assert format_storage_value(None) == "0 B"


def test_format_duration():
    """Test formatting duration in seconds to human-readable format."""
    # Test seconds
    assert format_duration(30) == "30s"
    
    # Test minutes and seconds
    assert format_duration(150) == "2m 30s"  # 2*60 + 30 = 150
    
    # Test hours, minutes and seconds
    assert format_duration(3750) == "1h 2m 30s"  # 1*3600 + 2*60 + 30 = 3750
    
    # Test days, hours, minutes and seconds
    assert format_duration(90061) == "1d 1h 1m"  # 1*86400 + 1*3600 + 1*60 + 1 = 90061
    
    # Test None value
    assert format_duration(None) == "Unknown"


def test_get_status_color():
    """Test getting color based on status."""
    assert get_status_color('Connected') == ft.colors.GREEN
    assert get_status_color('Disconnected') == ft.colors.RED
    assert get_status_color('Offline') == ft.colors.RED
    assert get_status_color('Online') == ft.colors.GREEN
    assert get_status_color('Active') == ft.colors.GREEN
    assert get_status_color('Inactive') == ft.colors.AMBER
    assert get_status_color('Unknown') == ft.colors.GREY
    
    # Test unknown status (should default to GREY)
    assert get_status_color('SomeRandomStatus') == ft.colors.GREY


def test_process_activity_logs():
    """Test processing and formatting activity logs."""
    activity_data = {
        'success': True,
        'data': [
            {'timestamp': '2023-05-01 10:00:00', 'type': 'INFO', 'message': 'System started', 'source': 'Server'},
            {'timestamp': '2023-05-01 10:05:00', 'type': 'ERROR', 'message': 'Connection failed', 'source': 'Network'}
        ]
    }
    
    processed_logs = process_activity_logs(activity_data)
    
    assert len(processed_logs) == 2
    assert processed_logs[0]['timestamp'] == '2023-05-01 10:00:00'
    assert processed_logs[0]['type'] == 'INFO'
    assert processed_logs[0]['message'] == 'System started'
    assert processed_logs[0]['source'] == 'Server'
    
    assert processed_logs[1]['timestamp'] == '2023-05-01 10:05:00'
    assert processed_logs[1]['type'] == 'ERROR'
    assert processed_logs[1]['message'] == 'Connection failed'
    assert processed_logs[1]['source'] == 'Network'
    
    # Test with failed data
    failed_data = {'success': False, 'data': []}
    processed_logs = process_activity_logs(failed_data)
    assert processed_logs == []
    
    # Test with None data
    processed_logs = process_activity_logs(None)
    assert processed_logs == []
    
    # Test with data but no success key
    partial_data = {'data': []}
    processed_logs = process_activity_logs(partial_data)
    assert processed_logs == []


if __name__ == "__main__":
    # Run the tests
    test_calculate_metrics_summary()
    test_format_storage_value()
    test_format_duration()
    test_get_status_color()
    test_process_activity_logs()
    print("All dashboard unit tests passed!")