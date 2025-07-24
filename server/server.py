import socket
import threading
import struct
import uuid
import os
import time
import logging
import re
import signal
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any, Tuple

# Import singleton manager
from server_singleton import ensure_single_server_instance

# Import crypto components through compatibility layer
from crypto_compat import AES, RSA, PKCS1_OAEP, pad, unpad, get_random_bytes

# Import custom exceptions
from exceptions import ServerError, ProtocolError, ClientError, FileError

# Import database module
from database import DatabaseManager

# Import request handler module
from request_handlers import RequestHandler

# Import network server module
from network_server import NetworkServer

# GUI Integration
from gui_integration import GUIManager

# --- Server Configuration Constants ---
SERVER_VERSION = 3
DEFAULT_PORT = 1256
PORT_CONFIG_FILE = "port.info"
DATABASE_NAME = "defensive.db"
FILE_STORAGE_DIR = "received_files" # Directory to store received files

# Behavior Configuration
CLIENT_SOCKET_TIMEOUT = 60.0  # Timeout for individual socket operations with a client
CLIENT_SESSION_TIMEOUT = 10 * 60  # Overall inactivity timeout for a client session (10 minutes)
PARTIAL_FILE_TIMEOUT = 15 * 60 # Timeout for incomplete multi-packet file transfers (15 minutes)
MAINTENANCE_INTERVAL = 60.0 # How often to run maintenance tasks (seconds)
MAX_PAYLOAD_READ_LIMIT = (16 * 1024 * 1024) + 1024  # Max size for a single payload read (16MB chunk + headers)
MAX_ORIGINAL_FILE_SIZE = 4 * 1024 * 1024 * 1024 # Max original file size (e.g., 4GB) - for sanity checking
MAX_CONCURRENT_CLIENTS = 50 # Max number of concurrent client connections

MAX_CLIENT_NAME_LENGTH = 100 # As per spec (implicit from me.info and general limits)
MAX_FILENAME_FIELD_SIZE = 255 # Size of the filename field in protocol
MAX_ACTUAL_FILENAME_LENGTH = 250 # Practical limit for actual filename within the field
RSA_PUBLIC_KEY_SIZE = 160 # Bytes, X.509 format (for 1024-bit RSA - per protocol specification)
AES_KEY_SIZE_BYTES = 32 # 256-bit AES

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for verbose output
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("server.log", mode='a'), # Append mode
        logging.StreamHandler(sys.stdout) # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# --- Protocol Codes ---
# Request codes from client
REQ_REGISTER = 1025
REQ_SEND_PUBLIC_KEY = 1026
REQ_RECONNECT = 1027
REQ_SEND_FILE = 1028
REQ_CRC_OK = 1029
REQ_CRC_INVALID_RETRY = 1030
REQ_CRC_FAILED_ABORT = 1031

# Response codes to client
RESP_REG_OK = 1600
RESP_REG_FAIL = 1601
RESP_PUBKEY_AES_SENT = 1602
RESP_FILE_CRC = 1603
RESP_ACK = 1604
RESP_RECONNECT_AES_SENT = 1605
RESP_RECONNECT_FAIL = 1606
RESP_GENERIC_SERVER_ERROR = 1607


# --- Client Representation ---
class Client:
    """
    Represents a connected client and stores its state.
    """
    def __init__(self, client_id: bytes, name: str, public_key_bytes: Optional[bytes] = None):
        """
        Initializes a Client object.

        Args:
            client_id: The unique UUID (bytes) of the client.
            name: The username of the client.
            public_key_bytes: The client's RSA public key in X.509 format (optional).
        """
        self.id: bytes = client_id
        self.name: str = name
        self.public_key_bytes: Optional[bytes] = public_key_bytes
        self.public_key_obj: Optional[RSA.RsaKey] = None # PyCryptodome RSA key object
        self.aes_key: Optional[bytes] = None # Current session AES key
        self.last_seen: float = time.monotonic() # Monotonic time for session timeout
        self.partial_files: Dict[str, Dict[str, Any]] = {} # For reassembling multi-packet files
        self.lock: threading.Lock = threading.Lock() # To protect concurrent access to client state

        if public_key_bytes:
            self._import_public_key()

    def _import_public_key(self):
        """Imports the RSA public key from bytes if available."""
        if self.public_key_bytes:
            try:
                self.public_key_obj = RSA.import_key(self.public_key_bytes)
                logger.debug(f"Client '{self.name}': Successfully imported public key.")
            except ValueError as e:
                logger.error(f"Client '{self.name}': Failed to import public key from stored bytes: {e}")
                self.public_key_obj = None # Ensure consistent state if import fails

    def update_last_seen(self):
        """Updates the last seen timestamp to the current monotonic time."""
        with self.lock:
            self.last_seen = time.monotonic()

    def set_public_key(self, public_key_bytes_data: bytes):
        """
        Sets and imports the client's RSA public key.

        Args:
            public_key_bytes_data: The public key in X.509 format.

        Raises:
            ProtocolError: If the key size is incorrect or the key format is invalid.
        """
        with self.lock:
            if len(public_key_bytes_data) != RSA_PUBLIC_KEY_SIZE:
                raise ProtocolError(f"Public key size is incorrect for client '{self.name}'. Expected {RSA_PUBLIC_KEY_SIZE}, got {len(public_key_bytes_data)}.")
            self.public_key_bytes = public_key_bytes_data
            self._import_public_key() # Attempt to parse and store the RsaKey object
            if not self.public_key_obj: # Check if import failed
                 raise ProtocolError(f"Invalid RSA public key format provided by client '{self.name}' (failed to import).")

    def get_aes_key(self) -> Optional[bytes]:
        """Returns the current session AES key."""
        # This might be accessed by the client's handler thread only after being set.
        # If other threads could modify/read it, a lock would be good practice.
        # For now, assuming primary access is serialized by client handler.
        return self.aes_key

    def set_aes_key(self, aes_key_data: bytes):
        """
        Sets the client's session AES key.

        Args:
            aes_key_data: The AES key (bytes).

        Raises:
            ValueError: If the AES key size is incorrect.
        """
        with self.lock: # Protect AES key modification
            if len(aes_key_data) != AES_KEY_SIZE_BYTES:
                 raise ValueError(f"AES key size for client '{self.name}' is incorrect. Expected {AES_KEY_SIZE_BYTES}, got {len(aes_key_data)}.")
            self.aes_key = aes_key_data
    
    def clear_partial_file(self, filename: str):
        """Removes partial file reassembly data for a given filename."""
        with self.lock:
            if filename in self.partial_files:
                del self.partial_files[filename]
                logger.debug(f"Client '{self.name}': Cleared partial file reassembly data for '{filename}'.")

    def cleanup_stale_partial_files(self) -> int:
        """
        Removes partial file data for transfers that haven't seen activity recently.

        Returns:
            The number of stale partial file transfers cleaned up for this client.
        """
        with self.lock:
            current_monotonic_time = time.monotonic()
            stale_files_to_remove = [
                filename for filename, data in self.partial_files.items()
                if current_monotonic_time - data.get("timestamp", 0) > PARTIAL_FILE_TIMEOUT
            ]
            
            # Remove stale entries
            for filename in stale_files_to_remove:
                logger.warning(f"Client '{self.name}': Stale partial file transfer timed out for '{filename}'. Removing associated data.")
                del self.partial_files[filename]
            
            return len(stale_files_to_remove)


# --- Main Server Class ---
class BackupServer:
    """
    The main server class that handles client connections, protocol messages,
    encryption, file storage, and database interactions.
    """
    _CRC32_TABLE = ( # Standard POSIX cksum CRC32 table, used by _calculate_crc
        0x00000000, 0x04c11db7, 0x09823b6e, 0x0d4326d9, 0x130476dc, 0x17c56b6b, 0x1a864db2, 0x1e475050,
        0x2608edb8, 0x22c9f00f, 0x2f8ad6d6, 0x2b4bcb61, 0x350c9b64, 0x31cd86d3, 0x3c8ea00a, 0x384fbdbd,
        0x4c11db70, 0x48d0c6c7, 0x4593e01e, 0x4152fda9, 0x5f15adac, 0x5bd4b01b, 0x569796c2, 0x52568b75,
        0x6a1936c8, 0x6ed82b7f, 0x639b0da6, 0x675a1011, 0x791d4014, 0x7ddc5da3, 0x709f7b7a, 0x745e66cd,
        0x9823b6e0, 0x9ce2ab57, 0x91a18d8e, 0x95609039, 0x8b27c03c, 0x8fe6dd8b, 0x82a5fb52, 0x8664e6e5,
        0xbe2b5b58, 0xbaea46ef, 0xb7a96036, 0xb3687d81, 0xad2f2d84, 0xa9ee3033, 0xa4ad16ea, 0xa06c0b5d,
        0xd4326d90, 0xd0f37027, 0xddb056fe, 0xd9714b49, 0xc7361b4c, 0xc3f706fb, 0xceb42022, 0xca753d95,
        0xf23a8028, 0xf6fb9d9f, 0xfbb8bb46, 0xff79a6f1, 0xe13ef6f4, 0xe5ffeb43, 0xe8bccd9a, 0xec7dd02d,
        0x34867077, 0x30476dc0, 0x3d044b19, 0x39c556ae, 0x278206ab, 0x23431b1c, 0x2e003dc5, 0x2ac12072,
        0x128e9dcf, 0x164f8078, 0x1b0ca6a1, 0x1fcdbb16, 0x018aeb13, 0x054bf6a4, 0x0808d07d, 0x0cc9cdca,
        0x7897ab07, 0x7c56b6b0, 0x71159069, 0x75d48dde, 0x6b93dddb, 0x6f52c06c, 0x6211e6b5, 0x66d0fb02,
        0x5e9f46bf, 0x5a5e5b08, 0x571d7dd1, 0x53dc6066, 0x4d9b3063, 0x495a2dd4, 0x44190b0d, 0x40d816ba,
        0xaca5c697, 0xa864db20, 0xa527fdf9, 0xa1e6e04e, 0xbfa1b04b, 0xbb60adfc, 0xb6238b25, 0xb2e29692,
        0x8aad2b2f, 0x8e6c3698, 0x832f1041, 0x87ee0df6, 0x99a95df3, 0x9d684044, 0x902b669d, 0x94ea7b2a,
        0xe0b41de7, 0xe4750050, 0xe9362689, 0xedf73b3e, 0xf3b06b3b, 0xf771768c, 0xfa325055, 0xfef34de2,
        0xc6bcf05f, 0xc27dede8, 0xcf3ecb31, 0xcbffd686, 0xd5b88683, 0xd1799b34, 0xdc3abded, 0xd8fba05a,
        0x690ce0ee, 0x6dcdfd59, 0x608edb80, 0x644fc637, 0x7a089632, 0x7ec98b85, 0x738aad5c, 0x774bb0eb,
        0x4f040d56, 0x4bc510e1, 0x46863638, 0x42472b8f, 0x5c007b8a, 0x58c1663d, 0x558240e4, 0x51435d53,
        0x251d3b9e, 0x21dc2629, 0x2c9f00f0, 0x285e1d47, 0x36194d42, 0x32d850f5, 0x3f9b762c, 0x3b5a6b9b,
        0x0315d626, 0x07d4cb91, 0x0a97ed48, 0x0e56f0ff, 0x1011a0fa, 0x14d0bd4d, 0x19939b94, 0x1d528623,
        0xf12f560e, 0xf5ee4bb9, 0xf8ad6d60, 0xfc6c70d7, 0xe22b20d2, 0xe6ea3d65, 0xeba91bbc, 0xef68060b,
        0xd727bbb6, 0xd3e6a601, 0xdea580d8, 0xda649d6f, 0xc423cd6a, 0xc0e2d0dd, 0xcda1f604, 0xc960ebb3,
        0xbd3e8d7e, 0xb9ff90c9, 0xb4bcb610, 0xb07daba7, 0xae3afba2, 0xaafbe615, 0xa7b8c0cc, 0xa379dd7b,
        0x9b3660c6, 0x9ff77d71, 0x92b45ba8, 0x9675461f, 0x8832161a, 0x8cf30bad, 0x81b02d74, 0x857130c3,
        0x5d8a9099, 0x594b8d2e, 0x5408abf7, 0x50c9b640, 0x4e8ee645, 0x4a4ffbf2, 0x470cdd2b, 0x43cdc09c,
        0x7b827d21, 0x7f436096, 0x7200464f, 0x76c15bf8, 0x68860bfd, 0x6c47164a, 0x61043093, 0x65c52d24,
        0x119b4be9, 0x155a565e, 0x18197087, 0x1cd86d30, 0x029f3d35, 0x065e2082, 0x0b1d065b, 0x0fdc1bec,
        0x3793a651, 0x3352bbe6, 0x3e119d3f, 0x3ad08088, 0x2497d08d, 0x2056cd3a, 0x2d15ebe3, 0x29d4f654,
        0xc5a92679, 0xc1683bce, 0xcc2b1d17, 0xc8ea00a0, 0xd6ad50a5, 0xd26c4d12, 0xdf2f6bcb, 0xdbee767c,
        0xe3a1cbc1, 0xe760d676, 0xea23f0af, 0xeee2ed18, 0xf0a5bd1d, 0xf464a0aa, 0xf9278673, 0xfde69bc4,
        0x89b8fd09, 0x8d79e0be, 0x803ac667, 0x84fbdbd0, 0x9abc8bd5, 0x9e7d9662, 0x933eb0bb, 0x97ffad0c,
        0xafb010b1, 0xab710d06, 0xa6322bdf, 0xa2f33668, 0xbcb4666d, 0xb8757bda, 0xb5365d03, 0xb1f740b4
    )

    def __init__(self):
        """Initializes the BackupServer instance."""
        self.clients: Dict[bytes, Client] = {} # In-memory store: client_id_bytes -> Client object
        self.clients_by_name: Dict[str, bytes] = {} # In-memory store: client_name_str -> client_id_bytes
        self.clients_lock: threading.Lock = threading.Lock() # Protects access to clients and clients_by_name
        
        # Use default port for now
        self.port = DEFAULT_PORT
        self.running = False
        self.shutdown_event = threading.Event()

        # Initialize request handler first, as it's needed by NetworkServer
        self.request_handler: RequestHandler = RequestHandler(self)

        # Initialize network server with proper parameters
        self.network_server: NetworkServer = NetworkServer(
            port=self.port,
            request_handler=self.request_handler.process_request,
            client_resolver=self.resolve_client,
            shutdown_event=self.shutdown_event
        )
        
        # Initialize database manager
        self.db_manager: DatabaseManager = DatabaseManager()
        
        # Initialize GUI manager
        self.gui_manager = GUIManager(self)
        self.gui_manager.initialize_gui()
        
        # Perform pre-flight checks and initialize database
        self.db_manager.check_startup_permissions() # Perform pre-flight checks before extensive setup
        self.db_manager.ensure_storage_dir() # Ensure 'received_files' directory exists
        self.db_manager.init_database()      # Initialize SQLite database and tables
        
        # Note: Signal handlers are now managed by NetworkServer
        # but we keep a reference for main server coordination
        # Port is already set during NetworkServer initialization

    def create_client(self, client_id: bytes, name: str) -> 'Client':
        """Factory method to create a new Client instance."""
        return Client(client_id, name)

    def resolve_client(self, client_id: bytes) -> Optional[Client]:
        """Resolves a client object from the in-memory store by client ID."""
        with self.clients_lock:
            return self.clients.get(client_id)

    def _send_response(self, sock: socket.socket, code: int, payload: bytes = b''):
        """Delegates sending a response to the network server."""
        self.network_server._send_response(sock, code, payload)

    def _update_gui_client_count(self):
        """Delegates updating the client count on the GUI."""
        # This is a placeholder implementation.
        # You might need to pass more specific data to the GUI manager.
        with self.clients_lock:
            total_clients = len(self.clients)
        self.gui_manager.update_client_stats(total=total_clients)

    def _update_gui_success(self, message: str):
        """Delegates logging a success message to the GUI."""
        self.gui_manager.queue_update("log", message)

    def _parse_string_from_payload(self, payload_bytes: bytes, field_len: int, max_actual_len: int, field_name: str = "String") -> str:
        """
        Parses a null-terminated, zero-padded string from a fixed-length field within a payload.
        """
        if len(payload_bytes) < field_len:
            raise ProtocolError(f"{field_name}: Field is shorter than expected ({len(payload_bytes)} < {field_len})")
        
        string_field = payload_bytes[:field_len]
        null_pos = string_field.find(b'\x00')
        
        if null_pos == -1:
            actual_string_bytes = string_field
        else:
            actual_string_bytes = string_field[:null_pos]
        
        if len(actual_string_bytes) > max_actual_len:
            raise ProtocolError(f"{field_name}: String too long ({len(actual_string_bytes)} > {max_actual_len})")
        
        try:
            return actual_string_bytes.decode('utf-8', errors='strict')
        except UnicodeDecodeError as e:
            raise ProtocolError(f"{field_name}: Invalid UTF-8 encoding: {e}")

    def _load_clients_from_db(self):
        """Loads existing client data from the database into memory at server startup."""
        logger.info("Loading existing clients from database into memory...")
        try:
            rows = self.db_manager.load_clients_from_db()
        except ServerError as e: # Raised by db_manager on critical read failure
            logger.critical(f"CRITICAL FAILURE: Could not load client data from database: {e}. Server cannot continue.")
            # This is a fatal error for server operation.
            raise SystemExit(f"Startup aborted: Failed to load critical client data from database. Details: {e}") from e

        with self.clients_lock: # Ensure thread-safe access to shared client dictionaries
            self.clients.clear()
            self.clients_by_name.clear()
            loaded_count = 0
            if rows: # Check if any rows were returned
                for row_id, name, pk_bytes, last_seen_iso_utc in rows:
                    try:
                        client = Client(row_id, name, pk_bytes) # Create Client object
                        # last_seen_iso_utc is from DB. Internal client.last_seen is monotonic for session timeout.
                        # We don't directly use DB's LastSeen for session timeout upon loading,
                        # but it's good for audit/record. Session starts fresh.
                        self.clients[row_id] = client
                        self.clients_by_name[name] = row_id
                        loaded_count +=1
                    except Exception as e_obj: # Catch errors creating individual Client objects (e.g. bad PK)
                        logger.error(f"Error creating Client object for '{name}' (ID: {row_id.hex() if row_id else 'N/A'}) from DB row: {e_obj}")
            logger.info(f"Successfully loaded {loaded_count} client(s) from database.")


    def _save_client_to_db(self, client: Client):
        """Saves or updates a client's information in the database."""
        self.db_manager.save_client_to_db(client.id, client.name, client.public_key_bytes, client.get_aes_key())


    def _save_file_info_to_db(self, client_id: bytes, file_name: str, path_name: str, verified: bool, file_size: int, mod_date: str, crc: Optional[int] = None):
        """Saves or updates file information in the database."""
        self.db_manager.save_file_info_to_db(client_id, file_name, path_name, verified, file_size, mod_date, crc)


    # Port configuration is now handled by NetworkServer


    def _periodic_maintenance_job(self):
        """
        Runs periodically to perform maintenance and send status updates to the GUI.
        """
        try:
            # --- Maintenance Tasks ---
            # (Existing cleanup logic remains the same)
            inactive_clients_removed_count = 0
            with self.clients_lock:
                current_monotonic_time = time.monotonic()
                inactive_client_ids_to_remove = [
                    cid for cid, client_obj in self.clients.items()
                    if (current_monotonic_time - client_obj.last_seen) > CLIENT_SESSION_TIMEOUT
                ]
                for cid in inactive_client_ids_to_remove:
                    client_obj = self.clients.pop(cid, None)
                    if client_obj:
                        self.clients_by_name.pop(client_obj.name, None)
                        inactive_clients_removed_count += 1
                        logger.info(f"Client '{client_obj.name}' session timed out.")

            with self.clients_lock:
                active_clients_list = list(self.clients.values())
            stale_partial_files_cleaned_count = sum(
                client_obj.cleanup_stale_partial_files() for client_obj in active_clients_list
            )

            # --- GUI Status Update ---
            if self.gui_manager.is_gui_ready():
                # 1. Gather all status information into dictionaries
                status_data = {
                    'running': self.running,
                    'address': self.network_server.host,
                    'port': self.port,
                    'uptime': time.time() - self.network_server.start_time if self.running else 0,
                    'error_message': self.network_server.last_error or ''
                }

                client_stats_data = {
                    'connected': self.network_server.get_connection_stats()['active_connections'],
                    'total': self.db_manager.get_total_clients_count(),
                    'active_transfers': 0 # Placeholder, needs real logic
                }

                maintenance_stats_data = {
                    'files_cleaned': 0, # Placeholder
                    'partial_files_cleaned': stale_partial_files_cleaned_count,
                    'clients_cleaned': inactive_clients_removed_count,
                    'last_cleanup': datetime.now().isoformat()
                }
                
                # 2. Put the gathered data into the GUI's queue
                self.gui_manager.queue_update("status", status_data)
                self.gui_manager.queue_update("client_stats", client_stats_data)
                self.gui_manager.queue_update("maintenance_stats", maintenance_stats_data)

        except Exception as e:
            logger.critical(f"Critical error in periodic maintenance job: {e}", exc_info=True)
            if self.gui_manager.is_gui_ready():
                self.gui_manager.queue_update("log", f"ERROR: Maintenance job failed: {e}")


    def start(self):
        """Starts the server: loads data, and begins listening for connections."""
        if self.running:
            logger.warning("Server is already running. Start command ignored.")
            return

        self.running = True
        self.shutdown_event.clear()
        
        try:
            self._load_clients_from_db()
        except SystemExit as e:
            logger.critical(f"Server startup aborted due to critical error during data loading: {e}")
            self.running = False
            self.shutdown_event.set()
            return

        # Start the network server
        self.network_server.start()

        logger.info(f"Encrypted Backup Server Version {SERVER_VERSION} started successfully on port {self.port}.")
        
        # Update GUI with server status
        self.gui_manager.update_server_status(True, "0.0.0.0", self.port)
        self.gui_manager.update_client_stats()


    def stop(self):
        """Initiates a graceful shutdown of the server."""
        if not self.running:
            logger.info("Server is not running.")
            return

        logger.warning("Server shutdown sequence initiated...")
        self.gui_manager.shutdown()
        self.network_server.stop()
        self.running = False
        logger.info("Server has been stopped.")


# --- Main Execution Guard ---
if __name__ == "__main__":
    # Display a startup banner for the server console
    print("=====================================================================")
    print(f"      Secure Encrypted File Backup Server - Version {SERVER_VERSION}      ")
    print(f"      Process ID: {os.getpid()}                                     ")
    print("=====================================================================")
    
    # Perform basic pre-flight checks before attempting to start the server
    if sys.version_info < (3, 7): # PyCryptodome generally works better with Python 3.7+
        print("Warning: Python 3.7 or newer is recommended for optimal server performance and security library compatibility.", file=sys.stderr)

    try:
        # Quick check to ensure PyCryptodome is available and basic operations work
        _ = RSA.generate(1024, randfunc=get_random_bytes) # Test RSA key generation
        _ = AES.new(get_random_bytes(AES_KEY_SIZE_BYTES), AES.MODE_CBC, iv=get_random_bytes(16)) # Test AES cipher creation
        logger.info("PyCryptodome library check passed: Basic crypto operations are available.")
    except Exception as e_crypto_check:
        print(f"CRITICAL FAILURE: PyCryptodome library is not installed correctly or is non-functional: {e_crypto_check}", file=sys.stderr)
        print("Please ensure PyCryptodome is properly installed (e.g., via 'pip install pycryptodomex'). Server cannot start.", file=sys.stderr)
        sys.exit(1) # Exit if essential crypto library is missing/broken

    # Instantiate the server
    server_instance = None
    try:
        # Instantiate the server
        server_instance = BackupServer()

        # The GUIManager was initialized in the BackupServer constructor.
        # The GUI is running in a separate thread, started by the GUIManager.
        # The main thread can now wait for a shutdown signal or simply keep alive.
        # The GUI's mainloop will handle user interaction and application lifetime.
        
        # We wait for the GUI to signal it's ready before we proceed.
        if server_instance.gui_manager.is_gui_ready():
            logger.info("GUI is ready. Main thread is now idle, application is driven by GUI and server threads.")
            # Keep the main thread alive. The application will exit when the GUI is closed.
            while server_instance.gui_manager.is_gui_running():
                time.sleep(1)
        else:
            # Fallback for console-only mode if GUI fails
            logger.warning("GUI did not become ready. Running in console-only mode.")
            logger.info("Starting server in console mode...")
            server_instance.start()
            while server_instance.running and not server_instance.shutdown_event.is_set():
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt detected in main execution block. Initiating shutdown.")
    except SystemExit as e_sys_exit:
        logger.critical(f"Server startup process was aborted: {e_sys_exit}")
    except Exception as e_main_fatal:
        logger.critical(f"Server encountered a fatal unhandled exception in main execution: {e_main_fatal}", exc_info=True)
    finally:
        if server_instance:
            logger.info("Ensuring server shutdown is called from __main__ 'finally' block...")
            server_instance.stop()
        
        logger.info("Server application has completed its full termination sequence.")
        print("Server shutdown process complete. Exiting.")