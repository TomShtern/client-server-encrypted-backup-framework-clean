# file_transfer.py
# File Transfer Manager Module for Backup Server
# Contains all file transfer operations extracted from server.py for better modularity
# Handles multi-packet file transfers, encryption/decryption, CRC validation, and file storage
#
# OVERVIEW:
# =========
# This module contains the FileTransferManager class which is the most complex and critical
# component of the backup server. It handles the complete file transfer workflow including:
#
# 1. MULTI-PACKET REASSEMBLY:
#    - Receives file chunks from clients across multiple packets
#    - Manages packet ordering and reassembly state
#    - Handles packet duplicates and missing packet scenarios
#    - Thread-safe concurrent transfers for multiple clients
#
# 2. ENCRYPTION/DECRYPTION:
#    - Decrypts received file chunks using AES-CBC with zero IV
#    - Validates encrypted content sizes and metadata
#    - Handles PKCS7 padding removal after decryption
#
# 3. CRC CALCULATION & VALIDATION:
#    - Implements POSIX cksum-compatible CRC32 algorithm
#    - Calculates checksums on decrypted file content
#    - Provides integrity verification for complete transfers
#
# 4. FILE STORAGE & SECURITY:
#    - Atomic file saving using temporary files and rename operations
#    - Comprehensive filename validation and sanitization
#    - Protection against path traversal and OS reserved names
#    - Safe handling of concurrent file operations
#
# 5. INTEGRATION POINTS:
#    - Integrates with server database for file record persistence
#    - Updates GUI with transfer progress and statistics
#    - Coordinates with client session management
#    - Provides clean interfaces for request handlers
#
# THREAD SAFETY:
# ==============
# The FileTransferManager is designed to handle concurrent file transfers safely:
# - Client-specific locks protect individual transfer states
# - Atomic file operations prevent corruption during concurrent access
# - Thread-safe integration with shared server resources
#
# USAGE:
# ======
# The FileTransferManager is instantiated by RequestHandler and called for each
# REQ_SEND_FILE request. It manages the complete workflow from packet reception
# to file storage and CRC response generation.
#
# EXTRACTED FROM:
# ===============
# This code was extracted from the monolithic server.py _handle_send_file method
# (approximately lines 990-1160 in server_backup.py) and modularized for better
# maintainability, testing, and separation of concerns.

import socket
import struct
import uuid
import os
import time
import threading
import logging
import re
from datetime import datetime
from typing import Dict, Optional, Any, Tuple

# Import crypto components through compatibility layer
from crypto_compat import AES, pad, unpad

# Import custom exceptions
from exceptions import ServerError, ProtocolError, ClientError, FileError

# Import configuration constants
from config import (
    FILE_STORAGE_DIR, MAX_FILENAME_FIELD_SIZE, MAX_ACTUAL_FILENAME_LENGTH,
    AES_KEY_SIZE_BYTES, MAX_PAYLOAD_READ_LIMIT, MAX_ORIGINAL_FILE_SIZE
)

# Import protocol constants
from protocol import RESP_FILE_CRC, RESP_GENERIC_SERVER_ERROR

logger = logging.getLogger(__name__)


class FileTransferManager:
    """
    Manages file transfer operations for the backup server.
    
    This class handles the complete file transfer workflow including:
    - Multi-packet file transfer reassembly
    - Encryption/decryption using AES
    - CRC calculation and validation
    - File storage operations
    - Thread-safe concurrent transfers
    - File validation and security checks
    """
    
    # Standard POSIX cksum CRC32 table for file integrity verification
    _CRC32_TABLE = (
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
    
    def __init__(self, server_instance):
        """
        Initialize the FileTransferManager.
        
        Args:
            server_instance: Reference to the main server instance for accessing
                           shared resources (database, GUI, client management, etc.)
        """
        self.server = server_instance
        self.transfer_lock = threading.Lock()  # Global lock for transfer operations
        self.active_transfers: Dict[str, Dict[str, Any]] = {}  # Track active transfers
        
        logger.info("FileTransferManager initialized")
    
    def handle_send_file(self, sock: socket.socket, client: Any, payload: bytes) -> None:
        """
        Handles a file transfer packet (Code 1028) from a client.
        Manages multi-packet reassembly, decryption, CRC calculation, and storage.
        
        Args:
            sock: The client's socket connection
            client: The resolved Client object containing session information
            payload: The request payload containing file transfer data
            
        Payload Structure:
          uint32_t encrypted_size;    // Size of 'content[]' in this specific packet
          uint32_t original_size;     // Total original (decrypted) file size
          uint16_t packet_number;     // Current packet number (1-based)
          uint16_t total_packets;     // Total number of packets for this entire file
          char     filename[255];     // Null-terminated, zero-padded filename field
          uint8_t  content[];         // Encrypted file chunk for this packet
        """
        try:
            # Parse and validate the file transfer metadata
            metadata = self._parse_file_transfer_metadata(payload)
            
            # Validate the filename for security and storage compatibility
            if not self._is_valid_filename_for_storage(metadata['filename']):
                raise FileError(f"Invalid or unsafe filename: '{metadata['filename']}'")
            
            # Get the client's AES key for decryption
            aes_key = client.get_aes_key()
            if not aes_key:
                raise ClientError(f"Client '{client.name}' has no active AES key for file decryption")
            
            # Log the file transfer progress
            logger.info(f"Client '{client.name}': Receiving file '{metadata['filename']}', "
                       f"Packet {metadata['packet_number']}/{metadata['total_packets']} "
                       f"(EncSize:{metadata['encrypted_size']}, OrigSize:{metadata['original_size']})")
            
            # Handle multi-packet reassembly logic
            is_complete = self._handle_packet_reassembly(client, metadata)
            
            if is_complete:
                # All packets received - process the complete file
                self._process_complete_file(sock, client, metadata['filename'], aes_key)
            
        except (ProtocolError, FileError, ClientError) as e:
            logger.error(f"File transfer error for client '{client.name}': {e}")
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
        except Exception as e:
            logger.critical(f"Unexpected error during file transfer for client '{client.name}': {e}", 
                          exc_info=True)
            self._send_response(sock, RESP_GENERIC_SERVER_ERROR)
    
    def _parse_file_transfer_metadata(self, payload: bytes) -> Dict[str, Any]:
        """
        Parses file transfer metadata from the payload.
        
        Args:
            payload: The raw payload bytes
            
        Returns:
            Dictionary containing parsed metadata
            
        Raises:
            ProtocolError: If the payload format is invalid
        """
        # Size of the metadata part of the payload (fields before the actual file content)
        metadata_header_size = 4 + 4 + 2 + 2 + MAX_FILENAME_FIELD_SIZE
        
        if len(payload) < metadata_header_size:
            raise ProtocolError(f"Payload too short for file metadata: {len(payload)} < {metadata_header_size}")
        
        # Unpack metadata fields (all little-endian)
        encrypted_size = struct.unpack("<I", payload[:4])[0]
        original_size = struct.unpack("<I", payload[4:8])[0]
        packet_number = struct.unpack("<H", payload[8:10])[0]
        total_packets = struct.unpack("<H", payload[10:12])[0]
        filename_bytes = payload[12:12 + MAX_FILENAME_FIELD_SIZE]
        
        # Validate metadata fields
        self._validate_transfer_metadata(encrypted_size, original_size, packet_number, total_packets)
        
        # Parse filename
        try:
            filename = filename_bytes.split(b'\0', 1)[0].decode('utf-8')
        except UnicodeDecodeError as e:
            raise ProtocolError("Filename field contains invalid UTF-8") from e
        
        # Extract encrypted content
        actual_content = payload[metadata_header_size:]
        if len(actual_content) != encrypted_size:
            raise ProtocolError(f"Content size mismatch: declared {encrypted_size}, actual {len(actual_content)}")
        
        return {
            'encrypted_size': encrypted_size,
            'original_size': original_size,
            'packet_number': packet_number,
            'total_packets': total_packets,
            'filename': filename,
            'filename_bytes': filename_bytes,  # Keep original for response
            'content': actual_content
        }
    
    def _validate_transfer_metadata(self, encrypted_size: int, original_size: int, 
                                   packet_number: int, total_packets: int) -> None:
        """
        Validates file transfer metadata for security and sanity.
        
        Args:
            encrypted_size: Size of encrypted content in this packet
            original_size: Total original file size
            packet_number: Current packet number
            total_packets: Total number of packets
            
        Raises:
            ProtocolError: If any metadata is invalid
        """
        if not (0 < encrypted_size <= MAX_PAYLOAD_READ_LIMIT):
            raise ProtocolError(f"Invalid encrypted_size: {encrypted_size}")
        
        if not (0 <= original_size <= MAX_ORIGINAL_FILE_SIZE):
            raise ProtocolError(f"Invalid original_size: {original_size}")
        
        if total_packets <= 0:
            raise ProtocolError(f"Invalid total_packets: {total_packets}")
        
        if not (1 <= packet_number <= total_packets):
            raise ProtocolError(f"Invalid packet_number {packet_number} for {total_packets} total packets")
    
    def _handle_packet_reassembly(self, client: Any, metadata: Dict[str, Any]) -> bool:
        """
        Handles multi-packet file reassembly logic.
        
        Args:
            client: The client object containing partial file state
            metadata: Parsed file transfer metadata
            
        Returns:
            True if all packets have been received, False otherwise
        """
        filename = metadata['filename']
        packet_number = metadata['packet_number']
        total_packets = metadata['total_packets']
        
        with client.lock:  # Thread-safe access to client's partial files
            # Initialize or validate partial file state
            if packet_number == 1:
                if filename in client.partial_files:
                    logger.warning(f"Client '{client.name}': Restarting transfer for '{filename}'")
                
                # Create new transfer state
                client.partial_files[filename] = {
                    "total_packets": total_packets,
                    "received_chunks": {},
                    "original_size": metadata['original_size'],
                    "timestamp": time.monotonic()
                }
            
            # Get current file state
            file_state = client.partial_files.get(filename)
            
            # Validate consistency for ongoing transfers
            if not file_state or (packet_number > 1 and 
                                (file_state["total_packets"] != total_packets or 
                                 file_state["original_size"] != metadata['original_size'])):
                logger.error(f"Client '{client.name}': Inconsistent metadata for '{filename}'")
                if file_state:
                    client.clear_partial_file(filename)
                raise ProtocolError("Inconsistent file transfer metadata")
            
            # Handle duplicate packets
            if packet_number in file_state["received_chunks"]:
                logger.warning(f"Client '{client.name}': Duplicate packet {packet_number} for '{filename}'")
            
            # Store the packet
            file_state["received_chunks"][packet_number] = metadata['content']
            file_state["timestamp"] = time.monotonic()
            
            # Check if transfer is complete
            return len(file_state["received_chunks"]) == total_packets
    
    def _process_complete_file(self, sock: socket.socket, client: Any, 
                              filename: str, aes_key: bytes) -> None:
        """
        Processes a complete file transfer (all packets received).
        
        Args:
            sock: Client socket for sending responses
            client: Client object
            filename: Name of the transferred file
            aes_key: AES key for decryption
        """
        with client.lock:
            file_state = client.partial_files.get(filename)
            if not file_state:
                raise ServerError(f"File state missing for complete transfer: {filename}")
            
            try:
                # Reassemble encrypted data
                full_encrypted_data = self._reassemble_encrypted_data(file_state)
                
                # Decrypt the complete file
                decrypted_data = self._decrypt_file_data(full_encrypted_data, aes_key)
                
                # Validate decrypted size
                if len(decrypted_data) != file_state["original_size"]:
                    raise FileError(f"Decrypted size mismatch for '{filename}': "
                                  f"{len(decrypted_data)} != {file_state['original_size']}")
                
                # Calculate CRC checksum
                crc_value = self._calculate_crc(decrypted_data)
                
                # Save file to storage
                final_path = self._save_file_to_storage(filename, decrypted_data)
                
                # Update database
                self.server._save_file_info_to_db(client.id, filename, final_path, False)
                
                # Update GUI statistics
                self._update_gui_stats(filename, client.name, len(decrypted_data))
                
                # Send CRC response to client
                self._send_file_crc_response(sock, client, filename, 
                                           len(full_encrypted_data), crc_value)
                
                logger.info(f"Client '{client.name}': File '{filename}' processed successfully. "
                           f"CRC: {crc_value}, Size: {len(decrypted_data)} bytes")
                
            finally:
                # Always clean up partial file state
                client.clear_partial_file(filename)
    
    def _reassemble_encrypted_data(self, file_state: Dict[str, Any]) -> bytes:
        """
        Reassembles encrypted data from all received packets.
        
        Args:
            file_state: File transfer state containing received chunks
            
        Returns:
            Complete encrypted data
            
        Raises:
            ServerError: If reassembly fails
        """
        try:
            full_encrypted_data = b''
            total_packets = file_state["total_packets"]
            
            for i in range(1, total_packets + 1):
                if i not in file_state["received_chunks"]:
                    raise ServerError(f"Missing packet {i} during reassembly")
                full_encrypted_data += file_state["received_chunks"][i]
            
            return full_encrypted_data
            
        except KeyError as e:
            raise ServerError(f"Packet reassembly failed: {e}") from e
    
    def _decrypt_file_data(self, encrypted_data: bytes, aes_key: bytes) -> bytes:
        """
        Decrypts file data using AES-CBC with zero IV.
        
        Args:
            encrypted_data: The encrypted file data
            aes_key: AES decryption key
            
        Returns:
            Decrypted file data
            
        Raises:
            FileError: If decryption fails
        """
        try:
            # AES-CBC mode with zero IV (as per protocol specification)
            cipher = AES.new(aes_key, AES.MODE_CBC, iv=b'\0' * 16)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            return decrypted_data
            
        except (ValueError, KeyError) as e:
            raise FileError(f"File decryption failed: {e}") from e
    
    def _save_file_to_storage(self, filename: str, data: bytes) -> str:
        """
        Atomically saves file data to storage.
        
        Args:
            filename: Name of the file
            data: File content to save
            
        Returns:
            Final file path
            
        Raises:
            FileError: If file save fails
        """
        # Generate temporary file path for atomic save
        temp_id = uuid.uuid4()
        temp_path = os.path.join(FILE_STORAGE_DIR, f"{filename}.{temp_id}.tmp_EncryptedBackup")
        final_path = os.path.join(FILE_STORAGE_DIR, filename)
        
        try:
            # Write to temporary file first
            with open(temp_path, 'wb') as f:
                f.write(data)
            
            # Remove existing file if it exists (Windows compatibility)
            if os.path.exists(final_path):
                os.remove(final_path)
                logger.debug(f"Removed existing file '{final_path}' before saving new version")
            
            # Atomically rename to final path
            os.rename(temp_path, final_path)
            logger.info(f"File '{filename}' saved to storage: '{final_path}'")
            
            return final_path
            
        except OSError as e:
            # Cleanup temporary file on error
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise FileError(f"Failed to save file '{filename}': {e}") from e
    
    def _send_file_crc_response(self, sock: socket.socket, client: Any, 
                               filename: str, encrypted_size: int, crc_value: int) -> None:
        """
        Sends file CRC response to client.
        
        Args:
            sock: Client socket
            client: Client object
            filename: Filename
            encrypted_size: Total encrypted file size
            crc_value: Calculated CRC value
        """
        # Prepare filename bytes (padded to 255 bytes)
        filename_bytes = filename.encode('utf-8')
        if len(filename_bytes) > MAX_ACTUAL_FILENAME_LENGTH:
            filename_bytes = filename_bytes[:MAX_ACTUAL_FILENAME_LENGTH]
        
        filename_padded = filename_bytes + b'\0' * (MAX_FILENAME_FIELD_SIZE - len(filename_bytes))
        
        # Construct response payload
        # Payload: client_id[16], encrypted_size[4], filename[255], crc[4]
        response_payload = (client.id + 
                          struct.pack("<I", encrypted_size) + 
                          filename_padded + 
                          struct.pack("<I", crc_value))
        
        self._send_response(sock, RESP_FILE_CRC, response_payload)
        logger.info(f"Client '{client.name}': Sent CRC response for '{filename}' (CRC: {crc_value})")
    
    def _calculate_crc(self, data: bytes) -> int:
        """
        Calculates a CRC32 checksum compatible with the Linux 'cksum' command.
        
        Args:
            data: Input bytes for CRC calculation
            
        Returns:
            32-bit CRC value
        """
        crc = 0
        
        # Process each byte of data
        for byte_val in data:
            crc = (self._CRC32_TABLE[(crc >> 24) ^ byte_val] ^ (crc << 8)) & 0xFFFFFFFF
        
        # Process the length of the data
        length = len(data)
        while length:
            crc = (self._CRC32_TABLE[(crc >> 24) ^ (length & 0xFF)] ^ (crc << 8)) & 0xFFFFFFFF
            length >>= 8
        
        # Return one's complement
        return (~crc) & 0xFFFFFFFF
    
    def _is_valid_filename_for_storage(self, filename: str) -> bool:
        """
        Validates a filename for secure storage.
        
        Args:
            filename: The filename to validate
            
        Returns:
            True if filename is valid and safe
        """
        # Check length
        if not (1 <= len(filename) <= MAX_ACTUAL_FILENAME_LENGTH):
            logger.debug(f"Filename validation failed: invalid length {len(filename)}")
            return False
        
        # Prevent path traversal
        if ('/' in filename or '\\' in filename or 
            '..' in filename or '\0' in filename):
            logger.debug(f"Filename validation failed: contains path traversal chars")
            return False
        
        # Check for safe characters only
        if not re.match(r"^[a-zA-Z0-9._\-\s]+$", filename):
            logger.debug(f"Filename validation failed: contains unsafe characters")
            return False
        
        # Check for OS reserved names
        base_name = os.path.splitext(filename)[0].upper()
        reserved_names = {"CON", "PRN", "AUX", "NUL"} | \
                        {f"COM{i}" for i in range(1, 10)} | \
                        {f"LPT{i}" for i in range(1, 10)}
        
        if base_name in reserved_names:
            logger.debug(f"Filename validation failed: reserved OS name '{base_name}'")
            return False
        
        return True
    
    def _update_gui_stats(self, filename: str, client_name: str, bytes_transferred: int) -> None:
        """
        Updates GUI with transfer statistics.
        
        Args:
            filename: Name of transferred file
            client_name: Name of client
            bytes_transferred: Number of bytes transferred
        """
        if hasattr(self.server, '_update_gui_transfer_stats'):
            self.server._update_gui_transfer_stats(bytes_transferred=bytes_transferred)
        
        if hasattr(self.server, '_update_gui_success'):
            self.server._update_gui_success(f"File '{filename}' received from '{client_name}'")
    
    def _send_response(self, sock: socket.socket, code: int, payload: bytes = b'') -> None:
        """
        Sends a response to the client.
        
        Args:
            sock: Client socket
            code: Response code
            payload: Response payload
        """
        # Delegate to server's response handler
        if hasattr(self.server, '_send_response'):
            self.server._send_response(sock, code, payload)
        else:
            # Fallback implementation
            from protocol import construct_response
            try:
                response_data = construct_response(code, payload)
                sock.sendall(response_data)
                logger.debug(f"Sent response code {code} with {len(payload)} bytes payload")
            except socket.error as e:
                logger.error(f"Failed to send response code {code}: {e}")
                raise
    
    def cleanup_stale_transfers(self, timeout_seconds: int = 900) -> int:
        """
        Cleans up stale file transfers that have been inactive.
        
        Args:
            timeout_seconds: Timeout in seconds for considering transfers stale
            
        Returns:
            Number of transfers cleaned up
        """
        cleaned_count = 0
        current_time = time.monotonic()
        
        with self.transfer_lock:
            # This would be used if we maintained global transfer state
            # For now, individual clients handle their own cleanup
            pass
        
        return cleaned_count
    
    def get_transfer_statistics(self) -> Dict[str, Any]:
        """
        Gets current transfer statistics.
        
        Returns:
            Dictionary containing transfer statistics
        """
        with self.transfer_lock:
            return {
                'active_transfers': len(self.active_transfers),
                'last_activity': datetime.now().isoformat()
            }