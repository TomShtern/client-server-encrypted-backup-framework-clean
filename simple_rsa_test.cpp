#include <iostream>
#include <chrono>
#include "third_party/crypto++/osrng.h"

int main() {
    try {
        std::cout << "Testing core entropy functionality that was causing hangs..." << std::endl;
        
        auto start = std::chrono::steady_clock::now();
        
        // This is the exact line that was hanging in the original problem
        std::cout << "Creating AutoSeededRandomPool..." << std::endl;
        CryptoPP::AutoSeededRandomPool rng;
        
        auto end = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "AutoSeededRandomPool created successfully in " << duration.count() << "ms!" << std::endl;
        
        // Test basic random generation
        std::cout << "Testing random byte generation..." << std::endl;
        unsigned char testBytes[32];
        rng.GenerateBlock(testBytes, 32);
        
        std::cout << "Generated 32 random bytes: ";
        for (int i = 0; i < 8; i++) {  // Show first 8 bytes as hex
            std::cout << std::hex << (int)testBytes[i] << " ";
        }
        std::cout << "..." << std::endl;
        
        std::cout << "SUCCESS: Entropy generation works without hanging!" << std::endl;
        std::cout << "The original hang issue has been RESOLVED!" << std::endl;
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << std::endl;
        return 1;
    }
}
