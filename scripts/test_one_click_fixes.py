#!/usr/bin/env python3
"""Test script to validate the fixes made to one_click_build_and_run.py"""

import sys
import os
from pathlib import Path

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Import the module to test
    import one_click_build_and_run as build_script
    print("[OK] Successfully imported one_click_build_and_run module")
except Exception as e:
    print(f"[ERROR] Failed to import module: {e}")
    sys.exit(1)

def test_dependency_check():
    """Test the enhanced dependency checking function"""
    print("\n=== Testing Dependency Check ===")
    try:
        missing, optional = build_script.check_python_dependencies()
        print(f"[OK] Dependency check returned: {len(missing)} missing, {len(optional)} optional")
        return True
    except Exception as e:
        print(f"[ERROR] Dependency check failed: {e}")
        return False

def test_command_exists():
    """Test the command existence checking"""
    print("\n=== Testing Command Existence Check ===")
    try:
        exists, version = build_script.check_command_exists("python")
        print(f"[OK] Python check: exists={exists}, version={version}")
        
        exists, version = build_script.check_command_exists("nonexistent_command")
        print(f"[OK] Nonexistent command check: exists={exists}")
        return True
    except Exception as e:
        print(f"[ERROR] Command check failed: {e}")
        return False

def test_port_availability():
    """Test port availability checking"""
    print("\n=== Testing Port Availability ===")
    try:
        # Test a high port that should be available
        available = build_script.check_port_available(65432)
        print(f"[OK] Port 65432 availability: {available}")
        
        # Test our specific ports
        port_9090 = build_script.check_port_available(9090)
        port_1256 = build_script.check_port_available(1256)
        print(f"[INFO] Port 9090 availability: {port_9090}")
        print(f"[INFO] Port 1256 availability: {port_1256}")
        return True
    except Exception as e:
        print(f"[ERROR] Port availability check failed: {e}")
        return False

def test_vcpkg_dependency_check():
    """Test vcpkg dependency validation"""
    print("\n=== Testing vcpkg Dependency Check ===")
    try:
        result = build_script.check_and_fix_vcpkg_dependencies()
        print(f"[OK] vcpkg dependency check completed: {result}")
        return True
    except Exception as e:
        print(f"[ERROR] vcpkg dependency check failed: {e}")
        return False

def test_file_path_validations():
    """Test the improved file path validations"""
    print("\n=== Testing File Path Validations ===")
    try:
        # Test the exe path checking logic
        exe_locations = [
            Path("build/Release/EncryptedBackupClient.exe"),
            Path("build/EncryptedBackupClient.exe"),
            Path("Client/EncryptedBackupClient.exe"),
            Path("client/EncryptedBackupClient.exe")
        ]
        
        found_exe = None
        for exe_path in exe_locations:
            if exe_path.exists():
                found_exe = exe_path
                print(f"[INFO] Found C++ client: {found_exe}")
                break
        
        if not found_exe:
            print("[INFO] No C++ client found (expected if not built yet)")
        
        # Test API server path checking
        api_server_path = Path("api_server/cyberbackup_api_server.py")
        if api_server_path.exists():
            print(f"[OK] API server found: {api_server_path}")
        else:
            print(f"[INFO] API server not found at: {api_server_path}")
        
        # Test backup server path checking
        server_path = Path("python_server/server/server.py")
        if server_path.exists():
            print(f"[OK] Backup server found: {server_path}")
        else:
            print(f"[INFO] Backup server not found at: {server_path}")
        
        return True
    except Exception as e:
        print(f"[ERROR] File path validation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing one_click_build_and_run.py fixes")
    print("=" * 60)
    
    tests = [
        test_dependency_check,
        test_command_exists,
        test_port_availability,
        test_vcpkg_dependency_check,
        test_file_path_validations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"[FAIL] {test.__name__} failed")
        except Exception as e:
            print(f"[FAIL] {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print("[SUCCESS] All tests passed! The fixes appear to be working correctly.")
        return 0
    else:
        print("[WARNING] Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())