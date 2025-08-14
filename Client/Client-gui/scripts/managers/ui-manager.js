import { debugLog } from '../core/debug-utils.js';

class NotificationManager {
    constructor() {
        if (!('Notification' in window)) {
            debugLog('Browser does not support notifications.', 'NOTIFICATIONS');
        }
    }

    async requestPermission() {
        if (!('Notification' in window)) {
            return;
        }
        const permission = await Notification.requestPermission();
        debugLog(`Notification permission: ${permission}`, 'NOTIFICATIONS');
        return permission;
    }

    show(title, body, options = {}) {
        if (!('Notification' in window) || Notification.permission !== 'granted') {
            debugLog('Notification permission not granted or not supported.', 'NOTIFICATIONS');
            return;
        }
        const notification = new Notification(title, { body, ...options });
        debugLog(`Notification shown: ${title} - ${body}`, 'NOTIFICATIONS');
        return notification;
    }
}

class ModalManager {
    constructor() {
        // Get elements directly from DOM - no circular dependency
        this.modalOverlay = document.getElementById('confirmModal');
        this.modalTitle = document.getElementById('confirmTitle');
        this.modalMessage = document.getElementById('confirmMessage');
        this.confirmOkBtn = document.getElementById('confirmOkBtn');
        this.cancelBtn = document.getElementById('cancelModalBtn');

        this.resolve = null;
        this.reject = null;

        if (this.cancelBtn) {
            this.cancelBtn.addEventListener('click', () => this.hide());
        }
        if (this.modalOverlay) {
            this.modalOverlay.addEventListener('click', (e) => {
                if (e.target === this.modalOverlay) {
                    this.hide();
                }
            });
        }
    }

    show(title, message, onConfirm) {
        this.modalTitle.textContent = title;
        this.modalMessage.textContent = message;
        this.confirmOkBtn.onclick = () => {
            onConfirm();
            this.hide();
        };
        this.modalOverlay.classList.add('show');
    }

    hide() {
        this.modalOverlay.classList.remove('show');
    }
}

class ConfirmModalManager extends ModalManager {
    constructor() {
        super();
        // Override the parent event listeners for promise-based flow
        if (this.confirmOkBtn) {
            this.confirmOkBtn.onclick = null; // Clear any existing onclick
            this.confirmOkBtn.addEventListener('click', () => {
                if (this.resolve) {
                    this.resolve(true);
                }
                this.hide();
            });
        }
        if (this.cancelBtn) {
            this.cancelBtn.onclick = null; // Clear any existing onclick
            this.cancelBtn.addEventListener('click', () => {
                if (this.resolve) {
                    this.resolve(false);
                }
                this.hide();
            });
        }
    }

    async confirm(title, message) {
        this.modalTitle.textContent = title;
        this.modalMessage.textContent = message;
        this.modalOverlay.classList.add('show');
        return new Promise((resolve, reject) => {
            this.resolve = resolve;
            this.reject = reject;
        });
    }
}

class ThemeManager {
    constructor() {
        this.currentTheme = 'cyberpunk';
        this.themes = {
            cyberpunk: 'cyberpunk',
            dark: 'dark', 
            matrix: 'matrix'
        };
    }
    
    loadSavedTheme() {
        try {
            const savedTheme = localStorage.getItem('cyberbackup_theme');
            if (savedTheme && this.themes[savedTheme]) {
                this.setTheme(savedTheme);
            }
        } catch (error) {
            console.warn('Failed to load saved theme:', error);
        }
    }
    
    setTheme(theme) {
        if (this.themes[theme]) {
            this.currentTheme = theme;
            document.body.className = theme;
            try {
                localStorage.setItem('cyberbackup_theme', theme);
            } catch (error) {
                console.warn('Failed to save theme:', error);
            }
            console.log('Theme set to:', theme);
        }
    }
}
class ButtonStateManager {
    constructor() {
        this.activeButtons = new Map();
        this.originalStates = new Map();
    }

    setLoading(button, loadingText = null) {
        if (!button) {
            return;
        }
        
        const buttonId = button.id || button.textContent.trim();
        
        // Store original state
        if (!this.originalStates.has(buttonId)) {
            const iconSpan = button.querySelector('.btn-icon');
            const textSpan = button.querySelector('.btn-text');
            this.originalStates.set(buttonId, {
                icon: iconSpan ? iconSpan.textContent : '',
                text: textSpan ? textSpan.textContent : button.textContent,
                disabled: button.disabled,
                classList: Array.from(button.classList)
            });
        }

        // Apply loading state
        button.classList.add('loading');
        button.disabled = true;

        if (loadingText) {
            this.updateButtonText(button, loadingText);
        }

        this.activeButtons.set(buttonId, button);
        debugLog(`Button ${buttonId} set to loading state`, 'BUTTON_STATE');
    }

    setSuccess(button, successText = null, duration = 2000) {
        if (!button) {
            return;
        }
        
        const buttonId = button.id || this.originalStates.get(button.id)?.text || 'unknown';
        
        // Remove loading state
        button.classList.remove('loading');
        button.classList.add('success-flash');
        
        if (successText) {
            this.updateButtonText(button, successText);
        }

        // Add status indicator
        this.addStatusIndicator(button, 'success');

        // Reset after duration
        setTimeout(() => {
            this.reset(button);
        }, duration);

        debugLog(`Button ${buttonId} set to success state`, 'BUTTON_STATE');
    }

    setError(button, errorText = null, duration = 3000) {
        if (!button) {
            return;
        }
        
        const buttonId = button.id || this.originalStates.get(button.id)?.text || 'unknown';
        
        // Remove loading state
        button.classList.remove('loading');
        button.classList.add('error-shake');
        
        if (errorText) {
            this.updateButtonText(button, errorText);
        }

        // Add status indicator
        this.addStatusIndicator(button, 'error');

        // Reset after duration
        setTimeout(() => {
            this.reset(button);
            button.classList.remove('error-shake');
        }, duration);

        debugLog(`Button ${buttonId} set to error state`, 'BUTTON_STATE');
    }

    reset(button) {
        if (!button) {
            return;
        }
        
        const buttonId = button.id || button.textContent.trim();
        const originalState = this.originalStates.get(buttonId);
        
        if (originalState) {
            // Restore original state
            const iconSpan = button.querySelector('.btn-icon');
            const textSpan = button.querySelector('.btn-text');

            if (iconSpan && textSpan) {
                iconSpan.textContent = originalState.icon;
                textSpan.textContent = originalState.text;
            } else if (originalState.icon) {
                // Fallback: recreate structure or use plain text
                button.innerHTML = `<span class="btn-icon">${originalState.icon}</span><span class="btn-text">${originalState.text}</span>`;
            } else {
                button.textContent = originalState.text;
            }

            button.disabled = originalState.disabled;
            button.className = originalState.classList.join(' ');

            // Remove any status indicators
            this.removeStatusIndicator(button);

            this.originalStates.delete(buttonId);
        }
        
        this.activeButtons.delete(buttonId);
        debugLog(`Button ${buttonId} reset to original state`, 'BUTTON_STATE');
    }

    updateButtonText(button, text) {
        // Safely update button text while preserving span structure
        const textSpan = button.querySelector('.btn-text');
        if (textSpan) {
            textSpan.textContent = text;
        } else {
            // Fallback for buttons without span structure
            button.textContent = text;
        }
    }

    addStatusIndicator(button, type) {
        this.removeStatusIndicator(button); // Remove existing indicator
        
        const indicator = document.createElement('div');
        indicator.className = `status-indicator ${type}`;
        indicator.setAttribute('data-button-status', 'true');
        
        button.classList.add('has-status');
        button.appendChild(indicator);
    }

    removeStatusIndicator(button) {
        const existing = button.querySelector('[data-button-status]');
        if (existing) {
            existing.remove();
        }
        button.classList.remove('has-status');
    }

    isLoading(button) {
        return button && button.classList.contains('loading');
    }

    // Batch operations
    setMultipleLoading(buttons, loadingText = null) {
        buttons.forEach(button => this.setLoading(button, loadingText));
    }

    resetMultiple(buttons) {
        buttons.forEach(button => this.reset(button));
    }

    // Clean up all states
    resetAll() {
        this.activeButtons.forEach(button => this.reset(button));
        this.activeButtons.clear();
        this.originalStates.clear();
        debugLog('All button states reset', 'BUTTON_STATE');
    }

    // Get stats for debugging
    getStats() {
        return {
            activeButtons: this.activeButtons.size,
            storedStates: this.originalStates.size,
            buttonIds: Array.from(this.activeButtons.keys())
        };
    }
}

export { NotificationManager, ModalManager, ConfirmModalManager, ThemeManager, ButtonStateManager };