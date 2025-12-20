/**
 * CyberBackup Client - UI Components
 * Log Management, File Handling, History, and Charts.
 * Depends on: config.js, core-utils.js, ui-core.js
 */
/* global dom, formatters, generateUUID, getStorageWithFallback, setStorageWithFallback, ProfessionalGUIEnhancements, downloadBlob, FILE_VALIDATION */

// --- Log Management ---

class LogStore {
    constructor(container, options = {}) {
        this.container = container;
        this.maxLogs = options.maxLogs || 50;
        this.logEntryCount = options.logEntryCount || dom.logEntryCount;
        this.logsEmptyState = options.logsEmptyState || dom.logsEmptyState;
        this.logs = [];
        this.visibleCount = 0;

        // Filter state
        this.currentQuery = '';
        this.currentLevel = 'all';
        this.recentOnly = false;
        this.RECENT_WINDOW_MS = 5 * 60 * 1000;

        // DOM refs for filtering
        this.searchInput = options.searchInput || dom.logSearchInput;
        this.searchClearBtn = options.searchClearBtn || dom.searchClearBtn;
        this.filterButtons = options.filterButtons || dom.logFilters;
        this.segmentIndicator = options.segmentIndicator || dom.segmentIndicator;
        this.recentFilterBtn = options.recentFilterBtn || dom.filterRecentLogsBtn;
        this.emptyTitle = options.emptyTitle || dom.logsEmptyTitle;
        this.emptyDesc = options.emptyDesc || dom.logsEmptyDesc;

        this.defaultEmptyTitle = this.emptyTitle?.textContent || 'No activity yet';
        this.defaultEmptyDesc = this.emptyDesc?.textContent || 'Connect and start a backup to see activity.';

        // Initialize filtering UI
        this.#initializeFiltering();
    }

    #initializeFiltering() {
        if (!this.searchInput || !this.container) return;

        // Search input (debounced)
        let searchTimeout;
        this.searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.currentQuery = (this.searchInput.value || '').toLowerCase().trim();
                if (this.searchClearBtn) this.searchClearBtn.hidden = !this.currentQuery;
                this.applyFilters();
            }, 200);
        });

        // Clear search button
        this.searchClearBtn?.addEventListener('click', () => {
            this.searchInput.value = '';
            this.currentQuery = '';
            this.searchClearBtn.hidden = true;
            this.applyFilters();
            this.searchInput.focus();
        });

        // Level filter buttons
        for (const btn of this.filterButtons || []) {
            btn.addEventListener('click', () => this.#setActiveFilterButton(btn));
        }

        // Recent logs toggle
        if (this.recentFilterBtn) {
            this.recentFilterBtn.setAttribute('aria-pressed', 'false');
            this.recentFilterBtn.title = 'Show only the last 5 minutes of log entries';
            this.recentFilterBtn.addEventListener('click', () => {
                this.recentOnly = !this.recentOnly;
                this.recentFilterBtn.setAttribute('aria-pressed', this.recentOnly ? 'true' : 'false');
                this.recentFilterBtn.classList.toggle('active', this.recentOnly);
                this.recentFilterBtn.title = this.recentOnly
                    ? 'Filtering to last 5 minutes (click to show all)'
                    : 'Show only the last 5 minutes of log entries';
                this.applyFilters();
            });
        }

        // Initial state
        if (this.searchClearBtn) this.searchClearBtn.hidden = true;
        const initialBtn = (this.filterButtons || []).find((b) => b.classList.contains('active')) || (this.filterButtons || [])[0];
        if (initialBtn) this.#setActiveFilterButton(initialBtn);
    }

    #setActiveFilterButton(btn) {
        if (!btn) return;

        for (const b of this.filterButtons || []) {
            const active = b === btn;
            b.classList.toggle('active', active);
            b.setAttribute('aria-pressed', active ? 'true' : 'false');
        }

        this.currentLevel = (btn.dataset.level || 'all').toLowerCase();

        if (this.segmentIndicator && btn.offsetParent) {
            this.segmentIndicator.style.left = `${btn.offsetLeft}px`;
            this.segmentIndicator.style.width = `${btn.offsetWidth}px`;
        }

        this.applyFilters();
    }

    #getEntryLevel(el) {
        const raw = (el.dataset.level || '').toLowerCase();
        if (raw) return raw;
        if (el.classList.contains('log-error')) return 'error';
        if (el.classList.contains('log-warn')) return 'warn';
        if (el.classList.contains('log-info')) return 'info';
        if (el.classList.contains('log-success')) return 'success';
        return 'info';
    }

    #levelMatches(level, entryLevel) {
        if (level === 'all') return true;
        if (level === 'info') return entryLevel === 'info' || entryLevel === 'success';
        return entryLevel === level;
    }

    #updateEmptyCopy({ totalLogs, visibleLogs }) {
        if (!this.logsEmptyState) return;

        if (visibleLogs > 0) {
            this.logsEmptyState.hidden = true;
            return;
        }

        this.logsEmptyState.hidden = false;

        if (!this.emptyTitle || !this.emptyDesc) return;

        if (totalLogs === 0) {
            this.emptyTitle.textContent = this.defaultEmptyTitle;
            this.emptyDesc.textContent = this.defaultEmptyDesc;
            return;
        }

        if (this.currentQuery) {
            this.emptyTitle.textContent = 'No matching logs';
            this.emptyDesc.textContent = 'Try clearing search or changing the filter.';
            return;
        }

        if (this.recentOnly) {
            this.emptyTitle.textContent = 'No recent logs';
            this.emptyDesc.textContent = 'Try again after activity, or disable the recent filter.';
            return;
        }

        if (this.currentLevel !== 'all') {
            this.emptyTitle.textContent = `No ${this.currentLevel} logs`;
            this.emptyDesc.textContent = 'Try a different level or clear the filter.';
            return;
        }

        this.emptyTitle.textContent = this.defaultEmptyTitle;
        this.emptyDesc.textContent = this.defaultEmptyDesc;
    }

    applyFilters() {
        const logEntries = this.container.querySelectorAll('[data-log-entry]');
        const query = this.currentQuery;
        const now = Date.now();

        let visibleCount = 0;
        for (const entry of logEntries) {
            const text = entry.textContent.toLowerCase();
            const entryLevel = this.#getEntryLevel(entry);

            const ts = Number(entry.dataset.ts);
            const withinRecentWindow = !Number.isFinite(ts) || (now - ts) <= this.RECENT_WINDOW_MS;

            const visible = (!query || text.includes(query))
                && this.#levelMatches(this.currentLevel, entryLevel)
                && (!this.recentOnly || withinRecentWindow);
            entry.style.display = visible ? '' : 'none';
            if (visible) visibleCount++;
        }

        this.setVisibleCount(visibleCount);
        this.#updateEmptyCopy({ totalLogs: logEntries.length, visibleLogs: visibleCount });
    }

    search(query) {
        this.currentQuery = (query || '').toLowerCase().trim();
        if (this.searchInput) this.searchInput.value = query || '';
        if (this.searchClearBtn) this.searchClearBtn.hidden = !this.currentQuery;
        this.applyFilters();
    }

    setLevel(level) {
        this.currentLevel = level || 'all';
        const btn = (this.filterButtons || []).find(b => (b.dataset.level || 'all').toLowerCase() === this.currentLevel);
        if (btn) this.#setActiveFilterButton(btn);
    }

    setRecentOnly(enabled) {
        this.recentOnly = !!enabled;
        if (this.recentFilterBtn) {
            this.recentFilterBtn.setAttribute('aria-pressed', this.recentOnly ? 'true' : 'false');
            this.recentFilterBtn.classList.toggle('active', this.recentOnly);
        }
        this.applyFilters();
    }

    export(format = 'json') {
        const visibleEntries = Array.from(this.container.querySelectorAll('[data-log-entry]'))
            .filter(el => el.style.display !== 'none')
            .map(el => ({
                timestamp: el.dataset.ts ? new Date(Number(el.dataset.ts)).toISOString() : '',
                level: this.#getEntryLevel(el),
                phase: el.dataset.phase || 'GENERAL',
                message: el.querySelector('.log-message')?.textContent || ''
            }));

        const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
        let filename, data, blob;

        if (format === 'json') {
            filename = `logs_${timestamp}.json`;
            data = JSON.stringify(visibleEntries, null, 2);
            blob = new Blob([data], { type: 'application/json' });
        } else if (format === 'csv') {
            filename = `logs_${timestamp}.csv`;
            const header = 'Timestamp,Level,Phase,Message\n';
            const rows = visibleEntries.map(e =>
                `"${e.timestamp}","${e.level}","${e.phase}","${e.message.replace(/"/g, '""')}"`
            ).join('\n');
            data = header + rows;
            blob = new Blob([data], { type: 'text/csv' });
        } else {
            filename = `logs_${timestamp}.txt`;
            data = visibleEntries.map(e =>
                `[${e.timestamp}] [${e.level.toUpperCase()}] [${e.phase}] ${e.message}`
            ).join('\n');
            blob = new Blob([data], { type: 'text/plain' });
        }

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);

        return filename;
    }

    add(message, { level = 'info', phase = 'GENERAL' } = {}) {
        const entry = {
            id: generateUUID(),
            timestamp: new Date(),
            message,
            level,
            phase
        };

        this.logs.unshift(entry);
        if (this.logs.length > this.maxLogs) this.logs.pop();
        this.#render(entry);

        // Increment visible count (new entries are visible by default)
        this.visibleCount++;

        // Reapply filters to ensure consistency
        this.applyFilters();

        this.#syncEmptyAndCount();
    }

    clear() {
        this.logs = [];
        this.visibleCount = 0;
        if (this.container) this.container.innerHTML = '';
        this.applyFilters();
        this.#syncEmptyAndCount();
    }

    #syncEmptyAndCount() {
        if (this.logEntryCount) {
            this.logEntryCount.textContent = String(this.logs.length);
        }
        if (this.logsEmptyState) {
            this.logsEmptyState.hidden = this.visibleCount > 0;
        }
    }

    /**
     * Updates the visible count (called by filter logic)
     * @param {number} count
     */
    setVisibleCount(count) {
        this.visibleCount = count;
        this.#syncEmptyAndCount();
    }

    #render(entry) {
        if (!this.container) return;

        const div = document.createElement('div');
        div.className = `log-entry log-${entry.level}`;
        div.dataset.logEntry = '';
        div.dataset.level = entry.level;
        div.dataset.phase = entry.phase;
        div.dataset.ts = String(entry.timestamp.getTime());

        const timeSpan = document.createElement('span');
        timeSpan.className = 'log-time';
        timeSpan.textContent = formatters.time(entry.timestamp);

        const phaseSpan = document.createElement('span');
        phaseSpan.className = 'log-phase';
        phaseSpan.textContent = `[${entry.phase}]`;

        const msgSpan = document.createElement('span');
        msgSpan.className = 'log-message';
        msgSpan.textContent = entry.message;

        div.appendChild(timeSpan);
        div.appendChild(phaseSpan);
        div.appendChild(msgSpan);

        this.container.insertBefore(div, this.container.firstChild);

        // Prune DOM
        while (this.container.children.length > this.maxLogs) {
            this.container.lastChild.remove();
        }
    }
}

// --- File Management ---

class FileManager {
    constructor(input, dropZone, onFileSelect) {
        this.input = input;
        this.dropZone = dropZone;
        this.onFileSelect = onFileSelect;
        this.toast = null;
        this.announcer = null;
        this.#bindEvents();
    }

    setToast(toastManager) {
        this.toast = toastManager;
        return this;
    }

    setAnnouncer(announcer) {
        this.announcer = announcer;
        return this;
    }

    #bindEvents() {
        this.input?.addEventListener('change', (e) => this.#handleFiles(e.target.files));

        if (this.dropZone) {
            for (const eventName of ['dragenter', 'dragover', 'dragleave', 'drop']) {
                this.dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            }

            for (const eventName of ['dragenter', 'dragover']) {
                this.dropZone.addEventListener(eventName, () => this.dropZone.classList.add('drag-active'));
            }

            for (const eventName of ['dragleave', 'drop']) {
                this.dropZone.addEventListener(eventName, () => this.dropZone.classList.remove('drag-active'));
            }

            this.dropZone.addEventListener('drop', (e) => this.#handleFiles(e.dataTransfer.files));
            this.dropZone.addEventListener('click', () => this.input?.click());
        }

        // Clear button
        if (dom.clearFileBtn) {
            dom.clearFileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.clear();
            });
        }
    }

    #handleFiles(files) {
        if (!files?.length) {
            this.#announce('No file selected');
            return;
        }

        const file = files[0];
        const validation = FILE_VALIDATION.validate(file);
        if (!validation.valid) {
            this.#showValidationError(validation.error || 'Unsupported file');
            this.clear(false);
            return;
        }

        this.#clearErrorState();
        this.onFileSelect(file);
        ProfessionalGUIEnhancements.updateFileCardPreview(file);
        this.#announce(`Selected file ${file.name}, size ${formatters.formatBytes(file.size)}`);
    }

    clear(announce = true) {
        if (this.input) this.input.value = '';
        this.#clearErrorState();
        ProfessionalGUIEnhancements.updateFileCardPreview(null);
        this.onFileSelect(null);
        if (announce) this.#announce('File selection cleared');
    }

    getFile() {
        return this.input?.files?.[0];
    }

    #showValidationError(message) {
        this.toast?.show(message, 'error');
        this.dropZone?.classList.add('input-error');
        this.input?.classList.add('input-error');
        this.#announce(message);
    }

    #clearErrorState() {
        this.dropZone?.classList.remove('input-error');
        this.input?.classList.remove('input-error');
    }

    #announce(message) {
        if (this.announcer) {
            this.announcer.announce(message);
        } else if (dom.srLive) {
            dom.srLive.textContent = '';
            requestAnimationFrame(() => { dom.srLive.textContent = message; });
        }
    }
}

// --- Transfer History ---

class TransferHistory {
    #maxEntries = 10;
    #storageKey = 'cyberbackup-history';

    get entries() {
        try {
            const data = getStorageWithFallback(this.#storageKey);
            if (!data) return [];
            const parsed = JSON.parse(data);
            return Array.isArray(parsed) ? parsed : [];
        } catch {
            return [];
        }
    }

    add(transfer) {
        const { entries } = this;
        const {
            filename = 'unknown',
            size = 0,
            status = 'completed',
            serverAddress = '',
            jobId = '',
        } = transfer ?? {};

        // Validation
        const validatedEntry = {
            id: generateUUID(),
            jobId: String(jobId || ''),
            filename: String(filename || 'unknown'),
            size: Number(size) || 0,
            status: String(status || 'completed'),
            timestamp: new Date().toISOString(),
            serverAddress: String(serverAddress || ''),
        };

        entries.unshift(validatedEntry);
        entries.length = Math.min(entries.length, this.#maxEntries);

        try {
            setStorageWithFallback(this.#storageKey, JSON.stringify(entries));
        } catch (e) {
            console.warn('Failed to save transfer history:', e);
        }
    }

    clear() {
        setStorageWithFallback(this.#storageKey, '[]');
    }

    filter(filterFn) {
        return this.entries.filter(filterFn);
    }

    filterByStatus(status) {
        if (!status || status === 'all') return this.entries;
        return this.entries.filter(entry => entry.status === status);
    }

    export(format = 'json', entries = null) {
        const dataToExport = entries || this.entries;

        if (!dataToExport || dataToExport.length === 0) {
            return null;
        }

        const timestamp = new Date().toISOString().replaceAll(':', '-').split('.')[0];
        let filename, data, blob;

        if (format === 'json') {
            filename = `transfer-history_${timestamp}.json`;
            data = JSON.stringify(dataToExport, null, 2);
            blob = new Blob([data], { type: 'application/json' });
        } else if (format === 'csv') {
            filename = `transfer-history_${timestamp}.csv`;
            const header = 'Timestamp,Job ID,Filename,Size (bytes),Status,Server Address\n';
            const rows = dataToExport.map(e =>
                `"${e.timestamp}","${e.jobId || ''}","${e.filename}",${e.size},"${e.status}","${e.serverAddress}"`
            ).join('\n');
            data = header + rows;
            blob = new Blob([data], { type: 'text/csv' });
        } else {
            filename = `transfer-history_${timestamp}.txt`;
            data = dataToExport.map(e =>
                `[${e.timestamp}] ${e.filename} (${formatters.formatBytes(e.size)}) - ${e.status.toUpperCase()} - ${e.serverAddress}`
            ).join('\n');
            blob = new Blob([data], { type: 'text/plain' });
        }

        // Use shared download utility
        downloadBlob(blob, filename);
        return filename;
    }
}

// --- Additional Components (Sparkline, LogInspector) ---

class SparklineChart {
    constructor(canvasId, color = '#007bff') {
        const element = document.getElementById(canvasId);
        this.data = [];
        this.maxData = 20;
        this.color = color;

        if (element) {
            if (element.tagName === 'CANVAS') {
                this.canvas = element;
            } else {
                // Create canvas inside container
                this.canvas = document.createElement('canvas');
                this.canvas.style.width = '100%';
                this.canvas.style.height = '100%';
                this.canvas.style.display = 'block';
                element.appendChild(this.canvas);
            }

            this.ctx = this.canvas.getContext('2d');
            this.resize();
            window.addEventListener('resize', domUtils.debounce(() => this.resize(), 200));
        }
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.draw();
    }

    update(value) {
        this.data.push(value);
        if (this.data.length > this.maxData) this.data.shift();
        this.draw();
    }

    draw() {
        if (!this.ctx) return;
        const { width, height } = this.canvas;

        this.ctx.clearRect(0, 0, width, height);
        if (this.data.length < 2) return;

        const max = Math.max(...this.data, 1);
        const step = width / (this.maxData - 1);

        this.ctx.beginPath();
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';

        this.data.forEach((val, i) => {
            const x = i * step;
            const h = (val / max) * (height * 0.8); // 80% height usage
            const y = height - h;
            if (i === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);
        });

        this.ctx.stroke();
    }
}

class LogInspector {
    // Placeholder for enhanced log viewing features
    constructor() {
        // Init logic
    }
}
