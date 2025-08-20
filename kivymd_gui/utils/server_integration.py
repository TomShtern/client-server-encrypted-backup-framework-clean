"""
Server integration bridge module for KivyMD GUI

This module provides a bridge between the KivyMD GUI and the existing BackupServer
implementation, handling threading, real-time status updates, and server control.

Key Features:
- Thread-safe communication using queue.Queue
- Real-time server monitoring and status updates
- Server lifecycle management (start, stop, restart)
- Client connection monitoring
- Error handling with graceful fallbacks
- Support for both standalone and integrated server modes
"""

import os
import sys
import queue
import threading
import logging
import time
import subprocess
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, List, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import contextlib

# Add path for importing server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import server components with fallback handling
try:
    from python_server.server.server import BackupServer
    from python_server.server.config import DEFAULT_PORT
    from python_server.server.exceptions import ServerError
    from Shared.logging_utils import setup_dual_logging
except ImportError as e:
    # Fallback for development/testing
    logging.warning(f"Could not import server modules: {e}")
    DEFAULT_PORT = 1256
    BackupServer = None
    ServerError = Exception

# Import GUI data models
from ..models.data_models import ServerStats, ClientInfo, FileInfo


@dataclass
class ServerStatus:
    """Server status information"""
    running: bool = False
    port: int = DEFAULT_PORT
    host: str = "localhost"
    uptime_seconds: float = 0.0
    start_time: Optional[datetime] = None
    error_message: Optional[str] = None
    client_count: int = 0
    bytes_transferred: int = 0
    total_files: int = 0


class ServerStatusMonitor:
    """Thread-safe server status monitoring"""
    
    def __init__(self, update_callback: Callable[[ServerStatus], None]):
        self.update_callback = update_callback
        self.status = ServerStatus()
        self.lock = threading.RLock()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self):
        """Start the status monitoring thread"""
        with self.lock:
            if self.monitoring:
                return
                
            self.monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="ServerStatusMonitor"
            )
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the status monitoring thread"""
        with self.lock:
            self.monitoring = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                with self.lock:
                    # Update status information
                    if self.status.running and self.status.start_time:
                        self.status.uptime_seconds = (
                            datetime.now() - self.status.start_time
                        ).total_seconds()
                    
                    # Call update callback
                    if self.update_callback:
                        self.update_callback(self.status.copy() if hasattr(self.status, 'copy') else self.status)
                        
                time.sleep(1.0)  # Update every second
            except Exception as e:
                logging.error(f"Error in status monitoring: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def update_status(self, **kwargs):
        """Update server status attributes"""
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(self.status, key):
                    setattr(self.status, key, value)


class ServerControlManager:
    """Manages server lifecycle and control operations"""
    
    def __init__(self, status_monitor: ServerStatusMonitor):
        self.status_monitor = status_monitor
        self.server_instance: Optional[Any] = None
        self.server_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
        
    def start_server(self, port: int = DEFAULT_PORT, 
                    standalone: bool = True) -> Tuple[bool, str]:
        """
        Start the backup server
        
        Args:
            port: Port number to run server on
            standalone: If True, run server in separate process; if False, run in-process
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if self.status_monitor.status.running:
                return False, "Server is already running"
            
            if standalone:
                return self._start_standalone_server(port)
            else:
                return self._start_integrated_server(port)
                
        except Exception as e:
            error_msg = f"Failed to start server: {e}"
            self.logger.error(error_msg)
            self.status_monitor.update_status(
                running=False,
                error_message=error_msg
            )
            return False, error_msg
    
    def _start_standalone_server(self, port: int) -> Tuple[bool, str]:
        """Start server in separate process"""
        try:
            # Path to server script
            server_script = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 
                'python_server', 'server', 'server.py'
            )
            
            if not os.path.exists(server_script):
                return False, f"Server script not found: {server_script}"
            
            # Start server process
            env = os.environ.copy()
            env['CYBERBACKUP_PORT'] = str(port)
            env['CYBERBACKUP_DISABLE_GUI'] = '1'  # Disable built-in GUI
            
            process = subprocess.Popen(
                [sys.executable, server_script],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Give server time to start
            time.sleep(2.0)
            
            # Check if server is running
            if self._check_server_connection(port):
                self.status_monitor.update_status(
                    running=True,
                    port=port,
                    start_time=datetime.now(),
                    error_message=None
                )
                return True, f"Server started successfully on port {port}"
            else:
                return False, "Server failed to start or is not responding"
                
        except Exception as e:
            return False, f"Error starting standalone server: {e}"
    
    def _start_integrated_server(self, port: int) -> Tuple[bool, str]:
        """Start server in same process"""
        try:
            if BackupServer is None:
                return False, "BackupServer class not available"
            
            # Create server instance
            self.server_instance = BackupServer()
            self.server_instance.port = port
            
            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self._run_server_thread,
                daemon=True,
                name="BackupServerThread"
            )
            self.server_thread.start()
            
            # Give server time to start
            time.sleep(2.0)
            
            # Check if server is running
            if hasattr(self.server_instance, 'running') and self.server_instance.running:
                self.status_monitor.update_status(
                    running=True,
                    port=port,
                    start_time=datetime.now(),
                    error_message=None
                )
                return True, f"Integrated server started on port {port}"
            else:
                return False, "Server failed to start properly"
                
        except Exception as e:
            return False, f"Error starting integrated server: {e}"
    
    def _run_server_thread(self):
        """Run server in background thread"""
        try:
            if self.server_instance:
                self.server_instance.start()
        except Exception as e:
            self.logger.error(f"Server thread error: {e}")
            self.status_monitor.update_status(
                running=False,
                error_message=str(e)
            )
    
    def _check_server_connection(self, port: int, timeout: float = 5.0) -> bool:
        """Check if server is responding on given port"""
        try:
            with socket.create_connection(('localhost', port), timeout=timeout):
                return True
        except (socket.error, OSError):
            return False
    
    def stop_server(self) -> Tuple[bool, str]:
        """Stop the backup server"""
        try:
            if not self.status_monitor.status.running:
                return True, "Server is not running"
            
            if self.server_instance:
                # Integrated server
                if hasattr(self.server_instance, 'stop'):
                    self.server_instance.stop()
                
                if self.server_thread and self.server_thread.is_alive():
                    self.server_thread.join(timeout=10.0)
                
                self.server_instance = None
                self.server_thread = None
            else:
                # Standalone server - need to find and terminate process
                self._terminate_standalone_server()
            
            self.status_monitor.update_status(
                running=False,
                start_time=None,
                uptime_seconds=0.0,
                error_message=None
            )
            
            return True, "Server stopped successfully"
            
        except Exception as e:
            error_msg = f"Error stopping server: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _terminate_standalone_server(self):
        """Terminate standalone server process"""
        # This is a simplified implementation
        # In production, you might want to store the process PID and terminate it properly
        try:
            if os.name == 'nt':
                # Windows
                os.system(f'taskkill /f /im python.exe')
            else:
                # Unix-like
                os.system('pkill -f "python.*server.py"')
        except Exception as e:
            self.logger.warning(f"Could not terminate standalone server: {e}")
    
    def restart_server(self, port: int = DEFAULT_PORT, 
                      standalone: bool = True) -> Tuple[bool, str]:
        """Restart the backup server"""
        # Stop server
        stop_success, stop_msg = self.stop_server()
        if not stop_success:
            return False, f"Failed to stop server: {stop_msg}"
        
        # Wait a bit
        time.sleep(3.0)
        
        # Start server
        return self.start_server(port, standalone)
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get detailed server information"""
        status = self.status_monitor.status
        
        info = {
            'running': status.running,
            'port': status.port,
            'host': status.host,
            'uptime_seconds': status.uptime_seconds,
            'uptime_formatted': self._format_uptime(status.uptime_seconds),
            'start_time': status.start_time.isoformat() if status.start_time else None,
            'error_message': status.error_message,
            'server_type': 'integrated' if self.server_instance else 'standalone'
        }
        
        # Add server-specific info if available
        if self.server_instance:
            try:
                if hasattr(self.server_instance, 'clients'):
                    info['client_count'] = len(self.server_instance.clients)
                if hasattr(self.server_instance, 'network_server'):
                    info['network_status'] = 'active'
            except Exception as e:
                self.logger.debug(f"Could not get server details: {e}")
        
        return info
    
    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Format uptime seconds into human-readable string"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}h {minutes}m {secs}s"


class ServerDataCollector:
    """Collects data from server for GUI display"""
    
    def __init__(self, server_control: ServerControlManager):
        self.server_control = server_control
        self.logger = logging.getLogger(__name__)
    
    def get_client_list(self) -> List[ClientInfo]:
        """Get list of connected clients"""
        clients = []
        
        try:
            server = self.server_control.server_instance
            if server and hasattr(server, 'clients'):
                with server.clients_lock if hasattr(server, 'clients_lock') else contextlib.nullcontext():
                    for client_id, client in server.clients.items():
                        client_info = ClientInfo(
                            client_id=client_id.hex() if isinstance(client_id, bytes) else str(client_id),
                            username=getattr(client, 'name', 'Unknown'),
                            ip_address=getattr(client, 'ip_address', 'Unknown'),
                            last_seen=datetime.fromtimestamp(
                                getattr(client, 'last_seen', time.time())
                            ),
                            files_transferred=0,  # TODO: Get from database
                            status='connected' if getattr(client, 'connected', True) else 'disconnected'
                        )
                        clients.append(client_info)
        except Exception as e:
            self.logger.error(f"Error getting client list: {e}")
        
        return clients
    
    def get_file_list(self) -> List[FileInfo]:
        """Get list of transferred files"""
        files = []
        
        try:
            # TODO: Integrate with database manager to get file list
            # For now, return empty list
            pass
        except Exception as e:
            self.logger.error(f"Error getting file list: {e}")
        
        return files
    
    def get_server_stats(self) -> ServerStats:
        """Get comprehensive server statistics"""
        try:
            status = self.server_control.status_monitor.status
            client_count = len(self.get_client_list())
            
            return ServerStats(
                uptime=self.server_control._format_uptime(status.uptime_seconds),
                total_files=status.total_files,
                total_clients=status.client_count,
                active_connections=client_count,
                bytes_transferred=status.bytes_transferred,
                last_update=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error getting server stats: {e}")
            # Return default stats
            return ServerStats(
                uptime="00:00:00",
                total_files=0,
                total_clients=0,
                active_connections=0,
                bytes_transferred=0,
                last_update=datetime.now()
            )


class ServerIntegrationBridge:
    """
    Main bridge class for KivyMD GUI and BackupServer integration
    
    This class provides a unified interface for:
    - Server lifecycle management
    - Real-time status monitoring
    - Data collection and updates
    - Thread-safe communication
    - Error handling and recovery
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize queues for thread-safe communication
        self.status_queue: queue.Queue = queue.Queue()
        self.command_queue: queue.Queue = queue.Queue()
        self.response_queue: queue.Queue = queue.Queue()
        
        # Status update callback
        self._status_callbacks: List[Callable[[ServerStatus], None]] = []
        
        # Initialize components
        self.status_monitor = ServerStatusMonitor(self._handle_status_update)
        self.server_control = ServerControlManager(self.status_monitor)
        self.data_collector = ServerDataCollector(self.server_control)
        
        # Control flags
        self.running = False
        self.bridge_thread: Optional[threading.Thread] = None
        
    def start_bridge(self):
        """Start the integration bridge"""
        if self.running:
            return
        
        self.logger.info("Starting server integration bridge")
        self.running = True
        
        # Start status monitoring
        self.status_monitor.start_monitoring()
        
        # Start bridge processing thread
        self.bridge_thread = threading.Thread(
            target=self._bridge_loop,
            daemon=True,
            name="ServerBridgeThread"
        )
        self.bridge_thread.start()
        
    def stop_bridge(self):
        """Stop the integration bridge"""
        if not self.running:
            return
            
        self.logger.info("Stopping server integration bridge")
        self.running = False
        
        # Stop status monitoring
        self.status_monitor.stop_monitoring()
        
        # Wait for bridge thread to finish
        if self.bridge_thread and self.bridge_thread.is_alive():
            self.bridge_thread.join(timeout=5.0)
    
    def _bridge_loop(self):
        """Main bridge processing loop"""
        while self.running:
            try:
                # Process any pending commands
                try:
                    command = self.command_queue.get_nowait()
                    self._process_command(command)
                except queue.Empty:
                    pass
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                self.logger.error(f"Error in bridge loop: {e}")
                time.sleep(1.0)
    
    def _process_command(self, command: Dict[str, Any]):
        """Process a command from the command queue"""
        try:
            cmd_type = command.get('type')
            cmd_data = command.get('data', {})
            
            if cmd_type == 'start_server':
                result = self.server_control.start_server(
                    port=cmd_data.get('port', DEFAULT_PORT),
                    standalone=cmd_data.get('standalone', True)
                )
            elif cmd_type == 'stop_server':
                result = self.server_control.stop_server()
            elif cmd_type == 'restart_server':
                result = self.server_control.restart_server(
                    port=cmd_data.get('port', DEFAULT_PORT),
                    standalone=cmd_data.get('standalone', True)
                )
            else:
                result = (False, f"Unknown command: {cmd_type}")
            
            # Send response
            response = {
                'command': cmd_type,
                'success': result[0],
                'message': result[1],
                'data': cmd_data
            }
            self.response_queue.put(response)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            self.response_queue.put({
                'command': command.get('type', 'unknown'),
                'success': False,
                'message': str(e),
                'data': command.get('data', {})
            })
    
    def _handle_status_update(self, status: ServerStatus):
        """Handle status updates from monitor"""
        # Put status in queue for GUI consumption
        try:
            self.status_queue.put(status, block=False)
        except queue.Full:
            # If queue is full, remove old status and add new one
            try:
                self.status_queue.get_nowait()
                self.status_queue.put(status, block=False)
            except queue.Empty:
                pass
        
        # Call registered callbacks
        for callback in self._status_callbacks:
            try:
                callback(status)
            except Exception as e:
                self.logger.error(f"Error in status callback: {e}")
    
    # Public API methods
    
    def add_status_callback(self, callback: Callable[[ServerStatus], None]):
        """Add a callback for status updates"""
        if callback not in self._status_callbacks:
            self._status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable[[ServerStatus], None]):
        """Remove a status update callback"""
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)
    
    def start_server_async(self, port: int = DEFAULT_PORT, standalone: bool = True):
        """Asynchronously start the server"""
        command = {
            'type': 'start_server',
            'data': {'port': port, 'standalone': standalone}
        }
        self.command_queue.put(command)
    
    def stop_server_async(self):
        """Asynchronously stop the server"""
        command = {'type': 'stop_server', 'data': {}}
        self.command_queue.put(command)
    
    def restart_server_async(self, port: int = DEFAULT_PORT, standalone: bool = True):
        """Asynchronously restart the server"""
        command = {
            'type': 'restart_server',
            'data': {'port': port, 'standalone': standalone}
        }
        self.command_queue.put(command)
    
    def get_latest_status(self) -> Optional[ServerStatus]:
        """Get the most recent server status"""
        try:
            return self.status_queue.get_nowait()
        except queue.Empty:
            return self.status_monitor.status
    
    def get_command_response(self) -> Optional[Dict[str, Any]]:
        """Get the most recent command response"""
        try:
            return self.response_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive server information"""
        return self.server_control.get_server_info()
    
    def get_client_list(self) -> List[ClientInfo]:
        """Get list of connected clients"""
        return self.data_collector.get_client_list()
    
    def get_file_list(self) -> List[FileInfo]:
        """Get list of transferred files"""
        return self.data_collector.get_file_list()
    
    def get_server_stats(self) -> ServerStats:
        """Get server statistics"""
        return self.data_collector.get_server_stats()
    
    def is_server_running(self) -> bool:
        """Check if server is currently running"""
        return self.status_monitor.status.running
    
    def cleanup(self):
        """Cleanup method for application shutdown"""
        try:
            self.logger.info("Cleaning up ServerIntegrationBridge...")
            self.stop_bridge()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


@contextmanager
def server_bridge_context():
    """Context manager for server bridge lifecycle"""
    bridge = ServerIntegrationBridge()
    try:
        bridge.start_bridge()
        yield bridge
    finally:
        bridge.stop_bridge()


# Legacy compatibility - maintain the existing ServerBridge interface
class ServerBridge:
    """Legacy bridge interface for backward compatibility"""
    
    def __init__(self, host="localhost", port=1256):
        self.host = host
        self.port = port
        self._bridge = ServerIntegrationBridge()
        self._bridge.start_bridge()
        
    def connect(self) -> bool:
        """Legacy connect method"""
        return self._bridge.is_server_running()
    
    def disconnect(self):
        """Legacy disconnect method"""
        pass
    
    def get_server_status(self) -> dict:
        """Legacy server status method"""
        info = self._bridge.get_server_info()
        return {
            "running": info.get('running', False),
            "port": info.get('port', self.port),
            "host": self.host,
            "uptime": info.get('uptime_formatted', '00:00:00'),
            "connections": info.get('client_count', 0)
        }
    
    def get_statistics(self) -> ServerStats:
        """Legacy statistics method"""
        return self._bridge.get_server_stats()


# Module-level convenience functions
_bridge_instance: Optional[ServerIntegrationBridge] = None

def get_server_bridge() -> ServerIntegrationBridge:
    """Get or create the global server bridge instance"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = ServerIntegrationBridge()
        _bridge_instance.start_bridge()
    return _bridge_instance

def shutdown_server_bridge():
    """Shutdown the global server bridge instance"""
    global _bridge_instance
    if _bridge_instance:
        _bridge_instance.stop_bridge()
        _bridge_instance = None


if __name__ == "__main__":
    # Test the bridge
    import sys
    
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing ServerIntegrationBridge...")
    
    with server_bridge_context() as bridge:
        logger.info("Bridge started")
        
        # Test server start
        bridge.start_server_async(standalone=False)
        time.sleep(3)
        
        # Get status
        status = bridge.get_latest_status()
        if status:
            logger.info(f"Server running: {status.running}")
        
        # Get info
        info = bridge.get_server_info()
        logger.info(f"Server info: {info}")
        
        # Stop server
        bridge.stop_server_async()
        time.sleep(2)
        
        logger.info("Test completed")