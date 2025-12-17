# CyberBackup Web UI - Comprehensive Implementation Plan

**Target Files:** `api_server/web_ui/`
**Estimated Effort:** 3-4 development sessions
**Priority:** Fix critical bugs first, then enhancements

---

## Progress Update (2025-12-16)

### Completed
- **Task 2 – Duplicate DOM registration**: Removed the second `dom.logContainer` assignment (see `js/core-utils.js`).
- **Task 3 – Browser compatibility**: Added `generateUUID` fallback and wired LogStore to use it (see `js/core-utils.js`, `js/ui.js`).
- **Task 4 – File validation**: Implemented size/type validation, toasts, announcer messaging, and preview clearing; added validation constants and CSS error/focus states (see `js/core-utils.js`, `js/ui.js`, `js/app.js`, `css/styles.css`).
- **Task 7 – Connection double-click prevention**: Added operation lock and connecting/disconnecting flags to guard connect/disconnect/start paths (see `js/app.js`).
- **Task 9 – Accessibility**:
  - Progress ring now exposes ARIA progressbar attrs and updates `aria-valuenow` (see `index.html`, `js/app.js`).
  - Speed chart has role/summary live text (see `index.html`, `js/ui.js`, `js/core-utils.js`).
  - File drop/selection now announces results via ScreenReaderAnnouncer (see `js/ui.js`).
  - Shortcut modal gained a focus trap; focus-visible outlines added for interactive controls (see `js/ui.js`, `css/styles.css`).
- **Task 10 – Performance**:
  - 10.1 Debounced SpeedChart resize handler to prevent excessive redraws (see `js/ui.js`).
  - 10.2 Log filtering now tracks visible count via LogStore instead of DOM scans (see `js/ui.js`).
  - 10.3 Animations pause when idle via render-time gating and CSS (see `js/app.js`, `css/styles.css`).
  - 10.4 Circuit pattern extracted to external SVG asset to reduce CSS weight (see `css/styles.css`, `img/circuit-pattern.svg`).
- **Task 19 – Global error handlers**: Added window-level `error` and `unhandledrejection` hooks in `app.js` that route failures through `ErrorBoundary` (toasts + status strip). Follow-up: registration is now performed once during `App.init()` (not during render/event binding) and includes a small alias wrapper to avoid future regressions.
- **Task 20 – LocalStorage error handling**: Implemented `safeLocalStorage`/`safeSessionStorage` with quota/security handling and in-memory fallback; replaced direct usage in theme persistence, advanced settings, and demo-mode detection (see `js/core-utils.js`, `js/ui.js`, `js/core.js`, `js/app.js`).

- **Task 15 – New Features (implemented)**:
  - 15.1 Auto theme mode (`dark`/`light`/`auto`) with system preference sync (see `js/ui.js`, `index.html`).
  - 15.2 Basic transfer history persistence (success/failure) using storage fallback (see `js/app.js`, `js/core-utils.js`).

- **Transfer History UI (follow-up completed)**:
  - Added a dedicated “Transfer History” section to the main dashboard with a semantic `<ul>` list and a “Clear history” action (see `index.html`).
  - Wired DOM registry support (`dom.transferHistoryList`) and added render + clear behavior (see `js/core-utils.js`, `js/app.js`).
  - Added layout/styling so the history sits between Status and Activity Logs without breaking the responsive grid (see `css/styles.css`).

- **Task 18 – Documentation Improvements (implemented)**:
  - 18.1 Added JSDoc to `App` (see `js/app.js`).
  - 18.2 Documented `AppState` shape (`@typedef`) (see `js/core-utils.js`).
  - 18.3 Documented `CONSTANTS` with JSDoc (see `js/core-utils.js`).

### Completed (since 2025-12-16)
- **Task 11 – Code Organization Refactoring**:
  - Demo mode extracted into `DemoMode` (`js/demo-mode.js`) and loaded before `app.js`; `app.js` now delegates demo start/pause/resume/stop to the class.
  - Minor `app.js` readability cleanup (stale comment + extra blank lines removed).
- **Task 9 – Accessibility (incremental)**:
  - Phase text is now a live `<output>` element (polite/atomic) so status transitions are announced more reliably (see `index.html`).
  - Progress ring semantics now use a visually-hidden native `<progress>` element (with the SVG ring marked decorative), avoiding misleading custom ARIA on SVG (see `index.html`, `js/core-utils.js`, `js/app.js`).
  - Stat cards are no longer keyboard-focusable and no longer use `role="status"` (they were not interactive); values remain readable and updated normally (see `index.html`, `js/app.js`).
  - Speed chart canvas no longer uses `role="img"`; it uses fallback text + `aria-describedby` pointing at the existing screen-reader summary (see `index.html`).
- **Task 13 – Missing Visual Feedback (key items)**:
  - Stats now pulse on change (lightweight value-change detection + CSS pulse) (see `js/app.js`).
  - Status panel now shows explicit visual accents for `paused` / `completed` / `error` (ring stroke + glow + status text) (see `js/app.js`, `css/styles.css`).
  - Log action buttons now provide brief positive feedback on success (flash state) (see `js/ui.js`, `css/styles.css`).
- **Task 14 – Feature Completions (selected items)**:
  - Keyboard shortcuts expanded (clear logs, open file picker, Enter primary action, Space pause/resume, Esc-to-stop safety latch) (see `js/ui.js`).
- **Task 12 – Visual Consistency Fixes (key items)**:
  - Consolidated spacing tokens: `--space-*` is primary and `--gap-*` are aliases for backward compatibility (see `css/styles.css`).
  - Consolidated motion tokens: transitions now derive from `--duration-*` + `--ease-default`; added `--duration-slow` (see `css/styles.css`).
  - Progress ring gradient now matches brand tokens (`--primary-400` / `--secondary-400` / `--accent-400`) (see `index.html`).
  - Inline banner icon contrast improved for theme consistency / accessibility tooling (see `css/styles.css`).
- **Testing tooling (quality-of-life)**:
  - Playwright web GUI capture script now retries `localhost` URLs with `127.0.0.1` on connection refusal (common IPv6/IPv4 binding mismatch on Windows) (see `tests/integration/test_web_gui.py`).

- **Task 9 – Accessibility (announcement strategy)**:
  - Removed noisy `aria-live` usage on frequently-updating UI regions (toasts container, header connection pills, quality/last-checked, speed chart summary, log container) to avoid constant screen reader interruptions (see `index.html`).
  - Added change-driven announcements for API/Backup server online/offline transitions (see `js/ui.js`).
  - Hardened `ScreenReaderAnnouncer` with dedupe/throttle behavior to reduce bursty repeated announcements (see `js/core-utils.js`).

### Outstanding / Not Started
- Optional follow-ups:
  - Add an “Export history” action (CSV/JSON) and/or a simple filter (success/fail).
  - Consider a confirmation dialog for “Clear history” if accidental clicks become a problem.
  - Add a small Playwright assertion to verify the Transfer History section renders and updates.

---

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Task 2: Duplicate DOM Registration Fix](#task-2-duplicate-dom-registration-fix)
3. [Task 3: Browser Compatibility Fix](#task-3-browser-compatibility-fix)
4. [Task 4: File Validation Implementation](#task-4-file-validation-implementation)
5. [Task 7: Connection Double-Click Prevention](#task-7-connection-double-click-prevention)
6. [Task 9: Accessibility Improvements](#task-9-accessibility-improvements)
7. [Task 10: Performance Optimizations](#task-10-performance-optimizations)
8. [Task 11: Code Organization Refactoring](#task-11-code-organization-refactoring)
9. [Task 12: Visual Consistency Fixes](#task-12-visual-consistency-fixes)
10. [Task 13: Missing Visual Feedback](#task-13-missing-visual-feedback)
11. [Task 14: Feature Completions](#task-14-feature-completions)
12. [Task 15: New Features](#task-15-new-features)
13. [Task 18: Documentation Improvements](#task-18-documentation-improvements)
14. [Task 19: Global Error Handlers](#task-19-global-error-handlers)
15. [Task 20: LocalStorage Error Handling](#task-20-localstorage-error-handling)
16. [Testing Checklist](#testing-checklist)

---

## Prerequisites

### File Structure Reference
```
api_server/web_ui/
├── index.html              # Main entry point
├── css/
│   └── styles.css          # All CSS (~2500 lines)
├── js/
│   ├── core-utils.js       # DOM registry, formatters, StateStore, utils (~700 lines)
│   ├── core.js             # ApiClient, SocketClient, ConnectionMonitor (~500 lines)
│   ├── ui.js               # ThemeManager, LogStore, FileManager, SpeedChart, ProfessionalGUIEnhancements (~800 lines)
│   └── app.js              # Main App class (~780 lines)
└── favicon.svg
```

### Key Classes to Understand
- `StateStore` (core-utils.js:676-699): Reactive state container with RAF batching
- `App` (app.js:7-768): Main controller, orchestrates all components
- `FileManager` (ui.js:145-203): Handles file selection and drag-drop
- `ProfessionalGUIEnhancements` (ui.js:338-800): UI enhancements, shortcuts, animations

### Constants to Use
```javascript
// Add to top of core-utils.js
const CONSTANTS = {
  MAX_FILE_SIZE: 1024 * 1024 * 1024, // 1GB
  ALLOWED_FILE_TYPES: ['application/zip', 'application/x-tar', 'application/x-gzip', 'application/gzip'],
  ALLOWED_EXTENSIONS: ['zip', 'tar', 'gz', 'tar.gz', 'tgz'],
  MIN_CHUNK_SIZE: 1,
  MAX_CHUNK_SIZE: 256,
  MIN_RETRY_LIMIT: 0,
  MAX_RETRY_LIMIT: 20,
  SERVER_PORT_MIN: 1,
  SERVER_PORT_MAX: 65535,
  USERNAME_MAX_LENGTH: 255,
  USERNAME_PATTERN: /^[\w\-. @]+$/, // Alphanumeric, dash, dot, space, @
};
```

---

## Task 2: Duplicate DOM Registration Fix

### Problem
`dom.logContainer` is assigned twice in `core-utils.js`, causing unnecessary computation and potential confusion.

### Current Code Location
**File:** `js/core-utils.js`
**Lines:** 144 and 163

```javascript
// Line 144
dom.logContainer = getElement('logContainer');

// ... more code ...

// Line 163 (DUPLICATE)
dom.logContainer = getElement('logContainer'); // Standardized name
```

### Fix Required
Remove the duplicate assignment on line 163.

### Implementation Steps

1. **Open** `js/core-utils.js`
2. **Find** line 163 containing duplicate `dom.logContainer`
3. **Delete** the entire line 163
4. **Verify** line 144 remains as the single source

### Before
```javascript
// Line 163
dom.logContainer = getElement('logContainer'); // Standardized name
```

### After
```javascript
// Line 163 - REMOVED
```

### Verification
- Search file for `dom.logContainer` - should appear exactly ONCE in assignment
- App should load without console errors

---

## Task 3: Browser Compatibility Fix

### Problem
`crypto.randomUUID()` used in `ui.js` is not supported in Safari < 15.4, but CLAUDE.md claims Safari 14+ support.

### Current Code Location
**File:** `js/ui.js`
**Lines:** 68-75 (LogStore.add method)

```javascript
add(message, { level = 'info', phase = 'GENERAL' } = {}) {
  const entry = {
    id: crypto.randomUUID(), // FAILS in Safari < 15.4
    timestamp: new Date(),
    message,
    level,
    phase
  };
```

### Fix Required
Add a fallback UUID generator that works in all browsers.

### Implementation Steps

1. **Add** UUID generator function to `js/core-utils.js` (after line 400):

```javascript
/**
 * Generates a UUID v4 compatible string
 * Uses crypto.randomUUID() when available, falls back to Math.random()
 * @returns {string} UUID string
 */
function generateUUID() {
  // Use native implementation if available (Chrome 92+, Firefox 95+, Safari 15.4+)
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }

  // Fallback for older browsers
  // Uses crypto.getRandomValues for better randomness when available
  if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const array = new Uint8Array(1);
      crypto.getRandomValues(array);
      const r = array[0] % 16;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // Last resort fallback using Math.random (less secure but works everywhere)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
```

2. **Update** `js/ui.js` LogStore class:

```javascript
// Line ~70 - Replace crypto.randomUUID() with generateUUID()
add(message, { level = 'info', phase = 'GENERAL' } = {}) {
  const entry = {
    id: generateUUID(), // Uses fallback for older browsers
    timestamp: new Date(),
    message,
    level,
    phase
  };
```

### Verification
- Test in Safari 14 simulator or BrowserStack
- Console should not show errors about `randomUUID`
- Log entries should have unique IDs

---

## Task 4: File Validation Implementation

### Problem
UI claims "Up to 1 GB" and ".zip, .tar" but no validation exists. Users can upload any file type of any size.

### Current Code Location
**File:** `js/ui.js`
**Class:** `FileManager`
**Lines:** 145-203

```javascript
#handleFiles(files) {
  if (files?.length) {
    const file = files[0];
    this.onFileSelect(file); // NO VALIDATION!
    ProfessionalGUIEnhancements.updateFileCardPreview(file);
  }
}
```

### Fix Required
Add file size and type validation before accepting files.

### Implementation Steps

1. **Add** validation constants to `js/core-utils.js` (after CONSTANTS):

```javascript
/**
 * File validation configuration
 */
const FILE_VALIDATION = {
  maxSize: 1024 * 1024 * 1024, // 1GB
  maxSizeDisplay: '1 GB',
  allowedMimeTypes: [
    'application/zip',
    'application/x-zip-compressed',
    'application/x-tar',
    'application/x-gzip',
    'application/gzip',
    'application/x-compressed-tar'
  ],
  allowedExtensions: ['zip', 'tar', 'gz', 'tgz', 'tar.gz'],

  /**
   * Validates a file against size and type constraints
   * @param {File} file - The file to validate
   * @returns {{valid: boolean, error?: string}} Validation result
   */
  validate(file) {
    if (!file) {
      return { valid: false, error: 'No file selected' };
    }

    // Size check
    if (file.size > this.maxSize) {
      const actualSize = formatters.formatBytes(file.size);
      return {
        valid: false,
        error: `File too large (${actualSize}). Maximum size is ${this.maxSizeDisplay}.`
      };
    }

    // Empty file check
    if (file.size === 0) {
      return { valid: false, error: 'File is empty' };
    }

    // Extension check
    const fileName = file.name || '';
    const extension = fileName.includes('.')
      ? fileName.split('.').pop().toLowerCase()
      : '';
    const hasDoubleExt = fileName.toLowerCase().endsWith('.tar.gz');
    const effectiveExt = hasDoubleExt ? 'tar.gz' : extension;

    if (!this.allowedExtensions.includes(effectiveExt)) {
      return {
        valid: false,
        error: `Invalid file type (.${extension}). Allowed: ${this.allowedExtensions.join(', ')}`
      };
    }

    // MIME type check (if available and reliable)
    // Note: MIME types can be spoofed, extension is primary check
    if (file.type && !this.allowedMimeTypes.includes(file.type) && file.type !== '') {
      console.warn(`MIME type mismatch: ${file.type} for file ${fileName}`);
      // Don't reject - browsers report inconsistent MIME types
    }

    return { valid: true };
  }
};
```

2. **Update** `FileManager` in `js/ui.js`:

```javascript
class FileManager {
  constructor(input, dropZone, onFileSelect) {
    this.input = input;
    this.dropZone = dropZone;
    this.onFileSelect = onFileSelect;
    this.toast = null; // Will be set from App
    this.#bindEvents();
  }

  /**
   * Sets the toast manager for showing validation errors
   * @param {ToastManager} toastManager
   */
  setToast(toastManager) {
    this.toast = toastManager;
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
    if (!files?.length) return;

    const file = files[0];

    // VALIDATION
    const validation = FILE_VALIDATION.validate(file);

    if (!validation.valid) {
      // Show error to user
      if (this.toast) {
        this.toast.show(validation.error, 'error');
      } else {
        console.error('File validation failed:', validation.error);
        alert(validation.error); // Fallback
      }

      // Clear the input
      if (this.input) this.input.value = '';
      return;
    }

    // File is valid - proceed
    this.onFileSelect(file);
    ProfessionalGUIEnhancements.updateFileCardPreview(file);
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
```

3. **Update** `App` constructor in `js/app.js` to pass toast manager:

```javascript
// After line 32 (FileManager instantiation)
this.fileManager = new FileManager(dom.fileInput, dom.fileDropZone, (file) => this.#onFileSelected(file));
this.fileManager.setToast(this.toast); // ADD THIS LINE
```

4. **Add** validation for advanced settings inputs in `js/ui.js` or create new `AdvancedSettings` class:

```javascript
/**
 * Advanced settings manager with validation
 */
class AdvancedSettings {
  constructor({ chunkInput, retryInput, resetButton, restoreLink, toast, announcer }) {
    this.chunkInput = chunkInput;
    this.retryInput = retryInput;
    this.resetButton = resetButton;
    this.restoreLink = restoreLink;
    this.toast = toast;
    this.announcer = announcer;

    this.defaults = {
      chunkSize: 8,
      retryLimit: 3
    };

    this.#bindEvents();
  }

  #bindEvents() {
    // Chunk size validation
    this.chunkInput?.addEventListener('blur', () => this.#validateChunkSize());
    this.chunkInput?.addEventListener('input', () => this.#clearError(this.chunkInput));

    // Retry limit validation
    this.retryInput?.addEventListener('blur', () => this.#validateRetryLimit());
    this.retryInput?.addEventListener('input', () => this.#clearError(this.retryInput));

    // Reset button
    this.resetButton?.addEventListener('click', () => this.reset());
    this.restoreLink?.addEventListener('click', (e) => {
      e.preventDefault();
      this.restoreDefaults();
    });
  }

  #validateChunkSize() {
    if (!this.chunkInput) return true;
    const value = parseInt(this.chunkInput.value, 10);

    if (isNaN(value) || value < 1 || value > 256) {
      this.#showInputError(this.chunkInput, 'Chunk size must be 1-256 MB');
      return false;
    }

    this.#clearError(this.chunkInput);
    return true;
  }

  #validateRetryLimit() {
    if (!this.retryInput) return true;
    const value = parseInt(this.retryInput.value, 10);

    if (isNaN(value) || value < 0 || value > 20) {
      this.#showInputError(this.retryInput, 'Retry limit must be 0-20');
      return false;
    }

    this.#clearError(this.retryInput);
    return true;
  }

  #showInputError(input, message) {
    const hint = input.parentElement?.querySelector('.hint');
    if (hint) {
      hint.textContent = message;
      hint.classList.add('error');
    }
    input.classList.add('input-error');
    input.setAttribute('aria-invalid', 'true');
  }

  #clearError(input) {
    const hint = input.parentElement?.querySelector('.hint');
    if (hint) {
      hint.classList.remove('error');
      // Restore original hint text
      if (input === this.chunkInput) hint.textContent = '1–256 MB';
      if (input === this.retryInput) hint.textContent = '0–20 retries';
    }
    input.classList.remove('input-error');
    input.removeAttribute('aria-invalid');
  }

  /**
   * Gets validated options for API calls
   * @returns {{chunkSize: number, retryLimit: number}|null} Options or null if invalid
   */
  getOptions() {
    const chunkValid = this.#validateChunkSize();
    const retryValid = this.#validateRetryLimit();

    if (!chunkValid || !retryValid) {
      this.toast?.show('Please fix invalid settings before starting', 'error');
      return null;
    }

    return {
      chunkSize: parseInt(this.chunkInput?.value, 10) || this.defaults.chunkSize,
      retryLimit: parseInt(this.retryInput?.value, 10) ?? this.defaults.retryLimit
    };
  }

  reset() {
    if (this.chunkInput) {
      this.chunkInput.value = '';
      this.#clearError(this.chunkInput);
    }
    if (this.retryInput) {
      this.retryInput.value = '';
      this.#clearError(this.retryInput);
    }
    this.toast?.show('Settings cleared', 'info');
  }

  restoreDefaults() {
    if (this.chunkInput) {
      this.chunkInput.value = this.defaults.chunkSize;
      this.#clearError(this.chunkInput);
    }
    if (this.retryInput) {
      this.retryInput.value = this.defaults.retryLimit;
      this.#clearError(this.retryInput);
    }
    this.toast?.show('Defaults restored', 'info');
  }
}
```

5. **Add** CSS for validation error state in `css/styles.css`:

```css
/* Input validation error state */
.input-error,
input.input-error,
input[aria-invalid="true"] {
  border-color: var(--danger) !important;
  box-shadow: 0 0 0 2px rgba(248, 81, 73, 0.2);
}

.hint.error {
  color: var(--danger);
  font-weight: 500;
}
```

### Verification
- Try uploading a 2GB file → Should show error toast
- Try uploading a .exe file → Should show error toast
- Try uploading a valid .zip file → Should succeed
- Try setting chunk size to 500 → Should show error on blur
- Try setting retry limit to -5 → Should show error on blur

---

## Task 7: Connection Double-Click Prevention

### Problem
Users can click CONNECT button multiple times rapidly, potentially causing race conditions.

### Current Code Location
**File:** `js/app.js`
**Lines:** 206-212

```javascript
#handlePrimaryAction() {
  if (this.state.snapshot.connected) {
    this.#handleDisconnect();
  } else {
    this.#handleConnect(); // Can be called multiple times!
  }
}
```

### Fix Required
Add operation lock and proper loading state management.

### Implementation Steps

1. **Add** operation lock state to App class:

```javascript
// In App constructor (around line 10)
constructor() {
  this.operationInProgress = false; // ADD THIS

  // Initialize State
  this.state = new StateStore({
    connected: false,
    connecting: false, // ADD THIS
    disconnecting: false, // ADD THIS
    // ... rest of state
  });
```

2. **Update** `#handlePrimaryAction`:

```javascript
#handlePrimaryAction() {
  // Prevent double-clicks during operations
  if (this.operationInProgress) {
    console.log('Operation already in progress, ignoring click');
    return;
  }

  if (this.state.snapshot.connected) {
    this.#handleDisconnect();
  } else {
    this.#handleConnect();
  }
}
```

3. **Update** `#handleConnect` with proper locking:

```javascript
async #handleConnect() {
  // Check for file:// protocol
  if (API_CONFIG.isFileProtocol()) {
    this.toast.show('API unavailable in file:// mode. Open http://localhost:9090 instead.', 'warn');
    this.setConnectionStatus('API unavailable in file:// mode', 'error');
    return;
  }

  // Prevent re-entry
  if (this.operationInProgress) return;
  this.operationInProgress = true;

  const addressInput = dom.serverInput?.value || dom.serverAddress?.value;
  const parsed = formatters.parseServerAddress(addressInput);
  const username = (dom.usernameInput?.value || '').trim() || this.state.snapshot.username;

  if (!parsed) {
    this.toast.show('Invalid server address format. Use host:port', 'error');
    this.#updateConnectionStatus('Invalid address format', 'error');
    this.operationInProgress = false;
    return;
  }

  try {
    // Update button to connecting state
    this.#setButtonState('connecting');
    this.state.update({ connecting: true });
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
      connecting: false,
      serverAddress: `${parsed.host}:${parsed.port}`,
      username
    });

    this.#setButtonState('connected');
    this.#updateConnectionStatus(`Connected to ${parsed.host}:${parsed.port}`, 'success');
    this.hideInlineBanner();
    this.toast.show('Connected to backup server', 'success');
    this.logs.add(`Connected to ${parsed.host}:${parsed.port}`, { phase: 'NET' });

  } catch (error) {
    this.state.update({ connecting: false });
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
```

4. **Update** `#handleDisconnect` with proper locking:

```javascript
async #handleDisconnect() {
  // Prevent re-entry
  if (this.operationInProgress) return;
  this.operationInProgress = true;

  try {
    this.#setButtonState('disconnecting');
    this.state.update({ disconnecting: true });
    this.#updateConnectionStatus('Disconnecting...', 'pending');

    await this.api.disconnect();
    this.state.update({
      connected: false,
      disconnecting: false,
      status: 'idle'
    });

    this.#setButtonState('idle');
    this.#updateConnectionStatus('Disconnected', 'info');
    this.toast.show('Disconnected from server', 'info');
    this.logs.add('Disconnected', { phase: 'NET' });
  } catch (error) {
    this.state.update({ disconnecting: false });
    this.#setButtonState('connected'); // Restore if disconnect failed
    this.#updateConnectionStatus('Disconnect failed', 'error');
    ErrorBoundary.handle(error, 'Disconnect');
  } finally {
    this.operationInProgress = false;
  }
}
```

5. **Also protect backup operations** - Update `#handleStartBackup`:

```javascript
async #handleStartBackup(fileArg) {
  const file = fileArg || this.fileManager.input?.files?.[0];

  if (!file) {
    this.toast.show('Please select a file first', 'warn');
    return;
  }

  if (!this.state.snapshot.connected) {
    this.toast.show('Please connect to a server first', 'warn');
    return;
  }

  // Prevent starting backup while one is in progress
  if (this.state.snapshot.status === 'uploading') {
    this.toast.show('Backup already in progress', 'warn');
    return;
  }

  // Validate advanced settings before starting
  const options = this.advancedSettings.getOptions();
  if (options === null) {
    return; // Validation failed, error already shown
  }

  try {
    this.state.update({
      status: 'uploading',
      progress: 0,
      startTime: Date.now(),
      totalBytes: file.size,
      bytesTransferred: 0,
    });

    const [host, port] = this.state.snapshot.serverAddress.split(':');

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
  }
}
```

### Verification
- Click CONNECT rapidly 5 times → Only first should work
- Click while "Connecting..." shows → Button should be disabled
- Click DISCONNECT while connecting → Should be ignored
- Watch for race condition errors in console

---

## Task 9: Accessibility Improvements

### Problem
Multiple accessibility issues: progress ring not announced, canvas without alt text, missing focus traps, etc.

### Implementation Steps

### 9.1 Progress Ring Accessibility

**File:** `index.html`
**Lines:** 347-372

**Current:**
```html
<svg id="progressRing" viewBox="0 0 100 100" aria-hidden="true">
```

**Change to:**
```html
<svg id="progressRing" viewBox="0 0 100 100" role="progressbar"
     aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"
     aria-label="Backup progress">
```

**Update** `js/app.js` `#renderProgressRing`:

```javascript
#renderProgressRing(progress) {
  if (!dom.progressArc) return;
  const pct = this.#clampPct(progress);
  const r = 45;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - pct / 100);
  dom.progressArc.style.strokeDasharray = `${circumference}`;
  dom.progressArc.style.strokeDashoffset = `${offset}`;

  // Update ARIA for screen readers
  if (dom.progressRing) {
    dom.progressRing.setAttribute('aria-valuenow', Math.round(pct));
  }
}
```

### 9.2 Speed Chart Canvas Accessibility

**File:** `index.html`
**Lines:** 454

**Current:**
```html
<canvas id="speedChart" class="speed-chart"></canvas>
```

**Change to:**
```html
<canvas id="speedChart" class="speed-chart" role="img"
        aria-label="Transfer speed chart showing throughput over the last 30 seconds"></canvas>
<div id="speedChartSummary" class="sr-only" aria-live="polite">
  Current speed: calculating...
</div>
```

**Update** `SpeedChart.draw()` in `js/ui.js`:

```javascript
draw() {
  if (!this.ctx || this.dataPoints.length === 0) return;
  // ... existing draw code ...

  // Update screen reader summary
  const summary = document.getElementById('speedChartSummary');
  if (summary && this.dataPoints.length > 0) {
    const latestSpeed = this.dataPoints[this.dataPoints.length - 1];
    summary.textContent = `Current speed: ${formatters.formatSpeed(latestSpeed)}. ` +
      `Peak: ${formatters.formatSpeed(this.maxSpeed)}.`;
  }
}
```

### 9.3 File Drop Zone State Announcements

**Update** `FileManager` in `js/ui.js`:

```javascript
#handleFiles(files) {
  if (!files?.length) return;

  const file = files[0];

  // VALIDATION
  const validation = FILE_VALIDATION.validate(file);

  if (!validation.valid) {
    // Announce error to screen readers
    this.#announce(`File rejected: ${validation.error}`);
    // ... rest of error handling
    return;
  }

  // Announce success
  this.#announce(`File selected: ${file.name}, ${formatters.formatBytes(file.size)}`);

  // File is valid - proceed
  this.onFileSelect(file);
  ProfessionalGUIEnhancements.updateFileCardPreview(file);
}

clear() {
  if (this.input) this.input.value = '';
  ProfessionalGUIEnhancements.updateFileCardPreview(null);
  this.onFileSelect(null);
  this.#announce('File selection cleared');
}

#announce(message) {
  if (dom.srLive) {
    dom.srLive.textContent = message;
    // Clear after a delay to allow repeated announcements
    setTimeout(() => {
      if (dom.srLive) dom.srLive.textContent = '';
    }, 1000);
  }
}
```

### 9.4 Modal Focus Trap

**Add** to `js/ui.js` or `ProfessionalGUIEnhancements`:

```javascript
/**
 * Focus trap utility for modal dialogs
 */
class FocusTrap {
  constructor(element) {
    this.element = element;
    this.firstFocusable = null;
    this.lastFocusable = null;
    this.previousActiveElement = null;
    this.handleKeydown = this.handleKeydown.bind(this);
  }

  activate() {
    this.previousActiveElement = document.activeElement;

    const focusables = this.element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusables.length === 0) return;

    this.firstFocusable = focusables[0];
    this.lastFocusable = focusables[focusables.length - 1];

    this.element.addEventListener('keydown', this.handleKeydown);
    this.firstFocusable.focus();
  }

  deactivate() {
    this.element.removeEventListener('keydown', this.handleKeydown);
    if (this.previousActiveElement && this.previousActiveElement.focus) {
      this.previousActiveElement.focus();
    }
  }

  handleKeydown(e) {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === this.firstFocusable) {
        e.preventDefault();
        this.lastFocusable.focus();
      }
    } else {
      // Tab
      if (document.activeElement === this.lastFocusable) {
        e.preventDefault();
        this.firstFocusable.focus();
      }
    }
  }
}

// Update setupShortcuts() to use focus trap:
static setupShortcuts() {
  const modal = document.getElementById('shortcutModal');
  const btn = document.getElementById('shortcutBtn');
  const closeBtn = document.getElementById('closeShortcutBtn');
  if (!modal || !btn || !closeBtn) return;

  let focusTrap = null;

  const openModal = () => {
    modal.showModal();
    focusTrap = new FocusTrap(modal);
    focusTrap.activate();
  };

  const closeModal = () => {
    modal.close();
    if (focusTrap) {
      focusTrap.deactivate();
      focusTrap = null;
    }
  };

  btn.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });
  modal.addEventListener('cancel', () => {
    if (focusTrap) focusTrap.deactivate();
  });

  // Global keyboard shortcut
  document.addEventListener('keydown', (e) => {
    if (e.key === '?' && e.shiftKey && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      openModal();
    }
    if (e.key === 'Escape' && modal.open) {
      closeModal();
    }
  });
}
```

### 9.5 Stats Interactive Explanation

**Update** `index.html` to add keyboard accessibility and tooltips:

```html
<!-- Replace each stat div with: -->
<div class="stat interactive" tabindex="0"
     role="status" aria-label="Bytes Sent: 0 B"
     title="Total bytes uploaded in current transfer">
  <!-- ... existing content ... -->
</div>
```

### 9.6 Add CSS for focus visibility

**Add** to `css/styles.css`:

```css
/* Enhanced focus visibility for accessibility */
:focus-visible {
  outline: var(--focus-ring-width, 3px) solid var(--focus);
  outline-offset: var(--focus-ring-offset, 3px);
  box-shadow: var(--focus-glow-soft);
}

/* Focus within for containers */
.stat:focus-visible,
.file-drop-zone:focus-visible,
.log-entry:focus-visible {
  border-color: var(--focus);
  box-shadow: var(--focus-glow-emphasis);
}

/* Skip link styling (already exists, ensure it's visible) */
.skip-link:focus {
  position: fixed;
  top: 10px;
  left: 10px;
  padding: 10px 20px;
  background: var(--surface);
  border: 2px solid var(--focus);
  border-radius: var(--radius-md);
  z-index: 9999;
  clip: auto;
  width: auto;
  height: auto;
}
```

### Verification
- Use VoiceOver/NVDA to navigate
- Progress ring should announce percentage updates
- Speed chart should have summary for screen readers
- Tab through modals should trap focus
- All interactive elements should be keyboard accessible

---

## Task 10: Performance Optimizations

### 10.1 Debounce Window Resize for SpeedChart

**File:** `js/ui.js`
**Lines:** 269-271

**Current:**
```javascript
#attachResizeListener() {
  this.#resizeHandler = () => this.resizeCanvas();
  window.addEventListener('resize', this.#resizeHandler);
}
```

**Change to:**
```javascript
#attachResizeListener() {
  // Debounce resize to prevent excessive redraws
  this.#resizeHandler = domUtils.debounce(() => this.resizeCanvas(), 250);
  window.addEventListener('resize', this.#resizeHandler);
}
```

### 10.2 Optimize Log Filtering

**File:** `js/ui.js`
**Class:** `LogStore`

**Add** visible count tracking:

```javascript
class LogStore {
  constructor(container, maxLogs = 50) {
    this.container = container;
    this.maxLogs = maxLogs;
    this.logs = [];
    this.visibleCount = 0; // ADD: Track visible count
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

    // Respect active UI filters/search (if enabled)
    globalThis.applyLogFilters?.();

    this.#syncEmptyAndCount();
  }

  clear() {
    this.logs = [];
    this.visibleCount = 0; // Reset count
    if (this.container) this.container.innerHTML = '';
    globalThis.applyLogFilters?.();
    this.#syncEmptyAndCount();
  }

  #syncEmptyAndCount() {
    if (dom.logEntryCount) {
      dom.logEntryCount.textContent = String(this.logs.length);
    }
    if (dom.logsEmptyState) {
      dom.logsEmptyState.hidden = this.visibleCount > 0;
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

  // ... rest of class
}
```

**Update** `applyLogFilters` in `setupLogSearch`:

```javascript
const applyFilters = () => {
  const logEntries = dom.logContainer.querySelectorAll('[data-log-entry]');
  const query = currentQuery;
  const now = Date.now();

  let visibleCount = 0;
  for (const entry of logEntries) {
    const text = entry.textContent.toLowerCase();
    const entryLevel = getEntryLevel(entry);

    const ts = Number(entry.dataset.ts);
    const withinRecentWindow = !Number.isFinite(ts) || (now - ts) <= RECENT_WINDOW_MS;

    const visible = (!query || text.includes(query))
      && levelMatches(currentLevel, entryLevel)
      && (!recentOnly || withinRecentWindow);
    entry.style.display = visible ? '' : 'none';
    if (visible) visibleCount++;
  }

  // Update LogStore's visible count instead of querying DOM again
  if (globalThis.app?.logs) {
    globalThis.app.logs.setVisibleCount(visibleCount);
  }

  updateEmptyCopy({ totalLogs: logEntries.length, visibleLogs: visibleCount });
};
```

### 10.3 Pause Animations When Idle

**File:** `js/app.js`

**Add** to `#render` method:

```javascript
#render(state) {
  const transferActive = this.#isTransferActive(state.status);
  const transferFinished = this.#isTransferFinished(state.status);

  // Animation gating: pause heavy visuals when idle
  const isIdle = !transferActive;
  document.documentElement.classList.toggle('app-idle', isIdle);

  // Pause status panel animations when not transferring
  const statusPanel = document.getElementById('statusPanel');
  if (statusPanel) {
    statusPanel.classList.toggle('animate-paused', isIdle);
  }

  this.#renderPhaseText(state.status);
  this.#renderProgressPct(state.progress);
  this.#renderProgressRing(state.progress);
  this.#renderStats(state, transferActive, transferFinished);
  this.#renderControls(state, transferActive);
  this.#renderSpeedChart(state, transferActive);
}
```

**Add** CSS for paused animations in `css/styles.css`:

```css
/* Pause animations when app is idle */
.app-idle .wave-layer,
.app-idle .ring-decoration::before,
.app-idle .ring-decoration::after,
.animate-paused .wave-layer,
.animate-paused .ring-decoration::before,
.animate-paused .ring-decoration::after {
  animation-play-state: paused !important;
}

/* Reduce opacity of background effects when idle */
.app-idle .status-bg-animation {
  opacity: 0.3;
  transition: opacity 0.5s ease;
}
```

### 10.4 Extract Circuit Pattern to External File

**Create** `api_server/web_ui/img/circuit-pattern.svg`:

```svg
<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'>
  <g fill='none' stroke='#58a6ff' stroke-width='0.4'>
    <rect x='10' y='10' width='16' height='16' rx='2' opacity='0.12'/>
    <rect x='94' y='10' width='16' height='16' rx='2' opacity='0.12'/>
    <rect x='10' y='94' width='16' height='16' rx='2' opacity='0.12'/>
    <rect x='94' y='94' width='16' height='16' rx='2' opacity='0.12'/>
    <circle cx='18' cy='18' r='2' opacity='0.15'/>
    <circle cx='102' cy='18' r='2' opacity='0.15'/>
    <circle cx='18' cy='102' r='2' opacity='0.15'/>
    <circle cx='102' cy='102' r='2' opacity='0.15'/>
    <circle cx='60' cy='60' r='3' opacity='0.1'/>
    <path d='M26 18 L60 18 M60 18 L60 57 M60 63 L60 102 M26 102 L57 102 M63 102 L94 102 M102 26 L102 57 M102 63 L102 94 M18 26 L18 94 M94 18 L63 18' stroke-linecap='round' opacity='0.08'/>
    <path d='M26 10 L30 10 L30 14 M94 10 L90 10 L90 14 M26 110 L30 110 L30 106 M94 110 L90 110 L90 106 M10 26 L10 30 L14 30 M110 26 L110 30 L106 30 M10 94 L10 90 L14 90 M110 94 L110 90 L106 90' stroke-linecap='round' opacity='0.1'/>
  </g>
</svg>
```

**Update** `css/styles.css` line 182:

```css
/* Replace data URI with external file */
--circuit-pattern: url("../img/circuit-pattern.svg");
```

### Verification
- Resize window rapidly → SpeedChart should not flicker
- Add 50 logs then filter → Should be smooth, no visible lag
- When idle, wave animations should pause
- Network tab should show circuit-pattern.svg loaded (and cached)

---

## Task 11: Code Organization Refactoring

### 11.1 Extract Demo Mode to Separate Class ✅ Completed

Implementation:
- Added `js/demo-mode.js` with a `DemoMode` class (enabled detection via query param or `safeLocalStorage`, start/pause/resume/stop, simulated transfer timer, global export on `globalThis`).
- Updated `index.html` to load `js/demo-mode.js` before `js/app.js` so the class is available at init.
- Refactored `app.js` to rely on `this.demo` for demo state/labels and removed legacy inline demo logic and timers.

Outcome:
- Demo mode is fully modular, reusable, and no longer tangled in `app.js`.
- Phase labels and progress rendering use `DemoMode.active`; log demo button calls `demo.start()`.

Next for Task 11: proceed to 11.2 (comment cleanup / minor refactors) and remaining organization items.

**Create** `js/demo-mode.js`:

```javascript
/**
 * Demo Mode Manager
 * Simulates backup transfers for testing and demonstration purposes
 */
class DemoMode {
  #app;
  #enabled;
  #active;
  #timer;
  #totalBytes;

  constructor(app) {
    this.#app = app;
    this.#enabled = this.#detectEnabled();
    this.#active = false;
    this.#timer = null;
    this.#totalBytes = 250 * 1024 * 1024; // 250MB simulated transfer
  }

  get enabled() {
    return this.#enabled;
  }

  get active() {
    return this.#active;
  }

  #detectEnabled() {
    try {
      const params = new URLSearchParams(globalThis.location?.search || '');
      if (params.has('demo')) return true;
      return safeLocalStorage('cyberbackup-demo-mode') === '1';
    } catch {
      return false;
    }
  }

  start() {
    if (!this.#enabled) return;
    if (this.#active) {
      this.#app.toast.show('Demo already running', 'info');
      return;
    }

    this.#active = true;
    this.#app.logs.add('Demo mode: starting simulated transfer', { phase: 'DEMO', level: 'info' });
    this.#app.setConnectionStatus('Demo mode (simulated) - no network traffic', 'info');

    this.#app.state.update({
      connected: false,
      jobId: 'demo',
      status: 'uploading',
      progress: 0,
      speed: 0,
      bytesTransferred: 0,
      totalBytes: this.#totalBytes,
      startTime: Date.now(),
    });

    this.#startTimer();
  }

  pause() {
    if (!this.#active) return;
    this.#stopTimer();
    this.#app.state.update({ status: 'paused' });
    this.#app.logs.add('Demo transfer paused', { phase: 'DEMO', level: 'info' });
  }

  resume() {
    if (!this.#active) return;
    this.#app.state.update({ status: 'uploading' });
    this.#app.logs.add('Demo transfer resumed', { phase: 'DEMO', level: 'info' });
    this.#startTimer();
  }

  stop() {
    if (!this.#active) return;
    this.#stopTimer();
    this.#active = false;
    this.#app.state.update({
      status: 'idle',
      progress: 0,
      jobId: null,
      speed: 0,
      bytesTransferred: 0
    });
    this.#app.logs.add('Demo transfer stopped', { phase: 'DEMO', level: 'warn' });
    this.#app.toast.show('Demo stopped', 'info');
  }

  #startTimer() {
    if (this.#timer) return;

    this.#timer = setInterval(() => {
      if (!this.#active) {
        this.#stopTimer();
        return;
      }
      if (this.#app.state.snapshot.status !== 'uploading') {
        return;
      }

      const currentPct = Math.max(0, Math.min(100, Number(this.#app.state.snapshot.progress) || 0));
      const bump = 2 + Math.random() * 7;
      const nextPct = Math.min(100, currentPct + bump);
      const totalBytes = this.#app.state.snapshot.totalBytes || 1;

      const speed = 8 * 1024 * 1024 + Math.random() * 3 * 1024 * 1024;
      const bytesTransferred = Math.floor(totalBytes * (nextPct / 100));

      if (nextPct >= 100) {
        this.#app.state.update({
          status: 'completed',
          progress: 100,
          speed: 0,
          bytesTransferred: totalBytes,
        });
        this.#app.logs.add('Demo transfer complete', { phase: 'DEMO', level: 'success' });
        this.#app.toast.show('Demo complete (simulated)', 'success');
        this.#active = false;
        this.#stopTimer();
        return;
      }

      this.#app.state.update({
        status: 'uploading',
        progress: nextPct,
        speed,
        bytesTransferred,
      });
    }, 650);
  }

  #stopTimer() {
    if (this.#timer) {
      clearInterval(this.#timer);
      this.#timer = null;
    }
  }

  destroy() {
    this.#stopTimer();
    this.#active = false;
  }
}
```

**Update** `index.html` to include new script:

```html
<script src="js/core-utils.js" defer></script>
<script src="js/core.js" defer></script>
<script src="js/ui.js" defer></script>
<script src="js/demo-mode.js" defer></script> <!-- ADD -->
<script src="js/app.js" defer></script>
```

**Update** `app.js` to use DemoMode class:

```javascript
// In constructor
this.demo = new DemoMode(this);

// In init()
if (this.demo.enabled && dom.logDemoBtn) {
  dom.logDemoBtn.hidden = false;
  dom.logDemoBtn.title = 'Run a simulated transfer (demo mode)';
}

// In #bindEvents()
dom.logDemoBtn?.addEventListener('click', () => this.demo.start());

// In #handlePause()
async #handlePause() {
  try {
    if (this.demo.active) {
      this.demo.pause();
      return;
    }
    // ... rest of method
  }
}

// In #handleResume()
async #handleResume() {
  try {
    if (this.demo.active) {
      this.demo.resume();
      return;
    }
    // ... rest of method
  }
}

// In #handleStop()
async #handleStop() {
  try {
    if (this.demo.active) {
      this.demo.stop();
      return;
    }
    // ... rest of method
  }
}

// In #renderPhaseText - access this.demo.active instead of this.demoActive
```

### 11.2 Remove Duplicate Comments and Clean Up ✅ Completed (2025-12-17)

**File:** `js/app.js`

Implementation:
- Confirmed the old duplicate "Initialize Managers" comment and "FIXED" trailing comment are no longer present (already resolved during earlier refactors).
- Removed one stale "Fix:" comment and tightened up extra blank lines in the constructor initialization sequence.

### Verification
- App should load without errors
- Demo mode should work as before
- No behavior changes; this is strictly readability / maintainability cleanup

---

## Task 12: Visual Consistency Fixes

### 12.1 Consolidate Spacing Naming Convention

**File:** `css/styles.css`

**Decision:** Use `--space-*` as primary, keep `--gap-*` as aliases for backward compatibility.

**Update** root variables section:

```css
/* Spacing - Primary naming convention */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 12px;
--space-lg: 16px;
--space-xl: 20px;
--space-2xl: 24px;
--space-3xl: 32px;

/* Legacy aliases (for backward compatibility) */
--gap-1: var(--space-xs);
--gap-2: var(--space-sm);
--gap-3: var(--space-md);
--gap-4: var(--space-lg);
--gap-5: var(--space-2xl);
--gap-6: var(--space-3xl);
```

### 12.2 Consolidate Animation Duration Naming

**Update** root variables:

```css
/* Motion system - Primary naming convention */
--duration-instant: 80ms;
--duration-micro: 120ms;
--duration-swift: 180ms;
--duration-smooth: 280ms;
--duration-slow: 400ms;

/* Transition shortcuts (combines duration + easing) */
--transition-fast: var(--duration-swift) var(--ease-default);
--transition-base: var(--duration-smooth) var(--ease-default);
--transition-slow: var(--duration-slow) var(--ease-default);

/* REMOVE these redundant definitions:
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
*/
```

### 12.3 Fix Progress Ring Gradient Colors

**File:** `css/styles.css` (around line 349)

**Current:**
```css
<linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#00f2ff" />
  <stop offset="50%" stop-color="#7000ff" />
  <stop offset="100%" stop-color="#ff0055" />
</linearGradient>
```

**Update** to match brand colors:

```html
<!-- In index.html, update the progress gradient -->
<linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#58a6ff" />   <!-- --primary-400 -->
  <stop offset="50%" stop-color="#a78bfa" />  <!-- --secondary-400 -->
  <stop offset="100%" stop-color="#22d3ee" /> <!-- --accent-400 -->
</linearGradient>
```

### 12.4 Remove Redundant Shadow Aliases

**Update** root variables:

```css
/* Five-level elevation system - Primary */
--shadow-1: 0 1px 3px rgba(0, 0, 0, 0.2), 0 1px 2px rgba(0, 0, 0, 0.12);
--shadow-2: 0 3px 6px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.15);
--shadow-3: 0 6px 12px rgba(0, 0, 0, 0.4), 0 3px 6px rgba(0, 0, 0, 0.2);
--shadow-4: 0 12px 24px rgba(0, 0, 0, 0.5), 0 6px 12px rgba(0, 0, 0, 0.25);
--shadow-5: 0 24px 48px rgba(0, 0, 0, 0.6), 0 12px 24px rgba(0, 0, 0, 0.3);

/* Semantic aliases (kept for clarity, reference levels) */
--shadow: var(--shadow-3);          /* Default card shadow */
--shadow-lg: var(--shadow-4);       /* Elevated elements */
--shadow-xl: var(--shadow-5);       /* Modals, dropdowns */
--shadow-large: var(--shadow-4);    /* DEPRECATED: use --shadow-lg */
--card-shadow: var(--shadow-2);     /* Cards specifically */
```

### Verification
- Visual appearance should be unchanged
- CSS file should be more consistent
- No console errors about undefined variables

---

## Task 13: Missing Visual Feedback

### 13.1 Copy Confirmation Feedback

**File:** `js/ui.js`

**Add** copy feedback utility:

```javascript
/**
 * Copies text to clipboard with visual feedback
 * @param {string} text - Text to copy
 * @param {HTMLElement} button - Button element for feedback
 * @param {ToastManager} toast - Toast manager for notifications
 */
async function copyWithFeedback(text, button, toast) {
  try {
    await navigator.clipboard.writeText(text);

    // Visual feedback on button
    const originalText = button.textContent;
    const originalClass = button.className;

    button.textContent = 'Copied!';
    button.classList.add('copy-success');

    setTimeout(() => {
      button.textContent = originalText;
      button.className = originalClass;
    }, 2000);

    toast?.show('Copied to clipboard', 'success');
  } catch (err) {
    console.error('Copy failed:', err);
    toast?.show('Failed to copy', 'error');
  }
}
```

**Add** CSS for copy feedback:

```css
/* Copy success state */
.copy-success {
  background: var(--success) !important;
  color: white !important;
  border-color: var(--success) !important;
}
```

**Wire up** copy buttons in `ProfessionalGUIEnhancements`:

```javascript
// In init() or separate method
static setupCopyButtons() {
  // Copy logs button
  dom.logCopyBtn?.addEventListener('click', async () => {
    const logs = globalThis.app?.logs?.logs || [];
    const text = logs.slice(0, 50).map(log =>
      `[${formatters.time(log.timestamp)}] [${log.phase}] ${log.message}`
    ).join('\n');
    await copyWithFeedback(text, dom.logCopyBtn, globalThis.app?.toast);
  });

  // Copy diagnostics button
  dom.copyDiagnosticsBtn?.addEventListener('click', async () => {
    const state = globalThis.app?.state?.snapshot || {};
    const diagnostics = {
      timestamp: new Date().toISOString(),
      connected: state.connected,
      status: state.status,
      serverAddress: state.serverAddress,
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    const text = JSON.stringify(diagnostics, null, 2);
    await copyWithFeedback(text, dom.copyDiagnosticsBtn, globalThis.app?.toast);
  });
}
```

### 13.2 Stats Update Animation

**Add** CSS for value updates:

```css
/* Stats value update animation */
.stat .value {
  transition: color var(--duration-swift) ease, transform var(--duration-swift) ease;
}

.stat .value.updating {
  color: var(--accent);
  transform: scale(1.05);
}

/* Keyframe version for more dramatic effect */
@keyframes value-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); color: var(--accent); }
  100% { transform: scale(1); }
}

.stat .value.pulse {
  animation: value-pulse 300ms ease-out;
}
```

**Update** `#renderStats` in `app.js`:

```javascript
#renderStats(state, transferActive, transferFinished) {
  // Helper to update value with animation
  const updateValue = (element, newText) => {
    if (!element) return;
    if (element.textContent !== newText) {
      element.textContent = newText;
      element.classList.add('updating');
      setTimeout(() => element.classList.remove('updating'), 300);
    }
  };

  if (dom.stats?.bytes) {
    const showBytes = transferActive || transferFinished || Number(state.totalBytes) > 0;
    updateValue(dom.stats.bytes, showBytes ? formatters.formatBytes(state.bytesTransferred || 0) : '—');
  }
  // ... apply updateValue to other stats
}
```

### 13.3 Connection Quality Color Coding

**Update** connection monitor result handler in `app.js`:

```javascript
#onMonitorResult(res) {
  if (dom.qualityBadge) {
    const quality = res.quality || 'checking';
    dom.qualityBadge.textContent = `Quality: ${quality}`;

    // Remove all quality classes
    dom.qualityBadge.classList.remove(
      'quality-excellent', 'quality-good', 'quality-fair', 'quality-poor', 'quality-offline'
    );

    // Add appropriate class based on quality
    const qualityClass = {
      'excellent': 'quality-excellent',
      'good': 'quality-good',
      'fair': 'quality-fair',
      'poor': 'quality-poor',
      'offline': 'quality-offline',
      'checking': ''
    }[quality] || '';

    if (qualityClass) {
      dom.qualityBadge.classList.add(qualityClass);
    }
  }
  // ... rest of method
}
```

### 13.4 File Drop Zone Hover State

**Add** CSS for enhanced file drop zone states:

```css
/* File drop zone states */
.file-drop-zone {
  transition: all var(--transition-base);
}

.file-drop-zone:hover:not(.file-selected) {
  border-color: var(--accent);
  background: rgba(88, 166, 255, 0.05);
  transform: translateY(-2px);
  box-shadow: var(--shadow-2), 0 0 20px rgba(88, 166, 255, 0.1);
}

.file-drop-zone.drag-active {
  border-color: var(--accent);
  background: rgba(88, 166, 255, 0.1);
  transform: scale(1.02);
  box-shadow: var(--shadow-3), 0 0 30px rgba(88, 166, 255, 0.2);
}

.file-drop-zone.file-selected {
  border-color: var(--success);
  background: rgba(63, 185, 80, 0.05);
}

.file-drop-zone.file-selected:hover {
  border-color: var(--success);
  background: rgba(63, 185, 80, 0.1);
}
```

### 13.5 Backup Complete Success State

**Update** progress ring and stats on completion:

```javascript
// In #render or separate method
#renderCompletionState(state) {
  const statusPanel = document.getElementById('statusPanel');
  if (!statusPanel) return;

  // Add/remove completion class
  statusPanel.classList.toggle('backup-complete', state.status === 'completed');
  statusPanel.classList.toggle('backup-error', state.status === 'error');
}
```

**Add** CSS for completion states:

```css
/* Backup completion success state */
.status-panel.backup-complete {
  border-color: rgba(63, 185, 80, 0.4);
  box-shadow:
    0 4px 32px rgba(0, 0, 0, 0.4),
    0 0 60px rgba(63, 185, 80, 0.15);
}

.status-panel.backup-complete .progress-fill {
  stroke: var(--success) !important;
  filter: drop-shadow(0 0 10px var(--success));
}

.status-panel.backup-complete .pct {
  color: var(--success);
}

/* Backup error state */
.status-panel.backup-error {
  border-color: rgba(248, 81, 73, 0.4);
  box-shadow:
    0 4px 32px rgba(0, 0, 0, 0.4),
    0 0 60px rgba(248, 81, 73, 0.15);
}

.status-panel.backup-error .progress-fill {
  stroke: var(--danger) !important;
}

.status-panel.backup-error .pct {
  color: var(--danger);
}
```

### Verification
- Click "Copy last 50" → Button should say "Copied!" briefly
- Stats should pulse when values change during transfer
- Quality badge should change color based on connection quality
- Drop zone should have visible hover state
- Completed backup should show green success styling

---

## Task 14: Feature Completions

### 14.1 Wire Up Troubleshoot Panel Actions

**File:** `js/ui.js`

**Add** to `ProfessionalGUIEnhancements`:

```javascript
static setupTroubleshootPanel() {
  const chip = dom.troubleshootChip;
  const sheet = dom.troubleshootSheet;
  const closeBtn = dom.closeTroubleshoot;
  const forcePingBtn = dom.forcePingBtn;
  const filterRecentBtn = dom.filterRecentLogsBtn;
  const copyDiagBtn = dom.copyDiagnosticsBtn;

  if (!chip || !sheet) return;

  // Open/close sheet
  chip.addEventListener('click', () => {
    sheet.showModal();
  });

  closeBtn?.addEventListener('click', () => {
    sheet.close();
  });

  sheet.addEventListener('click', (e) => {
    if (e.target === sheet) sheet.close();
  });

  // Force ping
  forcePingBtn?.addEventListener('click', async () => {
    forcePingBtn.disabled = true;
    forcePingBtn.textContent = 'Pinging...';

    try {
      await globalThis.app?.monitor?.forcePing?.();
      forcePingBtn.textContent = 'Ping sent!';
      setTimeout(() => {
        forcePingBtn.textContent = 'Force ping';
        forcePingBtn.disabled = false;
      }, 2000);
    } catch (err) {
      forcePingBtn.textContent = 'Ping failed';
      setTimeout(() => {
        forcePingBtn.textContent = 'Force ping';
        forcePingBtn.disabled = false;
      }, 2000);
    }
  });

  // Filter recent logs - already wired in setupLogSearch
  // Copy diagnostics - already wired in setupCopyButtons
}
```

### 14.2 Wire Up Log Export Button

```javascript
static setupLogExport() {
  const exportBtn = dom.logExportBtn;
  if (!exportBtn) return;

  exportBtn.addEventListener('click', () => {
    const logs = globalThis.app?.logs?.logs || [];
    if (logs.length === 0) {
      globalThis.app?.toast?.show('No logs to export', 'info');
      return;
    }

    const content = logs.map(log =>
      `[${log.timestamp.toISOString()}] [${log.level.toUpperCase()}] [${log.phase}] ${log.message}`
    ).join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cyberbackup-logs-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    globalThis.app?.toast?.show('Logs exported', 'success');
  });
}
```

### 14.3 Complete Keyboard Shortcuts

**Update** `setupShortcuts`:

```javascript
static setupShortcuts() {
  // ... existing modal code ...

  // Global keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Ignore if in input field
    const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);

    // ? - Show shortcuts (already exists)
    if (e.key === '?' && e.shiftKey && !isInput) {
      e.preventDefault();
      modal.showModal();
      return;
    }

    // Escape - Close modal or stop transfer
    if (e.key === 'Escape') {
      if (modal.open) {
        closeModal();
      } else if (globalThis.app?.state?.snapshot?.status === 'uploading') {
        globalThis.app?.toast?.show('Press Escape again to stop transfer', 'warn');
      }
      return;
    }

    // Ctrl+L - Clear logs
    if (e.ctrlKey && e.key === 'l' && !isInput) {
      e.preventDefault();
      globalThis.app?.logs?.clear();
      globalThis.app?.toast?.show('Logs cleared', 'info');
      return;
    }

    // Ctrl+O - Open file picker
    if (e.ctrlKey && e.key === 'o' && !isInput) {
      e.preventDefault();
      dom.fileInput?.click();
      return;
    }

    // Enter - Connect or start backup
    if (e.key === 'Enter' && !isInput) {
      e.preventDefault();
      dom.primaryActionBtn?.click();
      return;
    }

    // Space - Pause/Resume (when transfer active)
    if (e.key === ' ' && !isInput) {
      const status = globalThis.app?.state?.snapshot?.status;
      if (status === 'uploading') {
        e.preventDefault();
        dom.pauseBtn?.click();
      } else if (status === 'paused') {
        e.preventDefault();
        dom.resumeBtn?.click();
      }
      return;
    }
  });
}
```

### Verification
- Troubleshoot chip should open panel
- Force ping should work
- Log export should download file
- All keyboard shortcuts should work

---

## Task 15: New Features

### 15.1 Auto Theme Option

**File:** `js/ui.js`

**Update** `ThemeManager`:

```javascript
class ThemeManager {
  constructor() {
    this.themeToggle = dom.themeToggle;
    this.prefersDark = globalThis.matchMedia('(prefers-color-scheme: dark)');

    // Support 'dark', 'light', 'auto'
    const saved = safeLocalStorage('theme');
    this.mode = saved || 'auto';
    this.currentTheme = this.#resolveTheme();

    this.#init();
  }

  #resolveTheme() {
    if (this.mode === 'auto') {
      return this.prefersDark.matches ? 'dark' : 'light';
    }
    return this.mode;
  }

  #init() {
    this.#apply(this.currentTheme);

    // For checkbox: checked = dark
    this.themeToggle?.addEventListener('change', () => {
      this.mode = this.themeToggle.checked ? 'dark' : 'light';
      this.currentTheme = this.#resolveTheme();
      this.#apply(this.currentTheme);
      safeLocalStorage('theme', this.mode);
    });

    // React to system preference changes when in auto mode
    this.prefersDark.addEventListener('change', (e) => {
      if (this.mode === 'auto') {
        this.currentTheme = e.matches ? 'dark' : 'light';
        this.#apply(this.currentTheme);
      }
    });
  }

  toggle() {
    // Cycle: dark -> light -> auto -> dark
    if (this.mode === 'dark') this.mode = 'light';
    else if (this.mode === 'light') this.mode = 'auto';
    else this.mode = 'dark';

    this.currentTheme = this.#resolveTheme();
    this.#apply(this.currentTheme);
    safeLocalStorage('theme', this.mode);
  }

  #apply(theme) {
    this.currentTheme = theme;
    document.documentElement.classList.remove('theme-dark', 'theme-light');
    document.documentElement.classList.add(`theme-${theme}`);

    if (this.themeToggle) {
      this.themeToggle.checked = theme === 'dark';
      this.themeToggle.classList.add('rotating');
      setTimeout(() => this.themeToggle?.classList.remove('rotating'), 650);
    }

    if (dom.themeLabel) {
      const labels = {
        'dark': 'Dark mode',
        'light': 'Light mode',
        'auto': `Auto (${theme})`
      };
      dom.themeLabel.textContent = labels[this.mode] || labels[theme];
    }
  }
}
```

### 15.2 Transfer History (Basic)

**Add** to `js/app.js`:

```javascript
/**
 * Transfer history manager
 * Stores last N completed transfers in localStorage
 */
class TransferHistory {
  #maxEntries = 10;
  #storageKey = 'cyberbackup-history';

  get entries() {
    try {
      const data = safeLocalStorage(this.#storageKey);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  add(transfer) {
    const entries = this.entries;
    entries.unshift({
      id: generateUUID(),
      filename: transfer.filename,
      size: transfer.size,
      status: transfer.status,
      timestamp: new Date().toISOString(),
      serverAddress: transfer.serverAddress
    });

    // Limit history size
    if (entries.length > this.#maxEntries) {
      entries.length = this.#maxEntries;
    }

    try {
      safeLocalStorage(this.#storageKey, JSON.stringify(entries));
    } catch (e) {
      console.warn('Failed to save transfer history:', e);
    }
  }

  clear() {
    safeLocalStorage(this.#storageKey, '[]');
  }
}
```

### Verification
- Theme should follow system preference in auto mode
- Transfer history should persist across page reloads

---

## Task 18: Documentation Improvements

### 18.1 Add JSDoc to App Class

**File:** `js/app.js`

**Add** documentation:

```javascript
/**
 * Main application controller for CyberBackup Client
 * Orchestrates all UI components, state management, and server communication
 *
 * @class App
 * @property {StateStore} state - Reactive state container
 * @property {ApiClient} api - REST API client
 * @property {SocketClient} socket - WebSocket client for real-time updates
 * @property {ConnectionMonitor} monitor - Connection health monitor
 * @property {ToastManager} toast - Toast notification manager
 * @property {ScreenReaderAnnouncer} announcer - Accessibility announcer
 * @property {LogStore} logs - Activity log manager
 * @property {ThemeManager} theme - Theme switcher
 * @property {FileManager} fileManager - File selection handler
 * @property {AdvancedSettings} advancedSettings - Advanced settings manager
 * @property {DemoMode} demo - Demo mode controller
 * @property {boolean} operationInProgress - Lock flag for async operations
 */
class App {
  /**
   * Creates a new App instance
   * Initializes all managers and sets up initial state
   */
  constructor() {
    // ...
  }

  /**
   * Initializes the application
   * Sets up event listeners, starts monitoring, connects to socket
   * @returns {Promise<void>}
   */
  async init() {
    // ...
  }

  /**
   * Shows an inline banner with customizable severity and actions
   * @param {Object} options - Banner configuration
   * @param {'error'|'warn'|'info'} [options.severity='error'] - Severity level
   * @param {string} [options.title='Notice'] - Banner title
   * @param {string} [options.body=''] - Banner body text
   * @param {string} [options.actionHref=''] - Action link URL
   * @param {string} [options.actionText='Open'] - Action link text
   */
  showInlineBanner({ severity = 'error', title = 'Notice', body = '', actionHref = '', actionText = 'Open' } = {}) {
    // ...
  }

  // ... add JSDoc to all public methods
}
```

### 18.2 Document State Shape

**Add** to `js/core-utils.js` or separate `types.js`:

```javascript
/**
 * @typedef {Object} AppState
 * @property {boolean} connected - Whether connected to backup server
 * @property {boolean} connecting - Whether connection is in progress
 * @property {boolean} disconnecting - Whether disconnection is in progress
 * @property {string|null} jobId - Current backup job ID
 * @property {'idle'|'uploading'|'paused'|'completed'|'error'} status - Current transfer status
 * @property {number} progress - Transfer progress percentage (0-100)
 * @property {number} speed - Current transfer speed in bytes/second
 * @property {number} bytesTransferred - Bytes transferred so far
 * @property {number} totalBytes - Total file size in bytes
 * @property {number|null} startTime - Transfer start timestamp (Date.now())
 * @property {string} serverAddress - Server address in "host:port" format
 * @property {string} username - Current username
 */

/**
 * Initial state for the application
 * @type {AppState}
 */
const INITIAL_STATE = {
  connected: false,
  connecting: false,
  disconnecting: false,
  jobId: null,
  status: 'idle',
  progress: 0,
  speed: 0,
  bytesTransferred: 0,
  totalBytes: 0,
  startTime: null,
  serverAddress: 'localhost:1256',
  username: 'User-' + Math.floor(Math.random() * 10000)
};
```

### 18.3 Document Constants

```javascript
/**
 * Application constants
 * @namespace CONSTANTS
 */
const CONSTANTS = {
  /** Maximum file size in bytes (1 GB) */
  MAX_FILE_SIZE: 1024 * 1024 * 1024,

  /** Allowed MIME types for upload */
  ALLOWED_MIME_TYPES: ['application/zip', 'application/x-tar'],

  /** Allowed file extensions */
  ALLOWED_EXTENSIONS: ['zip', 'tar', 'gz', 'tgz'],

  /** Connection health check interval (ms) */
  HEALTH_CHECK_INTERVAL: 15000,

  /** Active job polling interval (ms) */
  ACTIVE_POLL_INTERVAL: 5000,

  /** Progress ring circumference for SVG calculations */
  PROGRESS_CIRCUMFERENCE: 2 * Math.PI * 45,

  /** Maximum log entries to keep */
  MAX_LOG_ENTRIES: 50,

  /** Speed chart data points */
  SPEED_CHART_POINTS: 30
};
```

### Verification
- IDE should show JSDoc tooltips for documented functions
- State shape should be clear to developers
- Constants should be self-documenting

---

## Task 19: Global Error Handlers

### Implementation

**Add** to `js/app.js` in `init()` method:

```javascript
async init() {
  // Set up global error handlers FIRST
  this.#setupGlobalErrorHandlers();

  // ... rest of init
}

/**
 * Sets up global error handlers for uncaught errors and unhandled rejections
 * @private
 */
#setupGlobalErrorHandlers() {
  // Handle uncaught errors
  window.onerror = (message, source, lineno, colno, error) => {
    console.error('Global error:', { message, source, lineno, colno, error });

    // Log to activity log
    this.logs.add(`Uncaught error: ${message}`, {
      phase: 'ERROR',
      level: 'error'
    });

    // Show user-friendly toast
    this.toast.show('An unexpected error occurred. Check logs for details.', 'error');

    // Report to error tracking (if available)
    if (typeof Sentry !== 'undefined' && Sentry.captureException) {
      Sentry.captureException(error || new Error(message));
    }

    // Don't prevent default handling
    return false;
  };

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);

    const message = event.reason?.message || String(event.reason) || 'Unknown error';

    // Log to activity log
    this.logs.add(`Unhandled promise rejection: ${message}`, {
      phase: 'ERROR',
      level: 'error'
    });

    // Show user-friendly toast (less alarming)
    this.toast.show('A background operation failed. Check logs for details.', 'warn');

    // Report to error tracking
    if (typeof Sentry !== 'undefined' && Sentry.captureException) {
      Sentry.captureException(event.reason);
    }
  });

  // Log when error handlers are set up
  console.log('Global error handlers initialized');
}
```

### ErrorBoundary Enhancement

**Update** `ErrorBoundary` class (if not already in codebase, add it):

```javascript
/**
 * Error boundary utility for handling errors with recovery options
 */
class ErrorBoundary {
  /**
   * Handles an error with logging, user notification, and optional recovery
   * @param {Error} error - The error that occurred
   * @param {string} context - Description of where the error occurred
   * @param {Function} [recoveryFn] - Optional function to attempt recovery
   */
  static handle(error, context, recoveryFn) {
    console.error(`Error in ${context}:`, error);

    // Log to app logs if available
    if (globalThis.app?.logs) {
      globalThis.app.logs.add(`${context}: ${error.message || error}`, {
        phase: 'ERROR',
        level: 'error'
      });
    }

    // Show toast notification
    if (globalThis.app?.toast) {
      globalThis.app.toast.show(`${context} failed: ${error.message || 'Unknown error'}`, 'error');
    }

    // Attempt recovery if provided
    if (typeof recoveryFn === 'function') {
      try {
        recoveryFn();
      } catch (recoveryError) {
        console.error('Recovery also failed:', recoveryError);
      }
    }

    // Report to error tracking
    if (typeof Sentry !== 'undefined' && Sentry.captureException) {
      Sentry.withScope((scope) => {
        scope.setTag('context', context);
        Sentry.captureException(error);
      });
    }
  }

  /**
   * Wraps an async operation with error handling
   * @param {Promise} promise - The promise to wrap
   * @param {string} context - Description for error messages
   * @param {Function} [recoveryFn] - Optional recovery function
   * @returns {Promise} - The wrapped promise
   */
  static async withErrorHandling(promise, context, recoveryFn) {
    try {
      return await promise;
    } catch (error) {
      this.handle(error, context, recoveryFn);
      throw error;
    }
  }
}
```

### Verification
- Throw an error in console → Should see toast and log entry
- Create a rejected promise → Should see warning toast
- ErrorBoundary.handle should work consistently

---

## Task 20: LocalStorage Error Handling

### Implementation

**Add** to `js/core-utils.js`:

```javascript
/**
 * Safe localStorage wrapper that handles errors gracefully
 * Handles private browsing mode, storage quota exceeded, and disabled storage
 *
 * @param {string} key - Storage key
 * @param {string} [value] - Value to set (omit to get)
 * @returns {string|null} - Retrieved value or null on error
 *
 * @example
 * // Get value
 * const theme = safeLocalStorage('theme');
 *
 * @example
 * // Set value
 * safeLocalStorage('theme', 'dark');
 *
 * @example
 * // Remove value
 * safeLocalStorage('theme', null);
 */
function safeLocalStorage(key, value) {
  try {
    if (typeof localStorage === 'undefined') {
      console.warn('localStorage is not available');
      return null;
    }

    // Remove
    if (value === null) {
      localStorage.removeItem(key);
      return null;
    }

    // Get
    if (value === undefined) {
      return localStorage.getItem(key);
    }

    // Set
    localStorage.setItem(key, value);
    return value;
  } catch (error) {
    // Handle specific errors
    if (error.name === 'QuotaExceededError') {
      console.warn('localStorage quota exceeded, attempting cleanup');
      try {
        // Try to clear old data and retry
        localStorage.removeItem('cyberbackup-history');
        if (value !== undefined && value !== null) {
          localStorage.setItem(key, value);
          return value;
        }
      } catch (retryError) {
        console.error('localStorage still failing after cleanup:', retryError);
      }
    } else if (error.name === 'SecurityError') {
      console.warn('localStorage access denied (private browsing?)');
    } else {
      console.warn('localStorage error:', error);
    }

    return null;
  }
}

/**
 * Safe sessionStorage wrapper with same API as safeLocalStorage
 * @param {string} key - Storage key
 * @param {string} [value] - Value to set (omit to get)
 * @returns {string|null} - Retrieved value or null on error
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

/**
 * In-memory storage fallback when localStorage is unavailable
 */
const memoryStorage = new Map();

/**
 * Gets storage value with fallback to memory
 * @param {string} key - Storage key
 * @returns {string|null} - Retrieved value
 */
function getStorageWithFallback(key) {
  const localValue = safeLocalStorage(key);
  if (localValue !== null) return localValue;
  return memoryStorage.get(key) || null;
}

/**
 * Sets storage value with fallback to memory
 * @param {string} key - Storage key
 * @param {string} value - Value to set
 */
function setStorageWithFallback(key, value) {
  const result = safeLocalStorage(key, value);
  if (result === null) {
    // Fallback to memory storage
    memoryStorage.set(key, value);
  }
}
```

### Update All localStorage Usage

**Find and replace** all direct localStorage calls:

```javascript
// BEFORE
localStorage.getItem('theme')
localStorage.setItem('theme', 'dark')

// AFTER
safeLocalStorage('theme')
safeLocalStorage('theme', 'dark')
```

**Files to update:**
- `js/ui.js` - ThemeManager constructor (line 13)
- `js/ui.js` - ThemeManager #init (line 24)
- `js/app.js` - Demo mode detection (line 687)
- Any other localStorage usages

### Verification
- Open in private browsing mode → Should not crash
- Fill localStorage to capacity → Should degrade gracefully
- All storage operations should be wrapped

---

## Testing Checklist

### Manual Testing

- [ ] **File Validation**
  - [ ] Upload 2GB file → Rejected with error message
  - [ ] Upload .exe file → Rejected with error message
  - [ ] Upload valid .zip → Accepted

- [ ] **Connection**
  - [ ] Rapid-click CONNECT → Only one connection attempt
  - [ ] Click while connecting → Button disabled

- [ ] **Accessibility**
  - [ ] Tab through all interactive elements
  - [ ] Screen reader announces progress updates
  - [ ] Focus trap works in modals

- [ ] **Performance**
  - [ ] Resize window rapidly → No flickering
  - [ ] Add 50 logs → Filter is smooth
  - [ ] Animations pause when idle

- [ ] **Visual**
  - [ ] Copy button shows "Copied!" feedback
  - [ ] Stats pulse when values change
  - [ ] Quality badge is color-coded

- [ ] **Keyboard Shortcuts**
  - [ ] Ctrl+L clears logs
  - [ ] Ctrl+O opens file picker
  - [ ] Shift+? opens shortcuts modal

- [ ] **Error Handling**
  - [ ] Throw error in console → Toast appears
  - [ ] Private browsing → App still works

- [ ] **Demo Mode**
  - [ ] Add ?demo to URL → Demo button appears
  - [ ] Demo transfer completes successfully

### Browser Testing

- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+ (with UUID fallback)
- [ ] Edge 90+

---

## Implementation Order

1. **Phase 1: Critical Fixes** (Tasks 2, 3, 4, 7)
   - Duplicate DOM fix
   - Browser compatibility
   - File validation
   - Double-click prevention

2. **Phase 2: Error Handling** (Tasks 19, 20)
   - Global error handlers
   - LocalStorage safety

3. **Phase 3: Accessibility** (Task 9)
   - Progress ring ARIA
   - Canvas alternatives
   - Focus traps

4. **Phase 4: Performance** (Task 10)
   - Debounce resize
   - Optimize log filtering
   - Animation pausing

5. **Phase 5: Visual Polish** (Tasks 12, 13)
   - Consistency fixes
   - Feedback animations

6. **Phase 6: Features** (Tasks 14, 15)
   - Complete existing features
   - Add new capabilities

7. **Phase 7: Code Quality** (Tasks 11, 18)
   - Extract demo mode
   - Add documentation

---

**Document Version:** 1.0
**Created:** 2025-12-15
**For:** AI Coding Agents implementing CyberBackup Web UI improvements
