import { debugLog } from '../core/debug-utils.js';

class BackupHistoryManager {
    constructor() {
        this.storageKey = 'cyberbackup_history';
        this.maxHistorySize = 50;
    }

    /**
     * Add a completed backup to history
     * @param {Object} backupInfo - Backup details
     */
    addBackup(backupInfo) {
        try {
            const backup = {
                id: Date.now().toString(36) + Math.random().toString(36).substr(2),
                timestamp: Date.now(),
                status: backupInfo.status || 'completed',
                filename: backupInfo.filename || 'unknown',
                fileSize: backupInfo.fileSize || 0,
                server: backupInfo.server || 'unknown',
                username: backupInfo.username || 'unknown',
                duration: backupInfo.duration || 0,
                transferSpeed: backupInfo.transferSpeed || 0,
                phase: backupInfo.phase || 'completed',
                clientId: backupInfo.clientId || null,
                error: backupInfo.error || null
            };

            const history = this.getHistory();
            history.unshift(backup);
            
            // Limit history size
            const trimmedHistory = history.slice(0, this.maxHistorySize);
            localStorage.setItem(this.storageKey, JSON.stringify(trimmedHistory));
            
            debugLog(`Backup added to history: ${backup.filename}`, 'BACKUP_HISTORY');
            return backup.id;
        } catch (error) {
            console.warn('Failed to add backup to history:', error);
            return null;
        }
    }

    /**
     * Get backup history
     * @returns {Array} Array of backup records
     */
    getHistory() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.warn('Failed to load backup history:', error);
            return [];
        }
    }

    /**
     * Get formatted history for UI display
     * @returns {Array} Array of formatted backup records
     */
    getFormattedHistory() {
        const history = this.getHistory();
        return history.map(backup => ({
            ...backup,
            dateFormatted: this.formatDate(backup.timestamp),
            timeAgo: this.formatTimeAgo(backup.timestamp),
            sizeFormatted: this.formatBytes(backup.fileSize),
            durationFormatted: this.formatDuration(backup.duration),
            speedFormatted: this.formatSpeed(backup.transferSpeed),
            statusIcon: this.getStatusIcon(backup.status),
            statusColor: this.getStatusColor(backup.status)
        }));
    }

    /**
     * Get successful backups only
     * @returns {Array} Array of successful backup records
     */
    getSuccessfulBackups() {
        return this.getHistory().filter(backup => backup.status === 'completed');
    }

    /**
     * Get failed backups only
     * @returns {Array} Array of failed backup records
     */
    getFailedBackups() {
        return this.getHistory().filter(backup => backup.status === 'failed' || backup.error);
    }

    /**
     * Get backup statistics
     * @returns {Object} Statistics object
     */
    getStatistics() {
        const history = this.getHistory();
        const successful = this.getSuccessfulBackups();
        const failed = this.getFailedBackups();
        
        const totalSize = successful.reduce((sum, backup) => sum + (backup.fileSize || 0), 0);
        const totalDuration = successful.reduce((sum, backup) => sum + (backup.duration || 0), 0);
        const averageSpeed = successful.length > 0 ? 
            successful.reduce((sum, backup) => sum + (backup.transferSpeed || 0), 0) / successful.length : 0;

        return {
            totalBackups: history.length,
            successfulBackups: successful.length,
            failedBackups: failed.length,
            successRate: history.length > 0 ? ((successful.length / history.length) * 100).toFixed(1) : '0',
            totalSizeTransferred: totalSize,
            totalSizeFormatted: this.formatBytes(totalSize),
            averageSpeed,
            averageSpeedFormatted: this.formatSpeed(averageSpeed),
            totalDuration,
            totalDurationFormatted: this.formatDuration(totalDuration)
        };
    }

    /**
     * Clear backup history
     */
    clearHistory() {
        localStorage.removeItem(this.storageKey);
        debugLog('Backup history cleared', 'BACKUP_HISTORY');
    }

    /**
     * Remove a specific backup from history
     * @param {string} backupId - ID of backup to remove
     */
    removeBackup(backupId) {
        try {
            const history = this.getHistory();
            const filteredHistory = history.filter(backup => backup.id !== backupId);
            localStorage.setItem(this.storageKey, JSON.stringify(filteredHistory));
            debugLog(`Backup removed from history: ${backupId}`, 'BACKUP_HISTORY');
        } catch (error) {
            console.warn('Failed to remove backup from history:', error);
        }
    }

    // Helper methods for formatting
    formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

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

    formatBytes(bytes) {
        if (bytes === 0) {
            return '0 Bytes';
        }
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(seconds) {
        if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        }
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    }

    formatSpeed(bytesPerSecond) {
        if (bytesPerSecond === 0) {
            return '0 B/s';
        }
        const k = 1024;
        const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
        const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k));
        return parseFloat((bytesPerSecond / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getStatusIcon(status) {
        const icons = {
            'completed': '✅',
            'failed': '❌',
            'cancelled': '⏹️',
            'in_progress': '⏳'
        };
        return icons[status] || '❓';
    }

    getStatusColor(status) {
        const colors = {
            'completed': 'var(--success)',
            'failed': 'var(--error)',
            'cancelled': 'var(--warning)',
            'in_progress': 'var(--primary)'
        };
        return colors[status] || 'var(--text-muted)';
    }
}

export { BackupHistoryManager };