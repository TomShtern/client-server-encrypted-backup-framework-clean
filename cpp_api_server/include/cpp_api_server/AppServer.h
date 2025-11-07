#pragma once

#include "Config.h"

namespace cpp_api_server {

/**
 * @brief Minimal stub application server used to keep the workspace error free.
 *
 * The original implementation relied on several external networking libraries.
 * For the moment we provide a lightweight placeholder that simply reports the
 * configuration it was initialised with. The fully-fledged server will be
 * reintroduced once the dependency stack is ready.
 */
class AppServer {
public:
    explicit AppServer(Config config);

    /// Start the stub server. This currently logs the configured endpoint.
    void start();

    /// Accessor used by tests.
    [[nodiscard]] const Config &config() const noexcept { return config_; }

private:
    Config config_;
};

}  // namespace cpp_api_server
