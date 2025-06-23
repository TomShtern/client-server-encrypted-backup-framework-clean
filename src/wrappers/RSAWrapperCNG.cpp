#include "../../include/wrappers/RSAWrapper.h"
#include <fstream>
#include <stdexcept>
#include <iostream>

// Helper function to check CNG status and throw exception on failure
void CheckCNGStatus(NTSTATUS status, const std::string& operation) {
    if (status != STATUS_SUCCESS) {
        char errorMsg[256];
        sprintf_s(errorMsg, "CNG operation failed: %s (Status: 0x%08X)", operation.c_str(), status);
        throw std::runtime_error(errorMsg);
    }
}

// RSAPublicWrapper implementation (using CNG backend)
RSAPublicWrapper::RSAPublicWrapper(const char* key, size_t keylen) : hPublicKey(NULL) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }

    keyData.assign(key, key + keylen);

    // Import the public key from DER format
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        DWORD paramSize = 0;
        DWORD paramSizeSize = sizeof(DWORD);
        status = BCryptGetProperty(hAlg, BCRYPT_OBJECT_LENGTH, (PBYTE)&paramSize, paramSizeSize, &paramSizeSize, 0);
        CheckCNGStatus(status, "Get object length property");

        std::vector<BYTE> keyBlob(keylen);
        memcpy(keyBlob.data(), key, keylen);

        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, keyBlob.data(), (ULONG)keylen, 0);
        CheckCNGStatus(status, "Import public key");
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPublicWrapper: Successfully loaded " << keylen << "-byte DER public key" << std::endl;
}

RSAPublicWrapper::RSAPublicWrapper(const std::string& filename) : hPublicKey(NULL) {
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

    keyData.assign(fileData.begin(), fileData.end());

    // Import the public key from DER format
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        DWORD paramSize = 0;
        DWORD paramSizeSize = sizeof(DWORD);
        status = BCryptGetProperty(hAlg, BCRYPT_OBJECT_LENGTH, (PBYTE)&paramSize, paramSizeSize, &paramSizeSize, 0);
        CheckCNGStatus(status, "Get object length property");

        std::vector<BYTE> keyBlob(keyData.size());
        memcpy(keyBlob.data(), keyData.data(), keyData.size());

        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, keyBlob.data(), (ULONG)keyData.size(), 0);
        CheckCNGStatus(status, "Import public key");
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPublicWrapper: Successfully loaded public key from " << filename << std::endl;
}

RSAPublicWrapper::~RSAPublicWrapper() {
    if (hPublicKey) {
        BCryptDestroyKey(hPublicKey);
        hPublicKey = NULL;
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
    if (!hPublicKey) {
        throw std::runtime_error("RSA public key not initialized");
    }

    try {
        // Set up padding info for OAEP with SHA-256
        BCRYPT_OAEP_PADDING_INFO paddingInfo = { 0 };
        paddingInfo.pszAlgId = BCRYPT_SHA256_ALGORITHM;

        // Calculate required output buffer size
        ULONG encryptedSize = 0;
        NTSTATUS status = BCryptEncrypt(hPublicKey, (PUCHAR)plain, (ULONG)length, &paddingInfo, NULL, 0, NULL, 0, &encryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Calculate encryption size");

        std::string encrypted(encryptedSize, 0);
        status = BCryptEncrypt(hPublicKey, (PUCHAR)plain, (ULONG)length, &paddingInfo, NULL, 0, (PUCHAR)encrypted.data(), encryptedSize, &encryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Encrypt data");

        return encrypted;
    } catch (const std::exception& e) {
        throw std::runtime_error("RSA encryption failed: " + std::string(e.what()));
    }
}

// RSAPrivateWrapper implementation (using CNG backend)
RSAPrivateWrapper::RSAPrivateWrapper() : hPrivateKey(NULL), hPublicKey(NULL) {
    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        // Generate a new 1024-bit RSA key pair
        status = BCryptGenerateKeyPair(hAlg, &hPrivateKey, BITS, 0);
        CheckCNGStatus(status, "Generate key pair");

        status = BCryptFinalizeKeyPair(hPrivateKey, 0);
        CheckCNGStatus(status, "Finalize key pair");

        // Export the private key in DER format
        ULONG privateKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPRIVATE_BLOB, NULL, 0, &privateKeySize, 0);
        CheckCNGStatus(status, "Calculate private key export size");

        privateKeyData.resize(privateKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPRIVATE_BLOB, (PUCHAR)privateKeyData.data(), privateKeySize, &privateKeySize, 0);
        CheckCNGStatus(status, "Export private key");

        // Export the public key in DER format
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Import the public key to a separate handle for encryption
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)publicKeyData.data(), publicKeySize, 0);
        CheckCNGStatus(status, "Import public key");
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPrivateKey) BCryptDestroyKey(hPrivateKey);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPrivateWrapper: Successfully generated 1024-bit RSA key pair" << std::endl;
}

RSAPrivateWrapper::RSAPrivateWrapper(const char* key, size_t keylen) : hPrivateKey(NULL), hPublicKey(NULL) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }

    privateKeyData.assign(key, key + keylen);

    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        // Import the private key from DER format
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPRIVATE_BLOB, &hPrivateKey, (PUCHAR)key, (ULONG)keylen, 0);
        CheckCNGStatus(status, "Import private key");

        // Export the public key part
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Import the public key to a separate handle for encryption
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)publicKeyData.data(), publicKeySize, 0);
        CheckCNGStatus(status, "Import public key");
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPrivateKey) BCryptDestroyKey(hPrivateKey);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPrivateWrapperCNG: Successfully loaded private key from buffer" << std::endl;
}

RSAPrivateWrapperCNG::RSAPrivateWrapperCNG(const std::string& filename) : hPrivateKey(NULL), hPublicKey(NULL) {
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

    BCRYPT_ALG_HANDLE hAlg = NULL;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RSA_ALGORITHM, NULL, 0);
    CheckCNGStatus(status, "Open RSA algorithm provider");

    try {
        // Import the private key from DER format
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPRIVATE_BLOB, &hPrivateKey, (PUCHAR)privateKeyData.data(), (ULONG)privateKeyData.size(), 0);
        CheckCNGStatus(status, "Import private key");

        // Export the public key part
        ULONG publicKeySize = 0;
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, NULL, 0, &publicKeySize, 0);
        CheckCNGStatus(status, "Calculate public key export size");

        publicKeyData.resize(publicKeySize);
        status = BCryptExportKey(hPrivateKey, NULL, BCRYPT_RSAPUBLIC_BLOB, (PUCHAR)publicKeyData.data(), publicKeySize, &publicKeySize, 0);
        CheckCNGStatus(status, "Export public key");

        // Import the public key to a separate handle for encryption
        status = BCryptImportKeyPair(hAlg, NULL, BCRYPT_RSAPUBLIC_BLOB, &hPublicKey, (PUCHAR)publicKeyData.data(), publicKeySize, 0);
        CheckCNGStatus(status, "Import public key");
    } catch (...) {
        if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
        if (hPrivateKey) BCryptDestroyKey(hPrivateKey);
        if (hPublicKey) BCryptDestroyKey(hPublicKey);
        throw;
    }

    if (hAlg) BCryptCloseAlgorithmProvider(hAlg, 0);
    std::cout << "[DEBUG] RSAPrivateWrapperCNG: Successfully loaded private key from " << filename << std::endl;
}

RSAPrivateWrapperCNG::~RSAPrivateWrapperCNG() {
    if (hPrivateKey) {
        BCryptDestroyKey(hPrivateKey);
        hPrivateKey = NULL;
    }
    if (hPublicKey) {
        BCryptDestroyKey(hPublicKey);
        hPublicKey = NULL;
    }
}

std::string RSAPrivateWrapperCNG::getPrivateKey() {
    return std::string(privateKeyData.begin(), privateKeyData.end());
}

void RSAPrivateWrapperCNG::getPrivateKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < privateKeyData.size()) {
        throw std::invalid_argument("Invalid output buffer or insufficient size");
    }
    std::memcpy(keyout, privateKeyData.data(), privateKeyData.size());
}

std::string RSAPrivateWrapperCNG::getPublicKey() {
    return std::string(publicKeyData.begin(), publicKeyData.end());
}

void RSAPrivateWrapperCNG::getPublicKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < publicKeyData.size()) {
        throw std::invalid_argument("Invalid output buffer or insufficient size");
    }
    std::memcpy(keyout, publicKeyData.data(), publicKeyData.size());
}

std::string RSAPrivateWrapperCNG::decrypt(const std::string& cipher) {
    return decrypt(cipher.c_str(), cipher.size());
}

std::string RSAPrivateWrapperCNG::decrypt(const char* cipher, size_t length) {
    if (!hPrivateKey) {
        throw std::runtime_error("RSA private key not initialized");
    }

    try {
        // Set up padding info for OAEP with SHA-256
        BCRYPT_OAEP_PADDING_INFO paddingInfo = { 0 };
        paddingInfo.pszAlgId = BCRYPT_SHA256_ALGORITHM;

        // Calculate required output buffer size
        ULONG decryptedSize = 0;
        NTSTATUS status = BCryptDecrypt(hPrivateKey, (PUCHAR)cipher, (ULONG)length, &paddingInfo, NULL, 0, NULL, 0, &decryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Calculate decryption size");

        std::string decrypted(decryptedSize, 0);
        status = BCryptDecrypt(hPrivateKey, (PUCHAR)cipher, (ULONG)length, &paddingInfo, NULL, 0, (PUCHAR)decrypted.data(), decryptedSize, &decryptedSize, BCRYPT_PAD_OAEP);
        CheckCNGStatus(status, "Decrypt data");

        return decrypted;
    } catch (const std::exception& e) {
        throw std::runtime_error("RSA decryption failed: " + std::string(e.what()));
    }
}
