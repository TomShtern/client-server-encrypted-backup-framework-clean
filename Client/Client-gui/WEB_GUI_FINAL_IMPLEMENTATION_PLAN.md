# CyberBackup Web GUI – Final Implementation Plan (Derived from `wireframe_v4.html`)

This document maps every structural element and behavior in the final wireframe template (`wireframe_v4.html`) to concrete JavaScript classes, handler functions, state flows, and integration sequences. It is the authoritative blueprint for implementing the production web GUI without introducing frameworks.

---
## 1. Architectural Overview

```
App (orchestrator)
├── ApiClient          (HTTP → Flask API bridge)
├── ConnectionMonitor  (ping latency, quality scoring)
├── FileManager        (selection, drag-drop, metadata, recent files)
├── TransferManager    (start/pause/resume/stop + progress calc/ETA)
├── AdvancedSettings   (chunk size, retry limit persistence & validation)
├── StatsAggregator    (bytes, speed, elapsed, file size; smoothing)
├── LogManager         (in-memory buffer + filtering + export)
├── ToastManager       (stack render + auto-dismiss + SR announcements)
├── ThemeManager       (light/dark toggle via <html> class)
├── ModalManager       (confirm stop dialog flow)
└── AccessibilityAnnouncer (screen reader polite/assertive regions)
```

All modules follow a passive data pattern + callback wiring; `App` coordinates cross-module updates.

---
## 2. DOM Element ID Mapping

| Purpose                     | ID                    | Module Owner                                           |
|-----------------------------|-----------------------|--------------------------------------------------------|
| Connection state badge      | `connStatus`          | ConnectionMonitor                                      |
| Latency display             | `connHealth`          | ConnectionMonitor                                      |
| Quality chip                | `connQuality`         | ConnectionMonitor                                      |
| Theme button                | `themeToggle`         | ThemeManager                                           |
| Server input                | `serverInput`         | App (validation delegate)                              |
| Server hint                 | `serverHint`          | App (validation delegate)                              |
| Username input              | `usernameInput`       | App (validation delegate)                              |
| Username hint               | `usernameHint`        | App (validation delegate)                              |
| File drop zone wrapper      | `fileDropZone`        | FileManager                                            |
| File choose button          | `fileSelectBtn`       | FileManager                                            |
| Hidden file input           | `fileInput`           | FileManager                                            |
| Recent files button         | `recentFilesBtn`      | FileManager                                            |
| Clear file button           | `clearFileBtn`        | FileManager                                            |
| File name label             | `fileName`            | FileManager                                            |
| File meta label             | `fileInfo`            | FileManager                                            |
| Advanced wrapper            | `advancedPanel`       | AdvancedSettings                                       |
| Chunk size input            | `advChunkSize`        | AdvancedSettings                                       |
| Retry limit input           | `advRetryLimit`       | AdvancedSettings                                       |
| Reset advanced button       | `advResetBtn`         | AdvancedSettings                                       |
| Phase text                  | `phaseText`           | TransferManager                                        |
| Progress ring svg           | `progressRing`        | TransferManager                                        |
| Progress arc                | `progressArc`         | TransferManager                                        |
| Percentage                  | `progressPct`         | TransferManager                                        |
| ETA text                    | `etaText`             | TransferManager                                        |
| Primary action              | `primaryActionBtn`    | App (delegates to TransferManager & ConnectionMonitor) |
| Pause                       | `pauseBtn`            | TransferManager                                        |
| Resume                      | `resumeBtn`           | TransferManager                                        |
| Stop                        | `stopBtn`             | TransferManager + ModalManager                         |
| Stat bytes                  | `statBytes`           | StatsAggregator                                        |
| Stat speed                  | `statSpeed`           | StatsAggregator                                        |
| Stat file size              | `statSize`            | StatsAggregator                                        |
| Stat elapsed                | `statElapsed`         | StatsAggregator                                        |
| Logs section <pre>          | `logContainer`        | LogManager                                             |
| Filter: all/info/warn/error | `filterAll` etc.      | LogManager                                             |
| Autoscroll toggle           | `logAutoscrollToggle` | LogManager                                             |
| Export button               | `logExportBtn`        | LogManager                                             |
| Toast stack container       | `toastStack`          | ToastManager                                           |
| Confirm modal root          | `modalConfirm`        | ModalManager                                           |
| Modal OK                    | `modalOkBtn`          | ModalManager                                           |
| Modal Cancel                | `modalCancelBtn`      | ModalManager                                           |
| Screen reader live region   | `srLive`              | AccessibilityAnnouncer                                 |

---
## 3. Core State Model

```ts
interface AppState {
  serverEndpoint: string;        // host:port
  username: string;              // non-empty
  connection: {
    status: 'disconnected' | 'connecting' | 'connected';
    latencyMs: number | null;
    quality: 'offline' | 'poor' | 'fair' | 'good' | 'excellent';
    lastPingAt: number | null;
  };
  file: {
    handle: File | null;
    size: number;                // bytes
    type: string;                // MIME or extension
    name: string;                // original name
    lastModified: number | null;
  };
  advanced: {
    chunkSizeMB: number;         // validated integer (>=1)
    retryLimit: number;          // validated integer (>=0)
  };
  transfer: {
    phase: 'idle' | 'connecting' | 'handshake' | 'uploading' | 'verifying' | 'completed' | 'failed' | 'paused' | 'stopped';
    bytesSent: number;
    totalBytes: number;          // file size
    speedBps: number;            // instantaneous
    smoothedSpeedBps: number;    // EMA smoothing
    startedAt: number | null;    // epoch ms
    elapsedMs: number;           // derived
    etaMs: number | null;        // derived
    progressPct: number;         // 0..100 computed
    pauseRequested: boolean;
    stopRequested: boolean;
  };
  logs: LogEntry[];              // capped buffer
  ui: {
    autoscroll: boolean;
    theme: 'dark' | 'light';
    modal: { type: 'confirm-stop' | null; data?: any };
  };
}
```

---
## 4. Module Responsibilities & Public API

### ApiClient
- `ping(server: string): Promise<number>` – returns latency ms or throws
- `startTransfer(payload: StartPayload): Promise<StartResponse>`
- `streamProgress(token: string, onChunk: (delta) => void)` – optionally SSE/WebSocket
- `pause(token: string)` / `resume(token: string)` / `stop(token: string)`
- `fetchLogs(range?): Promise<LogEntry[]>` (optional initial hydration)

### ConnectionMonitor
- Interval ping (~3–5s)
- Quality scoring thresholds:
  - offline: null
  - poor: > 800ms
  - fair: 400–800ms
  - good: 150–399ms
  - excellent: < 150ms
- Emits: `onLatencyUpdate(latencyMs, quality)`

### FileManager
- Drag & drop event binding: adds `drag-over` class
- Validation: size > 0, supported type (optional)
- Maintains recent files (LocalStorage: `cb_recent_files`)
- Methods:
  - `setFile(file: File)`
  - `clearFile()`
  - `getMetadata(): { name, size, type }`

### AdvancedSettings
- Load defaults + LocalStorage keys: `cb_chunk_size`, `cb_retry_limit`
- Validation numeric + clamp
- Expose current validated config to TransferManager

### TransferManager
- Lifecycle orchestrator
- Methods:
  - `begin(file: File, opts: {chunkSizeMB, retryLimit})`
  - `pause()` / `resume()` / `stop()`
  - Internal progress aggregator updates state + StatsAggregator
- Progress arc calculation: `strokeDashoffset = circumference * (1 - pct/100)`

### StatsAggregator
- Speed smoothing: EMA `smoothed = alpha*instant + (1-alpha)*prev` (alpha ≈ 0.25)
- Elapsed, ETA: `eta = (total - sent) / smoothedSpeedBps`
- Methods: `update(bytesDelta)`; `reset()`

### LogManager
- In-memory circular buffer (max e.g. 1500 entries)
- Filter application by level
- Export: builds text blob + triggers download (`logs_<timestamp>.txt`)
- Autoscroll: if enabled and at bottom → scroll after append
- Methods: `append(entry)`, `setFilter(level)`, `export()`

### ToastManager
- `push(type: 'success'|'error'|'info', message: string, { timeoutMs = 5000 })`
- Auto-dismiss timers, manual dismiss on click
- Announces via AccessibilityAnnouncer

### ThemeManager
- `toggle()` – switches `html.classList`
- Persists choice: LocalStorage key `cb_theme`

### ModalManager
- `confirmStop(onConfirm: fn)` – reveals modal
- `close()` – hides and clears state

### AccessibilityAnnouncer
- `announcePolite(msg)` / `announceAssertive(msg)` (assertive uses toast region implicitly)

---
## 5. Event Binding Matrix

| Event       | Source                | Handler                                  | Description                                        |
|-------------|-----------------------|------------------------------------------|----------------------------------------------------|
| `click`     | `themeToggle`         | `themeManager.toggle()`                  | Switch theme                                       |
| `input`     | `serverInput`         | `validateServer()`                       | Regex host:port; show hint                         |
| `input`     | `usernameInput`       | `validateUsername()`                     | Non-empty; show hint                               |
| `change`    | `fileInput`           | `fileManager.setFile(e.target.files[0])` | Select via dialog                                  |
| `click`     | `fileSelectBtn`       | `fileInput.click()`                      | Open dialog                                        |
| `dragover`  | `fileDropZone`        | `onDragOver(e)`                          | Prevent default + style                            |
| `dragleave` | `fileDropZone`        | `onDragLeave(e)`                         | Remove style                                       |
| `drop`      | `fileDropZone`        | `onDrop(e)`                              | Validate & set file                                |
| `click`     | `recentFilesBtn`      | `showRecentFiles()`                      | Display recent selection UI (optional)             |
| `click`     | `clearFileBtn`        | `fileManager.clearFile()`                | Clear current file                                 |
| `click`     | `advResetBtn`         | `advancedSettings.reset()`               | Reset values                                       |
| `click`     | `primaryActionBtn`    | `onPrimaryAction()`                      | Connect or start transfer                          |
| `click`     | `pauseBtn`            | `transferManager.pause()`                | Pause transfer                                     |
| `click`     | `resumeBtn`           | `transferManager.resume()`               | Resume transfer                                    |
| `click`     | `stopBtn`             | `modalManager.confirmStop()`             | Open confirm dialog                                |
| `click`     | `modalOkBtn`          | `transferManager.stop()`                 | Confirm stop                                       |
| `click`     | `modalCancelBtn`      | `modalManager.close()`                   | Cancel stop                                        |
| `click`     | `filter*` buttons     | `logManager.setFilter(level)`            | Adjust log view                                    |
| `change`    | `logAutoscrollToggle` | `logManager.setAutoscroll(bool)`         | Toggle autoscroll                                  |
| `click`     | `logExportBtn`        | `logManager.export()`                    | Download log file                                  |
| `keydown`   | `document`            | `globalShortcutHandler(e)`               | Theme toggle (Ctrl+T), focus server (Ctrl+K), etc. |

---
## 6. Validation Rules

| Field       | Rule                                               | Feedback Trigger            |
|-------------|----------------------------------------------------|-----------------------------|
| Server      | Regex: `^([\w.-]+):(\d{2,5})$` and port in 1–65535 | On blur or start attempt  |
| Username    | Non-empty, length ≤ 64                             | On input (debounced 200ms)|
| Chunk Size  | Integer >= 1 and <= 256                             | On blur                    |
| Retry Limit | Integer >= 0 and <= 20                              | On blur                    |

Errors: set `aria-invalid="true"`, remove hint `hidden`, push toast for severe cases.

---
## 7. Transfer Flow Sequence

1. Validate server + username + file + advanced settings
2. ConnectionMonitor ensures reachable (ping < 2000ms) else error toast & abort
3. Phase: `connecting` → ApiClient start handshake → `handshake`
4. Prepare `transfer.info` generation on server bridge endpoint (Flask side; not in UI) via API call
5. Enter `uploading`: stream progress events (SSE/WebSocket or poll every 500ms fallback)
6. StatsAggregator updates speed/ETA; TransferManager computes `progressPct`
7. On completion: switch `phase` to `verifying` → request server hash check (ApiClient) → finalize with `completed` or `failed`
8. Toast success or failure; log final summary line; enable Start again (file persists for re-upload if needed)

Pause/Resume:
- Pause sets phase `paused`, retains bytesSent. Resume returns to `uploading`.

Stop:
- Confirm modal. If OK: send stop, set phase `stopped`, finalize.

---
## 8. Logging Strategy

- Levels: `info`, `warn`, `error`.
- Structure:
  ```ts
  interface LogEntry { ts: number; level: 'info'|'warn'|'error'; msg: string; meta?: any }
  ```
- Rendering: minimal preformatted lines: `[HH:MM:SS] [LEVEL] message`
- Filtering: DOM re-render with selected level predicate
- Export: Join filtered buffer currently displayed
- Autoscroll: `if (autoscroll && nearBottomBeforeAppend) scrollToBottom()`

---
## 9. Toast Patterns

- Dismiss: click or auto-timeout
- Severe errors (e.g., failed transfer) use `error` toast + assertive SR announcement
- Success transfers use `success` with completed metrics summary (speed avg, duration)

---
## 10. Performance Considerations

| Concern                  | Mitigation                                                                      |
|--------------------------|---------------------------------------------------------------------------------|
| Excess reflows           | Batch DOM updates per tick (requestAnimationFrame) for progress elements        |
| Large log buffer         | Circular buffer + virtual prune (slice to last N)                               |
| Speed calculation jitter | EMA smoothing; update UI every 500ms instead of every delta event               |
| Drag & drop flicker      | Use single class toggle + `pointer-events: none` children during drag if needed |

---
## 11. Accessibility Plan

- Live regions: `toastStack` (assertive), `srLive` (polite)
- Modal: trap focus (first/last buttons) and restore previous focus on close
- Keyboard Shortcuts (recommended):
  - Ctrl+K: focus server input
  - Ctrl+U: focus username
  - Ctrl+F: open file dialog
  - Ctrl+T: toggle theme
  - Space/Enter when main button focused: trigger primary action
  - Escape: close modal / dismiss top toast

---
## 12. LocalStorage Keys

| Key               | Purpose                                    |
|-------------------|--------------------------------------------|
| `cb_theme`        | Persist theme selection                    |
| `cb_chunk_size`   | Advanced chunk size                        |
| `cb_retry_limit`  | Advanced retry limit                       |
| `cb_recent_files` | Array of recent file names (metadata only) |

---
## 13. Error Handling Conventions

- Soft validation error: inline hint only
- Hard pre-flight error: toast + focus field + inline hint
- Transfer failure: `error` toast + log entry + phase set to `failed`
- API exception: unify shape `{ success: false, error: string }` → toast

---
## 14. Implementation Order

1. Scaffold JS modules & `App.init()` binding
2. ThemeManager + persisted toggle
3. Validation functions for server/username/advanced
4. FileManager (drag/drop + recent + metadata render)
5. AdvancedSettings (load/save/reset)
6. ConnectionMonitor (ping loop + quality updates)
7. TransferManager + StatsAggregator (stub with mock progress for early UI testing)
8. LogManager (append + filter + export)
9. ToastManager & AccessibilityAnnouncer integration
10. ModalManager (confirm stop workflow)
11. Replace mock progress with real ApiClient streaming
12. Keyboard shortcuts & final a11y polish
13. Integration test (mock API responses → full chain)

---
## 15. Mocking Strategy (Pre-API Readiness)

- Simulate progress: increment bytesSent every 120ms
- Latency simulation: random 85–300ms for quality transitions
- Fake logs: periodic info/warn lines
- Swap to real ApiClient when backend stable

---
## 16. Security Hardening (UI Layer)

- Sanitize log messages before injection (textContent only)
- Reject suspicious serverInput containing spaces or protocol schema
- Limit username length + allow `[A-Za-z0-9_.-]` only
- No inline event handlers; all JS bound programmatically

---
## 17. Future Enhancements (Deferred)

- Progress segmentation (visual chunk markers)
- Speed graph (canvas sparkline)
- Multi-file queue system (batch mode)
- Offline cache of last successful transfer summary

---
## 18. Minimal Boot Code Sketch

```js
class App {
  constructor() {
    this.state = createInitialState();
    this.api = new ApiClient();
    this.theme = new ThemeManager(this.state);
    this.files = new FileManager(this.state);
    this.adv = new AdvancedSettings(this.state);
    this.conn = new ConnectionMonitor(this.state, this.api);
    this.transfer = new TransferManager(this.state, this.api);
    this.stats = new StatsAggregator(this.state);
    this.logs = new LogManager(this.state);
    this.toasts = new ToastManager(this.state);
    this.modal = new ModalManager(this.state);
    this.ax = new AccessibilityAnnouncer();
  }
  init() {
    bindDomEvents(this);
    this.theme.loadPersisted();
    this.adv.loadPersisted();
    this.conn.start();
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
  window.__CB_APP__ = app; // debugging access
});
```

---
## 19. Acceptance Criteria Checklist

- All IDs present and bound
- Start → progress ring animates smoothly, stats update, ETA computed
- Pause/Resume toggles phase and disables/enables correct buttons
- Stop prompts confirm modal; cancellation preserves state; confirm stops cleanly
- Logs filter instantly without rebuild flicker
- Toasts appear, stack correctly, auto-dismiss, are keyboard dismissible (Esc)
- Theme toggle persists across reload
- Validation prevents illegal start
- No uncaught exceptions during nominal flow

---
## 20. Migration Notes (High-Level)

1. Introduce new HTML alongside existing legacy page (`/beta`) for parallel testing
2. Implement mock progress to validate UI interactions early
3. Wire real API endpoints gradually: ping → start transfer → stream progress → pause/resume/stop
4. Add logging export & final verification step
5. Flip main route after QA approval; keep legacy accessible under `/legacy` for rollback window (1–2 weeks)

---
## 21. Final Notes

This plan preserves current functional requirements while modernizing structure, accessibility, and maintainability. It avoids framework lock-in, enabling straightforward extension while keeping surface area explicit.

Use this document during implementation and tick off sections as modules become stable. Hidden complexity (encryption, server integration) remains backend-bound; UI focuses on clarity and resilience.

---
**End of Implementation Plan**
