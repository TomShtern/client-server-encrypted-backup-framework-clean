// Client.cpp
// Encrypted File Backup System - Enhanced Client Implementation
// Fully compliant with project specifications

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>
#include <array>
#include <cstring>
#include <algorithm>
#include <chrono>
#include <thread>
//#include <filesystem>
#ifdef _WIN32
#include <direct.h>
#include <sys/stat.h>
#endif
#include <boost/asio.hpp>
#include <boost/system/error_code.hpp>
#include <boost/bind/bind.hpp>
#include "../../include/client/ClientWebSocketServer.h"
#include "../../include/client/ClientGUI.h"

// For file operations instead of C++17 filesystem
#include <atomic>
#include <ctime>

// Boost.Asio for cross-platform networking
#ifdef _WIN32
#include <shellapi.h>
#endif


// Windows console control
#ifdef _WIN32
#include <windows.h>
#include <io.h>
#include <fcntl.h>
#endif

// Required wrapper includes (provided by project)
#include "../../include/client/cksum.h"
#include "../../include/wrappers/AESWrapper.h"
#include "../../include/wrappers/Base64Wrapper.h"
#include "../../include/wrappers/RSAWrapper.h"

// Global batch mode flag
extern bool g_batchMode;

// Optional GUI support - already included in ClientWebSocketServer.h
// #ifdef _WIN32
// #include "../../include/client/ClientGUI.h"
// #endif

// Protocol constants
constexpr uint8_t CLIENT_VERSION = 3;
constexpr uint8_t SERVER_VERSION = 3;

// Request codes - MUST match server constants exactly
constexpr uint16_t REQ_REGISTER = 1025;
constexpr uint16_t REQ_SEND_PUBLIC_KEY = 1026;
constexpr uint16_t REQ_RECONNECT = 1027;
constexpr uint16_t REQ_SEND_FILE = 1028;
constexpr uint16_t REQ_CRC_OK = 1029;
constexpr uint16_t REQ_CRC_INVALID_RETRY = 1030;  // Fixed: matches server REQ_CRC_INVALID_RETRY
constexpr uint16_t REQ_CRC_FAILED_ABORT = 1031;   // Fixed: matches server REQ_CRC_FAILED_ABORT

// Response codes - MUST match server constants exactly
constexpr uint16_t RESP_REG_OK = 1600;              // Fixed: matches server RESP_REG_OK
constexpr uint16_t RESP_REG_FAIL = 1601;            // Fixed: matches server RESP_REG_FAIL
constexpr uint16_t RESP_PUBKEY_AES_SENT = 1602;
constexpr uint16_t RESP_FILE_CRC = 1603;            // Fixed: matches server RESP_FILE_CRC
constexpr uint16_t RESP_ACK = 1604;
constexpr uint16_t RESP_RECONNECT_AES_SENT = 1605;
constexpr uint16_t RESP_RECONNECT_FAIL = 1606;
constexpr uint16_t RESP_GENERIC_SERVER_ERROR = 1607; // Fixed: matches server RESP_GENERIC_SERVER_ERROR

// Size constants
constexpr size_t CLIENT_ID_SIZE = 16;
constexpr size_t MAX_NAME_SIZE = 255;
constexpr size_t RSA_KEY_SIZE = 160; // Spec-compliant: 160 bytes for RSA public key in DER format
constexpr size_t AES_KEY_SIZE = 32;
constexpr size_t MAX_PACKET_SIZE = 1024 * 1024;  // 1MB per packet
constexpr size_t OPTIMAL_BUFFER_SIZE = 64 * 1024; // 64KB for file reading

// Other constants
constexpr int MAX_RETRIES = 3;
constexpr int SOCKET_TIMEOUT_MS = 30000; // 30 seconds
constexpr int RECONNECT_DELAY_MS = 5000; // 5 seconds between reconnect attempts
constexpr int KEEPALIVE_INTERVAL = 60;   // 60 seconds

// Protocol structures
#pragma pack(push, 1)
struct RequestHeader {
    uint8_t client_id[16];
    uint8_t version;
    uint16_t code;
    uint32_t payload_size;
};

struct ResponseHeader {
    uint8_t version;
    uint16_t code;
    uint32_t payload_size;
};
#pragma pack(pop)

// Transfer statistics structure
struct TransferStats {
    std::chrono::steady_clock::time_point startTime;
    std::chrono::steady_clock::time_point lastUpdateTime;
    size_t totalBytes;
    size_t transferredBytes;
    size_t lastTransferredBytes;
    double currentSpeed;
    double averageSpeed;
    int estimatedTimeRemaining;
    
    TransferStats() : totalBytes(0), transferredBytes(0), lastTransferredBytes(0),
                      currentSpeed(0.0), averageSpeed(0.0), estimatedTimeRemaining(0) {}
    
    void reset() {
        startTime = std::chrono::steady_clock::now();
        lastUpdateTime = startTime;
        transferredBytes = 0;
        lastTransferredBytes = 0;
        currentSpeed = 0.0;
        averageSpeed = 0.0;
        estimatedTimeRemaining = 0;
    }
    
    void update(size_t newBytes) {
        auto now = std::chrono::steady_clock::now();
        transferredBytes = newBytes;
        
        // Calculate current speed
        auto timeSinceLastUpdate = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastUpdateTime).count();
        if (timeSinceLastUpdate > 0) {
            currentSpeed = ((transferredBytes - lastTransferredBytes) * 1000.0) / timeSinceLastUpdate;
        }
        
        // Calculate average speed
        auto totalTime = std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();
        if (totalTime > 0) {
            averageSpeed = (transferredBytes * 1000.0) / totalTime;
        }
        
        // Calculate estimated time remaining
        if (averageSpeed > 0 && totalBytes > transferredBytes) {
            estimatedTimeRemaining = static_cast<int>((totalBytes - transferredBytes) / averageSpeed);
        }
        
        lastUpdateTime = now;
        lastTransferredBytes = transferredBytes;
    }
};

// Enhanced error codes for better debugging
enum class ErrorType {
    NONE,
    NETWORK,
    FILE_IO,
    PROTOCOL,
    CRYPTO,
    CONFIG,
    AUTHENTICATION,
    SERVER_ERROR
};

class Client {
private:
    // Boost.Asio networking
    boost::asio::io_context ioContext;
    std::unique_ptr<boost::asio::ip::tcp::socket> socket;
    std::string serverIP;
    uint16_t serverPort;
    bool connected;
    std::atomic<bool> keepAliveEnabled;
    
    // Client info
    std::array<uint8_t, CLIENT_ID_SIZE> clientID;
    std::string username;
    std::string filepath;
    
    // Crypto
    RSAPrivateWrapper* rsaPrivate;
    std::string aesKey;
    
    // Retry counters
    int fileRetries;
    int crcRetries;
    int reconnectAttempts;
    
    // Transfer statistics
    TransferStats stats;
    
    // Console output control
    HANDLE hConsole;
    CONSOLE_SCREEN_BUFFER_INFO consoleInfo;
    WORD savedAttributes;
    
    // Error tracking
    ErrorType lastError;
    std::string lastErrorDetails;
    
    // Performance metrics
    std::chrono::steady_clock::time_point operationStartTime;

    // WebSocket server for GUI communication
    std::unique_ptr<ClientWebSocketServer> webSocketServer;

    // WebSocket command handling for interactive GUI
    void handleGUICommand(const std::map<std::string, std::string>& command);
    void handleConnectCommand(const std::map<std::string, std::string>& command);
    void handleStartBackupCommand(const std::map<std::string, std::string>& command);
    void handleFileSelectedCommand(const std::map<std::string, std::string>& command);
    void sendGUIResponse(const std::string& type, const std::string& message, bool success = true);
    
    // Interactive mode variables
    bool interactiveMode;
    std::string pendingServerIP;
    int pendingServerPort;
    std::string pendingUsername;
    std::string selectedFilePath;

public:
    Client();
    ~Client();
    
    // Main interface
    bool initialize();
    bool run();
    
private:
    // Configuration
    bool readTransferInfo();
    bool validateConfiguration();
    bool loadMeInfo();
    bool saveMeInfo();
    bool loadPrivateKey();
    bool savePrivateKey();
      // Network operations
    bool connectToServer();
    void closeConnection();
    bool sendRequest(uint16_t code, const std::vector<uint8_t>& payload = {});
    bool receiveResponse(ResponseHeader& header, std::vector<uint8_t>& payload);
    bool testConnection();
    void enableKeepAlive();
    
    // Socket management and recovery
    bool validateSocketConnection();
    bool attemptConnectionRecovery();
    
    // Protocol operations
    bool performRegistration();
    bool performReconnection();
    bool sendPublicKey();
    bool transferFile();
    bool sendFilePacket(const std::string& filename, const std::string& encryptedData, 
                       uint32_t originalSize, uint16_t packetNum, uint16_t totalPackets);
    bool verifyCRC(uint32_t serverCRC, const std::vector<uint8_t>& originalData, const std::string& filename);
    
    // Crypto operations
    bool generateRSAKeys();
    bool decryptAESKey(const std::vector<uint8_t>& encryptedKey);
    std::string encryptFile(const std::vector<uint8_t>& data);
    
    // Utility functions
    std::vector<uint8_t> readFile(const std::string& path);
    std::string bytesToHex(const uint8_t* data, size_t size);
    std::vector<uint8_t> hexToBytes(const std::string& hex);
    uint32_t calculateCRC32(const uint8_t* data, size_t size);
    std::string formatBytes(size_t bytes);
    std::string formatDuration(int seconds);
    std::string getCurrentTimestamp();
    
    // Visual feedback
    void displayStatus(const std::string& operation, bool success, const std::string& details = "");
    void displayProgress(const std::string& operation, size_t current, size_t total);
    void displayTransferStats();
    void displaySplashScreen();
    void clearLine();
    void displayConnectionInfo();
    void displayError(const std::string& message, ErrorType type = ErrorType::NONE);
    void displaySeparator();
    void displayPhase(const std::string& phase);
    void displaySummary();
};
 // Constructor
Client::Client() : socket(nullptr), connected(false), rsaPrivate(nullptr), 
                   fileRetries(0), crcRetries(0), reconnectAttempts(0),
                   keepAliveEnabled(false), lastError(ErrorType::NONE) {
    std::fill(clientID.begin(), clientID.end(), 0);

    // Initialize and start WebSocket server for GUI communication
    try {
        webSocketServer = std::make_unique<ClientWebSocketServer>(8765); // Port 8765 for WebSocket
        webSocketServer->setMessageHandler(std::bind(&Client::handleGUICommand, this, std::placeholders::_1));
        webSocketServer->start();
        displayStatus("GUI", true, "WebSocket server started on port 8765");
    } catch (const std::exception& e) {
        displayError("Failed to start WebSocket GUI server: " + std::string(e.what()), ErrorType::CONFIG);
    }

#ifdef _WIN32
    hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
    GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
    savedAttributes = consoleInfo.wAttributes;
#endif
}

// Destructor
Client::~Client() {
    keepAliveEnabled = false;
    closeConnection();
    if (rsaPrivate) {
        delete rsaPrivate;
    }
    if (webSocketServer) {
        webSocketServer->stop();
    }
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, savedAttributes);
#endif
}

// Initialize client
bool Client::initialize() {
    operationStartTime = std::chrono::steady_clock::now();
    displaySplashScreen();
    
    displayPhase("Initialization");
    
    displayStatus("System initialization", true, "Starting client v1.0");
    
    if (!readTransferInfo()) {
        return false;
    }
    
    if (!validateConfiguration()) {
        return false;
    }

    // Pre-generate or load RSA keys during initialization to avoid delays during registration
    displayStatus("Preparing RSA keys", true, "1024-bit key pair for encryption");

    // Try to load existing keys first to avoid regeneration
    if (loadPrivateKey()) {
        displayStatus("RSA keys loaded", true, "Using cached key pair");
    } else {
        displayStatus("Generating RSA keys", true, "Creating new 1024-bit key pair...");
        if (!generateRSAKeys()) {
            return false;
        }
        // Save the generated keys for future use
        savePrivateKey();
    }

    displayStatus("Initialization complete", true, "Ready to connect");
    return true;
}

// Main client run function
bool Client::run() {
    displayPhase("Connection Setup");
    
    displayStatus("Connecting to server", true, serverIP + ":" + std::to_string(serverPort));
    
    // Try to connect with retries
    bool connectedSuccessfully = false;
    for (int attempt = 1; attempt <= 3 && !connectedSuccessfully; attempt++) {
        if (attempt > 1) {
            displayStatus("Connection attempt", true, "Retry " + std::to_string(attempt) + " of 3");
            std::this_thread::sleep_for(std::chrono::milliseconds(RECONNECT_DELAY_MS));
        }
        
        if (connectToServer()) {
            connectedSuccessfully = true;
        }
    }
    
    if (!connectedSuccessfully) {
        displayError("Failed to connect after 3 attempts", ErrorType::NETWORK);
        return false;
    }
      displayConnectionInfo();
    
    // Test connection quality - Skip for now as test request causes server error
    // if (!testConnection()) {
    //     displayStatus("Connection test", false, "Poor connection quality detected");
    // }
    
    // Enable keep-alive for long transfers
    enableKeepAlive();
    
    displayPhase("Authentication");
    
    // Check if we have existing registration
    bool hasRegistration = loadMeInfo();
    
    if (hasRegistration) {
        displayStatus("Client credentials", true, "Found existing registration");
        displayStatus("Attempting reconnection", true, "Client: " + username);
        
        // Load private key
        if (!loadPrivateKey()) {
            displayStatus("Loading private key", false, "Key not found");
            hasRegistration = false;
        } else {
            // Try reconnection
            if (!performReconnection()) {
                displayStatus("Reconnection", false, "Server rejected - will register as new client");
                hasRegistration = false;
            }
        }
    }
    
    if (!hasRegistration) {
        displayStatus("Registering new client", true, username);
        
        if (!performRegistration()) {
            return false;
        }
        
        if (!sendPublicKey()) {
            return false;
        }
    }
    
    displayPhase("File Transfer");
    
    // Transfer the file with retry logic
    bool transferSuccess = false;
    fileRetries = 0;
    
    while (fileRetries < MAX_RETRIES && !transferSuccess) {
        if (fileRetries > 0) {
            displayStatus("File transfer", false, "Retrying (attempt " + 
                         std::to_string(fileRetries + 1) + " of " + std::to_string(MAX_RETRIES) + ")");
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }
        
        if (transferFile()) {
            transferSuccess = true;
        } else {
            fileRetries++;
        }
    }
    
    if (!transferSuccess) {
        displayError("File transfer failed after " + std::to_string(MAX_RETRIES) + " attempts", ErrorType::NETWORK);
        return false;
    }
    
    displayPhase("Transfer Complete");
    displaySummary();
    
    return true;
}

// Read transfer.info configuration
bool Client::readTransferInfo() {
    std::ifstream file("transfer.info");
    if (!file.is_open()) {
        displayError("Cannot open transfer.info", ErrorType::CONFIG);
        return false;
    }
    
    std::string line;
    
    // Line 1: server:port
    if (!std::getline(file, line)) {
        displayError("Invalid transfer.info format - missing server address", ErrorType::CONFIG);
        return false;
    }
    
    size_t colonPos = line.find(':');
    if (colonPos == std::string::npos) {
        displayError("Invalid server address format (expected IP:port)", ErrorType::CONFIG);
        return false;
    }
    
    serverIP = line.substr(0, colonPos);
    try {
        serverPort = static_cast<uint16_t>(std::stoi(line.substr(colonPos + 1)));
    } catch (...) {
        displayError("Invalid port number", ErrorType::CONFIG);
        return false;
    }
    
    // Line 2: username
    if (!std::getline(file, username) || username.empty()) {
        displayError("Invalid username - cannot be empty", ErrorType::CONFIG);
        return false;
    }
    
    if (username.length() > 100) {
        displayError("Username too long (max 100 characters)", ErrorType::CONFIG);
        return false;
    }
    
    // Line 3: filepath
    if (!std::getline(file, filepath) || filepath.empty()) {
        displayError("Invalid file path - cannot be empty", ErrorType::CONFIG);
        return false;
    }
    
    displayStatus("Configuration loaded", true, "transfer.info parsed successfully");
    return true;
}

// Validate configuration
bool Client::validateConfiguration() {
    displayStatus("Validating configuration", true, "Checking parameters");
    
    // Validate server IP (Boost.Asio will handle IP validation during connect)
    if (serverIP.empty()) {
        displayError("Invalid IP address: empty", ErrorType::CONFIG);
        return false;
    }
    
    // Validate port
    if (serverPort == 0 || serverPort > 65535) {
        displayError("Invalid port number: " + std::to_string(serverPort), ErrorType::CONFIG);
        return false;
    }
    
    // Validate file exists and get size
    std::ifstream testFile(filepath, std::ios::binary);
    if (!testFile.is_open()) {
        displayError("File not found: " + filepath, ErrorType::FILE_IO);
        return false;
    }
    
    testFile.seekg(0, std::ios::end);
    stats.totalBytes = testFile.tellg();
    testFile.close();
    
    if (stats.totalBytes == 0) {
        displayError("File is empty: " + filepath, ErrorType::FILE_IO);
        return false;
    }
    
    displayStatus("File validation", true, filepath + " (" + formatBytes(stats.totalBytes) + ")");
    displayStatus("Server validation", true, serverIP + ":" + std::to_string(serverPort));
    displayStatus("Username validation", true, username);
    
    return true;
}

// Load me.info
bool Client::loadMeInfo() {
    std::ifstream file("me.info");
    if (!file.is_open()) {
        return false;
    }
    
    std::string line;
    
    // Line 1: username (stored for reference, but not validated)
    // FIXED: Remove strict username validation that was preventing client ID loading
    if (!std::getline(file, line)) {
        return false;
    }
    // Store the username from me.info (but don't require exact match)
    std::string storedUsername = line;
    
    // Line 2: UUID hex
    if (!std::getline(file, line) || line.length() != 32) {
        return false;
    }
    
    auto bytes = hexToBytes(line);
    if (bytes.size() != CLIENT_ID_SIZE) {
        return false;
    }
    std::copy(bytes.begin(), bytes.end(), clientID.begin());
    
    displayStatus("Client ID loaded", true, "UUID: " + line.substr(0, 8) + "...");
    
    // Line 3: private key base64 (we'll load separately)
    return true;
}

// Save me.info
bool Client::saveMeInfo() {
    std::ofstream file("me.info");
    if (!file.is_open()) {
        displayError("Cannot create me.info", ErrorType::FILE_IO);
        return false;
    }
    
    file << username << "\n";
    std::string hexId = bytesToHex(clientID.data(), CLIENT_ID_SIZE);
    file << hexId << "\n";
    
    if (rsaPrivate) {
        std::string privateKey = rsaPrivate->getPrivateKey();
        std::string encoded = Base64Wrapper::encode(privateKey);
        file << encoded << "\n";
    }
    
    displayStatus("Client info saved", true, "me.info created");
    return true;
}

// Load private key
bool Client::loadPrivateKey() {
    // Try priv.key first
    std::ifstream keyFile("priv.key", std::ios::binary);
    if (keyFile.is_open()) {
        std::string keyData((std::istreambuf_iterator<char>(keyFile)), std::istreambuf_iterator<char>());
        keyFile.close();
        
        try {
            // priv.key contains binary DER data, use the char* constructor
            rsaPrivate = new RSAPrivateWrapper(keyData.c_str(), keyData.length());
            displayStatus("Private key loaded", true, "From priv.key");
            return true;
        } catch (const std::exception& e) {
            displayStatus("Loading private key", false, std::string("Failed to parse priv.key: ") + e.what());
            delete rsaPrivate;
            rsaPrivate = nullptr;
        }
    }
    
    // Try me.info
    std::ifstream infoFile("me.info");
    if (!infoFile.is_open()) {
        return false;
    }
    
    std::string line;
    std::getline(infoFile, line); // skip username
    std::getline(infoFile, line); // skip UUID
    
    if (!std::getline(infoFile, line) || line.empty()) {
        return false;
    }
      try {
        std::string decoded = Base64Wrapper::decode(line);
        rsaPrivate = new RSAPrivateWrapper(decoded);
        
        // Save to priv.key
        std::ofstream privKey("priv.key", std::ios::binary);
        if (privKey.is_open()) {
            privKey.write(decoded.c_str(), decoded.length());
            displayStatus("Private key cached", true, "Saved to priv.key");
        }
        
        return true;
    } catch (...) {
        if (rsaPrivate) {
            delete rsaPrivate;
            rsaPrivate = nullptr;
        }
        return false;
    }
}

// Save private key
bool Client::savePrivateKey() {
    if (!rsaPrivate) return false;
    
    std::string privateKey = rsaPrivate->getPrivateKey();
    std::ofstream file("priv.key", std::ios::binary);
    if (!file.is_open()) {
        displayError("Cannot create priv.key", ErrorType::FILE_IO);
        return false;
    }
    
    file.write(privateKey.c_str(), privateKey.length());
    displayStatus("Private key saved", true, "priv.key created");
    return true;
}

// Connect to server
bool Client::connectToServer() {
    std::cout << "[DEBUG] Attempting to connect to server at " << serverIP << ":" << serverPort << std::endl;
    try {
        socket = std::make_unique<boost::asio::ip::tcp::socket>(ioContext);
        
        boost::asio::ip::tcp::resolver resolver(ioContext);
        boost::asio::ip::tcp::resolver::results_type endpoints = 
            resolver.resolve(serverIP, std::to_string(serverPort));
        
        displayStatus("Connecting", true, "Resolving " + serverIP + ":" + std::to_string(serverPort));
        
        // Connect with proper error handling
        boost::system::error_code connectError;
        boost::asio::connect(*socket, endpoints, connectError);
        
        if (connectError) {
            displayError("Connection failed: " + connectError.message() + 
                        " (Code: " + std::to_string(connectError.value()) + ")", ErrorType::NETWORK);
            return false;
        }

        // Verify the connection is actually established
        if (!socket->is_open()) {
            displayError("Socket failed to open after connect", ErrorType::NETWORK);
            return false;
        }

        // Get the actual connected endpoint for verification
        auto localEndpoint = socket->local_endpoint();
        auto remoteEndpoint = socket->remote_endpoint();

        displayStatus("Connection verified", true,
                     "Local: " + localEndpoint.address().to_string() + ":" + std::to_string(localEndpoint.port()) +
                     " -> Remote: " + remoteEndpoint.address().to_string() + ":" + std::to_string(remoteEndpoint.port()));

        // Set socket options for better protocol handling
        socket->set_option(boost::asio::ip::tcp::no_delay(true)); // Disable Nagle algorithm
        socket->set_option(boost::asio::socket_base::keep_alive(true)); // Enable keep-alive
        
        // Set socket timeouts (platform-specific)
#ifdef _WIN32
        DWORD timeout = SOCKET_TIMEOUT_MS;
        setsockopt(socket->native_handle(), SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof(timeout));
        setsockopt(socket->native_handle(), SOL_SOCKET, SO_SNDTIMEO, (const char*)&timeout, sizeof(timeout));
#endif

        // Small delay to ensure connection is fully established
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        connected = true;
        displayStatus("Connected", true, "TCP connection established and configured");
        
        // Update GUI connection status (optional)
        try {
            ClientGUIHelpers::updateConnectionStatus(true);
        } catch (...) {
            // GUI update failed - continue without GUI
        }
        
        std::cout << "[DEBUG] Connected to server successfully." << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        displayError("Connection failed: " + std::string(e.what()), ErrorType::NETWORK);
        socket.reset();
        connected = false;
        
        // Update GUI connection status (optional)
        try {
            ClientGUIHelpers::updateConnectionStatus(false);
        } catch (...) {
            // GUI update failed - continue without GUI
        }
        
        std::cerr << "[ERROR] Failed to connect to server." << std::endl;
        return false;
    }
}

// Test connection quality
bool Client::testConnection() {
    auto start = std::chrono::steady_clock::now();
    
    // Send a small test request (empty payload)
    if (!sendRequest(0, {})) {
        return false;
    }
    
    auto end = std::chrono::steady_clock::now();
    auto latency = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    displayStatus("Connection test", true, "Latency: " + std::to_string(latency) + "ms");
    return latency < 1000; // Good if under 1 second
}

// Enable keep-alive
void Client::enableKeepAlive() {
    if (socket && socket->is_open()) {
        try {
            socket->set_option(boost::asio::socket_base::keep_alive(true));
            keepAliveEnabled = true;
            displayStatus("Keep-alive", true, "Enabled for stable connection");
        } catch (const std::exception& e) {
            displayStatus("Keep-alive", false, "Could not enable: " + std::string(e.what()));
        }
    }
}

// Close connection
void Client::closeConnection() {
    if (socket && socket->is_open()) {
        try {
            socket->close();
        } catch (const std::exception&) {
            // Ignore errors during close
        }    }
    socket.reset();
    connected = false;
    
    // Update GUI connection status (optional)
    try {
        ClientGUIHelpers::updateConnectionStatus(false);
    } catch (...) {
        // GUI update failed - continue without GUI
    }
}

// Send request to server with robust error handling
bool Client::sendRequest(uint16_t code, const std::vector<uint8_t>& payload) {
    // Basic connection validation
    if (!connected || !socket || !socket->is_open()) {
        displayError("Client not connected to server", ErrorType::NETWORK);
        return false;
    }
    
    try {
        // Construct complete message buffer for atomic transmission
        std::vector<uint8_t> completeMessage;
        completeMessage.reserve(23 + payload.size());
        
        // Manually construct header bytes in little-endian format
        std::vector<uint8_t> headerBytes(23);  // RequestHeader is 23 bytes total

        // Client ID (16 bytes) - copy as-is
        std::copy(clientID.begin(), clientID.end(), headerBytes.begin());

        // Version (1 byte) - byte 16
        headerBytes[16] = CLIENT_VERSION;

        // Code (2 bytes, little-endian) - bytes 17-18
        headerBytes[17] = code & 0xFF;        // Low byte
        headerBytes[18] = (code >> 8) & 0xFF; // High byte

        // Payload size (4 bytes, little-endian) - bytes 19-22
        uint32_t payload_size_val = static_cast<uint32_t>(payload.size());
        headerBytes[19] = payload_size_val & 0xFF;         // Byte 0
        headerBytes[20] = (payload_size_val >> 8) & 0xFF;  // Byte 1
        headerBytes[21] = (payload_size_val >> 16) & 0xFF; // Byte 2
        headerBytes[22] = (payload_size_val >> 24) & 0xFF; // Byte 3
        
        // Combine header and payload into single message buffer
        completeMessage.insert(completeMessage.end(), headerBytes.begin(), headerBytes.end());
        if (!payload.empty()) {
            completeMessage.insert(completeMessage.end(), payload.begin(), payload.end());
        }
        
        // Debug output for critical requests
        if (code == REQ_REGISTER || code == REQ_RECONNECT || code == REQ_SEND_PUBLIC_KEY) {
            displayStatus("Sending request", true,
                         "Code=" + std::to_string(code) +
                         ", PayloadSize=" + std::to_string(payload_size_val) +
                         ", TotalBytes=" + std::to_string(completeMessage.size()));
        }
        
        // ATOMIC TRANSMISSION: Send complete message in one operation
        boost::system::error_code sendError;
        size_t totalBytesSent = boost::asio::write(*socket, boost::asio::buffer(completeMessage), sendError);
        
        // Check for transmission errors
        if (sendError) {
            displayError("Socket write failed: " + sendError.message(), ErrorType::NETWORK);
            connected = false;
            return false;
        }
        
        // Verify complete transmission
        if (totalBytesSent != completeMessage.size()) {
            displayError("Incomplete write: " + std::to_string(totalBytesSent) + 
                        "/" + std::to_string(completeMessage.size()) + " bytes", ErrorType::NETWORK);
            connected = false;
            return false;
        }
        
        // Success confirmation for critical requests
        if (code == REQ_REGISTER || code == REQ_RECONNECT || code == REQ_SEND_PUBLIC_KEY) {
            displayStatus("Request sent successfully", true, 
                         std::to_string(totalBytesSent) + " bytes transmitted");
        }
        
        return true;
        
    } catch (const std::exception& e) {
        displayError("Send request failed: " + std::string(e.what()), ErrorType::NETWORK);
        connected = false;
        return false;
    }
}

// Receive response from server
bool Client::receiveResponse(ResponseHeader& header, std::vector<uint8_t>& payload) {
    if (!connected || !socket || !socket->is_open()) {
        displayError("Not connected to server", ErrorType::NETWORK);
        return false;
    }
    
    try {
        // Receive header - manually to handle endianness
        std::vector<uint8_t> headerBytes(7); // ResponseHeader is 7 bytes
        boost::asio::read(*socket, boost::asio::buffer(headerBytes));
        
        // Parse header manually with proper endianness handling
        header.version = headerBytes[0];
        header.code = headerBytes[1] | (headerBytes[2] << 8);  // Little-endian uint16_t
        header.payload_size = headerBytes[3] | (headerBytes[4] << 8) | (headerBytes[5] << 16) | (headerBytes[6] << 24); // Little-endian uint32_t
        
        // Debug output for important responses
        displayStatus("Debug: Response received", true, 
                     "Version=" + std::to_string(header.version) +
                     ", Code=" + std::to_string(header.code) +
                     ", PayloadSize=" + std::to_string(header.payload_size));
        
        // Check version
        if (header.version != SERVER_VERSION) {
            displayError("Protocol version mismatch - Server: " + std::to_string(header.version) + 
                        ", Client expects: " + std::to_string(SERVER_VERSION), ErrorType::PROTOCOL);
            return false;
        }
        
        // Check for error response
        if (header.code == RESP_GENERIC_SERVER_ERROR) {
            displayError("Server returned general error", ErrorType::SERVER_ERROR);
            return false;
        }
        
        // Validate payload size
        if (header.payload_size > MAX_PACKET_SIZE) {
            displayError("Invalid payload size: " + std::to_string(header.payload_size), ErrorType::PROTOCOL);
            return false;
        }
        
        // Receive payload if any
        payload.clear();
        if (header.payload_size > 0) {
            payload.resize(header.payload_size);
            boost::asio::read(*socket, boost::asio::buffer(payload));
        }
        
        return true;
        
    } catch (const std::exception& e) {
        displayError("Failed to receive response: " + std::string(e.what()), ErrorType::NETWORK);
        return false;
    }
}

// Perform registration with streamlined error handling
bool Client::performRegistration() {
    displayStatus("Starting registration", true, "Using pre-generated RSA keys");

    // RSA keys should already be generated during initialization
    if (!rsaPrivate) {
        displayError("RSA keys not available for registration", ErrorType::CRYPTO);
        return false;
    }
    
    // Prepare registration payload - EXACTLY 255 bytes as expected by server
    std::vector<uint8_t> payload(MAX_NAME_SIZE, 0);  // Initialize all bytes to 0
    
    // Validate username length
    if (username.length() > MAX_NAME_SIZE - 1) {
        displayError("Username too long: " + std::to_string(username.length()) + 
                    " bytes (max: " + std::to_string(MAX_NAME_SIZE - 1) + ")", ErrorType::CONFIG);
        return false;
    }
    
    // Copy username to payload (null-terminated, zero-padded)
    std::copy(username.begin(), username.end(), payload.begin());
    // Ensure null termination (redundant but explicit)
    payload[username.length()] = 0;
    
    displayStatus("Sending registration", true, "Username: " + username);
    
    // Debug: show exact payload construction
    displayStatus("Debug: Registration payload", true, 
                 "Size=" + std::to_string(payload.size()) + " bytes" +
                 ", Username='" + username + "' (" + std::to_string(username.length()) + " chars)" +
                 ", Null-terminated and zero-padded");

    // Send registration request
    if (!sendRequest(REQ_REGISTER, payload)) {
        displayError("Failed to send registration request", ErrorType::NETWORK);
        return false;
    }
    
    // Receive response
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        displayError("Failed to receive registration response", ErrorType::NETWORK);
        return false;
    }
    
    // Process response
    if (header.code == RESP_REG_FAIL) {
        displayError("Registration failed: Username already exists", ErrorType::AUTHENTICATION);
        return false;
    }
    
    if (header.code != RESP_REG_OK || responsePayload.size() != CLIENT_ID_SIZE) {
        displayError("Invalid registration response - Code: " + std::to_string(header.code) + 
                    ", Expected: " + std::to_string(RESP_REG_OK) + 
                    ", Payload size: " + std::to_string(responsePayload.size()), ErrorType::PROTOCOL);
        return false;
    }
    
    // Success! Store client ID and save registration info
    std::copy(responsePayload.begin(), responsePayload.end(), clientID.begin());
    
    // Save info
    if (!saveMeInfo() || !savePrivateKey()) {
        displayError("Failed to save registration info", ErrorType::FILE_IO);
        return false;
    }
    
    displayStatus("Registration successful", true, 
                 "Client ID: " + bytesToHex(clientID.data(), 8) + "...");
    
    std::cout << "[DEBUG] Registration completed successfully" << std::endl;
    return true;
}

// Perform reconnection
bool Client::performReconnection() {
    // Prepare reconnection payload
    std::vector<uint8_t> payload(MAX_NAME_SIZE, 0);
    std::copy(username.begin(), username.end(), payload.begin());
    
    displayStatus("Sending reconnection", true, "Client ID: " + bytesToHex(clientID.data(), 8) + "...");
    
    // Send reconnection request
    if (!sendRequest(REQ_RECONNECT, payload)) {
        return false;
    }
    
    // Receive response
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        return false;
    }
    
    if (header.code == RESP_RECONNECT_FAIL) {
        return false;
    }
    
    if (header.code != RESP_RECONNECT_AES_SENT || responsePayload.size() <= CLIENT_ID_SIZE) {
        displayError("Invalid reconnection response", ErrorType::PROTOCOL);
        return false;
    }
    
    // Extract encrypted AES key
    std::vector<uint8_t> encryptedKey(responsePayload.begin() + CLIENT_ID_SIZE, responsePayload.end());
    
    displayStatus("Decrypting AES key", true, "Using stored RSA private key");
    
    // Decrypt AES key
    if (!decryptAESKey(encryptedKey)) {
        return false;
    }
    
    displayStatus("Reconnection", true, "Successfully authenticated");
    return true;
}

// Send public key
bool Client::sendPublicKey() {
    if (!rsaPrivate) {
        displayError("No RSA keys available", ErrorType::CRYPTO);
        return false;
    }
    
    // Get the actual public key first
    std::string actualPublicKey = rsaPrivate->getPublicKey();
    
    displayStatus("Debug: Actual public key size", true, 
                 std::to_string(actualPublicKey.size()) + " bytes, expected 160 bytes");
    
    // Prepare payload with exactly 415 bytes (255 username + 160 RSA key)
    std::vector<uint8_t> payload(MAX_NAME_SIZE + RSA_KEY_SIZE, 0);
    
    // Add username (255 bytes, null-terminated, zero-padded)
    std::copy(username.begin(), username.end(), payload.begin());
    
    // Add public key - ensure exactly 160 bytes
    if (actualPublicKey.size() > RSA_KEY_SIZE) {
        // Truncate if too large
        displayStatus("Warning: Public key truncated", false, 
                     "From " + std::to_string(actualPublicKey.size()) + " to " + std::to_string(RSA_KEY_SIZE) + " bytes");
        std::copy(actualPublicKey.begin(), actualPublicKey.begin() + RSA_KEY_SIZE, payload.begin() + MAX_NAME_SIZE);
    } else {
        // Copy what we have and zero-pad the rest
        std::copy(actualPublicKey.begin(), actualPublicKey.end(), payload.begin() + MAX_NAME_SIZE);
        // Zero-padding is already done since payload was initialized with zeros
    }
    
    displayStatus("Sending public key", true, 
                 "Payload: " + std::to_string(payload.size()) + " bytes (255 username + 160 RSA key)");
    
    // Debug: show exact payload construction
    displayStatus("Debug: Public key payload", true, 
                 "Size=" + std::to_string(payload.size()) + " bytes" +
                 ", Username='" + username + "' (" + std::to_string(username.length()) + " chars)" +
                 ", RSA key=" + std::to_string(actualPublicKey.size()) + " bytes (padded to 160)");
    
    // Send request
    if (!sendRequest(REQ_SEND_PUBLIC_KEY, payload)) {
        return false;
    }
    
    // Receive response
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        return false;
    }
    
    if (header.code != RESP_PUBKEY_AES_SENT || responsePayload.size() <= CLIENT_ID_SIZE) {
        displayError("Invalid public key response", ErrorType::PROTOCOL);
        return false;
    }
    
    // Extract encrypted AES key
    std::vector<uint8_t> encryptedKey(responsePayload.begin() + CLIENT_ID_SIZE, responsePayload.end());
    
    displayStatus("Received AES key", true, "Encrypted with RSA");
    
    // Decrypt AES key
    if (!decryptAESKey(encryptedKey)) {
        return false;
    }
    
    displayStatus("Key exchange", true, "AES-256 key established");
    return true;
}

// Transfer file
bool Client::transferFile() {
    // Read file
    displayStatus("Reading file", true, filepath);
    auto fileData = readFile(filepath);
    if (fileData.empty()) {
        displayError("Cannot read file or file is empty", ErrorType::FILE_IO);
        return false;
    }
    
    stats.totalBytes = fileData.size();
    stats.reset();
    
    // Extract filename
    std::string filename = filepath;
    size_t lastSlash = filename.find_last_of("/\\");
    if (lastSlash != std::string::npos) {
        filename = filename.substr(lastSlash + 1);
    }
    
    displayStatus("File details", true, "Name: " + filename + ", Size: " + formatBytes(stats.totalBytes));
    displayStatus("Encrypting file", true, "AES-256-CBC encryption");
    
    // Encrypt file
    std::string encryptedData = encryptFile(fileData);
    if (encryptedData.empty()) {
        return false;
    }
    
    displayStatus("Encryption complete", true, "Encrypted size: " + formatBytes(encryptedData.size()));
    
    // Calculate packets
    size_t encryptedSize = encryptedData.size();
    uint16_t totalPackets = static_cast<uint16_t>((encryptedSize + MAX_PACKET_SIZE - 1) / MAX_PACKET_SIZE);
    
    displayStatus("Transfer preparation", true, "Splitting into " + std::to_string(totalPackets) + " packets");
    displaySeparator();
    
    // Send packets
    for (uint16_t packet = 1; packet <= totalPackets; packet++) {
        size_t offset = (packet - 1) * MAX_PACKET_SIZE;
        size_t chunkSize = std::min(MAX_PACKET_SIZE, encryptedSize - offset);
        
        std::string chunk = encryptedData.substr(offset, chunkSize);
        
        if (!sendFilePacket(filename, chunk, static_cast<uint32_t>(fileData.size()), packet, totalPackets)) {
            return false;
        }
        
        stats.update(offset + chunkSize);
        displayProgress("Transferring", stats.transferredBytes, encryptedData.size());
        
        if (packet % 10 == 0 || packet == totalPackets) {
            displayTransferStats();
        }
    }
    
    displaySeparator();
    displayStatus("Transfer complete", true, "All packets sent successfully");
    displayStatus("Waiting for server", true, "Server calculating CRC...");
    
    // Receive CRC response
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        return false;
    }
    
    if (header.code != RESP_FILE_CRC || responsePayload.size() < 279) {
        displayError("Invalid file transfer response", ErrorType::PROTOCOL);
        return false;
    }
    
    // Extract CRC
    uint32_t serverCRC;
    std::memcpy(&serverCRC, responsePayload.data() + 275, 4);
    
    // Verify CRC
    return verifyCRC(serverCRC, fileData, filename);
}

// Send file packet
bool Client::sendFilePacket(const std::string& filename, const std::string& encryptedData,
                           uint32_t originalSize, uint16_t packetNum, uint16_t totalPackets) {
    // Create payload
    std::vector<uint8_t> payload;
    
    // Add metadata
    uint32_t encryptedSize = static_cast<uint32_t>(encryptedData.size());
    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&encryptedSize),
                   reinterpret_cast<uint8_t*>(&encryptedSize) + 4);
    
    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&originalSize),
                   reinterpret_cast<uint8_t*>(&originalSize) + 4);
    
    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&packetNum),
                   reinterpret_cast<uint8_t*>(&packetNum) + 2);
    
    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&totalPackets),
                   reinterpret_cast<uint8_t*>(&totalPackets) + 2);
    
    // Add filename (255 bytes)
    std::vector<uint8_t> filenameBytes(255, 0);
    std::copy(filename.begin(), filename.end(), filenameBytes.begin());
    payload.insert(payload.end(), filenameBytes.begin(), filenameBytes.end());
    
    // Add encrypted data
    payload.insert(payload.end(), encryptedData.begin(), encryptedData.end());
    
    return sendRequest(REQ_SEND_FILE, payload);
}

// Verify CRC
bool Client::verifyCRC(uint32_t serverCRC, const std::vector<uint8_t>& originalData, const std::string& filename) {
    displayStatus("Calculating CRC", true, "Using cksum algorithm");
    
    uint32_t clientCRC = calculateCRC32(originalData.data(), originalData.size());
    
    displayStatus("CRC verification", true, "Server: " + std::to_string(serverCRC) + 
                  ", Client: " + std::to_string(clientCRC));
    
    // Prepare filename payload
    std::vector<uint8_t> payload(255, 0);
    std::copy(filename.begin(), filename.end(), payload.begin());
    
    if (serverCRC == clientCRC) {
        displayStatus("CRC verification", true, "✓ Checksums match - file integrity confirmed");
        sendRequest(REQ_CRC_OK, payload);
        
        // Wait for ACK
        ResponseHeader header;
        std::vector<uint8_t> responsePayload;
        receiveResponse(header, responsePayload);
        
        return true;
    } else {
        crcRetries++;
        if (crcRetries < MAX_RETRIES) {
            displayStatus("CRC verification", false, "Mismatch - Retry " + std::to_string(crcRetries) + " of " + std::to_string(MAX_RETRIES));
            sendRequest(REQ_CRC_INVALID_RETRY, payload);
            
            // Reset CRC retries for next attempt
            int savedRetries = crcRetries;
            crcRetries = 0;
            
            // Retry the transfer
            bool result = transferFile();
            
            // Restore retry count if transfer failed
            if (!result) {
                crcRetries = savedRetries;
            }
            
            return result;
        } else {
            displayStatus("CRC verification", false, "Maximum retries exceeded - aborting");
            sendRequest(REQ_CRC_FAILED_ABORT, payload);
            return false;
        }
    }
}

// Generate RSA keys
bool Client::generateRSAKeys() {
    std::cout << "[DEBUG] Client::generateRSAKeys() - Starting RSA key generation" << std::endl;
    try {
        std::cout << "[DEBUG] Client::generateRSAKeys() - About to create RSAPrivateWrapper" << std::endl;
        auto start = std::chrono::steady_clock::now();
        rsaPrivate = new RSAPrivateWrapper();
        std::cout << "[DEBUG] Client::generateRSAKeys() - RSAPrivateWrapper created successfully" << std::endl;
        auto end = std::chrono::steady_clock::now();        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        displayStatus("RSA key generation", true, "1024-bit keys generated in " + std::to_string(duration) + "ms");
        return true;
    } catch (const std::exception& e) {
        displayError("Failed to generate RSA keys: " + std::string(e.what()), ErrorType::CRYPTO);
        return false;
    } catch (...) {
        displayError("Failed to generate RSA keys: Unknown exception", ErrorType::CRYPTO);
        return false;
    }
}

// Decrypt AES key
bool Client::decryptAESKey(const std::vector<uint8_t>& encryptedKey) {
    if (!rsaPrivate) {
        displayError("No RSA private key available", ErrorType::CRYPTO);
        return false;
    }
    
    try {
        std::string encrypted(reinterpret_cast<const char*>(encryptedKey.data()), encryptedKey.size());
        aesKey = rsaPrivate->decrypt(encrypted);
        
        if (aesKey.size() != AES_KEY_SIZE) {
            displayError("Invalid AES key size: " + std::to_string(aesKey.size()) + " bytes (expected 32)", ErrorType::CRYPTO);
            return false;
        }
        
        displayStatus("AES key decrypted", true, "256-bit key ready");
        return true;
    } catch (...) {
        displayError("Failed to decrypt AES key", ErrorType::CRYPTO);
        return false;
    }
}

// Encrypt file with AES
std::string Client::encryptFile(const std::vector<uint8_t>& data) {
    if (aesKey.empty()) {
        displayError("No AES key available", ErrorType::CRYPTO);
        return "";
    }
      try {
        auto start = std::chrono::steady_clock::now();
        // Debug: Check actual AES key size
        displayStatus("AES key debug", true, "Key size: " + std::to_string(aesKey.size()) + " bytes");
        
        if (aesKey.size() != 32) {
            displayError("Invalid AES key size: " + std::to_string(aesKey.size()) + " bytes (expected 32)", ErrorType::CRYPTO);
            return "";
        }
        
        // Use 32-byte key and static IV of all zeros for protocol compliance
        AESWrapper aes(reinterpret_cast<const unsigned char*>(aesKey.c_str()), 32, true);
        std::string result = aes.encrypt(reinterpret_cast<const char*>(data.data()), data.size());
        auto end = std::chrono::steady_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        double speed = (data.size() / 1024.0 / 1024.0) / (duration / 1000.0);
        
        displayStatus("Encryption performance", true, 
                     std::to_string(duration) + "ms (" + 
                     std::to_string(static_cast<int>(speed)) + " MB/s)");
        
        return result;
    } catch (...) {
        displayError("Failed to encrypt file", ErrorType::CRYPTO);
        return "";
    }
}

// Read file
std::vector<uint8_t> Client::readFile(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        return {};
    }
    
    file.seekg(0, std::ios::end);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    
    std::vector<uint8_t> data(size);
    
    // Read in chunks for better performance
    size_t bytesRead = 0;
    while (bytesRead < size) {
        size_t toRead = std::min(OPTIMAL_BUFFER_SIZE, size - bytesRead);
        file.read(reinterpret_cast<char*>(data.data() + bytesRead), toRead);
        bytesRead += file.gcount();
    }
    
    return data;
}

// Convert bytes to hex string
std::string Client::bytesToHex(const uint8_t* data, size_t size) {
    std::stringstream ss;
    ss << std::hex << std::setfill('0');
    for (size_t i = 0; i < size; i++) {
        ss << std::setw(2) << static_cast<int>(data[i]);
    }
    return ss.str();
}

// Convert hex string to bytes
std::vector<uint8_t> Client::hexToBytes(const std::string& hex) {
    std::vector<uint8_t> bytes;
    for (size_t i = 0; i < hex.length(); i += 2) {
        std::string byteString = hex.substr(i, 2);
        bytes.push_back(static_cast<uint8_t>(std::stoi(byteString, nullptr, 16)));
    }
    return bytes;
}

// Calculate CRC32 using provided wrapper
uint32_t Client::calculateCRC32(const uint8_t* data, size_t size) {
    return calculateCRC(data, size);
}

// Format bytes to human readable
std::string Client::formatBytes(size_t bytes) {
    const char* sizes[] = {"B", "KB", "MB", "GB"};
    int order = 0;
    double size = static_cast<double>(bytes);
    
    while (size >= 1024 && order < 3) {
        order++;
        size /= 1024;
    }
    
    std::stringstream ss;
    ss << std::fixed << std::setprecision(2) << size << " " << sizes[order];
    return ss.str();
}

// Format duration to human readable
std::string Client::formatDuration(int seconds) {
    if (seconds < 60) {
        return std::to_string(seconds) + "s";
    } else if (seconds < 3600) {
        int minutes = seconds / 60;
        int secs = seconds % 60;
        return std::to_string(minutes) + "m " + std::to_string(secs) + "s";
    } else {
        int hours = seconds / 3600;
        int minutes = (seconds % 3600) / 60;
        return std::to_string(hours) + "h " + std::to_string(minutes) + "m";
    }
}

// Get current timestamp
std::string Client::getCurrentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time_t), "%H:%M:%S");
    return ss.str();
}

// Visual feedback functions
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

  // updateGUIStatus(operation, success, details);
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
double progressPercent = (total > 0) ? ((double)current / total) * 100.0 : 0.0;
    std::string speed = formatBytes(static_cast<size_t>(stats.currentSpeed)) + "/s";
    std::string eta = formatDuration(stats.estimatedTimeRemaining);
    std::string transferred = formatBytes(current);
    // updateGUIProgress(progressPercent, speed, eta, transferred);
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
    std::cout << "  Encryption: RSA-1024 + AES-256-CBC\n\n";
#else
    std::cout << "\n============================================\n";
    std::cout << "     ENCRYPTED FILE BACKUP CLIENT v1.0      \n";
    std::cout << "============================================\n";
    std::cout << "  Build Date: " << __DATE__ << " " << __TIME__ << "\n";
    std::cout << "  Protocol Version: " << static_cast<int>(CLIENT_VERSION) << "\n";    std::cout << "  Encryption: RSA-1024 + AES-256-CBC\n\n";
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
    displaySeparator();
}

void Client::displayError(const std::string& message, ErrorType type) {
    lastError = type;
    lastErrorDetails = message;
    
    // Temporarily show actual error message for debugging
    // Check if this is a server error response
    // if (message.find("server") != std::string::npos || 
    //     message.find("response") != std::string::npos ||
    //     type == ErrorType::SERVER_ERROR) {
    //     std::cerr << "server responded with an error" << std::endl;
    // } else {
#ifdef _WIN32
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_INTENSITY);
        std::cerr << "[ERROR] ";
        SetConsoleTextAttribute(hConsole, savedAttributes);
#else
        std::cerr << "[ERROR] ";
#endif
        
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
                break;            case ErrorType::AUTHENTICATION:
                std::cerr << "[AUTH] ";
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
    // }
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
// updateGUIPhase(phase);
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
    std::cout << "  Average Speed: " << formatBytes(static_cast<size_t>(stats.averageSpeed)) << "/s\n";    std::cout << "  Server: " << serverIP << ":" << serverPort << "\n";
    std::cout << "  Timestamp: " << getCurrentTimestamp() << "\n";
    displaySeparator();
    
    // Show GUI completion notification (optional)
    try {
        std::string successMessage = "File backup completed successfully!\n\nFile: " + filepath + 
                                   "\nSize: " + formatBytes(stats.totalBytes) + 
                                   "\nDuration: " + formatDuration(static_cast<int>(totalDuration));
        ClientGUIHelpers::showNotification("Backup Complete", successMessage);
    } catch (...) {
        // GUI notification failed - continue without GUI
    }
}

// Backup client function that can be called from main
bool runBackupClient() {
    // Write to a log file so we can see what's happening
    std::ofstream logFile("client_debug.log", std::ios::app);
    logFile << "=== ENCRYPTED BACKUP CLIENT DEBUG MODE ===" << std::endl;
    logFile << "Application started at: " << __DATE__ << " " << __TIME__ << std::endl;
    logFile.flush();
    
    // Also try console output
    std::cout << "=== ENCRYPTED BACKUP CLIENT DEBUG MODE ===" << std::endl;
    std::cout << "Console application started!" << std::endl;
    std::cout << "Starting client with console output..." << std::endl;

    try {
        logFile << "About to create client object..." << std::endl;
        logFile.flush();
        std::cout << "About to create client object..." << std::endl;
        std::cout.flush();
        
        Client client;
        logFile << "Client object created successfully!" << std::endl;
        logFile.flush();
        std::cout << "Client object created successfully!" << std::endl;

        std::cout << "About to initialize client..." << std::endl;
        std::cout.flush();
          if (!client.initialize()) {
            std::cerr << "Fatal: Client initialization failed" << std::endl;
            if (!g_batchMode) {
                std::cout << "\nPress Enter to exit...";
                std::cin.get();
            }
            return false;
        }

        std::cout << "Client initialized successfully. Starting backup operation..." << std::endl;
        if (!client.run()) {
            std::cerr << "Fatal: File backup failed" << std::endl;
#ifdef _WIN32            // Show error notification via GUI if available
            try {
                if (!g_batchMode) {
                    ClientGUIHelpers::showNotification("Backup Error", "File backup operation failed");
                    ClientGUIHelpers::updateError("Backup failed");
                }
            } catch (...) {}

            // Keep window open to show error
            if (!g_batchMode) {
                std::cout << "\nPress Enter to exit...";
                std::cin.get();
            }
#endif
            return false;
        }

        std::cout << "\nBackup completed successfully!" << std::endl;

#ifdef _WIN32
        // Show success notification via GUI if available
        try {
            if (!g_batchMode) {
                ClientGUIHelpers::showNotification("Backup Complete", "File backup completed successfully!");
                ClientGUIHelpers::updatePhase("Backup Complete");
            }
        } catch (...) {}

        // Keep window open to show success
        if (!g_batchMode) {
            std::cout << "\nPress Enter to exit...";
            std::cin.get();
        }
#endif

        return true;    } catch (const std::exception& e) {
        std::cerr << "Fatal exception: " << e.what() << std::endl;
#ifdef _WIN32
        try {
            if (!g_batchMode) {
                ClientGUIHelpers::showNotification("Critical Error", std::string("Exception: ") + e.what());
                ClientGUIHelpers::updateError(std::string("Critical error: ") + e.what());
            }
        } catch (...) {}

        if (!g_batchMode) {
            std::cout << "\nPress Enter to exit...";
            std::cin.get();
        }
#endif
        return false;    } catch (...) {
        std::cerr << "Fatal: Unknown exception occurred" << std::endl;
#ifdef _WIN32
        try {
            if (!g_batchMode) {
                ClientGUIHelpers::showNotification("Critical Error", "Unknown exception occurred");
                ClientGUIHelpers::updateError("Unknown critical error");
            }
        } catch (...) {}

        if (!g_batchMode) {
            std::cout << "\nPress Enter to exit...";
            std::cin.get();
        }
#endif
        return false;
    }
}
void Client::handleGUICommand(const std::map<std::string, std::string>& command) {
    // Generic command handler - dispatch to specific handlers based on command type
    auto it = command.find("type");
    if (it != command.end()) {
        const std::string& type = it->second;
        
        if (type == "connect") {
            handleConnectCommand(command);
        } else if (type == "start_backup") {
            handleStartBackupCommand(command);
        } else if (type == "file_selected") {
            handleFileSelectedCommand(command);
        } else {
            displayError("Unknown command type: " + type, ErrorType::PROTOCOL);
        }
    } else {
        displayError("Invalid command format - missing type", ErrorType::PROTOCOL);
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
            
            displayStatus("Connect command received", true, 
                         "IP: " + pendingServerIP + ", Port: " + std::to_string(pendingServerPort) + 
                         ", User: " + pendingUsername);
            
            // Attempt to connect to the server
            if (connectToServer()) {
                // Update client info
                username = pendingUsername;
                saveMeInfo();
                
                // Send success response
                sendGUIResponse("connect", "Connection successful");
            } else {
                sendGUIResponse("connect", "Connection failed", false);
            }
        } else {
            sendGUIResponse("connect", "Invalid parameters", false);
        }
    } catch (const std::exception& e) {
        sendGUIResponse("connect", "Error: " + std::string(e.what()), false);
    } catch (...) {
        sendGUIResponse("connect", "Unknown error", false);
    }
}

void Client::handleStartBackupCommand(const std::map<std::string, std::string>& command) {
    // Handle start backup command from GUI
    try {
        auto fileIt = command.find("file");
        
        if (fileIt != command.end()) {
            selectedFilePath = fileIt->second;
            
" << (success ? "true" : "false") << ","
               << "\"details\":\"" << details << "\"}\n";
    statusFile.flush();
}

void Client::updateGUIProgress(double percentage, const std::string& speed, const std::string& eta, const std::string& transferred) {
    std::ofstream progressFile("gui_progress.json");
    
    progressFile << "{"
                 << "\"percentage\":" << percentage << ","
                 << "\"speed\":\"" << speed << "\","
                 << "\"eta\":\"" << eta << "\","
                 << "\"transferred\":\"" << transferred << "\""
                 << "}\n";
    progressFile.flush();
    progressFile.close();
}

void Client::updateGUIPhase(const std::string& phase) {
    updateGUIStatus("Phase Change", true, phase);
}

void Client::initializeWebSocketCommands() {
    // Initialize WebSocket command handling - placeholder for future implementation
    // TODO: Implement WebSocket command handling when needed

    displayStatus("WebSocket", true, "Command handling placeholder initialized");
}

void Client::handleGUICommand(const std::map<std::string, std::string>& command) {
    // Generic command handler - dispatch to specific handlers based on command type
    auto it = command.find("type");
    if (it != command.end()) {
        const std::string& type = it->second;
        
        if (type == "connect") {
            handleConnectCommand(command);
        } else if (type == "start_backup") {
            handleStartBackupCommand(command);
        } else if (type == "file_selected") {
            handleFileSelectedCommand(command);
        } else {
            displayError("Unknown command type: " + type, ErrorType::PROTOCOL);
        }
    } else {
        displayError("Invalid command format - missing type", ErrorType::PROTOCOL);
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
            
            displayStatus("Connect command received", true, 
                         "IP: " + pendingServerIP + ", Port: " + std::to_string(pendingServerPort) + 
                         ", User: " + pendingUsername);
            
            // Attempt to connect to the server
            if (connectToServer()) {
                // Update client info
                username = pendingUsername;
                saveMeInfo();
                
                // Send success response
                sendGUIResponse("connect", "Connection successful");
            } else {
                sendGUIResponse("connect", "Connection failed", false);
            }
        } else {
            sendGUIResponse("connect", "Invalid parameters", false);
        }
    } catch (const std::exception& e) {
        sendGUIResponse("connect", "Error: " + std::string(e.what()), false);
    } catch (...) {
        sendGUIResponse("connect", "Unknown error", false);
    }
}

void Client::handleStartBackupCommand(const std::map<std::string, std::string>& command) {
    // Handle start backup command from GUI
    try {
        auto fileIt = command.find("file");
        
        if (fileIt != command.end()) {
            selectedFilePath = fileIt->second;
            
            displayStatus("Start backup command received", true, "File: " + selectedFilePath);
            
            // Update file path and re-read transfer info
            filepath = selectedFilePath;
            readTransferInfo();
            
            // Perform backup operation
            if (run()) {
                sendGUIResponse("start_backup", "Backup completed successfully");
            } else {
                sendGUIResponse("start_backup", "Backup failed", false);
            }
        } else {
            sendGUIResponse("start_backup", "Invalid parameters", false);
        }
   
    } catch (const std::exception& e) {
        sendGUIResponse("start_backup", "Error: " + std::string(e.what()), false);
    } catch (...) {
        sendGUIResponse("start_backup", "Unknown error", false);
    }
}

void Client::handleFileSelectedCommand(const std::map<std::string, std::string>& command) {
    // Handle file selected command from GUI
    try {
        auto fileIt = command.find("file");
        
        if (fileIt != command.end()) {
            std::string filePath = fileIt->second;
            selectedFilePath = filePath;
            
            displayStatus("File selected", true, "File: " + filePath);
            sendGUIResponse("file_selected", "File selection confirmed");
        } else {
            sendGUIResponse("file_selected", "Invalid parameters", false);
        }
    } catch ( const std::exception& e) {
        sendGUIResponse("file_selected", "Error: " + std::string(e.what()), false);
    }
}

void Client::sendGUIResponse(const std::string& type, const std::string& message, bool success) {
    // Send response back to GUI - placeholder implementation
    displayStatus("GUI Response", success, type + ": " + message);
    // TODO: Implement actual GUI communication when needed
}

// Socket validation and recovery functions
bool Client::validateSocketConnection() {
    if (!socket) {
        std::cout << "[DEBUG] Socket validation failed: socket is null" << std::endl;
        return false;
    }
    
    if (!socket->is_open()) {
        std::cout << "[DEBUG] Socket validation failed: socket is not open" << std::endl;
        return false;
    }
    
    // Check if socket is still connected by testing availability
    try {
        boost::system::error_code ec;
        size_t available = socket->available(ec);
        
        if (ec) {
            std::cout << "[DEBUG] Socket validation failed: " << ec.message() << std::endl;
            return false;
        }
        
        std::cout << "[DEBUG] Socket validation passed: " << available << " bytes available" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cout << "[DEBUG] Socket validation exception: " << e.what() << std::endl;
        return false;
    }
}

bool Client::attemptConnectionRecovery() {
    std::cout << "[DEBUG] Attempting connection recovery..." << std::endl;
    
    // Close existing socket
    if (socket && socket->is_open()) {
        try {
            socket->close();
        } catch (...) {
            // Ignore close errors
        }
    }
    
    connected = false;
    socket.reset();
    
    // Short delay before reconnection
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    
    // Attempt to reconnect
    displayStatus("Connection recovery", true, "Attempting to reconnect...");
    
    if (connectToServer()) {
        displayStatus("Connection recovery", true, "Successfully reconnected");
        std::cout << "[DEBUG] Connection recovery successful" << std::endl;
        return true;
    } else {
        displayError("Connection recovery failed", ErrorType::NETWORK);
        std::cout << "[DEBUG] Connection recovery failed" << std::endl;
        return false;
    }
}