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
- Sentry error tracking and monitoring

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
from typing import Optional

# Third-party imports
from flask import Flask, request, jsonify, send_from_directory, send_file, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# First-party imports (ensure_imports() must be called first)
from Shared.path_utils import setup_imports
setup_imports() # This must be called before any other first-party imports

from Shared.logging_utils import setup_dual_logging, create_log_monitor_info, create_enhanced_logger, log_performance_metrics
from Shared.utils.unified_config import get_config
from Shared.sentry_config import init_sentry, capture_error
from Shared.observability_middleware import setup_observability_for_flask
from Shared.unified_monitor import UnifiedFileMonitor
from Shared.utils.performance_monitor import get_performance_monitor # Moved from api_perf_job()

from python_server.server.server_singleton import ensure_single_server_instance
from python_server.server.connection_health import get_connection_health_monitor # Moved from global scope

# Define PROJECT_ROOT for consistent path resolution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Global paths for static file serving
CLIENT_GUI_PATH = os.path.join(PROJECT_ROOT, 'Client', 'Client-gui')
PYTHON_SERVER_PATH = os.path.join(PROJECT_ROOT, 'python_server')

# Initialize Sentry error tracking (after all imports)
SENTRY_INITIALIZED = init_sentry("api-server", traces_sample_rate=0.5)

# Configure enhanced dual logging (console + file) with observability
logger, api_log_file = setup_dual_logging(
    logger_name=__name__,
    server_type="api-server",
    console_level=logging.INFO,
    file_level=logging.DEBUG,
    console_format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import our real backup executor (needs to be after setup_imports and logging)
try:
    from .real_backup_executor import RealBackupExecutor
except ImportError:
    from real_backup_executor import RealBackupExecutor

# Performance monitoring singleton
perf_monitor = get_performance_monitor()
# Connection health monitoring
conn_health = get_connection_health_monitor()


app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Initialize SocketIO with origin-locked CORS for security
api_port = get_config('api.port', 9090)
socketio = SocketIO(app, cors_allowed_origins=[f"http://localhost:{api_port}", f"http://127.0.0.1:{api_port}"])

# Setup enhanced observability middleware and structured logging (after app creation)
observability_middleware = setup_observability_for_flask(app, "api-server")
structured_logger = create_enhanced_logger("api-server", logger)

# --- Global Singleton Monitor ---
# This monitor will be shared across all requests.
file_monitor = UnifiedFileMonitor(os.path.join(PROJECT_ROOT, 'received_files'))

# Add Sentry error handlers
if SENTRY_INITIALIZED:
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors with Sentry"""
        capture_error(error, "api-server", {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url
        })
        return jsonify({
            "error": "Internal server error",
            "message": "An error occurred while processing your request"
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors with Sentry"""
        capture_error(error, "api-server", {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "user_agent": request.headers.get("User-Agent")
        })
        logger.error(f"Unexpected error in {request.endpoint}: {error}")
        return jsonify({
            "error": "Unexpected error",
            "message": "An unexpected error occurred"
        }), 500

# Performance monitoring singleton
from Shared.utils.performance_monitor import get_performance_monitor
# Connection health monitoring
from python_server.server.connection_health import get_connection_health_monitor
conn_health = get_connection_health_monitor()

perf_monitor = get_performance_monitor()


# --- Initialize global variables & Locks ---
# For job-specific data
active_backup_jobs = {}
active_backup_jobs_lock = threading.Lock()

# For general, non-job-specific server status
def get_default_server_status():
    return {
        'connected': False,
        'backing_up': False,
        'phase': 'READY',
        'status': 'ready',
        'message': 'Ready for backup',
        'last_updated': datetime.now().isoformat()
    }
server_status = get_default_server_status()
server_status_lock = threading.Lock()
last_known_status = get_default_server_status()

# Other globals
connection_established = False
connection_timestamp = None
connected_clients = set()
websocket_enabled = True

# Server configuration
server_config = {
    'host': get_config('server.host', '127.0.0.1'),
    'port': get_config('server.port', 1256),
    'username': get_config('client.default_username', 'default_user')
}

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

def update_server_status(phase, message):
    """Update general server status with thread safety"""
    with server_status_lock:
        server_status['phase'] = phase
        server_status['message'] = message
        server_status['last_updated'] = datetime.now().isoformat()
    print(f"[SERVER_STATUS] {phase}: {message}")

def check_backup_server_status(host: Optional[str] = None, port: Optional[int] = None):
    """Check if the Python backup server is reachable.

    Uses dynamic server_config host/port unless explicitly overridden.
    Backwards compatible: callers without args still work (defaults applied).
    """
    try:
        import socket
        target_host = host or server_config.get('host')
        target_port = int(port or server_config.get('port') or 1256)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((target_host, target_port))
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
        'connected': check_backup_server_status(),  # dynamic via server_config
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
        # Use absolute path to handle working directory issues
        # Get the absolute path to this file, then go up to api_server, then up to project root
        html_path = os.path.join(CLIENT_GUI_PATH, 'NewGUIforClient.html')
        
        # Debug logging
        logger.debug(f"HTML path: {html_path}")
        logger.debug(f"HTML exists: {os.path.exists(html_path)}")
        
        return send_file(html_path)
    except FileNotFoundError as e:
        logger.error(f"HTML file not found: {e}")
        return "<h1>Client GUI not found</h1><p>Please ensure Client/Client-gui/NewGUIforClient.html exists</p>", 404
    except Exception as e:
        logger.error(f"Error serving HTML: {e}")
        return f"<h1>Server Error</h1><p>Error serving client: {e}</p>", 500

@app.route('/client/<path:filename>')
def serve_client_assets(filename):
    """Serve client assets (CSS, JS, images, etc.)"""
    try:
        # Use absolute path to handle working directory issues
        client_dir = CLIENT_GUI_PATH
        
        logger.debug(f"Serving asset {filename} from {client_dir}")
        return send_from_directory(client_dir, filename)
    except FileNotFoundError:
        logger.error(f"Asset not found: {filename}")
        return f"<h1>Asset not found: {filename}</h1>", 404

@app.route('/progress_config.json')
def serve_progress_config():
    """Serve the progress configuration file"""
    try:
        # Check for progress_config.json in python_server directory
        progress_config_path = os.path.join(PYTHON_SERVER_PATH, 'progress_config.json')
        if os.path.exists(progress_config_path):
            return send_file(progress_config_path)
        else:
            # Fallback to root directory
            return send_file('progress_config.json')
    except FileNotFoundError:
        return jsonify({'error': 'progress_config.json not found'}), 404

@app.route('/favicon.ico')
def serve_favicon():
    """Serve favicon with better error handling"""
    try:
        # Try to serve favicon from Client-gui directory if it exists
        favicon_path = os.path.join(CLIENT_GUI_PATH, 'favicon.ico')
        
        # Return favicon if it exists, otherwise return 204
        return send_file(favicon_path) if os.path.exists(favicon_path) else ('', 204)
    except Exception as e:
        logger.debug(f"Favicon serving error (non-critical): {e}")
        return '', 204

# API Endpoints for CyberBackup 3.0

@app.route('/api/test', methods=['POST'])
def api_test():
    """Simple test endpoint to debug POST requests"""
    print("[DEBUG] Test POST endpoint called!")
    return jsonify({'success': True, 'message': 'POST test successful'})

@app.route('/api/status')
def api_status():
    """Get current backup status with proper connection state management and timeout protection"""
    job_id = request.args.get('job_id')
    status = None

    if job_id:
        with active_backup_jobs_lock:
            if job_status := active_backup_jobs.get(job_id):
                status = job_status.copy()
                # Clear events after reading them
                events_to_send = status.get('events', [])
                active_backup_jobs[job_id]['events'] = []
                status['events'] = events_to_send
    
    if status is None:
        # No job_id provided or job_id not found, return general server status
        with server_status_lock:
            status = server_status.copy()
        status['backing_up'] = False # General status is never "backing up"

    # Always provide the latest connection status
    status['connected'] = check_backup_server_status() and connection_established
    status['isConnected'] = status['connected']

    return jsonify(status)

@app.route('/health')
def health_check():
    """Enhanced health check endpoint with timeout protection"""
    import psutil
    try:
        # Quick health check with timeout protection
        server_running = check_backup_server_status()
        
        # Get system metrics
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            active_connections = len(connected_clients) if 'connected_clients' in globals() else 0
        except Exception:
            cpu_usage = memory_usage = active_connections = 0
        
        with active_backup_jobs_lock:
            active_jobs_count = len(active_backup_jobs)

        return jsonify({
            'status': 'healthy' if server_running else 'degraded',
            'backup_server': 'running' if server_running else 'not_running',
            'api_server': 'running',
            'system_metrics': {
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage,
                'active_websocket_connections': active_connections,
                'active_backup_jobs': active_jobs_count
            },
            'timestamp': datetime.now().isoformat(),
            'uptime_info': 'API server responsive'
        })
    except Exception as e:
        # Even health check can fail - provide minimal response
        return jsonify({
            'status': 'error',
            'api_server': 'running_with_errors',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/connect', methods=['POST'])
def api_connect():
    """Connect to backup server with configuration using real backup protocol"""
    global server_config, connection_established, connection_timestamp

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

        # Normalize field naming (accept legacy 'server' alias for 'host')
        if 'server' in config:
            if 'host' not in config:
                config['host'] = config['server']
            elif config['server'] != config['host']:
                logger.warning(f"Both 'server' ({config['server']}) and 'host' ({config['host']}) provided; using 'host'.")
            config.pop('server')

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

        update_server_status('CONNECT', f'Testing connection to {server_config["host"]}:{server_config["port"]}...')

        # Test if backup server is reachable
        server_reachable = check_backup_server_status(server_config['host'], server_config['port'])
        
        message = ''
        if server_reachable:
            connection_established = True
            connection_timestamp = datetime.now()
            message = f'Connected to backup server at {server_config["host"]}:{server_config["port"]}'
            update_server_status('READY', 'Connected successfully. Ready for backup.')
            print(f"[DEBUG] Connection established at {connection_timestamp.isoformat()}")
        else:
            connection_established = False
            connection_timestamp = None
            message = 'Connection failed: Backup server not responding'
            update_server_status('ERROR', 'Connection test failed: Backup server not responding')
            print("[DEBUG] Connection failed - server not reachable")

        return jsonify({
            'success': server_reachable,
            'connected': server_reachable,
            'message': message,
            'server_config': server_config
        })

    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        update_server_status('ERROR', error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """Disconnect from backup server"""
    global connection_established, connection_timestamp

    print("[DEBUG] /api/disconnect called")

    try:
        connection_established = False
        connection_timestamp = None

        update_server_status('READY', 'Disconnected from backup server')
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
    start_time = time.time()

    structured_logger.info("Backup request received", operation="start_backup")

    # Generate unique job ID for this backup operation
    job_id = f"job_{int(time.time() * 1000000)}"

    # Initialize job tracking
    with active_backup_jobs_lock:
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
    try:
        api_server_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(api_server_dir)
        client_exe_path = os.path.join(project_root, "build", "Release", "EncryptedBackupClient.exe")
        
        backup_executor = RealBackupExecutor(client_exe_path)
        with active_backup_jobs_lock:
            active_backup_jobs[job_id]['executor'] = backup_executor
        print(f"[Job {job_id}] RealBackupExecutor instance created with client: {client_exe_path}")
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to initialize backup executor: {e}'
        }), 500

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    try:
        temp_dir = tempfile.mkdtemp()
        original_filename = file.filename or f"backup_file_{int(time.time())}"
        safe_temp_name = f"upload_{int(time.time() * 1000000)}_{original_filename}"
        temp_file_path = os.path.join(temp_dir, safe_temp_name)

        total_bytes = None
        with contextlib.suppress(Exception):
            total_bytes = os.path.getsize(temp_file_path)
        with contextlib.suppress(Exception):
            perf_monitor.start_job(job_id, total_bytes=total_bytes)

        print(f"[DEBUG] Original filename: {original_filename}")
        print(f"[DEBUG] Temp file path: {temp_file_path}")

        file.save(temp_file_path)

        username = request.form.get('username', server_config.get('username', 'default_user'))
        server_ip = request.form.get('host') or request.form.get('server') or server_config.get('host')
        server_port = request.form.get('port', server_config.get('port'))

        def status_handler(phase, data):
            with active_backup_jobs_lock:
                if job_id not in active_backup_jobs:
                    return
                
                job_data = active_backup_jobs[job_id]
                job_data['events'].append({'phase': phase, 'data': data})
                job_data['phase'] = phase
                job_data['last_updated'] = datetime.now().isoformat()

                if isinstance(data, dict):
                    job_data['message'] = data.get('message', phase)
                    if 'progress' in data:
                        job_data['progress']['percentage'] = data['progress']
                    if 'bytes_transferred' in data:
                        job_data['progress']['bytes_transferred'] = data['bytes_transferred']
                    if 'total_bytes' in data:
                        job_data['progress']['total_bytes'] = data['total_bytes']
                else:
                    job_data['message'] = data

            # Real-time WebSocket broadcasting
            if websocket_enabled and connected_clients:
                try:
                    socketio.emit('progress_update', {
                        'job_id': job_id,
                        'phase': phase,
                        'data': data,
                        'timestamp': time.time()
                    })
                except Exception as e:
                    print(f"[WEBSOCKET] Broadcast failed: {e}")

        backup_executor.set_status_callback(status_handler)

        with active_backup_jobs_lock:
            active_backup_jobs[job_id]['backing_up'] = True
            active_backup_jobs[job_id]['phase'] = 'BACKUP_IN_PROGRESS'
            active_backup_jobs[job_id]['progress']['current_file'] = original_filename
            active_backup_jobs[job_id]['message'] = f'Starting backup of {original_filename}...'

        def run_backup(executor, temp_file_path_for_thread, filename_for_thread, temp_dir_for_thread):
            try:
                expected_size = os.path.getsize(temp_file_path_for_thread)
                with open(temp_file_path_for_thread, 'rb') as f:
                    expected_hash = hashlib.sha256(f.read()).hexdigest()
                logger.info(f"[Job {job_id}] Calculated verification data: Size={expected_size}, Hash={expected_hash[:8]}...")

                def on_completion():
                    logger.info(f"[Job {job_id}] Received VERIFIED COMPLETION signal for '{filename_for_thread}'. Forcing 100%.")
                    with active_backup_jobs_lock:
                        if job_id in active_backup_jobs:
                            active_backup_jobs[job_id]['phase'] = 'COMPLETED_VERIFIED'
                            active_backup_jobs[job_id]['message'] = 'Backup complete and cryptographically verified.'
                            active_backup_jobs[job_id]['progress']['percentage'] = 100
                            active_backup_jobs[job_id]['backing_up'] = False

                def on_failure(reason: str):
                    logger.error(f"[Job {job_id}] Received VERIFICATION FAILED signal for '{filename_for_thread}': {reason}")
                    with active_backup_jobs_lock:
                        if job_id in active_backup_jobs:
                            active_backup_jobs[job_id]['phase'] = 'VERIFICATION_FAILED'
                            active_backup_jobs[job_id]['message'] = f'CRITICAL: {reason}'
                            active_backup_jobs[job_id]['backing_up'] = False

                monitor = file_monitor
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
                    server_port=int(server_port or 1256)
                )

                with active_backup_jobs_lock:
                    if job_id in active_backup_jobs:
                        if result and result.get('success'):
                            active_backup_jobs[job_id]['phase'] = 'COMPLETED'
                            active_backup_jobs[job_id]['message'] = 'Backup completed successfully!'
                            active_backup_jobs[job_id]['progress']['percentage'] = 100
                        else:
                            error_msg = result.get('error', 'Unknown error') if result else 'Backup executor returned None'
                            active_backup_jobs[job_id]['phase'] = 'FAILED'
                            active_backup_jobs[job_id]['message'] = f'Backup failed: {error_msg}'
                        active_backup_jobs[job_id]['backing_up'] = False

            except Exception as e:
                with active_backup_jobs_lock:
                    if job_id in active_backup_jobs:
                        active_backup_jobs[job_id]['phase'] = 'FAILED'
                        active_backup_jobs[job_id]['message'] = f'Backup error: {str(e)}'
                        active_backup_jobs[job_id]['backing_up'] = False
                print(f"[ERROR] Backup thread error: {str(e)}")
            finally:
                if os.path.exists(temp_file_path_for_thread):
                    os.remove(temp_file_path_for_thread)
                if os.path.exists(temp_dir_for_thread):
                    os.rmdir(temp_dir_for_thread)
                print(f"[DEBUG] Cleanup successful for: {temp_file_path_for_thread}")
                update_server_status('READY', 'Ready for new backup.')

        backup_thread = threading.Thread(target=run_backup, args=(backup_executor, temp_file_path, original_filename, temp_dir))
        backup_thread.daemon = True
        backup_thread.start()

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
            'job_id': job_id
        })

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        error_msg = f"Backup start error: {str(e)}"

        structured_logger.error(error_msg,
                              operation="start_backup",
                              duration_ms=duration_ms,
                              error_code=type(e).__name__,
                              context={"exception": str(e)})

        log_performance_metrics(logger, "start_backup", duration_ms, False,
                              error=str(e))

        print(f"[ERROR] {error_msg}")
        update_server_status('ERROR', error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/check_receipt/<filename>')
def api_check_file_receipt(filename):
    """Check if a specific file has been received by the server"""
    try:
        monitor = file_monitor
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
        monitor = file_monitor
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
        monitor = file_monitor
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
    current_file_abs = os.path.abspath(__file__)
    api_server_dir = os.path.dirname(current_file_abs)
    project_root = os.path.dirname(api_server_dir)
    client_html = os.path.join(project_root, 'Client', 'Client-gui', 'NewGUIforClient.html')
    if os.path.exists(client_html):
        print(f"[OK] HTML Client: {client_html}")
    else:
        print(f"[MISSING] HTML Client: {client_html} NOT FOUND")

    # Check C++ client
    client_exe = os.path.join(project_root, "build", "Release", "EncryptedBackupClient.exe")
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

    # Initialize and start the UnifiedFileMonitor
    try:
        file_monitor.start_monitoring()
        print(f"[OK] Unified File Monitor: Watching {file_monitor.watched_directory}")
    except Exception as e:
        print(f"[WARNING] Unified File Monitor: Failed to initialize - {e}")

    # Ensure only one API server instance runs at a time
    print("Ensuring single API server instance...")
    ensure_single_server_instance("APIServer", 9090)
    print("Singleton lock acquired for API server")

    try:
        print("[WEBSOCKET] Starting Flask-SocketIO server with real-time support...")
        print("[DEBUG] About to call socketio.run()...")
        socketio.run(
            app,
            host=get_config('api.host', '127.0.0.1'),
            port=get_config('api.port', 9090),
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
        # Cleanup the unified monitor
        try:
            file_monitor.stop_monitoring()
            print("[INFO] Unified file monitor stopped")
        except Exception as e:
            print(f"[WARNING] Error stopping unified file monitor: {e}")
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