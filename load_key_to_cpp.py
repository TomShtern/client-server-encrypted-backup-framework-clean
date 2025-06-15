#!/usr/bin/env python3
"""Convert the DER key to C++ byte array format for embedding in simple_client.cpp"""

def main():
    # Read the DER key
    with open('test_public_key.der', 'rb') as f:
        key_bytes = f.read()
    
    print(f"Key size: {len(key_bytes)} bytes")
    
    # Generate C++ byte array
    print("\nC++ byte array format:")
    print("std::vector<uint8_t> validRSAKey = {")
    
    # Format as hex bytes, 16 per line
    for i in range(0, len(key_bytes), 16):
        chunk = key_bytes[i:i+16]
        hex_values = [f"0x{b:02x}" for b in chunk]
        print("    " + ", ".join(hex_values) + ("," if i + 16 < len(key_bytes) else ""))
    
    print("};")
    
    # Also create a string literal version
    print("\nString literal format:")
    escaped_str = "".join(f"\\x{b:02x}" for b in key_bytes)
    print(f'std::string keyStr = "{escaped_str}";')
    print(f'std::vector<uint8_t> validRSAKey(keyStr.begin(), keyStr.end());')

if __name__ == "__main__":
    main()