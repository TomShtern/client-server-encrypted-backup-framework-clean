#include "aes_crypto.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <cstring>

// Use the existing Crypto++ integration from the project
#include "third_party/crypto++/aes.h"
#include "third_party/crypto++/modes.h"
#include "third_party/crypto++/filters.h"
#include "third_party/crypto++/osrng.h"
#include "third_party/crypto++/rsa.h"
#include "third_party/crypto++/base64.h"
#include "third_party/crypto++/files.h"

// Constructor
AESCrypto::AESCrypto() : keyLoaded(false) {
    // Initialize zero IV (16 bytes of zeros as per project specification)
    zeroIV.assign(AES_BLOCK_SIZE, 0);
    std::cout << "[AES] Initialized with zero IV for protocol compliance" << std::endl;
}

// Destructor
AESCrypto::~AESCrypto() {
    reset();
}

// Reset and clear all keys
void AESCrypto::reset() {
    // Clear sensitive data
    if (!aesKey.empty()) {
        std::fill(aesKey.begin(), aesKey.end(), 0);
        aesKey.clear();
    }
    keyLoaded = false;
    std::cout << "[AES] Reset - all keys cleared" << std::endl;
}

// Load RSA private key from file
bool AESCrypto::loadRSAPrivateKey(const std::string& privateKeyPath) {
    try {
        std::vector<uint8_t> keyData = AESCryptoUtils::loadFile(privateKeyPath);
        if (keyData.empty()) {
            std::cerr << "[AES] ERROR: Failed to load private key file: " << privateKeyPath << std::endl;
            return false;
        }
        
        return loadRSAPrivateKey(keyData);
    } catch (const std::exception& e) {
        std::cerr << "[AES] ERROR: Exception loading private key: " << e.what() << std::endl;
        return false;
    }
}

// Load RSA private key from memory
bool AESCrypto::loadRSAPrivateKey(const std::vector<uint8_t>& keyData) {
    try {
        // Test that the key can be loaded by creating a temporary RSA object
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(keyData.data()), keyData.size());
        queue.MessageEnd();
        
        CryptoPP::RSA::PrivateKey testKey;
        testKey.BERDecode(queue);
        
        std::cout << "[AES] ✅ RSA private key validated and ready for AES key decryption" << std::endl;
        return true;
        
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[AES] ERROR: Invalid RSA private key: " << e.what() << std::endl;
        return false;
    }
}

// Internal RSA decryption function
std::vector<uint8_t> AESCrypto::rsaDecrypt(const std::vector<uint8_t>& encryptedData, 
                                          const std::vector<uint8_t>& privateKeyDER) {
    try {
        // Load private key
        CryptoPP::ByteQueue queue;
        queue.Put(reinterpret_cast<const CryptoPP::byte*>(privateKeyDER.data()), privateKeyDER.size());
        queue.MessageEnd();
        
        CryptoPP::RSA::PrivateKey privateKey;
        privateKey.BERDecode(queue);
        
        // Decrypt using OAEP with SHA-256 (matching project specification)
        CryptoPP::AutoSeededRandomPool rng;
        CryptoPP::RSAES_OAEP_SHA256_Decryptor decryptor(privateKey);
        
        std::string decrypted;
        CryptoPP::StringSource ss(
            reinterpret_cast<const CryptoPP::byte*>(encryptedData.data()), 
            encryptedData.size(), 
            true,
            new CryptoPP::PK_DecryptorFilter(rng, decryptor, new CryptoPP::StringSink(decrypted))
        );
        
        std::vector<uint8_t> result(decrypted.begin(), decrypted.end());
        std::cout << "[AES] ✅ RSA decryption successful: " << result.size() << " bytes decrypted" << std::endl;
        return result;
        
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[AES] ERROR: RSA decryption failed: " << e.what() << std::endl;
        return std::vector<uint8_t>();
    }
}

// Decrypt AES key from server and load it
bool AESCrypto::decryptAndLoadAESKey(const std::vector<uint8_t>& encryptedAESKey) {
    if (encryptedAESKey.size() != RSA_ENCRYPTED_SIZE) {
        std::cerr << "[AES] ERROR: Invalid encrypted AES key size: " << encryptedAESKey.size() 
                  << " (expected " << RSA_ENCRYPTED_SIZE << ")" << std::endl;
        return false;
    }
    
    std::cout << "[AES] Decrypting AES key from server (" << encryptedAESKey.size() << " bytes)..." << std::endl;
    
    // For this implementation, we need to load the private key
    // Try to load from standard locations
    std::vector<std::string> keyPaths = {
        "me.info",           // Project standard location
        "client/priv.key",   // Client directory
        "data/priv.key",     // Data directory
        "priv.key"           // Current directory
    };
    
    std::vector<uint8_t> privateKeyData;
    bool keyFound = false;
    
    for (const auto& path : keyPaths) {
        try {
            privateKeyData = AESCryptoUtils::loadFile(path);
            if (!privateKeyData.empty()) {
                std::cout << "[AES] Found private key at: " << path << std::endl;
                keyFound = true;
                break;
            }
        } catch (...) {
            // Continue to next path
        }
    }
    
    if (!keyFound) {
        std::cerr << "[AES] ERROR: Could not find private key file" << std::endl;
        return false;
    }
    
    // Decrypt the AES key
    std::vector<uint8_t> decryptedKey = rsaDecrypt(encryptedAESKey, privateKeyData);
    
    if (decryptedKey.empty() || decryptedKey.size() != AES_KEY_SIZE) {
        std::cerr << "[AES] ERROR: Decrypted AES key has invalid size: " << decryptedKey.size() 
                  << " (expected " << AES_KEY_SIZE << ")" << std::endl;
        return false;
    }
    
    // Load the AES key
    return setAESKey(decryptedKey);
}

// Set AES key manually
bool AESCrypto::setAESKey(const std::vector<uint8_t>& key) {
    if (key.size() != AES_KEY_SIZE) {
        std::cerr << "[AES] ERROR: Invalid AES key size: " << key.size() 
                  << " (expected " << AES_KEY_SIZE << ")" << std::endl;
        return false;
    }
    
    aesKey = key;
    keyLoaded = true;
    
    std::cout << "[AES] ✅ AES-256 key loaded successfully" << std::endl;
    return true;
}

// Get current AES key
std::vector<uint8_t> AESCrypto::getAESKey() const {
    return aesKey;
}

// Add PKCS7 padding
std::vector<uint8_t> AESCrypto::addPKCS7Padding(const std::vector<uint8_t>& data) {
    size_t paddingLength = AES_BLOCK_SIZE - (data.size() % AES_BLOCK_SIZE);
    
    std::vector<uint8_t> padded = data;
    for (size_t i = 0; i < paddingLength; ++i) {
        padded.push_back(static_cast<uint8_t>(paddingLength));
    }
    
    return padded;
}

// Remove PKCS7 padding
std::vector<uint8_t> AESCrypto::removePKCS7Padding(const std::vector<uint8_t>& data) {
    if (data.empty()) {
        throw std::runtime_error("Cannot remove padding from empty data");
    }
    
    uint8_t paddingLength = data.back();
    
    if (paddingLength == 0 || paddingLength > AES_BLOCK_SIZE || paddingLength > data.size()) {
        throw std::runtime_error("Invalid PKCS7 padding");
    }
    
    // Verify padding bytes
    for (size_t i = data.size() - paddingLength; i < data.size(); ++i) {
        if (data[i] != paddingLength) {
            throw std::runtime_error("Invalid PKCS7 padding bytes");
        }
    }
    
    std::vector<uint8_t> unpadded(data.begin(), data.end() - paddingLength);
    return unpadded;
}

// Raw AES encryption
std::vector<uint8_t> AESCrypto::aesEncryptRaw(const std::vector<uint8_t>& plaintext) {
    try {
        std::string ciphertext;
        
        // Create AES-CBC encryption object
        CryptoPP::CBC_Mode<CryptoPP::AES>::Encryption encryption;
        encryption.SetKeyWithIV(aesKey.data(), aesKey.size(), zeroIV.data());
        
        // Encrypt - Crypto++ will handle PKCS7 padding automatically
        CryptoPP::StringSource ss(
            reinterpret_cast<const CryptoPP::byte*>(plaintext.data()), plaintext.size(), true,
            new CryptoPP::StreamTransformationFilter(
                encryption,
                new CryptoPP::StringSink(ciphertext),
                CryptoPP::StreamTransformationFilter::PKCS_PADDING
            )
        );
        
        std::vector<uint8_t> result(ciphertext.begin(), ciphertext.end());
        std::cout << "[AES] Encrypted " << plaintext.size() << " bytes to " << result.size() << " bytes" << std::endl;
        return result;
        
    } catch (const CryptoPP::Exception& e) {
        throw std::runtime_error("AES encryption failed: " + std::string(e.what()));
    }
}

// Raw AES decryption
std::vector<uint8_t> AESCrypto::aesDecryptRaw(const std::vector<uint8_t>& ciphertext) {
    try {
        std::string plaintext;
        
        // Create AES-CBC decryption object
        CryptoPP::CBC_Mode<CryptoPP::AES>::Decryption decryption;
        decryption.SetKeyWithIV(aesKey.data(), aesKey.size(), zeroIV.data());
        
        // Decrypt - Crypto++ will handle PKCS7 padding removal automatically
        CryptoPP::StringSource ss(
            reinterpret_cast<const CryptoPP::byte*>(ciphertext.data()), ciphertext.size(), true,
            new CryptoPP::StreamTransformationFilter(
                decryption,
                new CryptoPP::StringSink(plaintext),
                CryptoPP::StreamTransformationFilter::PKCS_PADDING
            )
        );
        
        std::vector<uint8_t> result(plaintext.begin(), plaintext.end());
        std::cout << "[AES] Decrypted " << ciphertext.size() << " bytes to " << result.size() << " bytes" << std::endl;
        return result;
        
    } catch (const CryptoPP::Exception& e) {
        throw std::runtime_error("AES decryption failed: " + std::string(e.what()));
    }
}

// Encrypt file data
std::vector<uint8_t> AESCrypto::encryptFileData(const std::vector<uint8_t>& fileData) {
    if (!isReady()) {
        throw std::runtime_error("AES key not loaded - call decryptAndLoadAESKey() first");
    }
    
    if (fileData.empty()) {
        throw std::runtime_error("Cannot encrypt empty file data");
    }
    
    std::cout << "[AES] Encrypting file data (" << fileData.size() << " bytes)..." << std::endl;
    return aesEncryptRaw(fileData);
}

// Decrypt file data
std::vector<uint8_t> AESCrypto::decryptFileData(const std::vector<uint8_t>& encryptedData) {
    if (!isReady()) {
        throw std::runtime_error("AES key not loaded - call decryptAndLoadAESKey() first");
    }
    
    if (encryptedData.empty()) {
        throw std::runtime_error("Cannot decrypt empty data");
    }
    
    std::cout << "[AES] Decrypting file data (" << encryptedData.size() << " bytes)..." << std::endl;
    return aesDecryptRaw(encryptedData);
}

// Test roundtrip encryption/decryption
bool AESCrypto::testRoundtrip(const std::vector<uint8_t>& testData) {
    if (!isReady()) {
        std::cerr << "[AES] ERROR: Cannot test - AES key not loaded" << std::endl;
        return false;
    }
    
    try {
        std::cout << "[AES] Testing roundtrip with " << testData.size() << " bytes..." << std::endl;
        
        // Encrypt
        std::vector<uint8_t> encrypted = encryptFileData(testData);
        
        // Decrypt
        std::vector<uint8_t> decrypted = decryptFileData(encrypted);
        
        // Compare
        bool success = (testData == decrypted);
        
        if (success) {
            std::cout << "[AES] ✅ Roundtrip test PASSED" << std::endl;
        } else {
            std::cout << "[AES] ❌ Roundtrip test FAILED - data mismatch" << std::endl;
            std::cout << "[AES]    Original size: " << testData.size() << std::endl;
            std::cout << "[AES]    Decrypted size: " << decrypted.size() << std::endl;
        }
        
        return success;
        
    } catch (const std::exception& e) {
        std::cerr << "[AES] ❌ Roundtrip test FAILED with exception: " << e.what() << std::endl;
        return false;
    }
}

// Utility functions implementation
namespace AESCryptoUtils {
    
    std::vector<uint8_t> loadFile(const std::string& filepath) {
        std::ifstream file(filepath, std::ios::binary);
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + filepath);
        }
        
        file.seekg(0, std::ios::end);
        size_t size = static_cast<size_t>(file.tellg());
        file.seekg(0, std::ios::beg);
        
        std::vector<uint8_t> data(size);
        file.read(reinterpret_cast<char*>(data.data()), size);
        
        if (!file) {
            throw std::runtime_error("Failed to read file: " + filepath);
        }
        
        return data;
    }
    
    bool saveFile(const std::string& filepath, const std::vector<uint8_t>& data) {
        try {
            std::ofstream file(filepath, std::ios::binary);
            if (!file.is_open()) {
                return false;
            }
            
            file.write(reinterpret_cast<const char*>(data.data()), data.size());
            return file.good();
            
        } catch (...) {
            return false;
        }
    }
    
    std::vector<uint8_t> hexToBytes(const std::string& hex) {
        std::vector<uint8_t> bytes;
        
        for (size_t i = 0; i < hex.length(); i += 2) {
            if (i + 1 < hex.length()) {
                std::string byteString = hex.substr(i, 2);
                uint8_t byte = static_cast<uint8_t>(std::stoul(byteString, nullptr, 16));
                bytes.push_back(byte);
            }
        }
        
        return bytes;
    }
    
    std::string bytesToHex(const std::vector<uint8_t>& data) {
        std::ostringstream oss;
        oss << std::hex << std::setfill('0');
        
        for (uint8_t byte : data) {
            oss << std::setw(2) << static_cast<unsigned>(byte);
        }
        
        return oss.str();
    }
}