#include <iostream>
#include <string>
#include "third_party/crypto++/osrng.h"
#include "third_party/crypto++/rsa.h"
#include "third_party/crypto++/base64.h"
#include "third_party/crypto++/files.h"

int main() {
    try {
        std::cout << "Testing complete RSA key generation (1024-bit)..." << std::endl;
        
        // Create random number generator
        CryptoPP::AutoSeededRandomPool rng;
        std::cout << "AutoSeededRandomPool created successfully." << std::endl;
        
        // Generate RSA key pair
        std::cout << "Generating 1024-bit RSA key pair..." << std::endl;
        CryptoPP::RSA::PrivateKey privateKey;
        privateKey.GenerateRandomWithKeySize(rng, 1024);
        std::cout << "Private key generated successfully!" << std::endl;
        
        // Get public key
        CryptoPP::RSA::PublicKey publicKey(privateKey);
        std::cout << "Public key derived successfully!" << std::endl;
        
        // Validate keys
        if (privateKey.Validate(rng, 3)) {
            std::cout << "Private key validation: PASSED" << std::endl;
        } else {
            std::cout << "Private key validation: FAILED" << std::endl;
            return 1;
        }
        
        if (publicKey.Validate(rng, 3)) {
            std::cout << "Public key validation: PASSED" << std::endl;
        } else {
            std::cout << "Public key validation: FAILED" << std::endl;
            return 1;
        }
        
        std::cout << "RSA key generation test PASSED!" << std::endl;
        std::cout << "Key size: " << privateKey.GetModulus().BitCount() << " bits" << std::endl;
        
    } catch (const std::exception& e) {
        std::cout << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
