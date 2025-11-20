#pragma once

#include "Config.h"

#include <SQLiteCpp/SQLiteCpp.h>
#include <cstdint>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <vector>

namespace cpp_api_server {

// Client structure matching the database schema
struct Client {
    std::string id;             // UUID as hex string (from BLOB(16))
    std::string name;           // VARCHAR(255) UNIQUE
    std::vector<uint8_t> public_key;  // BLOB(160), RSA public key
    std::string last_seen;      // TEXT (ISO 8601 timestamp)
    std::vector<uint8_t> aes_key;     // BLOB(32), AES-256 key
};

// File structure matching the database schema
struct File {
    std::string id;             // UUID as hex string
    std::string filename;       // VARCHAR(255)
    std::string pathname;       // VARCHAR(255)
    bool verified = false;      // BOOLEAN
    int64_t file_size = 0;      // INTEGER
    std::string modification_date; // TEXT (ISO 8601)
    uint32_t crc = 0;          // INTEGER (CRC32)
    std::string client_id;      // UUID as hex string (FOREIGN KEY)
};

// Metric for time-series data
struct Metric {
    int64_t id = 0;
    std::string timestamp;
    std::string metric_name;
    double value = 0.0;
};

class DatabaseService {
public:
    explicit DatabaseService(Config config);
    ~DatabaseService();

    // Database initialization
    bool initialize();
    bool is_connected() const;

    // Client operations
    std::optional<Client> get_client_by_id(const std::string& client_id);
    std::optional<Client> get_client_by_name(const std::string& name);
    std::vector<Client> get_all_clients();
    bool add_client(const Client& client);
    bool update_client_last_seen(const std::string& client_id);
    bool delete_client(const std::string& client_id);
    int get_client_count();

    // File operations
    std::optional<File> get_file_by_id(const std::string& file_id);
    std::vector<File> get_files_by_client(const std::string& client_id);
    std::vector<File> get_all_files();
    std::vector<File> get_unverified_files();
    bool add_file(const File& file);
    bool update_file_verified(const std::string& file_id, bool verified);
    bool delete_file(const std::string& file_id);
    int get_file_count();
    int64_t get_total_bytes();

    // Metrics operations
    bool add_metric(const std::string& metric_name, double value);
    std::vector<Metric> get_recent_metrics(const std::string& metric_name, int limit = 100);
    bool cleanup_old_metrics(int days_to_keep = 7);

    // Utility methods
    std::string health_snapshot() const;
    std::string status_snapshot() const;
    std::string get_database_path() const { return config_.database_path; }
    int64_t get_database_size_bytes();

private:
    // UUID conversion helpers
    static std::string blob_to_uuid_string(const void* blob, size_t size);
    static std::vector<uint8_t> uuid_string_to_blob(const std::string& uuid_str);
    static std::string get_current_timestamp();

    Config config_;
    std::unique_ptr<SQLite::Database> db_;
    mutable std::mutex mutex_;
    bool initialized_ = false;
};

}  // namespace cpp_api_server
