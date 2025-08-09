// Enhanced Observability for C++ Client
// Provides structured logging, metrics, and performance monitoring

#include <iostream>
#include <fstream>
#include <chrono>
#include <string>
#include <map>
#include <vector>
#include <mutex>
#include <iomanip>
#include <sstream>

class ClientMetrics {
private:
    mutable std::mutex metrics_mutex;
    std::map<std::string, int> counters;
    std::map<std::string, double> gauges;
    std::map<std::string, std::vector<double>> timers;
    std::chrono::steady_clock::time_point start_time;
    
public:
    ClientMetrics() : start_time(std::chrono::steady_clock::now()) {}
    
    void increment_counter(const std::string& name, int value = 1) {
        std::lock_guard<std::mutex> lock(metrics_mutex);
        counters[name] += value;
    }
    
    void set_gauge(const std::string& name, double value) {
        std::lock_guard<std::mutex> lock(metrics_mutex);
        gauges[name] = value;
    }
    
    void record_timer(const std::string& name, double duration_ms) {
        std::lock_guard<std::mutex> lock(metrics_mutex);
        timers[name].push_back(duration_ms);
        
        // Keep only last 100 measurements to prevent memory growth
        if (timers[name].size() > 100) {
            timers[name].erase(timers[name].begin());
        }
    }
    
    std::string get_summary() const {
        std::lock_guard<std::mutex> lock(metrics_mutex);
        std::stringstream ss;
        
        auto now = std::chrono::steady_clock::now();
        auto uptime = std::chrono::duration_cast<std::chrono::seconds>(now - start_time).count();
        
        ss << "=== Client Metrics Summary ===\n";
        ss << "Uptime: " << uptime << " seconds\n\n";
        
        ss << "Counters:\n";
        for (const auto& [name, value] : counters) {
            ss << "  " << name << ": " << value << "\n";
        }
        
        ss << "\nGauges:\n";
        for (const auto& [name, value] : gauges) {
            ss << "  " << name << ": " << std::fixed << std::setprecision(2) << value << "\n";
        }
        
        ss << "\nTimers (avg/min/max ms):\n";
        for (const auto& [name, measurements] : timers) {
            if (!measurements.empty()) {
                double sum = 0;
                double min_val = measurements[0];
                double max_val = measurements[0];
                
                for (double val : measurements) {
                    sum += val;
                    min_val = std::min(min_val, val);
                    max_val = std::max(max_val, val);
                }
                
                double avg = sum / measurements.size();
                ss << "  " << name << ": " << std::fixed << std::setprecision(2) 
                   << avg << "/" << min_val << "/" << max_val 
                   << " (" << measurements.size() << " samples)\n";
            }
        }
        
        return ss.str();
    }
    
    void log_metrics_to_file(const std::string& filename) const {
        std::ofstream file(filename, std::ios::app);
        if (file.is_open()) {
            auto now = std::chrono::system_clock::now();
            auto time_t = std::chrono::system_clock::to_time_t(now);
            
            file << "\n[" << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S") << "]\n";
            file << get_summary();
            file.close();
        }
    }
};

class StructuredLogger {
private:
    std::string component;
    std::ofstream log_file;
    std::mutex log_mutex;
    
    std::string get_timestamp() const {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;
        
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        ss << "." << std::setfill('0') << std::setw(3) << ms.count();
        return ss.str();
    }
    
public:
    StructuredLogger(const std::string& comp, const std::string& log_filename) 
        : component(comp) {
        log_file.open(log_filename, std::ios::app);
    }
    
    ~StructuredLogger() {
        if (log_file.is_open()) {
            log_file.close();
        }
    }
    
    void log(const std::string& level, const std::string& message, 
             const std::string& operation = "", double duration_ms = -1) {
        std::lock_guard<std::mutex> lock(log_mutex);
        
        std::stringstream structured_log;
        structured_log << "{";
        structured_log << "\"timestamp\":\"" << get_timestamp() << "\",";
        structured_log << "\"level\":\"" << level << "\",";
        structured_log << "\"component\":\"" << component << "\",";
        structured_log << "\"message\":\"" << message << "\"";
        
        if (!operation.empty()) {
            structured_log << ",\"operation\":\"" << operation << "\"";
        }
        
        if (duration_ms >= 0) {
            structured_log << ",\"duration_ms\":" << std::fixed << std::setprecision(2) << duration_ms;
        }
        
        structured_log << "}\n";
        
        // Write to file
        if (log_file.is_open()) {
            log_file << structured_log.str();
            log_file.flush();
        }
        
        // Also write human-readable to console
        std::cout << "[" << get_timestamp() << "] [" << level << "] [" << component << "] " 
                  << message;
        if (!operation.empty()) {
            std::cout << " [op:" << operation << "]";
        }
        if (duration_ms >= 0) {
            std::cout << " [" << duration_ms << "ms]";
        }
        std::cout << std::endl;
    }
    
    void info(const std::string& message, const std::string& operation = "", double duration_ms = -1) {
        log("INFO", message, operation, duration_ms);
    }
    
    void warn(const std::string& message, const std::string& operation = "", double duration_ms = -1) {
        log("WARN", message, operation, duration_ms);
    }
    
    void error(const std::string& message, const std::string& operation = "", double duration_ms = -1) {
        log("ERROR", message, operation, duration_ms);
    }
    
    void debug(const std::string& message, const std::string& operation = "", double duration_ms = -1) {
        log("DEBUG", message, operation, duration_ms);
    }
};

class OperationTimer {
private:
    std::chrono::steady_clock::time_point start_time;
    std::string operation_name;
    StructuredLogger* logger;
    ClientMetrics* metrics;
    
public:
    OperationTimer(const std::string& op_name, StructuredLogger* log, ClientMetrics* met) 
        : operation_name(op_name), logger(log), metrics(met) {
        start_time = std::chrono::steady_clock::now();
        if (logger) {
            logger->info("Starting " + operation_name, operation_name);
        }
    }
    
    ~OperationTimer() {
        auto end_time = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
        double duration_ms = duration.count() / 1000.0;
        
        if (logger) {
            logger->info("Completed " + operation_name, operation_name, duration_ms);
        }
        
        if (metrics) {
            metrics->record_timer("operation." + operation_name + ".duration", duration_ms);
            metrics->increment_counter("operation." + operation_name + ".completed");
        }
    }
    
    double get_elapsed_ms() const {
        auto now = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now - start_time);
        return duration.count() / 1000.0;
    }
};

// Global instances
static ClientMetrics g_metrics;
static StructuredLogger g_logger("cpp-client", "logs/client-observability.log");

// C-style interface for integration with existing client code
extern "C" {
    void log_client_info(const char* message, const char* operation) {
        g_logger.info(std::string(message), operation ? std::string(operation) : "");
    }
    
    void log_client_error(const char* message, const char* operation) {
        g_logger.error(std::string(message), operation ? std::string(operation) : "");
        g_metrics.increment_counter("errors.total");
    }
    
    void record_client_metric_counter(const char* name, int value) {
        g_metrics.increment_counter(std::string(name), value);
    }
    
    void record_client_metric_gauge(const char* name, double value) {
        g_metrics.set_gauge(std::string(name), value);
    }
    
    void record_client_metric_timer(const char* name, double duration_ms) {
        g_metrics.record_timer(std::string(name), duration_ms);
    }
    
    void log_client_metrics_summary() {
        std::cout << g_metrics.get_summary() << std::endl;
        g_metrics.log_metrics_to_file("logs/client-metrics.log");
    }
    
    // Operation timing helpers
    void* start_operation_timer(const char* operation_name) {
        return new OperationTimer(std::string(operation_name), &g_logger, &g_metrics);
    }
    
    void end_operation_timer(void* timer_ptr) {
        if (timer_ptr) {
            delete static_cast<OperationTimer*>(timer_ptr);
        }
    }
    
    double get_operation_elapsed_ms(void* timer_ptr) {
        if (timer_ptr) {
            return static_cast<OperationTimer*>(timer_ptr)->get_elapsed_ms();
        }
        return 0.0;
    }
}

// Macro helpers for easier integration
#define LOG_CLIENT_INFO(msg, op) log_client_info(msg, op)
#define LOG_CLIENT_ERROR(msg, op) log_client_error(msg, op)
#define RECORD_COUNTER(name, val) record_client_metric_counter(name, val)
#define RECORD_GAUGE(name, val) record_client_metric_gauge(name, val)
#define RECORD_TIMER(name, ms) record_client_metric_timer(name, ms)
#define TIMED_OPERATION(name) OperationTimer _timer(name, &g_logger, &g_metrics)
