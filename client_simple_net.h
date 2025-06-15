#pragma once
// Simple networking replacement for boost::asio

#include <string>
#include <cstdint>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#define closesocket close
#endif

class SimpleSocket {
private:
    int sock_fd;
    bool connected;
    
public:
    SimpleSocket() : sock_fd(-1), connected(false) {}
    ~SimpleSocket() { close(); }
    
    bool connect(const std::string& host, uint16_t port) {
        sock_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (sock_fd < 0) return false;
        
        sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        addr.sin_addr.s_addr = inet_addr(host.c_str());
        
        if (::connect(sock_fd, (sockaddr*)&addr, sizeof(addr)) == 0) {
            connected = true;
            return true;
        }
        close();
        return false;
    }
    
    bool send(const void* data, size_t size) {
        if (!connected) return false;
        return ::send(sock_fd, (const char*)data, size, 0) == (int)size;
    }
    
    bool receive(void* data, size_t size) {
        if (!connected) return false;
        return ::recv(sock_fd, (char*)data, size, 0) == (int)size;
    }
    
    void close() {
        if (sock_fd >= 0) {
#ifdef _WIN32
            closesocket(sock_fd);
#else
            ::close(sock_fd);
#endif
            sock_fd = -1;
            connected = false;
        }
    }
    
    bool is_connected() const { return connected; }
};