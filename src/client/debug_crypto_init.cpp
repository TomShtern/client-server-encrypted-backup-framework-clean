#include <iostream>
#include "osrng.h"
#include "cryptlib.h"

int main() {
    std::cout << "[DEBUG] main() entered. Attempting to initialize Crypto++..." << std::endl;
    try {
        CryptoPP::AutoSeededRandomPool rng;
        std::cout << "[SUCCESS] Crypto++ AutoSeededRandomPool constructed successfully." << std::endl;
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "[FATAL] Crypto++ exception during initialization: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "[FATAL] Standard exception during initialization: " << e.what() << std::endl;
        return 1;
    }

    std::cout << "[DEBUG] Program finished successfully. The Crypto++ library can be initialized." << std::endl;
    return 0;
}
