

"""
Server Singleton Manager - Ensures only one Python server instance runs at a time.
If a new instance is started, it will terminate the old one and take its place.
"""

import atexit
import logging
import os
import signal
import socket
import time
from pathlib import Path

# Try to import psutil for advanced process checking
try:
    import psutil
    HAS_PSUTIL = True
    psutil_module = psutil
except ImportError:
    HAS_PSUTIL = False
    psutil_module = None

logger = logging.getLogger(__name__)

class ServerSingletonManager:
    """
    Manages a single server instance. If a new instance is launched,
    it terminates the existing one.
    """

    def __init__(self, server_name: str = "BackupServer", port: int = 1256):
        """
        Initialize the singleton manager.
        
        Args:
            server_name: A unique name for the server process (e.g., "BackupServer", "BackupServerGUI").
            port: The port the server will use. This helps in identifying the process.
        """
        self.server_name = server_name
        self.port = port
        # Use a temporary directory for lock files for better cross-platform compatibility
        self.lock_dir = Path(os.environ.get("TEMP", "/tmp"))
        self.pid_file = self.lock_dir / f"{server_name}_{port}.pid"
        self.is_locked = False

        # Register cleanup to run when the process exits
        atexit.register(self.cleanup)

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with the given PID is running."""
        if not HAS_PSUTIL:
            # Basic check for non-psutil environments
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            else:
                return True

        return psutil_module.pid_exists(pid) if psutil_module else False

    def _terminate_process(self, pid: int):
        """Terminates the process with the given PID."""
        if not self._is_process_running(pid):
            logger.info(f"Process with PID {pid} is not running. No action needed.")
            return

        logger.warning(f"Terminating existing server process with PID {pid}.")
        try:
            if HAS_PSUTIL and psutil_module is not None:
                p = psutil_module.Process(pid)
                # Try to terminate gracefully first, then kill
                p.terminate()
                try:
                    p.wait(timeout=3)
                except Exception as timeout_ex:  # Use generic Exception since psutil might not be available
                    if "TimeoutExpired" in str(type(timeout_ex)):
                        logger.warning(f"Process {pid} did not terminate gracefully. Killing it.")
                        p.kill()
                        p.wait(timeout=3)
                    else:
                        raise
            else:
                # Fallback for systems without psutil
                os.kill(pid, signal.SIGTERM)
                time.sleep(2) # Give it time to die

            logger.info(f"Process {pid} terminated.")
            # Wait a moment for OS to release resources (e.g., network port)
            time.sleep(1.5)

        except Exception as e:
            logger.error(f"Failed to terminate process {pid}: {e}", exc_info=True)
            # Force kill using system command as last resort
            try:
                import subprocess
                if os.name == 'nt':  # Windows
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)
                    logger.warning(f"Used taskkill to force terminate PID {pid}")
                    time.sleep(2)
                else:  # Unix-like
                    subprocess.run(['kill', '-9', str(pid)], capture_output=True)
                    logger.warning(f"Used kill -9 to force terminate PID {pid}")
                    time.sleep(2)
            except Exception as force_kill_error:
                logger.critical(f"CRITICAL: Even force kill failed for PID {pid}: {force_kill_error}")
                # This is critical, if we can't kill the old process, the new one shouldn't start.
                raise RuntimeError(f"Could not terminate existing process {pid} - system may be in inconsistent state.") from e

    def acquire_lock(self) -> bool:
        """
        Acquires the singleton lock. If an existing instance is found, it's terminated.
        
        Returns:
            True if the lock was acquired, False otherwise.
        """
        # 1. Check for an existing PID file and terminate the process if it's running
        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text().strip())
                self._terminate_process(pid)
            except (ValueError, OSError) as e:
                logger.warning(f"Could not read or process PID file {self.pid_file}: {e}. Assuming stale lock.")
            except RuntimeError as e:
                logger.critical(f"CRITICAL: {e}")
                return False # Failed to kill the old process
            finally:
                # Clean up the old PID file
                try:
                    self.pid_file.unlink()
                except OSError:
                    pass # May already be gone

        # 2. Check if the port is in use with retry logic for Windows TIME_WAIT
        max_retries = 12  # Up to 60 seconds total wait
        retry_delay = 1   # Start with 1 second delay

        for attempt in range(max_retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # Enable socket reuse for faster recovery
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(("127.0.0.1", self.port))
                # Port is available, break out of retry loop
                break
            except OSError as e:
                if attempt < max_retries - 1:  # Not the last attempt
                    logger.warning(f"Port {self.port} still in use (attempt {attempt + 1}/{max_retries}). "
                                 f"Waiting {retry_delay} seconds... Error: {e}")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 10)  # Exponential backoff, max 10 seconds
                else:  # Last attempt failed
                    logger.error(f"Port {self.port} is still in use after {max_retries} attempts. Error: {e}")
                    logger.error("This may be due to another application using the port, or Windows TIME_WAIT state.")
                    logger.error("Try waiting a few minutes or use a different port.")
                    return False

        # 3. We are clear to start. Create our own PID file.
        try:
            self.pid_file.write_text(str(os.getpid()))
            self.is_locked = True
            logger.info(f"Successfully acquired singleton lock for {self.server_name} (PID: {os.getpid()}).")
            return True
        except OSError as e:
            logger.error(f"Failed to create new PID file {self.pid_file}: {e}")
            return False

    def cleanup(self):
        """Cleans up the PID file upon process exit."""
        if self.is_locked:
            try:
                if self.pid_file.exists() and int(self.pid_file.read_text().strip()) == os.getpid():
                    self.pid_file.unlink()
                    logger.info(f"Cleaned up PID file {self.pid_file}.")
            except (OSError, ValueError) as e:
                logger.warning(f"Error during PID file cleanup: {e}")
        self.is_locked = False

def ensure_single_server_instance(server_name: str = "BackupServer", port: int = 1256) -> "ServerSingletonManager":
    """
    Ensures only one instance of the server is running.
    If another instance is found, it is terminated.
    
    Args:
        server_name: A unique name for the server process.
        port: The port the server will use.
        
    Returns:
        A ServerSingletonManager instance.
        
    Raises:
        SystemExit: If the lock cannot be acquired.
    """
    singleton = ServerSingletonManager(server_name, port)

    if not singleton.acquire_lock():
        print(f"\n[CRITICAL ERROR] Could not acquire singleton lock for {server_name} on port {port}.")
        print("   Another instance may be running and could not be terminated,")
        print("   or the port might be in use by another application.")
        print("   This is a FATAL error - process will terminate immediately.")
        logger.critical(f"FATAL: Singleton lock acquisition failed for {server_name}:{port}")
        os._exit(1)  # Force immediate exit, bypassing any exception handlers

    return singleton

# CLI utility for checking and cleaning up
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Server Singleton Management Utility")
    parser.add_argument("--cleanup", action="store_true", help="Force cleanup of a stale lock file")
    parser.add_argument("--port", type=int, default=1256, help="Server port (default: 1256)")
    parser.add_argument("--name", default="BackupServer", help="Server name (default: BackupServer)")

    args = parser.parse_args()

    if args.cleanup:
        pid_file = Path(os.environ.get("TEMP", "/tmp")) / f"{args.name}_{args.port}.pid"
        if pid_file.exists():
            try:
                pid_file.unlink()
                print(f"[OK] Stale lock file removed: {pid_file}")
            except OSError as e:
                print(f"[ERROR] Failed to remove lock file: {e}")
        else:
            print("[INFO] No lock file found to clean up.")
