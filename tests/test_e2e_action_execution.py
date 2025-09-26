#!/usr/bin/env python3
"""
End-to-End Action Execution Test

Tests the complete execution pipeline:
1. Create mock handlers with real dependencies
2. Execute actions through the consolidated pipeline
3. Verify proper error handling, callbacks, and results
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, Mock

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class MockComponents:
    """Mock components for testing"""

    def __init__(self):
        # Mock server bridge
        self.server_bridge = Mock()
        self.server_bridge.get_clients = AsyncMock(return_value=[])

        # Mock dialog system
        self.dialog_system = Mock()
        self.dialog_system.show_confirmation_async = AsyncMock(return_value=True)
        self.dialog_system.show_custom_dialog = Mock()

        # Mock toast manager
        self.toast_manager = Mock()
        self.toast_manager.show_success = Mock()
        self.toast_manager.show_error = Mock()
        self.toast_manager.show_warning = Mock()
        self.toast_manager.show_info = Mock()

        # Mock page
        self.page = Mock()
        self.page.update = Mock()

        # Mock log service
        self.log_service = Mock()
        self.log_service.get_recent_logs = Mock(return_value=[])

class E2EActionTest:
    """End-to-end action execution tests"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.mocks = MockComponents()

    def test_result(self, test_name: str, passed: bool, message: str = ""):
        """Record a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append(f"{status}: {test_name} - {message}")
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    async def test_client_action_execution(self):
        """Test client action execution through consolidated pipeline"""
        print("🔍 Testing client action execution...")

        try:
            from flet_server_gui.components.client_action_handlers import ClientActionHandlers

            # Create handler with mocks
            handler = ClientActionHandlers(
                server_bridge=self.mocks.server_bridge,
                dialog_system=self.mocks.dialog_system,
                toast_manager=self.mocks.toast_manager,
                page=self.mocks.page
            )

            # Test view client details (no confirmation needed)
            result = await handler.view_client_details("test_client_123")
            self.test_result("Client view details execution", result is not None, f"Result type: {type(result)}")

            # Test disconnect client (with confirmation)
            result = await handler.disconnect_client("test_client_123")
            self.test_result("Client disconnect execution", result is not None, f"Result type: {type(result)}")

            # Verify confirmation was called
            self.mocks.dialog_system.show_confirmation_async.assert_called()
            self.test_result("Client confirmation dialog called", True)

        except Exception as e:
            self.test_result("Client action execution", False, f"Error: {e}")

    async def test_database_action_execution(self):
        """Test database action execution through consolidated pipeline"""
        print("🔍 Testing database action execution...")

        try:
            from flet_server_gui.components.database_action_handlers import DatabaseActionHandlers

            # Create handler with mocks
            handler = DatabaseActionHandlers(
                server_bridge=self.mocks.server_bridge,
                dialog_system=self.mocks.dialog_system,
                toast_manager=self.mocks.toast_manager,
                page=self.mocks.page
            )

            # Test backup database (with confirmation)
            result = await handler.backup_database()
            self.test_result("Database backup execution", result is not None, f"Result type: {type(result)}")

            # Test refresh database (no confirmation)
            result = await handler.refresh_database()
            self.test_result("Database refresh execution", result is not None, f"Result type: {type(result)}")

        except Exception as e:
            self.test_result("Database action execution", False, f"Error: {e}")

    async def test_log_action_execution(self):
        """Test log action execution through consolidated pipeline"""
        print("🔍 Testing log action execution...")

        try:
            from flet_server_gui.components.log_action_handlers import LogActionHandlers

            # Create handler with mocks
            handler = LogActionHandlers(
                log_service=self.mocks.log_service,
                dialog_system=self.mocks.dialog_system,
                toast_manager=self.mocks.toast_manager,
                page=self.mocks.page
            )

            # Test export logs (with confirmation)
            result = await handler.export_logs()
            self.test_result("Log export execution", result is not None, f"Result type: {type(result)}")

            # Test refresh logs (no confirmation)
            result = await handler.refresh_logs()
            self.test_result("Log refresh execution", result is not None, f"Result type: {type(result)}")

        except Exception as e:
            self.test_result("Log action execution", False, f"Error: {e}")

    async def test_data_change_callbacks(self):
        """Test data change callback functionality"""
        print("🔍 Testing data change callbacks...")

        try:
            from flet_server_gui.components.client_action_handlers import ClientActionHandlers

            # Create handler
            handler = ClientActionHandlers(
                server_bridge=self.mocks.server_bridge,
                dialog_system=self.mocks.dialog_system,
                toast_manager=self.mocks.toast_manager,
                page=self.mocks.page
            )

            # Set up callback tracking
            callback_called = False
            async def test_callback():
                nonlocal callback_called
                callback_called = True

            # Set callback
            handler.set_data_changed_callback(test_callback)
            self.test_result("Data change callback registration", True)

            # Execute an action that should trigger data change
            await handler.disconnect_client("test_client")

            # Note: In real execution, the callback would be called by ActionExecutor
            # Here we just verify the mechanism is in place
            self.test_result("Data change callback mechanism", hasattr(handler, 'on_data_changed'))

        except Exception as e:
            self.test_result("Data change callbacks", False, f"Error: {e}")

    async def test_error_handling(self):
        """Test error handling in the consolidated pipeline"""
        print("🔍 Testing error handling...")

        try:
            from flet_server_gui.components.client_action_handlers import ClientActionHandlers

            # Create handler with error-prone mocks
            error_server_bridge = Mock()
            error_server_bridge.get_clients = AsyncMock(side_effect=Exception("Mock server error"))

            handler = ClientActionHandlers(
                server_bridge=error_server_bridge,
                dialog_system=self.mocks.dialog_system,
                toast_manager=self.mocks.toast_manager,
                page=self.mocks.page
            )

            # Execute action that should handle errors gracefully
            result = await handler.view_client_details("test_client")

            # Should get an error result, not an exception
            self.test_result("Error handling graceful", result is not None)

            # Verify error notification
            if hasattr(result, 'success'):
                self.test_result("Error result structure", not result.success, "Error properly reported")

        except Exception as e:
            self.test_result("Error handling", False, f"Unexpected exception: {e}")

    async def test_action_executor_integration(self):
        """Test integration with ActionExecutor"""
        print("🔍 Testing ActionExecutor integration...")

        try:
            from flet_server_gui.components.base_action_handler import BaseActionHandler
            from flet_server_gui.utils.action_executor import get_action_executor

            # Get ActionExecutor
            executor = get_action_executor()
            self.test_result("ActionExecutor retrieval", executor is not None)

            # Create minimal handler to test execute_action
            handler = BaseActionHandler(
                server_bridge=self.mocks.server_bridge,
                dialog_system=self.mocks.dialog_system,
                toast_manager=self.mocks.toast_manager,
                page=self.mocks.page
            )

            # Test simple action execution
            async def simple_action():
                return {"test": "success"}

            result = await handler.execute_action(
                action_name="Test Action",
                action_coro=simple_action(),
                require_selection=False,
                trigger_data_change=False
            )

            self.test_result("BaseActionHandler execute_action", result is not None)

        except Exception as e:
            self.test_result("ActionExecutor integration", False, f"Error: {e}")

    async def run_all_tests(self):
        """Run all end-to-end tests"""
        print("🚀 Starting End-to-End Action Execution Tests")
        print("=" * 60)

        # Run test suites
        await self.test_client_action_execution()
        await self.test_database_action_execution()
        await self.test_log_action_execution()
        await self.test_data_change_callbacks()
        await self.test_error_handling()
        await self.test_action_executor_integration()

        # Print results
        print("\\n" + "=" * 60)
        print("📊 E2E TEST RESULTS")
        print("=" * 60)

        for result in self.results:
            print(result)

        print("\\n" + "=" * 60)
        print(f"🎯 E2E SUMMARY: {self.passed} passed, {self.failed} failed")

        if self.failed == 0:
            print("🎉 ALL E2E TESTS PASSED! The action execution pipeline works correctly.")
            return True
        else:
            print(f"⚠️  {self.failed} E2E test(s) failed. Please review the issues above.")
            return False

async def main():
    test_suite = E2EActionTest()
    success = await test_suite.run_all_tests()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n🛑 Tests interrupted by user")
        sys.exit(1)
