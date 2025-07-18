#pragma once

#include <string>
#include <atomic>
#include <memory>
#include <functional>

/**
 * WebServerBackend - HTTP API Server for HTML Client Integration
 * 
 * Provides REST API endpoints for the HTML GUI client to communicate
 * with the C++ backup client. This class can be integrated into the
 * main client application without conflicting main() functions.
 */
class WebServerBackend {
private:
    class Impl; // Forward declaration for PIMPL idiom
    std::unique_ptr<Impl> pImpl_;
    
public:
    WebServerBackend();
    ~WebServerBackend();
    
    /**
     * Start the web server on the specified address and port
     * @param address IP address to bind to (default: "127.0.0.1")
     * @param port Port number to bind to (default: 9090)
     * @return true if server started successfully, false otherwise
     */
    bool start(const std::string& address = "127.0.0.1", unsigned short port = 9090);
    
    /**
     * Stop the web server and clean up resources
     */
    void stop();
    
    /**
     * Check if the web server is currently running
     * @return true if running, false otherwise
     */
    bool isRunning() const;

    /**
     * Set the backup callback function
     * @param callback Function to call for backup operations
     */
    void setBackupCallback(std::function<bool()> callback);
    
    // Non-copyable
    WebServerBackend(const WebServerBackend&) = delete;
    WebServerBackend& operator=(const WebServerBackend&) = delete;
    
    // Movable
    WebServerBackend(WebServerBackend&&) = default;
    WebServerBackend& operator=(WebServerBackend&&) = default;
};
