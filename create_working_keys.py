#!/usr/bin/env python3
"""
Create working RSA keys that are compatible with both Python and C++ Crypto++
"""

import os
import subprocess
import sys

def create_openssl_keys():
    """Create RSA keys using OpenSSL which should be compatible with Crypto++"""
    print("Creating RSA keys using OpenSSL...")
    
    try:
        # Generate private key in DER format
        print("Generating 1024-bit RSA private key...")
        result = subprocess.run([
            'openssl', 'genpkey', 
            '-algorithm', 'RSA', 
            '-pkcs8',
            '-outform', 'DER',
            '-out', 'priv.key',
            '-pkeyopt', 'rsa_keygen_bits:1024'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"Private key generation failed: {result.stderr}")
            return False
            
        print(f"Private key saved to priv.key")
        
        # Generate public key in DER format
        print("Extracting public key...")
        result = subprocess.run([
            'openssl', 'pkey',
            '-in', 'priv.key',
            '-inform', 'DER',
            '-pubout',
            '-outform', 'DER',
            '-out', 'pub.key'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"Public key extraction failed: {result.stderr}")
            return False
            
        print(f"Public key saved to pub.key")
        
        # Copy to data directory
        os.makedirs('data', exist_ok=True)
        
        # Copy files
        import shutil
        shutil.copy2('priv.key', 'data/priv.key')
        shutil.copy2('pub.key', 'data/pub.key')
        
        print("Keys copied to data/ directory")
        
        # Check file sizes
        priv_size = os.path.getsize('priv.key')
        pub_size = os.path.getsize('pub.key')
        
        print(f"Private key size: {priv_size} bytes")
        print(f"Public key size: {pub_size} bytes")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("OpenSSL command timed out")
        return False
    except FileNotFoundError:
        print("OpenSSL not found. Please install OpenSSL.")
        return False
    except Exception as e:
        print(f"Error: {e}")
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
            print("✓ RSA key test passed!")
            return True
        else:
            print(f"✗ RSA key test failed: expected '{test_message}', got '{decrypted_message}'")
            return False
            
    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    print("RSA Key Generator for Crypto++ Compatibility")
    print("=" * 50)
    
    if create_openssl_keys():
        if test_keys():
            print("\n✓ RSA keys created and tested successfully!")
            print("The client should now be able to load these keys.")
        else:
            print("\n✗ Key test failed, but keys were created.")
    else:
        print("\n✗ Failed to create RSA keys.")
        sys.exit(1)
