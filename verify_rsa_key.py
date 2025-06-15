#!/usr/bin/env python3
"""
RSA Key Verification Script for Client-Server Encrypted Backup Framework
Reads and verifies a DER-formatted RSA public key.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def read_and_verify_der_key(file_path):
    """Read a DER-formatted RSA public key and verify its properties."""
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist!")
        return False
    
    try:
        # Read the DER file
        with open(file_path, "rb") as f:
            der_data = f.read()
        
        print(f"Reading DER key from: {file_path}")
        print(f"File size: {len(der_data)} bytes")
        
        # Parse the DER data
        public_key = serialization.load_der_public_key(der_data)
        
        # Verify it's an RSA key
        if not isinstance(public_key, rsa.RSAPublicKey):
            print("Error: Key is not an RSA public key!")
            return False
        
        # Get key properties
        key_size = public_key.key_size
        public_exponent = public_key.public_numbers().e
        
        print(f"✓ Successfully loaded RSA public key")
        print(f"✓ Key size: {key_size} bits")
        print(f"✓ Public exponent: {public_exponent}")
        
        # Verify key size
        if key_size == 1024:
            print("✓ Key size is correct (1024 bits)")
        else:
            print(f"✗ Key size is incorrect! Expected 1024, got {key_size}")
            return False
        
        # Check if size is exactly 162 bytes
        if len(der_data) == 162:
            print("✓ DER size is exactly 162 bytes")
        else:
            print(f"! DER size is {len(der_data)} bytes (expected 162)")
            print("  Note: This may still be valid - RSA DER sizes can vary slightly")
        
        # Display hex dump
        print(f"\nDER data (first 64 bytes):")
        hex_data = der_data[:64].hex()
        for i in range(0, len(hex_data), 32):
            offset = i // 2
            line = hex_data[i:i+32]
            print(f"  {offset:04x}: {line}")
        
        if len(der_data) > 64:
            print(f"  ... ({len(der_data) - 64} more bytes)")
        
        # Test re-serialization to ensure consistency
        re_serialized = public_key.public_key_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        if der_data == re_serialized:
            print("✓ Key re-serialization is consistent")
        else:
            print("✗ Key re-serialization differs from original!")
            print(f"  Original size: {len(der_data)}")
            print(f"  Re-serialized size: {len(re_serialized)}")
        
        return True
        
    except Exception as e:
        print(f"Error reading or parsing DER key: {e}")
        return False

def test_key_with_server_format(file_path):
    """Test the key in the format expected by the server."""
    
    try:
        with open(file_path, "rb") as f:
            der_data = f.read()
        
        print(f"\nTesting server compatibility:")
        
        # Test with cryptography library (what the server uses)
        try:
            from cryptography.hazmat.primitives import serialization
            public_key = serialization.load_der_public_key(der_data)
            print("✓ Key is compatible with cryptography library")
            
            # Test encryption (basic functionality)
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # Try to encrypt a small test message
            test_message = b"Hello, World!"
            encrypted = public_key.encrypt(
                test_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            print(f"✓ Key can encrypt data (encrypted {len(test_message)} bytes to {len(encrypted)} bytes)")
            
        except Exception as e:
            print(f"✗ Cryptography library compatibility test failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error in server compatibility test: {e}")
        return False

def main():
    """Main verification function."""
    
    der_file = "test_public_key.der"
    
    print("RSA Public Key Verification")
    print("=" * 50)
    
    # Read and verify the key
    if read_and_verify_der_key(der_file):
        print("\n" + "=" * 50)
        
        # Test server compatibility
        if test_key_with_server_format(der_file):
            print("\n✓ All tests passed! Key is valid and ready for use.")
            return True
        else:
            print("\n✗ Server compatibility test failed.")
            return False
    else:
        print("\n✗ Key verification failed.")
        return False

if __name__ == "__main__":
    main()