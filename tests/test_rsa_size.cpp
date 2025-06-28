#include "include/wrappers/RSAWrapper.h"
#include <iostream>

int main() {
    try {
        std::cout << "Creating RSA key pair..." << std::endl;
        RSAPrivateWrapper rsa;
        
        std::string publicKey = rsa.getPublicKey();
        std::cout << "RSA Public Key Size: " << publicKey.size() << " bytes" << std::endl;
        std::cout << "RSAPublicWrapper::KEYSIZE constant: " << RSAPublicWrapper::KEYSIZE << " bytes" << std::endl;
        std::cout << "RSA_KEY_SIZE should be: " << publicKey.size() << " bytes" << std::endl;
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
