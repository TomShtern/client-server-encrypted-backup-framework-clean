#!/usr/bin/env python3
"""
Real Backup Executor - Smart Process Control for EncryptedBackupClient.exe
This module provides REAL integration with the existing C++ client, not fake APIs.
It is responsible for configuring and launching the C++ subprocess.
Progress monitoring and verification are handled by the UnifiedFileMonitor.
"""

import os
import contextlib
import sys
import time
import hashlib
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from Shared.utils.file_lifecycle import SynchronizedFileManager
from Shared.utils.error_handler import handle_subprocess_error, ErrorSeverity
from Shared.utils.process_monitor import stop_process

logger = logging.getLogger(__name__)

class RealBackupExecutor:
    """
    A simplified wrapper for EncryptedBackupClient.exe that provides real backup functionality
    by managing the C++ subprocess.
    """
    def __init__(self, client_exe_path: Optional[str] = None):
        if not client_exe_path:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            possible_paths = [
                os.path.join(project_root, "build", "Release", "EncryptedBackupClient.exe"),
                r"build\Release\EncryptedBackupClient.exe",
                r"EncryptedBackupClient.exe"
            ]
            self.client_exe = next((path for path in possible_paths if os.path.exists(path)), None)
            if not self.client_exe:
                self.client_exe = os.path.join(project_root, "build", "Release", "EncryptedBackupClient.exe")
        else:
            self.client_exe = client_exe_path

        self.temp_dir = tempfile.mkdtemp()
        self.backup_process: Optional[subprocess.Popen] = None
        self.status_callback: Optional[Callable] = None
        self.file_manager = SynchronizedFileManager(self.temp_dir)
        self.process_id: Optional[int] = None

    def is_running(self) -> bool:
        """Return True if a backup subprocess is currently running"""
        return bool(self.backup_process) and self.backup_process.poll() is None

    def cancel(self, reason: str = "User requested cancellation") -> bool:
        """Attempt to cancel the running backup subprocess gracefully."""
        if not self.backup_process or not self.process_id:
            self._log_status("CANCEL", "No active backup process to cancel")
            return False

        self._log_status("CANCEL", f"Cancelling backup process (PID: {self.process_id}) - {reason}")
        try:
            return stop_process(self.process_id, timeout=5.0)
        except Exception as e:
            self._log_status("ERROR", f"Cancellation error: {e}")
            return False

    def set_status_callback(self, callback: Callable[[str, Any], None]):
        """Set callback function for real-time status updates"""
        self.status_callback = callback

    def _log_status(self, phase: str, message: str):
        """Log status updates via callback"""
        logger.info(f"[{phase}] {message}")
        if self.status_callback:
            self.status_callback(phase, {'message': message})

    def _generate_transfer_info(self, server_ip: str, server_port: int, username: str, file_path: str) -> str:
        """Generate managed transfer.info file for the C++ client"""
        absolute_file_path = os.path.abspath(file_path)
        content = f"{server_ip}:{server_port}\n{username}\n{absolute_file_path}"
        self._log_status("CONFIG", f"transfer.info content:\n---\n{content}---")
        
        transfer_info_path = self.file_manager.create_managed_file("transfer.info", content)
        self._log_status("CONFIG", f"Generated managed transfer.info: {transfer_info_path}")
        return transfer_info_path

    def execute_real_backup(self, username: str, file_path: str, server_ip: str, server_port: int) -> Dict[str, Any]:
        """Executes the C++ client, waits for it to complete, and returns the result."""
        if not os.path.exists(self.client_exe):
            error_msg = f"C++ client not found at {self.client_exe}"
            self._log_status("ERROR", error_msg)
            return {'success': False, 'error': error_msg}

        file_id, transfer_info_path = None, None
        try:
            file_id, transfer_info_path = self._generate_transfer_info(server_ip, server_port, username, file_path)
            client_cwd = os.path.dirname(transfer_info_path)

            self._log_status("EXECUTION", f"Starting C++ client: {self.client_exe} with --batch flag")
            self.backup_process = subprocess.Popen(
                [self.client_exe, "--batch"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=client_cwd
            )
            self.process_id = self.backup_process.pid

            stdout, stderr = self.backup_process.communicate(timeout=120) # 2-minute timeout
            return_code = self.backup_process.returncode

            self._log_status("COMPLETION", f"C++ client finished with exit code: {return_code}")
            if stdout:
                logger.debug(f"C++ Client STDOUT:\n{stdout}")
            if stderr:
                logger.warning(f"C++ Client STDERR:\n{stderr}")

            if return_code != 0:
                handle_subprocess_error(
                    message=f"C++ client exited with non-zero code: {return_code}",
                    details=stderr,
                    component="RealBackupExecutor",
                    severity=ErrorSeverity.HIGH
                )
                return {'success': False, 'error': f"Client process failed with code {return_code}", 'details': stderr}

            return {'success': True, 'message': 'Client process completed successfully.'}

        except subprocess.TimeoutExpired:
            self._log_status("ERROR", "C++ client process timed out.")
            self.cancel("Timeout")
            return {'success': False, 'error': 'Process timed out'}
        except Exception as e:
            logger.critical(f"An unexpected error occurred during backup execution: {e}", exc_info=True)
            return {'success': False, 'error': f"An unexpected error occurred: {e}"}
        finally:
            if file_id:
                self.file_manager.cleanup_managed_file(file_id)
            self.backup_process = None
            self.process_id = None

    def execute_backup_with_verification(self, username: str, file_path: str, 
                           server_ip: str = "127.0.0.1", server_port: int = 1256,
                           timeout: int = 120) -> Dict[str, Any]:
        """Execute REAL backup using the C++ client with verification and robust progress.

        This rewritten implementation corrects prior indentation corruption and consolidates
        lifecycle management (transfer.info generation, subprocess launch, monitoring,
        verification and cleanup) inside a single well-structured try/except/finally block.
        """
        self._log_status("START", f"Starting REAL backup for {username}: {file_path}")

        result: Dict[str, Any] = {
            'success': False,
            'error': None,
            'process_exit_code': None,
            'verification': None,
            'duration': 0.0,
            'network_activity': False
        }

        start_time = time.time()
        monitor: Optional[RobustProgressMonitor] = None
        file_id: Optional[str] = None
        transfer_info_path: Optional[str] = None
        stdout: Union[bytes, str] = b''  # predefine
        stderr: Union[bytes, str] = b''

        try:
            # --- Pre-flight validation ---
            if not os.path.exists(file_path):
                handle_file_transfer_error(
                    message="Source file not found for backup",
                    details=f"File path: {file_path}",
                    component="pre_flight_check",
                    severity=ErrorSeverity.HIGH
                )
                raise FileNotFoundError(file_path)

            if not self.client_exe or not os.path.exists(self.client_exe):
                handle_subprocess_error(
                    message="Client executable not found",
                    details=f"Expected path: {self.client_exe}",
                    component="pre_flight_check",
                    severity=ErrorSeverity.CRITICAL
                )
                raise FileNotFoundError(self.client_exe or "<unset>")

            self._clear_cached_credentials_if_username_changed(username)

            # --- transfer.info management (isolated managed file) ---
            client_dir = os.path.dirname(self.client_exe)
            file_id, managed_transfer_path = self._generate_transfer_info(server_ip, server_port, username, file_path)
            try:
                target_path = os.path.join(client_dir, 'transfer.info')
                if os.path.exists(target_path):
                    with contextlib.suppress(Exception):
                        os.remove(target_path)
                with open(managed_transfer_path, 'r', encoding='utf-8') as src, open(target_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                transfer_info_path = target_path
                self._log_status('CONFIG', f'Copied managed transfer.info to working dir: {target_path}')
            except Exception as copy_err:
                self._log_status('WARNING', f'Failed to copy managed transfer.info to working dir: {copy_err}. Using managed path directly.')
                transfer_info_path = managed_transfer_path

            if file_id:
                with contextlib.suppress(Exception):
                    self.file_manager.mark_in_subprocess_use(file_id)

            # --- Subprocess launch via registry ---
            client_working_dir = client_dir
            process_id = f"backup_client_{int(time.time())}"
            command = [str(self.client_exe), '--batch']
            self._log_status('LAUNCH', f"Starting subprocess with process registry: {' '.join(command)}")
            try:
                registry = get_process_registry()
                register_process(
                    process_id=process_id,
                    name='EncryptedBackupClient',
                    command=command,
                    cwd=client_working_dir,
                    auto_restart=False,
                    max_restarts=0
                )
                if not start_process(process_id,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=False):
                    self._log_status('ERROR', f'Failed to start backup process {process_id}')
                    raise RuntimeError(f'Failed to start backup process {process_id}')
                self.backup_process = registry.subprocess_handles[process_id]
                self.process_id = process_id
            except Exception as launch_err:
                raise RuntimeError(f'Subprocess launch failed: {launch_err}')

            self._log_status('PROCESS', f'Started backup client (ID: {process_id}, PID: {self.backup_process.pid})')

            # --- Progress monitoring ---
            monitor = RobustProgressMonitor(self.server_received_files)
            monitor.set_status_callback(self.status_callback or self._log_status)
            monitor.start_monitoring({
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'original_filename': os.path.basename(file_path),
                'process': self.backup_process
            })

            # --- Active polling (non-blocking) ---
            try:
                stdout, stderr = self._monitor_with_active_polling(monitor, timeout)
            except subprocess.TimeoutExpired:
                self._log_status('TIMEOUT', 'Terminating backup process due to timeout')
                if self.backup_process:
                    with contextlib.suppress(Exception):
                        self.backup_process.kill()
                stdout, stderr = (b'', b'')
                result['process_exit_code'] = -1
                result['error'] = 'Process timed out'
            else:
                result['process_exit_code'] = self.backup_process.returncode if self.backup_process else None

            # --- Decode & finalize output ---
            decoded_stdout = stdout.decode('utf-8', errors='replace') if isinstance(stdout, (bytes, bytearray)) else str(stdout or '')
            decoded_stderr = stderr.decode('utf-8', errors='replace') if isinstance(stderr, (bytes, bytearray)) else str(stderr or '')
            if decoded_stdout and monitor:
                monitor.finalize_with_output(decoded_stdout)
            if decoded_stdout:
                self._log_status('CLIENT_STDOUT', decoded_stdout[:4000])
            if decoded_stderr:
                self._log_status('CLIENT_STDERR', decoded_stderr[:4000])
                result['error'] = result['error'] or decoded_stderr

            # --- Verification ---
            verification = self._verify_file_transfer(file_path, username)
            result['verification'] = verification
            process_success = (result.get('process_exit_code') == 0)
            verification_success = verification.get('transferred', False)

            if monitor:
                monitor.finalize_progress(process_success, verification_success)
                monitor.stop_monitoring()

            if verification_success:
                result['success'] = True
                if process_success:
                    self._log_status('SUCCESS', 'REAL backup completed and verified!')
                else:
                    self._log_status('SUCCESS', 'Backup verified though process exit code was non-zero')
            else:
                result['error'] = result['error'] or 'No file transfer detected - backup may have failed'
                self._log_status('FAILURE', result['error'])

        except Exception as e:
            result['error'] = str(e)
            self._log_status('ERROR', f'Backup execution failed: {e}')
            with contextlib.suppress(Exception):
                if monitor:
                    monitor.finalize_progress(False, False)
                    monitor.stop_monitoring()
        finally:
            result['duration'] = time.time() - start_time
            if file_id:
                with contextlib.suppress(Exception):
                    self.file_manager.safe_cleanup(file_id, wait_timeout=10.0)
            if transfer_info_path and os.path.exists(transfer_info_path):
                with contextlib.suppress(Exception):
                    os.remove(transfer_info_path)

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

    print("[SECURE] Real Backup Executor - Testing Mode")
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