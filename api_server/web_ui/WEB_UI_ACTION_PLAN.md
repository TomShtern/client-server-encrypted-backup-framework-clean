CyberBackup Web UI – Actionable Plan (code + UX)

This document merges static code review and live UI/UX findings into a prioritized, actionable plan.

**Last Updated**: December 17, 2025

## Progress Summary
- ✅ **P0 Complete**: DOM cleanup, offline messaging, advanced settings, empty states
- ✅ **P1 Complete**: Layout improvements, UX polish, control wiring
- 🚧 **P2 In Progress**: Items 1-4 complete, items 5-7 remaining

## Priorities (P0-P2)
- ✅ **P0 COMPLETE**: Remove misleading/non-functional controls; reduce noise and duplicate error messaging.
- ✅ **P1 COMPLETE**: Tighten layout and empty states; make core actions and status clear and prominent.
- 🚧 **P2 IN PROGRESS**: Refactor structure (state, CSS, logging) for maintainability and performance.

## Immediate Fixes (P0) ✅ COMPLETE
1) ✅ Clean DOM cache and dead references
   - Remove duplicate dom.clearFileBtn assignment and legacy dom entries (connStatus/connQuality, unused speed chart toggles if absent).
   - Ensure required elements are present; demote rarely used elements to optional or guard initialization.

2) ✅ Simplify advanced settings until supported
   - Hide or disable Proxy/Polycene/Schedule/Compression/Encryption options that are not sent to the backend.
   - If keeping them, wire values into ApiClient.startBackup options with validation and backend contract, or add “coming soon” copy.

3) ✅ Clarify encryption and limits
   - UI currently offers AES128/ChaCha but server is fixed to AES-256-CBC. Restrict options to the supported mode or clearly label others as unavailable.
   - Keep file validation copy (zip/tar, 1 GB) in sync with FILE_VALIDATION; surface validation errors inline near the drop zone.

4) ✅ Consolidate offline messaging
   - Choose one primary offline indicator (banner or header pills). Reduce redundant alerts to avoid user fatigue.

5) ✅ Right-size empty states
   - Downscale Transfer History placeholder to a small inline empty state (target max height ~160–200px, simple icon/text row). Same for logs. Avoid full-height illustration that pushes content below the fold (see current oversized graphic in screenshots).

6) ✅ Layout: Logs left, Transfers right
   - Restructure the lower section into a two-column responsive grid where Activity Logs sit on the left and Recent Transfers on the right (swap from current stacked layout). On narrow viewports, stack with Logs first, Transfers second.
   - Give Recent Transfers the same card scaffolding as Activity Logs (header bar with actions, muted body, compact empty state) while keeping transfer-specific controls (clear/export/filter) and columns (status/time/file/size).

7) ✅ Guard demo mode and shortcuts
   - Prevent DemoMode from starting while a real job is active; surface a clear “Demo mode” badge and restore status when stopping. Scope global shortcuts (Enter/Escape/double-Escape stop) so they don’t fire inside tabs/dialogs unintentionally.

## UX/Layout Improvements (P1) ✅ COMPLETE
1) ✅ Rebalance layout
   - Reduce Status card vertical padding; align its height with the Configuration column. ALREADY DONE, NO NEED.
   - Resize primary CTA (“Connect & Start Backup”) to be more prominent; cluster Pause/Resume/Stop with clearer disabled states.

2) ✅ Advanced Settings interaction
   - Default collapsed; add short description under the toggle. If unsupported, move to a "Beta/Coming soon" panel instead of tabs.

2a) ✅ Troubleshoot sheet availability
    - Hide or disable "Troubleshoot" actions until monitor results exist; show a short "connect to enable diagnostics" note to avoid no-op buttons.

3) ✅ Logs area readability
   - Increase contrast (lighter background or darker text); place empty-state text inside the log list area; reduce duplicated headings.

4) ✅ Transfer History controls
   - Add quick actions: Clear, Export (CSV/JSON), Filter (success/fail). Render history as compact list; cap visible rows with scrolling.

5) ✅ Icon/typography scaling
   - Normalize icon sizes across header/empty states; ensure helper text is legible (>=13px). Use consistent padding tokens.

## Codebase Refactors (P2) 🚧 IN PROGRESS (4/7 Complete)
1) ✅ State consolidation
   - Move operational flags (connected, jobId, operationInProgress, buttonsEnabled) into StateStore; render via a single subscriber. Reduce scattered mutations in app.js/ui.js.
   - **Status**: Complete - All operational flags moved to StateStore, single subscriber pattern implemented.

2) ✅ Componentization and dependency injection
   - Pass DOM refs into constructors (ThemeManager, LogStore) instead of global dom singleton. Improves testability and SSR safety.
   - **Status**: Complete - ThemeManager and LogStore refactored to accept DOM refs via constructor.

3) ✅ Logging pipeline encapsulation
   - Encapsulate filters/search/export/autoscroll inside LogStore; remove reliance on global applyLogFilters. Add dedupe and configurable capacity.
   - **Status**: Complete - Log filtering logic encapsulated in LogStore class, global applyLogFilters removed.

4) ✅ Transfer history robustness
   - Store jobId, filename, size, status, serverAddress with validation; add filter/export methods; integrate into App event handlers.
   - **Status**: Complete - TransferHistory enhanced with filter(), filterByStatus(), and export() methods; jobId now captured in all transfer entries.

5) 📋 📋 CSS layering
   - Split styles.css into tokens/base/components; prune unused variables and deprecated aliases. Add prefers-reduced-motion handling for heavy glows/animations.
   - **Status**: TODO - Not started.

6) 📋 Performance guardrails
   - Lazy-load heavy visuals (speed chart) when toggled; throttle expensive updates; ensure animation pause respects reduced-motion.
   - **Status**: TODO - Not started.

7) 📋 Layout implementation notes
    - Use a responsive grid (e.g., CSS grid with two columns ≥1200px, single column below) to place Activity Logs (left) and Recent Transfers (right). Share spacing/padding tokens with the Status/Config cards.
    - Extract shared card shell styles (header row, action buttons area, body padding) so Logs and Transfers look consistent; keep content-specific internals (log filters vs transfer columns).

## Suggested Execution Order
1) ✅ P0 cleanup (DOM cache, offline messaging, advanced settings truth-in-advertising, empty state resizing).
2) ✅ UX polish (CTA prominence, layout rebalance, log contrast, history controls and sizing).
3) ✅ Functional wiring (advanced settings → ApiClient, validation clamping, transfer history filter/export).
4) 🚧 Refactors (state consolidation, logging encapsulation, CSS split, performance guards).
   - ✅ Items 1-4 complete (state, componentization, logging, transfer history)
   - 📋 Items 5-7 remaining (CSS layering, performance guardrails, layout notes)

## Acceptance Criteria
### ✅ Completed (P0 + P1 + P2.1-2.4)
- ✅ No dead/duplicate DOM assignments; initialization succeeds without optional elements.
- ✅ Advanced settings either hidden/clearly "coming soon" or fully wired to API payload with validation and backend support.
- ✅ Offline state communicated once, clearly; banner and pills do not duplicate.
- ✅ Status/CTA visible without excessive scrolling; empty states occupy minimal space and are informative.
- ✅ Logs readable with sufficient contrast; history list compact with clear actions (clear/export/filter) even when empty.
- ✅ Demo mode cannot start while a real job is active; a visible badge indicates simulated mode and stopping restores live status.
- ✅ Troubleshoot sheet and global shortcuts are scoped so inactive contexts (dialogs, tabs) do not trigger unintended actions.
- ✅ **State consolidation**: Operational flags in StateStore with single subscriber pattern.
- ✅ **Componentization**: ThemeManager and LogStore accept DOM refs via constructor.
- ✅ **Logging encapsulation**: Log filtering logic encapsulated in LogStore class.
- ✅ **Transfer history robustness**: Full validation, filter/export methods, jobId tracking.

### 📋 Remaining (P2.5-2.7)
- 📋 CSS split into logical layers (tokens/base/components).
- 📋 Performance guardrails (lazy loading, throttling, reduced-motion handling).
- 📋 Lintable, testable modules with reduced globals.
