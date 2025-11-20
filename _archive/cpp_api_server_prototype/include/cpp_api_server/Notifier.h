#pragma once

#include <cstddef>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

namespace cpp_api_server {

class Notifier : public std::enable_shared_from_this<Notifier> {
public:
    Notifier();

    void register_connection();
    void unregister_connection();
    void broadcast(const std::string &message);

    [[nodiscard]] std::size_t connection_count() const;
    [[nodiscard]] std::vector<std::string> recent_messages() const;

private:
    mutable std::mutex mutex_;
    std::size_t connection_count_{0};
    std::vector<std::string> messages_;
};

}  // namespace cpp_api_server
