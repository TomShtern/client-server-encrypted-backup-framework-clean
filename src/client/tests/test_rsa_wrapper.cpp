#include <iostream>
#include "include/wrappers/RSAWrapper.h"

int main() {
    try {
        std::cout << "[TEST] Starting RSA key generation test..." << std::endl;
        
        // Initialize RSA wrapper
        RSAPublicWrapper rsa;
        std::cout << "[TEST] RSAPublicWrapper created successfully" << std::endl;
        
        // Generate key pair (this is the critical test)
        std::cout << "[TEST] Generating 1024-bit RSA key pair..." << std::endl;
        rsa.GenerateKeys(1024);
        std::cout << "[TEST] ✅ RSA key generation completed successfully!" << std::endl;
        
        // Test if we can get the public key
        std::string publicKey = rsa.getPublicKey();
        if (!publicKey.empty()) {
            std::cout << "[TEST] ✅ Public key retrieved successfully" << std::endl;
        } else {
            std::cout << "[TEST] ❌ Public key is empty" << std::endl;
            return 1;
        }
        
        std::cout << "[TEST] ✅ All RSA operations completed without hanging!" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "[TEST] ❌ Exception: " << e.what() << std::endl;
        return 1;
    }
}
