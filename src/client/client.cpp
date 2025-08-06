// Client.cpp
// Encrypted File Backup System - Enhanced Client Implementation
// Fully compliant with project specifications

#include "../../include/client/client.h"
#include <chrono>
#include <iomanip>

// CRC table for polynomial 0x04C11DB7 (used by Linux cksum)
static const uint32_t crc_table[256] = {
    0x00000000, 0x04C11DB7, 0x09823B6E, 0x0D4326D9,
    0x130476DC, 0x17C56B6B, 0x1A864DB2, 0x1E475005,
    0x2608EDB8, 0x22C9F00F, 0x2F8AD6D6, 0x2B4BCB61,
    0x350C9B64, 0x31CD86D3, 0x3C8EA00A, 0x384FBDBD,
    0x4C11DB70, 0x48D0C6C7, 0x4593E01E, 0x4152FDA9,
    0x5F15ADAC, 0x5BD4B01B, 0x569796C2, 0x52568B75,
    0x6A1936C8, 0x6ED82B7F, 0x639B0DA6, 0x675A1011,
    0x791D4014, 0x7DDC5DA3, 0x709F7B7A, 0x745E66CD,
    0x9823B6E0, 0x9CE2AB57, 0x91A18D8E, 0x95609039,
    0x8B27C03C, 0x8FE6DD8B, 0x82A5FB52, 0x8664E6E5,
    0xBE2B5B58, 0xBAEA46EF, 0xB7A96036, 0xB3687D81,
    0xAD2F2D84, 0xA9EE3033, 0xA4AD16EA, 0xA06C0B5D,
    0xD4326D90, 0xD0F37027, 0xDDB056FE, 0xD9714B49,
    0xC7361B4C, 0xC3F706FB, 0xCEB42022, 0xCA753D95,
    0xF23A8028, 0xF6FB9D9F, 0xFBB8BB46, 0xFF79A6F1,
    0xE13EF6F4, 0xE5FFEB43, 0xE8BCCD9A, 0xEC7DD02D,
    0x34867077, 0x30476DC0, 0x3D044B19, 0x39C556AE,
    0x278206AB, 0x23431B1C, 0x2E003DC5, 0x2AC12072,
    0x128E9DCF, 0x164F8078, 0x1B0CA6A1, 0x1FCDBB16,
    0x018AEB13, 0x054BF6A4, 0x0808D07D, 0x0CC9CDCA,
    0x7897AB07, 0x7C56B6B0, 0x71159069, 0x75D48DDE,
    0x6B93DDDB, 0x6F52C06C, 0x6211E6B5, 0x66D0FB02,
    0x5E9F46BF, 0x5A5E5B08, 0x571D7DD1, 0x53DC6066,
    0x4D9B3063, 0x495A2DD4, 0x44190B0D, 0x40D816BA,
    0xACA5C697, 0xA864DB20, 0xA527FDF9, 0xA1E6E04E,
    0xBFA1B04B, 0xBB60ADFC, 0xB6238B25, 0xB2E29692,
    0x8AAD2B2F, 0x8E6C3698, 0x832F1041, 0x87EE0DF6,
    0x99A95DF3, 0x9D684044, 0x902B669D, 0x94EA7B2A,
    0xE0B41DE7, 0xE4750050, 0xE9362689, 0xEDF73B3E,
    0xF3B06B3B, 0xF771768C, 0xFA325055, 0xFEF34DE2,
    0xC6BCF05F, 0xC27DEDE8, 0xCF3ECB31, 0xCBFFD686,
    0xD5B88683, 0xD1799B34, 0xDC3ABDED, 0xD8FBA05A,
    0x690CE0EE, 0x6DCDFD59, 0x608EDB80, 0x644FC637,
    0x7A089632, 0x7EC98B85, 0x738AAD5C, 0x774BB0EB,
    0x4F040D56, 0x4BC510E1, 0x46863638, 0x42472B8F,
    0x5C007B8A, 0x58C1663D, 0x558240E4, 0x51435D53,
    0x251D3B9E, 0x21DC2629, 0x2C9F00F0, 0x285E1D47,
    0x36194D42, 0x32D850F5, 0x3F9B762C, 0x3B5A6B9B,
    0x0315D626, 0x07D4CB91, 0x0A97ED48, 0x0E56F0FF,
    0x1011A0FA, 0x14D0BD4D, 0x19939B94, 0x1D528623,
    0xF12F560E, 0xF5EE4BB9, 0xF8AD6D60, 0xFC6C70D7,
    0xE22B20D2, 0xE6EA3D65, 0xEBA91BBC, 0xEF68060B,
    0xD727BBB6, 0xD3E6A601, 0xDEA580D8, 0xDA649D6F,
    0xC423CD6A, 0xC0E2D0DD, 0xCDA1F604, 0xC960EBB3,
    0xBD3E8D7E, 0xB9FF90C9, 0xB4BCB610, 0xB07DABA7,
    0xAE3AFBA2, 0xAAFBE615, 0xA7B8C0CC, 0xA379DD7B,
    0x9B3660C6, 0x9FF77D71, 0x92B45BA8, 0x9675461F,
    0x8832161A, 0x8CF30BAD, 0x81B02D74, 0x857130C3,
    0x5D8A9099, 0x594B8D2E, 0x5408ABF7, 0x50C9B640,
    0x4E8EE645, 0x4A4FFBF2, 0x470CDD2B, 0x43CDC09C,
    0x7B827D21, 0x7F436096, 0x7200464F, 0x76C15BF8,
    0x68860BFD, 0x6C47164A, 0x61043093, 0x65C52D24,
    0x119B4BE9, 0x155A565E, 0x18197087, 0x1CD86D30,
    0x029F3D35, 0x065E2082, 0x0B1D065B, 0x0FDC1BEC,
    0x3793A651, 0x3352BBE6, 0x3E119D3F, 0x3AD08088,
    0x2497D08D, 0x2056CD3A, 0x2D15EBE3, 0x29D4F654,
    0xC5A92679, 0xC1683BCE, 0xCC2B1D17, 0xC8EA00A0,
    0xD6AD50A5, 0xD26C4D12, 0xDF2F6BCB, 0xDBEE767C,
    0xE3A1CBC1, 0xE760D676, 0xEA23F0AF, 0xEEE2ED18,
    0xF0A5BD1D, 0xF464A0AA, 0xF9278673, 0xFDE69BC4,
    0x89B8FD09, 0x8D79E0BE, 0x803AC667, 0x84FBDBD0,
    0x9ABC8BD5, 0x9E7D9662, 0x933EB0BB, 0x97FFAD0C,
    0xAFB010B1, 0xAB710D06, 0xA6322BDF, 0xA2F33668,
    0xBCB4666D, 0xB8757BDA, 0xB5365D03, 0xB1F740B4
};

class CRC32Stream {
public:
    CRC32Stream() : crc(0) {}

    void update(const uint8_t* data, size_t size) {
        for (size_t i = 0; i < size; i++) {
            crc = (crc << 8) ^ crc_table[(crc >> 24) ^ data[i]];
        }
    }

    uint32_t finalize(size_t total_size) {
        uint32_t final_crc = crc;
        size_t length = total_size;
        while (length > 0) {
            final_crc = (final_crc << 8) ^ crc_table[(final_crc >> 24) ^ (length & 0xFF)];
            length >>= 8;
        }
        return ~final_crc;
    }

private:
    uint32_t crc;
};

// Implementation of TransferStats methods
TransferStats::TransferStats() : totalBytes(0), transferredBytes(0), lastTransferredBytes(0),
                  currentSpeed(0.0), averageSpeed(0.0), estimatedTimeRemaining(0) {}

void TransferStats::reset() {
    startTime = std::chrono::steady_clock::now();
    lastUpdateTime = startTime;
    transferredBytes = 0;
    lastTransferredBytes = 0;
    currentSpeed = 0.0;
    averageSpeed = 0.0;
    estimatedTimeRemaining = 0;
}

void TransferStats::update(size_t newBytes) {
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

// ============================================================================
// TIMESTAMP LOGGING FOR PROGRESS TRACKING
// ============================================================================

// Log phase with high-resolution timestamp for progress calibration
void log_phase_with_timestamp(const std::string& phase) {
    auto now = std::chrono::high_resolution_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()).count();
    
    // Output format: [PHASE:timestamp] phase_name
    // This format is parsed by RealBackupExecutor for progress tracking
    std::cout << "[PHASE:" << timestamp << "] " << phase << std::endl;
    std::cout.flush(); // Ensure immediate output for subprocess monitoring
}

// ============================================================================
// CLIENT CLASS IMPLEMENTATION
// ============================================================================

 // Constructor
Client::Client() : socket(nullptr), connected(false), rsaPrivate(nullptr),
                   fileRetries(0), crcRetries(0), reconnectAttempts(0),
                   keepAliveEnabled(false), lastError(ErrorType::NONE) {
    std::fill(clientID.begin(), clientID.end(), 0);

    // DISABLED: HTTP API server to prevent port conflicts and simulation mode
    // The real API integration is handled by cyberbackup_api_server.py (Flask)
    // This C++ client should only run in --batch mode via real_backup_executor.py
    extern bool g_batchMode;
    if (!g_batchMode) {
        std::cout << "[INFO] Web server disabled - use cyberbackup_api_server.py for web interface" << std::endl;
        std::cout << "[INFO] This client should be launched via real_backup_executor.py in --batch mode" << std::endl;
    } else {
        std::cout << "[BATCH] HTTP API server disabled in batch mode" << std::endl;
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
    // Clean up HTTP API server
    if (webServer) {
        webServer->stop();
        std::cout << "[GUI] HTTP API server stopped" << std::endl;
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
    
    // Test connection quality with proper error handling
    displayStatus("Testing connection", true, "Verifying server communication...");
    if (!testConnection()) {
        displayStatus("Connection test", false, "Poor connection quality or server not responding properly");
        // Don't fail here, just warn the user
    } else {
        displayStatus("Connection test", true, "Server communication verified");
    }

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
        
        displayStatus("DEBUG: About to call sendPublicKey()", true, "Starting key exchange phase");
        if (!sendPublicKey()) {
            displayError("DEBUG: sendPublicKey() failed", ErrorType::CRYPTO);
            return false;
        }
        displayStatus("DEBUG: sendPublicKey() completed successfully", true, "Key exchange phase done");
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
        
        if (transferFileEnhanced(TransferConfig())) {
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
    log_phase_with_timestamp("COMPLETED");
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

// New method: validate and apply configuration directly (no file I/O)
bool Client::validateAndApplyConfig(const BackupConfig& config) {
    displayStatus("Validating direct configuration", true, "Checking parameters");
    
    // Basic validation using the BackupConfig isValid() method
    if (!config.isValid()) {
        displayError("Invalid configuration provided", ErrorType::CONFIG);
        return false;
    }
    
    // Additional validation for server IP (more thorough than just non-empty check)
    if (config.serverIP.empty() || config.serverIP.length() > 253) {
        displayError("Invalid IP address: " + config.serverIP, ErrorType::CONFIG);
        return false;
    }
    
    // Validate port range
    if (config.serverPort == 0 || config.serverPort > 65535) {
        displayError("Invalid port number: " + std::to_string(config.serverPort), ErrorType::CONFIG);
        return false;
    }
    
    // Validate username length and characters
    if (config.username.empty() || config.username.length() > 100) {
        displayError("Invalid username length (1-100 characters required)", ErrorType::CONFIG);
        return false;
    }
    
    // Validate file exists and get size
    std::ifstream testFile(config.filepath, std::ios::binary);
    if (!testFile.is_open()) {
        displayError("File not found: " + config.filepath, ErrorType::FILE_IO);
        return false;
    }
    
    testFile.seekg(0, std::ios::end);
    std::streampos fileSize = testFile.tellg();
    testFile.close();
    
    if (fileSize == 0) {
        displayError("File is empty: " + config.filepath, ErrorType::FILE_IO);
        return false;
    }
    
    if (fileSize > (4LL * 1024 * 1024 * 1024)) { // 4GB limit
        displayError("File too large (max 4GB): " + config.filepath, ErrorType::FILE_IO);
        return false;
    }
    
    // Apply the validated configuration to the client instance
    serverIP = config.serverIP;
    serverPort = config.serverPort;
    username = config.username;
    filepath = config.filepath;
    stats.totalBytes = static_cast<size_t>(fileSize);
    
    // Display validation success
    displayStatus("Direct configuration applied", true, config.filepath + " (" + formatBytes(stats.totalBytes) + ")");
    displayStatus("Server configuration", true, config.serverIP + ":" + std::to_string(config.serverPort));
    displayStatus("Username configured", true, config.username);
    
    return true;
}

// Load me.info
bool Client::loadMeInfo() {
    std::ifstream file("me.info");
    if (!file.is_open()) {
        return false;
    }
    
    std::string line;
    
    // Line 1: username
    if (!std::getline(file, line) || line != username) {
        return false;
    }
    
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
    try {
        socket = std::make_unique<boost::asio::ip::tcp::socket>(ioContext);
        
        boost::asio::ip::tcp::resolver resolver(ioContext);
        boost::asio::ip::tcp::resolver::results_type endpoints = 
            resolver.resolve(serverIP, std::to_string(serverPort));
        
        displayStatus("Connecting", true, "Establishing TCP connection...");
        
        boost::asio::connect(*socket, endpoints);

        // Verify the connection is actually established
        if (!socket->is_open()) {
            displayError("Socket failed to open", ErrorType::NETWORK);
            return false;
        }

        // Get the actual connected endpoint for verification
        auto localEndpoint = socket->local_endpoint();
        auto remoteEndpoint = socket->remote_endpoint();

        displayStatus("Connection verified", true,
                     "Local: " + localEndpoint.address().to_string() + ":" + std::to_string(localEndpoint.port()) +
                     " -> Remote: " + remoteEndpoint.address().to_string() + ":" + std::to_string(remoteEndpoint.port()));

        // Set socket options for timeouts and keep-alive
        socket->set_option(boost::asio::ip::tcp::no_delay(true));

        // Small delay to ensure connection is fully established
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        connected = true;
        displayStatus("Connected", true, "TCP connection established");
        
        return true;
        
    } catch (const std::exception& e) {        displayError("Connection failed: " + std::string(e.what()), ErrorType::NETWORK);
        socket.reset();
        connected = false;
        
        return false;
    }
}

// Test connection quality
bool Client::testConnection() {
    if (!socket || !socket->is_open()) {
        displayError("Cannot test connection - socket not open", ErrorType::NETWORK);
        return false;
    }
    
    try {
        auto start = std::chrono::steady_clock::now();
        
        // Instead of sending a test request with invalid code,
        // just check if the socket is still connected and responsive
        boost::system::error_code ec;
        size_t available = socket->available(ec);
        
        if (ec) {
            displayError("Connection test failed: " + ec.message(), ErrorType::NETWORK);
            return false;
        }
        
        auto end = std::chrono::steady_clock::now();
        auto latency = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        
        displayStatus("Connection test", true, "Socket responsive (checked in " + std::to_string(latency) + "ms)");
        return true;
        
    } catch (const std::exception& e) {
        displayError("Connection test exception: " + std::string(e.what()), ErrorType::NETWORK);
        return false;
    }
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
}

// Send request to server
bool Client::sendRequest(uint16_t code, const std::vector<uint8_t>& payload) {
    if (!connected || !socket || !socket->is_open()) {
        displayError("Not connected to server", ErrorType::NETWORK);
        return false;
    }
    
    try {
        // FIXED: Use proper struct serialization with explicit endianness handling
        // The Python server expects little-endian format explicitly
        RequestHeader header;
        
        // Client ID (16 bytes) - copy as-is
        std::copy(clientID.begin(), clientID.end(), header.client_id);
        
        // Version (1 byte)
        header.version = CLIENT_VERSION;
        
        // Code and payload_size need explicit little-endian conversion
        uint32_t payload_size_val = static_cast<uint32_t>(payload.size());
        
        // Convert to little-endian if needed (host to little-endian)
        auto hostToLittleEndian16 = [](uint16_t value) -> uint16_t {
            return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF);
        };
        
        auto hostToLittleEndian32 = [](uint32_t value) -> uint32_t {
            return ((value & 0xFF) << 24) | 
                   (((value >> 8) & 0xFF) << 16) |
                   (((value >> 16) & 0xFF) << 8) |
                   ((value >> 24) & 0xFF);
        };
        
        // Check system endianness and convert if necessary
        uint16_t endian_test = 1;
        bool is_little_endian = *reinterpret_cast<uint8_t*>(&endian_test) == 1;
        
        if (is_little_endian) {
            // System is already little-endian, use values directly
            header.code = code;
            header.payload_size = payload_size_val;
        } else {
            // System is big-endian, convert to little-endian
            header.code = hostToLittleEndian16(code);
            header.payload_size = hostToLittleEndian32(payload_size_val);
        }
        
        // Serialize struct to bytes
        std::vector<uint8_t> headerBytes(sizeof(RequestHeader));
        std::memcpy(headerBytes.data(), &header, sizeof(RequestHeader));
        
        // Debug: show header values for important requests
        if (code == REQ_REGISTER || code == REQ_RECONNECT || code == REQ_SEND_PUBLIC_KEY) {
            displayStatus("Debug: Request header", true,
                         "Version=" + std::to_string(CLIENT_VERSION) +
                         ", Code=" + std::to_string(code) +
                         ", PayloadSize=" + std::to_string(payload_size_val));

            // Add hex dump of header bytes for debugging
            std::stringstream hexDump;
            hexDump << "Header hex: ";
            for (size_t i = 0; i < headerBytes.size(); ++i) {
                hexDump << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(headerBytes[i]) << " ";
            }
            displayStatus("Debug: Header bytes", true, hexDump.str());
        }
        
        // Send header
        size_t headerBytesSent = boost::asio::write(*socket, boost::asio::buffer(headerBytes));
        if (headerBytesSent != headerBytes.size()) {
            displayError("Failed to send complete header", ErrorType::NETWORK);
            return false;
        }

        // Send payload if any - use adaptive chunking based on payload size
        if (!payload.empty()) {
            size_t payloadSize = payload.size();
            
            // Dynamic chunk sizing based on payload size for optimal performance
            size_t chunkSize;
            int delayMs = 0;
            
            if (payloadSize <= 1024) {
                // Small payloads (≤1KB): send in one chunk - no overhead
                chunkSize = payloadSize;
            } else if (payloadSize <= 16384) {
                // Medium payloads (1KB-16KB): send in 2-4 chunks of 4KB each
                chunkSize = 4096;
            } else if (payloadSize <= 65536) {
                // Large payloads (16KB-64KB): send in 8KB chunks with minimal delay
                chunkSize = 8192;
                delayMs = 1;
            } else {
                // Very large payloads (>64KB): send in 16KB chunks with 2ms delays
                chunkSize = 16384;
                delayMs = 2;
            }
            
            size_t totalSent = 0;
            while (totalSent < payloadSize) {
                size_t currentChunkSize = std::min(chunkSize, payloadSize - totalSent);
                boost::asio::const_buffer chunk_buffer(payload.data() + totalSent, currentChunkSize);
                
                size_t chunkBytes = boost::asio::write(*socket, chunk_buffer);
                if (chunkBytes != currentChunkSize) {
                    displayError("Failed to send complete payload chunk", ErrorType::NETWORK);
                    return false;
                }
                totalSent += chunkBytes;
                
                // Add delay between chunks only for large payloads and only if not the last chunk
                if (delayMs > 0 && totalSent < payloadSize) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(delayMs));
                }
            }
        }

        // Force flush the socket to ensure data is sent immediately
        ioContext.poll();

        // Debug: confirm data was sent for important requests
        if (code == REQ_REGISTER || code == REQ_RECONNECT || code == REQ_SEND_PUBLIC_KEY) {
            displayStatus("Debug: Data sent", true,
                         "Header: " + std::to_string(headerBytesSent) + " bytes, " +
                         "Payload: " + std::to_string(payload.size()) + " bytes");
        }

        return true;
        
    } catch (const std::exception& e) {
        displayError("Failed to send request: " + std::string(e.what()), ErrorType::NETWORK);
        return false;
    }
}

// Receive response from server with timeout to prevent subprocess hanging
bool Client::receiveResponse(ResponseHeader& header, std::vector<uint8_t>& payload) {
    if (!connected || !socket || !socket->is_open()) {
        displayError("Not connected to server", ErrorType::NETWORK);
        return false;
    }
    
    try {
        boost::system::error_code ec;
        
        // Set socket receive timeout to 25 seconds (less than 30s Python subprocess timeout)
        // This prevents the subprocess from hanging and getting killed
        
        // Windows socket timeout
        #ifdef _WIN32
            DWORD timeout = 25000; // 25 seconds in milliseconds
            if (setsockopt(socket->native_handle(), SOL_SOCKET, SO_RCVTIMEO, 
                          (const char*)&timeout, sizeof(timeout)) != 0) {
                displayStatus("Socket timeout", false, "Could not set receive timeout");
            } else {
                displayStatus("Socket timeout", true, "25s receive timeout set");
            }
        #else
            struct timeval tv;
            tv.tv_sec = 25;
            tv.tv_usec = 0;
            if (setsockopt(socket->native_handle(), SOL_SOCKET, SO_RCVTIMEO, 
                          (const char*)&tv, sizeof(tv)) != 0) {
                displayStatus("Socket timeout", false, "Could not set receive timeout");
            } else {
                displayStatus("Socket timeout", true, "25s receive timeout set");
            }
        #endif
        
        // Synchronously receive header with timeout
        displayStatus("Waiting for server response", true, "Max wait: 25 seconds");
        std::size_t headerBytes = boost::asio::read(*socket, boost::asio::buffer(&header, sizeof(header)), ec);
        
        if (ec) {
            if (ec == boost::asio::error::timed_out || ec == boost::asio::error::operation_aborted) {
                displayError("Timeout waiting for server response - this prevents subprocess kill", ErrorType::NETWORK);
            } else {
                displayError("Failed to receive header: " + ec.message(), ErrorType::NETWORK);
            }
            return false;
        }
        
        if (headerBytes != sizeof(header)) {
            displayError("Failed to receive complete header: got " + std::to_string(headerBytes) + " bytes, expected " + std::to_string(sizeof(header)), ErrorType::NETWORK);
            return false;
        }
        
        // Debug: show raw header bytes received
        uint8_t* rawBytes = reinterpret_cast<uint8_t*>(&header);
        std::stringstream hexStream;
        for (size_t i = 0; i < sizeof(header); i++) {
            hexStream << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(rawBytes[i]) << " ";
        }
        displayStatus("Debug: Raw header bytes", true, hexStream.str());
        
        // Debug: show interpreted header values
        displayStatus("Debug: Response received", true, 
                     "Version=" + std::to_string(header.version) + 
                     ", Code=" + std::to_string(header.code) + 
                     ", PayloadSize=" + std::to_string(header.payload_size));

        // Check version
        if (header.version != SERVER_VERSION) {
            displayError("Invalid server version: " + std::to_string(header.version), ErrorType::PROTOCOL);
            return false;
        }

        // Check for error response
        if (header.code == RESP_ERROR) {
            displayError("Server returned general error", ErrorType::SERVER_ERROR);
            return false;
        }

        // Receive payload if any
        payload.clear();
        if (header.payload_size > 0) {
            payload.resize(header.payload_size);
            
            std::size_t payloadBytes = boost::asio::read(*socket, boost::asio::buffer(payload), ec);
            if (ec || payloadBytes != header.payload_size) {
                displayError("Failed to receive payload: " + (ec ? ec.message() : "incomplete data"), ErrorType::NETWORK);
                return false;
            }
        }

        return true;

    } catch (const std::exception& e) {
        displayError("Failed to receive response: " + std::string(e.what()), ErrorType::NETWORK);
        return false;
    }
}

// Perform registration
bool Client::performRegistration() {
    displayStatus("Starting registration", true, "Using pre-generated RSA keys");

    // RSA keys should already be generated during initialization
    if (!rsaPrivate) {
        displayError("RSA keys not available for registration", ErrorType::CRYPTO);
        return false;
    }
    
    // Prepare registration payload
    std::vector<uint8_t> payload(MAX_NAME_SIZE, 0);
    std::copy(username.begin(), username.end(), payload.begin());
      displayStatus("Sending registration", true, "Username: " + username);
    
    // Debug: show what we're sending
    displayStatus("Debug: Registration packet", true, 
                 "Payload size=" + std::to_string(payload.size()) + 
                 " bytes, Username='" + username + "'");

    // Send registration request
    if (!sendRequest(REQ_REGISTER, payload)) {
        return false;
    }
    
    // Add small delay to ensure server processes request
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // Receive response
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        return false;
    }
    
    if (header.code == RESP_REGISTER_FAIL) {
        displayError("Registration failed: Username already exists", ErrorType::AUTHENTICATION);
        return false;
    }
    
    if (header.code != RESP_REGISTER_OK || responsePayload.size() != CLIENT_ID_SIZE) {
        displayError("Invalid registration response", ErrorType::PROTOCOL);
        return false;
    }
    
    // Store client ID
    std::copy(responsePayload.begin(), responsePayload.end(), clientID.begin());
    
    // Save info
    if (!saveMeInfo() || !savePrivateKey()) {
        displayError("Failed to save registration info", ErrorType::FILE_IO);
        return false;
    }
    
    displayStatus("Registration", true, "New client ID: " + bytesToHex(clientID.data(), 8) + "...");
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
    
    // Prepare payload
    std::vector<uint8_t> payload(MAX_NAME_SIZE + RSA_KEY_SIZE, 0);
    
    // Add username
    std::copy(username.begin(), username.end(), payload.begin());
    
    // Add public key
    char publicKeyBuffer[RSAPublicWrapper::KEYSIZE];
    rsaPrivate->getPublicKey(publicKeyBuffer, RSAPublicWrapper::KEYSIZE);
    std::copy(publicKeyBuffer, publicKeyBuffer + RSAPublicWrapper::KEYSIZE, payload.begin() + MAX_NAME_SIZE);
    
    displayStatus("Sending public key", true, "RSA 1024-bit public key");
    
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

// ============================================================================
// CRITICAL FIXES: Endianness and Validation Utilities
// ============================================================================

uint16_t Client::hostToLittleEndian16(uint16_t value) {
    // Convert 16-bit value from host byte order to little-endian
    return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF);
}

uint32_t Client::hostToLittleEndian32(uint32_t value) {
    // Convert 32-bit value from host byte order to little-endian
    return ((value & 0xFF) << 24) |
           (((value >> 8) & 0xFF) << 16) |
           (((value >> 16) & 0xFF) << 8) |
           ((value >> 24) & 0xFF);
}

bool Client::isSystemLittleEndian() {
    // Check system endianness by examining byte order of a test value
    uint16_t endian_test = 1;
    return *reinterpret_cast<uint8_t*>(&endian_test) == 1;
}

size_t Client::validateAndAlignBufferSize(size_t requestedSize, size_t fileSize) {
    // Validate and align buffer size for optimal performance and server compatibility

    // Ensure minimum buffer size
    if (requestedSize < MIN_BUFFER_SIZE) {
        requestedSize = MIN_BUFFER_SIZE;
    }

    // Ensure buffer doesn't exceed server limits
    if (requestedSize > MAX_SAFE_PACKET_SIZE) {
        requestedSize = MAX_SAFE_PACKET_SIZE;
    }

    // Align to AES block boundaries (16 bytes) for optimal encryption performance
    size_t alignedSize = ((requestedSize + AES_BLOCK_SIZE - 1) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;

    // Final validation against server limits
    if (alignedSize > MAX_SAFE_PACKET_SIZE) {
        alignedSize = (MAX_SAFE_PACKET_SIZE / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    }

    return alignedSize;
}

bool Client::validateFileSizeForTransfer(size_t fileSize) {
    // Validate file size against server limits and system capabilities

    if (fileSize == 0) {
        return false;  // Empty files not supported
    }

    if (fileSize > MAX_SAFE_FILE_SIZE) {
        return false;  // File too large for server
    }

    // Check if we have enough memory for the file (rough estimate)
    // This is a basic check - in production, we'd use more sophisticated memory detection
    if (fileSize > 1024 * 1024 * 1024) {  // 1GB threshold for memory check
        // For very large files, we should implement streaming in the future
        // For now, warn but allow (will be caught by allocation failure)
        std::cout << "[WARNING] Large file detected: " << fileSize << " bytes. May cause memory issues." << std::endl;
    }

    return true;
}

// ============================================================================
// END CRITICAL FIXES: Endianness and Validation Utilities
// ============================================================================

// Transfer file using a streaming approach with proper dynamic buffer management
bool Client::transferFile() {
    // Open the file for reading in binary mode
    std::ifstream fileStream(filepath, std::ios::binary);
    if (!fileStream.is_open()) {
        displayError("File transfer aborted: could not open file " + filepath, ErrorType::FILE_IO);
        return false;
    }

    // Get file size for dynamic buffer calculation
    fileStream.seekg(0, std::ios::end);
    size_t fileSize = fileStream.tellg();
    fileStream.seekg(0, std::ios::beg);

    // Extract filename
    std::string filename = filepath;
    size_t lastSlash = filename.find_last_of("/\\");
    if (lastSlash != std::string::npos) {
        filename = filename.substr(lastSlash + 1);
    }

    // CRITICAL FIX: Enhanced dynamic buffer calculation with validation
    // Buffer size remains constant throughout the entire transfer of this file
    // Realistic file size ranges: tiny configs to 1GB+ media files
    size_t rawBufferSize;
    if (fileSize <= 1024) {                       // ≤1KB files: 1KB buffer
        rawBufferSize = 1024;                     // Tiny files (config, small scripts, .env files)
    } else if (fileSize <= 4 * 1024) {           // 1KB-4KB files: 2KB buffer
        rawBufferSize = 2 * 1024;                 // Small files (small configs, text files, small scripts)
    } else if (fileSize <= 16 * 1024) {          // 4KB-16KB files: 4KB buffer
        rawBufferSize = 4 * 1024;                 // Code files (source files, small documents)
    } else if (fileSize <= 64 * 1024) {          // 16KB-64KB files: 8KB buffer
        rawBufferSize = 8 * 1024;                 // Medium files (larger code, formatted docs, small images)
    } else if (fileSize <= 512 * 1024) {         // 64KB-512KB files: 16KB buffer
        rawBufferSize = 16 * 1024;                // Large docs (PDFs, medium images, compiled binaries)
    } else if (fileSize <= 10 * 1024 * 1024) {   // 512KB-10MB files: 32KB buffer
        rawBufferSize = 32 * 1024;                // Large files (big images, small videos, archives) - L1 cache optimized
    } else {                                      // >10MB files: 64KB buffer
        rawBufferSize = 64 * 1024;                // Huge files (large videos, big archives, datasets up to 1GB+)
    }

    // CRITICAL FIX: Validate and align the calculated buffer size
    size_t dynamicBufferSize = validateAndAlignBufferSize(rawBufferSize, fileSize);

    displayStatus("File details", true, "Name: " + filename + ", Size: " + formatBytes(fileSize));
    displayStatus("Dynamic Buffer Transfer", true,
                 "Buffer size: " + formatBytes(dynamicBufferSize) +
                 " (AES-aligned, server-validated, constant for this file)");

    // Use the validated buffer size for this specific file's entire transfer
    return transferFileWithBuffer(fileStream, filename, fileSize, dynamicBufferSize);
}
// Transfer file with specified buffer size (dynamic per-file buffer sizing)
bool Client::transferFileWithBuffer(std::ifstream& fileStream, const std::string& filename,
                                   size_t fileSize, size_t bufferSize) {
    // CRITICAL FIX: Validate file size and buffer size before proceeding
    if (!validateFileSizeForTransfer(fileSize)) {
        displayError("File size validation failed: " + formatBytes(fileSize), ErrorType::FILE_IO);
        return false;
    }

    // CRITICAL FIX: Validate and align buffer size
    size_t validatedBufferSize = validateAndAlignBufferSize(bufferSize, fileSize);
    if (validatedBufferSize != bufferSize) {
        displayStatus("Buffer size adjusted", true,
                     "From " + formatBytes(bufferSize) + " to " + formatBytes(validatedBufferSize) +
                     " (AES-aligned, server-safe)");
        bufferSize = validatedBufferSize;
    }

    stats.totalBytes = fileSize;
    stats.reset();

    // CRITICAL FIX: Safe memory allocation with error handling
    std::vector<uint8_t> fileData;
    try {
        displayStatus("Memory allocation", true, "Allocating " + formatBytes(fileSize) + " for file data");
        fileData.reserve(fileSize);  // Reserve capacity first
        fileData.resize(fileSize);   // Then resize

        displayStatus("File reading", true, "Reading " + formatBytes(fileSize) + " from disk");
        fileStream.read(reinterpret_cast<char*>(fileData.data()), fileSize);

        if (fileStream.gcount() != static_cast<std::streamsize>(fileSize)) {
            displayError("File read incomplete: expected " + std::to_string(fileSize) +
                        " bytes, got " + std::to_string(fileStream.gcount()), ErrorType::FILE_IO);
            return false;
        }

        fileStream.close();
        displayStatus("File loaded", true, "Successfully loaded into memory");

    } catch (const std::bad_alloc& e) {
        displayError("Memory allocation failed for file size " + formatBytes(fileSize) +
                    ": " + std::string(e.what()), ErrorType::GENERAL);
        return false;
    } catch (const std::exception& e) {
        displayError("File loading failed: " + std::string(e.what()), ErrorType::FILE_IO);
        return false;
    }
    
    // Calculate CRC32 of the original file data  
    uint32_t clientCRC = calculateCRC32(fileData.data(), fileSize);
    
    // Encrypt the file data
    AESWrapper aes(reinterpret_cast<const unsigned char*>(aesKey.c_str()), AES_KEY_SIZE, true);
    std::string encryptedData;
    try {
        encryptedData = aes.encrypt(reinterpret_cast<const char*>(fileData.data()), fileSize);
    } catch (const std::exception& e) {
        displayError("File encryption failed: " + std::string(e.what()), ErrorType::CRYPTO);
        return false;
    }
    
    // CRITICAL FIX: Calculate number of packets with overflow protection
    size_t packetCount = (encryptedData.size() + bufferSize - 1) / bufferSize;

    if (packetCount == 0) {
        displayError("Invalid packet count calculation: encrypted data size " +
                    std::to_string(encryptedData.size()) + ", buffer size " + std::to_string(bufferSize),
                    ErrorType::PROTOCOL);
        return false;
    }

    if (packetCount > UINT16_MAX) {
        displayError("Too many packets required: " + std::to_string(packetCount) +
                    " (max: " + std::to_string(UINT16_MAX) + "). Use larger buffer size.",
                    ErrorType::PROTOCOL);
        return false;
    }

    uint16_t totalPackets = static_cast<uint16_t>(packetCount);

    displayStatus("Transfer Plan", true,
                 "Dynamic packet sizing: " + std::to_string(totalPackets) + " packets, " +
                 formatBytes(bufferSize) + " buffer");
    displayStatus("Encryption overhead", true,
                 "Original: " + formatBytes(fileSize) + " → Encrypted: " + formatBytes(encryptedData.size()) +
                 " (+" + std::to_string(encryptedData.size() - fileSize) + " bytes padding)");
    displayPhase("TRANSFERRING");
    displaySeparator();
    
    // Send file in packets using the calculated buffer size
    size_t dataOffset = 0;
    uint16_t packetNum = 1;
    
    while (dataOffset < encryptedData.size()) {
        size_t chunkSize = std::min(bufferSize, encryptedData.size() - dataOffset);
        std::string chunk = encryptedData.substr(dataOffset, chunkSize);
        
        if (!sendFilePacket(filename, chunk, static_cast<uint32_t>(fileSize), packetNum, totalPackets)) {
            displayError("Failed to send packet " + std::to_string(packetNum), ErrorType::NETWORK);
            return false;
        }
        
        dataOffset += chunkSize;
        packetNum++;
        stats.update(dataOffset);
        
        // Update progress display
        displayProgress("Transferring", stats.transferredBytes, stats.totalBytes);
    }
    
    displaySeparator();
    displayStatus("Transfer Complete", true, "All " + std::to_string(totalPackets) + " packets sent successfully");
    displayStatus("Waiting for server", true, "Server calculating CRC...");
    displayPhase("VERIFYING");
    
    // Wait for CRC response from server
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        displayError("Failed to receive CRC response", ErrorType::NETWORK);
        return false;
    }
    
    if (header.code != RESP_FILE_CRC || responsePayload.size() < 279) {
        displayError("Invalid file transfer response", ErrorType::PROTOCOL);
        return false;
    }
    
    // Extract server CRC from payload
    uint32_t serverCRC;
    std::memcpy(&serverCRC, responsePayload.data() + 275, 4);
    
    // Verify CRC
    return verifyCRC(serverCRC, clientCRC, filename);
}

// Enhanced transfer implementation with adaptive buffer management
bool Client::transferFileEnhanced(const TransferConfig& config) {
    // Open the file for reading in binary mode
    std::ifstream fileStream(filepath, std::ios::binary);
    if (!fileStream.is_open()) {
        displayError("File transfer aborted: could not open file " + filepath, ErrorType::FILE_IO);
        return false;
    }

    // Get file size for buffer calculation
    fileStream.seekg(0, std::ios::end);
    size_t fileSize = fileStream.tellg();
    fileStream.seekg(0, std::ios::beg);
    
    // Extract filename
    std::string filename = filepath;
    size_t lastSlash = filename.find_last_of("/\\");
    if (lastSlash != std::string::npos) {
        filename = filename.substr(lastSlash + 1);
    }

    // CRITICAL FIX: Enhanced dynamic buffer calculation with validation
    // Buffer size remains constant throughout the entire transfer of this file
    // Realistic file size ranges: tiny configs to 1GB+ media files
    size_t rawOptimalBufferSize;
    if (fileSize <= 1024) {                       // ≤1KB files: 1KB buffer
        rawOptimalBufferSize = 1024;              // Tiny files (config, small scripts, .env files)
    } else if (fileSize <= 4 * 1024) {           // 1KB-4KB files: 2KB buffer
        rawOptimalBufferSize = 2 * 1024;          // Small files (small configs, text files, small scripts)
    } else if (fileSize <= 16 * 1024) {          // 4KB-16KB files: 4KB buffer
        rawOptimalBufferSize = 4 * 1024;          // Code files (source files, small documents)
    } else if (fileSize <= 64 * 1024) {          // 16KB-64KB files: 8KB buffer
        rawOptimalBufferSize = 8 * 1024;          // Medium files (larger code, formatted docs, small images)
    } else if (fileSize <= 512 * 1024) {         // 64KB-512KB files: 16KB buffer
        rawOptimalBufferSize = 16 * 1024;         // Large docs (PDFs, medium images, compiled binaries)
    } else if (fileSize <= 10 * 1024 * 1024) {   // 512KB-10MB files: 32KB buffer
        rawOptimalBufferSize = 32 * 1024;         // Large files (big images, small videos, archives) - L1 cache optimized
    } else {                                      // >10MB files: 64KB buffer
        rawOptimalBufferSize = 64 * 1024;         // Huge files (large videos, big archives, datasets up to 1GB+)
    }

    // CRITICAL FIX: Validate and align the calculated buffer size
    size_t optimalBufferSize = validateAndAlignBufferSize(rawOptimalBufferSize, fileSize);

    displayStatus("Enhanced File Transfer", true, "File: " + filename + " (" + formatBytes(fileSize) + ")");
    displayStatus("Transfer Strategy", true, "Dynamic buffer sizing (cache-optimized, server-validated)");
    displayStatus("Dynamic Buffer Transfer", true,
                 "Optimal buffer: " + formatBytes(optimalBufferSize) +
                 " (AES-aligned, constant for this file)");

    // Use working transferFile logic with the validated buffer size
    return transferFileWithBuffer(fileStream, filename, fileSize, optimalBufferSize);
}

bool Client::sendFilePacket(const std::string& filename, const std::string& encryptedData,
                           uint32_t originalSize, uint16_t packetNum, uint16_t totalPackets) {
    // CRITICAL FIX: Create payload with proper endianness handling
    std::vector<uint8_t> payload;

    // Validate inputs first
    uint32_t encryptedSize = static_cast<uint32_t>(encryptedData.size());

    if (encryptedSize == 0) {
        displayError("Cannot send empty encrypted data packet", ErrorType::PROTOCOL);
        return false;
    }

    if (encryptedSize > MAX_SAFE_PACKET_SIZE) {
        displayError("Encrypted packet size exceeds server limits: " +
                    formatBytes(encryptedSize) + " > " + formatBytes(MAX_SAFE_PACKET_SIZE),
                    ErrorType::PROTOCOL);
        return false;
    }

    if (packetNum == 0 || packetNum > totalPackets) {
        displayError("Invalid packet number: " + std::to_string(packetNum) +
                    " (total: " + std::to_string(totalPackets) + ")", ErrorType::PROTOCOL);
        return false;
    }

    // CRITICAL FIX: Convert metadata to little-endian format (same logic as sendRequest)
    bool is_little_endian = isSystemLittleEndian();

    uint32_t le_encryptedSize = is_little_endian ? encryptedSize : hostToLittleEndian32(encryptedSize);
    uint32_t le_originalSize = is_little_endian ? originalSize : hostToLittleEndian32(originalSize);
    uint16_t le_packetNum = is_little_endian ? packetNum : hostToLittleEndian16(packetNum);
    uint16_t le_totalPackets = is_little_endian ? totalPackets : hostToLittleEndian16(totalPackets);

    // Add metadata in little-endian format (as expected by Python server)
    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&le_encryptedSize),
                   reinterpret_cast<uint8_t*>(&le_encryptedSize) + 4);

    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&le_originalSize),
                   reinterpret_cast<uint8_t*>(&le_originalSize) + 4);

    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&le_packetNum),
                   reinterpret_cast<uint8_t*>(&le_packetNum) + 2);

    payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&le_totalPackets),
                   reinterpret_cast<uint8_t*>(&le_totalPackets) + 2);
    
    // Add filename (255 bytes)
    std::vector<uint8_t> filenameBytes(255, 0);
    std::copy(filename.begin(), filename.end(), filenameBytes.begin());
    payload.insert(payload.end(), filenameBytes.begin(), filenameBytes.end());
    
    // Add encrypted data
    payload.insert(payload.end(), encryptedData.begin(), encryptedData.end());
    
    return sendRequest(REQ_SEND_FILE, payload);
}

bool Client::verifyCRC(uint32_t serverCRC, uint32_t clientCRC, const std::string& filename) {
    displayStatus("CRC verification", true, "Server: " + std::to_string(serverCRC) + 
                  ", Client: " + std::to_string(clientCRC));
    
    // Prepare filename payload
    std::vector<uint8_t> payload(255, 0);
    std::copy(filename.begin(), filename.end(), payload.begin());
    
    if (serverCRC == clientCRC) {
        displayStatus("CRC verification", true, "[OK] Checksums match - file integrity confirmed");
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
            sendRequest(REQ_CRC_RETRY, payload);
            
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
            sendRequest(REQ_CRC_ABORT, payload);
            return false;
        }
    }
}

// Generate RSA keys
bool Client::generateRSAKeys() {
    try {
        auto start = std::chrono::steady_clock::now();
        rsaPrivate = new RSAPrivateWrapper();
        auto end = std::chrono::steady_clock::now();

        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        displayStatus("RSA key generation", true, "512-bit keys generated in " + std::to_string(duration) + "ms");
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
    // First, check if the file exists using a simple test
    std::ifstream testFile(path);
    if (!testFile.good()) {
        displayError("File not found: " + path, ErrorType::FILE_IO);
        return {};
    }
    testFile.close();
    
    // Now attempt to open for binary reading
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        displayError("Cannot open file for reading: " + path, ErrorType::FILE_IO);
        return {};
    }
    
    // Get file size
    file.seekg(0, std::ios::end);
    std::streampos fileSize = file.tellg();
    file.seekg(0, std::ios::beg);
    
    // Handle negative file size (error condition)
    if (fileSize < 0) {
        displayError("Cannot determine file size: " + path, ErrorType::FILE_IO);
        file.close();
        return {};
    }
    
    size_t size = static_cast<size_t>(fileSize);
    
    // Check for empty file explicitly - this is a valid condition but should be logged
    if (size == 0) {
        displayError("File is empty: " + path, ErrorType::FILE_IO);
        file.close();
        return {};  // Return empty vector but calling code can check error details
    }
    
    // Check for extremely large files
    if (size > (4LL * 1024 * 1024 * 1024)) { // 4GB limit
        displayError("File too large (max 4GB): " + path + " (" + formatBytes(size) + ")", ErrorType::FILE_IO);
        file.close();
        return {};
    }
    
    std::vector<uint8_t> data(size);
    
    // Read in chunks for better performance
    size_t bytesRead = 0;
    while (bytesRead < size) {
        size_t toRead = std::min(OPTIMAL_BUFFER_SIZE, size - bytesRead);
        file.read(reinterpret_cast<char*>(data.data() + bytesRead), toRead);
        
        if (file.fail() && !file.eof()) {
            displayError("Failed to read file data at offset " + std::to_string(bytesRead) + ": " + path, ErrorType::FILE_IO);
            file.close();
            return {};
        }
        
        bytesRead += file.gcount();
    }
    
    file.close();
    
    // Verify we read the expected amount
    if (bytesRead != size) {
        displayError("Incomplete file read: expected " + std::to_string(size) + 
                    " bytes, got " + std::to_string(bytesRead) + " bytes from " + path, ErrorType::FILE_IO);
        return {};
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

// Linux cksum compatible CRC implementation
uint32_t calculateCRC(const uint8_t* data, size_t size) {
    uint32_t crc = 0x00000000;

    // Process file data
    for (size_t i = 0; i < size; i++) {
        crc = (crc << 8) ^ crc_table[(crc >> 24) ^ data[i]];
    }

    // Process file length
    size_t length = size;
    while (length > 0) {
        crc = (crc << 8) ^ crc_table[(crc >> 24) ^ (length & 0xFF)];
        length >>= 8;
    }

    // Final inversion
    return ~crc;
}

// Calculate CRC32 using consolidated implementation
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
    std::tm tm_buf;
    localtime_s(&tm_buf, &time_t);
    std::stringstream ss;
    ss << std::put_time(&tm_buf, "%H:%M:%S");
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
#else
    std::cout << "[" << getCurrentTimestamp() << "] ";
    std::cout << (success ? "[OK] " : "[FAIL] ") << operation;
    if (!details.empty()) {
        std::cout << " - " << details;
    }
    std::cout << std::endl;
#endif
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
    for (int i = 0; i < pos; i++) std::cout << "#";
    
    SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN);
    for (int i = pos; i < barWidth; i++) std::cout << ".";
    
    SetConsoleTextAttribute(hConsole, savedAttributes);
    std::cout << "] " << std::setw(3) << percentage << "% (" 
              << formatBytes(current) << "/" << formatBytes(total) << ")\r";
    std::cout.flush();
    
    if (current >= total) {
        std::cout << std::endl;
    }
#else
    std::cout << "\r" << operation << " " << percentage << "% (" 
              << formatBytes(current) << "/" << formatBytes(total) << ")";
    std::cout.flush();
    if (current >= total) {
        std::cout << std::endl;
    }
#endif
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
    std::cout << "\n╔════════════════════════════════════════════╗\n";
    std::cout << "║     ENCRYPTED FILE BACKUP CLIENT v1.0      ║\n";
    std::cout << "╚════════════════════════════════════════════╝\n";
    
    SetConsoleTextAttribute(hConsole, savedAttributes);
    std::cout << "  Build Date: " << __DATE__ << " " << __TIME__ << "\n";
    std::cout << "  Protocol Version: " << static_cast<int>(CLIENT_VERSION) << "\n";
    std::cout << "  Encryption: RSA-1024 + AES-256-CBC\n\n";
#else
    std::cout << "\n============================================\n";
    std::cout << "     ENCRYPTED FILE BACKUP CLIENT v1.0      \n";
    std::cout << "============================================\n";
    std::cout << "  Build Date: " << __DATE__ << " " << __TIME__ << "\n";
    std::cout << "  Protocol Version: " << static_cast<int>(CLIENT_VERSION) << "\n";
    std::cout << "  Encryption: RSA-1024 + AES-256-CBC\n\n";
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
}

void Client::displaySeparator() {
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, FOREGROUND_INTENSITY);
    std::cout << std::string(60, '─') << std::endl;
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
#else
    std::cout << "\n> " << phase << std::endl;
    displaySeparator();
#endif
}

void Client::displaySummary() {
    auto endTime = std::chrono::steady_clock::now();
    auto totalDuration = std::chrono::duration_cast<std::chrono::seconds>(endTime - operationStartTime).count();
    
    displaySeparator();
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, FOREGROUND_GREEN | FOREGROUND_INTENSITY);
    std::cout << "[SUCCESS] BACKUP COMPLETED SUCCESSFULLY\n";
    SetConsoleTextAttribute(hConsole, savedAttributes);
#else
    std::cout << "[SUCCESS] BACKUP COMPLETED SUCCESSFULLY\n";
#endif
    
    std::cout << "\nTransfer Summary:\n";
    std::cout << "  File: " << filepath << "\n";
    std::cout << "  Size: " << formatBytes(stats.totalBytes) << "\n";
    std::cout << "  Duration: " << formatDuration(static_cast<int>(totalDuration)) << "\n";
    std::cout << "  Average Speed: " << formatBytes(static_cast<size_t>(stats.averageSpeed)) << "/s\n";
    std::cout << "  Server: " << serverIP << ":" << serverPort << "\n";
    std::cout << "  Timestamp: " << getCurrentTimestamp() << "\n";
    displaySeparator();
}

// GUI-triggered backup operation (doesn't shut down WebServer)
bool Client::runBackupOperation() {
    try {
        // Re-read configuration in case it changed (legacy mode)
        if (!readTransferInfo()) {
            return false;
        }

        if (!validateConfiguration()) {
            return false;
        }

        // Run the backup operation
        return run();

    } catch (const std::exception& e) {
        displayError("Backup operation failed: " + std::string(e.what()), ErrorType::GENERAL);
        return false;
    } catch (...) {
        displayError("Unknown error in backup operation", ErrorType::GENERAL);
        return false;
    }
}

// New backup operation with direct configuration (eliminates transfer.info dependency)
bool Client::runBackupOperation(const BackupConfig& config) {
    try {
        // Validate and apply the provided configuration
        if (!validateAndApplyConfig(config)) {
            return false;
        }

        displayStatus("Configuration applied directly", true, 
            "Server: " + config.serverIP + ":" + std::to_string(config.serverPort) + 
            ", User: " + config.username + ", File: " + config.filepath);

        // Run the backup operation
        return run();

    } catch (const std::exception& e) {
        displayError("Backup operation failed: " + std::string(e.what()), ErrorType::GENERAL);
        return false;
    } catch (...) {
        displayError("Unknown error in backup operation", ErrorType::GENERAL);
        return false;
    }
}

// Function to run the backup client (called from main.cpp)
bool runBackupClient() {
    try {
        Client client;

        if (!client.initialize()) {
            return false;
        }

        return client.run();

    } catch (const std::exception& e) {
        std::cerr << "Error in runBackupClient: " << e.what() << std::endl;
        return false;
    } catch (...) {
        std::cerr << "Unknown error in runBackupClient" << std::endl;
        return false;
    }
}