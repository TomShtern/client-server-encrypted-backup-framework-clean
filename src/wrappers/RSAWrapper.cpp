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
#include <future>

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
    std::cout << "[DEBUG] RSAPrivateWrapper: Starting RSA key pair generation for " << BITS << " bits" << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    
    try {
        CryptoPP::AutoSeededRandomPool rng;
        std::cout << "[DEBUG] RSAPrivateWrapper: Initialized random number generator" << std::endl;
        
        // Attempt key generation with a timeout of 2 seconds
        bool generationSuccess = false;
        std::thread generationThread([&]() {
            try {
                privateKeyImpl = new CryptoPP::RSA::PrivateKey();
                CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
                std::cout << "[DEBUG] RSAPrivateWrapper: Beginning key generation process" << std::endl;
                privateKey->GenerateRandomWithKeySize(rng, BITS);
                std::cout << "[DEBUG] RSAPrivateWrapper: Key generation completed successfully" << std::endl;
                generationSuccess = true;
            } catch (const CryptoPP::Exception& e) {
                std::cerr << "[ERROR] RSAPrivateWrapper: Key generation failed: " << e.what() << std::endl;
            }
        });

        // Wait for key generation with a short timeout
        if (generationThread.joinable()) {
            auto future = std::async(std::launch::async, [&generationThread]() {
                generationThread.join();
            });

            if (future.wait_for(std::chrono::seconds(2)) == std::future_status::timeout) {
                std::cout << "[WARNING] RSAPrivateWrapper: Key generation timed out after 2 seconds, using fallback keys" << std::endl;
                generationSuccess = false;
                // Note: We can't safely terminate the thread, so we just proceed with fallback
            }
        }
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start);
        std::cout << "[DEBUG] RSAPrivateWrapper: Key generation took " << duration.count() << " ms" << std::endl;
        
        if (!generationSuccess || !privateKeyImpl) {
            std::cerr << "[WARNING] RSAPrivateWrapper: Key generation timed out or failed, attempting fallback to pre-generated keys" << std::endl;
            std::string privateKeyFile = "data/priv.key";
            std::string publicKeyFile = "data/pub.key";
            
            std::ifstream privateFile(privateKeyFile, std::ios::binary);
            if (!privateFile.is_open()) {
                std::cerr << "[ERROR] RSAPrivateWrapper: Cannot open fallback private key file: " << privateKeyFile << std::endl;
                throw std::runtime_error("Cannot load fallback private key: " + privateKeyFile);
            }
            
            std::ifstream publicFile(publicKeyFile, std::ios::binary);
            if (!publicFile.is_open()) {
                std::cerr << "[ERROR] RSAPrivateWrapper: Cannot open fallback public key file: " << publicKeyFile << std::endl;
                throw std::runtime_error("Cannot load fallback public key: " + publicKeyFile);
            }
            
            std::string privateData((std::istreambuf_iterator<char>(privateFile)), std::istreambuf_iterator<char>());
            std::string publicData((std::istreambuf_iterator<char>(publicFile)), std::istreambuf_iterator<char>());
            privateFile.close();
            publicFile.close();
            
            if (privateData.empty() || publicData.empty()) {
                throw std::runtime_error("Fallback key files are empty or corrupted");
            }
            
            privateKeyData.assign(privateData.begin(), privateData.end());
            publicKeyData.assign(publicData.begin(), publicData.end());
            
            try {
                // Load private key
                CryptoPP::ByteQueue privateQueue;
                privateQueue.Put(reinterpret_cast<const CryptoPP::byte*>(privateKeyData.data()), privateKeyData.size());
                privateQueue.MessageEnd();
                
                privateKeyImpl = new CryptoPP::RSA::PrivateKey();
                CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
                privateKey->BERDecode(privateQueue);
                
                // Load public key
                CryptoPP::ByteQueue publicQueue;
                publicQueue.Put(reinterpret_cast<const CryptoPP::byte*>(publicKeyData.data()), publicKeyData.size());
                publicQueue.MessageEnd();
                
                publicKeyImpl = new CryptoPP::RSA::PublicKey();
                CryptoPP::RSA::PublicKey* publicKey = static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
                publicKey->BERDecode(publicQueue);
                
                std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded fallback keys from " << privateKeyFile << " and " << publicKeyFile << std::endl;
            } catch (const CryptoPP::Exception& e) {
                std::cerr << "[ERROR] RSAPrivateWrapper: Failed to load fallback keys: " << e.what() << std::endl;
                if (privateKeyImpl) {
                    delete static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
                    privateKeyImpl = nullptr;
                }
                if (publicKeyImpl) {
                    delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
                    publicKeyImpl = nullptr;
                }
                throw std::runtime_error("Failed to load fallback RSA keys: " + std::string(e.what()));
            }
        } else {
            // Extract public key from private key
            CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
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
            
            std::cout << "[DEBUG] RSAPrivateWrapper: Successfully generated " << BITS << "-bit RSA key pair" << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] RSAPrivateWrapper: Key generation process failed: " << e.what() << std::endl;
        std::string privateKeyFile = "data/priv.key";
        std::string publicKeyFile = "data/pub.key";
        
        std::ifstream privateFile(privateKeyFile, std::ios::binary);
        if (!privateFile.is_open()) {
            std::cerr << "[ERROR] RSAPrivateWrapper: Cannot open fallback private key file: " << privateKeyFile << std::endl;
            throw std::runtime_error("Cannot load fallback private key: " + privateKeyFile);
        }
        
        std::ifstream publicFile(publicKeyFile, std::ios::binary);
        if (!publicFile.is_open()) {
            std::cerr << "[ERROR] RSAPrivateWrapper: Cannot open fallback public key file: " << publicKeyFile << std::endl;
            throw std::runtime_error("Cannot load fallback public key: " + publicKeyFile);
        }
        
        std::string privateData((std::istreambuf_iterator<char>(privateFile)), std::istreambuf_iterator<char>());
        std::string publicData((std::istreambuf_iterator<char>(publicFile)), std::istreambuf_iterator<char>());
        privateFile.close();
        publicFile.close();
        
        if (privateData.empty() || publicData.empty()) {
            throw std::runtime_error("Fallback key files are empty or corrupted");
        }
        
        privateKeyData.assign(privateData.begin(), privateData.end());
        publicKeyData.assign(publicData.begin(), publicData.end());
        
        try {
            // Load private key
            CryptoPP::ByteQueue privateQueue;
            privateQueue.Put(reinterpret_cast<const CryptoPP::byte*>(privateKeyData.data()), privateKeyData.size());
            privateQueue.MessageEnd();
            
            privateKeyImpl = new CryptoPP::RSA::PrivateKey();
            CryptoPP::RSA::PrivateKey* privateKey = static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
            privateKey->BERDecode(privateQueue);
            
            // Load public key
            CryptoPP::ByteQueue publicQueue;
            publicQueue.Put(reinterpret_cast<const CryptoPP::byte*>(publicKeyData.data()), publicKeyData.size());
            publicQueue.MessageEnd();
            
            publicKeyImpl = new CryptoPP::RSA::PublicKey();
            CryptoPP::RSA::PublicKey* publicKey = static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
            publicKey->BERDecode(publicQueue);
            
            std::cout << "[DEBUG] RSAPrivateWrapper: Successfully loaded fallback keys from " << privateKeyFile << " and " << publicKeyFile << std::endl;
        } catch (const CryptoPP::Exception& e) {
            std::cerr << "[ERROR] RSAPrivateWrapper: Failed to load fallback keys: " << e.what() << std::endl;
            if (privateKeyImpl) {
                delete static_cast<CryptoPP::RSA::PrivateKey*>(privateKeyImpl);
                privateKeyImpl = nullptr;
            }
            if (publicKeyImpl) {
                delete static_cast<CryptoPP::RSA::PublicKey*>(publicKeyImpl);
                publicKeyImpl = nullptr;
            }
            throw std::runtime_error("Failed to load fallback RSA keys: " + std::string(e.what()));
        }
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
