#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <memory>
#include <csignal>
#include <exception>
#include <string>
#include <sentry.h>

#ifdef _WIN32
#include <windows.h>
#include <conio.h>
#endif

// Global batch mode flag - accessible from other source files
extern bool g_batchMode;

// Include the client header
#include "client.h"

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
    
    // Initialize Sentry for error tracking
    sentry_options_t *options = sentry_options_new();
    sentry_options_set_dsn(options, "https://094a0bee5d42a7f7e8ec8a78a37c8819@o4509746411470848.ingest.us.sentry.io/4509747877773312");
    sentry_options_set_environment(options, "production");
    sentry_options_set_release(options, "cyberbackup-cpp@3.0.0");
    
    if (sentry_init(options) == 0) {
        std::cout << "[SENTRY] Error tracking initialized successfully" << std::endl;
        
        // Set context information
        sentry_set_tag("component", "cpp-client");
        sentry_set_tag("framework", "cyberbackup");
        sentry_set_tag("platform", "windows");
        
        sentry_value_t user = sentry_value_new_object();
        sentry_value_set_by_key(user, "id", sentry_value_new_string("cpp-client"));
        sentry_set_user(user);
    } else {
        std::cout << "[WARNING] Failed to initialize Sentry error tracking" << std::endl;
    }
    
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
            std::cout << "[SECURE] Encrypted Backup Client v3.0 - BATCH MODE" << std::endl;
        } else {
            std::cout << "[SECURE] Encrypted Backup Client v3.0 - Production Ready" << std::endl;
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
            std::cout << "[ERROR] Client initialization failed!" << std::endl;
            return 1;
        }

        std::cout << "[SUCCESS] Client initialized successfully!" << std::endl;

        if (g_batchMode) {
            // Batch mode: perform single backup operation and exit
            std::cout << "[INFO] Starting backup operation..." << std::endl;
            
            bool backupSuccess = client.runBackupOperation();
            
            if (backupSuccess) {
                std::cout << "[SUCCESS] Backup completed successfully!" << std::endl;
                exitCode = 0;
            } else {
                std::cout << "[ERROR] Backup operation failed!" << std::endl;
                exitCode = 1;
            }
        } else {
            // Interactive mode: run web GUI server
            std::cout << "[INFO] Web GUI available at: http://127.0.0.1:9090" << std::endl;
            std::cout << "[INFO] Ready for backup operations..." << std::endl;
            std::cout << "Press Ctrl+C to exit" << std::endl;

            // Keep the client alive and GUI server running
            // Reduced from 100ms to 1000ms to significantly reduce CPU usage
            while (!g_shutdownRequested.load()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(1000));
            }

            std::cout << "[INFO] Shutdown requested, cleaning up..." << std::endl;
            exitCode = 0;
        }
        
    } catch (const std::bad_alloc& e) {
        std::cerr << "[ERROR] Memory allocation failed: " << e.what() << std::endl;
        
        // Report to Sentry
        sentry_value_t exc = sentry_value_new_exception("std::bad_alloc", e.what());
        sentry_value_t event = sentry_value_new_event();
        sentry_value_set_by_key(event, "exception", exc);
        sentry_capture_event(event);
        
        exitCode = 2;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Fatal error: " << e.what() << std::endl;
        
        // Report to Sentry
        sentry_value_t exc = sentry_value_new_exception("std::exception", e.what());
        sentry_value_t event = sentry_value_new_event();
        sentry_value_set_by_key(event, "exception", exc);
        sentry_capture_event(event);
        
        exitCode = 3;
    } catch (...) {
        std::cerr << "[ERROR] Unknown fatal error occurred!" << std::endl;
        
        // Report to Sentry
        sentry_value_t exc = sentry_value_new_exception("unknown_exception", "Unknown fatal error");
        sentry_value_t event = sentry_value_new_event();
        sentry_value_set_by_key(event, "exception", exc);
        sentry_capture_event(event);
        
        exitCode = 4;
    }

    std::cout << "Client exiting with code: " << exitCode << std::endl;
    
    // Cleanup Sentry
    sentry_close();
    
#ifdef _WIN32
    // On Windows, wait for user input in debug builds
    #ifdef _DEBUG
    std::cout << "\nPress any key to exit..." << std::endl;
    _getch();
    #endif
#endif
    
    return exitCode;
}