#include "cpp_api_server/DatabaseService.h"

#include <spdlog/spdlog.h>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace cpp_api_server {

DatabaseService::DatabaseService(Config config) : config_(std::move(config)) {}

DatabaseService::~DatabaseService() {
    std::lock_guard<std::mutex> lock(mutex_);
    db_.reset();
}

bool DatabaseService::initialize() {
    std::lock_guard<std::mutex> lock(mutex_);

    try {
        spdlog::info("[DatabaseService] Opening database: {}", config_.database_path);

        // Open database with multi-threaded support
        db_ = std::make_unique<SQLite::Database>(
            config_.database_path,
            SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE
        );

        // Enable foreign keys
        db_->exec("PRAGMA foreign_keys = ON");

        // Set WAL mode for better concurrency
        db_->exec("PRAGMA journal_mode = WAL");

        // Verify tables exist
        SQLite::Statement query(*db_, "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('clients', 'files', 'metrics_history')");
        int table_count = 0;
        while (query.executeStep()) {
            table_count++;
        }

        if (table_count < 3) {
            spdlog::warn("[DatabaseService] Database schema incomplete (found {} tables), expecting Python server to initialize", table_count);
        } else {
            spdlog::info("[DatabaseService] Database validated - found all required tables");
        }

        initialized_ = true;
        return true;

    } catch (const std::exception& e) {
        spdlog::error("[DatabaseService] Failed to initialize: {}", e.what());
        initialized_ = false;
        return false;
    }
}

bool DatabaseService::is_connected() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return initialized_ && db_ != nullptr;
}

// Client operations - Full implementation with proper UUID handling
std::optional<Client> DatabaseService::get_client_by_name(const std::string& name) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!initialized_ || !db_) return std::nullopt;

    try {
        SQLite::Statement query(*db_, "SELECT ID, Name, PublicKey, LastSeen, AESKey FROM clients WHERE Name = ?");
        query.bind(1, name);

        if (query.executeStep()) {
            Client client;
            client.id = blob_to_uuid_string(query.getColumn(0).getBlob(), query.getColumn(0).getBytes());
            client.name = query.getColumn(1).getString();
            client.last_seen = query.getColumn(3).getString();
            return client;
        }
    } catch (const std::exception& e) {
        spdlog::error("[DatabaseService] get_client_by_name failed: {}", e.what());
    }

    return std::nullopt;
}

int DatabaseService::get_client_count() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!initialized_ || !db_) return 0;

    try {
        SQLite::Statement query(*db_, "SELECT COUNT(*) FROM clients");
        if (query.executeStep()) {
            return query.getColumn(0).getInt();
        }
    } catch (const std::exception& e) {
        spdlog::error("[DatabaseService] get_client_count failed: {}", e.what());
    }

    return 0;
}

int DatabaseService::get_file_count() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!initialized_ || !db_) return 0;

    try {
        SQLite::Statement query(*db_, "SELECT COUNT(*) FROM files");
        if (query.executeStep()) {
            return query.getColumn(0).getInt();
        }
    } catch (const std::exception& e) {
        spdlog::error("[DatabaseService] get_file_count failed: {}", e.what());
    }

    return 0;
}

int64_t DatabaseService::get_total_bytes() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!initialized_ || !db_) return 0;

    try {
        SQLite::Statement query(*db_, "SELECT COALESCE(SUM(FileSize), 0) FROM files");
        if (query.executeStep()) {
            return query.getColumn(0).getInt64();
        }
    } catch (const std::exception& e) {
        spdlog::error("[DatabaseService] get_total_bytes failed: {}", e.what());
    }

    return 0;
}

// Stub implementations for Phase 2 - to be fully implemented
std::optional<Client> DatabaseService::get_client_by_id(const std::string&) { return std::nullopt; }
std::vector<Client> DatabaseService::get_all_clients() { return {}; }
bool DatabaseService::add_client(const Client&) { return false; }
bool DatabaseService::update_client_last_seen(const std::string&) { return false; }
bool DatabaseService::delete_client(const std::string&) { return false; }

std::optional<File> DatabaseService::get_file_by_id(const std::string&) { return std::nullopt; }
std::vector<File> DatabaseService::get_files_by_client(const std::string&) { return {}; }
std::vector<File> DatabaseService::get_all_files() { return {}; }
std::vector<File> DatabaseService::get_unverified_files() { return {}; }
bool DatabaseService::add_file(const File&) { return false; }
bool DatabaseService::update_file_verified(const std::string&, bool) { return false; }
bool DatabaseService::delete_file(const std::string&) { return false; }

bool DatabaseService::add_metric(const std::string&, double) { return false; }
std::vector<Metric> DatabaseService::get_recent_metrics(const std::string&, int) { return {}; }
bool DatabaseService::cleanup_old_metrics(int) { return false; }

std::string DatabaseService::health_snapshot() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!initialized_ || !db_) {
        return "Database not connected";
    }

    try {
        std::ostringstream oss;
        oss << "Database: " << config_.database_path << " | ";

        SQLite::Statement clients_query(*db_, "SELECT COUNT(*) FROM clients");
        if (clients_query.executeStep()) {
            oss << "Clients: " << clients_query.getColumn(0).getInt() << " | ";
        }

        SQLite::Statement files_query(*db_, "SELECT COUNT(*) FROM files");
        if (files_query.executeStep()) {
            oss << "Files: " << files_query.getColumn(0).getInt();
        }

        return oss.str();

    } catch (const std::exception& e) {
        return std::string("Database error: ") + e.what();
    }
}

std::string DatabaseService::status_snapshot() const {
    return health_snapshot();
}

int64_t DatabaseService::get_database_size_bytes() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!initialized_ || !db_) return 0;

    try {
        SQLite::Statement query(*db_, "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()");
        if (query.executeStep()) {
            return query.getColumn(0).getInt64();
        }
    } catch (const std::exception& e) {
        spdlog::error("[DatabaseService] get_database_size_bytes failed: {}", e.what());
    }

    return 0;
}

// UUID conversion helpers
std::string DatabaseService::blob_to_uuid_string(const void* blob, size_t size) {
    if (size != 16) {
        throw std::runtime_error("Invalid UUID blob size");
    }

    const uint8_t* bytes = static_cast<const uint8_t*>(blob);
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');

    for (size_t i = 0; i < 16; ++i) {
        if (i == 4 || i == 6 || i == 8 || i == 10) {
            oss << '-';
        }
        oss << std::setw(2) << static_cast<int>(bytes[i]);
    }

    return oss.str();
}

std::vector<uint8_t> DatabaseService::uuid_string_to_blob(const std::string& uuid_str) {
    std::vector<uint8_t> blob;
    blob.reserve(16);

    std::string cleaned;
    for (char c : uuid_str) {
        if (c != '-') {
            cleaned += c;
        }
    }

    if (cleaned.size() != 32) {
        throw std::runtime_error("Invalid UUID string format");
    }

    for (size_t i = 0; i < cleaned.size(); i += 2) {
        uint8_t byte = static_cast<uint8_t>(std::stoi(cleaned.substr(i, 2), nullptr, 16));
        blob.push_back(byte);
    }

    return blob;
}

std::string DatabaseService::get_current_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);

    std::tm tm_struct{};
#ifdef _WIN32
    gmtime_s(&tm_struct, &time_t);
#else
    gmtime_r(&time_t, &tm_struct);
#endif

    std::ostringstream oss;
    oss << std::put_time(&tm_struct, "%Y-%m-%d %H:%M:%S");
    return oss.str();
}

}  // namespace cpp_api_server
