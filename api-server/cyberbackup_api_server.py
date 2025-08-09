#!/usr/bin/env python3
"""
CyberBackup 3.0 API Server - CANONICAL IMPLEMENTATION
=====================================================

This is the OFFICIAL and ONLY API server for CyberBackup 3.0.

Features:
- Complete Flask API backend for NewGUIforClient.html interface
- Real integration with C++ backup client and Python backup server
- Enhanced observability and structured logging
- Performance monitoring and metrics collection
- WebSocket support for real-time communication
- File receipt monitoring and health checks
- Singleton management and comprehensive error handling

Usage:
- Direct: python cyberbackup_api_server.py
- Recommended: python one_click_build_and_run.py

Port: 9090
Endpoints: /api/*, /health, /api/observability/*

NO SIMULATION - REAL INTEGRATION ONLY

Note: Other API server files have been archived to eliminate duplicates.
See API_SERVER_UNIFICATION.md for details.
"""

import os
import time
import threading
import tempfile
import logging
import hashlib
import contextlib
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file, session

# Import enhanced logging utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.shared.logging_utils import setup_dual_logging, create_log_monitor_info

# Configure enhanced dual logging (console + file) with observability
logger, api_log_file = setup_dual_logging(
    logger_name=__name__,
    server_type="api-server",
    console_level=logging.INFO,
    file_level=logging.DEBUG,
    console_format='%(asctime)s - %(levelname)s - %(message)s'
)

# Setup structured logging and observability
from src.shared.observability_middleware import setup_observability_for_flask
from src.shared.logging_utils import create_enhanced_logger, log_performance_metrics
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Import our real backup executor
from src.api.real_backup_executor import RealBackupExecutor

# Import singleton manager to prevent multiple API server instances
from src.server.server_singleton import ensure_single_server_instance

# Import file receipt monitoring
from src.server.file_receipt_monitor import initialize_file_receipt_monitor, get_file_receipt_monitor, stop_file_receipt_monitor

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Initialize SocketIO with origin-locked CORS for security
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:9090", "http://127.0.0.1:9090"])

# Setup enhanced observability middleware - FIXED VERSION
observability_middleware = setup_observability_for_flask(app, "api-server")
structured_logger = create_enhanced_logger("api-server", logger)

# Performance monitoring singleton
from src.shared.utils.performance_monitor import get_performance_monitor
# Connection health monitoring
from src.server.connection_health import get_connection_health_monitor
conn_health = get_connection_health_monitor()

perf_monitor = get_performance_monitor()


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
    import uuid as uuid_lib
    client_id = str(uuid_lib.uuid4())
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
    if client_id := session.get('client_id'):
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

    print("[DEBUG] /api/connect endpoint called")
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
        
        if missing_fields := [field for field in required_fields if field not in config or not config[field]]:
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
            update_backup_status('READY', 'Connected successfully. Ready for backup.')
            print(f"[DEBUG] Connection established at {connection_timestamp.isoformat()}")
        else:
            connection_established = False
            connection_timestamp = None

            backup_status['connected'] = False
            backup_status['status'] = 'connection_failed'
            backup_status['message'] = 'Connection failed: Backup server not responding'
            update_backup_status('ERROR', 'Connection test failed: Backup server not responding')
            print("[DEBUG] Connection failed - server not reachable")

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

    print("[DEBUG] /api/disconnect called")


    try:
        connection_established = False
        connection_timestamp = None

        backup_status['connected'] = False
        backup_status['status'] = 'disconnected'
        backup_status['message'] = 'Disconnected from backup server'
        backup_status['phase'] = 'READY'

        print("[DEBUG] Connection terminated")

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
def api_start_backup_working():
    """Start backup using REAL backup executor with enhanced observability"""
    global backup_status
    start_time = time.time()

    structured_logger.info("Backup request received", operation="start_backup")

    # Generate unique job ID for this backup operation
    job_id = f"job_{int(time.time() * 1000000)}"

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
        # Store executor on the job record for cancellation control
        active_backup_jobs[job_id]['executor'] = backup_executor
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

        # CRITICAL FIX: Preserve original filename but ensure safe temp file creation
        original_filename = file.filename or f"backup_file_{int(time.time())}"

        # Create a safe temporary filename while preserving the original for display
        safe_temp_name = f"upload_{int(time.time() * 1000000)}_{original_filename}"
        temp_file_path = os.path.join(temp_dir, safe_temp_name)

        # Initialize performance monitor for this job with known total bytes if available
        total_bytes = None
        with contextlib.suppress(Exception):
            total_bytes = os.path.getsize(temp_file_path)
        with contextlib.suppress(Exception):
            perf_monitor.start_job(job_id, total_bytes=total_bytes)

        print(f"[DEBUG] Original filename: {original_filename}")
        print(f"[DEBUG] Safe temp filename: {safe_temp_name}")
        print(f"[DEBUG] Temp file path: {temp_file_path}")

        file.save(temp_file_path)



        # Get form data
        username = request.form.get('username', server_config.get('username', 'default_user'))
        server_ip = request.form.get('server', server_config.get('host', '127.0.0.1'))
        server_port = request.form.get('port', server_config.get('port', 1256))

        # Define a dedicated status handler for this job
        def status_handler(phase, data):
            if job_id not in active_backup_jobs:
                return
                
            active_backup_jobs[job_id]['events'].append({'phase': phase, 'data': data})
            active_backup_jobs[job_id]['phase'] = phase

            # Debug logging for API server progress handling
            if isinstance(data, dict) and 'progress' in data:
                print(f"[API_DEBUG] Received progress update: {phase} - {data['progress']:.1f}% - {data.get('message', 'No message')}")

            # Update both job-specific and global backup status
            if isinstance(data, dict):
                message = data.get('message', phase)
                active_backup_jobs[job_id]['message'] = message
                if 'progress' in data:
                    progress_value = data['progress']
                    active_backup_jobs[job_id]['progress']['percentage'] = progress_value
                # Feed performance monitor when we get rich progress from executor
                with contextlib.suppress(Exception):
                    if isinstance(data, dict):
                        bytes_tx = data.get('bytes_transferred')
                        total_b = data.get('total_bytes')
                        speed = data.get('speed')
                        perf_monitor.record_sample(
                            job_id,
                            bytes_transferred=int(bytes_tx) if isinstance(bytes_tx, (int, float)) else None,
                            total_bytes=int(total_b) if isinstance(total_b, (int, float)) else None,
                            speed_bps=float(speed) if isinstance(speed, (int, float)) else None,
                            phase=phase,
                        )

                # Also update global backup status for unified API
                if 'progress' in data:
                    progress_value = data['progress']
                    update_backup_status(phase, message, progress_value)
                    print(f"[API_DEBUG] Updated job progress to {progress_value:.1f}%")
                else:
                    update_backup_status(phase, message)
            else:
                active_backup_jobs[job_id]['message'] = data
                update_backup_status(phase, data)

            # Enhanced completion logic with file receipt verification
            if phase in ['COMPLETED', 'FAILED', 'ERROR']:
                # Check actual file receipt regardless of reported status
                monitor = get_file_receipt_monitor()
                if monitor and original_filename:
                    file_filename = os.path.basename(original_filename)
                    receipt_check = monitor.check_file_receipt(file_filename)
                    if receipt_check.get('received', False):
                        # File actually received - override any failure status
                        if phase in ['FAILED', 'ERROR']:
                            print(f"[OVERRIDE] Process reported {phase} but file was received - marking as SUCCESS")
                            phase = 'COMPLETED'
                            active_backup_jobs[job_id]['phase'] = 'COMPLETED'
                            active_backup_jobs[job_id]['message'] = 'File successfully received and verified!'
                            update_backup_status('COMPLETED', 'File transfer verified - backup successful!', 100)
                    else:
                        # File not received - ensure we report failure even if process claims success
                        if phase == 'COMPLETED':
                            print("[OVERRIDE] Process reported COMPLETED but file not received - marking as FAILED")
                            phase = 'FAILED'
                            active_backup_jobs[job_id]['phase'] = 'FAILED'
                            active_backup_jobs[job_id]['message'] = 'Process completed but file not received on server'
                            update_backup_status('FAILED', 'File transfer failed - no file received', 0)

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

        # Set the callback for this specific executor instance
        backup_executor.set_status_callback(status_handler)

        # Update status
        backup_status['backing_up'] = True
        backup_status['phase'] = 'BACKUP_IN_PROGRESS'
        backup_status['progress']['current_file'] = original_filename
        update_backup_status('BACKUP_IN_PROGRESS', f'Starting backup of {original_filename}...')

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
        backup_thread = threading.Thread(target=run_backup, args=(backup_executor, temp_file_path, original_filename, temp_dir))
        backup_thread.daemon = True
        backup_thread.start()

        # Log successful backup initiation with performance metrics
        duration_ms = (time.time() - start_time) * 1000
        structured_logger.info(f"Backup job {job_id} started successfully",
                             operation="start_backup",
                             duration_ms=duration_ms,
                             context={
                                 "job_id": job_id,
                                 "username": username,
                                 "filename": original_filename
                             })

        log_performance_metrics(logger, "start_backup", duration_ms, True,
                              job_id=job_id, username=username)

        return jsonify({
            'success': True,
            'message': f'Backup started for {original_filename}',
            'filename': original_filename,
            'username': username,
            'job_id': job_id  # Include job_id in response for client tracking
        })

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        backup_status['backing_up'] = False
        error_msg = f"Backup start error: {str(e)}"

        structured_logger.error(error_msg,
                              operation="start_backup",
                              duration_ms=duration_ms,
                              error_code=type(e).__name__,
                              context={"exception": str(e)})

        log_performance_metrics(logger, "start_backup", duration_ms, False,
                              error=str(e))

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

@app.route('/api/server/connection_health')
def api_server_connection_health():
    """Get server connection health status"""
    try:
        return jsonify({'success': True, 'connections': conn_health.get_summary()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Enhanced server startup with WebSocket support ---

if __name__ == "__main__":
    print("=" * 70)
    print("* CyberBackup 3.0 API Server - REAL Integration")
    print("=" * 70)
    print("* API Server: http://localhost:9090")
    print("* Client GUI: http://localhost:9090/")
    print("* Health Check: http://localhost:9090/health")
    print()

    # Display logging information
    log_monitor_info = create_log_monitor_info(api_log_file, "API Server")
    print("* Logging Information:")
    print(f"* Log File: {log_monitor_info['file_path']}")
    print(f"* Live Monitor (PowerShell): {log_monitor_info['powershell_cmd']}")
    print("* Console Output: Visible in this window (dual output enabled)")
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
    if server_running := check_backup_server_status():
        print("[OK] Backup Server: Running on port 1256")
    else:
        print("[WARNING] Backup Server: Not running on port 1256")

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
        print("[DEBUG] About to call socketio.run()...")
        socketio.run(
            app,
            host='127.0.0.1',
            port=9090,
            debug=False,
            allow_unsafe_werkzeug=True,  # Allow threading with SocketIO
            use_reloader=False
        )
        print("[DEBUG] socketio.run() returned normally")
    except KeyboardInterrupt:
        print("\n[INFO] API Server shutdown requested")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[DEBUG] Entering finally block...")
        # Cleanup file receipt monitor
        try:
            stop_file_receipt_monitor()
            print("[INFO] File receipt monitor stopped")
        except Exception as e:
            print(f"[WARNING] Error stopping file receipt monitor: {e}")
        print("[DEBUG] API Server process ending...")


# --- Performance Monitoring Endpoints (after primary routes) ---
@app.route('/api/perf/<job_id>')
def api_perf_job(job_id):
    try:
        if not (summary := perf_monitor.get_job_summary(job_id)):
            return jsonify({'success': False, 'error': f'No performance data for job_id={job_id}'}), 404
        return jsonify({'success': True, 'job': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Cancellation Endpoint ---
@app.route('/api/cancel/<job_id>', methods=['POST'])
def api_cancel_job(job_id):
    try:
        if not (job := active_backup_jobs.get(job_id)):
            return jsonify({'success': False, 'error': f'Unknown job_id={job_id}'}), 404
        executor = job.get('executor')
        if not executor:
            return jsonify({'success': False, 'error': 'No executor associated with this job'}), 400
        ok = False
        try:
            ok = executor.cancel('API cancellation')
        except Exception as e:
            return jsonify({'success': False, 'error': f'Cancel failed: {e}'}), 500
        # Update job state
        job['phase'] = 'CANCELLED' if ok else 'CANCEL_REQUESTED'
        job['message'] = 'Backup cancelled' if ok else 'Cancellation requested'
        # Attach optional cancel reason to job record for UI consumption
        cancel_reason = None
        try:
            if request and request.is_json and request.json:
                cancel_reason = request.json.get('reason')
        except Exception:
            cancel_reason = None
        if cancel_reason:
            job['cancel_reason'] = cancel_reason
        if ok:
            job['progress']['percentage'] = max(job['progress'].get('percentage', 0), 0)
        # Broadcast over WebSocket if enabled
        try:
            if websocket_enabled and connected_clients:
                socketio.emit('job_cancelled', {
                    'job_id': job_id,
                    'success': ok,
                    'phase': job['phase'],
                    'reason': job.get('cancel_reason') if isinstance(job, dict) else None,
                    'timestamp': time.time()
                })
        except Exception as be:
            print(f"[WEBSOCKET] Cancel broadcast failed: {be}")
        return jsonify({'success': ok, 'job_id': job_id, 'phase': job['phase']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Cancel All Endpoint ---
@app.route('/api/cancel_all', methods=['POST'])
def api_cancel_all_jobs():
    try:
        results = {}
        for jid, job in list(active_backup_jobs.items()):
            if execu := job.get('executor'):
                try:
                    ok = execu.cancel('API cancel all')
                    job['phase'] = 'CANCELLED' if ok else job.get('phase', 'UNKNOWN')
                    job['message'] = 'Backup cancelled' if ok else job.get('message', '')
                    results[jid] = ok
                except Exception as e:
                    results[jid] = False
        # Broadcast
        try:
            if websocket_enabled and connected_clients:
                socketio.emit('jobs_cancelled', {'results': results, 'timestamp': time.time()})
        except Exception as be:
            print(f"[WEBSOCKET] Cancel-all broadcast failed: {be}")
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# --- Cancelable Jobs Endpoint ---
@app.route('/api/cancelable_jobs', methods=['GET'])
def api_cancelable_jobs():
    try:
        items = []
        for jid, job in active_backup_jobs.items():
            # A job is cancelable if it has an executor and is in a running phase
            cancelable = bool(job.get('executor')) and job.get('phase') not in ['COMPLETED', 'FAILED', 'ERROR', 'CANCELLED']
            if cancelable:
                items.append({
                    'job_id': jid,
                    'phase': job.get('phase'),
                    'file': job.get('progress', {}).get('current_file'),
                    'progress': job.get('progress', {}).get('percentage'),
                    'message': job.get('message')
                })
        return jsonify({'success': True, 'jobs': items})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/perf')
def api_perf_all():
    try:
        return jsonify({'success': True, 'jobs': perf_monitor.get_all_summaries()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500