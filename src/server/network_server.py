# network_server.py
# Network Server Infrastructure Module
# Extracted from monolithic server.py for better modularity

import socket
import threading
import signal
import struct
import logging
import time
from typing import Tuple, Optional, Callable, Any, Dict

from .config import (
    CLIENT_SOCKET_TIMEOUT, MAX_PAYLOAD_READ_LIMIT, MAX_CONCURRENT_CLIENTS,
    SERVER_VERSION
)
from .exceptions import ProtocolError
from .protocol import (
    REQ_REGISTER, REQ_RECONNECT, RESP_GENERIC_SERVER_ERROR, RESP_RECONNECT_FAIL
)

logger = logging.getLogger(__name__)

class NetworkServer:
    """
    Handles all network infrastructure concerns for the backup server.
    Manages socket operations, client connections, and server lifecycle.
    """
    
    def __init__(self, port: int, request_handler: Callable, client_resolver: Callable, 
                 shutdown_event: threading.Event):
        """
        Initialize the network server.
        
        Args:
            port: Port number to bind the server to
            request_handler: Function to handle client requests
            client_resolver: Function to resolve client objects
            shutdown_event: Event to signal server shutdown
        """
        self.port = port
        self.request_handler = request_handler
        self.client_resolver = client_resolver
        self.shutdown_event = shutdown_event
        
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.client_connection_semaphore = threading.Semaphore(MAX_CONCURRENT_CLIENTS)
        self.active_connections: Dict[bytes, socket.socket] = {}
        self.connections_lock = threading.Lock()
        self.host = '0.0.0.0' # Default host
        self.start_time = time.time() # Server start time
        self.last_error: Optional[str] = None # Last error encountered by the server
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum: int, frame: Optional[Any]):
            sig_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else f"Signal {signum}"
            logger.warning(f"{sig_name} received by network server. Initiating shutdown...")
            self.stop()
        
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    def disconnect_client(self, client_id: bytes) -> bool:
        """Forcefully disconnects a client by their ID."""
        with self.connections_lock:
            if client_id in self.active_connections:
                sock = self.active_connections.pop(client_id)
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                    logger.info(f"Forcefully disconnected client {client_id.hex()}")
                    return True
                except OSError as e:
                    logger.error(f"Error while disconnecting client {client_id.hex()}: {e}")
                    return False
        return False
    
    def start(self) -> bool:
        """
        Start the network server and begin accepting connections.
        
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            # Create and configure server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to address and port
            server_address = ('0.0.0.0', self.port)
            self.server_socket.bind(server_address)
            
            # Start listening for connections
            self.server_socket.listen(MAX_CONCURRENT_CLIENTS)
            self.running = True
            
            logger.info(f"Network server started successfully on {server_address[0]}:{self.port}")
            logger.info(f"Server is ready to accept up to {MAX_CONCURRENT_CLIENTS} concurrent client connections.")
            
            # Main server loop
            self._server_loop()
            
            return True
            
        except OSError as e:
            if e.errno == 98:  # Address already in use
                logger.critical(f"FATAL: Port {self.port} is already in use. Another server instance may be running.")
            elif e.errno == 13:  # Permission denied
                logger.critical(f"FATAL: Permission denied when trying to bind to port {self.port}. Try using a port > 1024 or run with elevated privileges.")
            else:
                logger.critical(f"FATAL: Socket error during server startup: {e}")
            
            self.stop()
            return False
            
        except Exception as e:
            logger.critical(f"Unexpected error during server startup: {e}", exc_info=True)
            self.stop()
            return False
    
    def _server_loop(self):
        """Main server loop that accepts and handles client connections."""
        logger.info("Network server entering main accept loop...")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Check if server socket is still valid before using it
                if not self.server_socket:
                    logger.error("Server socket is None, cannot continue server loop")
                    break
                
                # Set a short timeout for accept() to check shutdown status periodically
                self.server_socket.settimeout(1.0)
                
                try:
                    client_conn, client_address = self.server_socket.accept()
                except socket.timeout:
                    continue  # Check shutdown status and continue loop
                
                # Acquire semaphore slot for this client
                if not self.client_connection_semaphore.acquire(blocking=False):
                    logger.warning(f"Connection limit ({MAX_CONCURRENT_CLIENTS}) reached. Rejecting connection from {client_address}")
                    client_conn.close()
                    continue
                
                logger.info(f"New client connection accepted from {client_address[0]}:{client_address[1]}")
                
                # Start client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client_connection,
                    args=(client_conn, client_address, self.client_connection_semaphore),
                    daemon=True,
                    name=f"ClientHandler-{client_address[0]}:{client_address[1]}"
                )
                client_thread.start()
                
            except OSError as e:
                if self.running:  # Only log if we're still supposed to be running
                    logger.error(f"Socket error in server accept loop: {e}")
                    if e.errno == 9:  # Bad file descriptor - socket was closed
                        logger.info("Server socket was closed, exiting accept loop.")
                        break
                else:
                    break  # Normal shutdown
                    
            except Exception as e:
                logger.error(f"Unexpected error in server accept loop: {e}", exc_info=True)
                if self.running:
                    continue  # Try to keep running unless it's a shutdown
                else:
                    break
        
        logger.info("Network server exited main accept loop.")
    
    def stop(self):
        """Stop the network server gracefully."""
        if not self.running:
            return
            
        logger.info("Network server shutdown initiated...")
        self.running = False
        
        # Close server socket to stop accepting new connections
        if self.server_socket:
            try:
                self.server_socket.close()
                logger.info("Server socket closed successfully.")
            except Exception as e:
                logger.error(f"Error closing server socket: {e}")
        
        # Signal shutdown to all components
        self.shutdown_event.set()
        
        # Wait for active connections to finish (with timeout)
        max_wait_time = 30  # seconds
        wait_interval = 0.5  # seconds
        
        for _ in range(int(max_wait_time / wait_interval)):
            if self.client_connection_semaphore._value == MAX_CONCURRENT_CLIENTS:
                break  # All clients have disconnected
            threading.Event().wait(wait_interval)
        
        remaining_connections = MAX_CONCURRENT_CLIENTS - self.client_connection_semaphore._value
        if remaining_connections > 0:
            logger.warning(f"Shutdown completed with {remaining_connections} client connections still active.")
        else:
            logger.info("All client connections closed successfully.")
        
        logger.info("Network server shutdown completed.")

    def get_connection_stats(self) -> Dict[str, int]:
        """Returns current connection statistics."""
        with self.connections_lock:
            return {
                'active_connections': len(self.active_connections),
                'max_connections': MAX_CONCURRENT_CLIENTS,
                'available_slots': self.client_connection_semaphore._value,
                'uptime_seconds': int(time.time() - self.start_time)
            }
    
    def _read_exact(self, sock: socket.socket, num_bytes: int) -> bytes:
        """
        Reads exactly `num_bytes` from the socket.
        
        Args:
            sock: The socket to read from
            num_bytes: The number of bytes to read
            
        Returns:
            The bytes read from the socket
            
        Raises:
            ValueError: If `num_bytes` is negative
            ProtocolError: If `num_bytes` exceeds `MAX_PAYLOAD_READ_LIMIT`
            TimeoutError: If a socket timeout occurs during read
            ConnectionError: If the socket is closed or a socket error occurs
        """
        if num_bytes < 0:
            raise ValueError("Cannot read a negative number of bytes.")
        if num_bytes == 0:
            return b''  # Reading zero bytes returns empty bytes
        if num_bytes > MAX_PAYLOAD_READ_LIMIT:
            raise ProtocolError(f"Requested read of {num_bytes} bytes exceeds server's MAX_PAYLOAD_READ_LIMIT ({MAX_PAYLOAD_READ_LIMIT}).")
        
        data_chunks = []
        bytes_received_total = 0
        while bytes_received_total < num_bytes:
            try:
                # Calculate how many bytes are still needed, read up to 4096 at a time
                bytes_to_read_this_chunk = min(num_bytes - bytes_received_total, 4096)
                chunk = sock.recv(bytes_to_read_this_chunk)
            except socket.timeout as e:
                raise TimeoutError(f"Socket timeout occurred while attempting to read {num_bytes} bytes (already received {bytes_received_total} bytes).") from e
            except socket.error as e:
                raise ConnectionError(f"Socket error encountered during read operation: {e}") from e
            
            if not chunk:  # Empty chunk indicates socket was closed by peer
                raise ConnectionError(f"Socket connection was broken by peer while attempting to read {num_bytes} bytes (already received {bytes_received_total} bytes).")
            
            data_chunks.append(chunk)
            bytes_received_total += len(chunk)
        
        return b''.join(data_chunks)
    
    def _parse_request_header(self, header_data: bytes) -> Tuple[bytes, int, int, int]:
        """
        Parses the 23-byte request header.
        
        Args:
            header_data: The raw bytes of the header
            
        Returns:
            A tuple: (client_id_bytes, version, code, payload_size)
            
        Raises:
            ProtocolError: If the header length is incorrect
        """
        expected_header_len = 16 + 1 + 2 + 4  # client_id + version + code + payload_size
        if len(header_data) != expected_header_len:
            raise ProtocolError(f"Invalid request header length. Expected {expected_header_len} bytes, but received {len(header_data)} bytes.")
        
        client_id = header_data[:16]  # First 16 bytes are Client ID
        version = int(header_data[16])  # Next byte is Version
        code = struct.unpack("<H", header_data[17:19])[0]  # Bytes 17-18 for Code (little-endian)
        payload_size = struct.unpack("<I", header_data[19:23])[0]  # Bytes 19-22 for Payload Size (little-endian)
        
        return client_id, version, code, payload_size
    
    def _send_response(self, sock: socket.socket, code: int, payload: bytes = b''):
        """
        Constructs and sends a response to the client socket.
        
        Args:
            sock: The client socket to send the response to
            code: The response code
            payload: The response payload (bytes)
            
        Raises:
            TimeoutError: If a socket timeout occurs during send
            ConnectionError: If a socket error occurs during send
        """
        # ResponseHeader: version (1 byte) + code (2 bytes) + payload_size (4 bytes)
        header_bytes = struct.pack("<BHI", SERVER_VERSION, code, len(payload))
        full_response_bytes = header_bytes + payload
        
        try:
            sock.sendall(full_response_bytes)
            logger.debug(f"Successfully sent response: Code={code}, TotalSizeSent={len(full_response_bytes)} (Header:{len(header_bytes)}, Payload:{len(payload)})")
        except socket.timeout:
            logger.error(f"Socket timeout occurred while attempting to send response (Code: {code}). Client may not have received it.")
            raise
        except socket.error as e:
            logger.error(f"A socket error occurred during send operation (Code: {code}): {e}")
            raise ConnectionError(f"Failed to send response due to socket error: {e}") from e
    
    def _handle_client_connection(self, client_conn: socket.socket, client_address: Tuple[str, int], 
                                 conn_semaphore: threading.Semaphore):
        """
        Handles an individual client connection in a dedicated thread.
        
        Args:
            client_conn: The socket object for the connected client
            client_address: A tuple (ip_string, port_integer) for the client
            conn_semaphore: The semaphore used to limit concurrent connections
        """
        client_ip, client_port = client_address
        active_client_obj = None
        log_client_identifier = f"{client_ip}:{client_port}"
        
        try:
            client_conn.settimeout(CLIENT_SOCKET_TIMEOUT)
            
            # Send initial server version greeting to establish protocol compatibility
            # Client expects ResponseHeader: version(1) + code(2) + payload_size(4) = 7 bytes
            version_greeting = struct.pack("<BHI", SERVER_VERSION, 0, 0)  # version=3, code=0, payload_size=0
            client_conn.sendall(version_greeting)
            
            # Main loop for handling requests from this client
            while not self.shutdown_event.is_set():
                try:
                    # Read Request Header (23 bytes)
                    header_bytes = self._read_exact(client_conn, 16 + 1 + 2 + 4)
                    client_id_from_header, version_from_header, code_from_header, payload_size_from_header = self._parse_request_header(header_bytes)
                    
                    # Update log identifier with Client ID
                    current_log_id_str = client_id_from_header.hex() if any(client_id_from_header) else "REGISTRATION_ATTEMPT"
                    log_client_identifier = f"{client_ip}:{client_port} (ID:{current_log_id_str})"
                    
                    logger.info(f"Request received from {log_client_identifier}: Version={version_from_header}, Code={code_from_header}, PayloadSize={payload_size_from_header}")
                    
                    # Protocol Version Check (flexible compatibility)
                    from .protocol import validate_protocol_version
                    
                    if not validate_protocol_version(version_from_header):
                        logger.warning(f"Incompatible client protocol version {version_from_header} received from {log_client_identifier}. Closing connection.")
                        self._send_response(client_conn, RESP_GENERIC_SERVER_ERROR)
                        break
                    else:
                        logger.debug(f"Accepted client protocol version {version_from_header} from {log_client_identifier}")
                    
                    # Read Request Payload
                    payload_bytes = self._read_exact(client_conn, payload_size_from_header)
                    
                    # Resolve Client Object for non-registration requests
                    if code_from_header != REQ_REGISTER:
                        active_client_obj = self.client_resolver(client_id_from_header)
                        
                        if not active_client_obj:
                            logger.warning(f"Request (Code:{code_from_header}) received from an unknown or previously timed-out client ID: {current_log_id_str}. Denying request.")
                            if code_from_header == REQ_RECONNECT:
                                self._send_response(client_conn, RESP_RECONNECT_FAIL, client_id_from_header)
                            else:
                                self._send_response(client_conn, RESP_GENERIC_SERVER_ERROR)
                            break
                        
                        # Update client last seen and log identifier
                        active_client_obj.update_last_seen()
                        log_client_identifier = f"{client_ip}:{client_port} (Name:'{active_client_obj.name}', ID:{current_log_id_str})"
                        
                        # Add to active connections
                        with self.connections_lock:
                            self.active_connections[client_id_from_header] = client_conn
                    
                    # Process the Request
                    self.request_handler(
                        sock=client_conn,
                        client_id_from_header=client_id_from_header,
                        client=active_client_obj,
                        code=code_from_header,
                        payload=payload_bytes
                    )
                except (TimeoutError, ConnectionError) as e:
                    logger.warning(f"Connection issue with {log_client_identifier}: {e}. Closing connection.")
                    break
                except ProtocolError as e:
                    logger.error(f"Protocol error encountered with {log_client_identifier}: {e}. Sending generic error and closing connection.")
                    if client_conn.fileno() != -1:
                        try:
                            self._send_response(client_conn, RESP_GENERIC_SERVER_ERROR)
                        except Exception as send_error_exception:
                            logger.error(f"Failed to send error response to {log_client_identifier} after a protocol error occurred: {send_error_exception}")
                    break
                except Exception as e:
                    logger.critical(f"Unexpected critical error occurred while handling client {log_client_identifier}: {e}", exc_info=True)
                    if client_conn.fileno() != -1:
                        try:
                            self._send_response(client_conn, RESP_GENERIC_SERVER_ERROR)
                        except Exception as send_error_exception:
                            logger.error(f"Failed to send error response to {log_client_identifier} after an unexpected error: {send_error_exception}")
                    break
        except Exception as e:
            logger.critical(f"Unhandled exception in client handler for {log_client_identifier}: {e}", exc_info=True)
        finally:
            # Remove from active connections
            if active_client_obj:
                with self.connections_lock:
                    if active_client_obj.id in self.active_connections:
                        del self.active_connections[active_client_obj.id]

            if client_conn:
                client_conn.close()
            conn_semaphore.release()
            logger.info(f"Connection with {log_client_identifier} has been closed and semaphore released.")