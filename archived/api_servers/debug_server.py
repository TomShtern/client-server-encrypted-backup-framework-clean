#!/usr/bin/env python3
"""
⚠️  DEPRECATED AND ARCHIVED ⚠️

This file has been ARCHIVED and is no longer maintained.

REASON FOR ARCHIVAL:
- Was a debugging tool for isolating 500 errors in /api/status endpoint
- Issues have been resolved in the main API server
- Runs on different port (9091) and has limited functionality

USE INSTEAD:
- cyberbackup_api_server.py (project root)

ARCHIVED DATE: 2025-01-09
ARCHIVAL REASON: Unify API server entrypoint and eliminate duplicates

DO NOT USE THIS FILE - IT IS FOR DEBUGGING ONLY

Original Description:
Debug server to isolate the 500 error in the /api/status endpoint
"""

import sys
print("⚠️  WARNING: This API server has been DEPRECATED and ARCHIVED")
print("⚠️  This was a debugging tool only - use cyberbackup_api_server.py instead")
print("⚠️  The issues this was debugging have been resolved")
sys.exit(1)

import os
import sys
import socket
import traceback
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import the problematic modules
from src.api.real_backup_executor import RealBackupExecutor
from src.server.server_singleton import ensure_single_server_instance

app = Flask(__name__)
CORS(app)

# Global state similar to cyberbackup_api_server.py
backup_executor = RealBackupExecutor()
connection_established = False
backup_status = {
    'connected': False,
    'backing_up': False,
    'phase': 'READY',
    'progress': {'percentage': 0, 'current_file': '', 'bytes_transferred': 0, 'total_bytes': 0},
    'status': 'ready',
    'message': 'Ready for backup',
    'last_updated': datetime.now().isoformat()
}

def check_backup_server_status():
    """Check if the Python backup server is running on port 1256"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 1256))
        sock.close()
        return result == 0
    except Exception:
        return False

@app.route('/api/status')
def api_status():
    """Minimal recreation of the status endpoint that's causing 500 errors"""
    global backup_status, connection_established
    
    print(f"[DEBUG] /api/status called at {datetime.now().isoformat()}")
    
    try:
        # This is the exact logic from cyberbackup_api_server.py
        server_is_reachable = check_backup_server_status()
        print(f"[DEBUG] Backup server reachable: {server_is_reachable}")
        print(f"[DEBUG] Connection established: {connection_established}")
        
        is_connected = server_is_reachable and connection_established
        backup_status['connected'] = is_connected
        backup_status['isConnected'] = is_connected
        
        if is_connected:
            backup_status['status'] = 'connected'
            if backup_status['phase'] == 'READY':
                backup_status['message'] = f'Connected to backup server at 127.0.0.1:1256'
        elif server_is_reachable and not connection_established:
            backup_status['status'] = 'disconnected' 
            backup_status['message'] = 'Server available - click CONNECT to establish connection'
            backup_status['phase'] = 'READY'
        else:
            backup_status['status'] = 'disconnected'
            backup_status['message'] = 'Backup server not responding'
            backup_status['phase'] = 'DISCONNECTED'
            connection_established = False
            
        backup_status['last_updated'] = datetime.now().isoformat()
        
        print(f"[DEBUG] Returning status: connected={backup_status['connected']}")
        return jsonify(backup_status)
        
    except Exception as e:
        print(f"[ERROR] Exception in api_status: {str(e)}")
        print(f"[ERROR] Traceback:")
        traceback.print_exc()
        
        error_response = {
            'connected': False,
            'isConnected': False,
            'status': 'error',
            'message': f'API Error: {str(e)}',
            'phase': 'ERROR',
            'last_updated': datetime.now().isoformat()
        }
        return jsonify(error_response), 500

if __name__ == "__main__":
    print("Debug API Server - Testing /api/status endpoint")
    print("Starting on port 9091 to avoid conflicts...")
    
    try:
        app.run(
            host='127.0.0.1',
            port=9091,
            debug=False,  # Disable debug mode to avoid extra output
            threaded=True
        )
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()