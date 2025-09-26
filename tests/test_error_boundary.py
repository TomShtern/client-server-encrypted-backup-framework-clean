"""test_error_boundary.py

Comprehensive tests for the centralized error boundary system.
Tests error context creation, dialog functionality, and integration patterns.
"""

import os

# Add the flet_server_gui path for imports
import sys
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath('.'))

from flet_server_gui.components.base_action_handler import BaseActionHandler
from flet_server_gui.components.error_boundary import ErrorBoundary, GlobalErrorBoundary
from flet_server_gui.components.error_dialog import ErrorDialog
from flet_server_gui.utils.error_context import ErrorContext, ErrorFormatter, create_error_context


class TestErrorContext:
    """Test ErrorContext creation and functionality."""

    def test_error_context_from_exception(self):
        """Test creating ErrorContext from exception."""
        try:
            raise ValueError("Test error message")
        except Exception as e:
            context = ErrorContext.from_exception(
                e,
                operation="test operation",
                component="TestComponent"
            )

            assert context.error_type == "ValueError"
            assert context.error_message == "Test error message"
            assert context.operation == "test operation"
            assert context.component == "TestComponent"
            assert context.severity == "error"
            assert context.correlation_id is not None
            assert len(context.stack_trace) > 0

    def test_error_context_user_message_generation(self):
        """Test automatic user message generation."""
        test_cases = [
            (FileNotFoundError("file not found"), "The requested file could not be found."),
            (PermissionError("permission denied"), "Permission denied. Please check file permissions."),
            (ValueError("invalid value"), "Invalid input provided. Please check your data."),
            (RuntimeError("runtime issue"), "An unexpected error occurred during processing.")
        ]

        for exception, expected_message in test_cases:
            context = ErrorContext.from_exception(exception)
            assert expected_message in context.user_message

    def test_error_context_severity_classification(self):
        """Test error severity classification."""
        test_cases = [
            (MemoryError("out of memory"), "critical"),
            (SystemExit("system exit"), "critical"),
            (UserWarning("user warning"), "warning"),
            (ValueError("value error"), "error"),
            (Exception("generic exception"), "error")
        ]

        for exception, expected_severity in test_cases:
            context = ErrorContext.from_exception(exception)
            assert context.severity == expected_severity

    def test_error_context_to_clipboard_text(self):
        """Test clipboard text formatting."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            context = ErrorContext.from_exception(e, operation="test op")
            clipboard_text = context.to_clipboard_text()

            assert "Error Report" in clipboard_text
            assert context.correlation_id in clipboard_text
            assert "test op" in clipboard_text
            assert "ValueError" in clipboard_text
            assert "Stack Trace:" in clipboard_text


class TestErrorFormatter:
    """Test ErrorFormatter utility functions."""

    def test_format_for_user(self):
        """Test user-friendly formatting."""
        context = Mock()
        context.user_message = "User friendly message"
        context.error_message = "Technical error message"

        result = ErrorFormatter.format_for_user(context)
        assert result == "User friendly message"

    def test_format_for_developer(self):
        """Test developer formatting."""
        context = Mock()
        context.error_type = "ValueError"
        context.error_message = "Invalid input"

        result = ErrorFormatter.format_for_developer(context)
        assert result == "ValueError: Invalid input"

    def test_format_technical_details(self):
        """Test technical details formatting."""
        context = Mock()
        context.function_name = "test_function"
        context.file_name = "test_file.py"
        context.line_number = 42
        context.error_type = "ValueError"
        context.correlation_id = "test-id"
        context.timestamp = "2024-01-01T00:00:00"
        context.local_variables = {"var1": "value1", "var2": "value2"}

        details = ErrorFormatter.format_technical_details(context)

        assert any("test_function()" in detail for detail in details)
        assert any("test_file.py" in detail for detail in details)
        assert any("line 42" in detail for detail in details)
        assert any("ValueError" in detail for detail in details)
        assert any("test-id" in detail for detail in details)


class MockPage:
    """Mock Flet page for testing."""

    def __init__(self):
        self.dialog = None
        self.snack_bars = []
        self.clipboard_content = None

    def update(self):
        pass

    def show_snack_bar(self, snack_bar):
        self.snack_bars.append(snack_bar)

    def set_clipboard(self, content):
        self.clipboard_content = content


class TestErrorDialog:
    """Test ErrorDialog functionality."""

    def test_error_dialog_creation(self):
        """Test error dialog creation."""
        page = MockPage()
        dialog = ErrorDialog(page)

        # Create test error context
        try:
            raise ValueError("Test error")
        except Exception as e:
            context = create_error_context(e, operation="test operation")

            dialog.show_error(context)

            assert page.dialog is not None
            assert page.dialog.open is True

    def test_error_dialog_copy_functionality(self):
        """Test copy to clipboard functionality."""
        page = MockPage()
        dialog = ErrorDialog(page)

        try:
            raise ValueError("Test error")
        except Exception as e:
            context = create_error_context(e)
            dialog.show_error(context)

            # Simulate copy button click
            dialog._copy_to_clipboard(context)

            assert page.clipboard_content is not None
            assert "Error Report" in page.clipboard_content
            assert len(page.snack_bars) > 0  # Confirmation snack bar


class TestErrorBoundary:
    """Test ErrorBoundary functionality."""

    def test_error_boundary_initialization(self):
        """Test error boundary initialization."""
        page = MockPage()
        boundary = ErrorBoundary(page)

        assert boundary.page == page
        assert boundary.auto_show_dialog is True
        assert boundary.capture_locals is False
        assert boundary.log_errors is True

    def test_safe_callback_decorator(self):
        """Test safe callback decorator."""
        page = MockPage()
        boundary = ErrorBoundary(page)
        boundary.auto_show_dialog = False  # Disable dialog for test

        @boundary.safe_callback
        def test_callback():
            raise ValueError("Test error")

        # Should not raise exception
        result = test_callback()
        assert result is None  # Returns None for failed callbacks

    async def test_async_safe_callback(self):
        """Test async safe callback decorator."""
        page = MockPage()
        boundary = ErrorBoundary(page)
        boundary.auto_show_dialog = False  # Disable dialog for test

        @boundary.safe_callback
        async def test_async_callback():
            raise ValueError("Test async error")

        # Should not raise exception
        result = await test_async_callback()
        assert result is None

    async def test_protect_context_manager(self):
        """Test protect context manager."""
        page = MockPage()
        boundary = ErrorBoundary(page)
        boundary.auto_show_dialog = False  # Disable dialog for test

        try:
            async with boundary.protect("test operation"):
                raise ValueError("Test context manager error")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected exception

    def test_wrap_callback(self):
        """Test programmatic callback wrapping."""
        page = MockPage()
        boundary = ErrorBoundary(page)
        boundary.auto_show_dialog = False

        def original_callback():
            raise ValueError("Test error")

        wrapped = boundary.wrap_callback(original_callback, "test operation")
        result = wrapped()

        assert result is None  # Should not raise

    def test_custom_error_handler(self):
        """Test custom error handler registration."""
        page = MockPage()
        boundary = ErrorBoundary(page)

        handled_errors = []

        def custom_handler(error_context):
            handled_errors.append(error_context)
            return True  # Mark as handled

        boundary.add_error_handler(custom_handler)
        boundary.auto_show_dialog = False

        @boundary.safe_callback
        def test_callback():
            raise ValueError("Test error")

        test_callback()

        assert len(handled_errors) == 1
        assert handled_errors[0].error_type == "ValueError"


class TestGlobalErrorBoundary:
    """Test GlobalErrorBoundary singleton."""

    def test_global_initialization(self):
        """Test global error boundary initialization."""
        page = MockPage()
        boundary = GlobalErrorBoundary.initialize(page)

        assert boundary is not None
        assert GlobalErrorBoundary.get_instance() == boundary

    def test_global_safe_callback(self):
        """Test global safe callback decorator."""
        page = MockPage()
        GlobalErrorBoundary.initialize(page)

        @GlobalErrorBoundary.safe_callback
        def test_callback():
            raise ValueError("Global test error")

        # Should not raise exception
        result = test_callback()
        assert result is None


class MockActionHandler(BaseActionHandler):
    """Mock action handler for testing."""

    def __init__(self, page):
        # Mock the dependencies
        server_bridge = Mock()
        dialog_system = Mock()
        toast_manager = Mock()

        super().__init__(server_bridge, dialog_system, toast_manager, page)


class TestBaseActionHandlerIntegration:
    """Test BaseActionHandler integration with ErrorBoundary."""

    def test_base_action_handler_error_boundary_setup(self):
        """Test that BaseActionHandler sets up error boundary correctly."""
        page = MockPage()
        handler = MockActionHandler(page)

        assert handler.error_boundary is not None
        assert handler.error_boundary.page == page
        assert handler.error_boundary.auto_show_dialog is False
        assert handler.error_boundary.log_errors is True

    def test_create_safe_callback(self):
        """Test creating safe callbacks through BaseActionHandler."""
        page = MockPage()
        handler = MockActionHandler(page)

        def test_callback():
            raise ValueError("Handler test error")

        safe_callback = handler.create_safe_callback(test_callback, "test operation")
        result = safe_callback()

        assert result is None  # Should not raise

    def test_safe_callback_decorator(self):
        """Test safe callback decorator on BaseActionHandler."""
        page = MockPage()
        handler = MockActionHandler(page)

        @handler.safe_callback("test operation")
        def test_callback():
            raise ValueError("Decorator test error")

        result = test_callback()
        assert result is None  # Should not raise


def run_tests():
    """Run all error boundary tests."""
    print("🚀 Starting Error Boundary System Tests")
    print("=" * 60)

    # Test ErrorContext
    print("Testing ErrorContext...")
    test_context = TestErrorContext()
    test_context.test_error_context_from_exception()
    test_context.test_error_context_user_message_generation()
    test_context.test_error_context_severity_classification()
    test_context.test_error_context_to_clipboard_text()
    print("✅ ErrorContext tests passed")

    # Test ErrorFormatter
    print("\nTesting ErrorFormatter...")
    test_formatter = TestErrorFormatter()
    test_formatter.test_format_for_user()
    test_formatter.test_format_for_developer()
    test_formatter.test_format_technical_details()
    print("✅ ErrorFormatter tests passed")

    # Test ErrorDialog
    print("\nTesting ErrorDialog...")
    test_dialog = TestErrorDialog()
    test_dialog.test_error_dialog_creation()
    test_dialog.test_error_dialog_copy_functionality()
    print("✅ ErrorDialog tests passed")

    # Test ErrorBoundary
    print("\nTesting ErrorBoundary...")
    test_boundary = TestErrorBoundary()
    test_boundary.test_error_boundary_initialization()
    test_boundary.test_safe_callback_decorator()
    test_boundary.test_wrap_callback()
    test_boundary.test_custom_error_handler()
    print("✅ ErrorBoundary tests passed")

    # Test GlobalErrorBoundary
    print("\nTesting GlobalErrorBoundary...")
    test_global = TestGlobalErrorBoundary()
    test_global.test_global_initialization()
    test_global.test_global_safe_callback()
    print("✅ GlobalErrorBoundary tests passed")

    # Test BaseActionHandler integration
    print("\nTesting BaseActionHandler integration...")
    test_integration = TestBaseActionHandlerIntegration()
    test_integration.test_base_action_handler_error_boundary_setup()
    test_integration.test_create_safe_callback()
    test_integration.test_safe_callback_decorator()
    print("✅ BaseActionHandler integration tests passed")

    print("\n" + "=" * 60)
    print("🎉 ALL ERROR BOUNDARY TESTS PASSED!")
    print("\n📊 Test Summary:")
    print("✅ ErrorContext: 4 tests passed")
    print("✅ ErrorFormatter: 3 tests passed")
    print("✅ ErrorDialog: 2 tests passed")
    print("✅ ErrorBoundary: 4 tests passed")
    print("✅ GlobalErrorBoundary: 2 tests passed")
    print("✅ BaseActionHandler Integration: 3 tests passed")
    print("\n🎯 Total: 18 tests passed, 0 failed")
    print("\n🔥 The centralized error boundary system is working correctly!")


if __name__ == "__main__":
    run_tests()
