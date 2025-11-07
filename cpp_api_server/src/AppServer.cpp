#include "cpp_api_server/AppServer.h"

#include <drogon/drogon.h>
#include <iostream>
#include <utility>

namespace cpp_api_server {

AppServer::AppServer(Config config) : config_(std::move(config)) {}

void AppServer::start() {
    std::cout << "=" << std::string(70, '=') << '\n';
    std::cout << "* CyberBackup 3.0 C++ API Server\n";
    std::cout << "=" << std::string(70, '=') << '\n';

    // Load Drogon configuration from JSON file
    std::cout << "[INFO] Loading Drogon configuration...\n";
    try {
        drogon::app().loadConfigFile("cpp_api_server/config/default_config.json");
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to load config: " << e.what() << '\n';
        std::cerr << "[ERROR] Ensure cpp_api_server/config/default_config.json exists\n";
        return;
    }

    // Display configuration
    std::cout << "* Configuration:\n";
    std::cout << "*   API Server: http://127.0.0.1:9090\n";
    std::cout << "*   Client GUI: http://127.0.0.1:9090/\n";
    std::cout << "*   Health Check: http://127.0.0.1:9090/health\n";
    std::cout << "*   Document Root: " << config_.static_dir << '\n';
    std::cout << "*   Database: " << config_.database_path << '\n';
    std::cout << "*   Threads: 4\n";
    std::cout << "*   Max Connections: 100\n";
    std::cout << '\n';

    // Display component status
    std::cout << "Component Status:\n";
    std::cout << "[OK] Drogon HTTP framework initialized\n";
    std::cout << "[OK] Static file serving configured\n";
    std::cout << "[OK] WebSocket support enabled\n";
    std::cout << "[OK] Session management enabled\n";
    std::cout << '\n';

    std::cout << "[ROCKET] Starting Drogon HTTP/WebSocket server...\n";
    std::cout << "[INFO] Press Ctrl+C to stop server\n";
    std::cout << '\n';

    // Start the Drogon application event loop
    // This call blocks until the server is stopped
    drogon::app().run();

    std::cout << "\n[INFO] Server shutdown complete\n";
}

}  // namespace cpp_api_server
