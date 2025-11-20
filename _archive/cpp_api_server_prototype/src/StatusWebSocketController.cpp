#include "cpp_api_server/StatusWebSocketController.h"
#include "cpp_api_server/Notifier.h"

#include <json/json.h>
#include <chrono>
#include <iostream>
#include <memory>
#include <utility>

using namespace drogon;

namespace cpp_api_server {

namespace {
std::string to_iso_timestamp() {
    const auto now = std::chrono::system_clock::now();
    const auto time_t = std::chrono::system_clock::to_time_t(now);
    std::tm tm_struct{};
#ifdef _WIN32
    gmtime_s(&tm_struct, &time_t);
#else
    gmtime_r(&time_t, &tm_struct);
#endif
    char buffer[32];
    if (std::strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &tm_struct) == 0) {
        return "1970-01-01T00:00:00Z";
    }
    return buffer;
}

std::string to_json_string(const Json::Value& value) {
    Json::StreamWriterBuilder builder;
    builder["indentation"] = "";  // compact JSON for WebSocket payloads
    return Json::writeString(builder, value);
}

Json::Value parse_json_safely(const std::string& payload, bool& ok) {
    Json::Value root;
    Json::CharReaderBuilder builder;
    std::string errors;
    std::unique_ptr<Json::CharReader> reader(builder.newCharReader());
    ok = reader->parse(payload.data(), payload.data() + payload.size(), &root, &errors);
    if (!ok) {
        std::cerr << "[WebSocket] JSON parse error: " << errors << '\n';
    }
    return root;
}
}  // namespace

std::weak_ptr<Notifier> StatusWebSocketController::notifier_;

void StatusWebSocketController::handleNewMessage(
    const WebSocketConnectionPtr& wsConn,
    std::string&& message,
    const WebSocketMessageType& type
) {
    if (type != WebSocketMessageType::Text) {
        return;  // Only handle text messages
    }

    bool parsed_ok = false;
    const auto msg_json = parse_json_safely(message, parsed_ok);
    if (!parsed_ok) {
        return;
    }

    const auto event_type = msg_json.get("type", "").asString();

    if (event_type == "ping") {
        handlePing(wsConn);
    } else if (event_type == "request_status") {
        handleStatusRequest(wsConn, message);
    } else {
        std::cout << "[WebSocket] Unknown message type: " << event_type << '\n';
    }
}

void StatusWebSocketController::handleNewConnection(
    const HttpRequestPtr& req,
    const WebSocketConnectionPtr& wsConn
) {
    (void)req;
    if (auto notifier = notifier_.lock()) {
        notifier->register_connection();
    }

    std::cout << "[WebSocket] Client connected\n";

    Json::Value status_msg;
    status_msg["type"] = "status";
    status_msg["connected"] = true;  // TODO: Check actual backup server status
    status_msg["server_running"] = true;
    status_msg["timestamp"] = to_iso_timestamp();
    status_msg["message"] = "WebSocket connected - real-time updates enabled";

    wsConn->send(to_json_string(status_msg));
}

void StatusWebSocketController::handleConnectionClosed(
    const WebSocketConnectionPtr& wsConn
) {
    (void)wsConn;
    if (auto notifier = notifier_.lock()) {
        notifier->unregister_connection();
    }
    std::cout << "[WebSocket] Client disconnected\n";
}

void StatusWebSocketController::handlePing(const WebSocketConnectionPtr& wsConn) {
    Json::Value pong_msg;
    pong_msg["type"] = "pong";
    pong_msg["timestamp"] = to_iso_timestamp();
    wsConn->send(to_json_string(pong_msg));
}

void StatusWebSocketController::handleStatusRequest(
    const WebSocketConnectionPtr& wsConn,
    const std::string& /*message*/
) {
    Json::Value response;
    response["type"] = "status_response";

    Json::Value status;
    status["phase"] = "READY";
    status["message"] = "Ready for backup";
    status["connected"] = true;
    status["backing_up"] = false;

    Json::Value progress;
    progress["percentage"] = 0;
    progress["current_file"] = "";
    progress["bytes_transferred"] = static_cast<Json::UInt64>(0);
    progress["total_bytes"] = static_cast<Json::UInt64>(0);
    status["progress"] = progress;

    response["status"] = status;
    response["timestamp"] = to_iso_timestamp();

    wsConn->send(to_json_string(response));
}

void StatusWebSocketController::set_notifier(std::shared_ptr<Notifier> notifier) {
    notifier_ = std::move(notifier);
}

}  // namespace cpp_api_server
