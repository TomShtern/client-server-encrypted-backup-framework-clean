"""
Unit tests for database_pro.py business logic functions.

This module tests the pure functions in the database_pro.py_exp file
that perform filtering, data transformations, and validations.
"""

import sys
import os

# Add the FletV2 directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from views.database_pro_exp import (
    filter_records_by_query,
    sanitize_sensitive_fields,
    transform_for_display,
    prepare_records_for_export,
    get_record_id_field,
    validate_record_data,
    sort_records
)


def test_filter_records_by_query():
    """Test filtering records by search query."""
    records = [
        {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
        {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
        {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
    ]
    
    # Test filtering by name
    result = filter_records_by_query(records, 'John')
    assert len(result) == 1
    assert result[0]['name'] == 'John Doe'
    
    # Test filtering by email
    result = filter_records_by_query(records, 'jane@example.com')
    assert len(result) == 1
    assert result[0]['name'] == 'Jane Smith'
    
    # Test case insensitive search
    result = filter_records_by_query(records, 'JOHN')
    assert len(result) == 1
    assert result[0]['name'] == 'John Doe'
    
    # Test empty query returns all records
    result = filter_records_by_query(records, '')
    assert len(result) == 3
    
    # Test None query returns all records
    result = filter_records_by_query(records, None)
    assert len(result) == 3
    
    # Test empty records list
    result = filter_records_by_query([], 'John')
    assert len(result) == 0


def test_sanitize_sensitive_fields():
    """Test sanitizing sensitive fields in records."""
    records = [
        {
            'id': 1,
            'name': 'John Doe',
            'aes_key': 'sensitive_data_123',
            'public_key': 'public_data_456',
            'email': 'john@example.com'
        }
    ]
    
    sanitized = sanitize_sensitive_fields(records)
    
    assert sanitized[0]['id'] == 1
    assert sanitized[0]['name'] == 'John Doe'
    assert sanitized[0]['email'] == 'john@example.com'
    assert sanitized[0]['aes_key'] == 'REDACTED'
    assert sanitized[0]['public_key'] == 'REDACTED'


def test_transform_for_display():
    """Test transforming records for display by truncating long values."""
    long_text = "A" * 150  # Create a string longer than MAX_DISPLAY_LENGTH (100)
    records = [
        {
            'id': 1,
            'name': 'John Doe',
            'description': long_text
        }
    ]
    
    transformed = transform_for_display(records)
    
    assert transformed[0]['id'] == 1
    assert transformed[0]['name'] == 'John Doe'
    assert len(transformed[0]['description']) == 103  # 100 chars + "..."
    assert transformed[0]['description'].endswith('...')


def test_prepare_records_for_export():
    """Test preparing records for export."""
    records = [
        {
            'id': 1,
            'name': 'John Doe',
            'aes_key': 'sensitive_data',
            'long_field': "A" * 150
        }
    ]
    
    prepared = prepare_records_for_export(records)
    
    assert prepared[0]['id'] == 1
    assert prepared[0]['name'] == 'John Doe'
    assert prepared[0]['aes_key'] == 'REDACTED'  # Sanitized
    assert len(prepared[0]['long_field']) == 103  # Truncated with ...


def test_get_record_id_field():
    """Test getting the appropriate ID field for different table types."""
    assert get_record_id_field('clients') == 'id'
    assert get_record_id_field('files') == 'id'
    assert get_record_id_field('logs') == 'id'
    assert get_record_id_field('backups') == 'id'
    assert get_record_id_field('settings') == 'id'
    
    # Test unknown table type
    assert get_record_id_field('unknown') == 'id'


def test_validate_record_data():
    """Test validating record data based on table type."""
    # Test with clients table - should need id and name
    is_valid, msg = validate_record_data('clients', {'id': 1, 'name': 'Test Client'})
    assert is_valid == True
    
    is_valid, msg = validate_record_data('clients', {'id': 1})  # Missing name
    assert is_valid == False
    assert 'name' in msg
    
    # Test with files table - should need id, name, and client_id
    is_valid, msg = validate_record_data('files', {'id': 1, 'name': 'file.txt', 'client_id': 1})
    assert is_valid == True
    
    is_valid, msg = validate_record_data('files', {'id': 1, 'name': 'file.txt'})  # Missing client_id
    assert is_valid == False
    assert 'client_id' in msg


def test_sort_records():
    """Test sorting records by a specified field."""
    records = [
        {'name': 'Zebra', 'value': 3},
        {'name': 'Apple', 'value': 1},
        {'name': 'Mango', 'value': 2}
    ]
    
    # Test ascending sort
    sorted_records = sort_records(records, 'name', ascending=True)
    assert sorted_records[0]['name'] == 'Apple'
    assert sorted_records[-1]['name'] == 'Zebra'
    
    # Test descending sort
    sorted_records = sort_records(records, 'name', ascending=False)
    assert sorted_records[0]['name'] == 'Zebra'
    assert sorted_records[-1]['name'] == 'Apple'
    
    # Test sorting by numeric field
    sorted_records = sort_records(records, 'value', ascending=True)
    assert sorted_records[0]['name'] == 'Apple'
    assert sorted_records[-1]['name'] == 'Zebra'
    
    # Test with empty records
    sorted_records = sort_records([], 'name')
    assert sorted_records == []
    
    # Test with invalid sort field (should return original with error handling)
    sorted_records = sort_records(records, 'nonexistent_field', ascending=True)
    # Function should handle the error gracefully and return records unchanged


if __name__ == "__main__":
    # Run the tests
    test_filter_records_by_query()
    test_sanitize_sensitive_fields()
    test_transform_for_display()
    test_prepare_records_for_export()
    test_get_record_id_field()
    test_validate_record_data()
    test_sort_records()
    print("All database pro unit tests passed!")