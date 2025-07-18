#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <memory>
#include <csignal>
#include <exception>
#include <string>

#ifdef _WIN32
#include <windows.h>
#include <conio.h>
#endif

// Global batch mode flag - accessible from other source files
extern bool g_batchMode;

// Include the client header
#include "client/client.h"

// Signal handler for graceful shutdown
std::atomic<bool> g_shutdownRequested(false);

void signalHandler(int signal) {
    std::cout << "Shutdown signal received: " << signal << std::endl;
    g_shutdownRequested.store(true);
}

// Global flag for batch mode
bool g_batchMode = false;

// Production-ready main function with comprehensive error handling
int main(int argc, char* argv[]) {
    int exitCode = 1;
    
    // Parse command line arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--batch" || arg == "--non-interactive" || arg == "-b") {
            g_batchMode = true;
            break;
        }
    }
    
    try {
        // Initialize console output
        if (g_batchMode) {
            std::cout << "🔒 Encrypted Backup Client v3.0 - BATCH MODE" << std::endl;
        } else {
            std::cout << "🔒 Encrypted Backup Client v3.0 - Production Ready" << std::endl;
        }
        std::cout << "Starting client initialization..." << std::endl;

        // Set up signal handlers for graceful shutdown
        std::signal(SIGINT, signalHandler);
        std::signal(SIGTERM, signalHandler);

#ifdef _WIN32
        // Windows-specific console setup
        SetConsoleTitleA("Encrypted Backup Client v3.0");
        std::cout << "Windows console title set" << std::endl;
#endif

        std::cout << "About to create client object..." << std::endl;

        // Create persistent client object that keeps GUI running
        Client client;

        if (!client.initialize()) {
            std::cout << "❌ Client initialization failed!" << std::endl;
            return 1;
        }

        std::cout << "✅ Client initialized successfully!" << std::endl;
        std::cout << "🌐 Web GUI available at: http://127.0.0.1:9090" << std::endl;
        std::cout << "📁 Ready for backup operations..." << std::endl;
        std::cout << "Press Ctrl+C to exit" << std::endl;

        // Keep the client alive and GUI server running
        while (!g_shutdownRequested.load()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        std::cout << "✅ Shutdown requested, cleaning up..." << std::endl;
        exitCode = 0;
        
    } catch (const std::bad_alloc& e) {
        std::cerr << "❌ Memory allocation failed: " << e.what() << std::endl;
        exitCode = 2;
    } catch (const std::exception& e) {
        std::cerr << "❌ Fatal error: " << e.what() << std::endl;
        exitCode = 3;
    } catch (...) {
        std::cerr << "❌ Unknown fatal error occurred!" << std::endl;
        exitCode = 4;
    }

    std::cout << "Client exiting with code: " << exitCode << std::endl;
    
#ifdef _WIN32
    // On Windows, wait for user input in debug builds
    #ifdef _DEBUG
    std::cout << "\nPress any key to exit..." << std::endl;
    _getch();
    #endif
#endif
    
    return exitCode;
}
