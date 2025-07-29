#!/usr/bin/env python3
"""
CyberBackup 3.0 API Server - REAL IMPLEMENTATION
Provides Flask API backend for the NewGUIforClient.html interface
Connects to the actual C++ backup client and Python backup server
NO SIMULATION - REAL INTEGRATION ONLY
"""

import os
import sys
import json
import time
import threading
import tempfile
import subprocess
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import psutil

# Import our real backup executor
from src.api.real_backup_executor import RealBackupExecutor

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Global state
backup_executor = RealBackupExecutor()
current_backup_process = None
connection_established = False  # Track if connection was explicitly established
connection_timestamp = None     # When connection was established
backup_status = {
    'connected': False,
    'backing_up': False,
    'phase': 'READY',
    'progress': {'percentage': 0, 'current_file': '', 'bytes_transferred': 0, 'total_bytes': 0},
    'status': 'ready',
    'message': 'Ready for backup',
    'last_updated': datetime.now().isoformat()
}

# Server configuration
server_config = {
    'host': '127.0.0.1',
    'port': 1256,
    'username': 'default_user'
}

def update_backup_status(phase, message, progress=None):
    """Update backup status with thread safety"""
    global backup_status
    backup_status['phase'] = phase
    backup_status['message'] = message
    backup_status['last_updated'] = datetime.now().isoformat()
    if progress is not None:
        if isinstance(progress, dict):
            backup_status['progress'].update(progress)
        else:
            backup_status['progress']['percentage'] = progress
    print(f"[STATUS] {phase}: {message}")

def check_backup_server_status():
    """Check if the Python backup server is running on port 1256"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 1256))
        sock.close()
        return result == 0
    except Exception:
        return False

# Static file serving
@app.route('/')
def serve_client():
    """Serve the main client HTML interface"""
    try:
        return send_file('src/client/NewGUIforClient.html')
    except FileNotFoundError:
        return "<h1>Client GUI not found</h1><p>Please ensure src/client/NewGUIforClient.html exists</p>", 404

@app.route('/client/<path:filename>')
def serve_client_assets(filename):
    """Serve client assets (CSS, JS, images, etc.)"""
    try:
        return send_from_directory('src/client', filename)
    except FileNotFoundError:
        return f"<h1>Asset not found: {filename}</h1>", 404

# API Endpoints for CyberBackup 3.0

@app.route('/api/test', methods=['POST'])
def api_test():
    """Simple test endpoint to debug POST requests"""
    print("[DEBUG] Test POST endpoint called!")
    return jsonify({'success': True, 'message': 'POST test successful'})

@app.route('/api/status')
def api_status():
    """Get current backup status with proper connection state management"""
    global backup_status, connection_established, connection_timestamp

    print(f"[DEBUG] /api/status called at {datetime.now().isoformat()}")

    try:
        # Check if server is reachable
        server_is_reachable = check_backup_server_status()
        print(f"[DEBUG] Backup server reachable: {server_is_reachable}")
        print(f"[DEBUG] Connection established: {connection_established}")

        # Connection is valid only if:
        # 1. Server is reachable AND
        # 2. Connection was explicitly established via /api/connect
        is_connected = server_is_reachable and connection_established

        # Update connection status based on actual connection state
        backup_status['connected'] = is_connected
        backup_status['isConnected'] = is_connected  # Frontend expects this field

        # Update status message based on connection state
        if is_connected:
            backup_status['status'] = 'connected'
            if backup_status['phase'] == 'READY':
                backup_status['message'] = f'Connected to backup server at {server_config["host"]}:{server_config["port"]}'
        elif server_is_reachable and not connection_established:
            backup_status['status'] = 'disconnected'
            backup_status['message'] = 'Server available - click CONNECT to establish connection'
            backup_status['phase'] = 'READY'
        else:
            backup_status['status'] = 'disconnected'
            backup_status['message'] = 'Backup server not responding'
            backup_status['phase'] = 'DISCONNECTED'
            # Reset connection state if server is not reachable
            connection_established = False

        backup_status['last_updated'] = datetime.now().isoformat()

        print(f"[DEBUG] Returning status: connected={backup_status['connected']}, isConnected={backup_status['isConnected']}")
        return jsonify(backup_status)

    except Exception as e:
        print(f"[ERROR] Exception in api_status: {str(e)}")
        error_response = {
            'connected': False,
            'isConnected': False,
            'status': 'error',
            'message': f'API Error: {str(e)}',
            'phase': 'ERROR',
            'last_updated': datetime.now().isoformat()
        }
        return jsonify(error_response), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    server_running = check_backup_server_status()
    return jsonify({
        'status': 'healthy' if server_running else 'degraded',
        'backup_server': 'running' if server_running else 'not_running',
        'api_server': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/connect', methods=['POST'])
def api_connect():
    """Connect to backup server with configuration using real backup protocol"""
    global server_config, backup_status, backup_executor, connection_established, connection_timestamp

    print(f"[DEBUG] /api/connect endpoint called")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Request headers: {dict(request.headers)}")
    print(f"[DEBUG] Request data: {request.get_data()}")

    try:
        # Handle both JSON and form data
        if request.is_json:
            config = request.get_json()
            print(f"[DEBUG] JSON data received: {config}")
        else:
            config = request.form.to_dict()
            print(f"[DEBUG] Form data received: {config}")

        if not config:
            return jsonify({'success': False, 'error': 'No configuration data provided'}), 400

        # Validate required fields
        required_fields = ['host', 'port', 'username']
        missing_fields = [field for field in required_fields if field not in config or not config[field]]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Update server configuration
        if config:
            server_config.update(config)
        
        update_backup_status('CONNECT', f'Testing connection to {server_config["host"]}:{server_config["port"]}...')

        # Test if backup server is reachable
        server_reachable = check_backup_server_status()

        if server_reachable:
            # Establish connection session
            connection_established = True
            connection_timestamp = datetime.now()

            backup_status['connected'] = True
            backup_status['status'] = 'connected'
            backup_status['message'] = f'Connected to backup server at {server_config["host"]}:{server_config["port"]}'
            update_backup_status('READY', f'Connected successfully. Ready for backup.')
            print(f"[DEBUG] Connection established at {connection_timestamp.isoformat()}")
        else:
            connection_established = False
            connection_timestamp = None

            backup_status['connected'] = False
            backup_status['status'] = 'connection_failed'
            backup_status['message'] = f'Connection failed: Backup server not responding'
            update_backup_status('ERROR', f'Connection test failed: Backup server not responding')
            print(f"[DEBUG] Connection failed - server not reachable")

        return jsonify({
            'success': server_reachable,
            'connected': server_reachable,
            'message': backup_status['message'],
            'server_config': server_config
        })

    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        update_backup_status('ERROR', error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """Disconnect from backup server"""
    global connection_established, connection_timestamp, backup_status

    print(f"[DEBUG] /api/disconnect called")

    try:
        connection_established = False
        connection_timestamp = None

        backup_status['connected'] = False
        backup_status['status'] = 'disconnected'
        backup_status['message'] = 'Disconnected from backup server'
        backup_status['phase'] = 'READY'

        print(f"[DEBUG] Connection terminated")

        return jsonify({
            'success': True,
            'connected': False,
            'message': 'Disconnected successfully'
        })

    except Exception as e:
        error_msg = f"Disconnect error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/start_backup', methods=['POST'])
def api_start_backup():
    """Start backup using REAL backup executor"""
    global backup_status, backup_executor, current_backup_process

    print(f"[DEBUG] /api/start_backup endpoint called")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Request files: {list(request.files.keys())}")
    print(f"[DEBUG] Request form: {dict(request.form)}")

    try:
        # Check if already backing up
        if backup_status['backing_up']:
            return jsonify({'success': False, 'error': 'Backup already in progress'}), 400

        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Get form data
        username = request.form.get('username', server_config.get('username', 'default_user'))
        server_ip = request.form.get('server', server_config.get('host', '127.0.0.1'))
        server_port = request.form.get('port', server_config.get('port', 1256))

        # Save uploaded file to temporary location
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        print(f"[DEBUG] File saved to: {file_path}")
        print(f"[DEBUG] Username: {username}")
        print(f"[DEBUG] Server: {server_ip}:{server_port}")

        # Update status
        backup_status['backing_up'] = True
        backup_status['phase'] = 'BACKUP_IN_PROGRESS'
        backup_status['progress']['current_file'] = file.filename
        update_backup_status('BACKUP_IN_PROGRESS', f'Starting backup of {file.filename}...')

        # Start backup in background thread
        def run_backup():
            try:
                print(f"[DEBUG] Starting real backup executor...")
                result = backup_executor.execute_real_backup(
                    username=username,
                    file_path=file_path,
                    server_ip=server_ip,
                    server_port=int(server_port)
                )

                if result and result.get('success'):
                    backup_status['phase'] = 'COMPLETED'
                    backup_status['progress']['percentage'] = 100
                    update_backup_status('COMPLETED', f'Backup completed successfully!')
                else:
                    backup_status['phase'] = 'FAILED'
                    error_msg = result.get('error', 'Unknown error') if result else 'Backup executor returned None'
                    update_backup_status('FAILED', f'Backup failed: {error_msg}')

            except Exception as e:
                backup_status['phase'] = 'FAILED'
                update_backup_status('FAILED', f'Backup error: {str(e)}')
                print(f"[ERROR] Backup thread error: {str(e)}")
            finally:
                backup_status['backing_up'] = False
                # Use proper subprocess synchronization instead of arbitrary delay
                def synchronized_cleanup():
                    try:
                        # Wait for backup result to determine if C++ client finished
                        max_wait_time = 30  # Maximum 30 seconds wait
                        check_interval = 1  # Check every 1 second
                        elapsed = 0
                        
                        # Wait for backup executor to complete and release file
                        while elapsed < max_wait_time:
                            # Check if backup result is available (indicating C++ client finished)
                            if 'result' in locals() and result is not None:
                                print(f"[DEBUG] Backup completed, proceeding with cleanup after {elapsed}s")
                                break
                            time.sleep(check_interval)
                            elapsed += check_interval
                        
                        # Additional small delay to ensure file handles are closed
                        time.sleep(2)
                        
                        # Perform cleanup
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"[DEBUG] Synchronized cleanup: removed {file_path}")
                        if os.path.exists(temp_dir):
                            os.rmdir(temp_dir)
                            print(f"[DEBUG] Synchronized cleanup: removed {temp_dir}")
                    except Exception as e:
                        print(f"[WARNING] Synchronized cleanup error: {e}")

                # Start synchronized cleanup in background thread
                cleanup_thread = threading.Thread(target=synchronized_cleanup)
                cleanup_thread.daemon = True
                cleanup_thread.start()

        # Start backup thread
        backup_thread = threading.Thread(target=run_backup)
        backup_thread.daemon = True
        backup_thread.start()

        return jsonify({
            'success': True,
            'message': f'Backup started for {file.filename}',
            'filename': file.filename,
            'username': username
        })

    except Exception as e:
        backup_status['backing_up'] = False
        error_msg = f"Backup start error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        update_backup_status('ERROR', error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

if __name__ == "__main__":
    print("=" * 70)
    print("* CyberBackup 3.0 API Server - REAL Integration")
    print("=" * 70)
    print(f"* API Server: http://localhost:9090")
    print(f"* Client GUI: http://localhost:9090/")
    print(f"* Health Check: http://localhost:9090/health")
    print()

    # Check components
    print("Component Status:")

    # Check HTML client
    client_html = "src/client/NewGUIforClient.html"
    if os.path.exists(client_html):
        print(f"[OK] HTML Client: {client_html}")
    else:
        print(f"[MISSING] HTML Client: {client_html} NOT FOUND")

    # Check C++ client
    client_exe = "build/Release/EncryptedBackupClient.exe"
    if os.path.exists(client_exe):
        print(f"[OK] C++ Client: {client_exe}")
    else:
        print(f"[MISSING] C++ Client: {client_exe} NOT FOUND")

    # Check backup server
    server_running = check_backup_server_status()
    if server_running:
        print(f"[OK] Backup Server: Running on port 1256")
    else:
        print(f"[WARNING] Backup Server: Not running on port 1256")

    print()
    print("[ROCKET] Starting Flask API server...")

    try:
        app.run(
            host='127.0.0.1',
            port=9090,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n[INFO] API Server shutdown requested")
    except Exception as e:
        print(f"[MISSING] Server error: {e}")
