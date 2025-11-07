#include "cpp_api_server/HealthController.h"

#include <chrono>
#include <json/json.h>  // Drogon uses jsoncpp

#ifdef _WIN32
#include <winsock2.h>
#include <pdh.h>
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "pdh.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

using namespace drogon;

namespace cpp_api_server {

void HealthController::asyncHandleHttpRequest(
    const HttpRequestPtr& req,
    std::function<void(const HttpResponsePtr&)>&& callback
) {
    (void)req;
    // Check backup server status
    bool server_running = checkBackupServerStatus();

    // Get system metrics
    double cpu_usage = getCpuUsage();
    double memory_usage = getMemoryUsage();

    // Build response JSON using jsoncpp
    Json::Value response;
    response["status"] = server_running ? "healthy" : "degraded";
    response["backup_server_status"] = server_running ? "running" : "not_running";
    response["backup_server"] = server_running ? "running" : "not_running";
    response["api_server"] = "running";

    Json::Value system_metrics;
    system_metrics["cpu_usage_percent"] = cpu_usage;
    system_metrics["memory_usage_percent"] = memory_usage;
    system_metrics["active_websocket_connections"] = 0; // TODO: Get from Notifier
    system_metrics["active_backup_jobs"] = 0;            // TODO: Get from JobService
    response["system_metrics"] = system_metrics;

    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    std::tm tm_struct{};
#ifdef _WIN32
    gmtime_s(&tm_struct, &time_t);
#else
    gmtime_r(&time_t, &tm_struct);
#endif
    char time_buf[30];
    std::strftime(time_buf, sizeof(time_buf), "%Y-%m-%dT%H:%M:%S", &tm_struct);
    response["timestamp"] = time_buf;
    response["uptime_info"] = "API server responsive";

    // Create HTTP response
    auto resp = HttpResponse::newHttpJsonResponse(response);
    resp->setStatusCode(server_running ? k200OK : k503ServiceUnavailable);
    callback(resp);
}

bool HealthController::checkBackupServerStatus() const {
    const char* host = "127.0.0.1";
    int port = 1256;

#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        return false;
    }

    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        WSACleanup();
        return false;
    }

    // Set timeout to 2 seconds
    DWORD timeout = 2000;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (const char*)&timeout, sizeof(timeout));

    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_pton(AF_INET, host, &server_addr.sin_addr);

    bool connected = (connect(sock, (sockaddr*)&server_addr, sizeof(server_addr)) == 0);

    closesocket(sock);
    WSACleanup();
    return connected;
#else
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return false;
    }

    // Set timeout to 2 seconds
    struct timeval timeout;
    timeout.tv_sec = 2;
    timeout.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_pton(AF_INET, host, &server_addr.sin_addr);

    bool connected = (connect(sock, (sockaddr*)&server_addr, sizeof(server_addr)) == 0);

    close(sock);
    return connected;
#endif
}

double HealthController::getCpuUsage() const {
#ifdef _WIN32
    // TODO: Implement Windows CPU usage via PDH
    // For now return 0 to avoid complexity
    return 0.0;
#else
    // TODO: Implement Linux CPU usage via /proc/stat
    return 0.0;
#endif
}

double HealthController::getMemoryUsage() const {
#ifdef _WIN32
    // TODO: Implement Windows memory usage via GlobalMemoryStatusEx
    return 0.0;
#else
    // TODO: Implement Linux memory usage via /proc/meminfo
    return 0.0;
#endif
}

}  // namespace cpp_api_server
