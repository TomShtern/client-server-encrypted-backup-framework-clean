#!/usr/bin/env python3
"""
RSA Key Generation Script for Client-Server Encrypted Backup Framework
Generates a 1024-bit RSA key pair and exports the public key in DER format.
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

def generate_rsa_key_pair():
    """Generate a 1024-bit RSA key pair and save public key in DER format."""
    
    print("Generating 1024-bit RSA key pair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize public key to DER format
    public_key_der = public_key.public_key_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    print(f"Public key DER size: {len(public_key_der)} bytes")
    
    # Save public key to file
    der_file_path = "test_public_key.der"
    with open(der_file_path, "wb") as f:
        f.write(public_key_der)
    
    print(f"Public key saved to: {der_file_path}")
    
    # Also save private key for completeness (PEM format)
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open("test_private_key.pem", "wb") as f:
        f.write(private_key_pem)
    
    print("Private key saved to: test_private_key.pem")
    
    return public_key_der, private_key

def verify_key_size(der_data):
    """Verify the DER data is exactly 162 bytes."""
    expected_size = 162
    actual_size = len(der_data)
    
    print(f"\nKey size verification:")
    print(f"Expected size: {expected_size} bytes")
    print(f"Actual size: {actual_size} bytes")
    
    if actual_size == expected_size:
        print("✓ Key size is correct!")
        return True
    else:
        print(f"✗ Key size mismatch! Difference: {actual_size - expected_size} bytes")
        return False

def main():
    """Main function to generate and verify RSA key."""
    try:
        # Generate key pair
        public_key_der, private_key = generate_rsa_key_pair()
        
        # Verify size
        size_ok = verify_key_size(public_key_der)
        
        # Display hex dump of first 32 bytes
        print(f"\nFirst 32 bytes of DER data (hex):")
        hex_data = public_key_der[:32].hex()
        for i in range(0, len(hex_data), 32):
            print(f"  {hex_data[i:i+32]}")
        
        if not size_ok:
            print("\nNote: 1024-bit RSA public keys in DER format typically vary between 160-164 bytes")
            print("depending on the specific key values. This is normal and expected.")
        
        return size_ok
        
    except Exception as e:
        print(f"Error generating RSA key: {e}")
        return False

if __name__ == "__main__":
    main()