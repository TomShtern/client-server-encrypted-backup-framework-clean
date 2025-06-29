// === IMMEDIATE TEST ===
alert('JavaScript is working! Script started loading...');
console.log('JavaScript is working! Script started loading...');

// === COMPREHENSIVE DEBUG LOGGING ===
function debugLog(message) {
    console.log('[DEBUG] ' + message);
    // Also show in page for visibility
    const debugDiv = document.getElementById('debug-output') || createDebugDiv();
    debugDiv.innerHTML += '<div>[' + new Date().toLocaleTimeString() + '] ' + message + '</div>';
}

function createDebugDiv() {
    const div = document.createElement('div');
    div.id = 'debug-output';
    div.style.cssText = 'position:fixed;top:10px;right:10px;width:400px;height:200px;background:black;color:lime;padding:10px;border:1px solid lime;overflow-y:auto;z-index:9999;font-family:monospace;font-size:12px;';
    document.body.appendChild(div);
    return div;
}

debugLog('=== SCRIPT LOADING STARTED ===');

/**
 * =================================================================
 * API-DRIVEN CLIENT GUI v3.0
 * =================================================================
 * This version has been refactored to communicate with a local
 * C++ web server (via Boost.Beast) instead of a file-based system.
 * The GUI now acts as a true frontend to the C++ backend.
 * =================================================================
 */

// Interval Manager to prevent leaks
debugLog('Defining IntervalManager class...');
class IntervalManager {
    constructor() {
        this.intervals = new Map();
    }
    set(name, callback, delay) {
        this.clear(name);
        this.intervals.set(name, setInterval(callback, delay));
    }
    clear(name) {
        if (this.intervals.has(name)) {
            clearInterval(this.intervals.get(name));
            this.intervals.delete(name);
        }
    }
    clearAll() {
        this.intervals.forEach(id => clearInterval(id));
        this.intervals.clear();
    }
}
debugLog('IntervalManager class defined successfully');

/**
 * NEW: ApiClient
 * Handles all communication with the local C++ web server.
 */
debugLog('Defining ApiClient class...');
class ApiClient {
    constructor(baseUrl = 'http://127.0.0.1:9090') {
        this.baseUrl = baseUrl;
    }

    async _request(endpoint, options = {}) {
        try {
            console.log(`Making ${options.method || 'GET'} request to: ${this.baseUrl}${endpoint}`);
            if (options.body) {
                console.log('Request body:', options.body);
                debugLog(`API: ${options.method || 'GET'} ${endpoint} with body: ${options.body}`);
            }
            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            console.log('Response status:', response.status, response.statusText);
            debugLog(`API: Response status: ${response.status} ${response.statusText}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: response.statusText }));
                console.error('API Error data:', errorData);
                debugLog(`API ERROR: ${JSON.stringify(errorData)}`);
                throw new Error(`API Error: ${errorData.message || 'Unknown Error'}`);
            }
            const responseData = await response.json();
            console.log('Response data:', responseData);
            debugLog(`API: Response data: ${JSON.stringify(responseData)}`);
            return responseData;
        } catch (err) {
            // This catches network errors (e.g., C++ client not running) or API errors
            console.error(`API request to ${endpoint} failed:`, err);
            debugLog(`API NETWORK ERROR: ${err.message}`);
            throw err; // Re-throw to be handled by the calling function
        }
    }

    getStatus() {
        return this._request('/api/status');
    }

    connect(config) {
        console.log('ApiClient.connect() called with:', config);
        debugLog('API: Making POST request to /api/connect');
        return this._request('/api/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
    }

    startBackup(file, username = 'testuser') {
        // Create FormData to send the actual file
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', username);
        
        console.log('ApiClient.startBackup() called with file:', file.name, 'size:', file.size);
        debugLog('API: Making multipart/form-data POST request to /api/start_backup');
        
        // Send FormData (no Content-Type header needed - browser sets it automatically with boundary)
        return this._request('/api/start_backup', {
            method: 'POST',
            body: formData
        });
    }

    stop() { return this._request('/api/stop', { method: 'POST' }); }
    pause() { return this._request('/api/pause', { method: 'POST' }); }
    resume() { return this._request('/api/resume', { method: 'POST' }); }
}
debugLog('ApiClient class defined successfully');

// Configuration Manager (largely unchanged)        
debugLog('Defining ConfigManager class...');
class ConfigManager {
    constructor() {
        this.config = {
            server: '127.0.0.1',
            port: 1256,
            username: 'testuser', // Default username for testing
            filepath: 'test.txt', // Default file for testing
        };
    }
    loadFromStorage() {
        try {
            const saved = localStorage.getItem('cyberbackup_config');
            if (saved) {
                this.config = { ...this.config, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.warn('Invalid config in localStorage.');
            localStorage.removeItem('cyberbackup_config');
        }
    }
    saveToStorage() {
        localStorage.setItem('cyberbackup_config', JSON.stringify(this.config));
    }
    validate() {
        const errors = [];
        if (!this.config.server || !this.config.port) errors.push('Server address and port are required');
        if (!this.config.username) errors.push('Username is required');
        if (!this.config.filepath) errors.push('A file must be selected');
        return errors;
    }
}
debugLog('ConfigManager class defined successfully');

// UI Controller Classes (moved here to fix initialization order)
debugLog('Defining UIController class...');
class UIController {
    createLogEntry(log) { 
        const entry = document.createElement('div');
        entry.className = `log-entry ${log.type}`;
        const icon = log.type === 'success' ? '✓' : log.type === 'error' ? '✗' : log.type === 'warning' ? '⚠' : 'ℹ';
        entry.innerHTML = `<span class="log-timestamp">${log.timestamp}</span><div class="log-icon ${log.type}">${icon}</div><div class="log-content"><div class="log-message">${log.operation}</div><div class="log-details">${log.details || ''}</div></div>`;
        return entry;
     }
    updateProgressRing(p) { 
        const circle = document.getElementById('progressCircle');
        if (!circle || !p) return;
        if (!circle.getAttribute('data-circumference')) {
            const radius = parseFloat(circle.getAttribute('r'));
            circle.setAttribute('data-circumference', 2 * Math.PI * radius);
        }
        const circumference = circle.getAttribute('data-circumference');
        circle.style.strokeDasharray = circumference;
        circle.style.strokeDashoffset = circumference - (p / 100) * circumference;
    }
    showFilePreview(file) { /* Basic implementation */ }
    getFileIcon(type) { return '📁'; }
}
debugLog('UIController class defined successfully');

// Enhanced UI Controller with better visual feedback
debugLog('Defining EnhancedUIController class...');
class EnhancedUIController extends UIController {
    constructor() {
        super();
        this.animationId = null;
    }

    createLogEntry(log) { 
        const entry = document.createElement('div');
        entry.className = `log-entry ${log.type}`;
        entry.setAttribute('tabindex', '0');
        entry.setAttribute('role', 'listitem');
        
        const icon = log.type === 'success' ? '✓' : log.type === 'error' ? '✗' : log.type === 'warning' ? '⚠' : 'ℹ';
        entry.innerHTML = `
            <span class="log-timestamp">${log.timestamp}</span>
            <div class="log-icon ${log.type}">${icon}</div>
            <div class="log-content">
                <div class="log-message">${log.operation}</div>
                ${log.details ? `<div class="log-details">${log.details}</div>` : ''}
            </div>
        `;

        // Add entrance animation
        entry.style.opacity = '0';
        entry.style.transform = 'translateX(-20px)';
        
        requestAnimationFrame(() => {
            entry.style.transition = 'all 0.3s ease-out';
            entry.style.opacity = '1';
            entry.style.transform = 'translateX(0)';
        });

        return entry;
    }

    updateProgressRing(percentage) { 
        const circle = document.getElementById('progressCircle');
        const ring = document.querySelector('.progress-ring');
        
        if (!circle) return;

        if (!circle.getAttribute('data-circumference')) {
            const radius = parseFloat(circle.getAttribute('r'));
            const circumference = 2 * Math.PI * radius;
            circle.setAttribute('data-circumference', circumference);
            circle.style.strokeDasharray = circumference;
        }
        
        const circumference = parseFloat(circle.getAttribute('data-circumference'));
        const offset = circumference - (percentage / 100) * circumference;
        
        // Animate the progress change
        circle.style.transition = 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        circle.style.strokeDashoffset = offset;

        // Add glow effect when progress is active
        if (ring) {
            if (percentage > 0 && percentage < 100) {
                ring.classList.add('active');
            } else {
                ring.classList.remove('active');
            }
        }
    }

    showFilePreview(file) {
        const previewContainer = document.getElementById('filePreview');
        if (!previewContainer) return;

        previewContainer.innerHTML = '';
        
        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.style.maxWidth = '100px';
            img.style.maxHeight = '100px';
            img.style.borderRadius = '8px';
            previewContainer.appendChild(img);
        } else {
            const icon = this.getFileIcon(file.type || file.name);
            previewContainer.innerHTML = `<div class="file-icon-large">${icon}</div>`;
        }
    }

    getFileIcon(typeOrName) {
        const type = typeOrName.toLowerCase();
        if (type.includes('image/') || type.endsWith('.jpg') || type.endsWith('.png') || type.endsWith('.gif')) return '🖼️';
        if (type.includes('video/') || type.endsWith('.mp4') || type.endsWith('.avi') || type.endsWith('.mov')) return '🎥';
        if (type.includes('audio/') || type.endsWith('.mp3') || type.endsWith('.wav')) return '🎵';
        if (type.includes('text/') || type.endsWith('.txt') || type.endsWith('.md')) return '📄';
        if (type.endsWith('.pdf')) return '📕';
        if (type.endsWith('.zip') || type.endsWith('.rar') || type.endsWith('.7z')) return '🗜️';
        if (type.endsWith('.exe') || type.endsWith('.msi')) return '⚙️';
        return '📁';
    }
}
debugLog('EnhancedUIController class defined successfully');

// Browser Notification Manager
debugLog('Defining BrowserNotificationManager class...');
class BrowserNotificationManager {
    constructor() {
        this.supported = 'Notification' in window;
        this.permission = this.supported ? Notification.permission : 'denied';
        this.requestPermissionOnInit();
    }

    async requestPermissionOnInit() {
        if (this.supported && this.permission === 'default') {
            try {
                this.permission = await Notification.requestPermission();
            } catch (error) {
                console.warn('Could not request notification permission:', error);
            }
        }
    }

    show(title, message, options = {}) {
        // Show toast notification in GUI
        if (window.gui) {
            window.gui.showToast(`${title}: ${message}`, options.type || 'info');
        }

        // Show browser notification if supported and permitted
        if (this.supported && this.permission === 'granted') {
            const notification = new Notification(title, {
                body: message,
                icon: options.icon || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text y="18" font-size="20">🚀</text></svg>',
                badge: options.badge || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text y="18" font-size="20">🔒</text></svg>',
                requireInteraction: options.requireInteraction || false,
                silent: options.silent || false
            });

            // Auto-close after 5 seconds unless persistent
            if (!options.persistent) {
                setTimeout(() => notification.close(), 5000);
            }

            return notification;
        }

        return null;
    }

    showConnectionStatus(connected) {
        const title = connected ? 'Backup Client Connected' : 'Backup Client Disconnected';
        const message = connected ? 'Successfully connected to backup server' : 'Lost connection to backup server';
        this.show(title, message, { 
            type: connected ? 'success' : 'error',
            requireInteraction: !connected
        });
    }

    showBackupComplete(filename, success) {
        const title = success ? 'Backup Completed' : 'Backup Failed';
        const message = success ? `Successfully backed up ${filename}` : `Failed to backup ${filename}`;
        this.show(title, message, { 
            type: success ? 'success' : 'error',
            requireInteraction: !success
        });
    }

    showProgress(percentage, filename) {
        if (percentage === 25 || percentage === 50 || percentage === 75) {
            this.show('Backup Progress', `${filename} - ${percentage}% complete`, {
                type: 'info',
                silent: true
            });
        }
    }
}
debugLog('BrowserNotificationManager class defined successfully');

// Enhanced File Manager with modern APIs
debugLog('Defining EnhancedFileManager class...');
class EnhancedFileManager {
    constructor() {
        this.supportsFileSystemAccess = 'showOpenFilePicker' in window;
        this.supportsDragDrop = true;
    }

    async selectFile() {
        if (this.supportsFileSystemAccess) {
            try {
                const [fileHandle] = await window.showOpenFilePicker({
                    types: [{
                        description: 'All files',
                        accept: { '*/*': [] }
                    }],
                    excludeAcceptAllOption: false,
                    multiple: false
                });
                
                const file = await fileHandle.getFile();
                return file;
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.warn('File picker error:', error);
                }
                return null;
            }
        } else {
            // Fallback to traditional file input
            return new Promise((resolve) => {
                const input = document.createElement('input');
                input.type = 'file';
                input.onchange = () => resolve(input.files[0] || null);
                input.click();
            });
        }
    }

    setupDragAndDrop(dropZone, onFileSelected) {
        if (!this.supportsDragDrop) return;

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                onFileSelected(files[0]);
            }
        });
    }
}
debugLog('EnhancedFileManager class defined successfully');

// System Integration Manager
debugLog('Defining SystemIntegrationManager class...');
class SystemIntegrationManager {
    constructor() {
        this.notifications = new BrowserNotificationManager();
        this.fileManager = new EnhancedFileManager();
        this.visibility = document.visibilityState;
        this.setupVisibilityTracking();
    }

    setupVisibilityTracking() {
        document.addEventListener('visibilitychange', () => {
            this.visibility = document.visibilityState;
        });
    }

    isWindowVisible() {
        return this.visibility === 'visible';
    }

    notifyIfHidden(title, message, options = {}) {
        if (!this.isWindowVisible()) {
            this.notifications.show(title, message, { ...options, requireInteraction: true });
        }
    }

    // Keyboard shortcuts
    setupKeyboardShortcuts(gui) {
        document.addEventListener('keydown', (e) => {
            // Ctrl+O: Open file
            if (e.ctrlKey && e.key === 'o') {
                e.preventDefault();
                gui.selectFile();
            }
            
            // Ctrl+Enter: Start backup
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                gui.handlePrimaryAction();
            }
            
            // Escape: Stop operation
            if (e.key === 'Escape' && gui.state.isRunning) {
                e.preventDefault();
                gui.stopOperation();
            }
            
            // Ctrl+,: Open settings (future feature)
            if (e.ctrlKey && e.key === ',') {
                e.preventDefault();
                // gui.showSettings();
            }
        });
    }
}
debugLog('SystemIntegrationManager class defined successfully');

// Main Application Class (Refactored for API communication)
debugLog('Defining CyberBackupPro class...');
class CyberBackupPro {
    constructor() {
        this.api = new ApiClient();
        this.config = new ConfigManager();
        this.intervals = new IntervalManager();
        this.ui = new EnhancedUIController(); // Use enhanced UI controller
        this.system = new SystemIntegrationManager(); // Add system integration

        this.state = {
            isConnecting: false, // NEW: Tracks the connection attempt itself
            isConnected: false,  // Is the C++ client connected to the remote server
            isRunning: false,
            isPaused: false,
            clientId: null,
            currentPhase: 'SYSTEM_READY',
            logs: [],
            progress: {},
            debugVisible: false,
            autoScroll: true,
            selectedFile: null
        };
        
        this.pendingConfirmAction = null;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 CyberBackup Pro v3.0 (API Driven) Initializing...');
        this.config.loadFromStorage();
        this.updateConfigDisplay();
        this.setupEventListeners();
        this.ui = new EnhancedUIController(); // Use enhanced UI controller
        this.theme = new ThemeManager(); // assuming ThemeManager exists
        this.theme.loadSavedTheme();
        this.system.setupKeyboardShortcuts(this); // Add keyboard shortcuts

        // Start master status polling
        this.intervals.set('statusPoll', () => this.pollStatus(), 1000);
        this.addLog('System Initialized', 'success', 'Ready to connect to C++ client.');
        this.system.notifications.show('CyberBackup Pro', 'Application ready', { type: 'info', silent: true });
        
        try {
            // Initialize with enhanced file drop zone
            const dropZone = document.querySelector('.file-drop-zone');
            if (dropZone) {
                this.system.fileManager.setupDragAndDrop(dropZone, (file) => {
                    this.handleFileSelection({ target: { files: [file] } });
                });
            }
        } catch (error) {
            console.warn('Could not setup enhanced file handling:', error);
        }
    }

    setupEventListeners() {
         // Configuration inputs with validation
        document.getElementById('serverInput').addEventListener('input', (e) => {
            this.updateServerConfig(e.target.value);
            this.validateAndUpdateUI();
        });
        
        document.getElementById('usernameInput').addEventListener('input', (e) => {
            this.config.config.username = e.target.value;
            this.validateAndUpdateUI();
        });
        
        // Enhanced file input with drag & drop
        const fileInput = document.getElementById('fileInput');
        const dropZone = document.getElementById('fileDropZone');
        
        fileInput.addEventListener('change', (e) => this.handleFileSelection(e));
        
        // Drag & drop functionality
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
        dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.classList.remove('drag-over'); });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                this.handleFileSelection({ target: { files: e.dataTransfer.files } });
            }
        });
    }
    
    // NEW: Master Polling Function
    async pollStatus() {
        try {
            console.log('pollStatus() - fetching status...');
            const status = await this.api.getStatus();
            console.log('pollStatus() - received status:', status);
            debugLog('POLL: Status received: ' + JSON.stringify(status));
            
            // Update state machine
            this.state.isConnected = status.isConnected;
            this.state.isRunning = status.isRunning;
            this.state.isPaused = status.isPaused;
            this.state.currentPhase = status.phase;
            this.state.clientId = status.clientId;

            console.log('pollStatus() - updated state:', this.state);
            debugLog('POLL: State updated - connected: ' + this.state.isConnected);

            if (status.progress) this.updateProgress(status.progress);
            if (status.log) this.addLog(status.log.operation, status.log.success ? 'success' : 'error', status.log.details);
            
            // The connection attempt succeeded if we get a valid poll response
            if (this.state.isConnecting) this.state.isConnecting = false;

            // CRITICAL FIX: Update all UI elements after state changes
            this.updateAllUI();
            debugLog('POLL: UI updated after state change');

        } catch (error) {
            // This error means the C++ client is likely offline
            this.state.isConnecting = false;
            this.state.isConnected = false;
            this.state.isRunning = false;
        }
        
        // Update all UI elements based on the new state
        this.updateAllUI();
    }

    // NEW: Central UI Update Function
    updateAllUI() {
        this.updateConnectionStatus();
        this.updateControlButtons();
        this.updatePhase(this.state.currentPhase);
        this.updateClientIdDisplay();
        if (this.state.debugVisible) {
            document.getElementById('progressJsonViewer').textContent = JSON.stringify(this.state, null, 2);
        }
    }

    // REFACTORED: Action Handlers now call the API           
    async handlePrimaryAction() {
        console.log('Primary action clicked');
        console.log('Current state:', this.state);
        console.log('Current config:', this.config.config);
        
        if (!this.validateAndUpdateUI()) {
            console.log('Validation failed');
            const errors = this.config.validate();
            console.log('Validation errors:', errors);
            this.showToast('Please fill in all required fields: ' + errors.join(', '), 'error');
            return;
        }
        
        console.log('Validation passed');
        if (this.state.isRunning && this.state.isPaused) await this.resumeOperation();
        else if (!this.state.isConnected) await this.connectToServer();
        else if (!this.state.isRunning) await this.startBackup();
    }

    async connectToServer() {
        console.log('connectToServer() called');
        debugLog('CONNECT: Starting connection attempt...');
        this.state.isConnecting = true;
        this.updateAllUI(); // Immediately show "Connecting..."
        try {
            console.log('Sending config to API:', this.config.config);
            debugLog('CONNECT: Sending config to API: ' + JSON.stringify(this.config.config));
            const response = await this.api.connect(this.config.config);
            console.log('API connect response:', response);
            debugLog('CONNECT: API response received: ' + JSON.stringify(response));
            // No need to do anything here, the next pollStatus will update the state
            this.addLog('Connect command sent', 'info', `Awaiting response from ${this.config.config.server}`);
            debugLog('CONNECT: Command sent successfully');
            
            // Force immediate status poll to update GUI quickly
            setTimeout(() => this.pollStatus(), 100);
            debugLog('CONNECT: Immediate status poll scheduled');
        } catch (error) {
            console.error('Connect error:', error);
            debugLog('CONNECT ERROR: ' + error.message);
            this.state.isConnecting = false;
            this.updateAllUI();
            this.showToast('Failed to send connect command. Is the C++ client running?', 'error');
        }
    }

    async startBackup() {
        try {
            // Check if a file is selected
            if (!this.state.selectedFile) {
                this.showToast('No file selected for backup.', 'error');
                return;
            }
            
            // Get username from config
            const username = this.config.config.username || 'testuser';
            
            // Send the actual file for upload
            await this.api.startBackup(this.state.selectedFile, username);
            this.addLog('File backup started', 'success', `Uploading ${this.state.selectedFile.name}`);
        } catch (error) {
            console.error('Backup start error:', error);
            this.showToast('Failed to start backup: ' + error.message, 'error');
        }
    }
    
    async pauseOperation() { try { await this.api.pause(); } catch(e) { this.showToast('Failed to send pause command', 'error'); } }
    async resumeOperation() { try { await this.api.resume(); } catch(e) { this.showToast('Failed to send resume command', 'error'); } }
    
    stopOperation() {
        this.showConfirmModal('Stop Operation', 'Are you sure?', () => this.executeStop());
    }

    async executeStop() {
        try {
            await this.api.stop();
        } catch (e) {
            this.showToast('Failed to send stop command', 'error');
        }
    }

    // REFACTORED: UI Update Functions now read from this.state
    updateConnectionStatus() {
        console.log('updateConnectionStatus() called - state:', this.state);
        debugLog('UI: Updating connection status - connected: ' + this.state.isConnected + ', connecting: ' + this.state.isConnecting);
        
        const led = document.getElementById('connectionLed');
        const text = document.getElementById('connectionText');
        
        if (!led || !text) {
            console.error('Connection status elements not found!');
            debugLog('UI ERROR: Connection status elements not found');
            return;
        }
        
        led.classList.remove('connected', 'connecting');

        if (this.state.isConnecting) {
            led.classList.add('connecting');
            text.textContent = 'CONNECTING...';
            console.log('UI: Set to CONNECTING...');
            debugLog('UI: Connection status set to CONNECTING');
        } else if (this.state.isConnected) {
            led.classList.add('connected');
            text.textContent = 'ONLINE';
            console.log('UI: Set to ONLINE');
            debugLog('UI: Connection status set to ONLINE');
            // Show notification when connected
            this.system.notifications.showConnectionStatus(true);
        } else {
            text.textContent = 'OFFLINE';
            console.log('UI: Set to OFFLINE');
            debugLog('UI: Connection status set to OFFLINE');
            // Show notification when disconnected (but not on initial load)
            if (this.state.clientId) { // Only if we were previously connected
                this.system.notifications.showConnectionStatus(false);
            }
        }
    }

    updateControlButtons() {
        const primaryBtn = document.getElementById('primaryAction');
        const pauseBtn = document.getElementById('pauseBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        const primaryIcon = primaryBtn.querySelector('.btn-icon');
        const primaryText = primaryBtn.querySelector('.btn-text');
        
        primaryBtn.disabled = false; // Enable by default, disable in specific cases
        pauseBtn.disabled = true;
        stopBtn.disabled = true;

        if (this.state.isConnecting) {
            primaryBtn.disabled = true;
            primaryText.textContent = 'CONNECTING';
        } else if (this.state.isRunning) {
            if (this.state.isPaused) {
                primaryIcon.textContent = '▶️';
                primaryText.textContent = 'RESUME';
            } else {
                primaryBtn.disabled = true;
                primaryIcon.textContent = '🔗';
                primaryText.textContent = 'TRANSFERRING';
                pauseBtn.disabled = false;
            }
            stopBtn.disabled = false;
        } else if (this.state.isConnected) {
            primaryIcon.textContent = '🚀';
            primaryText.textContent = 'START BACKUP';
            if (!this.state.selectedFile) primaryBtn.disabled = true;
            stopBtn.disabled = false;
        } else { // Offline
            primaryIcon.textContent = '🚀';
            primaryText.textContent = 'CONNECT';
            if (!this.validateAndUpdateUI()) primaryBtn.disabled = true;
        }

        // Lock/unlock config panel
        const panel = document.querySelector('.config-panel');
        const inputs = panel.querySelectorAll('input, button');
        const isBusy = this.state.isConnecting || this.state.isRunning;
        panel.style.opacity = isBusy ? '0.6' : '1';
        inputs.forEach(input => input.disabled = isBusy);
    }

    updateProgress(data) {
        // This function is now just for rendering progress data from the state
        this.state.progress = data;
        const percentage = data.percentage || 0;
        this.ui.updateProgressRing(percentage);
        document.getElementById('progressPercentage').textContent = Math.round(percentage) + '%';
        document.getElementById('speedStat').textContent = data.speed || '0 B/s';
        document.getElementById('etaStat').textContent = data.eta || '--:--';
        document.getElementById('transferredStat').textContent = this.formatBytes(data.transferred || 0);
        
        // Show progress notifications at key milestones
        if (this.state.selectedFile) {
            this.system.notifications.showProgress(Math.round(percentage), this.state.selectedFile.name);
        }
    }
    
    updateClientIdDisplay() {
        const clientIdEl = document.getElementById('clientId');
        if (this.state.clientId) {
            clientIdEl.textContent = this.state.clientId.substring(0, 8) + '...';
            clientIdEl.title = this.state.clientId;
        } else {
            clientIdEl.textContent = 'Not connected';
        }
    }
    
    // Other functions (logging, modals, etc.) remain largely the same...
    addLog(operation, type, details) {
        const timestamp = new Date().toLocaleTimeString();
        const log = { timestamp, operation, type, details, id: Date.now() + Math.random() };
        this.state.logs.push(log);
        const logContainer = document.getElementById('logContainer');
        const entry = this.ui.createLogEntry(log); // Assumes UIController.createLogEntry exists
        logContainer.appendChild(entry);
        if (this.state.autoScroll) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        if (logContainer.children.length > 200) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<div class="toast-content"><div class="toast-message">${message}</div><button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button></div>`;
        container.appendChild(toast);
        setTimeout(() => {
            if ( container.contains(toast)) {
                toast.style.animation = 'toast-slide-out 0.3s forwards';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

     // ... [The rest of the helper functions: clearLog, exportLog, modal handlers, file handlers, etc.]
    updateServerConfig(value) {
        const parts = value.split(':');
        this.config.config.server = parts[0] || '';
        this.config.config.port = parseInt(parts[1]) || 1256;
    }

    validateAndUpdateUI() {
        const errors = this.config.validate();
        if (errors.length > 0) {
            // Optionally show errors, but the button state is handled by updateControlButtons
            return false;
        }
        return true;
    }

    handleFileSelection(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        this.state.selectedFile = file;
        this.config.config.filepath = file.name; // For saving config
        const sizeFormatted = this.formatBytes(file.size);
        
        document.getElementById('selectedFile').innerHTML = `<span class="file-icon">📁</span><div class="file-details"><div class="file-name" title="${file.name}">${file.name}</div><div class="file-size">${sizeFormatted}</div></div>`;
        document.getElementById('sizeStat').textContent = sizeFormatted;
        
        // Show file preview if supported
        this.ui.showFilePreview(file);
        
        this.addLog('File selected', 'info', `${file.name} (${sizeFormatted})`);
        this.updateAllUI();
    }

    async selectFile() {
        try {
            const file = await this.system.fileManager.selectFile();
            if (file) {
                this.handleFileSelection({ target: { files: [file] } });
            }
        } catch (error) {
            this.addLog('File selection failed', 'error', error.message);
        }
    }

    saveConfiguration() {
        this.config.saveToStorage();
        this.showToast('Configuration saved to browser storage.', 'success');
    }

    showConfirmModal(title, message, onConfirm) {
        this.pendingConfirmAction = onConfirm;
        document.getElementById('confirmTitle').textContent = title;
        document.getElementById('confirmMessage').textContent = message;
        document.getElementById('confirmModal').classList.add('show');
    }

    hideConfirmModal() {
        document.getElementById('confirmModal').classList.remove('show');
    }

    confirmAction() {
        if(this.pendingConfirmAction) this.pendingConfirmAction();
        this.hideConfirmModal();
    }

    updatePhase(phase) {
        this.state.currentPhase = phase;
        document.getElementById('currentPhase').innerHTML = `<span class="neon-text purple">${phase.replace(/_/g, ' ')}</span>`;
    }

    updateConfigDisplay() {
        document.getElementById('serverInput').value = `${this.config.config.server}:${this.config.config.port}`;
        document.getElementById('usernameInput').value = this.config.config.username;
    }

    clearLog() {
        this.state.logs = [];
        document.getElementById('logContainer').innerHTML = '';
        this.addLog('Log cleared', 'info', 'All previous entries removed');
    }

    exportLog() {
        const logData = this.state.logs.map(log => 
            `[${log.timestamp}] ${log.type.toUpperCase()}: ${log.operation}${log.details ? ' - ' + log.details : ''}`
        ).join('\n');
        
        const blob = new Blob([logData], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cyberbackup-log-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addLog('Log exported', 'success', `${this.state.logs.length} entries exported`);
    }

    toggleAutoScroll() {
        this.state.autoScroll = !this.state.autoScroll;
        const btn = document.getElementById('autoScrollBtn');
        btn.textContent = `📜 Auto-scroll: ${this.state.autoScroll ? 'ON' : 'OFF'}`;
        this.addLog('Auto-scroll toggled', 'info', this.state.autoScroll ? 'Enabled' : 'Disabled');
    }

    toggleDebug() {
        this.state.debugVisible = !this.state.debugVisible;
        const content = document.getElementById('debugContent');
        const btn = document.getElementById('debugToggle');
        
        if (this.state.debugVisible) {
            content.style.display = 'block';
            btn.setAttribute('aria-expanded', 'true');
        } else {
            content.style.display = 'none';
            btn.setAttribute('aria-expanded', 'false');
        }
    }

    setTheme(themeName) {
        // Theme switching logic
        document.body.className = `theme-${themeName}`;
        const themeButtons = document.querySelectorAll('.theme-btn');
        themeButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`.theme-btn.${themeName}`).classList.add('active');
        
        localStorage.setItem('cyberbackup_theme', themeName);
        this.addLog('Theme changed', 'info', `Switched to ${themeName} theme`);
    }
}
debugLog('CyberBackupPro class defined successfully');

// Theme Manager (keep this as it's still needed)
if (typeof ThemeManager === 'undefined') {
    class ThemeManager { 
        loadSavedTheme() {
            const savedTheme = localStorage.getItem('cyberbackup_theme') || 'cyberpunk';
            if (window.gui) {
                window.gui.setTheme(savedTheme);
            }
        } 
        setTheme(t) { 
            console.log(`Theme set to ${t}`); 
            if (window.gui) {
                window.gui.setTheme(t);
            }
        } 
    }
    window.ThemeManager = ThemeManager;
}

// Initialize the GUI - make it global so onclick handlers can access it
try {
    debugLog('Starting GUI initialization...');
    console.log('About to create CyberBackupPro...');
    alert('About to create CyberBackupPro...');
    
    // Check if classes are defined
    debugLog('Checking if classes are defined...');
    if (typeof ApiClient === 'undefined') {
        throw new Error('ApiClient class not defined');
    }
    debugLog('ApiClient class is defined');
    
    if (typeof ConfigManager === 'undefined') {
        throw new Error('ConfigManager class not defined'); 
    }
    debugLog('ConfigManager class is defined');
    
    if (typeof IntervalManager === 'undefined') {
        throw new Error('IntervalManager class not defined');
    }
    debugLog('IntervalManager class is defined');
    
    if (typeof CyberBackupPro === 'undefined') {
        throw new Error('CyberBackupPro class not defined');
    }
    debugLog('CyberBackupPro class is defined');
    
    console.log('All classes are defined, creating CyberBackupPro...');
    debugLog('All classes verified, instantiating CyberBackupPro...');
    window.gui = new CyberBackupPro();
    console.log('CyberBackupPro created successfully!');
    debugLog('CyberBackupPro instance created successfully');
    alert('CyberBackupPro created successfully! window.gui is now available.');
    
    // Test the method exists
    if (typeof window.gui.handlePrimaryAction === 'function') {
        console.log('handlePrimaryAction method is available');
        debugLog('handlePrimaryAction method verified');
    } else {
        throw new Error('handlePrimaryAction method not found on gui object');
    }
    
    debugLog('=== GUI INITIALIZATION COMPLETED SUCCESSFULLY ===');
    
} catch (error) {
    debugLog('ERROR during initialization: ' + error.message);
    console.error('ERROR creating CyberBackupPro:', error);
    alert('ERROR creating CyberBackupPro: ' + error.message + '\nStack: ' + error.stack);
}