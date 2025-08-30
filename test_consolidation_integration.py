#!/usr/bin/env python3
"""
Integration Test for Consolidated Action Handler Architecture

Tests the refactored action handlers to ensure:
1. All handlers inherit from BaseActionHandler properly
2. Action classes are accessible and functional
3. No import errors or missing dependencies
4. Method signatures are consistent
5. ActionExecutor integration works
"""

import sys
import os
import importlib
import inspect
from typing import Dict, List, Any

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class ConsolidationTest:
    """Test suite for the consolidated action handler architecture"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test_result(self, test_name: str, passed: bool, message: str = ""):
        """Record a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append(f"{status}: {test_name} - {message}")
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_imports(self):
        """Test that all modules can be imported without errors"""
        print("🔍 Testing imports...")
        
        modules_to_test = [
            ("flet_server_gui.components.base_action_handler", "BaseActionHandler"),
            ("flet_server_gui.components.client_action_handlers", "ClientActionHandlers"),
            ("flet_server_gui.components.database_action_handlers", "DatabaseActionHandlers"),
            ("flet_server_gui.components.log_action_handlers", "LogActionHandlers"),
            ("flet_server_gui.actions", "ClientActions"),
            ("flet_server_gui.actions", "DatabaseActions"),
            ("flet_server_gui.actions", "LogActions"),
            ("flet_server_gui.utils.action_executor", "get_action_executor"),
        ]
        
        for module_name, class_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                self.test_result(f"Import {module_name}.{class_name}", True, "Successfully imported")
            except ImportError as e:
                self.test_result(f"Import {module_name}.{class_name}", False, f"Import error: {e}")
            except AttributeError as e:
                self.test_result(f"Import {module_name}.{class_name}", False, f"Class not found: {e}")
            except Exception as e:
                self.test_result(f"Import {module_name}.{class_name}", False, f"Unexpected error: {e}")
    
    def test_inheritance(self):
        """Test that all handlers inherit from BaseActionHandler properly"""
        print("🔍 Testing inheritance hierarchy...")
        
        try:
            from flet_server_gui.components.base_action_handler import BaseActionHandler
            from flet_server_gui.components.client_action_handlers import ClientActionHandlers
            from flet_server_gui.components.database_action_handlers import DatabaseActionHandlers
            from flet_server_gui.components.log_action_handlers import LogActionHandlers
            
            # Test inheritance
            handlers = [
                ("ClientActionHandlers", ClientActionHandlers),
                ("DatabaseActionHandlers", DatabaseActionHandlers), 
                ("LogActionHandlers", LogActionHandlers)
            ]
            
            for name, handler_class in handlers:
                is_subclass = issubclass(handler_class, BaseActionHandler)
                self.test_result(f"{name} inherits from BaseActionHandler", is_subclass)
                
                # Check if execute_action method is available
                has_execute_action = hasattr(handler_class, 'execute_action')
                self.test_result(f"{name} has execute_action method", has_execute_action)
                
        except Exception as e:
            self.test_result("Inheritance testing", False, f"Error: {e}")
    
    def test_action_classes(self):
        """Test that action classes are properly structured"""
        print("🔍 Testing action classes...")
        
        try:
            from flet_server_gui.actions import ClientActions, DatabaseActions, LogActions
            
            # Test action classes have required methods
            action_tests = [
                (ClientActions, ["disconnect_client", "delete_client", "get_client_details"]),
                (DatabaseActions, ["backup_database", "optimize_database", "analyze_database"]),
                (LogActions, ["export_logs", "clear_logs", "filter_logs", "search_logs"])
            ]
            
            for action_class, required_methods in action_tests:
                class_name = action_class.__name__
                
                for method_name in required_methods:
                    has_method = hasattr(action_class, method_name)
                    self.test_result(f"{class_name}.{method_name} exists", has_method)
                    
                    if has_method:
                        method = getattr(action_class, method_name)
                        is_callable = callable(method)
                        self.test_result(f"{class_name}.{method_name} is callable", is_callable)
                        
        except Exception as e:
            self.test_result("Action classes testing", False, f"Error: {e}")
    
    def test_method_signatures(self):
        """Test that refactored methods have consistent signatures"""
        print("🔍 Testing method signatures...")
        
        try:
            from flet_server_gui.components.client_action_handlers import ClientActionHandlers
            from flet_server_gui.components.database_action_handlers import DatabaseActionHandlers
            from flet_server_gui.components.log_action_handlers import LogActionHandlers
            
            # Test that key methods exist and are async
            methods_to_test = [
                (ClientActionHandlers, ["view_client_details", "disconnect_client", "delete_client"]),
                (DatabaseActionHandlers, ["backup_database", "optimize_database", "analyze_database"]),
                (LogActionHandlers, ["export_logs", "clear_logs", "refresh_logs"])
            ]
            
            for handler_class, methods in methods_to_test:
                class_name = handler_class.__name__
                
                for method_name in methods:
                    if hasattr(handler_class, method_name):
                        method = getattr(handler_class, method_name)
                        is_async = inspect.iscoroutinefunction(method)
                        self.test_result(f"{class_name}.{method_name} is async", is_async)
                    else:
                        self.test_result(f"{class_name}.{method_name} exists", False, "Method not found")
                        
        except Exception as e:
            self.test_result("Method signatures testing", False, f"Error: {e}")
    
    def test_module_exports(self):
        """Test that modules export classes correctly"""
        print("🔍 Testing module exports...")
        
        try:
            # Test actions module exports
            from flet_server_gui.actions import ClientActions, DatabaseActions, LogActions
            self.test_result("Actions module exports", True, "All action classes exported")
            
            # Test components module exports
            from flet_server_gui.components import BaseActionHandler, UIActionMixin
            self.test_result("Components module exports", True, "Base classes exported")
            
        except ImportError as e:
            self.test_result("Module exports", False, f"Import error: {e}")
        except Exception as e:
            self.test_result("Module exports", False, f"Error: {e}")
    
    def test_action_executor_integration(self):
        """Test ActionExecutor integration"""
        print("🔍 Testing ActionExecutor integration...")
        
        try:
            from flet_server_gui.utils.action_executor import get_action_executor
            
            # Test ActionExecutor can be retrieved
            executor = get_action_executor()
            self.test_result("ActionExecutor retrieval", executor is not None)
            
            if executor:
                # Test key methods exist
                key_methods = ["run", "run_with_confirmation", "set_dialog_system", "add_data_change_callback"]
                for method_name in key_methods:
                    has_method = hasattr(executor, method_name)
                    self.test_result(f"ActionExecutor.{method_name} exists", has_method)
                    
        except Exception as e:
            self.test_result("ActionExecutor integration", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Consolidated Action Handler Integration Tests")
        print("=" * 60)
        
        # Run test suites
        self.test_imports()
        self.test_inheritance()
        self.test_action_classes()
        self.test_method_signatures()
        self.test_module_exports()
        self.test_action_executor_integration()
        
        # Print results
        print("\\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        
        for result in self.results:
            print(result)
        
        print("\\n" + "=" * 60)
        print(f"🎯 SUMMARY: {self.passed} passed, {self.failed} failed")
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED! The consolidated architecture is working correctly.")
            return True
        else:
            print(f"⚠️  {self.failed} test(s) failed. Please review the issues above.")
            return False

if __name__ == "__main__":
    test_suite = ConsolidationTest()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
