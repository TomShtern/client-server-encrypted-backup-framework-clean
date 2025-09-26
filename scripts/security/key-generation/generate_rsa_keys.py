import os

from Crypto.PublicKey import RSA


def generate_rsa_key_pair():
    # Generate a 1024-bit RSA key pair
    key = RSA.generate(1024)
    private_key = key.export_key(format='DER')
    public_key = key.publickey().export_key(format='DER')

    # Ensure the output directory exists
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)

    # Save the private key
    private_key_path = os.path.join(output_dir, 'private_key.der')
    with open(private_key_path, 'wb') as f:
        f.write(private_key)
    print(f"Private key saved to {private_key_path} ({len(private_key)} bytes)")

    # Save the public key
    public_key_path = os.path.join(output_dir, 'public_key.der')
    with open(public_key_path, 'wb') as f:
        f.write(public_key)
    print(f"Public key saved to {public_key_path} ({len(public_key)} bytes)")

    return private_key, public_key

if __name__ == "__main__":
    try:
        private_key, public_key = generate_rsa_key_pair()
        print("RSA-1024 key pair generated successfully.")
    except Exception as e:
        print(f"Error generating RSA keys: {e}")
