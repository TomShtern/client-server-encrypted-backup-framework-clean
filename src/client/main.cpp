#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>

// Forward declaration - we need to include the actual client class
class Client;

// Declare the actual client run function
extern bool runBackupClient();

int main() {
    std::cout << "🔒 Encrypted Backup Client v3.0 - Starting...\n";

    try {
        // For now, run the backup client directly without complex GUI initialization
        // The client.cpp has its own GUI handling through ClientWebSocketServer
        if (runBackupClient()) {
            std::cout << "✅ Backup completed successfully!" << std::endl;
            return 0;
        } else {
            std::cerr << "❌ Backup failed!" << std::endl;
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "Unknown fatal error occurred!" << std::endl;
        return 1;
    }
}
