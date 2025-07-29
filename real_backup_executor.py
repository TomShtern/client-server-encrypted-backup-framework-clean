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
from typing import Optional, Dict, Any, Callable, List

import psutil
from src.shared.utils.file_lifecycle import SynchronizedFileManager
from src.shared.utils.error_handler import (
    get_error_handler, handle_subprocess_error, handle_file_transfer_error,
    ErrorSeverity, ErrorCategory, ErrorCode
)
from src.shared.utils.process_monitor import (
    get_process_registry, register_process, start_process, stop_process,
    ProcessState, get_process_metrics
)

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
        
        self.server_received_files = r"src\server\received_files"
        self.temp_dir = tempfile.mkdtemp()
        self.backup_process = None
        self.status_callback = None
        self.file_manager = SynchronizedFileManager(self.temp_dir)
        
        # Ensure directories exist
        os.makedirs(self.server_received_files, exist_ok=True)
        
    def set_status_callback(self, callback: Callable[[str, Any], None]):
        """Set callback function for real-time status updates"""
        self.status_callback = callback
        
    def _log_status(self, phase: str, message: str):
        """Log status updates"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {phase}: {message}")
        if self.status_callback:
            # For simple string messages, wrap in a dict for consistency
            if isinstance(message, str):
                self.status_callback(phase, {'message': message})
            else:
                self.status_callback(phase, message)
    
    def _generate_transfer_info(self, server_ip: str, server_port: int, 
                              username: str, file_path: str) -> tuple:
        """Generate managed transfer.info file for the C++ client"""
        # Convert to absolute path to ensure client finds the correct file
        absolute_file_path = os.path.abspath(file_path)
        
        # Create transfer.info content
        content = f"{server_ip}:{server_port}\n{username}\n{absolute_file_path}\n"
        
        # Create managed file
        transfer_info_path = self.file_manager.create_managed_file("transfer.info", content)
        file_id = list(self.file_manager.managed_files.keys())[-1]
        
        self._log_status("CONFIG", f"Generated managed transfer.info: {server_ip}:{server_port}, {username}, {absolute_file_path}")
        return file_id, transfer_info_path

    def _clear_cached_credentials_if_username_changed(self, new_username: str):
        """Clear cached credentials if the username has changed to allow fresh registration"""
        try:
            # Check if me.info exists and has a different username
            me_info_paths = ["me.info", "data/me.info", "build/Release/me.info"]
            credentials_cleared = False

            for me_info_path in me_info_paths:
                if os.path.exists(me_info_path):
                    try:
                        with open(me_info_path, 'r') as f:
                            cached_username = f.readline().strip()

                        if cached_username and cached_username != new_username:
                            os.remove(me_info_path)
                            self._log_status("CLEANUP", f"Removed cached credentials for '{cached_username}' (switching to '{new_username}')")
                            credentials_cleared = True
                    except Exception as e:
                        self._log_status("WARNING", f"Could not check {me_info_path}: {e}")

            # Also clear private key files if credentials were cleared
            if credentials_cleared:
                priv_key_paths = ["priv.key", "build/Release/priv.key"]
                for priv_key_path in priv_key_paths:
                    if os.path.exists(priv_key_path):
                        try:
                            os.remove(priv_key_path)
                            self._log_status("CLEANUP", f"Removed cached private key: {priv_key_path}")
                        except Exception as e:
                            self._log_status("WARNING", f"Could not remove {priv_key_path}: {e}")

                self._log_status("INFO", f"Client will register fresh with username: {new_username}")
            else:
                self._log_status("INFO", f"Using username: {new_username}")

        except Exception as e:
            self._log_status("WARNING", f"Error checking cached credentials: {e}")
    
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
    
    def _monitor_process_health(self, process: subprocess.Popen) -> Dict[str, Any]:
        """Comprehensive process health monitoring with psutil"""
        try:
            proc = psutil.Process(process.pid)
            health_data = {
                'pid': process.pid,
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_mb': proc.memory_info().rss / 1024 / 1024,
                'status': proc.status(),
                'num_threads': proc.num_threads(),
                'open_files': len(proc.open_files()),
                'connections': len(proc.connections()),
                'create_time': proc.create_time(),
                'is_running': proc.is_running()
            }
            
            # Detect potential issues
            health_data['is_responsive'] = self._check_process_responsiveness(health_data)
            health_data['warnings'] = self._detect_health_warnings(health_data)
            
            return health_data
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self._log_status("WARNING", f"Process monitoring failed: {e}")
            return {'error': 'Process monitoring failed', 'exception': str(e)}
    
    def _check_process_responsiveness(self, health_data: Dict[str, Any]) -> bool:
        """Check if process appears responsive based on health metrics"""
        # High CPU usage might indicate heavy processing (normal)
        # but combined with no threads might indicate hanging
        cpu_percent = health_data.get('cpu_percent', 0)
        num_threads = health_data.get('num_threads', 0)
        
        if cpu_percent > 95 and num_threads <= 1:
            return False  # Potentially hung
        
        return True
    
    def _detect_health_warnings(self, health_data: Dict[str, Any]) -> List[str]:
        """Detect warning conditions from health metrics"""
        warnings = []
        
        cpu_percent = health_data.get('cpu_percent', 0)
        memory_mb = health_data.get('memory_mb', 0)
        open_files = health_data.get('open_files', 0)
        
        if cpu_percent > 90:
            warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        if memory_mb > 500:  # 500MB seems high for the client
            warnings.append(f"High memory usage: {memory_mb:.1f}MB")
        
        if open_files > 50:
            warnings.append(f"Many open files: {open_files}")
        
        return warnings
    
    def _detect_execution_phase(self, log_content: str) -> str:
        """Detect current execution phase from log content"""
        if not log_content:
            return "unknown"
        
        # Define phase detection patterns
        phase_patterns = {
            'initialization': ['starting', 'initializing', 'loading', 'begin'],
            'connection': ['connecting', 'handshake', 'protocol', 'socket'],
            'authentication': ['registering', 'login', 'credentials', 'auth'],
            'encryption': ['encrypting', 'key generation', 'crypto', 'aes', 'rsa'],
            'transfer': ['uploading', 'sending', 'transfer', 'progress', 'chunk'],
            'verification': ['verifying', 'checksum', 'validation', 'crc'],
            'completion': ['completed', 'finished', 'success', 'done']
        }
        
        # Check most recent content first
        recent_content = log_content.lower()
        
        # Reverse order to get the latest phase
        for phase, keywords in reversed(phase_patterns.items()):
            if any(keyword in recent_content for keyword in keywords):
                return phase
        
        return "unknown"
    
    def _read_stderr_nonblocking(self) -> str:
        """Read stderr from subprocess without blocking"""
        if not self.backup_process or not self.backup_process.stderr:
            return ""
        
        try:
            # Use select on Unix or similar approach
            import select
            import sys
            
            if sys.platform == "win32":
                # Windows doesn't support select on pipes, use peek approach
                return ""  # Simplified for Windows
            else:
                ready, _, _ = select.select([self.backup_process.stderr], [], [], 0)
                if ready:
                    return self.backup_process.stderr.read(1024)
        except Exception as e:
            self._log_status("DEBUG", f"stderr read failed: {e}")
        
        return ""
    
    def _correlate_subprocess_errors(self, stderr_line: str, health_data: Dict[str, Any]) -> None:
        """Correlate subprocess errors with system state and report to error framework"""
        if not stderr_line and not health_data.get('warnings'):
            return

        # High resource usage errors
        warnings = health_data.get('warnings', [])
        if warnings:
            warning_msg = "; ".join(warnings)
            handle_subprocess_error(
                message="Subprocess resource warning detected",
                details=f"Health warnings: {warning_msg}",
                component="subprocess_monitoring",
                severity=ErrorSeverity.MEDIUM
            )

        # stderr content errors
        if stderr_line and any(keyword in stderr_line.lower() for keyword in ['error', 'failed', 'exception']):
            handle_subprocess_error(
                message="Subprocess error detected in stderr",
                details=f"stderr: {stderr_line.strip()}",
                component="subprocess_stderr",
                severity=ErrorSeverity.HIGH
            )

        # Unresponsive process
        if not health_data.get('is_responsive', True):
            handle_subprocess_error(
                message="Subprocess appears unresponsive",
                details=f"Health data: {health_data}",
                component="subprocess_health",
                severity=ErrorSeverity.HIGH
            )

    def get_enhanced_process_metrics(self) -> Optional[Dict[str, Any]]:
        """Get enhanced process metrics from the monitoring system"""
        if not hasattr(self, 'process_id'):
            return None

        registry = get_process_registry()
        process_info = registry.get_process_info(self.process_id)

        if not process_info:
            return None

        # Get latest metrics
        metrics_history = list(process_info.metrics_history)
        if not metrics_history:
            return None

        latest_metrics = metrics_history[-1]

        return {
            'process_id': self.process_id,
            'process_name': process_info.name,
            'state': process_info.state.value,
            'pid': process_info.pid,
            'start_time': process_info.start_time.isoformat(),
            'restart_count': process_info.restart_count,
            'error_count': process_info.error_count,
            'last_error': process_info.last_error,
            'latest_metrics': {
                'timestamp': latest_metrics.timestamp.isoformat(),
                'cpu_percent': latest_metrics.cpu_percent,
                'memory_mb': latest_metrics.memory_mb,
                'memory_percent': latest_metrics.memory_percent,
                'num_threads': latest_metrics.num_threads,
                'open_files': latest_metrics.open_files,
                'connections': latest_metrics.connections,
                'io_read_bytes': latest_metrics.io_read_bytes,
                'io_write_bytes': latest_metrics.io_write_bytes,
                'status': latest_metrics.status,
                'is_responsive': latest_metrics.is_responsive,
                'warnings': latest_metrics.warnings
            },
            'metrics_count': len(metrics_history)
        }
    
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
        transfer_file_id = None  # Initialize to prevent unbound variable error
        
        try:
            # Pre-flight checks with structured error handling
            if not os.path.exists(file_path):
                error_info = handle_file_transfer_error(
                    message="Source file not found for backup",
                    details=f"File path: {file_path}",
                    component="pre_flight_check",
                    severity=ErrorSeverity.HIGH
                )
                raise FileNotFoundError(f"Source file does not exist: {file_path}")

            if not self.client_exe or not os.path.exists(self.client_exe):
                error_info = handle_subprocess_error(
                    message="Client executable not found",
                    details=f"Expected path: {self.client_exe}",
                    component="pre_flight_check",
                    severity=ErrorSeverity.CRITICAL
                )
                raise FileNotFoundError(f"Client executable not found: {self.client_exe}")

            # Clear cached credentials if username has changed
            self._clear_cached_credentials_if_username_changed(username)

            # Generate managed transfer.info
            transfer_file_id, transfer_info_path = self._generate_transfer_info(server_ip, server_port, username, file_path)

            # Copy transfer.info to BOTH the client executable directory AND the working directory
            # The client looks for transfer.info in the current working directory, not the executable directory
            client_dir = os.path.dirname(self.client_exe)
            client_transfer_info = os.path.join(client_dir, "transfer.info")
            working_dir_transfer_info = "transfer.info"  # Current working directory

            # Use synchronized file manager to copy to required locations
            target_locations = [client_transfer_info, working_dir_transfer_info]
            copy_locations = self.file_manager.copy_to_locations(transfer_file_id, target_locations)

            self._log_status("CONFIG", f"Copied transfer.info to {len(copy_locations)} locations: {copy_locations}")
            
            self._log_status("LAUNCH", f"Launching {self.client_exe}")
            # Launch client process with automated input handling and BATCH MODE
            if not self.client_exe:
                raise RuntimeError("Client executable path is not set")

            # Mark file as in use by subprocess to prevent premature cleanup
            self.file_manager.mark_in_subprocess_use(transfer_file_id)
            
            # Use the current working directory (where we copied transfer.info) instead of client directory
            # This ensures the client finds transfer.info in the current working directory
            current_working_dir = os.getcwd()
            self._log_status("DEBUG", f"Client executable: {os.path.abspath(self.client_exe)}")
            self._log_status("DEBUG", f"Client working directory: {current_working_dir}")
            self._log_status("DEBUG", f"Transfer.info location: {os.path.join(current_working_dir, 'transfer.info')}")

            # Register process with enhanced monitoring system
            process_id = f"backup_client_{int(time.time())}"
            command = [self.client_exe, "--batch"]  # Use batch mode to disable web GUI and prevent port conflicts

            registry = get_process_registry()
            process_info = register_process(
                process_id=process_id,
                name="EncryptedBackupClient",
                command=command,
                cwd=current_working_dir,
                auto_restart=False,  # Don't auto-restart backup processes
                max_restarts=0
            )

            # Start process with enhanced monitoring
            if not start_process(process_id,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True):
                raise RuntimeError(f"Failed to start backup process {process_id}")

            # Get the subprocess handle for compatibility
            self.backup_process = registry.subprocess_handles[process_id]
            self.process_id = process_id

            self._log_status("PROCESS", f"Started backup client with enhanced monitoring (ID: {process_id}, PID: {self.backup_process.pid})")
            
            # Start log monitoring in separate thread
            log_file = "client_debug.log"
            log_monitor_thread = threading.Thread(
                target=self._monitor_client_log, 
                args=(log_file, 180)  # 3 minute timeout
            )
            log_monitor_thread.daemon = True
            log_monitor_thread.start()
            # Enhanced subprocess monitoring with health checks and phase detection
            self._log_status("PROCESS", "Starting enhanced backup process monitoring...")

            timeout = 30  # 30 second timeout for connection test
            poll_interval = 2
            elapsed = 0
            latest_log_content = ""
            current_phase = "initialization"
            
            while elapsed < timeout:
                # Check if process is still running
                poll_result = self.backup_process.poll()
                if poll_result is not None:
                    # Process finished
                    result['process_exit_code'] = poll_result
                    self._log_status("PROCESS", f"Client process finished with exit code: {poll_result}")
                    break
                
                # Enhanced monitoring with health metrics
                health_data = self._monitor_process_health(self.backup_process)
                result['health_data'] = health_data
                
                # Monitor stderr for real-time errors
                stderr_data = self._read_stderr_nonblocking()
                
                # Read latest log content for phase detection
                try:
                    if os.path.exists(log_file):
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            latest_log_content = f.read()[-1000:]  # Last 1000 chars
                            current_phase = self._detect_execution_phase(latest_log_content)
                except Exception as e:
                    self._log_status("DEBUG", f"Log read for phase detection failed: {e}")
                
                # Correlate subprocess errors with health and stderr
                self._correlate_subprocess_errors(stderr_data, health_data)
                
                # Progress estimation based on phase
                progress_phases = ['initialization', 'connection', 'authentication', 'encryption', 'transfer', 'verification', 'completion']
                try:
                    phase_index = progress_phases.index(current_phase)
                    progress_percent = (phase_index / len(progress_phases)) * 100
                except ValueError:
                    progress_percent = 0
                
                result['current_phase'] = current_phase
                result['progress_percent'] = progress_percent
                
                # Enhanced status callback with enriched data
                if self.status_callback:
                    status_data = {
                        'progress': progress_percent,
                        'health': health_data,
                        'network_active': self._check_network_activity(server_port),
                        'elapsed_time': elapsed,
                        'warnings': health_data.get('warnings', [])
                    }
                    self.status_callback(current_phase, status_data)
                
                # Check for network activity periodically
                if self._check_network_activity(server_port):
                    result['network_activity'] = True
                
                # Log enhanced monitoring data
                warnings_str = ", ".join(health_data.get('warnings', [])) or "none"
                self._log_status("MONITOR", 
                    f"Phase: {current_phase}, Progress: {progress_percent:.0f}%, "
                    f"CPU: {health_data.get('cpu_percent', 0):.1f}%, "
                    f"Memory: {health_data.get('memory_mb', 0):.1f}MB, "
                    f"Warnings: {warnings_str}")
                
                time.sleep(poll_interval)
                elapsed += poll_interval
                
            # If process is still running, terminate it using enhanced monitoring
            if self.backup_process.poll() is None:
                self._log_status("TIMEOUT", "Terminating backup process due to timeout")
                if hasattr(self, 'process_id'):
                    # Use enhanced monitoring to stop process gracefully
                    stop_process(self.process_id, timeout=5.0)
                else:
                    # Fallback to direct termination
                    self.backup_process.terminate()
                    time.sleep(2)
                    if self.backup_process.poll() is None:
                        self.backup_process.kill()
                result['process_exit_code'] = -1
            
            # Release subprocess reference to allow safe cleanup
            self.file_manager.release_subprocess_use(transfer_file_id)
            
            # Verify actual file transfer
            self._log_status("VERIFY", "Verifying actual file transfer...")
            verification = self._verify_file_transfer(file_path, username)
            result['verification'] = verification
            
            # Determine overall success based on concrete evidence
            # Prioritize file transfer verification over process exit code
            if verification['transferred']:
                result['success'] = True
                if result['process_exit_code'] == 0:
                    self._log_status("SUCCESS", "REAL backup completed and verified!")
                else:
                    result['error'] = f"File transferred successfully but process exit code was {result['process_exit_code']}"
                    self._log_status("SUCCESS", f"REAL backup completed and verified! (Process was killed but transfer succeeded)")
            else:
                result['error'] = "No file transfer detected - backup may have failed"
                self._log_status("FAILURE", result['error'])
            
        except Exception as e:
            result['error'] = str(e)
            self._log_status("ERROR", f"Backup execution failed: {e}")
        
        finally:
            result['duration'] = time.time() - start_time
            
            # Safe cleanup using SynchronizedFileManager
            try:
                if transfer_file_id is not None:
                    self._log_status("CLEANUP", "Starting safe cleanup of transfer.info files")
                    # Wait for subprocess completion before cleanup
                    cleanup_success = self.file_manager.safe_cleanup(transfer_file_id, wait_timeout=10.0)
                    if cleanup_success:
                        self._log_status("CLEANUP", "Successfully cleaned up transfer.info files")
                    else:
                        self._log_status("WARNING", "Some files may not have been cleaned up properly")
            except Exception as e:
                self._log_status("WARNING", f"Error during safe cleanup: {e}")
        
        return result


def main():
    """Test the real backup executor"""
    if len(sys.argv) < 3:
        print("Usage: python real_backup_executor.py <username> <file_path>")
        sys.exit(1)
    
    username = sys.argv[1]
    file_path = sys.argv[2]
    
    executor = RealBackupExecutor()
    
    def status_update(phase, data):
        if isinstance(data, dict):
            if 'message' in data:
                print(f"STATUS: {phase} - {data['message']}")
            else:
                # Handle rich status data
                progress = data.get('progress', 0)
                warnings = data.get('warnings', [])
                warnings_str = f" (Warnings: {', '.join(warnings)})" if warnings else ""
                print(f"STATUS: {phase} - Progress: {progress:.0f}%{warnings_str}")
        else:
            print(f"STATUS: {phase} - {data}")
    
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