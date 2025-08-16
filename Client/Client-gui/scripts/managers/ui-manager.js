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

class TooltipManager {
    constructor() {
        this.tooltip = null;
        this.hideTimeout = null;
        this.showDelay = 500; // ms delay before showing tooltip
        this.hideDelay = 100; // ms delay before hiding tooltip
        this.isVisible = false;
        
        this.createTooltip();
        this.setupGlobalListeners();
    }

    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'enhanced-tooltip';
        this.tooltip.style.cssText = `
            position: absolute;
            background: var(--surface-08);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: var(--space-12);
            font-size: 0.875rem;
            line-height: 1.4;
            color: var(--text-primary);
            z-index: 3000;
            pointer-events: none;
            opacity: 0;
            transform: translateY(5px);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            max-width: 300px;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: var(--md-elevation-8);
        `;
        document.body.appendChild(this.tooltip);
    }

    setupGlobalListeners() {
        // Handle elements with data-tooltip attribute
        document.addEventListener('mouseover', (e) => {
            const tooltipElement = e.target.closest('[data-tooltip]');
            if (tooltipElement) {
                this.show(tooltipElement, tooltipElement.dataset.tooltip);
            }
        });

        document.addEventListener('mouseout', (e) => {
            const tooltipElement = e.target.closest('[data-tooltip]');
            if (tooltipElement) {
                this.hide();
            }
        });

        // Handle file elements specifically
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest('.file-preview-container, .file-item, .cyber-btn')) {
                this.handleFileTooltip(e);
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (e.target.closest('.file-preview-container, .file-item, .cyber-btn')) {
                this.hide();
            }
        });
    }

    handleFileTooltip(event) {
        const fileElement = event.target.closest('.file-preview-container, .file-item');
        const buttonElement = event.target.closest('.cyber-btn');
        
        if (fileElement) {
            this.showFileTooltip(fileElement, event);
        } else if (buttonElement) {
            this.showButtonTooltip(buttonElement, event);
        }
    }

    showFileTooltip(fileElement, event) {
        // Try to get file data from the element
        const fileName = fileElement.querySelector('.file-name')?.textContent ||
                        fileElement.dataset.fileName || 'Unknown file';
        const fileSize = fileElement.dataset.fileSize || 
                        fileElement.querySelector('.file-size')?.textContent;
        const fileType = fileElement.dataset.fileType || 
                        fileElement.querySelector('.file-type')?.textContent;
        const lastModified = fileElement.dataset.lastModified;

        // Create rich tooltip content
        const content = this.createFileTooltipContent(fileName, fileSize, fileType, lastModified);
        this.show(fileElement, content, event);
    }

    showButtonTooltip(buttonElement, event) {
        // Enhanced button tooltips with operation context
        const buttonText = buttonElement.querySelector('.btn-text')?.textContent || 
                          buttonElement.textContent.trim();
        const isDisabled = buttonElement.disabled;
        const isLoading = buttonElement.classList.contains('loading');
        
        let content = buttonText;
        
        // Add contextual information
        if (isDisabled) {
            content += '<br><span style="color: var(--text-secondary);">Currently unavailable</span>';
        } else if (isLoading) {
            content += '<br><span style="color: var(--neon-blue);">Operation in progress...</span>';
        }

        // Add keyboard shortcuts if available
        const shortcut = this.getKeyboardShortcut(buttonElement);
        if (shortcut) {
            content += `<br><span style="color: var(--text-dim); font-size: 0.75rem;">Shortcut: ${shortcut}</span>`;
        }

        this.show(buttonElement, content, event);
    }

    getKeyboardShortcut(buttonElement) {
        // Map common button IDs/classes to keyboard shortcuts
        const shortcuts = {
            'startBackupBtn': 'Ctrl+B',
            'pauseBtn': 'Ctrl+P', 
            'stopBtn': 'Ctrl+T',
            'connectBtn': 'Ctrl+Enter'
        };
        
        return shortcuts[buttonElement.id] || null;
    }

    createFileTooltipContent(fileName, fileSize, fileType, lastModified) {
        let content = `<div class="tooltip-file-info">`;
        
        // File name (truncated if too long)
        const displayName = fileName.length > 30 ? fileName.substring(0, 27) + '...' : fileName;
        content += `<div class="tooltip-file-name">${displayName}</div>`;
        
        // File details grid
        content += `<div class="tooltip-details">`;
        
        if (fileSize) {
            content += `<div class="tooltip-detail">
                <span class="tooltip-label">Size:</span>
                <span class="tooltip-value">${this.formatFileSize(fileSize)}</span>
            </div>`;
        }
        
        if (fileType) {
            content += `<div class="tooltip-detail">
                <span class="tooltip-label">Type:</span>
                <span class="tooltip-value">${fileType}</span>
            </div>`;
        }
        
        if (lastModified) {
            const date = new Date(lastModified);
            content += `<div class="tooltip-detail">
                <span class="tooltip-label">Modified:</span>
                <span class="tooltip-value">${date.toLocaleDateString()}</span>
            </div>`;
        }
        
        content += `</div></div>`;
        return content;
    }

    formatFileSize(size) {
        // If it's already formatted, return as-is
        if (typeof size === 'string' && (size.includes('B') || size.includes('bytes'))) {
            return size;
        }
        
        // Convert bytes to human readable
        const bytes = parseInt(size);
        if (isNaN(bytes)) return size;
        
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let unitIndex = 0;
        let value = bytes;
        
        while (value >= 1024 && unitIndex < units.length - 1) {
            value /= 1024;
            unitIndex++;
        }
        
        return `${value.toFixed(unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
    }

    show(element, content, event = null) {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }

        // Set content
        this.tooltip.innerHTML = content;
        
        // Position tooltip
        this.positionTooltip(element, event);
        
        // Show with delay
        this.showTimeout = setTimeout(() => {
            this.tooltip.style.opacity = '1';
            this.tooltip.style.transform = 'translateY(0)';
            this.isVisible = true;
        }, this.showDelay);
    }

    positionTooltip(element, event) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        const viewport = {
            width: window.innerWidth,
            height: window.innerHeight
        };
        
        let top, left;
        
        if (event) {
            // Position near mouse cursor
            left = event.clientX + 10;
            top = event.clientY + 10;
        } else {
            // Position relative to element
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
            top = rect.bottom + 8;
        }
        
        // Adjust if tooltip would go off-screen
        if (left + tooltipRect.width > viewport.width - 10) {
            left = viewport.width - tooltipRect.width - 10;
        }
        if (left < 10) {
            left = 10;
        }
        
        if (top + tooltipRect.height > viewport.height - 10) {
            top = rect.top - tooltipRect.height - 8;
        }
        
        this.tooltip.style.left = `${left}px`;
        this.tooltip.style.top = `${top}px`;
    }

    hide() {
        if (this.showTimeout) {
            clearTimeout(this.showTimeout);
            this.showTimeout = null;
        }
        
        this.hideTimeout = setTimeout(() => {
            this.tooltip.style.opacity = '0';
            this.tooltip.style.transform = 'translateY(5px)';
            this.isVisible = false;
        }, this.hideDelay);
    }

    // Public method to add tooltip to any element
    addTooltip(element, content) {
        element.dataset.tooltip = content;
    }

    // Public method to add file tooltip data
    addFileTooltip(element, fileData) {
        if (fileData.name) element.dataset.fileName = fileData.name;
        if (fileData.size) element.dataset.fileSize = fileData.size;
        if (fileData.type) element.dataset.fileType = fileData.type;
        if (fileData.lastModified) element.dataset.lastModified = fileData.lastModified;
    }
}

class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = new Map(); // Track active toasts
        this.maxToasts = 5; // Maximum visible toasts
        this.defaultDuration = 3000;
        this.touchStartY = null;
        this.touchStartX = null;
        
        this.initializeContainer();
    }

    initializeContainer() {
        this.container = document.getElementById('toastContainer');
        if (!this.container) {
            console.warn('[ToastManager] Toast container not found, creating fallback');
            this.container = document.createElement('div');
            this.container.id = 'toastContainer';
            this.container.className = 'toast-container';
            this.container.setAttribute('role', 'status');
            this.container.setAttribute('aria-live', 'polite');
            document.body.appendChild(this.container);
        }
    }

    show(message, type = 'info', duration = null) {
        if (!message) return null;

        // Use default duration if not specified
        if (duration === null) {
            duration = type === 'error' ? 5000 : this.defaultDuration;
        }

        // Create unique toast ID
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Limit number of visible toasts
        this.enforceMaxToasts();

        const toast = this.createToastElement(message, type, toastId);
        this.container.prepend(toast); // Add to top

        // Store toast reference
        this.toasts.set(toastId, {
            element: toast,
            type,
            duration,
            createdAt: Date.now()
        });

        // Setup interactions
        this.setupToastInteractions(toast, toastId);

        // Auto-dismiss if duration > 0
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(toastId);
            }, duration);
        }

        // Focus management for accessibility
        if (type === 'error') {
            setTimeout(() => toast.focus(), 100);
        }

        return toastId;
    }

    createToastElement(message, type, toastId) {
        const toast = document.createElement('div');
        toast.className = `toast toast-enhanced ${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        toast.setAttribute('tabindex', '-1');
        toast.setAttribute('data-toast-id', toastId);

        // Type-specific icons and colors
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon" aria-hidden="true">${icons[type] || icons.info}</span>
                <span class="toast-message">${message}</span>
                <button type="button" class="toast-close" aria-label="Close notification" tabindex="0">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;

        // Add CSS for proper styling and animations
        toast.style.cssText = `
            position: relative;
            margin-bottom: var(--space-xs, 8px);
            border-radius: var(--radius-md, 8px);
            overflow: hidden;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            touch-action: pan-x;
        `;

        // Trigger animation after DOM insertion
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 10);

        return toast;
    }

    setupToastInteractions(toast, toastId) {
        const closeButton = toast.querySelector('.toast-close');
        
        // Click to close
        closeButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.dismiss(toastId);
        });

        // Keyboard accessibility
        toast.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.dismiss(toastId);
            }
        });

        // Mobile swipe to dismiss
        this.setupSwipeGestures(toast, toastId);

        // Hover to pause auto-dismiss
        let isHovered = false;
        toast.addEventListener('mouseenter', () => {
            isHovered = true;
            toast.style.animationPlayState = 'paused';
        });

        toast.addEventListener('mouseleave', () => {
            isHovered = false;
            toast.style.animationPlayState = 'running';
        });
    }

    setupSwipeGestures(toast, toastId) {
        let startX = null;
        let startY = null;
        let currentX = null;
        let isDragging = false;

        const handleTouchStart = (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            toast.style.transition = 'none';
        };

        const handleTouchMove = (e) => {
            if (!startX || !startY) return;

            currentX = e.touches[0].clientX;
            const currentY = e.touches[0].clientY;
            
            const diffX = currentX - startX;
            const diffY = currentY - startY;

            // Only handle horizontal swipes (and primarily right swipes)
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 10) {
                isDragging = true;
                e.preventDefault();
                
                // Only allow right swipe (dismiss)
                if (diffX > 0) {
                    const progress = Math.min(diffX / 200, 1);
                    toast.style.transform = `translateX(${diffX}px)`;
                    toast.style.opacity = 1 - progress * 0.7;
                }
            }
        };

        const handleTouchEnd = (e) => {
            if (!isDragging) {
                toast.style.transition = '';
                return;
            }

            const diffX = currentX - startX;
            toast.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

            // Dismiss if swiped far enough
            if (diffX > 100) {
                this.dismiss(toastId);
            } else {
                // Snap back
                toast.style.transform = 'translateX(0)';
                toast.style.opacity = '1';
            }

            // Reset
            startX = null;
            startY = null;
            currentX = null;
            isDragging = false;
        };

        toast.addEventListener('touchstart', handleTouchStart, { passive: true });
        toast.addEventListener('touchmove', handleTouchMove, { passive: false });
        toast.addEventListener('touchend', handleTouchEnd, { passive: true });
    }

    dismiss(toastId) {
        const toastData = this.toasts.get(toastId);
        if (!toastData) return;

        const toast = toastData.element;
        
        // Animate out
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.maxHeight = '0';
        toast.style.marginBottom = '0';
        toast.style.padding = '0';

        // Remove from DOM after animation
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
            this.toasts.delete(toastId);
        }, 300);
    }

    dismissAll() {
        Array.from(this.toasts.keys()).forEach(toastId => {
            this.dismiss(toastId);
        });
    }

    dismissByType(type) {
        this.toasts.forEach((toastData, toastId) => {
            if (toastData.type === type) {
                this.dismiss(toastId);
            }
        });
    }

    enforceMaxToasts() {
        if (this.toasts.size >= this.maxToasts) {
            // Remove oldest toast
            const oldestToastId = Array.from(this.toasts.keys())[0];
            this.dismiss(oldestToastId);
        }
    }

    // Convenience methods
    success(message, duration = null) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = null) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = null) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = null) {
        return this.show(message, 'info', duration);
    }

    // Get stats for debugging
    getStats() {
        return {
            activeToasts: this.toasts.size,
            maxToasts: this.maxToasts,
            toastIds: Array.from(this.toasts.keys())
        };
    }
}

export { NotificationManager, ModalManager, ConfirmModalManager, ThemeManager, ButtonStateManager, TooltipManager, ToastManager };