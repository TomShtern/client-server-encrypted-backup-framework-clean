"""
Compatibility layer for crypto operations using python3-cryptography or PyCryptodome.
Provides a PyCryptodome-compatible interface using the installed cryptography library if needed.
"""
from typing import Optional
import os
import sys

# Try to import PyCryptodome, else fall back to cryptography
try:
    from Crypto.Cipher import AES as _PyCryptoAES  # type: ignore
    from Crypto.PublicKey import RSA as _PyCryptoRSA  # type: ignore
    from Crypto.Cipher import PKCS1_OAEP as _PyCryptoPKCS1_OAEP  # type: ignore
    from Crypto.Util.Padding import pad as _pycrypto_pad, unpad as _pycrypto_unpad  # type: ignore
    from Crypto.Random import get_random_bytes as _pycrypto_get_random_bytes  # type: ignore
    from Crypto.Hash import SHA256 as _PyCryptoSHA256  # type: ignore
    _CRYPTO_BACKEND = 'pycryptodome'
    print("Using PyCryptodome")
except ImportError:
    _PyCryptoAES = None
    _PyCryptoRSA = None
    _PyCryptoPKCS1_OAEP = None
    _pycrypto_pad = None
    _pycrypto_unpad = None
    _pycrypto_get_random_bytes = None
    _PyCryptoSHA256 = None
    _CRYPTO_BACKEND = 'cryptography'
    print("PyCryptodome not available, using cryptography library compatibility layer")
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # type: ignore
    from cryptography.hazmat.primitives import padding, serialization, hashes  # type: ignore
    from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding  # type: ignore
    from cryptography.hazmat.backends import default_backend  # type: ignore

# Unified SHA256 interface
class SHA256:
    """SHA256 hash algorithm class for PKCS1_OAEP compatibility"""
    @staticmethod
    def new(data: Optional[bytes] = None):
        if _CRYPTO_BACKEND == 'pycryptodome':
            return _PyCryptoSHA256.new(data) if data else _PyCryptoSHA256.new()
        import hashlib
        return hashlib.sha256(data) if data else hashlib.sha256()
    @staticmethod
    def digest_size() -> int:
        if _CRYPTO_BACKEND == 'pycryptodome':
            return _PyCryptoSHA256.digest_size
        return 32

# AES compatibility
if _CRYPTO_BACKEND == 'pycryptodome':
    AES = _PyCryptoAES
    RSA = _PyCryptoRSA
    PKCS1_OAEP = _PyCryptoPKCS1_OAEP
    pad = _pycrypto_pad
    unpad = _pycrypto_unpad
    get_random_bytes = _pycrypto_get_random_bytes
else:
    class AES:
        BLOCKSIZE = 16
        block_size = 16
        MODE_CBC = 2
        @staticmethod
        def new(key, mode_constant, iv=None):
            return AESCompat(key, mode_constant, iv)
    class AESCompat:
        def __init__(self, key, mode_constant, iv=None):
            self.key = key
            self.iv = iv or os.urandom(16)
            if mode_constant == AES.MODE_CBC:
                cipher = Cipher(algorithms.AES(key), modes.CBC(self.iv), backend=default_backend())
                self.encryptor = cipher.encryptor()
                self.decryptor = cipher.decryptor()
            else:
                raise ValueError(f"Unsupported AES mode: {mode_constant}")
        def encrypt(self, data):
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            return self.encryptor.update(padded_data) + self.encryptor.finalize()
        def decrypt(self, data):
            decrypted = self.decryptor.update(data) + self.decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            return unpadder.update(decrypted) + unpadder.finalize()
    class RSA:
        @staticmethod
        def generate(bits, randfunc=None):
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=bits,
                backend=default_backend()
            )
            return RSAKeyCompat(private_key)
        @staticmethod
        def import_key(data):
            try:
                if isinstance(data, str):
                    data = data.encode()
                private_key = serialization.load_der_private_key(
                    data, password=None, backend=default_backend()
                )
                return RSAKeyCompat(private_key)
            except Exception:
                public_key = serialization.load_der_public_key(
                    data, backend=default_backend()
                )
                return RSAKeyCompat(None, public_key)
    class RSAKeyCompat:
        def __init__(self, private_key=None, public_key=None):
            self.private_key = private_key
            self.public_key = public_key or (private_key.public_key() if private_key else None)
        def encrypt(self, data):
            if self.public_key is None:
                raise ValueError("No public key available for encryption.")
            if isinstance(data, str):
                data = data.encode()
            return self.public_key.encrypt(
                data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        def decrypt(self, data):
            if self.private_key is None:
                raise ValueError("No private key available for decryption.")
            return self.private_key.decrypt(
                data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        def export_key(self, format='DER'):
            if self.private_key is None:
                raise ValueError("No private key available for export.")
            if format == 'DER':
                return self.private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            else:
                raise ValueError("Unsupported format")
    class PKCS1_OAEP:
        def __init__(self, key, hashAlgo=None):
            self.key = key
            self.hash_algo = hashAlgo
        def encrypt(self, data):
            return self.key.encrypt(data)
        def decrypt(self, data):
            return self.key.decrypt(data)
        @staticmethod
        def new(key, hashAlgo=None):
            return PKCS1_OAEP(key, hashAlgo)
    def pad(data, block_size):
        padder = padding.PKCS7(block_size * 8).padder()
        return padder.update(data) + padder.finalize()
    def unpad(data, block_size):
        unpadder = padding.PKCS7(block_size * 8).unpadder()
        return unpadder.update(data) + unpadder.finalize()
    def get_random_bytes(length):
        return os.urandom(length)
# End of compatibility layer