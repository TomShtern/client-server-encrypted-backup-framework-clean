# UI Enhancement Execution Plan

Comprehensive, actionable plan to implement the current and expanded UI/UX improvements for the client web UI.

## Goals
- Elevate clarity of connection/health status (API + Backup) and surface diagnostics quickly.
- Make upload entry points unmistakable and reassuring (security cues, limits, guided drag/drop).
- Improve readability, filtering, and density in logs and activity views.
- Strengthen empty/loading states, error recovery, and accessibility.
- Ensure responsiveness, performance, and polish across desktop/mobile.

## Scope
- Web UI at `api_server/web_ui`: HTML, CSS, JS (`index.html`, `css/styles.css`, `js/app.js`, `js/ui.js`, `js/core.js`, `js/core-utils.js`).
- No backend protocol changes; reads existing APIs and sockets. New UI affordances may call existing endpoints (e.g., health, status, start_backup, verify).

## Assumptions & guardrails
- Keep binary protocol untouched; only front-end/UI logic changes.
- Honor existing response contract `{success, data, error}` and async/sync patterns.
- Avoid blocking UI; wrap sync calls via existing async helpers if needed.
- Maintain dark/light themes via CSS variables; do not hardcode colors.
- File limits and chunk/retry bounds must respect existing AdvancedSettings constraints.

## Workstreams & tasks

### 1) Status hero & diagnostics
- Add latency badge, “Last checked” timestamp, and explicit API/Backup labels with icons.
- Add compact “Troubleshoot” chip → opens a sheet with: force ping (reuse `ConnectionMonitor.forcePing()`), quick log filter (last 5 minutes), copy diagnostics (health payload + latency).
- Add inline quality indicator (good/fair/poor/offline) derived from `ConnectionMonitor` quality.

### 2) Primary CTA & dropzone
- Enlarge primary upload button with icon + sublabel (“Encrypted upload · AES-256 · CRC-verified”).
- Add helper line under CTA: “Drag & drop or pick a file · Max size / Supported types”.
- Drag-hover overlay: soft glow + subtle grid; “Release to upload” label.
- Provide small inline validation for unsupported types/oversize before submit; keep toast for errors.

### 3) Empty & loading states
- Logs: skeleton rows (timestamp + level badge placeholders) and empty-state message with CTA to view docs.
- Transfers/file cards: empty-state illustration/text; skeleton cards during fetch.
- Speed chart: placeholder “No data yet—start a backup to see throughput.”

### 4) Logs usability
- Add segmented filter (All / Info / Warn / Error) sticky at top of log panel.
- “Copy last 50 lines” action; respect current filter.
- Keep timestamps muted; levels own the color. Slightly tighter row density on mobile.

### 5) File cards & timeline
- Embed micro-timeline (queued → uploading → verifying → stored) with tooltips on hover.
- Inline “Verify CRC” action on completed cards (calls existing verify endpoint if available; otherwise no-op with toast).
- Show last update time on card footer; keep statuses color-consistent with badges.

### 6) Advanced settings UX
- Inline hints below inputs: “1–256 MB” and “0–20 retries”; live validation on blur/focus.
- Add “Restore defaults” text link beside reset button plus tooltip explaining effects.
- Persist values in localStorage (already present); ensure ARIA invalid states are toggled clearly.

### 7) Responsive & layout refinements
- On narrow widths: sidebar collapses to bottom sheet; status chips become horizontal scrollable pill bar.
- Masonry: two-column on medium, single-column on small; maintain gutter variables.
- Ensure sticky elements (log filters, status band) respect safe-area insets on mobile.

### 8) Feedback & toasts
- Severity-aware icons/backgrounds; error toasts persist until dismissed, success auto-dismiss.
- “View details” link in toast scrolls to logs with level filter applied.
- Subtle slide/fade animation for success; keep motion duration short for accessibility.

### 9) Accessibility & keyboard
- Visible focus rings for chips/segmented controls/log filters.
- “Skip to status” anchor and landmark roles for main sections.
- Ensure Tab + Enter/Space toggles filters and triggers CTA; announce advanced settings changes via live region.

### 10) Additional enhancements (new)
- **Theme accents**: allow selecting accent color from a small palette (stores in localStorage, maps to CSS vars).
- **Density toggle**: comfortable/compact switch that adjusts spacing tokens for cards/logs.
- **Time format/localization**: toggle 12h/24h; respect browser locale for timestamps.
- **Performance budget**: defer non-critical scripts, minimize forced reflows on large log updates (batch render).
- **Offline hinting**: if health fails, present a short checklist (check VPN/firewall, confirm port 9090/1256, retry ping).
- **Command palette (kbd)**: quick actions (focus dropzone, force ping, open logs, toggle theme) via `Ctrl/Cmd+K`.
- **Download receipts**: after completion, present a small “Download receipt” link (re-uses existing payload if available; otherwise placeholder with instructions).

## Sequencing (suggested)
1) Foundations: tokens, spacing/density toggles, accent palette plumbing.
2) Status hero/diagnostics and dropzone/CTA polish.
3) Empty/loading states and log filters + copy action.
4) File cards timeline + verify CTA; advanced settings hints/reset affordance.
5) Responsive tweaks (sidebar/bottom sheet, masonry) and accessibility passes.
6) Feedback/toasts refinements and offline/command palette additions.
7) QA pass: cross-browser, dark/light, mobile/desktop, perf sanity.

## Testing & acceptance
- Visual: compare against plan items; ensure theme parity dark/light.
- Functional: upload flows, advanced settings validation/persistence, log filters/copy, verify CRC action, troubleshooting sheet actions.
- Accessibility: keyboard navigation, focus rings, ARIA live regions, skip links.
- Performance: log rendering under load (batched), no layout thrash on resize; monitor console for errors.

## Rollout & toggles
- Gate new accent/density/command palette behind incremental flags in JS (localStorage-driven) if needed.
- Keep fallbacks for older browsers (no-grid overlay → basic outline; no IntersectionObserver → eager render).
- Document new shortcuts and troubleshooting chip behavior in README or inline help.

## Risks & mitigations
- Potential layout shifts on mobile: test sticky elements with safe-area insets.
- Extra JS for overlays/filters: keep modules lean, reuse existing helpers, batch DOM writes.
- Feature discoverability: tooltips and microcopy for new controls (troubleshoot chip, copy logs, density toggle).