#!/usr/bin/env python3
"""
Real Backup Executor - Smart Process Control for EncryptedBackupClient.exe
This module provides REAL integration with the existing C++ client, not fake APIs.
"""

import os
import sys
import time
import json
import hashlib
import subprocess
import threading
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Callable

import psutil

class RealBackupExecutor:
    """
    Smart wrapper for EncryptedBackupClient.exe that provides real backup functionality
    with automated process control and verification.
    """
    def __init__(self, client_exe_path: Optional[str] = None):
        # Try different possible locations for the client executable
        if not client_exe_path:
            possible_paths = [
                r"build\Release\EncryptedBackupClient.exe",
                r"client\EncryptedBackupClient_backup.exe",
                r"client\EncryptedBackupClient.exe",
                r"EncryptedBackupClient.exe"
            ]
            
            self.client_exe = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.client_exe = path
                    break
            
            if not self.client_exe:
                # Default to the most likely location
                self.client_exe = r"build\Release\EncryptedBackupClient.exe"
        else:
            self.client_exe = client_exe_path
        
        self.server_received_files = r"server\received_files"
        self.temp_dir = tempfile.mkdtemp()
        self.backup_process = None
        self.status_callback = None
        
        # Ensure directories exist
        os.makedirs(self.server_received_files, exist_ok=True)
        
    def set_status_callback(self, callback: Callable[[str, str], None]):
        """Set callback function for real-time status updates"""
        self.status_callback = callback
        
    def _log_status(self, phase: str, message: str):
        """Log status updates"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {phase}: {message}")
        if self.status_callback:
            self.status_callback(phase, message)
    
    def _generate_transfer_info(self, server_ip: str, server_port: int, 
                              username: str, file_path: str) -> str:
        """Generate transfer.info file for the C++ client"""
        # Convert to absolute path to ensure client finds the correct file
        absolute_file_path = os.path.abspath(file_path)
        
        transfer_info_path = os.path.join(self.temp_dir, "transfer.info")
        
        with open(transfer_info_path, 'w') as f:
            f.write(f"{server_ip}:{server_port}\n")
            f.write(f"{username}\n")
            f.write(f"{absolute_file_path}\n")
            
        self._log_status("CONFIG", f"Generated transfer.info: {server_ip}:{server_port}, {username}, {absolute_file_path}")
        return transfer_info_path
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for verification"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self._log_status("ERROR", f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _monitor_client_log(self, log_file: str, timeout: int = 300) -> bool:
        """Monitor client_debug.log for real progress updates"""
        self._log_status("MONITOR", f"Monitoring {log_file} for progress...")
        
        start_time = time.time()
        last_size = 0
        
        while time.time() - start_time < timeout:
            try:
                if os.path.exists(log_file):
                    current_size = os.path.getsize(log_file)
                    if current_size > last_size:
                        # Read new content
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            f.seek(last_size)
                            new_content = f.read()
                            
                        # Parse for meaningful status updates
                        for line in new_content.split('\n'):
                            line = line.strip()
                            if any(keyword in line.lower() for keyword in 
                                  ['connecting', 'connected', 'registering', 'registered', 
                                   'encrypting', 'transferring', 'complete', 'success', 'failed']):
                                self._log_status("CLIENT", line)
                        
                        last_size = current_size
                        
                        # Check for completion indicators
                        if 'backup completed successfully' in new_content.lower():
                            self._log_status("SUCCESS", "Client reported successful backup completion")
                            return True
                        elif 'failed' in new_content.lower() and 'fatal' in new_content.lower():
                            self._log_status("ERROR", "Client reported fatal error")
                            return False
                            
                time.sleep(1)
                
            except Exception as e:
                self._log_status("ERROR", f"Error monitoring log file: {e}")
                time.sleep(1)
        
        self._log_status("TIMEOUT", f"Log monitoring timed out after {timeout} seconds")
        return False
    
    def _verify_file_transfer(self, original_file: str, username: str) -> Dict[str, Any]:
        """Verify that file was actually transferred to server"""
        self._log_status("VERIFY", "Checking received_files directory for actual transfer...")
        
        verification = {
            'transferred': False,
            'file_found': False,
            'size_match': False,
            'hash_match': False,
            'received_file': None,
            'original_size': 0,
            'received_size': 0,
            'original_hash': '',
            'received_hash': ''
        }
        
        try:
            original_size = os.path.getsize(original_file)
            original_hash = self._calculate_file_hash(original_file)
            verification['original_size'] = original_size
            verification['original_hash'] = original_hash
            
            # Look for files in received_files directory
            received_files_dir = Path(self.server_received_files)
            if received_files_dir.exists():
                for received_file in received_files_dir.iterdir():
                    if received_file.is_file():
                        received_size = received_file.stat().st_size
                        received_hash = self._calculate_file_hash(str(received_file))
                        
                        self._log_status("VERIFY", f"Found file: {received_file.name}, size: {received_size}")
                        
                        # Check if this matches our uploaded file
                        if received_size == original_size:
                            verification['file_found'] = True
                            verification['received_file'] = str(received_file)
                            verification['received_size'] = received_size
                            verification['received_hash'] = received_hash
                            verification['size_match'] = True
                            
                            if received_hash == original_hash:
                                verification['hash_match'] = True
                                verification['transferred'] = True
                                self._log_status("SUCCESS", f"File transfer VERIFIED: {received_file.name}")
                                break
                            else:
                                self._log_status("ERROR", f"Hash mismatch for {received_file.name}")
                        
            if not verification['file_found']:
                self._log_status("ERROR", "No matching files found in received_files directory")
                
        except Exception as e:
            self._log_status("ERROR", f"Verification failed: {e}")
            
        return verification
    
    def _check_network_activity(self, server_port: int) -> bool:
        """Check for active network connections to server port"""
        try:
            connections = psutil.net_connections()
            for conn in connections:
                try:
                    # Check local address port
                    laddr_match = False
                    if hasattr(conn, 'laddr') and conn.laddr and hasattr(conn.laddr, 'port'):
                        laddr_match = conn.laddr.port == server_port
                    
                    # Check remote address port
                    raddr_match = False
                    if hasattr(conn, 'raddr') and conn.raddr and hasattr(conn.raddr, 'port'):
                        raddr_match = conn.raddr.port == server_port
                    
                    if laddr_match or raddr_match:
                        laddr_str = f"{conn.laddr}" if conn.laddr else "None"
                        raddr_str = f"{conn.raddr}" if conn.raddr else "None"
                        self._log_status("NETWORK", f"Active connection found: {laddr_str} -> {raddr_str}")
                        return True
                        
                except Exception as conn_error:
                    # Skip this connection if it has unexpected structure
                    self._log_status("DEBUG", f"Skipping connection due to attribute error: {conn_error}")
                    continue
                    
        except Exception as e:
            self._log_status("ERROR", f"Network check failed: {e}")
        return False
    
    def execute_real_backup(self, username: str, file_path: str, 
                           server_ip: str = "127.0.0.1", server_port: int = 1256, 
                           timeout: int = 30) -> Dict[str, Any]:
        """
        Execute REAL backup using the existing C++ client with full verification
        """
        self._log_status("START", f"Starting REAL backup for {username}: {file_path}")
        
        result = {
            'success': False,
            'error': None,
            'process_exit_code': None,
            'verification': None,
            'duration': 0,
            'network_activity': False
        }
        
        start_time = time.time()
        
        try:
            # Pre-flight checks
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file does not exist: {file_path}")
            
            if not self.client_exe or not os.path.exists(self.client_exe):
                raise FileNotFoundError(f"Client executable not found: {self.client_exe}")
            
            # Generate transfer.info
            transfer_info = self._generate_transfer_info(server_ip, server_port, username, file_path)
              # Copy transfer.info to client directory
            client_transfer_info = "transfer.info"
            with open(transfer_info, 'r') as src, open(client_transfer_info, 'w') as dst:
                dst.write(src.read())
            
            self._log_status("LAUNCH", f"Launching {self.client_exe}")
            # Launch client process with automated input handling and BATCH MODE
            if not self.client_exe:
                raise RuntimeError("Client executable path is not set")
                
            self.backup_process = subprocess.Popen(
                [self.client_exe, "--batch"],  # Use batch mode to prevent hanging
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(self.client_exe)) or '.'
            )
            
            # Start log monitoring in separate thread
            log_file = "client_debug.log"
            log_monitor_thread = threading.Thread(
                target=self._monitor_client_log, 
                args=(log_file, 180)  # 3 minute timeout
            )
            log_monitor_thread.daemon = True
            log_monitor_thread.start()
            # Monitor process - no need for manual input in batch mode
            self._log_status("PROCESS", "Monitoring backup process...")
            
            timeout = 300  # 5 minute timeout
            poll_interval = 2
            elapsed = 0
            
            while elapsed < timeout:
                # Check if process is still running
                poll_result = self.backup_process.poll()
                if poll_result is not None:
                    # Process finished
                    result['process_exit_code'] = poll_result
                    self._log_status("PROCESS", f"Client process finished with exit code: {poll_result}")
                    break
                
                # Check for network activity periodically
                if self._check_network_activity(server_port):
                    result['network_activity'] = True
                
                time.sleep(poll_interval)
                elapsed += poll_interval
                
            # If process is still running, terminate it
            if self.backup_process.poll() is None:
                self._log_status("TIMEOUT", "Terminating backup process due to timeout")
                self.backup_process.terminate()
                time.sleep(2)
                if self.backup_process.poll() is None:
                    self.backup_process.kill()
                result['process_exit_code'] = -1
            
            # Verify actual file transfer
            self._log_status("VERIFY", "Verifying actual file transfer...")
            verification = self._verify_file_transfer(file_path, username)
            result['verification'] = verification
            
            # Determine overall success based on concrete evidence
            if verification['transferred'] and result['process_exit_code'] == 0:
                result['success'] = True
                self._log_status("SUCCESS", "REAL backup completed and verified!")
            elif verification['transferred']:
                result['success'] = True
                result['error'] = f"File transferred but process exit code was {result['process_exit_code']}"
                self._log_status("WARNING", result['error'])
            else:
                result['error'] = "No file transfer detected - backup may have failed"
                self._log_status("FAILURE", result['error'])
            
        except Exception as e:
            result['error'] = str(e)
            self._log_status("ERROR", f"Backup execution failed: {e}")
        
        finally:
            result['duration'] = time.time() - start_time
            
            # Cleanup
            try:
                if os.path.exists("transfer.info"):
                    os.remove("transfer.info")
            except:
                pass
        
        return result


def main():
    """Test the real backup executor"""
    if len(sys.argv) < 3:
        print("Usage: python real_backup_executor.py <username> <file_path>")
        sys.exit(1)
    
    username = sys.argv[1]
    file_path = sys.argv[2]
    
    executor = RealBackupExecutor()
    
    def status_update(phase, message):
        print(f"STATUS: {phase} - {message}")
    
    executor.set_status_callback(status_update)
    
    print("🔒 Real Backup Executor - Testing Mode")
    print(f"Username: {username}")
    print(f"File: {file_path}")
    print()
    
    result = executor.execute_real_backup(username, file_path)
    
    print("\n" + "="*50)
    print("BACKUP EXECUTION RESULTS:")
    print("="*50)
    print(f"Success: {result['success']}")
    print(f"Duration: {result['duration']:.2f} seconds")
    print(f"Process Exit Code: {result['process_exit_code']}")
    print(f"Network Activity: {result['network_activity']}")
    if result['error']:
        print(f"Error: {result['error']}")
    
    if result['verification']:
        v = result['verification']
        print(f"\nFILE TRANSFER VERIFICATION:")
        print(f"File Found: {v['file_found']}")
        print(f"Size Match: {v['size_match']} ({v['original_size']} -> {v['received_size']})")
        print(f"Hash Match: {v['hash_match']}")
        print(f"Transferred: {v['transferred']}")
        if v['received_file']:
            print(f"Received File: {v['received_file']}")
    
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()