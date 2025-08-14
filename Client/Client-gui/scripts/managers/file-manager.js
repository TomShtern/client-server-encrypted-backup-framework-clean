import { debugLog } from '../core/debug-utils.js';

class FileManager {
    constructor() {
        this.supportsFileSystemAccess = 'showOpenFilePicker' in window;
        debugLog(`File System Access API supported: ${this.supportsFileSystemAccess}`, 'FILE_MANAGER');
        
        // File validation settings
        this.maxFileSize = 5 * 1024 * 1024 * 1024; // 5GB default
        this.allowedTypes = new Set([
            // Documents
            'application/pdf', 'text/plain', 'text/csv', 'application/json',
            'application/xml', 'text/xml', 'application/rtf',
            
            // Microsoft Office
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            
            // Images
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml',
            'image/tiff', 'image/ico',
            
            // Audio
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3', 'audio/flac', 'audio/aac',
            
            // Video
            'video/mp4', 'video/webm', 'video/ogg', 'video/avi', 'video/mov', 'video/wmv',
            'video/flv', 'video/mkv',
            
            // Archives
            'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
            'application/gzip', 'application/x-tar',
            
            // Code files
            'text/javascript', 'text/css', 'text/html', 'application/javascript',
            'text/x-python', 'text/x-java-source', 'text/x-c', 'text/x-c++',
            
            // Other common types
            'application/octet-stream' // Binary files (fallback)
        ]);
        
        this.blockedExtensions = new Set([
            '.exe', '.msi', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js', '.jar',
            '.dll', '.sys', '.drv', '.ocx', '.cpl', '.reg', '.inf', '.ini'
        ]);
    }
    
    validateFile(file) {
        const errors = [];
        const warnings = [];
        
        // Check file size
        if (file.size > this.maxFileSize) {
            errors.push(`File too large: ${this.formatFileSize(file.size)}. Maximum allowed: ${this.formatFileSize(this.maxFileSize)}`);
        }
        
        if (file.size === 0) {
            errors.push('File is empty (0 bytes)');
        }
        
        // Check file extension for security
        const fileName = file.name.toLowerCase();
        const hasBlockedExtension = Array.from(this.blockedExtensions).some(ext => fileName.endsWith(ext));
        
        if (hasBlockedExtension) {
            errors.push(`File type not allowed for security reasons: ${fileName.split('.').pop()}`);
        }
        
        // Check MIME type if available
        if (file.type) {
            if (!this.allowedTypes.has(file.type)) {
                // Don't block it entirely, but warn
                warnings.push(`File type '${file.type}' is not in the common allowed list. Upload may still work.`);
            }
        } else {
            warnings.push('File type could not be determined. Proceed with caution.');
        }
        
        // Large file warning
        if (file.size > 100 * 1024 * 1024) { // 100MB
            warnings.push(`Large file detected (${this.formatFileSize(file.size)}). Upload may take a long time.`);
        }
        
        return {
            isValid: errors.length === 0,
            errors,
            warnings,
            fileInfo: {
                name: file.name,
                size: file.size,
                type: file.type || 'unknown',
                lastModified: new Date(file.lastModified).toLocaleString()
            }
        };
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) {
            return '0 B';
        }
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    updateValidationSettings(settings) {
        if (settings.maxFileSize) {
            this.maxFileSize = settings.maxFileSize;
        }
        if (settings.allowedTypes) {
            this.allowedTypes = new Set(settings.allowedTypes);
        }
        if (settings.blockedExtensions) {
            this.blockedExtensions = new Set(settings.blockedExtensions);
        }
        debugLog('File validation settings updated', 'FILE_MANAGER');
    }

    async selectFile() {
        // First try modern File System Access API
        if (this.supportsFileSystemAccess) {
            try {
                // console.log('[FileManager] Attempting modern file picker...');
                const [fileHandle] = await window.showOpenFilePicker({
                    types: [{
                        description: 'All files',
                        accept: {
                            '*/*': ['.*']
                        }
                    }],
                    multiple: false
                });
                
                // console.log('[FileManager] Modern file picker succeeded:', file.name);
                return await fileHandle.getFile();
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.warn('[FileManager] Modern file picker failed:', error);
                    console.log('[FileManager] Falling back to traditional input...');
                } else {
                    console.log('[FileManager] User cancelled modern file picker');
                    return null;
                }
            }
        }
        
        // Fallback to traditional file input - improved version
        console.log('[FileManager] Using traditional file input fallback');
        return new Promise((resolve, reject) => {
            try {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '*/*';
                input.style.display = 'none';
                
                // Add to DOM for better browser compatibility
                document.body.appendChild(input);
                
                // Set up event handlers
                const cleanup = () => {
                    if (input.parentNode) {
                        input.parentNode.removeChild(input);
                    }
                };
                
                input.onchange = (event) => {
                    const file = event.target.files[0] || null;
                    console.log('[FileManager] Traditional file picker result:', file ? file.name : 'No file selected');
                    cleanup();
                    resolve(file);
                };
                
                input.oncancel = () => {
                    console.log('[FileManager] User cancelled traditional file picker');
                    cleanup();
                    resolve(null);
                };
                
                // Handle case where user closes dialog without triggering change
                const handleFocus = () => {
                    setTimeout(() => {
                        if (!input.files.length) {
                            console.log('[FileManager] Focus returned, assuming dialog was cancelled');
                            cleanup();
                            resolve(null);
                        }
                        window.removeEventListener('focus', handleFocus);
                    }, 300);
                };
                
                window.addEventListener('focus', handleFocus);
                
                // Trigger file dialog
                input.click();
                
                // Safety timeout
                setTimeout(() => {
                    if (input.parentNode) {
                        console.warn('[FileManager] File picker timeout, cleaning up');
                        cleanup();
                        resolve(null);
                    }
                }, 30000);
                
            } catch (error) {
                console.error('[FileManager] Fallback file picker error:', error);
                reject(error);
            }
        });
    }

    setupDragAndDrop(dropZone, onFileSelected) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length > 0) {
                onFileSelected(e.dataTransfer.files[0]);
            }
        });

        // Handle click on the drop zone to trigger file input
        dropZone.addEventListener('click', () => {
            const fileInput = dropZone.querySelector('.file-input');
            if (fileInput) {
                fileInput.click();
            }
        });

        // Handle file input change directly
        const fileInput = dropZone.querySelector('.file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    onFileSelected(e.target.files[0]);
                }
            });
        }
    }
}
class FileMemoryManager {
    constructor() {
        this.storageKey = 'cyberbackup_file_memory';
        this.maxHistorySize = 10;
    }

    /**
     * Save file information to memory
     * @param {File} file - The selected file
     */
    saveFileSelection(file) {
        try {
            const fileInfo = {
                name: file.name,
                size: file.size,
                type: file.type,
                lastModified: file.lastModified,
                timestamp: Date.now(),
                // Note: webkitRelativePath available for directory selection
                path: file.webkitRelativePath || file.name
            };

            // Get existing history
            const history = this.getFileHistory();
            
            // Remove duplicate entries (same name and size)
            const filteredHistory = history.filter(item => 
                !(item.name === fileInfo.name && item.size === fileInfo.size)
            );
            
            // Add new entry at the beginning
            filteredHistory.unshift(fileInfo);
            
            // Limit history size
            const trimmedHistory = filteredHistory.slice(0, this.maxHistorySize);
            
            // Save to localStorage
            localStorage.setItem(this.storageKey, JSON.stringify(trimmedHistory));
            
            debugLog(`File selection saved to memory: ${file.name}`, 'FILE_MEMORY');
        } catch (error) {
            console.warn('Failed to save file selection to memory:', error);
        }
    }

    /**
     * Get file selection history
     * @returns {Array} Array of file info objects
     */
    getFileHistory() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.warn('Failed to load file history:', error);
            return [];
        }
    }

    /**
     * Get the most recently selected file info
     * @returns {Object|null} Last file info or null
     */
    getLastFile() {
        const history = this.getFileHistory();
        return history.length > 0 ? history[0] : null;
    }

    /**
     * Clear file selection history
     */
    clearHistory() {
        localStorage.removeItem(this.storageKey);
        debugLog('File selection history cleared', 'FILE_MEMORY');
    }

    /**
     * Get file suggestions for UI display
     * @returns {Array} Array of recent files with formatted info
     */
    getFileSuggestions() {
        const history = this.getFileHistory();
        return history.map(file => ({
            ...file,
            sizeFormatted: this.formatBytes(file.size),
            timeAgo: this.formatTimeAgo(file.timestamp),
            displayName: file.name.length > 30 ? 
                file.name.substring(0, 27) + '...' : file.name
        }));
    }

    /**
     * Format bytes for display
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
     * Format time ago for display
     */
    formatTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) {
            return 'Just now';
        }
        if (minutes < 60) {
            return `${minutes}m ago`;
        }
        if (hours < 24) {
            return `${hours}h ago`;
        }
        return `${days}d ago`;
    }

    /**
     * Create recent files dropdown UI
     * @param {HTMLElement} container - Container to add the dropdown to
     * @param {Function} onFileSelect - Callback when file is selected from history
     */
    createRecentFilesUI(container, onFileSelect) {
        const suggestions = this.getFileSuggestions();
        if (suggestions.length === 0) {
            return;
        }

        const dropdown = document.createElement('div');
        dropdown.className = 'recent-files-dropdown fade-in';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: var(--space-sm);
            z-index: 1000;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 4px;
        `;

        const title = document.createElement('div');
        title.textContent = 'Recent Files';
        title.style.cssText = `
            font-size: var(--font-size-xs);
            color: var(--text-secondary);
            margin-bottom: var(--space-xs);
            text-transform: uppercase;
            font-weight: 600;
        `;
        dropdown.appendChild(title);

        // Batch dropdown items using DocumentFragment to reduce reflows
        const dropdownFragment = document.createDocumentFragment();
        
        suggestions.slice(0, 5).forEach(file => {
            const item = document.createElement('div');
            item.className = 'recent-file-item';
            item.style.cssText = `
                padding: var(--space-xs);
                border-radius: var(--radius-sm);
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background 0.2s ease;
            `;

            item.innerHTML = `
                <div style="flex: 1; min-width: 0;">
                    <div style="font-size: var(--font-size-sm); color: var(--text-primary); truncate;">
                        ${file.displayName}
                    </div>
                    <div style="font-size: var(--font-size-xs); color: var(--text-muted);">
                        ${file.sizeFormatted} • ${file.timeAgo}
                    </div>
                </div>
            `;

            item.addEventListener('mouseenter', () => {
                item.style.background = 'rgba(0, 191, 255, 0.1)';
            });

            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
            });

            item.addEventListener('click', () => {
                onFileSelect(file);
                dropdown.remove();
            });

            dropdownFragment.appendChild(item);
        });
        
        dropdown.appendChild(dropdownFragment);

        container.appendChild(dropdown);

        // Remove dropdown when clicking outside
        setTimeout(() => {
            const clickOutside = (e) => {
                if (!dropdown.contains(e.target)) {
                    dropdown.remove();
                    document.removeEventListener('click', clickOutside);
                }
            };
            document.addEventListener('click', clickOutside);
        }, 100);
    }
}

export { FileManager, FileMemoryManager };