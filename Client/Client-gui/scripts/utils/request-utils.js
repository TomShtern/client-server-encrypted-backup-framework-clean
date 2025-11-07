/**
 * Request Utilities for Web GUI
 * Provides unified fetch, retry, timeout, and error handling patterns
 * across different managers and API clients
 */

import { debugLog } from '../core/debug-utils.js';

export class RequestUtils {
    /**
     * Fetch with retry logic and exponential backoff
     * @param {string} url - Request URL
     * @param {Object} options - Fetch options
     * @param {Object} config - Request configuration
     * @returns {Promise<Response>} Fetch response
     */
    static async fetchWithRetry(url, options = {}, config = {}) {
        const {
            retries = 3,
            timeout = 30000,
            backoffMultiplier = 1000,
            maxBackoff = 10000,
            retryCondition = null,
            onRetry = null,
            onTimeout = null,
            onSuccess = null
        } = config;

        let lastError = null;

        for (let attempt = 0; attempt < retries; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => {
                    controller.abort();
                    if (onTimeout) onTimeout(attempt + 1, retries);
                }, timeout);

                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (response.ok) {
                    if (onSuccess) onSuccess(response, attempt + 1);
                    return response;
                }

                // Determine if we should retry based on status code
                const shouldRetry = this.shouldRetryStatus(response.status, attempt, retries);
                if (!shouldRetry) {
                    return response; // Don't retry client errors (4xx)
                }

                // Prepare for retry
                if (onRetry) onRetry(attempt + 1, retries, response.status);
                lastError = new Error(`HTTP ${response.status}: ${response.statusText}`);

            } catch (error) {
                if (error.name === 'AbortError') {
                    lastError = new Error(`Request timeout after ${timeout}ms`);
                    if (onTimeout) onTimeout(attempt + 1, retries);
                } else {
                    lastError = error;
                }

                // Check if we should retry based on custom condition
                if (retryCondition && !retryCondition(error, attempt + 1, retries)) {
                    throw error;
                }

                if (attempt < retries - 1) {
                    if (onRetry) onRetry(attempt + 1, retries, null);
                }
            }

            // If not the last attempt, wait before retrying
            if (attempt < retries - 1) {
                const backoff = Math.min(
                    backoffMultiplier * Math.pow(2, attempt),
                    maxBackoff
                );
                await this.sleep(backoff);
                debugLog(`Retrying request to ${url} (attempt ${attempt + 2}/${retries}) after ${backoff}ms`, 'REQUEST_UTILS');
            }
        }

        throw lastError;
    }

    /**
     * Determine if request should be retried based on status code
     * @param {number} status - HTTP status code
     * @param {number} attempt - Current attempt (1-based)
     * @param {number} maxRetries - Maximum retry attempts
     * @returns {boolean} Whether to retry
     */
    static shouldRetryStatus(status, attempt, maxRetries) {
        // Don't retry if this was the last attempt
        if (attempt >= maxRetries) return false;

        // Retry on server errors (5xx) and specific client errors
        const retryableStatuses = [
            408, // Request Timeout
            429, // Too Many Requests
            500, // Internal Server Error
            502, // Bad Gateway
            503, // Service Unavailable
            504, // Gateway Timeout
            507, // Insufficient Storage
            509, // Bandwidth Limit Exceeded
            520, // Unknown Error (Cloudflare)
            521, // Web Server Is Down (Cloudflare)
            522, // Connection Timed Out (Cloudflare)
            523, // Origin Is Unreachable (Cloudflare)
            524  // A Timeout Occurred (Cloudflare)
        ];

        return retryableStatuses.includes(status);
    }

    /**
     * Enhanced fetch with comprehensive error handling and logging
     * @param {string} url - Request URL
     * @param {Object} options - Fetch options
     * @param {Object} config - Request configuration
     * @returns {Promise<Object>} Response object with data, metadata
     */
    static async fetchWithMetadata(url, options = {}, config = {}) {
        const {
            includeTiming = true,
            includeHeaders = false,
            logRequests = false,
            logResponses = false,
            ...retryConfig
        } = config;

        const startTime = performance.now();
        const requestId = this.generateRequestId();

        try {
            if (logRequests) {
                debugLog(`[${requestId}] Request: ${options.method || 'GET'} ${url}`, 'REQUEST_UTILS');
            }

            const response = await this.fetchWithRetry(url, options, retryConfig);
            const endTime = performance.now();
            const responseTime = Math.round(endTime - startTime);

            const result = {
                ok: response.ok,
                status: response.status,
                statusText: response.statusText,
                url: response.url,
                redirected: response.redirected,
                responseTime,
                requestId
            };

            if (includeHeaders) {
                result.headers = Object.fromEntries(response.headers.entries());
            }

            // Handle response body based on content type
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                result.data = await response.json();
            } else if (contentType && contentType.includes('text/')) {
                result.data = await response.text();
            } else {
                result.data = await response.blob();
            }

            if (logResponses) {
                debugLog(`[${requestId}] Response: ${response.status} (${responseTime}ms)`, 'REQUEST_UTILS');
            }

            return result;

        } catch (error) {
            const endTime = performance.now();
            const responseTime = Math.round(endTime - startTime);

            debugLog(`[${requestId}] Request failed: ${error.message} (${responseTime}ms)`, 'REQUEST_UTILS');

            return {
                ok: false,
                error: error.message,
                responseTime,
                requestId,
                url
            };
        }
    }

    /**
     * Batch multiple requests with concurrency control
     * @param {Array} requests - Array of request objects {url, options, config}
     * @param {Object} batchConfig - Batch configuration
     * @returns {Promise<Array>} Array of results
     */
    static async fetchBatch(requests, batchConfig = {}) {
        const {
            concurrency = 3,
            failFast = false,
            onProgress = null
        } = batchConfig;

        const results = [];
        const errors = [];
        let completed = 0;

        // Process requests in batches
        for (let i = 0; i < requests.length; i += concurrency) {
            const batch = requests.slice(i, i + concurrency);

            const batchPromises = batch.map(async (request, index) => {
                try {
                    const result = await this.fetchWithMetadata(
                        request.url,
                        request.options || {},
                        request.config || {}
                    );

                    completed++;
                    if (onProgress) onProgress(completed, requests.length, i + index);

                    return { index: i + index, result, error: null };
                } catch (error) {
                    completed++;
                    if (onProgress) onProgress(completed, requests.length, i + index);

                    return { index: i + index, result: null, error: error.message };
                }
            });

            const batchResults = await Promise.all(batchPromises);

            for (const { index, result, error } of batchResults) {
                if (error && failFast) {
                    throw new Error(`Batch request failed at index ${index}: ${error}`);
                }

                if (error) {
                    errors.push({ index, error });
                }

                results[index] = result || { ok: false, error };
            }
        }

        return {
            results,
            errors,
            successCount: results.filter(r => r && r.ok).length,
            totalCount: requests.length
        };
    }

    /**
     * Create a request queue for managing concurrent requests
     * @param {Object} queueConfig - Queue configuration
     * @returns {Object} Queue interface
     */
    static createRequestQueue(queueConfig = {}) {
        const {
            maxConcurrent = 3,
            maxQueueSize = 50,
            defaultTimeout = 30000
        } = queueConfig;

        const queue = [];
        const active = new Set();
        let processed = 0;

        const processQueue = async () => {
            if (active.size >= maxConcurrent || queue.length === 0) {
                return;
            }

            const { request, resolve, reject } = queue.shift();
            const jobId = ++processed;

            active.add(jobId);

            try {
                const result = await this.fetchWithMetadata(
                    request.url,
                    request.options,
                    { ...request.config, timeout: request.config?.timeout || defaultTimeout }
                );
                resolve(result);
            } catch (error) {
                reject(error);
            } finally {
                active.delete(jobId);
                // Process next item in queue
                setTimeout(processQueue, 0);
            }
        };

        return {
            add: (request) => {
                return new Promise((resolve, reject) => {
                    if (queue.length >= maxQueueSize) {
                        reject(new Error('Request queue is full'));
                        return;
                    }

                    queue.push({ request, resolve, reject });
                    setTimeout(processQueue, 0);
                });
            },
            getStats: () => ({
                queued: queue.length,
                active: active.size,
                processed,
                maxConcurrent,
                maxQueueSize
            }),
            clear: () => {
                queue.length = 0;
                // Note: Active requests continue to run
            }
        };
    }

    /**
     * Utility: Sleep for specified milliseconds
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise} Promise that resolves after ms
     */
    static sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Utility: Generate unique request ID
     * @returns {string} Unique ID
     */
    static generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Utility: Parse retry-after header
     * @param {string|number} retryAfter - Retry-after header value
     * @returns {number} Seconds to wait before retry
     */
    static parseRetryAfter(retryAfter) {
        if (!retryAfter) return 0;

        // If it's a number, return it directly
        if (typeof retryAfter === 'number') {
            return Math.max(retryAfter, 0);
        }

        // If it's a string, try to parse as number first
        const parsed = parseInt(retryAfter, 10);
        if (!isNaN(parsed)) {
            return Math.max(parsed, 0);
        }

        // If it's an HTTP date, calculate the difference
        const httpDate = new Date(retryAfter);
        if (!isNaN(httpDate.getTime())) {
            const delay = Math.ceil((httpDate.getTime() - Date.now()) / 1000);
            return Math.max(delay, 0);
        }

        return 0;
    }

    /**
     * Utility: Create request options with sensible defaults
     * @param {Object} overrides - Option overrides
     * @returns {Object} Request options
     */
    static createRequestOptions(overrides = {}) {
        return {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                ...overrides.headers
            },
            mode: 'cors',
            credentials: 'same-origin',
            ...overrides
        };
    }

    /**
     * Utility: Validate URL before making request
     * @param {string} url - URL to validate
     * @returns {boolean} Whether URL is valid
     */
    static isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
}

// Export factory functions for common use cases
export const RequestUtilsFactory = {
    /**
     * Create API client with default settings
     */
    createApiClient(baseUrl = 'http://localhost:9090') {
        return {
            get: (endpoint, config = {}) => {
                const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
                return RequestUtils.fetchWithRetry(url, { method: 'GET' }, config);
            },

            post: (endpoint, data, config = {}) => {
                const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
                const options = RequestUtils.createRequestOptions({
                    method: 'POST',
                    body: typeof data === 'string' ? data : JSON.stringify(data)
                });
                return RequestUtils.fetchWithRetry(url, options, config);
            },

            put: (endpoint, data, config = {}) => {
                const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
                const options = RequestUtils.createRequestOptions({
                    method: 'PUT',
                    body: typeof data === 'string' ? data : JSON.stringify(data)
                });
                return RequestUtils.fetchWithRetry(url, options, config);
            },

            delete: (endpoint, config = {}) => {
                const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
                return RequestUtils.fetchWithRetry(url, { method: 'DELETE' }, config);
            }
        };
    },

    /**
     * Create status checker for health monitoring
     */
    createStatusChecker(statusUrl, config = {}) {
        const defaultConfig = {
            timeout: 5000,
            retries: 2,
            ...config
        };

        return {
            check: () => RequestUtils.fetchWithMetadata(statusUrl, { method: 'GET' }, defaultConfig),
            checkLatency: async () => {
                const start = performance.now();
                const result = await RequestUtils.fetchWithRetry(statusUrl, { method: 'GET' }, { timeout: 3000 });
                const end = performance.now();
                return {
                    ok: result.ok,
                    latency: Math.round(end - start),
                    status: result.status
                };
            }
        };
    }
};