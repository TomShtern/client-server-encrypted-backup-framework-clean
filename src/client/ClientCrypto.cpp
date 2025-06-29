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
        displayStatus("RSA key generation", true, "1024-bit keys generated in " + std::to_string(duration) + "ms");
        return true;
    } catch (const std::exception& e) {
        displayError("Failed to generate RSA keys: " + std::string(e.what()), ErrorType::CRYPTO);
        return false;
    } catch (...) {
        displayError("Failed to generate RSA keys: Unknown exception", ErrorType::CRYPTO);
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
            displayStatus("Private key loaded", true, "From priv.key");
            return true;
        } catch (const std::exception& e) {
            displayStatus("Loading private key", false, std::string("Failed to parse priv.key: ") + e.what());
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
            displayStatus("Private key cached", true, "Saved to priv.key");
        }
        
        displayStatus("Private key loaded", true, "From me.info");
        return true;
    } catch (const std::exception& e) {
        displayStatus("Loading private key", false, std::string("Failed to decode from me.info: ") + e.what());
        if (rsaPrivate) {
            delete rsaPrivate;
            rsaPrivate = nullptr;
        }
        return false;
    }
}

bool Client::savePrivateKey() {
    if (!rsaPrivate) {
        displayError("No RSA private key to save", ErrorType::CRYPTO);
        return false;
    }
    
    try {
        std::string privateKey = rsaPrivate->getPrivateKey();
        std::ofstream file("priv.key", std::ios::binary);
        if (!file.is_open()) {
            displayError("Cannot create priv.key", ErrorType::FILE_IO);
            return false;
        }
        
        file.write(privateKey.c_str(), privateKey.length());
        file.close();
        
        if (file.good()) {
            displayStatus("Private key saved", true, "priv.key created (" + std::to_string(privateKey.length()) + " bytes)");
            return true;
        } else {
            displayError("Failed to write priv.key", ErrorType::FILE_IO);
            return false;
        }
    } catch (const std::exception& e) {
        displayError("Failed to save private key: " + std::string(e.what()), ErrorType::CRYPTO);
        return false;
    }
}

// === AES ENCRYPTION OPERATIONS ===

bool Client::decryptAESKey(const std::vector<uint8_t>& encryptedKey) {
    if (!rsaPrivate) {
        displayError("No RSA private key available", ErrorType::CRYPTO);
        return false;
    }
    
    try {
        std::string encrypted(reinterpret_cast<const char*>(encryptedKey.data()), encryptedKey.size());
        aesKey = rsaPrivate->decrypt(encrypted);
        
        if (aesKey.size() != AES_KEY_SIZE) {
            displayError("Invalid AES key size: " + std::to_string(aesKey.size()) + " bytes (expected " + 
                        std::to_string(AES_KEY_SIZE) + ")", ErrorType::CRYPTO);
            return false;
        }
        
        displayStatus("AES key decrypted", true, "256-bit key ready (" + std::to_string(aesKey.size()) + " bytes)");
        return true;
    } catch (const std::exception& e) {
        displayError("Failed to decrypt AES key: " + std::string(e.what()), ErrorType::CRYPTO);
        return false;
    } catch (...) {
        displayError("Failed to decrypt AES key: Unknown exception", ErrorType::CRYPTO);
        return false;
    }
}

std::string Client::encryptFile(const std::vector<uint8_t>& data) {
    if (aesKey.empty()) {
        displayError("No AES key available", ErrorType::CRYPTO);
        return "";
    }
    
    try {
        auto start = std::chrono::steady_clock::now();
        
        // Debug: Check actual AES key size
        displayStatus("AES key debug", true, "Key size: " + std::to_string(aesKey.size()) + " bytes");
        
        if (aesKey.size() != AES_KEY_SIZE) {
            displayError("Invalid AES key size: " + std::to_string(aesKey.size()) + " bytes (expected " + 
                        std::to_string(AES_KEY_SIZE) + ")", ErrorType::CRYPTO);
            return "";
        }
        
        // Use 32-byte key and static IV of all zeros for protocol compliance
        AESWrapper aes(reinterpret_cast<const unsigned char*>(aesKey.c_str()), AES_KEY_SIZE, true);
        std::string result = aes.encrypt(reinterpret_cast<const char*>(data.data()), data.size());
        
        auto end = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        double speed = (data.size() / 1024.0 / 1024.0) / (duration / 1000.0);
        
        displayStatus("Encryption performance", true, 
                     std::to_string(duration) + "ms (" + 
                     std::to_string(static_cast<int>(speed)) + " MB/s)");
        
        displayStatus("File encryption", true, "Original: " + formatBytes(data.size()) + 
                     ", Encrypted: " + formatBytes(result.size()));
        
        return result;
    } catch (const std::exception& e) {
        displayError("Failed to encrypt file: " + std::string(e.what()), ErrorType::CRYPTO);
        return "";
    } catch (...) {
        displayError("Failed to encrypt file: Unknown exception", ErrorType::CRYPTO);
        return "";
    }
}

// === KEY EXCHANGE OPERATIONS ===

bool Client::sendPublicKey() {
    if (!rsaPrivate) {
        displayError("No RSA keys available", ErrorType::CRYPTO);
        return false;
    }
    
    try {
        // Get the actual public key first
        std::string actualPublicKey = rsaPrivate->getPublicKey();
        
        displayStatus("Debug: Actual public key size", true, 
                     std::to_string(actualPublicKey.size()) + " bytes, expected " + std::to_string(RSA_KEY_SIZE) + " bytes");
        
        // Prepare payload with exactly 415 bytes (255 username + 160 RSA key)
        std::vector<uint8_t> payload(MAX_NAME_SIZE + RSA_KEY_SIZE, 0);
        
        // Add username (255 bytes, null-terminated, zero-padded)
        if (username.length() >= MAX_NAME_SIZE) {
            displayError("Username too long for public key payload", ErrorType::CONFIG);
            return false;
        }
        std::copy(username.begin(), username.end(), payload.begin());
        
        // Add public key - ensure exactly 160 bytes
        if (actualPublicKey.size() > RSA_KEY_SIZE) {
            // Truncate if too large
            displayStatus("Warning: Public key truncated", false, 
                         "From " + std::to_string(actualPublicKey.size()) + " to " + std::to_string(RSA_KEY_SIZE) + " bytes");
            std::copy(actualPublicKey.begin(), actualPublicKey.begin() + RSA_KEY_SIZE, payload.begin() + MAX_NAME_SIZE);
        } else {
            // Copy what we have and zero-pad the rest
            std::copy(actualPublicKey.begin(), actualPublicKey.end(), payload.begin() + MAX_NAME_SIZE);
            // Zero-padding is already done since payload was initialized with zeros
        }
        
        displayStatus("Sending public key", true, 
                     "Payload: " + std::to_string(payload.size()) + " bytes (" + 
                     std::to_string(MAX_NAME_SIZE) + " username + " + std::to_string(RSA_KEY_SIZE) + " RSA key)");
        
        // Debug: show exact payload construction
        displayStatus("Debug: Public key payload", true, 
                     "Size=" + std::to_string(payload.size()) + " bytes" +
                     ", Username='" + username + "' (" + std::to_string(username.length()) + " chars)" +
                     ", RSA key=" + std::to_string(actualPublicKey.size()) + " bytes (padded to " + 
                     std::to_string(RSA_KEY_SIZE) + ")");
        
        // Send request
        if (!sendRequest(REQ_SEND_PUBLIC_KEY, payload)) {
            displayError("Failed to send public key request", ErrorType::NETWORK);
            return false;
        }
        
        // Receive response
        ResponseHeader header;
        std::vector<uint8_t> responsePayload;
        if (!receiveResponse(header, responsePayload)) {
            displayError("Failed to receive public key response", ErrorType::NETWORK);
            return false;
        }
        
        if (header.code != RESP_PUBKEY_AES_SENT) {
            displayError("Invalid public key response code: " + std::to_string(header.code) + 
                        ", expected: " + std::to_string(RESP_PUBKEY_AES_SENT), ErrorType::PROTOCOL);
            return false;
        }
        
        if (responsePayload.size() <= CLIENT_ID_SIZE) {
            displayError("Invalid public key response payload size: " + std::to_string(responsePayload.size()) + 
                        " bytes, expected > " + std::to_string(CLIENT_ID_SIZE), ErrorType::PROTOCOL);
            return false;
        }
        
        // Extract encrypted AES key
        std::vector<uint8_t> encryptedKey(responsePayload.begin() + CLIENT_ID_SIZE, responsePayload.end());
        
        displayStatus("Received AES key", true, "Encrypted with RSA (" + std::to_string(encryptedKey.size()) + " bytes)");
        
        // Decrypt AES key
        if (!decryptAESKey(encryptedKey)) {
            displayError("Failed to decrypt received AES key", ErrorType::CRYPTO);
            return false;
        }
        
        displayStatus("Key exchange", true, "AES-256 key established successfully");
        return true;
        
    } catch (const std::exception& e) {
        displayError("Public key exchange failed: " + std::string(e.what()), ErrorType::CRYPTO);
        return false;
    } catch (...) {
        displayError("Public key exchange failed: Unknown exception", ErrorType::CRYPTO);
        return false;
    }
}