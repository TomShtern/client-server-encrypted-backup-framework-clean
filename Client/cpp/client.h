#pragma once

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>
#include <array>
#include <deque>
#include <cstring>
#include <algorithm>
#include <chrono>
#include <thread>
#include <atomic>
#include <memory>
#include <ctime>
#include <cassert>
#include <cmath>

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
#include "../deps/AESWrapper.h"
#include "../deps/Base64Wrapper.h"
#include "../deps/RSAWrapper.h"
#include "WebServerBackend.h"

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

// Server limits (must match server-side constraints)
constexpr size_t MAX_SAFE_PACKET_SIZE = 16 * 1024 * 1024;  // 16MB - matches server MAX_PAYLOAD_READ_LIMIT
constexpr size_t MAX_SAFE_FILE_SIZE = 4ULL * 1024 * 1024 * 1024;  // 4GB - matches server MAX_ORIGINAL_FILE_SIZE

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

// Professional Dynamic Buffer Management with Network Performance Isolation
class ProperDynamicBufferManager {
private:
    // Buffer pool - pre-allocated, AES-aligned buffers to eliminate allocation overhead
    static constexpr size_t BUFFER_POOL_SIZES[] = {1024, 2048, 4096, 8192, 16384, 32768, 65536}; // 1KB to 64KB
    static constexpr size_t BUFFER_POOL_COUNT = sizeof(BUFFER_POOL_SIZES) / sizeof(size_t);
    
    std::vector<std::vector<uint8_t>> buffer_pool;
    size_t current_buffer_index;
    
    // Network performance tracking (isolated from encryption performance)
    std::deque<double> network_throughput_mbps;    // Megabits per second
    std::deque<std::chrono::milliseconds> encryption_times;
    
    // Adaptation control
    size_t packets_since_last_adaptation;
    size_t total_packets_sent;
    std::chrono::steady_clock::time_point last_adaptation_time;
    
    // Stability and hysteresis parameters
    static constexpr size_t MIN_PACKETS_FOR_ADAPTATION = 8;     // Collect data before adapting
    static constexpr size_t MIN_SECONDS_BETWEEN_ADAPTATIONS = 5; // Prevent rapid changes
    static constexpr double THROUGHPUT_IMPROVEMENT_THRESHOLD = 1.15; // 15% improvement to grow
    static constexpr double THROUGHPUT_DEGRADATION_THRESHOLD = 0.80; // 20% degradation to shrink
    static constexpr size_t THROUGHPUT_HISTORY_SIZE = 10;       // Samples for moving average
    
    // Performance analysis
    double calculateAverageThroughput() const;
    bool shouldGrowBuffer() const;
    bool shouldShrinkBuffer() const;
    void adaptBufferSize();

public:
    ProperDynamicBufferManager(size_t initial_buffer_size = 8192);
    
    // Get current buffer reference (zero-copy)
    std::vector<uint8_t>& getCurrentBuffer() { return buffer_pool[current_buffer_index]; }
    const std::vector<uint8_t>& getCurrentBuffer() const { return buffer_pool[current_buffer_index]; }
    
    // Get current buffer size for reads
    size_t getCurrentBufferSize() const { return BUFFER_POOL_SIZES[current_buffer_index]; }
    
    // Calculate total packets for protocol compliance
    uint16_t calculateTotalPackets(size_t file_size) const {
        size_t packets = (file_size + getCurrentBufferSize() - 1) / getCurrentBufferSize();
        return static_cast<uint16_t>(std::min(packets, static_cast<size_t>(UINT16_MAX)));
    }
    
    // Record performance metrics and trigger adaptation if needed
    void recordPacketMetrics(size_t bytes_sent, 
                           std::chrono::steady_clock::time_point send_start,
                           std::chrono::steady_clock::time_point send_end,
                           std::chrono::steady_clock::time_point encrypt_start,
                           std::chrono::steady_clock::time_point encrypt_end,
                           bool network_success);
    
    // Get performance diagnostics
    struct PerformanceStats {
        double current_throughput_mbps;
        double average_throughput_mbps;
        size_t current_buffer_size;
        size_t current_buffer_index;
        size_t total_adaptations;
        std::chrono::milliseconds avg_encryption_time;
    };
    PerformanceStats getPerformanceStats() const;
    
    // Reset for new transfer
    void reset(size_t suggested_initial_size = 8192);
    
private:
    size_t total_adaptations;
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
    bool transferFileWithBuffer(std::ifstream& fileStream, const std::string& filename, 
                               size_t fileSize, size_t bufferSize);
    bool sendFilePacket(const std::string& filename, const std::string& encryptedData,
                       uint32_t originalSize, uint16_t packetNum, uint16_t totalPackets);
    bool verifyCRC(uint32_t serverCRC, uint32_t clientCRC, const std::string& filename);

    // Enhanced transfer methods (removed broken implementations)

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

    // Endianness and validation utilities (CRITICAL FIXES)
    static uint16_t hostToLittleEndian16(uint16_t value);
    static uint32_t hostToLittleEndian32(uint32_t value);
    static bool isSystemLittleEndian();
    static size_t validateAndAlignBufferSize(size_t requestedSize, size_t fileSize);
    static bool validateFileSizeForTransfer(size_t fileSize);



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
