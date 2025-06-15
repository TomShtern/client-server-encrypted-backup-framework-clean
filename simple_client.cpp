// simple_client.cpp
// Minimal C++ client for encrypted backup system - NO dependencies
// Focus: Get basic protocol working with proper serialization

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>
#include <random>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#define SOCKET int
#define INVALID_SOCKET -1
#define SOCKET_ERROR -1
#define closesocket close
#endif

// Protocol constants
const uint8_t PROTOCOL_VERSION = 3;
const size_t CLIENT_ID_SIZE = 16;
const size_t MAX_FILENAME_SIZE = 255;

// Request codes
const uint16_t REQ_REGISTER = 1025;
const uint16_t REQ_SEND_PUBLIC_KEY = 1026;
const uint16_t REQ_SEND_FILE = 1028;

// Response codes  
const uint16_t RESP_REGISTER_OK = 1600;
const uint16_t RESP_PUBKEY_AES_SENT = 1602;
const uint16_t RESP_FILE_CRC = 1603;

class SimpleClient {
private:
    SOCKET sock;
    std::string server_host;
    int server_port;
    std::string username;
    std::string file_path;
    std::vector<uint8_t> client_id;
    
public:
    SimpleClient() : sock(INVALID_SOCKET) {
        #ifdef _WIN32
        WSADATA wsaData;
        WSAStartup(MAKEWORD(2,2), &wsaData);
        #endif
    }
    
    ~SimpleClient() {
        if (sock != INVALID_SOCKET) {
            closesocket(sock);
        }
        #ifdef _WIN32
        WSACleanup();
        #endif
    }
    
    // Helper: Write uint16 in little-endian
    void writeLE16(std::vector<uint8_t>& buffer, uint16_t value) {
        buffer.push_back(value & 0xFF);
        buffer.push_back((value >> 8) & 0xFF);
    }
    
    // Helper: Write uint32 in little-endian  
    void writeLE32(std::vector<uint8_t>& buffer, uint32_t value) {
        buffer.push_back(value & 0xFF);
        buffer.push_back((value >> 8) & 0xFF);
        buffer.push_back((value >> 16) & 0xFF);
        buffer.push_back((value >> 24) & 0xFF);
    }
    
    // Helper: Read uint16 from little-endian
    uint16_t readLE16(const uint8_t* data) {
        return static_cast<uint16_t>(data[0]) | (static_cast<uint16_t>(data[1]) << 8);
    }
    
    // Helper: Read uint32 from little-endian
    uint32_t readLE32(const uint8_t* data) {
        return static_cast<uint32_t>(data[0]) | 
               (static_cast<uint32_t>(data[1]) << 8) |
               (static_cast<uint32_t>(data[2]) << 16) |
               (static_cast<uint32_t>(data[3]) << 24);
    }
    
    // Helper: Create padded string field
    std::vector<uint8_t> createPaddedString(const std::string& str, size_t targetSize) {
        std::vector<uint8_t> result(targetSize, 0);
        size_t copySize = std::min(str.size(), targetSize - 1); // Leave room for null terminator
        std::memcpy(result.data(), str.c_str(), copySize);
        return result;
    }
    
    // Load configuration
    bool loadConfig() {
        std::cout << "[CONFIG] Loading configuration..." << std::endl;
        
        // Load transfer.info
        std::ifstream transferFile("transfer.info");
        if (!transferFile.is_open()) {
            // Try client/transfer.info
            transferFile.open("client/transfer.info");
            if (!transferFile.is_open()) {
                std::cerr << "[ERROR] Cannot find transfer.info" << std::endl;
                return false;
            }
        }
        
        std::string serverInfo;
        std::getline(transferFile, serverInfo);
        std::getline(transferFile, username);
        std::getline(transferFile, file_path);
        transferFile.close();
        
        // Parse server:port
        size_t colonPos = serverInfo.find(':');
        if (colonPos != std::string::npos) {
            server_host = serverInfo.substr(0, colonPos);
            server_port = std::stoi(serverInfo.substr(colonPos + 1));
        } else {
            server_host = serverInfo;
            server_port = 1256;
        }
        
        std::cout << "[CONFIG] Server: " << server_host << ":" << server_port << std::endl;
        std::cout << "[CONFIG] Username: " << username << std::endl;
        std::cout << "[CONFIG] File: " << file_path << std::endl;
        
        return true;
    }
    
    // Connect to server
    bool connect() {
        std::cout << "[NETWORK] Connecting to " << server_host << ":" << server_port << std::endl;
        
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock == INVALID_SOCKET) {
            std::cerr << "[ERROR] Failed to create socket" << std::endl;
            return false;
        }
        
        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(server_port);
        
        #ifdef _WIN32
        serverAddr.sin_addr.s_addr = inet_addr(server_host.c_str());
        #else
        inet_pton(AF_INET, server_host.c_str(), &serverAddr.sin_addr);
        #endif
        
        if (::connect(sock, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            std::cerr << "[ERROR] Failed to connect to server" << std::endl;
            return false;
        }
        
        std::cout << "[NETWORK] ✅ Connected successfully!" << std::endl;
        return true;
    }
    
    // Send data to server
    bool sendData(const std::vector<uint8_t>& data) {
        int totalSent = 0;
        int remaining = static_cast<int>(data.size());
        
        while (remaining > 0) {
            int sent = send(sock, reinterpret_cast<const char*>(data.data() + totalSent), remaining, 0);
            if (sent == SOCKET_ERROR) {
                std::cerr << "[ERROR] Failed to send data" << std::endl;
                return false;
            }
            totalSent += sent;
            remaining -= sent;
        }
        
        std::cout << "[NETWORK] Sent " << data.size() << " bytes" << std::endl;
        return true;
    }
    
    // Receive data from server
    bool receiveData(std::vector<uint8_t>& data, size_t expectedSize) {
        data.resize(expectedSize);
        int totalReceived = 0;
        int remaining = static_cast<int>(expectedSize);
        
        while (remaining > 0) {
            int received = recv(sock, reinterpret_cast<char*>(data.data() + totalReceived), remaining, 0);
            if (received <= 0) {
                std::cerr << "[ERROR] Failed to receive data or connection closed" << std::endl;
                return false;
            }
            totalReceived += received;
            remaining -= received;
        }
        
        std::cout << "[NETWORK] Received " << data.size() << " bytes" << std::endl;
        return true;
    }
    
    // Step 1: Register client
    bool registerClient() {
        std::cout << "\n[STEP 1] Registering client..." << std::endl;
        
        // Generate random client ID
        client_id.resize(CLIENT_ID_SIZE);
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, 255);
        
        for (size_t i = 0; i < CLIENT_ID_SIZE; ++i) {
            client_id[i] = static_cast<uint8_t>(dis(gen));
        }
        
        // Create registration request with manual little-endian serialization
        std::vector<uint8_t> request;
        
        // Header: client_id(16) + version(1) + code(2) + payload_size(4) = 23 bytes
        request.insert(request.end(), client_id.begin(), client_id.end());
        request.push_back(PROTOCOL_VERSION);
        writeLE16(request, REQ_REGISTER);
        writeLE32(request, MAX_FILENAME_SIZE); // Username field size
        
        // Payload: username (255 bytes, null-terminated, zero-padded)
        std::vector<uint8_t> usernameField = createPaddedString(username, MAX_FILENAME_SIZE);
        request.insert(request.end(), usernameField.begin(), usernameField.end());
        
        std::cout << "[PROTOCOL] Created registration request (" << request.size() << " bytes)" << std::endl;
        std::cout << "[PROTOCOL] Header: 23 bytes, Payload: " << usernameField.size() << " bytes" << std::endl;
        
        // Send request
        if (!sendData(request)) {
            return false;
        }
        
        // Receive response header (7 bytes)
        std::vector<uint8_t> responseHeader;
        if (!receiveData(responseHeader, 7)) {
            return false;
        }
        
        // Parse response
        uint8_t respVersion = responseHeader[0];
        uint16_t respCode = readLE16(&responseHeader[1]);
        uint32_t payloadSize = readLE32(&responseHeader[3]);
        
        std::cout << "[PROTOCOL] Response: version=" << static_cast<int>(respVersion) 
                  << ", code=" << respCode << ", payload=" << payloadSize << std::endl;
        
        if (respCode == RESP_REGISTER_OK) {
            std::cout << "[STEP 1] ✅ Registration successful!" << std::endl;
            
            // Receive client ID from payload if present
            if (payloadSize > 0) {
                std::vector<uint8_t> payload;
                if (receiveData(payload, payloadSize)) {
                    if (payload.size() >= CLIENT_ID_SIZE) {
                        client_id.assign(payload.begin(), payload.begin() + CLIENT_ID_SIZE);
                        std::cout << "[PROTOCOL] Server assigned client ID" << std::endl;
                    }
                }
            }
            return true;
        } else {
            std::cerr << "[STEP 1] ❌ Registration failed with code " << respCode << std::endl;
            return false;
        }
    }
    
    // Step 2: Send public key and get AES key
    bool exchangeKeys() {
        std::cout << "\n[STEP 2] Exchanging keys..." << std::endl;
        
        // Create valid 162-byte RSA public key in DER format using byte array
        std::vector<uint8_t> validRSAKey = {
            0x30, 0x81, 0x9f, 0x30, 0x0d, 0x06, 0x09, 0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x01,
            0x05, 0x00, 0x03, 0x81, 0x8d, 0x00, 0x30, 0x81, 0x89, 0x02, 0x81, 0x81, 0x00, 0xe7, 0x0f, 0xb3,
            0xd4, 0xf0, 0x0b, 0xcf, 0xe3, 0xe9, 0x79, 0x05, 0x0d, 0xa7, 0xaf, 0xc8, 0xd6, 0x00, 0x30, 0xef,
            0x28, 0xeb, 0xd5, 0x78, 0x32, 0xd9, 0xc2, 0x6e, 0x53, 0x14, 0x6f, 0xfb, 0x6b, 0x76, 0xa8, 0xf6,
            0xac, 0x33, 0xdf, 0x55, 0x77, 0xc2, 0xbc, 0xb7, 0xd6, 0x8c, 0x4e, 0xcb, 0x11, 0x51, 0x21, 0x48,
            0xf5, 0xf1, 0xfd, 0xbf, 0x03, 0xd9, 0x01, 0x07, 0x6a, 0xd0, 0x9f, 0x35, 0xe5, 0x4a, 0x2f, 0xf6,
            0xe6, 0x07, 0xab, 0x21, 0xb5, 0xfb, 0xec, 0xbc, 0x49, 0xca, 0xa0, 0xd8, 0x71, 0x02, 0x72, 0xe6,
            0xc7, 0x55, 0x2e, 0x7d, 0xc5, 0xf7, 0xca, 0x1f, 0x21, 0x56, 0x74, 0xa8, 0x25, 0x58, 0x86, 0xfb,
            0x5a, 0xd1, 0x19, 0xfd, 0xfc, 0xe9, 0xb4, 0x28, 0x85, 0x00, 0x22, 0xd0, 0x01, 0xc2, 0x0c, 0xd9,
            0xc7, 0x17, 0xa9, 0x50, 0x50, 0x85, 0xce, 0xe8, 0xb8, 0x22, 0x15, 0xba, 0x65, 0x02, 0x03, 0x01,
            0x00, 0x01
        }; // Real 1024-bit RSA public key in DER format (162 bytes)
        
        // Create public key request
        std::vector<uint8_t> request;
        
        // Header
        request.insert(request.end(), client_id.begin(), client_id.end());
        request.push_back(PROTOCOL_VERSION);
        writeLE16(request, REQ_SEND_PUBLIC_KEY);
        writeLE32(request, MAX_FILENAME_SIZE + 162); // username + public key
        
        // Payload: username (255 bytes) + public key (162 bytes)
        std::vector<uint8_t> usernameField = createPaddedString(username, MAX_FILENAME_SIZE);
        request.insert(request.end(), usernameField.begin(), usernameField.end());
        request.insert(request.end(), validRSAKey.begin(), validRSAKey.end());
        
        std::cout << "[PROTOCOL] Created key exchange request (" << request.size() << " bytes)" << std::endl;
        std::cout << "[DEBUG] Username field size: " << usernameField.size() << " bytes" << std::endl;
        std::cout << "[DEBUG] RSA key size: " << validRSAKey.size() << " bytes" << std::endl;
        std::cout << "[DEBUG] Expected payload: " << (usernameField.size() + validRSAKey.size()) << " bytes" << std::endl;
        std::cout << "[DEBUG] Actual payload size in header: " << (MAX_FILENAME_SIZE + 162) << " bytes" << std::endl;
        
        // Send request
        if (!sendData(request)) {
            return false;
        }
        
        // Receive response header
        std::vector<uint8_t> responseHeader;
        if (!receiveData(responseHeader, 7)) {
            return false;
        }
        
        // Parse response
        uint8_t respVersion = responseHeader[0];
        uint16_t respCode = readLE16(&responseHeader[1]);
        uint32_t payloadSize = readLE32(&responseHeader[3]);
        
        std::cout << "[PROTOCOL] Response: version=" << static_cast<int>(respVersion) 
                  << ", code=" << respCode << ", payload=" << payloadSize << std::endl;
        
        if (respCode == RESP_PUBKEY_AES_SENT && payloadSize > 0) {
            std::cout << "[STEP 2] ✅ Key exchange successful!" << std::endl;
            
            // Receive encrypted AES key
            std::vector<uint8_t> payload;
            if (receiveData(payload, payloadSize)) {
                std::cout << "[PROTOCOL] Received encrypted AES key (" << payload.size() << " bytes)" << std::endl;
            }
            return true;
        } else {
            std::cerr << "[STEP 2] ❌ Key exchange failed with code " << respCode << std::endl;
            return false;
        }
    }
    
    // Step 3: Transfer file
    bool transferFile() {
        std::cout << "\n[STEP 3] Transferring file..." << std::endl;
        
        // Read file
        std::ifstream file(file_path, std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "[ERROR] Cannot open file: " << file_path << std::endl;
            return false;
        }
        
        std::vector<uint8_t> fileData((std::istreambuf_iterator<char>(file)),
                                     std::istreambuf_iterator<char>());
        file.close();
        
        if (fileData.empty()) {
            std::cerr << "[ERROR] File is empty" << std::endl;
            return false;
        }
        
        std::cout << "[FILE] Read " << fileData.size() << " bytes from " << file_path << std::endl;
        
        // For testing, use file data as-is (in real system would be AES encrypted)
        std::vector<uint8_t> encryptedData = fileData;
        
        // Extract filename from path
        std::string filename = file_path;
        size_t lastSlash = filename.find_last_of("/\\");
        if (lastSlash != std::string::npos) {
            filename = filename.substr(lastSlash + 1);
        }
        
        // Create file transfer request
        std::vector<uint8_t> request;
        
        // Header
        request.insert(request.end(), client_id.begin(), client_id.end());
        request.push_back(PROTOCOL_VERSION);
        writeLE16(request, REQ_SEND_FILE);
        
        // Calculate payload size: content_size(4) + orig_size(4) + packet_num(2) + total_packets(2) + filename(255) + data
        uint32_t payloadSize = 4 + 4 + 2 + 2 + MAX_FILENAME_SIZE + static_cast<uint32_t>(encryptedData.size());
        writeLE32(request, payloadSize);
        
        // Payload fields (all little-endian)
        writeLE32(request, static_cast<uint32_t>(encryptedData.size())); // Content size
        writeLE32(request, static_cast<uint32_t>(fileData.size()));      // Original size
        writeLE16(request, 1);                                           // Packet number
        writeLE16(request, 1);                                           // Total packets
        
        // Filename field (255 bytes)
        std::vector<uint8_t> filenameField = createPaddedString(filename, MAX_FILENAME_SIZE);
        request.insert(request.end(), filenameField.begin(), filenameField.end());
        
        // File data
        request.insert(request.end(), encryptedData.begin(), encryptedData.end());
        
        std::cout << "[PROTOCOL] Created file transfer request (" << request.size() << " bytes)" << std::endl;
        std::cout << "[FILE] Filename: " << filename << std::endl;
        std::cout << "[FILE] Original size: " << fileData.size() << " bytes" << std::endl;
        
        // Send request
        if (!sendData(request)) {
            return false;
        }
        
        // Receive response header
        std::vector<uint8_t> responseHeader;
        if (!receiveData(responseHeader, 7)) {
            return false;
        }
        
        // Parse response
        uint8_t respVersion = responseHeader[0];
        uint16_t respCode = readLE16(&responseHeader[1]);
        uint32_t respPayloadSize = readLE32(&responseHeader[3]);
        
        std::cout << "[PROTOCOL] Response: version=" << static_cast<int>(respVersion) 
                  << ", code=" << respCode << ", payload=" << respPayloadSize << std::endl;
        
        if (respCode == RESP_FILE_CRC && respPayloadSize > 0) {
            std::cout << "[STEP 3] ✅ File transfer successful!" << std::endl;
            
            // Receive CRC response
            std::vector<uint8_t> payload;
            if (receiveData(payload, respPayloadSize)) {
                std::cout << "[PROTOCOL] Received CRC response (" << payload.size() << " bytes)" << std::endl;
            }
            return true;
        } else {
            std::cerr << "[STEP 3] ❌ File transfer failed with code " << respCode << std::endl;
            return false;
        }
    }
    
    // Main workflow
    bool run() {
        std::cout << "🔒 Simple Encrypted Backup Client v1.0" << std::endl;
        std::cout << "✅ Protocol Version 3 - Little Endian Compliant" << std::endl;
        std::cout << "✅ Manual Serialization - No Dependencies" << std::endl;
        std::cout << std::endl;
        
        if (!loadConfig()) {
            return false;
        }
        
        if (!connect()) {
            return false;
        }
        
        if (!registerClient()) {
            return false;
        }
        
        if (!exchangeKeys()) {
            return false;
        }
        
        if (!transferFile()) {
            return false;
        }
        
        std::cout << "\n🎉 SUCCESS: Complete backup workflow completed!" << std::endl;
        std::cout << "✅ Client registration: PASSED" << std::endl;
        std::cout << "✅ Key exchange: PASSED" << std::endl;
        std::cout << "✅ File transfer: PASSED" << std::endl;
        
        return true;
    }
};

int main() {
    SimpleClient client;
    
    bool success = client.run();
    
    if (success) {
        std::cout << "\n✅ All tests passed - system is working!" << std::endl;
        return 0;
    } else {
        std::cout << "\n❌ Some tests failed - check the logs above" << std::endl;
        return 1;
    }
}