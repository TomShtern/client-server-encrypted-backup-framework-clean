/**
 * CyberBackup Client - UI Components
 * Theme management, logging UI, file handling, and visual enhancements.
 * Depends on: core-utils.js
 */

// --- Theme Management ---

class ThemeManager {
  constructor() {
    this.themeToggle = dom.themeToggle;
    this.prefersDark = globalThis.matchMedia('(prefers-color-scheme: dark)');
    this.currentTheme = localStorage.getItem('theme') || (this.prefersDark.matches ? 'dark' : 'light');
    this.#init();
  }

  #init() {
    this.#apply(this.currentTheme);

    // Checkbox semantics: use change event and treat checked=true as dark mode
    this.themeToggle?.addEventListener('change', () => {
      const next = this.themeToggle.checked ? 'dark' : 'light';
      this.#apply(next);
      localStorage.setItem('theme', next);
    });

    this.prefersDark.addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        this.#apply(e.matches ? 'dark' : 'light');
      }
    });
  }

  toggle() {
    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.#apply(newTheme);
    localStorage.setItem('theme', newTheme);
  }

  #apply(theme) {
    this.currentTheme = theme;
    // Toggle classes to match CSS selectors (html.theme-dark, html.theme-light)
    document.documentElement.classList.remove('theme-dark', 'theme-light');
    document.documentElement.classList.add(`theme-${theme}`);

    if (this.themeToggle) {
      this.themeToggle.checked = theme === 'dark';
      // Optional micro-interaction hook
      this.themeToggle.classList.add('rotating');
      setTimeout(() => this.themeToggle?.classList.remove('rotating'), 650);
    }

    if (dom.themeLabel) {
      dom.themeLabel.textContent = theme === 'dark' ? 'Dark mode' : 'Light mode';
    }
  }
}

// --- Logging System ---

class LogStore {
  constructor(container, maxLogs = 50) {
    this.container = container;
    this.maxLogs = maxLogs;
    this.logs = [];
  }

  add(message, { level = 'info', phase = 'GENERAL' } = {}) {
    const entry = {
      id: crypto.randomUUID(),
      timestamp: new Date(),
      message,
      level,
      phase
    };

    this.logs.unshift(entry);
    if (this.logs.length > this.maxLogs) this.logs.pop();
    this.#render(entry);
    this.#syncEmptyAndCount();
  }

  clear() {
    this.logs = [];
    if (this.container) this.container.innerHTML = '';
    this.#syncEmptyAndCount();
  }

  #syncEmptyAndCount() {
    if (dom.logEntryCount) {
      dom.logEntryCount.textContent = String(this.logs.length);
    }
    if (dom.logsEmptyState) {
      dom.logsEmptyState.hidden = this.logs.length > 0;
    }
  }

  #render(entry) {
    if (!this.container) return;

    const div = document.createElement('div');
    div.className = `log-entry log-${entry.level}`;
    div.dataset.logEntry = '';

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
    this.#bindEvents();
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
    if (files?.length) {
      const file = files[0];
      this.onFileSelect(file);
      ProfessionalGUIEnhancements.updateFileCardPreview(file);
    }
  }

  clear() {
    if (this.input) this.input.value = '';
    ProfessionalGUIEnhancements.updateFileCardPreview(null);
    this.onFileSelect(null);
  }

  getFile() {
    return this.input?.files?.[0];
  }
}

// --- Speed Chart ---

class SpeedChart {
  #resizeHandler = null;
  #themeObserver = null;

  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.dataPoints = [];
    this.maxDataPoints = 30; // 30 seconds of data
    this.maxSpeed = 0;

    // Cache colors from CSS variables (theme-responsive)
    this.colors = this.#getColorsFromCSS();

    // Throttled draw function
    this.throttledDraw = domUtils.throttle(this.draw.bind(this), 16); // ~60fps cap

    // Setup canvas size
    this.resizeCanvas();
    this.#attachResizeListener();
    this.#attachThemeChangeListener();
  }

  destroy() {
    if (this.#resizeHandler) {
      window.removeEventListener('resize', this.#resizeHandler);
      this.#resizeHandler = null;
    }
    if (this.#themeObserver) {
      this.#themeObserver.disconnect();
      this.#themeObserver = null;
    }
  }

  #hexToRgba(hex, alpha) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
    const r = Number.parseInt(hex.substring(0, 2), 16);
    const g = Number.parseInt(hex.substring(2, 4), 16);
    const b = Number.parseInt(hex.substring(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  #getColorsFromCSS() {
    const root = document.documentElement;
    const computedStyle = getComputedStyle(root);
    return {
      grid: computedStyle.getPropertyValue('--border').trim() || '#ccc',
      line: computedStyle.getPropertyValue('--focus').trim() || '#007bff',
    };
  }

  #attachThemeChangeListener() {
    this.#themeObserver = new MutationObserver(() => {
      this.colors = this.#getColorsFromCSS();
      if (this.dataPoints.length > 0) this.throttledDraw();
    });
    this.#themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });
  }

  #attachResizeListener() {
    this.#resizeHandler = () => this.resizeCanvas();
    window.addEventListener('resize', this.#resizeHandler);
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.throttledDraw();
  }

  addDataPoint(speed) {
    this.dataPoints.push(speed);
    if (this.dataPoints.length > this.maxDataPoints) this.dataPoints.shift();
    this.maxSpeed = Math.max(...this.dataPoints, this.maxSpeed * 0.95);
    this.throttledDraw();
  }

  draw() {
    if (!this.ctx || this.dataPoints.length === 0) return;
    const width = this.canvas.width / window.devicePixelRatio;
    const height = this.canvas.height / window.devicePixelRatio;
    const padding = 10;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    this.ctx.clearRect(0, 0, width, height);

    this.ctx.strokeStyle = this.colors.grid;
    this.ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(padding, y);
      this.ctx.lineTo(width - padding, y);
      this.ctx.stroke();
    }

    this.ctx.strokeStyle = this.colors.line;
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();

    let index = 0;
    for (const speed of this.dataPoints) {
      const x = padding + (chartWidth / (this.maxDataPoints - 1)) * index;
      const y = padding + chartHeight - (speed / (this.maxSpeed || 1)) * chartHeight;
      if (index === 0) this.ctx.moveTo(x, y);
      else this.ctx.lineTo(x, y);
      index++;
    }

    this.ctx.stroke();
    this.ctx.lineTo(width - padding, height - padding);
    this.ctx.lineTo(padding, height - padding);
    this.ctx.closePath();

    const gradient = this.ctx.createLinearGradient(0, padding, 0, height - padding);
    gradient.addColorStop(0, this.#hexToRgba(this.colors.line, 0.2));
    gradient.addColorStop(1, this.#hexToRgba(this.colors.line, 0));
    this.ctx.fillStyle = gradient;
    this.ctx.fill();
  }
}

// --- Professional GUI Enhancements ---

class ProfessionalGUIEnhancements {
  static chartInstance = null;
  static initialized = false;

  static init() {
    if (this.initialized) return;
    this.initialized = true;

    this.initRippleEffects();
    this.initFloatingLabels();
    this.setupConnectionDropdown();
    this.setupLogSearch();
    this.setupSpeedChart();
    this.setupAdvancedSettingsPanel();
    this.setupDragAndDrop();
    this.setupShortcuts();
    this.setupBrowserNotifications();
    this.addEnhancementStyles();
  }

  static initRippleEffects() {
    document.addEventListener('click', (e) => {
      const target = e.target.closest('.ripple');
      if (!target) return;

      const rect = target.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const circle = document.createElement('span');
      const diameter = Math.max(rect.width, rect.height);
      const radius = diameter / 2;

      circle.style.width = circle.style.height = `${diameter}px`;
      circle.style.left = `${x - radius}px`;
      circle.style.top = `${y - radius}px`;
      circle.classList.add('ripple-effect');

      const ripple = target.getElementsByClassName('ripple-effect')[0];
      if (ripple) ripple.remove();

      target.appendChild(circle);
      setTimeout(() => circle.remove(), 600);
    });
  }

  static initFloatingLabels() {
    const inputs = document.querySelectorAll('.floating-label .interactive');
    for (const input of inputs) {
      if (input.value) input.classList.add('has-value');
      input.addEventListener('input', () => {
        if (input.value) input.classList.add('has-value');
        else input.classList.remove('has-value');
      });
      input.addEventListener('focus', () => input.parentElement.classList.add('focused'));
      input.addEventListener('blur', () => input.parentElement.classList.remove('focused'));
    }
  }

  static setupConnectionDropdown() {
    const statusBadge = dom.connStatus;
    const dropdown = dom.connectionDetails;

    if (!statusBadge || !dropdown) return;

    statusBadge.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target) && !statusBadge.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  }

  static setupLogSearch() {
    const searchInput = document.getElementById('logSearchInput');
    if (!searchInput) return;

    let searchTimeout;
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        const query = searchInput.value.toLowerCase().trim();
        const logEntries = document.querySelectorAll('[data-log-entry]');
        for (const entry of logEntries) {
          const text = entry.textContent.toLowerCase();
          entry.style.display = (!query || text.includes(query)) ? '' : 'none';
        }
      }, 300);
    });
  }

  static setupSpeedChart() {
    this.chartInstance = new SpeedChart('speedChart');
    const toggleBtn = document.getElementById('toggleSpeedChart');
    const container = document.getElementById('speedChartContainer');

    if (toggleBtn && container) {
      toggleBtn.addEventListener('click', () => {
        const isVisible = !container.hidden;
        if (isVisible) {
          container.hidden = true;
          container.classList.remove('show');
          toggleBtn.textContent = 'Show';
          toggleBtn.setAttribute('aria-expanded', 'false');
        } else {
          container.hidden = false;
          container.classList.add('show');
          toggleBtn.textContent = 'Hide';
          toggleBtn.setAttribute('aria-expanded', 'true');
          if (this.chartInstance) this.chartInstance.draw();
        }
      });
    }
  }

  static setupAdvancedSettingsPanel() {
    const panel = dom.advancedPanel;
    if (!panel) return;

    const toggle = panel.querySelector('.advanced-toggle');
    const content = dom.advancedContent || panel.querySelector('#advancedContent');
    if (!toggle || !content) return;

    const applyExpanded = (expanded) => {
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      panel.classList.toggle('expanded', expanded);
      content.hidden = !expanded;
    };

    // Initialize from markup
    applyExpanded(toggle.getAttribute('aria-expanded') !== 'false');

    toggle.addEventListener('click', () => {
      const next = toggle.getAttribute('aria-expanded') !== 'true';
      applyExpanded(next);
    });

    // Tabs
    const tabButtons = Array.from(panel.querySelectorAll('.tab-btn[role="tab"]'));
    const tabPanels = Array.from(panel.querySelectorAll('.tab-panel[role="tabpanel"]'));
    if (tabButtons.length === 0 || tabPanels.length === 0) return;

    const activateTab = (btn) => {
      const panelId = btn.getAttribute('aria-controls');
      for (const b of tabButtons) {
        const active = b === btn;
        b.classList.toggle('active', active);
        b.setAttribute('aria-selected', active ? 'true' : 'false');
        b.tabIndex = active ? 0 : -1;
      }
      for (const p of tabPanels) {
        const active = p.id === panelId;
        p.classList.toggle('active', active);
        p.hidden = !active;
      }
    };

    for (const btn of tabButtons) {
      btn.addEventListener('click', () => activateTab(btn));
      btn.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
        e.preventDefault();
        const idx = tabButtons.indexOf(btn);
        const dir = e.key === 'ArrowRight' ? 1 : -1;
        const next = tabButtons[(idx + dir + tabButtons.length) % tabButtons.length];
        next.focus();
        activateTab(next);
      });
    }

    const initial = tabButtons.find((b) => b.classList.contains('active')) || tabButtons[0];
    activateTab(initial);
  }

  static setupDragAndDrop() {
    const overlay = document.getElementById('dragOverlay');
    const fileInput = document.getElementById('fileInput');
    if (!overlay || !fileInput) return;

    let dragCounter = 0;
    for (const eventName of ['dragenter', 'dragover', 'dragleave', 'drop']) {
      document.body.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      });
    }

    document.body.addEventListener('dragenter', () => {
      dragCounter++;
      overlay.classList.add('active');
    });

    document.body.addEventListener('dragleave', () => {
      dragCounter--;
      if (dragCounter === 0) overlay.classList.remove('active');
    });

    document.body.addEventListener('drop', (e) => {
      dragCounter = 0;
      overlay.classList.remove('active');
      const { files } = e.dataTransfer;
      if (files.length > 0) {
        fileInput.files = files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  }

  static setupShortcuts() {
    const modal = document.getElementById('shortcutModal');
    const btn = document.getElementById('shortcutBtn');
    const closeBtn = document.getElementById('closeShortcutBtn');
    if (!modal || !btn || !closeBtn) return;

    btn.addEventListener('click', () => modal.showModal());
    closeBtn.addEventListener('click', () => modal.close());
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.close(); });

    document.addEventListener('keydown', (e) => {
      if (e.key === '?' && e.shiftKey && document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        modal.showModal();
      }
      // Ctrl/Cmd + Enter to start backup
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const startBtn = document.getElementById('start-backup-btn'); // Check ID
        if (startBtn && !startBtn.disabled) startBtn.click();
      }
    });
  }

  static setupBrowserNotifications() {
    if (!('Notification' in globalThis)) return;
    const requestPermission = () => {
      if (Notification.permission === 'default') Notification.requestPermission();
      document.removeEventListener('click', requestPermission);
    };
    document.addEventListener('click', requestPermission);
  }

  static showNotification(title, options) {
    if (!('Notification' in globalThis) || Notification.permission !== 'granted') return;
    try {
      new Notification(title, { icon: 'favicon.svg', ...options });
    } catch (e) { console.warn('Notification failed', e); }
  }

  static FILE_TYPE_ICONS = {
    pdf: { icon: '📄', badge: 'pdf', class: 'pdf' },
    doc: { icon: '📝', badge: 'doc', class: 'doc' },
    docx: { icon: '📝', badge: 'doc', class: 'doc' },
    txt: { icon: '📄', badge: 'txt', class: 'default' },
    xls: { icon: '📊', badge: 'xls', class: 'doc' },
    xlsx: { icon: '📊', badge: 'xlsx', class: 'doc' },
    csv: { icon: '📊', badge: 'csv', class: 'doc' },
    jpg: { icon: '🖼️', badge: 'jpg', class: 'img' },
    jpeg: { icon: '🖼️', badge: 'jpeg', class: 'img' },
    png: { icon: '🖼️', badge: 'png', class: 'img' },
    gif: { icon: '🖼️', badge: 'gif', class: 'img' },
    mp4: { icon: '🎥', badge: 'mp4', class: 'video' },
    mp3: { icon: '🎵', badge: 'mp3', class: 'audio' },
    zip: { icon: '📦', badge: 'zip', class: 'archive' },
    js: { icon: '💻', badge: 'js', class: 'code' },
    py: { icon: '💻', badge: 'py', class: 'code' },
    html: { icon: '💻', badge: 'html', class: 'code' },
    default: { icon: '📄', badge: 'file', class: 'default' }
  };

  static updateFileCardPreview(file) {
    const fileIcon = document.getElementById('fileIcon');
    const fileMetadata = document.getElementById('fileMetadata');
    const fileTypeBadge = document.getElementById('fileTypeBadge');
    const fileModified = document.getElementById('fileModified');
    const fileSize = document.getElementById('fileSize');
    const defaultContent = document.getElementById('defaultDropContent');
    const previewCard = document.getElementById('filePreviewCard');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const dropZone = document.getElementById('fileDropZone');

    if (!file) {
      if (defaultContent) defaultContent.style.display = 'flex';
      if (previewCard) previewCard.style.display = 'none';
      if (fileSize) fileSize.textContent = '';
      if (fileModified) fileModified.textContent = '';
      dropZone?.classList.remove('file-selected');
      return;
    }

    if (defaultContent) defaultContent.style.display = 'none';
    if (previewCard) previewCard.style.display = 'grid';
    dropZone?.classList.add('file-selected');

    const ext = file.name.split('.').pop().toLowerCase();
    const typeInfo = this.FILE_TYPE_ICONS[ext] || this.FILE_TYPE_ICONS.default;

    if (fileIcon) fileIcon.textContent = typeInfo.icon;
    if (fileNameDisplay) fileNameDisplay.textContent = file.name;
    if (fileMetadata) fileMetadata.style.display = 'flex';
    if (fileTypeBadge) {
      fileTypeBadge.textContent = typeInfo.badge.toUpperCase();
      fileTypeBadge.className = `file-badge ${typeInfo.class}`;
    }
    if (fileModified) {
      const date = new Date(file.lastModified);
      fileModified.textContent = `Modified: ${date.toLocaleDateString()}`;
    }
    if (fileSize) {
      fileSize.textContent = formatters.bytes?.(file.size) || `${file.size} B`;
    }
  }

  static addEnhancementStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple { to { transform: scale(2); opacity: 0; } }
        .ripple-effect { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.4); transform: scale(0); animation: ripple 0.6s linear; pointer-events: none; }
        .has-value + .label-text, .focused + .label-text { transform: translateY(-24px) scale(0.75); color: var(--primary); }
    `;
    document.head.appendChild(style);
  }
}


// --- Dual server status helpers (used by ConnectionMonitor) ---

function setStatusPill(pillEl, online, { onlineText = 'Online', offlineText = 'Offline' } = {}) {
  if (!pillEl) return;
  const dot = pillEl.querySelector('.status-dot');
  const text = pillEl.querySelector('.status-text');

  const state = online === true ? 'online' : online === false ? 'offline' : 'connecting';
  if (dot) dot.className = `status-dot ${state}`;
  if (text) {
    text.textContent = online === true ? onlineText : online === false ? offlineText : 'Checking';
  }
}

globalThis.updateDualServerStatus = ({ apiOnline, backupOnline, latency } = {}) => {
  setStatusPill(dom.webServerStatus, apiOnline, { onlineText: 'Online', offlineText: 'Offline' });
  setStatusPill(dom.backupServerStatus, backupOnline, { onlineText: 'Online', offlineText: 'Offline' });

  if (Number.isFinite(latency)) {
    const ms = Math.max(0, Math.round(latency));
    if (dom.latencyValue) dom.latencyValue.textContent = String(ms);
    if (dom.detailLatency) dom.detailLatency.textContent = `${ms} ms`;
    if (dom.connHealth) dom.connHealth.title = `Round-trip latency: ${ms} ms`;
  }

  if (dom.detailServer && dom.serverInput?.value) {
    dom.detailServer.textContent = dom.serverInput.value;
  }

  if (dom.detailStatus) {
    if (apiOnline === false) dom.detailStatus.textContent = 'Web server offline';
    else if (backupOnline === false) dom.detailStatus.textContent = 'Backup server offline';
    else if (apiOnline === true && backupOnline === true) dom.detailStatus.textContent = 'Ready';
    else dom.detailStatus.textContent = 'Checking';
  }
};
