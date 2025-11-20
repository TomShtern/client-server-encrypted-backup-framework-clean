#include "cpp_api_server/AppServer.h"

#include <iostream>
#include <string>

int main(int argc, char *argv[]) {
    std::string config_path;
    if (argc > 1) {
        config_path = argv[1];
    } else {
        config_path = "cpp_api_server/config/default_config.json";
    }

    std::cout << "[main] Loading configuration from '" << config_path << "'\n";

    auto config = cpp_api_server::Config::load_or_default(config_path);
    cpp_api_server::AppServer server(std::move(config));
    server.start();

    return 0;
}
