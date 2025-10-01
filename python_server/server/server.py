# GLOBAL UTF-8 AUTO-PATCHER: Automatically enables UTF-8 for ALL subprocess calls
import contextlib
import logging
import os
import socket
import sys
import threading
import time
from datetime import datetime
from typing import Any

# Enable global UTF-8 support automatically (replaces all manual UTF-8 setup)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Setup standardized import paths BEFORE importing any other Shared modules
from Shared.path_utils import setup_imports

setup_imports()

# Now import ALL Shared modules after path setup - consolidate all imports here
from Shared.logging_utils import create_enhanced_logger, create_log_monitor_info, setup_dual_logging
from Shared.observability import get_metrics_collector, get_system_monitor

# Try to import Sentry config - handle gracefully if not available
try:
    from Shared.sentry_config import init_sentry
    sentry_available = True
except ImportError:
    sentry_available = False
    def init_sentry(*args, **kwargs) -> bool:
        return False

# Import singleton manager
# Import crypto components directly from PyCryptodome
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from .config import *  # Configuration constants

# Import database module
from .database import DatabaseManager

# Import custom exceptions
from .exceptions import ProtocolError, ServerError

# GUI Integration
from .gui_integration import GUIManager

# Import network server module
from .network_server import NetworkServer

# Import protocol constants and configuration (refactored for modularity)
from .protocol import *  # Protocol constants and utilities

# Import request handler module
from .request_handlers import RequestHandler
from .server_singleton import ensure_single_server_instance

# Configuration constants now imported from config.py module
# Remaining server-specific constants:

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

# Enhanced Logging Configuration with dual output
# Initialize Sentry error tracking for backup server
if sentry_available:
    sentry_initialized = init_sentry("backup-server", traces_sample_rate=0.1)
else:
    sentry_initialized = False

# Set up enhanced dual logging with observability features
logger, backup_log_file = setup_dual_logging(
    logger_name=__name__,
    server_type="backup-server",
    console_level=logging.INFO,
    file_level=logging.DEBUG,
    console_format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
)

# Setup structured logging for backup server
structured_logger = create_enhanced_logger("backup-server", logger)
metrics_collector = get_metrics_collector()
system_monitor = get_system_monitor()

# Maintain compatibility: also log to the original server.log file
LOG_FORMAT = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
server_log_handler = logging.FileHandler("server.log", mode='a')
server_log_handler.setFormatter(logging.Formatter(LOG_FORMAT))
server_log_handler.setLevel(logging.DEBUG)
logger.addHandler(server_log_handler)

# Protocol constants now imported from protocol.py module


# --- Client Representation ---
class Client:
    """
    Represents a connected client and stores its state.
    """
    def __init__(self, client_id: bytes, name: str, public_key_bytes: bytes | None = None):
        """
        Initializes a Client object.

        Args:
            client_id: The unique UUID (bytes) of the client.
            name: The username of the client.
            public_key_bytes: The client's RSA public key in X.509 format (optional).
        """
        self.id: bytes = client_id
        self.name: str = name
        self.public_key_bytes: bytes | None = public_key_bytes
        self.public_key_obj: Any | None = None # PyCryptodome RSA key object or compatibility layer equivalent
        self.aes_key: bytes | None = None # Current session AES key
        self.last_seen: float = time.monotonic() # Monotonic time for session timeout
        self.last_seen_db: str | None = None # Database timestamp for audit purposes
        self.partial_files: dict[str, dict[str, Any]] = {} # For reassembling multi-packet files
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

    def get_aes_key(self) -> bytes | None:
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


    def clear_all_partial_files(self):
        """Clears all in-memory partial file transfer states for this client."""
        with self.lock:
            count = len(self.partial_files)
            self.partial_files.clear()
            logger.debug(f"Client '{self.name}': Cleared all partial file data ({count} entries)")

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
        0x00000000, 0x04c11db7, 0x09823b6e, 0x0d4326d9, 0x130476dc, 0x17c56b6b, 0x1a864db2, 0x1e475005,
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

    def _calculate_crc(self, data: bytes, crc: int = 0) -> int:
        for byte in data:
            crc = (crc << 8) ^ self._CRC32_TABLE[(crc >> 24) ^ byte]
        return crc

    def _finalize_crc(self, crc: int, total_size: int) -> int:
        length = total_size
        while length > 0:
            crc = (crc << 8) ^ self._CRC32_TABLE[(crc >> 24) ^ (length & 0xFF)]
            length >>= 8
        return ~crc & 0xFFFFFFFF

    def __init__(self):
        """Initializes the BackupServer instance."""
        self.clients: dict[bytes, Client] = {} # In-memory store: client_id_bytes -> Client object
        self.clients_by_name: dict[str, bytes] = {} # In-memory store: client_name_str -> client_id_bytes
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
        # Allow disabling integrated GUI when standalone GUI process will be launched
        disable_flag = os.environ.get("CYBERBACKUP_DISABLE_INTEGRATED_GUI")
        logger.info(f"[GUI] Embedded GUI disable flag value: {disable_flag!r}")
        if not disable_flag:
            logger.info("[GUI] Attempting embedded GUI initialization...")
            self.gui_manager.initialize_gui()
        else:
            logger.info("[GUI] Integrated Server GUI disabled via CYBERBACKUP_DISABLE_INTEGRATED_GUI=1 (no embedded GUI)")

        # Perform pre-flight checks and initialize database
        self.db_manager.check_startup_permissions() # Perform pre-flight checks before extensive setup
        self.db_manager.ensure_storage_dir() # Ensure 'received_files' directory exists
        self.db_manager.init_database()      # Initialize SQLite database and tables

        # Set backup_log_file instance attribute to enable enhanced log reading
        self.backup_log_file = backup_log_file

        # Note: Signal handlers are now managed by NetworkServer
        # but we keep a reference for main server coordination
        # Port is already set during NetworkServer initialization

    def create_client(self, client_id: bytes, name: str) -> 'Client':
        """Factory method to create a new Client instance."""
        return Client(client_id, name)

    def get_client_by_id(self, client_id: bytes) -> Client | None:
        """Resolves a client object from the in-memory store by client ID."""
        with self.clients_lock:
            return self.clients.get(client_id)

    def resolve_client(self, client_identifier: str) -> dict[str, Any]:
        """Resolve client by ID or name - compatible with ServerBridge signature."""
        try:
            # First try to resolve by client ID (hex string)
            if client_identifier in self.clients_by_name:
                # Found by name
                client_id_bytes = self.clients_by_name[client_identifier]
                if client := self.clients.get(client_id_bytes):
                    return self._format_response(True, {
                        'id': client.id.hex(),
                        'name': client.name,
                        'public_key_size': len(client.public_key_bytes) if client.public_key_bytes else 0
                    })

            # Try to resolve by hex ID
            with contextlib.suppress(ValueError):
                client_id_bytes = bytes.fromhex(client_identifier)
                if client := self.clients.get(client_id_bytes):
                    return self._format_response(True, {
                        'id': client.id.hex(),
                        'name': client.name,
                        'public_key_size': len(client.public_key_bytes) if client.public_key_bytes else 0
                    })
            return self._format_response(False, error=f"Client '{client_identifier}' not found")
        except Exception as e:
            logger.error(f"Failed to resolve client {client_identifier}: {e}")
            return self._format_response(False, error=str(e))

    def send_response(self, sock: socket.socket, code: int, payload: bytes = b''):
        """Delegates sending a response to the network server."""
        self.network_server.send_response(sock, code, payload)

    def _update_gui_client_count(self) -> None:
        """Delegates updating the client count on the GUI."""
        with self.clients_lock:
            connected_clients = len(self.clients)
            # Get total clients from database if available
            total_clients = connected_clients
            if hasattr(self, 'db_manager') and self.db_manager:
                with contextlib.suppress(Exception):
                    total_from_db = len(self.db_manager.get_all_clients())
                    total_clients = max(total_from_db, connected_clients)

        self.gui_manager.update_client_stats({
            'connected': connected_clients,
            'total': total_clients,
            'active_transfers': 0
        })

    def _update_gui_success(self, message: str):
        """Delegates logging a success message to the GUI."""
        self.gui_manager.queue_update("log", message)

    def _update_gui_transfer_stats(self, bytes_transferred: int = 0, last_activity: str = "") -> None:
        """Delegates updating transfer statistics to the GUI."""
        self.gui_manager.update_transfer_stats(bytes_transferred, last_activity)

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
            raise ProtocolError(f"{field_name}: Invalid UTF-8 encoding: {e}") from e

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
                        # Store DB timestamp for audit/logging while using fresh monotonic time for session
                        client.last_seen_db = last_seen_iso_utc  # Database timestamp for audit
                        self.clients[row_id] = client
                        self.clients_by_name[name] = row_id
                        loaded_count +=1
                    except Exception as e_obj: # Catch errors creating individual Client objects (e.g. bad PK)
                        logger.error(f"Error creating Client object for '{name}' (ID: {row_id.hex() if row_id else 'N/A'}) from DB row: {e_obj}")
            logger.info(f"Successfully loaded {loaded_count} client(s) from database.")


    def _save_client_to_db(self, client: Client):
        """Saves or updates a client's information in the database."""
        self.db_manager.save_client_to_db(client.id, client.name, client.public_key_bytes, client.get_aes_key())


    def _save_file_info_to_db(self, client_id: bytes, file_name: str, path_name: str, verified: bool, file_size: int, mod_date: str, crc: int | None = None):
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
                    if client_obj := self.clients.pop(cid, None):
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
                self._update_gui_with_status_data(inactive_clients_removed_count, stale_partial_files_cleaned_count)

        except Exception as e:
            logger.critical(f"Critical error in periodic maintenance job: {e}", exc_info=True)
            if self.gui_manager.is_gui_ready():
                self.gui_manager.queue_update("log", f"ERROR: Maintenance job failed: {e}")

    def _update_gui_with_status_data(self, inactive_clients_removed_count: int, stale_partial_files_cleaned_count: int):
        """Extract method to prepare and send status data to GUI."""
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
            'active_transfers': 0  # Placeholder, needs real logic
        }

        maintenance_stats_data = {
            'files_cleaned': 0,  # Placeholder
            'partial_files_cleaned': stale_partial_files_cleaned_count,
            'clients_cleaned': inactive_clients_removed_count,
            'last_cleanup': datetime.now().isoformat()
        }

        # 2. Put the gathered data into the GUI's queue
        self.gui_manager.queue_update("status", status_data)
        self.gui_manager.queue_update("client_stats", client_stats_data)
        self.gui_manager.queue_update("maintenance_stats", maintenance_stats_data)

    def _handle_startup_system_exit(self, e: SystemExit, start_time: float):
        """Extract method to handle SystemExit during startup."""
        duration_ms = (time.time() - start_time) * 1000
        structured_logger.error(f"Server startup aborted: {e}",
                              operation="server_start",
                              duration_ms=duration_ms,
                              error_code="SystemExit")
        logger.critical(f"Server startup aborted due to critical error during data loading: {e}")
        self.running = False
        self.shutdown_event.set()

    def start(self):
        """Starts the server: loads data, and begins listening for connections."""
        if self.running:
            logger.warning("Server is already running. Start command ignored.")
            return

        start_time = time.time()
        structured_logger.info("Starting backup server", operation="server_start")

        self.running = True
        self.shutdown_event.clear()

        try:
            # Start system monitoring
            if not system_monitor.running:
                system_monitor.start()
                structured_logger.info("System monitoring started")

            self._load_clients_from_db()

            # Record server start metrics
            metrics_collector.record_counter("server.starts.total")

        except SystemExit as e:
            self._handle_startup_system_exit(e, start_time)
            return

        # Start the network server in a separate thread
        import threading
        self.network_thread = threading.Thread(target=self.network_server.start, daemon=True)
        self.network_thread.start()

        duration_ms = (time.time() - start_time) * 1000
        structured_logger.info("Backup server started successfully",
                             operation="server_start",
                             duration_ms=duration_ms,
                             context={
                                 "version": SERVER_VERSION,
                                 "port": self.port,
                                 "clients_loaded": len(self.clients)
                             })

        logger.info(f"Encrypted Backup Server Version {SERVER_VERSION} started successfully on port {self.port}.")

        # Record successful start metrics
        metrics_collector.record_timer("server.startup.duration", duration_ms)
        metrics_collector.record_gauge("server.clients.loaded", len(self.clients))

        # Update GUI with server status
        self.gui_manager.update_server_status(True, "0.0.0.0", self.port)
        self.gui_manager.update_client_stats({
            'connected': 0,
            'total': len(self.clients),
            'active_transfers': 0
        })

        # Signal to the GUI that the initial data load is complete
        self.gui_manager.signal_data_loaded()


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

    # ============================================================================
    # ServerBridge Integration Layer - Wrapper Methods
    # ============================================================================

    def _format_response(self, success: bool, data: Any = None, error: str = "") -> dict[str, Any]:
        """Helper method to format responses in ServerBridge expected format."""
        return {
            'success': success,
            'data': data,
            'error': error
        }

    # --- Client Operations ---

    def get_clients(self) -> dict[str, Any]:
        """Get all clients - delegates to db_manager.get_all_clients()."""
        try:
            clients_data = self.db_manager.get_all_clients()
            return self._format_response(True, clients_data)
        except Exception as e:
            logger.error(f"Failed to get clients: {e}")
            return self._format_response(False, error=str(e))

    async def get_clients_async(self) -> dict[str, Any]:
        """Async version of get_clients()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_clients)

    def get_client_details(self, client_id: str) -> dict[str, Any]:
        """Get details for a specific client by ID."""
        try:
            client_id_bytes = bytes.fromhex(client_id)
            client_data = self.db_manager.get_client_by_id(client_id_bytes)
            if client_data:
                return self._format_response(True, {
                    'id': client_id_bytes.hex(),
                    'name': client_data[1],
                    'last_seen': client_data[3],
                    'public_key_size': len(client_data[2]) if client_data[2] else 0
                })
            else:
                return self._format_response(False, error=f"Client with ID {client_id} not found")
        except Exception as e:
            logger.error(f"Failed to get client details for {client_id}: {e}")
            return self._format_response(False, error=str(e))

    def add_client(self, client_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new client using existing client creation logic."""
        try:
            import uuid
            client_id = uuid.uuid4().bytes
            name = client_data.get('name', '')

            if not name:
                return self._format_response(False, error="Client name is required")

            # Check if client name already exists
            with self.clients_lock:
                if name in self.clients_by_name:
                    return self._format_response(False, error=f"Client name '{name}' already exists")

            # Create new client
            client = self.create_client(client_id, name)

            # Add to in-memory store
            with self.clients_lock:
                self.clients[client_id] = client
                self.clients_by_name[name] = client_id

            # Save to database
            self._save_client_to_db(client)

            return self._format_response(True, {
                'id': client_id.hex(),
                'name': name,
                'created': True
            })
        except Exception as e:
            logger.error(f"Failed to add client: {e}")
            return self._format_response(False, error=str(e))

    async def add_client_async(self, client_data: dict[str, Any]) -> dict[str, Any]:
        """Async version of add_client()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.add_client, client_data)

    def delete_client(self, client_id: str) -> dict[str, Any]:
        """Delete a client - delegates to db_manager.delete_client()."""
        try:
            client_id_bytes = bytes.fromhex(client_id)

            # Remove from in-memory store
            with self.clients_lock:
                if client := self.clients.pop(client_id_bytes, None):
                    self.clients_by_name.pop(client.name, None)

            # Delete from database
            success = self.db_manager.delete_client(client_id_bytes)

            if success:
                return self._format_response(True, {'deleted': True})
            else:
                return self._format_response(False, error="Failed to delete client from database")
        except Exception as e:
            logger.error(f"Failed to delete client {client_id}: {e}")
            return self._format_response(False, error=str(e))

    async def delete_client_async(self, client_id: str) -> dict[str, Any]:
        """Async version of delete_client()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.delete_client, client_id)

    def update_client(self, client_id: str, updated_data: dict[str, Any]) -> dict[str, Any]:
        """
        Update client information.

        Args:
            client_id: Client UUID as hex string
            updated_data: Dictionary with fields to update:
                - 'name': str (optional) - New client name
                - 'public_key': bytes (optional) - New public key

        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            # Convert hex string to bytes
            client_id_bytes = bytes.fromhex(client_id)

            # Extract fields to update
            name = updated_data.get('name')
            public_key = updated_data.get('public_key')  # Should be bytes if provided

            # Validate name if provided
            if name is not None:
                if not isinstance(name, str) or len(name) == 0:
                    return self._format_response(False, error="Invalid name: must be non-empty string")
                if len(name) > MAX_CLIENT_NAME_LENGTH:
                    return self._format_response(False, error=f"Name too long (max {MAX_CLIENT_NAME_LENGTH} chars)")

                # Check if new name conflicts with existing client
                with self.clients_lock:
                    if name in self.clients_by_name:
                        existing_id = self.clients_by_name[name]
                        if existing_id != client_id_bytes:
                            return self._format_response(False, error=f"Client name '{name}' already exists")

            # Update in database
            success = self.db_manager.update_client(client_id_bytes, name, public_key)

            if not success:
                return self._format_response(False, error="Failed to update client in database")

            # Update in-memory representation if client is currently connected
            with self.clients_lock:
                if client := self.clients.get(client_id_bytes):
                    old_name = client.name

                    # Update name mapping
                    if name and name != old_name:
                        self.clients_by_name.pop(old_name, None)
                        client.name = name
                        self.clients_by_name[name] = client_id_bytes
                        logger.info(f"Updated client name: '{old_name}' → '{name}'")

                    # Update public key if provided
                    if public_key:
                        client.set_public_key(public_key)
                        logger.info(f"Updated public key for client '{client.name}'")

            return self._format_response(True, {
                'id': client_id,
                'updated': True,
                'fields_updated': [k for k, v in {'name': name, 'public_key': public_key}.items() if v is not None]
            })

        except ValueError as e:
            logger.error(f"Invalid client ID format '{client_id}': {e}")
            return self._format_response(False, error=f"Invalid client ID: {e}")
        except Exception as e:
            logger.error(f"Failed to update client {client_id}: {e}")
            return self._format_response(False, error=str(e))

    async def update_client_async(self, client_id: str, updated_data: dict[str, Any]) -> dict[str, Any]:
        """Async version of update_client()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.update_client, client_id, updated_data)

    def disconnect_client(self, client_id: str) -> dict[str, Any]:
        """Disconnect a client (remove from in-memory store only)."""
        try:
            client_id_bytes = bytes.fromhex(client_id)

            with self.clients_lock:
                client = self.clients.pop(client_id_bytes, None)
                if client:
                    self.clients_by_name.pop(client.name, None)
                    logger.info(f"Client '{client.name}' disconnected")
                    return self._format_response(True, {'disconnected': True})
                else:
                    return self._format_response(False, error="Client not found in active connections")
        except Exception as e:
            logger.error(f"Failed to disconnect client {client_id}: {e}")
            return self._format_response(False, error=str(e))

    async def disconnect_client_async(self, client_id: str) -> dict[str, Any]:
        """Async version of disconnect_client()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.disconnect_client, client_id)

    # --- File Operations ---

    def get_files(self) -> dict[str, Any]:
        """Get all files - delegates to db_manager.get_all_files()."""
        try:
            files_data = self.db_manager.get_all_files()
            # Normalize client_id to hex string if it's bytes
            for file_data in files_data:
                if 'client_id' in file_data and isinstance(file_data['client_id'], bytes):
                    file_data['client_id'] = file_data['client_id'].hex()
            return self._format_response(True, files_data)
        except Exception as e:
            logger.error(f"Failed to get files: {e}")
            return self._format_response(False, error=str(e))

    async def get_files_async(self) -> dict[str, Any]:
        """Async version of get_files()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_files)

    def get_client_files(self, client_id: str) -> dict[str, Any]:
        """Get files for a specific client - delegates to db_manager.get_files_for_client()."""
        try:
            # Pass the hex string directly to db_manager.get_files_for_client
            files_data = self.db_manager.get_files_for_client(client_id)
            # Attach client_id to each file entry
            for file_data in files_data:
                file_data['client_id'] = client_id
            return self._format_response(True, files_data)
        except Exception as e:
            logger.error(f"Failed to get files for client {client_id}: {e}")
            return self._format_response(False, error=str(e))

    async def get_client_files_async(self, client_id: str) -> dict[str, Any]:
        """Async version of get_client_files()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_client_files, client_id)

    def delete_file(self, file_id: str) -> dict[str, Any]:
        """Delete a file - delegates to db_manager.delete_file()."""
        try:
            if ':' not in file_id:
                # Fallback: try to parse as a single identifier
                return self._format_response(False, error="Invalid file_id format. Expected 'client_id:filename'")

            client_id_str, filename = file_id.split(':', 1)
            if success := self.db_manager.delete_file(client_id_str, filename):
                return self._format_response(True, {'deleted': True})
            else:
                return self._format_response(False, error="Failed to delete file")
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return self._format_response(False, error=str(e))

    def delete_file_by_client_and_name(self, client_id: str, filename: str) -> dict[str, Any]:
        """Delete a file by client ID and filename."""
        try:
            success = self.db_manager.delete_file(client_id, filename)
            if success:
                return self._format_response(True, {'deleted': True})
            else:
                return self._format_response(False, error="Failed to delete file")
        except Exception as e:
            logger.error(f"Failed to delete file {client_id}:{filename}: {e}")
            return self._format_response(False, error=str(e))

    async def delete_file_async(self, file_id: str) -> dict[str, Any]:
        """Async version of delete_file()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.delete_file, file_id)

    async def delete_file_by_client_and_name_async(self, client_id: str, filename: str) -> dict[str, Any]:
        """Async version of delete_file_by_client_and_name()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.delete_file_by_client_and_name, client_id, filename)

    def download_file(self, file_id: str, destination_path: str) -> dict[str, Any]:
        """Download a file (placeholder implementation)."""
        try:
            # This would require implementation of actual file download logic
            # For now, returning a placeholder response
            logger.info(f"Download requested for file {file_id} to {destination_path}")
            return self._format_response(False, error="Download functionality not yet implemented")
        except Exception as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            return self._format_response(False, error=str(e))

    async def download_file_async(self, file_id: str, destination_path: str) -> dict[str, Any]:
        """Async version of download_file()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.download_file, file_id, destination_path)

    def verify_file(self, file_id: str) -> dict[str, Any]:
        """Verify a file's integrity (placeholder implementation)."""
        try:
            # This would require implementation of actual file verification logic
            logger.info(f"Verification requested for file {file_id}")
            return self._format_response(False, error="File verification functionality not yet implemented")
        except Exception as e:
            logger.error(f"Failed to verify file {file_id}: {e}")
            return self._format_response(False, error=str(e))

    async def verify_file_async(self, file_id: str) -> dict[str, Any]:
        """Async version of verify_file()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.verify_file, file_id)

    # --- Database Operations ---

    def get_database_info(self) -> dict[str, Any]:
        """Get database information - delegates to db_manager.get_database_stats()."""
        try:
            db_stats = self.db_manager.get_database_stats()
            return self._format_response(True, db_stats)
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return self._format_response(False, error=str(e))

    async def get_database_info_async(self) -> dict[str, Any]:
        """Async version of get_database_info()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_database_info)

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get data from a specific table (basic implementation)."""
        try:
            # This is a basic implementation - in a real system you'd want more sophisticated querying
            if table_name.lower() == 'clients':
                data = self.db_manager.get_all_clients()
            elif table_name.lower() == 'files':
                data = self.db_manager.get_all_files()
            else:
                return self._format_response(False, error=f"Table '{table_name}' not supported")

            return self._format_response(True, data)
        except Exception as e:
            logger.error(f"Failed to get table data for {table_name}: {e}")
            return self._format_response(False, error=str(e))

    async def get_table_data_async(self, table_name: str) -> dict[str, Any]:
        """Async version of get_table_data()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_table_data, table_name)

    def update_row(self, table_name: str, row_id: str, updated_data: dict[str, Any]) -> dict[str, Any]:
        """Update a row in a table (placeholder implementation)."""
        try:
            # This would require more sophisticated implementation based on the actual schema
            logger.info(f"Update requested for table {table_name}, row {row_id}")
            return self._format_response(False, error="Row update functionality not yet implemented")
        except Exception as e:
            logger.error(f"Failed to update row {row_id} in table {table_name}: {e}")
            return self._format_response(False, error=str(e))

    def delete_row(self, table_name: str, row_id: str) -> dict[str, Any]:
        """Delete a row from a table (placeholder implementation)."""
        try:
            # This would require more sophisticated implementation based on the actual schema
            logger.info(f"Delete requested for table {table_name}, row {row_id}")
            return self._format_response(False, error="Row deletion functionality not yet implemented")
        except Exception as e:
            logger.error(f"Failed to delete row {row_id} from table {table_name}: {e}")
            return self._format_response(False, error=str(e))

    # --- Server Status & Monitoring ---

    def is_connected(self) -> bool:
        """Check if server is connected and operational - required by ServerBridge."""
        try:
            # Server is considered connected if it's running and has a healthy database connection
            if not self.running:
                return False

            # Check database health if available
            if hasattr(self, 'db_manager') and self.db_manager:
                try:
                    # Quick database health check
                    health = self.db_manager.get_database_health()
                    return health.get('integrity_check', False) if isinstance(health, dict) else False
                except Exception:
                    return False

            # If no database manager, just check if server is running
            return self.running

        except Exception as e:
            logger.debug(f"is_connected check failed: {e}")
            return False

    def get_server_status(self) -> dict[str, Any]:
        """Get current server status including running state, port, uptime."""
        try:
            uptime = time.time() - self.network_server.start_time if self.running else 0
            status_data = {
                'running': self.running,
                'port': self.port,
                'host': getattr(self.network_server, 'host', '0.0.0.0'),
                'uptime_seconds': uptime,
                'uptime_formatted': f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
                'version': SERVER_VERSION if 'SERVER_VERSION' in globals() else 'Unknown',
                'last_error': getattr(self.network_server, 'last_error', '') or ''
            }
            return self._format_response(True, status_data)
        except Exception as e:
            logger.error(f"Failed to get server status: {e}")
            return self._format_response(False, error=str(e))

    async def get_server_status_async(self) -> dict[str, Any]:
        """Async version of get_server_status()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_server_status)

    def get_detailed_server_status(self) -> dict[str, Any]:
        """Get comprehensive server metrics including connection stats."""
        try:
            basic_status = self.get_server_status()['data']

            # Get connection statistics
            connection_stats = self.network_server.get_connection_stats() if hasattr(self.network_server, 'get_connection_stats') else {}

            # Get client statistics
            with self.clients_lock:
                connected_clients = len(self.clients)

            total_clients = self.db_manager.get_total_clients_count()

            detailed_data = {
                **basic_status,
                'connections': {
                    'active_connections': connection_stats.get('active_connections', connected_clients),
                    'total_connections': connection_stats.get('total_connections', 0),
                    'peak_connections': connection_stats.get('peak_connections', 0)
                },
                'clients': {
                    'connected': connected_clients,
                    'total_registered': total_clients
                },
                'database': {
                    'total_files': len(self.db_manager.get_all_files()) if hasattr(self.db_manager, 'get_all_files') else 0
                }
            }

            return self._format_response(True, detailed_data)
        except Exception as e:
            logger.error(f"Failed to get detailed server status: {e}")
            return self._format_response(False, error=str(e))

    async def get_detailed_server_status_async(self) -> dict[str, Any]:
        """Async version of get_detailed_server_status()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_detailed_server_status)

    def get_server_health(self) -> dict[str, Any]:
        """Get server health metrics."""
        try:
            health_data = {
                'status': 'healthy' if self.running else 'stopped',
                'database_accessible': True,  # Basic check
                'network_server_running': hasattr(self.network_server, 'running') and getattr(self.network_server, 'running', False),
                'gui_manager_ready': self.gui_manager.is_gui_ready() if hasattr(self.gui_manager, 'is_gui_ready') else False,
                'errors': []
            }

            # Perform basic health checks
            try:
                self.db_manager.get_total_clients_count()
            except Exception as e:
                health_data['database_accessible'] = False
                health_data['errors'].append(f"Database error: {e!s}")
                health_data['status'] = 'unhealthy'

            return self._format_response(True, health_data)
        except Exception as e:
            logger.error(f"Failed to get server health: {e}")
            return self._format_response(False, error=str(e))

    async def get_server_health_async(self) -> dict[str, Any]:
        """Async version of get_server_health()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_server_health)

    def start_server(self) -> dict[str, Any]:
        """Start the server (wrapper for existing start method)."""
        try:
            if self.running:
                return self._format_response(False, error="Server is already running")

            self.start()
            return self._format_response(True, {'started': True})
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return self._format_response(False, error=str(e))

    async def start_server_async(self) -> dict[str, Any]:
        """Async version of start_server()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.start_server)

    def stop_server(self) -> dict[str, Any]:
        """Stop the server (wrapper for existing stop method)."""
        try:
            if not self.running:
                return self._format_response(False, error="Server is not running")

            self.stop()
            return self._format_response(True, {'stopped': True})
        except Exception as e:
            logger.error(f"Failed to stop server: {e}")
            return self._format_response(False, error=str(e))

    async def stop_server_async(self) -> dict[str, Any]:
        """Async version of stop_server()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.stop_server)

    def test_connection(self) -> dict[str, Any]:
        """Test server connection status."""
        try:
            test_data = {
                'server_accessible': self.running,
                'database_accessible': True,
                'response_time_ms': 0  # Placeholder
            }

            # Basic database connectivity test
            start_time = time.time()
            try:
                self.db_manager.get_total_clients_count()
                test_data['response_time_ms'] = (time.time() - start_time) * 1000
            except Exception as e:
                test_data['database_accessible'] = False
                test_data['database_error'] = str(e)

            return self._format_response(True, test_data)
        except Exception as e:
            logger.error(f"Failed to test connection: {e}")
            return self._format_response(False, error=str(e))

    async def test_connection_async(self) -> dict[str, Any]:
        """Async version of test_connection()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.test_connection)

    # --- Analytics & System ---

    def get_system_status(self) -> dict[str, Any]:
        """Get system-level status information."""
        try:
            import psutil
            system_data = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
                'python_version': sys.version.split()[0],
                'platform': sys.platform
            }
            return self._format_response(True, system_data)
        except ImportError:
            # Fallback if psutil is not available
            system_data = {
                'python_version': sys.version.split()[0],
                'platform': sys.platform,
                'note': 'Limited system info available (psutil not installed)'
            }
            return self._format_response(True, system_data)
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return self._format_response(False, error=str(e))

    async def get_system_status_async(self) -> dict[str, Any]:
        """Async version of get_system_status()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_system_status)

    def get_analytics_data(self) -> dict[str, Any]:
        """Get analytics information."""
        try:
            analytics_data = {
                'total_clients': self.db_manager.get_total_clients_count(),
                'total_files': len(self.db_manager.get_all_files()) if hasattr(self.db_manager, 'get_all_files') else 0,
                'server_uptime_seconds': time.time() - self.network_server.start_time if self.running else 0,
                'database_stats': self.db_manager.get_database_stats() if hasattr(self.db_manager, 'get_database_stats') else {}
            }
            return self._format_response(True, analytics_data)
        except Exception as e:
            logger.error(f"Failed to get analytics data: {e}")
            return self._format_response(False, error=str(e))

    async def get_analytics_data_async(self) -> dict[str, Any]:
        """Async version of get_analytics_data()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_analytics_data)

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance data."""
        try:
            metrics_data = {
                'active_connections': len(self.clients),
                'database_response_time_ms': 0,  # Placeholder
                'memory_usage_mb': 0,  # Placeholder
                'cpu_usage_percent': 0  # Placeholder
            }

            # Test database response time
            start_time = time.time()
            try:
                self.db_manager.get_total_clients_count()
                metrics_data['database_response_time_ms'] = int((time.time() - start_time) * 1000)
            except Exception:
                metrics_data['database_response_time_ms'] = -1

            return self._format_response(True, metrics_data)
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return self._format_response(False, error=str(e))

    async def get_performance_metrics_async(self) -> dict[str, Any]:
        """Async version of get_performance_metrics()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_performance_metrics)

    def get_dashboard_summary(self) -> dict[str, Any]:
        """Get dashboard data."""
        try:
            dashboard_data = {
                'server_status': 'running' if self.running else 'stopped',
                'total_clients': self.db_manager.get_total_clients_count(),
                'connected_clients': len(self.clients),
                'total_files': len(self.db_manager.get_all_files()) if hasattr(self.db_manager, 'get_all_files') else 0,
                'server_version': SERVER_VERSION if 'SERVER_VERSION' in globals() else 'Unknown',
                'uptime': time.time() - self.network_server.start_time if self.running else 0
            }
            return self._format_response(True, dashboard_data)
        except Exception as e:
            logger.error(f"Failed to get dashboard summary: {e}")
            return self._format_response(False, error=str(e))

    async def get_dashboard_summary_async(self) -> dict[str, Any]:
        """Async version of get_dashboard_summary()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_dashboard_summary)

    def get_server_statistics(self) -> dict[str, Any]:
        """Get detailed statistics."""
        try:
            stats_data = {
                'server': {
                    'version': SERVER_VERSION if 'SERVER_VERSION' in globals() else 'Unknown',
                    'running': self.running,
                    'uptime_seconds': time.time() - self.network_server.start_time if self.running else 0,
                    'port': self.port
                },
                'clients': {
                    'total_registered': self.db_manager.get_total_clients_count(),
                    'currently_connected': len(self.clients)
                },
                'files': {
                    'total_files': len(self.db_manager.get_all_files()) if hasattr(self.db_manager, 'get_all_files') else 0
                },
                'database': self.db_manager.get_database_stats() if hasattr(self.db_manager, 'get_database_stats') else {}
            }
            return self._format_response(True, stats_data)
        except Exception as e:
            logger.error(f"Failed to get server statistics: {e}")
            return self._format_response(False, error=str(e))

    async def get_server_statistics_async(self) -> dict[str, Any]:
        """Async version of get_server_statistics()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_server_statistics)

    async def get_recent_activity_async(self, limit: int = 50) -> dict[str, Any]:
        """
        Get recent system activity from server logs.

        Args:
            limit: Maximum number of activity entries to return (default 50)

        Returns:
            dict: {'success': bool, 'data': list[dict], 'error': str}
                Each activity dict contains:
                - 'timestamp': ISO timestamp string
                - 'type': Activity type (info/warning/error/client/file)
                - 'message': Human-readable message
                - 'details': Optional additional context
        """
        import asyncio

        try:
            # Run log parsing in executor to avoid blocking
            loop = asyncio.get_event_loop()
            activities = await loop.run_in_executor(None, self._parse_recent_logs, limit)

            return self._format_response(True, activities)
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return self._format_response(False, error=str(e))

    def _parse_recent_logs(self, limit: int) -> list[dict[str, Any]]:
        """
        Parse recent log entries into structured activity records.

        Args:
            limit: Maximum number of entries to return

        Returns:
            list: Activity records sorted by timestamp (most recent first)
        """
        activities = []

        # Determine which log file to read
        log_file = getattr(self, 'backup_log_file', None)
        if not log_file or not os.path.exists(log_file):
            log_file = 'server.log'

        if not os.path.exists(log_file):
            logger.warning(f"Log file not found: {log_file}")
            return []

        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                # Read last N*2 lines (we'll filter and limit after parsing)
                lines = f.readlines()[-(limit * 2):]

            # Parse log format: "timestamp - thread - level - message"
            for line in lines:
                try:
                    parts = line.strip().split(' - ', 3)
                    if len(parts) < 4:
                        continue

                    timestamp_str, thread_name, log_level, message = parts

                    # Determine activity type based on message content
                    activity_type = self._classify_activity(message, log_level)

                    # Skip debug/verbose entries unless specifically requested
                    if log_level.upper() == 'DEBUG':
                        continue

                    activities.append({
                        'timestamp': timestamp_str,
                        'type': activity_type,
                        'level': log_level.upper(),
                        'message': message,
                        'thread': thread_name
                    })

                except (ValueError, IndexError) as e:
                    # Skip malformed log lines
                    logger.debug(f"Skipped malformed log line: {e}")
                    continue

            # Sort by timestamp (most recent first) and limit
            activities.reverse()
            return activities[:limit]

        except Exception as e:
            logger.error(f"Error reading log file {log_file}: {e}")
            return []

    def _classify_activity(self, message: str, log_level: str) -> str:
        """
        Classify activity type based on message content.

        Args:
            message: Log message text
            log_level: Log level (INFO/WARNING/ERROR)

        Returns:
            str: Activity type (client/file/server/error/warning/info)
        """
        message_lower = message.lower()

        # Client-related activities
        if any(keyword in message_lower for keyword in ['client', 'connected', 'disconnected', 'registered']):
            return 'client'

        # File-related activities
        if any(keyword in message_lower for keyword in ['file', 'upload', 'backup', 'download', 'verified']):
            return 'file'

        # Server-related activities
        if any(keyword in message_lower for keyword in ['server', 'started', 'stopped', 'shutdown', 'startup']):
            return 'server'

        # Error/warning based on log level
        if log_level.upper() == 'ERROR':
            return 'error'
        if log_level.upper() == 'WARNING':
            return 'warning'

        # Default
        return 'info'

    def get_historical_data(self, metric: str = "connections", hours: int = 24) -> dict[str, Any]:
        """Get historical data for metrics."""
        try:
            # Generate mock historical data points
            import random
            from datetime import datetime, timedelta

            points = []
            now = datetime.now()

            # Generate data points for the specified time range
            for i in range(hours):
                timestamp = now - timedelta(hours=i)
                # Generate mock values based on metric type
                if metric == "connections":
                    value = random.randint(0, 50)
                elif metric == "files":
                    value = random.randint(0, 100)
                elif metric == "bandwidth":
                    value = random.randint(0, 1000)
                else:
                    value = random.randint(0, 100)

                points.append({
                    'timestamp': timestamp.isoformat(),
                    'value': value
                })

            # Reverse to show oldest first
            points.reverse()

            return self._format_response(True, {'points': points})
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return self._format_response(False, error=str(e))

    async def get_historical_data_async(self, metric: str = "connections", hours: int = 24) -> dict[str, Any]:
        """Async version of get_historical_data()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_historical_data, metric, hours)

    # --- Log Operations ---

    def get_logs(self) -> dict[str, Any]:
        """Get system logs (basic implementation)."""
        try:
            # This is a basic implementation - in a production system you'd want proper log aggregation
            log_data = {
                'logs': [],
                'note': 'Log retrieval functionality requires implementation of log storage/retrieval system'
            }

            # Try to read recent log entries if log file exists
            try:
                # Check self.backup_log_file first, then module variable, then fallback to server.log
                if hasattr(self, 'backup_log_file') and os.path.exists(self.backup_log_file):
                    with open(self.backup_log_file, encoding='utf-8') as f:
                        lines = f.readlines()
                        # Get last 100 lines
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        log_data['logs'] = [line.strip() for line in recent_lines]
                elif os.path.exists(backup_log_file):  # Fallback to module variable
                    with open(backup_log_file, encoding='utf-8') as f:
                        lines = f.readlines()
                        # Get last 100 lines
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        log_data['logs'] = [line.strip() for line in recent_lines]
                elif os.path.exists('server.log'):
                    with open('server.log', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Get last 100 lines
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        log_data['logs'] = [line.strip() for line in recent_lines]
            except Exception as read_error:
                log_data['read_error'] = str(read_error)

            return self._format_response(True, log_data)
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return self._format_response(False, error=str(e))

    async def get_logs_async(self) -> dict[str, Any]:
        """Async version of get_logs()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_logs)

    async def clear_logs_async(self) -> dict[str, Any]:
        """Clear system logs (placeholder implementation)."""
        try:
            # This would require careful implementation to avoid disrupting active logging
            return self._format_response(False, error="Log clearing functionality not yet implemented for safety")
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            return self._format_response(False, error=str(e))

    async def export_logs_async(self, export_format: str, filters: dict[str, Any]) -> dict[str, Any]:
        """Export logs with filtering (placeholder implementation)."""
        try:
            return self._format_response(False, error="Log export functionality not yet implemented")
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return self._format_response(False, error=str(e))

    # --- Settings Management ---

    def save_settings(self, settings_data: dict[str, Any]) -> dict[str, Any]:
        """Save settings (placeholder implementation)."""
        try:
            # This would require implementation of a settings storage system
            logger.info("Settings save requested")
            return self._format_response(False, error="Settings save functionality not yet implemented")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return self._format_response(False, error=str(e))

    async def save_settings_async(self, settings_data: dict[str, Any]) -> dict[str, Any]:
        """Async version of save_settings()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.save_settings, settings_data)

    def load_settings(self) -> dict[str, Any]:
        """Load settings (placeholder implementation)."""
        try:
            # This would require implementation of a settings storage system
            default_settings = {
                'server_port': self.port,
                'max_clients': MAX_CONCURRENT_CLIENTS if 'MAX_CONCURRENT_CLIENTS' in globals() else 50,
                'log_level': 'INFO',
                'note': 'Settings load functionality requires implementation of settings storage system'
            }
            return self._format_response(True, default_settings)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return self._format_response(False, error=str(e))

    async def load_settings_async(self) -> dict[str, Any]:
        """Async version of load_settings()."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.load_settings)


# --- Main Execution Guard ---
if __name__ == "__main__":
    server_instance = None  # Initialize to ensure it's always bound
    try:
        # Display a startup banner for the server console
        print("=====================================================================")
        print(f"      Secure Encrypted File Backup Server - Version {SERVER_VERSION}      ")
        print(f"      Process ID: {os.getpid()}                                     ")
        print("=====================================================================")

        # Display logging information
        try:
            log_monitor_info = create_log_monitor_info(backup_log_file, "Backup Server")
            print("Logging Information:")
            print(f"  Enhanced Log: {log_monitor_info['file_path']}")
            print(f"  Legacy Log:   {os.path.abspath('server.log')}")
            print(f"  Live Monitor: {log_monitor_info['powershell_cmd']}")
            print("  Console:      Visible in this window (dual output enabled)")
            print("=====================================================================")
        except Exception as e:
            print(f"  [WARNING] Could not display logging info: {e}")
            print("=====================================================================")

        # Perform basic pre-flight checks before attempting to start the server
        if sys.version_info < (3, 7): # PyCryptodome generally works better with Python 3.7+
            print("Warning: Python 3.7 or newer is recommended for optimal server performance and security library compatibility.", file=sys.stderr)

        # Quick check to ensure PyCryptodome is available and basic operations work
        try:
            _ = RSA.generate(1024, randfunc=get_random_bytes) # Test RSA key generation
            _ = AES.new(get_random_bytes(AES_KEY_SIZE_BYTES), AES.MODE_CBC, iv=get_random_bytes(16))  # type: ignore[misc]  # Test AES cipher creation
            logger.info("PyCryptodome library check passed: Basic crypto operations are available.")
        except Exception as e_crypto_check:
            print(f"CRITICAL FAILURE: PyCryptodome library is not installed correctly or is non-functional: {e_crypto_check}", file=sys.stderr)
            print("Please ensure PyCryptodome is properly installed (e.g., via 'pip install pycryptodomex'). Server cannot start.", file=sys.stderr)
            sys.exit(1) # Exit if essential crypto library is missing/broken

        print("DEBUG: Checking crypto library...")
        # Ensure only one server instance runs at a time
        print("DEBUG: Ensuring single server instance...")
        ensure_single_server_instance("BackupServer", 1256)

        # Instantiate the server
        print("DEBUG: Creating BackupServer instance...")
        # Instantiate the server
        server_instance = BackupServer()
        print("DEBUG: BackupServer created successfully!")

        # The GUIManager was initialized in the BackupServer constructor.
        # The GUI is running in a separate thread, started by the GUIManager.
        # The main thread can now wait for a shutdown signal or simply keep alive.
        # The GUI's mainloop will handle user interaction and application lifetime.

        # Wait for the GUI to signal it's ready before we proceed (with timeout)
        print("DEBUG: Waiting for GUI to initialize...")
        logger.info("Waiting for GUI to initialize...")
        gui_ready = server_instance.gui_manager.gui_ready.wait(timeout=5.0)  # Reduced timeout
        print(f"DEBUG: GUI ready result: {gui_ready}")

        # Start the server regardless of GUI status
        print("DEBUG: Starting backup server...")
        logger.info("Starting backup server on port 1256...")
        server_instance.start()
        print("DEBUG: Backup server started successfully!")

        if gui_ready and hasattr(server_instance.gui_manager, 'is_gui_running') and server_instance.gui_manager.is_gui_running():
            print("DEBUG: GUI is running, entering GUI mode...")
            logger.info("GUI is ready. Main thread is now idle, application is driven by GUI and server threads.")
            # Keep the main thread alive. The application will exit when the GUI is closed.
            while server_instance.gui_manager.is_gui_running():
                time.sleep(1)
        else:
            # Console-only mode
            print("DEBUG: Running in console-only mode...")
            logger.info("Running in console-only mode. Press Ctrl+C to stop.")
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
