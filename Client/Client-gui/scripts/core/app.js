import { IntervalManager, debugLog, debugLogger } from './debug-utils.js';
import { EventListenerManager } from '../utils/event-manager.js';
import { ApiClient } from './api-client.js';
import { FileManager, FileMemoryManager } from '../managers/file-manager.js';
import { SystemManager, ConnectionHealthMonitor } from '../managers/system-manager.js';
import { NotificationManager, ModalManager, ConfirmModalManager, ThemeManager, ButtonStateManager, ToastManager } from '../managers/ui-manager.js';
import { BackupHistoryManager } from '../managers/backup-manager.js';
import { ErrorBoundary, ErrorMessageFormatter } from '../ui/error-boundary.js';
import { ParticleSystem } from '../ui/particle-system.js';
import { CopyManager } from '../utils/copy-manager.js';
import { FormValidator } from '../utils/form-validator.js';
import { InteractiveEffectsManager } from '../managers/interactive-effects-manager.js';

class App {
    constructor() {
        this.apiClient = new ApiClient();
        this.system = new SystemManager();
        this.intervals = new IntervalManager();
        this.eventListeners = new EventListenerManager();
        this.buttonStateManager = new ButtonStateManager();
        this.toastManager = new ToastManager(); // New enhanced toast system
        this.errorMessageFormatter = new ErrorMessageFormatter();
        this.copyManager = new CopyManager();
        this.formValidator = new FormValidator();
        this.fileMemoryManager = new FileMemoryManager();
        this.backupHistoryManager = new BackupHistoryManager();
        this.connectionHealthMonitor = new ConnectionHealthMonitor();
        this.interactiveEffects = new InteractiveEffectsManager();
        
        // Initialize WebSocket connection for real-time updates
        this.socket = null;
        this.socketConnected = false;
        this.initializeWebSocket();

        this.elements = {
            connectionLed: document.getElementById('connectionLed'),
            connectionText: document.getElementById('connectionText'),
            serverInput: document.getElementById('serverInput'),
            usernameInput: document.getElementById('usernameInput'),
            fileDropZone: document.getElementById('fileDropZone'),
            fileInput: document.getElementById('fileInput'),
            recentFilesBtn: document.getElementById('recentFilesBtn'),
            selectedFileDisplay: document.getElementById('selectedFile'),
            filePreview: document.getElementById('filePreview'),
            clientIdDisplay: document.getElementById('clientId'),
            copyClientIdButton: document.getElementById('copyClientId'),
            copyServerAddressButton: document.getElementById('copyServerAddress'),
            copyFileInfoButton: document.getElementById('copyFileInfo'),
            primaryActionButton: document.getElementById('primaryAction'),
            pauseButton: document.getElementById('pauseBtn'),
            stopButton: document.getElementById('stopBtn'),
            currentPhaseDisplay: document.getElementById('currentPhase'),
            progressCircle: document.getElementById('progressCircle'),
            progressPercentage: document.getElementById('progressPercentage'),
            progressStatus: document.getElementById('progressStatus'),
            // Data Stream Progress Ring elements
            dataChannelRing: document.getElementById('dataChannelRing'),
            phaseIndicatorArc: document.getElementById('phaseIndicatorArc'),
            particleStream: document.getElementById('particleStream'),
            progressRing: document.querySelector('.progress-ring'),
            speedStat: document.getElementById('speedStat'),
            etaStat: document.getElementById('etaStat'),
            transferredStat: document.getElementById('transferredStat'),
            sizeStat: document.getElementById('sizeStat'),
            logContainer: document.getElementById('logContainer'),
            autoScrollBtn: document.getElementById('autoScrollBtn'),
            debugToggle: document.getElementById('debugToggle'),
            debugContent: document.getElementById('debugContent'),
            statusJsonViewer: document.getElementById('statusJsonViewer'),
            progressJsonViewer: document.getElementById('progressJsonViewer'),
            toastContainer: document.getElementById('toastContainer'),
            confirmModal: document.getElementById('confirmModal'),
            confirmTitle: document.getElementById('confirmTitle'),
            confirmMessage: document.getElementById('confirmMessage'),
            confirmOkBtn: document.getElementById('confirmOkBtn'),
            cancelModalBtn: document.getElementById('cancelModalBtn'),
            connectionHealth: document.getElementById('connectionHealth'),
            healthIndicator: document.getElementById('healthIndicator'),
            pingDisplay: document.getElementById('pingDisplay'),
            // Additional frequently accessed elements
            saveConfigBtn: document.querySelector('[data-action="save-config"]'),
            exportLogBtn: document.querySelector('[data-action="export-log"]'),
            clearLogBtn: document.querySelector('[data-action="clear-log"]'),
            advancedSettings: document.querySelector('.advanced-settings'),
            debugPanel: document.querySelector('.debug-panel'),
            particleContainer: document.getElementById('particleContainer'),
            // Cached NodeLists for bulk operations
            themeButtons: document.querySelectorAll('.theme-btn'),
            lazyComponents: document.querySelectorAll('[data-lazy-component]')
        };

        // Verify critical DOM elements exist
        this.verifyDOMElements();

        this.state = {
            isConnected: false,
            isRunning: false,
            isPaused: false,
            phase: 'SYSTEM_READY',
            progress: 0,
            file_name: '',
            file_size: 0,
            transferred: 0,
            speed: 0,
            eta: '--:--',
            clientId: null,
            log: { operation: 'System Initialized', success: true, details: '' },
            lastApiStatus: null,
            selectedFile: null
        };

        // Enhanced state management for preventing race conditions and optimizing performance
        this.stateManagement = {
            isPolling: false,
            isUpdatingUI: false,
            lastPollTime: 0,
            pollCooldown: 2000, // Minimum time between polls in ms (increased from 500ms to 2s)
            adaptivePollInterval: 3000, // Dynamic interval that adapts based on activity (increased from 1s to 3s)
            maxPollInterval: 10000, // Maximum interval when idle (increased from 5s to 10s)
            minPollInterval: 2000, // Minimum interval when active (increased from 500ms to 2s)
            consecutiveNoChangeCount: 0, // Track periods of no activity
            uiUpdateQueue: [],
            updateUIDebounced: null // Will be set after debounce method is defined
        };
        
        this.pendingConfirmAction = null;
        this.autoScrollLog = true;
        this.themeManager = new ThemeManager();

        // Modal managers are already initialized in SystemManager constructor
        
        // Set up debounced UI update after methods are defined
        this.stateManagement.updateUIDebounced = this.debounce(() => this._updateAllUI(), 150);

        // Verify critical DOM elements exist before initialization
        if (!this.verifyDOMElements()) {
            console.error('[DOM_VERIFICATION] CRITICAL: Missing DOM elements - buttons will not work');
            alert('Error: Critical UI elements are missing. Please refresh the page.');
            return;
        }
        
        this.initEventListeners();
        this.loadSavedConfig();
        this.themeManager.loadSavedTheme();
        this.system.setupKeyboardShortcuts(this); // Add keyboard shortcuts

        // Initialize lazy loading system for performance
        this.lazyComponents = new Map();
        this.initializeLazyLoading();

        // Setup cleanup handlers for memory leak prevention
        this.setupPageUnloadHandler();

        // Initialize real-time WebSocket communication (replaces polling)
        this.uiUpdateTimeout = null; // For debounced UI updates
        this.progressConfig = null; // Progress configuration for rich UX
        this.phaseStartTime = null; // For ETA calculations
        this.fileReceiptPollingInterval = null; // For file receipt polling fallback
        this.loadProgressConfiguration();
        
        // Initialize Data Stream Progress Ring system
        this.dataStreamProgressRing = new DataStreamProgressRing(this.elements);
        
        this.connectWebSocket();
        this.addLog('System Initialized', 'success', 'Real-time communication enabled.');
        this.system.notifications.show('CyberBackup Pro', 'Application ready', { type: 'info', silent: true });
        
        // Request notification permission on startup
        this.system.notifications.requestPermission();
        
        // Setup form validation
        this.setupFormValidation();
        
        // Initialize connection health monitoring
        this.setupConnectionHealthMonitoring();
    }

    /**
     * Initialize WebSocket connection for real-time progress updates
     */
    initializeWebSocket() {
        debugLog('Initializing WebSocket connection...', 'WEBSOCKET');
        this.socket = io();
        this.setupWebSocketEventHandlers();
    }

    /**
     * Setup WebSocket event handlers for real-time communication
     */
    setupWebSocketEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            this.socketConnected = true;
            debugLog('WebSocket connected successfully', 'WEBSOCKET');
            this.addLog('Real-time connection', 'success', 'WebSocket connected - live updates enabled');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            this.socketConnected = false;
            debugLog('WebSocket disconnected', 'WEBSOCKET');
            this.addLog('Connection lost', 'warning', 'WebSocket disconnected - falling back to polling');
            this.updateConnectionStatus(false);
            // Fallback to polling if WebSocket fails
            this.startPollingFallback();
        });

        // Real-time progress updates
        this.socket.on('progress_update', (data) => {
            debugLog('Received progress update via WebSocket:', data, 'WEBSOCKET');
            this.handleRealTimeProgressUpdate(data);
        });

        // Status updates
        this.socket.on('status', (data) => {
            debugLog('Received status update via WebSocket:', data, 'WEBSOCKET');
            this.state.isConnected = data.connected;
            this.updateAllUI();
        });

        // Pong response for connection testing
        this.socket.on('pong', (data) => {
            debugLog('WebSocket ping response received', 'WEBSOCKET');
        });

        // Error handling for backup failures
        this.socket.on('backup_error', (data) => {
            debugLog('Backup error received via WebSocket:', data, 'ERROR');
            this.handleBackupError(data);
        });

        // File receipt notifications (definitive completion detection)
        this.socket.on('file_receipt', (data) => {
            debugLog('File receipt notification received via WebSocket:', data, 'FILE_RECEIPT');
            this.handleFileReceiptNotification(data);
        });

        // Connection error handling
        this.socket.on('connect_error', (error) => {
            debugLog('WebSocket connection error:', error, 'ERROR');
            this.handleConnectionError(error);
        });
    }

    /**
     * Connect to WebSocket server
     */
    connectWebSocket() {
        if (this.socket && this.socketConnected) {
            debugLog('WebSocket already connected', 'WEBSOCKET');
            return;
        }

        try {
            debugLog('Attempting WebSocket connection...', 'WEBSOCKET');
            this.initializeWebSocket();
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.addLog('WebSocket error', 'error', 'Failed to connect - using polling fallback');
            this.startPollingFallback();
        }
    }

    /**
     * Handle real-time progress updates from WebSocket with rich context
     */
    handleRealTimeProgressUpdate(data) {
        const { job_id, phase, data: progressData, timestamp, progress } = data;
        
        // Only process updates for current job
        if (job_id && this.state.jobId && job_id !== this.state.jobId) {
            debugLog('Ignoring progress update for different job', 'WEBSOCKET');
            return;
        }

        // Track phase transitions for ETA calculations
        if (phase && phase !== this.state.phase) {
            this.phaseStartTime = Date.now();
            debugLog(`Phase transition: ${this.state.phase} → ${phase}`, 'PROGRESS');
        }

        // Update state with real-time data
        if (phase) {
            this.state.phase = phase;
            // Use rich phase description from configuration
            this.state.phaseDescription = this.getPhaseDescription(phase);
        }
        
        if (progress !== null && progress !== undefined) {
            this.state.progress = progress;
        }

        // Process the progress data with enhanced context
        if (progressData) {
            if (typeof progressData === 'object') {
                const message = progressData.message || this.state.phaseDescription;
                this.state.log = { operation: phase, success: true, details: message };
                
                if (progressData.progress !== undefined) {
                    this.state.progress = progressData.progress;
                }
            } else {
                const message = progressData || this.state.phaseDescription;
                this.state.log = { operation: phase, success: true, details: message };
            }
        }

        // Calculate and update ETA
        if (this.phaseStartTime && phase) {
            const elapsedMs = Date.now() - this.phaseStartTime;
            const etaSeconds = this.calculateETA(phase, elapsedMs);
            if (etaSeconds !== null) {
                this.state.eta = this.formatETA(etaSeconds);
                this.state.etaSeconds = etaSeconds;
            }
        }

        // Debounced UI update for smooth performance (50ms debounce)
        this.debouncedUIUpdate();
        
        // Add timestamped log entry with rich context
        const timestampStr = new Date(timestamp * 1000).toLocaleTimeString();
        const phaseDesc = this.state.phaseDescription || phase;
        const etaInfo = this.state.eta ? ` (ETA: ${this.state.eta})` : '';
        debugLog(`Real-time update [${timestampStr}]: ${phaseDesc} - ${progress}%${etaInfo}`, 'PROGRESS');
        
        // Show phase transition notifications for important phases
        if (phase && ['CONNECTING', 'AUTHENTICATING', 'ENCRYPTING', 'TRANSFERRING', 'VERIFYING', 'COMPLETED'].includes(phase)) {
            this.showPhaseTransitionNotification(phase, this.state.phaseDescription);
        }
        
        // Check for completion and schedule auto-reset
        this.checkForCompletionAndScheduleReset(phase, progress);
    }

    /**
     * Show subtle notification for phase transitions
     */
    showPhaseTransitionNotification(phase, description) {
        // Only show notifications for significant phase changes, not every progress update
        if (this.lastNotificationPhase === phase) {
            return;
        }
        
        this.lastNotificationPhase = phase;
        
        // Use the existing toast system for phase notifications
        if (phase === 'COMPLETED') {
            this.showToast(description, 'success', 3000);
        } else if (phase === 'TRANSFERRING') {
            this.showToast(description, 'info', 2000);
        } else {
            // Subtle notifications for other phases
            debugLog(`Phase: ${description}`, 'PHASE');
        }
    }

    /**
     * Handle backup errors with restart option
     */
    handleBackupError(errorData) {
        const { message, phase, job_id } = errorData;
        
        // Update state to reflect error
        this.state.phase = 'ERROR';
        this.state.isRunning = false;
        this.state.hasError = true;
        this.state.errorMessage = message || 'Backup failed unexpectedly';
        this.state.errorPhase = phase || 'UNKNOWN';
        
        // Clear progress and ETA
        this.state.progress = 0;
        this.state.eta = null;
        this.state.etaSeconds = 0;
        
        // Add error log entry
        this.addLog('Backup failed', 'error', this.state.errorMessage);
        
        // Show error toast with restart option
        this.showErrorWithRestart(this.state.errorMessage);
        
        // Update UI to show error state
        this.updateAllUI();
        
        debugLog(`Backup error in phase ${this.state.errorPhase}: ${this.state.errorMessage}`, 'ERROR');
    }

    /**
     * Handle WebSocket connection errors
     */
    handleConnectionError(error) {
        debugLog('WebSocket connection error, falling back to polling', 'ERROR');
        this.addLog('Connection error', 'warning', 'WebSocket failed, using polling fallback');
        this.startPollingFallback();
    }

    /**
     * Show error message with restart button
     */
    showErrorWithRestart(errorMessage) {
        // Create error notification with restart button
        const errorHtml = `
            <div class="error-restart-container">
                <div class="error-message">❌ ${errorMessage}</div>
                <button id="restartBackupBtn" class="restart-btn" 
                                onclick="window.app.restartBackup()" 
                                style="margin-top: 10px; padding: 8px 16px; background: var(--neon-blue); color: var(--bg-dark); border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">
                            🔄 Restart Backup
                        </button>
            </div>
        `;
        
        // Show persistent error toast
        this.showToast(errorHtml, 'error', 0); // 0 = persistent (won't auto-hide)
        
        // Also update any error display elements in the UI
        this.updateErrorDisplay();
    }

    /**
     * Update error display elements in the UI
     */
    updateErrorDisplay() {
        // Find error display elements and update them
        const errorElements = document.querySelectorAll('.error-display, .backup-error');
        errorElements.forEach(element => {
            if (this.state.hasError) {
                element.innerHTML = `
                    <div class="error-content">
                        <div class="error-text">❌ ${this.state.errorMessage}</div>
                        <button class="restart-btn" onclick="window.app.restartBackup()">
                            🔄 Restart Backup
                        </button>
                    </div>
                `;
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        });
    }

    /**
     * Restart backup operation (called by restart button)
     */
    restartBackup() {
        debugLog('Manual backup restart requested', 'RESTART');
        
        // Cancel any pending auto-reset when user manually restarts
        this.cancelAutoReset();
        
        // Clear error state
        this.clearErrorState();
        
        // Reset progress state
        this.resetProgressState();
        
        // Close any error toasts
        this.clearErrorToasts();
        
        // Start fresh backup with current settings
        this.startBackup();
        
        this.addLog('Backup restarted', 'info', 'Manual restart initiated');
        this.showToast('Backup restarted - attempting fresh upload', 'info', 3000);
    }

    /**
     * Clear error state
     */
    clearErrorState() {
        this.state.hasError = false;
        this.state.errorMessage = null;
        this.state.errorPhase = null;
        this.state.phase = 'READY';
        this.lastNotificationPhase = null;
        
        // Update error display elements
        this.updateErrorDisplay();
    }

    /**
     * Reset progress state for fresh start
     */
    resetProgressState() {
        this.state.progress = 0;
        this.state.eta = null;
        this.state.etaSeconds = 0;
        this.state.isRunning = false;
        this.state.phaseDescription = null;
        this.phaseStartTime = null;
        
        // Reset Data Stream Progress Ring
        if (this.dataStreamProgressRing) {
            this.dataStreamProgressRing.reset();
        }
    }

    /**
     * Clear error toast notifications
     */
    clearErrorToasts() {
        // Use the new ToastManager to dismiss error toasts
        this.toastManager.dismissByType('error');
    }
    /**
     * Complete application reset to initial state
     */
    resetToInitialState() {
        debugLog('Performing complete application reset', 'RESET');
        
        // Clear any pending timeouts/intervals
        if (this.intervals) {
            this.intervals.clear('autoReset');
            this.intervals.clear('resetCountdown');
        }
        
        // Reset all state to initial values
        this.state = {
            isConnected: false,
            isRunning: false,
            isPaused: false,
            phase: 'SYSTEM_READY',
            progress: 0,
            eta: null,
            etaSeconds: 0,
            message: null,
            phaseDescription: null,
            selectedFile: null,
            jobId: null,
            hasError: false,
            errorMessage: null,
            errorPhase: null,
            websocketConnected: false
        };
        
        // Reset phase timing
        this.phaseStartTime = null;
        this.backupStartTime = null;
        this.lastNotificationPhase = null;
        
        // Clear file input
        if (this.elements.fileInput) {
            this.elements.fileInput.value = '';
        }
        
        // Clear selected file display
        if (this.elements.selectedFileDisplay) {
            this.elements.selectedFileDisplay.textContent = 'No file selected';
            this.elements.selectedFileDisplay.classList.remove('file-info');
        }
        
        // Hide file copy button
        if (this.elements.copyFileInfoButton) {
            this.elements.copyFileInfoButton.classList.add('u-hidden');
            this.elements.copyFileInfoButton.classList.remove('u-inline-flex');
        }
        
        // Clear and hide file preview
        if (this.elements.filePreview) {
            this.elements.filePreview.textContent = '';
            this.elements.filePreview.innerHTML = '';
            this.elements.filePreview.style.display = 'none';
            this.elements.filePreview.classList.add('u-hidden');
        }
        
        // Clear progress display
        if (this.elements.progressPercentage) {
            this.elements.progressPercentage.textContent = '0%';
        }
        if (this.elements.progressStatus) {
            this.elements.progressStatus.textContent = 'READY';
        }
        if (this.elements.progressCircle) {
            this.elements.progressCircle.style.strokeDashoffset = '';
            this.elements.progressCircle.classList.remove('active');
        }
        
        // Reset Data Stream Progress Ring
        if (this.dataStreamProgressRing) {
            this.dataStreamProgressRing.reset();
        }
        
        // Clear any file preview blob URLs to prevent memory leaks
        document.querySelectorAll('img[src^="blob:"]').forEach(img => {
            URL.revokeObjectURL(img.src);
            img.remove();
        });
        
        // Clear any lingering file-related elements
        const filePreviewElements = document.querySelectorAll('.file-preview, .file-preview-container, .enhanced-file-preview');
        filePreviewElements.forEach(element => {
            element.style.display = 'none';
            element.innerHTML = '';
        });
        
        // Reset button states
        if (this.buttonStateManager) {
            this.buttonStateManager.resetAll();
        }
        
        // Explicitly reset primary action button to initial state
        if (this.elements.primaryActionButton) {
            this.updateButtonContent(this.elements.primaryActionButton, '🚀', 'CONNECT');
            this.elements.primaryActionButton.classList.remove('success', 'error', 'loading');
            this.elements.primaryActionButton.classList.add('primary');
            this.elements.primaryActionButton.disabled = false;
        }
        
        // Clear any success/error toasts
        this.clearErrorToasts();
        const successToasts = document.querySelectorAll('.toast.success, .toast.info');
        successToasts.forEach(toast => {
            toast.remove();
        });
        
        // Stop any active polling/monitoring
        this.stopFileReceiptPolling();
        if (this.stateManagement) {
            this.stateManagement.isProcessingQueue = false;
            this.stateManagement.eventQueue = [];
        }
        
        // Clear client ID display if present
        if (this.elements.clientIdDisplay) {
            this.elements.clientIdDisplay.textContent = 'Not connected';
        }
        
        // Reset connection status
        if (this.elements.connectionLed) {
            this.elements.connectionLed.classList.remove('connected', 'connecting');
        }
        if (this.elements.connectionText) {
            this.elements.connectionText.textContent = 'OFFLINE';
        }
        
        // Force UI update to reflect reset state
        this.updateAllUI();
        this.updateTabTitle();
        
        // Add log entry
        this.addLog('System reset', 'info', 'Application reset to initial state - ready for next backup');
        
        debugLog('Application reset completed successfully', 'RESET');
    }

    /**
     * Handle file receipt notifications (definitive completion detection)
     */
    handleFileReceiptNotification(data) {
        const { event_type, data: receiptData, timestamp } = data;
        
        debugLog(`File receipt event: ${event_type}`, receiptData, 'FILE_RECEIPT');
        
        switch (event_type) {
            case 'file_received':
                this.handleFileReceived(receiptData);
                break;
            case 'transfer_completed':
                this.handleTransferCompleted(receiptData);
                break;
            default:
                debugLog(`Unknown file receipt event: ${event_type}`, 'FILE_RECEIPT');
        }
    }

    /**
     * Handle file received notification
     */
    handleFileReceived(data) {
        const { filename, status, timestamp } = data;
        
        debugLog(`File received on server: ${filename}`, 'FILE_RECEIPT');
        this.addLog('File received', 'success', `Server detected file: ${filename}`);
        
        // Update progress to show file was received (but not yet verified)
        this.state.progress = Math.max(this.state.progress, 85);
        this.state.phase = 'FILE_RECEIVED';
        this.state.message = 'File received on server - verifying...';
        
        this.updateAllUI();
        
        // Show quick notification
        this.showToast(`📄 File received: ${filename}`, 'info', 2000);
    }

    /**
     * Handle transfer completed notification (definitive success)
     */
    handleTransferCompleted(data) {
        const { filename, status, size, hash, duration, timestamp } = data;
        
        debugLog(`Transfer completed: ${filename}`, data, 'FILE_RECEIPT');
        
        // OVERRIDE ANY PREVIOUS FAILURE STATUS - FILE RECEIPT IS DEFINITIVE
        this.state.phase = 'COMPLETED';
        this.state.progress = 100;
        this.state.isRunning = false;
        this.state.hasError = false; // Clear any error state
        this.state.errorMessage = null;
        
        // Update with success information
        const sizeFormatted = this.formatBytes(size || 0);
        const durationFormatted = duration ? `${duration.toFixed(1)}s` : 'unknown';
        
        this.state.message = `✅ Transfer completed successfully! (${sizeFormatted} in ${durationFormatted})`;
        this.addLog('Transfer completed', 'success', `File: ${filename}, Size: ${sizeFormatted}, Duration: ${durationFormatted}`);
        
        // Show celebration notification
        this.showToast(`🎉 Backup completed successfully!\n${filename} (${sizeFormatted})`, 'success', 5000);
        
        // Update title and UI
        this.updateAllUI();
        this.updateTabTitle();
        
        // Stop file receipt polling since we have definitive confirmation
        this.stopFileReceiptPolling();
        
        debugLog(`DEFINITIVE SUCCESS: ${filename} received and verified on server`, 'FILE_RECEIPT');
        
        // Schedule auto-reset after success (7 seconds delay)
        this.scheduleAutoReset(7000);
    }

    /**
     * Schedule automatic reset after successful completion
     */
    scheduleAutoReset(delayMs = 7000) {
        debugLog(`Scheduling auto-reset in ${delayMs}ms`, 'AUTO_RESET');
        
        // Clear any existing reset timers
        if (this.intervals) {
            this.intervals.clear('autoReset');
            this.intervals.clear('resetCountdown');
        }
        
        let remainingSeconds = Math.ceil(delayMs / 1000);
        
        // Show initial reset notification
        this.showToast(`🔄 Auto-reset in ${remainingSeconds} seconds...`, 'info', remainingSeconds * 1000 + 500);
        
        // Start countdown timer
        this.intervals.set('resetCountdown', () => {
            remainingSeconds--;
            
            if (remainingSeconds > 0) {
                // Update countdown message
                this.state.message = `✅ Transfer completed! Auto-reset in ${remainingSeconds}s...`;
                this.updateAllUI();
                
                // Show countdown toast for last 3 seconds
                if (remainingSeconds <= 3) {
                    this.showToast(`🔄 Resetting in ${remainingSeconds}...`, 'info', 1000);
                }
            } else {
                // Clear the countdown interval
                this.intervals.clear('resetCountdown');
                
                // Perform the reset
                this.performAutoReset();
            }
        }, 1000);
        
        // Set the main reset timer as backup
        this.intervals.setTimeout('autoReset', () => {
            this.performAutoReset();
        }, delayMs);
    }

    /**
     * Perform the actual auto-reset
     */
    performAutoReset() {
        debugLog('Performing scheduled auto-reset', 'AUTO_RESET');
        
        // Clear any remaining timers
        if (this.intervals) {
            this.intervals.clear('autoReset');
            this.intervals.clear('resetCountdown');
        }
        
        // Show reset notification
        this.showToast('🔄 Resetting for next backup...', 'info', 2000);
        
        // Small delay to show the reset message
        setTimeout(() => {
            this.resetToInitialState();
            this.showToast('✨ Ready for next backup!', 'success', 3000);
        }, 500);
    }

    /**
     * Check if backup is completed and schedule auto-reset if needed
     */
    checkForCompletionAndScheduleReset(phase, progress) {
        // Avoid scheduling multiple resets
        if (this.intervals && (this.intervals.has('autoReset') || this.intervals.has('resetCountdown'))) {
            return;
        }
        
        // Check for various completion scenarios
        const isCompleted = (
            // Phase-based completion
            (phase === 'COMPLETED') ||
            (phase === 'CLEANUP' && progress >= 100) ||
            // Progress-based completion (100% in certain phases)
            (progress >= 100 && ['VERIFYING', 'COMPLETED', 'CLEANUP', 'SUCCESS'].includes(phase)) ||
            // State-based completion
            (!this.state.isRunning && this.state.progress >= 100 && ['COMPLETED', 'SUCCESS'].includes(this.state.phase))
        );
        
        if (isCompleted) {
            debugLog(`Completion detected: phase=${phase}, progress=${progress}`, 'AUTO_RESET');
            
            // Add a small delay to let the UI show the completion state
            setTimeout(() => {
                // Double-check we're still in a completed state
                if (this.state.progress >= 100 && !this.state.hasError) {
                    this.scheduleAutoReset(7000);
                }
            }, 1000);
        }
    }

    /**
     * Cancel auto-reset (called when user interacts with interface)
     */
    cancelAutoReset() {
        if (this.intervals && (this.intervals.has('autoReset') || this.intervals.has('resetCountdown'))) {
            debugLog('Auto-reset cancelled due to user interaction', 'AUTO_RESET');
            this.intervals.clear('autoReset');
            this.intervals.clear('resetCountdown');
            
            // Update message to show reset was cancelled
            if (this.state.phase === 'COMPLETED' && this.state.message && this.state.message.includes('Auto-reset')) {
                this.state.message = this.state.message.replace(/Auto-reset in \d+s\.\.\./, 'Auto-reset cancelled');
                this.updateAllUI();
            }
            
            this.showToast('Auto-reset cancelled', 'info', 2000);
            return true;
        }
        return false;
    }

    /**
     * Multi-channel file receipt verification (HTTP fallback)
     */
    async checkFileReceiptHTTP(filename) {
        try {
            debugLog(`Checking file receipt via HTTP: ${filename}`, 'FILE_RECEIPT');
            
            const response = await fetch(`/api/check_receipt/${encodeURIComponent(filename)}`);
            const result = await response.json();
            
            if (result.success && result.received) {
                debugLog(`HTTP confirmed file receipt: ${filename}`, result, 'FILE_RECEIPT');
                
                // Simulate transfer completed event
                this.handleTransferCompleted({
                    filename: result.filename,
                    status: 'completed',
                    size: result.size,
                    hash: result.hash,
                    duration: 0,
                    timestamp: Date.now() / 1000
                });
                
                return true;
            } else {
                debugLog(`HTTP file receipt check failed: ${filename}`, result, 'FILE_RECEIPT');
                return false;
            }
        } catch (error) {
            debugLog(`HTTP file receipt check error: ${error.message}`, 'ERROR');
            return false;
        }
    }

    /**
     * Start periodic file receipt checking (fallback mechanism)
     */
    startFileReceiptPolling(filename) {
        // Only start if not already polling
        if (this.fileReceiptPollingInterval) {
            return;
        }
        
        debugLog(`Starting file receipt polling for: ${filename}`, 'FILE_RECEIPT');
        
        this.fileReceiptPollingInterval = setInterval(async () => {
            const received = await this.checkFileReceiptHTTP(filename);
            
            if (received) {
                // File found - stop polling
                this.stopFileReceiptPolling();
            }
        }, 2000); // Check every 2 seconds
        
        // Auto-stop polling after 60 seconds
        setTimeout(() => {
            if (this.fileReceiptPollingInterval) {
                debugLog('File receipt polling timeout - stopping', 'FILE_RECEIPT');
                this.stopFileReceiptPolling();
            }
        }, 60000);
    }

    /**
     * Stop file receipt polling
     */
    stopFileReceiptPolling() {
        if (this.fileReceiptPollingInterval) {
            clearInterval(this.fileReceiptPollingInterval);
            this.fileReceiptPollingInterval = null;
            debugLog('File receipt polling stopped', 'FILE_RECEIPT');
        }
    }

    /**
     * Format bytes in human readable format
     */
    formatBytes(bytes) {
        if (bytes === 0) {
            return '0 Bytes';
        }
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Enhanced error detection for backup failures
     */
    detectBackupFailure(statusData) {
        // Detect failure conditions from status data
        if (statusData.status === 'error' || statusData.phase === 'FAILED') {
            const errorMessage = statusData.message || 'Backup operation failed';
            this.handleBackupError({
                message: errorMessage,
                phase: statusData.phase || 'UNKNOWN',
                job_id: this.state.jobId
            });
            return true;
        }
        
        // Detect timeout conditions
        if (this.state.isRunning && this.state.progress === 0) {
            const elapsedTime = Date.now() - (this.backupStartTime || Date.now());
            if (elapsedTime > 60000) { // 60 seconds with no progress
                this.handleBackupError({
                    message: 'Backup appears to be stuck - no progress after 60 seconds',
                    phase: this.state.phase || 'TIMEOUT',
                    job_id: this.state.jobId
                });
                return true;
            }
        }
        
        return false;
    }

    /**
     * Debounced UI update for smooth real-time progress
     */
    debouncedUIUpdate() {
        if (this.uiUpdateTimeout) {
            clearTimeout(this.uiUpdateTimeout);
        }
        
        this.uiUpdateTimeout = setTimeout(() => {
            requestAnimationFrame(() => {
                this.updateAllUI();
            });
        }, 50); // 50ms debounce for smooth UI updates
    }

    /**
     * Start polling fallback when WebSocket fails
     */
    startPollingFallback() {
        if (this.socketConnected) {
            debugLog('WebSocket connected, skipping polling fallback', 'WEBSOCKET');
            return;
        }

        debugLog('Starting polling fallback...', 'POLL');
        this.startAdaptivePolling();
    }

    /**
     * Load progress configuration for rich UX
     */
    async loadProgressConfiguration() {
        try {
            const response = await fetch('/progress_config.json');
            if (response.ok) {
                this.progressConfig = await response.json();
                debugLog('Progress configuration loaded successfully', 'CONFIG');
                this.addLog('Progress system', 'success', 'Rich progress context enabled');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.warn('Could not load progress configuration:', error);
            this.addLog('Progress config', 'warning', 'Using default progress display');
            // Use fallback configuration
            this.progressConfig = this.getDefaultProgressConfig();
        }
    }

    /**
     * Get default progress configuration if file loading fails
     */
    getDefaultProgressConfig() {
        return {
            phases: {
                "CONNECTING": { weight: 0.10, description: "Connecting to server...", progress_range: [0, 10] },
                "AUTHENTICATING": { weight: 0.15, description: "Authenticating...", progress_range: [10, 25] },
                "ENCRYPTING": { weight: 0.30, description: "Encrypting file...", progress_range: [25, 55] },
                "TRANSFERRING": { weight: 0.35, description: "Transferring data...", progress_range: [55, 90] },
                "VERIFYING": { weight: 0.10, description: "Verifying integrity...", progress_range: [90, 100] },
                "COMPLETED": { weight: 0.00, description: "Backup completed!", progress_range: [100, 100] }
            },
            calibration_info: { total_avg_duration_ms: 4200 }
        };
    }

    /**
     * Calculate ETA based on current phase and elapsed time
     */
    calculateETA(currentPhase, elapsedMs) {
        if (!this.progressConfig || !currentPhase) {
            return null;
        }

        const phaseConfig = this.progressConfig.phases[currentPhase];
        if (!phaseConfig) {
            return null;
        }

        // Calculate total expected duration
        const totalExpectedMs = this.progressConfig.calibration_info.total_avg_duration_ms || 4200;
        
        // Calculate progress through current phase
        const phaseProgress = this.getPhaseProgress(currentPhase);
        
        // Estimate remaining time
        const completedWeight = this.getCompletedWeight(currentPhase, phaseProgress);
        const remainingWeight = 1.0 - completedWeight;
        const estimatedRemainingMs = remainingWeight * totalExpectedMs;

        return Math.max(0, Math.round(estimatedRemainingMs / 1000)); // Return seconds
    }

    /**
     * Get progress within current phase (0.0 to 1.0)
     */
    getPhaseProgress(currentPhase) {
        if (!this.progressConfig || !currentPhase) {
            return 0;
        }
        
        const phaseConfig = this.progressConfig.phases[currentPhase];
        if (!phaseConfig || !phaseConfig.progress_range) {
            return 0;
        }
        
        const [rangeStart, rangeEnd] = phaseConfig.progress_range;
        const rangeSize = rangeEnd - rangeStart;
        
        if (rangeSize <= 0) {
            return 1.0;
        }
        
        // Calculate progress within this phase based on current overall progress
        const currentProgress = this.state.progress || 0;
        const progressInRange = Math.max(0, Math.min(currentProgress - rangeStart, rangeSize));
        
        return progressInRange / rangeSize;
    }

    /**
     * Get total completed weight across all phases
     */
    getCompletedWeight(currentPhase, phaseProgress) {
        if (!this.progressConfig) {
            return 0;
        }
        
        let completedWeight = 0;
        const phases = Object.keys(this.progressConfig.phases);
        const currentPhaseIndex = phases.indexOf(currentPhase);
        
        // Add weight from completed phases
        for (let i = 0; i < currentPhaseIndex; i++) {
            const phase = phases[i];
            completedWeight += this.progressConfig.phases[phase].weight || 0;
        }
        
        // Add partial weight from current phase
        if (currentPhaseIndex >= 0) {
            const currentPhaseWeight = this.progressConfig.phases[currentPhase].weight || 0;
            completedWeight += currentPhaseWeight * phaseProgress;
        }
        
        return Math.min(1.0, completedWeight);
    }

    /**
     * Get rich phase description from configuration
     */
    getPhaseDescription(phase) {
        if (!this.progressConfig || !phase) {
            return phase;
        }
        
        const phaseConfig = this.progressConfig.phases[phase];
        return phaseConfig ? phaseConfig.description : phase;
    }

    /**
     * Format ETA for display
     */
    formatETA(seconds) {
        if (!seconds || seconds <= 0) {
            return 'Calculating...';
        }
        
        if (seconds < 60) {
            return `${seconds}s remaining`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${minutes}m ${secs}s remaining`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m remaining`;
        }
    }

    /**
     * Test WebSocket connection
     */
    testWebSocketConnection() {
        if (this.socketConnected) {
            this.socket.emit('ping');
            debugLog('WebSocket ping sent', 'WEBSOCKET');
            return true;
        }
        return false;
    }

    /**
     * Update connection status in UI
     */
    updateConnectionStatus(connected) {
        // This method can be enhanced to show WebSocket connection status
        // in addition to server connection status
        this.state.websocketConnected = connected;
        // The existing updateAllUI() will handle the visual updates
    }

    /**
     * Setup form validation rules and real-time validation
     */
    setupFormValidation() {
        // Add validation rules
        this.formValidator.addRule('serverInput', 'serverAddress', 'Please enter a valid server address (IP:PORT)');
        this.formValidator.addRule('usernameInput', 'username', 'Username must be 2-32 characters (letters, numbers, _ -)');

        // Setup real-time validation
        this.formValidator.setupRealTimeValidation(this.elements.serverInput, 'serverInput');
        this.formValidator.setupRealTimeValidation(this.elements.usernameInput, 'usernameInput');
    }

    /**
     * Setup connection health monitoring system
     */
    setupConnectionHealthMonitoring() {
        // Initialize the health monitor with the UI elements
        this.connectionHealthMonitor.initialize(
            this.elements.connectionHealth,
            this.elements.healthIndicator,
            this.elements.pingDisplay
        );
    }

    verifyDOMElements() {
        console.log('[DOM_VERIFICATION] Verifying critical DOM elements...');
        const criticalElements = [
            'primaryActionButton',
            'pauseButton', 
            'stopButton',
            'serverInput',
            'usernameInput',
            'fileDropZone',
            'saveConfigBtn',
            'confirmModal'
        ];
        
        const missingElements = [];
        
        for (const elementKey of criticalElements) {
            const element = this.elements[elementKey];
            if (!element) {
                missingElements.push(elementKey);
                console.error(`[DOM_VERIFICATION] Critical element missing: ${elementKey}`);
            } else {
                console.log(`[DOM_VERIFICATION] ✓ Found: ${elementKey}`);
            }
        }
        
        if (missingElements.length > 0) {
            console.error('[DOM_VERIFICATION] CRITICAL: Missing DOM elements:', missingElements);
            return false;
        }
        
        console.log('[DOM_VERIFICATION] All critical elements found successfully');
        return true;
    }

    initEventListeners() {
        console.log('[EVENT_DEBUG] Initializing event listeners...');
        console.log('[EVENT_DEBUG] Primary action button element:', this.elements.primaryActionButton);
        
        // Main action buttons - using managed event listeners for cleanup
        const primaryResult = this.eventListeners.add('primary-action', this.elements.primaryActionButton, 'click', () => this.handlePrimaryAction());
        console.log('[EVENT_DEBUG] Primary action listener result:', primaryResult);
        this.eventListeners.add('pause-action', this.elements.pauseButton, 'click', () => this.togglePause());
        this.eventListeners.add('stop-action', this.elements.stopButton, 'click', () => this.stopBackup());
        
        // Copy buttons - using managed event listeners
        this.eventListeners.add('copy-client-id', this.elements.copyClientIdButton, 'click', () => this.copyClientId());
        this.eventListeners.add('copy-server-addr', this.elements.copyServerAddressButton, 'click', () => this.copyServerAddress());
        this.eventListeners.add('copy-file-info', this.elements.copyFileInfoButton, 'click', () => this.copyFileInfo());
        
        // Recent files button
        this.elements.recentFilesBtn.addEventListener('click', () => this.showRecentFiles());
        
        // Config save button
        this.elements.saveConfigBtn.addEventListener('click', () => this.saveConfig());

        // File drop zone
        this.system.fileManager.setupDragAndDrop(
            this.elements.fileDropZone,
            (file) => this.handleFileSelection(file)
        );

        // Log controls
        this.elements.exportLogBtn.addEventListener('click', () => this.exportLog());
        this.elements.clearLogBtn.addEventListener('click', () => this.clearLog());
        this.elements.autoScrollBtn.addEventListener('click', () => this.toggleAutoScroll());

        // Debug toggle
        this.elements.debugToggle.addEventListener('click', () => this.toggleDebugConsole());

        // Theme buttons - using managed event listeners to prevent memory leaks
        this.elements.themeButtons.forEach((btn, index) => {
            this.eventListeners.add(`theme-btn-${index}`, btn, 'click', (e) => {
                const theme = e.target.classList[1]; // e.g., 'cyberpunk', 'dark', 'matrix'
                this.themeManager.setTheme(theme);
            });
        });

        // Modals
        this.elements.confirmOkBtn.addEventListener('click', () => {
            if (this.pendingConfirmAction) {
                this.pendingConfirmAction.resolve(true);
                this.pendingConfirmAction = null;
            }
            this.system.confirmModal.hide();
        });
        this.elements.cancelModalBtn.addEventListener('click', () => {
            if (this.pendingConfirmAction) {
                this.pendingConfirmAction.resolve(false);
                this.pendingConfirmAction = null;
            }
            this.system.confirmModal.hide();
        });
    }

    async pollStatus() {
        if (this.stateManagement.isPolling) {
            debugLog('Skipping poll: already polling', 'POLL');
            return;
        }

        const now = Date.now();
        if (now - this.stateManagement.lastPollTime < this.stateManagement.pollCooldown) {
            debugLog('Skipping poll: cooldown active', 'POLL');
            return;
        }

        this.stateManagement.isPolling = true;
        this.stateManagement.lastPollTime = now;

        try {
            const status = await this.apiClient.getStatus(this.state.jobId);

            if (status.events && status.events.length > 0) {
                this.processStatusQueue(status.events);
            }

            // Update general status from the latest snapshot
            this.state.isConnected = status.isConnected;
            this.state.isRunning = status.backing_up;
            this.updateAllUI();

        } catch (error) {
            console.error('Error polling status:', error);
            this.state.isConnected = false;
            this.updateAllUI();
        } finally {
            this.stateManagement.isPolling = false;
        }
    }

    processStatusQueue(events) {
        if (this.stateManagement.isProcessingQueue) {
            this.stateManagement.eventQueue.push(...events);
            return;
        }

        this.stateManagement.isProcessingQueue = true;
        this.stateManagement.eventQueue.push(...events);

        const processNextEvent = () => {
            if (this.stateManagement.eventQueue.length === 0) {
                this.stateManagement.isProcessingQueue = false;
                return;
            }

            const event = this.stateManagement.eventQueue.shift();

            this.state.phase = event.phase;
            if (event.data && typeof event.data === 'object') {
                if (event.data.progress >= 0) {
                    this.state.progress = event.data.progress;
                }
                this.state.log = { operation: event.phase, success: true, details: event.data.message };
            } else {
                this.state.log = { operation: event.phase, success: true, details: event.data };
            }

            this.updateAllUI();

            setTimeout(processNextEvent, 400); // Slower timeout for better visual effect
        };

        processNextEvent();
    }

    processStatusQueue(events) {
        if (this.stateManagement.isProcessingQueue) {
            this.stateManagement.eventQueue.push(...events);
            return;
        }

        this.stateManagement.isProcessingQueue = true;
        this.stateManagement.eventQueue.push(...events);

        const processNextEvent = () => {
            if (this.stateManagement.eventQueue.length === 0) {
                this.stateManagement.isProcessingQueue = false;
                return;
            }

            const event = this.stateManagement.eventQueue.shift();

            this.state.phase = event.phase;
            if (event.progress >= 0) {
                this.state.progress = event.progress;
            }
            this.state.log = { operation: event.phase, success: true, details: event.details };

            this.updateAllUI();

            setTimeout(processNextEvent, 300);
        };

        processNextEvent();
    }

    // Lazy loading system for performance optimization
    initializeLazyLoading() {
        // Mark components for lazy initialization
        this.lazyComponents.set('debugConsole', {
            initialized: false,
            element: '#debugContent',
            initFunction: () => this.initializeDebugConsole()
        });
        
        this.lazyComponents.set('advancedSettings', {
            initialized: false,
            element: '.advanced-settings',
            initFunction: () => this.initializeAdvancedSettings()
        });

        // Set up intersection observer for components that become visible
        if ('IntersectionObserver' in window) {
            this.setupLazyLoadObserver();
        }
        
        console.log('[LazyLoad] Lazy loading system initialized for', this.lazyComponents.size, 'components');
    }

    setupLazyLoadObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const componentId = entry.target.getAttribute('data-lazy-component');
                    if (componentId && this.lazyComponents.has(componentId)) {
                        this.loadLazyComponent(componentId);
                    }
                }
            });
        }, { threshold: 0.1 });

        // Observe elements marked for lazy loading
        this.elements.lazyComponents.forEach(el => {
            observer.observe(el);
        });
    }

    loadLazyComponent(componentId) {
        const component = this.lazyComponents.get(componentId);
        if (component && !component.initialized) {
            console.log('[LazyLoad] Loading component:', componentId);
            try {
                component.initFunction();
                component.initialized = true;
                console.log('[LazyLoad] Component loaded successfully:', componentId);
            } catch (error) {
                console.error('[LazyLoad] Failed to load component:', componentId, error);
            }
        }
    }

    initializeDebugConsole() {
        // Initialize debug console only when needed
        const { debugContent } = this.elements;
        if (debugContent && !debugContent.getAttribute('data-initialized')) {
            debugContent.setAttribute('data-initialized', 'true');
            // Additional heavy debug console initialization can go here
            console.log('[LazyLoad] Debug console initialized');
        }
    }

    initializeAdvancedSettings() {
        // Initialize advanced settings panel only when accessed
        const { advancedSettings } = this.elements;
        if (advancedSettings && !advancedSettings.getAttribute('data-initialized')) {
            advancedSettings.setAttribute('data-initialized', 'true');
            // Additional heavy settings initialization can go here  
            console.log('[LazyLoad] Advanced settings initialized');
        }
    }

    // Adaptive polling system - adjusts frequency based on activity
    startAdaptivePolling() {
        const scheduleNextPoll = () => {
            if (this.intervals && this.intervals.has) {
                this.intervals.clear('statusPoll');
                this.intervals.set('statusPoll', () => {
                    this.pollStatus().then(() => {
                        scheduleNextPoll(); // Schedule next poll with updated interval
                    }).catch(() => {
                        scheduleNextPoll(); // Continue even on error
                    });
                }, this.stateManagement.adaptivePollInterval);
            } else {
                // Fallback using managed timeout to prevent leaks
                this.intervals.setTimeout('statusPollFallback', () => {
                    this.pollStatus().then(() => {
                        scheduleNextPoll();
                    }).catch(() => {
                        scheduleNextPoll();
                    });
                }, this.stateManagement.adaptivePollInterval);
            }
        };
        
        // Start the adaptive polling
        scheduleNextPoll();
        // console.log('[Polling] Adaptive polling started with initial interval:', this.stateManagement.adaptivePollInterval + 'ms');
    }

    // Public UI Update Function (uses debouncing)
    updateAllUI() {
        this.stateManagement.updateUIDebounced();
    }

    _updateAllUI() {
        debugLog('Updating all UI elements...', 'UI');
        if (this.stateManagement.isUpdatingUI) {
            debugLog('Skipping UI update: already updating', 'UI');
            return;
        }
        this.stateManagement.isUpdatingUI = true;

        try {
            // Update connection status
            this.elements.connectionLed.classList.toggle('connected', this.state.isConnected);
            this.elements.connectionLed.classList.toggle('connecting', this.state.phase === 'CONNECT');
            this.elements.connectionText.textContent = this.state.isConnected ? 'ONLINE' : 'OFFLINE';

            // Update primary action button
            if (this.state.isConnected && !this.state.isRunning) {
                this.updateButtonContent(this.elements.primaryActionButton, '🚀', 'START BACKUP');
                this.elements.primaryActionButton.classList.remove('primary');
                this.elements.primaryActionButton.classList.add('success');
                this.elements.primaryActionButton.disabled = false;
            } else if (this.state.isRunning) {
                this.updateButtonContent(this.elements.primaryActionButton, '🔄', 'BACKING UP...');
                this.elements.primaryActionButton.classList.remove('success');
                this.elements.primaryActionButton.classList.add('primary');
                this.elements.primaryActionButton.disabled = true;
            } else {
                this.updateButtonContent(this.elements.primaryActionButton, '🚀', 'CONNECT');
                this.elements.primaryActionButton.classList.remove('success');
                this.elements.primaryActionButton.classList.add('primary');
                this.elements.primaryActionButton.disabled = false;
            }

            // Update pause/stop buttons
            this.elements.pauseButton.disabled = !this.state.isRunning;
            this.elements.stopButton.disabled = !this.state.isRunning;
            this.elements.pauseButton.textContent = this.state.isPaused ? '▶️ RESUME' : '⏸️ PAUSE';
            this.elements.pauseButton.classList.toggle('primary', this.state.isPaused);
            this.elements.pauseButton.classList.toggle('secondary', !this.state.isPaused);

            // Update phase display
            this.elements.currentPhaseDisplay.querySelector('span').textContent = this.state.phase.replace(/_/g, ' ');
            this.elements.currentPhaseDisplay.querySelector('span').className = `neon-text ${this.getPhaseColor(this.state.phase)}`;

            // Update progress ring
            const radius = this.elements.progressCircle.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            const offset = circumference - (this.state.progress / 100) * circumference;
            this.elements.progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
            this.elements.progressCircle.style.strokeDashoffset = offset;
            this.elements.progressCircle.classList.toggle('active', this.state.isRunning);

            // Update Data Stream Progress Ring system
            if (this.dataStreamProgressRing) {
                this.dataStreamProgressRing.updatePhase(this.state.phase, this.state.speed);
                this.dataStreamProgressRing.setActive(this.state.isRunning);
            }

            this.elements.progressPercentage.textContent = `${Math.round(this.state.progress)}%`;
            this.elements.progressStatus.textContent = this.state.log.operation || this.state.message;

            // Update stats grid
            this.elements.speedStat.textContent = this.formatBytesPerSecond(this.state.speed);
            this.elements.etaStat.textContent = this.formatTime(this.state.eta);
            this.elements.transferredStat.textContent = this.formatBytes(this.state.transferred);
            this.elements.sizeStat.textContent = this.formatBytes(this.state.file_size);

            // Update selected file display
            if (this.state.selectedFile) {
                // Create safe DOM elements instead of innerHTML to prevent XSS
                const fileIcon = document.createElement('span');
                fileIcon.className = 'file-icon neon-text blue';
                fileIcon.textContent = '📄';
                
                const fileDetails = document.createElement('div');
                fileDetails.className = 'file-details';
                
                const fileName = document.createElement('div');
                fileName.className = 'file-name';
                fileName.textContent = this.state.selectedFile.name;
                
                const fileSize = document.createElement('div');
                fileSize.className = 'file-size';
                fileSize.textContent = this.formatBytes(this.state.selectedFile.size);
                
                fileDetails.appendChild(fileName);
                fileDetails.appendChild(fileSize);
                
                this.elements.selectedFileDisplay.textContent = '';
                this.elements.selectedFileDisplay.appendChild(fileIcon);
                this.elements.selectedFileDisplay.appendChild(fileDetails);
                this.elements.selectedFileDisplay.classList.add('file-info');
                this.elements.copyFileInfoButton.classList.remove('u-hidden');
                this.elements.copyFileInfoButton.classList.add('u-inline-flex'); // Show copy button
                this.elements.filePreview.textContent = ''; // Clear previous preview safely
                this.elements.filePreview.style.display = 'flex';
                this.renderFilePreview(this.state.selectedFile);
            } else {
                this.elements.selectedFileDisplay.textContent = 'No file selected';
                this.elements.selectedFileDisplay.classList.remove('file-info');
                this.elements.copyFileInfoButton.classList.add('u-hidden'); // Hide copy button
                this.elements.filePreview.classList.add('u-hidden');
            }

            // Update client ID
            this.elements.clientIdDisplay.textContent = this.state.clientId ? this.state.clientId.substring(0, 8) + '...' : 'Not connected';

            // Update debug JSON viewers
            if (this.elements.statusJsonViewer) {
                this.elements.statusJsonViewer.textContent = JSON.stringify(this.state.lastApiStatus, null, 2);
            }
            if (this.elements.progressJsonViewer) {
                this.elements.progressJsonViewer.textContent = JSON.stringify(this.state, null, 2);
            }

            // Update browser tab title with progress
            this.updateTabTitle();

        } catch (error) {
            console.error('Error updating UI:', error);
            debugLog('Error updating UI: ' + error.message, 'ERROR');
        } finally {
            this.stateManagement.isUpdatingUI = false;
        }
    }

    /**
     * Update browser tab title with progress information
     */
    updateTabTitle() {
        try {
            const baseTitle = 'CyberBackup';
            let titleParts = [baseTitle];

            if (this.state.isRunning && this.state.progress !== undefined) {
                // Show progress percentage when backup is running
                const progressPercent = Math.round(this.state.progress);
                titleParts.unshift(`${progressPercent}%`);
                
                // Add operation status
                if (this.state.isPaused) {
                    titleParts.push('(Paused)');
                } else if (this.state.phase === 'BACKING_UP') {
                    titleParts.push('(Backing up)');
                } else if (this.state.phase === 'VERIFY') {
                    titleParts.push('(Verifying)');
                }
            } else if (this.state.isConnected) {
                // Show connection status when connected but not running
                titleParts.push('(Connected)');
            } else if (this.state.phase === 'COMPLETED') {
                // Show completion status
                titleParts.unshift('✅ Complete');
            } else if (this.state.phase === 'FAILED' || this.state.phase === 'ERROR') {
                // Show error status
                titleParts.unshift('❌ Failed');
            }

            // Set the title
            document.title = titleParts.join(' ');
            
        } catch (error) {
            console.error('Error updating tab title:', error);
            debugLog('Error updating tab title: ' + error.message, 'ERROR');
        }
    }

    getPhaseColor(phase) {
        switch (phase) {
            case 'SYSTEM_READY': return 'purple';
            case 'CONNECT': return 'blue';
            case 'CONNECTED': return 'green';
            case 'START': return 'blue';
            case 'BACKING_UP': return 'blue';
            case 'VERIFY': return 'yellow';
            case 'COMPLETED': return 'green';
            case 'SUCCESS': return 'green';
            case 'PAUSED': return 'yellow';
            case 'STOPPED': return 'pink';
            case 'FAILED': return 'red';
            case 'ERROR': return 'red';
            case 'CONNECTION_FAILED': return 'red';
            case 'SERVER_OFFLINE': return 'red';
            default: return 'purple';
        }
    }

    updateProgressData(progressData) {
        // Update progress information from API status
        if (progressData) {
            if (progressData.progress !== undefined) {
                this.state.progress = progressData.progress;
            }
            if (progressData.transferred !== undefined) {
                this.state.transferred = progressData.transferred;
            }
            if (progressData.speed !== undefined) {
                this.state.speed = progressData.speed;
            }
            if (progressData.eta !== undefined) {
                this.state.eta = progressData.eta;
            }
        }
    }

    updateButtonContent(button, icon, text) {
        // Safely update button content while preserving span structure
        if (!button) {
            return;
        }

        const iconSpan = button.querySelector('.btn-icon');
        const textSpan = button.querySelector('.btn-text');

        if (iconSpan && textSpan) {
            iconSpan.textContent = icon;
            textSpan.textContent = text;
        } else {
            // Fallback: recreate the structure if spans are missing
            button.innerHTML = `<span class="btn-icon">${icon}</span><span class="btn-text">${text}</span>`;
        }
    }

    async handlePrimaryAction() {
        console.log('[BUTTON_DEBUG] handlePrimaryAction called!');
        
        // Cancel any pending auto-reset when user interacts
        this.cancelAutoReset();
        
        // Prevent multiple simultaneous actions
        if (this.buttonStateManager.isLoading(this.elements.primaryActionButton)) {
            console.log('[BUTTON_DEBUG] Button is loading, skipping action');
            return;
        }

        if (!this.state.isConnected) {
            // Connect to server
            const serverAddress = this.elements.serverInput.value;
            const username = this.elements.usernameInput.value;
            const [serverIP, serverPortStr] = serverAddress.split(':');
            const serverPort = parseInt(serverPortStr);

            if (!serverIP || isNaN(serverPort) || !username) {
                this.buttonStateManager.setError(this.elements.primaryActionButton, '❌ Invalid Input');
                this.showToast('Please enter valid server address and username.', 'error');
                this.addLog('Connection failed', 'error', 'Invalid server address or username.');
                return;
            }

            // Set loading state
            this.buttonStateManager.setLoading(this.elements.primaryActionButton, '🔄 Connecting...');
            
            this.addLog(`Attempting to connect to ${serverIP}:${serverPort} as ${username}...`, 'info');
            this.state.phase = 'CONNECT';
            this.state.log = { operation: 'Connecting...', success: true, details: '' };
            this.updateAllUI();

            try {
                // Include filepath in connect call if file is selected
                const connectConfig = { host: serverIP, port: serverPort, username: username };
                if (this.state.selectedFile) {
                    connectConfig.filepath = this.state.selectedFile.name;
                }

                const result = await this.apiClient.connect(connectConfig);
                if (result.success) {
                    this.buttonStateManager.setSuccess(this.elements.primaryActionButton, '✅ Connected!');
                    this.showToast('Connected to server successfully!', 'success');
                    this.addLog('Connected to server', 'success', `Server: ${serverIP}:${serverPort}`);
                    this.state.isConnected = true;
                    this.state.phase = 'CONNECTED';
                    this.state.log = { operation: 'Ready for backup', success: true, details: '' };
                    this.updateAllUI();
                } else {
                    const errorInfo = this.errorMessageFormatter.formatError('connection', result.message);
                    this.buttonStateManager.setError(this.elements.primaryActionButton, '❌ Failed');
                    this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                    this.addLog('Connection failed', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                    this.state.isConnected = false;
                    this.state.phase = 'CONNECTION_FAILED';
                    this.state.log = { operation: 'Connection Failed', success: false, details: result.message };
                    this.updateAllUI();
                }
            } catch (error) {
                const errorInfo = this.errorMessageFormatter.formatError('connection', error.message);
                this.buttonStateManager.setError(this.elements.primaryActionButton, '❌ Error');
                this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                this.addLog('Connection Error', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                this.state.isConnected = false;
                this.state.phase = 'ERROR';
                this.state.log = { operation: 'API Error', success: false, details: error.message };
                this.updateAllUI();
            }
        } else if (this.state.isConnected && !this.state.isRunning) {
            // Start backup
            if (!this.state.selectedFile) {
                this.buttonStateManager.setError(this.elements.primaryActionButton, '❌ No File');
                this.showToast('Please select a file to backup first.', 'warning');
                this.addLog('Backup failed', 'warning', 'No file selected.');
                return;
            }

            const confirm = await this.system.confirmModal.confirm(
                'Confirm Backup',
                `Are you sure you want to backup "${this.state.selectedFile.name}" to ${this.elements.serverInput.value}?`
            );

            if (confirm) {
                // Set loading state
                this.buttonStateManager.setLoading(this.elements.primaryActionButton, '🚀 Starting...');
                
                this.addLog(`Starting backup of ${this.state.selectedFile.name}...`, 'info');
                this.state.isRunning = true;
                this.state.phase = 'START';
                this.state.log = { operation: 'Initiating backup', success: true, details: '' };
                this.updateAllUI();

                try {
                    const result = await this.apiClient.startBackup(
                        this.state.selectedFile,
                        { 
                            username: this.elements.usernameInput.value,
                            serverIP: this.elements.serverInput.value.split(':')[0],
                            serverPort: parseInt(this.elements.serverInput.value.split(':')[1])
                        }
                    );
                    if (result.success) {
                        this.buttonStateManager.setSuccess(this.elements.primaryActionButton, '✅ Started!');
                        this.showToast('Backup process started!', 'success');
                        this.addLog('Backup initiated', 'success', `File: ${result.filename}`);
                        
                        // Start file receipt polling as fallback mechanism
                        const filename = result.filename || this.state.selectedFile.name;
                        this.startFileReceiptPolling(filename);
                        
                        // Status polling will update the rest
                    } else {
                        const errorInfo = this.errorMessageFormatter.formatError('backup', result.message);
                        this.buttonStateManager.setError(this.elements.primaryActionButton, '❌ Failed');
                        this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                        this.addLog('Backup failed', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                        this.state.isRunning = false;
                        this.state.phase = 'FAILED';
                        this.state.log = { operation: 'Backup Failed', success: false, details: result.message };
                        this.updateAllUI();
                    }
                } catch (error) {
                    const errorInfo = this.errorMessageFormatter.formatError('backup', error.message);
                    this.buttonStateManager.setError(this.elements.primaryActionButton, '❌ Error');
                    this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                    this.addLog('Backup Error', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                    this.state.isRunning = false;
                    this.state.phase = 'ERROR';
                    this.state.log = { operation: 'API Error', success: false, details: error.message };
                    this.updateAllUI();
                }
            } else {
                this.addLog('Backup cancelled by user', 'info');
                this.showToast('Backup cancelled.', 'info');
            }
        }
    }

    async togglePause() {
        // Cancel any pending auto-reset when user interacts
        this.cancelAutoReset();
        
        // Prevent multiple simultaneous actions
        if (this.buttonStateManager.isLoading(this.elements.pauseButton)) {
            return;
        }

        if (this.state.isRunning) {
            if (this.state.isPaused) {
                // Resume
                this.buttonStateManager.setLoading(this.elements.pauseButton, '▶️ Resuming...');
                this.addLog('Resuming backup...', 'info');
                this.state.phase = 'RESUME';
                this.state.log = { operation: 'Resuming backup', success: true, details: '' };
                this.updateAllUI();
                try {
                    const result = await this.apiClient.resumeBackup();
                    if (result.success) {
                        this.buttonStateManager.setSuccess(this.elements.pauseButton, '✅ Resumed!');
                        this.showToast('Backup resumed!', 'info');
                        this.addLog('Backup resumed', 'success');
                        this.state.isPaused = false;
                        this.state.phase = 'BACKING_UP';
                        this.state.log = { operation: 'Backing up...', success: true, details: '' };
                        this.updateAllUI();
                    } else {
                        const errorInfo = this.errorMessageFormatter.formatError('resume', result.message);
                        this.buttonStateManager.setError(this.elements.pauseButton, '❌ Failed');
                        this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                        this.addLog('Resume failed', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                    }
                } catch (error) {
                    const errorInfo = this.errorMessageFormatter.formatError('resume', error.message);
                    this.buttonStateManager.setError(this.elements.pauseButton, '❌ Error');
                    this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                    this.addLog('Resume Error', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                }
            } else {
                // Pause
                this.buttonStateManager.setLoading(this.elements.pauseButton, '⏸️ Pausing...');
                this.addLog('Pausing backup...', 'info');
                this.state.phase = 'PAUSE';
                this.state.log = { operation: 'Pausing backup', success: true, details: '' };
                this.updateAllUI();
                try {
                    const result = await this.apiClient.pauseBackup();
                    if (result.success) {
                        this.buttonStateManager.setSuccess(this.elements.pauseButton, '⏸️ Paused!');
                        this.showToast('Backup paused!', 'warning');
                        this.addLog('Backup paused', 'warning');
                        this.state.isPaused = true;
                        this.state.phase = 'PAUSED';
                        this.state.log = { operation: 'Backup paused', success: true, details: '' };
                        this.updateAllUI();
                    } else {
                        const errorInfo = this.errorMessageFormatter.formatError('pause', result.message);
                        this.buttonStateManager.setError(this.elements.pauseButton, '❌ Failed');
                        this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                        this.addLog('Pause failed', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                    }
                } catch (error) {
                    const errorInfo = this.errorMessageFormatter.formatError('pause', error.message);
                    this.buttonStateManager.setError(this.elements.pauseButton, '❌ Error');
                    this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                    this.addLog('Pause Error', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                }
            }
        }
    }

    async stopBackup() {
        // Cancel any pending auto-reset when user interacts
        this.cancelAutoReset();
        
        // Prevent multiple simultaneous actions
        if (this.buttonStateManager.isLoading(this.elements.stopButton)) {
            return;
        }

        if (this.state.isRunning) {
            const confirm = await this.system.confirmModal.confirm(
                'Confirm Stop',
                'Are you sure you want to stop the current backup operation?'
            );

            if (confirm) {
                this.buttonStateManager.setLoading(this.elements.stopButton, '🛑 Stopping...');
                this.addLog('Stopping backup...', 'info');
                this.state.phase = 'STOP';
                this.state.log = { operation: 'Stopping backup', success: true, details: '' };
                this.updateAllUI();
                try {
                    const result = await this.apiClient.stopBackup();
                    if (result.success) {
                        this.buttonStateManager.setSuccess(this.elements.stopButton, '✅ Stopped!');
                        this.showToast('Backup stopped!', 'info');
                        this.addLog('Backup stopped', 'info');
                        this.state.isRunning = false;
                        this.state.isPaused = false;
                        this.state.progress = 0;
                        this.state.phase = 'STOPPED';
                        this.state.log = { operation: 'Backup stopped', success: true, details: '' };
                        this.updateAllUI();
                    } else {
                        const errorInfo = this.errorMessageFormatter.formatError('stop', result.message);
                        this.buttonStateManager.setError(this.elements.stopButton, '❌ Failed');
                        this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                        this.addLog('Stop failed', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                    }
                } catch (error) {
                    const errorInfo = this.errorMessageFormatter.formatError('stop', error.message);
                    this.buttonStateManager.setError(this.elements.stopButton, '❌ Error');
                    this.showToast(`${errorInfo.userMessage}. ${errorInfo.suggestion}`, 'error');
                    this.addLog('Stop Error', 'error', `${errorInfo.userMessage} - ${errorInfo.technical}`);
                }
            } else {
                this.addLog('Stop cancelled by user', 'info');
                this.showToast('Stop cancelled.', 'info');
            }
        } else {
            this.buttonStateManager.setError(this.elements.stopButton, '❌ Not Running');
            this.showToast('No backup is currently running.', 'info');
        }
    }

    handleFileSelection(file) {
        debugLog('File selected:' + file.name, 'FILE_MANAGER');
        
        // Cancel any pending auto-reset when user selects a new file
        this.cancelAutoReset();
        
        // Validate the file before accepting it
        const validation = this.system.fileManager.validateFile(file);
        
        if (!validation.isValid) {
            // File has errors - reject it
            const errorInfo = this.errorMessageFormatter.formatFileValidationError(validation.errors);
            this.addLog(`File rejected: ${file.name}`, 'error', `${errorInfo.message} - ${validation.errors.join('; ')}`);
            this.showToast(`${errorInfo.message}. ${errorInfo.suggestion}`, 'error', 5000);
            
            // Show detailed error in a modal
            this.system.modal.show(
                'File Validation Failed',
                `The selected file cannot be used for backup:\n\n${validation.errors.join('\n\n')}`,
                () => {}
            );
            return;
        }
        
        // File is valid - show warnings if any
        if (validation.warnings.length > 0) {
            validation.warnings.forEach(warning => {
                this.addLog(`File warning: ${file.name}`, 'warning', warning);
                this.showToast(warning, 'warning', 4000);
            });
        }
        
        // Accept the file
        this.state.selectedFile = file;
        
        // Save file to memory for future quick access
        this.fileMemoryManager.saveFileSelection(file);
        
        this.updateAllUI();
        this.addLog(`File selected: ${file.name}`, 'success', 
            `Size: ${this.formatBytes(file.size)}, Type: ${file.type || 'unknown'}`);
        
        // Show success with file details
        this.showToast(
            `File selected: ${file.name} (${this.system.fileManager.formatFileSize(file.size)})`, 
            'success', 
            3000
        );
    }

    renderFilePreview(file) {
        const previewContainer = this.elements.filePreview;
        previewContainer.textContent = ''; // Clear safely

        // Create enhanced preview with metadata
        const previewWrapper = document.createElement('div');
        previewWrapper.className = 'enhanced-file-preview';
        previewWrapper.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: var(--space-sm);
            padding: var(--space-md);
            background: rgba(0, 0, 0, 0.2);
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
        `;

        const fileInfo = this.getFileTypeInfo(file);
        
        // File icon and type
        const iconElement = document.createElement('div');
        iconElement.className = 'file-preview-icon';
        iconElement.style.cssText = `
            font-size: 2.5rem;
            color: ${fileInfo.color};
            text-shadow: 0 0 10px ${fileInfo.color}40;
            margin-bottom: var(--space-xs);
        `;
        iconElement.textContent = fileInfo.icon;
        previewWrapper.appendChild(iconElement);

        // File type label
        const typeLabel = document.createElement('div');
        typeLabel.className = 'file-type-label';
        typeLabel.style.cssText = `
            font-size: var(--font-size-sm);
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        `;
        typeLabel.textContent = fileInfo.typeLabel;
        previewWrapper.appendChild(typeLabel);

        // File metadata
        const metadata = document.createElement('div');
        metadata.className = 'file-metadata';
        metadata.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 2px;
            font-size: var(--font-size-xs);
            color: var(--text-muted);
            text-align: center;
        `;
        
        // Batch metadata elements using DocumentFragment to reduce reflows
        const metadataFragment = document.createDocumentFragment();
        
        const sizeInfo = document.createElement('div');
        sizeInfo.textContent = `Size: ${this.formatBytes(file.size)}`;
        metadataFragment.appendChild(sizeInfo);
        
        const lastModified = document.createElement('div');
        lastModified.textContent = `Modified: ${new Date(file.lastModified).toLocaleDateString()}`;
        metadataFragment.appendChild(lastModified);
        
        metadata.appendChild(metadataFragment);
        
        previewWrapper.appendChild(metadata);

        // Content preview for specific file types
        if (file.type.startsWith('image/')) {
            this.addImagePreview(previewWrapper, file);
        } else if (file.type.startsWith('text/') || file.name.endsWith('.json') || file.name.endsWith('.xml')) {
            this.addTextPreview(previewWrapper, file);
        } else if (file.type === 'application/pdf') {
            this.addPdfPreview(previewWrapper, file);
        }

        previewContainer.appendChild(previewWrapper);
    }

    /**
     * Get file type information with icon and color
     */
    getFileTypeInfo(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        const { type } = file;

        const fileTypes = {
            // Images
            'image/': { icon: '🖼️', color: 'var(--neon-blue)', typeLabel: 'Image File' },
            'jpg': { icon: '🖼️', color: 'var(--neon-blue)', typeLabel: 'JPEG Image' },
            'png': { icon: '🖼️', color: 'var(--neon-blue)', typeLabel: 'PNG Image' },
            'gif': { icon: '🎞️', color: 'var(--neon-purple)', typeLabel: 'GIF Animation' },
            'svg': { icon: '🎨', color: 'var(--neon-blue)', typeLabel: 'SVG Vector' },
            
            // Documents
            'application/pdf': { icon: '📄', color: 'var(--error)', typeLabel: 'PDF Document' },
            'txt': { icon: '📝', color: 'var(--text-primary)', typeLabel: 'Text File' },
            'md': { icon: '📋', color: 'var(--neon-blue)', typeLabel: 'Markdown' },
            'json': { icon: '🔧', color: 'var(--warning)', typeLabel: 'JSON Data' },
            'xml': { icon: '🏷️', color: 'var(--neon-green)', typeLabel: 'XML Data' },
            'csv': { icon: '📊', color: 'var(--success)', typeLabel: 'CSV Data' },
            
            // Code files
            'js': { icon: '⚡', color: 'var(--warning)', typeLabel: 'JavaScript' },
            'html': { icon: '🌐', color: 'var(--neon-orange)', typeLabel: 'HTML' },
            'css': { icon: '🎨', color: 'var(--neon-blue)', typeLabel: 'CSS' },
            'py': { icon: '🐍', color: 'var(--neon-green)', typeLabel: 'Python' },
            'cpp': { icon: '⚙️', color: 'var(--neon-blue)', typeLabel: 'C++' },
            'c': { icon: '⚙️', color: 'var(--neon-blue)', typeLabel: 'C' },
            
            // Archives
            'zip': { icon: '📦', color: 'var(--neon-purple)', typeLabel: 'ZIP Archive' },
            'rar': { icon: '📦', color: 'var(--neon-purple)', typeLabel: 'RAR Archive' },
            'tar': { icon: '📦', color: 'var(--neon-purple)', typeLabel: 'TAR Archive' },
            '7z': { icon: '📦', color: 'var(--neon-purple)', typeLabel: '7-Zip Archive' },
            
            // Media
            'mp3': { icon: '🎵', color: 'var(--neon-green)', typeLabel: 'MP3 Audio' },
            'mp4': { icon: '🎬', color: 'var(--neon-red)', typeLabel: 'MP4 Video' },
            'avi': { icon: '🎬', color: 'var(--neon-red)', typeLabel: 'AVI Video' },
            'wav': { icon: '🎵', color: 'var(--neon-green)', typeLabel: 'WAV Audio' },
            
            // Default
            'default': { icon: '📄', color: 'var(--text-secondary)', typeLabel: 'Unknown File' }
        };

        // Check by MIME type first
        for (const [key, value] of Object.entries(fileTypes)) {
            if (type.startsWith(key)) {
                return value;
            }
        }

        // Check by extension
        return fileTypes[ext] || fileTypes.default;
    }

    /**
     * Add image preview
     */
    addImagePreview(container, file) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.cssText = `
            max-width: 120px;
            max-height: 80px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--glass-border);
            margin-top: var(--space-sm);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        `;
        img.onerror = () => {
            img.style.display = 'none';
        };
        container.appendChild(img);
    }

    /**
     * Add text file preview
     */
    addTextPreview(container, file) {
        if (file.size > 50000) {
            return; // Skip large files
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            const previewText = document.createElement('pre');
            previewText.textContent = content.substring(0, 150) + (content.length > 150 ? '...' : '');
            previewText.style.cssText = `
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.7rem;
                color: var(--text-dim);
                background: var(--bg-black);
                padding: var(--space-sm);
                border-radius: var(--radius-sm);
                border: 1px solid var(--glass-border);
                margin-top: var(--space-sm);
                max-width: 200px;
                overflow: hidden;
                white-space: pre-wrap;
                line-height: 1.2;
            `;
            container.appendChild(previewText);
        };
        reader.readAsText(file);
    }

    /**
     * Add PDF preview placeholder
     */
    addPdfPreview(container, file) {
        const pdfInfo = document.createElement('div');
        pdfInfo.style.cssText = `
            margin-top: var(--space-sm);
            padding: var(--space-sm);
            background: rgba(255, 0, 64, 0.1);
            border-radius: var(--radius-sm);
            border: 1px solid var(--error);
            font-size: var(--font-size-xs);
            color: var(--text-secondary);
            text-align: center;
        `;
        pdfInfo.textContent = 'PDF preview requires external viewer';
        container.appendChild(pdfInfo);
    }

    addLog(message, type = 'info', details = '') {
        // Store log entry for potential batching
        this._pendingLogs = this._pendingLogs || [];
        this._pendingLogs.push({ message, type, details, timestamp: new Date() });
        
        // Debounce DOM updates but show critical logs immediately
        if (!this._logUpdateDebounced) {
            this._logUpdateDebounced = this.debounce(() => this._flushPendingLogs(), 50);
        }
        
        // Show critical errors immediately
        if (type === 'error') {
            this._flushPendingLogs();
        } else {
            this._logUpdateDebounced();
        }
    }

    _flushPendingLogs() {
        if (!this._pendingLogs || this._pendingLogs.length === 0) {
            return;
        }

        // Process all pending logs
        const fragment = document.createDocumentFragment();
        
        this._pendingLogs.forEach(logData => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${logData.type}`;
            logEntry.setAttribute('tabindex', '0');
            
            // Create safe DOM elements instead of innerHTML
            const timestamp = document.createElement('span');
            timestamp.className = 'log-timestamp';
            timestamp.textContent = logData.timestamp.toLocaleTimeString();
            
            const icon = document.createElement('span');
            icon.className = `log-icon ${logData.type}`;
            icon.textContent = this.getLogIcon(logData.type);
            
            const content = document.createElement('div');
            content.className = 'log-content';
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'log-message';
            messageDiv.textContent = logData.message;
            content.appendChild(messageDiv);
            
            if (logData.details) {
                const detailsDiv = document.createElement('div');
                detailsDiv.className = 'log-details';
                detailsDiv.textContent = logData.details;
                content.appendChild(detailsDiv);
            }
            
            logEntry.appendChild(timestamp);
            logEntry.appendChild(icon);
            logEntry.appendChild(content);
            
            fragment.appendChild(logEntry);
        });
        
        // Add all entries at once to reduce reflows
        this.elements.logContainer.prepend(fragment);
        
        // Clear pending logs
        this._pendingLogs = [];

        // Debounce cleanup operations to avoid excessive DOM manipulation
        if (!this._logCleanupDebounced) {
            this._logCleanupDebounced = this.debounce(() => this._cleanupLogEntries(), 1000);
        }
        this._logCleanupDebounced();
    }

    _cleanupLogEntries() {
        // Limit log entries - batch removal for better performance
        const { logContainer } = this.elements;
        const childrenToRemove = logContainer.children.length - 200;
        if (childrenToRemove > 0) {
            // Remove excess children in batch to reduce reflows
            const elementsToRemove = Array.from(logContainer.children).slice(-childrenToRemove);
            elementsToRemove.forEach(element => logContainer.removeChild(element));
        }

        if (this.autoScrollLog) {
            this.elements.logContainer.scrollTop = 0; // Scroll to top for prepend
        }
    }

    getLogIcon(type) {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return '💬';
        }
    }

    clearLog() {
        this.elements.logContainer.innerHTML = '';
        this.addLog('Log cleared', 'info');
        this.showToast('Operation log cleared.', 'info');
    }

    exportLog() {
        const logEntries = Array.from(this.elements.logContainer.children).map(entryDiv => {
            const timestamp = entryDiv.querySelector('.log-timestamp').textContent;
            const message = entryDiv.querySelector('.log-message').textContent;
            const details = entryDiv.querySelector('.log-details') ? entryDiv.querySelector('.log-details').textContent : '';
            const type = entryDiv.classList.contains('success') ? 'SUCCESS' :
                         entryDiv.classList.contains('error') ? 'ERROR' :
                         entryDiv.classList.contains('warning') ? 'WARNING' : 'INFO';
            return `[${timestamp}] [${type}] ${message} ${details}`.trim();
        }).reverse(); // Reverse to get chronological order

        const blob = new Blob([logEntries.join('\n')], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `cyberbackup_log_${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        this.showToast('Log exported successfully.', 'success');
    }

    toggleAutoScroll() {
        this.autoScrollLog = !this.autoScrollLog;
        this.elements.autoScrollBtn.textContent = `📜 Auto-scroll: ${this.autoScrollLog ? 'ON' : 'OFF'}`;
        this.showToast(`Auto-scroll ${this.autoScrollLog ? 'enabled' : 'disabled'}.`, 'info');
    }

    toggleDebugConsole() {
        const { debugPanel, debugContent, debugToggle } = this.elements;
        const isExpanded = debugToggle.getAttribute('aria-expanded') === 'true';

        if (isExpanded) {
            debugPanel.style.maxHeight = '0';
            debugContent.classList.remove('show');
            debugToggle.setAttribute('aria-expanded', 'false');
        } else {
            debugPanel.style.maxHeight = debugPanel.scrollHeight + 'px'; // Set to actual height
            debugContent.classList.add('show');
            debugToggle.setAttribute('aria-expanded', 'true');
            this.loadLazyComponent('debugConsole'); // Lazy load debug console content
        }
    }

    showToast(message, type = 'info', duration = 3000) {
        // Use the new enhanced ToastManager for all toast functionality
        return this.toastManager.show(message, type, duration);
    }

    // Convenience methods for different toast types (backward compatibility)
    showSuccessToast(message, duration = 3000) {
        return this.toastManager.success(message, duration);
    }

    showErrorToast(message, duration = 5000) {
        return this.toastManager.error(message, duration);
    }

    showWarningToast(message, duration = 4000) {
        return this.toastManager.warning(message, duration);
    }

    showInfoToast(message, duration = 3000) {
        return this.toastManager.info(message, duration);
    }

    // Additional toast management methods
    dismissAllToasts() {
        return this.toastManager.dismissAll();
    }

    dismissToastsByType(type) {
        return this.toastManager.dismissByType(type);
    }

    formatBytes(bytes) {
        if (bytes === 0) {
            return '0 B';
        }
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }

    formatBytesPerSecond(bytesPerSecond) {
        if (bytesPerSecond === 0) {
            return '0 B/s';
        }
        const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s'];
        const i = parseInt(Math.floor(Math.log(bytesPerSecond) / Math.log(1024)));
        return Math.round(bytesPerSecond / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }

    formatTime(seconds) {
        if (seconds === '--:--') {
            return seconds; // Handle initial state
        }
        if (seconds < 0) {
            return '--:--';
        }
        const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
        const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
        const s = Math.floor(seconds % 60).toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    verifyDOMElements() {
        console.log('[DOM_VERIFICATION] Verifying critical DOM elements...');
        const criticalElements = [
            'primaryActionButton',
            'pauseButton', 
            'stopButton',
            'serverInput',
            'usernameInput',
            'fileDropZone',
            'saveConfigBtn',
            'confirmModal'
        ];
        
        const missingElements = [];
        
        for (const elementKey of criticalElements) {
            const element = this.elements[elementKey];
            if (!element) {
                missingElements.push(elementKey);
                console.error(`[DOM_VERIFICATION] Critical element missing: ${elementKey}`);
            } else {
                console.log(`[DOM_VERIFICATION] ✓ Found: ${elementKey}`);
            }
        }
        
        if (missingElements.length > 0) {
            console.error('[DOM_VERIFICATION] CRITICAL: Missing DOM elements:', missingElements);
            return false;
        }
        
        console.log('[DOM_VERIFICATION] All critical elements found successfully');
        return true;
    }

    saveConfig() {
        const config = {
            serverAddress: this.elements.serverInput.value,
            username: this.elements.usernameInput.value,
        };
        localStorage.setItem('cyberbackup_config', JSON.stringify(config));
        this.showToast('Configuration saved!', 'success');
        this.addLog('Configuration saved', 'info');
    }

    loadSavedConfig() {
        try {
            const savedConfig = localStorage.getItem('cyberbackup_config');
            if (savedConfig) {
                const config = JSON.parse(savedConfig);
                this.elements.serverInput.value = config.serverAddress || '127.0.0.1:1256';
                this.elements.usernameInput.value = config.username || '';  // No default username - let user enter their own
                this.addLog('Loaded saved configuration', 'info');
            }
        } catch (error) {
            console.warn('Failed to load saved config:', error);
            this.addLog('Failed to load config', 'warning', error.message);
        }
    }

    /**
     * Copy client ID to clipboard
     */
    copyClientId() {
        const { clientId } = this.state;
        if (!clientId) {
            this.showToast('No client ID available to copy', 'warning');
            return;
        }
        
        this.copyManager.copyToClipboard(
            clientId, 
            this.elements.copyClientIdButton,
            'Client ID copied to clipboard!'
        );
    }

    /**
     * Copy server address to clipboard
     */
    copyServerAddress() {
        const serverAddress = this.elements.serverInput.value;
        if (!serverAddress) {
            this.showToast('No server address to copy', 'warning');
            return;
        }
        
        this.copyManager.copyToClipboard(
            serverAddress, 
            this.elements.copyServerAddressButton,
            'Server address copied to clipboard!'
        );
    }

    /**
     * Copy selected file information to clipboard
     */
    copyFileInfo() {
        if (!this.state.selectedFile) {
            this.showToast('No file selected to copy', 'warning');
            return;
        }
        
        const fileInfo = `File: ${this.state.selectedFile.name}\nSize: ${this.formatBytes(this.state.selectedFile.size)}\nType: ${this.state.selectedFile.type || 'Unknown'}`;
        
        this.copyManager.copyToClipboard(
            fileInfo, 
            null,
            'File information copied to clipboard!'
        );
    }

    /**
     * Show recent files dropdown
     */
    showRecentFiles() {
        const container = this.elements.recentFilesBtn.parentElement;
        
        // Remove any existing dropdown
        const existingDropdown = container.querySelector('.recent-files-dropdown');
        if (existingDropdown) {
            existingDropdown.remove();
            return; // Toggle behavior
        }
        
        // Create and show recent files dropdown
        this.fileMemoryManager.createRecentFilesUI(container, (fileInfo) => {
            // Create a simulated file object from stored info
            const simulatedFile = {
                name: fileInfo.name,
                size: fileInfo.size,
                type: fileInfo.type,
                lastModified: fileInfo.lastModified
            };
            
            // Update state and UI as if user selected this file
            this.state.selectedFile = simulatedFile;
            this.addLog(`Recent file selected: ${fileInfo.name}`, 'info', 
                `Size: ${fileInfo.sizeFormatted}, Selected ${fileInfo.timeAgo}`);
            
            this.showToast(`Selected recent file: ${fileInfo.displayName}`, 'success', 2000);
            this.updateAllUI();
        });
        
        // Update button text temporarily
        const originalText = this.elements.recentFilesBtn.textContent;
        this.elements.recentFilesBtn.textContent = '✨ Select from recent...';
        
        setTimeout(() => {
            this.elements.recentFilesBtn.textContent = originalText;
        }, 3000);
    }

    /**
     * Record a backup to history when it completes or fails
     * @param {Object} status - Current backup status
     * @param {boolean} success - Whether the backup was successful
     */
    recordBackupToHistory(status, success) {
        try {
            const backupInfo = {
                status: success ? 'completed' : 'failed',
                filename: this.state.file_name || status.file_name || 'unknown',
                fileSize: this.state.file_size || status.file_size || 0,
                server: this.elements.serverInput?.value || 'unknown',
                username: this.elements.usernameInput?.value || 'unknown',
                duration: status.duration || 0,
                transferSpeed: this.state.speed || status.speed || 0,
                phase: status.phase,
                clientId: this.state.clientId,
                error: success ? null : (status.error || status.log?.operation || 'Unknown error')
            };

            const backupId = this.backupHistoryManager.addBackup(backupInfo);
            
            if (success) {
                this.addLog(`Backup recorded to history`, 'success', 
                    `File: ${backupInfo.filename}, Size: ${this.formatBytes(backupInfo.fileSize)}`);
                this.showToast(`✅ Backup completed and saved to history`, 'success', 4000);
            } else {
                this.addLog(`Failed backup recorded to history`, 'warning', 
                    `File: ${backupInfo.filename}, Error: ${backupInfo.error}`);
                this.showToast(`❌ Backup failed - recorded to history`, 'error', 4000);
            }
            
            debugLog(`Backup ${success ? 'completed' : 'failed'} - recorded to history with ID: ${backupId}`, 'BACKUP_HISTORY');
        } catch (error) {
            console.warn('Failed to record backup to history:', error);
            debugLog('Failed to record backup to history: ' + error.message, 'ERROR');
        }
    }

    /**
     * Format bytes for display
     */
    formatBytes(bytes) {
        if (bytes === 0) {
            return '0 Bytes';
        }
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Enhanced cleanup method to prevent memory leaks
    cleanup() {
        debugLog('Performing app cleanup...', 'APP_CLEANUP');
        
        try {
            // Clear all intervals and timeouts
            if (this.intervals) {
                this.intervals.clearAll();
            }

            // Clear state management intervals
            if (this.stateManagement && this.stateManagement.updateUIDebounced) {
                // Clear any pending debounced updates
                clearTimeout(this.stateManagement.updateUIDebounced);
            }

            // Cleanup file manager (remove any created elements)
            if (this.system && this.system.fileManager) {
                // Remove any temporary file inputs created by FileManager
                const tempFileInputs = document.querySelectorAll('input[type="file"]');
                tempFileInputs.forEach(input => {
                    if (input.style.display === 'none' && !input.id) {
                        input.remove();
                    }
                });
            }

            // Cleanup modals and overlays
            if (this.system && this.system.modal) {
                this.system.modal.hide();
            }
            if (this.system && this.system.confirmModal) {
                this.system.confirmModal.hide();
            }

            // Clear any pending toast notifications
            if (this.elements && this.elements.toastContainer) {
                this.elements.toastContainer.textContent = ''; // Clear safely
            }

            // Clear large log entries to free memory
            if (this.elements && this.elements.logContainer) {
                const { logContainer } = this.elements;
                const childrenToRemove = logContainer.children.length - 10;
                if (childrenToRemove > 0) {
                    // Batch remove for better performance
                    const elementsToRemove = Array.from(logContainer.children).slice(-childrenToRemove);
                    elementsToRemove.forEach(element => logContainer.removeChild(element));
                }
            }

            // Cleanup particle system
            if (this.particleSystem) {
                this.particleSystem.destroy();
            }
        

            // Cleanup error boundary
            if (this.errorBoundary) {
                this.errorBoundary.reset();
            }

            // Revoke any object URLs that might have been created for file previews
            document.querySelectorAll('img[src^="blob:"]').forEach(img => {
                URL.revokeObjectURL(img.src);
            });

            debugLog('App cleanup completed successfully', 'APP_CLEANUP');
        } catch (error) {
            console.error('[App] Cleanup error:', error);
            debugLog('App cleanup failed: ' + error.message, 'APP_CLEANUP');
        }
    }

    // Add page unload handler for cleanup
    setupPageUnloadHandler() {
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });

        // Also cleanup on page visibility change (when tab becomes hidden)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Pause expensive operations when tab is hidden
                if (this.particleSystem) {
                    this.particleSystem.toggle();
                }
                // Reduce polling frequency
                if (this.stateManagement) {
                    this.stateManagement.adaptivePollInterval = Math.min(
                        this.stateManagement.maxPollInterval,
                        this.stateManagement.adaptivePollInterval * 2
                    );
                }
            } else {
                // Resume normal operations when tab becomes visible
                if (this.particleSystem && !this.particleSystem.isEnabled) {
                    this.particleSystem.toggle();
                }
                // Reset polling frequency
                if (this.stateManagement) {
                    this.stateManagement.adaptivePollInterval = this.stateManagement.minPollInterval;
                }
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // === SENTRY INITIALIZATION ===
    console.log('Initializing Sentry error tracking...');
    try {
        Sentry.init({
            dsn: "https://1676bfc28540fa5c2bcdb72d402125fd@o4509746411470848.ingest.us.sentry.io/4509747877773312",
            environment: window.location.hostname === 'localhost' ? 'development' : 'production',
            integrations: [
                new Sentry.BrowserTracing(),
                new Sentry.BrowserProfilingIntegration(),
            ],
            // Performance Monitoring
            tracesSampleRate: 0.1, // 10% of transactions for performance monitoring
            profilesSampleRate: 0.1, // 10% of transactions for profiling
            
            // Additional configuration
            debug: window.location.hostname === 'localhost',
            beforeSend(event, hint) {
                // Filter out common non-critical errors
                if (hint.originalException) {
                    const error = hint.originalException;
                    // Filter out WebSocket connection errors (expected during network issues)
                    if (error.message && error.message.includes('WebSocket connection')) {
                        return null;
                    }
                    // Filter out fetch abort errors (expected during navigation)
                    if (error.name === 'AbortError') {
                        return null;
                    }
                }
                return event;
            },
        });
        
        // Set user context
        Sentry.setTag('component', 'web-gui');
        Sentry.setTag('framework', 'cyberbackup');
        Sentry.setContext('browser', {
            name: navigator.userAgent,
            url: window.location.href
        });
        
        console.log('✅ Sentry initialized successfully for CyberBackup Web GUI');
    } catch (error) {
        console.warn('⚠️ Failed to initialize Sentry:', error);
    }
    
    // === IMMEDIATE TEST ===
    console.log('JavaScript is working! Script started loading...');
    
    debugLog('=== SCRIPT LOADING STARTED ===');
    
    debugLog('Defining App class...');

    // Initialize the main application
    debugLog('Initializing App instance...');
    window.app = new App(); // Make globally accessible
    debugLog('App instance initialized.');

    // Initialize error boundary system
    debugLog('Initializing ErrorBoundary...');
    const errorBoundary = new ErrorBoundary(window.app);
    window.app.errorBoundary = errorBoundary;
    debugLog('ErrorBoundary initialized.');

    // Initialize particle system
    debugLog('Initializing ParticleSystem...');
    const particleSystem = new ParticleSystem(window.app);
    particleSystem.init();
    window.app.particleSystem = particleSystem;
    debugLog('ParticleSystem initialized.');

    // Initialize interactive effects
    debugLog('Initializing InteractiveEffects...');
    window.app.interactiveEffects.initialize();
    debugLog('InteractiveEffects initialized.');

    // Initial UI update
    window.app.updateAllUI();

    debugLog('=== SCRIPT LOADING COMPLETE ===');
});

/**
 * Data Stream Progress Ring System
 * Manages the multi-ring progress visualization with particle effects
 */
class DataStreamProgressRing {
    constructor(elements) {
        this.elements = elements;
        this.particles = [];
        this.lastPhase = null;
        this.particleCount = 0;
        this.maxParticles = 12;
        this.animationSpeed = 3000; // Base animation duration in ms
        
        // Phase position mapping (in degrees, starting from top)
        this.phasePositions = {
            'SYSTEM_READY': 0,
            'CONNECTING': 0,
            'AUTHENTICATING': 90,
            'ENCRYPTING': 180,
            'TRANSFERRING': 270,
            'VERIFYING': 45,
            'COMPLETED': 360,
            'ERROR': 315
        };
        
        this.init();
    }
    
    init() {
        // Initialize SVG path for progress circle
        if (this.elements.progressCircle) {
            const radius = this.elements.progressCircle.r.baseVal.value;
            this.circleRadius = radius;
            this.circumference = radius * 2 * Math.PI;
        }
        
        // Create particle template
        this.createParticleTemplate();
        
        console.log('[DataStreamProgressRing] Initialized');
    }
    
    createParticleTemplate() {
        // Create reusable SVG path for particles to follow
        this.particlePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        this.particlePath.setAttribute('d', `M 150 ${150 - this.circleRadius} A ${this.circleRadius} ${this.circleRadius} 0 1 1 ${150 - 0.1} ${150 - this.circleRadius}`);
        this.particlePath.setAttribute('fill', 'none');
        this.particlePath.setAttribute('stroke', 'none');
        this.particlePath.setAttribute('id', 'particleMotionPath');
        
        // Add path to SVG defs
        const defs = this.elements.progressRing.querySelector('defs');
        if (defs && !document.getElementById('particleMotionPath')) {
            defs.appendChild(this.particlePath);
        }
    }
    
    updatePhase(phase, speed = 0) {
        if (this.lastPhase !== phase) {
            this.animatePhaseTransition(phase);
            this.lastPhase = phase;
        }
        
        this.updatePhaseIndicator(phase);
        this.updateParticleSystem(speed, phase);
        this.updateRingState(phase);
    }
    
    updatePhaseIndicator(phase) {
        const position = this.phasePositions[phase] || 0;
        const arcLength = 60; // 60 degree arc
        
        // Calculate SVG path for phase indicator arc
        const startAngle = (position - arcLength / 2) * Math.PI / 180;
        const endAngle = (position + arcLength / 2) * Math.PI / 180;
        
        const radius = this.circleRadius - 10; // Slightly inside the main progress ring
        const centerX = 150;
        const centerY = 150;
        
        const startX = centerX + radius * Math.sin(startAngle);
        const startY = centerY - radius * Math.cos(startAngle);
        const endX = centerX + radius * Math.sin(endAngle);
        const endY = centerY - radius * Math.cos(endAngle);
        
        const largeArcFlag = arcLength > 180 ? 1 : 0;
        
        const pathData = `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${endX} ${endY}`;
        
        if (this.elements.phaseIndicatorArc) {
            this.elements.phaseIndicatorArc.setAttribute('d', pathData);
            this.elements.phaseIndicatorArc.classList.add('active');
        }
    }
    
    updateParticleSystem(speed, phase) {
        if (!this.elements.particleStream) {
            return;
        }
        
        // Adjust particle count and speed based on transfer speed
        const targetParticleCount = Math.min(this.maxParticles, Math.max(2, Math.floor(speed / 100000))); // 1 particle per 100KB/s
        const speedMultiplier = Math.max(0.5, Math.min(3, speed / 1000000)); // Speed factor based on MB/s
        
        // Generate new particles if needed
        if (this.particles.length < targetParticleCount && phase === 'TRANSFERRING') {
            this.generateParticles(targetParticleCount - this.particles.length, speedMultiplier);
        }
        
        // Remove excess particles
        if (this.particles.length > targetParticleCount) {
            this.removeParticles(this.particles.length - targetParticleCount);
        }
        
        // Update particle animation speed
        this.updateParticleSpeed(speedMultiplier, phase);
    }
    
    generateParticles(count, speedMultiplier) {
        for (let i = 0; i < count; i++) {
            const particle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            particle.classList.add('data-particle');
            particle.setAttribute('r', '2');
            particle.setAttribute('fill', 'var(--neon-blue)');
            particle.setAttribute('filter', 'url(#particleGlow)');
            
            // Create animation
            const animateMotion = document.createElementNS('http://www.w3.org/2000/svg', 'animateMotion');
            animateMotion.setAttribute('dur', `${this.animationSpeed / speedMultiplier}ms`);
            animateMotion.setAttribute('repeatCount', 'indefinite');
            animateMotion.setAttribute('begin', `${i * 200}ms`); // Stagger particles
            
            const mpath = document.createElementNS('http://www.w3.org/2000/svg', 'mpath');
            mpath.setAttribute('href', '#particleMotionPath');
            
            animateMotion.appendChild(mpath);
            particle.appendChild(animateMotion);
            
            this.elements.particleStream.appendChild(particle);
            this.particles.push({
                element: particle,
                animation: animateMotion,
                id: Date.now() + i
            });
        }
    }
    
    removeParticles(count) {
        for (let i = 0; i < count && this.particles.length > 0; i++) {
            const particle = this.particles.pop();
            if (particle.element.parentNode) {
                particle.element.parentNode.removeChild(particle.element);
            }
        }
    }
    
    updateParticleSpeed(speedMultiplier, phase) {
        const newDuration = this.animationSpeed / speedMultiplier;
        
        this.particles.forEach(particle => {
            if (particle.animation) {
                particle.animation.setAttribute('dur', `${newDuration}ms`);
                
                // Apply phase-specific particle styling
                if (phase === 'TRANSFERRING') {
                    particle.element.setAttribute('fill', 'var(--neon-green)');
                } else if (phase === 'ENCRYPTING') {
                    particle.element.setAttribute('fill', 'var(--neon-purple)');
                } else {
                    particle.element.setAttribute('fill', 'var(--neon-blue)');
                }
            }
        });
    }
    
    updateRingState(phase) {
        if (!this.elements.progressRing) {
            return;
        }
        
        // Remove existing phase classes
        this.elements.progressRing.classList.remove('connecting', 'encrypting', 'transferring');
        
        // Add current phase class
        if (phase === 'CONNECTING' || phase === 'AUTHENTICATING') {
            this.elements.progressRing.classList.add('connecting');
        } else if (phase === 'ENCRYPTING') {
            this.elements.progressRing.classList.add('encrypting');
        } else if (phase === 'TRANSFERRING') {
            this.elements.progressRing.classList.add('transferring');
        }
    }
    
    animatePhaseTransition(newPhase) {
        // Trigger glitch effect on phase display
        if (this.elements.progressStatus) {
            this.elements.progressStatus.classList.add('phase-transition');
            
            setTimeout(() => {
                this.elements.progressStatus.classList.remove('phase-transition');
            }, 800);
        }
        
        // Reset phase indicator for smooth transition
        if (this.elements.phaseIndicatorArc) {
            this.elements.phaseIndicatorArc.classList.remove('active');
            
            setTimeout(() => {
                this.elements.phaseIndicatorArc.classList.add('active');
            }, 100);
        }
    }
    
    reset() {
        // Clear all particles
        this.removeParticles(this.particles.length);
        
        // Reset phase indicator
        if (this.elements.phaseIndicatorArc) {
            this.elements.phaseIndicatorArc.classList.remove('active');
        }
        
        // Reset ring state
        if (this.elements.progressRing) {
            this.elements.progressRing.classList.remove('connecting', 'encrypting', 'transferring');
        }
        
        this.lastPhase = null;
    }
    
    setActive(isActive) {
        if (this.elements.progressRing) {
            this.elements.progressRing.classList.toggle('active', isActive);
        }
    }
}

export { App };
