# request_handlers.py
# Request Handler Module for Backup Server
# Contains all request processing logic extracted from server.py for better modularity

import socket
import struct
import uuid
import os
import logging
import re
from typing import Dict, Optional, Any, Callable

# Import crypto components through compatibility layer
from crypto_compat import AES, RSA, PKCS1_OAEP, pad, unpad, get_random_bytes, SHA256

# Import custom exceptions
from exceptions import ServerError, ProtocolError, ClientError, FileError

# Import configuration constants
from config import (
    SERVER_VERSION, FILE_STORAGE_DIR, MAX_CLIENT_NAME_LENGTH, 
    MAX_FILENAME_FIELD_SIZE, MAX_ACTUAL_FILENAME_LENGTH, 
    RSA_PUBLIC_KEY_SIZE, AES_KEY_SIZE_BYTES, MAX_PAYLOAD_READ_LIMIT,
    MAX_ORIGINAL_FILE_SIZE
)

# Import protocol constants
from protocol import (
    REQ_REGISTER, REQ_SEND_PUBLIC_KEY, REQ_RECONNECT, REQ_SEND_FILE,
    REQ_CRC_OK, REQ_CRC_INVALID_RETRY, REQ_CRC_FAILED_ABORT,
    RESP_REG_OK, RESP_REG_FAIL, RESP_PUBKEY_AES_SENT, RESP_FILE_CRC,
    RESP_ACK, RESP_RECONNECT_AES_SENT, RESP_RECONNECT_FAIL,
    RESP_GENERIC_SERVER_ERROR
)

logger = logging.getLogger(__name__)


class RequestHandler:
    """
    Handles all client request processing for the backup server.
    
    This class contains all the request processing methods that were previously
    part of the monolithic Server class, providing better separation of concerns
    and modularity.
    """
    
    def __init__(self, server_instance):
        """
        Initialize the RequestHandler with a reference to the server instance.
        
        Args:
            server_instance: The main Server instance containing shared resources
                           (client management, database, GUI, etc.)
        """
        self.server = server_instance
        
        # Initialize file transfer manager
        from file_transfer import FileTransferManager
        self.file_transfer_manager = FileTransferManager(server_instance)
        
        # Request handler mapping - dispatches requests to appropriate handlers
        self.handler_map = {
            REQ_REGISTER: self._handle_registration,
            REQ_SEND_PUBLIC_KEY: self._handle_send_public_key,
            REQ_RECONNECT: self._handle_reconnect,
            REQ_SEND_FILE: self._handle_send_file,
            REQ_CRC_OK: self._handle_crc_ok,
            REQ_CRC_INVALID_RETRY: self._handle_crc_invalid_retry,
            REQ_CRC_FAILED_ABORT: self._handle_crc_failed_abort,
        }
        
    def process_request(self, sock: socket.socket, client_id_from_header: bytes, 
                       client: Optional[Any], code: int, payload: bytes):
        """
        Dispatches a client request to the appropriate handler method based on the request code.

        Args:
            sock: The client's socket.
            client_id_from_header: The Client ID received in the request header.
            client: The resolved Client object (None for registration requests).
            code: The request code.
            payload: The request payload.
        """
        
        handler_method = self.handler_map.get(code)

        if handler_method:
            if code == REQ_REGISTER:
                # Registration is special: client_id_from_header is all zeros, and `client` object is not yet created/resolved.
                # The handler itself will generate the new client ID and create the Client object.
                handler_method(sock, payload) 
            elif client: 
                # For all other requests, a valid `client` object (resolved by client_id_from_header) must exist.
                # The `client` object contains the authoritative client ID (client.id).
                handler_method(sock, client, payload) 
            else: 
                # This state (handler method exists, but `client` object is None for a non-registration request)
                # indicates a logic flaw in the calling sequence (e.g., _handle_client_connection did not resolve client).
                logger.critical(f"INTERNAL SERVER ERROR: Client object is None for a non-registration request (Code: {code}, Header ID: {client_id_from_header.hex()}). This should have been caught earlier.")
                self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
        else:
            # If the request code is not found in our handler_map
            client_name_for_log = client.name if client else client_id_from_header.hex()
            logger.warning(f"Unknown or unsupported request code {code} received from client '{client_name_for_log}'.")
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)

    def _handle_registration(self, sock: socket.socket, payload: bytes):
        """
        Handles client registration request (Code 1025).
        Payload: char name[255]; (null-terminated, zero-padded)
        """
        name_field_protocol_len = 255
        if len(payload) != name_field_protocol_len:
            raise ProtocolError(f"Registration Request (1025): Invalid payload size. Expected {name_field_protocol_len} bytes, got {len(payload)}.")
        
        try:
            # Parse client name from payload, enforcing max actual length and character set
            client_name = self._parse_string_from_payload(payload, name_field_protocol_len, MAX_CLIENT_NAME_LENGTH, "Client Name")
            
            with self.server.clients_lock:
                if client_name in self.server.clients_by_name:
                    logger.warning(f"Registration attempt failed: Username '{client_name}' is already registered.")
                    self._send_response(sock, RESP_REG_FAIL)
                    return
                
                # Generate a new unique client ID (UUID version 4)
                new_client_id_bytes = uuid.uuid4().bytes
                # Use the server's factory method to create a new client
                new_client = self.server.create_client(new_client_id_bytes, client_name)
                
                # Add the new client to in-memory tracking structures
                self.server.clients[new_client_id_bytes] = new_client
                self.server.clients_by_name[client_name] = new_client_id_bytes
                
                self.server._save_client_to_db(new_client)
            
            logger.info(f"Client '{client_name}' successfully registered with New Client ID: {new_client_id_bytes.hex()}.")
            
            # Update GUI with new client registration
            self.server._update_gui_client_count()
            self.server._update_gui_success(f"New client '{client_name}' registered successfully")
            
            # Send Registration Success (1600) response with the new client ID as payload
            self._send_response(sock, RESP_REG_OK, new_client_id_bytes)
        
        except ProtocolError as e:
            logger.error(f"Registration protocol error: {e}")
            self._send_response(sock, RESP_REG_FAIL)

    def _handle_send_public_key(self, sock: socket.socket, client: Any, payload: bytes):
        """
        Handles client's public key submission (Code 1026).
        Client object is already resolved by ID from request header.
        Payload: char name[255]; uint8_t public_key[160];
        """
        name_field_protocol_len = 255
        expected_payload_size = name_field_protocol_len + RSA_PUBLIC_KEY_SIZE
        if len(payload) != expected_payload_size:
            raise ProtocolError(f"SendPublicKey Request (1026): Invalid payload size. Expected {expected_payload_size} bytes, got {len(payload)}.")
        
        try:
            # Parse client name from the first part of the payload
            name_from_payload = self._parse_string_from_payload(payload, name_field_protocol_len, MAX_CLIENT_NAME_LENGTH, "Client Name")
            # Extract the public key bytes from the latter part of the payload
            public_key_bytes_from_payload = payload[name_field_protocol_len:]

            # Validate that the name in payload matches the name associated with the client ID from header
            if client.name != name_from_payload:
                logger.warning(f"SendPublicKey: Name mismatch for Client ID {client.id.hex()}. Client's known name: '{client.name}', Name in payload: '{name_from_payload}'. This indicates a protocol violation or client-side inconsistency.")
                self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
                return

            client.set_public_key(public_key_bytes_from_payload)
            
            # Generate a new AES session key for this client
            new_aes_key = get_random_bytes(AES_KEY_SIZE_BYTES)
            client.set_aes_key(new_aes_key)
            
            # Encrypt the new AES key using the client's RSA public key (PKCS1_OAEP padding)
            if not client.public_key_obj:
                raise ServerError("Internal Server Error: Client's public key object is not available for RSA encryption after an import attempt. This should not happen.")
            
            cipher_rsa = PKCS1_OAEP.new(client.public_key_obj, hashAlgo=SHA256)
            aes_key = client.get_aes_key()
            if aes_key is None:
                raise ServerError("Internal Server Error: Client's AES key is not available for encryption.")
            encrypted_aes_key = cipher_rsa.encrypt(aes_key)
            
            # Update client's record in the database (PublicKey, LastSeen, and new session AESKey)
            self.server._save_client_to_db(client)
            
            # Construct and send Response 1602 (Public Key ACK + AES Key)
            # Payload: client_id[16] (client's own ID), encrypted_aes_key[] (variable length from RSA encryption)
            response_payload = client.id + encrypted_aes_key
            self._send_response(sock, RESP_PUBKEY_AES_SENT, response_payload)
            logger.info(f"Public key successfully received and processed for client '{client.name}'. New AES session key has been sent (encrypted).")

        except (ProtocolError, ServerError, ValueError) as e:
            logger.error(f"Error processing SendPublicKey request for client '{client.name}': {e}")
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
        except Exception as e_crypto:
            logger.critical(f"Unexpected critical error during RSA encryption for client '{client.name}': {e_crypto}", exc_info=True)
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)

    def _handle_reconnect(self, sock: socket.socket, client: Any, payload: bytes):
        """
        Handles client reconnection request (Code 1027).
        Client object is already resolved by ID from request header.
        Payload: char name[255]; (null-terminated, padded)
        """
        name_field_protocol_len = 255
        if len(payload) != name_field_protocol_len:
            raise ProtocolError(f"Reconnect Request (1027): Invalid payload size. Expected {name_field_protocol_len} bytes, got {len(payload)}.")
        
        try:
            name_from_payload = self._parse_string_from_payload(payload, name_field_protocol_len, MAX_CLIENT_NAME_LENGTH, "Client Name")

            # Validate that name in payload matches the known name for this client ID
            if client.name != name_from_payload:
                logger.warning(f"Reconnect: Name mismatch for Client ID {client.id.hex()}. Client's known name: '{client.name}', Name in payload: '{name_from_payload}'. Sending Reconnect Failed response.")
                # Response Payload (1606): client_id[16] (client's ID from header, as per spec)
                self._send_response(sock, RESP_RECONNECT_FAIL, client.id)
                return
            
            # Client must have a public key on record from a previous session to encrypt a new AES key
            if not client.public_key_obj: 
                logger.warning(f"Reconnect Failed: Client '{client.name}' (ID: {client.id.hex()}) attempting to reconnect, but has no public key on record. Cannot send a new AES key.")
                self._send_response(sock, RESP_RECONNECT_FAIL, client.id)
                return

            # Generate a new AES session key for this reconnected session
            new_aes_key = get_random_bytes(AES_KEY_SIZE_BYTES)
            client.set_aes_key(new_aes_key)
            
            # Encrypt the new AES key with the client's stored public RSA key
            cipher_rsa = PKCS1_OAEP.new(client.public_key_obj, hashAlgo=SHA256)
            aes_key = client.get_aes_key()
            if aes_key is None:
                raise ServerError("Internal Server Error: Client's AES key is not available for encryption.")
            encrypted_aes_key = cipher_rsa.encrypt(aes_key)
            
            # Update client's record in the database (updates LastSeen and current session AESKey)
            self.server._save_client_to_db(client)

            # Construct and send Response 1605 (Reconnect Success + AES Key)
            # Payload: client_id[16] (client's ID), encrypted_aes_key[]
            response_payload = client.id + encrypted_aes_key
            self._send_response(sock, RESP_RECONNECT_AES_SENT, response_payload)
            logger.info(f"Client '{client.name}' reconnected successfully. A new AES session key has been sent (encrypted).")

        except ProtocolError as e:
            logger.error(f"Reconnect protocol error for client '{client.name}': {e}")
            self._send_response(sock, RESP_RECONNECT_FAIL, client.id)
        except Exception as e_reconnect:
            logger.critical(f"Unexpected critical error during reconnect process for client '{client.name}': {e_reconnect}", exc_info=True)
            self._send_response(sock, RESP_RECONNECT_FAIL, client.id)

    def _handle_send_file(self, sock: socket.socket, client: Any, payload: bytes):
        """
        Handles a file transfer packet (Code 1028) from a client.
        Manages multi-packet reassembly, decryption, CRC calculation, and storage.
        Client object is already resolved by ID from request header.

        Payload Structure:
          uint32_t encrypted_size;    // Size of 'content[]' in this specific packet
          uint32_t original_size;     // Total original (decrypted) file size
          uint16_t packet_number;     // Current packet number (1-based)
          uint16_t total_packets;     // Total number of packets for this entire file
          char     filename[255];     // Null-terminated, zero-padded filename field
          uint8_t  content[];         // Encrypted file chunk for this packet
        """
        
        logger.debug(f"File transfer request from client '{client.name}' - delegating to FileTransferManager")
        
        # Delegate to the dedicated file transfer manager
        self.file_transfer_manager.handle_send_file(sock, client, payload)

    def _handle_crc_ok(self, sock: socket.socket, client: Any, payload: bytes):
        """
        Handles client's confirmation that CRC matches (Code 1029).
        Client object is already resolved.
        Payload: char filename[255]; (null-terminated, padded)
        """
        filename_field_protocol_len = 255
        if len(payload) != filename_field_protocol_len:
            raise ProtocolError(f"CRC OK Request (1029): Invalid payload size. Expected {filename_field_protocol_len} bytes, got {len(payload)}.")
        
        try:
            # Parse filename from payload
            filename_str = self._parse_string_from_payload(payload, filename_field_protocol_len, MAX_ACTUAL_FILENAME_LENGTH, "Filename")
        except ProtocolError as e_parse:
            logger.error(f"Client '{client.name}': CRC OK request error - {e_parse}")
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
            return

        logger.info(f"Client '{client.name}' confirmed CRC OK for file '{filename_str}'. File transfer is now successfully completed and verified.")
        
        # Determine the path where the file was saved
        final_save_path = os.path.join(FILE_STORAGE_DIR, filename_str)
        file_size = os.path.getsize(final_save_path) if os.path.exists(final_save_path) else 0
        mod_time = os.path.getmtime(final_save_path) if os.path.exists(final_save_path) else 0
        mod_date = datetime.fromtimestamp(mod_time).isoformat() if mod_time else datetime.now().isoformat()

        # Update the file's record in the database to mark it as verified
        self.server.db_manager.save_file_info_to_db(client.id, filename_str, final_save_path, True, file_size, mod_date)
        
        # Send Response 1604 (General ACK)
        # Payload: client_id[16] (client's own ID)
        self._send_response(sock, RESP_ACK, client.id)

    def _handle_crc_invalid_retry(self, sock: socket.socket, client: Any, payload: bytes):
        """
        Handles client's report that CRC does not match and they will retry (Code 1030).
        Client object is already resolved.
        Payload: char filename[255]; (null-terminated, padded)
        """
        filename_field_protocol_len = 255
        if len(payload) != filename_field_protocol_len:
            raise ProtocolError(f"CRC Invalid Retry Request (1030): Invalid payload size. Expected {filename_field_protocol_len}, got {len(payload)}.")
        
        try:
            filename_str = self._parse_string_from_payload(payload, filename_field_protocol_len, MAX_ACTUAL_FILENAME_LENGTH, "Filename")
        except ProtocolError as e_parse:
            logger.error(f"Client '{client.name}': CRC Invalid Retry request error - {e_parse}")
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
            return
            
        logger.warning(f"Client '{client.name}' reported CRC invalid for file '{filename_str}'. Client will attempt to retry sending the entire file.")
        
        # Server-Side Action:
        # The file on disk (if it was saved from the previous attempt) is currently marked as unverified in the DB.
        # The client is expected to re-initiate the entire file transfer sequence (REQ_SEND_FILE from packet 1).
        # The server's in-memory partial file reassembly state for this filename (if any) was cleared
        # when the RESP_FILE_CRC was sent after the previous attempt.
        # If the file exists on disk from the failed attempt, it will be overwritten when the new transfer attempt succeeds.
        # Ensure the database record reflects the file is not verified.
        final_save_path = os.path.join(FILE_STORAGE_DIR, filename_str)
        self.server._save_file_info_to_db(client.id, filename_str, final_save_path, False)
        
        # Send Response 1604 (General ACK)
        self._send_response(sock, RESP_ACK, client.id)

    def _handle_crc_failed_abort(self, sock: socket.socket, client: Any, payload: bytes):
        """
        Handles client's report of final CRC failure and aborting transfer (Code 1031).
        Client object is already resolved.
        Payload: char filename[255]; (null-terminated, padded)
        """
        filename_field_protocol_len = 255
        if len(payload) != filename_field_protocol_len:
            raise ProtocolError(f"CRC Failed Abort Request (1031): Invalid payload size. Expected {filename_field_protocol_len}, got {len(payload)}.")
        
        try:
            filename_str = self._parse_string_from_payload(payload, filename_field_protocol_len, MAX_ACTUAL_FILENAME_LENGTH, "Filename")
        except ProtocolError as e_parse:
            logger.error(f"Client '{client.name}': CRC Failed Abort request error - {e_parse}")
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
            return

        logger.error(f"Client '{client.name}' aborted transfer for file '{filename_str}' due to final CRC mismatch. Server will delete its copy of this file.")
        final_save_path = os.path.join(FILE_STORAGE_DIR, filename_str)
        
        try:
            if os.path.exists(final_save_path):
                os.remove(final_save_path)
                logger.info(f"Successfully removed aborted file from server storage: {final_save_path}")
            else:
                logger.warning(f"Aborted file '{final_save_path}' was not found on server for deletion (Client: '{client.name}'). It might have failed saving earlier.")
        except OSError as e_os_remove:
            logger.error(f"Error occurred while attempting to remove aborted file '{final_save_path}' from storage: {e_os_remove}")
            
        # Update Database: The file is confirmed as not verified.
        # Depending on specific requirements, one might choose to delete the file record from the database entirely,
        # or simply ensure its 'Verified' status is False. The specification implies keeping a record, so update Verified status.
        self.server._save_file_info_to_db(client.id, filename_str, final_save_path, False)
        
        # Send Response 1604 (General ACK)
        self._send_response(sock, RESP_ACK, client.id)

    def _parse_string_from_payload(self, payload_bytes: bytes, field_len: int, max_actual_len: int, field_name: str = "String") -> str:
        """
        Parses a null-terminated, zero-padded string from a fixed-length field within a payload.

        Args:
            payload_bytes: The bytes containing the string field.
            field_len: The total length of the field in the protocol.
            max_actual_len: The maximum allowed actual string length.
            field_name: Name of the field for error reporting.

        Returns:
            The parsed string.

        Raises:
            ProtocolError: If the string is invalid or too long.
        """
        # Delegate to server's existing implementation
        if hasattr(self.server, '_parse_string_from_payload'):
            return self.server._parse_string_from_payload(payload_bytes, field_len, max_actual_len, field_name)
        else:
            # Fallback implementation
            if len(payload_bytes) < field_len:
                raise ProtocolError(f"{field_name}: Field is shorter than expected ({len(payload_bytes)} < {field_len})")
            
            string_field = payload_bytes[:field_len]
            null_pos = string_field.find(b'\x00')
            
            if null_pos == -1:
                # No null terminator found
                actual_string_bytes = string_field
            else:
                # Use string up to null terminator
                actual_string_bytes = string_field[:null_pos]
            
            if len(actual_string_bytes) > max_actual_len:
                raise ProtocolError(f"{field_name}: String too long ({len(actual_string_bytes)} > {max_actual_len})")
            
            try:
                return actual_string_bytes.decode('utf-8', errors='strict')
            except UnicodeDecodeError as e:
                raise ProtocolError(f"{field_name}: Invalid UTF-8 encoding: {e}")

    def _send_response(self, sock: socket.socket, code: int, payload: bytes = b''):
        """
        Constructs and sends a response to the client socket.

        Args:
            sock: The client socket to send the response to.
            code: The response code.
            payload: The response payload (bytes).

        Raises:
            TimeoutError: If a socket timeout occurs during send.
        """
        # Delegate to server's existing implementation
        if hasattr(self.server, '_send_response'):
            return self.server._send_response(sock, code, payload)
        else:
            # Fallback implementation using protocol module
            from protocol import construct_response
            
            try:
                response_data = construct_response(code, payload)
                sock.sendall(response_data)
                logger.debug(f"Sent response code {code} with {len(payload)} bytes payload")
            except socket.error as e:
                logger.error(f"Failed to send response code {code}: {e}")
                raise

    def _is_valid_filename_for_storage(self, filename_str: str) -> bool:
        """
        Validates a filename string for storage on the server.
        Checks length, allowed characters, and common OS reserved names.

        Args:
            filename_str: The filename string to validate.

        Returns:
            True if the filename is considered valid and safe for storage, False otherwise.
        """
        # Check actual length of the filename string (not the padded field size)
        if not (1 <= len(filename_str) <= MAX_ACTUAL_FILENAME_LENGTH):
            logger.debug(f"Filename validation failed for '{filename_str}': Length ({len(filename_str)}) is out of allowed range (1-{MAX_ACTUAL_FILENAME_LENGTH}).")
            return False
        
        # Disallow path traversal characters (slashes, backslashes, '..') and null bytes within the actual filename
        if '/' in filename_str or '\\' in filename_str or '..' in filename_str or '\0' in filename_str:
            logger.debug(f"Filename validation failed for '{filename_str}': Contains path traversal sequence or null characters.")
            return False
        
        # Regex for generally safe filename characters:
        # Allows alphanumeric, dots, underscores, hyphens, and spaces.
        # This can be made stricter or more lenient based on specific server OS and policies.
        if not re.match(r"^[a-zA-Z0-9._\-\s]+$", filename_str):
            logger.debug(f"Filename validation failed for '{filename_str}': Contains disallowed characters (does not match regex '^[a-zA-Z0-9._\\-\\s]+$').")
            return False
        
        # Check for names that are problematic on some operating systems (e.g., Windows reserved names like CON, PRN)
        # Comparison is case-insensitive for these reserved names.
        # We check the base name of the file (without extension) against reserved names.
        base_filename_no_ext = os.path.splitext(filename_str)[0].upper()
        reserved_os_names = {"CON", "PRN", "AUX", "NUL"} | \
                            {f"COM{i}" for i in range(1,10)} | \
                            {f"LPT{i}" for i in range(1,10)}
        if base_filename_no_ext in reserved_os_names:
             logger.debug(f"Filename validation failed for '{filename_str}': Base name '{base_filename_no_ext}' is a reserved OS name.")
             return False
        
        return True