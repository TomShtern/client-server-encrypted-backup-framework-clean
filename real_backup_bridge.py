#!/usr/bin/env python3
"""
Real Backup Bridge - Connects HTML client to real backup system
This script provides HTTP API endpoints that call the actual backup client
"""

import http.server
import socketserver
import json
import subprocess
import threading
import time
import os
from urllib.parse import urlparse, parse_qs

class BackupState:
    def __init__(self):
        self.phase = "READY"
        self.status = "Backup bridge ready"
        self.progress = 0
        self.connected = False
        self.client_id = ""
        self.backup_process = None
        
    def to_dict(self):
        return {
            "phase": self.phase,
            "status": self.status,
            "progress": self.progress,
            "connected": self.connected,
            "client_id": self.client_id
        }

backup_state = BackupState()

class BackupHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = backup_state.to_dict()
            self.wfile.write(json.dumps(response).encode())
            print(f"[API] Status request: {response}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode()) if post_data else {}
        except:
            data = {}

        response = {"success": False, "message": "Unknown endpoint"}

        if self.path == '/api/connect':
            print(f"[API] Connect request: {data}")
            backup_state.phase = "CONNECTING"
            backup_state.status = "Connecting to real backup server..."
            
            # Test connection to Python backup server
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('127.0.0.1', 1256))
                sock.close()
                
                if result == 0:
                    backup_state.connected = True
                    backup_state.phase = "CONNECTED"
                    backup_state.status = "Connected to backup server"
                    backup_state.client_id = f"CLIENT_{int(time.time())}"
                    response = {"success": True, "message": "Connected to real backup server", "client_id": backup_state.client_id}
                    print(f"[SUCCESS] Connected to backup server on port 1256")
                else:
                    backup_state.phase = "ERROR"
                    backup_state.status = "Failed to connect to backup server"
                    response = {"success": False, "message": "Backup server not available on port 1256"}
                    print(f"[ERROR] Backup server not available on port 1256")
            except Exception as e:
                backup_state.phase = "ERROR"
                backup_state.status = f"Connection error: {str(e)}"
                response = {"success": False, "message": str(e)}
                print(f"[ERROR] Connection error: {e}")

        elif self.path == '/api/backup':
            print(f"[API] Backup request: {data}")
            if not backup_state.connected:
                response = {"success": False, "message": "Not connected to backup server"}
            else:
                # Start real backup using the C++ client
                def run_real_backup():
                    try:
                        backup_state.phase = "BACKUP_IN_PROGRESS"
                        backup_state.status = "Starting real backup..."
                        backup_state.progress = 0
                        print(f"[BACKUP] Starting real backup using C++ client")
                        
                        # Change to client directory and run the real backup client
                        client_dir = os.path.join(os.path.dirname(__file__), 'client')
                        client_exe = os.path.join(client_dir, 'EncryptedBackupClient.exe')
                        
                        if os.path.exists(client_exe):
                            print(f"[BACKUP] Executing: {client_exe}")
                            backup_state.status = "Running C++ backup client..."
                            
                            # Run the backup client
                            process = subprocess.Popen(
                                [client_exe],
                                cwd=client_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            backup_state.backup_process = process
                            
                            # Monitor progress
                            for i in range(10):
                                if process.poll() is not None:
                                    break
                                backup_state.progress = min(90, i * 10)
                                backup_state.status = f"Backup in progress: {backup_state.progress}%"
                                time.sleep(2)
                            
                            # Wait for completion
                            stdout, stderr = process.communicate()
                            
                            if process.returncode == 0:
                                backup_state.phase = "COMPLETED"
                                backup_state.status = "Real backup completed successfully"
                                backup_state.progress = 100
                                print(f"[SUCCESS] Backup completed successfully")
                                print(f"[OUTPUT] {stdout}")
                            else:
                                backup_state.phase = "ERROR"
                                backup_state.status = f"Backup failed (exit code: {process.returncode})"
                                print(f"[ERROR] Backup failed: {stderr}")
                        else:
                            backup_state.phase = "ERROR"
                            backup_state.status = "C++ backup client not found"
                            print(f"[ERROR] Client executable not found: {client_exe}")
                            
                    except Exception as e:
                        backup_state.phase = "ERROR"
                        backup_state.status = f"Backup error: {str(e)}"
                        print(f"[ERROR] Backup exception: {e}")
                
                # Start backup in background thread
                backup_thread = threading.Thread(target=run_real_backup)
                backup_thread.daemon = True
                backup_thread.start()
                
                response = {"success": True, "message": "Real backup started", "task_id": f"BACKUP_{int(time.time())}"}

        elif self.path == '/api/stop':
            print(f"[API] Stop request")
            if backup_state.backup_process:
                backup_state.backup_process.terminate()
            backup_state.phase = "STOPPED"
            backup_state.status = "Backup stopped"
            backup_state.progress = 0
            response = {"success": True, "message": "Backup stopped"}

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def main():
    port = 9090
    print(f"Starting REAL Backup Bridge Server on port {port}")
    print(f"This server will call the actual C++ backup client")
    print(f"HTML client can connect to http://127.0.0.1:{port}")
    
    with socketserver.TCPServer(("", port), BackupHandler) as httpd:
        print(f"REAL Backup Bridge ready on port {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
