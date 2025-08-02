#!/usr/bin/env python3
"""
CyberBackup 3.0 API Server - REAL IMPLEMENTATION
Provides Flask API backend for the NewGUIforClient.html interface
Connects to the actual C++ backup client and Python backup server
NO SIMULATION - REAL INTEGRATION ONLY
"""

import os
import time
import threading
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Import our real backup executor
from src.api.real_backup_executor import RealBackupExecutor

# Import singleton manager to prevent multiple API server instances
from src.server.server_singleton import ensure_single_server_instance

import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Initialize SocketIO with origin-locked CORS for security
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:9090", "http://127.0.0.1:9090"])

# --- Initialize global variables ---
connection_established = False
connection_timestamp = None
active_backup_jobs = {}
connected_clients = set()
websocket_enabled = True  # Control WebSocket functionality

# Initialize the real backup executor
try:
    backup_executor = RealBackupExecutor()
    print("[OK] RealBackupExecutor initialized successfully.")
except Exception as e:
    print(f"[CRITICAL] Failed to initialize RealBackupExecutor: {e}")
    # Optionally, exit or disable backup functionality
    backup_executor = None


def get_default_status():
    return {
        'connected': False,
        'backing_up': False,
        'phase': 'READY',
        'progress': {'percentage': 0, 'current_file': '', 'bytes_transferred': 0, 'total_bytes': 0},
        'status': 'ready',
        'message': 'Ready for backup',
        'events': [],
        'last_updated': datetime.now().isoformat()
    }

backup_status = get_default_status()

last_known_status = get_default_status() # For providing a consistent default

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

# --- WebSocket Event Handlers ---

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket client connection"""
    # Generate a unique client ID and store it in the session
    client_id = str(uuid.uuid4())
    session['client_id'] = client_id
    connected_clients.add(client_id)
    print(f"[WEBSOCKET] Client connected: {client_id} (Total: {len(connected_clients)})")
    
    # Send initial status to new client
    emit('status', {
        'connected': check_backup_server_status(),
        'server_running': True,
        'timestamp': time.time(),
        'message': 'WebSocket connected - real-time updates enabled'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket client disconnection"""
    client_id = session.get('client_id')
    if client_id:
        connected_clients.discard(client_id)
        print(f"[WEBSOCKET] Client disconnected: {client_id} (Total: {len(connected_clients)})")

@socketio.on('request_status')
def handle_status_request(data):
    """Handle client status requests via WebSocket"""
    job_id = data.get('job_id') if data else None
    status = active_backup_jobs.get(job_id, last_known_status) if job_id else last_known_status
    
    # Always provide the latest connection status
    status['connected'] = check_backup_server_status() and connection_established
    status['isConnected'] = status['connected']
    
    emit('status_response', {
        'status': status,
        'job_id': job_id,
        'timestamp': time.time()
    })

@socketio.on('ping')
def handle_ping():
    """Handle WebSocket ping for connection testing"""
    emit('pong', {'timestamp': time.time()})

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

@app.route('/progress_config.json')
def serve_progress_config():
    """Serve the progress configuration file"""
    try:
        return send_file('progress_config.json')
    except FileNotFoundError:
        return jsonify({'error': 'progress_config.json not found'}), 404

# API Endpoints for CyberBackup 3.0

@app.route('/api/test', methods=['POST'])
def api_test():
    """Simple test endpoint to debug POST requests"""
    print("[DEBUG] Test POST endpoint called!")
    return jsonify({'success': True, 'message': 'POST test successful'})

@app.route('/api/status')
def api_status():
    """Get current backup status with proper connection state management"""
    try:
        global last_known_status, active_backup_jobs

        job_id = request.args.get('job_id')
        status = active_backup_jobs.get(job_id, last_known_status)

        # Always provide the latest connection status
        status['connected'] = check_backup_server_status() and connection_established
        status['isConnected'] = status['connected']

        # Clear events after reading them
        events_to_send = status.get('events', [])
        if job_id and job_id in active_backup_jobs:
            active_backup_jobs[job_id]['events'] = []

        response = status.copy()
        response['events'] = events_to_send

        return jsonify(response)

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
    global backup_status
    
    # Check if backup executor is available
    if backup_executor is None:
        return jsonify({
            'success': False, 
            'error': 'Backup executor not available. Please restart the API server.'
        }), 500
    
    job_id = str(uuid.uuid4())
    active_backup_jobs[job_id] = get_default_status()
    active_backup_jobs[job_id]['backing_up'] = True

    def status_handler(phase, data):
        if job_id in active_backup_jobs:
            active_backup_jobs[job_id]['events'].append({'phase': phase, 'data': data})
            active_backup_jobs[job_id]['phase'] = phase
            
            # Update both job-specific and global backup status
            if isinstance(data, dict):
                message = data.get('message', phase)
                active_backup_jobs[job_id]['message'] = message
                if 'progress' in data:
                    progress_value = data['progress']
                    active_backup_jobs[job_id]['progress']['percentage'] = progress_value
                    # Also update global backup status for unified API
                    update_backup_status(phase, message, progress_value)
                else:
                    update_backup_status(phase, message)
            else:
                active_backup_jobs[job_id]['message'] = data
                update_backup_status(phase, data)
            
            # Real-time WebSocket broadcasting
            if websocket_enabled and connected_clients:
                try:
                    socketio.emit('progress_update', {
                        'job_id': job_id,
                        'phase': phase,
                        'data': data,
                        'timestamp': time.time(),
                        'progress': active_backup_jobs[job_id]['progress']['percentage'] if isinstance(data, dict) and 'progress' in data else None
                    })
                    print(f"[WEBSOCKET] Broadcasted progress update: {phase}")
                except Exception as e:
                    print(f"[WEBSOCKET] Broadcast failed: {e}")

    # Add null check before setting status callback
    if backup_executor is not None:
        backup_executor.set_status_callback(status_handler)
    else:
        return jsonify({
            'success': False, 
            'error': 'Backup executor is not initialized. Cannot start backup.'
        }), 500

    # ... (rest of the function remains the same)


    print(f"[DEBUG] /api/start_backup endpoint called")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Request files: {list(request.files.keys())}")
    print(f"[DEBUG] Request form: {dict(request.form)}")
    print(f"[DEBUG] Content-Type: {request.content_type}")
    print(f"[DEBUG] Request headers: {dict(request.headers)}")
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    print(f"[DEBUG] Client executable path: {backup_executor.client_exe}")
    print(f"[DEBUG] Client executable exists: {os.path.exists(backup_executor.client_exe) if backup_executor.client_exe else 'N/A'}")

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
        # Handle case where file.filename might be None
        filename = file.filename or f"backup_file_{int(time.time())}"
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)

        print(f"[DEBUG] File saved to: {file_path}")
        print(f"[DEBUG] Username: {username}")
        print(f"[DEBUG] Server: {server_ip}:{server_port}")

        # Update status
        backup_status['backing_up'] = True
        backup_status['phase'] = 'BACKUP_IN_PROGRESS'
        backup_status['progress']['current_file'] = filename
        update_backup_status('BACKUP_IN_PROGRESS', f'Starting backup of {filename}...')

        # Start backup in background thread
        def run_backup():
            try:
                print(f"[DEBUG] Starting real backup executor...")
                # Add additional null check before calling execute_real_backup
                if backup_executor is None:
                    update_backup_status('FAILED', 'Backup executor not available')
                    return
                    
                result = backup_executor.execute_real_backup(
                    username=username,
                    file_path=file_path,
                    server_ip=server_ip,
                    server_port=int(server_port)
                )

                if result and result.get('success'):
                    update_backup_status('COMPLETED', 'Backup completed successfully!', 100)
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'Backup executor returned None'
                    update_backup_status('FAILED', f'Backup failed: {error_msg}')

            except Exception as e:
                update_backup_status('FAILED', f'Backup error: {str(e)}')
                print(f"[ERROR] Backup thread error: {str(e)}")
            finally:
                backup_status['backing_up'] = False
                
                # Perform cleanup with incremental progress updates
                def cleanup_with_progress():
                    """Perform cleanup with progressive status updates"""
                    try:
                        # Step 1: Start cleanup (90%)
                        update_backup_status('CLEANUP', 'Starting cleanup...', 90)
                        time.sleep(0.5)
                        
                        # Step 2: Remove temp files (95%)
                        update_backup_status('CLEANUP', 'Removing temporary files...', 95)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        if os.path.exists(temp_dir):
                            os.rmdir(temp_dir)
                        print(f"[DEBUG] Cleanup successful for: {file_path}")
                        time.sleep(0.5)
                        
                        # Step 3: Finalizing (98%)
                        update_backup_status('CLEANUP', 'Finalizing...', 98)
                        time.sleep(0.3)
                        
                        # Step 4: Complete (100%)
                        update_backup_status('COMPLETED', 'Backup process completed successfully!', 100)
                        time.sleep(0.2)
                        
                    except Exception as e:
                        print(f"[WARNING] Cleanup error: {e}")
                        update_backup_status('COMPLETED', 'Backup completed with cleanup warnings.', 100)
                    
                    finally:
                        # Reset status to ready for next job after a brief display period
                        time.sleep(1.0) # Allow user to see completion status
                        backup_status = get_default_status()
                        backup_status['connected'] = True # Assume still connected
                        update_backup_status('READY', 'Ready for new backup.')
                
                cleanup_with_progress()

        # Start backup thread
        backup_thread = threading.Thread(target=run_backup)
        backup_thread.daemon = True
        backup_thread.start()

        return jsonify({
            'success': True,
            'message': f'Backup started for {filename}',
            'filename': filename,
            'username': username
        })

    except Exception as e:
        backup_status['backing_up'] = False
        error_msg = f"Backup start error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        update_backup_status('ERROR', error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

# --- Enhanced server startup with WebSocket support ---

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
    print("[ROCKET] Starting Flask API server with WebSocket support...")
    
    # Ensure only one API server instance runs at a time
    print("Ensuring single API server instance...")
    ensure_single_server_instance("APIServer", 9090)
    print("Singleton lock acquired for API server")

    try:
        print("[WEBSOCKET] Starting Flask-SocketIO server with real-time support...")
        socketio.run(
            app,
            host='127.0.0.1',
            port=9090,
            debug=True,
            allow_unsafe_werkzeug=True  # Allow threading with SocketIO
        )
    except KeyboardInterrupt:
        print("\n[INFO] API Server shutdown requested")
    except Exception as e:
        print(f"[MISSING] Server error: {e}")