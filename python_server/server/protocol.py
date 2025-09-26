# protocol.py
# Protocol Constants and Utilities
# Extracted from monolithic server.py for better modularity

import logging
import socket
import struct

# Import configuration constants
from .config import MAX_PAYLOAD_READ_LIMIT, SERVER_VERSION
from .exceptions import ProtocolError

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

# --- Protocol Functions ---

def parse_request_header(header_data: bytes) -> tuple[bytes, int, int, int]:
    """
    Parses the 23-byte request header.
    
    Returns:
        Tuple of (client_id, version, code, payload_size)
    """
    expected_header_len = 23
    if len(header_data) != expected_header_len:
        raise ProtocolError(f"Invalid request header length. Expected {expected_header_len}, got {len(header_data)}.")

    client_id = header_data[:16]
    version = header_data[16]
    code = struct.unpack("<H", header_data[17:19])[0]
    payload_size = struct.unpack("<I", header_data[19:23])[0]

    return client_id, version, code, payload_size

def create_response(code: int, payload: bytes = b"") -> bytes:
    """
    Constructs a complete response message to send to the client.
    """
    header = struct.pack("<BHI", SERVER_VERSION, code, len(payload))
    return header + payload

def read_exact(sock: socket.socket, num_bytes: int) -> bytes:
    """
    Reads exactly `num_bytes` from the socket.
    """
    if num_bytes < 0:
        raise ValueError("Cannot read a negative number of bytes.")
    if num_bytes == 0:
        return b''
    if num_bytes > MAX_PAYLOAD_READ_LIMIT:
        raise ProtocolError(f"Requested read of {num_bytes} bytes exceeds limit.")

    parts: list[bytes] = []
    bytes_read = 0
    while bytes_read < num_bytes:
        try:
            chunk = sock.recv(min(num_bytes - bytes_read, 4096))
        except TimeoutError as e:
            raise TimeoutError(f"Socket timeout reading {num_bytes} bytes.") from e
        except OSError as e:
            raise ConnectionError(f"Socket error during read: {e}") from e

        if not chunk:
            raise ConnectionError(f"Socket closed while reading {num_bytes} bytes.")

        parts.append(chunk)
        bytes_read += len(chunk)

    return b''.join(parts)

def validate_protocol_version(version: int) -> bool:
    """
    Validates if the client's protocol version is compatible.
    """
    return version == SERVER_VERSION
