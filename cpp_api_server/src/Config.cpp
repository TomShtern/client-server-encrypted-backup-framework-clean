#include "../include/cpp_api_server/Config.h"

#include <fstream>
#include <sstream>
#include <string>

namespace cpp_api_server {
namespace {
constexpr auto kDefaultStaticDir = "Client/Client-gui";
constexpr auto kDefaultDatabasePath = "python_server/server/defensive.db";
constexpr auto kDefaultDrogonConfig = "cpp_api_server/config/drogon.config.json";

void apply_defaults(Config &config) {
    if (config.static_dir.empty()) {
        config.static_dir = kDefaultStaticDir;
    }
    if (config.database_path.empty()) {
        config.database_path = kDefaultDatabasePath;
    }
    if (config.drogon_config_path.empty()) {
        config.drogon_config_path = kDefaultDrogonConfig;
    }
}
}  // namespace

Config Config::load_or_default(const std::string &config_path) {
    Config config;
    apply_defaults(config);

    if (config_path.empty()) {
        return config;
    }

    std::ifstream input(config_path);
    if (!input.is_open()) {
        return config;
    }

    std::string line;
    while (std::getline(input, line)) {
        std::istringstream stream(line);
        std::string key;
        if (!std::getline(stream, key, '=')) {
            continue;
        }
        std::string value;
        if (!std::getline(stream, value)) {
            continue;
        }

        if (key == "host") {
            config.host = value;
        } else if (key == "port") {
            try {
                config.port = static_cast<unsigned short>(std::stoi(value));
            } catch (...) {
                // Ignore malformed entries and keep defaults.
            }
        } else if (key == "staticDir") {
            config.static_dir = value;
        } else if (key == "databasePath") {
            config.database_path = value;
        } else if (key == "drogonConfig") {
            config.drogon_config_path = value;
        } else if (key == "enableLegacyFlaskProxy") {
            config.enable_legacy_flask_proxy = (value == "true" || value == "1");
        }
    }

    apply_defaults(config);
    return config;
}

}  // namespace cpp_api_server
