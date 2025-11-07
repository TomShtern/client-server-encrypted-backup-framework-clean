#pragma once

#include <drogon/WebSocketController.h>
#include <memory>
#include <string>

namespace cpp_api_server {

class Notifier;

/**
 * @brief WebSocket controller for real-time status updates.
 *
 * Handles WebSocket connections for:
 * - Client connection/disconnection management
 * - Ping/pong keepalive
 * - Status request/response
 * - Progress updates broadcast
 * - File receipt notifications
 * - Job cancellation events
 */
class StatusWebSocketController
    : public drogon::WebSocketController<StatusWebSocketController> {
public:
    void handleNewMessage(
        const drogon::WebSocketConnectionPtr& wsConn,
        std::string&& message,
        const drogon::WebSocketMessageType& type
    ) override;

    void handleNewConnection(
        const drogon::HttpRequestPtr& req,
        const drogon::WebSocketConnectionPtr& wsConn
    ) override;

    void handleConnectionClosed(
        const drogon::WebSocketConnectionPtr& wsConn
    ) override;

    WS_PATH_LIST_BEGIN
    // Register WebSocket path
    WS_PATH_ADD("/ws/status");
    WS_PATH_LIST_END

    /// Set the notifier for broadcasting messages
    static void set_notifier(std::shared_ptr<Notifier> notifier);

private:
    static std::weak_ptr<Notifier> notifier_;

    /// Handle ping message
    void handlePing(const drogon::WebSocketConnectionPtr& wsConn);

    /// Handle status request
    void handleStatusRequest(
        const drogon::WebSocketConnectionPtr& wsConn,
        const std::string& message
    );
};

}  // namespace cpp_api_server
