"""
Canonical header canonicalization for the Client-Server Encrypted Backup Framework.

This module implements the exact canonicalization rules defined in the protocol
specification for consistent header processing across all components.
"""

import logging
import re
import unicodedata

from .crc import calculate_crc32

logger = logging.getLogger(__name__)


class CanonicalizeError(Exception):
    """Base exception for canonicalization errors."""

    pass


class DuplicateHeaderError(CanonicalizeError):
    """Raised when duplicate header names are detected."""

    pass


class InvalidUTF8Error(CanonicalizeError):
    """Raised when invalid UTF-8 sequences are encountered."""

    pass


class MalformedHeaderError(CanonicalizeError):
    """Raised when header format is malformed."""

    pass


def normalize_header_name(name: str) -> str:
    """
    Normalize header name according to protocol specification.

    Args:
        name: Original header name

    Returns:
        Normalized header name (lowercase, stripped)
    """
    return name.strip().lower()


def normalize_header_value(value: str) -> str:
    """
    Normalize header value according to protocol specification.

    Args:
        value: Original header value

    Returns:
        Normalized header value
    """
    # Unicode NFC normalization
    normalized = unicodedata.normalize("NFC", value)

    # Strip leading and trailing whitespace
    stripped = normalized.strip()

    # Collapse internal whitespace to single space
    collapsed = re.sub(r"\s+", " ", stripped)

    # Remove control characters except tab (which gets converted to space above)
    return re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", "", collapsed)


def parse_bhi_headers(bhi_content: str) -> dict[str, str]:
    """
    Parse BHI header content into normalized key-value pairs.

    Args:
        bhi_content: Raw BHI header content (without <bhi> tags)

    Returns:
        Dictionary of normalized headers

    Raises:
        DuplicateHeaderError: If duplicate header names are found
        MalformedHeaderError: If header format is invalid
    """
    headers = {}

    for line in bhi_content.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        if ":" not in line:
            raise MalformedHeaderError(f"Invalid header format (missing colon): {line}")

        name, value = line.split(":", 1)
        normalized_name = normalize_header_name(name)
        normalized_value = normalize_header_value(value)

        if normalized_name in headers:
            raise DuplicateHeaderError(f"Duplicate header name: {normalized_name}")

        headers[normalized_name] = normalized_value

    return headers


def canonicalize_headers_bhi(raw_input: str | bytes) -> bytes:
    """
    Canonicalize BHI headers according to protocol specification.

    This is the main canonicalization function that implements the exact
    rules defined in Shared/specs/protocol.md.

    Args:
        raw_input: Raw BHI header block as string or bytes

    Returns:
        Canonical byte sequence

    Raises:
        InvalidUTF8Error: If input contains invalid UTF-8
        DuplicateHeaderError: If duplicate headers are found
        MalformedHeaderError: If header format is invalid
    """
    # Convert to string if bytes
    if isinstance(raw_input, bytes):
        try:
            raw_input_str = raw_input.decode("utf-8")
        except UnicodeDecodeError as e:
            raise InvalidUTF8Error(f"Invalid UTF-8 sequence: {e}") from e
    else:
        raw_input_str = str(raw_input)

    # Extract content between <bhi> tags
    bhi_match = re.search(r"<bhi>\s*(.*?)\s*</bhi>", raw_input_str, re.DOTALL)
    if not bhi_match:
        raise MalformedHeaderError("Missing or malformed <bhi> tags")

    bhi_content = bhi_match[1]

    # Parse headers
    headers = parse_bhi_headers(bhi_content)

    # Build canonical format
    canonical_lines = ["<bhi>"]

    # Sort headers alphabetically by name
    canonical_lines.extend(f"{name}:{headers[name]}" for name in sorted(headers.keys()))

    canonical_lines.append("</bhi>")

    # Join with newlines and encode as UTF-8
    canonical_str = "\n".join(canonical_lines) + "\n"
    return canonical_str.encode("utf-8")


def canonicalize_and_crc(raw_input: str | bytes) -> tuple[bytes, int]:
    """
    Canonicalize headers and calculate CRC32 in one operation.

    Args:
        raw_input: Raw BHI header block

    Returns:
        Tuple of (canonical_bytes, crc32_value)
    """
    canonical_bytes = canonicalize_headers_bhi(raw_input)
    crc32_value = calculate_crc32(canonical_bytes)
    return canonical_bytes, crc32_value


def verify_canonicalization(raw_input: str | bytes, expected_crc: int) -> bool:
    """
    Verify that canonicalization produces expected CRC.

    Args:
        raw_input: Raw BHI header block
        expected_crc: Expected CRC32 value

    Returns:
        True if CRC matches, False otherwise
    """
    try:
        _, calculated_crc = canonicalize_and_crc(raw_input)
        return calculated_crc == expected_crc
    except Exception as e:
        logger.error(f"Canonicalization verification failed: {e}")
        return False


def format_timestamp_iso8601(timestamp: int | float | str) -> str:
    """
    Format timestamp in ISO 8601 format for protocol compliance.

    Args:
        timestamp: Unix timestamp, float, or existing ISO string

    Returns:
        ISO 8601 formatted timestamp string
    """
    import datetime

    if isinstance(timestamp, str):
        # Assume already formatted, validate and return
        try:
            datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return timestamp
        except ValueError as e:
            raise ValueError(f"Invalid ISO 8601 timestamp: {timestamp}") from e

    # Convert numeric timestamp to ISO 8601
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def create_bhi_headers(headers: dict[str, str | int | float]) -> str:
    """
    Create BHI header block from dictionary.

    Args:
        headers: Dictionary of header name-value pairs

    Returns:
        Formatted BHI header block string
    """
    lines = ["<bhi>"]

    for name, value in headers.items():
        # Convert non-string values
        if isinstance(value, (int, float)):
            if name.lower() == "timestamp":
                value = format_timestamp_iso8601(value)
            else:
                value = str(value)

        lines.append(f"{name}: {value}")

    lines.append("</bhi>")
    return "\n".join(lines)


class HeaderCanonicalizer:
    """
    Stateful header canonicalizer for batch processing.
    """

    def __init__(self):
        """Initialize canonicalizer."""
        self.processed_count = 0
        self.error_count = 0
        self.last_error: Exception | None = None

    def canonicalize(self, raw_input: str | bytes) -> tuple[bytes, int]:
        """
        Canonicalize headers and return canonical bytes with CRC.

        Args:
            raw_input: Raw header input

        Returns:
            Tuple of (canonical_bytes, crc32)
        """
        try:
            result = canonicalize_and_crc(raw_input)
            self.processed_count += 1
            return result
        except Exception as e:
            self.error_count += 1
            self.last_error = e
            raise

    def get_stats(self) -> dict[str, int | str | None]:
        """Get processing statistics."""
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "last_error": str(self.last_error) if self.last_error else None,
        }

    def reset_stats(self):
        """Reset processing statistics."""
        self.processed_count = 0
        self.error_count = 0
        self.last_error = None


# Convenience functions for common operations
def quick_canonicalize(headers_dict: dict[str, str | int | float]) -> bytes:
    """
    Quick canonicalization from dictionary.

    Args:
        headers_dict: Dictionary of headers

    Returns:
        Canonical bytes
    """
    bhi_str = create_bhi_headers(headers_dict)
    return canonicalize_headers_bhi(bhi_str)


def validate_header_format(raw_input: str | bytes) -> bool:
    """
    Validate header format without full canonicalization.

    Args:
        raw_input: Raw header input

    Returns:
        True if format is valid, False otherwise
    """
    try:
        canonicalize_headers_bhi(raw_input)
        return True
    except Exception:
        return False


# Legacy compatibility functions
def canonicalize_protocol_headers(raw_input: str | bytes) -> bytes:
    """
    Legacy compatibility function.

    DEPRECATED: Use canonicalize_headers_bhi() instead.
    """
    logger.warning("canonicalize_protocol_headers() is deprecated, use canonicalize_headers_bhi() instead")
    return canonicalize_headers_bhi(raw_input)
