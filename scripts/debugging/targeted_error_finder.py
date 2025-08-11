#!/usr/bin/env python3
"""
Quick targeted error finder - focuses on specific runtime issues
"""

import sys
import os
import importlib.util

# Setup standardized import paths
from Shared.path_utils import setup_imports
setup_imports()

def test_server_gui_import():
    """Test ServerGUI imports"""
    print("Testing ServerGUI imports...")
    try:
        from ServerGUI import (
            ServerGUI, ModernCard, ModernProgressBar, ModernStatusIndicator,
            ModernTheme, ToastNotification, ModernTable, SettingsDialog,
            ModernChart, initialize_server_gui, get_server_gui, shutdown_server_gui
        )
        print("✓ All ServerGUI imports successful")
        return True
    except Exception as e:
        print(f"✗ ServerGUI import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_other_files():
    """Test other Python files for import issues"""
    files_to_test = [
        'config_manager.py',
        'comprehensive_test_suite.py',
        'quick_validation.py'
    ]
    
    results = []
    for file in files_to_test:
        if os.path.exists(file):
            print(f"Testing {file}...")
            try:
                spec = importlib.util.spec_from_file_location("test_module", file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✓ {file} imports successfully")
                results.append(f"✓ {file}")
            except Exception as e:
                print(f"✗ {file} error: {e}")
                results.append(f"✗ {file}: {e}")
        else:
            print(f"? {file} not found")
            results.append(f"? {file} not found")
    
    return results

def test_minimal_functionality():
    """Test minimal ServerGUI functionality"""
    print("\nTesting minimal ServerGUI functionality...")
    try:
        from ServerGUI import ServerGUI
        
        # Create instance
        gui = ServerGUI()
        print("✓ ServerGUI instance created")
        
        # Test basic methods
        gui.update_server_status(True, "127.0.0.1", 1256)
        print("✓ update_server_status works")
        
        gui.update_client_stats(5, 10, 2)
        print("✓ update_client_stats works")
        
        gui.update_transfer_stats(1024, "now")
        print("✓ update_transfer_stats works")
        
        gui.show_error("test error")
        print("✓ show_error works")
        
        gui.show_success("test success")
        print("✓ show_success works")
        
        gui.show_info("test info")
        print("✓ show_info works")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_syntax_errors():
    """Check for syntax errors in Python files"""
    print("\nChecking Python files for syntax errors...")
    import py_compile
    
    python_files = [
        'server/ServerGUI.py',
        'config_manager.py',
        'comprehensive_test_suite.py',
        'comprehensive_test_gui.py',
        'demo_server_gui.py',
        'find_gui_errors.py',
        'validate_server_gui.py',
        'test_server_gui.py'
    ]
    
    results = []
    for file in python_files:
        if os.path.exists(file):
            try:
                py_compile.compile(file, doraise=True)
                print(f"✓ {file} - No syntax errors")
                results.append(f"✓ {file}")
            except py_compile.PyCompileError as e:
                print(f"✗ {file} - Syntax error: {e}")
                results.append(f"✗ {file}: {e}")
        else:
            print(f"? {file} not found")
            results.append(f"? {file} not found")
    
    return results

def main():
    print("🎯 TARGETED ERROR DETECTION")
    print("=" * 50)
    
    # Test 1: Check syntax errors
    syntax_results = check_syntax_errors()
    
    # Test 2: Test ServerGUI import
    import_success = test_server_gui_import()
    
    # Test 3: Test other files
    other_results = test_other_files()
    
    # Test 4: Test basic functionality (only if import successful)
    func_success = False
    if import_success:
        func_success = test_minimal_functionality()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    print("\nSyntax check results:")
    for result in syntax_results:
        print(f"  {result}")
    
    print(f"\nServerGUI import: {'✓ SUCCESS' if import_success else '✗ FAILED'}")
    
    print("\nOther files:")
    for result in other_results:
        print(f"  {result}")
    
    print(f"\nFunctionality test: {'✓ SUCCESS' if func_success else '✗ FAILED'}")
    
    # Count issues
    syntax_errors = len([r for r in syntax_results if r.startswith('✗')])
    other_errors = len([r for r in other_results if r.startswith('✗')])
    
    total_errors = syntax_errors + other_errors + (0 if import_success else 1) + (0 if func_success else 1)
    
    if total_errors == 0:
        print(f"\n🎉 NO ERRORS FOUND! All tests passed.")
    else:
        print(f"\n❌ FOUND {total_errors} ERRORS that need to be fixed.")

if __name__ == "__main__":
    main()
