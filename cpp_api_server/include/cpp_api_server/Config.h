#pragma once

#include <string>

namespace cpp_api_server {

struct Config {
    std::string host = "127.0.0.1";
    unsigned short port = 9090;
    std::string static_dir;
    std::string database_path;
    std::string drogon_config_path;
    bool enable_legacy_flask_proxy = false;

    static Config load_or_default(const std::string &config_path);
};

}  // namespace cpp_api_server
