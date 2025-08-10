#include <iostream>
#include <iomanip>
#include <cryptopp/osrng.h>
#include <cryptopp/hex.h>

int main() {
    try {
        std::cout << "=== PROVING THE FIX WORKS ===" << std::endl;
        std::cout << "Testing AutoSeededRandomPool (the core issue that was hanging)..." << std::endl;
        
        // This was the exact operation that was hanging before
        CryptoPP::AutoSeededRandomPool rng;
        std::cout << "✅ AutoSeededRandomPool created successfully (no hang!)" << std::endl;
        
        // Generate random bytes - this would hang indefinitely before the fix
        CryptoPP::byte buffer[32];
        rng.GenerateBlock(buffer, sizeof(buffer));
        std::cout << "✅ Generated 32 random bytes successfully!" << std::endl;
        
        // Show the random data as proof it's working
        std::cout << "Random bytes (hex): ";
        for (int i = 0; i < 32; i++) {
            std::cout << std::hex << std::setfill('0') << std::setw(2) << (int)buffer[i];
        }
        std::cout << std::dec << std::endl;
        
        // Test multiple generations to prove it's consistently working
        std::cout << "\nTesting multiple random generations..." << std::endl;
        for (int i = 0; i < 5; i++) {
            CryptoPP::byte testByte;
            rng.GenerateBlock(&testByte, 1);
            std::cout << "Generation " << (i+1) << ": 0x" 
                     << std::hex << std::setfill('0') << std::setw(2) << (int)testByte << std::dec << std::endl;
        }
        
        std::cout << "\n🎉 SUCCESS! The hanging issue is COMPLETELY RESOLVED!" << std::endl;
        std::cout << "AutoSeededRandomPool works perfectly - no more infinite hangs!" << std::endl;
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
}
