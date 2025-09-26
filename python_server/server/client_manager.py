# client_manager.py
# Client Management Module
# Extracted from monolithic server.py for better modularity and organization

import logging
import threading
import time
from datetime import UTC, datetime
from typing import Any

# Import crypto components through compatibility layer
from Crypto.PublicKey import RSA

from .config import (
    AES_KEY_SIZE_BYTES,
    CLIENT_SESSION_TIMEOUT,
    PARTIAL_FILE_TIMEOUT,
    RSA_PUBLIC_KEY_SIZE,
)
from .database import DatabaseManager

# Import custom exceptions and configuration
from .exceptions import ClientError, ProtocolError, ServerError

logger = logging.getLogger(__name__)


class Client:
    """
    Represents a connected client and stores its state.
    Thread-safe client object with comprehensive state management.
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
        self.public_key_obj: Any | None = None  # Use flexible type for compatibility layer
        self.aes_key: bytes | None = None  # Current session AES key
        self.last_seen: float = time.monotonic()  # Monotonic time for session timeout
        self.partial_files: dict[str, dict[str, Any]] = {}  # For reassembling multi-packet files
        self.lock: threading.Lock = threading.Lock()  # To protect concurrent access to client state

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
                self.public_key_obj = None  # Ensure consistent state if import fails

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
            self._import_public_key()  # Attempt to parse and store the RsaKey object
            if not self.public_key_obj:  # Check if import failed
                raise ProtocolError(f"Invalid RSA public key format provided by client '{self.name}' (failed to import).")

    def get_aes_key(self) -> bytes | None:
        """Returns the current session AES key."""
        return self.aes_key

    def set_aes_key(self, aes_key_data: bytes):
        """
        Sets the client's session AES key.

        Args:
            aes_key_data: The AES key (bytes).

        Raises:
            ValueError: If the AES key size is incorrect.
        """
        with self.lock:  # Protect AES key modification
            if len(aes_key_data) != AES_KEY_SIZE_BYTES:
                raise ValueError(f"AES key size for client '{self.name}' is incorrect. Expected {AES_KEY_SIZE_BYTES}, got {len(aes_key_data)}.")
            self.aes_key = aes_key_data

    def clear_partial_file(self, filename: str):
        """Removes partial file reassembly data for a given filename."""
        with self.lock:
            if filename in self.partial_files:
                del self.partial_files[filename]
                logger.debug(f"Client '{self.name}': Cleared partial file reassembly data for '{filename}'.")


    def clear_all_partial_files(self) -> int:
        """Clears all in-memory partial file transfer states for this client.
        Returns the number of cleared partial entries.
        """
        with self.lock:
            count = len(self.partial_files)
            self.partial_files.clear()
            if count > 0:
                logger.info(f"Client '{self.name}': Cleared all partial file data due to disconnect/cancellation ({count} entries)")
            else:
                logger.debug(f"Client '{self.name}': No partial file data to clear on disconnect/cancellation")
            return count

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

    def is_session_expired(self) -> bool:
        """
        Checks if the client session has expired based on inactivity.

        Returns:
            True if the session has expired, False otherwise.
        """
        with self.lock:
            return (time.monotonic() - self.last_seen) > CLIENT_SESSION_TIMEOUT

    def get_session_age(self) -> float:
        """
        Returns the age of the current session in seconds.

        Returns:
            The session age in seconds.
        """
        with self.lock:
            return time.monotonic() - self.last_seen

    def has_public_key(self) -> bool:
        """
        Checks if the client has a valid public key.

        Returns:
            True if the client has a valid public key, False otherwise.
        """
        with self.lock:
            return self.public_key_obj is not None

    def has_aes_key(self) -> bool:
        """
        Checks if the client has an AES key set.

        Returns:
            True if the client has an AES key, False otherwise.
        """
        return self.aes_key is not None

    def get_partial_file_count(self) -> int:
        """
        Returns the number of partial files currently being tracked.

        Returns:
            The number of partial files.
        """
        with self.lock:
            return len(self.partial_files)

    def __str__(self) -> str:
        """String representation of the client."""
        return f"Client(id={self.id.hex()[:8]}..., name='{self.name}', has_pk={self.has_public_key()}, has_aes={self.has_aes_key()})"


class ClientManager:
    """
    Manages client collections, registration, updates, and cleanup.
    Provides thread-safe operations for client management with database persistence.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the ClientManager.

        Args:
            db_manager: DatabaseManager instance for persistence operations.
        """
        self.db_manager = db_manager
        self.clients: dict[bytes, Client] = {}  # In-memory store: client_id_bytes -> Client object
        self.clients_by_name: dict[str, bytes] = {}  # In-memory store: client_name_str -> client_id_bytes
        self.clients_lock: threading.Lock = threading.Lock()  # Protects access to clients and clients_by_name
        self.maintenance_stats: dict[str, Any] = {
            'last_cleanup': None,
            'clients_removed_total': 0,
            'partial_files_cleaned_total': 0
        }

    def load_clients_from_db(self):
        """
        Loads existing client data from the database into memory at startup.

        Raises:
            SystemExit: If critical client data cannot be loaded from database.
        """
        logger.info("Loading existing clients from database into memory...")
        try:
            rows = self.db_manager.load_clients_from_db()
        except ServerError as e:  # Raised by db_manager on critical read failure
            logger.critical(f"CRITICAL FAILURE: Could not load client data from database: {e}. Server cannot continue.")
            # This is a fatal error for server operation.
            raise SystemExit(f"Startup aborted: Failed to load critical client data from database. Details: {e}") from e

        with self.clients_lock:  # Ensure thread-safe access to shared client dictionaries
            self.clients.clear()
            self.clients_by_name.clear()
            loaded_count = 0
            if rows:  # Check if any rows were returned
                for row_id, name, pk_bytes, _last_seen_iso_utc in rows:
                    try:
                        client = Client(row_id, name, pk_bytes)  # Create Client object
                        # last_seen_iso_utc is from DB. Internal client.last_seen is monotonic for session timeout.
                        # We don't directly use DB's LastSeen for session timeout upon loading,
                        # but it's good for audit/record. Session starts fresh.
                        self.clients[row_id] = client
                        self.clients_by_name[name] = row_id
                        loaded_count += 1
                    except Exception as e_obj:  # Catch errors creating individual Client objects (e.g. bad PK)
                        logger.error(f"Error creating Client object for '{name}' (ID: {row_id.hex() if row_id else 'N/A'}) from DB row: {e_obj}")
            logger.info(f"Successfully loaded {loaded_count} client(s) from database.")

    def save_client_to_db(self, client: Client):
        """
        Saves or updates a client's information in the database.

        Args:
            client: The client object to save to database.
        """
        self.db_manager.save_client_to_db(client.id, client.name, client.public_key_bytes, client.get_aes_key())

    def register_client(self, client_id: bytes, name: str, public_key_bytes: bytes | None = None) -> Client:
        """
        Registers a new client or retrieves an existing one.

        Args:
            client_id: The unique UUID (bytes) of the client.
            name: The username of the client.
            public_key_bytes: The client's RSA public key in X.509 format (optional).

        Returns:
            The Client object (new or existing).

        Raises:
            ClientError: If there's a conflict with existing client data.
        """
        with self.clients_lock:
            # Check if client already exists by ID
            if client_id in self.clients:
                existing_client = self.clients[client_id]
                # Verify name consistency
                if existing_client.name != name:
                    raise ClientError(f"Client ID {client_id.hex()} already registered with different name: '{existing_client.name}' vs '{name}'")
                existing_client.update_last_seen()
                return existing_client

            # Check if name is already taken by different client
            if name in self.clients_by_name:
                existing_id = self.clients_by_name[name]
                if existing_id != client_id:
                    raise ClientError(f"Client name '{name}' already registered with different ID: {existing_id.hex()}")

            # Create new client
            client = Client(client_id, name, public_key_bytes)
            self.clients[client_id] = client
            self.clients_by_name[name] = client_id

            logger.info(f"Registered new client: '{name}' (ID: {client_id.hex()})")
            return client

    def get_client_by_id(self, client_id: bytes) -> Client | None:
        """
        Retrieves a client by ID.

        Args:
            client_id: The client's unique ID.

        Returns:
            The Client object if found, None otherwise.
        """
        with self.clients_lock:
            client = self.clients.get(client_id)
            if client:
                client.update_last_seen()
            return client

    def get_client_by_name(self, name: str) -> Client | None:
        """
        Retrieves a client by name.

        Args:
            name: The client's name.

        Returns:
            The Client object if found, None otherwise.
        """
        with self.clients_lock:
            if client_id := self.clients_by_name.get(name):
                client = self.clients.get(client_id)
                if client:
                    client.update_last_seen()
                return client
            return None

    def update_client_activity(self, client_id: bytes):
        """
        Updates the last seen timestamp for a client.

        Args:
            client_id: The client's unique ID.
        """
        with self.clients_lock:
            if client := self.clients.get(client_id):
                client.update_last_seen()

    def remove_client(self, client_id: bytes) -> bool:
        """
        Removes a client from memory (not from database).

        Args:
            client_id: The client's unique ID.

        Returns:
            True if client was removed, False if not found.
        """
        with self.clients_lock:
            if client := self.clients.pop(client_id, None):
                self.clients_by_name.pop(client.name, None)
                logger.info(f"Removed client '{client.name}' (ID: {client_id.hex()}) from active memory pool.")
                return True
            return False

    def cleanup_expired_sessions(self) -> int:
        """
        Removes clients with expired sessions from memory.

        Returns:
            The number of expired clients removed.
        """
        expired_clients: list[bytes] = []
        current_time = time.monotonic()

        with self.clients_lock:
            # Identify expired clients
            expired_clients.extend(
                client_id
                for client_id, client in self.clients.items()
                if current_time - client.last_seen > CLIENT_SESSION_TIMEOUT
            )
            # Remove expired clients
            removed_count = 0
            for client_id in expired_clients:
                client = self.clients.pop(client_id, None)
                if client is not None:
                    self.clients_by_name.pop(client.name, None)
                    removed_count += 1
                    logger.info(f"Client '{client.name}' (ID: {client_id.hex()}) session timed out due to inactivity. Removed from active memory pool.")

        self.maintenance_stats['clients_removed_total'] += removed_count
        return removed_count

    def cleanup_stale_partial_files(self) -> int:
        """
        Cleans up stale partial file transfer data for all active clients.

        Returns:
            The total number of stale partial files cleaned up.
        """
        # Get snapshot of current clients to avoid holding lock during cleanup
        with self.clients_lock:
            active_clients = list(self.clients.values())

        total_cleaned = sum(client.cleanup_stale_partial_files() for client in active_clients)
        self.maintenance_stats['partial_files_cleaned_total'] += total_cleaned
        return total_cleaned

    def run_maintenance(self) -> dict[str, int]:
        """
        Runs maintenance tasks including expired session cleanup and partial file cleanup.

        Returns:
            Dictionary with maintenance statistics.
        """
        logger.debug("Running client maintenance tasks...")

        # Clean up expired sessions
        expired_sessions_removed = self.cleanup_expired_sessions()

        # Clean up stale partial files
        stale_files_cleaned = self.cleanup_stale_partial_files()

        self.maintenance_stats['last_cleanup'] = datetime.now(UTC).isoformat()

        stats = {
            'expired_sessions_removed': expired_sessions_removed,
            'stale_files_cleaned': stale_files_cleaned,
            'active_clients': self.get_active_client_count(),
            'total_partial_files': self.get_total_partial_files()
        }

        if expired_sessions_removed > 0 or stale_files_cleaned > 0:
            logger.info(f"Maintenance completed: {expired_sessions_removed} expired sessions removed, {stale_files_cleaned} stale partial files cleaned")

        return stats

    def get_active_client_count(self) -> int:
        """
        Returns the number of currently active clients in memory.

        Returns:
            The number of active clients.
        """
        with self.clients_lock:
            return len(self.clients)

    def get_total_partial_files(self) -> int:
        """
        Returns the total number of partial files across all clients.

        Returns:
            The total number of partial files.
        """
        with self.clients_lock:
            return sum(client.get_partial_file_count() for client in self.clients.values())

    def get_client_stats(self) -> dict[str, Any]:
        """
        Returns comprehensive client statistics.

        Returns:
            Dictionary containing various client statistics.
        """
        with self.clients_lock:
            clients_with_keys = sum(bool(client.has_public_key())
                                for client in self.clients.values())
            clients_with_aes = sum(bool(client.has_aes_key())
                                for client in self.clients.values())

            return {
                'active_clients': len(self.clients),
                'clients_with_public_keys': clients_with_keys,
                'clients_with_aes_keys': clients_with_aes,
                'total_partial_files': self.get_total_partial_files(),
                'maintenance_stats': self.maintenance_stats.copy()
            }

    def get_client_list(self) -> list[dict[str, Any]]:
        """
        Returns a list of client information dictionaries.

        Returns:
            List of dictionaries containing client information.
        """
        with self.clients_lock:
            client_list: list[dict[str, Any]] = []
            for client in self.clients.values():
                client_info = {
                    'id': client.id.hex(),
                    'name': client.name,
                    'has_public_key': client.has_public_key(),
                    'has_aes_key': client.has_aes_key(),
                    'session_age': client.get_session_age(),
                    'partial_files_count': client.get_partial_file_count()
                }
                client_list.append(client_info)
            return client_list

    def is_name_available(self, name: str, exclude_id: bytes | None = None) -> bool:
        """
        Checks if a client name is available for registration.

        Args:
            name: The name to check.
            exclude_id: Optional client ID to exclude from the check.

        Returns:
            True if the name is available, False otherwise.
        """
        with self.clients_lock:
            if name not in self.clients_by_name:
                return True

            if exclude_id is not None:
                existing_id = self.clients_by_name[name]
                return existing_id == exclude_id

            return False

    def shutdown(self):
        """
        Performs cleanup operations before shutdown.
        """
        logger.info("ClientManager shutting down...")
        with self.clients_lock:
            active_count = len(self.clients)
            self.clients.clear()
            self.clients_by_name.clear()
            logger.info(f"ClientManager shutdown complete. Cleared {active_count} active clients from memory.")
