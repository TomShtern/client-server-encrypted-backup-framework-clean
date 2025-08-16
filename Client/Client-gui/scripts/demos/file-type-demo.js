/**
 * File Type Icon System Demo
 * Demonstrates integration of the comprehensive file type icon system
 * with the CyberBackup Pro web interface
 */

import { FileManager } from '../managers/file-manager.js';
import { 
    createFileTypeIcon, 
    createValidationBadge, 
    createFileInfoDisplay, 
    createEnhancedFilePreview,
    createCategoryFilters,
    createFileTypeLegend,
    updateFileDisplay
} from '../utils/file-type-helpers.js';
import { debugLog } from '../core/debug-utils.js';

/**
 * Demo class showcasing the file type icon system capabilities
 */
class FileTypeIconDemo {
    constructor() {
        this.fileManager = new FileManager();
        this.demoContainer = null;
        this.selectedFiles = [];
        
        debugLog('File Type Icon Demo initialized', 'DEMO');
    }
    
    /**
     * Initialize the demo interface
     * @param {HTMLElement} container - Container element for the demo
     */
    init(container) {
        this.demoContainer = container;
        this.createDemoInterface();
        debugLog('File Type Icon Demo interface created', 'DEMO');
    }
    
    /**
     * Create the complete demo interface
     * @private
     */
    createDemoInterface() {
        this.demoContainer.innerHTML = '';
        this.demoContainer.className = 'file-type-demo';
        this.demoContainer.style.cssText = `
            padding: var(--space-lg);
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            border: 1px solid var(--glass-border);
        `;
        
        // Demo title
        const title = document.createElement('h2');
        title.textContent = 'File Type Icon System Demo';
        title.style.cssText = `
            color: var(--neon-blue);
            text-align: center;
            margin-bottom: var(--space-lg);
            font-family: 'Orbitron', monospace;
        `;
        this.demoContainer.appendChild(title);
        
        // Create demo sections
        this.createFileSelectionSection();
        this.createIconShowcaseSection();
        this.createValidationDemoSection();
        this.createCategoryFilterSection();
        this.createLegendSection();
    }
    
    /**
     * Create file selection section
     * @private
     */
    createFileSelectionSection() {
        const section = this.createSection('File Selection & Analysis', 'Choose files to see the icon system in action');
        
        // File input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.className = 'cyber-input';
        fileInput.style.marginBottom = 'var(--space-md)';
        
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(Array.from(e.target.files));
        });
        
        section.appendChild(fileInput);
        
        // File display area
        const fileDisplayArea = document.createElement('div');
        fileDisplayArea.id = 'selected-files-display';
        fileDisplayArea.style.cssText = `
            min-height: 200px;
            border: 2px dashed var(--glass-border);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            margin-top: var(--space-md);
        `;
        section.appendChild(fileDisplayArea);
        
        this.demoContainer.appendChild(section);
    }
    
    /**
     * Create icon showcase section
     * @private
     */
    createIconShowcaseSection() {
        const section = this.createSection('Icon Showcase', 'Preview of file type icons across categories');
        
        const showcaseGrid = document.createElement('div');
        showcaseGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: var(--space-md);
            margin-top: var(--space-md);
        `;
        
        // Sample file types for showcase
        const sampleTypes = [
            { name: 'document.pdf', type: 'application/pdf' },
            { name: 'image.jpg', type: 'image/jpeg' },
            { name: 'video.mp4', type: 'video/mp4' },
            { name: 'audio.mp3', type: 'audio/mpeg' },
            { name: 'code.js', type: 'text/javascript' },
            { name: 'archive.zip', type: 'application/zip' },
            { name: 'spreadsheet.xlsx', type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
            { name: 'presentation.pptx', type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' }
        ];
        
        sampleTypes.forEach(sample => {
            const mockFile = this.createMockFile(sample.name, sample.type);
            const iconInfo = this.fileManager.getFileTypeIcon(mockFile);
            
            const showcaseItem = document.createElement('div');
            showcaseItem.style.cssText = `
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: var(--space-sm);
                padding: var(--space-md);
                background: rgba(255, 255, 255, 0.02);
                border-radius: var(--radius-md);
                border: 1px solid var(--glass-border);
            `;
            
            const icon = createFileTypeIcon(iconInfo, 'large');
            const label = document.createElement('div');
            label.style.cssText = `
                font-size: var(--font-size-caption);
                color: var(--text-secondary);
                text-align: center;
            `;
            label.textContent = iconInfo.category;
            
            showcaseItem.appendChild(icon);
            showcaseItem.appendChild(label);
            showcaseGrid.appendChild(showcaseItem);
        });
        
        section.appendChild(showcaseGrid);
        this.demoContainer.appendChild(section);
    }
    
    /**
     * Create validation demo section
     * @private
     */
    createValidationDemoSection() {
        const section = this.createSection('Validation System', 'File validation badges and risk assessment');
        
        const validationGrid = document.createElement('div');
        validationGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-md);
            margin-top: var(--space-md);
        `;
        
        // Sample validation states
        const validationSamples = [
            { 
                status: 'valid', 
                icon: '✅', 
                message: 'Valid file', 
                color: '--success',
                description: 'File passes all validation checks'
            },
            { 
                status: 'warning', 
                icon: '⚠️', 
                message: '1 warning', 
                color: '--warning',
                description: 'File has minor issues but can be processed'
            },
            { 
                status: 'large', 
                icon: '⚠️', 
                message: 'Large file', 
                color: '--neon-orange',
                description: 'File is large and may take time to upload'
            },
            { 
                status: 'error', 
                icon: '❌', 
                message: '2 errors', 
                color: '--error',
                description: 'File has critical issues and cannot be processed'
            }
        ];
        
        validationSamples.forEach(sample => {
            const validationItem = document.createElement('div');
            validationItem.style.cssText = `
                padding: var(--space-md);
                background: rgba(255, 255, 255, 0.02);
                border-radius: var(--radius-md);
                border: 1px solid var(--glass-border);
                text-align: center;
            `;
            
            const badge = createValidationBadge(sample);
            const description = document.createElement('div');
            description.style.cssText = `
                font-size: var(--font-size-caption);
                color: var(--text-secondary);
                margin-top: var(--space-sm);
            `;
            description.textContent = sample.description;
            
            validationItem.appendChild(badge);
            validationItem.appendChild(description);
            validationGrid.appendChild(validationItem);
        });
        
        section.appendChild(validationGrid);
        this.demoContainer.appendChild(section);
    }
    
    /**
     * Create category filter section
     * @private
     */
    createCategoryFilterSection() {
        const section = this.createSection('Category Filters', 'Interactive file type category filtering');
        
        const categories = [
            { key: 'documents', label: 'Documents' },
            { key: 'images', label: 'Images' },
            { key: 'video', label: 'Video' },
            { key: 'audio', label: 'Audio' },
            { key: 'code', label: 'Code' },
            { key: 'archives', label: 'Archives' }
        ];
        
        const filterContainer = createCategoryFilters(categories, (category) => {
            debugLog(`Category filter selected: ${category}`, 'DEMO');
            this.showToast(`Filtered by: ${category === 'all' ? 'All Files' : category}`, 'info');
        });
        
        section.appendChild(filterContainer);
        this.demoContainer.appendChild(section);
    }
    
    /**
     * Create legend section
     * @private
     */
    createLegendSection() {
        const section = this.createSection('File Type Legend', 'Visual guide to file type categories');
        
        const legend = createFileTypeLegend();
        section.appendChild(legend);
        this.demoContainer.appendChild(section);
    }
    
    /**
     * Handle file selection for demo
     * @private
     * @param {File[]} files - Selected files
     */
    handleFileSelection(files) {
        this.selectedFiles = files;
        const displayArea = document.getElementById('selected-files-display');
        
        if (files.length === 0) {
            updateFileDisplay(displayArea, null, this.fileManager);
            return;
        }
        
        displayArea.innerHTML = '';
        
        files.forEach((file, index) => {
            const validationResult = this.fileManager.validateFile(file);
            
            const filePreview = createEnhancedFilePreview(file, validationResult, {
                showFullDetails: false,
                allowRemoval: true,
                onRemove: (removedFile) => {
                    this.removeFile(removedFile);
                }
            });
            
            filePreview.style.marginBottom = 'var(--space-md)';
            displayArea.appendChild(filePreview);
        });
        
        this.showToast(`Analyzed ${files.length} file${files.length > 1 ? 's' : ''}`, 'success');
    }
    
    /**
     * Remove file from selection
     * @private
     * @param {File} fileToRemove - File to remove
     */
    removeFile(fileToRemove) {
        this.selectedFiles = this.selectedFiles.filter(file => file !== fileToRemove);
        this.handleFileSelection(this.selectedFiles);
        this.showToast(`Removed: ${fileToRemove.name}`, 'warning');
    }
    
    /**
     * Create a demo section with title and description
     * @private
     * @param {string} title - Section title
     * @param {string} description - Section description
     * @returns {HTMLElement} Section element
     */
    createSection(title, description) {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: var(--space-xl);
            padding: var(--space-lg);
            background: rgba(255, 255, 255, 0.02);
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
        `;
        
        const titleElement = document.createElement('h3');
        titleElement.textContent = title;
        titleElement.style.cssText = `
            color: var(--neon-purple);
            margin-bottom: var(--space-sm);
            font-family: 'Orbitron', monospace;
        `;
        
        const descElement = document.createElement('p');
        descElement.textContent = description;
        descElement.style.cssText = `
            color: var(--text-secondary);
            margin-bottom: var(--space-md);
            font-size: var(--font-size-caption);
        `;
        
        section.appendChild(titleElement);
        section.appendChild(descElement);
        
        return section;
    }
    
    /**
     * Create a mock file object for demonstration
     * @private
     * @param {string} name - File name
     * @param {string} type - MIME type
     * @returns {Object} Mock file object
     */
    createMockFile(name, type) {
        return {
            name: name,
            type: type,
            size: Math.floor(Math.random() * 1000000) + 1000, // Random size between 1KB and 1MB
            lastModified: Date.now() - Math.floor(Math.random() * 86400000) // Random time in last 24 hours
        };
    }
    
    /**
     * Show a toast notification
     * @private
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, warning, error, info)
     */
    showToast(message, type = 'info') {
        // This would integrate with the existing toast system
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Create a simple visual feedback for demo
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-card);
            color: var(--text-primary);
            padding: var(--space-md);
            border-radius: var(--radius-md);
            border: 1px solid var(--glass-border);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Export for use in other modules
export { FileTypeIconDemo };

// Auto-initialize if running in browser
if (typeof window !== 'undefined') {
    window.FileTypeIconDemo = FileTypeIconDemo;
    
    // Add CSS animations for demo toasts
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    debugLog('File Type Icon Demo ready for use', 'DEMO');
}