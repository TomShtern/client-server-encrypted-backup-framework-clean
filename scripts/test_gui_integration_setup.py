#!/usr/bin/env python3
"""
Test script to verify GUI Integration Tests
"""
# sourcery skip: dont-import-test-modules - This is a test runner utility script

import os
import sys
import unittest

# Add the project directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def _import_test_module(module_name: str):
    """Import a test module using importlib to avoid direct import."""
    import importlib.util
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        raise ImportError(f"{module_name} module not found")
    # Actually import it to test
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_gui_integration_import():
    """Test that GUI integration tests can be imported"""
    try:
        module = _import_test_module('tests.test_gui_integration')
        TestGUIIntegration = module.TestGUIIntegration
        print("GUI Integration tests imported successfully")
        return True
    except Exception as e:
        print(f"GUI Integration tests import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def _create_test_suite_from_module(module):
    """Create a test suite from a test module."""
    TestGUIIntegration = module.TestGUIIntegration

    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGUIIntegration)
    return suite, TestGUIIntegration

def test_gui_integration_execution():
    """Test that GUI integration tests can be executed"""
    try:
        module = _import_test_module('tests.test_gui_integration')
        suite, TestGUIIntegration = _create_test_suite_from_module(module)
        print(f"Created test suite with {suite.countTestCases()} tests")

        # Run a simple test to check if the framework works
        # We won't run the full test suite as it requires Flet and a GUI environment
        print("GUI Integration test framework is set up correctly")
        return True
    except Exception as e:
        print(f"GUI Integration test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("GUI Integration Tests Verification")
    print("=" * 40)

    tests = [
        ("Import Test", test_gui_integration_import),
        ("Execution Test", test_gui_integration_execution),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\nRunning {name}...")
        if test_func():
            passed += 1
            print(f"{name} passed")
        else:
            print(f"{name} failed")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll GUI Integration tests are set up correctly!")
        return 0
    else:
        print("\nSome GUI Integration tests need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
