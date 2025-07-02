// WebServerBackend.cpp - Simple HTTP API Server for HTML Client
// Provides REST API endpoints for the new HTML GUI client

#include <iostream>
#include <string>
#include <thread>
#include <map>
#include <mutex>
#include <chrono>
#include <sstream>
#include <ctime>
#include <vector>

// Boost includes
#include <boost/asio.hpp>
#include <boost/beast.hpp>
#include <boost/beast/http.hpp>

// Namespace aliases
namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = boost::asio::ip::tcp;

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

// Simple JSON object for responses
class JsonObject {
private:
    std::map<std::string, std::string> data_;
    
public:
    void set(const std::string& key, const std::string& value) {
        data_[key] = value;
    }
    
    void set(const std::string& key, bool value) {
        data_[key] = value ? "true" : "false";
    }
    
    void set(const std::string& key, int value) {
        data_[key] = std::to_string(value);
    }
    
    std::string serialize() const {
        std::ostringstream ss;
        ss << "{";
        bool first = true;
        for (const auto& pair : data_) {
            if (!first) ss << ",";
            ss << "\"" << pair.first << "\":\"" << pair.second << "\"";
            first = false;
        }
        ss << "}";
        return ss.str();
    }
};

// Application state management
class BackupState {
private:
    std::mutex mutex_;
    std::string phase_ = "DISCONNECTED";
    std::string status_ = "Ready to connect";
    int progress_ = 0;
    bool connected_ = false;
    std::string client_id_ = "";
    std::string server_address_ = "127.0.0.1:1256";
    std::string username_ = "";
    std::map<std::string, std::string> stats_;
    std::vector<std::string> logs_;

public:
    // Thread-safe getters
    std::string getPhase() {
        std::lock_guard<std::mutex> lock(mutex_);
        return phase_;
    }
    
    std::string getStatus() {
        std::lock_guard<std::mutex> lock(mutex_);
        return status_;
    }
    
    int getProgress() {
        std::lock_guard<std::mutex> lock(mutex_);
        return progress_;
    }
    
    bool isConnected() {
        std::lock_guard<std::mutex> lock(mutex_);
        return connected_;
    }
    
    std::string getClientId() {
        std::lock_guard<std::mutex> lock(mutex_);
        return client_id_;
    }
    
    // Thread-safe setters
    void setPhase(const std::string& phase) {
        std::lock_guard<std::mutex> lock(mutex_);
        phase_ = phase;
    }
    
    void setStatus(const std::string& status) {
        std::lock_guard<std::mutex> lock(mutex_);
        status_ = status;
    }
    
    void setProgress(int progress) {
        std::lock_guard<std::mutex> lock(mutex_);
        progress_ = progress;
    }
    
    void setConnected(bool connected) {
        std::lock_guard<std::mutex> lock(mutex_);
        connected_ = connected;
    }
    
    void setClientId(const std::string& id) {
        std::lock_guard<std::mutex> lock(mutex_);
        client_id_ = id;
    }
    
    void addLog(const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);
        logs_.push_back(message);
        if (logs_.size() > 100) { // Keep only last 100 logs
            logs_.erase(logs_.begin());
        }
    }
      // Get current state as JSON
    JsonObject getStateJson() {
        std::lock_guard<std::mutex> lock(mutex_);
        JsonObject state;
        state.set("phase", phase_);
        state.set("status", status_);
        state.set("progress", progress_);
        state.set("connected", connected_);
        state.set("client_id", client_id_);
        state.set("server_address", server_address_);
        state.set("username", username_);
        return state;
    }
};

// Global application state
BackupState g_state;

// CORS headers for web client
void add_cors_headers(http::response<http::string_body>& res) {
    res.set(http::field::access_control_allow_origin, "*");
    res.set(http::field::access_control_allow_methods, "GET, POST, PUT, DELETE, OPTIONS");
    res.set(http::field::access_control_allow_headers, "Content-Type, Authorization");
}

// Handle HTTP requests
template<class Body, class Allocator>
http::response<http::string_body>
handle_request(http::request<Body, http::basic_fields<Allocator>>&& req) {
    // Create response
    http::response<http::string_body> res;
    res.version(req.version());
    res.set(http::field::server, "CyberBackup-WebAPI/1.0");
    res.set(http::field::content_type, "application/json");
    add_cors_headers(res);
    
    // Handle CORS preflight
    if (req.method() == http::verb::options) {
        res.result(http::status::ok);
        res.body() = "";
        res.prepare_payload();
        return res;
    }
    
    auto const target = req.target();
    
    try {        // GET /api/status - Get current application state
        if (req.method() == http::verb::get && target == "/api/status") {
            auto state = g_state.getStateJson();
            res.result(http::status::ok);
            res.body() = state.serialize();
        }
        
        // POST /api/connect - Connect to backup server
        else if (req.method() == http::verb::post && target == "/api/connect") {
            try {
                // Simple parsing - look for server and username in request body
                std::string body = req.body();
                std::string server = "127.0.0.1:1256"; // default
                std::string username = "user"; // default
                
                // TODO: Implement actual connection logic
                g_state.setPhase("CONNECTING");
                g_state.setStatus("Connecting to server...");
                g_state.addLog("Connection attempt started for " + server);
                
                // Simulate connection (replace with real logic)
                std::this_thread::sleep_for(std::chrono::milliseconds(1000));
                g_state.setConnected(true);
                g_state.setClientId("CLIENT_" + std::to_string(time(nullptr)));
                g_state.setPhase("CONNECTED");
                g_state.setStatus("Connected successfully");
                g_state.addLog("Connected to " + server + " as " + username);
                
                JsonObject response;
                response.set("success", true);
                response.set("message", "Connected successfully");
                response.set("client_id", g_state.getClientId());
                
                res.result(http::status::ok);
                res.body() = response.serialize();
            } catch (const std::exception& e) {
                JsonObject response;
                response.set("success", false);
                response.set("error", e.what());
                res.result(http::status::bad_request);
                res.body() = response.serialize();
            }
        }
          // POST /api/backup - Start backup operation
        else if (req.method() == http::verb::post && target == "/api/backup") {
            try {
                std::string filename = "selected_file.txt"; // default
                
                g_state.setPhase("BACKUP_IN_PROGRESS");
                g_state.setStatus("Starting backup...");
                g_state.setProgress(0);
                g_state.addLog("Backup started for file: " + filename);
                
                JsonObject response;
                response.set("success", true);
                response.set("message", "Backup started");
                response.set("task_id", "BACKUP_" + std::to_string(time(nullptr)));
                
                res.result(http::status::ok);
                res.body() = response.serialize();
            } catch (const std::exception& e) {
                JsonObject response;
                response.set("success", false);
                response.set("error", e.what());
                res.result(http::status::bad_request);
                res.body() = response.serialize();
            }
        }
        
        // POST /api/stop - Stop current operation
        else if (req.method() == http::verb::post && target == "/api/stop") {
            g_state.setPhase("STOPPED");
            g_state.setStatus("Operation stopped");
            g_state.setProgress(0);
            g_state.addLog("Operation stopped by user");
            
            JsonObject response;
            response.set("success", true);
            response.set("message", "Operation stopped");
            
            res.result(http::status::ok);
            res.body() = response.serialize();
        }
        
        // POST /api/pause - Pause current operation
        else if (req.method() == http::verb::post && target == "/api/pause") {
            g_state.setPhase("PAUSED");
            g_state.setStatus("Operation paused");
            g_state.addLog("Operation paused by user");
            
            JsonObject response;
            response.set("success", true);
            response.set("message", "Operation paused");
            
            res.result(http::status::ok);
            res.body() = response.serialize();
        }
        
        // POST /api/resume - Resume paused operation
        else if (req.method() == http::verb::post && target == "/api/resume") {
            g_state.setPhase("BACKUP_IN_PROGRESS");
            g_state.setStatus("Operation resumed");
            g_state.addLog("Operation resumed by user");
            
            JsonObject response;
            response.set("success", true);
            response.set("message", "Operation resumed");
            
            res.result(http::status::ok);
            res.body() = response.serialize();
        }
        
        // Unknown endpoint
        else {
            JsonObject response;
            response.set("error", "Endpoint not found");
            res.result(http::status::not_found);
            res.body() = response.serialize();
        }    } catch (const std::exception& e) {
        JsonObject response;
        response.set("error", std::string("Server error: ") + e.what());
        res.result(http::status::internal_server_error);
        res.body() = response.serialize();
    }
    
    res.prepare_payload();
    return res;
}

// HTTP session handler
class HttpSession : public std::enable_shared_from_this<HttpSession> {
private:
    tcp::socket socket_;
    beast::flat_buffer buffer_;
    http::request<http::string_body> req_;

public:
    explicit HttpSession(tcp::socket&& socket) : socket_(std::move(socket)) {}
    
    void run() {
        do_read();
    }
    
private:
    void do_read() {
        auto self = shared_from_this();
        http::async_read(socket_, buffer_, req_,
            [self](beast::error_code ec, std::size_t bytes_transferred) {
                boost::ignore_unused(bytes_transferred);
                if (!ec) {
                    self->handle_request();
                }
            });
    }
    
    void handle_request() {
        auto response = handle_request(std::move(req_));
        auto sp = std::make_shared<http::response<http::string_body>>(std::move(response));
        
        auto self = shared_from_this();
        http::async_write(socket_, *sp,
            [self, sp](beast::error_code ec, std::size_t bytes_transferred) {
                boost::ignore_unused(bytes_transferred);
                self->socket_.shutdown(tcp::socket::shutdown_send, ec);
            });
    }
};

// HTTP server listener
class HttpListener : public std::enable_shared_from_this<HttpListener> {
private:
    net::io_context& ioc_;
    tcp::acceptor acceptor_;

public:
    HttpListener(net::io_context& ioc, tcp::endpoint endpoint) 
        : ioc_(ioc), acceptor_(net::make_strand(ioc)) {
        beast::error_code ec;
        
        acceptor_.open(endpoint.protocol(), ec);
        if (ec) {
            std::cerr << "Failed to open acceptor: " << ec.message() << std::endl;
            return;
        }
        
        acceptor_.set_option(net::socket_base::reuse_address(true), ec);
        if (ec) {
            std::cerr << "Failed to set reuse_address: " << ec.message() << std::endl;
            return;
        }
        
        acceptor_.bind(endpoint, ec);
        if (ec) {
            std::cerr << "Failed to bind: " << ec.message() << std::endl;
            return;
        }
        
        acceptor_.listen(net::socket_base::max_listen_connections, ec);
        if (ec) {
            std::cerr << "Failed to listen: " << ec.message() << std::endl;
            return;
        }
        
        std::cout << "HTTP API Server listening on " << endpoint << std::endl;
    }
    
    void run() {
        do_accept();
    }
    
private:
    void do_accept() {
        auto self = shared_from_this();
        acceptor_.async_accept(net::make_strand(ioc_),
            [self](beast::error_code ec, tcp::socket socket) {
                if (!ec) {
                    std::make_shared<HttpSession>(std::move(socket))->run();
                }
                self->do_accept();
            });
    }
};

// Progress simulation thread (for demo purposes)
void progress_simulator() {
    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        
        if (g_state.getPhase() == "BACKUP_IN_PROGRESS") {
            int current = g_state.getProgress();
            if (current < 100) {
                g_state.setProgress(current + 10);
                g_state.setStatus("Backup in progress... " + std::to_string(current + 10) + "%");
                
                if (current + 10 >= 100) {
                    g_state.setPhase("COMPLETED");
                    g_state.setStatus("Backup completed successfully");
                    g_state.addLog("Backup completed successfully");
                }
            }
        }
    }
}

// Main server function
int main() {
    try {
        auto const address = net::ip::make_address("127.0.0.1");
        auto const port = static_cast<unsigned short>(9090);
        
        net::io_context ioc{1};
        
        // Start progress simulator thread
        std::thread sim_thread(progress_simulator);
        sim_thread.detach();
        
        // Initialize application state
        g_state.setPhase("READY");
        g_state.setStatus("Web API server ready");
        g_state.addLog("CyberBackup Web API Server started");
        
        // Create and run HTTP listener
        std::make_shared<HttpListener>(ioc, tcp::endpoint{address, port})->run();
        
        std::cout << "CyberBackup Web API Server started on port " << port << std::endl;
        std::cout << "Ready to serve HTML client requests..." << std::endl;
        
        ioc.run();
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    
    return EXIT_SUCCESS;
}
