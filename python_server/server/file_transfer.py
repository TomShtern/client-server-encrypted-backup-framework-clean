"""
FILE TRANSFER MANAGER - MULTI-PACKET FILE TRANSFER ENGINE
==========================================================

PURPOSE: Handles complete file transfer workflow - packet reassembly, decryption, validation, storage.
USED BY: RequestHandler for each REQ_SEND_FILE request.
THREADSAFE: Supports concurrent transfers across multiple clients.

WORKFLOW:
1. Receive multi-packet encrypted file data from clients
2. Reassemble packets in correct order with duplicate detection
3. Decrypt using AES-256-CBC, validate content integrity
4. Calculate CRC32 checksum using centralized crc_utils
5. Store files atomically with validation and security checks
6. Update database records and send CRC response to client

KEY DEPENDENCIES:
- server.crc_utils.calculate_crc32() for checksum calculation
- server.network_server.send_response() for client responses
- server.db_manager for file record persistence

SECURITY FEATURES:
- Filename validation and sanitization
- Path traversal protection
- Atomic file operations
- Concurrent access safety

NOTE: CRC calculation now uses centralized crc_utils module (no local implementation).
"""

import contextlib
import logging
import os
import re
import socket
import struct
import threading
import time
import uuid
from datetime import datetime
from typing import Any

# Import observability components
from Shared.observability import get_metrics_collector

# Import crypto components through compatibility layer
# Import configuration constants
from .config import (
    FILE_STORAGE_DIR,
    MAX_ACTUAL_FILENAME_LENGTH,
    MAX_FILENAME_FIELD_SIZE,
    MAX_ORIGINAL_FILE_SIZE,
    MAX_PAYLOAD_READ_LIMIT,
)

# Import custom exceptions
from .exceptions import ClientError, FileError, ProtocolError, ServerError

# Import protocol constants
from .protocol import RESP_FILE_CRC, RESP_GENERIC_SERVER_ERROR
from .crc_utils import calculate_crc32  # Centralized CRC calculation

logger = logging.getLogger(__name__)

# Module version tag for runtime verification in logs
__FTM_VERSION__ = "2025-08-06a"


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

    def __init__(self, server_instance: Any) -> None:
        """
        Initialize the FileTransferManager.

        Args:
            server_instance: Reference to the main server instance for accessing
                           shared resources (database, GUI, client management, etc.)
        """
        self.server = server_instance
        self.transfer_lock = threading.Lock()  # Global lock for transfer operations
        self.active_transfers: dict[str, dict[str, Any]] = {}  # Track active transfers
        self.version = __FTM_VERSION__

        logger.info(f"FileTransferManager initialized (version={__FTM_VERSION__})")

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
        # High-signal pre-parse log
        with contextlib.suppress(Exception):
            # Do not let logging failures impact flow
            logger.debug(
                f"XFER/PARSE: client='{client.name}', payload_len={len(payload)}"
            )

        try:
            self._process_file_transfer_packet(payload, client, sock)  # type: ignore
        except (ProtocolError, FileError, ClientError) as e:
            logger.error(f"File transfer error for client '{client.name}': {e}")
            self.server.network_server.send_response(sock, RESP_GENERIC_SERVER_ERROR)
        except Exception as e:
            logger.critical(f"Unexpected error during file transfer for client '{client.name}': {e}",
                          exc_info=True)
            self.server.network_server.send_response(sock, RESP_GENERIC_SERVER_ERROR)

    def _process_file_transfer_packet(self, payload, client, sock):
        # Parse and validate the file transfer metadata
        metadata = self._parse_file_transfer_metadata(payload)

        # Validate the filename for security and storage compatibility
        if not self._is_valid_filename_for_storage(metadata['filename']):
            raise FileError(f"Invalid or unsafe filename: '{metadata['filename']}'")

        # Get the client's AES key for decryption
        aes_key = client.get_aes_key()  # type: ignore
        if not aes_key:
            raise ClientError(f"Client '{client.name}' has no active AES key for file decryption")  # type: ignore

        # Log the file transfer progress with enhanced debugging
        logger.info(f"Client '{client.name}': Receiving file '{metadata['filename']}', "  # type: ignore
                   f"Packet {metadata['packet_number']}/{metadata['total_packets']} "
                   f"(EncSize:{metadata['encrypted_size']}, OrigSize:{metadata['original_size']})")

        # Enhanced logging for multi-packet transfers
        if metadata['total_packets'] > 1:
            logger.debug(f"Multi-packet transfer: Client '{client.name}', File '{metadata['filename']}', "  # type: ignore
                       f"Packet {metadata['packet_number']}/{metadata['total_packets']}, "
                       f"Content size: {len(metadata['content'])} bytes")

        # Handle multi-packet reassembly logic
        is_complete = self._handle_packet_reassembly(client, metadata)

        # Log reassembly status
        if metadata['total_packets'] > 1:
            logger.debug(f"Reassembly status: Client '{client.name}', File '{metadata['filename']}', "  # type: ignore
                       f"Packet {metadata['packet_number']}/{metadata['total_packets']}, "
                       f"Complete: {is_complete}")

        if is_complete:
            # All packets received - process the complete file
            logger.debug(f"COMPLETE TRANSFER: Processing complete file '{metadata['filename']}' for client '{client.name}'")  # type: ignore
            self._process_complete_file(sock, client, metadata['filename'], aes_key)

    def _parse_file_transfer_metadata(self, payload: bytes) -> dict[str, Any]:
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
            logger.error(
                f"XFER/PARSE_ERR: payload_too_short payload_len={len(payload)} expected_at_least={metadata_header_size}"
            )
            raise ProtocolError(f"Payload too short for file metadata: {len(payload)} < {metadata_header_size}")

        # Unpack metadata fields (all little-endian)
        encrypted_size = struct.unpack("<I", payload[:4])[0]
        original_size = struct.unpack("<I", payload[4:8])[0]
        packet_number = struct.unpack("<H", payload[8:10])[0]
        total_packets = struct.unpack("<H", payload[10:12])[0]
        filename_bytes = payload[12:12 + MAX_FILENAME_FIELD_SIZE]

        # Validate metadata fields
        logger.debug(
            f"XFER/PARSE: hdr enc_size={encrypted_size}, orig_size={original_size}, pkt={packet_number}, total={total_packets}"
        )
        self._validate_transfer_metadata(encrypted_size, original_size, packet_number, total_packets)

        # Parse filename
        try:
            filename = filename_bytes.split(b'\0', 1)[0].decode('utf-8')
        except UnicodeDecodeError as e:
            raise ProtocolError("Filename field contains invalid UTF-8") from e

        # Extract encrypted content
        actual_content = payload[metadata_header_size:]
        if len(actual_content) != encrypted_size:
            logger.error(
                f"XFER/PARSE_ERR: content_len_mismatch declared={encrypted_size} actual={len(actual_content)} "
                f"pkt={packet_number}/{total_packets}"
            )
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
            logger.error(f"XFER/VALIDATE_ERR: invalid_encrypted_size value={encrypted_size}")
            raise ProtocolError(f"Invalid encrypted_size: {encrypted_size}")

        if not (0 <= original_size <= MAX_ORIGINAL_FILE_SIZE):
            logger.error(f"XFER/VALIDATE_ERR: invalid_original_size value={original_size}")
            raise ProtocolError(f"Invalid original_size: {original_size}")

        if total_packets <= 0:
            logger.error(f"XFER/VALIDATE_ERR: invalid_total_packets value={total_packets}")
            raise ProtocolError(f"Invalid total_packets: {total_packets}")

        if not (1 <= packet_number <= total_packets):
            logger.error(
                f"XFER/VALIDATE_ERR: invalid_packet_number pkt={packet_number} total={total_packets}"
            )
            raise ProtocolError(f"Invalid packet_number {packet_number} for {total_packets} total packets")

    def _handle_packet_reassembly(self, client: Any, metadata: dict[str, Any]) -> bool:
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
                logger.warning(
                    f"XFER/REASM_WARN: duplicate_packet client='{client.name}', file='{filename}', pkt={packet_number}"
                )

            # Store the packet
            file_state["received_chunks"][packet_number] = metadata['content']
            file_state["timestamp"] = time.monotonic()

            # Emit concise state snapshot
            with contextlib.suppress(Exception):
                received_count = len(file_state["received_chunks"])
                # For efficiency, only compute cumulative bytes for small N
                cumulative_enc = sum(len(ch) for ch in file_state["received_chunks"].values()) if received_count <= 64 else -1
                logger.debug(
                    f"XFER/REASM_STATE: client='{client.name}', file='{filename}', received={received_count}/{total_packets}, "
                    f"cum_enc_bytes={cumulative_enc if cumulative_enc >= 0 else 'skipped'}"
                )

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
        # Start timing the complete file processing operation
        processing_start = time.time()

        with client.lock:
            file_state = client.partial_files.get(filename)
            if not file_state:
                raise ServerError(f"File state missing for complete transfer: {filename}")

            try:
                # Reassemble encrypted data
                full_encrypted_data = self._reassemble_encrypted_data(file_state)
                logger.info(
                    f"XFER/FINAL: client='{client.name}', file='{filename}', total_packets={file_state['total_packets']}, "
                    f"assembled_enc_size={len(full_encrypted_data)}"
                )

                # Decrypt the complete file
                decrypt_start = time.perf_counter()
                decrypted_data = self._decrypt_file_data(full_encrypted_data, aes_key)
                decrypt_ms = int((time.perf_counter() - decrypt_start) * 1000)
                logger.info(
                    f"XFER/FINAL: client='{client.name}', file='{filename}', decrypted_size={len(decrypted_data)}, "
                    f"expected_orig_size={file_state['original_size']}, decrypt_ms={decrypt_ms}"
                )

                # Validate decrypted size
                if len(decrypted_data) != file_state["original_size"]:
                    raise FileError(f"Decrypted size mismatch for '{filename}': "
                                  f"{len(decrypted_data)} != {file_state['original_size']}")

                # Calculate CRC checksum
                crc_value = calculate_crc32(decrypted_data)
                logger.debug(
                    f"XFER/FINAL: client='{client.name}', file='{filename}', crc=0x{crc_value:08x}"
                )

                # Save file to storage
                final_path, mod_date = self._save_file_to_storage(filename, decrypted_data)

                # Update database
                self.server.db_manager.save_file_info_to_db(client.id, filename, final_path, False, len(decrypted_data), mod_date, crc_value)

                # Update GUI statistics
                self._update_gui_stats(filename, client.name, len(decrypted_data))

                # Send CRC response to client
                self._send_file_crc_response(sock, client, filename,
                                           len(full_encrypted_data), crc_value)

                logger.info(f"Client '{client.name}': File '{filename}' processed successfully. "
                           f"CRC: {crc_value}, Size: {len(decrypted_data)} bytes")

                # Record metrics for successful file upload
                processing_duration_ms = (time.time() - processing_start) * 1000
                size_mb = len(decrypted_data) / (1024 * 1024)
                get_metrics_collector().record_counter("file.uploads.total",
                                                      tags={'client_id': client.id.hex()})
                get_metrics_collector().record_timer("file.upload.duration",
                                                    processing_duration_ms,
                                                    tags={'size_mb': f'{size_mb:.2f}'})

            finally:
                # Always clean up partial file state
                client.clear_partial_file(filename)

    def _reassemble_encrypted_data(self, file_state: dict[str, Any]) -> bytes:
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
                    logger.error(f"XFER/REASM_ERR: missing_packet index={i} of {total_packets}")
                    raise ServerError(f"Missing packet {i} during reassembly")
                full_encrypted_data += file_state["received_chunks"][i]

            logger.debug(
                f"XFER/REASM_OK: assembled_bytes={len(full_encrypted_data)} from {total_packets} packets"
            )

            return full_encrypted_data

        except KeyError as e:
            logger.error(f"XFER/REASM_ERR: key_error detail={e}")
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
            logger.debug(f"XFER/DECRYPT: enc_size={len(encrypted_data)}")
            # AES-CBC mode with zero IV (as per protocol specification)
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            cipher = AES.new(aes_key, AES.MODE_CBC, iv=b'\0' * 16)  # type: ignore
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            logger.debug(f"XFER/DECRYPT_OK: dec_size={len(decrypted_data)}")
            return decrypted_data

        except (ValueError, KeyError) as e:
            logger.error(f"XFER/DECRYPT_ERR: detail={e}")
            raise FileError(f"File decryption failed: {e}") from e

    def _save_file_to_storage(self, filename: str, data: bytes) -> tuple[str, str]:
        """
        Atomically saves file data to storage.

        Args:
            filename: Name of the file
            data: File content to save

        Returns:
            A tuple containing the final file path and the modification date as an ISO 8601 string.

        Raises:
            FileError: If file save fails
        """
        # Generate temporary file path for atomic save
        temp_id = uuid.uuid4()
        temp_path = os.path.join(FILE_STORAGE_DIR, f"{filename}.{temp_id}.tmp_EncryptedBackup")
        final_path = os.path.join(FILE_STORAGE_DIR, filename)

        try:
            return self._perform_atomic_file_save(
                temp_path, data, final_path, filename
            )
        except OSError as e:
            # Cleanup temporary file on error
            if os.path.exists(temp_path):
                with contextlib.suppress(OSError):
                    os.remove(temp_path)
            raise FileError(f"Failed to save file '{filename}': {e}") from e

    def _perform_atomic_file_save(self, temp_path: str, data: bytes,
                                 final_path: str, filename: str) -> tuple[str, str]:
        """
        Performs atomic file save operation.

        Args:
            temp_path: Path to temporary file
            data: File data to write
            final_path: Final destination path
            filename: Name of the file

        Returns:
            Tuple of (final_path, mod_date)
        """
        # Ensure storage directory exists (defensive; server should already create it)
        os.makedirs(FILE_STORAGE_DIR, exist_ok=True)
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

        mod_time = os.path.getmtime(final_path)
        mod_date = datetime.fromtimestamp(mod_time).isoformat()

        return final_path, mod_date

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

        self.server.network_server.send_response(sock, RESP_FILE_CRC, response_payload)
        logger.info(f"Client '{client.name}': Sent CRC response for '{filename}' (CRC: {crc_value})")

    
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
            logger.debug("Filename validation failed: contains path traversal chars")
            return False

        # Check for safe characters only
        # Allow common punctuation often present in user filenames: space, dot, underscore, dash,
        # ampersand, hash, parentheses, plus, comma
        if not re.match(r"^[a-zA-Z0-9._\-\s&#()+,]+$", filename):
            logger.debug("Filename validation failed: contains unsafe characters")
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
        # GUI notifications removed - FletV2 GUI gets file transfer data through ServerBridge

    
    def cleanup_stale_transfers(self, timeout_seconds: int = 900) -> int:
        _ = timeout_seconds  # Currently unused but preserved for API compatibility
        """
        Cleans up stale file transfers that have been inactive.

        Args:
            timeout_seconds: Timeout in seconds for considering transfers stale

        Returns:
            Number of transfers cleaned up
        """
        _ = time.monotonic()  # Reserved for future stale transfer detection

        with self.transfer_lock:
            # This would be used if we maintained global transfer state
            # For now, individual clients handle their own cleanup
            pass

        return 0  # Inline the immediately returned variable

    def get_transfer_statistics(self) -> dict[str, Any]:
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
