#pragma once

#include <string>
#include <vector>
#include <stdexcept>

/**
 * AES Crypto Implementation for Simple Client
 * 
 * This implementation provides:
 * 1. RSA decryption to decrypt AES key received from server (144 bytes)
 * 2. AES-256-CBC encryption for file data with zero IV (per project spec)
 * 3. PKCS7 padding handling
 * 4. Self-contained with minimal dependencies
 * 
 * Compatible with project's crypto wrapper design and Crypto++ backend
 */

class AESCrypto {
public:
    static const size_t AES_KEY_SIZE = 32;     // AES-256 requires 32-byte keys
    static const size_t AES_BLOCK_SIZE = 16;   // AES block size is always 16 bytes
    static const size_t RSA_ENCRYPTED_SIZE = 144; // Server sends 144-byte encrypted AES key
    
private:
    std::vector<uint8_t> aesKey;
    std::vector<uint8_t> zeroIV;
    bool keyLoaded;
    
    // Internal RSA decryption using pre-loaded private key
    std::vector<uint8_t> rsaDecrypt(const std::vector<uint8_t>& encryptedData, 
                                   const std::vector<uint8_t>& privateKeyDER);
    
    // PKCS7 padding functions
    std::vector<uint8_t> addPKCS7Padding(const std::vector<uint8_t>& data);
    std::vector<uint8_t> removePKCS7Padding(const std::vector<uint8_t>& data);
    
    // Low-level AES operations
    std::vector<uint8_t> aesEncryptRaw(const std::vector<uint8_t>& plaintext);
    std::vector<uint8_t> aesDecryptRaw(const std::vector<uint8_t>& ciphertext);
    
public:
    AESCrypto();
    ~AESCrypto();
    
    /**
     * Load RSA private key from file for AES key decryption
     * @param privateKeyPath Path to DER-format private key file
     * @return true if key loaded successfully
     */
    bool loadRSAPrivateKey(const std::string& privateKeyPath);
    
    /**
     * Load RSA private key from memory buffer
     * @param keyData DER-format private key data
     * @return true if key loaded successfully
     */
    bool loadRSAPrivateKey(const std::vector<uint8_t>& keyData);
    
    /**
     * Decrypt AES key received from server using RSA private key
     * @param encryptedAESKey 144-byte encrypted AES key from server
     * @return true if AES key decrypted and loaded successfully
     */
    bool decryptAndLoadAESKey(const std::vector<uint8_t>& encryptedAESKey);
    
    /**
     * Encrypt file data using AES-256-CBC with zero IV
     * @param fileData Raw file data to encrypt
     * @return Encrypted data with PKCS7 padding
     */
    std::vector<uint8_t> encryptFileData(const std::vector<uint8_t>& fileData);
    
    /**
     * Decrypt file data using AES-256-CBC with zero IV
     * @param encryptedData Encrypted data with PKCS7 padding
     * @return Decrypted file data
     */
    std::vector<uint8_t> decryptFileData(const std::vector<uint8_t>& encryptedData);
    
    /**
     * Manual AES key setting (for testing or when key is obtained differently)
     * @param key 32-byte AES-256 key
     * @return true if key is valid and loaded
     */
    bool setAESKey(const std::vector<uint8_t>& key);
    
    /**
     * Get current AES key (for debugging/testing)
     * @return Current AES key, empty if not loaded
     */
    std::vector<uint8_t> getAESKey() const;
    
    /**
     * Test encrypt/decrypt roundtrip to verify implementation
     * @param testData Data to test with
     * @return true if roundtrip successful
     */
    bool testRoundtrip(const std::vector<uint8_t>& testData);
    
    /**
     * Check if AES key is loaded and ready for encryption/decryption
     * @return true if ready to encrypt/decrypt
     */
    bool isReady() const { return keyLoaded && !aesKey.empty(); }
    
    /**
     * Clear all loaded keys and reset state
     */
    void reset();
};

/**
 * Utility functions for the simple client
 */
namespace AESCryptoUtils {
    /**
     * Load file into byte vector
     * @param filepath Path to file
     * @return File contents as byte vector
     */
    std::vector<uint8_t> loadFile(const std::string& filepath);
    
    /**
     * Save byte vector to file
     * @param filepath Path to save file
     * @param data Data to save
     * @return true if successful
     */
    bool saveFile(const std::string& filepath, const std::vector<uint8_t>& data);
    
    /**
     * Convert hex string to bytes (for testing)
     * @param hex Hex string (e.g., "deadbeef")
     * @return Byte vector
     */
    std::vector<uint8_t> hexToBytes(const std::string& hex);
    
    /**
     * Convert bytes to hex string (for debugging)
     * @param data Byte vector
     * @return Hex string
     */
    std::string bytesToHex(const std::vector<uint8_t>& data);
}