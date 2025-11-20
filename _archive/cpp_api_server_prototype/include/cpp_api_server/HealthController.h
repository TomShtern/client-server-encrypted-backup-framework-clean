#pragma once

#include <drogon/HttpSimpleController.h>
#include <functional>

namespace cpp_api_server {

/**
 * @brief Health check endpoint controller.
 *
 * Provides system health status including:
 * - Backup server connectivity
 * - API server status
 * - System metrics (CPU, memory)
 * - Active connections and jobs
 */
class HealthController : public drogon::HttpSimpleController<HealthController> {
public:
    void asyncHandleHttpRequest(
        const drogon::HttpRequestPtr& req,
        std::function<void(const drogon::HttpResponsePtr&)>&& callback
    ) override;

    PATH_LIST_BEGIN
    // Register paths for health check endpoints
    PATH_ADD("/health", drogon::Get);
    PATH_ADD("/api/health", drogon::Get);
    PATH_LIST_END

private:
    /// Check if backup server is reachable on port 1256
    bool checkBackupServerStatus() const;

    /// Get system CPU usage percentage
    double getCpuUsage() const;

    /// Get system memory usage percentage
    double getMemoryUsage() const;
};

}  // namespace cpp_api_server
