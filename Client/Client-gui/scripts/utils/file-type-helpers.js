/**
 * File Type Helpers - UI Integration for File Type Icon System
 * Provides easy-to-use functions for integrating the file type icon system
 * with the CyberBackup Pro web interface
 */

import { debugLog } from '../core/debug-utils.js';

/**
 * Create a complete file type icon element with all visual enhancements
 * @param {Object} iconInfo - Icon information from FileManager.getFileTypeIcon()
 * @param {string} size - Icon size ('small', 'large', 'extra-large', or default)
 * @param {boolean} showTooltip - Whether to show tooltip on hover
 * @returns {HTMLElement} Complete file type icon element
 */
export function createFileTypeIcon(iconInfo, size = '', showTooltip = true) {
    const iconElement = document.createElement('div');
    iconElement.className = `file-type-icon ${size}`.trim();
    iconElement.setAttribute('data-category', iconInfo.category);
    iconElement.textContent = iconInfo.icon;
    
    // Apply dynamic color styling
    iconElement.style.setProperty('color', `var(${iconInfo.color})`);
    
    // Add tooltip if requested
    if (showTooltip) {
        const tooltip = document.createElement('div');
        tooltip.className = 'file-type-tooltip';
        tooltip.textContent = `${iconInfo.category} • ${iconInfo.extension.toUpperCase()}`;
        iconElement.appendChild(tooltip);
    }
    
    // Add accessibility attributes
    iconElement.setAttribute('role', 'img');
    iconElement.setAttribute('aria-label', `${iconInfo.category} file: ${iconInfo.extension}`);
    
    debugLog(`Created file type icon for ${iconInfo.extension} (${iconInfo.category})`, 'FILE_TYPE_HELPERS');
    
    return iconElement;
}

/**
 * Create a file validation badge element
 * @param {Object} badgeInfo - Badge information from FileManager.getFileValidationBadge()
 * @param {boolean} showDetails - Whether to show detailed message
 * @returns {HTMLElement} File validation badge element
 */
export function createValidationBadge(badgeInfo, showDetails = true) {
    const badgeElement = document.createElement('div');
    badgeElement.className = `file-validation-badge ${badgeInfo.status}`;
    
    // Create icon span
    const iconSpan = document.createElement('span');
    iconSpan.textContent = badgeInfo.icon;
    iconSpan.setAttribute('aria-hidden', 'true');
    badgeElement.appendChild(iconSpan);
    
    // Create message span
    if (showDetails) {
        const messageSpan = document.createElement('span');
        messageSpan.textContent = badgeInfo.message;
        badgeElement.appendChild(messageSpan);
    }
    
    // Apply dynamic color styling
    badgeElement.style.setProperty('border-color', `var(${badgeInfo.color})`);
    badgeElement.style.setProperty('color', `var(${badgeInfo.color})`);
    
    // Add accessibility attributes
    badgeElement.setAttribute('role', 'status');
    badgeElement.setAttribute('aria-label', `File validation: ${badgeInfo.message}`);
    
    debugLog(`Created validation badge: ${badgeInfo.status} - ${badgeInfo.message}`, 'FILE_TYPE_HELPERS');
    
    return badgeElement;
}

/**
 * Create a comprehensive file info display with icon, details, and badges
 * @param {File} file - The file object
 * @param {Object} validationResult - Result from FileManager.validateFile()
 * @param {Object} options - Display options
 * @returns {HTMLElement} Complete file info display element
 */
export function createFileInfoDisplay(file, validationResult, options = {}) {
    const {
        showRiskIndicator = true,
        showMetadata = true,
        iconSize = 'large',
        allowActions = true
    } = options;
    
    const container = document.createElement('div');
    container.className = 'file-info-display';
    
    // File icon section
    const iconSection = document.createElement('div');
    iconSection.className = 'file-icon-section';
    const fileIcon = createFileTypeIcon(validationResult.iconInfo, iconSize);
    iconSection.appendChild(fileIcon);
    
    // File details section
    const detailsSection = document.createElement('div');
    detailsSection.className = 'file-details-section';
    
    // File name
    const fileName = document.createElement('h3');
    fileName.className = 'file-name';
    fileName.textContent = validationResult.iconInfo.displayName;
    detailsSection.appendChild(fileName);
    
    // File metadata
    if (showMetadata) {
        const metadata = document.createElement('div');
        metadata.className = 'file-metadata';
        
        // Size
        const sizeItem = document.createElement('div');
        sizeItem.className = 'metadata-item';
        sizeItem.innerHTML = `<span>📏</span><span>${validationResult.badge.details.sizeFormatted}</span>`;
        metadata.appendChild(sizeItem);
        
        // Type
        const typeItem = document.createElement('div');
        typeItem.className = 'metadata-item';
        typeItem.innerHTML = `<span>🏷️</span><span>${validationResult.iconInfo.category}</span>`;
        metadata.appendChild(typeItem);
        
        // Last modified
        const modifiedItem = document.createElement('div');
        modifiedItem.className = 'metadata-item';
        modifiedItem.innerHTML = `<span>📅</span><span>${validationResult.fileInfo.lastModified}</span>`;
        metadata.appendChild(modifiedItem);
        
        detailsSection.appendChild(metadata);
    }
    
    // Actions section
    const actionsSection = document.createElement('div');
    actionsSection.className = 'file-actions-section';
    
    // Validation badge
    const validationBadge = createValidationBadge(validationResult.badge);
    actionsSection.appendChild(validationBadge);
    
    // Risk indicator
    if (showRiskIndicator && validationResult.riskLevel) {
        const riskIndicator = createRiskIndicator(validationResult.riskLevel);
        actionsSection.appendChild(riskIndicator);
    }
    
    // Assemble the complete display
    container.appendChild(iconSection);
    container.appendChild(detailsSection);
    container.appendChild(actionsSection);
    
    // Add data attributes for programmatic access
    container.setAttribute('data-file-name', file.name);
    container.setAttribute('data-file-size', file.size);
    container.setAttribute('data-file-type', validationResult.iconInfo.category);
    container.setAttribute('data-validation-status', validationResult.badge.status);
    
    debugLog(`Created file info display for: ${file.name}`, 'FILE_TYPE_HELPERS');
    
    return container;
}

/**
 * Create a risk assessment indicator
 * @param {Object} riskInfo - Risk information from FileManager.assessFileRiskLevel()
 * @returns {HTMLElement} Risk indicator element
 */
export function createRiskIndicator(riskInfo) {
    const indicator = document.createElement('div');
    indicator.className = `file-risk-indicator ${riskInfo.level}`;
    
    // Risk level text
    const levelText = document.createElement('span');
    levelText.textContent = `${riskInfo.level.toUpperCase()} RISK`;
    indicator.appendChild(levelText);
    
    // Apply dynamic styling
    indicator.style.setProperty('color', `var(${riskInfo.color})`);
    indicator.style.setProperty('border-color', `var(${riskInfo.color})`);
    
    // Add tooltip with recommendation
    indicator.title = riskInfo.recommendation;
    
    // Accessibility
    indicator.setAttribute('role', 'status');
    indicator.setAttribute('aria-label', `Risk level: ${riskInfo.level}. ${riskInfo.recommendation}`);
    
    return indicator;
}

/**
 * Create file category filter chips for filtering file displays
 * @param {Array} categories - Array of category objects
 * @param {Function} onCategorySelect - Callback when category is selected
 * @returns {HTMLElement} Container with filter chips
 */
export function createCategoryFilters(categories, onCategorySelect) {
    const container = document.createElement('div');
    container.className = 'file-category-filters';
    container.style.cssText = `
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-sm);
        margin-bottom: var(--space-md);
    `;
    
    // Add 'All' filter
    const allFilter = createCategoryFilter('all', 'All Files', true);
    allFilter.addEventListener('click', () => {
        setActiveFilter(container, allFilter);
        onCategorySelect('all');
    });
    container.appendChild(allFilter);
    
    // Add category filters
    categories.forEach(category => {
        const filter = createCategoryFilter(category.key, category.label, false);
        filter.addEventListener('click', () => {
            setActiveFilter(container, filter);
            onCategorySelect(category.key);
        });
        container.appendChild(filter);
    });
    
    return container;
}

/**
 * Create individual category filter chip
 * @private
 */
function createCategoryFilter(key, label, isActive = false) {
    const filter = document.createElement('button');
    filter.className = `file-category-filter ${isActive ? 'active' : ''}`;
    filter.setAttribute('data-category', key);
    filter.textContent = label;
    filter.type = 'button';
    
    return filter;
}

/**
 * Set active state for category filter
 * @private
 */
function setActiveFilter(container, activeFilter) {
    // Remove active class from all filters
    container.querySelectorAll('.file-category-filter').forEach(filter => {
        filter.classList.remove('active');
    });
    
    // Add active class to selected filter
    activeFilter.classList.add('active');
}

/**
 * Enhanced file preview with comprehensive visual feedback
 * @param {File} file - The file object
 * @param {Object} validationResult - Validation result
 * @param {Object} options - Preview options
 * @returns {HTMLElement} Enhanced file preview element
 */
export function createEnhancedFilePreview(file, validationResult, options = {}) {
    const {
        showFullDetails = true,
        allowRemoval = true,
        onRemove = null
    } = options;
    
    const preview = document.createElement('div');
    preview.className = 'file-preview-enhanced';
    
    // Preview header
    const header = document.createElement('div');
    header.className = 'preview-header';
    
    const headerLeft = document.createElement('div');
    headerLeft.style.display = 'flex';
    headerLeft.style.alignItems = 'center';
    headerLeft.style.gap = 'var(--space-sm)';
    
    // File icon
    const icon = createFileTypeIcon(validationResult.iconInfo, 'small', false);
    headerLeft.appendChild(icon);
    
    // File name
    const nameElement = document.createElement('span');
    nameElement.style.fontWeight = 'var(--font-weight-medium)';
    nameElement.textContent = validationResult.iconInfo.displayName;
    headerLeft.appendChild(nameElement);
    
    header.appendChild(headerLeft);
    
    // Header actions
    const headerActions = document.createElement('div');
    headerActions.style.display = 'flex';
    headerActions.style.alignItems = 'center';
    headerActions.style.gap = 'var(--space-xs)';
    
    // Validation badge
    const badge = createValidationBadge(validationResult.badge, false);
    headerActions.appendChild(badge);
    
    // Remove button
    if (allowRemoval && onRemove) {
        const removeBtn = document.createElement('button');
        removeBtn.className = 'cyber-btn small danger';
        removeBtn.innerHTML = '✕';
        removeBtn.title = 'Remove file';
        removeBtn.addEventListener('click', () => onRemove(file));
        headerActions.appendChild(removeBtn);
    }
    
    header.appendChild(headerActions);
    preview.appendChild(header);
    
    // Preview content
    if (showFullDetails) {
        const content = document.createElement('div');
        content.className = 'preview-content';
        
        const fileInfoDisplay = createFileInfoDisplay(file, validationResult, {
            showRiskIndicator: true,
            showMetadata: true,
            iconSize: '',
            allowActions: false
        });
        
        content.appendChild(fileInfoDisplay);
        preview.appendChild(content);
    }
    
    return preview;
}

/**
 * Utility function to update file displays when file selection changes
 * @param {HTMLElement} container - Container to update
 * @param {File|null} file - Selected file or null
 * @param {Object} fileManager - FileManager instance
 */
export function updateFileDisplay(container, file, fileManager) {
    // Clear existing content
    container.innerHTML = '';
    
    if (!file) {
        // Show empty state
        const emptyState = document.createElement('div');
        emptyState.className = 'file-empty-state';
        emptyState.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: var(--space-xl);
            color: var(--text-dim);
            text-align: center;
        `;
        emptyState.innerHTML = `
            <div style="font-size: 3rem; margin-bottom: var(--space-md);">📁</div>
            <div style="font-size: var(--font-size-h6); margin-bottom: var(--space-sm);">No file selected</div>
            <div style="font-size: var(--font-size-caption);">Choose a file to see details and validation status</div>
        `;
        container.appendChild(emptyState);
        return;
    }
    
    // Validate file and create display
    const validationResult = fileManager.validateFile(file);
    const fileDisplay = createFileInfoDisplay(file, validationResult, {
        showRiskIndicator: true,
        showMetadata: true,
        iconSize: 'large',
        allowActions: true
    });
    
    container.appendChild(fileDisplay);
    
    debugLog(`Updated file display for: ${file.name}`, 'FILE_TYPE_HELPERS');
}

/**
 * Create a file type legend/guide for users
 * @returns {HTMLElement} File type legend element
 */
export function createFileTypeLegend() {
    const legend = document.createElement('div');
    legend.className = 'file-type-legend';
    legend.style.cssText = `
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--space-sm);
        padding: var(--space-md);
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        margin: var(--space-md) 0;
    `;
    
    const categories = [
        { key: 'documents', label: 'Documents', icon: '📄', color: '--text-secondary' },
        { key: 'images', label: 'Images', icon: '🖼️', color: '--neon-purple' },
        { key: 'video', label: 'Video', icon: '📹', color: '--neon-red' },
        { key: 'audio', label: 'Audio', icon: '🎵', color: '--neon-yellow' },
        { key: 'code', label: 'Code', icon: '💻', color: '--electric-blue' },
        { key: 'archives', label: 'Archives', icon: '📦', color: '--neon-blue' }
    ];
    
    categories.forEach(category => {
        const item = document.createElement('div');
        item.style.cssText = `
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            padding: var(--space-sm);
            border-radius: var(--radius-sm);
            background: rgba(255, 255, 255, 0.02);
            font-size: var(--font-size-caption);
        `;
        
        item.innerHTML = `
            <span style="font-size: 1.2em;">${category.icon}</span>
            <span style="color: var(${category.color}); font-weight: var(--font-weight-medium);">${category.label}</span>
        `;
        
        legend.appendChild(item);
    });
    
    return legend;
}