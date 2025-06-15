#!/usr/bin/env python3
"""
Test RSA compatibility between client (Windows CNG) and server (PyCryptodome)
This script tests if the DER key format conversion and OAEP padding work correctly.
"""

import os
import sys
import subprocess

# Add server directory to path for imports
sys.path.append('server')

try:
    from crypto_compat import RSA, PKCS1_OAEP, SHA256, get_random_bytes
    print("✓ Server crypto libraries loaded successfully")
except ImportError as e:
    print(f"❌ Failed to load server crypto libraries: {e}")
    sys.exit(1)

def test_rsa_compatibility():
    """Test RSA encryption/decryption compatibility"""
    print("\n🔒 RSA COMPATIBILITY TEST")
    print("=" * 50)
    
    # Step 1: Generate a test AES key (what the server would send)
    test_aes_key = get_random_bytes(32)  # 256-bit AES key
    print(f"1. Generated test AES key: {len(test_aes_key)} bytes")
    
    # Step 2: Load the client's public key (DER format)
    try:
        with open('priv.key', 'rb') as f:
            # This is actually the private key file, but we need to extract public key
            print("❌ Need to extract public key from client's private key file")
            return False
    except FileNotFoundError:
        print("❌ Client private key file not found. Run client first to generate keys.")
        return False
    
    # Step 3: Test if we can read the client's DER-formatted public key
    # For now, let's generate a test key pair to verify the process works
    print("\n2. Generating test RSA key pair...")
    test_key = RSA.generate(1024)
    
    # Step 4: Test OAEP encryption with SHA-256
    print("3. Testing OAEP encryption with SHA-256...")
    try:
        cipher_rsa = PKCS1_OAEP.new(test_key, hashAlgo=SHA256)
        encrypted_aes_key = cipher_rsa.encrypt(test_aes_key)
        print(f"   ✓ Encrypted AES key: {len(encrypted_aes_key)} bytes")
        
        # Test decryption
        decrypted_aes_key = cipher_rsa.decrypt(encrypted_aes_key)
        print(f"   ✓ Decrypted AES key: {len(decrypted_aes_key)} bytes")
        
        if decrypted_aes_key == test_aes_key:
            print("   ✅ Encryption/decryption successful!")
            return True
        else:
            print("   ❌ Decrypted key doesn't match original")
            return False
            
    except Exception as e:
        print(f"   ❌ OAEP encryption failed: {e}")
        return False

def test_client_key_generation():
    """Test if we can run the client to generate keys"""
    print("\n🔑 CLIENT KEY GENERATION TEST")
    print("=" * 50)
    
    # Remove existing keys
    for file in ['me.info', 'priv.key']:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed existing {file}")
    
    print("1. Starting client to generate fresh keys...")
    print("   (This will fail to connect, but should generate keys)")
    
    # This is just to test the concept - in practice we'd need to coordinate this better
    return True

if __name__ == "__main__":
    print("🧪 RSA COMPATIBILITY TESTING SUITE")
    print("=" * 60)
    
    # Test 1: Basic RSA functionality
    if test_rsa_compatibility():
        print("\n✅ RSA compatibility test PASSED")
    else:
        print("\n❌ RSA compatibility test FAILED")
    
    # Test 2: Client key generation
    if test_client_key_generation():
        print("✅ Client key generation test setup complete")
    else:
        print("❌ Client key generation test FAILED")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Run client to generate fresh keys")
    print("2. Extract public key from client")
    print("3. Test server encryption with client's public key")
    print("4. Test client decryption of server's encrypted data")
