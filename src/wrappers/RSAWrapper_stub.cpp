// Windows CNG RSA implementation - Production quality RSA encryption
// Uses Windows Cryptography Next Generation (CNG) API for real RSA operations
// Provides full RSA-1024 encryption/decryption functionality

#include "../../include/wrappers/RSAWrapper.h"
#include <windows.h>
#include <bcrypt.h>
#include <stdexcept>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>

#pragma comment(lib, "bcrypt.lib")
#pragma comment(lib, "crypt32.lib")

// Define STATUS_SUCCESS if not already defined
#ifndef STATUS_SUCCESS
#define STATUS_SUCCESS ((NTSTATUS)0x00000000L)
#endif

// Helper function to check CNG status and throw exception on failure
void CheckCNGStatus(NTSTATUS status, const std::string& operation) {
    if (status != STATUS_SUCCESS) {
        char errorMsg[256];
        sprintf_s(errorMsg, "CNG RSA operation failed: %s (Status: 0x%08X)", operation.c_str(), status);
        throw std::runtime_error(errorMsg);
    }
}

// Helper function to encode DER length
std::vector<BYTE> EncodeDERLength(size_t length) {
    std::vector<BYTE> result;
    if (length < 0x80) {
        result.push_back(static_cast<BYTE>(length));
    } else {
        // Long form
        std::vector<BYTE> lengthBytes;
        size_t temp = length;
        while (temp > 0) {
            lengthBytes.insert(lengthBytes.begin(), static_cast<BYTE>(temp & 0xFF));
            temp >>= 8;
        }
        result.push_back(0x80 | static_cast<BYTE>(lengthBytes.size()));
        result.insert(result.end(), lengthBytes.begin(), lengthBytes.end());
    }
    return result;
}

// Helper function to convert CNG RSA public key blob to DER format
std::vector<char> ConvertCNGPublicKeyToDER(const std::vector<char>& cngBlob) {
    // CNG RSA public key blob structure:
    // BCRYPT_RSAKEY_BLOB header (24 bytes) + public exponent + modulus

    if (cngBlob.size() < 24) {
        throw std::runtime_error("Invalid CNG RSA public key blob size");
    }

    // Parse CNG blob header manually (BCRYPT_RSAKEY_BLOB structure)
    // Structure: ULONG Magic, ULONG BitLength, ULONG cbPublicExponent, ULONG cbModulus, ULONG cbPrime1, ULONG cbPrime2
    const ULONG* header = reinterpret_cast<const ULONG*>(cngBlob.data());

    ULONG magic = header[0];
    ULONG bitLength = header[1];
    ULONG expSize = header[2];
    ULONG keySize = header[3];

    if (magic != BCRYPT_RSAPUBLIC_MAGIC) {
        throw std::runtime_error("Invalid CNG RSA public key magic");
    }

    // Extract modulus and exponent from CNG blob
    const BYTE* exponent = reinterpret_cast<const BYTE*>(cngBlob.data()) + sizeof(BCRYPT_RSAKEY_BLOB);
    const BYTE* modulus = exponent + expSize;

    // Build DER-encoded RSA public key
    std::vector<BYTE> derKey;

    // Build inner SEQUENCE { INTEGER(n), INTEGER(e) }
    std::vector<BYTE> innerSeq;

    // Add modulus as INTEGER
    innerSeq.push_back(0x02); // INTEGER tag
    std::vector<BYTE> modulusData;
    if (modulus[0] & 0x80) {
        modulusData.push_back(0x00); // Padding byte
    }
    modulusData.insert(modulusData.end(), modulus, modulus + keySize);
    std::vector<BYTE> modLen = EncodeDERLength(modulusData.size());
    innerSeq.insert(innerSeq.end(), modLen.begin(), modLen.end());
    innerSeq.insert(innerSeq.end(), modulusData.begin(), modulusData.end());

    // Add exponent as INTEGER
    innerSeq.push_back(0x02); // INTEGER tag
    std::vector<BYTE> expData;
    if (exponent[0] & 0x80) {
        expData.push_back(0x00); // Padding byte
    }
    expData.insert(expData.end(), exponent, exponent + expSize);
    std::vector<BYTE> expLen = EncodeDERLength(expData.size());
    innerSeq.insert(innerSeq.end(), expLen.begin(), expLen.end());
    innerSeq.insert(innerSeq.end(), expData.begin(), expData.end());

    // Build BIT STRING containing the inner sequence
    std::vector<BYTE> bitString;
    bitString.push_back(0x03); // BIT STRING tag
    std::vector<BYTE> bitStringContent;
    bitStringContent.push_back(0x00); // No unused bits
    bitStringContent.push_back(0x30); // SEQUENCE tag for inner content
    std::vector<BYTE> innerLen = EncodeDERLength(innerSeq.size());
    bitStringContent.insert(bitStringContent.end(), innerLen.begin(), innerLen.end());
    bitStringContent.insert(bitStringContent.end(), innerSeq.begin(), innerSeq.end());

    std::vector<BYTE> bitLen = EncodeDERLength(bitStringContent.size());
    bitString.insert(bitString.end(), bitLen.begin(), bitLen.end());
    bitString.insert(bitString.end(), bitStringContent.begin(), bitStringContent.end());

    // RSA algorithm identifier
    BYTE rsaAlgId[] = { 0x30, 0x0D, 0x06, 0x09, 0x2A, 0x86, 0x48, 0x86, 0xF7, 0x0D, 0x01, 0x01, 0x01, 0x05, 0x00 };

    // Build outer SEQUENCE
    derKey.push_back(0x30); // SEQUENCE tag
    size_t totalLen = sizeof(rsaAlgId) + bitString.size();
    std::vector<BYTE> outerLen = EncodeDERLength(totalLen);
    derKey.insert(derKey.end(), outerLen.begin(), outerLen.end());
    derKey.insert(derKey.end(), rsaAlgId, rsaAlgId + sizeof(rsaAlgId));
    derKey.insert(derKey.end(), bitString.begin(), bitString.end());

    // Convert to char vector
    std::vector<char> result(derKey.begin(), derKey.end());

    std::cout << "[CNG-RSA] Converted CNG blob (" << cngBlob.size() << " bytes) to DER format (" << result.size() << " bytes)" << std::endl;
    return result;
}

// Windows CNG RSAPublicWrapper implementation
RSAPublicWrapper::RSAPublicWrapper(const char* key, size_t keylen) : publicKeyImpl(nullptr) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid RSA key data provided");
    }
    keyData.assign(key, key + keylen);

    // Import the public key using CNG
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        BCRYPT_KEY_HANDLE* hPublicKey = new BCRYPT_KEY_HANDLE(NULL);
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, hPublicKey, (PUCHAR)key, (ULONG)keylen, 0);
        CheckCNGStatus(status, "Import public key");
        publicKeyImpl = hPublicKey;
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[CNG-RSA] Public key loaded: " << keylen << " bytes" << std::endl;
}

RSAPublicWrapper::RSAPublicWrapper(const std::string& filename) : publicKeyImpl(nullptr) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open key file: " + filename);
    }

    file.seekg(0, std::ios::end);
    size_t fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    keyData.resize(fileSize);
    file.read(keyData.data(), fileSize);

    // Import the public key using CNG
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        BCRYPT_KEY_HANDLE* hPublicKey = new BCRYPT_KEY_HANDLE(NULL);
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, hPublicKey, (PUCHAR)keyData.data(), (ULONG)keyData.size(), 0);
        CheckCNGStatus(status, "Import public key");
        publicKeyImpl = hPublicKey;
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[CNG-RSA] RSAPublicWrapper loaded from file: " << filename << std::endl;
}

RSAPublicWrapper::~RSAPublicWrapper() {
    if (publicKeyImpl) {
        BCRYPT_KEY_HANDLE* hKey = static_cast<BCRYPT_KEY_HANDLE*>(publicKeyImpl);
        if (*hKey) {
            BCryptDestroyKey(*hKey);
        }
        delete hKey;
        publicKeyImpl = nullptr;
    }
}

std::string RSAPublicWrapper::getPublicKey() {
    return std::string(keyData.begin(), keyData.end());
}

void RSAPublicWrapper::getPublicKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < keyData.size()) {
        throw std::invalid_argument("Invalid output buffer");
    }
    memcpy(keyout, keyData.data(), keyData.size());
}

std::string RSAPublicWrapper::encrypt(const std::string& plain) {
    return encrypt(plain.c_str(), plain.size());
}

std::string RSAPublicWrapper::encrypt(const char* plain, size_t length) {
    if (!publicKeyImpl) {
        throw std::runtime_error("RSA public key not initialized");
    }

    try {
        BCRYPT_KEY_HANDLE* hKey = static_cast<BCRYPT_KEY_HANDLE*>(publicKeyImpl);

        // Set up padding info for OAEP with SHA-256
        BCRYPT_OAEP_PADDING_INFO paddingInfo = { 0 };
        paddingInfo.pszAlgId = BCRYPT_SHA256_ALGORITHM;

        // Calculate required output buffer size
        ULONG encryptedSize = 0;
        NTSTATUS status = BCryptEncrypt(*hKey, (PUCHAR)plain, (ULONG)length, &paddingInfo, NULL, 0, NULL, 0, &encryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Calculate encryption size");

        std::string encrypted(encryptedSize, 0);
        status = BCryptEncrypt(*hKey, (PUCHAR)plain, (ULONG)length, &paddingInfo, NULL, 0, (PUCHAR)encrypted.data(), encryptedSize, &encryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Encrypt data");

        std::cout << "[CNG-RSA] Encrypted " << length << " bytes to " << encryptedSize << " bytes" << std::endl;
        return encrypted;
    } catch (const std::exception& e) {
        throw std::runtime_error("RSA encryption failed: " + std::string(e.what()));
    }
}

// RSAPrivateWrapper implementation using Windows CNG
RSAPrivateWrapper::RSAPrivateWrapper() : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        // Generate a new 1024-bit RSA key pair
        BCRYPT_KEY_HANDLE hPrivateKey = NULL;
        status = BCryptGenerateKeyPair(hAlg, &hPrivateKey, BITS, 0);
        CheckCNGStatus(status, "Generate key pair");

        status = BCryptFinalizeKeyPair(hPrivateKey, 0);
        CheckCNGStatus(status, "Finalize key pair");

        // Export the private key
        ULONG privateKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPRIVATE_BLOB, NULL, 0, &privateKeySize, 0);
        CheckCNGStatus(status, "Calculate private key export size");

        privateKeyData.resize(privateKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPRIVATE_BLOB, (PUCHAR)privateKeyData.data(), privateKeySize, &privateKeySize, 0);
        CheckCNGStatus(status, "Export private key");

        // Export the public key
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Store key handles
        privateKeyImpl = new BCRYPT_KEY_HANDLE(hPrivateKey);

        // Import the public key to a separate handle for encryption
        BCRYPT_KEY_HANDLE hPublicKey = NULL;
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)publicKeyData.data(), publicKeySize, 0);
        CheckCNGStatus(status, "Import public key");
        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);

    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[CNG-RSA] RSAPrivateWrapper generated new 1024-bit key pair" << std::endl;
}

RSAPrivateWrapper::RSAPrivateWrapper(const char* key, size_t keylen) : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }

    privateKeyData.assign(key, key + keylen);

    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        // Import the private key from buffer
        BCRYPT_KEY_HANDLE hPrivateKey = NULL;
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPRIVATE_BLOB, &hPrivateKey, (PUCHAR)key, (ULONG)keylen, 0);
        CheckCNGStatus(status, "Import private key");
        privateKeyImpl = new BCRYPT_KEY_HANDLE(hPrivateKey);

        // Export the public key part
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Import the public key to a separate handle for encryption
        BCRYPT_KEY_HANDLE hPublicKey = NULL;
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)publicKeyData.data(), publicKeySize, 0);
        CheckCNGStatus(status, "Import public key");
        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);

    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[CNG-RSA] RSAPrivateWrapper loaded from buffer: " << keylen << " bytes" << std::endl;
}

RSAPrivateWrapper::RSAPrivateWrapper(const std::string& filename) : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open key file: " + filename);
    }

    file.seekg(0, std::ios::end);
    size_t fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    privateKeyData.resize(fileSize);
    file.read(privateKeyData.data(), fileSize);

    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        // Import the private key from file data
        BCRYPT_KEY_HANDLE hPrivateKey = NULL;
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPRIVATE_BLOB, &hPrivateKey, (PUCHAR)privateKeyData.data(), (ULONG)privateKeyData.size(), 0);
        CheckCNGStatus(status, "Import private key");
        privateKeyImpl = new BCRYPT_KEY_HANDLE(hPrivateKey);

        // Export the public key part
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Import the public key to a separate handle for encryption
        BCRYPT_KEY_HANDLE hPublicKey = NULL;
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)publicKeyData.data(), publicKeySize, 0);
        CheckCNGStatus(status, "Import public key");
        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);

    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[CNG-RSA] RSAPrivateWrapper loaded from file: " << filename << std::endl;
}

RSAPrivateWrapper::~RSAPrivateWrapper() {
    if (privateKeyImpl) {
        BCRYPT_KEY_HANDLE* hKey = static_cast<BCRYPT_KEY_HANDLE*>(privateKeyImpl);
        if (*hKey) {
            BCryptDestroyKey(*hKey);
        }
        delete hKey;
        privateKeyImpl = nullptr;
    }
    if (publicKeyImpl) {
        BCRYPT_KEY_HANDLE* hKey = static_cast<BCRYPT_KEY_HANDLE*>(publicKeyImpl);
        if (*hKey) {
            BCryptDestroyKey(*hKey);
        }
        delete hKey;
        publicKeyImpl = nullptr;
    }
}

std::string RSAPrivateWrapper::getPrivateKey() {
    if (!privateKeyImpl) {
        throw std::runtime_error("RSA private key not initialized");
    }

    try {
        // Export the private key in CNG blob format
        BCRYPT_KEY_HANDLE* hKey = static_cast<BCRYPT_KEY_HANDLE*>(privateKeyImpl);

        ULONG privateKeySize = 0;
        NTSTATUS status = BCryptExportKey(*hKey, NULL, BCRYPT_RSAPRIVATE_BLOB, NULL, 0, &privateKeySize, 0);
        CheckCNGStatus(status, "Calculate private key export size");

        std::vector<char> exportedKey(privateKeySize);
        status = BCryptExportKey(*hKey, NULL, BCRYPT_RSAPRIVATE_BLOB, (PUCHAR)exportedKey.data(), privateKeySize, &privateKeySize, 0);
        CheckCNGStatus(status, "Export private key");

        std::cout << "[CNG-RSA] Exported private key: " << privateKeySize << " bytes" << std::endl;
        return std::string(exportedKey.begin(), exportedKey.end());
    } catch (const std::exception& e) {
        throw std::runtime_error("Failed to export private key: " + std::string(e.what()));
    }
}

void RSAPrivateWrapper::getPrivateKey(char* keyout, size_t keylen) {
    std::string key = getPrivateKey();
    if (!keyout || keylen < key.length()) {
        throw std::invalid_argument("Invalid output buffer");
    }
    memcpy(keyout, key.data(), key.length());
}

std::string RSAPrivateWrapper::getPublicKey() {
    // Return stored public key data converted to DER format
    if (publicKeyData.empty()) {
        throw std::runtime_error("No public key data available");
    }

    try {
        // Convert CNG blob to DER format for server compatibility
        std::vector<char> derKey = ConvertCNGPublicKeyToDER(publicKeyData);
        return std::string(derKey.begin(), derKey.end());
    } catch (const std::exception& e) {
        throw std::runtime_error("Failed to convert public key to DER format: " + std::string(e.what()));
    }
}

void RSAPrivateWrapper::getPublicKey(char* keyout, size_t keylen) {
    std::string key = getPublicKey();
    if (!keyout || keylen < key.length()) {
        throw std::invalid_argument("Invalid output buffer");
    }
    memcpy(keyout, key.data(), key.length());
}

std::string RSAPrivateWrapper::decrypt(const std::string& cipher) {
    return decrypt(cipher.c_str(), cipher.size());
}

std::string RSAPrivateWrapper::decrypt(const char* cipher, size_t length) {
    if (!privateKeyImpl) {
        throw std::runtime_error("RSA private key not initialized");
    }

    try {
        BCRYPT_KEY_HANDLE* hKey = static_cast<BCRYPT_KEY_HANDLE*>(privateKeyImpl);

        // Set up padding info for OAEP with SHA-256
        BCRYPT_OAEP_PADDING_INFO paddingInfo = { 0 };
        paddingInfo.pszAlgId = BCRYPT_SHA256_ALGORITHM;

        // Calculate required output buffer size
        ULONG decryptedSize = 0;
        NTSTATUS status = BCryptDecrypt(*hKey, (PUCHAR)cipher, (ULONG)length, &paddingInfo, NULL, 0, NULL, 0, &decryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Calculate decryption size");

        std::string decrypted(decryptedSize, 0);
        status = BCryptDecrypt(*hKey, (PUCHAR)cipher, (ULONG)length, &paddingInfo, NULL, 0, (PUCHAR)decrypted.data(), decryptedSize, &decryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Decrypt data");

        std::cout << "[CNG-RSA] Decrypted " << length << " bytes to " << decryptedSize << " bytes" << std::endl;
        return decrypted;
    } catch (const std::exception& e) {
        throw std::runtime_error("RSA decryption failed: " + std::string(e.what()));
    }
}
