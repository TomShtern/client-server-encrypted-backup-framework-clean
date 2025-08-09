# protocol.py
# Protocol Constants and Utilities
# Extracted from monolithic server.py for better modularity

import struct
import logging
from typing import Tuple, Optional

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

logger = logging.getLogger(__name__)

def parse_request_header(data: bytes) -> Tuple[bytes, int, int]:
    """
    Parses a request header from the client.
    
    Args:
        data: Raw header data (first 23 bytes)
        
    Returns:
        Tuple of (client_id, version, code)
        
    Raises:
        struct.error: If header format is invalid
    """
    if len(data) < 23:
        raise ValueError(f"Header too short: expected 23 bytes, got {len(data)}")
    
    client_id = data[:16]  # 16-byte UUID
    version, code = struct.unpack('<BI', data[16:23])  # 1 byte version, 4 bytes code (little-endian)
    
    logger.debug(f"Parsed header - Client ID: {client_id.hex()}, Version: {version}, Code: {code}")
    return client_id, version, code

def construct_response(code: int, payload: bytes = b"") -> bytes:
    """
    Constructs a response message to send to the client.
    
    Args:
        code: Response code
        payload: Optional payload data
        
    Returns:
        Complete response message as bytes
    """
    from .config import SERVER_VERSION
    
    # Response format: 1 byte version + 2 bytes code + 4 bytes payload size + payload
    payload_size = len(payload)
    header = struct.pack('<BHI', SERVER_VERSION, code, payload_size)
    response = header + payload
    
    logger.debug(f"Constructed response - Code: {code}, Payload size: {payload_size}")
    return response

def extract_null_terminated_string(data: bytes, max_length: int) -> str:
    """
    Extracts a null-terminated string from a fixed-size byte field.
    
    Args:
        data: The byte data containing the string
        max_length: Maximum expected length of the field
        
    Returns:
        Decoded string (without null terminator)
        
    Raises:
        ValueError: If data is too long or contains invalid characters
    """
    if len(data) > max_length:
        raise ValueError(f"String field too long: {len(data)} > {max_length}")
    
    # Find null terminator
    null_pos = data.find(b'\x00')
    if null_pos == -1:
        # No null terminator found, use entire data
        string_bytes = data
    else:
        # Use data up to null terminator
        string_bytes = data[:null_pos]
    
    try:
        # Decode as UTF-8
        decoded_string = string_bytes.decode('utf-8', errors='strict')
        logger.debug(f"Extracted string: '{decoded_string}' from {len(data)}-byte field")
        return decoded_string
    except UnicodeDecodeError as e:
        logger.error(f"Failed to decode string from bytes {string_bytes.hex()}: {e}")
        raise ValueError(f"Invalid UTF-8 encoding in string field: {e}")

def validate_protocol_version(version: int) -> bool:
    """
    Validates that the client protocol version is compatible.
    
    Args:
        version: Client protocol version
        
    Returns:
        True if version is compatible, False otherwise
    """
    from .config import SERVER_VERSION
    
    # Flexible version compatibility checking (fixes rigid version issue from CLAUDE.md)
    from .config import (
        SERVER_VERSION, MIN_SUPPORTED_CLIENT_VERSION, MAX_SUPPORTED_CLIENT_VERSION,
        COMPATIBLE_VERSIONS, ALLOW_BACKWARD_COMPATIBILITY, VERSION_TOLERANCE_ENABLED
    )
    
    # If version tolerance is disabled, fall back to exact match
    if not VERSION_TOLERANCE_ENABLED:
        is_compatible = version == SERVER_VERSION
        if not is_compatible:
            logger.warning(f"Protocol version mismatch (strict mode): client version {version}, server version {SERVER_VERSION}")
        return is_compatible
    
    # Check if version is in explicitly compatible versions list
    if version in COMPATIBLE_VERSIONS:
        logger.debug(f"Client version {version} found in compatible versions list")
        return True
    
    # Check if version is within supported range
    if MIN_SUPPORTED_CLIENT_VERSION <= version <= MAX_SUPPORTED_CLIENT_VERSION:
        logger.debug(f"Client version {version} within supported range [{MIN_SUPPORTED_CLIENT_VERSION}-{MAX_SUPPORTED_CLIENT_VERSION}]")
        return True
    
    # Check backward compatibility
    if ALLOW_BACKWARD_COMPATIBILITY and version < SERVER_VERSION:
        # Allow clients that are at most 1 version behind for backward compatibility
        if version >= (SERVER_VERSION - 1) and version >= MIN_SUPPORTED_CLIENT_VERSION:
            logger.info(f"Allowing backward compatible client version {version} (server version {SERVER_VERSION})")
            return True
    
    # Check forward compatibility (allowing newer clients)
    if version > SERVER_VERSION and version <= MAX_SUPPORTED_CLIENT_VERSION:
        logger.info(f"Allowing forward compatible client version {version} (server version {SERVER_VERSION})")
        return True
    
    # Version not compatible
    logger.warning(f"Protocol version incompatible: client version {version}, server version {SERVER_VERSION}")
    logger.warning(f"Supported range: [{MIN_SUPPORTED_CLIENT_VERSION}-{MAX_SUPPORTED_CLIENT_VERSION}], Compatible versions: {COMPATIBLE_VERSIONS}")
    
    return False

def validate_request_code(code: int) -> bool:
    """
    Validates that the request code is recognized.
    
    Args:
        code: Request code from client
        
    Returns:
        True if code is valid, False otherwise
    """
    valid_codes = {
        REQ_REGISTER,
        REQ_SEND_PUBLIC_KEY,
        REQ_RECONNECT,
        REQ_SEND_FILE,
        REQ_CRC_OK,
        REQ_CRC_INVALID_RETRY,
        REQ_CRC_FAILED_ABORT
    }
    
    is_valid = code in valid_codes
    
    if not is_valid:
        logger.warning(f"Invalid request code received: {code}")
    
    return is_valid