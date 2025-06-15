// Simplified client.cpp that replaces boost with simple networking
// and focuses only on the core backup functionality

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <array>
#include <cstring>
#include <chrono>
#include <thread>

// Simple networking instead of boost
#include "../../client_simple_net.h"

// Required wrapper includes
#include "../../include/client/cksum.h"
#include "../../include/wrappers/AESWrapper.h"
#include "../../include/wrappers/Base64Wrapper.h"
#include "../../include/wrappers/RSAWrapper.h"

// Protocol constants
constexpr uint8_t CLIENT_VERSION = 3;
constexpr uint16_t REQ_REGISTER = 1025;
constexpr uint16_t REQ_SEND_PUBLIC_KEY = 1026;
constexpr uint16_t REQ_SEND_FILE = 1028;
constexpr uint16_t RESP_REGISTER_OK = 1600;
constexpr uint16_t RESP_PUBKEY_AES_SENT = 1602;
constexpr uint16_t RESP_FILE_OK = 1603;
constexpr size_t CLIENT_ID_SIZE = 16;
constexpr size_t MAX_NAME_SIZE = 255;
constexpr size_t AES_KEY_SIZE = 32;

class SimpleClient {
private:
    SimpleSocket socket;
    std::string serverIP;
    uint16_t serverPort;
    std::array<uint8_t, CLIENT_ID_SIZE> clientID;
    std::string username;
    std::string filepath;
    RSAPrivateWrapper* rsaPrivate;
    std::string aesKey;
    
public:
    SimpleClient() : rsaPrivate(nullptr) {}
    ~SimpleClient() { if (rsaPrivate) delete rsaPrivate; }
    
    bool initialize() {
        std::cout << "Initializing Simple Client..." << std::endl;
        
        // Read transfer.info
        std::ifstream file("transfer.info");
        if (!file.is_open()) {
            std::cerr << "Cannot open transfer.info" << std::endl;
            return false;
        }
        
        std::string serverInfo;
        std::getline(file, serverInfo);
        std::getline(file, username);
        std::getline(file, filepath);
        file.close();
        
        // Parse server:port
        size_t colonPos = serverInfo.find(':');
        if (colonPos != std::string::npos) {
            serverIP = serverInfo.substr(0, colonPos);
            serverPort = std::stoi(serverInfo.substr(colonPos + 1));
        } else {
            serverIP = serverInfo;
            serverPort = 1256;
        }
        
        std::cout << "Server: " << serverIP << ":" << serverPort << std::endl;
        std::cout << "Username: " << username << std::endl;
        std::cout << "File: " << filepath << std::endl;
        
        // Initialize RSA keys
        std::cout << "Loading RSA keys..." << std::endl;
        try {
            rsaPrivate = new RSAPrivateWrapper();
            std::cout << "RSA keys ready!" << std::endl;
            return true;
        } catch (const std::exception& e) {
            std::cerr << "RSA key generation failed: " << e.what() << std::endl;
            return false;
        }
    }
    
    bool run() {
        std::cout << "Starting backup operation..." << std::endl;
        
        // Connect to server
        std::cout << "Connecting to server..." << std::endl;
        if (!socket.connect(serverIP, serverPort)) {
            std::cerr << "Failed to connect to server" << std::endl;
            return false;
        }
        std::cout << "Connected successfully!" << std::endl;
        
        // Register client
        if (!registerClient()) return false;
        
        // Exchange keys
        if (!exchangeKeys()) return false;
        
        // Transfer file
        if (!transferFile()) return false;
        
        std::cout << "Backup completed successfully!" << std::endl;
        return true;
    }
    
private:
    bool registerClient() {
        std::cout << "Registering client..." << std::endl;
        
        // Generate random client ID
        for (size_t i = 0; i < CLIENT_ID_SIZE; ++i) {
            clientID[i] = rand() % 256;
        }
        
        // Create request
        std::vector<uint8_t> request;
        
        // Header: client_id(16) + version(1) + code(2) + payload_size(4)
        request.insert(request.end(), clientID.begin(), clientID.end());
        request.push_back(CLIENT_VERSION);
        request.push_back(REQ_REGISTER & 0xFF);
        request.push_back((REQ_REGISTER >> 8) & 0xFF);
        request.push_back(MAX_NAME_SIZE & 0xFF);
        request.push_back((MAX_NAME_SIZE >> 8) & 0xFF);
        request.push_back((MAX_NAME_SIZE >> 16) & 0xFF);
        request.push_back((MAX_NAME_SIZE >> 24) & 0xFF);
        
        // Payload: username (255 bytes, padded)
        std::vector<uint8_t> usernameField(MAX_NAME_SIZE, 0);
        size_t copySize = std::min(username.size(), MAX_NAME_SIZE - 1);
        std::memcpy(usernameField.data(), username.c_str(), copySize);
        request.insert(request.end(), usernameField.begin(), usernameField.end());
        
        // Send request
        if (!socket.send(request.data(), request.size())) {
            std::cerr << "Failed to send registration request" << std::endl;
            return false;
        }
        
        // Receive response
        uint8_t responseHeader[7];
        if (!socket.receive(responseHeader, 7)) {
            std::cerr << "Failed to receive registration response" << std::endl;
            return false;
        }
        
        uint16_t respCode = responseHeader[1] | (responseHeader[2] << 8);
        if (respCode == RESP_REGISTER_OK) {
            std::cout << "Registration successful!" << std::endl;
            return true;
        } else {
            std::cerr << "Registration failed with code " << respCode << std::endl;
            return false;
        }
    }
    
    bool exchangeKeys() {
        std::cout << "Exchanging keys..." << std::endl;
        
        // Get public key
        std::string publicKey = rsaPrivate->getPublicKey();
        std::cout << "Public key size: " << publicKey.size() << " bytes" << std::endl;
        
        // Create request
        std::vector<uint8_t> request;
        
        // Header
        request.insert(request.end(), clientID.begin(), clientID.end());
        request.push_back(CLIENT_VERSION);
        request.push_back(REQ_SEND_PUBLIC_KEY & 0xFF);
        request.push_back((REQ_SEND_PUBLIC_KEY >> 8) & 0xFF);
        
        uint32_t payloadSize = MAX_NAME_SIZE + publicKey.size();
        request.push_back(payloadSize & 0xFF);
        request.push_back((payloadSize >> 8) & 0xFF);
        request.push_back((payloadSize >> 16) & 0xFF);
        request.push_back((payloadSize >> 24) & 0xFF);
        
        // Payload: username + public key
        std::vector<uint8_t> usernameField(MAX_NAME_SIZE, 0);
        size_t copySize = std::min(username.size(), MAX_NAME_SIZE - 1);
        std::memcpy(usernameField.data(), username.c_str(), copySize);
        request.insert(request.end(), usernameField.begin(), usernameField.end());
        request.insert(request.end(), publicKey.begin(), publicKey.end());
        
        // Send request
        if (!socket.send(request.data(), request.size())) {
            std::cerr << "Failed to send key exchange request" << std::endl;
            return false;
        }
        
        // Receive response
        uint8_t responseHeader[7];
        if (!socket.receive(responseHeader, 7)) {
            std::cerr << "Failed to receive key exchange response header" << std::endl;
            return false;
        }
        
        uint16_t respCode = responseHeader[1] | (responseHeader[2] << 8);
        uint32_t payloadSizeResp = responseHeader[3] | (responseHeader[4] << 8) | (responseHeader[5] << 16) | (responseHeader[6] << 24);
        
        if (respCode == RESP_PUBKEY_AES_SENT && payloadSizeResp > 0) {
            // Receive encrypted AES key
            std::vector<uint8_t> payload(payloadSizeResp);
            if (!socket.receive(payload.data(), payloadSizeResp)) {
                std::cerr << "Failed to receive encrypted AES key" << std::endl;
                return false;
            }
            
            // Skip client ID and decrypt AES key
            std::vector<uint8_t> encryptedAESKey(payload.begin() + CLIENT_ID_SIZE, payload.end());
            
            try {
                std::string encrypted(reinterpret_cast<const char*>(encryptedAESKey.data()), encryptedAESKey.size());
                aesKey = rsaPrivate->decrypt(encrypted);
                
                if (aesKey.size() == AES_KEY_SIZE) {
                    std::cout << "AES key decrypted successfully!" << std::endl;
                    return true;
                } else {
                    std::cerr << "Invalid AES key size: " << aesKey.size() << std::endl;
                    return false;
                }
            } catch (const std::exception& e) {
                std::cerr << "AES key decryption failed: " << e.what() << std::endl;
                return false;
            }
        } else {
            std::cerr << "Key exchange failed with code " << respCode << std::endl;
            return false;
        }
    }
    
    bool transferFile() {
        std::cout << "Transferring file..." << std::endl;
        
        // Read file
        std::ifstream file(filepath, std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "Cannot open file: " << filepath << std::endl;
            return false;
        }
        
        std::vector<uint8_t> fileData((std::istreambuf_iterator<char>(file)),
                                     std::istreambuf_iterator<char>());
        file.close();
        
        std::cout << "File size: " << fileData.size() << " bytes" << std::endl;
        
        // Encrypt file data
        try {
            AESWrapper aes(reinterpret_cast<const unsigned char*>(aesKey.c_str()), 32, true);
            std::string encryptedData = aes.encrypt(reinterpret_cast<const char*>(fileData.data()), fileData.size());
            
            std::cout << "File encrypted: " << fileData.size() << " → " << encryptedData.size() << " bytes" << std::endl;
            
            // Extract filename
            std::string filename = filepath;
            size_t lastSlash = filename.find_last_of("/\\");
            if (lastSlash != std::string::npos) {
                filename = filename.substr(lastSlash + 1);
            }
            
            // Create file transfer request
            std::vector<uint8_t> request;
            
            // Header
            request.insert(request.end(), clientID.begin(), clientID.end());
            request.push_back(CLIENT_VERSION);
            request.push_back(REQ_SEND_FILE & 0xFF);
            request.push_back((REQ_SEND_FILE >> 8) & 0xFF);
            
            uint32_t payloadSize = 4 + 4 + 2 + 2 + MAX_NAME_SIZE + encryptedData.size();
            request.push_back(payloadSize & 0xFF);
            request.push_back((payloadSize >> 8) & 0xFF);
            request.push_back((payloadSize >> 16) & 0xFF);
            request.push_back((payloadSize >> 24) & 0xFF);
            
            // Payload
            uint32_t contentSize = encryptedData.size();
            request.push_back(contentSize & 0xFF);
            request.push_back((contentSize >> 8) & 0xFF);
            request.push_back((contentSize >> 16) & 0xFF);
            request.push_back((contentSize >> 24) & 0xFF);
            
            uint32_t origSize = fileData.size();
            request.push_back(origSize & 0xFF);
            request.push_back((origSize >> 8) & 0xFF);
            request.push_back((origSize >> 16) & 0xFF);
            request.push_back((origSize >> 24) & 0xFF);
            
            request.push_back(1); // packet number (low byte)
            request.push_back(0); // packet number (high byte)
            request.push_back(1); // total packets (low byte)
            request.push_back(0); // total packets (high byte)
            
            // Filename
            std::vector<uint8_t> filenameField(MAX_NAME_SIZE, 0);
            size_t copySize = std::min(filename.size(), MAX_NAME_SIZE - 1);
            std::memcpy(filenameField.data(), filename.c_str(), copySize);
            request.insert(request.end(), filenameField.begin(), filenameField.end());
            
            // Encrypted file data
            request.insert(request.end(), encryptedData.begin(), encryptedData.end());
            
            // Send request
            if (!socket.send(request.data(), request.size())) {
                std::cerr << "Failed to send file transfer request" << std::endl;
                return false;
            }
            
            // Receive response
            uint8_t responseHeader[7];
            if (!socket.receive(responseHeader, 7)) {
                std::cerr << "Failed to receive file transfer response" << std::endl;
                return false;
            }
            
            uint16_t respCode = responseHeader[1] | (responseHeader[2] << 8);
            if (respCode == RESP_FILE_OK) {
                std::cout << "File transfer successful!" << std::endl;
                return true;
            } else {
                std::cerr << "File transfer failed with code " << respCode << std::endl;
                return false;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "File encryption failed: " << e.what() << std::endl;
            return false;
        }
    }
};

bool runBackupClient() {
    SimpleClient client;
    if (!client.initialize()) return false;
    return client.run();
}