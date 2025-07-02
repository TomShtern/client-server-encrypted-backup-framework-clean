// ClientCrypto.cpp
// Enhanced Client Cryptographic Operations
// Contains RSA key management, AES encryption, and cryptographic utilities

#include "../../include/client/ClientCore.h"

// === RSA KEY MANAGEMENT ===

bool Client::generateRSAKeys() {
    std::cout << "[DEBUG] Client::generateRSAKeys() - Starting RSA key generation" << std::endl;
    try {
        std::cout << "[DEBUG] Client::generateRSAKeys() - About to create RSAPrivateWrapper" << std::endl;
        auto start = std::chrono::steady_clock::now();
        rsaPrivate = new RSAPrivateWrapper();
        std::cout << "[DEBUG] Client::generateRSAKeys() - RSAPrivateWrapper created successfully" << std::endl;
        auto end = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        std::cout << "[INFO] RSA key generation: 1024-bit keys generated in " << duration << "ms" << std::endl;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to generate RSA keys: " << e.what() << std::endl;
        return false;
    } catch (...) {
        std::cerr << "[ERROR] Failed to generate RSA keys: Unknown exception" << std::endl;
        return false;
    }
}

bool Client::loadPrivateKey() {
    // Try priv.key first (binary DER format)
    std::ifstream keyFile("priv.key", std::ios::binary);
    if (keyFile.is_open()) {
        std::string keyData((std::istreambuf_iterator<char>(keyFile)), std::istreambuf_iterator<char>());
        keyFile.close();
        
        try {
            // priv.key contains binary DER data, use the char* constructor
            rsaPrivate = new RSAPrivateWrapper(keyData.c_str(), keyData.length());
            std::cout << "[INFO] Private key loaded: From priv.key" << std::endl;
            return true;
        } catch (const std::exception& e) {
            std::cerr << "[ERROR] Loading private key: Failed to parse priv.key: " << e.what() << std::endl;
            delete rsaPrivate;
            rsaPrivate = nullptr;
        }
    }
    
    // Try me.info (Base64 encoded format)
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
        
        // Save to priv.key for faster loading next time
        std::ofstream privKey("priv.key", std::ios::binary);
        if (privKey.is_open()) {
            privKey.write(decoded.c_str(), decoded.length());
            std::cout << "[INFO] Private key cached: Saved to priv.key" << std::endl;
        }
        
        std::cout << "[INFO] Private key loaded: From me.info" << std::endl;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Loading private key: Failed to decode from me.info: " << e.what() << std::endl;
        if (rsaPrivate) {
            delete rsaPrivate;
            rsaPrivate = nullptr;
        }
        return false;
    }
}

bool Client::savePrivateKey() {
    if (!rsaPrivate) {
        std::cerr << "[ERROR] No RSA private key to save" << std::endl;
        return false;
    }
    
    try {
        std::string privateKey = rsaPrivate->getPrivateKey();
        std::ofstream file("priv.key", std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "[ERROR] Cannot create priv.key" << std::endl;
            return false;
        }
        
        file.write(privateKey.c_str(), privateKey.length());
        file.close();
        
        if (file.good()) {
            std::cout << "[INFO] Private key saved: priv.key created (" << privateKey.length() << " bytes)" << std::endl;
            return true;
        } else {
            std::cerr << "[ERROR] Failed to write priv.key" << std::endl;
            return false;
        }
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to save private key: " << e.what() << std::endl;
        return false;
    }
}

// === AES ENCRYPTION OPERATIONS ===

bool Client::decryptAESKey(const std::vector<uint8_t>& encryptedKey) {
    if (!rsaPrivate) {
        std::cerr << "[ERROR] No RSA private key available" << std::endl;
        return false;
    }
    
    try {
        std::string encrypted(reinterpret_cast<const char*>(encryptedKey.data()), encryptedKey.size());
        aesKey = rsaPrivate->decrypt(encrypted);
        
        if (aesKey.size() != AES_KEY_SIZE) {
            std::cerr << "[ERROR] Invalid AES key size: " << aesKey.size() << " bytes (expected " << AES_KEY_SIZE << ")" << std::endl;
            return false;
        }
        
        std::cout << "[INFO] AES key decrypted: 256-bit key ready (" << aesKey.size() << " bytes)" << std::endl;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to decrypt AES key: " << e.what() << std::endl;
        return false;
    } catch (...) {
        std::cerr << "[ERROR] Failed to decrypt AES key: Unknown exception" << std::endl;
        return false;
    }
}

std::string Client::encryptFile(const std::vector<uint8_t>& data) {
    if (aesKey.empty()) {
        std::cerr << "[ERROR] No AES key available" << std::endl;
        return "";
    }
    
    try {
        auto start = std::chrono::steady_clock::now();
        
        // Debug: Check actual AES key size
        std::cout << "[DEBUG] AES key debug: Key size: " << aesKey.size() << " bytes" << std::endl;
        
        if (aesKey.size() != AES_KEY_SIZE) {
            std::cerr << "[ERROR] Invalid AES key size: " << aesKey.size() << " bytes (expected " << AES_KEY_SIZE << ")" << std::endl;
            return "";
        }
        
        // Use 32-byte key and static IV of all zeros for protocol compliance
        AESWrapper aes(reinterpret_cast<const unsigned char*>(aesKey.c_str()), AES_KEY_SIZE, true);
        std::string result = aes.encrypt(reinterpret_cast<const char*>(data.data()), data.size());
        
        auto end = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        double speed = (data.size() / 1024.0 / 1024.0) / (duration / 1000.0);
        
        std::cout << "[INFO] Encryption performance: " << duration << "ms (" << static_cast<int>(speed) << " MB/s)" << std::endl;
        
        std::cout << "[INFO] File encryption: Original: " << formatBytes(data.size()) << ", Encrypted: " << formatBytes(result.size()) << std::endl;
        
        return result;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Failed to encrypt file: " << e.what() << std::endl;
        return "";
    } catch (...) {
        std::cerr << "[ERROR] Failed to encrypt file: Unknown exception" << std::endl;
        return "";
    }
}

// === KEY EXCHANGE OPERATIONS ===

bool Client::sendPublicKey() {
    if (!rsaPrivate) {
        std::cerr << "[ERROR] No RSA keys available" << std::endl;
        return false;
    }
    
    try {
        // Get the actual public key first
        std::string actualPublicKey = rsaPrivate->getPublicKey();
        
        std::cout << "[DEBUG] Actual public key size: " << actualPublicKey.size() << " bytes, expected " << RSA_KEY_SIZE << " bytes" << std::endl;
        
        // Prepare payload with exactly 415 bytes (255 username + 160 RSA key)
        std::vector<uint8_t> payload(MAX_NAME_SIZE + RSA_KEY_SIZE, 0);
        
        // Add username (255 bytes, null-terminated, zero-padded)
        if (username.length() >= MAX_NAME_SIZE) {
            std::cerr << "[ERROR] Username too long for public key payload" << std::endl;
            return false;
        }
        std::copy(username.begin(), username.end(), payload.begin());
        
        // Add public key - ensure exactly 160 bytes
        if (actualPublicKey.size() > RSA_KEY_SIZE) {
            // Truncate if too large
            std::cout << "[WARNING] Public key truncated: From " << actualPublicKey.size() << " to " << RSA_KEY_SIZE << " bytes" << std::endl;
            std::copy(actualPublicKey.begin(), actualPublicKey.begin() + RSA_KEY_SIZE, payload.begin() + MAX_NAME_SIZE);
        } else {
            // Copy what we have and zero-pad the rest
            std::copy(actualPublicKey.begin(), actualPublicKey.end(), payload.begin() + MAX_NAME_SIZE);
            // Zero-padding is already done since payload was initialized with zeros
        }
        
        std::cout << "[INFO] Sending public key: Payload: " << payload.size() << " bytes (" << MAX_NAME_SIZE << " username + " << RSA_KEY_SIZE << " RSA key)" << std::endl;
        
        // Debug: show exact payload construction
        std::cout << "[DEBUG] Public key payload: Size=" << payload.size() << " bytes, Username='" << username << "' (" << username.length() << " chars), RSA key=" << actualPublicKey.size() << " bytes (padded to " << RSA_KEY_SIZE << ")" << std::endl;
        
        // Send request
        if (!sendRequest(REQ_SEND_PUBLIC_KEY, payload)) {
            std::cerr << "[ERROR] Failed to send public key request" << std::endl;
            return false;
        }
        
        // Receive response
        ResponseHeader header;
        std::vector<uint8_t> responsePayload;
        if (!receiveResponse(header, responsePayload)) {
            std::cerr << "[ERROR] Failed to receive public key response" << std::endl;
            return false;
        }
        
        if (header.code != RESP_PUBKEY_AES_SENT) {
            std::cerr << "[ERROR] Invalid public key response code: " << header.code << ", expected: " << RESP_PUBKEY_AES_SENT << std::endl;
            return false;
        }
        
        if (responsePayload.size() <= CLIENT_ID_SIZE) {
            std::cerr << "[ERROR] Invalid public key response payload size: " << responsePayload.size() << " bytes, expected > " << CLIENT_ID_SIZE << std::endl;
            return false;
        }
        
        // Extract encrypted AES key
        std::vector<uint8_t> encryptedKey(responsePayload.begin() + CLIENT_ID_SIZE, responsePayload.end());
        
        std::cout << "[INFO] Received AES key: Encrypted with RSA (" << encryptedKey.size() << " bytes)" << std::endl;
        
        // Decrypt AES key
        if (!decryptAESKey(encryptedKey)) {
            std::cerr << "[ERROR] Failed to decrypt received AES key" << std::endl;
            return false;
        }
        
        std::cout << "[INFO] Key exchange: AES-256 key established successfully" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] Public key exchange failed: " << e.what() << std::endl;
        return false;
    } catch (...) {
        std::cerr << "[ERROR] Public key exchange failed: Unknown exception" << std::endl;
        return false;
    }
}