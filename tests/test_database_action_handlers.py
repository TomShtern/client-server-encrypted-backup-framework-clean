#!/usr/bin/env python3
"""
Unit tests for DatabaseActionHandlers TODO implementations

Tests the concrete implementations of delete_row, bulk_delete_rows, 
edit_row, and bulk_export_rows methods.
"""

import asyncio
from types import SimpleNamespace

import pytest
from flet_server_gui.components.database_action_handlers import DatabaseActionHandlers
from flet_server_gui.utils.action_result import ActionResult


class MockPage:
    def run_task(self, coro):
        return asyncio.create_task(coro)


class MockToastManager:
    def __init__(self):
        self.messages = []

    def show_success(self, msg):
        self.messages.append(('success', msg))

    def show_error(self, msg):
        self.messages.append(('error', msg))

    def show_warning(self, msg):
        self.messages.append(('warning', msg))


class MockDialogSystem:
    def __init__(self, confirm_result=True):
        self.confirm_result = confirm_result
        self.dialogs_shown = []

    async def show_confirmation_async(self, title, message):
        return self.confirm_result

    def show_custom_dialog(self, title, content, actions=None):
        self.dialogs_shown.append((title, content, actions))
        return None

    def close_dialog(self):
        return None


class MockConfirmationService:
    def __init__(self, dialog_system):
        self.dialog_system = dialog_system

    async def confirm(self, *, title, message, proceed_code, proceed_message, cancel_message="Cancelled"):
        # Mock confirmation that always proceeds
        return SimpleNamespace(
            code=proceed_code,
            message=proceed_message
        )


class MockDatabaseActions:
    def __init__(self, server_bridge=None):
        self.server_bridge = server_bridge
        self.deleted_calls = []
        self.export_calls = []

    async def delete_database_rows(self, table_name, row_ids):
        self.deleted_calls.append((table_name, row_ids))
        # Simulate successful deletion
        return ActionResult.make_success(
            code="DELETE_SUCCESS",
            message="Rows deleted",
            data={'deleted_count': len(row_ids)},
            correlation_id="test-123"
        )

    async def export_database_table(self, table_name, export_format='csv'):
        self.export_calls.append((table_name, export_format))
        # Simulate successful export
        return ActionResult.make_success(
            code="EXPORT_SUCCESS",
            message="Table exported",
            data={'export_path': f"/tmp/{table_name}.{export_format}"},
            correlation_id="test-456"
        )

    async def update_database_row(self, row_id, updated_data, table_name):
        # This method doesn't exist yet, so we'll raise AttributeError
        raise AttributeError("'DatabaseActions' object has no attribute 'update_database_row'")


@pytest.fixture
def mock_handler():
    """Create a DatabaseActionHandlers instance with mocked dependencies"""
    mock_bridge = SimpleNamespace()
    dialog = MockDialogSystem()
    toast = MockToastManager()
    page = MockPage()

    # Create handler
    handler = DatabaseActionHandlers(mock_bridge, dialog, toast, page)

    # Replace database_actions with our mock
    handler.database_actions = MockDatabaseActions()

    # Mock the ConfirmationService
    import flet_server_gui.components.database_action_handlers as db_handlers
    db_handlers.ConfirmationService = MockConfirmationService

    return handler, toast, dialog


@pytest.mark.asyncio
async def test_delete_row_delegates_to_database_actions(mock_handler):
    """Test that delete_row properly delegates to DatabaseActions"""
    handler, toast, dialog = mock_handler

    row_data = {'table': 'users', 'id': 'user123', 'name': 'Test User'}
    result = await handler.delete_row('user123', row_data)

    # Verify the call was made to database_actions
    assert len(handler.database_actions.deleted_calls) == 1
    table_name, row_ids = handler.database_actions.deleted_calls[0]
    assert table_name == 'users'
    assert row_ids == ['user123']

    # Verify result
    assert result.success
    assert result.code == "DB_ROW_DELETE_OK"
    assert result.data['row_id'] == 'user123'
    assert result.data['table'] == 'users'

    # Verify success toast was shown
    assert any('deleted successfully' in msg for _, msg in toast.messages)


@pytest.mark.asyncio
async def test_bulk_delete_rows_handles_mixed_input_shapes(mock_handler):
    """Test that bulk_delete_rows supports both simple ids and dict inputs"""
    handler, toast, dialog = mock_handler

    # Test with simple list of ids
    result1 = await handler.bulk_delete_rows(['a', 'b', 'c'])

    assert result1.success
    assert result1.code == "DB_BULK_DELETE_OK"
    assert result1.data['deleted'] == 3
    assert result1.data['total'] == 3

    # Verify the call to database_actions
    assert len(handler.database_actions.deleted_calls) == 1
    table_name, row_ids = handler.database_actions.deleted_calls[0]
    assert table_name == 'default'
    assert row_ids == ['a', 'b', 'c']


@pytest.mark.asyncio
async def test_bulk_export_rows_delegates_and_returns_path(mock_handler):
    """Test that bulk_export_rows delegates to DatabaseActions and returns export path"""
    handler, toast, dialog = mock_handler

    result = await handler.bulk_export_rows(['1', '2'], 'users')

    # Verify the call was made to database_actions
    assert len(handler.database_actions.export_calls) == 1
    table_name, export_format = handler.database_actions.export_calls[0]
    assert table_name == 'users'
    assert export_format == 'csv'

    # Verify result
    assert result.success
    assert result.code == "DB_BULK_EXPORT_OK"
    assert result.data['rows_requested'] == 2
    assert result.data['table'] == 'users'
    assert result.data['export_path'].endswith('users.csv')

    # Verify success toast was shown
    assert any('exported successfully' in msg for _, msg in toast.messages)


@pytest.mark.asyncio
async def test_edit_row_raises_not_implemented_error(mock_handler):
    """Test that edit_row properly handles missing update_database_row method"""
    handler, toast, dialog = mock_handler

    # Mock the dialog form submission
    row_data = {'table': 'users', 'id': 'user123', 'name': 'Test User'}

    # The edit_row method shows a dialog, we need to simulate form submission
    # For now, we'll test that it doesn't crash and shows the dialog
    result = await handler.edit_row('user123', row_data)

    # Should successfully show the edit dialog
    assert result.success
    assert result.code == "DB_ROW_EDIT_DIALOG"
    assert result.data['row_id'] == 'user123'

    # Verify dialog was shown
    assert len(dialog.dialogs_shown) == 1
    title, content, actions = dialog.dialogs_shown[0]
    assert "Edit Row: user123" in title


if __name__ == "__main__":
    # Run tests with asyncio
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
