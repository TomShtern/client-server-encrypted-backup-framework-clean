#include "aes_crypto.h"
#include <iostream>
#include <vector>
#include <string>
#include <cassert>

/**
 * Comprehensive test suite for AES crypto implementation
 * Tests all major functionality needed for the simple client
 */

class AESCryptoTester {
private:
    AESCrypto crypto;
    int testsPassed = 0;
    int testsTotal = 0;
    
    void runTest(const std::string& testName, bool result) {
        testsTotal++;
        std::cout << "[TEST] " << testName << ": ";
        if (result) {
            std::cout << "✅ PASSED" << std::endl;
            testsPassed++;
        } else {
            std::cout << "❌ FAILED" << std::endl;
        }
    }
    
public:
    void testBasicFunctionality() {
        std::cout << "\n=== BASIC FUNCTIONALITY TESTS ===" << std::endl;
        
        // Test 1: Initial state
        runTest("Initial state check", !crypto.isReady());
        
        // Test 2: Manual AES key setting
        std::vector<uint8_t> testKey(32, 0x42); // 32 bytes of 0x42
        runTest("Set AES key manually", crypto.setAESKey(testKey));
        runTest("Crypto ready after key set", crypto.isReady());
        
        // Test 3: Get AES key
        std::vector<uint8_t> retrievedKey = crypto.getAESKey();
        runTest("Get AES key matches set key", retrievedKey == testKey);
        
        // Test 4: Reset functionality
        crypto.reset();
        runTest("Reset clears state", !crypto.isReady());
    }
    
    void testEncryptionDecryption() {
        std::cout << "\n=== ENCRYPTION/DECRYPTION TESTS ===" << std::endl;
        
        // Set up crypto with known key
        std::vector<uint8_t> testKey(32);
        for (int i = 0; i < 32; i++) {
            testKey[i] = static_cast<uint8_t>(i);
        }
        crypto.setAESKey(testKey);
        
        // Test data of various sizes
        std::vector<std::vector<uint8_t>> testCases = {
            {'H', 'e', 'l', 'l', 'o'},                                    // 5 bytes
            {'T', 'h', 'i', 's', ' ', 'i', 's', ' ', 'a', ' ', 't', 'e', 's', 't'}, // 14 bytes
            std::vector<uint8_t>(16, 'A'),                                // Exactly one block
            std::vector<uint8_t>(32, 'B'),                                // Exactly two blocks
            std::vector<uint8_t>(33, 'C'),                                // More than two blocks
            std::vector<uint8_t>(1000, 'D'),                              // Large data
        };
        
        for (size_t i = 0; i < testCases.size(); i++) {
            std::string testName = "Roundtrip test case " + std::to_string(i + 1) + 
                                 " (" + std::to_string(testCases[i].size()) + " bytes)";
            runTest(testName, crypto.testRoundtrip(testCases[i]));
        }
    }
    
    void testFileOperations() {
        std::cout << "\n=== FILE OPERATION TESTS ===" << std::endl;
        
        // Create test file
        std::string testFilename = "test_crypto_file.tmp";
        std::vector<uint8_t> testData = {'T', 'e', 's', 't', ' ', 'f', 'i', 'l', 'e', ' ', 'd', 'a', 't', 'a'};
        
        runTest("Save test file", AESCryptoUtils::saveFile(testFilename, testData));
        
        std::vector<uint8_t> loadedData = AESCryptoUtils::loadFile(testFilename);
        runTest("Load test file", loadedData == testData);
        
        // Clean up
        std::remove(testFilename.c_str());
    }
    
    void testUtilityFunctions() {
        std::cout << "\n=== UTILITY FUNCTION TESTS ===" << std::endl;
        
        // Test hex conversion
        std::vector<uint8_t> testBytes = {0xDE, 0xAD, 0xBE, 0xEF, 0x12, 0x34};
        std::string expectedHex = "deadbeef1234";
        
        std::string actualHex = AESCryptoUtils::bytesToHex(testBytes);
        runTest("Bytes to hex conversion", actualHex == expectedHex);
        
        std::vector<uint8_t> actualBytes = AESCryptoUtils::hexToBytes(expectedHex);
        runTest("Hex to bytes conversion", actualBytes == testBytes);
    }
    
    void testErrorHandling() {
        std::cout << "\n=== ERROR HANDLING TESTS ===" << std::endl;
        
        AESCrypto testCrypto;
        
        // Test encryption without key
        std::vector<uint8_t> testData = {'t', 'e', 's', 't'};
        bool caughtException = false;
        try {
            testCrypto.encryptFileData(testData);
        } catch (const std::runtime_error&) {
            caughtException = true;
        }
        runTest("Encryption without key throws exception", caughtException);
        
        // Test invalid key size
        std::vector<uint8_t> invalidKey(16); // Wrong size (16 instead of 32)
        runTest("Invalid key size rejected", !testCrypto.setAESKey(invalidKey));
        
        // Test empty data encryption
        std::vector<uint8_t> validKey(32, 0x55);
        testCrypto.setAESKey(validKey);
        caughtException = false;
        try {
            std::vector<uint8_t> emptyData;
            testCrypto.encryptFileData(emptyData);
        } catch (const std::runtime_error&) {
            caughtException = true;
        }
        runTest("Empty data encryption throws exception", caughtException);
    }
    
    void testMockRSAKeyDecryption() {
        std::cout << "\n=== MOCK RSA KEY DECRYPTION TEST ===" << std::endl;
        
        // Test with mock encrypted AES key (would normally come from server)
        // For testing, we'll create a mock scenario
        std::vector<uint8_t> mockEncryptedKey(144, 0xAB); // Mock 144-byte encrypted key
        
        // This test will likely fail since we don't have proper RSA setup,
        // but it demonstrates the interface
        bool result = crypto.decryptAndLoadAESKey(mockEncryptedKey);
        std::cout << "[TEST] Mock RSA key decryption: ";
        if (result) {
            std::cout << "✅ PASSED (unexpected - no real keys available)" << std::endl;
        } else {
            std::cout << "❌ FAILED (expected - no real RSA keys set up)" << std::endl;
        }
        std::cout << "[INFO] This test requires proper RSA key setup to pass" << std::endl;
    }
    
    void runAllTests() {
        std::cout << "🔒 AES Crypto Implementation Test Suite" << std::endl;
        std::cout << "=======================================" << std::endl;
        
        testBasicFunctionality();
        testEncryptionDecryption();
        testFileOperations();
        testUtilityFunctions();
        testErrorHandling();
        testMockRSAKeyDecryption();
        
        std::cout << "\n=== TEST RESULTS ===" << std::endl;
        std::cout << "Tests passed: " << testsPassed << "/" << testsTotal << std::endl;
        
        if (testsPassed == testsTotal) {
            std::cout << "🎉 ALL TESTS PASSED!" << std::endl;
        } else {
            std::cout << "⚠️  Some tests failed - check implementation" << std::endl;
        }
        
        // Calculate percentage
        double percentage = (static_cast<double>(testsPassed) / testsTotal) * 100.0;
        std::cout << "Success rate: " << std::fixed << std::setprecision(1) << percentage << "%" << std::endl;
    }
};

// Simple client integration demo
void demonstrateSimpleClientIntegration() {
    std::cout << "\n🔗 SIMPLE CLIENT INTEGRATION DEMO" << std::endl;
    std::cout << "==================================" << std::endl;
    
    AESCrypto clientCrypto;
    
    // Step 1: Simulate receiving encrypted AES key from server
    std::cout << "[DEMO] Step 1: Server sends encrypted AES key (144 bytes)" << std::endl;
    std::vector<uint8_t> encryptedAESKey(144, 0xCC); // Mock encrypted key
    
    // Step 2: Try to decrypt AES key (will fail without proper RSA setup)
    std::cout << "[DEMO] Step 2: Attempting to decrypt AES key..." << std::endl;
    bool keyDecrypted = clientCrypto.decryptAndLoadAESKey(encryptedAESKey);
    
    if (!keyDecrypted) {
        std::cout << "[DEMO] Key decryption failed (expected) - using manual key for demo" << std::endl;
        // For demo, set a manual key
        std::vector<uint8_t> demoKey(32, 0x77);
        clientCrypto.setAESKey(demoKey);
    }
    
    // Step 3: Encrypt file data
    std::cout << "[DEMO] Step 3: Encrypting file data..." << std::endl;
    std::string fileContent = "This is test file content that would be sent to the server.";
    std::vector<uint8_t> fileData(fileContent.begin(), fileContent.end());
    
    try {
        std::vector<uint8_t> encryptedFile = clientCrypto.encryptFileData(fileData);
        std::cout << "[DEMO] ✅ File encrypted successfully!" << std::endl;
        std::cout << "[DEMO]    Original size: " << fileData.size() << " bytes" << std::endl;
        std::cout << "[DEMO]    Encrypted size: " << encryptedFile.size() << " bytes" << std::endl;
        
        // Step 4: Verify decryption works
        std::vector<uint8_t> decryptedFile = clientCrypto.decryptFileData(encryptedFile);
        bool roundtripSuccess = (decryptedFile == fileData);
        
        std::cout << "[DEMO] Step 4: Decryption verification: " 
                  << (roundtripSuccess ? "✅ SUCCESS" : "❌ FAILED") << std::endl;
        
        if (roundtripSuccess) {
            std::cout << "[DEMO] 🎉 Complete encryption workflow demonstrated!" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cout << "[DEMO] ❌ Encryption failed: " << e.what() << std::endl;
    }
}

int main() {
    // Run comprehensive test suite
    AESCryptoTester tester;
    tester.runAllTests();
    
    // Show integration demo
    demonstrateSimpleClientIntegration();
    
    std::cout << "\n📋 USAGE NOTES FOR SIMPLE CLIENT:" << std::endl;
    std::cout << "1. Include aes_crypto.h and aes_crypto.cpp in your build" << std::endl;
    std::cout << "2. Link with existing Crypto++ libraries (already in project)" << std::endl;
    std::cout << "3. Call decryptAndLoadAESKey() with server's encrypted key" << std::endl;
    std::cout << "4. Use encryptFileData() before sending files to server" << std::endl;
    std::cout << "5. Implementation uses zero IV as per project specification" << std::endl;
    
    std::cout << "\nPress Enter to exit..." << std::endl;
    std::cin.get();
    
    return 0;
}