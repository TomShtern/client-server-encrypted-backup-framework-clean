import { debugLog } from './debug-utils.js';

class ApiClient {
    constructor(baseUrl = 'http://127.0.0.1:9090') {
        this.baseUrl = baseUrl;
        this.defaultTimeout = 30000; // 30 seconds default
        this.statusTimeout = 5000;   // 5 seconds for status checks (reduced from 10s)
        this.connectTimeout = 15000; // 15 seconds for connection attempts
        this.uploadTimeout = 300000; // 5 minutes for file uploads
    }

    // Helper method to create fetch requests with timeout
    async fetchWithTimeout(url, options = {}, timeoutMs = this.defaultTimeout) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, timeoutMs);

        try {
            const startTime = performance.now();
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            const endTime = performance.now();
            const responseTime = endTime - startTime;

            clearTimeout(timeoutId);
            
            // Store response time for debugging
            this.lastResponseTime = responseTime;
            // debugLog(`API call to ${url} completed in ${responseTime.toFixed(0)}ms`, 'API_TIMING');

            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${timeoutMs}ms`);
            }
            throw error;
        }
    }

    async getStatus() {
        debugLog('Fetching status...', 'API');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/status`, {}, this.statusTimeout);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // debugLog('Status response:' + JSON.stringify(data), 'API');
        return await response.json();
    }

    async connect(config) {
        debugLog('Connecting to server...' + JSON.stringify(config), 'API');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/connect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config),
        }, this.connectTimeout);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        debugLog('Connect response:' + JSON.stringify(data), 'API');
        return data;
    }

    async startBackup(file, config) {
        debugLog('Starting backup...', 'API');
        console.log('[DEBUG] startBackup called with:', {file: file.name, config});
        console.log('[DEBUG] API URL:', `${this.baseUrl}/api/start_backup`);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', config.username);
        formData.append('server', config.serverIP);
        formData.append('port', config.serverPort);
        console.log('[DEBUG] FormData prepared:', {
            file: file.name,
            username: config.username,
            server: config.serverIP,
            port: config.serverPort
        });

        console.log('[DEBUG] Sending POST request to Flask API...');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/start_backup`, {
            method: 'POST',
            body: formData,
        }, this.uploadTimeout);
        console.log('[DEBUG] Response received:', response.status, response.statusText);
        if (!response.ok) {
            console.log('[ERROR] HTTP error in startBackup:', response.status, response.statusText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('[DEBUG] Start backup response data:', data);
        debugLog('Start backup response:' + JSON.stringify(data), 'API');
        return data;
    }

    async stopBackup() {
        debugLog('Stopping backup...', 'API');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/stop`, { method: 'POST' }, this.defaultTimeout);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        debugLog('Stop backup response:' + JSON.stringify(data), 'API');
        return data;
    }

    async pauseBackup() {
        debugLog('Pausing backup...', 'API');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/pause`, { method: 'POST' }, this.defaultTimeout);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        debugLog('Pause backup response:' + JSON.stringify(data), 'API');
        return data;
    }

    async resumeBackup() {
        debugLog('Resuming backup...', 'API');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/resume`, { method: 'POST' }, this.defaultTimeout);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        debugLog('Resume backup response:' + JSON.stringify(data), 'API');
        return data;
    }

    async getServerInfo() {
        debugLog('Fetching server info...', 'API');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/server_info`, {}, this.defaultTimeout);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        debugLog('Server info response:' + JSON.stringify(data), 'API');
        return data;
    }

    async getReceivedFiles() {
        debugLog('Fetching received files...', 'API');
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/received_files`, {}, this.defaultTimeout);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        debugLog('Received files response:' + JSON.stringify(data), 'API');
        return data;
    }

    // Get timing and performance information
    getPerformanceInfo() {
        return {
            lastResponseTime: this.lastResponseTime || 0,
            baseUrl: this.baseUrl,
            timeouts: {
                default: this.defaultTimeout,
                status: this.statusTimeout,
                connect: this.connectTimeout,
                upload: this.uploadTimeout
            }
        };
    }

    // Update timeout settings
    updateTimeouts(timeouts) {
        if (timeouts.default) {
            this.defaultTimeout = timeouts.default;
        }
        if (timeouts.status) {
            this.statusTimeout = timeouts.status;
        }
        if (timeouts.connect) {
            this.connectTimeout = timeouts.connect;
        }
        if (timeouts.upload) {
            this.uploadTimeout = timeouts.upload;
        }
        debugLog('API timeouts updated', 'API');
    }
}

export { ApiClient };