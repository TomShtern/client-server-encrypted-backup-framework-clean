#pragma once

#include <string>

// Stub implementation for ClientGUIHelpers to maintain compatibility
// The actual GUI is now the HTML-based NewGUIforClient.html
namespace ClientGUIHelpers {
    // Stub functions - no-op implementations since we use HTML GUI
    bool initializeGUI();
    void shutdownGUI();
    void updatePhase(const std::string& phase);
    void updateOperation(const std::string& operation, bool success = true, const std::string& details = "");
    void updateProgress(int current, int total, const std::string& speed = "", const std::string& eta = "");
    void updateConnectionStatus(bool connected);
    void updateError(const std::string& message);
    void showNotification(const std::string& title, const std::string& message);
}
