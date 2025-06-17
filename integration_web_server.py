#!/usr/bin/env python3
"""
Real Integration Web Server
Provides ACTUAL backup integration using the existing working C++ client
"""

import os
import sys
import json
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string

# Import our real backup executor
from real_backup_executor import RealBackupExecutor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Global variables
backup_executor = RealBackupExecutor()
active_backups = {}

def check_server_status():
    """Check if the Python backup server is running"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 1256))
        sock.close()
        
        if result == 0:
            # Try to get more details if possible
            return {'running': True, 'clients': 'Unknown'}
        else:
            return {'running': False, 'clients': 0}
    except Exception:
        return {'running': False, 'clients': 0}

@app.route('/')
def index():
    """Serve the main HTML interface"""
    try:
        with open('RealBackupClient.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Error: RealBackupClient.html not found</h1>
        <p>Please make sure RealBackupClient.html is in the same directory as this server.</p>
        """, 404

@app.route('/api/server-status')
def api_server_status():
    """Check backup server status"""
    status = check_server_status()
    return jsonify(status)

@app.route('/api/backup', methods=['POST'])
def api_backup():
    """Handle real backup requests"""
    try:
        # Get form data
        username = request.form.get('username')
        file = request.files.get('file')
        
        if not username or not file:
            return jsonify({'success': False, 'error': 'Missing username or file'}), 400
        
        # Validate username
        if len(username) > 100 or not username.strip():
            return jsonify({'success': False, 'error': 'Invalid username'}), 400
        
        # Save uploaded file to temporary location
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        file.save(temp_file_path)
        
        print(f"🔒 REAL BACKUP REQUEST:")
        print(f"   Username: {username}")
        print(f"   File: {file.filename} ({os.path.getsize(temp_file_path)} bytes)")
        print(f"   Temp Path: {temp_file_path}")
        print()
        
        # Execute REAL backup using the C++ client
        result = backup_executor.execute_real_backup(
            username=username.strip(),
            file_path=temp_file_path,
            server_ip="127.0.0.1",
            server_port=1256
        )
        
        # Cleanup temp file
        try:
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        print(f"🔒 BACKUP RESULT:")
        print(f"   Success: {result['success']}")
        print(f"   Duration: {result['duration']:.2f}s")
        print(f"   Process Exit Code: {result['process_exit_code']}")
        if result['verification']:
            v = result['verification']
            print(f"   File Transferred: {v['transferred']}")
            print(f"   Size Match: {v['size_match']} ({v['original_size']} -> {v['received_size']} bytes)")
            print(f"   Hash Match: {v['hash_match']}")
        print()
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ BACKUP ERROR: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/received-files')
def api_received_files():
    """List files in the received_files directory for verification"""
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

@app.route('/received-files/<filename>')
def download_received_file(filename):
    """Download a file from received_files directory"""
    try:
        received_files_dir = os.path.abspath("server/received_files")
        return send_from_directory(received_files_dir, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def print_startup_info():
    """Print startup information"""
    print("=" * 60)
    print("🔒 REAL ENCRYPTED BACKUP INTEGRATION SERVER")
    print("=" * 60)
    print(f"Server URL: http://localhost:5000")
    print(f"HTML Interface: http://localhost:5000/")
    print(f"API Endpoint: http://localhost:5000/api/backup")
    print()
    
    # Check components
    print("Component Status:")
    
    # Check C++ client
    client_exe = "client/EncryptedBackupClient.exe"
    if os.path.exists(client_exe):
        print(f"✅ C++ Client: {client_exe}")
    else:
        print(f"❌ C++ Client: {client_exe} NOT FOUND")
    
    # Check received files directory
    received_dir = "server/received_files"
    if os.path.exists(received_dir):
        print(f"✅ Received Files Directory: {received_dir}")
    else:
        print(f"❌ Received Files Directory: {received_dir} NOT FOUND")
        os.makedirs(received_dir, exist_ok=True)
        print(f"✅ Created: {received_dir}")
    
    # Check backup server
    server_status = check_server_status()
    if server_status['running']:
        print(f"✅ Backup Server: Running on port 1256")
    else:
        print(f"❌ Backup Server: NOT running on port 1256")
        print("   Please start the Python backup server (server.py)")
    
    print()
    print("Integration Features:")
    print("• REAL file uploads and transfers")
    print("• Actual C++ client execution")
    print("• File verification in received_files directory")
    print("• Process monitoring and exit code checking")
    print("• Network activity verification")
    print("• Complete audit trail")
    print()
    print("=" * 60)

def main():
    """Main server startup"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Real Integration Web Server")
        print("Usage: python integration_web_server.py [--debug]")
        print()
        print("This server provides REAL integration with the existing")
        print("EncryptedBackupClient.exe using actual file transfers.")
        return
    
    debug_mode = '--debug' in sys.argv
    
    print_startup_info()
    
    # Start the server
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=debug_mode,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server shutdown requested")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
