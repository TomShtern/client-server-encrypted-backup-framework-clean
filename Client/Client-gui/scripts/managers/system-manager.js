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
        if (!this.isMonitoring || !this.serverAddress) return;

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
        if (!isConnected || latency === null) return 'offline';
        if (latency < 50) return 'excellent';
        if (latency < 150) return 'good';
        if (latency < 300) return 'fair';
        if (latency < 1000) return 'poor';
        return 'very_poor';
    }

    /**
     * Update health indicator UI
     */
    updateHealthUI() {
        if (!this.healthIndicatorElement || !this.pingDisplayElement) return;

        // Update ping display
        if (this.currentLatency !== null) {
            this.pingDisplayElement.textContent = `${this.currentLatency}ms`;
        } else {
            this.pingDisplayElement.textContent = 'timeout';
        }

        // Update health indicator icon and color
        const qualityConfig = {
            offline: { icon: '📵', color: 'var(--error)', title: 'Connection failed' },
            excellent: { icon: '📶', color: 'var(--success)', title: 'Excellent connection' },
            good: { icon: '📶', color: 'var(--neon-green)', title: 'Good connection' },
            fair: { icon: '📶', color: 'var(--warning)', title: 'Fair connection' },
            poor: { icon: '📶', color: 'var(--neon-orange)', title: 'Poor connection' },
            very_poor: { icon: '📶', color: 'var(--error)', title: 'Very poor connection' }
        };

        const config = qualityConfig[this.connectionQuality] || qualityConfig.offline;

        this.healthIndicatorElement.textContent = config.icon;
        this.healthIndicatorElement.style.color = config.color;
        this.healthIndicatorElement.title = `${config.title} (${this.currentLatency || '--'}ms)`;
        this.pingDisplayElement.style.color = config.color;

        // Add subtle animation for poor connections
        if (this.connectionQuality === 'poor' || this.connectionQuality === 'very_poor') {
            this.healthIndicatorElement.style.animation = 'pulse 2s infinite';
        } else {
            this.healthIndicatorElement.style.animation = 'none';
        }
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
        if (validPings.length === 0) return null;
        
        const sum = validPings.reduce((acc, h) => acc + h.latency, 0);
        return Math.round(sum / validPings.length);
    }
}

export { SystemManager, ConnectionHealthMonitor };