#include "cpp_api_server/JobService.h"

#include <spdlog/spdlog.h>

#include <string>
#include <utility>

namespace cpp_api_server {

namespace {
constexpr auto kDefaultClientExecutable = "build/Release/EncryptedBackupClient.exe";
}

JobService::JobService(Config config) : config_(std::move(config)) {}

JobStatus JobService::current_status() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (active_job_) {
        return *active_job_;
    }
    return {};
}

bool JobService::start_backup(const std::string &job_id, const std::string &transfer_info_path, const std::string &file_path) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (active_job_ && active_job_->running) {
        spdlog::warn("Job '{}' ignored because another job is active", job_id);
        return false;
    }

    active_job_ = JobStatus{job_id, "INITIALISING", 0.0, true};
    spdlog::info("[JobService] Launch request for job '{}' using transfer info '{}', file '{}'", job_id, transfer_info_path, file_path);

    // TODO Phase 2: Implement process launch with boost::process
    // child_process_.reset();
    active_job_->phase = "WAITING";
    active_job_->progress_percent = 0.0;

    return true;
}

bool JobService::cancel(const std::string &job_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!active_job_ || active_job_->id != job_id) {
        spdlog::warn("[JobService] Cancel requested for unknown job '{}'", job_id);
        return false;
    }

    // TODO: Process termination to be implemented in Phase 2
    // if (child_process_ && child_process_->running()) {
    //     spdlog::info("[JobService] Requesting termination for job '{}'", job_id);
    //     child_process_->terminate();
    // }

    reset_state();
    return true;
}

void JobService::reset_state() {
    // TODO: Process cleanup to be implemented in Phase 2
    // if (child_process_) {
    //     if (child_process_->running()) {
    //         child_process_->terminate();
    //     }
    //     child_process_.reset();
    // }
    active_job_.reset();
}

}  // namespace cpp_api_server
