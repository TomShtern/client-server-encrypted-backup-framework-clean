#include <iostream>
#include <string>
#include "third_party/crypto++/osrng.h"

int main() {
    try {
        std::cout << "Testing AutoSeededRandomPool..." << std::endl;
        
        CryptoPP::AutoSeededRandomPool rng;
        
        // Generate 16 random bytes
        unsigned char buffer[16];
        rng.GenerateBlock(buffer, sizeof(buffer));
        
        std::cout << "Generated random bytes: ";
        for (int i = 0; i < 16; i++) {
            std::cout << std::hex << (int)buffer[i] << " ";
        }
        std::cout << std::endl;
        
        std::cout << "AutoSeededRandomPool test PASSED!" << std::endl;
        
    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
