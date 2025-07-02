#pragma once

// ClientCore.h
// Enhanced Client Class Definition - Modular Architecture
// Contains class definition, constants, and data structures

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
#include <atomic>
#include <ctime>
#include <memory>
#include <map>

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <direct.h>
#include <sys/stat.h>
#include <windows.h>
#include <io.h>
#include <fcntl.h>
#include <shellapi.h>
#endif

// Boost.Asio for cross-platform networking
#include <boost/asio.hpp>
#include <boost/system/error_code.hpp>
#include <boost/bind/bind.hpp>

// Project-specific includes
#include "../client/cksum.h"
#include "../wrappers/AESWrapper.h"
#include "../wrappers/Base64Wrapper.h"
#include "../wrappers/RSAWrapper.h"

// Global batch mode flag (defined in main.cpp)
// extern bool g_batchMode;

// Protocol constants
constexpr uint8_t CLIENT_VERSION = 3;
constexpr uint8_t SERVER_VERSION = 3;

// Request codes - MUST match server constants exactly
constexpr uint16_t REQ_REGISTER = 1025;
constexpr uint16_t REQ_SEND_PUBLIC_KEY = 1026;
constexpr uint16_t REQ_RECONNECT = 1027;
constexpr uint16_t REQ_SEND_FILE = 1028;
constexpr uint16_t REQ_CRC_OK = 1029;
constexpr uint16_t REQ_CRC_INVALID_RETRY = 1030;
constexpr uint16_t REQ_CRC_FAILED_ABORT = 1031;

// Response codes - MUST match server constants exactly
constexpr uint16_t RESP_REG_OK = 1600;
constexpr uint16_t RESP_REG_FAIL = 1601;
constexpr uint16_t RESP_PUBKEY_AES_SENT = 1602;
constexpr uint16_t RESP_FILE_CRC = 1603;
constexpr uint16_t RESP_ACK = 1604;
constexpr uint16_t RESP_RECONNECT_AES_SENT = 1605;
constexpr uint16_t RESP_RECONNECT_FAIL = 1606;
constexpr uint16_t RESP_GENERIC_SERVER_ERROR = 1607;

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

// Enhanced Client class with modular design
class Client {
private:
    // === NETWORKING & CONNECTION ===
    boost::asio::io_context ioContext;
    std::unique_ptr<boost::asio::ip::tcp::socket> socket;
    std::string serverIP;
    uint16_t serverPort;
    bool connected;
    std::atomic<bool> keepAliveEnabled;
    
    // === CLIENT IDENTIFICATION ===
    std::array<uint8_t, CLIENT_ID_SIZE> clientID;
    std::string username;
    std::string filepath;
    
    // === CRYPTOGRAPHY ===
    RSAPrivateWrapper* rsaPrivate;
    std::string aesKey;
    
    // === OPERATION TRACKING ===
    int fileRetries;
    int crcRetries;
    int reconnectAttempts;
    TransferStats stats;
    
    // === ERROR HANDLING ===
    ErrorType lastError;
    std::string lastErrorDetails;
    
    // === PERFORMANCE METRICS ===
    std::chrono::steady_clock::time_point operationStartTime;
    
    // === INTERACTIVE MODE ===
    bool interactiveMode;
    uint16_t pendingServerPort;

#ifdef _WIN32
    // === CONSOLE CONTROL (Windows) ===
    HANDLE hConsole;
    CONSOLE_SCREEN_BUFFER_INFO consoleInfo;
    WORD savedAttributes;
#endif

public:
    // === CORE LIFECYCLE ===
    Client();
    ~Client();
    
    // === MAIN INTERFACE ===
    bool initialize();
    bool run();

    // === NETWORKING & PROTOCOL OPERATIONS (ClientCore.cpp) ===
    bool connectToServer();
    void closeConnection();
    bool sendRequest(uint16_t code, const std::vector<uint8_t>& payload = {});
    bool receiveResponse(ResponseHeader& header, std::vector<uint8_t>& payload);
    bool testConnection();
    void enableKeepAlive();
    bool validateSocketConnection();
    bool attemptConnectionRecovery();
    bool performRegistration();
    bool performReconnection();

    // === CRYPTOGRAPHIC OPERATIONS (ClientCrypto.cpp) ===
    bool generateRSAKeys();
    bool loadPrivateKey();
    bool savePrivateKey();
    bool decryptAESKey(const std::vector<uint8_t>& encryptedKey);
    std::string encryptFile(const std::vector<uint8_t>& data);
    bool sendPublicKey();

    // === FILE OPERATIONS (ClientFileOps.cpp) ===
    bool readTransferInfo();
    bool validateConfiguration();
    bool loadMeInfo();
    bool saveMeInfo();
    std::vector<uint8_t> readFile(const std::string& path);
    bool transferFile();
    bool sendFilePacket(const std::string& filename, const std::string& encryptedData, 
                       uint32_t originalSize, uint16_t packetNum, uint16_t totalPackets);
    bool verifyCRC(uint32_t serverCRC, const std::vector<uint8_t>& originalData, const std::string& filename);
    uint32_t calculateCRC32(const uint8_t* data, size_t size);

    // === UTILITY FUNCTIONS ===
    std::string bytesToHex(const uint8_t* data, size_t size);
    std::vector<uint8_t> hexToBytes(const std::string& hex);
    std::string formatBytes(size_t bytes);
    std::string formatDuration(int seconds);
    std::string getCurrentTimestamp();
};

// === GLOBAL FUNCTION (defined in ClientCore.cpp) ===
bool runBackupClient();