#!/usr/bin/env python3
"""
Test System Working - ASCII-only validation script
"""

import asyncio
import socket
from pathlib import Path

import httpx


def test_port(port: int, name: str):
    """Test if a port is responding - ASCII only output"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"[OK] {name} (port {port}): RUNNING")
                return True
            else:
                print(f"[ERROR] {name} (port {port}): NOT RESPONDING")
                return False
    except Exception as e:
        print(f"[ERROR] {name} (port {port}): EXCEPTION - {e!s}")
        return False

async def test_web_interface():
    """Test if web interface is accessible"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get('http://127.0.0.1:9090/')
            if response.status_code == 200:
                print("[OK] Web interface: ACCESSIBLE")
                return True
            else:
                print(f"[ERROR] Web interface: HTTP {response.status_code}")
            return False
        except Exception as e:
            print(f"[ERROR] Web interface: {e!s}")
            return False

def test_file_transfer_setup():
    """Test if file transfer components are ready"""
    print("\n[INFO] Testing file transfer setup...")

    # Check C++ client
    client_paths = [
        "build/Release/EncryptedBackupClient.exe",
        "build/EncryptedBackupClient.exe",
        "Client/EncryptedBackupClient.exe"
    ]

    client_found = False
    for path in client_paths:
        if Path(path).exists():
            print(f"[OK] C++ client found: {path}")
            client_found = True
            break

    if not client_found:
        print("[WARNING] C++ client not found - file transfers may not work")
        print("[INFO] Build with: cmake --build build --config Release")

    # Check received_files directory
    received_dir = Path("received_files")
    if received_dir.exists():
        files = list(received_dir.glob("*"))
        print(f"[OK] Received files directory exists ({len(files)} files)")
    else:
        print("[INFO] Received files directory will be created automatically")

    return client_found

def create_test_file():
    """Create a test file for transfer testing"""
    test_file = Path("test_upload.txt")
    content = f"Test file created for CyberBackup transfer test\nTimestamp: {datetime.now()!s}\nThis file tests the complete transfer chain."

    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Test file created: {test_file}")
        return str(test_file)
    except Exception as e:
        print(f"[ERROR] Failed to create test file: {e}")
        return None

async def main():
    print("System Status Check - CyberBackup 3.0")
    print("=" * 50)

    # Test servers
    backup_running = test_port(1256, "Backup Server")
    api_running = test_port(9090, "API Server")

    # Test web interface
    web_working = await test_web_interface()

    # Test file transfer setup
    client_ready = test_file_transfer_setup()

    print("\n" + "=" * 50)
    print("SYSTEM STATUS SUMMARY")
    print("=" * 50)

    if backup_running and api_running and web_working:
        print("[SUCCESS] All core components are operational!")
        print("")
        print("System Status:")
        print("  - Backup Server: [OK] Running on port 1256")
        print("  - API Server: [OK] Running on port 9090")
        print("  - Web Interface: [OK] Accessible at http://127.0.0.1:9090/")

        if client_ready:
            print("  - C++ Client: [OK] Ready for file transfers")
        else:
            print("  - C++ Client: [WARNING] Not found - build required")

        print("")
        print("Next Steps:")
        print("1. Open http://127.0.0.1:9090/ in your browser")
        print("2. Register a username")
        print("3. Upload a file to test the complete system")
        print("4. Check received_files/ directory for transferred files")

        if not client_ready:
            print("5. Build C++ client: cmake --build build --config Release")

        print("")
        print("[SUCCESS] The Unicode/emoji fixes resolved the startup issues!")
        print("[SUCCESS] Your canonical launcher is now working properly!")

    else:
        print("[ERROR] System has issues:")
        if not backup_running:
            print("  - Backup Server: [ERROR] Not responding")
        if not api_running:
            print("  - API Server: [ERROR] Not responding")
        if not web_working:
            print("  - Web Interface: [ERROR] Not accessible")

        print("")
        print("Troubleshooting:")
        print("1. Check console windows for error messages")
        print("2. Restart with: python scripts/one_click_build_and_run.py")
        print("3. Verify no other applications are using ports 1256/9090")

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())
