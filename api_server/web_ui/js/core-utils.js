/**
 * CyberBackup Client - Core Utilities
 * Bundled: dom, formatters, performance-optimizer, state-store, toasts, accessibility
 */

// --- utils/dom.js ---
/**
 * Gets a DOM element by ID with optional fallback
 * @param {string} id - The element ID
 * @param {boolean} [required=true] - Whether the element is required (throws if not found)
 * @returns {HTMLElement|null} The DOM element or null if not found and not required
 * @throws {Error} When element is required but not found
 */
function getElement(id, required = true) {
  const el = document.getElementById(id);
  if (!el && required) {
    throw new Error(`Missing required element: #${id}`);
  }
  return el;
}

/**
 * Gets a DOM element by ID, returns null if not found (no throw)
 * @param {string} id - The element ID
 * @returns {HTMLElement|null} The DOM element or null if not found
 */
function getOptionalElement(id) {
  return document.getElementById(id);
}

/**
 * Query for a DOM element using CSS selector and throw if not found
 * @param {string} selector - The CSS selector
 * @param {Document|HTMLElement} [parent=document] - The parent element to query within
 * @returns {HTMLElement} The matching DOM element
 * @throws {Error} When element is not found for the selector
 */
function querySelector(selector, parent = document) {
  const el = parent.querySelector(selector);
  if (!el) {
    throw new Error(`Missing required element for selector: ${selector}`);
  }
  return el;
}

/**
 * Centralized DOM element cache - initialized as empty object
 * Will be populated after DOMContentLoaded to avoid timing issues
 */
const dom = {};

// Initialize DOM cache after document is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeDom);
} else {
  // DOM already loaded
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

/**
 * Utility functions for DOM manipulation and error-safe operations
 */
/**
 * Utility functions for DOM manipulation and error-safe operations
 */
const domUtils = {
  /**
   * Safely executes a DOM operation with error handling
   * @param {Function} operation - The DOM operation to execute
   * @param {string} [context='DOM operation'] - Context for error logging
   * @returns {*} The result of the operation or null if failed
   */
  safeExecute(operation, context = 'DOM operation') {
    try {
      return operation();
    } catch (error) {
      console.warn(`DOM error in ${context}:`, error);
      return null;
    }
  },

  /**
   * Checks if an element is visible
   * @param {HTMLElement} element - The element to check
   * @returns {boolean} True if element is visible
   */
  isVisible(element) {
    return element &&
      element.offsetWidth > 0 &&
      element.offsetHeight > 0 &&
      getComputedStyle(element).display !== 'none';
  },

  /**
   * Adds an event listener and returns a cleanup function
   * @param {HTMLElement} element - The element to add listener to
   * @param {string} event - The event type
   * @param {Function} handler - The event handler
   * @param {Object} [options={}] - Event listener options
   * @returns {Function} Cleanup function to remove the listener
   */
  addCleanupListener(element, event, handler, options = {}) {
    element.addEventListener(event, handler, options);
    return () => element.removeEventListener(event, handler, options);
  },

  /**
   * Creates a debounced function
   * @param {Function} func - The function to debounce
   * @param {number} wait - Delay in milliseconds
   * @returns {Function} Debounced function
   */
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

  /**
   * Creates a throttled function
   * @param {Function} func - The function to throttle
   * @param {number} limit - Throttle limit in milliseconds
   * @returns {Function} Throttled function
   */
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
  /**
   * Formats a Date object to a time string (HH:mm:ss)
   * @param {Date|string|number} date - The date to format
   * @returns {string} Formatted time string
   */
  time(date) {
    if (!date) return '--:--:--';
    const d = new Date(date);
    if (Number.isNaN(d.getTime())) return '--:--:--';
    return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  },

  /**
   * Formats bytes to human-readable string with appropriate units
   * @param {number} bytes - The number of bytes to format
   * @returns {string} Formatted string
   */
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

  /**
   * Formats bytes per second to human-readable speed string
   * @param {number} bytesPerSecond - The speed in bytes per second
   * @returns {string} Formatted speed string
   */
  formatSpeed(bytesPerSecond) {
    if (!Number.isFinite(bytesPerSecond) || bytesPerSecond < 0) return '–';
    if (bytesPerSecond === 0) return '0 B/s';
    return `${this.formatBytes(bytesPerSecond)}/s`;
  },

  /**
   * Formats seconds to human-readable duration string
   * @param {number} seconds - The duration in seconds
   * @returns {string} Formatted duration string
   */
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

  /**
   * Formats a timestamp to a relative time string
   * @param {number} timestamp - The timestamp to format
   * @returns {string} Formatted relative time string
   */
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

  /**
   * Formats milliseconds to human-readable latency string
   * @param {number} ms - The latency in milliseconds
   * @returns {string} Formatted latency string
   */
  formatLatency(ms) {
    if (!Number.isFinite(ms) || ms <= 0) return '–';
    return `${Math.max(1, Math.round(ms))} ms`;
  },

  /**
   * Formats a numeric value to percentage string
   * @param {number} value - The value to format (0-100)
   * @returns {string} Formatted percentage string
   */
  formatPercentage(value) {
    if (!Number.isFinite(value)) return '0%';
    return `${Math.min(100, Math.max(0, value)).toFixed(0)}%`;
  },

  /**
   * Parses server address string into host and port components
   * @param {string} input - The server address string
   * @returns {{host: string, port: number}|null} Parsed host and port
   */
  parseServerAddress(input) {
    if (!input || typeof input !== 'string') return null;
    let trimmed = input.trim();
    if (trimmed.length === 0) return null;
    if (trimmed.startsWith('http://')) trimmed = trimmed.slice(7);
    else if (trimmed.startsWith('https://')) trimmed = trimmed.slice(8);

    // Remove trailing path
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

/**
 * Clamps a numeric value between minimum and maximum bounds
 * @param {number} value - The value to clamp
 * @param {{min: number, max: number}} bounds - The minimum and maximum bounds
 * @returns {number} The clamped value
 */
function clamp(value, { min, max }) {
  return Math.min(Math.max(value, min), max);
}

/**
 * Generates a UUID v4 compatible string with browser-safe fallback.
 * Uses native crypto.randomUUID when available, otherwise derives from
 * crypto.getRandomValues or Math.random as a last resort.
 * @returns {string} UUID string
 */
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
    // Simple Math.random fallback as a last resort
    return `fallback-${Date.now()}-${Math.floor(Math.random() * 1e9)}`;
  }
}

/**
 * Validates and parses numeric input from an HTML input element
 * @param {HTMLInputElement} input - The input element to validate
 * @param {{min: number, max: number}} bounds - The minimum and maximum allowed values
 * @returns {number|null} The parsed and clamped number, or null if invalid/empty
 */
function validateNumericInput(input, { min, max }) {
  const raw = input.value.trim();
  if (raw.length === 0) {
    return null;
  }
  const numeric = Number.parseInt(raw, 10);
  if (!Number.isFinite(numeric)) {
    return null;
  }
  return clamp(numeric, { min, max });
}

/**
 * Copies text to clipboard with a robust fallback for non-secure contexts.
 *
 * @param {string} text
 * @returns {Promise<boolean>} True if copy succeeded
 */
async function copyTextToClipboard(text) {
  try {
    const content = String(text ?? '');
    if (content.length === 0) {
      return false;
    }

    // Modern API (requires secure context: https:// or http://localhost)
    if (globalThis.navigator?.clipboard?.writeText) {
      await globalThis.navigator.clipboard.writeText(content);
      return true;
    }
  } catch (error) {
    console.warn('navigator.clipboard.writeText failed, falling back:', error);
  }

  // Fallback: show a prompt so the user can copy manually.
  // We intentionally avoid the deprecated copy command API.
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
/**
 * Manages performance-critical updates using requestAnimationFrame batching
 * Prevents excessive DOM updates by batching multiple updates into a single frame
 */
class PerformanceOptimizer {
  /**
   * Creates a new PerformanceOptimizer instance
   */
  constructor() {
    this.pendingUpdates = new Map();
    this.rafId = null;
    this.isScheduled = false;
  }

  /**
   * Schedules an update to be executed in the next animation frame
   * @param {string} key - Unique identifier for the update
   * @param {Function} updateFn - Function to execute when update is flushed
   */
  scheduleUpdate(key, updateFn) {
    this.pendingUpdates.set(key, updateFn);

    if (!this.isScheduled) {
      this.isScheduled = true;
      this.rafId = requestAnimationFrame(() => this.flush());
    }
  }

  /**
   * Executes all pending updates and clears the queue
   */
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

  /**
   * Cancels all pending updates and stops the animation frame
   */
  cancel() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    this.pendingUpdates.clear();
    this.isScheduled = false;
  }
}

/**
 * Creates a debounced function that uses both setTimeout and requestAnimationFrame
 * @param {Function} fn - The function to debounce
 * @param {number} [wait=16] - Delay in milliseconds (approximately 1 frame)
 * @returns {Function} Debounced function
 */
function rafDebounce(fn, wait = 16) {
  let timeoutId = null;
  let rafId = null;

  return function debounced(...args) {
    const later = () => {
      timeoutId = null;
      rafId = requestAnimationFrame(() => {
        fn.apply(this, args);
        rafId = null;
      });
    };

    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    if (rafId) {
      cancelAnimationFrame(rafId);
    }

    timeoutId = setTimeout(later, wait);
  };
}

/**
 * Creates a throttled function that uses requestAnimationFrame
 * @param {Function} fn - The function to throttle
 * @param {number} [limit=16] - Throttle limit in milliseconds (approximately 1 frame)
 * @returns {Function} Throttled function
 */
function rafThrottle(fn, limit = 16) {
  let inThrottle = false;

  return function throttled(...args) {
    if (!inThrottle) {
      requestAnimationFrame(() => {
        fn.apply(this, args);
      });
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

/**
 * Smoothly animates numeric value changes with easing
 * Uses requestAnimationFrame for smooth 60fps animations
 */
class SmoothCounter {
  /**
   * Creates a new SmoothCounter instance
   * @param {HTMLElement} element - The DOM element to update
   * @param {Object} [options] - Animation options
   * @param {number} [options.duration=300] - Animation duration in milliseconds
   * @param {Function} [options.formatFn] - Function to format the display value
   */
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

  /**
   * Sets a new target value and starts animation
   * @param {number} value - The target value
   */
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

  /**
   * Animation loop using requestAnimationFrame
   * @param {DOMHighResTimeStamp} timestamp - The current time
   */
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

  /**
   * Sets the value immediately without animation
   * @param {number} value - The value to set
   */
  setImmediate(value) {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    this.currentValue = value;
    this.targetValue = value;
    this.element.textContent = this.formatFn(value);
  }

  /**
   * Cleans up the animation frame
   */
  destroy() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
  }
}

const performanceOptimizer = new PerformanceOptimizer();

// --- state/state-store.js ---
/**
 * Transfer/backup lifecycle status values used by the Web UI.
 * @typedef {'idle'|'uploading'|'paused'|'completed'|'error'} TransferStatus
 */

/**
 * Canonical application state shape for the Web UI.
 *
 * Notes:
 * - This state is managed by {@link StateStore} and is rendered by `App`.
 * - `serverAddress` uses the format `host:port` (e.g. `localhost:1256`).
 * - `startTime` is a `Date.now()` timestamp (ms) or `null` when idle.
 *
 * @typedef {Object} AppState
 * @property {boolean} connected - Whether the C++ client is connected to the backup server
 * @property {string|null} jobId - Current backup job id (from API) or null
 * @property {TransferStatus} status - Current transfer status
 * @property {number} progress - Progress percentage (0-100)
 * @property {number} speed - Bytes/sec (may be 0 when idle)
 * @property {number} bytesTransferred - Bytes transferred so far
 * @property {number} totalBytes - Total file size in bytes
 * @property {number|null} startTime - Transfer start timestamp (ms since epoch)
 * @property {string} serverAddress - Target backup server address (`host:port`)
 * @property {string} username - Username sent to the backup server
 */

/**
 * Creates a shallow clone of a value
 * @param {*} value - The value to clone
 * @returns {*} The cloned value
 */
function shallowClone(value) {
  if (value === null || typeof value !== 'object') {
    return value;
  }

  if (Array.isArray(value)) {
    return [...value];
  }

  return { ...value };
}

/**
 * Performs shallow equality comparison between two objects
 * @param {*} objA - First object to compare
 * @param {*} objB - Second object to compare
 * @returns {boolean} True if objects are shallowly equal
 */
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

/**
 * Reactive state container with requestAnimationFrame batching
 * Provides a centralized way to manage application state with efficient updates
 * @template T
 */
class StateStore {
  #state;
  #listeners;
  #pendingUpdate;
  #updateScheduled;

  /**
   * Creates a new StateStore instance
    * @param {T} initialState - The initial state
   */
  constructor(initialState) {
    this.#state = shallowClone(initialState);
    this.#listeners = new Set();
    this.#pendingUpdate = null;
    this.#updateScheduled = false;
  }

  /**
   * Gets the current state snapshot
   * @returns {T} The current state
   */
  get snapshot() {
    return this.#state;
  }

  /**
   * Updates state with a patch object
   * Updates are batched and executed in the next animation frame
    * @param {Partial<T>} patch - Partial state update
   */
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

  /**
   * Flushes pending updates to state and notifies listeners
   * @private
   */
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

  /**
   * Updates state immediately without batching
    * @param {Partial<T>} patch - Partial state update
   */
  updateImmediate(patch) {
    const next = { ...this.#state, ...patch };
    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }
  }

  /**
   * Mutates state directly using a mutator function
   * Useful for complex updates that need reference equality detection
    * @param {(draft: T) => void} mutator - Function that receives and mutates the state
   */
  mutate(mutator) {
    const next = { ...this.#state };
    mutator(next);

    if (!shallowEqual(this.#state, next)) {
      this.#state = next;
      this.#notifyListeners(next);
    }
  }

  /**
   * Notifies all listeners of state changes
    * @param {T} state - The new state
   * @private
   */
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

  /**
   * Subscribes a listener to state changes
   * Returns an unsubscribe function
    * @param {(state: T) => void} listener - Function to call when state changes
   * @returns {Function} Unsubscribe function
   */
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

/**
 * Manages toast notifications with accessibility features
 * Supports multiple variants and automatic cleanup
 */
class ToastManager {
  #stack;
  #activeToasts;

  /**
   * Creates a new ToastManager instance
   * @param {HTMLElement} stackElement - The container element for toasts
   */
  constructor(stackElement) {
    this.#stack = stackElement;
    this.#activeToasts = new Set();
  }

  /**
   * Shows a toast notification
   * @param {string} message - The toast message
   * @param {string} [variant='info'] - Toast variant (info, success, warning, error)
   * @param {number} [duration=4000] - Duration in milliseconds (0 for persistent)
   * @returns {Function} Function to close the toast manually
   */
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

  /**
   * Clears all active toast notifications
   */
  clear() {
    for (const toast of this.#activeToasts) {
      toast.remove();
    }
    this.#activeToasts.clear();
  }
}

// --- ui/accessibility.js ---
/**
 * Manages screen reader announcements using live regions
 * Queues announcements to prevent overlap and ensure proper timing
 */
class ScreenReaderAnnouncer {
  #pendingMessages = [];
  #isAnnouncing = false;
  #lastMessage = '';
  #lastAnnounceAt = 0;

  /**
   * Creates a new ScreenReaderAnnouncer instance
   * @param {HTMLElement} liveRegion - The live region element for announcements
   */
  constructor(liveRegion) {
    this.liveRegion = liveRegion;
  }

  /**
   * Announces a message to screen readers
   * Messages are queued and announced sequentially
   * @param {string} message - The message to announce
   */
  announce(message) {
    if (!this.liveRegion) return;

    const next = String(message ?? '').trim();
    if (!next) return;

    const now = Date.now();
    // Dedupe repeated messages within a short window to avoid chatty live regions.
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

  /**
   * Flushes the message queue to announce pending messages
   * @private
   */
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

// --- utils/api-config.js ---
/**
 * API Configuration utilities for cross-origin and protocol detection
 */
/**
 * API Configuration utilities for cross-origin and protocol detection
 */
/**
 * @typedef {Object} ApiConfig
 * @property {number} API_PORT - Flask API server port
 * @property {number} STATIC_PORT - Static file server port (development)
 * @property {() => boolean} isFileProtocol - True when opened via file://
 * @property {() => string} getApiBaseUrl - Base URL for API calls ('' for same-origin)
 * @property {(toastFn: Function) => void} showFileProtocolWarning - User hint for file:// mode
 */

/** @type {ApiConfig} */
const API_CONFIG = {
  // Default API server port
  API_PORT: 9090,
  // Static file server port (when served separately)
  STATIC_PORT: 9091,

  /**
   * Check if the page is opened via file:// protocol
   * @returns {boolean} True if page is opened via file:// protocol
   */
  isFileProtocol() {
    return globalThis.location?.protocol === 'file:';
  },

  /**
   * Get the appropriate API base URL based on current origin
   * @returns {string} The API base URL or empty string for same-origin
   */
  getApiBaseUrl() {
    const { location } = globalThis;
    if (!location) return '';

    // If opened as file://, we can't make API calls - return empty and let app handle gracefully
    if (location.protocol === 'file:') {
      console.warn('[API Config] Page opened via file:// protocol - API calls will not work');
      return '';
    }

    const { hostname = 'localhost', port, protocol } = location;
    const currentPort = Number.parseInt(port, 10) || (protocol === 'https:' ? 443 : 80);

    // If we're on the API server port (9090), use same origin
    if (currentPort === this.API_PORT) {
      return '';
    }

    // If we're on a different port (e.g., static server on 9091), point to API server
    return `http://${hostname}:${this.API_PORT}`;
  },

  /**
   * Show a small notification when page is opened via file:// protocol
   * @param {Function} toastFn - Toast function to show notification
   */
  showFileProtocolWarning(toastFn) {
    if (typeof toastFn === 'function') {
      toastFn(
        '⚠️ Running from file:// - API features disabled. Use HTTP server for full functionality.',
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

/**
 * Safe sessionStorage wrapper with the same API as safeLocalStorage.
 * @param {string} key
 * @param {string|null|undefined} [value]
 * @returns {string|null}
 */
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

// In-memory fallback when persistent storage is unavailable
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
/**
 * Unified timer management utility
 * Handles setInterval/clearInterval patterns with automatic cleanup
 */
/**
 * Unified timer management utility
 * Handles setInterval/clearInterval patterns with automatic cleanup
 */
class TimerManager {
  #timerId = null;

  /**
   * Start a timer, automatically clearing any existing timer first
   * @param {Function} callback - Function to execute repeatedly
   * @param {number} interval - Interval in milliseconds
   * @returns {void}
   */
  start(callback, interval) {
    this.stop();
    this.#timerId = globalThis.setInterval(callback, interval);
  }

  /**
   * Stop the timer if it exists
   * @returns {void}
   */
  stop() {
    if (this.#timerId) {
      globalThis.clearInterval(this.#timerId);
      this.#timerId = null;
    }
  }

  /**
   * Check if timer is currently running
   * @returns {boolean} True if timer is active
   */
  isRunning() {
    return this.#timerId !== null;
  }

  /**
   * Get the current timer ID (for debugging)
   * @returns {number|null} Timer ID or null if not running
   */
  getTimerId() {
    return this.#timerId;
  }
}

/**
 * Shared application constants.
 *
 * Focus: validation + safe defaults used across modules.
 * @namespace CONSTANTS
 */
const CONSTANTS = {
  /** Maximum allowed upload size in bytes (1 GB). */
  MAX_FILE_SIZE: 1024 * 1024 * 1024,

  /** Allowed username characters: alphanumeric, underscore, dash, dot, space, @. */
  USERNAME_PATTERN: /^[\w\-. @]+$/,
};

/**
 * File validation configuration
 */
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
  ],
  errorMessages: {
    sizeExceeded: 'File too large. Maximum allowed size is 1 GB.',
    invalidType: 'Unsupported file type. Only .zip and .tar archives are allowed.',
    empty: 'File is empty.',
  },

  isExtensionAllowed(filename) {
    if (!filename) return false;
    const lower = filename.toLowerCase();
    return this.allowedExtensions.some((ext) => lower.endsWith(ext));
  },

  isMimeAllowed(mime) {
    if (!mime) return false;
    return this.allowedMimeTypes.includes(mime.toLowerCase());
  },

  validate(file) {
    if (!file) {
      return { valid: false, error: this.errorMessages.invalidType };
    }

    if (file.size === 0) {
      return { valid: false, error: this.errorMessages.empty };
    }

    if (file.size > this.maxSize) {
      return { valid: false, error: this.errorMessages.sizeExceeded };
    }

    const typeOk = this.isMimeAllowed(file.type) || this.isExtensionAllowed(file.name || '');
    if (!typeOk) {
      return { valid: false, error: this.errorMessages.invalidType };
    }

    return { valid: true };
  },
};

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
  rafDebounce,
  rafThrottle,
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