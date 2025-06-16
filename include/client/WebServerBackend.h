#pragma once
// WebServerBackend.h - Header for HTTP API Server

#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <boost/json.hpp>
#include <string>
#include <map>
#include <vector>
#include <mutex>

namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = boost::asio::ip::tcp;

// Application state management class
class BackupState {
private:
    std::mutex mutex_;
    std::string phase_;
    std::string status_;
    int progress_;
    bool connected_;
    std::string client_id_;
    std::string server_address_;
    std::string username_;
    std::map<std::string, std::string> stats_;
    std::vector<std::string> logs_;

public:
    // Thread-safe getters
    std::string getPhase();
    std::string getStatus();
    int getProgress();
    bool isConnected();
    std::string getClientId();
    
    // Thread-safe setters
    void setPhase(const std::string& phase);
    void setStatus(const std::string& status);
    void setProgress(int progress);
    void setConnected(bool connected);
    void setClientId(const std::string& id);
    void addLog(const std::string& message);
    
    // Get current state as JSON
    boost::json::object getStateJson();
};

// HTTP session handler
class HttpSession : public std::enable_shared_from_this<HttpSession> {
private:
    tcp::socket socket_;
    beast::flat_buffer buffer_;
    http::request<http::string_body> req_;

public:
    explicit HttpSession(tcp::socket&& socket);
    void run();
    
private:
    void do_read();
    void handle_request();
};

// HTTP server listener
class HttpListener : public std::enable_shared_from_this<HttpListener> {
private:
    net::io_context& ioc_;
    tcp::acceptor acceptor_;

public:
    HttpListener(net::io_context& ioc, tcp::endpoint endpoint);
    void run();
    
private:
    void do_accept();
};

// Utility functions
void add_cors_headers(http::response<http::string_body>& res);

template<class Body, class Allocator>
http::response<http::string_body>
handle_request(http::request<Body, http::basic_fields<Allocator>>&& req);

// Progress simulation for demo
void progress_simulator();
