#include <iostream>
#include <chrono>
#include "third_party/crypto++/osrng.h"

int main() {
    std::cout << "=== AUTOSEEDED RANDOM POOL TEST ===" << std::endl;
    
    try {
        std::cout << "[INFO] This test focuses on the core hang issue with AutoSeededRandomPool" << std::endl;
        std::cout << "[TEST] Creating AutoSeededRandomPool (this is where the hang occurred)..." << std::endl;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        // This is the exact line that was causing the hang
        CryptoPP::AutoSeededRandomPool rng(false, 16);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "[SUCCESS] AutoSeededRandomPool created in " << duration.count() << "ms!" << std::endl;
        
        std::cout << "[TEST] Generating random bytes..." << std::endl;
        CryptoPP::byte testBytes[32];
        rng.GenerateBlock(testBytes, 32);
        
        std::cout << "[SUCCESS] Generated random bytes: ";
        for (int i = 0; i < 8; i++) {
            std::cout << std::hex << (int)testBytes[i] << " ";
        }
        std::cout << "..." << std::endl;
        
        std::cout << "[SUCCESS] AutoSeededRandomPool fix is working correctly!" << std::endl;
        std::cout << "[RESULT] The hang issue has been RESOLVED with your comprehensive crypto++ build!" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "[ERROR] AutoSeededRandomPool test failed: " << e.what() << std::endl;
        return 1;
    }
}
