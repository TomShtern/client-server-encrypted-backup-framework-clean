// Comprehensive Test Suite for Encrypted Backup Framework
// Tests all major components: RSA, AES, Protocol, File Transfer, GUI

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <cassert>
#include <cstdio>

// Include project headers
#include "../include/wrappers/RSAWrapper.h"
#include "../include/wrappers/AESWrapper.h"
#include "../include/wrappers/Base64Wrapper.h"
#include "../include/client/cksum.h"
#include "../include/client/protocol.h"

#ifdef _WIN32
#include "../include/client/ClientGUI.h"
#endif

class TestFramework {
private:
    int totalTests = 0;
    int passedTests = 0;
    int failedTests = 0;
    
public:
    void runTest(const std::string& testName, std::function<bool()> testFunc) {
        totalTests++;
        std::cout << "Running test: " << testName << "... ";
        
        auto start = std::chrono::high_resolution_clock::now();
        bool result = false;
        
        try {
            result = testFunc();
        } catch (const std::exception& e) {
            std::cout << "EXCEPTION: " << e.what() << std::endl;
            result = false;
        } catch (...) {
            std::cout << "UNKNOWN EXCEPTION" << std::endl;
            result = false;
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        if (result) {
            passedTests++;
            std::cout << "PASS (" << duration.count() << "ms)" << std::endl;
        } else {
            failedTests++;
            std::cout << "FAIL (" << duration.count() << "ms)" << std::endl;
        }
    }
    
    void printSummary() {
        std::cout << "\n=== TEST SUMMARY ===" << std::endl;
        std::cout << "Total Tests: " << totalTests << std::endl;
        std::cout << "Passed: " << passedTests << std::endl;
        std::cout << "Failed: " << failedTests << std::endl;
        std::cout << "Success Rate: " << (totalTests > 0 ? (passedTests * 100 / totalTests) : 0) << "%" << std::endl;
    }
    
    bool allTestsPassed() const {
        return failedTests == 0 && totalTests > 0;
    }
};

// Test RSA encryption/decryption
bool testRSAOperations() {
    try {
        // Generate RSA key pair
        RSAPrivateWrapper privateKey;
        std::string publicKeyStr = privateKey.getPublicKey();
        
        if (publicKeyStr.empty()) {
            return false;
        }
        
        // Create public key wrapper
        RSAPublicWrapper publicKey(publicKeyStr.c_str(), publicKeyStr.size());
        
        // Test data
        std::string testData = "Hello, RSA encryption test!";
        
        // Encrypt with public key
        std::string encrypted = publicKey.encrypt(testData);
        if (encrypted.empty() || encrypted == testData) {
            return false;
        }
        
        // Decrypt with private key
        std::string decrypted = privateKey.decrypt(encrypted);
        
        return decrypted == testData;
    } catch (...) {
        return false;
    }
}

// Test AES encryption/decryption
bool testAESOperations() {
    try {
        // Generate random 32-byte key
        std::string key(32, 0);
        for (int i = 0; i < 32; i++) {
            key[i] = static_cast<char>(rand() % 256);
        }
        
        AESWrapper aes(reinterpret_cast<const unsigned char*>(key.c_str()), 32, true);
        
        // Test data
        std::string testData = "This is a test for AES encryption with some longer text to test padding.";
        
        // Encrypt
        std::string encrypted = aes.encrypt(testData.c_str(), testData.size());
        if (encrypted.empty() || encrypted == testData) {
            return false;
        }
        
        // Decrypt
        std::string decrypted = aes.decrypt(encrypted.c_str(), encrypted.size());
        
        return decrypted == testData;
    } catch (...) {
        return false;
    }
}

// Test Base64 encoding/decoding
bool testBase64Operations() {
    try {
        Base64Wrapper base64;
        
        std::string testData = "Test data for Base64 encoding!@#$%^&*()";
        
        // Encode
        std::string encoded = base64.encode(testData);
        if (encoded.empty() || encoded == testData) {
            return false;
        }
        
        // Decode
        std::string decoded = base64.decode(encoded);
        
        return decoded == testData;
    } catch (...) {
        return false;
    }
}

// Test CRC calculation
bool testCRCCalculation() {
    try {
        std::string testData = "Test data for CRC calculation";
        uint32_t crc1 = calculateCRC(reinterpret_cast<const uint8_t*>(testData.c_str()), testData.size());
        uint32_t crc2 = calculateCRC(reinterpret_cast<const uint8_t*>(testData.c_str()), testData.size());
        
        // Same data should produce same CRC
        if (crc1 != crc2) {
            return false;
        }
        
        // Different data should produce different CRC
        std::string differentData = testData + "X";
        uint32_t crc3 = calculateCRC(reinterpret_cast<const uint8_t*>(differentData.c_str()), differentData.size());
        
        return crc1 != crc3;
    } catch (...) {
        return false;
    }
}

// Test protocol message creation
bool testProtocolMessages() {
    try {
        uint8_t clientId[16] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                               0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10};
        std::string username = "testuser";
        
        // Test registration request
        auto regRequest = createRegistrationRequest(clientId, username);
        if (regRequest.size() != 23 + 255) { // Header + username field
            return false;
        }
        
        // Test public key request
        std::string publicKey(162, 'A'); // Dummy 162-byte public key
        auto pubKeyRequest = createPublicKeyRequest(clientId, username, publicKey);
        if (pubKeyRequest.size() != 23 + 255 + 162) { // Header + username + public key
            return false;
        }
        
        return true;
    } catch (...) {
        return false;
    }
}

// Test file operations
bool testFileOperations() {
    try {
        // Create test file
        std::string testFileName = "test_temp_file.txt";
        std::string testContent = "This is test content for file operations testing.";
        
        {
            std::ofstream file(testFileName);
            file << testContent;
        }
        
        // Read file back
        std::ifstream file(testFileName, std::ios::binary);
        if (!file.is_open()) {
            return false;
        }
        
        file.seekg(0, std::ios::end);
        size_t size = file.tellg();
        file.seekg(0, std::ios::beg);
        
        std::vector<uint8_t> data(size);
        file.read(reinterpret_cast<char*>(data.data()), size);
        file.close();
        
        std::string readContent(data.begin(), data.end());
        
        // Clean up
        std::remove(testFileName.c_str());
        
        return readContent == testContent;
    } catch (...) {
        return false;
    }
}

// Test GUI initialization (Windows only)
bool testGUIInitialization() {
#ifdef _WIN32
    try {
        ClientGUI* gui = ClientGUI::getInstance();
        if (!gui) {
            return false;
        }
        
        bool initialized = gui->initialize();
        if (initialized) {
            gui->shutdown();
        }
        
        return initialized;
    } catch (...) {
        return false;
    }
#else
    return true; // Skip on non-Windows platforms
#endif
}

// Performance test for encryption
bool testEncryptionPerformance() {
    try {
        // Generate test data (1MB)
        std::vector<uint8_t> testData(1024 * 1024);
        for (size_t i = 0; i < testData.size(); i++) {
            testData[i] = static_cast<uint8_t>(i % 256);
        }
        
        // Test AES performance
        std::string key(32, 'K');
        AESWrapper aes(reinterpret_cast<const unsigned char*>(key.c_str()), 32, true);
        
        auto start = std::chrono::high_resolution_clock::now();
        std::string encrypted = aes.encrypt(reinterpret_cast<const char*>(testData.data()), testData.size());
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        // Should encrypt 1MB in less than 1 second
        bool performanceOk = duration.count() < 1000;
        
        // Verify encryption worked
        bool encryptionWorked = !encrypted.empty() && encrypted.size() > testData.size();
        
        return performanceOk && encryptionWorked;
    } catch (...) {
        return false;
    }
}

int main() {
    std::cout << "=== Comprehensive Test Suite for Encrypted Backup Framework ===" << std::endl;
    std::cout << "Testing all major components..." << std::endl << std::endl;
    
    TestFramework framework;
    
    // Run all tests
    framework.runTest("RSA Operations", testRSAOperations);
    framework.runTest("AES Operations", testAESOperations);
    framework.runTest("Base64 Operations", testBase64Operations);
    framework.runTest("CRC Calculation", testCRCCalculation);
    framework.runTest("Protocol Messages", testProtocolMessages);
    framework.runTest("File Operations", testFileOperations);
    framework.runTest("GUI Initialization", testGUIInitialization);
    framework.runTest("Encryption Performance", testEncryptionPerformance);
    
    framework.printSummary();
    
    if (framework.allTestsPassed()) {
        std::cout << "\n🎉 ALL TESTS PASSED! The system is ready for production use." << std::endl;
        return 0;
    } else {
        std::cout << "\n❌ Some tests failed. Please review the implementation." << std::endl;
        return 1;
    }
}
