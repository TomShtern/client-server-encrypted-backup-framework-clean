#include "../../include/wrappers/RSAWrapper.h"
#include <fstream>
#include <stdexcept>
#include <iostream>
#include <windows.h>
#include <bcrypt.h>
#include <ntstatus.h>
#pragma comment(lib, "bcrypt.lib")

// Helper function to check CNG status and throw exception on failure
void CheckCNGStatus(NTSTATUS status, const std::string& operation) {
    if (status != STATUS_SUCCESS) {
        char errorMsg[256];
        sprintf_s(errorMsg, "CNG operation failed: %s (Status: 0x%08X)", operation.c_str(), status);
        throw std::runtime_error(errorMsg);
    }
}

// RSAPrivateWrapper implementation using Windows CNG
RSAPrivateWrapper::RSAPrivateWrapper() {
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    BCRYPT_KEY_HANDLE hPrivateKey = NULL;
    BCRYPT_KEY_HANDLE hPublicKey = NULL;

    try {
        std::cout << "[DEBUG] RSAPrivateWrapper: Generating 1024-bit RSA key pair with Windows CNG..." << std::endl;
        
        // Generate a new 1024-bit RSA key pair
        status = BCryptGenerateKeyPair(hAlg, &hPrivateKey, 1024, 0);
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

        // Store the key handles
        privateKeyImpl = new BCRYPT_KEY_HANDLE(hPrivateKey);
        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);

    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPrivateKey) BCryptDestroyKey(hPrivateKey);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPrivateWrapper: Successfully generated 1024-bit RSA key pair with CNG" << std::endl;
}

RSAPrivateWrapper::RSAPrivateWrapper(const char* key, size_t keylen) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }
    privateKeyData.assign(key, key + keylen);
    
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    BCRYPT_KEY_HANDLE hPrivateKey = NULL;
    BCRYPT_KEY_HANDLE hPublicKey = NULL;

    try {
        // Import the private key
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPRIVATE_BLOB, &hPrivateKey, (PUCHAR)key, (ULONG)keylen, 0);
        CheckCNGStatus(status, "Import private key");

        // Export the public key part
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Store the key handles
        privateKeyImpl = new BCRYPT_KEY_HANDLE(hPrivateKey);
        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);

    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPrivateKey) BCryptDestroyKey(hPrivateKey);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded private key from buffer with CNG" << std::endl;
}

RSAPrivateWrapper::RSAPrivateWrapper(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filename);
    }
    
    // Read file content
    std::string fileData((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();
    
    if (fileData.empty()) {
        throw std::runtime_error("Empty key file: " + filename);
    }
    
    privateKeyData.assign(fileData.begin(), fileData.end());
    
    // Initialize using the same logic as buffer constructor
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    BCRYPT_KEY_HANDLE hPrivateKey = NULL;
    BCRYPT_KEY_HANDLE hPublicKey = NULL;

    try {
        // Import the private key
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPRIVATE_BLOB, &hPrivateKey, (PUCHAR)privateKeyData.data(), (ULONG)privateKeyData.size(), 0);
        CheckCNGStatus(status, "Import private key");

        // Export the public key part
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Store the key handles
        privateKeyImpl = new BCRYPT_KEY_HANDLE(hPrivateKey);
        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);

    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPrivateKey) BCryptDestroyKey(hPrivateKey);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    
    std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded private key from " << filename << " with CNG" << std::endl;
}

RSAPrivateWrapper::~RSAPrivateWrapper() {
    if (privateKeyImpl) {
        BCRYPT_KEY_HANDLE* hPrivateKey = static_cast<BCRYPT_KEY_HANDLE*>(privateKeyImpl);
        if (*hPrivateKey) BCryptDestroyKey(*hPrivateKey);
        delete hPrivateKey;
        privateKeyImpl = nullptr;
    }
    if (publicKeyImpl) {
        BCRYPT_KEY_HANDLE* hPublicKey = static_cast<BCRYPT_KEY_HANDLE*>(publicKeyImpl);
        if (*hPublicKey) BCryptDestroyKey(*hPublicKey);
        delete hPublicKey;
        publicKeyImpl = nullptr;
    }
}

std::string RSAPrivateWrapper::getPrivateKey() {
    return std::string(privateKeyData.begin(), privateKeyData.end());
}

void RSAPrivateWrapper::getPrivateKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < privateKeyData.size()) {
        throw std::invalid_argument("Invalid output buffer or insufficient size");
    }
    std::memcpy(keyout, privateKeyData.data(), privateKeyData.size());
}

std::string RSAPrivateWrapper::getPublicKey() {
    return std::string(publicKeyData.begin(), publicKeyData.end());
}

void RSAPrivateWrapper::getPublicKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < publicKeyData.size()) {
        throw std::invalid_argument("Invalid output buffer or insufficient size");
    }
    std::memcpy(keyout, publicKeyData.data(), publicKeyData.size());
}

std::string RSAPrivateWrapper::decrypt(const std::string& cipher) {
    return decrypt(cipher.c_str(), cipher.size());
}

std::string RSAPrivateWrapper::decrypt(const char* cipher, size_t length) {
    if (!privateKeyImpl) {
        throw std::runtime_error("RSA private key not initialized");
    }

    try {
        BCRYPT_KEY_HANDLE* hPrivateKey = static_cast<BCRYPT_KEY_HANDLE*>(privateKeyImpl);
        
        // Set up padding info for OAEP with SHA-256
        BCRYPT_OAEP_PADDING_INFO paddingInfo = { 0 };
        paddingInfo.pszAlgId = BCRYPT_SHA256_ALGORITHM;

        // Calculate required output buffer size
        ULONG decryptedSize = 0;
        NTSTATUS status = BCryptDecrypt(*hPrivateKey, (PUCHAR)cipher, (ULONG)length, &paddingInfo, NULL, 0, NULL, 0, &decryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Calculate decryption size");

        std::string decrypted(decryptedSize, 0);
        status = BCryptDecrypt(*hPrivateKey, (PUCHAR)cipher, (ULONG)length, &paddingInfo, NULL, 0, (PUCHAR)decrypted.data(), decryptedSize, &decryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Decrypt data");

        std::cout << "[DEBUG] RSAPrivateWrapper: Successfully decrypted " << length << " bytes with CNG" << std::endl;
        return decrypted;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: CNG decryption failed: " << e.what() << std::endl;
        throw std::runtime_error("RSA decryption failed: " + std::string(e.what()));
    }
}

// RSAPublicWrapper implementation using Windows CNG
RSAPublicWrapper::RSAPublicWrapper(const char* key, size_t keylen) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }

    keyData.assign(key, key + keylen);

    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    BCRYPT_KEY_HANDLE hPublicKey = NULL;

    try {
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)key, (ULONG)keylen, 0);
        CheckCNGStatus(status, "Import public key");
        
        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPublicWrapper: Successfully loaded " << keylen << "-byte public key with CNG" << std::endl;
}

RSAPublicWrapper::RSAPublicWrapper(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filename);
    }

    // Read file content
    std::string fileData((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();

    if (fileData.empty()) {
        throw std::runtime_error("Empty key file: " + filename);
    }

    // Initialize using the same logic as buffer constructor
    keyData.assign(fileData.begin(), fileData.end());

    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    BCRYPT_KEY_HANDLE hPublicKey = NULL;

    try {
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)fileData.c_str(), (ULONG)fileData.length(), 0);
        CheckCNGStatus(status, "Import public key");

        publicKeyImpl = new BCRYPT_KEY_HANDLE(hPublicKey);
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    
    std::cout << "[DEBUG] RSAPublicWrapper: Successfully loaded public key from " << filename << " with CNG" << std::endl;
}

RSAPublicWrapper::~RSAPublicWrapper() {
    if (publicKeyImpl) {
        BCRYPT_KEY_HANDLE* hPublicKey = static_cast<BCRYPT_KEY_HANDLE*>(publicKeyImpl);
        if (*hPublicKey) BCryptDestroyKey(*hPublicKey);
        delete hPublicKey;
        publicKeyImpl = nullptr;
    }
}

std::string RSAPublicWrapper::getPublicKey() {
    return std::string(keyData.begin(), keyData.end());
}

void RSAPublicWrapper::getPublicKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < keyData.size()) {
        throw std::invalid_argument("Invalid output buffer or insufficient size");
    }
    std::memcpy(keyout, keyData.data(), keyData.size());
}

std::string RSAPublicWrapper::encrypt(const std::string& plain) {
    return encrypt(plain.c_str(), plain.size());
}

std::string RSAPublicWrapper::encrypt(const char* plain, size_t length) {
    if (!publicKeyImpl) {
        throw std::runtime_error("RSA public key not initialized");
    }

    try {
        BCRYPT_KEY_HANDLE* hPublicKey = static_cast<BCRYPT_KEY_HANDLE*>(publicKeyImpl);
        
        // Set up padding info for OAEP with SHA-256
        BCRYPT_OAEP_PADDING_INFO paddingInfo = { 0 };
        paddingInfo.pszAlgId = BCRYPT_SHA256_ALGORITHM;

        // Calculate required output buffer size
        ULONG encryptedSize = 0;
        NTSTATUS status = BCryptEncrypt(*hPublicKey, (PUCHAR)plain, (ULONG)length, &paddingInfo, NULL, 0, NULL, 0, &encryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Calculate encryption size");

        std::string encrypted(encryptedSize, 0);
        status = BCryptEncrypt(*hPublicKey, (PUCHAR)plain, (ULONG)length, &paddingInfo, NULL, 0, (PUCHAR)encrypted.data(), encryptedSize, &encryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Encrypt data");

        std::cout << "[DEBUG] RSAPublicWrapper: Successfully encrypted " << length << " bytes with CNG" << std::endl;
        return encrypted;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] RSAPublicWrapper: CNG encryption failed: " << e.what() << std::endl;
        throw std::runtime_error("RSA encryption failed: " + std::string(e.what()));
    }
}
