// CyberBackup Client - Core Utilities
// Bundled: dom, formatters, performance-optimizer, state-store, toasts, accessibility

// --- utils/dom.js ---
function getElement(id, required = true) {
  const el = document.getElementById(id);
  if (!el && required) {
    throw new Error(`Missing required element: #${id}`);
  }
  return el;
}

function getOptionalElement(id) {
  return document.getElementById(id);
}

function querySelector(selector, parent = document) {
  const el = parent.querySelector(selector);
  if (!el) {
    throw new Error(`Missing required element for selector: ${selector}`);
  }
  return el;
}

const dom = {};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeDom);
} else {
  initializeDom();
}


function initializeDom() {
  dom.container = querySelector('.container');
  dom.statusOutput = getElement('statusOutput');
  dom.connHealth = getElement('connHealth');
  dom.latencyValue = getOptionalElement('latencyValue');
  dom.webServerStatus = getOptionalElement('webServerStatus');
  dom.backupServerStatus = getOptionalElement('backupServerStatus');
  dom.detailStatus = getOptionalElement('detailStatus');
  dom.detailLatency = getOptionalElement('detailLatency');
  dom.detailServer = getOptionalElement('detailServer');
  dom.detailUptime = getOptionalElement('detailUptime');
  dom.themeLabel = document.querySelector('.theme-label');
  dom.themeToggle = getElement('themeToggle');
  dom.serverInput = getElement('serverInput');
  dom.usernameInput = getElement('usernameInput');
  dom.serverValidIcon = getElement('serverValidIcon');
  dom.usernameValidIcon = getElement('usernameValidIcon');
  dom.serverHint = getElement('serverHint');
  dom.usernameHint = getElement('usernameHint');
  dom.fileDropZone = getElement('fileDropZone');
  dom.fileInput = getElement('fileInput');
  // New File Card Elements
  dom.fileIcon = getOptionalElement('fileIcon');
  dom.fileNameDisplay = getOptionalElement('fileNameDisplay');
  dom.fileMetadata = getOptionalElement('fileMetadata');
  dom.fileTypeBadge = getOptionalElement('fileTypeBadge');
  dom.fileModified = getOptionalElement('fileModified');
  // Optional file action buttons
  dom.fileSelectBtn = getOptionalElement('chooseFileBtn');
  dom.recentFilesBtn = getOptionalElement('recentFilesBtn');
  dom.clearFileBtn = getOptionalElement('clearFileBtn');
  dom.fileName = getOptionalElement('fileName');
  dom.fileInfo = getOptionalElement('fileInfo');
  dom.primaryActionBtn = getElement('primaryActionBtn');
  dom.primaryBtnText = getOptionalElement('primaryBtnText');
  dom.primaryBtnSpinner = getOptionalElement('primaryBtnSpinner');
  // Connection status message
  dom.connectionStatusMessage = getOptionalElement('connectionStatusMessage');
  dom.connectionStatusSpinner = getOptionalElement('connectionStatusSpinner');
  dom.connectionStatusText = getOptionalElement('connectionStatusText');
  dom.connectionStatusIcon = getOptionalElement('connectionStatusIcon');
  dom.performanceToggle = getOptionalElement('performanceToggle');
  dom.performanceToggleText = getOptionalElement('performanceToggleText');
  dom.qualityBadge = getOptionalElement('qualityBadge');
  dom.lastChecked = getOptionalElement('lastChecked');
  dom.troubleshootChip = getOptionalElement('troubleshootChip');
  dom.pauseBtn = getElement('pauseBtn');
  dom.resumeBtn = getElement('resumeBtn');
  dom.stopBtn = getElement('stopBtn');
  dom.advChunkSize = getOptionalElement('advChunkSize');
  dom.advRetryLimit = getOptionalElement('advRetryLimit');
  dom.advResetBtn = getOptionalElement('advResetBtn');
  dom.advRestoreDefaults = getOptionalElement('advRestoreDefaults');
  // Advanced settings panel elements
  dom.advancedPanel = getOptionalElement('advancedPanel');
  dom.advancedContent = getOptionalElement('advancedContent');
  dom.phaseText = getElement('phaseText');
  dom.progressRing = getElement('progressRing');
  dom.progressArc = getElement('progressArc');
  dom.progressNative = getOptionalElement('progressNative');
  dom.progressPct = getElement('progressPct');
  dom.etaText = getElement('etaText');
  dom.stats = {
    bytes: getElement('statBytes'),
    speed: getElement('statSpeed'),
    size: getElement('statSize'),
    elapsed: getElement('statElapsed'),
  };
  dom.statsContainers = {
    bytes: getOptionalElement('statBytesContainer'),
    speed: getOptionalElement('statSpeedContainer'),
    size: getOptionalElement('statSizeContainer'),
    elapsed: getOptionalElement('statElapsedContainer'),
  };
  // Log filter buttons
  dom.logFilters = [
    getElement('filterAll'),
    getElement('filterInfo'),
    getElement('filterWarn'),
    getElement('filterError'),
  ];
  // Log filter segment indicator (for sliding animation)
  dom.segmentIndicator = getOptionalElement('segmentIndicator');
  dom.logAutoscrollToggle = getOptionalElement('logAutoscrollToggle');
  dom.logExportBtn = getOptionalElement('logExportBtn');
  dom.logClearBtn = getOptionalElement('logClearBtn');
  dom.logCopyBtn = getOptionalElement('logCopyBtn');
  dom.logDemoBtn = getOptionalElement('logDemoBtn');
  dom.logSearchInput = getOptionalElement('logSearchInput');
  dom.searchClearBtn = getOptionalElement('searchClearBtn');
  dom.logEntryCount = getOptionalElement('logEntryCount');
  dom.logContainer = getElement('logContainer');
  dom.logsEmptyState = getOptionalElement('logsEmptyState');
  dom.logsEmptyTitle = getOptionalElement('logsEmptyTitle');
  dom.logsEmptyDesc = getOptionalElement('logsEmptyDesc');
  dom.logsSkeleton = getOptionalElement('logsSkeleton');

  // Transfer history (optional)
  dom.transferHistoryPanel = getOptionalElement('transferHistoryPanel');
  dom.transferHistoryList = getOptionalElement('transferHistoryList');
  dom.transferHistoryEmpty = getOptionalElement('transferHistoryEmpty');
  dom.transferHistoryCount = getOptionalElement('transferHistoryCount');
  dom.transferHistoryClearBtn = getOptionalElement('transferHistoryClearBtn');
  dom.transferHistoryExportBtn = getOptionalElement('transferHistoryExportBtn');
  dom.transferHistoryFilter = getOptionalElement('transferHistoryFilter');

  dom.toastStack = getElement('toastStack');
  dom.modal = getElement('modalConfirm');
  dom.modalCancelBtn = getElement('modalCancelBtn');
  dom.modalOkBtn = getElement('modalOkBtn');
  dom.srLive = getElement('srLive');

  // Inline banner (optional)
  dom.inlineErrorBanner = getOptionalElement('inlineErrorBanner');
  dom.inlineErrorTitle = getOptionalElement('inlineErrorTitle');
  dom.inlineErrorBody = getOptionalElement('inlineErrorBody');
  dom.inlineErrorAction = getOptionalElement('inlineErrorAction');
  dom.inlineErrorDismiss = getOptionalElement('inlineErrorDismiss');

  // Additional optional elements
  dom.connectionDetails = getOptionalElement('connectionDetails');
  dom.speedChart = getOptionalElement('speedChart');
  dom.toggleSpeedChart = getOptionalElement('toggleSpeedChart');
  dom.speedChartContainer = getOptionalElement('speedChartContainer');
  dom.speedChartPlaceholder = getOptionalElement('speedChartPlaceholder');
  dom.speedChartSummary = getOptionalElement('speedChartSummary');
  dom.dragOverlay = getOptionalElement('dragOverlay');
  dom.dragOverlayLabel = getOptionalElement('dragOverlayLabel');
  dom.shortcutModal = getOptionalElement('shortcutModal');
  dom.shortcutBtn = getOptionalElement('shortcutBtn');
  dom.closeShortcutBtn = getOptionalElement('closeShortcutBtn');
  dom.troubleshootSheet = getOptionalElement('troubleshootSheet');
  dom.closeTroubleshoot = getOptionalElement('closeTroubleshoot');
  dom.forcePingBtn = getOptionalElement('forcePingBtn');
  dom.filterRecentLogsBtn = getOptionalElement('filterRecentLogsBtn');
  dom.copyDiagnosticsBtn = getOptionalElement('copyDiagnosticsBtn');
  dom.offlineChecklist = getOptionalElement('offlineChecklist');
}

const domUtils = {
  safeExecute(operation, context = 'DOM operation') {
    try {
      return operation();
    } catch (error) {
      console.warn(`DOM error in ${context}:`, error);
      return null;
    }
  },
  isVisible(element) {
    return element &&
      element.offsetWidth > 0 &&
      element.offsetHeight > 0 &&
      getComputedStyle(element).display !== 'none';
  },
  addCleanupListener(element, event, handler, options = {}) {
    element.addEventListener(event, handler, options);
    return () => element.removeEventListener(event, handler, options);
  },
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
};

// --- utils/formatters.js ---
const BYTE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB'];

const formatters = {
  time(date) {
    if (!date) return '--:--:--';
    const d = new Date(date);
    if (Number.isNaN(d.getTime())) return '--:--:--';
    return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  },
  formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes < 0) return '–';
    if (bytes === 0) return '0 B';
    const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), BYTE_UNITS.length - 1);
    const value = bytes / Math.pow(1024, exponent);
    let precision;
    if (value >= 100) precision = 0;
    else if (value >= 10) precision = 1;
    else precision = 2;
    return `${value.toFixed(precision)} ${BYTE_UNITS[exponent]}`;
  },
  formatSpeed(bytesPerSecond) {
    if (!Number.isFinite(bytesPerSecond) || bytesPerSecond < 0) return '–';
    if (bytesPerSecond === 0) return '0 B/s';
    return `${this.formatBytes(bytesPerSecond)}/s`;
  },
  formatDuration(seconds) {
    if (!Number.isFinite(seconds) || seconds < 0) return '–';
    if (seconds < 1) return `${seconds.toFixed(1)} s`;
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (hrs > 0) return `${hrs}h ${mins.toString().padStart(2, '0')}m`;
    if (mins > 0) return `${mins}m ${secs.toString().padStart(2, '0')}s`;
    return `${secs}s`;
  },
  relativeTime(timestamp) {
    if (!timestamp) return '—';
    const now = Date.now();
    const diff = Math.max(0, now - Number(timestamp));
    const seconds = Math.floor(diff / 1000);
    if (seconds < 5) return 'Just now';
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  },
  formatLatency(ms) {
    if (!Number.isFinite(ms) || ms <= 0) return '–';
    return `${Math.max(1, Math.round(ms))} ms`;
  },
  formatPercentage(value) {
    if (!Number.isFinite(value)) return '0%';
    return `${Math.min(100, Math.max(0, value)).toFixed(0)}%`;
  },
  parseServerAddress(input) {
    if (!input || typeof input !== 'string') return null;
    let trimmed = input.trim();
    if (trimmed.length === 0) return null;
    if (trimmed.startsWith('http://')) trimmed = trimmed.slice(7);
    else if (trimmed.startsWith('https://')) trimmed = trimmed.slice(8);
    const slashIdx = trimmed.indexOf('/');
    if (slashIdx > -1) trimmed = trimmed.slice(0, slashIdx);
    const hasColon = trimmed.includes(':');
    if (!hasColon) return { host: trimmed, port: 1256 };
    const [hostPart, portPart] = trimmed.split(':');
    const parsedPort = Number.parseInt(portPart, 10);
    if (!Number.isFinite(parsedPort) || parsedPort <= 0 || parsedPort > 65535) return null;
    return { host: hostPart, port: parsedPort };
  }
};

function clamp(value, { min, max }) {
  return Math.min(Math.max(value, min), max);
}

function generateUUID() {
  try {
    if (globalThis.crypto?.randomUUID) {
      return globalThis.crypto.randomUUID();
    }
    const getRandomValues = globalThis.crypto?.getRandomValues?.bind(globalThis.crypto);
    const template = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx';
    const randomNibble = () => {
      if (getRandomValues) {
        const buf = new Uint8Array(1);
        getRandomValues(buf);
        return buf[0] % 16;
      }
      return Math.floor(Math.random() * 16);
    };
    return template.replaceAll(/[xy]/g, (c) => {
      const r = randomNibble();
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  } catch (err) {
    console.warn('UUID generation fallback used:', err);
    return `fallback-${Date.now()}-${Math.floor(Math.random() * 1e9)}`;
  }
}

function validateNumericInput(input, { min, max }) {
  const raw = input.value.trim();
  if (raw.length === 0) return null;
  const numeric = Number.parseInt(raw, 10);
  if (!Number.isFinite(numeric)) return null;
  return clamp(numeric, { min, max });
}

async function copyTextToClipboard(text) {
  try {
    const content = String(text ?? '');
    if (content.length === 0) return false;
    if (globalThis.navigator?.clipboard?.writeText) {
      await globalThis.navigator.clipboard.writeText(content);
      return true;
    }
  } catch (error) {
    console.warn('navigator.clipboard.writeText failed, falling back:', error);
  }
  try {
    if (typeof globalThis.prompt !== 'function') return false;
    globalThis.prompt('Copy to clipboard (Ctrl+C, Enter):', String(text ?? ''));
    return true;
  } catch (error) {
    console.warn('Clipboard fallback prompt failed:', error);
    return false;
  }
}

// --- utils/performance-optimizer.js ---
class PerformanceOptimizer {
  constructor() {
    this.pendingUpdates = new Map();
    this.rafId = null;
    this.isScheduled = false;
  }
  scheduleUpdate(key, updateFn) {
    this.pendingUpdates.set(key, updateFn);
    if (!this.isScheduled) {
      this.isScheduled = true;
      this.rafId = requestAnimationFrame(() => this.flush());
    }
  }
  flush() {
    if (this.pendingUpdates.size === 0) {
      this.isScheduled = false;
      return;
    }
    for (const [key, updateFn] of this.pendingUpdates) {
      try {
        updateFn();
      } catch (error) {
        console.error(`Update failed for ${key}:`, error);
      }
    }
    this.pendingUpdates.clear();
    this.isScheduled = false;
  }
  cancel() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    this.pendingUpdates.clear();
    this.isScheduled = false;
  }
}

function downloadBlob(blob, filename) {
  try {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.rel = 'noopener';
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return true;
  } catch (error) {
    console.warn('downloadBlob failed:', error);
    return false;
  }
}

class SmoothCounter {
  constructor(element, options = {}) {
    this.element = element;
    this.targetValue = 0;
    this.currentValue = 0;
    this.duration = options.duration || 300;
    this.formatFn = options.formatFn || ((v) => Math.round(v).toString());
    this.rafId = null;
    this.startTime = null;
    this.startValue = 0;
  }
  setValue(value) {
    if (value === this.targetValue) return;
    this.startValue = this.currentValue;
    this.targetValue = value;
    this.startTime = null;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
    this.animate();
  }
  animate(timestamp) {
    if (!this.startTime) {
      this.startTime = timestamp;
    }
    const elapsed = timestamp - this.startTime;
    const progress = Math.min(elapsed / this.duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    this.currentValue = this.startValue + (this.targetValue - this.startValue) * eased;
    this.element.textContent = this.formatFn(this.currentValue);
    if (progress < 1) {
      this.rafId = requestAnimationFrame((t) => this.animate(t));
    } else {
      this.currentValue = this.targetValue;
      this.element.textContent = this.formatFn(this.targetValue);
      this.rafId = null;
    }
  }
  setImmediate(value) {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    this.currentValue = value;
    this.targetValue = value;
    this.element.textContent = this.formatFn(value);
  }
  destroy() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
  }
}

const performanceOptimizer = new PerformanceOptimizer();

// --- state/state-store.js ---
function shallowClone(value) {
  if (value === null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return [...value];
  return { ...value };
}

function shallowEqual(objA, objB) {
  if (objA === objB) return true;
  if (typeof objA !== 'object' || typeof objB !== 'object' || objA === null || objB === null) {
    return false;
  }
  const keysA = Object.keys(objA);
  const keysB = Object.keys(objB);
  if (keysA.length !== keysB.length) return false;
  for (const key of keysA) {
    if (objA[key] !== objB[key]) return false;
  }
  return true;
}

class StateStore {
  #state;
  #listeners;
  #pendingUpdate;
  #updateScheduled;
  constructor(initialState) {
    this.#state = shallowClone(initialState);
    this.#listeners = new Set();
    this.#pendingUpdate = null;
    this.#updateScheduled = false;
  }
  get snapshot() {
    return this.#state;
  }
  update(patch) {
    if (!this.#pendingUpdate) {
      this.#pendingUpdate = {};
    }
    Object.assign(this.#pendingUpdate, patch);
    if (!this.#updateScheduled) {
      this.#updateScheduled = true;
      requestAnimationFrame(() => this.#flushUpdate());
    }
  }
  #flushUpdate() {
    if (!this.#pendingUpdate) {
      this.#updateScheduled = false;
      return;
    }
    const next = { ...this.#state, ...this.#pendingUpdate };
    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }
    this.#pendingUpdate = null;
    this.#updateScheduled = false;
  }
  updateImmediate(patch) {
    const next = { ...this.#state, ...patch };
    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }
  }
  mutate(mutator) {
    const next = { ...this.#state };
    mutator(next);
    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }
  }
  #notifyListeners(state) {
    queueMicrotask(() => {
      for (const listener of this.#listeners) {
        try {
          listener(state);
        } catch (error) {
          console.error('State listener error:', error);
        }
      }
    });
  }
  subscribe(listener) {
    if (typeof listener !== 'function') {
      throw new TypeError('Listener must be a function');
    }
    this.#listeners.add(listener);
    queueMicrotask(() => listener(this.#state));
    return () => this.#listeners.delete(listener);
  }
}

// --- ui/toasts.js ---
const DEFAULT_DURATION = 4000;

class ToastManager {
  #stack;
  #activeToasts;
  constructor(stackElement) {
    this.#stack = stackElement;
    this.#activeToasts = new Set();
  }
  show(message, variant = 'info', duration = DEFAULT_DURATION) {
    if (!this.#stack) {
      return () => { };
    }
    const toast = document.createElement('div');
    toast.className = `toast ${variant}`;
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.textContent = message;
    this.#stack.append(toast);
    this.#activeToasts.add(toast);
    const close = () => {
      if (!this.#activeToasts.has(toast)) {
        return;
      }
      this.#activeToasts.delete(toast);
      toast.classList.add('closing');
      toast.addEventListener('transitionend', () => toast.remove(), { once: true });
      setTimeout(() => toast.remove(), 300);
    };
    if (duration > 0) {
      setTimeout(close, duration);
    }
    return close;
  }
  clear() {
    for (const toast of this.#activeToasts) {
      toast.remove();
    }
    this.#activeToasts.clear();
  }
}

// --- ui/accessibility.js ---
class ScreenReaderAnnouncer {
  #pendingMessages = [];
  #isAnnouncing = false;
  #lastMessage = '';
  #lastAnnounceAt = 0;
  constructor(liveRegion) {
    this.liveRegion = liveRegion;
  }
  announce(message) {
    if (!this.liveRegion) return;
    const next = String(message ?? '').trim();
    if (!next) return;
    const now = Date.now();
    if (next === this.#lastMessage && now - this.#lastAnnounceAt < 1500) {
      return;
    }
    const lastQueued = this.#pendingMessages.at(-1) || '';
    if (next === lastQueued) {
      return;
    }
    this.#pendingMessages.push(next);
    if (!this.#isAnnouncing) {
      void this.#flushQueue();
    }
  }
  async #flushQueue() {
    this.#isAnnouncing = true;
    while (this.#pendingMessages.length > 0) {
      const next = this.#pendingMessages.shift();
      if (!next) {
        continue;
      }
      this.#lastMessage = next;
      this.#lastAnnounceAt = Date.now();
      this.liveRegion.textContent = '';
      await new Promise((resolve) => {
        requestAnimationFrame(() => {
          this.liveRegion.textContent = next;
          setTimeout(resolve, 120);
        });
      });
    }
    this.#isAnnouncing = false;
  }
}

// --- utils/storage.js ---
/**
 * Safe localStorage wrapper that handles errors gracefully.
 * Handles private browsing, quota limits, and disabled storage.
 *
 * @param {string} key - Storage key
 * @param {string|null|undefined} [value] - Value to set (omit to get, null to remove)
 * @returns {string|null} Retrieved value or null on error
 */
function safeLocalStorage(key, value) {
  try {
    if (typeof localStorage === 'undefined') {
      console.warn('localStorage is not available');
      return null;
    }
    if (value === null) {
      localStorage.removeItem(key);
      return null;
    }
    if (value === undefined) {
      return localStorage.getItem(key);
    }
    localStorage.setItem(key, value);
    return value;
  } catch (error) {
    if (error?.name === 'QuotaExceededError') {
      console.warn('localStorage quota exceeded, attempting cleanup');
      try {
        localStorage.removeItem('cyberbackup-history');
        if (value !== undefined && value !== null) {
          localStorage.setItem(key, value);
          return value;
        }
      } catch (retryError) {
        console.error('localStorage still failing after cleanup:', retryError);
      }
    } else if (error?.name === 'SecurityError') {
      console.warn('localStorage access denied (private browsing?)');
    } else {
      console.warn('localStorage error:', error);
    }
    return null;
  }
}

function safeSessionStorage(key, value) {
  try {
    if (typeof sessionStorage === 'undefined') {
      console.warn('sessionStorage is not available');
      return null;
    }
    if (value === null) {
      sessionStorage.removeItem(key);
      return null;
    }
    if (value === undefined) {
      return sessionStorage.getItem(key);
    }
    sessionStorage.setItem(key, value);
    return value;
  } catch (error) {
    console.warn('sessionStorage error:', error);
    return null;
  }
}

const memoryStorage = new Map();

function getStorageWithFallback(key) {
  const localValue = safeLocalStorage(key);
  if (localValue !== null) return localValue;
  return memoryStorage.get(key) || null;
}

function setStorageWithFallback(key, value) {
  const result = safeLocalStorage(key, value);
  if (result === null) {
    memoryStorage.set(key, value);
  }
}

// --- utils/timer-manager.js ---
class TimerManager {
  #timerId = null;
  start(callback, interval) {
    this.stop();
    this.#timerId = globalThis.setInterval(callback, interval);
  }
  stop() {
    if (this.#timerId) {
      globalThis.clearInterval(this.#timerId);
      this.#timerId = null;
    }
  }
  isRunning() {
    return this.#timerId !== null;
  }
  getTimerId() {
    return this.#timerId;
  }
}


// Expose shared utilities to classic scripts and tests, avoiding unused-var lint noise
const EXPORTED_GLOBALS = {
  dom,
  domUtils,
  formatters,
  clamp,
  generateUUID,
  validateNumericInput,
  copyTextToClipboard,
  PerformanceOptimizer,
  downloadBlob,
  SmoothCounter,
  performanceOptimizer,
  StateStore,
  ToastManager,
  ScreenReaderAnnouncer,
  API_CONFIG,
  safeLocalStorage,
  safeSessionStorage,
  getStorageWithFallback,
  setStorageWithFallback,
  TimerManager,
  CONSTANTS,
  FILE_VALIDATION,
};

Object.assign(globalThis, EXPORTED_GLOBALS);