/**
 * File Type Icon System Integration Example
 * 
 * This example demonstrates how to integrate the comprehensive file type icon system
 * with existing CyberBackup Pro components, specifically showing integration with:
 * 
 * 1. File selection UI
 * 2. Backup validation
 * 3. Progress monitoring
 * 4. History display
 * 5. User feedback systems
 * 
 * This serves as a reference implementation for developers working with the system.
 */

import { FileManager } from '../managers/file-manager.js';
import { BackupHistoryManager } from '../managers/backup-manager.js';
import { 
    createFileTypeIcon, 
    createValidationBadge, 
    createFileInfoDisplay, 
    createEnhancedFilePreview,
    updateFileDisplay
} from '../utils/file-type-helpers.js';
import { debugLog } from '../core/debug-utils.js';

/**
 * Enhanced File Selection Component with File Type Icon System
 */
class EnhancedFileSelector {
    constructor(containerElement, options = {}) {
        this.container = containerElement;
        this.fileManager = new FileManager();
        this.selectedFile = null;
        this.options = {
            showFilePreview: true,
            showValidationDetails: true,
            allowFileTypes: 'all', // 'all' or array of categories
            maxFileSize: 5 * 1024 * 1024 * 1024, // 5GB
            onFileSelected: null,
            onFileRemoved: null,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.createFileSelector();
        debugLog('Enhanced File Selector initialized', 'FILE_SELECTOR');
    }
    
    createFileSelector() {
        this.container.innerHTML = '';
        this.container.className = 'enhanced-file-selector';
        
        // Create drop zone
        const dropZone = this.createDropZone();
        this.container.appendChild(dropZone);
        
        // Create file preview area
        if (this.options.showFilePreview) {
            const previewArea = this.createPreviewArea();
            this.container.appendChild(previewArea);
        }
        
        // Create validation details area
        if (this.options.showValidationDetails) {
            const validationArea = this.createValidationArea();
            this.container.appendChild(validationArea);
        }
    }
    
    createDropZone() {
        const dropZone = document.createElement('div');
        dropZone.className = 'file-drop-zone enhanced';
        dropZone.style.cssText = `
            border: 2px dashed var(--glass-border);
            border-radius: var(--radius-lg);
            padding: var(--space-xl);
            text-align: center;
            background: var(--bg-glass);
            transition: var(--transition);
            cursor: pointer;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: var(--space-md);
        `;
        
        // Icon
        const iconElement = document.createElement('div');
        iconElement.style.cssText = `
            font-size: 3rem;
            color: var(--text-dim);
            margin-bottom: var(--space-md);
        `;
        iconElement.textContent = '📁';
        
        // Main text
        const mainText = document.createElement('div');
        mainText.style.cssText = `
            font-size: var(--font-size-h6);
            color: var(--text-primary);
            margin-bottom: var(--space-sm);
        `;
        mainText.textContent = 'Drop files here or click to browse';
        
        // Subtitle
        const subtitle = document.createElement('div');
        subtitle.style.cssText = `
            font-size: var(--font-size-caption);
            color: var(--text-secondary);
        `;
        subtitle.textContent = 'Supports all file types up to 5GB';
        
        dropZone.appendChild(iconElement);
        dropZone.appendChild(mainText);
        dropZone.appendChild(subtitle);
        
        // Set up drag and drop + click functionality
        this.setupDropZoneEvents(dropZone);
        
        return dropZone;
    }
    
    createPreviewArea() {
        const previewArea = document.createElement('div');
        previewArea.id = 'file-preview-area';
        previewArea.style.cssText = `
            margin-top: var(--space-lg);
            min-height: 100px;
        `;
        
        return previewArea;
    }
    
    createValidationArea() {
        const validationArea = document.createElement('div');
        validationArea.id = 'validation-details-area';
        validationArea.style.cssText = `
            margin-top: var(--space-md);
            min-height: 60px;
        `;
        
        return validationArea;
    }
    
    setupDropZoneEvents(dropZone) {
        // Drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--neon-blue)';
            dropZone.style.background = 'rgba(0, 255, 255, 0.1)';
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = 'var(--glass-border)';
            dropZone.style.background = 'var(--bg-glass)';
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--glass-border)';
            dropZone.style.background = 'var(--bg-glass)';
            
            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                this.handleFileSelection(files[0]); // Take first file
            }
        });
        
        // Click to browse
        dropZone.addEventListener('click', async () => {
            try {
                const file = await this.fileManager.selectFile();
                if (file) {
                    this.handleFileSelection(file);
                }
            } catch (error) {
                console.error('File selection error:', error);
            }
        });
    }
    
    handleFileSelection(file) {
        this.selectedFile = file;
        
        // Validate file
        const validationResult = this.fileManager.validateFile(file);
        
        // Update preview area
        this.updateFilePreview(file, validationResult);
        
        // Update validation area
        this.updateValidationDetails(validationResult);
        
        // Notify parent component
        if (this.options.onFileSelected) {
            this.options.onFileSelected(file, validationResult);
        }
        
        debugLog(`File selected: ${file.name} (${validationResult.iconInfo.category})`, 'FILE_SELECTOR');
    }
    
    updateFilePreview(file, validationResult) {
        const previewArea = document.getElementById('file-preview-area');
        if (!previewArea) return;
        
        previewArea.innerHTML = '';
        
        const filePreview = createEnhancedFilePreview(file, validationResult, {
            showFullDetails: true,
            allowRemoval: true,
            onRemove: (removedFile) => {
                this.handleFileRemoval(removedFile);
            }
        });
        
        previewArea.appendChild(filePreview);
    }
    
    updateValidationDetails(validationResult) {
        const validationArea = document.getElementById('validation-details-area');
        if (!validationArea) return;
        
        validationArea.innerHTML = '';
        
        // Create validation summary
        const validationSummary = document.createElement('div');
        validationSummary.style.cssText = `
            display: flex;
            flex-wrap: wrap;
            gap: var(--space-sm);
            align-items: center;
        `;
        
        // Validation badge
        const badge = createValidationBadge(validationResult.badge);
        validationSummary.appendChild(badge);
        
        // Risk indicator
        if (validationResult.riskLevel) {
            const riskIndicator = document.createElement('div');
            riskIndicator.className = `file-risk-indicator ${validationResult.riskLevel.level}`;
            riskIndicator.textContent = `${validationResult.riskLevel.level.toUpperCase()} RISK`;
            riskIndicator.title = validationResult.riskLevel.recommendation;
            validationSummary.appendChild(riskIndicator);
        }
        
        validationArea.appendChild(validationSummary);
        
        // Show errors and warnings if any
        if (validationResult.errors.length > 0 || validationResult.warnings.length > 0) {
            const details = this.createValidationDetails(validationResult);
            validationArea.appendChild(details);
        }
    }
    
    createValidationDetails(validationResult) {
        const details = document.createElement('div');
        details.style.cssText = `
            margin-top: var(--space-md);
            padding: var(--space-md);
            background: rgba(255, 255, 255, 0.02);
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
        `;
        
        // Errors
        if (validationResult.errors.length > 0) {
            const errorsSection = document.createElement('div');
            errorsSection.innerHTML = `
                <div style="color: var(--error); font-weight: var(--font-weight-medium); margin-bottom: var(--space-sm);">
                    ❌ Errors (${validationResult.errors.length})
                </div>
            `;
            
            validationResult.errors.forEach(error => {
                const errorItem = document.createElement('div');
                errorItem.style.cssText = `
                    color: var(--text-secondary);
                    font-size: var(--font-size-caption);
                    margin-bottom: var(--space-xs);
                    padding-left: var(--space-md);
                `;
                errorItem.textContent = `• ${error}`;
                errorsSection.appendChild(errorItem);
            });
            
            details.appendChild(errorsSection);
        }
        
        // Warnings
        if (validationResult.warnings.length > 0) {
            const warningsSection = document.createElement('div');
            warningsSection.innerHTML = `
                <div style="color: var(--warning); font-weight: var(--font-weight-medium); margin-bottom: var(--space-sm); margin-top: var(--space-md);">
                    ⚠️ Warnings (${validationResult.warnings.length})
                </div>
            `;
            
            validationResult.warnings.forEach(warning => {
                const warningItem = document.createElement('div');
                warningItem.style.cssText = `
                    color: var(--text-secondary);
                    font-size: var(--font-size-caption);
                    margin-bottom: var(--space-xs);
                    padding-left: var(--space-md);
                `;
                warningItem.textContent = `• ${warning}`;
                warningsSection.appendChild(warningItem);
            });
            
            details.appendChild(warningsSection);
        }
        
        return details;
    }
    
    handleFileRemoval(file) {
        this.selectedFile = null;
        
        // Clear preview and validation areas
        const previewArea = document.getElementById('file-preview-area');
        const validationArea = document.getElementById('validation-details-area');
        
        if (previewArea) previewArea.innerHTML = '';
        if (validationArea) validationArea.innerHTML = '';
        
        // Notify parent component
        if (this.options.onFileRemoved) {
            this.options.onFileRemoved(file);
        }
        
        debugLog(`File removed: ${file.name}`, 'FILE_SELECTOR');
    }
    
    getSelectedFile() {
        return this.selectedFile;
    }
    
    clearSelection() {
        if (this.selectedFile) {
            this.handleFileRemoval(this.selectedFile);
        }
    }
}

/**
 * Enhanced Backup History Display with File Type Icons
 */
class EnhancedBackupHistory {
    constructor(containerElement) {
        this.container = containerElement;
        this.backupHistory = new BackupHistoryManager();
        this.fileManager = new FileManager();
        
        this.init();
    }
    
    init() {
        this.createHistoryDisplay();
        debugLog('Enhanced Backup History initialized', 'BACKUP_HISTORY');
    }
    
    createHistoryDisplay() {
        this.container.innerHTML = '';
        this.container.className = 'enhanced-backup-history';
        
        const history = this.backupHistory.getFormattedHistory();
        
        if (history.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Create history list
        const historyList = document.createElement('div');
        historyList.className = 'backup-history-list';
        historyList.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: var(--space-md);
        `;
        
        history.forEach(backup => {
            const historyItem = this.createHistoryItem(backup);
            historyList.appendChild(historyItem);
        });
        
        this.container.appendChild(historyList);
    }
    
    createHistoryItem(backup) {
        const item = document.createElement('div');
        item.className = 'backup-history-item enhanced';
        item.style.cssText = `
            display: flex;
            align-items: center;
            gap: var(--space-md);
            padding: var(--space-md);
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            transition: var(--transition);
        `;
        
        // File type icon (mock file for icon generation)
        const mockFile = {\n            name: backup.filename,\n            type: this.guessFileType(backup.filename),\n            size: backup.fileSize\n        };\n        const iconInfo = this.fileManager.getFileTypeIcon(mockFile);\n        const fileIcon = createFileTypeIcon(iconInfo, 'large', false);\n        \n        // File details section\n        const detailsSection = document.createElement('div');\n        detailsSection.style.cssText = `\n            flex: 1;\n            min-width: 0;\n        `;\n        \n        // File name\n        const fileName = document.createElement('div');\n        fileName.style.cssText = `\n            font-size: var(--font-size-body1);\n            font-weight: var(--font-weight-medium);\n            color: var(--text-primary);\n            margin-bottom: var(--space-xs);\n            word-break: break-word;\n        `;\n        fileName.textContent = backup.filename;\n        \n        // Metadata\n        const metadata = document.createElement('div');\n        metadata.style.cssText = `\n            display: flex;\n            flex-wrap: wrap;\n            gap: var(--space-sm);\n            font-size: var(--font-size-caption);\n            color: var(--text-secondary);\n        `;\n        \n        metadata.innerHTML = `\n            <span>📏 ${backup.sizeFormatted}</span>\n            <span>⏱️ ${backup.durationFormatted}</span>\n            <span>🚀 ${backup.speedFormatted}</span>\n            <span>📅 ${backup.timeAgo}</span>\n            <span>🖥️ ${backup.server}</span>\n            <span>👤 ${backup.username}</span>\n        `;\n        \n        detailsSection.appendChild(fileName);\n        detailsSection.appendChild(metadata);\n        \n        // Status section\n        const statusSection = document.createElement('div');\n        statusSection.style.cssText = `\n            display: flex;\n            flex-direction: column;\n            align-items: flex-end;\n            gap: var(--space-xs);\n        `;\n        \n        // Status badge\n        const statusBadge = document.createElement('div');\n        statusBadge.className = `file-validation-badge ${backup.status}`;\n        statusBadge.style.cssText = `\n            color: var(${backup.statusColor});\n            border-color: var(${backup.statusColor});\n        `;\n        statusBadge.innerHTML = `\n            <span>${backup.statusIcon}</span>\n            <span>${backup.status.toUpperCase()}</span>\n        `;\n        \n        statusSection.appendChild(statusBadge);\n        \n        // Assemble item\n        item.appendChild(fileIcon);\n        item.appendChild(detailsSection);\n        item.appendChild(statusSection);\n        \n        // Hover effects\n        item.addEventListener('mouseenter', () => {\n            item.style.borderColor = 'var(--glass-border-active)';\n            item.style.transform = 'translateY(-1px)';\n            item.style.boxShadow = 'var(--md-elevation-2)';\n        });\n        \n        item.addEventListener('mouseleave', () => {\n            item.style.borderColor = 'var(--glass-border)';\n            item.style.transform = 'translateY(0)';\n            item.style.boxShadow = 'none';\n        });\n        \n        return item;\n    }\n    \n    showEmptyState() {\n        const emptyState = document.createElement('div');\n        emptyState.style.cssText = `\n            display: flex;\n            flex-direction: column;\n            align-items: center;\n            justify-content: center;\n            padding: var(--space-xl);\n            text-align: center;\n            color: var(--text-dim);\n        `;\n        \n        emptyState.innerHTML = `\n            <div style=\"font-size: 3rem; margin-bottom: var(--space-md);\">📊</div>\n            <div style=\"font-size: var(--font-size-h6); margin-bottom: var(--space-sm);\">No backup history</div>\n            <div style=\"font-size: var(--font-size-caption);\">Complete your first backup to see history here</div>\n        `;\n        \n        this.container.appendChild(emptyState);\n    }\n    \n    guessFileType(filename) {\n        const extension = filename.toLowerCase().split('.').pop();\n        \n        // Simple MIME type mapping\n        const mimeMap = {\n            'pdf': 'application/pdf',\n            'doc': 'application/msword',\n            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',\n            'jpg': 'image/jpeg',\n            'jpeg': 'image/jpeg',\n            'png': 'image/png',\n            'gif': 'image/gif',\n            'mp4': 'video/mp4',\n            'mp3': 'audio/mpeg',\n            'zip': 'application/zip',\n            'js': 'text/javascript',\n            'html': 'text/html',\n            'css': 'text/css',\n            'txt': 'text/plain'\n        };\n        \n        return mimeMap[extension] || 'application/octet-stream';\n    }\n    \n    refresh() {\n        this.createHistoryDisplay();\n    }\n}\n\n/**\n * Usage Examples and Integration Patterns\n */\nclass IntegrationExamples {\n    /**\n     * Example 1: Basic file selector integration\n     */\n    static createBasicFileSelector(container) {\n        return new EnhancedFileSelector(container, {\n            showFilePreview: true,\n            showValidationDetails: true,\n            onFileSelected: (file, validation) => {\n                console.log('File selected:', file.name, validation.iconInfo.category);\n            },\n            onFileRemoved: (file) => {\n                console.log('File removed:', file.name);\n            }\n        });\n    }\n    \n    /**\n     * Example 2: Backup history with file type icons\n     */\n    static createEnhancedHistory(container) {\n        return new EnhancedBackupHistory(container);\n    }\n    \n    /**\n     * Example 3: Complete backup interface integration\n     */\n    static createCompleteBackupInterface(container) {\n        container.innerHTML = '';\n        container.style.cssText = `\n            display: grid;\n            grid-template-columns: 1fr 1fr;\n            gap: var(--space-lg);\n            height: 100%;\n        `;\n        \n        // File selector section\n        const selectorSection = document.createElement('div');\n        selectorSection.style.cssText = `\n            padding: var(--space-lg);\n            background: var(--bg-card);\n            border-radius: var(--radius-lg);\n            border: 1px solid var(--glass-border);\n        `;\n        \n        const selectorTitle = document.createElement('h3');\n        selectorTitle.textContent = 'Select File for Backup';\n        selectorTitle.style.cssText = `\n            color: var(--neon-blue);\n            margin-bottom: var(--space-lg);\n            font-family: 'Orbitron', monospace;\n        `;\n        selectorSection.appendChild(selectorTitle);\n        \n        const fileSelector = IntegrationExamples.createBasicFileSelector(selectorSection);\n        \n        // History section\n        const historySection = document.createElement('div');\n        historySection.style.cssText = `\n            padding: var(--space-lg);\n            background: var(--bg-card);\n            border-radius: var(--radius-lg);\n            border: 1px solid var(--glass-border);\n            overflow-y: auto;\n        `;\n        \n        const historyTitle = document.createElement('h3');\n        historyTitle.textContent = 'Backup History';\n        historyTitle.style.cssText = `\n            color: var(--neon-purple);\n            margin-bottom: var(--space-lg);\n            font-family: 'Orbitron', monospace;\n        `;\n        historySection.appendChild(historyTitle);\n        \n        const historyDisplay = IntegrationExamples.createEnhancedHistory(historySection);\n        \n        container.appendChild(selectorSection);\n        container.appendChild(historySection);\n        \n        return { fileSelector, historyDisplay };\n    }\n}\n\n// Export classes for use in other modules\nexport { \n    EnhancedFileSelector, \n    EnhancedBackupHistory, \n    IntegrationExamples \n};\n\n// Auto-initialize for browser use\nif (typeof window !== 'undefined') {\n    window.EnhancedFileSelector = EnhancedFileSelector;\n    window.EnhancedBackupHistory = EnhancedBackupHistory;\n    window.IntegrationExamples = IntegrationExamples;\n    \n    debugLog('File Type Integration Examples ready for use', 'INTEGRATION');\n}