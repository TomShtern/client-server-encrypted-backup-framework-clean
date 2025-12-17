/**
 * CyberBackup Client - Main Application
 * Orchestrates Core Logic and UI Components.
 * Depends on: core-utils.js, core.js, ui.js
 */
/* global DemoMode, generateUUID, getStorageWithFallback, setStorageWithFallback */

/**
 * Transfer history manager.
 * Stores last N completed transfers in localStorage (with in-memory fallback).
 */
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

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);

    return filename;
  }
}

/**
 * Main application controller for CyberBackup Client.
 * Orchestrates UI components, state management, and API/WebSocket interactions.
 *
 * @class App
 * @property {StateStore} state - Reactive state container
 * @property {ApiClient} api - REST API client
 * @property {SocketClient} socket - WebSocket client for real-time updates
 * @property {ConnectionMonitor} monitor - Connection health monitor
 * @property {ToastManager} toast - Toast notification manager
 * @property {ScreenReaderAnnouncer} announcer - Accessibility announcer
 * @property {LogStore} logs - Activity log manager
 * @property {ThemeManager} theme - Theme manager
 * @property {TransferHistory} transferHistory - Stores recent completed/failed transfers
 * @property {FileManager} fileManager - File selection handler
 * @property {AdvancedSettings} advancedSettings - Advanced settings manager
 * @property {DemoMode} demo - Demo mode controller
 * @property {boolean} operationInProgress - Lock flag for async operations
 */
class App {
  constructor() {
    // Initialize State
    /** @type {StateStore<AppState>} */
    this.state = new StateStore({
      connected: false,
      jobId: null,
      status: 'idle', // idle, uploading, paused, completed, error
      progress: 0,
      speed: 0,
      bytesTransferred: 0,
      totalBytes: 0,
      startTime: null,
      serverAddress: 'localhost:1256',
      username: 'User-' + Math.floor(Math.random() * 10000),
      operationInProgress: false,
      buttonsEnabled: {
        primary: true,
        pause: false,
        resume: false,
        stop: false
      }
    });

    // Track last rendered values to support lightweight UI pulse animations.
    this._valuePulseTimers = new WeakMap();

    // Initialize Managers
    this.api = new ApiClient(API_CONFIG.getApiBaseUrl());
    this.toast = new ToastManager(dom.toastStack);
    this.announcer = new ScreenReaderAnnouncer(dom.srLive);
    this.logs = new LogStore(dom.logContainer, {
      maxLogs: 50,
      logEntryCount: dom.logEntryCount,
      logsEmptyState: dom.logsEmptyState,
      searchInput: dom.logSearchInput,
      searchClearBtn: dom.searchClearBtn,
      filterButtons: dom.logFilters,
      segmentIndicator: dom.segmentIndicator,
      recentFilterBtn: dom.filterRecentLogsBtn,
      emptyTitle: dom.logsEmptyTitle,
      emptyDesc: dom.logsEmptyDesc
    });
    this.theme = new ThemeManager(dom.themeToggle, dom.themeLabel);
    this.transferHistory = new TransferHistory();

    // Capture the currently active transfer metadata (filename/size) for history.
    this._activeTransferMeta = null;

    this.fileManager = new FileManager(dom.fileInput, dom.fileDropZone, (file) => this.#onFileSelected(file));
    this.fileManager.setToast(this.toast).setAnnouncer(this.announcer);

    this.advancedSettings = new AdvancedSettings({
      chunkInput: dom.advChunkSize,
      retryInput: dom.advRetryLimit,
      resetButton: dom.advResetBtn,
      restoreLink: dom.advRestoreDefaults,
      toast: this.toast,
      announcer: this.announcer
    });

    this._globalHandlersRegistered = false;

    // Initialize Networking
    this.socket = new SocketClient({
      url: API_CONFIG.getApiBaseUrl(),
      onConnect: () => this.#onSocketConnect(),
      onDisconnect: () => this.#onSocketDisconnect(),
      onError: (err) => this.#onSocketError(err),
      onStatus: (status) => this.#onServerStatus(status),
      onProgress: (progress) => this.#onProgress(progress),
      onFileReceipt: (receipt) => this.#onFileReceipt(receipt)
    });

    this.monitor = new ConnectionMonitor({
      api: this.api,
      onResult: (res) => this.#onMonitorResult(res)
    });

    // Demo mode controller
    this.demo = new DemoMode(this);

    // Bind UI Events
    this.#bindEvents();

    // Cache the last rendered transfer history signature to avoid redundant DOM work.
    this._lastTransferHistorySig = '';
  }

  async init() {
    // Register global error handlers as early as possible.
    // Must happen during init (not in render or file selection) to avoid repeated work.
    this.#setupGlobalErrorHandlers();

    ProfessionalGUIEnhancements.init();

    // Subscribe to state changes early so the UI can render even when offline
    this.state.subscribe((state) => this.#render(state));

    // Render persisted transfer history immediately (independent of network state)
    this.#renderTransferHistory({ force: true });

    const isFileProtocol = API_CONFIG.isFileProtocol();

    // Check protocol
    if (isFileProtocol) {
      API_CONFIG.showFileProtocolWarning(this.toast.show.bind(this.toast));
      this.showInlineBanner({
        severity: 'error',
        title: 'API disabled in file:// mode',
        body: 'Open the client UI from the API server to enable live monitoring and actions.',
        actionHref: 'http://localhost:9090',
        actionText: 'Open http://localhost:9090'
      });

      // Avoid confusing failures: file:// mode cannot reach the API.
      this.setConnectionStatus('API not available in file:// mode. Open via http://localhost:9090', 'error');

      if (dom.primaryActionBtn && !this.demo.enabled) {
        dom.primaryActionBtn.disabled = true;
      }
    }

    // IMPORTANT:
    // When the UI is served standalone (e.g., via start_client_gui.py), the API server may not be running.
    // Avoid automatic network calls on load to prevent noisy console errors.
    const isHostedByApiServer =
      !isFileProtocol && (globalThis.location?.port === String(API_CONFIG.API_PORT));

    if (isHostedByApiServer) {
      this.hideInlineBanner();
      this.monitor.start();
      await this.socket.start();
    } else {
      // Set initial status to offline/unknown without touching the network.
      if (globalThis.updateDualServerStatus) {
        globalThis.updateDualServerStatus({ apiOnline: false, backupOnline: false });
      }

      // Make the "offline" state visually obvious (quality/status fields) without triggering network calls.
      this.#onMonitorResult({ ok: false, quality: 'offline', timestamp: 0 });
      this.setConnectionStatus(
        'API server not detected. Start the API server and open http://localhost:9090 for live status.',
        'info'
      );

      if (!isFileProtocol) {
        this.showInlineBanner({
          severity: 'info',
          title: 'Offline UI mode',
          body: 'Live status is disabled on this origin. Start the API server and open http://localhost:9090 for full functionality.',
          actionHref: 'http://localhost:9090',
          actionText: 'Open live UI'
        });
      }

      this.logs.add(
        'API server not detected on this origin. Network monitoring will start after you connect.',
        { phase: 'NET', level: 'warn' }
      );
    }

    if (this.demo.enabled && dom.logDemoBtn) {
      dom.logDemoBtn.hidden = false;
      dom.logDemoBtn.title = 'Run a simulated transfer (demo mode)';
    }

    // GPU Optimization: Pause animations when tab is hidden
    document.addEventListener('visibilitychange', () => {
      const state = document.hidden ? 'paused' : 'running';
      document.documentElement.style.setProperty('--animation-play-state', state);
    });

    this.logs.add('Application initialized', { phase: 'INIT' });
  }

  // --- Event Handlers ---

  #bindEvents() {
    // Primary Action Button - State Machine (CONNECT ↔ DISCONNECT)
    dom.primaryActionBtn?.addEventListener('click', () => this.#handlePrimaryAction());

    // Backup Controls
    dom.pauseBtn?.addEventListener('click', () => this.#handlePause());
    dom.resumeBtn?.addEventListener('click', () => this.#handleResume());
    dom.stopBtn?.addEventListener('click', () => this.#handleStop());

    // Demo mode helper (hidden unless enabled)
    dom.logDemoBtn?.addEventListener('click', () => this.demo.start());

    // Transfer history
    dom.transferHistoryClearBtn?.addEventListener('click', () => this.#handleClearTransferHistory());
    dom.transferHistoryExportBtn?.addEventListener('click', (e) => {
      // Show export format menu on click
      this.#showExportMenu(e);
    });
    dom.transferHistoryFilter?.addEventListener('change', (e) => {
      this.#handleTransferHistoryFilter(e.target.value);
    });

    // Settings
    dom.settingsToggle?.addEventListener('click', () => {
      dom.settingsPanel?.classList.toggle('open');
    });

    // Inline banner dismiss
    dom.inlineErrorDismiss?.addEventListener('click', () => this.hideInlineBanner());
  }

  #handleClearTransferHistory() {
    try {
      const { entries } = this.transferHistory;
      if (!entries || entries.length === 0) {
        this.toast.show('Transfer history is already empty', 'info');
        return;
      }

      this.transferHistory.clear();
      this.#renderTransferHistory({ force: true });

      this.logs.add('Transfer history cleared', { phase: 'UI' });
      this.toast.show('Transfer history cleared', 'info');
      this.announcer.announce('Transfer history cleared');
    } catch (error) {
      ErrorBoundary.handle(error, 'Clear Transfer History');
    }
  }

  #handleExportTransferHistory(format = 'json') {
    try {
      const filteredEntries = this.#getFilteredTransfers();

      if (!filteredEntries || filteredEntries.length === 0) {
        this.toast.show('No transfers to export', 'info');
        return;
      }

      const filename = this.transferHistory.export(format, filteredEntries);

      if (!filename) {
        this.toast.show('Failed to export transfer history', 'error');
        return;
      }

      this.logs.add(`Exported ${filteredEntries.length} transfers to ${filename}`, { phase: 'UI' });
      this.toast.show(`Exported ${filteredEntries.length} transfers as ${format.toUpperCase()}`, 'success');
      this.announcer.announce(`Exported ${filteredEntries.length} transfers`);
    } catch (error) {
      ErrorBoundary.handle(error, 'Export Transfer History');
    }
  }

  #showExportMenu(event) {
    const existingMenu = document.getElementById('exportFormatMenu');
    if (existingMenu) {
      existingMenu.remove();
      return;
    }

    const menu = document.createElement('div');
    menu.id = 'exportFormatMenu';
    menu.className = 'export-menu';
    menu.innerHTML = `
      <button class='export-menu-item' data-format='json'>
        <span class='export-icon'>📄</span>
        <span>Export as JSON</span>
      </button>
      <button class='export-menu-item' data-format='csv'>
        <span class='export-icon'>📊</span>
        <span>Export as CSV</span>
      </button>
    `;

    menu.style.position = 'absolute';
    menu.style.top = `${event.clientY}px`;
    menu.style.left = `${event.clientX}px`;

    menu.querySelectorAll('.export-menu-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const { format } = e.currentTarget.dataset;
        this.#handleExportTransferHistory(format);
        menu.remove();
      });
    });

    document.addEventListener('click', function closeMenu(e) {
      if (!menu.contains(e.target)) {
        menu.remove();
        document.removeEventListener('click', closeMenu);
      }
    });

    document.body.appendChild(menu);
  }

  #getFilteredTransfers() {
    const filter = dom.transferHistoryFilter?.value || 'all';

    if (filter === 'all') {
      return this.transferHistory.entries;
    }

    // Map UI filter values to status values
    if (filter === 'success') {
      return this.transferHistory.filter(entry => {
        const status = String(entry?.status || 'completed').toLowerCase();
        return status === 'completed' || status === 'success';
      });
    }

    if (filter === 'fail') {
      return this.transferHistory.filter(entry => {
        const status = String(entry?.status || 'completed').toLowerCase();
        return status !== 'completed' && status !== 'success';
      });
    }

    return this.transferHistory.entries;
  }

  #handleTransferHistoryFilter(filterValue) {
    try {
      this.#renderTransferHistory({ force: true });

      const count = this.#getFilteredTransfers().length;
      let filterName;

      if (filterValue === 'all') {
        filterName = 'all transfers';
      } else if (filterValue === 'success') {
        filterName = 'successful transfers';
      } else {
        filterName = 'failed transfers';
      }

      this.announcer.announce(`Showing ${filterName}: ${count} items`);
    } catch (error) {
      ErrorBoundary.handle(error, 'Filter Transfer History');
    }
  }

  showInlineBanner({ severity = 'error', title = 'Notice', body = '', actionHref = '', actionText = 'Open' } = {}) {
    const banner = dom.inlineErrorBanner;
    if (!banner || !dom.inlineErrorTitle || !dom.inlineErrorBody) return;

    banner.hidden = false;
    banner.classList.remove('is-info', 'is-warn', 'is-error');
    let cls = 'is-error';
    if (severity === 'warn') cls = 'is-warn';
    else if (severity === 'info') cls = 'is-info';
    banner.classList.add(cls);

    dom.inlineErrorTitle.textContent = String(title);
    dom.inlineErrorBody.textContent = String(body);

    if (dom.inlineErrorAction) {
      const showAction = Boolean(actionHref);
      dom.inlineErrorAction.hidden = !showAction;
      if (showAction) {
        dom.inlineErrorAction.href = String(actionHref);
        dom.inlineErrorAction.textContent = String(actionText || 'Open');
      }
    }
  }

  hideInlineBanner() {
    if (!dom.inlineErrorBanner) return;
    dom.inlineErrorBanner.hidden = true;
  }

  /**
   * State machine for primary action button.
   * Toggles between connect and disconnect based on current state.
   */
  #handlePrimaryAction() {
    if (this.state.snapshot.operationInProgress) {
      this.toast.show('Operation in progress, please wait…', 'info');
      return;
    }
    if (this.state.snapshot.connected) {
      this.#handleDisconnect();
    } else {
      this.#handleConnect();
    }
  }

  async #handleConnect() {
    if (this.state.snapshot.operationInProgress) return;
    if (API_CONFIG.isFileProtocol()) {
      this.toast.show('API unavailable in file:// mode. Open http://localhost:9090 instead.', 'warn');
      // Use inline banner as primary indicator for file:// protocol error
      this.showInlineBanner({
        severity: 'error',
        title: 'Cannot connect in file:// mode',
        body: 'Open the Web UI from the API server to connect and start backups.',
        actionHref: 'http://localhost:9090',
        actionText: 'Open live UI'
      });
      // Hide transient status message to avoid duplication
      this.#hideConnectionStatus();
      return;
    }

    const addressInput = dom.serverInput?.value || dom.serverAddress?.value;
    const parsed = formatters.parseServerAddress(addressInput);

    const username = (dom.usernameInput?.value || '').trim() || this.state.snapshot.username;

    if (!parsed) {
      this.toast.show('Invalid server address format. Use host:port', 'error');
      this.#updateConnectionStatus('Invalid address format', 'error');
      return;
    }

    if (!CONSTANTS.USERNAME_PATTERN.test(username)) {
      this.toast.show('Invalid username. Use letters, numbers, spaces, dot, dash, or @.', 'error');
      this.#updateConnectionStatus('Invalid username', 'error');
      return;
    }

    try {
      this.state.update({ operationInProgress: true });
      // Update button to connecting state
      this.#setButtonState('connecting');
      this.#updateConnectionStatus('Connecting...', 'pending');

      await this.api.connect({
        host: parsed.host,
        port: parsed.port,
        username
      });

      // Start monitoring + websocket AFTER we know the API server is reachable.
      this.monitor.start();
      if (!this.socket.socket) {
        await this.socket.start();
      }

      this.state.update({
        connected: true,
        serverAddress: `${parsed.host}:${parsed.port}`,
        username
      });

      this.#setButtonState('connected');
      this.#updateConnectionStatus(`Connected to ${parsed.host}:${parsed.port}`, 'success');
      this.hideInlineBanner();
      this.toast.show('Connected to backup server', 'success');
      this.logs.add(`Connected to ${parsed.host}:${parsed.port}`, { phase: 'NET' });

    } catch (error) {
      this.#setButtonState('idle');
      // Use inline banner as primary offline indicator
      this.showInlineBanner({
        severity: 'error',
        title: 'Connection failed',
        body: 'Could not connect. Ensure the API server is running (port 9090) and the backup server is reachable (port 1256).',
        actionHref: 'http://localhost:9090',
        actionText: 'Open live UI'
      });
      // Hide transient status message to avoid duplication
      this.#hideConnectionStatus();
      ErrorBoundary.handle(error, 'Connection');
      } finally {
        this.state.update({ operationInProgress: false });
    }
  }

  async #handleDisconnect() {
      if (this.state.snapshot.operationInProgress) return;
    try {
        this.state.update({ operationInProgress: true });
      this.#setButtonState('disconnecting');
      this.#updateConnectionStatus('Disconnecting...', 'pending');

      await this.api.disconnect();
      this.state.update({ connected: false, status: 'idle' });

      this.#setButtonState('idle');
      this.#updateConnectionStatus('Disconnected', 'info');
      this.toast.show('Disconnected from server', 'info');
      this.logs.add('Disconnected', { phase: 'NET' });
    } catch (error) {
      this.#setButtonState('connected'); // Restore if disconnect failed
      this.#updateConnectionStatus('Disconnect failed', 'error');
      ErrorBoundary.handle(error, 'Disconnect');
    } finally {
      this.state.update({ operationInProgress: false });
    }
  }

  /**
   * Updates primary action button state with visual feedback.
   * @param {'idle'|'connecting'|'connected'|'disconnecting'} state
   */
  #setButtonState(state) {
    const btn = dom.primaryActionBtn;
    const text = dom.primaryBtnText;
    const spinner = dom.primaryBtnSpinner;
    if (!btn) return;

    const configByState = {
      idle: { disabled: false, loading: false, connected: false, text: 'CONNECT', spinner: false },
      connecting: { disabled: true, loading: true, connected: false, text: 'CONNECTING', spinner: true },
      connected: { disabled: false, loading: false, connected: true, text: 'DISCONNECT', spinner: false },
      disconnecting: { disabled: true, loading: true, connected: true, text: 'DISCONNECTING', spinner: true },
    };

    const cfg = configByState[state] || configByState.idle;
    btn.disabled = cfg.disabled;
    btn.classList.toggle('loading', cfg.loading);
    btn.classList.toggle('connected', cfg.connected);
    if (text) text.textContent = cfg.text;
    if (spinner) spinner.classList.toggle('active', cfg.spinner);

    // Update troubleshoot button based on connection state
    if (dom.troubleshootChip) {
      const isConnected = state === 'connected';
      dom.troubleshootChip.disabled = !isConnected;
      dom.troubleshootChip.title = isConnected ?
        'Troubleshoot connection issues' :
        'Connect to enable diagnostics';
    }
  }

  /**
   * Updates connection status message area.
   * @param {string} message
   * @param {'pending'|'success'|'error'|'info'} type
   */
  #updateConnectionStatus(message, type = 'info') {
    const container = dom.connectionStatusMessage;
    const textEl = dom.connectionStatusText;
    const iconEl = dom.connectionStatusIcon;
    const spinnerEl = dom.connectionStatusSpinner;
    if (!container || !textEl) return;

    // Show container if hidden
    if (container.hidden) container.hidden = false;

    // Update text
    textEl.textContent = message;

    // Update classes for styling
    container.className = 'connection-status-message ' + type + (type === 'pending' ? ' loading' : '');

    // Spinner (inline, near status text)
    if (spinnerEl) {
      spinnerEl.classList.toggle('active', type === 'pending');
    }

    // Update icon
    if (iconEl) {
      const icons = { pending: '⏳', success: '✓', error: '✕', info: 'ℹ' };
      iconEl.textContent = icons[type] || '';
    }
  }

  /**
   * Hides connection status message (to avoid redundancy with inline banner).
   */
  #hideConnectionStatus() {
    const container = dom.connectionStatusMessage;
    if (container) {
      container.hidden = true;
    }
  }

  #onFileSelected(file) {
    if (file) {
      this.logs.add(`File selected: ${file.name} (${formatters.formatBytes(file.size)})`, { phase: 'FILE' });

      // Keep stats useful even before progress events arrive.
      this.state.update({
        totalBytes: file.size,
        bytesTransferred: 0,
        progress: 0,
      });

      // Update file label if it exists
      // Reset progress if new file selected
      if (this.state.snapshot.status === 'completed' || this.state.snapshot.status === 'error') {
        this.state.update({ status: 'idle', progress: 0, bytesTransferred: 0 });
      }

      // Auto-start backup if connected
      if (this.state.snapshot.connected) {
        this.#handleStartBackup(file);
      }
    }
  }

  async #handleStartBackup(fileArg) {
    if (this.operationInProgress) return;
    const file = fileArg || this.fileManager.input?.files?.[0];
    if (!file) {
      this.toast.show('Please select a file first', 'warn');
      return;
    }

    if (!this.state.snapshot.connected) {
      this.toast.show('Please connect to a server first', 'warn');
      return;
    }

    try {
      this.state.update({ operationInProgress: true });
      this.state.update({
        status: 'uploading',
        progress: 0,
        startTime: Date.now(),
        totalBytes: file.size,
        bytesTransferred: 0,
      });

      this._activeTransferMeta = {
        filename: file.name,
        size: file.size,
      };

      const [host, port] = this.state.snapshot.serverAddress.split(':');
      const options = this.advancedSettings.getOptions();

      const result = await this.api.startBackup({
        file,
        username: this.state.snapshot.username,
        host,
        port,
        options
      });

      this.state.update({ jobId: result.job_id });
      this.socket.watchJob(result.job_id);

      this.logs.add(`Backup started: ${result.job_id}`, { phase: 'BACKUP' });
      this.toast.show('Backup started successfully', 'success');

    } catch (error) {
      this.state.update({ status: 'error' });
      ErrorBoundary.handle(error, 'Start Backup');
    } finally {
      this.state.update({ operationInProgress: false });
    }
  }

  async #handlePause() {
    try {
      if (this.demo.active) {
        this.demo.pause();
        return;
      }

      await this.api.pause();
      this.state.update({ status: 'paused' });
      this.logs.add('Backup paused', { phase: 'BACKUP' });
    } catch (error) {
      ErrorBoundary.handle(error, 'Pause');
    }
  }

  async #handleResume() {
    try {
      if (this.demo.active) {
        this.demo.resume();
        return;
      }

      await this.api.resume();
      this.state.update({ status: 'uploading' });
      this.logs.add('Backup resumed', { phase: 'BACKUP' });
    } catch (error) {
      ErrorBoundary.handle(error, 'Resume');
    }
  }

  async #handleStop() {
    try {
      if (this.demo.active) {
        this.demo.stop();
        return;
      }

      await this.api.stop();
      this.state.update({ status: 'idle', progress: 0, jobId: null });
      this.socket.clearJob();
      this._activeTransferMeta = null;
      this.logs.add('Backup stopped', { phase: 'BACKUP' });
      this.toast.show('Backup stopped', 'info');
    } catch (error) {
      ErrorBoundary.handle(error, 'Stop');
    }
  }

  // --- Socket & Monitor Callbacks ---

  #onSocketConnect() {
    this.logs.add('WebSocket connected', { phase: 'NET' });
  }

  #onSocketDisconnect() {
    this.logs.add('WebSocket disconnected', { phase: 'NET', level: 'warn' });
  }

  #onSocketError(err) {
    console.error('Socket error:', err);

    // Mirror socket errors into the status strip as a non-blocking hint.
    this.setConnectionStatus('WebSocket error - status updates may be delayed', 'info');
  }

  #onServerStatus(_status) {
    // Handle general server status updates if needed
  }

  #onProgress(data) {
    // data: { job_id, percent, bytes_transferred, total_bytes, speed, status }
    if (data.status === 'completed') {
      this.state.update({
        status: 'completed',
        progress: 100,
        bytesTransferred: data.total_bytes
      });
      this.logs.add('Backup completed successfully', { phase: 'BACKUP', level: 'success' });
      this.toast.show('Backup completed!', 'success');
      this.socket.clearJob();

      // Persist transfer history (Task 15.2)
      if (!this.demo.active && this._activeTransferMeta) {
        this.transferHistory.add({
          filename: this._activeTransferMeta.filename,
          size: this._activeTransferMeta.size,
          status: 'completed',
          serverAddress: this.state.snapshot.serverAddress,
          jobId: this.state.snapshot.jobId,
        });

        this.#renderTransferHistory();
      }
      this._activeTransferMeta = null;
    } else if (data.status === 'failed') {
      this.state.update({ status: 'error' });
      this.logs.add(`Backup failed: ${data.error || 'Unknown error'}`, { phase: 'BACKUP', level: 'error' });
      this.toast.show('Backup failed', 'error');

      // Persist failure in history too (Task 15.2)
      if (!this.demo.active && this._activeTransferMeta) {
        this.transferHistory.add({
          filename: this._activeTransferMeta.filename,
          size: this._activeTransferMeta.size,
          status: 'failed',
          serverAddress: this.state.snapshot.serverAddress,
          jobId: this.state.snapshot.jobId,
        });

        this.#renderTransferHistory();
      }
      this._activeTransferMeta = null;
    } else {
      this.state.update({
        status: 'uploading',
        progress: data.percent,
        bytesTransferred: data.bytes_transferred,
        totalBytes: data.total_bytes,
        speed: data.speed
      });
    }
  }

  #onFileReceipt(receipt) {
    this.logs.add(`File receipt: ${receipt.filename} stored as ${receipt.file_id}`, { phase: 'BACKUP' });
  }

  #onMonitorResult(res) {
    if (dom.qualityBadge) {
      dom.qualityBadge.textContent = `Quality: ${res.quality || 'checking'}`;
    }

    if (dom.lastChecked) {
      dom.lastChecked.textContent = `Last checked ${formatters.relativeTime(res.timestamp)}`;
    }

    if (dom.detailStatus) {
      dom.detailStatus.textContent = res.ok ? 'Online' : 'Offline';
    }

    if (dom.detailLatency) {
      dom.detailLatency.textContent = Number.isFinite(res.latency)
        ? `${Math.max(0, Math.round(res.latency))} ms`
        : '—';
    }
  }

  // --- Rendering ---

  #isTransferActive(status) {
    return status === 'uploading' || status === 'paused';
  }

  #isTransferFinished(status) {
    return status === 'completed' || status === 'error';
  }

  #clampPct(value) {
    return Math.max(0, Math.min(100, Number(value) || 0));
  }

  #renderPhaseText(status) {
    if (!dom.phaseText) return;
    const labels = {
      idle: 'Idle',
      uploading: this.demo.active ? 'Simulated upload' : 'Uploading',
      paused: this.demo.active ? 'Simulated (paused)' : 'Paused',
      completed: this.demo.active ? 'Simulated complete' : 'Completed',
      error: 'Error',
    };
    dom.phaseText.textContent = labels[status] || 'Idle';
  }

  #renderProgressPct(progress) {
    if (!dom.progressPct) return;
    const next = `${Math.round(this.#clampPct(progress))}%`;
    if (dom.progressPct.textContent === next) return;

    dom.progressPct.textContent = next;
    dom.progressPct.classList.add('updating');
    setTimeout(() => dom.progressPct?.classList.remove('updating'), 350);
  }

  #renderProgressRing(progress) {
    if (!dom.progressArc) return;
    const pct = this.#clampPct(progress);
    const r = 45;
    const circumference = 2 * Math.PI * r;
    const offset = circumference * (1 - pct / 100);
    dom.progressArc.style.strokeDasharray = `${circumference}`;
    dom.progressArc.style.strokeDashoffset = `${offset}`;

    // Accessibility: keep a native <progress> element in sync for assistive tech.
    if (dom.progressNative) {
      const rounded = Math.round(pct);
      dom.progressNative.value = rounded;
      dom.progressNative.textContent = `${rounded}%`;
    }
  }

  #setTextWithOptionalPulse(el, nextText, { pulse = true } = {}) {
    if (!el) return;

    const next = String(nextText ?? '');
    if (el.textContent === next) return;

    el.textContent = next;

    if (!pulse) return;

    // Respect reduced-motion preferences.
    const reduceMotion = globalThis.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
    if (reduceMotion) return;

    // Restart animation reliably.
    el.classList.remove('value-updating');
    // Re-add on the next frame so the animation retriggers reliably without forcing layout.
    const schedule = globalThis.requestAnimationFrame
      ? globalThis.requestAnimationFrame.bind(globalThis)
      : (cb) => globalThis.setTimeout(cb, 0);
    schedule(() => {
      // Element may have been removed between updates.
      if (!el.isConnected) return;
      el.classList.add('value-updating');
    });

    const priorTimer = this._valuePulseTimers.get(el);
    if (priorTimer) {
      globalThis.clearTimeout(priorTimer);
    }

    const timer = globalThis.setTimeout(() => {
      el.classList.remove('value-updating');
      this._valuePulseTimers.delete(el);
    }, 320);

    this._valuePulseTimers.set(el, timer);
  }

  #renderStats(state, transferActive, transferFinished) {
    const isUploading = state.status === 'uploading';

    this.#applyTransferActiveStyles(isUploading);
    this.#renderStatBytes(state, transferActive, transferFinished, isUploading);
    this.#renderStatSize(state);
    this.#renderStatSpeed(state, transferActive, isUploading);
    this.#renderStatElapsed(state, transferActive, transferFinished);
    this.#renderEta(state, transferActive);
  }

  #applyTransferActiveStyles(isUploading) {
    if (!dom.statsContainers) return;

    for (const container of Object.values(dom.statsContainers)) {
      container?.classList.toggle('transfer-active', isUploading);
    }

    dom.statsContainers.speed?.classList.toggle('primary-stat', isUploading);
  }

  #renderStatBytes(state, transferActive, transferFinished, isUploading) {
    if (!dom.stats?.bytes) return;

    const showBytes = transferActive || transferFinished || Number(state.totalBytes) > 0;
    const bytesText = showBytes ? formatters.formatBytes(state.bytesTransferred || 0) : '—';
    this.#setTextWithOptionalPulse(dom.stats.bytes, bytesText, { pulse: isUploading });
    dom.statsContainers?.bytes?.setAttribute('aria-label', `Bytes Sent: ${dom.stats.bytes.textContent}`);
  }

  #renderStatSize(state) {
    if (!dom.stats?.size) return;

    const hasSize = Number(state.totalBytes) > 0;
    const sizeText = hasSize ? formatters.formatBytes(state.totalBytes || 0) : '—';
    // Size changes rarely; pulse is useful even when not actively uploading.
    this.#setTextWithOptionalPulse(dom.stats.size, sizeText, { pulse: true });
    dom.statsContainers?.size?.setAttribute('aria-label', `File Size: ${dom.stats.size.textContent}`);
  }

  #renderStatSpeed(state, transferActive, isUploading) {
    if (!dom.stats?.speed) return;

    const speedText = this.#getSpeedText(state, transferActive);
    this.#setTextWithOptionalPulse(dom.stats.speed, speedText, { pulse: isUploading });
    dom.statsContainers?.speed?.setAttribute('aria-label', `Speed: ${dom.stats.speed.textContent}`);
  }

  #getSpeedText(state, transferActive) {
    if (transferActive) return formatters.formatSpeed(state.speed || 0);
    if (state.status === 'paused') return 'Paused';
    if (state.status === 'completed') return '0 B/s';
    return '—';
  }

  #renderStatElapsed(state, transferActive, transferFinished) {
    if (!dom.stats?.elapsed) return;

    const canShow = Boolean(state.startTime) && (transferActive || transferFinished);
    const text = canShow
      ? formatters.formatDuration(Math.max(0, (Date.now() - Number(state.startTime)) / 1000))
      : '--';

    this.#setTextWithOptionalPulse(dom.stats.elapsed, text, { pulse: false });
    dom.statsContainers?.elapsed?.setAttribute('aria-label', `Elapsed: ${dom.stats.elapsed.textContent}`);
  }

  #renderEta(state, transferActive) {
    if (!dom.etaText) return;

    if (state.status === 'paused') {
      dom.etaText.textContent = 'Paused';
      return;
    }

    if (state.status === 'completed') {
      dom.etaText.textContent = 'Done';
      return;
    }

    const showEta = transferActive && state.totalBytes > 0 && state.speed > 0;
    if (!showEta) {
      dom.etaText.textContent = '—';
      return;
    }

    const remainingBytes = Math.max(0, (state.totalBytes || 0) - (state.bytesTransferred || 0));
    const etaSec = remainingBytes / Math.max(1, state.speed);
    dom.etaText.textContent = formatters.formatDuration(etaSec);
  }

  #renderControls(state, transferActive) {
    if (dom.pauseBtn) dom.pauseBtn.disabled = state.status !== 'uploading';
    if (dom.resumeBtn) dom.resumeBtn.disabled = state.status !== 'paused';
    if (dom.stopBtn) dom.stopBtn.disabled = !transferActive;
  }

  #renderSpeedChart(state, transferActive) {
    if (!transferActive) return;
    if (!ProfessionalGUIEnhancements.chartInstance) return;
    if (!Number.isFinite(state.speed)) return;
    ProfessionalGUIEnhancements.chartInstance.addDataPoint(Number(state.speed) || 0);
  }

  #renderTransferHistory({ force = false } = {}) {
    if (!dom.transferHistoryList || !dom.transferHistoryEmpty || !dom.transferHistoryCount) return;

    const filteredEntries = this.#getFilteredTransfers();
    const { entries } = this.transferHistory;
    const sig = JSON.stringify(entries);
    if (!force && sig === this._lastTransferHistorySig) return;
    this._lastTransferHistorySig = sig;

    const totalCount = Array.isArray(entries) ? entries.length : 0;
    const filteredCount = Array.isArray(filteredEntries) ? filteredEntries.length : 0;

    // Show filtered count / total count
    const filterValue = dom.transferHistoryFilter?.value || 'all';
    if (filterValue === 'all') {
      dom.transferHistoryCount.textContent = String(totalCount);
    } else {
      dom.transferHistoryCount.textContent = `${filteredCount} of ${totalCount}`;
    }

    if (dom.transferHistoryClearBtn) {
      dom.transferHistoryClearBtn.disabled = totalCount === 0;
    }

    if (dom.transferHistoryExportBtn) {
      dom.transferHistoryExportBtn.disabled = totalCount === 0;
    }

    // Empty state
    const showEmpty = filteredCount === 0;
    dom.transferHistoryEmpty.hidden = !showEmpty;
    dom.transferHistoryList.hidden = showEmpty;

    // Render filtered list
    dom.transferHistoryList.textContent = '';
    if (showEmpty) return;

    const frag = document.createDocumentFragment();

    for (const entry of filteredEntries) {
      const li = document.createElement('li');
      li.className = 'transfer-history-item';

      const main = document.createElement('div');
      main.className = 'transfer-history-main';

      const filename = document.createElement('div');
      filename.className = 'transfer-history-filename';
      filename.textContent = String(entry?.filename || 'unknown');
      filename.title = String(entry?.filename || 'unknown');

      const meta = document.createElement('div');
      meta.className = 'transfer-history-meta';

      const size = document.createElement('span');
      size.textContent = formatters.formatBytes(Number(entry?.size) || 0);

      const server = document.createElement('span');
      server.textContent = String(entry?.serverAddress || '—');

      meta.append(size, server);
      main.append(filename, meta);

      const badges = document.createElement('div');
      badges.className = 'transfer-history-badges';

      const status = document.createElement('span');
      const rawStatus = String(entry?.status || 'completed');
      const isSuccess = rawStatus === 'completed' || rawStatus === 'success';
      status.className = `transfer-history-status ${isSuccess ? 'is-success' : 'is-error'}`;
      status.textContent = isSuccess ? 'Completed' : 'Failed';

      const time = document.createElement('span');
      time.className = 'transfer-history-time';
      const ts = Date.parse(String(entry?.timestamp || ''));
      time.textContent = Number.isFinite(ts) ? formatters.relativeTime(ts) : '—';
      time.title = Number.isFinite(ts) ? new Date(ts).toISOString() : '';

      badges.append(status, time);
      li.append(main, badges);
      frag.appendChild(li);
    }

    dom.transferHistoryList.appendChild(frag);
  }

  #registerGlobalErrorHandlers() {
    if (this._globalHandlersRegistered) return;
    this._globalHandlersRegistered = true;

    // Capture unexpected runtime errors
    globalThis.addEventListener('error', (event) => {
      if (!event) return;
      // Ignore known benign ResizeObserver noise in Chromium
      if (typeof event.message === 'string' && event.message.includes('ResizeObserver loop limit exceeded')) {
        return;
      }
      const err = event.error || event.message || 'Unknown error';
      ErrorBoundary.handle(err, 'Global Error');
    });

    // Capture unhandled promise rejections
    globalThis.addEventListener('unhandledrejection', (event) => {
      if (!event) return;
      const reason = event.reason || event;
      ErrorBoundary.handle(reason, 'Unhandled Rejection');
    });
  }

  // Backwards-compatible alias used by earlier plan iterations.
  // Keep this small wrapper so any lingering call sites don't cause a parse-time failure.
  #setupGlobalErrorHandlers() {
    this.#registerGlobalErrorHandlers();
  }

  #render(state) {
    const transferActive = this.#isTransferActive(state.status);
    const transferFinished = this.#isTransferFinished(state.status);

    // Animation gating: pause heavy visuals when idle.
    const isIdle = transferActive === false;
    document.documentElement.classList.toggle('app-idle', isIdle);

    const statusPanel = document.getElementById('statusPanel');
    if (statusPanel) {
      statusPanel.classList.toggle('animate-paused', isIdle);
      statusPanel.classList.toggle('idle', state.status === 'idle');
      statusPanel.classList.toggle('uploading', state.status === 'uploading');
      statusPanel.classList.toggle('paused', state.status === 'paused');
      statusPanel.classList.toggle('completed', state.status === 'completed');
      statusPanel.classList.toggle('error', state.status === 'error');
    }

    this.#renderPhaseText(state.status);
    this.#renderProgressPct(state.progress);
    this.#renderProgressRing(state.progress);
    this.#renderStats(state, transferActive, transferFinished);
    this.#renderControls(state, transferActive);
    this.#renderSpeedChart(state, transferActive);
  }

  // --- Public helpers (used by ErrorBoundary) ---

  setConnectionStatus(message, type = 'info') {
    this.#updateConnectionStatus(String(message), type);
  }

  // --- Demo mode ---

}

// --- Bootstrap ---

document.addEventListener('DOMContentLoaded', () => {
  // Ensure DOM is fully ready before initializing app
  setTimeout(() => {
    globalThis.app = new App();
    globalThis.app.init().catch(err => {
      console.error('Fatal initialization error:', err);
      document.body.innerHTML = '<div style="color:red; padding:20px;"><h1>Fatal Error</h1><p>Application failed to initialize. See console for details.</p></div>';
    });
  }, 0);
});
