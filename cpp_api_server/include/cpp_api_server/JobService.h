#pragma once

// TODO Phase 2: Re-enable boost::process for subprocess management
// // Must define before including boost/process on Windows to avoid WinSock conflicts
// #ifdef _WIN32
// #define WIN32_LEAN_AND_MEAN
// #include <winsock2.h>
// #include <windows.h>
// #endif

#include "Config.h"

// #include <boost/process.hpp>  // TODO Phase 2
#include <memory>
#include <mutex>
#include <optional>
#include <string>

namespace cpp_api_server {

struct JobStatus {
    std::string id;
    std::string phase;
    double progress_percent = 0.0;
    bool running = false;
};

class JobService {
public:
    explicit JobService(Config config);

    JobStatus current_status() const;
    bool start_backup(const std::string &job_id, const std::string &transfer_info_path, const std::string &file_path);
    bool cancel(const std::string &job_id);

private:
    void reset_state();

    Config config_;
    mutable std::mutex mutex_;
    std::optional<JobStatus> active_job_;
    // TODO Phase 2: boost::process integration
    // std::unique_ptr<boost::process::child> child_process_;
};

}  // namespace cpp_api_server
