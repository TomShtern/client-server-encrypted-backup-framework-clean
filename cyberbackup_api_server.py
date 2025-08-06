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
import logging
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file, session

# Import enhanced logging utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from shared.logging_utils import setup_dual_logging, create_log_monitor_info

# Configure enhanced dual logging (console + file)
logger, api_log_file = setup_dual_logging(
    logger_name=__name__,
    server_type="api-server",
    console_level=logging.INFO,
    file_level=logging.DEBUG,
    console_format='%(asctime)s - %(levelname)s - %(message)s'
)
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Import our real backup executor
from src.api.real_backup_executor import RealBackupExecutor

# Import singleton manager to prevent multiple API server instances
from src.server.server_singleton import ensure_single_server_instance

# Import file receipt monitoring
from src.server.file_receipt_monitor import initialize_file_receipt_monitor, get_file_receipt_monitor, stop_file_receipt_monitor

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




def broadcast_file_receipt(event_type: str, data: dict):
    """Broadcast file receipt events to all connected clients"""
    try:
        if websocket_enabled and connected_clients:
            socketio.emit('file_receipt', {
                'event_type': event_type,
                'data': data,
                'timestamp': time.time()
            })
            print(f"[WEBSOCKET] Broadcasted file receipt event: {event_type}")
    except Exception as e:
        print(f"[WEBSOCKET] Error broadcasting file receipt: {e}")


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
    
    # Generate unique job ID for this backup operation
    job_id = str(uuid.uuid4())
    
    # Initialize job tracking
    active_backup_jobs[job_id] = {
        'phase': 'INITIALIZING',
        'message': 'Initializing backup job...',
        'progress': {'percentage': 0, 'current_file': '', 'bytes_transferred': 0, 'total_bytes': 0},
        'status': 'initializing',
        'events': [],
        'connected': True,
        'backing_up': True,
        'last_updated': datetime.now().isoformat()
    }
    
    # Create a new, dedicated backup executor for this specific job.
    # This is the core of the fix for the race condition.
    try:
        backup_executor = RealBackupExecutor()
        print(f"[Job {job_id}] RealBackupExecutor instance created.")
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Failed to initialize backup executor: {e}'
        }), 500

    # Get uploaded file
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    try:
        # --- STREAMING LOGIC ---
        # Save the uploaded file directly to a temporary file on disk
        # to avoid loading it into memory. This is the key to handling large files.
        temp_dir = tempfile.mkdtemp()
        filename = file.filename or f"backup_file_{int(time.time())}"
        temp_file_path = os.path.join(temp_dir, filename)
        file.save(temp_file_path)

        

        # Get form data
        username = request.form.get('username', server_config.get('username', 'default_user'))
        server_ip = request.form.get('server', server_config.get('host', '127.0.0.1'))
        server_port = request.form.get('port', server_config.get('port', 1256))

        # Define a dedicated status handler for this job
        def status_handler(phase, data):
            if job_id in active_backup_jobs:
                active_backup_jobs[job_id]['events'].append({'phase': phase, 'data': data})
                active_backup_jobs[job_id]['phase'] = phase
                
                if isinstance(data, dict):
                    message = data.get('message', phase)
                    active_backup_jobs[job_id]['message'] = message
                    if 'progress' in data:
                        progress_value = data['progress']
                        active_backup_jobs[job_id]['progress']['percentage'] = progress_value
                        update_backup_status(phase, message, progress_value)
                    else:
                        update_backup_status(phase, message)
                else:
                    active_backup_jobs[job_id]['message'] = data
                    update_backup_status(phase, data)
                
                if websocket_enabled and connected_clients:
                    try:
                        socketio.emit('progress_update', {
                            'job_id': job_id,
                            'phase': phase,
                            'data': data,
                            'timestamp': time.time(),
                            'progress': active_backup_jobs[job_id]['progress']['percentage'] if isinstance(data, dict) and 'progress' in data else None
                        })
                    except Exception as e:
                        print(f"[WEBSOCKET] Broadcast failed: {e}")

        # Set the callback for this specific executor instance
        backup_executor.set_status_callback(status_handler)

        # Update status
        backup_status['backing_up'] = True
        backup_status['phase'] = 'BACKUP_IN_PROGRESS'
        backup_status['progress']['current_file'] = filename
        update_backup_status('BACKUP_IN_PROGRESS', f'Starting backup of {filename}...')

        # Start backup in background thread
        def run_backup(executor, temp_file_path_for_thread, filename_for_thread, temp_dir_for_thread):
            global backup_status

            try:
                # --- Verification Setup ---
                expected_size = os.path.getsize(temp_file_path_for_thread)
                with open(temp_file_path_for_thread, 'rb') as f:
                    expected_hash = hashlib.sha256(f.read()).hexdigest()
                logger.info(f"[Job {job_id}] Calculated verification data: Size={expected_size}, Hash={expected_hash[:8]}...")

                # --- Completion/Failure Callbacks ---
                def on_completion():
                    logger.info(f"[Job {job_id}] Received VERIFIED COMPLETION signal for '{filename_for_thread}'. Forcing 100%.")
                    if job_id in active_backup_jobs:
                        active_backup_jobs[job_id]['phase'] = 'COMPLETED_VERIFIED'
                        active_backup_jobs[job_id]['message'] = 'Backup complete and cryptographically verified.'
                        active_backup_jobs[job_id]['progress']['percentage'] = 100

                def on_failure(reason: str):
                    logger.error(f"[Job {job_id}] Received VERIFICATION FAILED signal for '{filename_for_thread}': {reason}")
                    if job_id in active_backup_jobs:
                        active_backup_jobs[job_id]['phase'] = 'VERIFICATION_FAILED'
                        active_backup_jobs[job_id]['message'] = f'CRITICAL: {reason}'

                # --- Register with File Receipt Monitor ---
                monitor = get_file_receipt_monitor()
                if monitor:
                    monitor.register_job(
                        filename=filename_for_thread,
                        job_id=job_id,
                        expected_size=expected_size,
                        expected_hash=expected_hash,
                        completion_callback=on_completion,
                        failure_callback=on_failure
                    )
                else:
                    logger.warning(f"[Job {job_id}] File receipt monitor not available. Verification will be skipped.")

                result = executor.execute_real_backup(
                    username=username,
                    file_path=temp_file_path_for_thread,
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
                
                # Cleanup the temporary file and directory
                if os.path.exists(temp_file_path_for_thread):
                    os.remove(temp_file_path_for_thread)
                if os.path.exists(temp_dir_for_thread):
                    os.rmdir(temp_dir_for_thread)
                print(f"[DEBUG] Cleanup successful for: {temp_file_path_for_thread}")

                time.sleep(1.0)
                backup_status = get_default_status()
                backup_status['connected'] = True
                update_backup_status('READY', 'Ready for new backup.')

        # Start backup thread, passing the new executor instance
        backup_thread = threading.Thread(target=run_backup, args=(backup_executor, temp_file_path, filename, temp_dir))
        backup_thread.daemon = True
        backup_thread.start()

        return jsonify({
            'success': True,
            'message': f'Backup started for {filename}',
            'filename': filename,
            'username': username,
            'job_id': job_id  # Include job_id in response for client tracking
        })

    except Exception as e:
        backup_status['backing_up'] = False
        error_msg = f"Backup start error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        update_backup_status('ERROR', error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/check_receipt/<filename>')
def api_check_file_receipt(filename):
    """Check if a specific file has been received by the server"""
    try:
        monitor = get_file_receipt_monitor()
        if not monitor:
            return jsonify({
                'success': False,
                'error': 'File receipt monitoring not available',
                'received': False
            }), 503
        
        receipt_info = monitor.check_file_receipt(filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            **receipt_info
        })
        
    except Exception as e:
        error_msg = f"Error checking file receipt: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg,
            'received': False
        }), 500

@app.route('/api/received_files')
def api_list_received_files():
    """List all files that have been received by the server"""
    try:
        monitor = get_file_receipt_monitor()
        if not monitor:
            return jsonify({
                'success': False,
                'error': 'File receipt monitoring not available'
            }), 503
        
        files_info = monitor.list_received_files()
        return jsonify(files_info)
        
    except Exception as e:
        error_msg = f"Error listing received files: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/monitor_status')
def api_monitor_status():
    """Get file receipt monitoring status"""
    try:
        monitor = get_file_receipt_monitor()
        if not monitor:
            return jsonify({
                'monitoring_active': False,
                'error': 'File receipt monitoring not initialized'
            })
        
        status = monitor.get_monitoring_status()
        return jsonify(status)
        
    except Exception as e:
        error_msg = f"Error getting monitor status: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({
            'monitoring_active': False,
            'error': error_msg
        }), 500

# --- Enhanced server startup with WebSocket support ---

if __name__ == "__main__":
    print("=" * 70)
    print("* CyberBackup 3.0 API Server - REAL Integration")
    print("=" * 70)
    print(f"* API Server: http://localhost:9090")
    print(f"* Client GUI: http://localhost:9090/")
    print(f"* Health Check: http://localhost:9090/health")
    print()
    
    # Display logging information
    log_monitor_info = create_log_monitor_info(api_log_file, "API Server")
    print("* Logging Information:")
    print(f"* Log File: {log_monitor_info['file_path']}")
    print(f"* Live Monitor (PowerShell): {log_monitor_info['powershell_cmd']}")
    print(f"* Console Output: Visible in this window (dual output enabled)")
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
    
    # Initialize file receipt monitoring
    try:
        received_files_dir = "received_files"  # Match server's actual file storage location
        file_receipt_monitor = initialize_file_receipt_monitor(received_files_dir, broadcast_file_receipt)
        print(f"[OK] File Receipt Monitor: Watching {received_files_dir}")
    except Exception as e:
        print(f"[WARNING] File Receipt Monitor: Failed to initialize - {e}")
    
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
            allow_unsafe_werkzeug=True,  # Allow threading with SocketIO
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n[INFO] API Server shutdown requested")
    except Exception as e:
        print(f"[MISSING] Server error: {e}")
    finally:
        # Cleanup file receipt monitor
        try:
            stop_file_receipt_monitor()
            print("[INFO] File receipt monitor stopped")
        except Exception as e:
            print(f"[WARNING] Error stopping file receipt monitor: {e}")