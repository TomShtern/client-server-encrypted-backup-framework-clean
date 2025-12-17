CyberBackup Web UI – Code Review (static analysis)

## Snapshot
- Scope: api_server/web_ui (index.html, css/styles.css, js/core-utils.js, js/core.js, js/ui.js, js/app.js, js/demo-mode.js)
- Size red flags: styles.css ≈4.8k lines, core-utils.js ≈1.3k, ui.js ≈1.4k, app.js ≈1k. Monolithic modules make ownership and change isolation hard.

## Strengths
- Clear separation of “engine vs UI” intent: core.js handles API/socket, ui.js handles theming/logs/file manager, app.js orchestrates.
- Accessibility attention: aria labels, live regions, progress native element, keyboard shortcut modal, focus-visible styling.
- Defensive utilities: storage fallbacks, global error handlers, announcer, debounced/throttled helpers.
- Transfer history and theme persistence exist (basic localStorage support with fallback).

## Issues and Opportunities

### Architecture & State Management
- Heavy reliance on global singletons (dom, globalThis.app, globalThis.applyLogFilters). Increases coupling and test friction.
- State is spread: StateStore in core-utils, plus many mutable fields on App (operationInProgress, _activeTransferMeta, _valuePulseTimers). No single source of truth for UI/connection states.
- Event wiring lives across modules (app.js, ui.js, ProfessionalGUIEnhancements) with no central registry; risk of duplicate listeners when re-initing.

### DOM Cache / Initialization
- initializeDom() contains duplicate/legacy elements (connStatus, connQuality) that are no longer rendered. Needs pruning to reduce null checks.
- clearFileBtn is assigned twice in dom cache (one in “optional elements” and again in “Missing Elements” section) indicating drift.
- Missing null-guards on required elements could still throw during SSR/tests; optional vs required not enforced consistently.

### Over-Engineering vs Missing Integrations
- Advanced settings tabs (Network/Schedule/Compression/Encryption) are mostly UI-only; values are never sent in ApiClient.startBackup options (chunk size, compression, schedule, encryption choice). Users can change them but backend ignores them. UI defaults to expanded (per user screenshots), adding noise for non-functional controls.
- Proxy/Polycene toggles, schedule types, retry limit, compression choices: no validation, no persistence, no server contract. They bloat UI without function.
- Encryption select allows AES128/ChaCha but backend/server protocol is fixed to AES-256-CBC; options are misleading and may generate invalid expectations.
- Connection details drawer exists but is not populated when offline; minimal usage of monitor results.
 - Troubleshoot sheet is wired (forcePing, copy diagnostics) but depends on app.monitor/lastMonitorResult; when offline those handlers still render and silently no-op—should be guarded or hidden until monitor is available.
 - Demo mode can be toggled via query/localStorage and the “Demo” button; it forcibly sets status to uploading even when connected state is unknown, and can run alongside real UI states. Needs a clear badge and a guard to avoid mixing simulated and real sessions.

### Keyboard shortcuts & accessibility
- Global keydown handler is always active and triggers primary action on Enter and Escape double-tap stop logic even when focus is on non-form interactive elements (e.g., tabs). Scope shortcuts to top-level context or disable while dialogs/menus are open.

### Logging & Telemetry
- LogStore capped at 50 entries and relies on global applyLogFilters to manage visibility; filters/search logic is scattered and not encapsulated.
- No persistence for logs; exporting/copy limited, and autoscroll toggle state not persisted.
- Repeated info-level logs on init/offline can spam limited buffer.

### Transfer History
- Local-only storage (max 10) with no filtering, dedupe, or export; no link to server job IDs. Status strings are free-form. Empty-state illustration is oversized in UI (per user screenshots), dominating the viewport instead of a compact message.
- No validation for malformed stored entries (only try/catch JSON.parse). Clear operation does not re-render list immediately unless renderTransferHistory called.

### Error Handling
- ErrorBoundary mirrors errors to logs, toast, and status strip without dedupe, so a single failure may surface 3 times.
- Global handlers added in App.init but not removed; potential duplicate registration if init called twice (e.g., hot reload).

### Performance / Structure
- Large CSS token set with many legacy aliases, multiple gradient/glow systems, and unused variables increases load and maintenance overhead.
- Repeated comments/headers in core-utils.js (Utility functions block duplicated) indicate unrefactored merges.
- SpeedChart debounce exists but canvas creation still runs even when placeholder hidden; could lazy-load chart only when toggled on.
- Inline SVG/complex gradients on progress ring plus heavy shadows might impact low-end devices; no prefers-reduced-motion handling beyond animation pause on tab hide.

### Consistency / Validation
- File validation depends on FILE_VALIDATION in core-utils.js; ensure drop zone text matches accepted types (currently zip/tar only) and size (1 GB). UI copy may drift from validator config.
- Advanced inputs (chunk size, retry limit) accept any string; validate and clamp before use.
- Username/server validation exists but visual icons/hints are always mounted; needs cleanup to avoid duplicated state updates.

### CSS Bloat & Organization
- styles.css mixes design tokens, layout, components, animations, and legacy aliases in one file. No layering (base/utilities/components/pages). Hard to find and remove unused rules.
- Large empty states (transfer history, logs) rely on oversized SVG placeholders; could be simplified via reusable utility classes.
- Theme tokens for light/dark are intertwined; consider separate theme overrides to reduce duplication.

## Quick Wins
- Remove dead DOM entries and duplicate assignments (e.g., clearFileBtn, connQuality/connStatus).
- Centralize filter/search logic inside LogStore; drop global applyLogFilters.
- Wire advanced settings to ApiClient.startBackup or hide them until supported; remove misleading encryption/Polycene/proxy toggles.
- Add validation/clamping for chunk size/retry inputs; propagate to API payload (options map) or remove fields.
- Split styles.css into tokens + base + components to shrink cognitive load; prune unused CSS variables and deprecated aliases.
- Gate heavy visuals (progress ring glows, speed chart) behind prefers-reduced-motion/performance flags.

## Bigger Refactors (suggested sequence)
1) Encapsulate UI state: Move operational flags (connected, jobId, buttons enabled, history list) into StateStore; render via a single subscriber to reduce scattered mutations.
2) Decouple DOM cache from globals: pass required elements into constructors (ThemeManager, FileManager, LogStore) instead of importing dom everywhere.
3) Make advanced settings functional or hide: define a contract between UI → ApiClient → backend; otherwise remove tabs. Document supported options.
4) Logging pipeline: move filters/search/export into LogStore; add capacity controls and dedupe by timestamp/message; persist optional.
5) Transfer history: unify with job IDs, allow filter/export, and add graceful rendering with pagination to avoid oversized placeholders.
6) CSS re-organization: extract tokens to tokens.css, base resets to base.css, components to components.css; remove redundant shadows/glows and legacy aliases.
