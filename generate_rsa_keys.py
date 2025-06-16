#!/usr/bin/env python3
"""
Generate RSA keys in DER format for the encrypted backup client
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

def generate_rsa_keys():
    """Generate RSA key pair and save to DER format files"""
    print("Generating 1024-bit RSA key pair...")
    
    # Generate RSA key pair
    key = RSA.generate(1024)
    
    # Get private and public keys
    private_key = key
    public_key = key.publickey()
    
    # Export to DER format
    private_der = private_key.export_key('DER')
    public_der = public_key.export_key('DER')
    
    # Save to files
    with open('priv.key', 'wb') as f:
        f.write(private_der)
    print(f"Saved private key to priv.key ({len(private_der)} bytes)")
    
    with open('pub.key', 'wb') as f:
        f.write(public_der)
    print(f"Saved public key to pub.key ({len(public_der)} bytes)")
    
    # Also save to data directory
    os.makedirs('data', exist_ok=True)
    with open('data/priv.key', 'wb') as f:
        f.write(private_der)
    print(f"Saved private key to data/priv.key ({len(private_der)} bytes)")
    
    with open('data/pub.key', 'wb') as f:
        f.write(public_der)
    print(f"Saved public key to data/pub.key ({len(public_der)} bytes)")
    
    # Test encryption/decryption
    print("\nTesting RSA encryption/decryption...")
    cipher = PKCS1_OAEP.new(public_key)
    test_message = b"Hello, RSA!"
    encrypted = cipher.encrypt(test_message)
    print(f"Encrypted message: {len(encrypted)} bytes")
    
    decipher = PKCS1_OAEP.new(private_key)
    decrypted = decipher.decrypt(encrypted)
    print(f"Decrypted message: {decrypted}")
    
    if decrypted == test_message:
        print("✓ RSA encryption/decryption test passed!")
    else:
        print("✗ RSA encryption/decryption test failed!")
    
    print("\nRSA key generation completed successfully!")

if __name__ == "__main__":
    generate_rsa_keys()
