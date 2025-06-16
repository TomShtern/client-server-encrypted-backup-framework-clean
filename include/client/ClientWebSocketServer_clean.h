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
    }

    bool start() {
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

#endif // CLIENT_WEBSOCKET_SERVER_H
