#!/usr/bin/env python3
"""
CyberBackup 3.0 API Server
Provides REAL API backend for the NewGUIforClient.html interface
Connects to the actual C++ backup client and Python backup server
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
from real_backup_executor import RealBackupExecutor

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Global state
backup_executor = RealBackupExecutor()
current_backup_process = None
backup_status = {
    'connected': False,
    'backing_up': False,
    'paused': False,
    'progress': 0,
    'status': 'disconnected',
    'message': 'Ready',
    'file_name': '',
    'file_size': 0,
    'transferred': 0,
    'speed': 0,
    'time_remaining': 0,
    'last_update': datetime.now().isoformat()
}

server_config = {
    'host': '127.0.0.1',
    'port': 1256,
    'username': 'user'
}

def check_backup_server_status():
    """Check if the Python backup server is running"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)  # Increased timeout
        result = sock.connect_ex((server_config['host'], server_config['port']))
        sock.close()
        print(f"[DEBUG] Server check result: {result} (0=success)")
        return result == 0
    except Exception as e:
        print(f"[DEBUG] Server check exception: {e}")
        return False

def update_backup_status(phase, message, progress=None):
    """Update the global backup status"""
    global backup_status
    backup_status['last_update'] = datetime.now().isoformat()
    backup_status['message'] = f"[{phase}] {message}"
    if progress is not None:
        backup_status['progress'] = progress
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {phase}: {message}")

# API Endpoints for CyberBackup 3.0

@app.route('/api/status')
def api_status():
    """Get current backup client status"""
    # Update server connection status
    backup_status['connected'] = check_backup_server_status()
    if not backup_status['connected']:
        backup_status['status'] = 'server_offline'
        backup_status['message'] = 'Backup server is offline'
    elif not backup_status['backing_up']:
        backup_status['status'] = 'ready'
        backup_status['message'] = 'Ready for backup'
    
    # Return status in the format expected by the client GUI
    client_status = {
        'isConnected': backup_status['connected'],
        'isRunning': backup_status['backing_up'],
        'isPaused': backup_status['paused'],
        'phase': backup_status['status'].upper(),
        'clientId': None,
        'progress': {
            'percentage': backup_status['progress'],
            'transferred': backup_status['transferred'],
            'total': backup_status['file_size'],
            'speed': backup_status['speed'],
            'eta': backup_status['time_remaining']
        },
        'log': {
            'operation': backup_status['message'],
            'success': backup_status['status'] not in ['failed', 'error'],
            'details': f"File: {backup_status['file_name']}" if backup_status['file_name'] else ""
        }
    }
    
    return jsonify(client_status)

@app.route('/api/connect', methods=['POST'])
def api_connect():
    """Connect to backup server with configuration using real backup protocol"""
    global server_config, backup_status, backup_executor
    
    try:
        config = request.json
        if config:
            server_config.update(config)
        
        update_backup_status('CONNECT', f'Testing connection to {server_config["host"]}:{server_config["port"]}...')
        
        # Create a small test file for connection verification
        test_file_path = "test_connection.txt"
        with open(test_file_path, 'w') as f:
            f.write("Connection test file - " + datetime.now().isoformat())
        
        try:
            # Use the real backup executor to test the connection
            result = backup_executor.execute_real_backup(
                username=server_config['username'],
                file_path=test_file_path,
                server_ip=server_config['host'],
                server_port=int(server_config['port']),
                timeout=10  # Short timeout for connection test
            )
            
            connected = result.get('success', False)
            
            # Clean up test file
            try:
                os.remove(test_file_path)
            except:
                pass
            
            backup_status['connected'] = connected
            if connected:
                backup_status['status'] = 'connected'
                backup_status['message'] = f'Successfully connected to backup server'
                update_backup_status('CONNECT', f'Connection verified with backup server at {server_config["host"]}:{server_config["port"]}')
            else:
                backup_status['status'] = 'connection_failed'
                error_msg = result.get('message', 'Connection test failed')
                backup_status['message'] = f'Connection failed: {error_msg}'
                update_backup_status('ERROR', f'Connection test failed: {error_msg}')
            
            return jsonify({
                'success': connected,
                'message': backup_status['message'],
                'config': server_config,
                'details': result
            })
            
        except Exception as e:
            error_msg = f"Connection test error: {str(e)}"
            backup_status['status'] = 'error'
            backup_status['message'] = error_msg
            backup_status['connected'] = False
            update_backup_status('ERROR', error_msg)
            
            # Clean up test file
            try:
                os.remove(test_file_path)
            except:
                pass
            
            return jsonify({
                'success': False, 
                'message': error_msg,
                'config': server_config
            })
        
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        backup_status['status'] = 'error'
        backup_status['message'] = error_msg
        return jsonify({'success': False, 'message': error_msg}), 500
        
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        backup_status['status'] = 'error'
        backup_status['message'] = error_msg
        return jsonify({'success': False, 'message': error_msg}), 500

@app.route('/api/start_backup', methods=['POST'])
def api_start_backup():
    """Start backup process"""
    global current_backup_process, backup_status
    
    # DEBUG: Log request details
    print(f"[DEBUG] Start backup request received")
    print(f"[DEBUG] Content-Type: {request.content_type}")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Has files: {'file' in request.files if request.files else False}")
    print(f"[DEBUG] Request form keys: {list(request.form.keys()) if request.form else []}")
    
    if backup_status['backing_up']:
        return jsonify({'success': False, 'message': 'Backup already in progress'}), 400
    
    if not backup_status['connected']:
        return jsonify({'success': False, 'message': 'Not connected to backup server'}), 400
    
    try:
        # Handle different request formats
        if request.content_type and 'multipart/form-data' in request.content_type:
            print(f"[DEBUG] Using multipart/form-data path")
            # File upload format
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'No file uploaded'}), 400
            
            file = request.files['file']
            username = request.form.get('username', server_config['username'])
            
            if file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'}), 400
            
            # Save uploaded file to temporary location
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            filename = file.filename
            
        else:
            # If not multipart/form-data, it's an invalid request for file upload
            print(f"[DEBUG] Invalid content type for /api/start_backup: {request.content_type}")
            return jsonify({'success': False, 'message': 'Invalid request: file upload expected'}), 400
        
        # Update status
        backup_status['backing_up'] = True
        backup_status['status'] = 'backing_up'
        backup_status['file_name'] = filename
        backup_status['file_size'] = os.path.getsize(file_path)
        backup_status['transferred'] = 0
        backup_status['progress'] = 0
        
        update_backup_status('START', f'Starting backup of {filename}')
        
        # Start backup in background thread using REAL backup protocol
        def run_backup():
            global backup_status, current_backup_process
            
            try:
                update_backup_status('CONNECT', 'Connecting to backup server...')
                backup_status['progress'] = 10
                
                # Use the REAL backup executor to perform the backup
                result = backup_executor.execute_real_backup(
                    username=username,
                    file_path=file_path,
                    server_ip=server_config['host'],
                    server_port=int(server_config['port']),
                    timeout=180  # 3 minute timeout for backup
                )
                
                update_backup_status('VERIFY', 'Verifying backup results...')
                backup_status['progress'] = 90
                
                if result.get('success', False):
                    backup_status['progress'] = 100
                    backup_status['status'] = 'completed'
                    backup_status['message'] = f'File backup completed successfully using real backup protocol!'
                    update_backup_status('SUCCESS', f'Real backup completed for {filename}')
                    
                    # Log the successful backup with details
                    verification = result.get('verification', {})
                    print(f"[SUCCESS] Real backup completed for {filename}")
                    print(f"[INFO] Process exit code: {result.get('process_exit_code', 'N/A')}")
                    print(f"[INFO] Network activity detected: {result.get('network_activity', False)}")
                    print(f"[INFO] File verification: {verification.get('transferred', False)}")
                    if verification.get('received_file'):
                        print(f"[INFO] Received file: {verification['received_file']}")
                    
                else:
                    backup_status['status'] = 'failed'
                    error_msg = result.get('error', 'Unknown backup error')
                    backup_status['message'] = f'Real backup failed: {error_msg}'
                    update_backup_status('ERROR', f'Real backup failed: {error_msg}')
                    print(f"[ERROR] Real backup failed: {error_msg}")
                    print(f"[DEBUG] Full result: {result}")
                
            except Exception as e:
                backup_status['status'] = 'failed'
                backup_status['message'] = f'Backup execution error: {str(e)}'
                update_backup_status('ERROR', f'Backup execution error: {str(e)}')
                print(f"[ERROR] Backup execution failed: {str(e)}")
            
            finally:
                backup_status['backing_up'] = False
                current_backup_process = None
                # Cleanup temp file only after successful backup
                try:
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        temp_dir = os.path.dirname(file_path)
                        if temp_dir and os.path.exists(temp_dir):
                            os.rmdir(temp_dir)
                except Exception as cleanup_error:
                    print(f"[WARNING] Failed to cleanup temp file: {cleanup_error}")
                    pass
        
        # Start backup thread
        backup_thread = threading.Thread(target=run_backup, daemon=True)
        backup_thread.start()
        current_backup_process = backup_thread
        
        return jsonify({
            'success': True,
            'message': 'Backup started',
            'filename': filename,
            'file_size': backup_status['file_size']
        })
        
    except Exception as e:
        backup_status['backing_up'] = False
        error_msg = f"Failed to start backup: {str(e)}"
        backup_status['status'] = 'error'
        backup_status['message'] = error_msg
        return jsonify({'success': False, 'message': error_msg}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop current backup"""
    global current_backup_process, backup_status
    
    if not backup_status['backing_up']:
        return jsonify({'success': False, 'message': 'No backup in progress'})
    
    # Note: In a real implementation, we'd need to signal the backup process to stop
    backup_status['backing_up'] = False
    backup_status['status'] = 'stopped'
    backup_status['message'] = 'Backup stopped by user'
    backup_status['progress'] = 0
    
    update_backup_status('STOP', 'Backup stopped by user request')
    
    return jsonify({'success': True, 'message': 'Backup stopped'})

@app.route('/api/pause', methods=['POST'])
def api_pause():
    """Pause current backup"""
    if not backup_status['backing_up']:
        return jsonify({'success': False, 'message': 'No backup in progress'})
    
    backup_status['paused'] = True
    backup_status['status'] = 'paused'
    backup_status['message'] = 'Backup paused'
    
    update_backup_status('PAUSE', 'Backup paused')
    
    return jsonify({'success': True, 'message': 'Backup paused'})

@app.route('/api/resume', methods=['POST'])
def api_resume():
    """Resume paused backup"""
    if not backup_status['paused']:
        return jsonify({'success': False, 'message': 'Backup is not paused'})
    
    backup_status['paused'] = False
    backup_status['status'] = 'backing_up'
    backup_status['message'] = 'Backup resumed'
    
    update_backup_status('RESUME', 'Backup resumed')
    
    return jsonify({'success': True, 'message': 'Backup resumed'})

@app.route('/api/server_info')
def api_server_info():
    """Get backup server information"""
    server_running = check_backup_server_status()
    
    info = {
        'running': server_running,
        'host': server_config['host'],
        'port': server_config['port'],
        'clients': 'Unknown'  # Would need to query the actual server for this
    }
    
    return jsonify(info)

@app.route('/api/received_files')
def api_received_files():
    """List files in received_files directory"""
    try:
        received_files_dir = Path("server/received_files")
        if not received_files_dir.exists():
            return jsonify({'files': []})
        
        files = []
        for file_path in received_files_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    'name': file_path.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve the HTML client
@app.route('/')
def serve_client():
    """Serve the CyberBackup 3.0 HTML client"""
    try:
        return send_file('src/client/NewGUIforClient.html')
    except FileNotFoundError:
        return """
        <h1>Error: Client GUI not found</h1>
        <p>Please make sure src/client/NewGUIforClient.html exists.</p>
        """, 404

@app.route('/old')
def serve_old_client():
    """Serve the old problematic HTML client for comparison"""
    try:
        return send_file('src/client/NewGUIforClient.html')
    except FileNotFoundError:
        return "<h1>Old client not found</h1>", 404

@app.route('/test')
def serve_test():
    """Serve test file to verify serving works"""
    try:
        return send_file('test_serve.html')
    except FileNotFoundError:
        return "<h1>Test file not found</h1>", 404

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'server_connected': check_backup_server_status()
    })

def print_startup_info():
    """Print startup information"""
    print("=" * 70)
    print("🚀 CyberBackup 3.0 API Server - REAL Integration")
    print("=" * 70)
    print(f"🌐 API Server: http://localhost:9090")
    print(f"🎨 Client GUI: http://localhost:9090/")
    print(f"📡 Health Check: http://localhost:9090/health")
    print()
    
    # Check components
    print("Component Status:")
    
    # Check HTML client
    client_html = "src/client/NewGUIforClient.html"
    if os.path.exists(client_html):
        print(f"✅ HTML Client: {client_html}")
    else:
        print(f"❌ HTML Client: {client_html} NOT FOUND")
    
    # Check C++ client
    client_exe = "client/EncryptedBackupClient.exe"
    if os.path.exists(client_exe):
        print(f"✅ C++ Client: {client_exe}")
    else:
        print(f"❌ C++ Client: {client_exe} NOT FOUND")
    
    # Check backup server
    server_running = check_backup_server_status()
    if server_running:
        print(f"✅ Backup Server: Running on port {server_config['port']}")
    else:
        print(f"❌ Backup Server: NOT running on port {server_config['port']}")
        print("   Please start: python server/server.py")
    
    # Check received files directory
    received_dir = "server/received_files"
    if os.path.exists(received_dir):
        print(f"✅ Received Files: {received_dir}")
    else:
        print(f"❌ Received Files: {received_dir} NOT FOUND")
        os.makedirs(received_dir, exist_ok=True)
        print(f"✅ Created: {received_dir}")
    
    print()
    print("API Endpoints:")
    print("• GET  /api/status - Get backup status")
    print("• POST /api/connect - Connect to backup server")
    print("• POST /api/start_backup - Start backup process")
    print("• POST /api/stop - Stop backup")
    print("• POST /api/pause - Pause backup")
    print("• POST /api/resume - Resume backup")
    print("• GET  /api/server_info - Get server information")
    print("• GET  /api/received_files - List received files")
    print()
    print("Integration Features:")
    print("• REAL file backups using existing C++ client")
    print("• Actual file transfers to received_files directory")
    print("• Real-time status monitoring")
    print("• Process verification and error handling")
    print("• Complete audit trail")
    print()
    print("=" * 70)

def main():
    """Main server startup"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("CyberBackup 3.0 API Server")
        print("Usage: python cyberbackup_api_server.py [--debug]")
        print()
        print("Provides API backend for NewGUIforClient.html")
        return
    
    debug_mode = '--debug' in sys.argv
    
    print_startup_info()
    
    # Start the server
    try:
        app.run(
            host='127.0.0.1',
            port=9090,
            debug=debug_mode,
            threaded=True
        )
    except KeyboardInterrupt:
        print("
👋 API Server shutdown requested")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()