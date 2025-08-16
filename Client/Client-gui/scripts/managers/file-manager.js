import { debugLog } from '../core/debug-utils.js';

class FileManager {
    constructor() {
        this.supportsFileSystemAccess = 'showOpenFilePicker' in window;
        debugLog(`File System Access API supported: ${this.supportsFileSystemAccess}`, 'FILE_MANAGER');
        
        // File validation settings
        this.maxFileSize = 5 * 1024 * 1024 * 1024; // 5GB default
        
        // File type icon mappings for comprehensive visual feedback
        this.fileTypeIcons = this._initializeFileTypeIcons();
        this.fileCategories = this._initializeFileCategories();
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
    
    /**
     * Initialize comprehensive file type icon mappings
     * @private
     * @returns {Map} File extension to icon mapping
     */
    _initializeFileTypeIcons() {
        return new Map([
            // Documents & Text
            ['.txt', { icon: '📄', color: '--text-secondary' }],
            ['.doc', { icon: '📝', color: '--neon-blue' }],
            ['.docx', { icon: '📝', color: '--neon-blue' }],
            ['.pdf', { icon: '📕', color: '--neon-red' }],
            ['.rtf', { icon: '📄', color: '--text-secondary' }],
            ['.odt', { icon: '📝', color: '--neon-blue' }],
            
            // Spreadsheets & Data
            ['.xls', { icon: '📊', color: '--neon-green' }],
            ['.xlsx', { icon: '📊', color: '--neon-green' }],
            ['.csv', { icon: '📈', color: '--cyber-lime' }],
            ['.ods', { icon: '📊', color: '--neon-green' }],
            
            // Presentations
            ['.ppt', { icon: '📽️', color: '--neon-orange' }],
            ['.pptx', { icon: '📽️', color: '--neon-orange' }],
            ['.odp', { icon: '📽️', color: '--neon-orange' }],
            
            // Images
            ['.jpg', { icon: '🖼️', color: '--neon-purple' }],
            ['.jpeg', { icon: '🖼️', color: '--neon-purple' }],
            ['.png', { icon: '🖼️', color: '--neon-purple' }],
            ['.gif', { icon: '🎞️', color: '--plasma-pink' }],
            ['.bmp', { icon: '🖼️', color: '--neon-purple' }],
            ['.webp', { icon: '🖼️', color: '--neon-purple' }],
            ['.svg', { icon: '🎨', color: '--electric-blue' }],
            ['.ico', { icon: '🔸', color: '--neon-yellow' }],
            ['.tiff', { icon: '🖼️', color: '--neon-purple' }],
            ['.tif', { icon: '🖼️', color: '--neon-purple' }],
            
            // Audio
            ['.mp3', { icon: '🎵', color: '--neon-yellow' }],
            ['.wav', { icon: '🎵', color: '--neon-yellow' }],
            ['.flac', { icon: '🎶', color: '--neon-orange' }],
            ['.aac', { icon: '🎵', color: '--neon-yellow' }],
            ['.ogg', { icon: '🎵', color: '--neon-yellow' }],
            ['.m4a', { icon: '🎵', color: '--neon-yellow' }],
            ['.wma', { icon: '🎵', color: '--neon-yellow' }],
            
            // Video
            ['.mp4', { icon: '📹', color: '--neon-red' }],
            ['.avi', { icon: '📹', color: '--neon-red' }],
            ['.mov', { icon: '🎬', color: '--plasma-pink' }],
            ['.wmv', { icon: '📹', color: '--neon-red' }],
            ['.flv', { icon: '📹', color: '--neon-red' }],
            ['.mkv', { icon: '🎬', color: '--plasma-pink' }],
            ['.webm', { icon: '📹', color: '--neon-red' }],
            ['.m4v', { icon: '📹', color: '--neon-red' }],
            
            // Archives
            ['.zip', { icon: '📦', color: '--neon-blue' }],
            ['.rar', { icon: '📦', color: '--neon-blue' }],
            ['.7z', { icon: '📦', color: '--neon-blue' }],
            ['.tar', { icon: '📦', color: '--neon-blue' }],
            ['.gz', { icon: '📦', color: '--neon-blue' }],
            ['.bz2', { icon: '📦', color: '--neon-blue' }],
            ['.xz', { icon: '📦', color: '--neon-blue' }],
            
            // Code & Development
            ['.js', { icon: '💛', color: '--neon-yellow' }],
            ['.ts', { icon: '💙', color: '--electric-blue' }],
            ['.jsx', { icon: '⚛️', color: '--neon-blue' }],
            ['.tsx', { icon: '⚛️', color: '--electric-blue' }],
            ['.html', { icon: '🌐', color: '--neon-orange' }],
            ['.css', { icon: '🎨', color: '--neon-purple' }],
            ['.scss', { icon: '🎨', color: '--plasma-pink' }],
            ['.sass', { icon: '🎨', color: '--plasma-pink' }],
            ['.json', { icon: '📋', color: '--neon-green' }],
            ['.xml', { icon: '📋', color: '--neon-orange' }],
            ['.yaml', { icon: '📋', color: '--cyber-lime' }],
            ['.yml', { icon: '📋', color: '--cyber-lime' }],
            ['.py', { icon: '🐍', color: '--neon-green' }],
            ['.java', { icon: '☕', color: '--neon-orange' }],
            ['.cpp', { icon: '⚙️', color: '--electric-blue' }],
            ['.c', { icon: '⚙️', color: '--neon-blue' }],
            ['.cs', { icon: '💜', color: '--neon-purple' }],
            ['.php', { icon: '🐘', color: '--neon-purple' }],
            ['.rb', { icon: '💎', color: '--neon-red' }],
            ['.go', { icon: '🐹', color: '--electric-blue' }],
            ['.rs', { icon: '🦀', color: '--neon-orange' }],
            ['.swift', { icon: '🦉', color: '--neon-orange' }],
            ['.kt', { icon: '🟣', color: '--neon-purple' }],
            ['.sh', { icon: '💻', color: '--neon-green' }],
            ['.bat', { icon: '⚡', color: '--neon-yellow' }],
            ['.ps1', { icon: '💙', color: '--electric-blue' }],
            
            // Configuration & System
            ['.config', { icon: '⚙️', color: '--text-dim' }],
            ['.ini', { icon: '⚙️', color: '--text-dim' }],
            ['.cfg', { icon: '⚙️', color: '--text-dim' }],
            ['.conf', { icon: '⚙️', color: '--text-dim' }],
            ['.env', { icon: '🔐', color: '--neon-yellow' }],
            ['.log', { icon: '📜', color: '--text-secondary' }],
            
            // Databases
            ['.sql', { icon: '🗃️', color: '--electric-blue' }],
            ['.db', { icon: '🗄️', color: '--neon-blue' }],
            ['.sqlite', { icon: '🗄️', color: '--neon-blue' }],
            ['.mdb', { icon: '🗄️', color: '--neon-blue' }],
            
            // Fonts
            ['.ttf', { icon: '🔤', color: '--text-primary' }],
            ['.otf', { icon: '🔤', color: '--text-primary' }],
            ['.woff', { icon: '🔤', color: '--text-primary' }],
            ['.woff2', { icon: '🔤', color: '--text-primary' }],
            
            // 3D & Design
            ['.blend', { icon: '🎭', color: '--neon-orange' }],
            ['.obj', { icon: '🧊', color: '--neon-blue' }],
            ['.fbx', { icon: '🧊', color: '--neon-blue' }],
            ['.dae', { icon: '🧊', color: '--neon-blue' }],
            ['.psd', { icon: '🎨', color: '--neon-purple' }],
            ['.ai', { icon: '🎨', color: '--neon-orange' }],
            ['.sketch', { icon: '🎨', color: '--neon-yellow' }],
            ['.fig', { icon: '🎨', color: '--neon-purple' }],
            
            // Default fallback
            ['default', { icon: '📄', color: '--text-secondary' }]
        ]);
    }
    
    /**
     * Initialize file category classifications for enhanced filtering
     * @private
     * @returns {Map} Category to extensions mapping
     */
    _initializeFileCategories() {
        return new Map([
            ['documents', ['.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt']],
            ['spreadsheets', ['.xls', '.xlsx', '.csv', '.ods']],
            ['presentations', ['.ppt', '.pptx', '.odp']],
            ['images', ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif']],
            ['audio', ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']],
            ['video', ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v']],
            ['archives', ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz']],
            ['code', ['.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass', '.json', '.xml', '.yaml', '.yml', '.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.sh', '.bat', '.ps1']],
            ['config', ['.config', '.ini', '.cfg', '.conf', '.env', '.log']],
            ['database', ['.sql', '.db', '.sqlite', '.mdb']],
            ['fonts', ['.ttf', '.otf', '.woff', '.woff2']],
            ['design', ['.blend', '.obj', '.fbx', '.dae', '.psd', '.ai', '.sketch', '.fig']]
        ]);
    }
    
    /**
     * Get file type icon and color information
     * @param {File} file - The file object
     * @returns {Object} Icon and color information
     */
    getFileTypeIcon(file) {
        const fileName = file.name.toLowerCase();
        const extension = '.' + fileName.split('.').pop();
        
        // Get icon info from mapping or default
        const iconInfo = this.fileTypeIcons.get(extension) || this.fileTypeIcons.get('default');
        
        // Add file category classification
        const category = this.getFileCategory(extension);
        
        return {
            icon: iconInfo.icon,
            color: iconInfo.color,
            extension: extension,
            category: category,
            displayName: this.getFileDisplayName(file)
        };
    }
    
    /**
     * Get file validation badge with visual status indicators
     * @param {Object} validationResult - Result from validateFile method
     * @returns {Object} Badge information with icon, color, and status
     */
    getFileValidationBadge(validationResult) {
        const { isValid, errors, warnings, fileInfo } = validationResult;
        
        // Determine overall status
        let status, icon, color, message;
        
        if (!isValid) {
            status = 'error';
            icon = '❌';
            color = '--error';
            message = `${errors.length} error${errors.length > 1 ? 's' : ''}`;
        } else if (warnings.length > 0) {
            // Check for large file specifically
            const hasLargeFileWarning = warnings.some(w => w.includes('Large file'));
            if (hasLargeFileWarning) {
                status = 'large';
                icon = '⚠️';
                color = '--warning';
                message = 'Large file';
            } else {
                status = 'warning';
                icon = '⚠️';
                color = '--warning';
                message = `${warnings.length} warning${warnings.length > 1 ? 's' : ''}`;
            }
        } else {
            status = 'valid';
            icon = '✅';
            color = '--success';
            message = 'Valid file';
        }
        
        return {
            status,
            icon,
            color,
            message,
            details: {
                errors: errors.length,
                warnings: warnings.length,
                size: fileInfo.size,
                sizeFormatted: this.formatFileSize(fileInfo.size)
            }
        };
    }
    
    /**
     * Enhanced file validation with improved visual feedback integration
     * @param {File} file - The file to validate
     * @returns {Object} Enhanced validation result with UI helpers
     */
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
        
        // Enhanced size warnings with specific thresholds
        if (file.size > 1024 * 1024 * 1024) { // 1GB
            warnings.push(`Very large file detected (${this.formatFileSize(file.size)}). Upload may take considerable time.`);
        } else if (file.size > 100 * 1024 * 1024) { // 100MB
            warnings.push(`Large file detected (${this.formatFileSize(file.size)}). Upload may take a long time.`);
        }
        
        // Create base validation result
        const validationResult = {
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
        
        // Add enhanced UI helpers
        validationResult.iconInfo = this.getFileTypeIcon(file);
        validationResult.badge = this.getFileValidationBadge(validationResult);
        validationResult.riskLevel = this.assessFileRiskLevel(file, validationResult);
        
        return validationResult;
    }
    
    /**
     * Get file category based on extension
     * @private
     * @param {string} extension - File extension
     * @returns {string} Category name
     */
    getFileCategory(extension) {
        for (const [category, extensions] of this.fileCategories) {
            if (extensions.includes(extension)) {
                return category;
            }
        }
        return 'other';
    }
    
    /**
     * Generate user-friendly display name for file
     * @private
     * @param {File} file - File object
     * @returns {string} Display name
     */
    getFileDisplayName(file) {
        const name = file.name;
        if (name.length <= 30) {
            return name;
        }
        
        const extension = '.' + name.split('.').pop();
        const baseName = name.substring(0, name.lastIndexOf('.'));
        const maxBaseLength = 30 - extension.length - 3; // 3 for '...'
        
        return baseName.substring(0, maxBaseLength) + '...' + extension;
    }
    
    /**
     * Assess overall file risk level for enhanced security feedback
     * @private
     * @param {File} file - File object
     * @param {Object} validationResult - Validation result
     * @returns {Object} Risk assessment
     */
    assessFileRiskLevel(file, validationResult) {
        let riskScore = 0;
        let riskFactors = [];
        
        // Size-based risk
        if (file.size > 1024 * 1024 * 1024) { // 1GB+
            riskScore += 3;
            riskFactors.push('Very large file size');
        } else if (file.size > 100 * 1024 * 1024) { // 100MB+
            riskScore += 2;
            riskFactors.push('Large file size');
        }
        
        // Type-based risk
        if (!file.type) {
            riskScore += 2;
            riskFactors.push('Unknown file type');
        }
        
        // Extension-based risk
        const fileName = file.name.toLowerCase();
        const extension = '.' + fileName.split('.').pop();
        const isExecutable = ['.exe', '.msi', '.bat', '.cmd', '.scr'].includes(extension);
        if (isExecutable) {
            riskScore += 5;
            riskFactors.push('Executable file type');
        }
        
        // Error/warning based risk
        riskScore += validationResult.errors.length * 3;
        riskScore += validationResult.warnings.length * 1;
        
        // Determine risk level
        let riskLevel, riskColor;
        if (riskScore >= 7) {
            riskLevel = 'high';
            riskColor = '--error';
        } else if (riskScore >= 4) {
            riskLevel = 'medium';
            riskColor = '--warning';
        } else if (riskScore >= 2) {
            riskLevel = 'low';
            riskColor = '--info';
        } else {
            riskLevel = 'minimal';
            riskColor = '--success';
        }
        
        return {
            level: riskLevel,
            score: riskScore,
            color: riskColor,
            factors: riskFactors,
            recommendation: this.getRiskRecommendation(riskLevel)
        };
    }
    
    /**
     * Get risk-based recommendation for file handling
     * @private
     * @param {string} riskLevel - Calculated risk level
     * @returns {string} User recommendation
     */
    getRiskRecommendation(riskLevel) {
        const recommendations = {
            'minimal': 'File appears safe to upload',
            'low': 'Review file before uploading',
            'medium': 'Use caution - verify file source and content',
            'high': 'High risk - strongly recommend avoiding upload'
        };
        
        return recommendations[riskLevel] || 'Unknown risk level';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) {
            return '0 B';
        }
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    /**
     * Get file type icon and metadata based on file extension and MIME type
     * @param {File} file - The file object
     * @returns {Object} Icon information with emoji, color, and category
     */
    getFileTypeIcon(file) {
        const fileName = file.name.toLowerCase();
        const fileType = file.type.toLowerCase();
        const extension = fileName.split('.').pop();
        
        // File type mappings with cyberpunk-themed colors
        const fileTypeMap = {
            // Documents
            'txt': { icon: '📄', color: 'var(--text-secondary)', category: 'document' },
            'pdf': { icon: '📕', color: 'var(--neon-red)', category: 'document' },
            'doc': { icon: '📘', color: 'var(--neon-blue)', category: 'document' },
            'docx': { icon: '📘', color: 'var(--neon-blue)', category: 'document' },
            'rtf': { icon: '📄', color: 'var(--text-secondary)', category: 'document' },
            
            // Images
            'jpg': { icon: '🖼️', color: 'var(--neon-purple)', category: 'image' },
            'jpeg': { icon: '🖼️', color: 'var(--neon-purple)', category: 'image' },
            'png': { icon: '🖼️', color: 'var(--neon-purple)', category: 'image' },
            'gif': { icon: '🎞️', color: 'var(--neon-pink)', category: 'image' },
            'webp': { icon: '🖼️', color: 'var(--neon-purple)', category: 'image' },
            'svg': { icon: '🎨', color: 'var(--neon-green)', category: 'image' },
            'bmp': { icon: '🖼️', color: 'var(--neon-purple)', category: 'image' },
            'ico': { icon: '🏷️', color: 'var(--neon-yellow)', category: 'image' },
            
            // Video
            'mp4': { icon: '📹', color: 'var(--neon-red)', category: 'video' },
            'avi': { icon: '📹', color: 'var(--neon-red)', category: 'video' },
            'mov': { icon: '🎬', color: 'var(--neon-red)', category: 'video' },
            'wmv': { icon: '📹', color: 'var(--neon-red)', category: 'video' },
            'flv': { icon: '📹', color: 'var(--neon-red)', category: 'video' },
            'webm': { icon: '📹', color: 'var(--neon-red)', category: 'video' },
            'mkv': { icon: '📹', color: 'var(--neon-red)', category: 'video' },
            
            // Audio
            'mp3': { icon: '🎵', color: 'var(--neon-yellow)', category: 'audio' },
            'wav': { icon: '🎵', color: 'var(--neon-yellow)', category: 'audio' },
            'flac': { icon: '🎶', color: 'var(--neon-yellow)', category: 'audio' },
            'aac': { icon: '🎵', color: 'var(--neon-yellow)', category: 'audio' },
            'ogg': { icon: '🎵', color: 'var(--neon-yellow)', category: 'audio' },
            
            // Code
            'js': { icon: '⚡', color: 'var(--electric-blue)', category: 'code' },
            'html': { icon: '🌐', color: 'var(--neon-orange)', category: 'code' },
            'css': { icon: '🎨', color: 'var(--neon-blue)', category: 'code' },
            'json': { icon: '📋', color: 'var(--neon-green)', category: 'code' },
            'xml': { icon: '📋', color: 'var(--neon-green)', category: 'code' },
            'py': { icon: '🐍', color: 'var(--neon-green)', category: 'code' },
            'java': { icon: '☕', color: 'var(--neon-orange)', category: 'code' },
            'cpp': { icon: '⚙️', color: 'var(--electric-blue)', category: 'code' },
            'c': { icon: '⚙️', color: 'var(--electric-blue)', category: 'code' },
            
            // Archives
            'zip': { icon: '📦', color: 'var(--neon-blue)', category: 'archive' },
            'rar': { icon: '📦', color: 'var(--neon-blue)', category: 'archive' },
            '7z': { icon: '📦', color: 'var(--neon-blue)', category: 'archive' },
            'tar': { icon: '📦', color: 'var(--neon-blue)', category: 'archive' },
            'gz': { icon: '📦', color: 'var(--neon-blue)', category: 'archive' },
            
            // Spreadsheets
            'xls': { icon: '📊', color: 'var(--neon-green)', category: 'spreadsheet' },
            'xlsx': { icon: '📊', color: 'var(--neon-green)', category: 'spreadsheet' },
            'csv': { icon: '📈', color: 'var(--neon-green)', category: 'spreadsheet' },
            
            // Presentations  
            'ppt': { icon: '📽️', color: 'var(--neon-orange)', category: 'presentation' },
            'pptx': { icon: '📽️', color: 'var(--neon-orange)', category: 'presentation' }
        };
        
        // Get file info from extension or fallback to generic
        const fileInfo = fileTypeMap[extension] || { 
            icon: '📄', 
            color: 'var(--text-dim)', 
            category: 'unknown' 
        };
        
        return {
            ...fileInfo,
            extension: extension,
            mimeType: fileType,
            name: file.name,
            size: file.size,
            formattedSize: this.formatFileSize(file.size)
        };
    }
    
    /**
     * Create a file validation badge based on validation results
     * @param {Object} validationResult - Result from validateFile method
     * @returns {Object} Badge information with icon, color, and message
     */
    getFileValidationBadge(validationResult) {
        const { isValid, errors, warnings } = validationResult;
        
        if (errors.length > 0) {
            return {
                icon: '❌',
                color: 'var(--error)',
                type: 'error',
                message: errors[0],
                className: 'validation-badge error'
            };
        }
        
        if (warnings.length > 0) {
            return {
                icon: '⚠️',
                color: 'var(--warning)',
                type: 'warning', 
                message: warnings[0],
                className: 'validation-badge warning'
            };
        }
        
        return {
            icon: '✅',
            color: 'var(--success)',
            type: 'valid',
            message: 'File is ready for upload',
            className: 'validation-badge success'
        };
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
    
    /**
     * Create enhanced file preview with icons and validation badges
     * @param {File} file - The file to preview
     * @param {HTMLElement} container - Container element for the preview
     */
    createEnhancedFilePreview(file, container) {
        // Clear existing content
        container.innerHTML = '';
        
        const fileTypeInfo = this.getFileTypeIcon(file);
        const validationResult = this.validateFile(file);
        const validationBadge = this.getFileValidationBadge(validationResult);
        
        // Create enhanced file info container
        const fileInfoContainer = document.createElement('div');
        fileInfoContainer.className = 'enhanced-file-info';
        
        // File header with icon and details
        const fileHeader = document.createElement('div');
        fileHeader.className = 'file-info-header';
        
        // File type icon
        const iconContainer = document.createElement('div');
        iconContainer.className = 'file-info-icon';
        const icon = document.createElement('span');
        icon.className = 'file-type-icon large';
        icon.textContent = fileTypeInfo.icon;
        icon.style.color = fileTypeInfo.color;
        iconContainer.appendChild(icon);
        
        // File details
        const detailsContainer = document.createElement('div');
        detailsContainer.className = 'file-info-details';
        
        const fileName = document.createElement('div');
        fileName.className = 'file-info-name';
        fileName.textContent = file.name;
        fileName.title = file.name; // Tooltip for long names
        
        const fileMeta = document.createElement('div');
        fileMeta.className = 'file-info-meta';
        
        const sizeSpan = document.createElement('span');
        sizeSpan.textContent = fileTypeInfo.formattedSize;
        
        const typeSpan = document.createElement('span');
        typeSpan.textContent = fileTypeInfo.category.toUpperCase();
        typeSpan.style.color = fileTypeInfo.color;
        
        const lastModified = document.createElement('span');
        lastModified.textContent = new Date(file.lastModified).toLocaleDateString();
        
        fileMeta.appendChild(sizeSpan);
        fileMeta.appendChild(typeSpan);
        fileMeta.appendChild(lastModified);
        
        detailsContainer.appendChild(fileName);
        detailsContainer.appendChild(fileMeta);
        
        fileHeader.appendChild(iconContainer);
        fileHeader.appendChild(detailsContainer);
        
        // Validation badge
        const badgeContainer = document.createElement('div');
        badgeContainer.className = 'file-info-badge-container';
        
        const badge = document.createElement('div');
        badge.className = validationBadge.className;
        badge.style.color = validationBadge.color;
        badge.innerHTML = `${validationBadge.icon} ${validationBadge.message}`;
        badge.title = validationBadge.message;
        
        badgeContainer.appendChild(badge);
        
        // Add file size warning if needed
        if (file.size > 100 * 1024 * 1024) { // 100MB
            const warning = document.createElement('div');
            warning.className = file.size > 1024 * 1024 * 1024 ? 'file-size-warning huge' : 'file-size-warning large';
            
            const estimatedTime = this.estimateTransferTime(file.size);
            warning.innerHTML = `⏱️ Large file: Est. transfer time ${estimatedTime}`;
            
            fileInfoContainer.appendChild(warning);
        }
        
        fileInfoContainer.appendChild(fileHeader);
        fileInfoContainer.appendChild(badgeContainer);
        
        // Add fade-in animation
        fileInfoContainer.style.opacity = '0';
        fileInfoContainer.style.transform = 'translateY(10px)';
        container.appendChild(fileInfoContainer);
        
        // Animate in
        requestAnimationFrame(() => {
            fileInfoContainer.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            fileInfoContainer.style.opacity = '1';
            fileInfoContainer.style.transform = 'translateY(0)';
        });
        
        return fileInfoContainer;
    }
    
    /**
     * Estimate file transfer time based on size
     * @param {number} fileSize - File size in bytes
     * @returns {string} Estimated time string
     */
    estimateTransferTime(fileSize) {
        // Assume average transfer speed of 10 MB/s (reasonable for local network)
        const avgSpeedMBps = 10;
        const fileSizeMB = fileSize / (1024 * 1024);
        const timeSeconds = fileSizeMB / avgSpeedMBps;
        
        if (timeSeconds < 60) {
            return `${Math.ceil(timeSeconds)}s`;
        } else if (timeSeconds < 3600) {
            return `${Math.ceil(timeSeconds / 60)}m`;
        } else {
            return `${Math.ceil(timeSeconds / 3600)}h`;
        }
    }
}

export { FileManager, FileMemoryManager };