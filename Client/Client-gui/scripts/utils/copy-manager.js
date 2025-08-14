class CopyManager {
    constructor() {
        this.copyTimeout = null;
    }

    /**
     * Copy text to clipboard with visual feedback
     * @param {string} text - Text to copy
     * @param {HTMLElement} button - Button element for visual feedback
     * @param {string} successMessage - Toast message on success
     */
    async copyToClipboard(text, button = null, successMessage = 'Copied to clipboard!') {
        try {
            // Use modern clipboard API if available
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers or non-secure contexts
                this.fallbackCopyToClipboard(text);
            }

            // Visual feedback on button
            if (button) {
                this.showCopyFeedback(button);
            }

            // Show success toast
            if (window.app && window.app.showToast) {
                window.app.showToast(successMessage, 'success', 2000);
            }

            return true;
        } catch (error) {
            console.error('Copy failed:', error);
            
            // Show error toast
            if (window.app && window.app.showToast) {
                window.app.showToast('Failed to copy to clipboard', 'error', 3000);
            }
            
            return false;
        }
    }

    /**
     * Fallback copy method for older browsers
     */
    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
        } finally {
            document.body.removeChild(textArea);
        }
    }

    /**
     * Show visual feedback on copy button
     */
    showCopyFeedback(button) {
        if (!button) {
            return;
        }

        // Clear any existing timeout
        if (this.copyTimeout) {
            clearTimeout(this.copyTimeout);
        }

        // Add copied class for animation
        button.classList.add('copied');

        // Remove class after animation
        this.copyTimeout = setTimeout(() => {
            button.classList.remove('copied');
        }, 1500);
    }

    /**
     * Create a copy button element
     * @param {string} text - Text to copy when clicked
     * @param {string} tooltip - Tooltip text
     * @returns {HTMLElement} Copy button element
     */
    createCopyButton(text, tooltip = 'Copy to clipboard') {
        const button = document.createElement('button');
        button.className = 'copy-btn';
        button.innerHTML = '📋';
        button.title = tooltip;
        button.setAttribute('aria-label', tooltip);
        
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            await this.copyToClipboard(text, button);
        });

        return button;
    }

    /**
     * Add copy functionality to an existing element
     * @param {HTMLElement} element - Element to make copyable
     * @param {string} text - Text to copy (optional, uses element text if not provided)
     * @param {string} position - Where to place the copy button ('after', 'before', 'inside')
     */
    makeCopyable(element, text = null, position = 'after') {
        if (!element) {
            return null;
        }

        const textToCopy = text || element.textContent.trim();
        const copyButton = this.createCopyButton(textToCopy);

        switch (position) {
            case 'before':
                element.parentNode.insertBefore(copyButton, element);
                break;
            case 'inside':
                element.appendChild(copyButton);
                break;
            case 'after':
            default:
                element.parentNode.insertBefore(copyButton, element.nextSibling);
                break;
        }

        return copyButton;
    }

    /**
     * Create a copy container with text and copy button
     * @param {string} text - Text to display and copy
     * @param {string} className - Additional CSS class for the container
     */
    createCopyContainer(text, className = '') {
        const container = document.createElement('div');
        container.className = `copy-container ${className}`.trim();

        const content = document.createElement('span');
        content.className = 'copy-content';
        content.textContent = text;

        const copyButton = this.createCopyButton(text);

        container.appendChild(content);
        container.appendChild(copyButton);

        return container;
    }
}

export { CopyManager };