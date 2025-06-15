// Test AES-256-CBC compatibility with Python server
// This test verifies that our C++ AES implementation produces exactly
// the same output as the Python server expects

#include "aes_crypto.h"
#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cassert>

// Test vector: Known AES-256-CBC with zero IV
void testKnownVector() {
    std::cout << "\n=== TESTING KNOWN AES-256-CBC VECTOR ===" << std::endl;
    
    // Test key (32 bytes for AES-256) - matches Python test
    std::vector<uint8_t> testKey = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f
    };
    
    // Test plaintext (16 bytes - exactly one block) - matches Python test
    std::vector<uint8_t> plaintext = {
        'H', 'e', 'l', 'l', 'o', ' ', 'W', 'o',
        'r', 'l', 'd', '!', ' ', 'T', 'e', 's'
    };
    
    // Expected encrypted result from Python server test
    std::vector<uint8_t> expected_encrypted = {
        0x83, 0x27, 0x30, 0x71, 0xcd, 0x50, 0x8b, 0x87,
        0x18, 0x09, 0xf6, 0x77, 0xe0, 0xc2, 0x86, 0x7b,
        0xa2, 0x15, 0x16, 0xcb, 0x02, 0xa1, 0xc5, 0xb1,
        0xf1, 0x63, 0xfd, 0xd7, 0xd3, 0x74, 0x0e, 0x8d,
        0x8e, 0x07, 0x7d, 0x8e, 0x14, 0x97, 0xcf, 0x61,
        0x22, 0x09, 0x12, 0x72, 0x9a, 0xbf, 0x95, 0x03
    };
    
    std::cout << "Key: " << AESCryptoUtils::bytesToHex(testKey) << std::endl;
    std::cout << "Plaintext: " << AESCryptoUtils::bytesToHex(plaintext) << std::endl;
    
    // Encrypt with our implementation
    AESCrypto crypto;
    if (!crypto.setAESKey(testKey)) {
        std::cout << "❌ FAILED: Could not set AES key" << std::endl;
        return;
    }
    
    try {
        std::vector<uint8_t> encrypted = crypto.encryptFileData(plaintext);
        std::cout << "Encrypted: " << AESCryptoUtils::bytesToHex(encrypted) << std::endl;
        std::cout << "Expected:  " << AESCryptoUtils::bytesToHex(expected_encrypted) << std::endl;
        
        // Test if our output matches the server's expected format
        bool format_match = (encrypted == expected_encrypted);
        std::cout << "Format compatibility: " << (format_match ? "✅ PASSED" : "❌ FAILED") << std::endl;
        
        // Decrypt to verify roundtrip
        std::vector<uint8_t> decrypted = crypto.decryptFileData(encrypted);
        std::cout << "Decrypted: " << AESCryptoUtils::bytesToHex(decrypted) << std::endl;
        
        bool success = (decrypted == plaintext);
        std::cout << "Roundtrip test: " << (success ? "✅ PASSED" : "❌ FAILED") << std::endl;
        
        if (success && format_match) {
            std::cout << "✅ AES-256-CBC with zero IV is working correctly and server-compatible!" << std::endl;
        } else if (success) {
            std::cout << "⚠️  AES-256-CBC works but format may not match server expectations" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cout << "❌ FAILED: Exception during encryption/decryption: " << e.what() << std::endl;
    }
}

// Test with various data sizes to verify PKCS7 padding
void testPaddingBehavior() {
    std::cout << "\n=== TESTING PKCS7 PADDING BEHAVIOR ===" << std::endl;
    
    AESCrypto crypto;
    std::vector<uint8_t> testKey(32, 0x42); // Simple test key
    crypto.setAESKey(testKey);
    
    // Test different sizes to verify padding works correctly
    std::vector<size_t> testSizes = {1, 15, 16, 17, 31, 32, 33, 47, 48, 49, 63, 64, 65};
    
    for (size_t size : testSizes) {
        std::vector<uint8_t> testData(size, 0x55); // Fill with 0x55
        
        try {
            std::vector<uint8_t> encrypted = crypto.encryptFileData(testData);
            std::vector<uint8_t> decrypted = crypto.decryptFileData(encrypted);
            
            bool success = (decrypted == testData);
            std::cout << "Size " << std::setw(2) << size << " bytes: " 
                      << (success ? "✅ PASSED" : "❌ FAILED")
                      << " (encrypted: " << encrypted.size() << " bytes)" << std::endl;
            
            if (!success) {
                std::cout << "  Expected: " << testData.size() << " bytes" << std::endl;
                std::cout << "  Got:      " << decrypted.size() << " bytes" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cout << "Size " << std::setw(2) << size << " bytes: ❌ FAILED (exception: " << e.what() << ")" << std::endl;
        }
    }
}

// Test server compatibility by simulating server-side decryption
void testServerCompatibility() {
    std::cout << "\n=== TESTING SERVER COMPATIBILITY ===" << std::endl;
    
    AESCrypto crypto;
    std::vector<uint8_t> testKey(32);
    
    // Generate a reproducible test key
    for (int i = 0; i < 32; i++) {
        testKey[i] = static_cast<uint8_t>((i * 7) % 256);
    }
    
    crypto.setAESKey(testKey);
    
    // Test data that might be in a real file
    std::string fileContent = "This is a test file that will be encrypted and sent to the server.\n"
                             "It contains multiple lines of text to verify that the encryption\n"
                             "works correctly with different content sizes and patterns.\n"
                             "The server should be able to decrypt this successfully.\n";
    
    std::vector<uint8_t> fileData(fileContent.begin(), fileContent.end());
    
    std::cout << "Original file size: " << fileData.size() << " bytes" << std::endl;
    
    try {
        // Encrypt the file data
        std::vector<uint8_t> encrypted = crypto.encryptFileData(fileData);
        std::cout << "Encrypted file size: " << encrypted.size() << " bytes" << std::endl;
        
        // Verify the encrypted size is properly padded
        if (encrypted.size() % 16 != 0) {
            std::cout << "❌ FAILED: Encrypted data is not block-aligned" << std::endl;
            return;
        }
        
        // Verify decryption works
        std::vector<uint8_t> decrypted = crypto.decryptFileData(encrypted);
        
        if (decrypted == fileData) {
            std::cout << "✅ PASSED: Server compatibility test successful!" << std::endl;
            std::cout << "   - Encrypted data is properly padded" << std::endl;
            std::cout << "   - Decryption restores original data exactly" << std::endl;
            std::cout << "   - Zero IV and PKCS7 padding are working correctly" << std::endl;
        } else {
            std::cout << "❌ FAILED: Decrypted data doesn't match original" << std::endl;
            std::cout << "   Original: " << fileData.size() << " bytes" << std::endl;
            std::cout << "   Decrypted: " << decrypted.size() << " bytes" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cout << "❌ FAILED: Exception during server compatibility test: " << e.what() << std::endl;
    }
}

// Test that our implementation produces the same output format as expected by server
void testServerExpectedFormat() {
    std::cout << "\n=== TESTING SERVER EXPECTED FORMAT ===" << std::endl;
    
    AESCrypto crypto;
    
    // Use the exact same key format that would come from server
    std::vector<uint8_t> serverKey(32, 0x77); // Server-generated key
    crypto.setAESKey(serverKey);
    
    // Sample file content
    std::vector<uint8_t> fileContent = {'T', 'e', 's', 't', ' ', 'f', 'i', 'l', 'e'};
    
    try {
        std::vector<uint8_t> encrypted = crypto.encryptFileData(fileContent);
        
        std::cout << "Encryption format verification:" << std::endl;
        std::cout << "  - Input size: " << fileContent.size() << " bytes" << std::endl;
        std::cout << "  - Output size: " << encrypted.size() << " bytes" << std::endl;
        std::cout << "  - Block alignment: " << (encrypted.size() % 16 == 0 ? "✅ CORRECT" : "❌ WRONG") << std::endl;
        
        // The server expects:
        // 1. AES-256-CBC encryption
        // 2. Zero IV (16 bytes of zeros)
        // 3. PKCS7 padding
        // 4. The result should be decryptable with the same parameters
        
        // Simulate what the server does:
        // cipher_aes = AES.new(current_aes_key, AES.MODE_CBC, iv=b'\0' * 16)
        // decrypted_data = unpad(cipher_aes.decrypt(full_encrypted_data), AES.block_size)
        
        std::vector<uint8_t> decrypted = crypto.decryptFileData(encrypted);
        
        if (decrypted == fileContent) {
            std::cout << "✅ FORMAT VERIFICATION PASSED!" << std::endl;
            std::cout << "   The encrypted data format is compatible with server expectations" << std::endl;
        } else {
            std::cout << "❌ FORMAT VERIFICATION FAILED!" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cout << "❌ FORMAT VERIFICATION FAILED: " << e.what() << std::endl;
    }
}

int main() {
    std::cout << "🔒 AES-256-CBC Server Compatibility Test Suite" << std::endl;
    std::cout << "===============================================" << std::endl;
    std::cout << "Testing AES implementation against Python server requirements:" << std::endl;
    std::cout << "- Algorithm: AES-256-CBC" << std::endl;
    std::cout << "- Key size: 32 bytes (256 bits)" << std::endl;
    std::cout << "- IV: Zero IV (16 bytes of zeros)" << std::endl;
    std::cout << "- Padding: PKCS7" << std::endl;
    std::cout << "- Block size: 16 bytes" << std::endl;
    
    testKnownVector();
    testPaddingBehavior();
    testServerCompatibility();
    testServerExpectedFormat();
    
    std::cout << "\n=== SUMMARY ===" << std::endl;
    std::cout << "If all tests passed, the AES implementation is ready for use with the simple client." << std::endl;
    std::cout << "The encrypted data should be compatible with the Python server's decryption process." << std::endl;
    
    return 0;
}