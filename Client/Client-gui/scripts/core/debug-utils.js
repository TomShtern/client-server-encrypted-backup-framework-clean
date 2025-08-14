// === ENHANCED DEBUG LOGGING SYSTEM ===
class DebugLogger {
    constructor() {
        this.levels = {
            ERROR: { value: 0, color: '#ff0040', prefix: 'ERROR' },
            WARN: { value: 1, color: '#ffff00', prefix: 'WARN' },
            INFO: { value: 2, color: '#00ffff', prefix: 'INFO' },
            DEBUG: { value: 3, color: '#00ff00', prefix: 'DEBUG' },
            TRACE: { value: 4, color: '#888888', prefix: 'TRACE' }
        };
        
        this.currentLevel = this.levels.ERROR; // Only show errors to reduce spam
        this.filters = new Set(); // Category filters
        this.debugDiv = null;
        this.isEnabled = true;
        this.maxEntries = 1000; // Prevent memory issues
        this.entries = [];
        
        // Load preferences from localStorage
        this.loadPreferences();
        
        // Setup keyboard shortcut for debug toggle
        this.setupKeyboardShortcuts();
    }

    setLevel(levelName) {
        if (this.levels[levelName]) {
            this.currentLevel = this.levels[levelName];
            this.savePreferences();
            this.log('DEBUG', 'DEBUG', `Debug level set to ${levelName}`);
        }
    }

    addFilter(category) {
        this.filters.add(category.toUpperCase());
        this.savePreferences();
    }

    removeFilter(category) {
        this.filters.delete(category.toUpperCase());
        this.savePreferences();
    }

    clearFilters() {
        this.filters.clear();
        this.savePreferences();
    }

    toggle() {
        this.isEnabled = !this.isEnabled;
        if (this.debugDiv) {
            this.debugDiv.classList.toggle('u-hidden', !this.isEnabled);
        }
        this.savePreferences();
    }

    log(level, category, message) {
        const levelObj = this.levels[level];
        if (!levelObj || !this.isEnabled) {
            return;
        }
        
        // Check level filtering
        if (levelObj.value > this.currentLevel.value) {
            return;
        }
        
        // Check category filtering
        if (this.filters.size > 0 && !this.filters.has(category.toUpperCase())) {
            return;
        }

        const timestamp = new Date().toLocaleTimeString();
        const entry = { timestamp, level, category, message, levelObj };
        
        // Add to entries array
        this.entries.push(entry);
        if (this.entries.length > this.maxEntries) {
            this.entries.shift(); // Remove oldest entry
        }

        // Console logging with object lookup (performance improvement)
        const consoleMessage = `[${levelObj.prefix}] [${category}] ${message}`;
        const consoleMethods = {
            'ERROR': console.error,
            'WARN': console.warn,
            'INFO': console.info
        };
        const consoleMethod = consoleMethods[level] || console.log;
        consoleMethod(consoleMessage);

        // Visual debug div
        this.updateDebugDiv(entry);
    }

    updateDebugDiv(entry) {
        if (!this.debugDiv) {
            this.debugDiv = this.createDebugDiv();
        }

        const entryDiv = document.createElement('div');
        entryDiv.style.cssText = `color: ${entry.levelObj.color}; margin-bottom: 2px; font-size: 11px; line-height: 1.2;`;
        
        // Create safe DOM elements instead of innerHTML to prevent XSS
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'u-text-gray';
        timestampSpan.textContent = `[${entry.timestamp}]`;
        
        const levelSpan = document.createElement('span');
        levelSpan.style.cssText = `color: ${entry.levelObj.color}; font-weight: bold;`;
        levelSpan.textContent = `[${entry.levelObj.prefix}]`;
        
        const categorySpan = document.createElement('span');
        categorySpan.className = 'u-text-light-gray';
        categorySpan.textContent = `[${entry.category}]`;
        
        const messageSpan = document.createElement('span');
        messageSpan.textContent = ` ${entry.message}`;
        
        entryDiv.appendChild(timestampSpan);
        entryDiv.appendChild(document.createTextNode(' '));
        entryDiv.appendChild(levelSpan);
        entryDiv.appendChild(document.createTextNode(' '));
        entryDiv.appendChild(categorySpan);
        entryDiv.appendChild(messageSpan);
        
        this.debugDiv.appendChild(entryDiv);
        
        // Auto-scroll to bottom
        this.debugDiv.scrollTop = this.debugDiv.scrollHeight;
        
        // Limit entries in DOM
        if (this.debugDiv.children.length > 200) {
            this.debugDiv.removeChild(this.debugDiv.firstChild);
        }
    }

    createDebugDiv() {
        const div = document.createElement('div');
        div.id = 'debug-output';
        div.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 450px;
            height: 300px;
            background: rgba(0, 0, 0, 0.95);
            color: #00ff00;
            padding: 10px;
            border: 2px solid #00ffff;
            border-radius: 8px;
            overflow-y: auto;
            z-index: 9999;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            -webkit-backdrop-filter: blur(10px);
            backdrop-filter: blur(10px);
            display: ${this.isEnabled ? 'block' : 'none'};
        `;
        
        // Add header with controls (secure DOM creation)
        const header = this.createHeaderElement();
        
        div.appendChild(header);
        document.body.appendChild(div);
        return div;
    }

    createHeaderElement() {
        const header = document.createElement('div');
        header.style.cssText = 'position: sticky; top: 0; background: rgba(0, 0, 0, 0.9); padding: 5px 0; border-bottom: 1px solid #00ffff; margin-bottom: 5px;';
        
        const headerContainer = document.createElement('div');
        headerContainer.style.cssText = 'display: flex; justify-content: space-between; align-items: center;';
        
        // Title
        const titleSpan = document.createElement('span');
        titleSpan.style.cssText = 'color: #00ffff; font-weight: bold;';
        titleSpan.textContent = 'Debug Console';
        
        // Button container
        const buttonContainer = document.createElement('div');
        
        // Clear button
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.style.cssText = 'background: none; border: 1px solid #00ffff; color: #00ffff; padding: 2px 6px; font-size: 10px; cursor: pointer;';
        clearButton.textContent = 'Clear';
        clearButton.addEventListener('click', () => this.clearEntries());
        
        // Close button
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.style.cssText = 'background: none; border: 1px solid #ff0040; color: #ff0040; padding: 2px 6px; font-size: 10px; cursor: pointer;';
        closeButton.textContent = '×';
        closeButton.addEventListener('click', () => this.toggle());
        
        buttonContainer.appendChild(clearButton);
        buttonContainer.appendChild(closeButton);
        
        headerContainer.appendChild(titleSpan);
        headerContainer.appendChild(buttonContainer);
        header.appendChild(headerContainer);
        
        return header;
    }

    clearEntries() {
        this.entries = [];
        if (this.debugDiv) {
            // Keep only the header
            const header = this.debugDiv.firstChild;
            this.debugDiv.textContent = ''; // Clear safely
            this.debugDiv.appendChild(header);
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+D toggles debug console
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.toggle();
            }
        });
    }

    savePreferences() {
        const prefs = {
            level: Object.keys(this.levels).find(key => this.levels[key] === this.currentLevel),
            filters: Array.from(this.filters),
            enabled: this.isEnabled
        };
        localStorage.setItem('cyberbackup_debug_prefs', JSON.stringify(prefs));
    }

    loadPreferences() {
        try {
            const saved = localStorage.getItem('cyberbackup_debug_prefs');
            if (saved) {
                const prefs = JSON.parse(saved);
                if (prefs.level && this.levels[prefs.level]) {
                    this.currentLevel = this.levels[prefs.level];
                }
                if (prefs.filters) {
                    this.filters = new Set(prefs.filters);
                }
                if (typeof prefs.enabled === 'boolean') {
                    this.isEnabled = prefs.enabled;
                }
            }
        } catch (error) {
            console.warn('Failed to load debug preferences:', error);
        }
    }

    getStatus() {
        return {
            level: Object.keys(this.levels).find(key => this.levels[key] === this.currentLevel),
            filters: Array.from(this.filters),
            enabled: this.isEnabled,
            entryCount: this.entries.length
        };
    }
}
class IntervalManager {
    constructor() {
        this.intervals = new Map();
        this.timeouts = new Map();
        
        // Add cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }
    
    set(name, callback, delay) {
        this.clear(name);
        const intervalId = setInterval(() => {
            try {
                callback();
            } catch (error) {
                console.error(`[IntervalManager] Error in interval '${name}':`, error);
                // Don't clear the interval automatically to prevent infinite error loops
            }
        }, delay);
        this.intervals.set(name, intervalId);
        debugLog(`Interval '${name}' set with ${delay}ms delay`, 'INTERVAL_MANAGER');
        return intervalId;
    }
    
    setTimeout(name, callback, delay) {
        this.clearTimeout(name);
        const timeoutId = setTimeout(() => {
            try {
                callback();
            } catch (error) {
                console.error(`[IntervalManager] Error in timeout '${name}':`, error);
            } finally {
                this.timeouts.delete(name); // Auto-cleanup completed timeouts
            }
        }, delay);
        this.timeouts.set(name, timeoutId);
        debugLog(`Timeout '${name}' set with ${delay}ms delay`, 'INTERVAL_MANAGER');
        return timeoutId;
    }
    
    clear(name) {
        if (this.intervals.has(name)) {
            clearInterval(this.intervals.get(name));
            this.intervals.delete(name);
            debugLog(`Interval '${name}' cleared`, 'INTERVAL_MANAGER');
            return true;
        }
        return false;
    }
    
    clearTimeout(name) {
        if (this.timeouts.has(name)) {
            clearTimeout(this.timeouts.get(name));
            this.timeouts.delete(name);
            debugLog(`Timeout '${name}' cleared`, 'INTERVAL_MANAGER');
            return true;
        }
        return false;
    }
    
    clearAll() {
        this.intervals.forEach((id, name) => {
            clearInterval(id);
            debugLog(`Clearing interval '${name}'`, 'INTERVAL_MANAGER');
        });
        this.timeouts.forEach((id, name) => {
            clearTimeout(id);
            debugLog(`Clearing timeout '${name}'`, 'INTERVAL_MANAGER');
        });
        this.intervals.clear();
        this.timeouts.clear();
        debugLog('All intervals and timeouts cleared', 'INTERVAL_MANAGER');
    }
    
    has(name) {
        return this.intervals.has(name) || this.timeouts.has(name);
    }
    
    getStats() {
        return {
            intervalCount: this.intervals.size,
            timeoutCount: this.timeouts.size,
            intervalNames: Array.from(this.intervals.keys()),
            timeoutNames: Array.from(this.timeouts.keys())
        };
    }
    
    cleanup() {
        debugLog('Performing cleanup...', 'INTERVAL_MANAGER');
        this.clearAll();
    }
}

// Create global instances using module pattern
const createGlobalInstances = () => {
    const logger = new DebugLogger();
    const logFn = (message, category = 'GENERAL') => logger.log('DEBUG', category, message);
    return { logger, logFn };
};

const { logger: debugLogger, logFn: debugLog } = createGlobalInstances();

// Export for module use
export { DebugLogger, IntervalManager, debugLogger, debugLog };
