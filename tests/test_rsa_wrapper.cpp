#include "../../include/wrappers/RSAWrapper.h"
#include <iostream>
#include <string>
#include <cassert>

void test_rsa_key_generation() {
    std::cout << "[TEST] Starting RSA key generation test" << std::endl;
    try {
        RSAPrivateWrapper privateWrapper;
        std::string privateKey = privateWrapper.getPrivateKey();
        std::string publicKey = privateWrapper.getPublicKey();
        
        assert(!privateKey.empty() && "Private key should not be empty");
        assert(!publicKey.empty() && "Public key should not be empty");
        std::cout << "[TEST] RSA key generation successful. Private key size: " << privateKey.size() << " bytes, Public key size: " << publicKey.size() << " bytes" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "[TEST ERROR] RSA key generation failed: " << e.what() << std::endl;
        assert(false && "RSA key generation failed");
    }
}

void test_rsa_encryption_decryption() {
    std::cout << "[TEST] Starting RSA encryption/decryption test" << std::endl;
    try {
        RSAPrivateWrapper privateWrapper;
        std::string publicKey = privateWrapper.getPublicKey();
        
        RSAPublicWrapper publicWrapper(publicKey.c_str(), publicKey.size());
        
        std::string originalText = "Test message for RSA encryption and decryption.";
        std::cout << "[TEST] Original text: " << originalText << std::endl;
        
        std::string encrypted = publicWrapper.encrypt(originalText);
        std::cout << "[TEST] Encryption successful. Encrypted size: " << encrypted.size() << " bytes" << std::endl;
        
        std::string decrypted = privateWrapper.decrypt(encrypted);
        std::cout << "[TEST] Decryption successful. Decrypted text: " << decrypted << std::endl;
        
        assert(originalText == decrypted && "Decrypted text should match original text");
        std::cout << "[TEST] RSA encryption/decryption test passed!" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "[TEST ERROR] RSA encryption/decryption failed: " << e.what() << std::endl;
        assert(false && "RSA encryption/decryption failed");
    }
}

int main() {
    std::cout << "[TEST SUITE] Starting RSA Wrapper Tests" << std::endl;
    test_rsa_key_generation();
    test_rsa_encryption_decryption();
    std::cout << "[TEST SUITE] All RSA Wrapper Tests completed successfully!" << std::endl;
    return 0;
}
