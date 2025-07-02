// ClientFileOps.cpp
// Enhanced Client File Operations
// Contains file I/O, configuration management, transfer operations, and data validation

#include "../../include/client/ClientCore.h"

// === CONFIGURATION MANAGEMENT ===

bool Client::readTransferInfo() {
    std::ifstream file("transfer.info");
    if (!file.is_open()) {
        std::cerr << "[ERROR] Cannot open transfer.info" << std::endl;
        return false;
    }
    
    std::string line;
    
    // Line 1: server:port
    if (!std::getline(file, line)) {
        std::cerr << "[ERROR] Invalid transfer.info format - missing server address" << std::endl;
        return false;
    }
    
    size_t colonPos = line.find(':');
    if (colonPos == std::string::npos) {
        std::cerr << "[ERROR] Invalid server address format (expected IP:port)" << std::endl;
        return false;
    }
    
    serverIP = line.substr(0, colonPos);
    try {
        serverPort = static_cast<uint16_t>(std::stoi(line.substr(colonPos + 1)));
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Invalid port number: " << e.what() << std::endl;
        return false;
    }
    
    // Line 2: username
    if (!std::getline(file, username) || username.empty()) {
        std::cerr << "[ERROR] Invalid username - cannot be empty" << std::endl;
        return false;
    }
    
    if (username.length() > 100) {
        std::cerr << "[ERROR] Username too long (max 100 characters)" << std::endl;
        return false;
    }
    
    // Line 3: filepath
    if (!std::getline(file, filepath) || filepath.empty()) {
        std::cerr << "[ERROR] Invalid file path - cannot be empty" << std::endl;
        return false;
    }
    
    std::cout << "[INFO] Configuration loaded: transfer.info parsed successfully" << std::endl;
    std::cout << "[INFO] Server config: " << serverIP << ":" << serverPort << std::endl;
    std::cout << "[INFO] User config: " << username << std::endl;
    std::cout << "[INFO] File config: " << filepath << std::endl;
    
    return true;
}

bool Client::validateConfiguration() {
    std::cout << "[INFO] Validating configuration: Checking parameters" << std::endl;
    
    // Validate server IP (Boost.Asio will handle IP validation during connect)
    if (serverIP.empty()) {
        std::cerr << "[ERROR] Invalid IP address: empty" << std::endl;
        return false;
    }
    
    // Validate port
    if (serverPort == 0 || serverPort > 65535) {
        std::cerr << "[ERROR] Invalid port number: " << serverPort << std::endl;
        return false;
    }
    
    // Validate file exists and get size
    std::ifstream testFile(filepath, std::ios::binary);
    if (!testFile.is_open()) {
        std::cerr << "[ERROR] File not found: " << filepath << std::endl;
        return false;
    }
    
    testFile.seekg(0, std::ios::end);
    stats.totalBytes = testFile.tellg();
    testFile.close();
    
    if (stats.totalBytes == 0) {
        std::cerr << "[ERROR] File is empty: " << filepath << std::endl;
        return false;
    }
    
    std::cout << "[INFO] File validation: " << filepath << " (" << formatBytes(stats.totalBytes) << ")" << std::endl;
    std::cout << "[INFO] Server validation: " << serverIP << ":" << serverPort << std::endl;
    std::cout << "[INFO] Username validation: " << username << std::endl;
    
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
    
    std::cout << "[INFO] Client ID loaded: UUID: " << line.substr(0, 8) << "..." << std::endl;
    std::cout << "[INFO] Stored username: " << storedUsername << std::endl;
    
    // Line 3: private key base64 (we'll load separately)
    return true;
}

bool Client::saveMeInfo() {
    std::ofstream file("me.info");
    if (!file.is_open()) {
        std::cerr << "[ERROR] Cannot create me.info" << std::endl;
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
        std::cout << "[INFO] Client info saved: me.info created" << std::endl;
        std::cout << "[INFO] Saved data: Username: " << username << ", ID: " << hexId.substr(0, 8) << "..." << std::endl;
        return true;
    } else {
        std::cerr << "[ERROR] Failed to write me.info" << std::endl;
        return false;
    }
}

// === FILE OPERATIONS ===

std::vector<uint8_t> Client::readFile(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "[ERROR] Cannot open file: " << path << std::endl;
        return {};
    }
    
    file.seekg(0, std::ios::end);
    size_t size = file.tellg();
    file.seekg(0, std::ios::beg);
    
    if (size == 0) {
        std::cerr << "[ERROR] File is empty: " << path << std::endl;
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
            std::cerr << "[ERROR] Failed to read file data at offset " << bytesRead << std::endl;
            return {};
        }
        
        bytesRead += actuallyRead;
    }
    
    file.close();
    
    if (bytesRead != size) {
        std::cerr << "[ERROR] Incomplete file read: " << bytesRead << "/" << size << " bytes" << std::endl;
        return {};
    }
    
    std::cout << "[INFO] File read: " << path << " (" << formatBytes(size) << ")" << std::endl;
    return data;
}

// === FILE TRANSFER OPERATIONS ===

bool Client::transferFile() {
    // Read file
    std::cout << "[INFO] Reading file: " << filepath << std::endl;
    auto fileData = readFile(filepath);
    if (fileData.empty()) {
        std::cerr << "[ERROR] Cannot read file or file is empty" << std::endl;
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
    
    std::cout << "[INFO] File details: Name: " << filename << ", Size: " << formatBytes(stats.totalBytes) << std::endl;
    std::cout << "[INFO] Encrypting file: AES-256-CBC encryption" << std::endl;
    
    // Encrypt file
    std::string encryptedData = encryptFile(fileData);
    if (encryptedData.empty()) {
        std::cerr << "[ERROR] File encryption failed" << std::endl;
        return false;
    }
    
    std::cout << "[INFO] Encryption complete: Encrypted size: " << formatBytes(encryptedData.size()) << std::endl;
    
    // Calculate packets
    size_t encryptedSize = encryptedData.size();
    uint16_t totalPackets = static_cast<uint16_t>((encryptedSize + MAX_PACKET_SIZE - 1) / MAX_PACKET_SIZE);
    
    std::cout << "[INFO] Transfer preparation: Splitting into " << totalPackets << " packets" << std::endl;
    std::cout << "=== Transfer Progress ===" << std::endl;
    
    // Send packets
    for (uint16_t packet = 1; packet <= totalPackets; packet++) {
        size_t offset = (packet - 1) * MAX_PACKET_SIZE;
        size_t chunkSize = std::min(MAX_PACKET_SIZE, encryptedSize - offset);
        
        std::string chunk = encryptedData.substr(offset, chunkSize);
        
        if (!sendFilePacket(filename, chunk, static_cast<uint32_t>(fileData.size()), packet, totalPackets)) {
            std::cerr << "[ERROR] Failed to send packet " << packet << "/" << totalPackets << std::endl;
            return false;
        }
        
        stats.update(offset + chunkSize);
        std::cout << "[PROGRESS] Transferring: " << stats.transferredBytes << "/" << encryptedData.size() << " bytes" << std::endl;
        
        if (packet % 10 == 0 || packet == totalPackets) {
            std::cout << "[STATS] Transfer stats updated" << std::endl;
        }
    }
    
    std::cout << "=== Transfer Progress ===" << std::endl;
    std::cout << "[INFO] Transfer complete: All packets sent successfully" << std::endl;
    std::cout << "[INFO] Waiting for server: Server calculating CRC..." << std::endl;
    
    // Receive CRC response
    ResponseHeader header;
    std::vector<uint8_t> responsePayload;
    if (!receiveResponse(header, responsePayload)) {
        std::cerr << "[ERROR] Failed to receive CRC response" << std::endl;
        return false;
    }
    
    if (header.code != RESP_FILE_CRC) {
        std::cerr << "[ERROR] Invalid file transfer response code: " << header.code << ", expected: " << RESP_FILE_CRC << std::endl;
        return false;
    }
    
    if (responsePayload.size() < 279) {
        std::cerr << "[ERROR] Invalid file transfer response payload size: " << responsePayload.size() << " bytes, expected >= 279" << std::endl;
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
            std::cerr << "[ERROR] Filename too long for packet: " << filename.length() << " chars" << std::endl;
            return false;
        }
        std::copy(filename.begin(), filename.end(), filenameBytes.begin());
        payload.insert(payload.end(), filenameBytes.begin(), filenameBytes.end());
        
        // Add encrypted data
        payload.insert(payload.end(), encryptedData.begin(), encryptedData.end());
        
        // Debug info for first and last packets
        if (packetNum == 1 || packetNum == totalPackets) {
            std::cout << "[DEBUG] Packet " << packetNum << ": EncSize=" << encryptedSize << ", OrigSize=" << originalSize << ", PayloadSize=" << payload.size() << std::endl;
        }
        
        return sendRequest(REQ_SEND_FILE, payload);
        
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to create file packet: " << e.what() << std::endl;
        return false;
    }
}

// === VERIFICATION OPERATIONS ===

bool Client::verifyCRC(uint32_t serverCRC, const std::vector<uint8_t>& originalData, const std::string& filename) {
    std::cout << "[INFO] Calculating CRC: Using cksum algorithm" << std::endl;
    
    uint32_t clientCRC = calculateCRC32(originalData.data(), originalData.size());
    
    std::cout << "[INFO] CRC verification: Server: " << serverCRC << ", Client: " << clientCRC << std::endl;
    
    // Prepare filename payload
    std::vector<uint8_t> payload(255, 0);
    if (filename.length() >= 255) {
        std::cerr << "[ERROR] Filename too long for CRC verification" << std::endl;
        return false;
    }
    std::copy(filename.begin(), filename.end(), payload.begin());
    
    if (serverCRC == clientCRC) {
        std::cout << "[INFO] CRC verification: ✓ Checksums match - file integrity confirmed" << std::endl;
        
        if (!sendRequest(REQ_CRC_OK, payload)) {
            std::cerr << "[ERROR] Failed to send CRC OK confirmation" << std::endl;
            return false;
        }
        
        // Wait for ACK
        ResponseHeader header;
        std::vector<uint8_t> responsePayload;
        if (receiveResponse(header, responsePayload)) {
            std::cout << "[INFO] Transfer confirmed: Server acknowledged successful transfer" << std::endl;
        } else {
            std::cout << "[WARNING] Transfer warning: CRC OK but no server acknowledgment" << std::endl;
        }
        
        return true;
    } else {
        crcRetries++;
        if (crcRetries < MAX_RETRIES) {
            std::cout << "[WARNING] CRC verification: Mismatch - Retry " << crcRetries << " of " << MAX_RETRIES << std::endl;
            
            if (!sendRequest(REQ_CRC_INVALID_RETRY, payload)) {
                std::cerr << "[ERROR] Failed to send CRC retry request" << std::endl;
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
            std::cout << "[ERROR] CRC verification: Maximum retries exceeded - aborting" << std::endl;
            
            if (!sendRequest(REQ_CRC_FAILED_ABORT, payload)) {
                std::cerr << "[ERROR] Failed to send CRC abort request" << std::endl;
            }
            
            return false;
        }
    }
}

uint32_t Client::calculateCRC32(const uint8_t* data, size_t size) {
    if (!data || size == 0) {
        std::cerr << "[ERROR] Invalid data for CRC calculation" << std::endl;
        return 0;
    }
    
    // Use the project's cksum implementation (POSIX-compliant)
    uint32_t crc = calculateCRC(data, size);
    
    std::cout << "[INFO] CRC calculated: Value: " << crc << " for " << formatBytes(size) << " of data" << std::endl;
    
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
        std::cerr << "[ERROR] Invalid hex string length: " << hex.length() << std::endl;
        return bytes;
    }
    
    try {
        for (size_t i = 0; i < hex.length(); i += 2) {
            std::string byteString = hex.substr(i, 2);
            bytes.push_back(static_cast<uint8_t>(std::stoi(byteString, nullptr, 16)));
        }
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to parse hex string: " << e.what() << std::endl;
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
            std::tm tm_buf;
        localtime_s(&tm_buf, &time_t);
        ss << std::put_time(&tm_buf, "%H:%M:%S");
    return ss.str();
}