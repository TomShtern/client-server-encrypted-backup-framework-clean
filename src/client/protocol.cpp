#include "../../include/client/protocol.h"
#include "../../include/client/cksum.h"
#include <iostream>
#include <vector>
#include <cstring>
#include <stdexcept>

// Protocol constants - definitions for extern declarations in header
const uint8_t PROTOCOL_VERSION = 3;
const size_t CLIENT_ID_SIZE = 16;
const size_t HEADER_SIZE = 23;
const size_t MAX_FILENAME_SIZE = 255;

// Request codes
const uint16_t REQ_REGISTER = 1025;
const uint16_t REQ_SEND_PUBLIC_KEY = 1026;
const uint16_t REQ_RECONNECT = 1027;
const uint16_t REQ_SEND_FILE = 1028;
const uint16_t REQ_CRC_OK = 1029;
const uint16_t REQ_CRC_INVALID_RETRY = 1030;  // Fixed: matches server
const uint16_t REQ_CRC_FAILED_ABORT = 1031;   // Fixed: matches server

// Response codes
const uint16_t RESP_REG_OK = 1600;              // Fixed: matches server
const uint16_t RESP_REG_FAIL = 1601;            // Fixed: matches server
const uint16_t RESP_PUBKEY_AES_SENT = 1602;
const uint16_t RESP_FILE_CRC = 1603;
const uint16_t RESP_ACK = 1604;
const uint16_t RESP_RECONNECT_AES_SENT = 1605;
const uint16_t RESP_RECONNECT_FAIL = 1606;
const uint16_t RESP_GENERIC_SERVER_ERROR = 1607; // Fixed: matches server

// Protocol structures (packed)
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

// Helper functions for guaranteed little-endian serialization
void writeLE16(std::vector<uint8_t>& buffer, uint16_t value) {
    buffer.push_back(value & 0xFF);
    buffer.push_back((value >> 8) & 0xFF);
}

void writeLE32(std::vector<uint8_t>& buffer, uint32_t value) {
    buffer.push_back(value & 0xFF);
    buffer.push_back((value >> 8) & 0xFF);
    buffer.push_back((value >> 16) & 0xFF);
    buffer.push_back((value >> 24) & 0xFF);
}

uint16_t readLE16(const uint8_t* data) {
    return static_cast<uint16_t>(data[0]) | (static_cast<uint16_t>(data[1]) << 8);
}

uint32_t readLE32(const uint8_t* data) {
    return static_cast<uint32_t>(data[0]) | 
           (static_cast<uint32_t>(data[1]) << 8) | 
           (static_cast<uint32_t>(data[2]) << 16) | 
           (static_cast<uint32_t>(data[3]) << 24);
}

// Deprecated functions - use writeLE/readLE instead
uint16_t hostToLittleEndian16(uint16_t value) {
    uint8_t bytes[2];
    bytes[0] = value & 0xFF;
    bytes[1] = (value >> 8) & 0xFF;
    uint16_t result;
    std::memcpy(&result, bytes, 2);
    return result;
}

uint32_t hostToLittleEndian32(uint32_t value) {
    uint8_t bytes[4];
    bytes[0] = value & 0xFF;
    bytes[1] = (value >> 8) & 0xFF;
    bytes[2] = (value >> 16) & 0xFF;
    bytes[3] = (value >> 24) & 0xFF;
    uint32_t result;
    std::memcpy(&result, bytes, 4);
    return result;
}

uint16_t littleEndianToHost16(uint16_t value) {
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&value);
    return readLE16(bytes);
}

uint32_t littleEndianToHost32(uint32_t value) {
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&value);
    return readLE32(bytes);
}

// Helper function to create padded string fields
std::vector<uint8_t> createPaddedString(const std::string& str, size_t targetSize) {
    std::vector<uint8_t> result(targetSize, 0);
    size_t copySize = std::min(str.size(), targetSize - 1); // Leave room for null terminator
    std::memcpy(result.data(), str.c_str(), copySize);
    return result;
}

// Create registration request (Code 1025) with proper manual serialization
std::vector<uint8_t> createRegistrationRequest(const uint8_t* clientId, const std::string& username) {
    std::vector<uint8_t> request;
    
    // Manual header serialization for guaranteed little-endian compliance
    // client_id(16) + version(1) + code(2) + payload_size(4) = 23 bytes
    request.resize(CLIENT_ID_SIZE);
    std::memcpy(request.data(), clientId, CLIENT_ID_SIZE);
    
    request.push_back(PROTOCOL_VERSION);
    writeLE16(request, REQ_REGISTER);
    writeLE32(request, MAX_FILENAME_SIZE); // Username field size
    
    // Add username payload (255 bytes, null-terminated, zero-padded)
    std::vector<uint8_t> usernameField = createPaddedString(username, MAX_FILENAME_SIZE);
    request.insert(request.end(), usernameField.begin(), usernameField.end());
    
    std::cout << "[DEBUG] Created registration request: " << request.size() << " bytes" << std::endl;
    return request;
}

// Create public key submission request (Code 1026) with proper serialization
std::vector<uint8_t> createPublicKeyRequest(const uint8_t* clientId, const std::string& username, 
                                          const std::string& publicKey) {
    std::vector<uint8_t> request;
    
    // Validate public key size (162 bytes for RSA DER format - actual implementation)
    if (publicKey.size() != 162) {
        throw std::invalid_argument("Public key must be exactly 162 bytes for protocol compliance");
    }
    
    // Manual header serialization for guaranteed little-endian compliance
    request.resize(CLIENT_ID_SIZE);
    std::memcpy(request.data(), clientId, CLIENT_ID_SIZE);
    
    request.push_back(PROTOCOL_VERSION);
    writeLE16(request, REQ_SEND_PUBLIC_KEY);
    writeLE32(request, MAX_FILENAME_SIZE + 162); // username (255) + public key (162)
    
    // Add username field (255 bytes, null-terminated, zero-padded)
    std::vector<uint8_t> usernameField = createPaddedString(username, MAX_FILENAME_SIZE);
    request.insert(request.end(), usernameField.begin(), usernameField.end());
    
    // Add public key (exactly 162 bytes)
    request.insert(request.end(), publicKey.begin(), publicKey.end());
    
    std::cout << "[DEBUG] Created public key request: " << request.size() << " bytes" << std::endl;
    return request;
}

// Create reconnection request (Code 1027) with proper serialization
std::vector<uint8_t> createReconnectionRequest(const uint8_t* clientId, const std::string& username) {
    std::vector<uint8_t> request;
    
    // Manual header serialization for guaranteed little-endian compliance
    request.resize(CLIENT_ID_SIZE);
    std::memcpy(request.data(), clientId, CLIENT_ID_SIZE);
    
    request.push_back(PROTOCOL_VERSION);
    writeLE16(request, REQ_RECONNECT);
    writeLE32(request, MAX_FILENAME_SIZE); // Username field size
    
    // Add username payload (255 bytes, null-terminated, zero-padded)
    std::vector<uint8_t> usernameField = createPaddedString(username, MAX_FILENAME_SIZE);
    request.insert(request.end(), usernameField.begin(), usernameField.end());
    
    std::cout << "[DEBUG] Created reconnection request: " << request.size() << " bytes" << std::endl;
    return request;
}

// Create file transfer request (Code 1028) with chunking support
std::vector<uint8_t> createFileTransferRequest(const uint8_t* clientId, const std::string& filename,
                                              const std::vector<uint8_t>& encryptedData, 
                                              uint32_t originalSize, uint16_t packetNumber, 
                                              uint16_t totalPackets) {
    std::vector<uint8_t> request;
    
    // Manual serialization for guaranteed little-endian compliance
    // Header: client_id(16) + version(1) + code(2) + payload_size(4) = 23 bytes
    request.resize(CLIENT_ID_SIZE);
    std::memcpy(request.data(), clientId, CLIENT_ID_SIZE);
    
    request.push_back(PROTOCOL_VERSION);
    writeLE16(request, REQ_SEND_FILE);
    
    // Calculate payload size: content_size(4) + orig_file_size(4) + packet_number(2) + total_packets(2) + filename(255) + data
    uint32_t payloadSize = 4 + 4 + 2 + 2 + MAX_FILENAME_SIZE + static_cast<uint32_t>(encryptedData.size());
    writeLE32(request, payloadSize);
    
    // Payload fields - all manually serialized as little-endian
    writeLE32(request, static_cast<uint32_t>(encryptedData.size())); // Content size
    writeLE32(request, originalSize);                                // Original file size
    writeLE16(request, packetNumber);                               // Packet number (1-based)
    writeLE16(request, totalPackets);                               // Total packets
    
    // Filename field (255 bytes, null-terminated, zero-padded)
    std::vector<uint8_t> filenameField = createPaddedString(filename, MAX_FILENAME_SIZE);
    request.insert(request.end(), filenameField.begin(), filenameField.end());
    
    // Encrypted file data chunk
    request.insert(request.end(), encryptedData.begin(), encryptedData.end());
    
    std::cout << "[DEBUG] Created file transfer request: " << request.size() << " bytes (packet " 
              << packetNumber << "/" << totalPackets << ")" << std::endl;
    return request;
}

// Overload for backward compatibility (single packet)
std::vector<uint8_t> createFileTransferRequest(const uint8_t* clientId, const std::string& filename,
                                              const std::vector<uint8_t>& encryptedData, 
                                              uint32_t originalSize) {
    return createFileTransferRequest(clientId, filename, encryptedData, originalSize, 1, 1);
}

// Split large files into chunks for transmission
std::vector<std::vector<uint8_t>> createChunkedFileTransferRequests(const uint8_t* clientId, 
                                                                   const std::string& filename,
                                                                   const std::vector<uint8_t>& encryptedData, 
                                                                   uint32_t originalSize) {
    std::vector<std::vector<uint8_t>> requests;
    
    // Maximum chunk size: 1MB for data + headers (~1MB total per packet)
    const size_t MAX_CHUNK_SIZE = 1024 * 1024; // 1MB
    
    if (encryptedData.size() <= MAX_CHUNK_SIZE) {
        // Single packet
        requests.push_back(createFileTransferRequest(clientId, filename, encryptedData, originalSize, 1, 1));
        return requests;
    }
    
    // Multiple packets needed
    size_t totalChunks = (encryptedData.size() + MAX_CHUNK_SIZE - 1) / MAX_CHUNK_SIZE;
    uint16_t totalPackets = static_cast<uint16_t>(std::min(totalChunks, static_cast<size_t>(65535)));
    
    for (uint16_t packet = 1; packet <= totalPackets; ++packet) {
        size_t startOffset = (packet - 1) * MAX_CHUNK_SIZE;
        size_t endOffset = std::min(startOffset + MAX_CHUNK_SIZE, encryptedData.size());
        
        std::vector<uint8_t> chunk(encryptedData.begin() + startOffset, encryptedData.begin() + endOffset);
        requests.push_back(createFileTransferRequest(clientId, filename, chunk, originalSize, packet, totalPackets));
        
        std::cout << "[DEBUG] Created chunk " << packet << "/" << totalPackets 
                  << " (" << chunk.size() << " bytes)" << std::endl;
    }
    
    return requests;
}

// Create CRC verification requests (Codes 1029, 1030, 1031) with proper serialization
std::vector<uint8_t> createCRCRequest(const uint8_t* clientId, uint16_t requestCode, 
                                     const std::string& filename) {
    std::vector<uint8_t> request;
    
    // Manual header serialization for guaranteed little-endian compliance
    request.resize(CLIENT_ID_SIZE);
    std::memcpy(request.data(), clientId, CLIENT_ID_SIZE);
    
    request.push_back(PROTOCOL_VERSION);
    writeLE16(request, requestCode);
    writeLE32(request, MAX_FILENAME_SIZE); // Filename field size
    
    // Add filename payload (255 bytes, null-terminated, zero-padded)
    std::vector<uint8_t> filenameField = createPaddedString(filename, MAX_FILENAME_SIZE);
    request.insert(request.end(), filenameField.begin(), filenameField.end());
    
    std::cout << "[DEBUG] Created CRC request (code " << requestCode << "): " << request.size() << " bytes" << std::endl;
    return request;
}

// Parse response header
bool parseResponseHeader(const std::vector<uint8_t>& data, uint8_t& version, 
                        uint16_t& code, uint32_t& payloadSize) {
    if (data.size() < sizeof(ResponseHeader)) {
        std::cerr << "[ERROR] Response data too small for header" << std::endl;
        return false;
    }
    
    const ResponseHeader* header = reinterpret_cast<const ResponseHeader*>(data.data());
    version = header->version;
    code = littleEndianToHost16(header->code);
    payloadSize = littleEndianToHost32(header->payload_size);
    
    std::cout << "[DEBUG] Parsed response: version=" << static_cast<int>(version) 
              << ", code=" << code << ", payload_size=" << payloadSize << std::endl;
    
    return true;
}

// Extract response payload
std::vector<uint8_t> extractResponsePayload(const std::vector<uint8_t>& data) {
    if (data.size() <= sizeof(ResponseHeader)) {
        return std::vector<uint8_t>(); // No payload
    }
    
    return std::vector<uint8_t>(data.begin() + sizeof(ResponseHeader), data.end());
}

// Parse registration success response (1600)
bool parseRegistrationResponse(const std::vector<uint8_t>& payload, std::vector<uint8_t>& clientId) {
    if (payload.size() < CLIENT_ID_SIZE) {
        std::cerr << "[ERROR] Registration response payload too small" << std::endl;
        return false;
    }
    
    clientId.assign(payload.begin(), payload.begin() + CLIENT_ID_SIZE);
    std::cout << "[DEBUG] Parsed registration response: received " << clientId.size() << "-byte client ID" << std::endl;
    return true;
}

// Parse public key/reconnection response (1602/1605) 
bool parseKeyExchangeResponse(const std::vector<uint8_t>& payload, std::vector<uint8_t>& clientId,
                             std::vector<uint8_t>& encryptedAESKey) {
    if (payload.size() < CLIENT_ID_SIZE) {
        std::cerr << "[ERROR] Key exchange response payload too small" << std::endl;
        return false;
    }
    
    // Extract client ID (first 16 bytes)
    clientId.assign(payload.begin(), payload.begin() + CLIENT_ID_SIZE);
    
    // Extract encrypted AES key (remaining bytes)
    if (payload.size() > CLIENT_ID_SIZE) {
        encryptedAESKey.assign(payload.begin() + CLIENT_ID_SIZE, payload.end());
    }
    
    std::cout << "[DEBUG] Parsed key exchange response: client ID " << clientId.size() 
              << " bytes, encrypted AES key " << encryptedAESKey.size() << " bytes" << std::endl;
    return true;
}

// Parse file transfer response (1603)
bool parseFileTransferResponse(const std::vector<uint8_t>& payload, std::vector<uint8_t>& clientId,
                              uint32_t& contentSize, std::string& filename, uint32_t& checksum) {
    // Expected structure: client_id(16) + content_size(4) + filename(255) + checksum(4)
    const size_t expectedSize = CLIENT_ID_SIZE + 4 + MAX_FILENAME_SIZE + 4;
    if (payload.size() < expectedSize) {
        std::cerr << "[ERROR] File transfer response payload too small: " << payload.size() 
                  << " < " << expectedSize << std::endl;
        return false;
    }
    
    size_t offset = 0;
    
    // Extract client ID
    clientId.assign(payload.begin() + offset, payload.begin() + offset + CLIENT_ID_SIZE);
    offset += CLIENT_ID_SIZE;
    
    // Extract content size
    contentSize = littleEndianToHost32(*reinterpret_cast<const uint32_t*>(payload.data() + offset));
    offset += 4;
    
    // Extract filename (null-terminated string from 255-byte field)
    const char* filenamePtr = reinterpret_cast<const char*>(payload.data() + offset);
    filename = std::string(filenamePtr);
    offset += MAX_FILENAME_SIZE;
    
    // Extract checksum
    checksum = littleEndianToHost32(*reinterpret_cast<const uint32_t*>(payload.data() + offset));
    
    std::cout << "[DEBUG] Parsed file transfer response: content_size=" << contentSize 
              << ", filename='" << filename << "', checksum=0x" << std::hex << checksum << std::dec << std::endl;
    return true;
}

// Calculate CRC using the Linux cksum compatible algorithm
uint32_t calculateFileCRC(const std::vector<uint8_t>& data) {
    return calculateCRC(data.data(), data.size());
}

// Utility function to print hex dump for debugging
void printHexDump(const std::vector<uint8_t>& data, const std::string& label) {
    std::cout << "[DEBUG] " << label << " (" << data.size() << " bytes):" << std::endl;
    for (size_t i = 0; i < data.size(); ++i) {
        if (i % 16 == 0) std::cout << "  ";
        std::cout << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(data[i]) << " ";
        if ((i + 1) % 16 == 0 || i == data.size() - 1) std::cout << std::endl;
    }
    std::cout << std::dec;
}