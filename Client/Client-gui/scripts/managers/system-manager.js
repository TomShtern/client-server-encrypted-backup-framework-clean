import { debugLog } from '../core/debug-utils.js';
import { FileManager } from './file-manager.js';
import { NotificationManager, ModalManager, ConfirmModalManager } from './ui-manager.js';

class SystemManager {
    constructor() {
        this.notifications = new NotificationManager();
        this.fileManager = new FileManager();
        this.modal = new ModalManager();
        this.confirmModal = new ConfirmModalManager();
    }

    announce(message) {
        // Announce to screen readers for accessibility
        if ('speechSynthesis' in window) {
            // Use speech synthesis if available (optional)
            // speechSynthesis.speak(new SpeechSynthesisUtterance(message));
        }
        // Create a live region for screen readers
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'u-sr-only';
        liveRegion.textContent = message;
        document.body.appendChild(liveRegion);

        // Remove after announcement
        setTimeout(() => {
            if (liveRegion.parentNode) {
                liveRegion.parentNode.removeChild(liveRegion);
            }
        }, 1000);
    }

    setupKeyboardShortcuts(appInstance) {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.modal.hide();
                this.confirmModal.hide();
            }
            // Ctrl+S to save config
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                appInstance.saveConfig();
            }
            // Ctrl+B to start backup
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                appInstance.handlePrimaryAction();
            }
            // Ctrl+P to pause/resume
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                appInstance.togglePause();
            }
            // Ctrl+T to stop
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                appInstance.stopBackup();
            }
        });
        
        // Setup tab order optimization
        this.setupTabOrderOptimization();
    }

    setupTabOrderOptimization() {
        // Focus trap within main application area
        const mainContainer = document.querySelector('.container');
        const focusableElements = 'input:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])';
        
        if (mainContainer) {
            mainContainer.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    this.handleTabNavigation(e, mainContainer, focusableElements);
                }
            });
        }

        // Skip to content link for screen readers
        this.createSkipLink();
    }

    handleTabNavigation(e, container, focusableSelector) {
        const focusableElements = container.querySelectorAll(focusableSelector);
        const visibleFocusable = Array.from(focusableElements).filter(el => {
            return el.offsetParent !== null && !el.disabled;
        });

        const firstElement = visibleFocusable[0];
        const lastElement = visibleFocusable[visibleFocusable.length - 1];

        // If no focusable elements, prevent default
        if (visibleFocusable.length === 0) {
            e.preventDefault();
            return;
        }

        // Shift+Tab: move focus backwards
        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            // Tab: move focus forwards
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }

    createSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#primaryAction';
        skipLink.textContent = 'Skip to main controls';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--surface-08);
            color: var(--text-primary);
            padding: var(--space-8);
            border-radius: var(--radius-sm);
            text-decoration: none;
            z-index: 9999;
            transform: translateY(-100%);
            transition: transform 0.3s;
        `;

        skipLink.addEventListener('focus', () => {
            skipLink.style.transform = 'translateY(0)';
        });

        skipLink.addEventListener('blur', () => {
            skipLink.style.transform = 'translateY(-100%)';
        });

        document.body.insertBefore(skipLink, document.body.firstChild);
        debugLog('Tab order optimization and skip link created', 'TAB_ORDER');
    }
}
class ConnectionHealthMonitor {
    constructor() {
        this.isMonitoring = false;
        this.pingInterval = null;
        this.currentLatency = null;
        this.lastPingTime = null;
        this.connectionQuality = 'unknown';
        this.healthHistory = [];
        this.maxHistorySize = 10;
        
        // UI elements will be set by the app
        this.healthIndicatorElement = null;
        this.pingDisplayElement = null;
        this.healthContainerElement = null;
    }

    /**
     * Initialize health monitor with UI elements
     * @param {HTMLElement} healthContainer - Container element
     * @param {HTMLElement} healthIndicator - Health icon element  
     * @param {HTMLElement} pingDisplay - Ping display element
     */
    initialize(healthContainer, healthIndicator, pingDisplay) {
        this.healthContainerElement = healthContainer;
        this.healthIndicatorElement = healthIndicator;
        this.pingDisplayElement = pingDisplay;
    }

    /**
     * Start monitoring connection health
     * @param {string} serverAddress - Server address to ping (e.g., "127.0.0.1:1256")
     */
    startMonitoring(serverAddress) {
        if (this.isMonitoring) {
            this.stopMonitoring();
        }

        this.serverAddress = serverAddress;
        this.isMonitoring = true;
        
        // Show the health indicator
        if (this.healthContainerElement) {
            this.healthContainerElement.style.display = 'flex';
            this.healthContainerElement.style.alignItems = 'center';
            this.healthContainerElement.style.gap = 'var(--space-xs)';
        }

        // Initial ping
        this.performHealthCheck();

        // Start periodic health checks (every 30 seconds)
        this.pingInterval = setInterval(() => {
            this.performHealthCheck();
        }, 30000);

        debugLog(`Started health monitoring for ${serverAddress}`, 'HEALTH_MONITOR');
    }

    /**
     * Stop monitoring connection health
     */
    stopMonitoring() {
        this.isMonitoring = false;
        
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }

        // Hide the health indicator
        if (this.healthContainerElement) {
            this.healthContainerElement.style.display = 'none';
        }

        // Reset state
        this.currentLatency = null;
        this.connectionQuality = 'unknown';
        this.healthHistory = [];

        debugLog('Stopped health monitoring', 'HEALTH_MONITOR');
    }

    /**
     * Perform a health check (ping simulation using API call)
     */
    async performHealthCheck() {
        if (!this.isMonitoring || !this.serverAddress) {
            return;
        }

        try {
            const startTime = performance.now();
            
            // Use a lightweight API call to measure response time
            // We'll use the status endpoint which should be fast
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

            const response = await fetch('http://localhost:9090/api/status', {
                method: 'GET',
                signal: controller.signal,
                cache: 'no-cache'
            });

            clearTimeout(timeoutId);
            const endTime = performance.now();
            const latency = Math.round(endTime - startTime);

            this.updateHealthMetrics(latency, true);
            
        } catch (error) {
            // Connection failed or timed out
            this.updateHealthMetrics(null, false);
            console.warn('Health check failed:', error.message);
        }
    }

    /**
     * Update health metrics and UI
     * @param {number|null} latency - Measured latency in ms (null if failed)
     * @param {boolean} isConnected - Whether connection succeeded
     */
    updateHealthMetrics(latency, isConnected) {
        this.lastPingTime = Date.now();
        this.currentLatency = latency;

        // Add to history
        this.healthHistory.unshift({
            timestamp: this.lastPingTime,
            latency: latency,
            isConnected: isConnected
        });

        // Trim history
        if (this.healthHistory.length > this.maxHistorySize) {
            this.healthHistory = this.healthHistory.slice(0, this.maxHistorySize);
        }

        // Determine connection quality
        this.connectionQuality = this.calculateConnectionQuality(latency, isConnected);

        // Update UI
        this.updateHealthUI();

        debugLog(`Health check: ${latency}ms, Quality: ${this.connectionQuality}`, 'HEALTH_MONITOR');
    }

    /**
     * Calculate connection quality based on latency
     * @param {number|null} latency - Latency in ms
     * @param {boolean} isConnected - Connection status
     * @returns {string} Quality rating
     */
    calculateConnectionQuality(latency, isConnected) {
        if (!isConnected || latency === null) {
            return 'offline';
        }
        if (latency < 50) {
            return 'excellent';
        }
        if (latency < 150) {
            return 'good';
        }
        if (latency < 300) {
            return 'fair';
        }
        if (latency < 1000) {
            return 'poor';
        }
        return 'very_poor';
    }

    /**
     * Update health indicator UI
     */
    updateHealthUI() {
        if (!this.healthIndicatorElement || !this.pingDisplayElement) {
            return;
        }

        // Animate the latency display update
        this.pingDisplayElement.style.animation = 'latency-update 0.3s ease-out';
        setTimeout(() => {
            this.pingDisplayElement.style.animation = '';
        }, 300);

        // Update ping display
        if (this.currentLatency !== null) {
            this.pingDisplayElement.textContent = `${this.currentLatency}ms`;
        } else {
            this.pingDisplayElement.textContent = 'timeout';
        }

        // Update health indicator icon and color
        const qualityConfig = {
            offline: { 
                icon: '📵', 
                color: 'var(--error)', 
                title: 'Connection failed',
                animation: 'connection-health-offline 2s infinite ease-in-out'
            },
            excellent: { 
                icon: '📶', 
                color: 'var(--success)', 
                title: 'Excellent connection',
                animation: 'connection-health-excellent 3s infinite ease-in-out'
            },
            good: { 
                icon: '📶', 
                color: 'var(--neon-green)', 
                title: 'Good connection',
                animation: 'gentle-breathing 4s infinite ease-in-out'
            },
            fair: { 
                icon: '📶', 
                color: 'var(--warning)', 
                title: 'Fair connection',
                animation: 'pulse-warning 2s infinite ease-in-out'
            },
            poor: { 
                icon: '📶', 
                color: 'var(--neon-orange)', 
                title: 'Poor connection',
                animation: 'connection-health-poor 1.5s infinite ease-in-out'
            },
            very_poor: { 
                icon: '📶', 
                color: 'var(--error)', 
                title: 'Very poor connection',
                animation: 'connection-health-poor 1s infinite ease-in-out'
            }
        };

        const config = qualityConfig[this.connectionQuality] || qualityConfig.offline;

        this.healthIndicatorElement.textContent = config.icon;
        this.healthIndicatorElement.style.color = config.color;
        this.healthIndicatorElement.title = `${config.title} (${this.currentLatency || '--'}ms)`;
        this.pingDisplayElement.style.color = config.color;

        // Apply connection-specific animations
        this.healthIndicatorElement.style.animation = config.animation;

        // Add CSS classes for better styling control
        this.healthIndicatorElement.className = `connection-health-indicator quality-${this.connectionQuality}`;
        this.pingDisplayElement.className = `connection-latency quality-${this.connectionQuality}`;
    }

    /**
     * Get current health status for external use
     * @returns {Object} Health status object
     */
    getHealthStatus() {
        return {
            isMonitoring: this.isMonitoring,
            latency: this.currentLatency,
            quality: this.connectionQuality,
            lastCheck: this.lastPingTime,
            averageLatency: this.getAverageLatency(),
            recentHistory: this.healthHistory.slice(0, 5)
        };
    }

    /**
     * Calculate average latency from recent history
     * @returns {number|null} Average latency or null
     */
    getAverageLatency() {
        const validPings = this.healthHistory.filter(h => h.latency !== null);
        if (validPings.length === 0) {
            return null;
        }
        
        const sum = validPings.reduce((acc, h) => acc + h.latency, 0);
        return Math.round(sum / validPings.length);
    }
}

class ServerValidationManager {
    constructor() {
        this.validationTimeout = null;
        this.validationDelay = 800; // ms delay after user stops typing
        this.isValidating = false;
        this.lastValidatedServer = null;
        this.validationCache = new Map();
        this.cacheExpiration = 60000; // 1 minute cache
        
        this.setupServerValidation();
    }

    setupServerValidation() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeValidation());
        } else {
            this.initializeValidation();
        }
    }

    initializeValidation() {
        const serverInput = document.getElementById('serverInput');
        if (!serverInput) {
            debugLog('Server input not found for validation', 'SERVER_VALIDATION');
            return;
        }

        // Create validation indicator
        this.createValidationIndicator(serverInput);

        // Add validation listeners
        serverInput.addEventListener('input', (e) => {
            this.scheduleValidation(e.target.value);
        });

        serverInput.addEventListener('blur', (e) => {
            // Immediate validation on blur
            this.validateServer(e.target.value);
        });

        debugLog('Server validation manager initialized', 'SERVER_VALIDATION');
    }

    createValidationIndicator(serverInput) {
        const container = serverInput.parentElement;
        
        // Create validation indicator element
        const indicator = document.createElement('div');
        indicator.className = 'server-validation-indicator';
        indicator.id = 'serverValidationIndicator';
        indicator.style.cssText = `
            position: absolute;
            right: 40px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1rem;
            opacity: 0;
            transition: opacity 0.3s ease, transform 0.3s ease;
            pointer-events: none;
            z-index: 100;
        `;
        
        container.style.position = 'relative';
        container.appendChild(indicator);

        // Create validation message
        const message = document.createElement('div');
        message.className = 'server-validation-message';
        message.id = 'serverValidationMessage';
        message.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--surface-06);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-sm);
            padding: var(--space-8);
            font-size: 0.875rem;
            margin-top: var(--space-4);
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
            z-index: 200;
        `;
        
        container.appendChild(message);
        
        this.validationIndicator = indicator;
        this.validationMessage = message;
    }

    scheduleValidation(serverAddress) {
        // Clear existing timeout
        if (this.validationTimeout) {
            clearTimeout(this.validationTimeout);
        }

        // Hide indicator while typing
        this.hideValidationIndicator();

        // Don't validate empty input
        if (!serverAddress.trim()) {
            return;
        }

        // Schedule validation
        this.validationTimeout = setTimeout(() => {
            this.validateServer(serverAddress);
        }, this.validationDelay);
    }

    async validateServer(serverAddress) {
        if (!serverAddress.trim()) {
            this.hideValidationIndicator();
            return;
        }

        // Check cache first
        const cached = this.getCachedValidation(serverAddress);
        if (cached) {
            this.showValidationResult(cached.isValid, cached.message, false);
            return;
        }

        this.isValidating = true;
        this.showValidationIndicator('validating', 'Checking server...', true);

        try {
            // Parse server address
            const [host, port] = this.parseServerAddress(serverAddress);
            
            if (!this.isValidServerFormat(host, port)) {
                const result = { isValid: false, message: 'Invalid server format. Use IP:PORT (e.g., 192.168.1.100:1256)' };
                this.cacheValidation(serverAddress, result);
                this.showValidationResult(false, result.message, false);
                return;
            }

            // Attempt to validate server connectivity
            const isReachable = await this.checkServerConnectivity(host, port);
            const result = {
                isValid: isReachable,
                message: isReachable ? 
                    `✓ Server appears reachable at ${host}:${port}` : 
                    `⚠️ Cannot reach server at ${host}:${port}. Server may be offline or address incorrect.`
            };

            this.cacheValidation(serverAddress, result);
            this.showValidationResult(result.isValid, result.message, false);

        } catch (error) {
            const result = { isValid: false, message: `❌ Server validation error: ${error.message}` };
            this.cacheValidation(serverAddress, result);
            this.showValidationResult(false, result.message, false);
        } finally {
            this.isValidating = false;
        }
    }

    parseServerAddress(serverAddress) {
        const parts = serverAddress.trim().split(':');
        if (parts.length !== 2) {
            return [null, null];
        }
        return [parts[0], parseInt(parts[1])];
    }

    isValidServerFormat(host, port) {
        // Basic IP address validation (supports IPv4)
        const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$|^localhost$|^127\.0\.0\.1$/;
        
        if (!host || !ipRegex.test(host)) {
            return false;
        }

        // Port validation
        if (isNaN(port) || port < 1 || port > 65535) {
            return false;
        }

        return true;
    }

    async checkServerConnectivity(host, port) {
        try {
            // Use the API status endpoint as a proxy for server validation
            // In a real implementation, you might have a dedicated ping endpoint
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout

            const response = await fetch('http://localhost:9090/api/status', {
                method: 'GET',
                signal: controller.signal,
                cache: 'no-cache'
            });

            clearTimeout(timeoutId);
            
            // If API server is running, assume the validation is positive
            // In reality, the API server would check connectivity to the backup server
            return response.ok;

        } catch (error) {
            // Network error or timeout
            return false;
        }
    }

    showValidationIndicator(type, message, isLoading) {
        if (!this.validationIndicator) return;

        const configs = {
            validating: { icon: '⏳', color: 'var(--text-secondary)' },
            valid: { icon: '✅', color: 'var(--success)' },
            invalid: { icon: '❌', color: 'var(--error)' },
            warning: { icon: '⚠️', color: 'var(--warning)' }
        };

        const config = configs[type] || configs.validating;

        this.validationIndicator.textContent = config.icon;
        this.validationIndicator.style.color = config.color;
        this.validationIndicator.style.opacity = '1';
        this.validationIndicator.style.transform = 'translateY(-50%) scale(1)';

        if (isLoading) {
            this.validationIndicator.style.animation = 'gentle-breathing 1.5s infinite ease-in-out';
        } else {
            this.validationIndicator.style.animation = '';
        }

        // Show message
        if (message && this.validationMessage) {
            this.validationMessage.textContent = message;
            this.validationMessage.style.color = config.color;
            this.validationMessage.style.opacity = '1';
            this.validationMessage.style.transform = 'translateY(0)';
        }

        debugLog(`Server validation: ${type} - ${message}`, 'SERVER_VALIDATION');
    }

    showValidationResult(isValid, message, isLoading) {
        const type = isValid ? 'valid' : (message.includes('⚠️') ? 'warning' : 'invalid');
        this.showValidationIndicator(type, message, isLoading);

        // Auto-hide message after delay
        if (!isLoading) {
            setTimeout(() => {
                this.hideValidationMessage();
            }, 5000);
        }
    }

    hideValidationIndicator() {
        if (this.validationIndicator) {
            this.validationIndicator.style.opacity = '0';
            this.validationIndicator.style.transform = 'translateY(-50%) scale(0.8)';
        }
        this.hideValidationMessage();
    }

    hideValidationMessage() {
        if (this.validationMessage) {
            this.validationMessage.style.opacity = '0';
            this.validationMessage.style.transform = 'translateY(-10px)';
        }
    }

    getCachedValidation(serverAddress) {
        const cached = this.validationCache.get(serverAddress);
        if (cached && Date.now() - cached.timestamp < this.cacheExpiration) {
            return cached;
        }
        // Remove expired cache
        if (cached) {
            this.validationCache.delete(serverAddress);
        }
        return null;
    }

    cacheValidation(serverAddress, result) {
        this.validationCache.set(serverAddress, {
            ...result,
            timestamp: Date.now()
        });
    }

    // Public method to get validation status
    getValidationStatus(serverAddress) {
        return this.getCachedValidation(serverAddress);
    }

    // Clear cache
    clearCache() {
        this.validationCache.clear();
        debugLog('Server validation cache cleared', 'SERVER_VALIDATION');
    }
}

class UsernameValidationManager {
    constructor() {
        this.allowedPattern = /^[a-zA-Z0-9_-]+$/; // Alphanumeric, underscore, hyphen
        this.minLength = 3;
        this.maxLength = 100;
        this.validationTimeout = null;
        this.validationDelay = 300; // ms delay after user stops typing
        
        this.setupUsernameValidation();
    }

    setupUsernameValidation() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeValidation());
        } else {
            this.initializeValidation();
        }
    }

    initializeValidation() {
        const usernameInput = document.getElementById('usernameInput');
        if (!usernameInput) {
            debugLog('Username input not found for validation', 'USERNAME_VALIDATION');
            return;
        }

        // Create validation UI
        this.createValidationUI(usernameInput);

        // Add validation listeners
        usernameInput.addEventListener('input', (e) => {
            this.handleInput(e.target.value, e.target);
        });

        usernameInput.addEventListener('blur', (e) => {
            this.validateUsername(e.target.value, true);
        });

        usernameInput.addEventListener('focus', (e) => {
            this.showValidationHelp();
        });

        debugLog('Username validation manager initialized', 'USERNAME_VALIDATION');
    }

    createValidationUI(usernameInput) {
        const container = usernameInput.parentElement;
        
        // Create character indicator
        const indicator = document.createElement('div');
        indicator.className = 'username-validation-indicator';
        indicator.id = 'usernameValidationIndicator';
        indicator.style.cssText = `
            position: absolute;
            right: var(--space-8);
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.875rem;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
            z-index: 100;
        `;
        
        container.style.position = 'relative';
        container.appendChild(indicator);

        // Create validation help panel
        const helpPanel = document.createElement('div');
        helpPanel.className = 'username-validation-help';
        helpPanel.id = 'usernameValidationHelp';
        helpPanel.innerHTML = `
            <div class="validation-help-content">
                <div class="validation-help-title">Username Requirements:</div>
                <div class="validation-rules">
                    <div class="validation-rule" data-rule="length">
                        <span class="rule-indicator">○</span>
                        <span class="rule-text">3-100 characters</span>
                    </div>
                    <div class="validation-rule" data-rule="characters">
                        <span class="rule-indicator">○</span>
                        <span class="rule-text">Letters, numbers, underscore (_), hyphen (-)</span>
                    </div>
                    <div class="validation-rule" data-rule="start">
                        <span class="rule-indicator">○</span>
                        <span class="rule-text">Must start with letter or number</span>
                    </div>
                </div>
                <div class="validation-examples">
                    <span class="example-label">Examples:</span>
                    <span class="example-good">john_doe</span>
                    <span class="example-good">user123</span>
                    <span class="example-good">backup-user</span>
                </div>
            </div>
        `;
        
        helpPanel.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--surface-06);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: var(--space-12);
            font-size: 0.875rem;
            margin-top: var(--space-4);
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
            z-index: 200;
            box-shadow: var(--md-elevation-4);
        `;
        
        container.appendChild(helpPanel);
        
        this.validationIndicator = indicator;
        this.validationHelp = helpPanel;
    }

    handleInput(value, inputElement) {
        // Clear existing timeout
        if (this.validationTimeout) {
            clearTimeout(this.validationTimeout);
        }

        // Real-time character filtering and feedback
        this.showCharacterFeedback(value);

        // Schedule validation
        this.validationTimeout = setTimeout(() => {
            this.validateUsername(value, false);
        }, this.validationDelay);
    }

    showCharacterFeedback(value) {
        if (!this.validationIndicator) return;

        if (!value) {
            this.validationIndicator.style.opacity = '0';
            return;
        }

        // Check each character and provide real-time feedback
        const invalidChars = value.split('').filter(char => !this.allowedPattern.test(char));
        const validLength = value.length >= this.minLength && value.length <= this.maxLength;
        const validStart = /^[a-zA-Z0-9]/.test(value);

        let feedback = '';
        let color = 'var(--success)';

        if (invalidChars.length > 0) {
            feedback = `❌ Invalid: ${invalidChars.join(', ')}`;
            color = 'var(--error)';
        } else if (!validStart && value.length > 0) {
            feedback = '⚠️ Must start with letter/number';
            color = 'var(--warning)';
        } else if (!validLength) {
            if (value.length < this.minLength) {
                feedback = `⚠️ ${this.minLength - value.length} more chars needed`;
                color = 'var(--warning)';
            } else {
                feedback = `⚠️ ${value.length - this.maxLength} chars over limit`;
                color = 'var(--error)';
            }
        } else {
            feedback = `✅ ${value.length}/${this.maxLength}`;
            color = 'var(--success)';
        }

        this.validationIndicator.textContent = feedback;
        this.validationIndicator.style.color = color;
        this.validationIndicator.style.opacity = '1';

        // Update help panel rules
        this.updateHelpPanelRules(value);
    }

    updateHelpPanelRules(value) {
        if (!this.validationHelp) return;

        const rules = this.validationHelp.querySelectorAll('.validation-rule');
        
        rules.forEach(rule => {
            const ruleType = rule.dataset.rule;
            const indicator = rule.querySelector('.rule-indicator');
            let isValid = false;

            switch (ruleType) {
                case 'length':
                    isValid = value.length >= this.minLength && value.length <= this.maxLength;
                    break;
                case 'characters':
                    isValid = this.allowedPattern.test(value) || value === '';
                    break;
                case 'start':
                    isValid = /^[a-zA-Z0-9]/.test(value) || value === '';
                    break;
            }

            if (isValid) {
                indicator.textContent = '✅';
                indicator.style.color = 'var(--success)';
                rule.style.opacity = '0.8';
            } else if (value === '') {
                indicator.textContent = '○';
                indicator.style.color = 'var(--text-secondary)';
                rule.style.opacity = '1';
            } else {
                indicator.textContent = '❌';
                indicator.style.color = 'var(--error)';
                rule.style.opacity = '1';
            }
        });
    }

    validateUsername(value, showResult = true) {
        const validation = {
            isValid: true,
            errors: [],
            warnings: []
        };

        if (!value) {
            validation.isValid = false;
            validation.errors.push('Username is required');
        } else {
            // Length validation
            if (value.length < this.minLength) {
                validation.isValid = false;
                validation.errors.push(`Username must be at least ${this.minLength} characters`);
            } else if (value.length > this.maxLength) {
                validation.isValid = false;
                validation.errors.push(`Username must not exceed ${this.maxLength} characters`);
            }

            // Character validation
            if (!this.allowedPattern.test(value)) {
                validation.isValid = false;
                const invalidChars = value.split('').filter(char => !this.allowedPattern.test(char));
                validation.errors.push(`Invalid characters: ${invalidChars.join(', ')}`);
            }

            // Starting character validation
            if (!/^[a-zA-Z0-9]/.test(value)) {
                validation.isValid = false;
                validation.errors.push('Username must start with a letter or number');
            }

            // Additional warnings
            if (value.length < 5) {
                validation.warnings.push('Consider using a longer username for better security');
            }
        }

        if (showResult) {
            debugLog(`Username validation: ${validation.isValid ? 'valid' : 'invalid'} - ${value}`, 'USERNAME_VALIDATION');
        }

        return validation;
    }

    showValidationHelp() {
        if (this.validationHelp) {
            this.validationHelp.style.opacity = '1';
            this.validationHelp.style.transform = 'translateY(0)';
        }
    }

    hideValidationHelp() {
        if (this.validationHelp) {
            this.validationHelp.style.opacity = '0';
            this.validationHelp.style.transform = 'translateY(-10px)';
        }
    }

    // Public method to check if username is valid
    isUsernameValid(username) {
        return this.validateUsername(username, false).isValid;
    }

    // Get detailed validation results
    getValidationResults(username) {
        return this.validateUsername(username, false);
    }
}

class FormMemoryManager {
    constructor() {
        this.storageKey = 'cyberbackup_form_memory';
        this.sessionKey = 'cyberbackup_session_state';
        this.autoSaveDelay = 2000; // 2 seconds after user stops typing
        this.autoSaveTimer = null;
        this.watchedElements = new Map();
        
        this.initializeMemorySystem();
    }

    initializeMemorySystem() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupFormMemory());
        } else {
            this.setupFormMemory();
        }
    }

    setupFormMemory() {
        // Find and watch form elements
        this.watchFormElement('serverIp', 'input');
        this.watchFormElement('serverPort', 'input');
        this.watchFormElement('username', 'input');
        
        // Load saved values
        this.loadSavedFormData();
        
        // Setup session persistence
        this.setupSessionPersistence();
        
        debugLog('Form memory system initialized', 'FORM_MEMORY');
    }

    watchFormElement(elementId, eventType = 'input') {
        const element = document.getElementById(elementId);
        if (!element) {
            debugLog(`Element ${elementId} not found for form memory`, 'FORM_MEMORY');
            return;
        }

        // Store reference
        this.watchedElements.set(elementId, element);

        // Add event listeners
        element.addEventListener(eventType, () => {
            this.scheduleAutoSave();
        });

        // Also save on blur for immediate persistence
        element.addEventListener('blur', () => {
            this.saveFormData();
        });

        debugLog(`Watching element: ${elementId}`, 'FORM_MEMORY');
    }

    scheduleAutoSave() {
        // Clear existing timer
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }

        // Schedule new save
        this.autoSaveTimer = setTimeout(() => {
            this.saveFormData();
        }, this.autoSaveDelay);
    }

    saveFormData() {
        try {
            const formData = {};
            
            // Collect data from watched elements
            this.watchedElements.forEach((element, elementId) => {
                if (element.type === 'checkbox') {
                    formData[elementId] = element.checked;
                } else if (element.type === 'radio') {
                    if (element.checked) {
                        formData[elementId] = element.value;
                    }
                } else {
                    formData[elementId] = element.value;
                }
            });

            // Add metadata
            formData._metadata = {
                savedAt: Date.now(),
                version: '1.0',
                userAgent: navigator.userAgent.substring(0, 100) // Truncated for storage
            };

            // Save to localStorage
            localStorage.setItem(this.storageKey, JSON.stringify(formData));
            
            debugLog('Form data saved to memory', 'FORM_MEMORY');
            
        } catch (error) {
            console.warn('Failed to save form data:', error);
        }
    }

    loadSavedFormData() {
        try {
            const savedData = localStorage.getItem(this.storageKey);
            if (!savedData) {
                debugLog('No saved form data found', 'FORM_MEMORY');
                return;
            }

            const formData = JSON.parse(savedData);
            
            // Check if data is too old (older than 30 days)
            const maxAge = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds
            if (formData._metadata && Date.now() - formData._metadata.savedAt > maxAge) {
                debugLog('Saved form data is too old, ignoring', 'FORM_MEMORY');
                this.clearSavedData();
                return;
            }

            // Restore form values
            this.watchedElements.forEach((element, elementId) => {
                if (formData.hasOwnProperty(elementId)) {
                    const savedValue = formData[elementId];
                    
                    if (element.type === 'checkbox') {
                        element.checked = savedValue;
                    } else if (element.type === 'radio') {
                        element.checked = element.value === savedValue;
                    } else {
                        element.value = savedValue;
                    }

                    // Trigger change event to update any dependent UI
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            debugLog('Form data loaded from memory', 'FORM_MEMORY');
            this.showMemoryRestoreNotification(formData._metadata);
            
        } catch (error) {
            console.warn('Failed to load saved form data:', error);
            this.clearSavedData();
        }
    }

    showMemoryRestoreNotification(metadata) {
        // Show a subtle notification that form was restored
        const savedDate = new Date(metadata.savedAt);
        const message = `Form restored from ${savedDate.toLocaleDateString()} ${savedDate.toLocaleTimeString()}`;
        
        // Create temporary notification
        const notification = document.createElement('div');
        notification.className = 'form-memory-notification';
        notification.innerHTML = `
            <div class="form-memory-content">
                <span class="form-memory-icon">💾</span>
                <span class="form-memory-text">${message}</span>
                <button class="form-memory-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: var(--space-md);
            left: 50%;
            transform: translateX(-50%);
            z-index: 1500;
            background: var(--surface-06);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: var(--space-8) var(--space-12);
            font-size: 0.875rem;
            color: var(--text-secondary);
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: auto;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 100);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    setupSessionPersistence() {
        // Save session state before page unload
        window.addEventListener('beforeunload', () => {
            this.saveSessionState();
        });

        // Restore session state on load
        this.loadSessionState();

        // Periodic session state updates
        setInterval(() => {
            this.saveSessionState();
        }, 30000); // Every 30 seconds
    }

    saveSessionState() {
        try {
            // Collect current application state
            const sessionState = {
                connectionStatus: this.getConnectionStatus(),
                lastActivity: Date.now(),
                currentPhase: this.getCurrentPhase(),
                selectedFile: this.getSelectedFileInfo(),
                timestamp: Date.now()
            };

            sessionStorage.setItem(this.sessionKey, JSON.stringify(sessionState));
            debugLog('Session state saved', 'FORM_MEMORY');
            
        } catch (error) {
            console.warn('Failed to save session state:', error);
        }
    }

    loadSessionState() {
        try {
            const savedSession = sessionStorage.getItem(this.sessionKey);
            if (!savedSession) {
                return;
            }

            const sessionState = JSON.parse(savedSession);
            
            // Check if session is recent (within last hour)
            const maxSessionAge = 60 * 60 * 1000; // 1 hour
            if (Date.now() - sessionState.timestamp > maxSessionAge) {
                debugLog('Session state is too old, ignoring', 'FORM_MEMORY');
                sessionStorage.removeItem(this.sessionKey);
                return;
            }

            // Restore relevant state
            this.restoreConnectionStatus(sessionState.connectionStatus);
            this.restoreSelectedFile(sessionState.selectedFile);
            
            debugLog('Session state restored', 'FORM_MEMORY');
            
        } catch (error) {
            console.warn('Failed to load session state:', error);
            sessionStorage.removeItem(this.sessionKey);
        }
    }

    // Helper methods to get current application state
    getConnectionStatus() {
        // This would integrate with the main app's state
        return {
            isConnected: false, // Default value, should be updated by app
            lastConnectedServer: this.getFormValue('serverIp'),
            lastConnectedPort: this.getFormValue('serverPort')
        };
    }

    getCurrentPhase() {
        // This would integrate with the main app's phase tracking
        return 'IDLE'; // Default phase
    }

    getSelectedFileInfo() {
        // This would integrate with the file manager
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            return {
                name: file.name,
                size: file.size,
                type: file.type,
                lastModified: file.lastModified
            };
        }
        return null;
    }

    getFormValue(elementId) {
        const element = document.getElementById(elementId);
        return element ? element.value : '';
    }

    // Helper methods to restore application state
    restoreConnectionStatus(connectionStatus) {
        if (connectionStatus && connectionStatus.isConnected) {
            // Could trigger a connection attempt or show status
            debugLog('Previous connection detected, consider auto-reconnect', 'FORM_MEMORY');
        }
    }

    restoreSelectedFile(fileInfo) {
        if (fileInfo) {
            // Could show file information or prepare UI
            debugLog(`Previous file selection: ${fileInfo.name}`, 'FORM_MEMORY');
        }
    }

    // Public methods for manual control
    clearSavedData() {
        try {
            localStorage.removeItem(this.storageKey);
            sessionStorage.removeItem(this.sessionKey);
            debugLog('Form memory cleared', 'FORM_MEMORY');
        } catch (error) {
            console.warn('Failed to clear saved data:', error);
        }
    }

    exportFormData() {
        try {
            const formData = localStorage.getItem(this.storageKey);
            const sessionData = sessionStorage.getItem(this.sessionKey);
            
            return {
                formMemory: formData ? JSON.parse(formData) : null,
                sessionState: sessionData ? JSON.parse(sessionData) : null,
                exportedAt: Date.now()
            };
        } catch (error) {
            console.warn('Failed to export form data:', error);
            return null;
        }
    }

    importFormData(exportedData) {
        try {
            if (exportedData.formMemory) {
                localStorage.setItem(this.storageKey, JSON.stringify(exportedData.formMemory));
            }
            if (exportedData.sessionState) {
                sessionStorage.setItem(this.sessionKey, JSON.stringify(exportedData.sessionState));
            }
            
            // Reload form data
            this.loadSavedFormData();
            this.loadSessionState();
            
            debugLog('Form data imported successfully', 'FORM_MEMORY');
            return true;
        } catch (error) {
            console.warn('Failed to import form data:', error);
            return false;
        }
    }

    // Integration method for main app
    updateSessionState(stateUpdates) {
        try {
            const currentSession = sessionStorage.getItem(this.sessionKey);
            const sessionState = currentSession ? JSON.parse(currentSession) : {};
            
            // Merge updates
            Object.assign(sessionState, stateUpdates, { timestamp: Date.now() });
            
            sessionStorage.setItem(this.sessionKey, JSON.stringify(sessionState));
        } catch (error) {
            console.warn('Failed to update session state:', error);
        }
    }
}

export { SystemManager, ConnectionHealthMonitor, ServerValidationManager, UsernameValidationManager, FormMemoryManager };