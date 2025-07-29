#!/usr/bin/env python3
"""
Create working RSA keys that are compatible with both Python and C++ Crypto++
"""

import os
import subprocess
import sys

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import shutil

def create_pycryptodome_keys():
    """Create RSA keys using PyCryptodome"""
    print("Creating RSA keys using PyCryptodome...")
    
    try:
        # Generate RSA key pair
        print("Generating 1024-bit RSA key pair...")
        key = RSA.generate(1024, randfunc=get_random_bytes)

        # Export private key in DER PKCS#8 format
        private_key_der = key.export_key(format='DER', pkcs=8)
        with open('priv.key', 'wb') as f:
            f.write(private_key_der)
        print("Private key saved to priv.key")

        # Export public key in DER X.509 format
        public_key_der = key.public_key().export_key(format='DER', pkcs=8) # PKCS#8 for public key is also X.509 compatible
        with open('pub.key', 'wb') as f:
            f.write(public_key_der)
        print("Public key saved to pub.key")
        
        # Copy to data directory
        os.makedirs('data', exist_ok=True)
        shutil.copy2('priv.key', 'data/priv.key')
        shutil.copy2('pub.key', 'data/pub.key')
        print("Keys copied to data/ directory")
        
        # Check file sizes
        priv_size = os.path.getsize('priv.key')
        pub_size = os.path.getsize('pub.key')
        
        print(f"Private key size: {priv_size} bytes")
        print(f"Public key size: {pub_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"Error creating keys with PyCryptodome: {e}")
        return False

def test_pycryptodome_keys():
    """Test the generated keys using PyCryptodome"""
    print("\nTesting generated keys with PyCryptodome...")
    
    try:
        with open('pub.key', 'rb') as f:
            public_key = RSA.import_key(f.read())
        with open('priv.key', 'rb') as f:
            private_key = RSA.import_key(f.read())

        test_message = b"Hello, RSA test!"
        
        # Encrypt with public key
        cipher_rsa = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
        encrypted_data = cipher_rsa.encrypt(test_message)
        print(f"Encryption successful: {len(encrypted_data)} bytes")
        
        # Decrypt with private key
        cipher_rsa = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
        decrypted_message = cipher_rsa.decrypt(encrypted_data)
        
        print(f"Decryption successful: '{decrypted_message.decode()}'")
        
        if decrypted_message == test_message:
            print("[OK] RSA key test passed!")
            return True
        else:
            print(f"[X] RSA key test failed: expected '{test_message.decode()}', got '{decrypted_message.decode()}'")
            return False
            
    except Exception as e:
        print(f"Test error with PyCryptodome: {e}")
        return False

def test_keys():
    """Test the generated keys"""
    print("\nTesting generated keys...")
    
    try:
        # Test with OpenSSL
        test_message = "Hello, RSA test!"
        
        # Encrypt with public key
        result = subprocess.run([
            'openssl', 'pkeyutl',
            '-encrypt',
            '-pubin',
            '-inkey', 'pub.key',
            '-keyform', 'DER',
            '-in', '-'
        ], input=test_message, capture_output=True, text=False, timeout=10)
        
        if result.returncode != 0:
            print(f"Encryption test failed: {result.stderr}")
            return False
            
        encrypted_data = result.stdout
        print(f"Encryption successful: {len(encrypted_data)} bytes")
        
        # Decrypt with private key
        result = subprocess.run([
            'openssl', 'pkeyutl',
            '-decrypt',
            '-inkey', 'priv.key',
            '-keyform', 'DER',
            '-in', '-'
        ], input=encrypted_data, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"Decryption test failed: {result.stderr}")
            return False
            
        decrypted_message = result.stdout.strip()
        print(f"Decryption successful: '{decrypted_message}'")
        
        if decrypted_message == test_message:
            print("[OK] RSA key test passed!")
            return True
        else:
            print(f"[X] RSA key test failed: expected '{test_message}', got '{decrypted_message}'")
            return False
            
    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("RSA Key Generator for Crypto++ Compatibility")
    print("=" * 50)
    
    if create_pycryptodome_keys():
        if test_pycryptodome_keys():
            print("\n[OK] RSA keys created and tested successfully!")
            print("The client should now be able to load these keys.")
        else:
            print("\n[X] Key test failed, but keys were created.")
    else:
        print("\n[X] Failed to create RSA keys.")
        sys.exit(1)
