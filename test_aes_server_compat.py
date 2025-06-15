#!/usr/bin/env python3
"""
Test AES compatibility with the server's expected format
This simulates exactly what the server does when decrypting files
"""

import sys
import os

# Use the server's crypto compatibility layer
sys.path.append('server')
from crypto_compat import AES, pad, unpad

def test_server_decryption():
    print("🔒 Testing Server-Side AES Decryption")
    print("=====================================")
    
    # Test key (32 bytes for AES-256) - same as C++ test
    test_key = bytes([
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f
    ])
    
    # Test plaintext (16 bytes - exactly one block)
    plaintext = b'Hello World! Tes'
    
    print(f"Key: {test_key.hex()}")
    print(f"Plaintext: {plaintext.hex()}")
    print(f"Plaintext (text): {plaintext.decode('utf-8', errors='ignore')}")
    
    try:
        # Encrypt using the server's method (with zero IV)
        zero_iv = b'\0' * 16
        cipher_aes = AES.new(test_key, AES.MODE_CBC, iv=zero_iv)
        
        # Add PKCS7 padding manually to see what happens
        padded_data = pad(plaintext, AES.block_size)
        print(f"Padded: {padded_data.hex()} ({len(padded_data)} bytes)")
        
        # Encrypt
        encrypted = cipher_aes.encrypt(padded_data)
        print(f"Encrypted: {encrypted.hex()}")
        
        # Now decrypt (simulating server)
        cipher_aes_decrypt = AES.new(test_key, AES.MODE_CBC, iv=zero_iv)
        decrypted_padded = cipher_aes_decrypt.decrypt(encrypted)
        print(f"Decrypted (padded): {decrypted_padded.hex()}")
        
        # Remove padding
        decrypted = unpad(decrypted_padded, AES.block_size)
        print(f"Decrypted (unpadded): {decrypted.hex()}")
        print(f"Decrypted (text): {decrypted.decode('utf-8', errors='ignore')}")
        
        success = (decrypted == plaintext)
        print(f"Roundtrip test: {'✅ PASSED' if success else '❌ FAILED'}")
        
        return encrypted, success
        
    except Exception as e:
        print(f"❌ FAILED: Exception during encryption/decryption: {e}")
        return None, False

def test_various_sizes():
    print("\n🔧 Testing Various Data Sizes")
    print("==============================")
    
    test_key = b'A' * 32  # Simple 32-byte key
    zero_iv = b'\0' * 16
    
    test_sizes = [1, 15, 16, 17, 31, 32, 33, 47, 48, 49, 100, 255, 256, 257]
    
    all_passed = True
    
    for size in test_sizes:
        test_data = bytes([0x55] * size)  # Fill with 0x55
        
        try:
            # Server-side encryption process
            cipher_encrypt = AES.new(test_key, AES.MODE_CBC, iv=zero_iv)
            padded_data = pad(test_data, AES.block_size)
            encrypted = cipher_encrypt.encrypt(padded_data)
            
            # Server-side decryption process (what the server actually does)
            cipher_decrypt = AES.new(test_key, AES.MODE_CBC, iv=zero_iv)
            decrypted_padded = cipher_decrypt.decrypt(encrypted)
            decrypted = unpad(decrypted_padded, AES.block_size)
            
            success = (decrypted == test_data)
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"Size {size:3d} bytes: {status} (encrypted: {len(encrypted)} bytes)")
            
            if not success:
                all_passed = False
                print(f"  Expected: {len(test_data)} bytes")
                print(f"  Got:      {len(decrypted)} bytes")
                
        except Exception as e:
            print(f"Size {size:3d} bytes: ❌ FAILED (exception: {e})")
            all_passed = False
    
    return all_passed

def test_file_like_data():
    print("\n📄 Testing File-Like Data")
    print("=========================")
    
    test_key = bytes([(i * 7) % 256 for i in range(32)])  # Reproducible key
    zero_iv = b'\0' * 16
    
    file_content = (
        "This is a test file that will be encrypted and sent to the server.\n"
        "It contains multiple lines of text to verify that the encryption\n"
        "works correctly with different content sizes and patterns.\n"
        "The server should be able to decrypt this successfully.\n"
    ).encode('utf-8')
    
    print(f"Original file size: {len(file_content)} bytes")
    
    try:
        # Encrypt (client-side simulation)
        cipher_encrypt = AES.new(test_key, AES.MODE_CBC, iv=zero_iv)
        padded_data = pad(file_content, AES.block_size)
        encrypted = cipher_encrypt.encrypt(padded_data)
        
        print(f"Encrypted file size: {len(encrypted)} bytes")
        
        # Verify block alignment
        if len(encrypted) % 16 != 0:
            print("❌ FAILED: Encrypted data is not block-aligned")
            return False
        
        # Decrypt (server-side simulation - this is what the server actually does)
        cipher_decrypt = AES.new(test_key, AES.MODE_CBC, iv=zero_iv)
        decrypted_padded = cipher_decrypt.decrypt(encrypted)
        decrypted = unpad(decrypted_padded, AES.block_size)
        
        if decrypted == file_content:
            print("✅ PASSED: File-like data test successful!")
            print("   - Encrypted data is properly padded")
            print("   - Decryption restores original data exactly")
            print("   - Zero IV and PKCS7 padding are working correctly")
            return True
        else:
            print("❌ FAILED: Decrypted data doesn't match original")
            print(f"   Original: {len(file_content)} bytes")
            print(f"   Decrypted: {len(decrypted)} bytes")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception during file-like data test: {e}")
        return False

def create_test_vector():
    print("\n📋 Creating Test Vector for C++ Implementation")
    print("===============================================")
    
    # Create a known test vector that C++ can use to verify compatibility
    test_key = bytes(range(32))  # 0x00, 0x01, 0x02, ..., 0x1f
    test_data = b"Hello World! Test data for AES compatibility."
    zero_iv = b'\0' * 16
    
    try:
        cipher = AES.new(test_key, AES.MODE_CBC, iv=zero_iv)
        padded_data = pad(test_data, AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        
        print("Test Vector:")
        print(f"  Key:        {test_key.hex()}")
        print(f"  Plaintext:  {test_data.hex()}")
        print(f"  Padded:     {padded_data.hex()}")
        print(f"  Encrypted:  {encrypted.hex()}")
        print(f"  IV:         {zero_iv.hex()}")
        
        print("\nC++ Test Code:")
        print("// Expected encrypted result for compatibility test")
        print(f"std::vector<uint8_t> expected_encrypted = {{")
        hex_bytes = [f"0x{b:02x}" for b in encrypted]
        for i in range(0, len(hex_bytes), 8):
            line = ", ".join(hex_bytes[i:i+8])
            print(f"    {line},")
        print("};")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Exception creating test vector: {e}")
        return False

def main():
    print("🔐 AES Server Compatibility Test Suite")
    print("======================================")
    print("Testing Python server's AES decryption capabilities")
    print("This simulates exactly what the server does when receiving encrypted files")
    print()
    
    results = []
    
    # Test 1: Basic encryption/decryption
    _, result1 = test_server_decryption()
    results.append(("Basic encryption/decryption", result1))
    
    # Test 2: Various data sizes
    result2 = test_various_sizes()
    results.append(("Various data sizes", result2))
    
    # Test 3: File-like data
    result3 = test_file_like_data()
    results.append(("File-like data", result3))
    
    # Test 4: Create test vector
    result4 = create_test_vector()
    results.append(("Test vector creation", result4))
    
    print("\n📊 RESULTS SUMMARY")
    print("==================")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The server's AES decryption is working correctly.")
        print("C++ client implementation should use:")
        print("- AES-256-CBC mode")
        print("- Zero IV (16 bytes of 0x00)")
        print("- PKCS7 padding")
        print("- 32-byte key from server")
    else:
        print("⚠️ SOME TESTS FAILED!")
        print("Check the server's crypto implementation.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())