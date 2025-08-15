#!/usr/bin/env python3
"""
Test script to verify all fixes are working properly
"""

import os
import sys
import subprocess

import socket
from pathlib import Path

# Change to project root
project_root = Path(__file__).parent.parent
os.chdir(project_root)

def test_imports():
    """Test that critical imports work"""
    print("Testing imports...")
    
    tests = [
        ("GUI integration with GUI disabled", 
         "import os; os.environ['CYBERBACKUP_DISABLE_GUI']='1'; from python_server.server.gui_integration import GUIManager; print('SUCCESS')"),
        ("API server imports",
         "import sys; sys.path.insert(0, '.'); from api_server.cyberbackup_api_server import app; print('SUCCESS')"),
        ("Backup executor imports", 
         "import sys; sys.path.insert(0, '.'); from api_server.real_backup_executor import RealBackupExecutor; print('SUCCESS')")
    ]
    
    for name, test_code in tests:
        try:
            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10,
                cwd=project_root
            )
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ {name}: EXCEPTION - {e}")

def test_port_availability():
    """Test if ports are available"""
    print("\nTesting port availability...")
    
    for port, service in [(1256, "Backup Server"), (9090, "API Server")]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('127.0.0.1', port))
                print(f"✅ Port {port} ({service}): AVAILABLE")
        except OSError:
            print(f"❌ Port {port} ({service}): IN USE")

def test_file_paths():
    """Test that required files exist"""
    print("\nTesting file paths...")
    
    required_files = [
        "python_server/server/server.py",
        "api_server/cyberbackup_api_server.py", 
        "scripts/fixed_launcher.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}: EXISTS")
        else:
            print(f"❌ {file_path}: MISSING")

def test_cpp_client():
    """Test C++ client availability"""
    print("\nTesting C++ client...")
    
    possible_paths = [
        "build/Release/EncryptedBackupClient.exe",
        "build/EncryptedBackupClient.exe", 
        "Client/EncryptedBackupClient.exe"
    ]
    
    found = False
    for path_str in possible_paths:
        path = Path(path_str)
        if path.exists():
            print(f"✅ C++ client found: {path}")
            found = True
            break
    
    if not found:
        print("❌ C++ client not found")
        print("   Build with: cmake --build build --config Release")

def main():
    print("=" * 60)
    print("   TESTING CYBERBACKUP FIXES")
    print("=" * 60)
    
    test_imports()
    test_port_availability()
    test_file_paths()
    test_cpp_client()
    
    print("\n" + "=" * 60)
    print("Test completed. If all tests pass, run:")
    print("   python scripts/fixed_launcher.py")
    print("=" * 60)

if __name__ == "__main__":
    main()