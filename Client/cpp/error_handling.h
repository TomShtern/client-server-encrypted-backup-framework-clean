#pragma once

#include <functional>
#include <string>
#include <iostream>
#include <chrono>
#include <thread>

// Error handling utility for spec-compliant retry logic
class RetryHandler {
public:
    // Execute operation with exactly 3 attempts and spec-compliant error messages
    template<typename T>
    static bool executeWithRetry(std::function<bool()> operation, const std::string& context) {
        for (int attempt = 1; attempt <= 3; ++attempt) {
            std::cout << "[RETRY] Attempt " << attempt << "/3 for " << context << std::endl;
            
            if (operation()) {
                if (attempt > 1) {
                    std::cout << "[SUCCESS] " << context << " succeeded on attempt " << attempt << std::endl;
                }
                return true;
            }
            
            // Spec-compliant error message (lowercase as required)
            std::cout << "server responded with an error" << std::endl;
            
            if (attempt == 3) {
                // Final failure message as per spec
                std::cout << "Fatal error: " << context << " after 3 attempts." << std::endl;
                return false;
            }
            
            // Brief delay between retries (not required by spec but good practice)
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
        
        return false; // Should never reach here
    }
    
    // Network operation retry wrapper
    static bool retryNetworkOperation(std::function<bool()> networkOp, const std::string& operationName) {
        return executeWithRetry<bool>(networkOp, operationName);
    }
    
    // File operation retry wrapper
    static bool retryFileOperation(std::function<bool()> fileOp, const std::string& operationName) {
        return executeWithRetry<bool>(fileOp, operationName);
    }
    
    // Protocol operation retry wrapper
    static bool retryProtocolOperation(std::function<bool()> protocolOp, const std::string& operationName) {
        return executeWithRetry<bool>(protocolOp, operationName);
    }
};

// Specific error handling for CRC verification (up to 3 CRC retries)
class CRCRetryHandler {
private:
    int attempts = 0;
    static const int MAX_CRC_ATTEMPTS = 3;
    
public:
    enum class CRCResult {
        SUCCESS,        // CRC matches
        RETRY_NEEDED,   // CRC mismatch, can retry
        FATAL_FAILURE   // CRC mismatch after 3 attempts
    };
    
    CRCResult handleCRCCheck(bool crcMatches, const std::string& filename) {
        attempts++;
        
        if (crcMatches) {
            if (attempts > 1) {
                std::cout << "[CRC SUCCESS] File " << filename << " verified on attempt " << attempts << std::endl;
            }
            return CRCResult::SUCCESS;
        }
        
        std::cout << "[CRC MISMATCH] File " << filename << " failed CRC check (attempt " 
                  << attempts << "/" << MAX_CRC_ATTEMPTS << ")" << std::endl;
        
        if (attempts >= MAX_CRC_ATTEMPTS) {
            std::cout << "Fatal error: CRC verification for " << filename 
                      << " failed after 3 attempts." << std::endl;
            return CRCResult::FATAL_FAILURE;
        }
        
        return CRCResult::RETRY_NEEDED;
    }
    
    void reset() {
        attempts = 0;
    }
    
    int getAttemptCount() const {
        return attempts;
    }
};

// Connection error handling
class ConnectionHandler {
public:
    static bool retryConnection(std::function<bool()> connectOp, const std::string& serverInfo) {
        return RetryHandler::executeWithRetry<bool>(connectOp, "connection to " + serverInfo);
    }
    
    static bool retryRegistration(std::function<bool()> regOp, const std::string& username) {
        return RetryHandler::executeWithRetry<bool>(regOp, "registration for user " + username);
    }
    
    static bool retryKeyExchange(std::function<bool()> keyOp) {
        return RetryHandler::executeWithRetry<bool>(keyOp, "key exchange");
    }
    
    static bool retryFileTransfer(std::function<bool()> transferOp, const std::string& filename) {
        return RetryHandler::executeWithRetry<bool>(transferOp, "file transfer for " + filename);
    }
};