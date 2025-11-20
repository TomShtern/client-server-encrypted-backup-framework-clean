#include "cpp_api_server/Notifier.h"

#include <iostream>
#include <mutex>
#include <vector>

namespace cpp_api_server {

Notifier::Notifier() = default;

void Notifier::register_connection() {
    std::lock_guard<std::mutex> lock(mutex_);
    ++connection_count_;
    std::cout << "[Notifier] Connection registered. Total: " << connection_count_ << '\n';
}

void Notifier::unregister_connection() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (connection_count_ > 0) {
        --connection_count_;
    }
    std::cout << "[Notifier] Connection removed. Total: " << connection_count_ << '\n';
}

void Notifier::broadcast(const std::string &message) {
    std::lock_guard<std::mutex> lock(mutex_);
    messages_.push_back(message);
    std::cout << "[Notifier] Broadcast message: " << message << '\n';
}

std::size_t Notifier::connection_count() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return connection_count_;
}

std::vector<std::string> Notifier::recent_messages() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return messages_;
}

}  // namespace cpp_api_server
