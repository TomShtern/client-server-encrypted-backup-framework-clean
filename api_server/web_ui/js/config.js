/**
 * CyberBackup Client - Configuration
 * Centralized settings for ports, constants, and validation rules.
 */

const API_CONFIG = {
    API_PORT: 9090,
    STATIC_PORT: 9091,

    isFileProtocol() {
        return globalThis.location?.protocol === 'file:';
    },

    getApiBaseUrl() {
        const { location } = globalThis;
        if (!location) return '';

        if (location.protocol === 'file:') {
            console.warn('[API Config] Page opened via file:// protocol - API calls will not work');
            return '';
        }

        const { hostname = 'localhost', port, protocol } = location;
        const currentPort = Number.parseInt(port, 10) || (protocol === 'https:' ? 443 : 80);

        // If we are served from the API port, use relative path (empty string)
        if (currentPort === this.API_PORT) {
            return '';
        }

        // Otherwise (e.g. VS Code Live Server), point to the API port
        return `http://${hostname}:${this.API_PORT}`;
    },

    showFileProtocolWarning(toastFn) {
        if (typeof toastFn === 'function') {
            toastFn(
                '⚠️  Running from file:// - API features disabled. Use HTTP server for full functionality.',
                'warn',
                8000
            );
        }
        console.warn(
            '[API Config] Page opened via file:// protocol.\n' +
            'To enable API features, run: python api_server/cyberbackup_api_server.py\n' +
            'Then open: http://localhost:9090'
        );
    }
};

const CONSTANTS = {
    MAX_FILE_SIZE: 1024 * 1024 * 1024, // 1GB
    USERNAME_PATTERN: /^[\w\-. @]+$/,
};

const FILE_VALIDATION = {
    maxSize: CONSTANTS.MAX_FILE_SIZE,
    allowedExtensions: ['.zip', '.tar', '.tgz', '.gz', '.tar.gz'],
    allowedMimeTypes: [
        'application/zip',
        'application/x-zip-compressed',
        'application/x-tar',
        'application/gzip',
        'application/x-gzip',
        'application/x-gtar',
        'application/octet-stream' // Fallback
    ],
    validate(file) {
        if (!file) return { valid: false, error: 'No file selected' };

        if (file.size > this.maxSize) {
            return {
                valid: false,
                error: `File too large (${formatters.formatBytes(file.size)}). Max: ${formatters.formatBytes(this.maxSize)}`
            };
        }

        // Note: Extension check is advisory; server validates content
        return { valid: true };
    }
};
