"""
Unit tests for enhanced_logs.py business logic functions.

This module tests the pure functions in the enhanced_logs.py_exp file
that perform filtering, calculations, and data transformations.
"""

import sys
import os
from datetime import datetime

# Add the FletV2 directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from views.enhanced_logs_exp import (
    filter_logs_by_query,
    filter_logs_by_level,
    calculate_log_statistics,
    export_logs_to_csv,
    export_logs_to_json,
    _compile_search_regex,
    highlight_text_with_search
)

import pytest
import re


def test_filter_logs_by_query():
    """Test filtering logs by search query."""
    logs = [
        {'message': 'Error occurred in module', 'level': 'ERROR', 'time': '2023-05-01 10:00:00'},
        {'message': 'Info message for user', 'level': 'INFO', 'time': '2023-05-01 10:01:00'},
        {'message': 'Warning about resource usage', 'level': 'WARNING', 'time': '2023-05-01 10:02:00'}
    ]
    
    # Test filtering by message content
    result = filter_logs_by_query(logs, 'error')
    assert len(result) == 1
    assert result[0]['level'] == 'ERROR'
    
    # Test filtering by level
    result = filter_logs_by_query(logs, 'info')
    assert len(result) == 1
    assert result[0]['level'] == 'INFO'
    
    # Test filtering by timestamp
    result = filter_logs_by_query(logs, '10:01')
    assert len(result) == 1
    assert result[0]['time'] == '2023-05-01 10:01:00'
    
    # Test empty query returns all logs
    result = filter_logs_by_query(logs, '')
    assert len(result) == 3
    
    # Test None query returns all logs
    result = filter_logs_by_query(logs, None)
    assert len(result) == 3
    
    # Test empty logs list
    result = filter_logs_by_query([], 'error')
    assert len(result) == 0


def test_filter_logs_by_level():
    """Test filtering logs by log level."""
    logs = [
        {'message': 'Error occurred', 'level': 'ERROR'},
        {'message': 'Info message', 'level': 'INFO'},
        {'message': 'Warning message', 'level': 'WARNING'},
        {'message': 'Debug message', 'level': 'DEBUG'}
    ]
    
    # Test filtering by specific level
    result = filter_logs_by_level(logs, 'ERROR')
    assert len(result) == 1
    assert result[0]['level'] == 'ERROR'
    
    # Test filtering with 'All' returns all logs
    result = filter_logs_by_level(logs, 'All')
    assert len(result) == 4
    
    # Test filtering with None returns all logs
    result = filter_logs_by_level(logs, None)
    assert len(result) == 4
    
    # Test empty logs list
    result = filter_logs_by_level([], 'ERROR')
    assert len(result) == 0
    
    # Test non-existent level returns empty list
    result = filter_logs_by_level(logs, 'CRITICAL')
    assert len(result) == 0


def test_calculate_log_statistics():
    """Test calculation of log statistics."""
    logs = [
        {'level': 'ERROR', 'time': '2023-05-01 10:00:00'},
        {'level': 'INFO', 'time': '2023-05-01 10:01:00'},
        {'level': 'WARNING', 'time': '2023-05-01 10:02:00'},
        {'level': 'ERROR', 'time': '2023-05-01 10:03:00'},
        {'level': 'INFO', 'time': '2023-05-01 11:00:00'},
    ]
    
    stats = calculate_log_statistics(logs)
    
    assert stats['total'] == 5
    assert stats['by_level']['ERROR'] == 2
    assert stats['by_level']['INFO'] == 2
    assert stats['by_level']['WARNING'] == 1
    assert stats['latest'] == logs[0]  # First log should be latest since it's not sorted
    
    # Test with empty logs
    stats = calculate_log_statistics([])
    assert stats['total'] == 0
    assert stats['by_level'] == {}
    assert stats['by_hour'] == {}
    assert stats['latest'] is None


def test_compile_search_regex():
    """Test compiling search regex patterns."""
    # Test plain text search
    pattern = _compile_search_regex("error")
    assert pattern.search("This is an error message") is not None
    
    # Test case insensitive by default
    pattern = _compile_search_regex("ERROR")
    assert pattern.search("This is an error message") is not None
    
    # Test regex pattern with flags
    pattern = _compile_search_regex("/error/i")  # Case insensitive
    assert pattern.search("This is an ERROR message") is not None
    
    # Test invalid regex falls back to literal
    pattern = _compile_search_regex("/(unclosed/i")  # Invalid regex
    assert pattern.search("This contains (unclosed pattern") is not None


def test_highlight_text_with_search():
    """Test text highlighting functionality."""
    # Test with match
    result = highlight_text_with_search("This is an error message", "error")
    # This function returns a Flet Text control, so we just test that it doesn't error
    assert result is not None
    
    # Test with no match
    result = highlight_text_with_search("This is a normal message", "error")
    assert result is not None
    
    # Test with empty inputs
    result = highlight_text_with_search("", "error")
    assert result is not None
    
    result = highlight_text_with_search("This is a message", "")
    assert result is not None


if __name__ == "__main__":
    # Run the tests
    test_filter_logs_by_query()
    test_filter_logs_by_level()
    test_calculate_log_statistics()
    test_compile_search_regex()
    test_highlight_text_with_search()
    print("All enhanced logs unit tests passed!")