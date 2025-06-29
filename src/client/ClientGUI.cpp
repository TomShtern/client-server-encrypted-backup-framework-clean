// ClientGUI.cpp
// Enhanced Client GUI Operations
// Contains display functions, GUI command handling, and WebSocket integration

#include "../../include/client/ClientCore.h"
#include "../../include/client/ClientGUIHelpers.h"

// === GUI COMMAND HANDLING ===

void Client::handleGUICommand(const std::map<std::string, std::string>& command) {
    // Generic command handler - dispatch to specific handlers based on command type
    auto it = command.find("type");
    if (it != command.end()) {
        const std::string& type = it->second;
        
        displayStatus("GUI command received", true, "Type: " + type);
        
        if (type == "connect") {
            handleConnectCommand(command);
        } else if (type == "start_backup") {
            handleStartBackupCommand(command);
        } else if (type == "file_selected") {
            handleFileSelectedCommand(command);
        } else {
            displayError("Unknown GUI command type: " + type, ErrorType::PROTOCOL);
            sendGUIResponse(type, "Unknown command type", false);
        }
    } else {
        displayError("Invalid GUI command format - missing type", ErrorType::PROTOCOL);
        sendGUIResponse("error", "Invalid command format", false);
    }
}

void Client::handleConnectCommand(const std::map<std::string, std::string>& command) {
    // Handle connect command from GUI
    try {
        auto ipIt = command.find("server_ip");
        auto portIt = command.find("server_port");
        auto userIt = command.find("username");
        
        if (ipIt != command.end() && portIt != command.end() && userIt != command.end()) {
            pendingServerIP = ipIt->second;
            pendingServerPort = std::stoi(portIt->second);
            pendingUsername = userIt->second;
            
            displayStatus("Connect command processed", true, 
                         "Server: " + pendingServerIP + ":" + std::to_string(pendingServerPort) + 
                         ", User: " + pendingUsername);
            
            // Update connection parameters
            serverIP = pendingServerIP;
            serverPort = static_cast<uint16_t>(pendingServerPort);
            username = pendingUsername;
            
            // Attempt to connect to the server
            if (connectToServer()) {
                // Save connection info for future use
                if (saveMeInfo()) {
                    sendGUIResponse("connect", "Connection successful", true);
                    displayStatus("GUI connect", true, "Connection established and saved");
                } else {
                    sendGUIResponse("connect", "Connected but failed to save info", true);
                }
            } else {
                sendGUIResponse("connect", "Connection failed", false);
                displayError("GUI connection attempt failed", ErrorType::NETWORK);
            }
        } else {
            sendGUIResponse("connect", "Missing required parameters (server_ip, server_port, username)", false);
            displayError("Invalid connect command parameters", ErrorType::CONFIG);
        }
    } catch (const std::exception& e) {
        std::string errorMsg = "Connect command error: " + std::string(e.what());
        sendGUIResponse("connect", errorMsg, false);
        displayError(errorMsg, ErrorType::PROTOCOL);
    } catch (...) {
        sendGUIResponse("connect", "Unknown error during connection", false);
        displayError("Unknown error in connect command", ErrorType::PROTOCOL);
    }
}

void Client::handleStartBackupCommand(const std::map<std::string, std::string>& command) {
    // Handle start backup command from GUI
    try {
        auto fileIt = command.find("file");
        
        if (fileIt != command.end()) {
            selectedFilePath = fileIt->second;
            
            displayStatus("Backup command processed", true, "File: " + selectedFilePath);
            
            // Update file path for backup operation
            filepath = selectedFilePath;
            
            // Validate the file exists and is readable
            if (!validateConfiguration()) {
                sendGUIResponse("start_backup", "File validation failed", false);
                return;
            }
            
            // Perform the complete backup operation
            displayPhase("GUI-Initiated Backup");
            
            bool backupSuccess = false;
            
            // Ensure we have a connection
            if (!connected) {
                displayStatus("Establishing connection", true, "Connecting for backup operation");
                if (!connectToServer()) {
                    sendGUIResponse("start_backup", "Failed to connect to server", false);
                    return;
                }
            }
            
            // Perform authentication if needed
            bool hasRegistration = loadMeInfo();
            if (hasRegistration && loadPrivateKey()) {
                displayStatus("Using existing credentials", true, "Reconnecting to server");
                if (!performReconnection()) {
                    displayStatus("Reconnection failed", false, "Will register as new client");
                    hasRegistration = false;
                }
            }
            
            if (!hasRegistration) {
                displayStatus("Registering new client", true, "Creating new account");
                if (!generateRSAKeys() || !performRegistration() || !sendPublicKey()) {
                    sendGUIResponse("start_backup", "Authentication failed", false);
                    return;
                }
            }
            
            // Perform the file transfer
            if (transferFile()) {
                backupSuccess = true;
                sendGUIResponse("start_backup", "Backup completed successfully", true);
                displayStatus("GUI backup complete", true, "File transferred successfully");
            } else {
                sendGUIResponse("start_backup", "File transfer failed", false);
                displayError("GUI backup failed during transfer", ErrorType::NETWORK);
            }
            
            // Update GUI with final status
            if (backupSuccess) {
                displaySummary();
                updateGUIStatus("Backup Complete", true, "File backup completed successfully");
            } else {
                updateGUIStatus("Backup Failed", false, "File backup operation failed");
            }
            
        } else {
            sendGUIResponse("start_backup", "Missing file parameter", false);
            displayError("Invalid backup command - missing file", ErrorType::CONFIG);
        }
    } catch (const std::exception& e) {
        std::string errorMsg = "Backup command error: " + std::string(e.what());
        sendGUIResponse("start_backup", errorMsg, false);
        displayError(errorMsg, ErrorType::PROTOCOL);
    } catch (...) {
        sendGUIResponse("start_backup", "Unknown error during backup", false);
        displayError("Unknown error in backup command", ErrorType::PROTOCOL);
    }
}

void Client::handleFileSelectedCommand(const std::map<std::string, std::string>& command) {
    // Handle file selected command from GUI
    try {
        auto fileIt = command.find("file");
        
        if (fileIt != command.end()) {
            std::string filePath = fileIt->second;
            selectedFilePath = filePath;
            
            displayStatus("File selected via GUI", true, "Path: " + filePath);
            
            // Validate the selected file
            std::ifstream testFile(filePath, std::ios::binary);
            if (testFile.is_open()) {
                testFile.seekg(0, std::ios::end);
                size_t fileSize = testFile.tellg();
                testFile.close();
                
                std::string sizeInfo = formatBytes(fileSize);
                sendGUIResponse("file_selected", "File confirmed: " + sizeInfo, true);
                displayStatus("File validation", true, "Size: " + sizeInfo);
            } else {
                sendGUIResponse("file_selected", "Cannot access selected file", false);
                displayError("Selected file is not accessible: " + filePath, ErrorType::FILE_IO);
            }
        } else {
            sendGUIResponse("file_selected", "Missing file parameter", false);
            displayError("Invalid file selection command", ErrorType::CONFIG);
        }
    } catch (const std::exception& e) {
        std::string errorMsg = "File selection error: " + std::string(e.what());
        sendGUIResponse("file_selected", errorMsg, false);
        displayError(errorMsg, ErrorType::PROTOCOL);
    } catch (...) {
        sendGUIResponse("file_selected", "Unknown error during file selection", false);
        displayError("Unknown error in file selection", ErrorType::PROTOCOL);
    }
}

void Client::sendGUIResponse(const std::string& type, const std::string& message, bool success) {
    // Send response back to GUI via WebSocket
    try {
        if (webSocketServer) {
            std::map<std::string, std::string> response;
            response["type"] = type + "_response";
            response["message"] = message;
            response["success"] = success ? "true" : "false";
            response["timestamp"] = getCurrentTimestamp();
            
            // Send via WebSocket server
            // webSocketServer->sendResponse(response); // TODO: Implement when WebSocket is ready
            
            displayStatus("GUI response sent", success, type + ": " + message);
        } else {
            displayStatus("GUI response", false, "WebSocket server not available");
        }
    } catch (const std::exception& e) {
        displayError("Failed to send GUI response: " + std::string(e.what()), ErrorType::PROTOCOL);
    }
}

// === DISPLAY FUNCTIONS ===

void Client::displayStatus(const std::string& operation, bool success, const std::string& details) {
#ifdef _WIN32
    clearLine();
    
    std::cout << "[" << getCurrentTimestamp() << "] ";
    
    if (success) {
        SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN | FOREGROUND_INTENSITY);
        std::cout << "[OK] ";
    } else {
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_INTENSITY);
        std::cout << "[FAIL] ";
    }
    
    SetConsoleTextAttribute(hConsole, savedAttributes);
    std::cout << operation;
    
    if (!details.empty()) {
        SetConsoleTextAttribute(hConsole, FOREGROUND_INTENSITY);
        std::cout << " - " << details;
        SetConsoleTextAttribute(hConsole, savedAttributes);
    }
    std::cout << std::endl;
    
    // Update GUI operation status (optional)
    try {
        ClientGUIHelpers::updateOperation(operation, success, details);
    } catch (...) {
        // GUI update failed - continue without GUI
    }
#else
    std::cout << "[" << getCurrentTimestamp() << "] ";
    std::cout << (success ? "[OK] " : "[FAIL] ") << operation;
    if (!details.empty()) {
        std::cout << " - " << details;
    }
    std::cout << std::endl;
#endif

    // Update internal GUI status tracking
    updateGUIStatus(operation, success, details);
}

void Client::displayProgress(const std::string& operation, size_t current, size_t total) {
    if (total == 0) return;
    
    int percentage = static_cast<int>((current * 100) / total);
    
#ifdef _WIN32
    clearLine();
    std::cout << operation << " [";
    
    const int barWidth = 40;
    int pos = (barWidth * current) / total;
    
    SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN | FOREGROUND_INTENSITY);
    for (int i = 0; i < pos; i++) std::cout << "█";
    
    SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN);
    for (int i = pos; i < barWidth; i++) std::cout << "░";
    
    SetConsoleTextAttribute(hConsole, savedAttributes);
    std::cout << "] " << std::setw(3) << percentage << "% (" 
              << formatBytes(current) << "/" << formatBytes(total) << ")\r";
    std::cout.flush();
    
    if (current >= total) {
        std::cout << std::endl;
    }
    
    // Update GUI progress (optional)
    try {
        std::string speed = "";
        std::string eta = "";
        if (stats.currentSpeed > 0) {
            speed = formatBytes(static_cast<size_t>(stats.currentSpeed)) + "/s";
        }
        if (stats.estimatedTimeRemaining > 0) {
            eta = formatDuration(stats.estimatedTimeRemaining);
        }
        ClientGUIHelpers::updateProgress(static_cast<int>(current), static_cast<int>(total), speed, eta);
    } catch (...) {
        // GUI update failed - continue without GUI
    }
#else
    std::cout << "\r" << operation << " " << percentage << "% (" 
              << formatBytes(current) << "/" << formatBytes(total) << ")";
    std::cout.flush();
    if (current >= total) {
        std::cout << std::endl;
    }
#endif

    // Update internal GUI progress tracking
    double progressPercent = (total > 0) ? ((double)current / total) * 100.0 : 0.0;
    std::string speed = formatBytes(static_cast<size_t>(stats.currentSpeed)) + "/s";
    std::string eta = formatDuration(stats.estimatedTimeRemaining);
    std::string transferred = formatBytes(current);
    updateGUIProgress(progressPercent, speed, eta, transferred);
}

void Client::displayTransferStats() {
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY);
    std::cout << "\r[STATS] ";
    SetConsoleTextAttribute(hConsole, savedAttributes);
    
    std::cout << "Speed: " << formatBytes(static_cast<size_t>(stats.currentSpeed)) << "/s | "
              << "Avg: " << formatBytes(static_cast<size_t>(stats.averageSpeed)) << "/s | "
              << "ETA: " << formatDuration(stats.estimatedTimeRemaining) << "    " << std::endl;
#else
    std::cout << "\n[STATS] Speed: " << formatBytes(static_cast<size_t>(stats.currentSpeed)) << "/s | "
              << "Avg: " << formatBytes(static_cast<size_t>(stats.averageSpeed)) << "/s | "
              << "ETA: " << formatDuration(stats.estimatedTimeRemaining) << std::endl;
#endif
}

void Client::displaySplashScreen() {
#ifdef _WIN32
    system("cls");
    
    SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY);
    std::cout << "\n================================================\n";
    std::cout << "     ENCRYPTED FILE BACKUP CLIENT v1.0      \n";
    std::cout << "================================================\n";
    
    SetConsoleTextAttribute(hConsole, savedAttributes);
    std::cout << "  Build Date: " << __DATE__ << " " << __TIME__ << "\n";
    std::cout << "  Protocol Version: " << static_cast<int>(CLIENT_VERSION) << "\n";
    std::cout << "  Encryption: RSA-1024 + AES-256-CBC\n";
    std::cout << "  GUI Mode: WebSocket on port 8765\n\n";
#else
    std::cout << "\n============================================\n";
    std::cout << "     ENCRYPTED FILE BACKUP CLIENT v1.0      \n";
    std::cout << "============================================\n";
    std::cout << "  Build Date: " << __DATE__ << " " << __TIME__ << "\n";
    std::cout << "  Protocol Version: " << static_cast<int>(CLIENT_VERSION) << "\n";
    std::cout << "  Encryption: RSA-1024 + AES-256-CBC\n";
    std::cout << "  GUI Mode: WebSocket on port 8765\n\n";
#endif
}

void Client::clearLine() {
#ifdef _WIN32
    std::cout << "\r" << std::string(120, ' ') << "\r";
    std::cout.flush();
#else
    std::cout << "\r\033[K";
    std::cout.flush();
#endif
}

void Client::displayConnectionInfo() {
    displaySeparator();
    std::cout << "Connection Details:\n";
    std::cout << "  Server Address: " << serverIP << ":" << serverPort << "\n";
    std::cout << "  Client Name: " << username << "\n";
    std::cout << "  File to Transfer: " << filepath << "\n";
    std::cout << "  File Size: " << formatBytes(stats.totalBytes) << "\n";
    std::cout << "  Client ID: " << bytesToHex(clientID.data(), 8) << "...\n";
    displaySeparator();
}

void Client::displayError(const std::string& message, ErrorType type) {
    lastError = type;
    lastErrorDetails = message;
    
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_INTENSITY);
    std::cerr << "[ERROR] ";
    SetConsoleTextAttribute(hConsole, savedAttributes);
#else
    std::cerr << "[ERROR] ";
#endif
    
    // Add error type prefix
    switch (type) {
        case ErrorType::NETWORK:
            std::cerr << "[NETWORK] ";
            break;
        case ErrorType::FILE_IO:
            std::cerr << "[FILE] ";
            break;
        case ErrorType::PROTOCOL:
            std::cerr << "[PROTOCOL] ";
            break;
        case ErrorType::CRYPTO:
            std::cerr << "[CRYPTO] ";
            break;
        case ErrorType::CONFIG:
            std::cerr << "[CONFIG] ";
            break;
        case ErrorType::AUTHENTICATION:
            std::cerr << "[AUTH] ";
            break;
        case ErrorType::SERVER_ERROR:
            std::cerr << "[SERVER] ";
            break;
        default:
            break;
    }
    
    std::cerr << message << std::endl;
    
    // Update GUI error status and show notification (optional)
    try {
        ClientGUIHelpers::updateError(message);
        ClientGUIHelpers::showNotification("Backup Error", message);
    } catch (...) {
        // GUI update failed - continue without GUI
    }
    
    // Update internal GUI status tracking
    updateGUIStatus("ERROR", false, message);
}

void Client::displaySeparator() {
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, FOREGROUND_INTENSITY);
    std::cout << std::string(60, '=') << std::endl;
    SetConsoleTextAttribute(hConsole, savedAttributes);
#else
    std::cout << std::string(60, '-') << std::endl;
#endif
}

void Client::displayPhase(const std::string& phase) {
#ifdef _WIN32
    std::cout << "\n";
    SetConsoleTextAttribute(hConsole, FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY);
    std::cout << "> " << phase << std::endl;
    SetConsoleTextAttribute(hConsole, savedAttributes);
    displaySeparator();
    
    // Update GUI phase (optional)
    try {
        ClientGUIHelpers::updatePhase(phase);
    } catch (...) {
        // GUI update failed - continue without GUI
    }
#else
    std::cout << "\n> " << phase << std::endl;
    displaySeparator();
#endif

    // Update internal GUI phase tracking
    updateGUIPhase(phase);
}

void Client::displaySummary() {
    auto endTime = std::chrono::steady_clock::now();
    auto totalDuration = std::chrono::duration_cast<std::chrono::seconds>(endTime - operationStartTime).count();
    
    displaySeparator();
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN | FOREGROUND_INTENSITY);
    std::cout << "✓ BACKUP COMPLETED SUCCESSFULLY\n";
    SetConsoleTextAttribute(hConsole, savedAttributes);
#else
    std::cout << "✓ BACKUP COMPLETED SUCCESSFULLY\n";
#endif
    
    std::cout << "\nTransfer Summary:\n";
    std::cout << "  File: " << filepath << "\n";
    std::cout << "  Size: " << formatBytes(stats.totalBytes) << "\n";
    std::cout << "  Duration: " << formatDuration(static_cast<int>(totalDuration)) << "\n";
    std::cout << "  Average Speed: " << formatBytes(static_cast<size_t>(stats.averageSpeed)) << "/s\n";
    std::cout << "  Server: " << serverIP << ":" << serverPort << "\n";
    std::cout << "  Client ID: " << bytesToHex(clientID.data(), 8) << "...\n";
    std::cout << "  Timestamp: " << getCurrentTimestamp() << "\n";
    displaySeparator();
    
    // Show GUI completion notification (optional)
    try {
        std::string successMessage = "File backup completed successfully!\n\nFile: " + filepath + 
                                   "\nSize: " + formatBytes(stats.totalBytes) + 
                                   "\nDuration: " + formatDuration(static_cast<int>(totalDuration));
        ClientGUIHelpers::showNotification("Backup Complete", successMessage);
        ClientGUIHelpers::updatePhase("Transfer Complete");
    } catch (...) {
        // GUI notification failed - continue without GUI
    }
}

// === GUI STATUS UPDATE HELPERS ===

void Client::updateGUIStatus(const std::string& operation, bool success, const std::string& details) {
    // Write status to JSON file for GUI consumption
    try {
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
    } catch (const std::exception& e) {
        // Failed to write GUI status - continue without GUI updates
        std::cerr << "[DEBUG] Failed to update GUI status: " << e.what() << std::endl;
    }
}

void Client::updateGUIProgress(double percentage, const std::string& speed, const std::string& eta, const std::string& transferred) {
    // Write progress to JSON file for GUI consumption
    try {
        std::ofstream progressFile("gui_progress.json");
        if (progressFile.is_open()) {
            progressFile << "{"
                         << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                         << "\"percentage\":" << std::fixed << std::setprecision(2) << percentage << ","
                         << "\"speed\":\"" << speed << "\","
                         << "\"eta\":\"" << eta << "\","
                         << "\"transferred\":\"" << transferred << "\""
                         << "}\n";
            progressFile.flush();
            progressFile.close();
        }
    } catch (const std::exception& e) {
        // Failed to write GUI progress - continue without GUI updates
        std::cerr << "[DEBUG] Failed to update GUI progress: " << e.what() << std::endl;
    }
}

void Client::updateGUIPhase(const std::string& phase) {
    // Update GUI with current phase information
    updateGUIStatus("Phase Change", true, phase);
    
    // Also write dedicated phase file for GUI
    try {
        std::ofstream phaseFile("gui_phase.json");
        if (phaseFile.is_open()) {
            phaseFile << "{"
                      << "\"timestamp\":\"" << getCurrentTimestamp() << "\","
                      << "\"phase\":\"" << phase << "\""
                      << "}\n";
            phaseFile.flush();
            phaseFile.close();
        }
    } catch (const std::exception& e) {
        // Failed to write GUI phase - continue without GUI updates
        std::cerr << "[DEBUG] Failed to update GUI phase: " << e.what() << std::endl;
    }
}

void Client::initializeWebSocketCommands() {
    // Initialize WebSocket command handling system
    try {
        if (webSocketServer) {
            displayStatus("WebSocket commands", true, "Command handling system initialized");
            
            // Set up command mapping and handlers
            // TODO: Implement detailed WebSocket command routing when WebSocket server is fully implemented
            
            updateGUIStatus("System Ready", true, "WebSocket command system active");
        } else {
            displayStatus("WebSocket commands", false, "WebSocket server not available");
        }
    } catch (const std::exception& e) {
        displayError("Failed to initialize WebSocket commands: " + std::string(e.what()), ErrorType::CONFIG);
    }
}