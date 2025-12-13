---
title: "Client Web UI Improvement Plan"
status: draft
updated: 2025-12-14
owner: frontend
scope: "api_server/web_ui"
---

# Client Web UI Improvement Plan

## Goals
- Modernize the visual language (color, depth, typography) while staying lightweight and dependency-free.
- Improve clarity for connectivity states, file selection, and transfer progress.
- Enhance logs and empty states so the UI feels alive even when idle.
- Keep the current vanilla ES6 structure; avoid build steps; ensure accessibility and responsiveness.

## Constraints & Principles
- No new build tools; stay pure HTML/JS/CSS (per current project setup).
- Keep assets light; favor SVG/inline icons already present or small additions.
- Maintain existing interactions and API contracts; changes should be additive and non-breaking.
- Respect theme toggle; colors must adapt for light/dark.

## Work Packages (with priorities)

### P0 — Quick Visual Wins
1) **Establish accent color token**
   - Add CSS variables for `--color-accent`, `--color-accent-strong`, `--surface-elevated`, `--text-secondary` for both light/dark themes.
   - Apply to primary CTA, tabs, chips, and active states.
2) **Cards & spacing normalization**
   - Standardize card padding (20–24px), radius (12–14px), shadow (sm) for hero/status/log panels.
   - Ensure consistent gap scales (8/12/16/20) across sections.
3) **File drop area polish**
   - Dashed outline, hover glow, larger cloud-upload icon, and inline helper text for accepted types/size.
   - On selection, show filename, size, and a removable chip.
4) **Status chips**
   - Replace “Offline” text with colored chips (green/yellow/red) and microcopy hint.

### P1 — Clarity & Feedback
5) **Hero/status clarity**
   - Enlarge latency widget, align units, add sparkline placeholder, and graceful idle text (“Waiting to connect”).
   - CONNECT button: full-width primary with icon; add ghost “Test Ping” button.
6) **Advanced tabs polish**
   - Add icons to tabs; tint tab panel background; normalize padding; convert toggles to switch styling with helper text.
7) **Activity logs readability**
   - Filter chips with counts and colored badges for levels.
   - Alternate row backgrounds; monospace timestamps; “Copy last log” and “Pause auto-scroll” controls.

### P2 — Empty States & Microinteractions
8) **Empty/idle states**
   - Friendly illustration/message for no activity; skeleton shimmer for metrics when idle.
9) **Hover/focus states**
   - Define consistent hover/focus for buttons, chips, inputs; ensure visible focus rings.
10) **Responsive tweaks**
    - Stack sections on narrow viewports; ensure dropzone fills width; trim banner padding on mobile.

## Implementation Steps (sequenced)
1. **Add design tokens**: Extend `css/styles.css` with light/dark palettes and spacing/radius/shadow utilities.
2. **Refine layout primitives**: Apply unified card styles to hero/status/log containers; adjust global gaps.
3. **Update dropzone**: Replace icon size/outline, add helper text and selected-file chip rendering in `js/ui.js` (or relevant module).
4. **Status chips & CTA**: Create chip component styles; wire API/Backup status to chips; restyle CONNECT/Test Ping buttons.
5. **Latency/metrics block**: Adjust layout to larger dial/text; add sparkline placeholder; ensure idle text and skeleton states.
6. **Tabs & toggles**: Add icons and panel tint; convert toggles to switch visuals with helper microcopy.
7. **Logs**: Implement level badges, filter chips with counts, row striping, monospace timestamps, and quick actions (copy last, pause auto-scroll).
8. **Empty states**: Add illustration or icon + friendly copy for “No activity yet”; skeleton shimmer for metrics.
9. **Microinteractions**: Add hover/focus styles, transitions, and cursor cues across buttons/links/chips.
10. **Responsive pass**: Add media queries for stacking, padding adjustments, and ensuring dropzone/CTA sizing on mobile widths.

## Acceptance Checklist
- [ ] Colors and elevation are consistent across cards, tabs, and dropzone in both light/dark modes.
- [ ] CONNECT CTA is prominent; statuses use colored chips with helper text.
- [ ] Dropzone shows dashed outline, hover glow, and selected-file chips.
- [ ] Latency/metrics block presents clear idle state and improved hierarchy.
- [ ] Logs show colored level badges, filter chips with counts, striped rows, and utility actions work.
- [ ] Empty/idle views display friendly illustrations/text; skeletons appear while idle.
- [ ] Hover/focus states are visible and accessible; responsive layout holds on narrow screens.

## Notes
- Keep assets inline SVG or existing icon set to avoid new dependencies.
- If adding illustrations, prefer small inline SVGs under `assets/` or data URIs to avoid build tooling.
- Ensure theme toggle updates chip backgrounds and surface colors; verify contrast ratios.