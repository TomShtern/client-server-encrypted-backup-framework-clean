import { debugLogger } from '../core/debug-utils.js';

class ErrorBoundary {
    constructor(app) {
        this.app = app;
        this.errorCount = 0;
        this.lastErrors = [];
        this.maxErrors = 10;
        
        // Error loop prevention safeguards
        this.isProcessingError = false;
        this.errorTimestamps = [];
        this.maxErrorsPerWindow = 10;
        this.errorTimeWindow = 5000; // 5 seconds
        this.circuitBreakerOpen = false;
        this.circuitBreakerResetTime = 30000; // 30 seconds
        
        this.setupGlobalHandlers();
    }

    setupGlobalHandlers() {
        // Handle uncaught JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError('JavaScript Error', event.error, {
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError('Unhandled Promise Rejection', event.reason, {
                promise: event.promise
            });
            event.preventDefault(); // Prevent default browser behavior
        });

        // Handle API errors specifically
        this.setupApiErrorHandling();
    }

    setupApiErrorHandling() {
        // Wrap existing API calls with error boundaries
        if (this.app && this.app.apiClient) {
            const originalMethods = ['getStatus', 'connect', 'startBackup', 'stopBackup', 'pauseBackup', 'resumeBackup'];
            
            originalMethods.forEach(methodName => {
                const original = this.app.apiClient[methodName];
                if (original) {
                    this.app.apiClient[methodName] = async (...args) => {
                        try {
                            return await original.apply(this.app.apiClient, args);
                        } catch (error) {
                            this.handleError(`API Error: ${methodName}`, error, { method: methodName, args });
                            throw error; // Re-throw for upstream handling
                        }
                    };
                }
            });
        }
    }

    handleError(type, error, context = {}) {
        // SAFEGUARD 1: Prevent recursive error processing
        if (this.isProcessingError) {
            console.warn('[ErrorBoundary] Recursive error detected, ignoring:', type);
            return;
        }
        
        // SAFEGUARD 2: Circuit breaker - stop processing if too many errors
        if (this.circuitBreakerOpen) {
            const now = Date.now();
            if (now - this.circuitBreakerOpenTime < this.circuitBreakerResetTime) {
                console.warn('[ErrorBoundary] Circuit breaker open, ignoring error:', type);
                return;
            } else {
                // Reset circuit breaker
                this.circuitBreakerOpen = false;
                console.info('[ErrorBoundary] Circuit breaker reset');
            }
        }
        
        // SAFEGUARD 3: Rate limiting - prevent error spam
        const now = Date.now();
        this.errorTimestamps = this.errorTimestamps.filter(timestamp => 
            now - timestamp < this.errorTimeWindow
        );
        
        if (this.errorTimestamps.length >= this.maxErrorsPerWindow) {
            console.warn('[ErrorBoundary] Too many errors, opening circuit breaker');
            this.circuitBreakerOpen = true;
            this.circuitBreakerOpenTime = now;
            return;
        }
        
        this.errorTimestamps.push(now);
        this.isProcessingError = true;
        
        try {
            this.errorCount++;
            const errorInfo = {
                type,
                message: error?.message || String(error),
                stack: error?.stack,
                context,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };

            // Store error for debugging
            this.lastErrors.push(errorInfo);
            if (this.lastErrors.length > this.maxErrors) {
                this.lastErrors.shift();
            }

            // Log to console and debug system
            console.error(`[ErrorBoundary] ${type}:`, error, context);
            debugLogger.log('ERROR', 'ERROR_BOUNDARY', `${type}: ${errorInfo.message}`);

            // Update UI with error information - wrapped in additional safety
            try {
                this.updateErrorUI(errorInfo);
            } catch (uiError) {
                console.error('[ErrorBoundary] Failed to update UI during error handling:', uiError);
            }

            // Attempt recovery if possible
            this.attemptRecovery(type, error);

            // Show user-friendly notification
            this.showErrorNotification(errorInfo);
            
        } catch (processingError) {
            // If error processing itself fails, log to console only
            console.error('[ErrorBoundary] Error processing failed:', processingError);
        } finally {
            // Always reset the processing flag
            this.isProcessingError = false;
        }
    }

    updateErrorUI(errorInfo) {
        try {
            if (this.app) {
                // Add to operation log
                this.app.addLog(`Error: ${errorInfo.type}`, 'error', errorInfo.message);
                
                // Update connection status if it's an API error
                if (errorInfo.type.includes('API')) {
                    this.app.state.isConnected = false;
                    this.app.state.phase = 'ERROR';
                    this.app.updateAllUI();
                }
            }
        } catch (uiError) {
            console.error('[ErrorBoundary] Failed to update UI:', uiError);
        }
    }

    attemptRecovery(type, error) {
        try {
            // Attempt different recovery strategies based on error type
            if (type.includes('API') && this.app) {
                // For API errors, reset connection state and try to recover
                this.app.state.isRunning = false;
                this.app.state.isPaused = false;
                
                // Clear any running intervals that might be causing issues
                if (this.app.intervals) {
                    this.app.intervals.clearAll();
                    // Restart adaptive polling
                    setTimeout(() => {
                        if (this.app.startAdaptivePolling) {
                            this.app.startAdaptivePolling();
                        }
                    }, 2000);
                }
            }

            // Memory cleanup
            if (type.includes('Memory') || type.includes('OutOfMemory')) {
                this.performMemoryCleanup();
            }

        } catch (recoveryError) {
            console.error('[ErrorBoundary] Recovery attempt failed:', recoveryError);
        }
    }

    performMemoryCleanup() {
        try {
            // Clear any large data structures
            if (this.app) {
                // Limit log entries
                const logContainer = this.app.elements?.logContainer;
                if (logContainer && logContainer.children.length > 50) {
                    // Batch remove for better performance  
                    const childrenToRemove = logContainer.children.length - 25;
                    const elementsToRemove = Array.from(logContainer.children).slice(-childrenToRemove);
                    elementsToRemove.forEach(element => logContainer.removeChild(element));
                }

                // Clear debug logger entries
                if (debugLogger && debugLogger.clearEntries) {
                    debugLogger.clearEntries();
                }
            }

            // Force garbage collection if available
            if (window.gc) {
                window.gc();
            }
        } catch (cleanupError) {
            console.error('[ErrorBoundary] Memory cleanup failed:', cleanupError);
        }
    }

    showErrorNotification(errorInfo) {
        try {
            let message = 'An unexpected error occurred';
            
            // Provide more specific messages for common errors
            if (errorInfo.type.includes('API')) {
                message = 'Connection error. Please check your network and try again.';
            } else if (errorInfo.message.includes('fetch')) {
                message = 'Network request failed. Please check your connection.';
            } else if (errorInfo.message.includes('timeout')) {
                message = 'Operation timed out. Please try again.';
            }

            if (this.app && this.app.showToast) {
                this.app.showToast(message, 'error', 5000);
            }
        } catch (notificationError) {
            console.error('[ErrorBoundary] Failed to show notification:', notificationError);
        }
    }

    getErrorStats() {
        return {
            totalErrors: this.errorCount,
            recentErrors: this.lastErrors.slice(-5),
            errorTypes: this.lastErrors.reduce((acc, error) => {
                acc[error.type] = (acc[error.type] || 0) + 1;
                return acc;
            }, {})
        };
    }

    reset() {
        this.errorCount = 0;
        this.lastErrors = [];
    }
}
class ErrorMessageFormatter {
    constructor() {
        this.commonErrorPatterns = {
            connection: {
                patterns: ['ECONNREFUSED', 'ENOTFOUND', 'ETIMEDOUT', 'connection refused', 'network error'],
                userMessage: 'Unable to connect to the backup server',
                suggestion: 'Check server address, port, and network connection. Ensure the backup server is running.'
            },
            authentication: {
                patterns: ['authentication failed', 'invalid credentials', 'unauthorized', 'login failed'],
                userMessage: 'Authentication failed',
                suggestion: 'Verify your username and ensure your client keys are properly configured.'
            },
            fileAccess: {
                patterns: ['ENOENT', 'EACCES', 'permission denied', 'file not found', 'access denied'],
                userMessage: 'File access problem',
                suggestion: 'Check file permissions and ensure the file exists and is accessible.'
            },
            serverError: {
                patterns: ['server error', '500', 'internal server error'],
                userMessage: 'Server encountered an error',
                suggestion: 'The backup server experienced an issue. Try again in a few moments.'
            },
            timeout: {
                patterns: ['timeout', 'request timed out', 'operation timed out'],
                userMessage: 'Operation timed out',
                suggestion: 'The operation took too long. Check network speed and server load, then try again.'
            },
            encryption: {
                patterns: ['encryption failed', 'decryption failed', 'key error', 'crypto error'],
                userMessage: 'Encryption/decryption error',
                suggestion: 'Verify RSA keys are properly configured and compatible with the server.'
            },
            diskSpace: {
                patterns: ['no space', 'disk full', 'insufficient space', 'ENOSPC'],
                userMessage: 'Insufficient storage space',
                suggestion: 'Free up disk space on the server or select a smaller file to backup.'
            },
            fileSize: {
                patterns: ['file too large', 'size limit', 'maximum size exceeded'],
                userMessage: 'File is too large',
                suggestion: 'Select a smaller file or check server file size limits.'
            }
        };

        this.operationSpecificMessages = {
            connection: {
                success: 'Successfully connected to backup server',
                failure: 'Failed to establish connection'
            },
            backup: {
                success: 'Backup completed successfully',
                failure: 'Backup operation failed'
            },
            pause: {
                success: 'Backup paused successfully',
                failure: 'Failed to pause backup'
            },
            resume: {
                success: 'Backup resumed successfully',
                failure: 'Failed to resume backup'
            },
            stop: {
                success: 'Backup stopped successfully',
                failure: 'Failed to stop backup'
            }
        };
    }

    /**
     * Format an error message to be more user-friendly
     * @param {string} operation - The operation that failed (e.g., 'connection', 'backup')
     * @param {string} rawError - The raw error message from the system
     * @param {Object} context - Additional context (optional)
     * @returns {Object} Formatted error with userMessage and suggestion
     */
    formatError(operation, rawError, context = {}) {
        const lowerError = rawError.toLowerCase();
        
        // Find matching error pattern
        for (const [category, config] of Object.entries(this.commonErrorPatterns)) {
            if (config.patterns.some(pattern => lowerError.includes(pattern))) {
                return {
                    userMessage: this.getOperationMessage(operation, 'failure') || config.userMessage,
                    suggestion: config.suggestion,
                    category: category,
                    technical: rawError
                };
            }
        }

        // If no pattern matches, provide a generic but helpful message
        return {
            userMessage: this.getOperationMessage(operation, 'failure') || 'An unexpected error occurred',
            suggestion: this.getGenericSuggestion(operation),
            category: 'unknown',
            technical: rawError
        };
    }

    /**
     * Get operation-specific message
     */
    getOperationMessage(operation, type) {
        return this.operationSpecificMessages[operation]?.[type];
    }

    /**
     * Get generic suggestion based on operation
     */
    getGenericSuggestion(operation) {
        const suggestions = {
            connection: 'Verify server address and port, then try again.',
            backup: 'Check file selection and server connection, then retry.',
            pause: 'Ensure backup is running before attempting to pause.',
            resume: 'Ensure backup is paused before attempting to resume.',
            stop: 'Ensure backup is running before attempting to stop.',
            default: 'Check your connection and settings, then try again.'
        };
        return suggestions[operation] || suggestions.default;
    }

    /**
     * Format a success message
     */
    formatSuccess(operation, details = '') {
        const message = this.getOperationMessage(operation, 'success') || 'Operation completed successfully';
        return {
            userMessage: message,
            details: details
        };
    }

    /**
     * Get user-friendly file validation error
     */
    formatFileValidationError(errors) {
        const errorMap = {
            'File size exceeds maximum limit': {
                message: 'File is too large for backup',
                suggestion: 'Select a smaller file or compress it before backup.'
            },
            'Invalid file type': {
                message: 'File type not supported',
                suggestion: 'Select a different file type or check server configuration.'
            },
            'File is empty': {
                message: 'Cannot backup empty file',
                suggestion: 'Select a file with content to backup.'
            },
            'Special characters in filename': {
                message: 'Filename contains unsupported characters',
                suggestion: 'Rename the file to remove special characters, then try again.'
            }
        };

        const firstError = errors[0];
        const errorInfo = Object.entries(errorMap).find(([key]) => 
            firstError.includes(key)
        );

        if (errorInfo) {
            return errorInfo[1];
        } else {
            return {
                message: 'File validation failed',
                suggestion: 'Check file properties and try selecting a different file.'
            };
        }
    }
}

export { ErrorBoundary, ErrorMessageFormatter };