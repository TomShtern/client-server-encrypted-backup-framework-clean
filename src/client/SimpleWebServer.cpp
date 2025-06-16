// SimpleWebServer.cpp - Basic HTTP API Server for HTML Client
// Minimal implementation without external dependencies

#include <iostream>
#include <string>
#include <thread>
#include <map>
#include <mutex>
#include <chrono>
#include <sstream>
#include <ctime>
#include <vector>

#ifdef _WIN32
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
    std::vector<std::string> logs_;

public:
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
    
    void setPhase(const std::string& phase) {
        std::lock_guard<std::mutex> lock(mutex_);
        phase_ = phase;
        std::cout << "[STATUS] Phase: " << phase << std::endl;
    }
    
    void setStatus(const std::string& status) {
        std::lock_guard<std::mutex> lock(mutex_);
        status_ = status;
        std::cout << "[STATUS] Status: " << status << std::endl;
    }
    
    void setProgress(int progress) {
        std::lock_guard<std::mutex> lock(mutex_);
        progress_ = progress;
        std::cout << "[STATUS] Progress: " << progress << "%" << std::endl;
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
        if (logs_.size() > 100) {
            logs_.erase(logs_.begin());
        }
        std::cout << "[LOG] " << message << std::endl;
    }
    
    JsonObject getStateJson() {
        std::lock_guard<std::mutex> lock(mutex_);
        JsonObject state;
        state.set("phase", phase_);
        state.set("status", status_);
        state.set("progress", progress_);
        state.set("connected", connected_);
        state.set("client_id", client_id_);
        return state;
    }
};
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
    
    JsonObject getStateJson() {
        std::lock_guard<std::mutex> lock(mutex_);
        JsonObject state;
        state.set("phase", phase_);
        state.set("status", status_);
        state.set("progress", progress_);
        state.set("connected", connected_);
        state.set("client_id", client_id_);
        return state;
    }
};

BackupState g_state;

// Build HTTP response
std::string buildHttpResponse(int status_code, const std::string& body) {
    std::ostringstream response;
    response << "HTTP/1.1 " << status_code << " OK\r\n";
    response << "Content-Type: application/json\r\n";
    response << "Content-Length: " << body.length() << "\r\n";
    response << "Access-Control-Allow-Origin: *\r\n";
    response << "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n";
    response << "Access-Control-Allow-Headers: Content-Type\r\n";
    response << "\r\n";
    response << body;
    return response.str();
}

// Parse HTTP request
void parseHttpRequest(const std::string& request, std::string& method, std::string& path) {
    std::istringstream iss(request);
    std::string line;
    if (std::getline(iss, line)) {
        std::istringstream lineStream(line);
        lineStream >> method >> path;
    }
}

// Handle API requests
std::string handleApiRequest(const std::string& method, const std::string& path) {
    JsonObject response;
    
    if (method == "OPTIONS") {
        return buildHttpResponse(200, "");
    }
    else if (method == "GET" && path == "/api/status") {
        auto state = g_state.getStateJson();
        return buildHttpResponse(200, state.serialize());
    }
    else if (method == "POST" && path == "/api/connect") {
        g_state.setPhase("CONNECTING");
        g_state.setStatus("Connecting...");
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        
        g_state.setConnected(true);
        g_state.setClientId("CLIENT_" + std::to_string(time(nullptr)));
        g_state.setPhase("CONNECTED");
        g_state.setStatus("Connected successfully");
        
        response.set("success", true);
        response.set("message", "Connected successfully");
        return buildHttpResponse(200, response.serialize());
    }    else if (method == "POST" && path == "/api/backup") {
        g_state.setPhase("BACKUP_IN_PROGRESS");
        g_state.setStatus("Starting real backup...");
        g_state.setProgress(0);
        g_state.addLog("Starting real backup operation");
        
        // Call the real C++ client executable in a separate thread
        std::thread backupThread([]() {
            try {
                g_state.addLog("Executing real C++ backup client...");
                
                // Change to client directory and run the real backup client
                std::string command = "cd ..\\client && EncryptedBackupClient.exe";
                int result = std::system(command.c_str());
                
                if (result == 0) {
                    g_state.setPhase("COMPLETED");
                    g_state.setStatus("Backup completed successfully");
                    g_state.setProgress(100);
                    g_state.addLog("Real backup completed successfully");
                } else {
                    g_state.setPhase("ERROR");
                    g_state.setStatus("Backup failed");
                    g_state.addLog("Real backup failed with error code: " + std::to_string(result));
                }
            } catch (const std::exception& e) {
                g_state.setPhase("ERROR");
                g_state.setStatus("Backup error: " + std::string(e.what()));
                g_state.addLog("Backup error: " + std::string(e.what()));
            }
        });
        backupThread.detach();
        
        response.set("success", true);
        response.set("message", "Real backup operation started");
        return buildHttpResponse(200, response.serialize());
    }
    else if (method == "POST" && path == "/api/stop") {
        g_state.setPhase("STOPPED");
        g_state.setStatus("Operation stopped");
        
        response.set("success", true);
        response.set("message", "Operation stopped");
        return buildHttpResponse(200, response.serialize());
    }
    else {
        response.set("error", "Not found");
        return buildHttpResponse(404, response.serialize());
    }
}

// Progress simulation
void progressSimulator() {
    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(2000));
        
        if (g_state.getPhase() == "BACKUP_IN_PROGRESS") {
            int current = g_state.getProgress();
            if (current < 100) {
                g_state.setProgress(current + 10);
                g_state.setStatus("Backup progress: " + std::to_string(current + 10) + "%");
                
                if (current + 10 >= 100) {
                    g_state.setPhase("COMPLETED");
                    g_state.setStatus("Backup completed successfully");
                }
            }
        }
    }
}

// Main server
int main() {
    std::cout << "Starting CyberBackup Web API Server..." << std::endl;
    
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
#ifdef _WIN32
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, (char*)&opt, sizeof(opt));
#else
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(9090);

    bind(server_fd, (struct sockaddr*)&address, sizeof(address));
    listen(server_fd, 3);

    g_state.setPhase("READY");
    g_state.setStatus("Web API server ready");
    
    std::thread sim_thread(progressSimulator);
    sim_thread.detach();

    std::cout << "Server listening on port 9090..." << std::endl;

    while (true) {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        int client_socket = accept(server_fd, (struct sockaddr*)&client_addr, &addr_len);

        char buffer[4096];
        int bytes_read = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            std::string request(buffer);
            
            std::string method, path;
            parseHttpRequest(request, method, path);
            
            std::string response = handleApiRequest(method, path);
            send(client_socket, response.c_str(), response.length(), 0);
        }

#ifdef _WIN32
        closesocket(client_socket);
#else
        close(client_socket);
#endif
    }

    return 0;
}
