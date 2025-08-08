#!/usr/bin/env python3
"""
Minimal API Server for testing UUID fix
"""

import os
import time
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Minimal API Server - UUID Fix Test"

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'working', 'message': 'UUID fix applied'})

@app.route('/api/start_backup', methods=['POST'])
def api_start_backup_minimal():
    """Minimal backup endpoint to test UUID fix"""
    
    # Generate unique job ID without UUID issues
    job_id = f"job_{int(time.time() * 1000000)}"
    
    print(f"[API] Starting backup job: {job_id}")
    
    # Validate request
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Get form data
    username = request.form.get('username', 'TestUser')
    server_ip = request.form.get('server', '127.0.0.1')
    server_port = request.form.get('port', '1256')
    
    print(f"[API] Backup request - User: {username}, Server: {server_ip}:{server_port}")
    print(f"[API] File: {file.filename}")
    
    try:
        # Save file to temp location
        temp_dir = tempfile.mkdtemp()
        original_filename = file.filename or f"backup_file_{int(time.time())}"
        safe_temp_name = f"upload_{int(time.time() * 1000000)}_{original_filename}"
        temp_file_path = os.path.join(temp_dir, safe_temp_name)
        
        file.save(temp_file_path)
        
        # Verify file was saved
        if not os.path.exists(temp_file_path):
            return jsonify({'success': False, 'error': 'Failed to save uploaded file'}), 500
        
        file_size = os.path.getsize(temp_file_path)
        print(f"[API] File saved: {temp_file_path} ({file_size} bytes)")
        
        # Simulate successful backup (for testing)
        print(f"[API] Simulating backup for: {original_filename}")
        
        # Cleanup temp file
        try:
            os.unlink(temp_file_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': f'Backup completed for {original_filename}',
            'filename': original_filename,
            'username': username,
            'job_id': job_id,
            'file_size': file_size
        })

    except Exception as e:
        error_msg = f"Backup error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

if __name__ == "__main__":
    print("Minimal API Server - UUID Fix Test")
    print("=" * 50)
    print("Starting on http://127.0.0.1:9090")
    
    try:
        app.run(
            host='127.0.0.1',
            port=9090,
            debug=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n[INFO] Server shutdown requested")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
