// ClientWebSocketServer.h
// WebSocket server using Boost.Beast (built on Boost.Asio)

#ifndef CLIENT_WEBSOCKET_SERVER_H
#define CLIENT_WEBSOCKET_SERVER_H

#include <boost/beast/core.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/strand.hpp>
#include <thread>
#include <mutex>
#include <set>
#include <memory>
#include <string>
#include <sstream>
#include <functional>
#include <atomic>
#include <map>
#ifdef _WIN32
#include <shellapi.h>
#endif

namespace beast = boost::beast;
namespace websocket = beast::websocket;
namespace net = boost::asio;
using tcp = net::ip::tcp;

// Simple JSON builder for our needs (no external dependency)
class SimpleJSON {
public:
    SimpleJSON() : first(true) { ss << "{"; }
    
    SimpleJSON& add(const std::string& key, const std::string& value) {
        if (!first) ss << ",";
        ss << "\"" << key << "\":\"" << escape(value) << "\"";
        first = false;
        return *this;
    }
    
    SimpleJSON& add(const std::string& key, int value) {
        if (!first) ss << ",";
        ss << "\"" << key << "\":" << value;
        first = false;
        return *this;
    }
    
    SimpleJSON& add(const std::string& key, bool value) {
        if (!first) ss << ",";
        ss << "\"" << key << "\":" << (value ? "true" : "false");
        first = false;
        return *this;
    }
    
    SimpleJSON& add(const std::string& key, double value) {
        if (!first) ss << ",";
        ss << "\"" << key << "\":" << value;
        first = false;
        return *this;
    }
    
    SimpleJSON& add(const std::string& key, size_t value) {
        if (!first) ss << ",";
        ss << "\"" << key << "\":" << value;
        first = false;
        return *this;
    }
    
    std::string str() const { return ss.str() + "}"; }
    
private:
    std::stringstream ss;
    bool first;
    
    std::string escape(const std::string& s) {
        std::string result;
        for (char c : s) {
            switch (c) {
                case '"': result += "\\\""; break;
                case '\\': result += "\\\\"; break;
                case '\n': result += "\\n"; break;
                case '\r': result += "\\r"; break;
                case '\t': result += "\\t"; break;
                default: result += c;
            }
        }
        return result;
    }
};

// Simple JSON parser for incoming messages
class SimpleJSONParser {
public:
    static std::map<std::string, std::string> parse(const std::string& json) {
        std::map<std::string, std::string> result;
        
        // Very basic parser - just extract "type" and simple values
        size_t pos = 0;
        while ((pos = json.find("\"", pos)) != std::string::npos) {
            size_t keyStart = pos + 1;
            size_t keyEnd = json.find("\"", keyStart);
            if (keyEnd == std::string::npos) break;
            
            std::string key = json.substr(keyStart, keyEnd - keyStart);
            
            pos = json.find(":", keyEnd);
            if (pos == std::string::npos) break;
            pos++;
            
            // Skip whitespace
            while (pos < json.length() && std::isspace(json[pos])) pos++;
            
            if (json[pos] == '"') {
                // String value
                size_t valueStart = pos + 1;
                size_t valueEnd = json.find("\"", valueStart);
                if (valueEnd != std::string::npos) {
                    result[key] = json.substr(valueStart, valueEnd - valueStart);
                    pos = valueEnd + 1;
                }
            } else {
                // Number or boolean
                size_t valueEnd = json.find_first_of(",}", pos);
                if (valueEnd != std::string::npos) {
                    std::string value = json.substr(pos, valueEnd - pos);
                    // Trim whitespace
                    value.erase(0, value.find_first_not_of(" \n\r\t"));
                    value.erase(value.find_last_not_of(" \n\r\t") + 1);
                    result[key] = value;
                    pos = valueEnd;
                }
            }
        }
        
        return result;
    }
};

// WebSocket session
class WebSocketSession : public std::enable_shared_from_this<WebSocketSession> {
    websocket::stream<tcp::socket> ws_;
    beast::flat_buffer buffer_;
    std::function<void(std::shared_ptr<WebSocketSession>, const std::string&)> messageHandler_;
    std::function<void(std::shared_ptr<WebSocketSession>)> closeHandler_;

public:
    explicit WebSocketSession(tcp::socket socket)
        : ws_(std::move(socket)) {}

    void setHandlers(
        std::function<void(std::shared_ptr<WebSocketSession>, const std::string&)> messageHandler,
        std::function<void(std::shared_ptr<WebSocketSession>)> closeHandler) {
        messageHandler_ = messageHandler;
        closeHandler_ = closeHandler;
    }

    void run() {
        // Accept the websocket handshake
        ws_.async_accept(
            beast::bind_front_handler(
                &WebSocketSession::on_accept,
                shared_from_this()));
    }

    void send(const std::string& message) {
        ws_.async_write(
            net::buffer(message),
            [self = shared_from_this()](beast::error_code ec, std::size_t) {
                if (ec) {
                    std::cerr << "Write error: " << ec.message() << std::endl;
                }
            });
    }

    void close() {
        ws_.async_close(websocket::close_code::normal,
            [self = shared_from_this()](beast::error_code ec) {
                if (ec) {
                    std::cerr << "Close error: " << ec.message() << std::endl;
                }
            });
    }

private:
    void on_accept(beast::error_code ec) {
        if (ec) {
            std::cerr << "Accept error: " << ec.message() << std::endl;
            return;
        }

        // Read a message
        do_read();
    }

    void do_read() {
        ws_.async_read(
            buffer_,
            beast::bind_front_handler(
                &WebSocketSession::on_read,
                shared_from_this()));
    }

    void on_read(beast::error_code ec, std::size_t bytes_transferred) {
        boost::ignore_unused(bytes_transferred);

        if (ec) {
            if (closeHandler_) {
                closeHandler_(shared_from_this());
            }
            return;
        }

        // Process the message
        std::string message = beast::buffers_to_string(buffer_.data());
        buffer_.consume(buffer_.size());

        if (messageHandler_) {
            messageHandler_(shared_from_this(), message);
        }

        // Read another message
        do_read();
    }
};

// WebSocket server
class ClientWebSocketServer {
private:
    net::io_context ioc_;
    std::unique_ptr<tcp::acceptor> acceptor_;
    std::thread serverThread_;
    std::set<std::shared_ptr<WebSocketSession>> sessions_;
    std::mutex sessionsMutex_;
    std::atomic<bool> running_;
    uint16_t port_;

    // Callbacks
    std::function<void(const std::map<std::string, std::string>&)> onMessage_;

public:
    ClientWebSocketServer(uint16_t port = 8765)
        : port_(port), running_(false) {
        try {
            // Create acceptor and bind to port
            acceptor_ = std::make_unique<tcp::acceptor>(ioc_, tcp::endpoint(tcp::v4(), port));
            std::cout << "Successfully bound to port " << port << std::endl;
        } catch (const std::exception& e) {
            std::cout << "Failed to bind to port " << port << ": " << e.what() << std::endl;
            throw;
        }
    }

    ~ClientWebSocketServer() {
        stop();
    }    bool start() {
        if (running_) return true;
        
        if (!acceptor_) {
            std::cout << "Cannot start server: acceptor not initialized" << std::endl;
            return false;
        }

        try {
            running_ = true;
            
            std::cout << "Starting to accept connections on port " << port_ << "..." << std::endl;
            
            // Start accepting connections
            do_accept();

            // Run the I/O service in a separate thread
            serverThread_ = std::thread([this]() {
                try {
                    std::cout << "I/O context thread started" << std::endl;
                    ioc_.run();
                    std::cout << "I/O context thread ended" << std::endl;
                } catch (const std::exception& e) {
                    std::cerr << "WebSocket server I/O error: " << e.what() << std::endl;
                }
            });

            // Give the server a moment to start
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            
            std::cout << "WebSocket server listening on port " << port_ << std::endl;
            return true;
        } catch (const std::exception& e) {
            std::cerr << "Failed to start WebSocket server: " << e.what() << std::endl;
            running_ = false;
            return false;
        }
    }

    void stop() {
        if (!running_) return;

        running_ = false;

        // Close all sessions
        {
            std::lock_guard<std::mutex> lock(sessionsMutex_);
            for (auto& session : sessions_) {
                session->close();
            }
        }

        // Stop the I/O service
        ioc_.stop();

        if (serverThread_.joinable()) {
            serverThread_.join();
        }
    }

    void broadcast(const std::string& message) {
        std::lock_guard<std::mutex> lock(sessionsMutex_);
        for (auto& session : sessions_) {
            session->send(message);
        }
    }

    // Send various types of updates
    void sendStatusUpdate(const std::string& operation, bool success, const std::string& details = "") {
        SimpleJSON json;
        json.add("type", "status_update")
            .add("operation", operation)
            .add("success", success)
            .add("details", details)
            .add("timestamp", getCurrentTimestamp());
        broadcast(json.str());
    }

    void sendProgressUpdate(int percentage, const std::string& speed, const std::string& eta, 
                           const std::string& transferred, size_t speedBytes = 0) {
        SimpleJSON json;
        json.add("type", "progress_update")
            .add("percentage", percentage)
            .add("speed", speed)
            .add("eta", eta)
            .add("transferred", transferred)
            .add("speedBytes", speedBytes);
        broadcast(json.str());
    }

    void sendLog(const std::string& message, const std::string& level = "info") {
        SimpleJSON json;
        json.add("type", "log_entry")
            .add("message", message)
            .add("level", level)
            .add("timestamp", getCurrentTimestamp());
        broadcast(json.str());
    }

    void sendPhaseUpdate(const std::string& phase) {
        SimpleJSON json;
        json.add("type", "phase_update")
            .add("phase", phase);
        broadcast(json.str());
    }

    void sendSecurityUpdate(bool rsa, bool aes, bool integrity) {
        SimpleJSON json;
        json.add("type", "security_update")
            .add("rsa", rsa)
            .add("aes", aes)
            .add("integrity", integrity);
        broadcast(json.str());
    }

    void sendTransferStarted(const std::string& filename) {
        SimpleJSON json;
        json.add("type", "transfer_started")
            .add("filename", filename);
        broadcast(json.str());
    }

    void sendTransferCompleted(int filesTransferred) {
        SimpleJSON json;
        json.add("type", "transfer_completed")
            .add("filesTransferred", filesTransferred);
        broadcast(json.str());
    }

    void sendError(const std::string& message, bool fatal = false) {
        SimpleJSON json;
        json.add("type", "error")
            .add("message", message)
            .add("fatal", fatal);
        broadcast(json.str());
    }

    void sendConnectionStatus(bool connected) {
        SimpleJSON json;
        json.add("type", "connection_status")
            .add("connected", connected);
        broadcast(json.str());
    }

    void setMessageHandler(std::function<void(const std::map<std::string, std::string>&)> handler) {
        onMessage_ = handler;
    }

private:
    void do_accept() {
        if (!acceptor_) return;
        
        acceptor_->async_accept(
            [this](beast::error_code ec, tcp::socket socket) {
                if (!ec) {
                    std::cout << "New WebSocket connection accepted" << std::endl;
                    auto session = std::make_shared<WebSocketSession>(std::move(socket));
                    
                    session->setHandlers(
                        [this](std::shared_ptr<WebSocketSession> sess, const std::string& msg) {
                            on_message(sess, msg);
                        },
                        [this](std::shared_ptr<WebSocketSession> sess) {
                            on_close(sess);
                        });

                    {
                        std::lock_guard<std::mutex> lock(sessionsMutex_);
                        sessions_.insert(session);
                    }

                    session->run();
                    
                    // Send connection confirmation
                    SimpleJSON json;
                    json.add("type", "connection_established")
                        .add("version", "1.0.0");
                    session->send(json.str());
                } else {
                    std::cout << "Accept error: " << ec.message() << std::endl;
                }

                // Accept another connection
                if (running_) {
                    do_accept();
                }
            });
    }

    void on_message(std::shared_ptr<WebSocketSession> session, const std::string& message) {
        auto data = SimpleJSONParser::parse(message);
        
        if (onMessage_) {
            onMessage_(data);
        }
        
        // Handle built-in message types
        if (data["type"] == "get_status") {
            SimpleJSON json;
            json.add("type", "status_response")
                .add("connected", true);
            session->send(json.str());
        }
    }

    void on_close(std::shared_ptr<WebSocketSession> session) {
        std::lock_guard<std::mutex> lock(sessionsMutex_);
        sessions_.erase(session);
    }

    std::string getCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time_t), "%H:%M:%S");
        return ss.str();
    }
};

// Enhanced ClientGUI class using Boost WebSocket
class ClientGUI {
private:
    static ClientGUI* instance;
    ClientWebSocketServer* wsServer;
    bool guiEnabled;
    
    // Static web content server using Boost.Asio
    class SimpleWebServer {
        net::io_context& ioc_;
        tcp::acceptor acceptor_;
        std::string webRoot_;
        
    public:
        SimpleWebServer(net::io_context& ioc, uint16_t port, const std::string& webRoot)
            : ioc_(ioc)
            , acceptor_(ioc, tcp::endpoint(tcp::v4(), port))
            , webRoot_(webRoot) {
            do_accept();
        }
        
    private:
        void do_accept() {
            acceptor_.async_accept(
                [this](beast::error_code ec, tcp::socket socket) {
                    if (!ec) {
                        handle_request(std::move(socket));
                    }
                    do_accept();
                });
        }
        
        void handle_request(tcp::socket socket) {
            auto req = std::make_shared<beast::flat_buffer>();
            auto parser = std::make_shared<beast::http::request_parser<beast::http::string_body>>();
            
            beast::http::async_read(socket, *req, *parser,
                [this, socket = std::move(socket), req, parser](beast::error_code ec, std::size_t) mutable {
                    if (!ec) {
                        // Serve the GUI files
                        std::string path = parser->get().target();
                        if (path == "/") path = "/index.html";
                        
                        std::string content;
                        std::string contentType = "text/html";
                        
                        if (path == "/index.html" || path == "/gui.html") {
                            content = getGuiHtml();
                        } else if (path == "/backup-client.js") {
                            content = getGuiJs();
                            contentType = "application/javascript";
                        }
                        
                        beast::http::response<beast::http::string_body> res{
                            beast::http::status::ok, parser->get().version()};
                        res.set(beast::http::field::server, "SecureBackup/1.0");
                        res.set(beast::http::field::content_type, contentType);
                        res.body() = content;
                        res.prepare_payload();
                          beast::http::async_write(socket, res,
                            [&socket](beast::error_code ec, std::size_t) {
                                beast::error_code shutdown_ec;
                                socket.shutdown(tcp::socket::shutdown_send, shutdown_ec);
                            });
                    }
                });
        }
        
        std::string getGuiHtml() {
            // Return the HTML content (you can embed it here or load from file)
            return R"(<!DOCTYPE html>
<!-- Paste the enhanced-backup-gui.html content here -->
)";
        }
        
        std::string getGuiJs() {
            // Return the JavaScript content (you can embed it here or load from file)
            return R"(// backup-client.js content
<!-- Paste the backup-client.js content here -->
)";
        }
    };
    
public:
    ClientGUI() : wsServer(nullptr), guiEnabled(false) {}
    
    ~ClientGUI() {
        if (wsServer) {
            delete wsServer;
        }
    }
    
    static ClientGUI* getInstance() {
        if (!instance) {
            instance = new ClientGUI();
        }
        return instance;
    }    bool initialize(uint16_t wsPort = 8765) {
        try {
            std::cout << "Attempting to create WebSocket server on port " << wsPort << "..." << std::endl;
            wsServer = new ClientWebSocketServer(wsPort);
            
            std::cout << "WebSocket server created, attempting to start..." << std::endl;
            guiEnabled = wsServer->start();
            
            if (guiEnabled) {
                std::cout << "WebSocket server started successfully on port " << wsPort << std::endl;
                
                // Verify the server is actually listening
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                
                // Open GUI in default browser with correct port
                #ifdef _WIN32
                std::string url = "http://localhost:" + std::to_string(wsPort);
                std::cout << "Opening GUI at: " << url << std::endl;
                ShellExecuteA(NULL, "open", url.c_str(), NULL, NULL, SW_SHOWNORMAL);
                #elif __APPLE__
                system(("open http://localhost:" + std::to_string(wsPort)).c_str());
                #else
                system(("xdg-open http://localhost:" + std::to_string(wsPort)).c_str());
                #endif
            } else {
                std::cout << "Failed to start WebSocket server" << std::endl;
            }
            
            return guiEnabled;
        } catch (const std::exception& e) {
            std::cout << "Exception during GUI initialization: " << e.what() << std::endl;
            return false;
        } catch (...) {
            std::cout << "Unknown exception during GUI initialization" << std::endl;
            return false;
        }
    }
    
    void shutdown() {
        if (wsServer) {
            wsServer->stop();
        }
    }
    
    // GUI update methods
    void updateOperation(const std::string& operation, bool success, const std::string& details = "") {
        if (wsServer) {
            wsServer->sendStatusUpdate(operation, success, details);
        }
    }
    
    void updateProgress(int current, int total, const std::string& speed = "", const std::string& eta = "") {
        if (wsServer && total > 0) {
            int percentage = (current * 100) / total;
            std::string transferred = formatBytes(current) + " / " + formatBytes(total);
            wsServer->sendProgressUpdate(percentage, speed, eta, transferred);
        }
    }
    
    void updatePhase(const std::string& phase) {
        if (wsServer) {
            wsServer->sendPhaseUpdate(phase);
        }
    }
    
    void updateConnectionStatus(bool connected) {
        if (wsServer) {
            wsServer->sendConnectionStatus(connected);
        }
    }
    
    void updateError(const std::string& error) {
        if (wsServer) {
            wsServer->sendError(error);
        }
    }
      void showNotification(const std::string& title, const std::string& message) {
        if (wsServer) {
            SimpleJSON json;
            json.add("type", "notification")
                .add("title", title)
                .add("message", message);
            wsServer->broadcast(json.str());
        }
    }
    
    // Additional methods required by main.cpp
    void showStatusWindow(bool show) {
        // For WebSocket-based GUI, this is always "shown" when clients connect
        // Just send a status update
        if (wsServer && show) {
            updateOperation("Status window visible", true, "GUI interface ready");
        }
    }
      void setRetryCallback(const std::function<void()>& callback) {
        // Store the callback for use when retry is requested from GUI
        retryCallback = callback;
        
        // Set up message handler to process retry requests
        if (wsServer) {
            wsServer->setMessageHandler([this](const std::map<std::string, std::string>& data) {
                if (data.find("type") != data.end() && data.at("type") == "retry" && retryCallback) {
                    retryCallback();
                }
            });
        }
    }
    
    void setBackupState(bool inProgress, bool completed) {
        if (wsServer) {
            SimpleJSON json;
            json.add("type", "backup_state")
                .add("inProgress", inProgress)
                .add("completed", completed);
            wsServer->broadcast(json.str());
        }
    }
    
    ClientWebSocketServer* getWebSocketServer() {
        return wsServer;
    }

private:
    std::function<void()> retryCallback;
    std::string formatBytes(size_t bytes) {
        const char* sizes[] = {"B", "KB", "MB", "GB"};
        int order = 0;
        double size = static_cast<double>(bytes);
        
        while (size >= 1024 && order < 3) {
            order++;
            size /= 1024;
        }
        
        std::stringstream ss;
        ss << std::fixed << std::setprecision(2) << size << " " << sizes[order];
        return ss.str();
    }
};

// Initialize static member
ClientGUI* ClientGUI::instance = nullptr;

// Helper namespace
namespace ClientGUIHelpers {
    inline bool initializeGUI() {
        return ClientGUI::getInstance()->initialize(8765);
    }
    
    inline void shutdownGUI() {
        ClientGUI::getInstance()->shutdown();
    }
    
    inline void updateOperation(const std::string& operation, bool success, const std::string& details = "") {
        ClientGUI::getInstance()->updateOperation(operation, success, details);
    }
    
    inline void updateProgress(int current, int total, const std::string& speed = "", const std::string& eta = "") {
        ClientGUI::getInstance()->updateProgress(current, total, speed, eta);
    }
    
    inline void updatePhase(const std::string& phase) {
        ClientGUI::getInstance()->updatePhase(phase);
    }
    
    inline void updateConnectionStatus(bool connected) {
        ClientGUI::getInstance()->updateConnectionStatus(connected);
    }
    
    inline void updateError(const std::string& error) {
        ClientGUI::getInstance()->updateError(error);
    }
      inline void showNotification(const std::string& title, const std::string& message) {
        ClientGUI::getInstance()->showNotification(title, message);
    }
    
    // Overloaded version for compatibility with main.cpp
    inline void showNotification(const std::string& title, const std::string& message, unsigned long iconType) {
        // Ignore iconType parameter in WebSocket implementation
        ClientGUI::getInstance()->showNotification(title, message);
    }
}

#endif // CLIENT_WEBSOCKET_SERVER_H