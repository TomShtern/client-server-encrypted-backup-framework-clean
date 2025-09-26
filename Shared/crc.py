"""
Canonical CRC32 implementation for the Client-Server Encrypted Backup Framework.

This module provides a centralized, POSIX cksum-compatible CRC32 implementation
that ensures consistency across all Python components in the system.

Compatible with the C++ client implementation for cross-language consistency.
"""

import logging

logger = logging.getLogger(__name__)

# Standard POSIX cksum CRC32 table for polynomial 0x04C11DB7
_CRC32_TABLE = (
    0x00000000, 0x04c11db7, 0x09823b6e, 0x0d4326d9, 0x130476dc, 0x17c56b6b, 0x1a864db2, 0x1e475005,
    0x2608edb8, 0x22c9f00f, 0x2f8ad6d6, 0x2b4bcb61, 0x350c9b64, 0x31cd86d3, 0x3c8ea00a, 0x384fbdbd,
    0x4c11db70, 0x48d0c6c7, 0x4593e01e, 0x4152fda9, 0x5f15adac, 0x5bd4b01b, 0x569796c2, 0x52568b75,
    0x6a1936c8, 0x6ed82b7f, 0x639b0da6, 0x675a1011, 0x791d4014, 0x7ddc5da3, 0x709f7b7a, 0x745e66cd,
    0x9823b6e0, 0x9ce2ab57, 0x91a18d8e, 0x95609039, 0x8b27c03c, 0x8fe6dd8b, 0x82a5fb52, 0x8664e6e5,
    0xbe2b5b58, 0xbaea46ef, 0xb7a96036, 0xb3687d81, 0xad2f2d84, 0xa9ee3033, 0xa4ad16ea, 0xa06c0b5d,
    0xd4326d90, 0xd0f37027, 0xddb056fe, 0xd9714b49, 0xc7361b4c, 0xc3f706fb, 0xceb42022, 0xca753d95,
    0xf23c8028, 0xf6fd9d9f, 0xfbbebb46, 0xff7fa6f1, 0xe138f6f4, 0xe5f9eb43, 0xe8bacd9a, 0xec7bd02d,
    0x68ddb3f8, 0x6c1cae4f, 0x615f8896, 0x659e9521, 0x7bd9c524, 0x7f18d893, 0x725bfe4a, 0x769ae3fd,
    0x4ed55640, 0x4a144bf7, 0x47576d2e, 0x43967099, 0x5dd1209c, 0x59103d2b, 0x54531bf2, 0x50920645,
    0x246c6088, 0x20ad7d3f, 0x2dee5be6, 0x292f4651, 0x37681654, 0x33a90be3, 0x3eea2d3a, 0x3a2b308d,
    0x02648d30, 0x06a59087, 0x0be6b65e, 0x0f27abe9, 0x1160fbec, 0x15a1e65b, 0x18e2c082, 0x1c23dd35,
    0xd06f6bae, 0xd4ae7619, 0xd9ed50c0, 0xdd2c4d77, 0xc36b1d72, 0xc7aa00c5, 0xca69261c, 0xcea83bab,
    0xf6e78616, 0xf2269ba1, 0xff65bd78, 0xfba4a0cf, 0xe5e3f0ca, 0xe122ed7d, 0xec61cba4, 0xe8a0d613,
    0x9c5eb4de, 0x989fa969, 0x95dc8fb0, 0x911d9207, 0x8f5ac202, 0x8b9bdfb5, 0x86d8f96c, 0x8219e4db,
    0xba565966, 0xbe9744d1, 0xb3d46208, 0xb7157fbf, 0xa9522fba, 0xad93320d, 0xa0d014d4, 0xa4110963,
    0x1bb6d7f0, 0x1f77ca47, 0x1234ec9e, 0x16f5f129, 0x08b2a12c, 0x0c73bc9b, 0x01309a42, 0x05f187f5,
    0x3dbe3a48, 0x397f27ff, 0x343c0126, 0x30fd1c91, 0x2eba4c94, 0x2a7b5123, 0x273877fa, 0x23f96a4d,
    0x57070880, 0x53c61537, 0x5e8533ee, 0x5a442e59, 0x44037e5c, 0x40c263eb, 0x4d814532, 0x49405885,
    0x710fe538, 0x75cef88f, 0x788dde56, 0x7c4cc3e1, 0x620b93e4, 0x66ca8e53, 0x6b89a88a, 0x6f48b53d,
    0x73b6d7f8, 0x7777ca4f, 0x7a34ec96, 0x7ef5f121, 0x60b2a124, 0x6473bc93, 0x69309a4a, 0x6df187fd,
    0x55be3a40, 0x517f27f7, 0x5c3c012e, 0x58fd1c99, 0x46ba4c9c, 0x427b512b, 0x4f3877f2, 0x4bf96a45,
    0x3f070888, 0x3bc6153f, 0x368533e6, 0x32442e51, 0x2c037e54, 0x28c263e3, 0x2581453a, 0x2140588d,
    0x190fe530, 0x1dcef887, 0x108dde5e, 0x144cc3e9, 0x0a0b93ec, 0x0eca8e5b, 0x0389a882, 0x0748b535,
    0xe3a1cbc1, 0xe760d676, 0xea23f0af, 0xeee2ed18, 0xf0a5bd1d, 0xf464a0aa, 0xf9278673, 0xfde69bc4,
    0xc5a92679, 0xc1683bce, 0xcc2b1d17, 0xc8ea00a0, 0xd6ad50a5, 0xd26c4d12, 0xdf2f6bcb, 0xdbee767c,
    0xaf1014b1, 0xabd10906, 0xa6922fdf, 0xa2533268, 0xbc14626d, 0xb8d57fda, 0xb5965903, 0xb15744b4,
    0x8918f909, 0x8dd9e4be, 0x809ac267, 0x845bdfd0, 0x9a1c8fd5, 0x9edd9262, 0x939eb4bb, 0x975fa90c,
    0x8b81cb89, 0x8f40d63e, 0x8203f0e7, 0x86c2ed50, 0x9885bd55, 0x9c44a0e2, 0x9107863b, 0x95c69b8c,
    0xad892631, 0xa9483b86, 0xa40b1d5f, 0xa0ca00e8, 0xbe8d50ed, 0xba4c4d5a, 0xb70f6b83, 0xb3ce7634,
    0xc73014f9, 0xc3f1094e, 0xce922f97, 0xca533220, 0xd4146225, 0xd0d57f92, 0xdd96594b, 0xd95744fc,
    0xe118f941, 0xe5d9e4f6, 0xe89ac22f, 0xec5bdf98, 0xf21c8f9d, 0xf6dd922a, 0xfb9eb4f3, 0xff5fa944
)


def calculate_crc32(data: bytes | str) -> int:
    """
    Calculate CRC32 checksum compatible with POSIX cksum command.
    
    This is the canonical implementation that replaces all duplicate CRC
    calculations throughout the codebase.
    
    Args:
        data: Input data as bytes or string (will be encoded as UTF-8)
        
    Returns:
        32-bit CRC value as unsigned integer
        
    Raises:
        TypeError: If data is not bytes or string
        UnicodeEncodeError: If string cannot be encoded as UTF-8
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif not isinstance(data, bytes):
        raise TypeError(f"Data must be bytes or string, got {type(data)}")

    crc = 0

    # Process each byte of data
    for byte_val in data:
        crc = ((crc << 8) ^ _CRC32_TABLE[(crc >> 24) ^ byte_val]) & 0xFFFFFFFF

    # Process the length of the data (POSIX cksum requirement)
    length = len(data)
    while length:
        crc = ((crc << 8) ^ _CRC32_TABLE[(crc >> 24) ^ (length & 0xFF)]) & 0xFFFFFFFF
        length >>= 8

    # Return one's complement
    return (~crc) & 0xFFFFFFFF


class CRC32Stream:
    """
    Streaming CRC32 calculator for large files or incremental processing.
    
    Maintains state between update() calls and provides final CRC calculation
    that includes length processing.
    """

    def __init__(self):
        """Initialize streaming CRC calculator."""
        self.crc = 0
        self.total_length = 0

    def update(self, data: bytes | str) -> None:
        """
        Update CRC with new data chunk.
        
        Args:
            data: Data chunk as bytes or string
            
        Raises:
            TypeError: If data is not bytes or string
            UnicodeEncodeError: If string cannot be encoded as UTF-8
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif not isinstance(data, bytes):
            raise TypeError(f"Data must be bytes or string, got {type(data)}")

        for byte_val in data:
            self.crc = ((self.crc << 8) ^ _CRC32_TABLE[(self.crc >> 24) ^ byte_val]) & 0xFFFFFFFF

        self.total_length += len(data)

    def finalize(self) -> int:
        """
        Finalize CRC calculation including length processing.
        
        Returns:
            32-bit CRC value as unsigned integer
        """
        final_crc = self.crc
        length = self.total_length

        # Process the total length (POSIX cksum requirement)
        while length:
            final_crc = ((final_crc << 8) ^ _CRC32_TABLE[(final_crc >> 24) ^ (length & 0xFF)]) & 0xFFFFFFFF
            length >>= 8

        # Return one's complement
        return (~final_crc) & 0xFFFFFFFF

    def reset(self) -> None:
        """Reset the CRC calculator to initial state."""
        self.crc = 0
        self.total_length = 0


def verify_crc32(data: bytes | str, expected_crc: int) -> bool:
    """
    Verify data against expected CRC32 value.
    
    Args:
        data: Data to verify
        expected_crc: Expected CRC32 value
        
    Returns:
        True if CRC matches, False otherwise
    """
    calculated_crc = calculate_crc32(data)
    return calculated_crc == expected_crc


# Legacy compatibility functions for existing code
def _calculate_crc(data: bytes, crc: int = 0) -> int:
    """
    Legacy compatibility function.
    
    DEPRECATED: Use calculate_crc32() instead.
    This function is provided for backward compatibility during migration.
    """
    logger.warning("_calculate_crc() is deprecated, use calculate_crc32() instead")
    return calculate_crc32(data)


def _finalize_crc(crc: int, total_size: int) -> int:
    """
    Legacy compatibility function.
    
    DEPRECATED: Use CRC32Stream.finalize() instead.
    This function is provided for backward compatibility during migration.
    """
    logger.warning("_finalize_crc() is deprecated, use CRC32Stream instead")
    # Simulate the old finalize behavior
    final_crc = crc
    length = total_size
    while length > 0:
        final_crc = ((final_crc << 8) ^ _CRC32_TABLE[(final_crc >> 24) ^ (length & 0xFF)]) & 0xFFFFFFFF
        length >>= 8
    return (~final_crc) & 0xFFFFFFFF
