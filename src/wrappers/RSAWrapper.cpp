#include "../../include/wrappers/RSAWrapper.h"
#include <rsa.h>
#include <osrng.h>
#include <base64.h>
#include <files.h>
#include <stdexcept>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <atomic>
#include <exception>
#include <future>
#include <atomic>

// Windows headers for entropy sources
#ifdef _WIN32
#include <windows.h>
#include <process.h>
#endif

// RSAPublicWrapper implementation using Crypto++
RSAPublicWrapper::RSAPublicWrapper(const char* key, size_t keylen) : publicKeyImpl(nullptr) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }
    keyData.assign(key, key + keylen);
    
    try {
        // Load the public key from DER format
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(key), keylen);
        queue.MessageEnd();
        
        publicKeyImpl = new CryptoPP::RSA::PublicKey();
        CryptoPP::RSA::PublicKey* publicKey = static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
        publicKey->BERDecode(queue);
        
        std::cout << "[DEBUG] RSAPublicWrapper: Successfully loaded " << keylen << "-byte public key from buffer" << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPublicWrapper: Failed to load public key from buffer: " << e.what() << std::endl;
        throw std::runtime_error("Failed to load RSA public key from buffer");
    }
}

RSAPublicWrapper::RSAPublicWrapper(const std::string& filename) : publicKeyImpl(nullptr) {
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
    
    try {
        // Load the public key from DER format
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(keyData.data()), keyData.size());
        queue.MessageEnd();
        
        publicKeyImpl = new CryptoPP::RSA::PublicKey();
        CryptoPP::RSA::PublicKey* publicKey = static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
        publicKey->BERDecode(queue);
        
        std::cout << "[DEBUG] RSAPublicWrapper: Successfully loaded public key from " << filename << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPublicWrapper: Failed to load public key from file " << filename << ": " << e.what() << std::endl;
        throw std::runtime_error("Failed to load RSA public key from file: " + filename);
    }
}

RSAPublicWrapper::~RSAPublicWrapper() {
    if (publicKeyImpl) {
        delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
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
        CryptoPP::RSA::PublicKey* publicKey = static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);

        // Use AutoSeededRandomPool for consistency
        CryptoPP::AutoSeededRandomPool rng;

        // Use OAEP with SHA-256 for spec compliance
        CryptoPP::RSAES_OAEP_SHA256_Encryptor encryptor(*publicKey);
        
        std::string cipher;
        CryptoPP::StringSource ss(reinterpret_cast<const CryptoPP::byte*>(plain), length, true,
            new CryptoPP::PK_EncryptorFilter(rng, encryptor, new CryptoPP::StringSink(cipher)));
        
        std::cout << "[DEBUG] RSAPublicWrapper: Successfully encrypted " << length << " bytes" << std::endl;
        return cipher;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPublicWrapper: Encryption failed: " << e.what() << std::endl;
        throw std::runtime_error("RSA encryption failed: " + std::string(e.what()));
    }
}

// RSAPrivateWrapper implementation using Crypto++
RSAPrivateWrapper::RSAPrivateWrapper() : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
    std::cout << "[DEBUG] RSAPrivateWrapper: Constructor called for " << BITS << " bits" << std::endl;
    std::cout << "[DEBUG] RSAPrivateWrapper: Starting RSA key generation with AutoSeededRandomPool..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();

    try {
        // Use AutoSeededRandomPool as recommended for Crypto++
        CryptoPP::AutoSeededRandomPool rng;

        std::cout << "[DEBUG] RSAPrivateWrapper: AutoSeededRandomPool created successfully." << std::endl;

        privateKeyImpl = new CryptoPP::RSA::PrivateKey();
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);

        std::cout << "[DEBUG] RSAPrivateWrapper: Generating 1024-bit RSA key pair..." << std::endl;
        privateKey->GenerateRandomWithKeySize(rng, 1024);

        std::cout << "[DEBUG] RSAPrivateWrapper: RSA key generation completed successfully!" << std::endl;

        // Extract public key from private key
        publicKeyImpl = new CryptoPP::RSA::PublicKey(*privateKey);

        // Save keys to DER format
        CryptoPP::ByteQueue privateQueue, publicQueue;
        privateKey->DEREncode(privateQueue);
        static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl)->DEREncode(publicQueue);
        privateQueue.MessageEnd();
        publicQueue.MessageEnd();

        size_t privateSize = privateQueue.MaxRetrievable();
        size_t publicSize = publicQueue.MaxRetrievable();
        privateKeyData.resize(privateSize);
        publicKeyData.resize(publicSize);
        privateQueue.Get(reinterpret_cast<CryptoPP::byte*>(&privateKeyData[0]), privateSize);
        publicQueue.Get(reinterpret_cast<CryptoPP::byte*>(&publicKeyData[0]), publicSize);

        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start);
        std::cout << "[DEBUG] RSAPrivateWrapper: Successfully generated " << BITS << "-bit RSA key pair in " << duration.count() << "ms" << std::endl;
        std::cout << "[DEBUG] RSAPrivateWrapper: Private key size: " << privateKeyData.size() << " bytes, Public key size: " << publicKeyData.size() << " bytes" << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Key generation failed: " << e.what() << std::endl;
        if (privateKeyImpl) {
            delete static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
            privateKeyImpl = nullptr;
        }
        if (publicKeyImpl) {
            delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
            publicKeyImpl = nullptr;
        }
        throw std::runtime_error("Failed to generate RSA keys: " + std::string(e.what()));
    }
}

RSAPrivateWrapper::RSAPrivateWrapper(const char* key, size_t keylen) : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }
    privateKeyData.assign(key, key + keylen);
    
    try {
        // Load the private key from DER format
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(key), keylen);
        queue.MessageEnd();
        
        privateKeyImpl = new CryptoPP::RSA::PrivateKey();
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
        privateKey->BERDecode(queue);
        
        // Extract public key
        publicKeyImpl = new CryptoPP::RSA::PublicKey(*privateKey);
        
        // Save public key to DER format
        CryptoPP::ByteQueue publicQueue;
        static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl)->DEREncode(publicQueue);
        publicQueue.MessageEnd();
        
        size_t publicSize = publicQueue.MaxRetrievable();
        publicKeyData.resize(publicSize);
        publicQueue.Get(reinterpret_cast<CryptoPP::byte*>(&publicKeyData[0]), publicSize);
        
        std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded private key from buffer" << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Failed to load private key from buffer: " << e.what() << std::endl;
        throw std::runtime_error("Failed to load RSA private key from buffer");
    }
}

RSAPrivateWrapper::RSAPrivateWrapper(const std::string& filename) : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
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
    
    try {
        // Load the private key from DER format
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(privateKeyData.data()), privateKeyData.size());
        queue.MessageEnd();
        
        privateKeyImpl = new CryptoPP::RSA::PrivateKey();
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
        privateKey->BERDecode(queue);
        
        // Extract public key
        publicKeyImpl = new CryptoPP::RSA::PublicKey(*privateKey);
        
        // Save public key to DER format
        CryptoPP::ByteQueue publicQueue;
        static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl)->DEREncode(publicQueue);
        publicQueue.MessageEnd();
        
        size_t publicSize = publicQueue.MaxRetrievable();
        publicKeyData.resize(publicSize);
        publicQueue.Get(reinterpret_cast<CryptoPP::byte*>(&publicKeyData[0]), publicSize);
        
        std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded private key from " << filename << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Failed to load private key from file " << filename << ": " << e.what() << std::endl;
        throw std::runtime_error("Failed to load RSA private key from file: " + filename);
    }
}

RSAPrivateWrapper::~RSAPrivateWrapper() {
    if (privateKeyImpl) {
        delete static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
        privateKeyImpl = nullptr;
    }
    if (publicKeyImpl) {
        delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
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
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);

        // Use AutoSeededRandomPool for consistency
        CryptoPP::AutoSeededRandomPool rng;

        // Use OAEP with SHA-256 for spec compliance
        CryptoPP::RSAES_OAEP_SHA256_Decryptor decryptor(*privateKey);

        std::string plain;
        CryptoPP::StringSource ss(reinterpret_cast<const CryptoPP::byte*>(cipher), length, true,
            new CryptoPP::PK_DecryptorFilter(rng, decryptor, new CryptoPP::StringSink(plain)));

        std::cout << "[DEBUG] RSAPrivateWrapper: Successfully decrypted " << length << " bytes" << std::endl;
        return plain;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Decryption failed: " << e.what() << std::endl;
        throw std::runtime_error("RSA decryption failed: " + std::string(e.what()));
    }
}
