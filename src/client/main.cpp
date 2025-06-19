#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <memory>
#include <csignal>
#include <exception>
#include "../../include/client/ClientLogger.h"

#ifdef _WIN32
#include <windows.h>
#include <conio.h>
#endif

// Global logger instance
ClientLogger* g_logger = nullptr;

// Global batch mode flag - accessible from other source files
extern bool g_batchMode;

// Forward declaration - we need to include the actual client class
class Client;

// Declare the actual client run function
extern bool runBackupClient();

// Signal handler for graceful shutdown
std::atomic<bool> g_shutdownRequested(false);

void signalHandler(int signal) {
    if (g_logger) {
        g_logger->warning("Shutdown signal received: " + std::to_string(signal));
    }
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
        // Initialize logging system first
        g_logger = new ClientLogger("client_debug.log", ClientLogger::LogLevel::INFO, true, true);
        if (g_batchMode) {
            LOG_INFO("🔒 Encrypted Backup Client v3.0 - BATCH MODE");
        } else {
            LOG_INFO("🔒 Encrypted Backup Client v3.0 - Production Ready");
        }
        LOG_INFO("Starting client initialization...");
        
        // Set up signal handlers for graceful shutdown
        std::signal(SIGINT, signalHandler);
        std::signal(SIGTERM, signalHandler);
        
#ifdef _WIN32
        // Windows-specific console setup
        SetConsoleTitleA("Encrypted Backup Client v3.0");
        LOG_DEBUG("Windows console title set");
#endif
        
        LOG_INFO("About to create client object...");
        
        // Run the main backup client
        bool success = false;
        try {
            success = runBackupClient();
        } catch (const std::runtime_error& e) {
            LOG_ERRORF("Runtime error in backup client: %s", e.what());
            std::cerr << "❌ Runtime error: " << e.what() << std::endl;
        } catch (const std::logic_error& e) {
            LOG_ERRORF("Logic error in backup client: %s", e.what());
            std::cerr << "❌ Logic error: " << e.what() << std::endl;
        } catch (const std::exception& e) {
            LOG_ERRORF("Standard exception in backup client: %s", e.what());
            std::cerr << "❌ Exception: " << e.what() << std::endl;
        }
          if (success) {
            LOG_INFO("✅ Backup completed successfully!");
            if (!g_batchMode) {
                std::cout << "✅ Backup completed successfully!" << std::endl;
            }
            exitCode = 0;
        } else {
            LOG_ERROR("❌ Backup failed!");
            if (!g_batchMode) {
                std::cerr << "❌ Backup failed!" << std::endl;
            }
            exitCode = 1;
        }
        
    } catch (const std::bad_alloc& e) {
        std::cerr << "❌ Memory allocation failed: " << e.what() << std::endl;
        if (g_logger) LOG_CRITICAL("Memory allocation failed: " + std::string(e.what()));
        exitCode = 2;
    } catch (const std::exception& e) {
        std::cerr << "❌ Fatal error: " << e.what() << std::endl;
        if (g_logger) LOG_CRITICAL("Fatal error: " + std::string(e.what()));
        exitCode = 3;
    } catch (...) {
        std::cerr << "❌ Unknown fatal error occurred!" << std::endl;
        if (g_logger) LOG_CRITICAL("Unknown fatal error occurred!");
        exitCode = 4;
    }
    
    // Clean up logging
    if (g_logger) {
        LOG_INFOF("Client exiting with code: %d", exitCode);
        delete g_logger;
        g_logger = nullptr;
    }
    
#ifdef _WIN32
    // On Windows, wait for user input in debug builds
    #ifdef _DEBUG
    std::cout << "\nPress any key to exit..." << std::endl;
    _getch();
    #endif
#endif
    
    return exitCode;
}
