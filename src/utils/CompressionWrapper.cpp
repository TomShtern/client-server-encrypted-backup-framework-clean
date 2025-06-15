#include "../../include/utils/CompressionWrapper.h"
#include <iostream>
#include <chrono>
#include <algorithm>

// Simple compression implementation using run-length encoding for demonstration
// In production, you would use zlib or another compression library

std::vector<uint8_t> CompressionWrapper::compress(const uint8_t* data, size_t size) {
    if (!data || size == 0) {
        return {};
    }
    
    // Simple run-length encoding implementation
    std::vector<uint8_t> compressed;
    compressed.reserve(size); // Reserve space to avoid frequent reallocations
    
    for (size_t i = 0; i < size; ) {
        uint8_t currentByte = data[i];
        size_t count = 1;
        
        // Count consecutive identical bytes (max 255)
        while (i + count < size && data[i + count] == currentByte && count < 255) {
            count++;
        }
        
        if (count >= 3) {
            // Use RLE for runs of 3 or more
            compressed.push_back(0xFF); // Escape byte
            compressed.push_back(static_cast<uint8_t>(count));
            compressed.push_back(currentByte);
        } else {
            // Store bytes directly, escaping 0xFF
            for (size_t j = 0; j < count; j++) {
                if (currentByte == 0xFF) {
                    compressed.push_back(0xFF);
                    compressed.push_back(0x00); // Escaped 0xFF
                } else {
                    compressed.push_back(currentByte);
                }
            }
        }
        
        i += count;
    }
    
    // Only return compressed data if it's actually smaller
    if (compressed.size() < size) {
        return compressed;
    } else {
        // Return original data if compression didn't help
        return std::vector<uint8_t>(data, data + size);
    }
}

std::vector<uint8_t> CompressionWrapper::compress(const std::string& data) {
    return compress(reinterpret_cast<const uint8_t*>(data.c_str()), data.size());
}

std::vector<uint8_t> CompressionWrapper::decompress(const std::vector<uint8_t>& compressedData) {
    if (compressedData.empty()) {
        return {};
    }
    
    std::vector<uint8_t> decompressed;
    decompressed.reserve(compressedData.size() * 2); // Estimate decompressed size
    
    for (size_t i = 0; i < compressedData.size(); ) {
        if (compressedData[i] == 0xFF && i + 1 < compressedData.size()) {
            if (compressedData[i + 1] == 0x00) {
                // Escaped 0xFF
                decompressed.push_back(0xFF);
                i += 2;
            } else if (i + 2 < compressedData.size()) {
                // RLE sequence
                uint8_t count = compressedData[i + 1];
                uint8_t value = compressedData[i + 2];
                
                for (uint8_t j = 0; j < count; j++) {
                    decompressed.push_back(value);
                }
                i += 3;
            } else {
                // Malformed data
                return {};
            }
        } else {
            // Regular byte
            decompressed.push_back(compressedData[i]);
            i++;
        }
    }
    
    return decompressed;
}

std::string CompressionWrapper::decompressToString(const std::vector<uint8_t>& compressedData) {
    auto decompressed = decompress(compressedData);
    if (decompressed.empty()) {
        return "";
    }
    
    return std::string(decompressed.begin(), decompressed.end());
}

double CompressionWrapper::getCompressionRatio(size_t originalSize, size_t compressedSize) {
    if (originalSize == 0) {
        return 0.0;
    }
    
    return static_cast<double>(compressedSize) / static_cast<double>(originalSize);
}

bool CompressionWrapper::shouldCompress(const uint8_t* data, size_t size) {
    if (!data || size < MIN_COMPRESSION_SIZE) {
        return false;
    }
    
    // Quick entropy check - if data has low entropy (many repeated bytes), compression will help
    std::array<size_t, 256> byteFreq = {};
    
    // Sample first 1KB to estimate entropy
    size_t sampleSize = std::min(size, static_cast<size_t>(1024));
    for (size_t i = 0; i < sampleSize; i++) {
        byteFreq[data[i]]++;
    }
    
    // Count unique bytes
    size_t uniqueBytes = 0;
    for (size_t freq : byteFreq) {
        if (freq > 0) {
            uniqueBytes++;
        }
    }
    
    // If less than 50% unique bytes in sample, compression likely beneficial
    return uniqueBytes < 128;
}

std::vector<uint8_t> EnhancedCompressionWrapper::compressWithMetrics(const uint8_t* data, size_t size, CompressionMetrics& metrics) {
    auto start = std::chrono::high_resolution_clock::now();
    
    metrics.originalSize = size;
    metrics.compressionUsed = CompressionWrapper::shouldCompress(data, size);
    
    std::vector<uint8_t> result;
    
    if (metrics.compressionUsed) {
        result = CompressionWrapper::compress(data, size);
        
        // Check if compression was actually beneficial
        if (result.size() >= size * CompressionWrapper::MIN_COMPRESSION_RATIO) {
            // Compression didn't help enough, use original data
            result = std::vector<uint8_t>(data, data + size);
            metrics.compressionUsed = false;
        }
    } else {
        // Don't compress, use original data
        result = std::vector<uint8_t>(data, data + size);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    metrics.compressionTimeMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    metrics.compressedSize = result.size();
    metrics.compressionRatio = CompressionWrapper::getCompressionRatio(size, result.size());
    
    return result;
}

std::vector<uint8_t> EnhancedCompressionWrapper::decompressWithMetrics(const std::vector<uint8_t>& compressedData, bool wasCompressed, CompressionMetrics& metrics) {
    auto start = std::chrono::high_resolution_clock::now();
    
    std::vector<uint8_t> result;
    
    if (wasCompressed) {
        result = CompressionWrapper::decompress(compressedData);
    } else {
        result = compressedData; // Data wasn't compressed
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    metrics.decompressionTimeMs = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    return result;
}
