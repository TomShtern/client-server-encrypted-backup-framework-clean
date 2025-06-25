#include "../../include/client/ClientGUI.h"
#include <iostream>

// Stub implementations for ClientGUIHelpers
// The actual GUI is now the HTML-based NewGUIforClient.html served by the web server
namespace ClientGUIHelpers {
    bool initializeGUI() {
        std::cout << "[GUI] HTML GUI will be served via web interface\n";
        return true;
    }
    
    void shutdownGUI() {
        std::cout << "[GUI] GUI shutdown\n";
    }
    
    void updatePhase(const std::string& phase) {
        std::cout << "[GUI] Phase: " << phase << "\n";
    }
    
    void updateOperation(const std::string& operation, bool success, const std::string& details) {
        std::cout << "[GUI] Operation: " << operation << " [" << (success ? "SUCCESS" : "FAILED") << "] " << details << "\n";
    }
    
    void updateProgress(int current, int total, const std::string& speed, const std::string& eta) {
        double percentage = total > 0 ? (static_cast<double>(current) / total) * 100.0 : 0.0;
        std::cout << "[GUI] Progress: " << percentage << "% (" << current << "/" << total << ") " << speed << " ETA: " << eta << "\n";
    }
    
    void updateConnectionStatus(bool connected) {
        std::cout << "[GUI] Connection: " << (connected ? "CONNECTED" : "DISCONNECTED") << "\n";
    }
    
    void updateError(const std::string& message) {
        std::cout << "[GUI] ERROR: " << message << "\n";
    }
    
    void showNotification(const std::string& title, const std::string& message) {
        std::cout << "[GUI] NOTIFICATION: " << title << " - " << message << "\n";
    }
}
