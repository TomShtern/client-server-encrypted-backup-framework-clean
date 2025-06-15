#include "simple_crypto.h"
#include <algorithm>
#include <cstring>

SimpleCrypto::SimpleCrypto() : keyLoaded(false) {
}

SimpleCrypto::~SimpleCrypto() {
    // Clear sensitive data
    std::fill(aesKey.begin(), aesKey.end(), 0);
    std::fill(privateKey.begin(), privateKey.end(), 0);
}

bool SimpleCrypto::loadRSAPrivateKey(const std::vector<uint8_t>& keyData) {
    std::cout << "[CRYPTO] Loading RSA private key (" << keyData.size() << " bytes)" << std::endl;
    privateKey = keyData;
    return true;
}

bool SimpleCrypto::decryptAndLoadAESKey(const std::vector<uint8_t>& encryptedAESKey) {
    std::cout << "[CRYPTO] Decrypting AES key (" << encryptedAESKey.size() << " bytes)" << std::endl;
    
    // Accept either 144 bytes (full payload) or 128 bytes (just encrypted AES key)
    if (encryptedAESKey.size() != 144 && encryptedAESKey.size() != 128) {
        std::cerr << "[CRYPTO] Invalid encrypted AES key size (expected 144 or 128, got " << encryptedAESKey.size() << ")" << std::endl;
        return false;
    }
    
    // Simplified decryption: Extract first 32 bytes as AES key
    // In real implementation, this would use RSA-OAEP decryption
    // For testing, we extract a pattern from the encrypted data
    aesKey.resize(AES_KEY_SIZE);
    
    // Use a deterministic method to derive AES key from encrypted data
    // This simulates RSA decryption result
    for (size_t i = 0; i < AES_KEY_SIZE; ++i) {
        aesKey[i] = encryptedAESKey[i % encryptedAESKey.size()] ^ 0x42 ^ (i & 0xFF);
    }
    
    keyLoaded = true;
    std::cout << "[CRYPTO] AES key extracted and loaded" << std::endl;
    
    // Debug: show first few bytes of AES key
    std::cout << "[CRYPTO] AES key preview: ";
    for (size_t i = 0; i < std::min(size_t(8), aesKey.size()); ++i) {
        printf("%02x ", aesKey[i]);
    }
    std::cout << "..." << std::endl;
    
    return true;
}

std::vector<uint8_t> SimpleCrypto::xorEncrypt(const std::vector<uint8_t>& data, const std::vector<uint8_t>& key) {
    std::vector<uint8_t> result(data.size());
    
    for (size_t i = 0; i < data.size(); ++i) {
        result[i] = data[i] ^ key[i % key.size()];
    }
    
    return result;
}

std::vector<uint8_t> SimpleCrypto::addPadding(const std::vector<uint8_t>& data) {
    // PKCS7-like padding
    size_t paddingLength = AES_BLOCK_SIZE - (data.size() % AES_BLOCK_SIZE);
    if (paddingLength == 0) {
        paddingLength = AES_BLOCK_SIZE;
    }
    
    std::vector<uint8_t> padded = data;
    for (size_t i = 0; i < paddingLength; ++i) {
        padded.push_back(static_cast<uint8_t>(paddingLength));
    }
    
    return padded;
}

std::vector<uint8_t> SimpleCrypto::encryptFileData(const std::vector<uint8_t>& fileData) {
    if (!isReady()) {
        std::cerr << "[CRYPTO] AES key not loaded" << std::endl;
        return {};
    }
    
    std::cout << "[CRYPTO] Encrypting file data (" << fileData.size() << " bytes)" << std::endl;
    
    // Add padding to make data multiple of block size
    std::vector<uint8_t> paddedData = addPadding(fileData);
    
    std::cout << "[CRYPTO] After padding: " << paddedData.size() << " bytes" << std::endl;
    
    // Simple XOR encryption with the AES key
    // In real implementation, this would be AES-256-CBC with zero IV
    std::vector<uint8_t> encrypted = xorEncrypt(paddedData, aesKey);
    
    std::cout << "[CRYPTO] Encryption complete (" << encrypted.size() << " bytes)" << std::endl;
    
    return encrypted;
}

bool SimpleCrypto::setAESKey(const std::vector<uint8_t>& key) {
    if (key.size() != AES_KEY_SIZE) {
        std::cerr << "[CRYPTO] Invalid AES key size: " << key.size() << std::endl;
        return false;
    }
    
    aesKey = key;
    keyLoaded = true;
    std::cout << "[CRYPTO] AES key set manually" << std::endl;
    
    return true;
}