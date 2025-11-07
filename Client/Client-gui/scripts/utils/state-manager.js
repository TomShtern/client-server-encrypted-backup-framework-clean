/**
 * Generic State Manager for Web GUI
 * Provides a unified pattern for localStorage-based state management
 * across different UI components (ThemeManager, ButtonStateManager, etc.)
 */

import { debugLog } from '../core/debug-utils.js';

export class StateManager {
    constructor(storageKey, defaultState = {}) {
        this.storageKey = storageKey;
        this.defaultState = defaultState;
        this.state = Object.freeze(this.load() || { ...defaultState });
        this.listeners = new Map(); // Event listeners for state changes
    }

    /**
     * Load state from localStorage
     * @returns {Object|null} Loaded state or null if failed
     */
    load() {
        try {
            const data = localStorage.getItem(this.storageKey);
            if (!data) return null;

            const parsed = JSON.parse(data);

            // Validate structure
            if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
                console.error(`Invalid state structure for ${this.storageKey}`);
                return null;
            }

            // Check for prototype pollution attempts
            if ('__proto__' in parsed || 'constructor' in parsed || 'prototype' in parsed) {
                console.error(`Prototype pollution attempt detected in ${this.storageKey}`);
                return null;
            }

            debugLog(`State loaded for ${this.storageKey}:`, parsed);
            return parsed;
        } catch (error) {
            console.error(`Failed to load state for ${this.storageKey}:`, error);
            return null;
        }
    }

    /**
     * Save current state to localStorage
     * @returns {boolean} Success status
     */
    save() {
        try {
            const serialized = JSON.stringify(this.state);
            const sizeKB = new Blob([serialized]).size / 1024;

            // Enforce 500KB limit per state manager
            if (sizeKB > 500) {
                console.error(`State too large for ${this.storageKey}: ${sizeKB.toFixed(1)}KB exceeds 500KB limit`);
                return false;
            }

            localStorage.setItem(this.storageKey, serialized);
            debugLog(`State saved for ${this.storageKey}: ${sizeKB.toFixed(1)}KB`);
            return true;
        } catch (error) {
            console.error(`Failed to save state for ${this.storageKey}:`, error);
            return false;
        }
    }

    /**
     * Update state with new values
     * @param {Object} updates - Key-value pairs to update
     * @returns {boolean} Success status
     */
    update(updates) {
        const oldState = this.state;
        // Create new frozen object
        this.state = Object.freeze({ ...this.state, ...updates });

        const success = this.save();
        if (success) {
            this.notifyListeners(oldState, this.state, updates);
        }

        return success;
    }

    /**
     * Get a specific value from state
     * @param {string} key - State key
     * @param {*} defaultValue - Default value if key not found
     * @returns {*} State value
     */
    get(key, defaultValue = null) {
        return this.state[key] !== undefined ? this.state[key] : defaultValue;
    }

    /**
     * Set a specific value in state
     * @param {string} key - State key
     * @param {*} value - New value
     * @returns {boolean} Success status
     */
    set(key, value) {
        return this.update({ [key]: value });
    }

    /**
     * Delete a key from state
     * @param {string} key - Key to delete
     * @returns {boolean} Success status
     */
    delete(key) {
        if (key in this.state) {
            const oldState = { ...this.state };
            delete this.state[key];
            const success = this.save();
            if (success) {
                this.notifyListeners(oldState, this.state, { [key]: undefined });
            }
            return success;
        }
        return true; // Key doesn't exist, consider it successful
    }

    /**
     * Reset state to default values
     * @returns {boolean} Success status
     */
    reset() {
        const oldState = { ...this.state };
        this.state = { ...this.defaultState };
        const success = this.save();
        if (success) {
            this.notifyListeners(oldState, this.state, null); // null indicates full reset
        }
        return success;
    }

    /**
     * Clear all state and remove from localStorage
     */
    clear() {
        const oldState = { ...this.state };
        this.state = {};
        localStorage.removeItem(this.storageKey);
        this.notifyListeners(oldState, this.state, null); // null indicates clear
        debugLog(`State cleared for ${this.storageKey}`);
    }

    /**
     * Get entire state object
     * @returns {Object} Current state
     */
    getState() {
        return this.state; // Already frozen, safe to return directly
    }

    /**
     * Check if state has a specific key
     * @param {string} key - Key to check
     * @returns {boolean} True if key exists
     */
    has(key) {
        return key in this.state;
    }

    /**
     * Get state keys
     * @returns {Array<string>} Array of state keys
     */
    keys() {
        return Object.keys(this.state);
    }

    /**
     * Get state size (number of keys)
     * @returns {number} Number of keys in state
     */
    size() {
        return Object.keys(this.state).length;
    }

    /**
     * Subscribe to state changes
     * @param {Function} listener - Callback function (oldState, newState, changes)
     * @returns {Function} Unsubscribe function
     */
    subscribe(listener) {
        const MAX_LISTENERS = 50;

        if (this.listeners.size >= MAX_LISTENERS) {
            console.warn(`Maximum listeners (${MAX_LISTENERS}) reached for ${this.storageKey}`);
            return () => {}; // No-op unsubscribe
        }

        const id = Symbol('listener');
        this.listeners.set(id, listener);

        // Return unsubscribe function
        return () => {
            this.listeners.delete(id);
        };
    }

    /**
     * Notify all listeners of state change
     * @param {Object} oldState - Previous state
     * @param {Object} newState - New state
     * @param {Object|null} changes - Specific changes or null for full reset
     */
    notifyListeners(oldState, newState, changes) {
        this.listeners.forEach((listener, id) => {
            try {
                listener(oldState, newState, changes);
            } catch (error) {
                console.error(`State listener ${String(id)} failed:`, error);
            }
        });
    }

    /**
     * Create a backup of current state
     * @returns {string} Backup JSON string
     */
    backup() {
        return JSON.stringify({
            version: this.version || 1, // Add version field
            timestamp: Date.now(),
            storageKey: this.storageKey,
            state: this.state
        });
    }

    /**
     * Restore state from backup
     * @param {string} backupJson - Backup JSON string
     * @returns {boolean} Success status
     */
    restore(backupJson) {
        try {
            const backup = JSON.parse(backupJson);

            // NEW: Version validation
            const currentVersion = this.version || 1;
            if (backup.version !== currentVersion) {
                throw new Error(
                    `Version mismatch: backup is v${backup.version}, current is v${currentVersion}`
                );
            }

            if (backup.storageKey !== this.storageKey) {
                throw new Error('Backup storage key mismatch');
            }

            const oldState = this.state;
            this.state = Object.freeze({ ...backup.state });
            const success = this.save();
            if (success) {
                this.notifyListeners(oldState, this.state, null); // null indicates restore
                debugLog(`State restored for ${this.storageKey} from backup`);
            }
            return success;
        } catch (error) {
            console.error(`Failed to restore state for ${this.storageKey}:`, error);
            return false;
        }
    }

    /**
     * Get debug information
     * @returns {Object} Debug info
     */
    getDebugInfo() {
        return {
            storageKey: this.storageKey,
            stateSize: this.size(),
            listenerCount: this.listeners.size,
            hasData: this.size() > 0,
            lastUpdated: localStorage.getItem(`${this.storageKey}_lastUpdated`) || null
        };
    }
}

/**
 * Enhanced StateManager with auto-save and persistence features
 */
export class PersistentStateManager extends StateManager {
    constructor(storageKey, defaultState = {}, options = {}) {
        super(storageKey, defaultState);

        this.autoSave = options.autoSave !== false; // Default true
        this.debounceMs = options.debounceMs || 300;
        this.saveTimeout = null;
        this.version = options.version || 1;

        // Track last save time
        this.updateLastSaved();
    }

    /**
     * Update with debounced auto-save
     * @param {Object} updates - Key-value pairs to update
     * @returns {Promise<boolean>} Success status
     */
    async update(updates) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...updates };

        let success;
        if (this.autoSave) {
            // Wait for debounced save to complete
            success = await this.debounceSaveAsync();
        } else {
            success = this.save();
        }

        // Only notify listeners after successful save
        if (success) {
            this.notifyListeners(oldState, this.state, updates);
        }

        return success;
    }

    /**
     * Debounced save with async completion
     * @returns {Promise<boolean>} Save success status
     */
    debounceSaveAsync() {
        return new Promise((resolve) => {
            if (this.saveTimeout) {
                clearTimeout(this.saveTimeout);
            }

            this.saveTimeout = setTimeout(() => {
                const success = this.save();
                this.updateLastSaved();
                resolve(success);
            }, this.debounceMs);
        });
    }

    /**
     * Debounced save to prevent excessive localStorage writes
     */
    debounceSave() {
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }

        this.saveTimeout = setTimeout(() => {
            this.save();
            this.updateLastSaved();
        }, this.debounceMs);
    }

    /**
     * Force immediate save
     * @returns {boolean} Success status
     */
    forceSave() {
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
            this.saveTimeout = null;
        }
        const success = this.save();
        if (success) {
            this.updateLastSaved();
        }
        return success;
    }

    /**
     * Update last saved timestamp
     */
    updateLastSaved() {
        try {
            localStorage.setItem(`${this.storageKey}_lastUpdated`, Date.now().toString());
        } catch (error) {
            console.warn(`Failed to update last saved time for ${this.storageKey}:`, error);
        }
    }

    /**
     * Get last saved timestamp
     * @returns {number|null} Timestamp or null
     */
    getLastSaved() {
        const timestamp = localStorage.getItem(`${this.storageKey}_lastUpdated`);
        return timestamp ? parseInt(timestamp, 10) : null;
    }

    /**
     * Check if state is stale (older than specified minutes)
     * @param {number} maxAgeMinutes - Maximum age in minutes
     * @returns {boolean} True if stale
     */
    isStale(maxAgeMinutes = 60) {
        const lastSaved = this.getLastSaved();
        if (!lastSaved) return true;

        const maxAge = maxAgeMinutes * 60 * 1000;
        return (Date.now() - lastSaved) > maxAge;
    }

    /**
     * Save with version information
     * @returns {boolean} Success status
     */
    save() {
        try {
            const data = {
                version: this.version,
                timestamp: Date.now(),
                state: this.state
            };
            localStorage.setItem(this.storageKey, JSON.stringify(data));
            debugLog(`Persistent state saved for ${this.storageKey} (v${this.version})`);
            return true;
        } catch (error) {
            console.error(`Failed to save persistent state for ${this.storageKey}:`, error);
            return false;
        }
    }

    /**
     * Load with version checking
     * @returns {Object|null} Loaded state or null
     */
    load() {
        try {
            const data = localStorage.getItem(this.storageKey);
            if (!data) return null;

            const parsed = JSON.parse(data);

            // Handle both versioned and legacy data
            if (parsed.version && parsed.state) {
                debugLog(`Versioned state loaded for ${this.storageKey} (v${parsed.version})`);
                return parsed.state;
            } else {
                // Legacy data without version
                debugLog(`Legacy state loaded for ${this.storageKey}`);
                return parsed;
            }
        } catch (error) {
            console.error(`Failed to load persistent state for ${this.storageKey}:`, error);
            return null;
        }
    }
}

// Export factory functions for common use cases
export function createStateManager(storageKey, defaultState = {}) {
    return new StateManager(storageKey, defaultState);
}

export function createPersistentStateManager(storageKey, defaultState = {}, options = {}) {
    return new PersistentStateManager(storageKey, defaultState, options);
}

// Pre-configured managers for common CyberBackup state types
export const CyberBackupStateManager = {
    /**
     * Create theme state manager
     */
    createThemeManager() {
        return new PersistentStateManager('cyberbackup_theme', {
            mode: 'cyberpunk',
            customColors: {},
            animations: true
        }, {
            debounceMs: 100,
            version: 1
        });
    },

    /**
     * Create button state manager
     */
    createButtonStateManager() {
        return new StateManager('cyberbackup_button_states', {});
    },

    /**
     * Create backup settings manager
     */
    createBackupSettingsManager() {
        return new PersistentStateManager('cyberbackup_backup_settings', {
            autoBackup: false,
            interval: 24,
            compression: true,
            encryption: true
        }, {
            debounceMs: 500,
            version: 1
        });
    },

    /**
     * Create user preferences manager
     */
    createUserPreferencesManager() {
        return new PersistentStateManager('cyberbackup_user_preferences', {
            language: 'en',
            notifications: true,
            autoConnect: false,
            debugMode: false
        }, {
            debounceMs: 300,
            version: 1
        });
    }
};