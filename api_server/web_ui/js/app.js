/**
 * CyberBackup Client - Main Application
 * Orchestrates Core Logic and UI Components.
 * Depends on: core-utils.js, core.js, ui.js
 */

class App {
  constructor() {
    // Initialize State
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
      username: 'User-' + Math.floor(Math.random() * 10000)
    });

    this.operationInProgress = false;

    // Initialize Managers
    // Initialize Managers
    this.api = new ApiClient(API_CONFIG.getApiBaseUrl());
    this.toast = new ToastManager(dom.toastStack);
    this.announcer = new ScreenReaderAnnouncer(dom.srLive);
    this.logs = new LogStore(dom.logContainer); // FIXED: Was dom.logsContainer (undefined in core-utils)
    this.theme = new ThemeManager(); // Uses dom.themeToggle internally

    // Fix: FileManager takes 3 args (input, dropZone, callback)
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

    // Bind UI Events
    this.#bindEvents();

    // Demo mode (secondary, opt-in)
    this.demoEnabled = this.#detectDemoMode();
    this.demoActive = false;
    this.demoTimer = null;
  }

  async init() {
    ProfessionalGUIEnhancements.init();

    // Subscribe to state changes early so the UI can render even when offline
    this.state.subscribe((state) => this.#render(state));

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

      if (dom.primaryActionBtn && !this.demoEnabled) {
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

    if (this.demoEnabled && dom.logDemoBtn) {
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
    dom.logDemoBtn?.addEventListener('click', () => this.#startDemoTransfer());

    // Settings
    dom.settingsToggle?.addEventListener('click', () => {
      dom.settingsPanel?.classList.toggle('open');
    });

    // Inline banner dismiss
    dom.inlineErrorDismiss?.addEventListener('click', () => this.hideInlineBanner());
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
    if (this.operationInProgress) {
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
    if (this.operationInProgress) return;
    if (API_CONFIG.isFileProtocol()) {
      this.toast.show('API unavailable in file:// mode. Open http://localhost:9090 instead.', 'warn');
      this.setConnectionStatus('API unavailable in file:// mode', 'error');
      this.showInlineBanner({
        severity: 'error',
        title: 'Cannot connect in file:// mode',
        body: 'Open the Web UI from the API server to connect and start backups.',
        actionHref: 'http://localhost:9090',
        actionText: 'Open live UI'
      });
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
      this.operationInProgress = true;
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
      this.#updateConnectionStatus('Connection failed', 'error');
      this.showInlineBanner({
        severity: 'error',
        title: 'Connection failed',
        body: 'Could not connect. Ensure the API server is running (port 9090) and the backup server is reachable (port 1256).',
        actionHref: 'http://localhost:9090',
        actionText: 'Open live UI'
      });
      ErrorBoundary.handle(error, 'Connection');
      } finally {
        this.operationInProgress = false;
    }
  }

  async #handleDisconnect() {
      if (this.operationInProgress) return;
    try {
        this.operationInProgress = true;
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
      this.operationInProgress = false;
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
      if (dom.fileLabel) {
        dom.fileLabel.textContent = file.name;
      }
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
      this.operationInProgress = true;
      this.state.update({
        status: 'uploading',
        progress: 0,
        startTime: Date.now(),
        totalBytes: file.size,
        bytesTransferred: 0,
      });

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
      this.operationInProgress = false;
    }
  }

  async #handlePause() {
    try {
      if (this.demoActive) {
        this.#stopDemoTimer();
        this.state.update({ status: 'paused' });
        this.logs.add('Demo transfer paused', { phase: 'DEMO', level: 'info' });
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
      if (this.demoActive) {
        this.state.update({ status: 'uploading' });
        this.logs.add('Demo transfer resumed', { phase: 'DEMO', level: 'info' });
        this.#ensureDemoTimer();
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
      if (this.demoActive) {
        this.#stopDemoTimer();
        this.demoActive = false;
        this.state.update({ status: 'idle', progress: 0, jobId: null, speed: 0, bytesTransferred: 0 });
        this.logs.add('Demo transfer stopped', { phase: 'DEMO', level: 'warn' });
        this.toast.show('Demo stopped', 'info');
        return;
      }

      await this.api.stop();
      this.state.update({ status: 'idle', progress: 0, jobId: null });
      this.socket.clearJob();
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

  #onServerStatus(status) {
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
    } else if (data.status === 'failed') {
      this.state.update({ status: 'error' });
      this.logs.add(`Backup failed: ${data.error || 'Unknown error'}`, { phase: 'BACKUP', level: 'error' });
      this.toast.show('Backup failed', 'error');
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
      uploading: this.demoActive ? 'Simulated upload' : 'Uploading',
      paused: this.demoActive ? 'Simulated (paused)' : 'Paused',
      completed: this.demoActive ? 'Simulated complete' : 'Completed',
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
    if (dom.progressRing) {
      dom.progressRing.setAttribute('aria-valuenow', Math.round(pct).toString());
    }
  }

  #renderStats(state, transferActive, transferFinished) {
    if (dom.stats?.bytes) {
      const showBytes = transferActive || transferFinished || Number(state.totalBytes) > 0;
      dom.stats.bytes.textContent = showBytes ? formatters.formatBytes(state.bytesTransferred || 0) : '—';
      dom.statsContainers?.bytes?.setAttribute('aria-label', `Bytes Sent: ${dom.stats.bytes.textContent}`);
    }

    if (dom.stats?.size) {
      const hasSize = Number(state.totalBytes) > 0;
      dom.stats.size.textContent = hasSize ? formatters.formatBytes(state.totalBytes || 0) : '—';
      dom.statsContainers?.size?.setAttribute('aria-label', `File Size: ${dom.stats.size.textContent}`);
    }

    if (dom.stats?.speed) {
      let speedText = '—';
      if (transferActive) speedText = formatters.formatSpeed(state.speed || 0);
      else if (state.status === 'paused') speedText = 'Paused';
      else if (state.status === 'completed') speedText = '0 B/s';
      dom.stats.speed.textContent = speedText;
      dom.statsContainers?.speed?.setAttribute('aria-label', `Speed: ${dom.stats.speed.textContent}`);
    }

    if (dom.stats?.elapsed) {
      const canShow = Boolean(state.startTime) && (transferActive || transferFinished);
      if (canShow) {
        const elapsedSec = Math.max(0, (Date.now() - Number(state.startTime)) / 1000);
        dom.stats.elapsed.textContent = formatters.formatDuration(elapsedSec);
      } else {
        dom.stats.elapsed.textContent = '--';
      }
      dom.statsContainers?.elapsed?.setAttribute('aria-label', `Elapsed: ${dom.stats.elapsed.textContent}`);
    }

    if (dom.etaText) {
      if (state.status === 'paused') {
        dom.etaText.textContent = 'Paused';
      } else if (state.status === 'completed') {
        dom.etaText.textContent = 'Done';
      } else {
        const showEta = transferActive && state.totalBytes > 0 && state.speed > 0;
        if (showEta) {
          const remainingBytes = Math.max(0, (state.totalBytes || 0) - (state.bytesTransferred || 0));
          const etaSec = remainingBytes / Math.max(1, state.speed);
          dom.etaText.textContent = formatters.formatDuration(etaSec);
        } else {
          dom.etaText.textContent = '—';
        }
      }
    }
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

  #render(state) {
    const transferActive = this.#isTransferActive(state.status);
    const transferFinished = this.#isTransferFinished(state.status);

    // Animation gating: pause heavy visuals when idle.
    const isIdle = transferActive === false;
    document.documentElement.classList.toggle('app-idle', isIdle);

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

  #detectDemoMode() {
    try {
      const params = new URLSearchParams(globalThis.location?.search || '');
      if (params.has('demo')) return true;
      return localStorage.getItem('cyberbackup-demo-mode') === '1';
    } catch {
      return false;
    }
  }

  #startDemoTransfer() {
    if (!this.demoEnabled) return;
    if (this.demoActive) {
      this.toast.show('Demo already running', 'info');
      return;
    }

    this.demoActive = true;
    const totalBytes = 250 * 1024 * 1024;
    this.logs.add('Demo mode: starting simulated transfer', { phase: 'DEMO', level: 'info' });
    this.setConnectionStatus('Demo mode (simulated) - no network traffic', 'info');

    this.state.update({
      connected: false,
      jobId: 'demo',
      status: 'uploading',
      progress: 0,
      speed: 0,
      bytesTransferred: 0,
      totalBytes,
      startTime: Date.now(),
    });

    this.#ensureDemoTimer();
  }

  #ensureDemoTimer() {
    if (!this.demoActive || this.demoTimer) return;

    this.demoTimer = setInterval(() => {
      if (!this.demoActive) {
        this.#stopDemoTimer();
        return;
      }
      if (this.state.snapshot.status !== 'uploading') {
        return;
      }

      const currentPct = Math.max(0, Math.min(100, Number(this.state.snapshot.progress) || 0));
      const bump = 2 + Math.random() * 7;
      const nextPct = Math.min(100, currentPct + bump);
      const totalBytes = this.state.snapshot.totalBytes || 1;

      const speed = 8 * 1024 * 1024 + Math.random() * 3 * 1024 * 1024;
      const bytesTransferred = Math.floor(totalBytes * (nextPct / 100));

      if (nextPct >= 100) {
        this.state.update({
          status: 'completed',
          progress: 100,
          speed: 0,
          bytesTransferred: totalBytes,
        });
        this.logs.add('Demo transfer complete', { phase: 'DEMO', level: 'success' });
        this.toast.show('Demo complete (simulated)', 'success');
        this.demoActive = false;
        this.#stopDemoTimer();
        return;
      }

      this.state.update({
        status: 'uploading',
        progress: nextPct,
        speed,
        bytesTransferred,
      });
    }, 650);
  }

  #stopDemoTimer() {
    if (this.demoTimer) {
      clearInterval(this.demoTimer);
      this.demoTimer = null;
    }
  }
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
