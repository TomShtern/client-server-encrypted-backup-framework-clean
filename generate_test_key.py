#!/usr/bin/env python3
"""Generate a valid 1024-bit RSA public key in DER format for testing."""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_rsa_key_pair():
    """Generate 1024-bit RSA key pair and return public key in DER format."""
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize public key to DER format
    der_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return der_public_key, private_key

def main():
    print("Generating 1024-bit RSA key pair...")
    
    # Generate key pair
    public_der, private_key = generate_rsa_key_pair()
    
    print(f"Public key DER size: {len(public_der)} bytes")
    
    # Save to file
    with open('test_public_key.der', 'wb') as f:
        f.write(public_der)
    
    print("Saved public key to: test_public_key.der")
    
    # Verify it can be loaded
    try:
        from cryptography.hazmat.primitives import serialization
        loaded_key = serialization.load_der_public_key(public_der)
        print("✅ Key validation: Successfully loaded DER public key")
        print(f"Key size: {loaded_key.key_size} bits")
    except Exception as e:
        print(f"❌ Key validation failed: {e}")
    
    # Show hex representation for C++ integration
    print("\nFirst 32 bytes (hex):", public_der[:32].hex())
    print("Last 32 bytes (hex):", public_der[-32:].hex())

if __name__ == "__main__":
    main()