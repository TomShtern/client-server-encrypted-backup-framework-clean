#!/usr/bin/env python3
"""
⚠️  DEPRECATED AND ARCHIVED ⚠️

This file has been ARCHIVED and is no longer maintained.

REASON FOR ARCHIVAL:
- Superseded by the canonical cyberbackup_api_server.py
- Contains outdated import paths and missing features
- No longer used by any part of the system

USE INSTEAD:
- cyberbackup_api_server.py (project root)

ARCHIVED DATE: 2025-01-09
ARCHIVAL REASON: Unify API server entrypoint and eliminate duplicates

DO NOT USE THIS FILE - IT MAY NOT WORK CORRECTLY

Original Description:
CyberBackup 3.0 API Server - FIXED VERSION
Provides Flask API backend for the NewGUIforClient.html interface
Connects to the actual C++ backup client and Python backup server
NO SIMULATION - REAL INTEGRATION ONLY
"""

import sys
print("⚠️  WARNING: This API server has been DEPRECATED and ARCHIVED")
print("⚠️  Use cyberbackup_api_server.py instead (project root)")
print("⚠️  This file may not work correctly and is no longer maintained")
sys.exit(1)

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
    "api-server",
    console_level=logging.INFO,
    file_level=logging.DEBUG
)

# Import Flask extensions
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

# Global state management
backup_status = {
    'backing_up': False,
    'phase': 'IDLE',
    'progress': {'percentage': 0, 'current_file': '', 'bytes_transferred': 0, 'total_bytes': 0},
    'message': 'Ready to backup',
    'last_updated': datetime.now().isoformat(),
    'connected': False
}

# Track active backup jobs
active_backup_jobs = {}

# Track connected WebSocket clients
connected_clients = set()

def update_backup_status(phase, message, progress=None):
    """Update backup status and broadcast to all connected clients"""
    global backup_status
    backup_status['phase'] = phase
    backup_status['message'] = message
    backup_status['last_updated'] = datetime.now().isoformat()
    
    if progress:
        backup_status['progress'].update(progress)
    
    # Broadcast to all connected WebSocket clients
    socketio.emit('status', backup_status, broadcast=True)
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
        'backing_up': backup_status['backing_up'],
        'phase': backup_status['phase'],
        'message': backup_status['message'],
        'progress': backup_status['progress'],
        'last_updated': backup_status['last_updated']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket client disconnection"""
    client_id = session.get('client_id')
    if client_id and client_id in connected_clients:
        connected_clients.remove(client_id)
        print(f"[WEBSOCKET] Client disconnected: {client_id} (Total: {len(connected_clients)})")

def broadcast_file_receipt(file_info):
    """Broadcast file receipt notification to all connected clients"""
    socketio.emit('file_received', file_info, broadcast=True)
    print(f"[FILE_RECEIPT] Broadcasting: {file_info['filename']} ({file_info['size']} bytes)")

@app.route('/')
def serve_gui():
    """Serve the main GUI interface"""
    try:
        gui_path = "src/client/NewGUIforClient.html"
        if os.path.exists(gui_path):
            return send_file(gui_path)
        else:
            return jsonify({'error': f'GUI file not found: {gui_path}'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to serve GUI: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """Get current backup status"""
    return jsonify({
        'connected': check_backup_server_status(),
        'backing_up': backup_status['backing_up'],
        'phase': backup_status['phase'],
        'message': backup_status['message'],
        'progress': backup_status['progress'],
        'last_updated': backup_status['last_updated']
    })

@app.route('/api/start_backup', methods=['POST'])
def api_start_backup_new():
    """Start backup using REAL backup executor - FIXED VERSION"""
    global backup_status
    
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
    
    print(f"[API] Starting backup job: {job_id}")
    
    # Validate request
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Get form data
    username = request.form.get('username', 'DefaultUser')
    server_ip = request.form.get('server', '127.0.0.1')
    server_port = request.form.get('port', '1256')
    
    print(f"[API] Backup request - User: {username}, Server: {server_ip}:{server_port}")
    
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
        
        print(f"[DEBUG] Original filename: {original_filename}")
        print(f"[DEBUG] Safe temp filename: {safe_temp_name}")
        print(f"[DEBUG] Temp file path: {temp_file_path}")
        
        file.save(temp_file_path)
        
        # Verify file was saved
        if not os.path.exists(temp_file_path):
            return jsonify({'success': False, 'error': 'Failed to save uploaded file'}), 500
        
        file_size = os.path.getsize(temp_file_path)
        print(f"[API] File saved: {temp_file_path} ({file_size} bytes)")
        
        # Create backup executor instance for this specific job
        backup_executor = RealBackupExecutor()
        
        def run_backup(executor, file_path, filename, temp_dir):
            """Run backup in background thread"""
            try:
                print(f"[BACKUP_THREAD] Starting backup for: {filename}")
                
                # Execute the backup
                result = executor.execute_backup(
                    file_path=file_path,
                    username=username,
                    server_ip=server_ip,
                    server_port=int(server_port)
                )
                
                if result['success']:
                    update_backup_status('COMPLETED', f'Backup completed successfully for {filename}')
                    print(f"[BACKUP_THREAD] Backup completed successfully: {filename}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    update_backup_status('ERROR', f'Backup failed: {error_msg}')
                    print(f"[BACKUP_THREAD] Backup failed: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Backup thread error: {str(e)}"
                update_backup_status('ERROR', error_msg)
                print(f"[BACKUP_THREAD] Exception: {error_msg}")
            finally:
                # Cleanup
                try:
                    if os.path.exists(temp_dir):
                        import shutil
                        shutil.rmtree(temp_dir)
                        print(f"[CLEANUP] Removed temp directory: {temp_dir}")
                except Exception as cleanup_error:
                    print(f"[CLEANUP] Failed to remove temp directory: {cleanup_error}")
                
                # Reset backup status
                backup_status['backing_up'] = False
                print(f"[BACKUP_THREAD] Backup thread completed for: {filename}")
        
        # Update status
        backup_status['backing_up'] = True
        backup_status['phase'] = 'BACKUP_IN_PROGRESS'
        backup_status['progress']['current_file'] = original_filename
        update_backup_status('BACKUP_IN_PROGRESS', f'Starting backup of {original_filename}...')
        
        # Start backup thread, passing the new executor instance
        backup_thread = threading.Thread(target=run_backup, args=(backup_executor, temp_file_path, original_filename, temp_dir))
        backup_thread.daemon = True
        backup_thread.start()

        return jsonify({
            'success': True,
            'message': f'Backup started for {original_filename}',
            'filename': original_filename,
            'username': username,
            'job_id': job_id  # Include job_id in response for client tracking
        })

    except Exception as e:
        backup_status['backing_up'] = False
        error_msg = f"Backup start error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        update_backup_status('ERROR', error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

if __name__ == "__main__":
    print("CyberBackup 3.0 API Server - FIXED VERSION")
    print("=" * 50)
    
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
        print(f"[ERROR] Server error: {e}")
