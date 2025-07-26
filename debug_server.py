#!/usr/bin/env python3
"""
Debug script to run the server with detailed error reporting
"""

import sys
import traceback
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    print("Starting debug server...")

    # Change to server directory
    import os
    os.chdir('server')

    # Add current directory to path
    sys.path.insert(0, '.')

    # Test individual imports
    print("Testing imports...")

    print("1. Testing crypto imports...")
    from crypto_compat import AES, RSA, PKCS1_OAEP, pad, unpad, get_random_bytes
    print("   Crypto imports OK")

    print("2. Testing database import...")
    from database import DatabaseManager
    print("   Database import OK")

    print("3. Testing GUI integration import...")
    from gui_integration import GUIManager
    print("   GUI integration import OK")

    print("4. Testing server import...")
    from server import BackupServer
    print("   Server import OK")

    print("All imports successful!")

    print("\n5. Creating BackupServer instance...")
    server_instance = BackupServer()
    print("   BackupServer created successfully!")

    print("6. Starting server...")
    server_instance.start()
    print("   Server started successfully!")

    print("7. Server is running... (will run for 5 seconds)")
    import time
    time.sleep(5)

    print("8. Stopping server...")
    server_instance.stop()
    print("   Server stopped successfully!")

except Exception as e:
    print(f"ERROR during import: {e}")
    print("Full traceback:")
    traceback.print_exc()
    input("Press Enter to exit...")
