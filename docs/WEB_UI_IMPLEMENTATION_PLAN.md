# CyberBackup Web UI – Implementation Plan (Desktop/Laptop Focus)

## Scope & guardrails
- Platform: Desktop/laptop only (no mobile/tablet requirements).
- Goals: Improve clarity of connection flow, accessibility, contrast, and reduce visual noise; fix observed bugs; keep animations tasteful and respectful of reduced-motion and idle states.
- Non-goals: Large-scale JS modularization; mobile layouts; heavy refactors without clear ROI.

## Decisions based on feedback
- Primary CTA sublabel: Remove the decorative sublabel under CONNECT; keep concise main label and improve inline status feedback elsewhere.
- Animation/`will-change`: Leave existing `will-change` hints largely intact; only remove if clearly unused or on non-animated elements. Prefer gating heavy animations by state instead of broad removals.
- JS modularity: Treat as low priority; do not split unless measurable startup benefit is proven.
- Network safety guard: Add a simple guard to skip socket init when API base URL is missing (e.g., file://) and show a persistent “API not available” badge if appropriate.
- State batching: Optional. Consider rAF-batched rendering for logs/stats only if profiling shows benefit and without destabilizing UI state.
- Demo mode: Provide a hidden/secondary demo mode for testing/sales; must not overshadow the real backup flow and should be clearly marked as simulated.

## Priority roadmap
### P0 (Immediate polish & bug fixes)
- Remove CONNECT sublabel; add inline spinner near status text on connect attempts.
- Surface server status + latency inline (not hover-only); keep dropdown for details.
- Fix logs empty-state overlap when entries exist; implement Recent filter control behavior.
- Increase light-mode contrast for toolbar search/chips and ensure icon-only buttons have `aria-label` and visible focus.
- Ensure Skip link is focus-visible with proper offset; add `aria-live="polite"` to status message.
- Add click-to-toggle for connection details dropdown to support touch/pen; close on outside click.

### P1 (Near term: UX/accessibility/IA)
- Pause or soften heavy animations when idle/offline and respect `prefers-reduced-motion`; keep drag-over pulse only during drag.
- Add focus outlines to custom pills/segmented controls (use accent ring); adjust contrast of secondary text/borders.
- Compress header pills at narrower desktop widths (≤1200px), stacking latency/quality below server pills to avoid wrap.
- Lighten idle progress hero; reserve full neon/tech ring for active uploads.
- Add microcopy under stats and align numbers right with tabular numerals.
- Add error banner in status strip mirroring toast when network errors occur.

### P2 (Quality/performance/optional)
- Gate heavy animations behind an `app-idle`/`reduced-motion` class; prune any clearly unused animation blocks.
- Optional: rAF-batch log/stats rendering if profiling shows meaningful reduction in layout/paint churn.
- Optional: Guard socket init on missing API base URL; show “API not available” badge in header.
- Optional: Demo mode (simulated transfer) accessible via non-primary entry (e.g., settings toggle or query flag), clearly labeled as simulation.

## Work breakdown (taskable items)
- CTA & status
  - Remove CONNECT sublabel text.
  - Add inline spinner/feedback in status strip during connect attempts.
  - Always show status + latency text; retain dropdown for detail.
- Logs & filters
  - Fix empty-state visibility logic; show caption like “Last N entries” when data exists.
  - Implement Recent filter to limit to last N entries.
  - Ensure toolbar inputs/chips meet contrast and focus specs.
- Accessibility
  - Add `aria-label` to icon-only controls; verify tab order.
  - Make Skip link focus-visible and positioned; add `aria-live` to status message.
  - Ensure advanced tabs have proper roles/tabindex and keyboard cycling.
- Visual polish
  - Soften idle animations; restrict pulses/glow to drag-over/active states.
  - Adjust header pill layout at ≤1200px for desktop; maintain two-column layout otherwise.
  - Add stat microcopy and right-align numbers.
- Error handling
  - Mirror network errors in a status-strip banner in addition to toast/log.
- Optional/perf
  - Profile logs/stats rendering; if beneficial, introduce single rAF batch update.
  - Add API base URL guard and badge when absent.
  - Add hidden demo mode clearly labeled as simulated.

## Acceptance checks
- Accessibility: Icon-only controls have labels; skip link focus-visible; status changes announced politely; focus rings visible in light mode; advanced tabs keyboard-navigable.
- Visual: Light-mode contrast meets WCAG AA for form borders/icons; idle animations are subdued; header pills don’t wrap awkwardly at narrower desktop widths; progress hero is calmer when idle.
- Behavior: Status + latency always visible; connect shows inline progress; logs empty state only when truly empty; Recent filter works; connection details accessible via click on touch/pen.
- Performance/optional: Any batching or animation gating shows measurable reduction in unnecessary paints without UI regressions.
- Demo mode: Present but secondary, clearly marked as simulation, not default.

## Risks & mitigations
- Animation changes causing regressions: Toggle via state classes and keep a quick revert flag.
- Batching side effects on UI freshness: Limit to logs/stats and ship behind a small feature flag.
- Demo mode confusion: Hide behind settings/flag, label prominently as “Simulated”.

## Next steps
1) Confirm scope for optional items (animation gating, batching, API guard, demo mode).
2) Implement P0 items first; verify with screenshots (dark/light) and quick accessibility spot-checks.
3) Proceed to P1 polish; profile before any P2/perf work.
