#include <iostream>
#include <chrono>

// Crypto++ includes
#include "third_party/crypto++/rsa.h"
#include "third_party/crypto++/osrng.h"
#include "third_party/crypto++/base64.h"
#include "third_party/crypto++/files.h"

int main() {
    std::cout << "Testing Crypto++ RSA key generation..." << std::endl;
    
    try {
        auto start = std::chrono::high_resolution_clock::now();
        
        // Create random number generator
        CryptoPP::AutoSeededRandomPool rng;
        std::cout << "Random number generator created" << std::endl;
        
        // Create RSA private key
        CryptoPP::RSA::PrivateKey privateKey;
        std::cout << "Starting 512-bit RSA key generation..." << std::endl;
        
        // Generate 512-bit key
        privateKey.GenerateRandomWithKeySize(rng, 512);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        std::cout << "RSA key generation completed in " << duration.count() << " ms" << std::endl;
        
        // Test encryption/decryption
        CryptoPP::RSA::PublicKey publicKey(privateKey);
        
        std::string message = "Hello, RSA!";
        std::string encrypted, decrypted;
        
        // Encrypt
        CryptoPP::RSAES_OAEP_SHA_Encryptor encryptor(publicKey);
        CryptoPP::StringSource ss1(message, true,
            new CryptoPP::PK_EncryptorFilter(rng, encryptor,
                new CryptoPP::StringSink(encrypted)
            )
        );
        
        // Decrypt
        CryptoPP::RSAES_OAEP_SHA_Decryptor decryptor(privateKey);
        CryptoPP::StringSource ss2(encrypted, true,
            new CryptoPP::PK_DecryptorFilter(rng, decryptor,
                new CryptoPP::StringSink(decrypted)
            )
        );
        
        std::cout << "Original: " << message << std::endl;
        std::cout << "Decrypted: " << decrypted << std::endl;
        
        if (message == decrypted) {
            std::cout << "SUCCESS: RSA encryption/decryption test passed!" << std::endl;
            return 0;
        } else {
            std::cout << "FAILURE: RSA encryption/decryption test failed!" << std::endl;
            return 1;
        }
        
    } catch (const CryptoPP::Exception& e) {
        std::cerr << "Crypto++ Exception: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Standard Exception: " << e.what() << std::endl;
        return 1;
    }
}
