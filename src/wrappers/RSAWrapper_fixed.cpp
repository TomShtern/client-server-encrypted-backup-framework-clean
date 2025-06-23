#include "../../include/wrappers/RSAWrapper.h"
#include <rsa.h>
#include <osrng.h>
#include <oaep.h>
#include <sha.h>
#include <files.h>
#include <stdexcept>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cstring>
#include <chrono>
#include <thread>

#ifdef _WIN32
#include <windows.h>
#include <wincrypt.h>
#endif

// Fast entropy source for RSA key generation that doesn't hang
class FastRandomPool : public CryptoPP::RandomNumberGenerator {
private:
    CryptoPP::AutoSeededRandomPool fallback;
    bool useSystemEntropy;

public:
    FastRandomPool() : useSystemEntropy(true) {
        std::cout << "[DEBUG] FastRandomPool: Initializing fast entropy source..." << std::endl;
    }

    void GenerateBlock(CryptoPP::byte *output, size_t size) override {
        if (useSystemEntropy && size <= 32) {
            // For small requests, use system entropy quickly
            #ifdef _WIN32
            HCRYPTPROV hProv;
            if (CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
                if (CryptGenRandom(hProv, size, output)) {
                    CryptReleaseContext(hProv, 0);
                    std::cout << "[DEBUG] FastRandomPool: Generated " << size << " bytes using Windows CryptoAPI" << std::endl;
                    return;
                }
                CryptReleaseContext(hProv, 0);
            }
            #endif
        }
        
        // Fallback to AutoSeededRandomPool with timeout
        std::cout << "[DEBUG] FastRandomPool: Using fallback entropy source..." << std::endl;
        fallback.GenerateBlock(output, size);
    }

    CryptoPP::byte GenerateByte() override {
        CryptoPP::byte b;
        GenerateBlock(&b, 1);
        return b;
    }
};

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

        // Use fast entropy source
        FastRandomPool rng;
        
        CryptoPP::RSAES_OAEP_SHA_Encryptor encryptor(*publicKey);
        
        std::string cipher;
        CryptoPP::StringSource ss(reinterpret_cast<const CryptoPP::byte*>(plain), length, true,
            new CryptoPP::PK_EncryptorFilter(rng, encryptor,
                new CryptoPP::StringSink(cipher)
            )
        );
        
        return cipher;
    } catch (const CryptoPP::Exception& e) {
        throw std::runtime_error("RSA encryption failed: " + std::string(e.what()));
    }
}

// RSAPrivateWrapper implementation
RSAPrivateWrapper::RSAPrivateWrapper() : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
    std::cout << "[DEBUG] RSAPrivateWrapper: Checking for existing key files..." << std::endl;
    
    // Try to load existing keys first
    if (loadExistingKeys()) {
        std::cout << "[DEBUG] RSAPrivateWrapper: Loaded existing RSA keys successfully!" << std::endl;
        return;
    }
    
    std::cout << "[DEBUG] RSAPrivateWrapper: Generating new " << BITS << "-bit RSA key pair..." << std::endl;

    try {
        // Use fast entropy source to avoid hanging
        std::cout << "[DEBUG] RSAPrivateWrapper: Creating fast entropy source..." << std::endl;
        FastRandomPool rng;

        // Create private key and generate
        privateKeyImpl = new CryptoPP::RSA::PrivateKey();
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);

        // Generate RSA key pair with timeout protection
        std::cout << "[DEBUG] RSAPrivateWrapper: Starting RSA key generation with fast entropy..." << std::endl;
        
        auto start = std::chrono::steady_clock::now();
        privateKey->Initialize(rng, BITS);
        auto end = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "[DEBUG] RSAPrivateWrapper: RSA key generation completed in " << duration.count() << "ms!" << std::endl;

        // Extract public key from private key
        publicKeyImpl = new CryptoPP::RSA::PublicKey(*privateKey);

        // Save keys to DER format
        saveKeysToData();
        saveKeysToFiles();

        std::cout << "[DEBUG] RSAPrivateWrapper: Key pair initialized and saved successfully!" << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Key generation failed: " << e.what() << std::endl;
        
        // Clean up on failure
        if (privateKeyImpl) {
            delete static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
            privateKeyImpl = nullptr;
        }
        if (publicKeyImpl) {
            delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
            publicKeyImpl = nullptr;
        }
        
        throw std::runtime_error("Failed to generate RSA key pair: " + std::string(e.what()));
    }
}

RSAPrivateWrapper::RSAPrivateWrapper(const char* key, size_t keylen) : privateKeyImpl(nullptr), publicKeyImpl(nullptr) {
    if (!key || keylen == 0) {
        throw std::invalid_argument("Invalid key data");
    }
    
    try {
        std::cout << "[DEBUG] RSAPrivateWrapper: Loading private key from buffer (" << keylen << " bytes)" << std::endl;
        
        // Load the private key from DER format
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(key), keylen);
        queue.MessageEnd();
        
        privateKeyImpl = new CryptoPP::RSA::PrivateKey();
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
        privateKey->BERDecode(queue);
        
        // Extract public key from private key
        publicKeyImpl = new CryptoPP::RSA::PublicKey(*privateKey);
        
        // Save keys to data
        saveKeysToData();
        
        std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded private key from buffer" << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Failed to load private key from buffer: " << e.what() << std::endl;
        
        // Clean up on failure
        if (privateKeyImpl) {
            delete static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
            privateKeyImpl = nullptr;
        }
        if (publicKeyImpl) {
            delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
            publicKeyImpl = nullptr;
        }
        
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
    
    try {
        std::cout << "[DEBUG] RSAPrivateWrapper: Loading private key from file " << filename << std::endl;
        
        // Load the private key from DER format
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(fileData.data()), fileData.size());
        queue.MessageEnd();
        
        privateKeyImpl = new CryptoPP::RSA::PrivateKey();
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
        privateKey->BERDecode(queue);
        
        // Extract public key from private key
        publicKeyImpl = new CryptoPP::RSA::PublicKey(*privateKey);
        
        // Save keys to data
        saveKeysToData();
        
        std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded private key from " << filename << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Failed to load private key from file " << filename << ": " << e.what() << std::endl;
        
        // Clean up on failure
        if (privateKeyImpl) {
            delete static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
            privateKeyImpl = nullptr;
        }
        if (publicKeyImpl) {
            delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
            publicKeyImpl = nullptr;
        }
        
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

std::string RSAPrivateWrapper::decrypt(const std::string& cipher) {
    return decrypt(cipher.c_str(), cipher.size());
}

std::string RSAPrivateWrapper::decrypt(const char* cipher, size_t length) {
    if (!privateKeyImpl) {
        throw std::runtime_error("RSA private key not initialized");
    }
    
    try {
        CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);

        // Use fast entropy source
        FastRandomPool rng;
        
        CryptoPP::RSAES_OAEP_SHA_Decryptor decryptor(*privateKey);
        
        std::string recovered;
        CryptoPP::StringSource ss(reinterpret_cast<const CryptoPP::byte*>(cipher), length, true,
            new CryptoPP::PK_DecryptorFilter(rng, decryptor,
                new CryptoPP::StringSink(recovered)
            )
        );
        
        return recovered;
    } catch (const CryptoPP::Exception& e) {
        throw std::runtime_error("RSA decryption failed: " + std::string(e.what()));
    }
}

std::string RSAPrivateWrapper::getPublicKey() {
    return std::string(reinterpret_cast<const char*>(publicKeyData.data()), publicKeyData.size());
}

void RSAPrivateWrapper::getPublicKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < publicKeyData.size()) {
        throw std::invalid_argument("Invalid output buffer or insufficient size");
    }
    std::memcpy(keyout, publicKeyData.data(), publicKeyData.size());
}

std::string RSAPrivateWrapper::getPrivateKey() {
    return std::string(reinterpret_cast<const char*>(privateKeyData.data()), privateKeyData.size());
}

void RSAPrivateWrapper::getPrivateKey(char* keyout, size_t keylen) {
    if (!keyout || keylen < privateKeyData.size()) {
        throw std::invalid_argument("Invalid output buffer or insufficient size");
    }
    std::memcpy(keyout, privateKeyData.data(), privateKeyData.size());
}
