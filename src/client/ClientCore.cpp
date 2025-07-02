// ClientCore.cpp
// Enhanced Client Core Implementation - Networking & Protocol Operations
// Contains networking, connection management, and protocol handling

#include "../../include/client/ClientCore.h"

// === CONSTRUCTOR & DESTRUCTOR ===

Client::Client() : socket(nullptr), connected(false), rsaPrivate(nullptr), 
                   fileRetries(0), crcRetries(0), reconnectAttempts(0),
                   keepAliveEnabled(false), lastError(ErrorType::NONE),
                   interactiveMode(false), pendingServerPort(0) {
    std::fill(clientID.begin(), clientID.end(), 0);

    // WebSocket server removed - using HTML GUI instead

#ifdef _WIN32
    hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
    GetConsoleScreenBufferInfo(hConsole, &consoleInfo);
    savedAttributes = consoleInfo.wAttributes;
#endif
}

Client::~Client() {
    keepAliveEnabled = false;
    closeConnection();
    if (rsaPrivate) {
        delete rsaPrivate;
    }
    // WebSocket server cleanup removed
#ifdef _WIN32
    SetConsoleTextAttribute(hConsole, savedAttributes);
#endif
}

// === CORE LIFECYCLE METHODS ===

bool Client::initialize() {
    operationStartTime = std::chrono::steady_clock::now();
    // Display functions removed - using HTML GUI
    
    std::cout << "[PHASE] Initialization" << std::endl;
    
    std::cout << "[INFO] System initialization: Starting client v1.0" << std::endl;
    
    if (!readTransferInfo()) {
        return false;
    }
    
    if (!validateConfiguration()) {
        return false;
    }

    // Pre-generate or load RSA keys during initialization to avoid delays during registration
    std::cout << "[INFO] Preparing RSA keys: 1024-bit key pair for encryption" << std::endl;

    // Try to load existing keys first to avoid regeneration
    if (loadPrivateKey()) {
        std::cout << "[INFO] RSA keys loaded: Using cached key pair" << std::endl;
    } else {
        std::cout << "[INFO] Generating RSA keys: Creating new 1024-bit key pair..." << std::endl;
        if (!generateRSAKeys()) {
            return false;
        }
        // Save the generated keys for future use
        savePrivateKey();
    }

    std::cout << "[INFO] Initialization complete: Ready to connect" << std::endl;
    return true;
}

bool Client::run() {
    std::cout << "[PHASE] Connection Setup" << std::endl;
    
    std::cout << "[INFO] Connecting to server: " << serverIP << ":" << serverPort << std::endl;
    
    // Try to connect with retries
    bool connectedSuccessfully = false;
    for (int attempt = 1; attempt <= 3 && !connectedSuccessfully; attempt++) {
        if (attempt > 1) {
            std::cout << "[INFO] Connection attempt: Retry " << attempt << " of 3" << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(RECONNECT_DELAY_MS));
        }
        
        if (connectToServer()) {
            connectedSuccessfully = true;
        }
    }
    
    if (!connectedSuccessfully) {
        std::cerr << "[ERROR] Failed to connect after 3 attempts" << std::endl;
        return false;
    }
    
    std::cout << "[INFO] Connection established" << std::endl;
    
    // Enable keep-alive for long transfers
    enableKeepAlive();
    
    std::cout << "[PHASE] Authentication" << std::endl;
    
    // Check if we have existing registration
    bool hasRegistration = loadMeInfo();
    
    if (hasRegistration) {
        std::cout << "[INFO] Client credentials: Found existing registration" << std::endl;
        std::cout << "[INFO] Attempting reconnection: Client: " << username << std::endl;
        
        // Load private key
        if (!loadPrivateKey()) {
            std::cerr << "[ERROR] Loading private key: Key not found" << std::endl;
            hasRegistration = false;
        } else {
            // Try reconnection
            if (!performReconnection()) {
                std::cout << "[WARNING] Reconnection: Server rejected - will register as new client" << std::endl;
                hasRegistration = false;
            }
        }
    }
    
    if (!hasRegistration) {
        std::cout << "[INFO] Registering new client: " << username << std::endl;
        
        if (!performRegistration()) {
            return false;
        }
        
        if (!sendPublicKey()) {
            return false;
        }
    }
    
    std::cout << "[PHASE] File Transfer" << std::endl;
    
    // Transfer the file with retry logic
    bool transferSuccess = false;
    fileRetries = 0;
    
    while (fileRetries < MAX_RETRIES && !transferSuccess) {
        if (fileRetries > 0) {
            std::cout << "[WARNING] File transfer: Retrying (attempt " << (fileRetries + 1) << " of " << MAX_RETRIES << ")" << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }
        
        if (transferFile()) {
            transferSuccess = true;
        } else {
            fileRetries++;
        }
    }
    
    if (!transferSuccess) {
        std::cerr << "[ERROR] File transfer failed after " << MAX_RETRIES << " attempts" << std::endl;
        return false;
    }
    
    std::cout << "[PHASE] Transfer Complete" << std::endl;
    std::cout << "[INFO] Transfer completed successfully" << std::endl;
    
    return true;
}

// === NETWORKING OPERATIONS ===

bool Client::connectToServer() {
    std::cout << "[DEBUG] Attempting to connect to server at " << serverIP << ":" << serverPort << std::endl;
    try {
        socket = std::make_unique<boost::asio::ip::tcp::socket>(ioContext);
        
        boost::asio::ip::tcp::resolver resolver(ioContext);
        boost::asio::ip::tcp::resolver::results_type endpoints = 
            resolver.resolve(serverIP, std::to_string(serverPort));
        
        std::cout << "[INFO] Connecting: Resolving " << serverIP << ":" << serverPort << std::endl;
        
        // Connect with proper error handling
        boost::system::error_code connectError;
        boost::asio::connect(*socket, endpoints, connectError);
        
        if (connectError) {
            std::cerr << "[ERROR] Connection failed: " << connectError.message() << " (Code: " << connectError.value() << ")" << std::endl;
            return false;
        }

        // Verify the connection is actually established
        if (!socket->is_open()) {
            std::cerr << "[ERROR] Socket failed to open after connect" << std::endl;
            return false;
        }

        // Get the actual connected endpoint for verification
        auto localEndpoint = socket->local_endpoint();
        auto remoteEndpoint = socket->remote_endpoint();

        std::cout << "[INFO] Connection verified - Local: " << localEndpoint.address().to_string() << ":" << localEndpoint.port() << " -> Remote: " << remoteEndpoint.address().to_string() << ":" << remoteEndpoint.port() << std::endl;

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
        std::cout << "[INFO] Connected: TCP connection established and configured" << std::endl;
        
        // GUI update removed - using HTML GUI
        
        std::cout << "[DEBUG] Connected to server successfully." << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Connection failed: " << e.what() << std::endl;
        socket.reset();
        connected = false;
        
        // GUI update removed - using HTML GUI
        
        std::cerr << "[ERROR] Failed to connect to server." << std::endl;
        return false;
    }
}

void Client::closeConnection() {
    if (socket && socket->is_open()) {
        try {
            socket->close();
        } catch (const std::exception&) {
            // Ignore errors during close
        }
    }
    socket.reset();
    connected = false;
    
    // GUI update removed - using HTML GUI
}

bool Client::testConnection() {
    auto start = std::chrono::steady_clock::now();
    
    // Send a small test request (empty payload)
    if (!sendRequest(0, {})) {
        return false;
    }
    
    auto end = std::chrono::steady_clock::now();
    auto latency = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    std::cout << "[INFO] Connection test: Latency: " << latency << "ms" << std::endl;
    return latency < 1000; // Good if under 1 second
}

void Client::enableKeepAlive() {
    if (socket && socket->is_open()) {
        try {
            socket->set_option(boost::asio::socket_base::keep_alive(true));
            keepAliveEnabled = true;
            std::cout << "[INFO] Keep-alive: Enabled for stable connection" << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "[WARNING] Keep-alive: Could not enable: " << e.what() << std::endl;
        }
    }
}

// === PROTOCOL OPERATIONS ===

bool Client::sendRequest(uint16_t code, const std::vector<uint8_t>& payload) {
    // Basic connection validation
    if (!connected || !socket || !socket->is_open()) {
        std::cerr << "[ERROR] Client not connected to server" << std::endl;
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
            std::cout << "[INFO] Sending request: Code=" << code << ", PayloadSize=" << payload_size_val << ", TotalBytes=" << completeMessage.size() << std::endl;
        }
        
        // ATOMIC TRANSMISSION: Send complete message in one operation
        boost::system::error_code sendError;
        size_t totalBytesSent = boost::asio::write(*socket, boost::asio::buffer(completeMessage), sendError);
        
        // Check for transmission errors
        if (sendError) {
            std::cerr << "[ERROR] Socket write failed: " << sendError.message() << std::endl;
            connected = false;
            return false;
        }
        
        // Verify complete transmission
        if (totalBytesSent != completeMessage.size()) {
            std::cerr << "[ERROR] Incomplete write: " << totalBytesSent << "/" << completeMessage.size() << " bytes" << std::endl;
            connected = false;
            return false;
        }
        
        // Success confirmation for critical requests
        if (code == REQ_REGISTER || code == REQ_RECONNECT || code == REQ_SEND_PUBLIC_KEY) {
            std::cout << "[INFO] Request sent successfully: " << totalBytesSent << " bytes transmitted" << std::endl;
        }
        
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Send request failed: " << e.what() << std::endl;
        connected = false;
        return false;
    }
}

bool Client::receiveResponse(ResponseHeader& header, std::vector<uint8_t>& payload) {
    if (!connected || !socket || !socket->is_open()) {
        std::cerr << "[ERROR] Not connected to server" << std::endl;
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
        std::cout << "[DEBUG] Response received: Version=" << header.version << ", Code=" << header.code << ", PayloadSize=" << header.payload_size << std::endl;
        
        // Check version
        if (header.version != SERVER_VERSION) {
            std::cerr << "[ERROR] Protocol version mismatch - Server: " << header.version << ", Client expects: " << SERVER_VERSION << std::endl;
            return false;
        }
        
        // Check for error response
        if (header.code == RESP_GENERIC_SERVER_ERROR) {
            std::cerr << "[ERROR] Server returned general error" << std::endl;
            return false;
        }
        
        // Validate payload size
        if (header.payload_size > MAX_PACKET_SIZE) {
            std::cerr << "[ERROR] Invalid payload size: " << header.payload_size << std::endl;
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
        std::cerr << "[ERROR] Failed to receive response: " << e.what() << std::endl;
        return false;
    }
}

bool Client::performRegistration() {
    std::cout << "[INFO] Starting registration: Using pre-generated RSA keys" << std::endl;

    // RSA keys should already be generated during initialization
    if (!rsaPrivate) {
        std::cerr << "[ERROR] RSA keys not available for registration" << std::endl;
        return false;
    }
    
    // Prepare registration payload - EXACTLY 255 bytes as expected by server
    std::vector<uint8_t> payload(MAX_NAME_SIZE, 0);  // Initialize all bytes to 0
    
    // Validate username length
    if (username.length() > MAX_NAME_SIZE - 1) {
        std::cerr << "[ERROR] Username too long: " << username.length() << " bytes (max: " << (MAX_NAME_SIZE - 1) << ")" << std::endl;
        return false;
    }
    
    // Copy username to payload (null-terminated, zero-padded)
    std::copy(username.begin(), username.end(), payload.begin());
    // Ensure null termination (redundant but explicit)
    payload[username.length()] = 0;
    
    std::cout << "[INFO] Sending registration: Username: " << username << std::endl;
    
    // Debug: show exact payload construction
    std::cout << "[DEBUG] Registration payload: Size=" << payload.size() << " bytes, Username='" << username << "' (" << username.length() << " chars), Null-terminated and zero-padded" << std::endl;

    // Send registration request
    if (!sendRequest(REQ_REGISTER, payload)) {
        std::cerr << "[ERROR] Failed to send registration request" << std::endl;
        return false;
    }
    
    // Receive response
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        std::cerr << "[ERROR] Failed to receive registration response" << std::endl;
        return false;
    }
    
    // Process response
    if (header.code == RESP_REG_FAIL) {
        std::cerr << "[ERROR] Registration failed: Username already exists" << std::endl;
        return false;
    }
    
    if (header.code != RESP_REG_OK || responsePayload.size() != CLIENT_ID_SIZE) {
        std::cerr << "[ERROR] Invalid registration response - Code: " << header.code << ", Expected: " << RESP_REG_OK << ", Payload size: " << responsePayload.size() << std::endl;
        return false;
    }
    
    // Success! Store client ID and save registration info
    std::copy(responsePayload.begin(), responsePayload.end(), clientID.begin());
    
    // Save info
    if (!saveMeInfo() || !savePrivateKey()) {
        std::cerr << "[ERROR] Failed to save registration info" << std::endl;
        return false;
    }
    
    std::cout << "[INFO] Registration successful: Client ID: " << bytesToHex(clientID.data(), 8) << "..." << std::endl;
    
    std::cout << "[DEBUG] Registration completed successfully" << std::endl;
    return true;
}

bool Client::performReconnection() {
    // Prepare reconnection payload
    std::vector<uint8_t> payload(MAX_NAME_SIZE, 0);
    std::copy(username.begin(), username.end(), payload.begin());
    
    std::cout << "[INFO] Sending reconnection: Client ID: " << bytesToHex(clientID.data(), 8) << "..." << std::endl;
    
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
        std::cerr << "[ERROR] Invalid reconnection response" << std::endl;
        return false;
    }
    
    // Extract encrypted AES key
    std::vector<uint8_t> encryptedKey(responsePayload.begin() + CLIENT_ID_SIZE, responsePayload.end());
    
    std::cout << "[INFO] Decrypting AES key: Using stored RSA private key" << std::endl;
    
    // Decrypt AES key
    if (!decryptAESKey(encryptedKey)) {
        return false;
    }
    
    std::cout << "[INFO] Reconnection: Successfully authenticated" << std::endl;
    return true;
}

// === SOCKET MANAGEMENT & RECOVERY ===

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
    std::cout << "[INFO] Connection recovery: Attempting to reconnect..." << std::endl;
    
    if (connectToServer()) {
        std::cout << "[INFO] Connection recovery: Successfully reconnected" << std::endl;
        std::cout << "[DEBUG] Connection recovery successful" << std::endl;
        return true;
    } else {
        std::cerr << "[ERROR] Connection recovery failed" << std::endl;
        std::cout << "[DEBUG] Connection recovery failed" << std::endl;
        return false;
    }
}

// === GLOBAL FUNCTION ===

bool runBackupClient() {
    std::cout << "=== ENCRYPTED BACKUP CLIENT DEBUG MODE ===" << std::endl;
    std::cout << "Console application started!" << std::endl;
    std::cout << "Starting client with console output..." << std::endl;

    Client client;
    if (!client.initialize()) {
        std::cerr << "Fatal: Client initialization failed" << std::endl;
        return false;
    }

    if (!client.run()) {
        std::cerr << "Fatal: File backup failed" << std::endl;
        return false;
    }

    std::cout << "\nBackup completed successfully!" << std::endl;
    return true;
}