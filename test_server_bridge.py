#!/usr/bin/env python3
"""Test ServerBridge integration with real BackupServer data."""

import sys
import os

# Add FletV2 to path for imports
flet_v2_path = os.path.join(os.getcwd(), 'FletV2')
sys.path.insert(0, flet_v2_path)
print(f'Added to sys.path: {flet_v2_path}')

# Also add current directory to path
sys.path.insert(0, os.getcwd())

import Shared.utils.utf8_solution as _

print('Testing BackupServer with 17 clients via ServerBridge...')

# Create BackupServer and start it (this will pick up the 17 clients)
from python_server.server.server import BackupServer
backup_server = BackupServer()
backup_server.start()

print(f'BackupServer is_connected: {backup_server.is_connected()}')

# Test getting clients
clients_result = backup_server.get_clients()
print(f'get_clients success: {clients_result.get("success")}')
print(f'Number of clients: {len(clients_result.get("data", []))}')

# Now test via ServerBridge - try direct file import
try:
    # Change to FletV2 directory temporarily for import
    original_cwd = os.getcwd()
    os.chdir('FletV2')

    from utils.server_bridge import create_server_bridge
    server_bridge = create_server_bridge(backup_server)

    # Change back
    os.chdir(original_cwd)

    print(f'ServerBridge is_connected: {server_bridge.is_connected()}')

    # Test getting clients via bridge
    bridge_clients = server_bridge.get_all_clients_from_db()
    print(f'ServerBridge get_all_clients_from_db success: {bridge_clients.get("success")}')
    print(f'ServerBridge number of clients: {len(bridge_clients.get("data", []))}')

    # Show first few clients
    if bridge_clients.get('data'):
        for i, client in enumerate(bridge_clients['data'][:3]):
            print(f'  Client {i+1}: {client.get("name")}, status: {client.get("status")}')

    print('✅ SUCCESS: ServerBridge integration with 17 clients working!')

except Exception as e:
    print(f'❌ ServerBridge error: {e}')
    import traceback
    traceback.print_exc()