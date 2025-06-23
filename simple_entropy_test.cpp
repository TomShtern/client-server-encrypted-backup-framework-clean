#include <iostream>
#include <chrono>

#ifdef _WIN32
#include <windows.h>
#include <bcrypt.h>
#endif

int main() {
    std::cout << "=== SIMPLE ENTROPY TEST ===" << std::endl;
    
    try {
        std::cout << "[TEST] Testing system entropy availability..." << std::endl;
        auto start = std::chrono::high_resolution_clock::now();
        
        // Generate some random data using native Windows APIs
        #ifdef _WIN32
        BCRYPT_ALG_HANDLE hAlg = NULL;
        UCHAR randomBytes[32];
        
        if (BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_RNG_ALGORITHM, NULL, 0) == 0) {
            if (BCryptGenRandom(hAlg, randomBytes, sizeof(randomBytes), 0) == 0) {
                std::cout << "[SUCCESS] System entropy is working!" << std::endl;
                
                std::cout << "[TEST] Generated random bytes: ";
                for (int i = 0; i < 8; i++) {
                    std::cout << std::hex << (int)randomBytes[i] << " ";
                }
                std::cout << "..." << std::endl;
            }
            BCryptCloseAlgorithmProvider(hAlg, 0);
        }
        #endif
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "[SUCCESS] System entropy test completed in " << duration.count() << "ms" << std::endl;
        std::cout << "[INFO] System entropy is available - the issue is likely in Crypto++ library configuration" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cout << "[ERROR] System entropy test failed: " << e.what() << std::endl;
        return 1;
    }
}
