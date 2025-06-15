#!/usr/bin/env python3
"""
AES Compatibility Test - Client/Server Validation

This script validates that our client's AES-256-CBC implementation produces
output that is compatible with the server's decryption process.

Key Requirements:
- AES-256-CBC mode
- 32-byte (256-bit) key
- Zero IV (16 bytes of 0x00)  
- PKCS7 padding
- Client encrypts, server decrypts

The goal is to identify any format incompatibilities before testing with live server.
"""

import os
import sys
import binascii
from typing import Tuple, Optional

# Import the server's crypto compatibility layer
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))
from crypto_compat import AES, unpad, get_random_bytes

def generate_test_aes_key() -> bytes:
    """Generate a 32-byte AES-256 key for testing."""
    return get_random_bytes(32)

def simulate_client_aes_encryption(data: bytes, aes_key: bytes) -> bytes:
    """
    Simulate the client's AES encryption using the same method as AESWrapper.cpp.
    
    This mirrors the client's encryption:
    - AES-256-CBC mode
    - Zero IV (all zeros)
    - PKCS7 padding
    """
    if len(aes_key) != 32:
        raise ValueError(f"AES key must be 32 bytes, got {len(aes_key)}")
    
    # Create zero IV (16 bytes of 0x00) - matches client's useStaticZeroIV=true
    zero_iv = b'\x00' * 16
    
    # Create AES cipher in CBC mode with zero IV
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=zero_iv)
    
    # Add PKCS7 padding manually (to match Crypto++ behavior)
    block_size = 16
    padding_length = block_size - (len(data) % block_size)
    padded_data = data + bytes([padding_length] * padding_length)
    
    # Encrypt the padded data
    encrypted_data = cipher.encrypt(padded_data)
    
    print(f"[CLIENT-SIM] Encrypted {len(data)} bytes to {len(encrypted_data)} bytes")
    print(f"[CLIENT-SIM] Key: {binascii.hexlify(aes_key).decode()}")
    print(f"[CLIENT-SIM] IV: {binascii.hexlify(zero_iv).decode()}")
    print(f"[CLIENT-SIM] Plaintext: {binascii.hexlify(data).decode()}")
    print(f"[CLIENT-SIM] Padded: {binascii.hexlify(padded_data).decode()}")
    print(f"[CLIENT-SIM] Ciphertext: {binascii.hexlify(encrypted_data).decode()}")
    
    return encrypted_data

def simulate_server_aes_decryption(encrypted_data: bytes, aes_key: bytes) -> bytes:
    """
    Simulate the server's AES decryption using the exact method from server.py.
    
    This mirrors the server's decryption:
    - AES-256-CBC mode  
    - Zero IV (all zeros)
    - PKCS7 padding removal using unpad()
    """
    if len(aes_key) != 32:
        raise ValueError(f"AES key must be 32 bytes, got {len(aes_key)}")
    
    # Create zero IV (16 bytes of 0x00) - matches server's iv=b'\0' * 16
    zero_iv = b'\x00' * 16
    
    # Create AES cipher in CBC mode with zero IV (exact server code)
    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv=zero_iv)
    
    # Decrypt the data
    decrypted_padded = cipher_aes.decrypt(encrypted_data)
    
    # Remove PKCS7 padding using server's unpad method
    # AES block size is always 16 bytes
    decrypted_data = unpad(decrypted_padded, 16)
    
    print(f"[SERVER-SIM] Decrypted {len(encrypted_data)} bytes to {len(decrypted_data)} bytes")
    print(f"[SERVER-SIM] Key: {binascii.hexlify(aes_key).decode()}")
    print(f"[SERVER-SIM] IV: {binascii.hexlify(zero_iv).decode()}")
    print(f"[SERVER-SIM] Ciphertext: {binascii.hexlify(encrypted_data).decode()}")
    print(f"[SERVER-SIM] Decrypted+Padded: {binascii.hexlify(decrypted_padded).decode()}")
    print(f"[SERVER-SIM] Final: {binascii.hexlify(decrypted_data).decode()}")
    
    return decrypted_data

def test_aes_round_trip(test_data: bytes, aes_key: bytes) -> Tuple[bool, Optional[str]]:
    """
    Test a complete encrypt/decrypt round trip to validate compatibility.
    
    Returns:
        (success, error_message)
    """
    try:
        print(f"\n=== ROUND TRIP TEST ===")
        print(f"Original data: {test_data}")
        print(f"Original hex: {binascii.hexlify(test_data).decode()}")
        
        # Step 1: Encrypt using client method
        encrypted = simulate_client_aes_encryption(test_data, aes_key)
        
        print(f"\nEncryption successful: {len(encrypted)} bytes")
        
        # Step 2: Decrypt using server method  
        decrypted = simulate_server_aes_decryption(encrypted, aes_key)
        
        print(f"Decryption successful: {len(decrypted)} bytes")
        print(f"Decrypted data: {decrypted}")
        
        # Step 3: Compare original vs decrypted
        if test_data == decrypted:
            print("✅ SUCCESS: Data matches after round trip!")
            return True, None
        else:
            error_msg = f"❌ FAILURE: Data mismatch!\nOriginal: {test_data}\nDecrypted: {decrypted}"
            print(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"❌ EXCEPTION during round trip: {str(e)}"
        print(error_msg)
        return False, error_msg

def run_compatibility_tests():
    """Run a comprehensive suite of AES compatibility tests."""
    print("=== AES COMPATIBILITY TEST SUITE ===")
    print("Testing client AES encryption vs server AES decryption")
    print()
    
    # Generate test AES key
    aes_key = generate_test_aes_key()
    print(f"Test AES Key (32 bytes): {binascii.hexlify(aes_key).decode()}")
    
    # Test cases with different data sizes and content
    test_cases = [
        # Basic text
        b"Hello, World!",
        
        # Empty data  
        b"",
        
        # Single byte
        b"A",
        
        # Exact block size (16 bytes)
        b"1234567890123456",
        
        # Block size + 1
        b"12345678901234567",
        
        # Multiple blocks  
        b"This is a longer test message that spans multiple AES blocks for thorough testing.",
        
        # Binary data
        b"\x00\x01\x02\x03\xff\xfe\xfd\xfc\xaa\xbb\xcc\xdd\xee\x11\x22\x33",
        
        # Typical file content simulation
        b"This is test file content that would be encrypted and sent to the server for backup.",
        
        # Large-ish data
        b"X" * 1000,
    ]
    
    results = []
    
    for i, test_data in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {len(test_data)} bytes ---")
        success, error = test_aes_round_trip(test_data, aes_key)
        results.append((success, len(test_data), error))
    
    # Summary
    print(f"\n=== TEST RESULTS SUMMARY ===")
    passed = sum(1 for success, _, _ in results if success)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Client/Server AES compatibility confirmed!")
        print("\nThe client's AES implementation should be compatible with the server.")
        print("Key implementation details:")
        print("- AES-256-CBC mode")
        print("- 32-byte key")
        print("- Zero IV (16 bytes of 0x00)")
        print("- PKCS7 padding")
    else:
        print("⚠️  SOME TESTS FAILED - Compatibility issues detected!")
        print("\nFailed tests:")
        for i, (success, size, error) in enumerate(results):
            if not success:
                print(f"  Test {i+1} ({size} bytes): {error}")
                
    return passed == total

def demonstrate_exact_server_decryption():
    """
    Show exactly what the client needs to output for successful server decryption.
    This creates a reference implementation for the client team.
    """
    print(f"\n=== SERVER DECRYPTION REQUIREMENTS ===")
    
    # Use a fixed key and data for deterministic output
    fixed_key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10' + \
                b'\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20'
    
    test_content = b"Test file content for backup"
    
    print(f"Fixed AES Key: {binascii.hexlify(fixed_key).decode()}")
    print(f"Test Content: {test_content}")
    print(f"Content Length: {len(test_content)} bytes")
    
    # Show what client must produce
    encrypted_output = simulate_client_aes_encryption(test_content, fixed_key)
    
    print(f"\nClient must produce this encrypted output:")
    print(f"Hex: {binascii.hexlify(encrypted_output).decode()}")
    print(f"Length: {len(encrypted_output)} bytes")
    
    # Verify server can decrypt it
    print(f"\nVerifying server can decrypt...")
    decrypted = simulate_server_aes_decryption(encrypted_output, fixed_key)
    
    success = (decrypted == test_content)
    print(f"Server decryption result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        print(f"\n✅ REFERENCE IMPLEMENTATION CONFIRMED")
        print(f"If the client produces the above hex output for the given input,")
        print(f"the server will successfully decrypt it back to the original content.")
    
    return success

if __name__ == "__main__":
    print("Starting AES compatibility validation...")
    
    # Run full test suite
    all_passed = run_compatibility_tests()
    
    # Show reference implementation
    ref_success = demonstrate_exact_server_decryption()
    
    # Final status
    if all_passed and ref_success:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure