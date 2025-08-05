#pragma once

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
#include <memory>
#include <ctime>

// Boost.Asio for cross-platform networking
#include <boost/asio.hpp>
#include <boost/system/error_code.hpp>
#include <boost/bind/bind.hpp>

// Windows console control
#ifdef _WIN32
#include <windows.h>
#include <io.h>
#include <fcntl.h>
#endif

// Required wrapper includes
#include "wrappers/AESWrapper.h"
#include "wrappers/Base64Wrapper.h"
#include "wrappers/RSAWrapper.h"
#include "client/WebServerBackend.h"

// Protocol constants
constexpr uint8_t CLIENT_VERSION = 3;
constexpr uint8_t SERVER_VERSION = 3;

// Request codes
constexpr uint16_t REQ_REGISTER = 1025;
constexpr uint16_t REQ_SEND_PUBLIC_KEY = 1026;
constexpr uint16_t REQ_RECONNECT = 1027;
constexpr uint16_t REQ_SEND_FILE = 1028;
constexpr uint16_t REQ_CRC_OK = 1029;
constexpr uint16_t REQ_CRC_RETRY = 1030;
constexpr uint16_t REQ_CRC_ABORT = 1031;

// Response codes
constexpr uint16_t RESP_REGISTER_OK = 1600;
constexpr uint16_t RESP_REGISTER_FAIL = 1601;
constexpr uint16_t RESP_PUBKEY_AES_SENT = 1602;
constexpr uint16_t RESP_FILE_CRC = 1603;
constexpr uint16_t RESP_ACK = 1604;
constexpr uint16_t RESP_RECONNECT_AES_SENT = 1605;
constexpr uint16_t RESP_RECONNECT_FAIL = 1606;
constexpr uint16_t RESP_ERROR = 1607;

// Size constants
constexpr size_t CLIENT_ID_SIZE = 16;
constexpr size_t MAX_NAME_SIZE = 255;
constexpr size_t RSA_KEY_SIZE = 160;
constexpr size_t AES_KEY_SIZE = 32;
constexpr size_t MAX_PACKET_SIZE = 1024 * 1024;
constexpr size_t OPTIMAL_BUFFER_SIZE = 64 * 1024;  // Legacy - will be replaced by adaptive sizing

// Adaptive buffer constants
constexpr size_t MIN_BUFFER_SIZE = 1024;        // 1KB minimum
constexpr size_t MAX_BUFFER_SIZE = 32768;       // 32KB maximum for L1 cache efficiency
constexpr size_t MMAP_THRESHOLD = 1024 * 1024; // 1MB threshold for memory mapping
constexpr size_t AES_BLOCK_SIZE = 16;           // AES-256-CBC block size

// Other constants
constexpr int MAX_RETRIES = 3;
constexpr int SOCKET_TIMEOUT_MS = 30000;
constexpr int RECONNECT_DELAY_MS = 5000;
constexpr int KEEPALIVE_INTERVAL = 60;

// Enhanced error codes for better debugging
enum class ErrorType {
    NONE,
    NETWORK,
    FILE_IO,
    PROTOCOL,
    CRYPTO,
    CONFIG,
    AUTHENTICATION,
    SERVER_ERROR,
    GENERAL
};

// Protocol structures
#pragma pack(push, 1)
struct RequestHeader {
    uint8_t client_id[CLIENT_ID_SIZE];
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

    TransferStats();
    void reset();
    void update(size_t newBytes);
};

// Dynamic Buffer Management System with Network Adaptation
class DynamicBufferManager {
private:
    size_t currentBufferSize;
    size_t minBufferSize;
    size_t maxBufferSize;
    
    // Performance metrics for adaptation
    std::chrono::steady_clock::time_point lastPacketTime;
    double averagePacketTime;
    double packetTimeVariance;
    size_t consecutiveSuccesses;
    size_t consecutiveFailures;
    
    // Adaptation parameters
    static constexpr double GROWTH_FACTOR = 1.5;
    static constexpr double SHRINK_FACTOR = 0.75;
    static constexpr size_t SUCCESS_THRESHOLD = 3;
    static constexpr size_t FAILURE_THRESHOLD = 2;
    static constexpr double VARIANCE_THRESHOLD = 0.3;

public:
    DynamicBufferManager(size_t initialSize = 4096) 
        : currentBufferSize(alignToAESBlocks(initialSize))
        , minBufferSize(MIN_BUFFER_SIZE)
        , maxBufferSize(MAX_BUFFER_SIZE)
        , averagePacketTime(0.0)
        , packetTimeVariance(0.0)
        , consecutiveSuccesses(0)
        , consecutiveFailures(0) {
        lastPacketTime = std::chrono::steady_clock::now();
    }
    
    // Get current buffer size
    size_t getCurrentBufferSize() const { return currentBufferSize; }
    
    // Adapt buffer size based on transfer performance
    void adaptAfterPacket(bool success, size_t bytesTransferred);
    
    // Reset for new transfer
    void reset(size_t suggestedInitialSize = 4096);
    
    // Align size to AES block boundaries
    static size_t alignToAESBlocks(size_t size) {
        return ((size + AES_BLOCK_SIZE - 1) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    }
    
    // Calculate initial buffer size based on file size hint
    static size_t calculateInitialBufferSize(size_t fileSize) {
        if (fileSize <= 16 * 1024) return 2048;    // 2KB for small files
        if (fileSize <= 256 * 1024) return 8192;   // 8KB for medium files  
        if (fileSize <= 2 * 1024 * 1024) return 16384; // 16KB for large files
        return 32768; // 32KB for very large files
    }
};

// Enhanced File Transfer Engine
enum class TransferStrategy {
    ADAPTIVE_BUFFER,    // Adaptive buffer sizing (default)
    MEMORY_MAPPED,      // Memory-mapped I/O for large files
    STREAMING_ROBUST    // Robust streaming with error recovery
};

struct TransferConfig {
    TransferStrategy strategy = TransferStrategy::ADAPTIVE_BUFFER;
    size_t bufferSize = 0;  // 0 = auto-calculate
    bool enableProgressiveRecovery = true;
    bool enableMemoryMapping = true;
    size_t mmapThreshold = MMAP_THRESHOLD;
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
#ifdef _WIN32
    HANDLE hConsole;
    CONSOLE_SCREEN_BUFFER_INFO consoleInfo;
    WORD savedAttributes;
#endif

    // Error tracking
    ErrorType lastError;
    std::string lastErrorDetails;

    // Performance metrics
    std::chrono::steady_clock::time_point operationStartTime;

    // GUI Integration
    std::unique_ptr<WebServerBackend> webServer;

public:
    Client();
    ~Client();

    // Main interface
    bool initialize();
    bool run();

    // Configuration structure for backup operations
    struct BackupConfig {
        std::string serverIP;
        uint16_t serverPort;
        std::string username;
        std::string filepath;
        
        // Validation method
        bool isValid() const {
            return !serverIP.empty() && serverPort > 0 && serverPort <= 65535 && 
                   !username.empty() && username.length() <= 100 && !filepath.empty();
        }
    };

    // GUI interface for web-triggered operations
    bool runBackupOperation();
    bool runBackupOperation(const BackupConfig& config);

    // Non-copyable
    Client(const Client&) = delete;
    Client& operator=(const Client&) = delete;

private:
    // Configuration methods
    bool readTransferInfo();  // Legacy method, will be deprecated
    bool validateConfiguration();  // Legacy method, will be deprecated
    bool validateAndApplyConfig(const BackupConfig& config);  // New method
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

    // Protocol operations
    bool performRegistration();
    bool performReconnection();
    bool sendPublicKey();
    bool transferFile();
    bool transferFileEnhanced(const TransferConfig& config = TransferConfig());
    bool sendFilePacket(const std::string& filename, const std::string& encryptedData,
                       uint32_t originalSize, uint16_t packetNum, uint16_t totalPackets);
    bool verifyCRC(uint32_t serverCRC, uint32_t clientCRC, const std::string& filename);

    // Enhanced transfer methods
    bool transferWithAdaptiveBuffer(size_t fileSize, const std::string& filename, std::ifstream& fileStream);
    bool transferWithMemoryMapping(size_t fileSize, const std::string& filename);
    bool transferWithRobustStreaming(size_t fileSize, const std::string& filename, std::ifstream& fileStream);

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

// Global functions
uint32_t calculateCRC(const uint8_t* data, size_t size);

// Function to run the backup client (called from main.cpp)
bool runBackupClient();
