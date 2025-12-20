Based on the comprehensive audit provided, here is a strict plan to remove dead code, duplications, and redundancies. This plan focuses solely on cleanup and deletion as requested, using the audit as the source of truth.

### Phase 1: HTML Cleanup

**1. Remove Unused External Resource**
*   **Source**: Section 1.1 (Typography)
*   **Action**: Remove the Google Fonts `<link>` tag for the "Inter" font.
*   **Location**: `index.html` (Line 37).
*   **Reasoning**: The audit states Inter is loaded but "not even applied in the CSS," making it purely wasteful network overhead.

### Phase 2: CSS Dead Code Removal

**2. Delete Unused CSS Variables**
*   **Source**: Section 2.1 (Issue 5)
*   **Action**: Delete the following undefined variables from the `:root` block:
    *   `--text-secondary-strong` (Line 24)
    *   `--bg-tertiary`, `--bg-quaternary` (Lines 28-29)
    *   `--border-default` (Line 30)
    *   `--text-fluid-sm` (Line 36)
    *   `--gradient-primary`, `--gradient-flow`, `--gradient-flow-size`, `--card-gradient` (Lines 51-54)
    *   `--blur-xs` (Line 64)
    *   `--glow-accent`, `--glow-warning` (Lines 78, 81)
    *   `--ease-in`, `--ease-elastic`, `--ease-snappy` (Lines 147, 149, 164)
    *   `--ring-glow-idle`, `--ring-glow-active`, `--ring-glow-completing`, `--ring-glow-complete` (Lines 180-183)
    *   `--circuit-pattern` (Line 188)
*   **Target Savings**: ~60 lines.

**3. Delete Dead Style Blocks and Comments**
*   **Source**: Section 2.1 (Issue 6)
*   **Action**: Remove the following unused code blocks:
    *   Empty comment blocks at lines 1019-1021 ("Light mode server status adjustments"), 1319 ("Light mode label contrast").
    *   15 consecutive blank lines (Lines 1324-1339).
    *   Elements permanently set to `display: none`:
        *   `.phase::after` (Line 1856)
        *   `.center::before` (Line 1886)
        *   `.file-drop-zone .drop-zone-wave` (Lines 2262-2264)
    *   Unused skeleton loading CSS `.logs-skeleton` (Lines 4644-4665) – Audit confirms this is "not present in HTML".
*   **Target Savings**: ~70 lines.

### Phase 3: Removing Duplications (CSS)

**4. Consolidate Duplicate Toggle Switches**
*   **Source**: Section 2.1 (Issue 2)
*   **Action**:
    *   Identify the two near-identical implementations: `.theme-switch` (Lines 2124-2163) and `.toggle-switch` (Lines 2664-2735).
    *   Refactor to a single `.toggle-base` class.
    *   **Delete** the ~60 lines of redundant code caused by having two separate blocks for the same UI element.

**5. Deduplicate Keyframe Animations**
*   **Source**: Section 2.1 (Issue 3)
*   **Action**: Remove duplicate `@keyframe` definitions and map elements to a single shared animation name:
    *   **Pulse Group**: Keep one (e.g., `pulse-dot`) and delete redundant definitions for `pulse-icon`, `pulse-core`, and `tabDotPulse`. Consolidate `pulse-connected` and `pulse-connecting`.
    *   **Fade Group**: Keep one generic fade (e.g., `fade-in`) and delete redundant `fadeInUp`, `fadeSlideIn`, `log-entry-in`, and `stagger-fade-in`.
    *   **Rotation Group**: Delete `rotate-tech` (identical to `spin`). Delete `rotate-tech-reverse` and use `animation-direction: reverse` instead.
    *   **Shimmer Group**: Merge `shimmer` and `shimmer-sweep`.
*   **Target Savings**: ~86 lines (approx. 26% of animation code).

**6. Remove Redundant Color Definitions**
*   **Source**: Section 1.2 and 2.1 (Issue 4)
*   **Action**:
    *   Identify the 108+ instances of hardcoded `rgba(88, 166, 255, ...)` strings.
    *   **Delete** these repeated hardcoded strings throughout the CSS.
    *   Replace them with references to the existing opacity variables (or the single definition created during cleanup) to remove the bloat of repeating the specific RGBA values 108 times.

### Summary of Cleanup
*   **Files Affected**: `index.html`, `css/styles.css`
*   **Estimated Total Lines Removed**: ~336+ lines of CSS + 1 line of HTML.
*   **Primary Goal**: strictly removing unused resources, dead variables, hidden elements, and code duplications as identified in the audit.