"""
Server Singleton Manager - Ensures only one Python server instance runs at a time
Provides multiple mechanisms to prevent multiple server instances:
1. PID file locking 
2. Socket binding check
3. File locking mechanism
4. Process checking
"""

import os
import sys
import time
import signal
import socket
import atexit
import logging
from pathlib import Path
from typing import Optional

# Try to import psutil for advanced process checking
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Try to import fcntl for file locking (Unix/Linux)
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

logger = logging.getLogger(__name__)

class ServerSingletonManager:
    """Manages single server instance enforcement using multiple mechanisms."""
    
    def __init__(self, server_name: str = "BackupServer", port: int = 1256):
        """
        Initialize the singleton manager.
        
        Args:
            server_name: Name of the server process
            port: Port the server will bind to
        """
        self.server_name = server_name
        self.port = port
        self.pid_file = Path(f"{server_name}_{port}.pid")
        self.lock_file = Path(f"{server_name}_{port}.lock")
        self.lock_fd: Optional[int] = None
        self.is_locked = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def acquire_singleton_lock(self) -> bool:
        """
        Acquire singleton lock using multiple mechanisms.
        
        Returns:
            True if lock acquired successfully, False if another instance is running
        """
        try:
            # Method 1: Check if port is already in use
            if self._is_port_in_use():
                logger.error(f"Port {self.port} is already in use by another process")
                return False
            
            # Method 2: Check PID file
            if self._check_pid_file():
                logger.error("Another server instance is already running (PID file check)")
                return False
            
            # Method 3: File locking mechanism
            if not self._acquire_file_lock():
                logger.error("Could not acquire file lock - another instance may be running")
                return False
            
            # Method 4: Process name checking
            if self._check_running_processes():
                logger.error("Found another server process with same name")
                return False
            
            # All checks passed - create PID file and mark as locked
            self._create_pid_file()
            self.is_locked = True
            
            logger.info(f"Successfully acquired singleton lock for {self.server_name} on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error acquiring singleton lock: {e}")
            self.cleanup()
            return False
    
    def _is_port_in_use(self) -> bool:
        """Check if the port is already in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                result = sock.bind(('127.0.0.1', self.port))
                return False  # Port is available
        except OSError:
            return True  # Port is in use
    
    def _check_pid_file(self) -> bool:
        """Check if PID file exists and contains a running process."""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            if self._is_process_running(pid):
                logger.warning(f"Found running process with PID {pid} from PID file")
                return True
            else:
                # Stale PID file - remove it
                logger.info(f"Removing stale PID file for process {pid}")
                self.pid_file.unlink()
                return False
                
        except (ValueError, OSError) as e:
            logger.warning(f"Error reading PID file: {e}")
            # Remove corrupted PID file
            try:
                self.pid_file.unlink()
            except OSError:
                pass
            return False
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        if HAS_PSUTIL:
            try:
                return psutil.pid_exists(pid)
            except (psutil.Error, OSError):
                return False
        else:
            # Fallback for Windows without psutil
            try:
                if sys.platform == "win32":
                    import subprocess
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                          capture_output=True, text=True)
                    return str(pid) in result.stdout
                else:
                    # Unix-like systems
                    try:
                        os.kill(pid, 0)
                        return True
                    except OSError:
                        return False
            except Exception:
                return False
    
    def _acquire_file_lock(self) -> bool:
        """Acquire exclusive file lock."""
        if not HAS_FCNTL:
            # Windows fallback - use file existence as lock
            try:
                if self.lock_file.exists():
                    # Check if lock is stale
                    try:
                        with open(self.lock_file, 'r') as f:
                            pid = int(f.read().strip())
                        if not self._is_process_running(pid):
                            # Stale lock, remove it
                            self.lock_file.unlink()
                        else:
                            return False  # Active lock
                    except (ValueError, OSError):
                        # Corrupted lock file, remove it
                        self.lock_file.unlink()
                
                # Create new lock file
                with open(self.lock_file, 'w') as f:
                    f.write(str(os.getpid()))
                return True
                
            except OSError:
                return False
        
        try:
            self.lock_fd = os.open(str(self.lock_file), os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write current PID to lock file
            os.write(self.lock_fd, str(os.getpid()).encode())
            os.fsync(self.lock_fd)
            
            return True
            
        except (OSError, IOError) as e:
            if self.lock_fd:
                try:
                    os.close(self.lock_fd)
                except OSError:
                    pass
                self.lock_fd = None
            return False
    
    def _check_running_processes(self) -> bool:
        """Check for other running server processes."""
        if not HAS_PSUTIL:
            # Simplified check without psutil
            try:
                if sys.platform == "win32":
                    import subprocess
                    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                          capture_output=True, text=True)
                    lines = result.stdout.split('\n')
                    python_processes = [line for line in lines if 'python.exe' in line.lower()]
                    # Basic heuristic - if more than 2 python processes, might be another server
                    return len(python_processes) > 2
                else:
                    return False  # Skip process checking on Unix without psutil
            except Exception:
                return False
        
        try:
            current_pid = os.getpid()
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['pid'] == current_pid:
                        continue
                    
                    # Check process name and command line
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if ('server.py' in cmdline and 
                        'python' in proc.info['name'].lower() and
                        str(self.port) in cmdline):
                        logger.warning(f"Found potential server process: PID {proc.info['pid']}, CMD: {cmdline}")
                        return True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking running processes: {e}")
            return False
    
    def _create_pid_file(self) -> None:
        """Create PID file with current process ID."""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.debug(f"Created PID file: {self.pid_file}")
        except OSError as e:
            logger.error(f"Failed to create PID file: {e}")
    
    def cleanup(self) -> None:
        """Clean up all locks and files."""
        if not self.is_locked:
            return
        
        try:
            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
                logger.debug(f"Removed PID file: {self.pid_file}")
        except OSError as e:
            logger.warning(f"Failed to remove PID file: {e}")
        
        try:
            # Release file lock
            if self.lock_fd and HAS_FCNTL:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
                self.lock_fd = None
                logger.debug("Released file lock")
        except OSError as e:
            logger.warning(f"Failed to release file lock: {e}")
        
        try:
            # Remove lock file
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.debug(f"Removed lock file: {self.lock_file}")
        except OSError as e:
            logger.warning(f"Failed to remove lock file: {e}")
        
        self.is_locked = False
        logger.info("Singleton cleanup completed")
    
    def force_cleanup_stale_locks(self) -> None:
        """Force cleanup of stale lock files (use with caution)."""
        logger.warning("Forcing cleanup of potentially stale lock files...")
        
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                logger.info(f"Force removed PID file: {self.pid_file}")
        except OSError as e:
            logger.error(f"Failed to force remove PID file: {e}")
        
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.info(f"Force removed lock file: {self.lock_file}")
        except OSError as e:
            logger.error(f"Failed to force remove lock file: {e}")


def ensure_single_server_instance(server_name: str = "BackupServer", port: int = 1256) -> ServerSingletonManager:
    """
    Convenience function to ensure only one server instance runs.
    
    Args:
        server_name: Name of the server process
        port: Port the server will bind to
        
    Returns:
        ServerSingletonManager instance if successful
        
    Raises:
        SystemExit: If another instance is already running
    """
    singleton = ServerSingletonManager(server_name, port)
    
    if not singleton.acquire_singleton_lock():
        print(f"\n❌ ERROR: Another {server_name} instance is already running on port {port}")
        print("   Possible solutions:")
        print("   1. Stop the existing server instance")
        print("   2. Wait for the existing server to finish")
        print("   3. Use a different port")
        print("   4. Kill existing server processes if they're stuck")
        print(f"   5. Force cleanup: python -c \"from server_singleton import ServerSingletonManager; ServerSingletonManager('{server_name}', {port}).force_cleanup_stale_locks()\"")
        print()
        sys.exit(1)
    
    return singleton


# CLI utility for managing server instances
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Server Singleton Management Utility")
    parser.add_argument("--cleanup", action="store_true", help="Force cleanup stale lock files")
    parser.add_argument("--check", action="store_true", help="Check if server is running")
    parser.add_argument("--port", type=int, default=1256, help="Server port (default: 1256)")
    parser.add_argument("--name", default="BackupServer", help="Server name (default: BackupServer)")
    
    args = parser.parse_args()
    
    singleton = ServerSingletonManager(args.name, args.port)
    
    if args.cleanup:
        singleton.force_cleanup_stale_locks()
        print("✅ Lock cleanup completed")
    elif args.check:
        if singleton._is_port_in_use():
            print(f"❌ Server appears to be running on port {args.port}")
            sys.exit(1)
        else:
            print(f"✅ No server running on port {args.port}")
            sys.exit(0)
    else:
        print("Use --cleanup or --check options")