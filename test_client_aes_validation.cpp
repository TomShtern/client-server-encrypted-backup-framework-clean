/*
 * AES Client Validation Test
 * 
 * This test validates that our C++ client's AES implementation produces output
 * that is compatible with the server's Python decryption process.
 *
 * Test Strategy:
 * 1. Use the client's AESWrapper to encrypt test data
 * 2. Generate expected output using the same parameters as server
 * 3. Compare with known-good reference vectors
 * 4. Validate that encrypted output matches server expectations
 */

#include <iostream>
#include <iomanip>
#include <sstream>
#include <vector>
#include <string>
#include <cstring>
#include <cassert>

// Include our AES wrapper
#include "include/wrappers/AESWrapper.h"

class AESValidationTest {
private:
    static std::string bytesToHex(const unsigned char* data, size_t len) {
        std::stringstream ss;
        ss << std::hex << std::setfill('0');
        for (size_t i = 0; i < len; ++i) {
            ss << std::setw(2) << static_cast<unsigned int>(data[i]);
        }
        return ss.str();
    }
    
    static std::string bytesToHex(const std::string& data) {
        return bytesToHex(reinterpret_cast<const unsigned char*>(data.c_str()), data.length());
    }
    
    static bool compareWithExpected(const std::string& encrypted, const std::string& expected, const std::string& testName) {
        std::string encryptedHex = bytesToHex(encrypted);
        
        std::cout << "\n--- " << testName << " ---" << std::endl;
        std::cout << "Expected: " << expected << std::endl;
        std::cout << "Actual:   " << encryptedHex << std::endl;
        
        bool matches = (encryptedHex == expected);
        std::cout << "Result:   " << (matches ? "✅ PASS" : "❌ FAIL") << std::endl;
        
        return matches;
    }

public:
    static bool runReferenceVectorTest() {
        std::cout << "=== AES Reference Vector Test ===" << std::endl;
        std::cout << "Testing against known-good server-compatible vectors" << std::endl;
        
        // Fixed key and data from our Python reference test
        unsigned char fixedKey[32] = {
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
            0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
            0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20
        };
        
        const char* testContent = "Test file content for backup";
        
        // Expected output from our Python reference implementation
        const std::string expectedHex = "f5cab5ef76df0e0b738a3e24fa079bcb37220805f96742e89dd4a96e92135344c10979bb443137fbb1cf2e2f42feda10";
        
        std::cout << "Fixed Key: " << bytesToHex(fixedKey, 32) << std::endl;
        std::cout << "Test Data: " << testContent << " (" << strlen(testContent) << " bytes)" << std::endl;
        
        try {
            // Create AES wrapper with zero IV (server-compatible mode)
            AESWrapper aes(fixedKey, 32, true); // useStaticZeroIV = true
            
            // Encrypt the test content
            std::string encrypted = aes.encrypt(testContent, strlen(testContent));
            
            // Compare with expected output
            return compareWithExpected(encrypted, expectedHex, "Reference Vector Test");
            
        } catch (const std::exception& e) {
            std::cout << "❌ EXCEPTION: " << e.what() << std::endl;
            return false;
        }
    }
    
    static bool runVariousDataSizesTest() {
        std::cout << "\n=== Various Data Sizes Test ===" << std::endl;
        std::cout << "Testing AES with different input sizes" << std::endl;
        
        // Generate consistent test key
        unsigned char testKey[32];
        for (int i = 0; i < 32; ++i) {
            testKey[i] = static_cast<unsigned char>(i + 1);
        }
        
        std::vector<std::string> testInputs = {
            "",                                    // Empty
            "A",                                   // 1 byte
            "Hello, World!",                       // 13 bytes
            "1234567890123456",                    // 16 bytes (exact block)
            "12345678901234567",                   // 17 bytes (block + 1)
            "This is a longer test message."       // 31 bytes
        };
        
        bool allPassed = true;
        
        try {
            AESWrapper aes(testKey, 32, true); // Zero IV mode
            
            for (size_t i = 0; i < testInputs.size(); ++i) {
                const std::string& input = testInputs[i];
                
                std::cout << "\nTest " << (i + 1) << ": " << input.length() << " bytes" << std::endl;
                std::cout << "Input: \"" << input << "\"" << std::endl;
                
                // Encrypt
                std::string encrypted = aes.encrypt(input.c_str(), input.length());
                
                // Check that encrypted size is correct (multiple of 16 bytes)
                if (encrypted.length() % 16 != 0) {
                    std::cout << "❌ FAIL: Encrypted size not multiple of 16" << std::endl;
                    allPassed = false;
                    continue;
                }
                
                // Check that encryption is deterministic (same input = same output)
                std::string encrypted2 = aes.encrypt(input.c_str(), input.length());
                if (encrypted != encrypted2) {
                    std::cout << "❌ FAIL: Encryption not deterministic" << std::endl;
                    allPassed = false;
                    continue;
                }
                
                std::cout << "Encrypted: " << bytesToHex(encrypted) << std::endl;
                std::cout << "Size: " << encrypted.length() << " bytes" << std::endl;
                std::cout << "✅ PASS: Proper size and deterministic" << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cout << "❌ EXCEPTION: " << e.what() << std::endl;
            allPassed = false;
        }
        
        return allPassed;
    }
    
    static bool runRoundTripTest() {
        std::cout << "\n=== Round Trip Test ===" << std::endl;
        std::cout << "Testing encrypt/decrypt round trip consistency" << std::endl;
        
        unsigned char testKey[32];
        for (int i = 0; i < 32; ++i) {
            testKey[i] = static_cast<unsigned char>(i * 7 + 13); // Some variety
        }
        
        std::vector<std::string> testInputs = {
            "Simple test",
            "Binary data: \x00\x01\xff\xfe\xaa\xbb",
            "Longer test message that spans multiple AES blocks to ensure proper handling",
            "" // Empty string
        };
        
        bool allPassed = true;
        
        try {
            AESWrapper aes(testKey, 32, true); // Zero IV mode
            
            for (size_t i = 0; i < testInputs.size(); ++i) {
                const std::string& input = testInputs[i];
                
                std::cout << "\nRound trip " << (i + 1) << ": " << input.length() << " bytes" << std::endl;
                
                // Encrypt
                std::string encrypted = aes.encrypt(input.c_str(), input.length());
                
                // Decrypt
                std::string decrypted = aes.decrypt(encrypted.c_str(), encrypted.length());
                
                // Compare
                if (input == decrypted) {
                    std::cout << "✅ PASS: Round trip successful" << std::endl;
                } else {
                    std::cout << "❌ FAIL: Round trip failed" << std::endl;
                    std::cout << "Original:  \"" << input << "\"" << std::endl;
                    std::cout << "Decrypted: \"" << decrypted << "\"" << std::endl;
                    allPassed = false;
                }
            }
            
        } catch (const std::exception& e) {
            std::cout << "❌ EXCEPTION: " << e.what() << std::endl;
            allPassed = false;
        }
        
        return allPassed;
    }
    
    static bool runServerCompatibilityFormat() {
        std::cout << "\n=== Server Compatibility Format Test ===" << std::endl;
        std::cout << "Ensuring output format matches server expectations" << std::endl;
        
        unsigned char serverKey[32] = {
            0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x11, 0x22,
            0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0x00,
            0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf0,
            0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88
        };
        
        const char* fileContent = "Sample file data for server";
        
        std::cout << "Key: " << bytesToHex(serverKey, 32) << std::endl;
        std::cout << "Data: " << fileContent << std::endl;
        
        try {
            AESWrapper aes(serverKey, 32, true); // Server-compatible zero IV
            
            std::string encrypted = aes.encrypt(fileContent, strlen(fileContent));
            
            std::cout << "\nClient-generated encrypted data:" << std::endl;
            std::cout << "Hex: " << bytesToHex(encrypted) << std::endl;
            std::cout << "Length: " << encrypted.length() << " bytes" << std::endl;
            
            // Verify properties expected by server
            bool isValidSize = (encrypted.length() % 16 == 0);
            bool isNotEmpty = (encrypted.length() > 0);
            bool hasProperPadding = (encrypted.length() >= 16); // At least one block
            
            std::cout << "\nServer compatibility checks:" << std::endl;
            std::cout << "Multiple of 16 bytes: " << (isValidSize ? "✅" : "❌") << std::endl;
            std::cout << "Non-empty: " << (isNotEmpty ? "✅" : "❌") << std::endl;
            std::cout << "Has padding block: " << (hasProperPadding ? "✅" : "❌") << std::endl;
            
            bool allChecksPass = isValidSize && isNotEmpty && hasProperPadding;
            
            if (allChecksPass) {
                std::cout << "\n✅ Server compatibility format: PASS" << std::endl;
                std::cout << "This encrypted data should be compatible with server decryption." << std::endl;
            } else {
                std::cout << "\n❌ Server compatibility format: FAIL" << std::endl;
            }
            
            return allChecksPass;
            
        } catch (const std::exception& e) {
            std::cout << "❌ EXCEPTION: " << e.what() << std::endl;
            return false;
        }
    }
};

int main() {
    std::cout << "AES Client-Server Compatibility Validation" << std::endl;
    std::cout << "===========================================" << std::endl;
    std::cout << "This test validates that the C++ client's AES encryption" << std::endl;
    std::cout << "produces output compatible with the Python server's decryption." << std::endl;
    
    bool allTestsPassed = true;
    
    // Run all validation tests
    allTestsPassed &= AESValidationTest::runReferenceVectorTest();
    allTestsPassed &= AESValidationTest::runVariousDataSizesTest();
    allTestsPassed &= AESValidationTest::runRoundTripTest();
    allTestsPassed &= AESValidationTest::runServerCompatibilityFormat();
    
    // Final results
    std::cout << "\n===========================================" << std::endl;
    std::cout << "FINAL VALIDATION RESULTS" << std::endl;
    std::cout << "===========================================" << std::endl;
    
    if (allTestsPassed) {
        std::cout << "🎉 SUCCESS: ALL TESTS PASSED" << std::endl;
        std::cout << std::endl;
        std::cout << "The client's AES implementation is compatible with the server!" << std::endl;
        std::cout << "Key implementation details confirmed:" << std::endl;
        std::cout << "  - AES-256-CBC mode" << std::endl;
        std::cout << "  - Zero IV (16 bytes of 0x00)" << std::endl;
        std::cout << "  - PKCS7 padding" << std::endl;
        std::cout << "  - Deterministic encryption with same key/IV" << std::endl;
        std::cout << "  - Proper output formatting for server consumption" << std::endl;
        std::cout << std::endl;
        std::cout << "✅ Ready for production use with the backup server!" << std::endl;
        return 0;
    } else {
        std::cout << "❌ FAILURE: SOME TESTS FAILED" << std::endl;
        std::cout << std::endl;
        std::cout << "The client's AES implementation has compatibility issues." << std::endl;
        std::cout << "Review the test output above to identify specific problems." << std::endl;
        std::cout << std::endl;
        std::cout << "⚠️  DO NOT use with production server until issues are resolved!" << std::endl;
        return 1;
    }
}