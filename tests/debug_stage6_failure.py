#!/usr/bin/env python3
"""
DEBUG SCRIPT: Diagnose Stage 6/7 Failures in one_click_build_and_run.py
This script mimics the exact subprocess calls from stage 6/7 but with enhanced error capture
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path

def check_port_available(port):
    """Check if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except Exception as e:
        return False, str(e)

def check_dependencies():
    """Check required Python dependencies"""
    required_modules = ['flask', 'flask_cors', 'psutil', 'cryptography']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"[OK] {module} is available")
        except ImportError as e:
            missing_modules.append(module)
            print(f"[ERROR] {module} is missing: {e}")
    
    return missing_modules

def test_server_module():
    """Test if the server module can be imported"""
    try:
        # Change to project root
        project_root = Path(__file__).parent
        os.chdir(project_root)
        from Shared.path_utils import setup_imports
        setup_imports()
        
        print(f"Working directory: {os.getcwd()}")
        
        # Try to import the server module
        import python_server.server.server
        print("[OK] python_server.server.server module imports successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Cannot import python_server.server.server: {e}")
        return False

def test_api_server():
    """Test if the API server file can be executed"""
    try:
        api_server_path = Path("cyberbackup_api_server.py")
        if not api_server_path.exists():
            print(f"[ERROR] API server file not found: {api_server_path}")
            return False
        
        # Test syntax by compiling the file
        with open(api_server_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        compile(content, str(api_server_path), 'exec')
        print("[OK] cyberbackup_api_server.py has valid syntax")
        return True
    except Exception as e:
        print(f"[ERROR] cyberbackup_api_server.py syntax error: {e}")
        return False

def test_subprocess_calls():
    """Test the exact subprocess calls from the script with error capture"""
    print("\n" + "="*60)
    print("TESTING SUBPROCESS CALLS (with error capture)")
    print("="*60)
    
    # Test 1: Backup Server Command
    print("\n1. Testing Backup Server Command:")
    print("   Command: python -m python_server.server.server")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "python_server.server.server"],
            timeout=5,  # 5 second timeout
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        print(f"   Exit Code: {result.returncode}")
        if result.stdout:
            print(f"   STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"   STDERR:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   [INFO] Command timed out after 5s (server may be starting normally)")
    except Exception as e:
        print(f"   [ERROR] Command failed: {e}")
    
    # Test 2: API Server Command
    print("\n2. Testing API Server Command:")
    print("   Command: python cyberbackup_api_server.py")
    
    try:
        result = subprocess.run(
            [sys.executable, "cyberbackup_api_server.py"],
            timeout=5,  # 5 second timeout
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        print(f"   Exit Code: {result.returncode}")
        if result.stdout:
            print(f"   STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"   STDERR:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   [INFO] Command timed out after 5s (server may be starting normally)")
    except Exception as e:
        print(f"   [ERROR] Command failed: {e}")

def main():
    print("STAGE 6/7 FAILURE DIAGNOSTIC SCRIPT")
    print("="*50)
    
    # Check 1: Dependencies
    print("\nCHECK 1: Python Dependencies")
    print("-" * 30)
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"\n[CRITICAL] Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return
    
    # Check 2: Port Availability
    print("\nCHECK 2: Port Availability")
    print("-" * 30)
    
    port_1256 = check_port_available(1256)
    port_9090 = check_port_available(9090)
    
    if port_1256 == True:
        print("[OK] Port 1256 is available")
    else:
        print(f"[ERROR] Port 1256 is in use: {port_1256[1] if isinstance(port_1256, tuple) else 'unknown reason'}")
    
    if port_9090 == True:
        print("[OK] Port 9090 is available")
    else:
        print(f"[ERROR] Port 9090 is in use: {port_9090[1] if isinstance(port_9090, tuple) else 'unknown reason'}")
    
    # Check 3: File Existence
    print("\nCHECK 3: Required Files")
    print("-" * 30)
    
    server_file = Path("python_server/server/server.py")
    api_file = Path("cyberbackup_api_server.py")
    
    print(f"Server file: {server_file} - {'EXISTS' if server_file.exists() else 'MISSING'}")
    print(f"API file: {api_file} - {'EXISTS' if api_file.exists() else 'MISSING'}")
    
    # Check 4: Module Import
    print("\nCHECK 4: Module Import")
    print("-" * 30)
    test_server_module()
    
    # Check 5: API Server Syntax
    print("\nCHECK 5: API Server Syntax")
    print("-" * 30)
    test_api_server()
    
    # Check 6: Subprocess Commands
    test_subprocess_calls()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print("If both servers show 'TimeoutExpired', they are likely starting correctly")
    print("but the CMD windows are closing due to other issues.")
    print("\nCommon fixes:")
    print("1. Install missing dependencies: pip install flask flask-cors")
    print("2. Free up ports 1256 and 9090 if they're in use")
    print("3. Check console windows for error messages before they close")
    print("4. Use 'pause' command to keep windows open")

if __name__ == "__main__":
    main()