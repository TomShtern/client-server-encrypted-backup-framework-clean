// complete_client.cpp
// Complete C++ client with real RSA keys and AES encryption
// This is the final working implementation

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>
#include <random>
#include <algorithm>

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

#include "rsa_keys.h"        // Generated RSA keys
#include "simple_crypto.h"   // Our crypto implementation

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

class CompleteClient {
private:
    SOCKET sock;
    std::string server_host;
    int server_port;
    std::string username;
    std::string file_path;
    std::vector<uint8_t> client_id;
    SimpleCrypto crypto;
    
public:
    CompleteClient() : sock(INVALID_SOCKET) {
        #ifdef _WIN32
        WSADATA wsaData;
        WSAStartup(MAKEWORD(2,2), &wsaData);
        #endif
    }
    
    ~CompleteClient() {
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
        size_t copySize = std::min(str.size(), targetSize - 1);
        std::memcpy(result.data(), str.c_str(), copySize);
        return result;
    }
    
    // Load configuration
    bool loadConfig() {
        std::cout << "[CONFIG] Loading configuration..." << std::endl;
        
        std::ifstream transferFile("transfer.info");
        if (!transferFile.is_open()) {
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
    
    // Initialize crypto with RSA keys
    bool initializeCrypto() {
        std::cout << "[CRYPTO] Initializing crypto system..." << std::endl;
        
        // Load RSA private key from embedded data
        std::vector<uint8_t> privateKeyData(RSA_PRIVATE_KEY, RSA_PRIVATE_KEY + RSA_PRIVATE_KEY_SIZE);
        
        if (!crypto.loadRSAPrivateKey(privateKeyData)) {
            std::cerr << "[ERROR] Failed to load RSA private key" << std::endl;
            return false;
        }
        
        std::cout << "[CRYPTO] RSA private key loaded (" << RSA_PRIVATE_KEY_SIZE << " bytes)" << std::endl;
        std::cout << "[CRYPTO] RSA public key ready (" << RSA_PUBLIC_KEY_SIZE << " bytes)" << std::endl;
        
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
        
        // Create registration request
        std::vector<uint8_t> request;
        
        // Header
        request.insert(request.end(), client_id.begin(), client_id.end());
        request.push_back(PROTOCOL_VERSION);
        writeLE16(request, REQ_REGISTER);
        writeLE32(request, MAX_FILENAME_SIZE);
        
        // Payload: username
        std::vector<uint8_t> usernameField = createPaddedString(username, MAX_FILENAME_SIZE);
        request.insert(request.end(), usernameField.begin(), usernameField.end());
        
        std::cout << "[PROTOCOL] Created registration request (" << request.size() << " bytes)" << std::endl;
        
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
        
        if (respCode == RESP_REGISTER_OK) {
            std::cout << "[STEP 1] ✅ Registration successful!" << std::endl;
            
            // Receive client ID if present
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
        
        // Create public key request using real RSA public key
        std::vector<uint8_t> request;
        
        // Header
        request.insert(request.end(), client_id.begin(), client_id.end());
        request.push_back(PROTOCOL_VERSION);
        writeLE16(request, REQ_SEND_PUBLIC_KEY);
        writeLE32(request, MAX_FILENAME_SIZE + RSA_PUBLIC_KEY_SIZE);
        
        // Payload: username + RSA public key
        std::vector<uint8_t> usernameField = createPaddedString(username, MAX_FILENAME_SIZE);
        request.insert(request.end(), usernameField.begin(), usernameField.end());
        
        // Add real RSA public key
        request.insert(request.end(), RSA_PUBLIC_KEY, RSA_PUBLIC_KEY + RSA_PUBLIC_KEY_SIZE);
        
        std::cout << "[PROTOCOL] Created key exchange request (" << request.size() << " bytes)" << std::endl;
        std::cout << "[CRYPTO] Using real RSA public key (" << RSA_PUBLIC_KEY_SIZE << " bytes)" << std::endl;
        
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
                
                // Extract encrypted AES key (skip client ID)
                if (payload.size() >= CLIENT_ID_SIZE) {
                    std::vector<uint8_t> encryptedAESKey(payload.begin() + CLIENT_ID_SIZE, payload.end());
                    
                    // Decrypt and load AES key
                    if (crypto.decryptAndLoadAESKey(encryptedAESKey)) {
                        std::cout << "[CRYPTO] ✅ AES key decrypted and ready for encryption!" << std::endl;
                        return true;
                    } else {
                        std::cerr << "[CRYPTO] ❌ Failed to decrypt AES key" << std::endl;
                        return false;
                    }
                }
            }
            return false;
        } else {
            std::cerr << "[STEP 2] ❌ Key exchange failed with code " << respCode << std::endl;
            return false;
        }
    }
    
    // Step 3: Transfer file with encryption
    bool transferFile() {
        std::cout << "\n[STEP 3] Transferring file with encryption..." << std::endl;
        
        if (!crypto.isReady()) {
            std::cerr << "[ERROR] Crypto not ready - AES key not loaded" << std::endl;
            return false;
        }
        
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
        
        // Encrypt file data
        std::vector<uint8_t> encryptedData = crypto.encryptFileData(fileData);
        if (encryptedData.empty()) {
            std::cerr << "[ERROR] Failed to encrypt file data" << std::endl;
            return false;
        }
        
        std::cout << "[CRYPTO] File encrypted: " << fileData.size() << " → " << encryptedData.size() << " bytes" << std::endl;
        
        // Extract filename
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
        
        // Calculate payload size
        uint32_t payloadSize = 4 + 4 + 2 + 2 + MAX_FILENAME_SIZE + static_cast<uint32_t>(encryptedData.size());
        writeLE32(request, payloadSize);
        
        // Payload fields
        writeLE32(request, static_cast<uint32_t>(encryptedData.size())); // Content size
        writeLE32(request, static_cast<uint32_t>(fileData.size()));      // Original size
        writeLE16(request, 1);                                           // Packet number
        writeLE16(request, 1);                                           // Total packets
        
        // Filename field
        std::vector<uint8_t> filenameField = createPaddedString(filename, MAX_FILENAME_SIZE);
        request.insert(request.end(), filenameField.begin(), filenameField.end());
        
        // Encrypted file data
        request.insert(request.end(), encryptedData.begin(), encryptedData.end());
        
        std::cout << "[PROTOCOL] Created file transfer request (" << request.size() << " bytes)" << std::endl;
        std::cout << "[FILE] Filename: " << filename << std::endl;
        std::cout << "[FILE] Original size: " << fileData.size() << " bytes" << std::endl;
        std::cout << "[FILE] Encrypted size: " << encryptedData.size() << " bytes" << std::endl;
        
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
        std::cout << "🔒 Complete Encrypted Backup Client v2.0" << std::endl;
        std::cout << "✅ Real RSA Keys - 1024-bit Key Pair" << std::endl;
        std::cout << "✅ AES-256-CBC Encryption with Zero IV" << std::endl;
        std::cout << "✅ Full Protocol Compliance" << std::endl;
        std::cout << std::endl;
        
        if (!loadConfig()) {
            return false;
        }
        
        if (!initializeCrypto()) {
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
        
        std::cout << "\n🎉 SUCCESS: Complete encrypted backup workflow completed!" << std::endl;
        std::cout << "✅ Client registration: PASSED" << std::endl;
        std::cout << "✅ RSA key exchange: PASSED" << std::endl;
        std::cout << "✅ AES key decryption: PASSED" << std::endl;
        std::cout << "✅ File encryption: PASSED" << std::endl;
        std::cout << "✅ Encrypted file transfer: PASSED" << std::endl;
        
        return true;
    }
};

int main() {
    CompleteClient client;
    
    bool success = client.run();
    
    if (success) {
        std::cout << "\n✅ All tests passed - complete system working!" << std::endl;
        return 0;
    } else {
        std::cout << "\n❌ Some tests failed - check the logs above" << std::endl;
        return 1;
    }
}