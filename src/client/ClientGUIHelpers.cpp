#include "../../include/client/ClientGUI.h"
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <chrono>

#ifdef _WIN32
#include <windows.h>
#endif

// ClientGUIHelpers - Bridge functions for HTML-based GUI integration
// Implements JSON file communication pattern for real-time GUI updates
namespace ClientGUIHelpers {
    
    // Helper function to get current timestamp in ISO format
    std::string getCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;
        
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        ss << '.' << std::setfill('0') << std::setw(3) << ms.count();
        return ss.str();
    }
    
    bool initializeGUI() {
        try {
            // Initialize GUI status files
            std::ofstream statusFile("gui_status.json");
            if (statusFile.is_open()) {
                statusFile << "{"
                           << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                           << "\"operation\":\"System Initialization\","
                           << "\"success\":true,"
                           << "\"details\":\"GUI system ready - HTML interface available\""
                           << "}\n";
                statusFile.flush();
                statusFile.close();
            }
            
            // Initialize phase tracking
            std::ofstream phaseFile("gui_phase.json");
            if (phaseFile.is_open()) {
                phaseFile << "{"
                          << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                          << "\"phase\":\"Initialization\""
                          << "}\n";
                phaseFile.flush();
                phaseFile.close();
            }
            
            // Initialize progress tracking
            std::ofstream progressFile("gui_progress.json");
            if (progressFile.is_open()) {
                progressFile << "{"
                             << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                             << "\"percentage\":0.0,"
                             << "\"speed\":\"\","
                             << "\"eta\":\"\","
                             << "\"transferred\":\"\""
                             << "}\n";
                progressFile.flush();
                progressFile.close();
            }
            
            std::cout << "[GUI] GUI system initialized - HTML interface ready on WebSocket port 8765\n";
            return true;
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Failed to initialize GUI system: " << e.what() << std::endl;
            return false;
        }
    }
    
    void shutdownGUI() {
        try {
            // Write shutdown status
            std::ofstream statusFile("gui_status.json");
            if (statusFile.is_open()) {
                statusFile << "{"
                           << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                           << "\"operation\":\"System Shutdown\","
                           << "\"success\":true,"
                           << "\"details\":\"GUI system shutting down\""
                           << "}\n";
                statusFile.flush();
                statusFile.close();
            }
            
            std::cout << "[GUI] GUI system shutdown complete\n";
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Error during shutdown: " << e.what() << std::endl;
        }
    }
    
    void updatePhase(const std::string& phase) {
        try {
            // Write phase update to JSON file for GUI consumption
            std::ofstream phaseFile("gui_phase.json");
            if (phaseFile.is_open()) {
                phaseFile << "{"
                          << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                          << "\"phase\":\"" << phase << "\""
                          << "}\n";
                phaseFile.flush();
                phaseFile.close();
            }
            
            // Also update general status
            updateOperation("Phase Change", true, phase);
            
            std::cout << "[GUI] Phase: " << phase << "\n";
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Failed to update phase: " << e.what() << std::endl;
        }
    }
    
    void updateOperation(const std::string& operation, bool success, const std::string& details) {
        try {
            // Write operation status to JSON file for GUI consumption
            std::ofstream statusFile("gui_status.json");
            if (statusFile.is_open()) {
                statusFile << "{"
                           << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                           << "\"operation\":\"" << operation << "\","
                           << "\"success\":" << (success ? "true" : "false") << ","
                           << "\"details\":\"" << details << "\""
                           << "}\n";
                statusFile.flush();
                statusFile.close();
            }
            
            std::cout << "[GUI] Operation: " << operation << " [" << (success ? "SUCCESS" : "FAILED") << "] " << details << "\n";
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Failed to update operation: " << e.what() << std::endl;
        }
    }
    
    void updateProgress(int current, int total, const std::string& speed, const std::string& eta) {
        try {
            double percentage = total > 0 ? (static_cast<double>(current) / total) * 100.0 : 0.0;
            std::string transferred = std::to_string(current);
            
            // Write progress to JSON file for GUI consumption
            std::ofstream progressFile("gui_progress.json");
            if (progressFile.is_open()) {
                progressFile << "{"
                             << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                             << "\"percentage\":" << std::fixed << std::setprecision(2) << percentage << ","
                             << "\"speed\":\"" << speed << "\","
                             << "\"eta\":\"" << eta << "\","
                             << "\"transferred\":\"" << transferred << "\","
                             << "\"current\":" << current << ","
                             << "\"total\":" << total
                             << "}\n";
                progressFile.flush();
                progressFile.close();
            }
            
            std::cout << "[GUI] Progress: " << std::fixed << std::setprecision(1) << percentage << "% (" << current << "/" << total << ") " << speed << " ETA: " << eta << "\n";
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Failed to update progress: " << e.what() << std::endl;
        }
    }
    
    void updateConnectionStatus(bool connected) {
        try {
            // Write connection status
            updateOperation("Connection Status", connected, connected ? "Connected to server" : "Disconnected from server");
            
            std::cout << "[GUI] Connection: " << (connected ? "CONNECTED" : "DISCONNECTED") << "\n";
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Failed to update connection status: " << e.what() << std::endl;
        }
    }
    
    void updateError(const std::string& message) {
        try {
            // Write error status
            updateOperation("Error", false, message);
            
            std::cout << "[GUI] ERROR: " << message << "\n";
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Failed to update error: " << e.what() << std::endl;
        }
    }
    
    void showNotification(const std::string& title, const std::string& message) {
        try {
            // Write notification to status file with special notification format
            std::ofstream statusFile("gui_status.json");
            if (statusFile.is_open()) {
                statusFile << "{"
                           << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                           << "\"operation\":\"Notification\","
                           << "\"success\":true,"
                           << "\"details\":\"" << title << ": " << message << "\","
                           << "\"title\":\"" << title << "\","
                           << "\"message\":\"" << message << "\","
                           << "\"type\":\"notification\""
                           << "}\n";
                statusFile.flush();
                statusFile.close();
            }
            
#ifdef _WIN32
            // On Windows, also show a system notification if possible
            try {
                std::string command = "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('" + message + "', '" + title + "', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)\"";
                // Note: This would show a blocking dialog, so we just log it for now
            } catch (...) {
                // Ignore errors in system notification
            }
#endif
            
            std::cout << "[GUI] NOTIFICATION: " << title << " - " << message << "\n";
        } catch (const std::exception& e) {
            std::cerr << "[GUI] Failed to show notification: " << e.what() << std::endl;
        }
    }
}
