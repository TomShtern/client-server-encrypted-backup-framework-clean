// ClientCore.cpp
// Enhanced Client Core Implementation - Networking & Protocol Operations
// Contains networking, connection management, and protocol handling

#include "../../include/client/ClientCore.h"
#include "../../include/client/ClientGUIHelpers.h"

// === CONSTRUCTOR & DESTRUCTOR ===

Client::Client() : socket(nullptr), connected(false), rsaPrivate(nullptr), 
                   fileRetries(0), crcRetries(0), reconnectAttempts(0),
                   keepAliveEnabled(false), lastError(ErrorType::NONE),
                   interactiveMode(false), pendingServerPort(0) {
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

// === CORE LIFECYCLE METHODS ===

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

// === NETWORKING OPERATIONS ===

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
    
    // Update GUI connection status (optional)
    try {
        ClientGUIHelpers::updateConnectionStatus(false);
    } catch (...) {
        // GUI update failed - continue without GUI
    }
}

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

// === PROTOCOL OPERATIONS ===

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

// === GLOBAL FUNCTION ===

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
#ifdef _WIN32
            // Show error notification via GUI if available
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

        return true;
    } catch (const std::exception& e) {
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
        return false;
    } catch (...) {
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