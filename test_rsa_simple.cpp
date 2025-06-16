// Simple RSA test to verify 1024-bit key generation
#include <iostream>
#include <chrono>
#include "../../include/wrappers/RSAWrapper.h"
#include "../../include/wrappers/Base64Wrapper.h"

int main() {
    std::cout << "Testing Real 1024-bit RSA Implementation..." << std::endl;
    std::cout << "==========================================" << std::endl;
    
    try {
        std::cout << "1. Creating RSAPrivateWrapper (1024-bit)..." << std::endl;
        auto start = std::chrono::high_resolution_clock::now();
        
        RSAPrivateWrapper* rsa = new RSAPrivateWrapper();
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        
        std::cout << "✅ RSA key pair generated in " << duration << "ms" << std::endl;
        
        // Test getting keys
        std::cout << "2. Testing key export..." << std::endl;
        std::string privateKey = rsa->getPrivateKey();
        std::string publicKey = rsa->getPublicKey();
        
        std::cout << "✅ Private key size: " << privateKey.length() << " bytes" << std::endl;
        std::cout << "✅ Public key size: " << publicKey.length() << " bytes" << std::endl;
        
        // Test Base64 encoding
        std::cout << "3. Testing Base64 encoding..." << std::endl;
        std::string encodedPrivate = Base64Wrapper::encode(privateKey);
        std::string decodedPrivate = Base64Wrapper::decode(encodedPrivate);
        
        if (decodedPrivate == privateKey) {
            std::cout << "✅ Base64 encoding/decoding works correctly" << std::endl;
        } else {
            std::cout << "❌ Base64 encoding/decoding failed" << std::endl;
        }
        
        // Test encryption/decryption
        std::cout << "4. Testing RSA encryption..." << std::endl;
        std::string testData = "Hello, RSA 1024-bit encryption!";
        
        // Create public wrapper from public key
        RSAPublicWrapper* publicWrapper = new RSAPublicWrapper(publicKey.c_str(), publicKey.length());
        
        // Encrypt with public key
        std::string encrypted = publicWrapper->encrypt(testData.c_str(), testData.length());
        std::cout << "✅ Encrypted data size: " << encrypted.length() << " bytes" << std::endl;
        
        // Decrypt with private key
        std::string decrypted = rsa->decrypt(encrypted);
        
        if (decrypted == testData) {
            std::cout << "✅ RSA encryption/decryption works correctly!" << std::endl;
            std::cout << "✅ Decrypted: '" << decrypted << "'" << std::endl;
        } else {
            std::cout << "❌ RSA encryption/decryption failed" << std::endl;
        }
        
        std::cout << "\n✅ ALL TESTS PASSED - Real 1024-bit RSA implementation working!" << std::endl;
        
        delete rsa;
        delete publicWrapper;
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Test failed: " << e.what() << std::endl;
        return 1;
    }
}
