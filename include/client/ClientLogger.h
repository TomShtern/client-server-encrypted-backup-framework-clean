#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <mutex>

// Production-quality logging system for the client
class ClientLogger {
public:
    enum class LogLevel {
        DEBUG = 0,
        INFO = 1,
        WARNING = 2,
        ERROR = 3,
        CRITICAL = 4
    };

private:
    std::ofstream logFile;
    LogLevel currentLevel;
    bool logToConsole;
    bool logToFile;
    std::mutex logMutex;
    
    std::string levelToString(LogLevel level) {
        switch (level) {
            case LogLevel::DEBUG: return "DEBUG";
            case LogLevel::INFO: return "INFO";
            case LogLevel::WARNING: return "WARNING";
            case LogLevel::ERROR: return "ERROR";
            case LogLevel::CRITICAL: return "CRITICAL";
            default: return "UNKNOWN";
        }
    }
    
    std::string getTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;
        
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        ss << '.' << std::setfill('0') << std::setw(3) << ms.count();
        return ss.str();
    }

public:
    ClientLogger(const std::string& filename = "client_debug.log", 
                 LogLevel level = LogLevel::INFO, 
                 bool console = true, 
                 bool file = true) 
        : currentLevel(level), logToConsole(console), logToFile(file) {
        
        if (logToFile) {
            logFile.open(filename, std::ios::app);
            if (logFile.is_open()) {
                log(LogLevel::INFO, "=== ENCRYPTED BACKUP CLIENT DEBUG MODE ===");
                log(LogLevel::INFO, "Application started at: " + getTimestamp());
            }
        }
    }
    
    ~ClientLogger() {
        if (logFile.is_open()) {
            log(LogLevel::INFO, "Application ended at: " + getTimestamp());
            log(LogLevel::INFO, "=== SESSION END ===");
            logFile.close();
        }
    }
    
    void setLevel(LogLevel level) {
        currentLevel = level;
    }
    
    void log(LogLevel level, const std::string& message) {
        if (level < currentLevel) return;
        
        std::lock_guard<std::mutex> lock(logMutex);
        
        std::string timestamp = getTimestamp();
        std::string levelStr = levelToString(level);
        std::string formattedMessage = "[" + timestamp + "] [" + levelStr + "] " + message;
        
        if (logToConsole) {
            if (level >= LogLevel::ERROR) {
                std::cerr << formattedMessage << std::endl;
            } else {
                std::cout << formattedMessage << std::endl;
            }
        }
        
        if (logToFile && logFile.is_open()) {
            logFile << formattedMessage << std::endl;
            logFile.flush();
        }
    }
    
    void debug(const std::string& message) { log(LogLevel::DEBUG, message); }
    void info(const std::string& message) { log(LogLevel::INFO, message); }
    void warning(const std::string& message) { log(LogLevel::WARNING, message); }
    void error(const std::string& message) { log(LogLevel::ERROR, message); }
    void critical(const std::string& message) { log(LogLevel::CRITICAL, message); }
    
    // Formatted logging
    template<typename... Args>
    void logf(LogLevel level, const std::string& format, Args... args) {
        char buffer[1024];
        snprintf(buffer, sizeof(buffer), format.c_str(), args...);
        log(level, std::string(buffer));
    }
    
    template<typename... Args>
    void infof(const std::string& format, Args... args) {
        logf(LogLevel::INFO, format, args...);
    }
    
    template<typename... Args>
    void errorf(const std::string& format, Args... args) {
        logf(LogLevel::ERROR, format, args...);
    }
};

// Global logger instance
extern ClientLogger* g_logger;

// Convenience macros
#define LOG_DEBUG(msg) if(g_logger) g_logger->debug(msg)
#define LOG_INFO(msg) if(g_logger) g_logger->info(msg)
#define LOG_WARNING(msg) if(g_logger) g_logger->warning(msg)
#define LOG_ERROR(msg) if(g_logger) g_logger->error(msg)
#define LOG_CRITICAL(msg) if(g_logger) g_logger->critical(msg)

#define LOG_INFOF(fmt, ...) if(g_logger) g_logger->infof(fmt, __VA_ARGS__)
#define LOG_ERRORF(fmt, ...) if(g_logger) g_logger->errorf(fmt, __VA_ARGS__)
