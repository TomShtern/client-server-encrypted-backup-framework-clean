#!/usr/bin/env python3
"""
Simple test script to verify Phase 5 components
"""

import sys
import os

# Add the project directory to the path
project_root = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(project_root)
sys.path.insert(0, parent_dir)

def test_performance_manager():
    """Test performance manager import"""
    try:
        from flet_server_gui.utils.performance_manager import PerformanceManager
        pm = PerformanceManager()
        print("PerformanceManager imported and instantiated successfully")
        return True
    except Exception as e:
        print(f"PerformanceManager test failed: {e}")
        return False

def test_test_gui_integration():
    """Test test_gui_integration import"""
    try:
        import tests.test_gui_integration
        print("test_gui_integration imported successfully")
        return True
    except Exception as e:
        print(f"test_gui_integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Phase 5 Component Verification")
    print("=" * 40)
    
    tests = [
        ("Performance Manager", test_performance_manager),
        ("Test GUI Integration", test_test_gui_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        if test_func():
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll Phase 5 components are working correctly!")
        return 0
    else:
        print("\nSome components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())