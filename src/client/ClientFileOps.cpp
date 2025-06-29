// ClientFileOps.cpp
// Enhanced Client File Operations
// Contains file I/O, configuration management, transfer operations, and data validation

#include "../../include/client/ClientCore.h"

// === CONFIGURATION MANAGEMENT ===

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
    } catch (const std::exception& e) {
        displayError("Invalid port number: " + std::string(e.what()), ErrorType::CONFIG);
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
    displayStatus("Server config", true, serverIP + ":" + std::to_string(serverPort));
    displayStatus("User config", true, username);
    displayStatus("File config", true, filepath);
    
    return true;
}

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

// === DATA PERSISTENCE ===

bool Client::loadMeInfo() {
    std::ifstream file("me.info");
    if (!file.is_open()) {
        return false;
    }
    
    std::string line;
    
    // Line 1: username (stored for reference, but not validated)
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
    displayStatus("Stored username", true, storedUsername);
    
    // Line 3: private key base64 (we'll load separately)
    return true;
}

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
    
    file.close();
    
    if (file.good()) {
        displayStatus("Client info saved", true, "me.info created");
        displayStatus("Saved data", true, "Username: " + username + ", ID: " + hexId.substr(0, 8) + "...");
        return true;
    } else {
        displayError("Failed to write me.info", ErrorType::FILE_IO);
        return false;
    }
}

// === FILE OPERATIONS ===

std::vector<uint8_t> Client::readFile(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        displayError("Cannot open file: " + path, ErrorType::FILE_IO);
        return {};
    }
    
    file.seekg(0, std::ios::end);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    
    if (size == 0) {
        displayError("File is empty: " + path, ErrorType::FILE_IO);
        return {};
    }
    
    std::vector<uint8_t> data(size);
    
    // Read in chunks for better performance
    size_t bytesRead = 0;
    while (bytesRead < size) {
        size_t toRead = std::min(OPTIMAL_BUFFER_SIZE, size - bytesRead);
        file.read(reinterpret_cast<char*>(data.data() + bytesRead), toRead);
        
        std::streamsize actuallyRead = file.gcount();
        if (actuallyRead <= 0) {
            displayError("Failed to read file data at offset " + std::to_string(bytesRead), ErrorType::FILE_IO);
            return {};
        }
        
        bytesRead += actuallyRead;
    }
    
    file.close();
    
    if (bytesRead != size) {
        displayError("Incomplete file read: " + std::to_string(bytesRead) + "/" + std::to_string(size) + " bytes", ErrorType::FILE_IO);
        return {};
    }
    
    displayStatus("File read", true, path + " (" + formatBytes(size) + ")");
    return data;
}

// === FILE TRANSFER OPERATIONS ===

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
        displayError("File encryption failed", ErrorType::CRYPTO);
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
            displayError("Failed to send packet " + std::to_string(packet) + "/" + std::to_string(totalPackets), ErrorType::NETWORK);
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
        displayError("Failed to receive CRC response", ErrorType::NETWORK);
        return false;
    }
    
    if (header.code != RESP_FILE_CRC) {
        displayError("Invalid file transfer response code: " + std::to_string(header.code) + 
                    ", expected: " + std::to_string(RESP_FILE_CRC), ErrorType::PROTOCOL);
        return false;
    }
    
    if (responsePayload.size() < 279) {
        displayError("Invalid file transfer response payload size: " + std::to_string(responsePayload.size()) + 
                    " bytes, expected >= 279", ErrorType::PROTOCOL);
        return false;
    }
    
    // Extract CRC (at offset 275, 4 bytes)
    uint32_t serverCRC;
    std::memcpy(&serverCRC, responsePayload.data() + 275, 4);
    
    // Verify CRC
    return verifyCRC(serverCRC, fileData, filename);
}

bool Client::sendFilePacket(const std::string& filename, const std::string& encryptedData,
                           uint32_t originalSize, uint16_t packetNum, uint16_t totalPackets) {
    try {
        // Create payload buffer
        std::vector<uint8_t> payload;
        payload.reserve(267 + encryptedData.size()); // Pre-allocate for efficiency
        
        // Add metadata in little-endian format
        uint32_t encryptedSize = static_cast<uint32_t>(encryptedData.size());
        
        // Encrypted size (4 bytes)
        payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&encryptedSize),
                       reinterpret_cast<uint8_t*>(&encryptedSize) + 4);
        
        // Original size (4 bytes)
        payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&originalSize),
                       reinterpret_cast<uint8_t*>(&originalSize) + 4);
        
        // Packet number (2 bytes)
        payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&packetNum),
                       reinterpret_cast<uint8_t*>(&packetNum) + 2);
        
        // Total packets (2 bytes)
        payload.insert(payload.end(), reinterpret_cast<uint8_t*>(&totalPackets),
                       reinterpret_cast<uint8_t*>(&totalPackets) + 2);
        
        // Add filename (255 bytes, null-terminated, zero-padded)
        std::vector<uint8_t> filenameBytes(255, 0);
        if (filename.length() >= 255) {
            displayError("Filename too long for packet: " + std::to_string(filename.length()) + " chars", ErrorType::CONFIG);
            return false;
        }
        std::copy(filename.begin(), filename.end(), filenameBytes.begin());
        payload.insert(payload.end(), filenameBytes.begin(), filenameBytes.end());
        
        // Add encrypted data
        payload.insert(payload.end(), encryptedData.begin(), encryptedData.end());
        
        // Debug info for first and last packets
        if (packetNum == 1 || packetNum == totalPackets) {
            displayStatus("Debug: Packet " + std::to_string(packetNum), true,
                         "EncSize=" + std::to_string(encryptedSize) + 
                         ", OrigSize=" + std::to_string(originalSize) + 
                         ", PayloadSize=" + std::to_string(payload.size()));
        }
        
        return sendRequest(REQ_SEND_FILE, payload);
        
    } catch (const std::exception& e) {
        displayError("Failed to create file packet: " + std::string(e.what()), ErrorType::PROTOCOL);
        return false;
    }
}

// === VERIFICATION OPERATIONS ===

bool Client::verifyCRC(uint32_t serverCRC, const std::vector<uint8_t>& originalData, const std::string& filename) {
    displayStatus("Calculating CRC", true, "Using cksum algorithm");
    
    uint32_t clientCRC = calculateCRC32(originalData.data(), originalData.size());
    
    displayStatus("CRC verification", true, "Server: " + std::to_string(serverCRC) + 
                  ", Client: " + std::to_string(clientCRC));
    
    // Prepare filename payload
    std::vector<uint8_t> payload(255, 0);
    if (filename.length() >= 255) {
        displayError("Filename too long for CRC verification", ErrorType::CONFIG);
        return false;
    }
    std::copy(filename.begin(), filename.end(), payload.begin());
    
    if (serverCRC == clientCRC) {
        displayStatus("CRC verification", true, "✓ Checksums match - file integrity confirmed");
        
        if (!sendRequest(REQ_CRC_OK, payload)) {
            displayError("Failed to send CRC OK confirmation", ErrorType::NETWORK);
            return false;
        }
        
        // Wait for ACK
        ResponseHeader header;
        std::vector<uint8_t> responsePayload;
        if (receiveResponse(header, responsePayload)) {
            displayStatus("Transfer confirmed", true, "Server acknowledged successful transfer");
        } else {
            displayStatus("Transfer warning", false, "CRC OK but no server acknowledgment");
        }
        
        return true;
    } else {
        crcRetries++;
        if (crcRetries < MAX_RETRIES) {
            displayStatus("CRC verification", false, "Mismatch - Retry " + std::to_string(crcRetries) + " of " + std::to_string(MAX_RETRIES));
            
            if (!sendRequest(REQ_CRC_INVALID_RETRY, payload)) {
                displayError("Failed to send CRC retry request", ErrorType::NETWORK);
                return false;
            }
            
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
            
            if (!sendRequest(REQ_CRC_FAILED_ABORT, payload)) {
                displayError("Failed to send CRC abort request", ErrorType::NETWORK);
            }
            
            return false;
        }
    }
}

uint32_t Client::calculateCRC32(const uint8_t* data, size_t size) {
    if (!data || size == 0) {
        displayError("Invalid data for CRC calculation", ErrorType::PROTOCOL);
        return 0;
    }
    
    // Use the project's cksum implementation (POSIX-compliant)
    uint32_t crc = calculateCRC(data, size);
    
    displayStatus("CRC calculated", true, "Value: " + std::to_string(crc) + 
                 " for " + formatBytes(size) + " of data");
    
    return crc;
}

// === UTILITY FUNCTIONS ===

std::string Client::bytesToHex(const uint8_t* data, size_t size) {
    if (!data || size == 0) {
        return "";
    }
    
    std::stringstream ss;
    ss << std::hex << std::setfill('0');
    for (size_t i = 0; i < size; i++) {
        ss << std::setw(2) << static_cast<int>(data[i]);
    }
    return ss.str();
}

std::vector<uint8_t> Client::hexToBytes(const std::string& hex) {
    std::vector<uint8_t> bytes;
    
    if (hex.length() % 2 != 0) {
        displayError("Invalid hex string length: " + std::to_string(hex.length()), ErrorType::PROTOCOL);
        return bytes;
    }
    
    try {
        for (size_t i = 0; i < hex.length(); i += 2) {
            std::string byteString = hex.substr(i, 2);
            bytes.push_back(static_cast<uint8_t>(std::stoi(byteString, nullptr, 16)));
        }
    } catch (const std::exception& e) {
        displayError("Failed to parse hex string: " + std::string(e.what()), ErrorType::PROTOCOL);
        bytes.clear();
    }
    
    return bytes;
}

std::string Client::formatBytes(size_t bytes) {
    const char* sizes[] = {"B", "KB", "MB", "GB", "TB"};
    int order = 0;
    double size = static_cast<double>(bytes);
    
    while (size >= 1024 && order < 4) {
        order++;
        size /= 1024;
    }
    
    std::stringstream ss;
    if (size < 10 && order > 0) {
        ss << std::fixed << std::setprecision(2) << size << " " << sizes[order];
    } else {
        ss << std::fixed << std::setprecision(1) << size << " " << sizes[order];
    }
    return ss.str();
}

std::string Client::formatDuration(int seconds) {
    if (seconds < 0) {
        return "0s";
    }
    
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

std::string Client::getCurrentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time_t), "%H:%M:%S");
    return ss.str();
}