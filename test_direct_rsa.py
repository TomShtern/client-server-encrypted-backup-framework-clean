#!/usr/bin/env python3
"""
Direct RSA test - Generate keys and test encryption/decryption
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

def generate_compatible_keys():
    """Generate RSA keys in a format compatible with both client and server"""
    print("🔑 Generating RSA key pair...")
    
    # Generate 1024-bit RSA key pair
    key = RSA.generate(1024)
    
    # Export private key in DER format
    private_der = key.export_key(format='DER')
    
    # Export public key in DER format  
    public_der = key.publickey().export_key(format='DER')
    
    print(f"   Private key: {len(private_der)} bytes")
    print(f"   Public key: {len(public_der)} bytes")
    
    # Save keys
    with open('test_private.der', 'wb') as f:
        f.write(private_der)
    
    with open('test_public.der', 'wb') as f:
        f.write(public_der)
    
    return key

def test_server_encryption():
    """Test server-side encryption with OAEP SHA-256"""
    print("\n🔒 Testing server-side encryption...")
    
    # Load the key
    with open('test_public.der', 'rb') as f:
        public_der = f.read()
    
    # Import public key
    public_key = RSA.import_key(public_der)
    
    # Generate test AES key
    test_aes_key = get_random_bytes(32)
    print(f"   Test AES key: {len(test_aes_key)} bytes")
    
    # Encrypt with OAEP SHA-256 (matching client expectations)
    cipher_rsa = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    encrypted_data = cipher_rsa.encrypt(test_aes_key)
    
    print(f"   Encrypted data: {len(encrypted_data)} bytes")
    
    # Save encrypted data for client test
    with open('test_encrypted.bin', 'wb') as f:
        f.write(encrypted_data)
    
    return test_aes_key, encrypted_data

def test_server_decryption(original_key, encrypted_data):
    """Test server-side decryption"""
    print("\n🔓 Testing server-side decryption...")
    
    # Load private key
    with open('test_private.der', 'rb') as f:
        private_der = f.read()
    
    private_key = RSA.import_key(private_der)
    
    # Decrypt with OAEP SHA-256
    cipher_rsa = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    decrypted_data = cipher_rsa.decrypt(encrypted_data)
    
    print(f"   Decrypted data: {len(decrypted_data)} bytes")
    
    if decrypted_data == original_key:
        print("   ✅ Server decryption successful!")
        return True
    else:
        print("   ❌ Server decryption failed - data mismatch")
        return False

def create_client_test():
    """Create a simple client test program"""
    print("\n📝 Creating client test program...")
    
    # Copy the DER private key to the format the client expects
    with open('test_private.der', 'rb') as f:
        private_der = f.read()
    
    with open('priv.key', 'wb') as f:
        f.write(private_der)
    
    print("   ✓ Created priv.key for client testing")
    
    # Create a simple C++ test program
    cpp_test = '''
#include <iostream>
#include <fstream>
#include <vector>
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt.lib")

void CheckCNGStatus(NTSTATUS status, const std::string& operation) {
    if (status != STATUS_SUCCESS) {
        std::cerr << "CNG operation failed: " << operation << " (Status: 0x" << std::hex << status << ")" << std::endl;
        throw std::runtime_error("CNG operation failed");
    }
}

int main() {
    std::cout << "🧪 Client RSA Decryption Test" << std::endl;
    
    try {
        // Load private key
        std::ifstream privFile("priv.key", std::ios::binary);
        if (!privFile) {
            std::cerr << "❌ Cannot open priv.key" << std::endl;
            return 1;
        }
        
        privFile.seekg(0, std::ios::end);
        size_t keySize = privFile.tellg();
        privFile.seekg(0, std::ios::beg);
        
        std::vector<char> keyData(keySize);
        privFile.read(keyData.data(), keySize);
        privFile.close();
        
        std::cout << "✓ Loaded private key: " << keySize << " bytes" << std::endl;
        
        // Load encrypted data
        std::ifstream encFile("test_encrypted.bin", std::ios::binary);
        if (!encFile) {
            std::cerr << "❌ Cannot open test_encrypted.bin" << std::endl;
            return 1;
        }
        
        encFile.seekg(0, std::ios::end);
        size_t encSize = encFile.tellg();
        encFile.seekg(0, std::ios::beg);
        
        std::vector<char> encData(encSize);
        encFile.read(encData.data(), encSize);
        encFile.close();
        
        std::cout << "✓ Loaded encrypted data: " << encSize << " bytes" << std::endl;
        
        // TODO: Add CNG decryption code here
        std::cout << "⚠️  CNG decryption test not implemented yet" << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
}
'''
    
    with open('test_client_decrypt.cpp', 'w') as f:
        f.write(cpp_test)
    
    print("   ✓ Created test_client_decrypt.cpp")

if __name__ == "__main__":
    print("🧪 DIRECT RSA COMPATIBILITY TEST")
    print("=" * 50)
    
    try:
        # Step 1: Generate compatible keys
        key = generate_compatible_keys()
        
        # Step 2: Test server encryption
        original_aes_key, encrypted_data = test_server_encryption()
        
        # Step 3: Test server decryption (sanity check)
        if test_server_decryption(original_aes_key, encrypted_data):
            print("✅ Server-side encryption/decryption works correctly")
        else:
            print("❌ Server-side test failed")
            sys.exit(1)
        
        # Step 4: Create client test
        create_client_test()
        
        print("\n" + "=" * 50)
        print("✅ Test setup complete!")
        print("\nNEXT STEPS:")
        print("1. The encrypted AES key is saved in 'test_encrypted.bin'")
        print("2. The private key is saved in 'priv.key' (DER format)")
        print("3. Run the client to test if it can decrypt the data")
        print("4. If successful, the RSA compatibility issue is resolved")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
