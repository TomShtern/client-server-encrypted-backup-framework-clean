#pragma once

#include <vector>
#include <string>
#include <cstdint>
#include <iostream>

/**
 * Simplified Crypto Implementation for Simple Client
 * Uses OpenSSL-style interface with basic crypto operations
 * Compatible with the server's crypto protocol
 */

class SimpleCrypto {
private:
    std::vector<uint8_t> aesKey;
    std::vector<uint8_t> privateKey;
    bool keyLoaded;
    
    // Simple XOR-based fallback encryption (for when OpenSSL unavailable)
    std::vector<uint8_t> xorEncrypt(const std::vector<uint8_t>& data, const std::vector<uint8_t>& key);
    
public:
    static const size_t AES_KEY_SIZE = 32;
    static const size_t AES_BLOCK_SIZE = 16;
    
    SimpleCrypto();
    ~SimpleCrypto();
    
    /**
     * Load RSA private key from memory
     * @param keyData DER-format RSA private key
     * @return true if successful
     */
    bool loadRSAPrivateKey(const std::vector<uint8_t>& keyData);
    
    /**
     * Decrypt AES key received from server
     * Uses simple XOR decryption as fallback when RSA unavailable
     * @param encryptedAESKey 144-byte encrypted AES key from server
     * @return true if successful
     */
    bool decryptAndLoadAESKey(const std::vector<uint8_t>& encryptedAESKey);
    
    /**
     * Encrypt file data using simple algorithm
     * Uses AES-like XOR encryption with the loaded key
     * @param fileData Raw file data
     * @return Encrypted data
     */
    std::vector<uint8_t> encryptFileData(const std::vector<uint8_t>& fileData);
    
    /**
     * Simple padding to make data multiple of block size
     * @param data Input data
     * @return Padded data
     */
    std::vector<uint8_t> addPadding(const std::vector<uint8_t>& data);
    
    /**
     * Set AES key manually (for testing)
     * @param key 32-byte AES key
     * @return true if valid
     */
    bool setAESKey(const std::vector<uint8_t>& key);
    
    /**
     * Check if ready to encrypt
     * @return true if AES key loaded
     */
    bool isReady() const { return keyLoaded && aesKey.size() == AES_KEY_SIZE; }
    
    /**
     * Get current AES key (for debugging)
     * @return Current AES key
     */
    std::vector<uint8_t> getAESKey() const { return aesKey; }
};