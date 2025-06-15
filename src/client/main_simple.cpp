// Simplified main.cpp without GUI dependencies
#include <iostream>

// Forward declaration of our main backup function
extern bool runBackupClient();

int main() {
    std::cout << "🔒 Encrypted Backup Client v3.0 - Real Crypto Edition" << std::endl;
    std::cout << "✅ Real RSA-1024 with Crypto++" << std::endl;
    std::cout << "✅ Real AES-256-CBC with zero IV" << std::endl;
    std::cout << "✅ PKCS7 padding" << std::endl;
    std::cout << "✅ Protocol Version 3 compliance" << std::endl;
    std::cout << std::endl;

    try {
        bool success = runBackupClient();
        
        if (success) {
            std::cout << "\n✅ All operations completed successfully!" << std::endl;
            return 0;
        } else {
            std::cout << "\n❌ Backup operation failed!" << std::endl;
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal exception: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "Fatal: Unknown exception occurred" << std::endl;
        return 1;
    }
}