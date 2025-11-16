# CyberBackup Client GUI - Design Issues Analysis

**Analysis Date**: 2025-11-16
**Analyzed Files**: `NewGUIforClient.html`, `styles/app.css`, `scripts/enhancements.js`
**Source**: Screenshots of current GUI implementation

---

## Executive Summary

This document identifies **32 critical design, layout, spacing, and alignment issues** found in the CyberBackup Client web GUI. Issues are categorized by severity and type, with specific fixes provided for each. A comprehensive action plan is included at the end.

**Severity Levels:**
- 🔴 **Critical**: Significantly impacts usability or visual quality
- 🟡 **High**: Noticeable issues that detract from user experience
- 🟢 **Medium**: Minor polish items that improve overall quality

---

## 1. Layout & Grid Structure Issues

### 🔴 Issue #1: Unbalanced Two-Column Grid
**Location**: `main` grid layout (Configuration vs Status panels)
**Problem**: The left column (400px fixed) is too narrow relative to the right column (1fr), creating visual imbalance. The progress ring dominates the right panel, leaving the left feeling cramped.

**Current Code** (app.css:410-415):
```css
main {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: var(--space-lg);
  align-items: start;
}
```

**Fix**:
```css
main {
  display: grid;
  grid-template-columns: minmax(420px, 480px) minmax(600px, 1fr);
  gap: var(--space-xl); /* Increase from --space-lg (24px) to --space-xl (32px) */
  align-items: start;
  max-width: 1400px; /* Prevent excessive stretching on ultra-wide screens */
  margin: 0 auto;
}
```

**Rationale**: Wider left panel (420-480px) provides breathing room for inputs and file card. Max-width prevents layout from looking stretched on 4K displays.

---

### 🟡 Issue #2: Inconsistent Section Padding
**Location**: `.stack` class used for both Configuration and Status panels
**Problem**: Both panels use identical padding (var(--space-xl) = 32px), but the Status panel feels cramped due to the large progress ring, while Configuration feels spacious.

**Current Code** (app.css:417-425):
```css
.stack,
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 100%), var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: var(--space-xl); /* 32px all sides */
  box-shadow: var(--shadow);
}
```

**Fix**:
```css
.stack,
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 100%), var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: var(--space-lg) var(--space-xl); /* 24px vertical, 32px horizontal */
  box-shadow: var(--shadow);
}

/* Specific overrides for different panel types */
main > .stack:first-child {
  padding: var(--space-xl); /* Configuration panel keeps square padding */
}

main > .stack:last-child {
  padding: var(--space-2xl) var(--space-xl); /* Status panel gets more vertical space (48px) */
}
```

**Rationale**: Status panel needs more vertical breathing room around the progress ring. Configuration panel benefits from symmetric padding.

---

### 🟡 Issue #3: Progress Ring Container Layout Issues
**Location**: `.center` class containing progress ring
**Problem**: The ring takes up excessive vertical space, pushing action buttons down. The container doesn't properly constrain the ring's maximum size.

**Current Code** (app.css:469-480):
```css
.center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  width: 100%;
  padding: var(--space-lg) 0 var(--space-md);
  min-height: 320px;
}
```

**Fix**:
```css
.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm); /* Reduce gap from 16px to 12px */
  width: 100%;
  padding: var(--space-md) 0; /* Reduce vertical padding */
  min-height: 280px; /* Reduce from 320px */
  max-height: 380px; /* Add constraint */
  position: relative;
}

/* Remove flex: 1 to prevent excessive growth */
```

**Rationale**: Removing `flex: 1` prevents the container from greedily expanding. Tighter constraints create better visual proportion.

---

### 🔴 Issue #4: Progress Ring Sizing
**Location**: `#progressRing` SVG element
**Problem**: At 320px (desktop), the ring dominates the panel. It's sized absolutely rather than responsively.

**Current Code** (app.css:105-107, 914-924):
```css
:root {
  --ring-size: 320px;
  --ring-max: 380px;
}

#progressRing {
  width: var(--ring-size);
  height: var(--ring-size);
  max-width: var(--ring-max);
  max-height: var(--ring-max);
  /* ... */
}
```

**Fix**:
```css
:root {
  --ring-size: clamp(240px, 28vw, 300px); /* Responsive between 240-300px */
  --ring-max: 300px; /* Reduce from 380px */
}

#progressRing {
  width: var(--ring-size);
  height: var(--ring-size);
  max-width: var(--ring-max);
  max-height: var(--ring-max);
  aspect-ratio: 1 / 1; /* Ensure perfect square */
  margin: var(--space-md) auto; /* Add vertical margin, center horizontally */
  position: relative;
  display: grid;
  place-items: center;
  filter: drop-shadow(0 4px 16px rgba(88, 166, 255, 0.3)) drop-shadow(0 0 32px rgba(88, 166, 255, 0.12));
}
```

**Rationale**: Smaller ring (240-300px range) provides better proportion. `clamp()` makes it responsive to viewport width while maintaining constraints.

---

### 🟢 Issue #5: Stats Grid Proportions
**Location**: `#statsGrid` container
**Problem**: Stats cards are too wide on large screens, making the numbers feel disconnected from labels. Grid doesn't adapt well to available space.

**Current Code** (app.css:1005-1012):
```css
#statsGrid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}
```

**Fix**:
```css
#statsGrid {
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 180px)); /* Constrain card width */
  gap: var(--space-md);
  width: 100%;
  justify-content: center; /* Center the grid */
  margin: var(--space-lg) auto 0; /* Add top margin for separation */
}
```

**Rationale**: Constraining card width (120-180px) keeps stats compact and readable. `justify-content: center` prevents excessive stretching.

---

## 2. Typography & Visual Hierarchy

### 🔴 Issue #6: Inconsistent Section Header Styling
**Location**: `.phase` class used for "Configuration", "Status", "Activity Logs"
**Problem**: Headers have identical styling despite different contexts. "Activity Logs" uses `.heading-centered` which has different padding/border.

**Current Code** (app.css:868-899, 1129-1137):
```css
.phase {
  font-weight: var(--weight-bold);
  font-size: var(--fs-24);
  /* ... */
  padding-bottom: var(--space-sm);
}

.phase::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 64px;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), transparent);
}

.heading-centered {
  margin: 0 0 var(--gap-4) 0;
  padding-bottom: var(--gap-3);
  border-bottom: 1px solid var(--border);
  text-align: center;
  font-size: var(--fs-18); /* Smaller! */
  font-weight: 700;
}
```

**Fix**:
```css
/* Base phase styling - applies to all section headers */
.phase {
  font-weight: var(--weight-bold);
  font-size: var(--fs-24);
  letter-spacing: -0.5px;
  line-height: 1.2;
  margin: 0 0 var(--space-lg) 0; /* Increase from --space-md */
  padding-bottom: var(--space-md); /* Increase from --space-sm */
  color: var(--fg);
  position: relative;
  border-bottom: 2px solid var(--border);
}

/* Remove the gradient underline - use full-width border instead */
.phase::after {
  display: none;
}

/* Centered variant for full-width sections like Activity Logs */
.phase.heading-centered {
  text-align: center;
  font-size: var(--fs-24); /* Match other headers */
  border-bottom-color: var(--border-hover); /* Slightly stronger */
}

/* Panel headers inside stacks */
.stack > .phase:first-child {
  margin-top: 0;
}
```

**Rationale**: Consistent font size (24px) across all headers. Full-width border is cleaner than gradient. Increased spacing improves visual separation.

---

### 🟡 Issue #7: Weak Font Hierarchy
**Location**: Overall typography system
**Problem**: Font weights and sizes don't create enough differentiation. Body text (14px) and labels (13px) are too similar.

**Current Code** (app.css:80-96):
```css
--fs-10: 10px;
--fs-11: 11px;
--fs-12: 12px;
--fs-13: 13px;
--fs-14: 14px;
--fs-15: 15px;
--fs-16: 16px;
/* ... too many incremental steps */
```

**Fix**:
```css
/* Use a type scale with clear jumps */
:root {
  /* Body & UI Text */
  --fs-xs: 11px;   /* Captions, metadata */
  --fs-sm: 13px;   /* Labels, secondary text */
  --fs-base: 15px; /* Body text (increase from 14px) */
  --fs-md: 16px;   /* Emphasized body */
  --fs-lg: 18px;   /* Subheadings */

  /* Headings */
  --fs-xl: 24px;   /* Section headers */
  --fs-2xl: 32px;  /* Page title */
  --fs-3xl: 40px;  /* Hero elements */

  /* Display */
  --fs-display: clamp(64px, 8vw, 96px); /* Progress percentage */
}

/* Update body to use new base */
body {
  font-size: var(--fs-base); /* 15px instead of 14px */
  line-height: 1.6; /* Increase from 1.5 for better readability */
}

/* Update labels */
label,
.label-text {
  font-size: var(--fs-sm); /* 13px */
  font-weight: var(--weight-semibold); /* 600 instead of current 600 */
}

/* Update captions */
.file-sub,
.hint,
.text-caption {
  font-size: var(--fs-xs); /* 11px */
  font-weight: var(--weight-normal); /* 400 */
}
```

**Rationale**: Clearer type scale with meaningful jumps. Larger base font (15px) improves readability. Consistent labeling across UI.

---

### 🟡 Issue #8: Poor Text Contrast in File Drop Zone
**Location**: File drop zone placeholder text
**Problem**: "Drag & drop a file here or choose above" uses default text color which has insufficient contrast against the gradient background.

**Current Code** (app.css:818-829):
```css
.file-name {
  font-weight: 600;
  font-size: var(--fs-14);
  /* ... */
  color: var(--fg); /* Full opacity */
}
```

**Fix**:
```css
.file-name {
  font-weight: 600;
  font-size: var(--fs-base); /* Use new base size (15px) */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--fg);
  line-height: 1.5;
  max-width: 100%;
}

/* When showing placeholder (no file selected) */
.file-name:empty::before,
.file-name.placeholder {
  content: attr(data-placeholder);
  color: var(--muted);
  font-weight: var(--weight-normal); /* Reduce from 600 */
  font-style: italic;
}

/* When file is selected */
.file-name:not(:empty):not(.placeholder) {
  color: var(--fg);
  font-weight: var(--weight-semibold);
}
```

**Enhancement in HTML**:
```html
<div class="file-name placeholder" id="fileName" data-placeholder="Drag & drop a file here or choose above">
</div>
```

**Rationale**: Placeholder text should be visually distinct (muted color, lighter weight, italic). Actual filename is bold and high-contrast.

---

## 3. Component Spacing & Alignment

### 🔴 Issue #9: Cramped File Drop Zone Buttons
**Location**: Button row in file drop zone
**Problem**: "Choose File" and "Recent" buttons are too close together, creating visual tension. No clear visual hierarchy between primary and secondary action.

**Current Code** (app.css:762-771):
```css
.file-drop-zone .row {
  margin-bottom: var(--space-md);
  justify-content: center;
  gap: var(--space-md); /* 16px */
}

.file-drop-zone .row button {
  flex: 0 1 auto;
  min-width: 140px;
}
```

**Fix**:
```css
.file-drop-zone .row {
  margin-bottom: var(--space-lg); /* Increase from 16px to 24px */
  justify-content: center;
  gap: var(--space-lg); /* Increase gap to 24px */
  flex-wrap: wrap; /* Allow wrapping on narrow screens */
}

.file-drop-zone .row button {
  flex: 0 1 auto;
  min-width: 140px;
  padding: 12px 24px; /* Increase from default */
}

/* Make "Choose File" button more prominent */
#fileSelectBtn {
  background: var(--surface-hover);
  border-color: var(--border-hover);
  font-weight: var(--weight-semibold);
}

#fileSelectBtn:hover {
  background: linear-gradient(135deg, rgba(88, 166, 255, 0.15), rgba(88, 166, 255, 0.08));
  border-color: var(--focus);
  transform: translateY(-2px);
}

/* "Recent" button stays ghost style but more subdued */
#recentFilesBtn {
  opacity: 0.85;
}
```

**Rationale**: Increased spacing (24px) provides breathing room. Visual differentiation makes primary action clear.

---

### 🟡 Issue #10: File Card Layout Too Tight
**Location**: `.file-card` grid layout
**Problem**: 64px icon is cramped next to metadata. Grid gaps are too small. Clear button feels tacked on.

**Current Code** (app.css:773-791):
```css
.file-card {
  display: grid;
  grid-template-columns: 64px 1fr auto;
  gap: var(--space-md); /* 16px */
  align-items: center;
  padding: var(--space-lg);
  /* ... */
}
```

**Fix**:
```css
.file-card {
  display: grid;
  grid-template-columns: 72px 1fr auto; /* Increase icon column to 72px */
  gap: var(--space-lg); /* Increase to 24px */
  align-items: center;
  padding: var(--space-lg) var(--space-xl); /* More horizontal padding */
  background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%), var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow);
  min-height: 96px; /* Add minimum height */
}

.file-icon {
  width: 72px; /* Increase from 64px */
  height: 72px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-lg); /* Increase from --radius-md */
  background: linear-gradient(135deg, rgba(88, 166, 255, 0.15) 0%, rgba(34, 211, 238, 0.08) 100%), var(--surface-alt);
  border: 1px solid rgba(88, 166, 255, 0.3);
  font-size: var(--fs-36); /* Increase from --fs-32 */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(88, 166, 255, 0.1);
}

.file-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs); /* Add gap between name and metadata */
  padding: var(--space-xs) 0; /* Vertical padding */
}
```

**Rationale**: Larger icon (72px) is more prominent. Increased gaps create spacious feel. Minimum height prevents collapse when empty.

---

### 🟡 Issue #11: Action Buttons Row Spacing
**Location**: `.actions` container below progress ring
**Problem**: Buttons are too close together. Primary button doesn't stand out enough. No clear visual grouping.

**Current Code** (app.css:954-967):
```css
.actions {
  display: flex;
  gap: var(--space-md); /* 16px */
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
  margin-top: var(--space-lg);
  margin-bottom: var(--space-md);
}

.actions button {
  flex: 0 1 auto;
  min-width: 100px;
}
```

**Fix**:
```css
.actions {
  display: flex;
  gap: var(--space-md); /* Keep 16px for buttons */
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
  margin-top: var(--space-xl); /* Increase from 24px to 32px */
  margin-bottom: var(--space-lg); /* Increase from 16px to 24px */
  padding: 0 var(--space-md); /* Add horizontal padding */
}

.actions button {
  flex: 0 1 auto;
  min-width: 110px; /* Slightly wider */
  padding: 14px 20px; /* More balanced padding */
}

/* Create visual separation between primary and secondary actions */
.actions button.primary {
  margin-right: var(--space-md); /* Add 16px margin after primary button */
}

/* Group pause/resume/stop buttons together */
.actions button:not(.primary) {
  min-width: 100px; /* Slightly narrower for secondary actions */
}
```

**Rationale**: Extra spacing around actions creates visual breathing room. Margin after primary button creates clear grouping.

---

### 🟡 Issue #12: Activity Logs Toolbar Misalignment
**Location**: `.toolbar` container with search, filters, controls
**Problem**: Elements don't align properly. Search bar, filter buttons, and autoscroll checkbox are on different visual baselines. Inconsistent spacing.

**Current Code** (app.css:1139-1146):
```css
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--gap-3);
  gap: var(--gap-3);
  flex-wrap: wrap;
}
```

**Fix**:
```css
.toolbar {
  display: grid;
  grid-template-columns: minmax(200px, 320px) auto 1fr auto;
  grid-template-areas: "search filters spacer controls";
  align-items: center;
  gap: var(--space-lg); /* Increase from var(--gap-3) = 12px to 24px */
  margin-bottom: var(--space-lg); /* Increase from 12px to 24px */
  padding: var(--space-md); /* Add padding around entire toolbar */
  background: rgba(255, 255, 255, 0.02); /* Subtle background */
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.log-search {
  grid-area: search;
  min-width: 200px;
  max-width: 320px;
}

.filter-group {
  grid-area: filters;
  justify-self: start;
}

.toolbar > .row {
  grid-area: controls;
  justify-self: end;
  gap: var(--space-md);
}

/* Responsive: stack on narrow screens */
@media (max-width: 900px) {
  .toolbar {
    grid-template-columns: 1fr;
    grid-template-areas:
      "search"
      "filters"
      "controls";
    gap: var(--space-md);
  }
}
```

**Rationale**: CSS Grid provides precise control over alignment. All elements align on same baseline. Responsive fallback for narrow screens.

---

### 🔴 Issue #13: Filter Button Group Spacing
**Location**: `.filter-group` with All/Info/Warn/Error buttons
**Problem**: Buttons are too tight together (no visual separation). Active state isn't prominent enough.

**Current Code** (app.css:1183-1210):
```css
.filter-group {
  display: flex;
  gap: var(--gap-2); /* 8px - too tight */
  padding: 0;
  border: none;
  margin: 0;
}

.filter-btn {
  padding: 6px 12px;
  /* ... */
}

.filter-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}
```

**Fix**:
```css
.filter-group {
  display: inline-flex;
  gap: 0; /* Remove gap - use segmented control style */
  padding: 4px;
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface-alt);
  margin: 0;
}

.filter-btn {
  padding: 8px 16px; /* Increase padding */
  border-radius: var(--radius-md);
  border: none; /* Remove individual borders */
  background: transparent;
  font-size: var(--fs-sm); /* 13px */
  font-weight: var(--weight-semibold);
  transition: all 0.2s ease;
  color: var(--fg-secondary);
  position: relative;
  min-width: 64px;
}

.filter-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
  color: var(--fg);
}

.filter-btn.active {
  background: var(--accent);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(88, 166, 255, 0.3);
  font-weight: var(--weight-bold);
}

/* Add subtle separator between buttons */
.filter-btn:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 25%;
  height: 50%;
  width: 1px;
  background: var(--border);
  opacity: 0.5;
}

.filter-btn.active::after,
.filter-btn.active + .filter-btn::after {
  display: none; /* Hide separator next to active button */
}
```

**Rationale**: Segmented control design (iOS/macOS style) is cleaner and more modern. Active state is more prominent. Subtle separators prevent buttons from blurring together.

---

### 🟢 Issue #14: Autoscroll Checkbox Misalignment
**Location**: Autoscroll label + checkbox in toolbar
**Problem**: Checkbox and label text aren't vertically aligned. Spacing between checkbox and "Export" button is inconsistent.

**Current Code** (app.css:1270-1281):
```css
.label-autoscroll {
  gap: var(--gap-2);
  cursor: pointer;
}

.label-autoscroll input {
  cursor: pointer;
}

.label-autoscroll span {
  font-size: var(--fs-13);
}
```

**Fix**:
```css
.label-autoscroll {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs); /* 8px */
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  transition: background 0.2s ease;
  font-size: var(--fs-sm);
  font-weight: var(--weight-medium);
  color: var(--fg-secondary);
  user-select: none;
}

.label-autoscroll:hover {
  background: rgba(255, 255, 255, 0.03);
  color: var(--fg);
}

.label-autoscroll input[type="checkbox"] {
  cursor: pointer;
  width: 18px;
  height: 18px;
  margin: 0;
  accent-color: var(--accent); /* Modern checkbox styling */
}

.label-autoscroll span {
  font-size: var(--fs-sm);
  line-height: 1;
}

/* Ensure proper spacing in toolbar row */
.toolbar > .row {
  display: flex;
  align-items: center;
  gap: var(--space-md); /* 16px between autoscroll and export */
}
```

**Rationale**: `inline-flex` with `align-items: center` ensures perfect vertical alignment. Hover state provides feedback. `accent-color` modernizes checkbox appearance.

---

## 4. Visual Hierarchy & Emphasis

### 🔴 Issue #15: No Clear Primary Action
**Location**: All buttons have similar visual weight
**Problem**: Primary action button ("Connect & Start") doesn't stand out enough from secondary actions (Pause, Resume, Stop). Users can't quickly identify the main action.

**Current Code** (app.css:631-663):
```css
button.primary {
  background: linear-gradient(180deg, var(--accent-hover) 0%, var(--accent) 100%);
  color: #ffffff;
  border-color: var(--accent);
  font-weight: var(--weight-bold);
  /* ... */
  box-shadow: 0 2px 8px rgba(31, 111, 235, 0.3), ...;
}
```

**Fix**:
```css
button.primary {
  background: linear-gradient(135deg, #388bfd 0%, #1f6feb 100%);
  color: #ffffff;
  border: 2px solid rgba(88, 166, 255, 0.4); /* Thicker border */
  font-weight: var(--weight-bold);
  font-size: var(--fs-md); /* 16px - larger than others */
  min-height: 56px; /* Taller than default 52px */
  padding: 16px 40px; /* More generous padding */
  letter-spacing: 0.5px;
  text-transform: uppercase; /* Make it stand out */
  box-shadow:
    0 4px 16px rgba(88, 166, 255, 0.4),
    0 8px 32px rgba(88, 166, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

button.primary::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.15) 50%, transparent 100%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

button.primary:hover::before {
  transform: translateX(100%);
}

button.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #58a6ff 0%, #388bfd 100%);
  border-color: rgba(88, 166, 255, 0.6);
  box-shadow:
    0 6px 24px rgba(88, 166, 255, 0.5),
    0 12px 48px rgba(88, 166, 255, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transform: translateY(-2px) scale(1.02);
}

/* Make secondary buttons more subdued */
button:not(.primary):not(.ghost) {
  background: var(--surface-alt);
  color: var(--fg-secondary);
  border: 1px solid var(--border);
  font-size: var(--fs-sm); /* 13px - smaller than primary */
}

button:not(.primary):not(.ghost):hover:not(:disabled) {
  background: var(--surface-hover);
  color: var(--fg);
  border-color: var(--border-hover);
}
```

**Rationale**: Larger size, uppercase text, thicker border, and stronger shadow make primary button unmissable. Secondary buttons are intentionally subdued.

---

### 🟡 Issue #16: Status Badges Low Contrast
**Location**: Connection status badges in header (Ready, Latency, Offline)
**Problem**: Badges blend into header background. Color differentiation between states isn't strong enough.

**Current Code** (app.css:345-408):
```css
.badge,
.chip {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: var(--fs-12);
  font-weight: 500;
  border: 1px solid var(--border);
  background: var(--surface-alt);
  /* ... */
}

.badge.connected {
  border-color: rgba(63, 185, 80, 0.3);
  background: rgba(63, 185, 80, 0.1);
  color: var(--success);
}
```

**Fix**:
```css
.badge,
.chip {
  padding: 6px 14px; /* Increase from 4px 10px */
  border-radius: var(--radius-full);
  font-size: var(--fs-sm); /* 13px, up from 12px */
  font-weight: var(--weight-semibold); /* 600, up from 500 */
  letter-spacing: 0.3px;
  border: 2px solid; /* Thicker border */
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  transition: all 0.3s ease;
}

/* Connected state - vibrant green */
.badge.connected {
  border-color: rgba(63, 185, 80, 0.5);
  background: linear-gradient(135deg, rgba(63, 185, 80, 0.20) 0%, rgba(63, 185, 80, 0.12) 100%);
  color: #3fb950;
  box-shadow: 0 2px 12px rgba(63, 185, 80, 0.25);
  animation: pulse-connected 3s ease-in-out infinite;
}

@keyframes pulse-connected {
  0%, 100% {
    box-shadow: 0 2px 12px rgba(63, 185, 80, 0.25);
  }
  50% {
    box-shadow: 0 2px 16px rgba(63, 185, 80, 0.4);
  }
}

/* Connecting state - animated orange */
.badge.connecting {
  border-color: rgba(255, 165, 0, 0.5);
  background: linear-gradient(135deg, rgba(255, 165, 0, 0.20) 0%, rgba(255, 165, 0, 0.12) 100%);
  color: #ffa500;
  box-shadow: 0 2px 12px rgba(255, 165, 0, 0.25);
  animation: pulse-connecting 1.5s ease-in-out infinite;
}

@keyframes pulse-connecting {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Disconnected state - red with emphasis */
.badge.disconnected {
  border-color: rgba(248, 81, 73, 0.5);
  background: linear-gradient(135deg, rgba(248, 81, 73, 0.20) 0%, rgba(248, 81, 73, 0.12) 100%);
  color: #f85149;
  box-shadow: 0 2px 12px rgba(248, 81, 73, 0.25);
}

/* Quality chips - similar treatment */
.chip.quality-excellent {
  color: #3fb950;
  border-color: rgba(63, 185, 80, 0.4);
  background: linear-gradient(135deg, rgba(63, 185, 80, 0.15) 0%, rgba(63, 185, 80, 0.08) 100%);
  font-weight: var(--weight-bold);
}

/* Add pulsing dot indicator */
.badge::before,
.chip::before {
  content: '●';
  font-size: 10px;
  animation: inherit; /* Inherit pulse animation from parent */
}
```

**Rationale**: Thicker borders, gradients, and box shadows create depth. Pulsing animations draw attention to status changes. Color vibrancy increased for better contrast.

---

### 🟢 Issue #17: Progress Ring Idle State Invisible
**Location**: `#progressRing.idle` state
**Problem**: In idle state, the ring is nearly invisible (grayscale + 40% opacity), making the entire Status panel feel empty.

**Current Code** (app.css:1506-1509):
```css
#progressRing.idle {
  filter: grayscale(1) opacity(0.4);
  transition: filter 0.3s ease;
}
```

**Fix**:
```css
#progressRing.idle {
  filter: grayscale(0.3) opacity(0.6); /* Less grayscale, more opacity */
  transition: filter 0.5s ease;
}

#progressRing.idle #progressArc {
  stroke: var(--border-hover); /* Use border color instead of gradient */
  stroke-opacity: 0.5;
}

/* Add subtle breathing animation */
#progressRing.idle {
  animation: idle-breathe 4s ease-in-out infinite;
}

@keyframes idle-breathe {
  0%, 100% {
    filter: grayscale(0.3) opacity(0.6);
  }
  50% {
    filter: grayscale(0.2) opacity(0.7);
  }
}

/* Show the percentage text even in idle */
#progressRing.idle .kpi .pct {
  opacity: 0.7; /* Don't hide completely */
  filter: grayscale(0.5);
}
```

**Rationale**: Reduced grayscale (0.3 vs 1.0) keeps some color. Higher opacity (0.6 vs 0.4) makes ring visible. Breathing animation indicates "ready" state.

---

### 🟡 Issue #18: Border Radius Inconsistency
**Location**: Various UI elements use different border radii
**Problem**: Some cards use `--radius-xl` (16px), buttons use `--radius-lg` (12px), inputs use `--radius-md` (8px). No clear system.

**Current Analysis**:
```css
/* Current border radius values */
--radius-sm: 6px;   /* Used for: badges, small elements */
--radius-md: 8px;   /* Used for: inputs, dropdowns */
--radius-lg: 12px;  /* Used for: buttons, cards */
--radius-xl: 16px;  /* Used for: main panels (.stack, .card) */
--radius-2xl: 24px; /* Rarely used */
--radius-full: 9999px; /* Badges, pills */
```

**Fix** - Establish Clear Hierarchy:
```css
:root {
  /* Border radius scale - from subtle to prominent */
  --radius-xs: 4px;   /* NEW: Very subtle corners (inner elements) */
  --radius-sm: 6px;   /* Small UI elements (badges, tags) */
  --radius-md: 10px;  /* INCREASE: Medium elements (inputs, dropdowns) */
  --radius-lg: 14px;  /* INCREASE: Large elements (buttons) */
  --radius-xl: 18px;  /* INCREASE: Containers (cards, panels) */
  --radius-2xl: 24px; /* Hero elements (modals, dialogs) */
  --radius-full: 9999px; /* Pills and circular elements */
}

/* Apply consistently */
input[type="text"],
input[type="file"],
select,
textarea {
  border-radius: var(--radius-md); /* 10px */
}

button {
  border-radius: var(--radius-lg); /* 14px */
}

.stack,
.card,
.file-drop-zone,
.file-card {
  border-radius: var(--radius-xl); /* 18px */
}

.badge,
.chip {
  border-radius: var(--radius-full); /* Pills */
}

.toolbar,
.speed-chart-container,
details {
  border-radius: var(--radius-md); /* 10px - less prominent than cards */
}

dialog,
.modal-card {
  border-radius: var(--radius-2xl); /* 24px - hero prominence */
}

/* Nested elements use smaller radius */
.file-icon {
  border-radius: var(--radius-md); /* 10px - smaller than parent card (18px) */
}

.stat {
  border-radius: var(--radius-lg); /* 14px - smaller than parent stack (18px) */
}
```

**Rationale**: Systematic hierarchy where larger/more prominent elements have larger radii. Nested elements use smaller radii than containers. Incremental steps (4px → 6px → 10px → 14px → 18px → 24px) create visual harmony.

---

## 5. Interaction & Feedback

### 🟡 Issue #19: Weak Hover States
**Location**: Interactive elements lack clear hover feedback
**Problem**: Hover states are too subtle. Users can't easily tell what's clickable.

**Current Code** (Various):
```css
button:hover:not(:disabled) {
  background: var(--surface-hover);
  border-color: var(--border-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}
```

**Fix**:
```css
/* Establish interaction principles */
.interactive {
  cursor: pointer;
  user-select: none;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

/* Primary interactive elements (buttons, cards) */
button:hover:not(:disabled):not(.ghost),
.stat:hover,
.file-card:hover {
  transform: translateY(-3px) scale(1.01); /* More pronounced lift */
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.4),
    0 0 32px rgba(88, 166, 255, 0.15); /* Add glow */
  border-color: rgba(88, 166, 255, 0.5);
}

/* Active/pressed state */
button:active:not(:disabled),
.stat:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition-duration: 0.1s;
}

/* Ghost buttons - subtle hover */
button.ghost:hover:not(:disabled) {
  background: rgba(88, 166, 255, 0.08);
  border-color: rgba(88, 166, 255, 0.3);
  transform: none; /* No lift for ghost */
}

/* Input fields - glow on focus */
input[type="text"]:hover {
  border-color: var(--border-hover);
  background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%), var(--surface);
}

input[type="text"]:focus {
  outline: none;
  border-color: var(--focus);
  box-shadow:
    0 0 0 4px rgba(88, 166, 255, 0.15), /* Wider glow ring */
    0 4px 16px rgba(88, 166, 255, 0.3); /* Depth shadow */
  background: var(--surface);
  transform: translateY(-1px);
}

/* File drop zone - clear hover state */
.file-drop-zone:hover {
  border-color: rgba(88, 166, 255, 0.6); /* Stronger blue */
  background: linear-gradient(180deg, rgba(88, 166, 255, 0.12) 0%, rgba(88, 166, 255, 0.05) 100%), var(--surface);
  box-shadow:
    0 6px 24px rgba(88, 166, 255, 0.25),
    inset 0 0 48px rgba(88, 166, 255, 0.08);
  transform: translateY(-3px);
}
```

**Rationale**: More pronounced lift (3px vs 1px) on hover. Glow effects indicate interactivity. Consistent scale animation (1.01) adds polish. Active states provide tactile feedback.

---

### 🔴 Issue #20: File Drop Zone Lacks Visual Invitation
**Location**: `.file-drop-zone` styling
**Problem**: Drop zone doesn't look inviting or interactive. Users might not recognize it's draggable. Empty state is bland.

**Current Code** (app.css:718-760):
```css
.file-drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius-xl);
  background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.01) 100%), var(--surface-alt);
  padding: var(--space-lg);
  /* ... */
}
```

**Fix**:
```css
.file-drop-zone {
  border: 3px dashed var(--border-hover); /* Thicker, more visible */
  border-radius: var(--radius-xl);
  background:
    radial-gradient(circle at 50% 50%, rgba(88, 166, 255, 0.05) 0%, transparent 60%),
    linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%),
    var(--surface-alt);
  padding: var(--space-xl); /* Increase from --space-lg */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  min-height: 200px; /* Increase from 160px */
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--space-lg); /* Increase from --space-md */
}

/* Add animated dashed border */
.file-drop-zone {
  background-image:
    repeating-linear-gradient(
      0deg,
      var(--border-hover) 0px,
      var(--border-hover) 10px,
      transparent 10px,
      transparent 20px
    );
  background-size: 3px 100%;
  background-position: 0 0, 100% 0, 0 0, 0 100%;
  background-repeat: no-repeat;
  animation: dash-animation 20s linear infinite;
}

@keyframes dash-animation {
  to {
    background-position: 0 -100%, 100% 100%, 100% 0, -100% 100%;
  }
}

/* Pulsing glow when hovering */
.file-drop-zone::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  background: radial-gradient(circle at center, rgba(88, 166, 255, 0.08) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.file-drop-zone:hover::before {
  opacity: 1;
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
}

/* Drag-over state - super prominent */
.file-drop-zone.drag-over {
  background:
    radial-gradient(circle at 50% 50%, rgba(88, 166, 255, 0.2) 0%, transparent 70%),
    linear-gradient(135deg, rgba(34, 211, 238, 0.15) 0%, rgba(139, 92, 246, 0.12) 100%);
  border-color: var(--accent);
  border-style: solid; /* Change from dashed */
  box-shadow:
    0 0 0 4px rgba(88, 166, 255, 0.2),
    0 8px 32px rgba(88, 166, 255, 0.4),
    inset 0 0 64px rgba(34, 211, 238, 0.15);
  transform: scale(1.02);
}

/* Add icon when empty */
.file-drop-zone:not(:has(.file-card:not(.placeholder)))::after {
  content: '📁';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 64px;
  opacity: 0.2;
  pointer-events: none;
  z-index: 0;
}
```

**Rationale**: Animated dashed border creates movement and interest. Radial gradient creates depth. Pulsing glow on hover signals interactivity. Drag-over state is unmistakable. Large folder emoji provides visual anchor in empty state.

---

## 6. Responsive & Container Issues

### 🟢 Issue #21: Container Max-Width Too Wide
**Location**: `.container` wrapper
**Problem**: On ultra-wide screens (>1600px), content stretches excessively, making scanning difficult. No center constraint.

**Current Code** (app.css:215-224):
```css
.container {
  max-width: 1600px; /* Too wide */
  width: 100%;
  margin: 0 auto;
  padding: var(--space-md) var(--space-xl);
  /* ... */
}
```

**Fix**:
```css
.container {
  max-width: 1400px; /* Reduce from 1600px */
  width: 100%;
  margin: 0 auto;
  padding: var(--space-lg) var(--space-2xl); /* Increase padding on large screens */
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl); /* Increase from --space-lg */
  min-height: 100vh;
}

/* Responsive padding */
@media (max-width: 1200px) {
  .container {
    padding: var(--space-md) var(--space-xl);
    gap: var(--space-xl);
  }
}

@media (max-width: 768px) {
  .container {
    padding: var(--space-sm) var(--space-md);
    gap: var(--space-lg);
  }
}
```

**Rationale**: 1400px max-width is more readable. Larger screens get more padding for comfortable viewing. Responsive scaling for tablets/mobile.

---

### 🟢 Issue #22: Header Sticky Positioning Issues
**Location**: `header` element with sticky positioning
**Problem**: `top: var(--gap-5)` creates awkward gap when scrolling. On mobile, sticky header takes up too much space.

**Current Code** (app.css:226-237):
```css
header {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--gap-4);
  box-shadow: var(--shadow);
  position: sticky;
  top: var(--gap-5); /* 24px gap at top */
  z-index: 10;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
```

**Fix**:
```css
header {
  background: rgba(22, 27, 34, 0.95); /* Semi-transparent for blur effect */
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-md) var(--space-lg); /* More balanced padding */
  box-shadow:
    0 4px 16px rgba(0, 0, 0, 0.3),
    0 1px 0 rgba(255, 255, 255, 0.05) inset; /* Inner highlight */
  position: sticky;
  top: var(--space-md); /* Reduce from 24px to 16px */
  z-index: 100; /* Increase from 10 */
  -webkit-backdrop-filter: blur(12px) saturate(180%); /* Stronger blur */
  backdrop-filter: blur(12px) saturate(180%);
  transition: all 0.3s ease;
}

/* Add scroll shadow when scrolled */
header.scrolled {
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.5),
    0 0 48px rgba(88, 166, 255, 0.15);
  border-color: rgba(88, 166, 255, 0.3);
}

/* Mobile: remove gap and make header flush */
@media (max-width: 768px) {
  header {
    top: 0;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg); /* Only bottom corners */
    padding: var(--space-sm) var(--space-md);
  }
}
```

**Enhancement in JS** (app.js or enhancements.js):
```javascript
// Add scroll detection for header shadow
const header = document.querySelector('header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }

  lastScroll = currentScroll;
});
```

**Rationale**: Reduced top gap (16px vs 24px) saves space. Stronger blur creates depth. Scroll-triggered shadow provides visual feedback. Mobile optimization removes unnecessary spacing.

---

## 7. Empty States & Content

### 🟡 Issue #23: Weak Empty State in Logs
**Location**: `#logContainer` when empty
**Problem**: Empty log container is just blank dark space. No indication of what will appear or how to use it.

**Current Code**: No empty state styling

**Fix**:
```css
/* Empty state for log container */
#logContainer:empty::before {
  content: 'No logs yet. Activity will appear here when you connect and transfer files.';
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  color: var(--muted);
  font-size: var(--fs-sm);
  font-style: italic;
  text-align: center;
  padding: var(--space-xl);
  background:
    radial-gradient(circle at 50% 50%, rgba(88, 166, 255, 0.03) 0%, transparent 70%),
    var(--surface-alt);
  border-radius: var(--radius-md);
}

/* Add subtle animation */
#logContainer:empty::after {
  content: '📋';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -120%);
  font-size: 48px;
  opacity: 0.15;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(-50%, -120%);
  }
  50% {
    transform: translate(-50%, -130%);
  }
}
```

**Rationale**: Clear messaging tells users what to expect. Visual interest prevents "broken" feeling. Animation adds polish.

---

### 🟢 Issue #24: Stats Grid Empty State
**Location**: `#statsGrid` .stat elements showing "—"
**Problem**: Em dash ("—") doesn't clearly indicate "no data yet". Looks like a rendering bug.

**Current Code**: JavaScript sets `.value` to "—"

**Fix in CSS**:
```css
.stat .value:empty::before,
.stat .value:contains("—")::before {
  content: '0';
  opacity: 0.3;
  font-weight: var(--weight-normal);
}

/* Or use a more descriptive empty state */
.stat[data-empty="true"] .value::before {
  content: 'N/A';
  font-size: var(--fs-lg);
  font-weight: var(--weight-semibold);
  opacity: 0.4;
  font-family: -apple-system, sans-serif; /* Use system font for N/A */
}
```

**Fix in JS** (app.js):
```javascript
// Instead of setting to "—", add data attribute
function updateStat(id, value) {
  const elem = document.getElementById(id);
  if (!value || value === 0) {
    elem.setAttribute('data-empty', 'true');
    elem.textContent = '';
  } else {
    elem.removeAttribute('data-empty');
    elem.textContent = formatValue(value);
  }
}
```

**Rationale**: "0" or "N/A" is clearer than "—". Data attribute approach is more semantic and accessible.

---

## 8. Accessibility & Usability

### 🟡 Issue #25: Low Color Contrast on Labels
**Location**: Label text uses `var(--fg-secondary)` color
**Problem**: Color contrast ratio may not meet WCAG AA standards (4.5:1 for normal text).

**Current Code** (app.css:508-516):
```css
label {
  display: flex;
  flex-direction: column;
  gap: var(--gap-2);
  font-size: var(--fs-13);
  font-weight: 600;
  color: var(--fg-secondary); /* #c9d1d9 on dark bg */
  margin-bottom: var(--gap-2);
}
```

**Fix**:
```css
label,
.label-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  font-size: var(--fs-sm); /* 13px */
  font-weight: var(--weight-semibold); /* 600 */
  color: var(--fg); /* Use primary text color instead */
  margin-bottom: var(--space-xs);
  letter-spacing: 0.3px; /* Improve readability */
}

/* Secondary labels (hints, captions) can use muted color */
.hint,
.text-caption,
.file-sub {
  color: var(--muted);
  font-size: var(--fs-xs);
  font-weight: var(--weight-normal);
}

/* Ensure sufficient contrast in light mode too */
html.theme-light label,
html.theme-light .label-text {
  color: var(--text-primary); /* #24292f */
}
```

**Rationale**: Using primary text color (--fg) ensures WCAG AA compliance. Secondary text properly uses muted color. Letter-spacing improves readability at small sizes.

---

### 🟢 Issue #26: Focus Indicators Too Subtle
**Location**: Focus states on interactive elements
**Problem**: Default focus outline is thin and barely visible, making keyboard navigation difficult.

**Current Code** (app.css:591-595):
```css
button:focus-visible,
summary:focus-visible {
  outline: 2px solid var(--focus);
  outline-offset: 2px;
}
```

**Fix**:
```css
/* Global focus indicator */
*:focus-visible {
  outline: 3px solid var(--accent); /* Thicker, more visible */
  outline-offset: 3px; /* More spacing */
  border-radius: 4px; /* Rounded for polish */
}

/* Specific adjustments for buttons */
button:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 4px;
  box-shadow:
    0 0 0 6px rgba(88, 166, 255, 0.15), /* Glow ring */
    0 4px 16px rgba(88, 166, 255, 0.3);
}

/* Input fields - inner glow instead of offset outline */
input:focus-visible {
  outline: none;
  box-shadow:
    0 0 0 4px rgba(88, 166, 255, 0.2),
    0 0 0 1px var(--accent) inset,
    0 4px 16px rgba(88, 166, 255, 0.3);
}

/* Skip link for screen readers (should be visible on focus) */
.skip-link:focus {
  position: fixed;
  top: 10px;
  left: 10px;
  background: var(--accent);
  color: white;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  z-index: 10000;
  outline: 3px solid white;
  outline-offset: 2px;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  *:focus-visible {
    transition: none;
  }
}
```

**Rationale**: Thicker outline (3px) is more visible. Glow effect provides additional visual feedback. Inner glow on inputs looks polished while maintaining visibility. Skip links improve keyboard navigation.

---

## 9. Polish & Refinement

### 🟢 Issue #27: Inconsistent Shadow Depths
**Location**: Various shadow definitions
**Problem**: Too many shadow variations create visual noise. No clear hierarchy.

**Current Code** (app.css:43-48):
```css
--shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 12px 32px rgba(0, 0, 0, 0.6);
--shadow-large: 0 10px 40px rgba(0, 0, 0, 0.5); /* Redundant with shadow-lg */
--shadow-primary: 0 4px 16px rgba(31, 111, 235, 0.3);
```

**Fix**:
```css
:root {
  /* Shadow system - clear elevation hierarchy */
  --shadow-1: 0 1px 3px rgba(0, 0, 0, 0.2), 0 1px 2px rgba(0, 0, 0, 0.12); /* Subtle */
  --shadow-2: 0 3px 6px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.15); /* Low */
  --shadow-3: 0 6px 12px rgba(0, 0, 0, 0.4), 0 3px 6px rgba(0, 0, 0, 0.2); /* Medium - default */
  --shadow-4: 0 12px 24px rgba(0, 0, 0, 0.5), 0 6px 12px rgba(0, 0, 0, 0.25); /* High */
  --shadow-5: 0 24px 48px rgba(0, 0, 0, 0.6), 0 12px 24px rgba(0, 0, 0, 0.3); /* Hero */

  /* Colored shadows for emphasis */
  --shadow-accent: 0 4px 16px rgba(88, 166, 255, 0.3), 0 2px 8px rgba(88, 166, 255, 0.2);
  --shadow-success: 0 4px 16px rgba(63, 185, 80, 0.3), 0 2px 8px rgba(63, 185, 80, 0.2);
  --shadow-danger: 0 4px 16px rgba(248, 81, 73, 0.3), 0 2px 8px rgba(248, 81, 73, 0.2);
}

/* Application */
.stack,
.card {
  box-shadow: var(--shadow-3); /* Medium elevation */
}

header {
  box-shadow: var(--shadow-2); /* Lower than content */
}

button.primary {
  box-shadow: var(--shadow-accent);
}

button.primary:hover {
  box-shadow:
    var(--shadow-4), /* Depth */
    var(--shadow-accent); /* Accent glow */
}

.modal-card {
  box-shadow: var(--shadow-5); /* Highest elevation */
}

.stat:hover {
  box-shadow: var(--shadow-3), var(--shadow-accent);
}
```

**Rationale**: Five-level shadow system (1-5) creates clear depth hierarchy. Layered shadows (base + accent) create rich, dimensional effects. Consistent naming improves maintainability.

---

### 🟢 Issue #28: Missing Loading States
**Location**: Buttons and async operations
**Problem**: No visual feedback during loading/processing. Users don't know if their action was received.

**Current Code**: Limited loading spinner implementation

**Fix**:
```css
/* Loading spinner - already exists but improve */
.loading-spinner {
  display: inline-block;
  width: 20px; /* Increase from 16px */
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.2); /* Thicker */
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Button loading state - improve */
button.loading {
  position: relative;
  color: transparent;
  pointer-events: none;
  cursor: wait;
}

button.loading::before {
  content: '';
  position: absolute;
  inset: 0;
  background: inherit;
  border-radius: inherit;
  opacity: 0.8;
}

button.loading .loading-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: inline-block;
}

/* Add loading state for other elements */
.stat.loading .value {
  position: relative;
  color: transparent;
}

.stat.loading .value::after {
  content: '';
  position: absolute;
  inset: 25% 35%;
  border: 3px solid var(--accent);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Skeleton loading for file card */
.file-card.loading {
  pointer-events: none;
}

.file-card.loading .file-icon,
.file-card.loading .file-name,
.file-card.loading .file-sub {
  background: linear-gradient(
    90deg,
    var(--surface-alt) 0%,
    var(--surface-hover) 50%,
    var(--surface-alt) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
  color: transparent;
}

@keyframes skeleton-pulse {
  0%, 100% {
    background-position: 200% 0;
  }
  50% {
    background-position: 0 0;
  }
}
```

**Rationale**: Prominent spinners (20px) are easier to see. Skeleton loading provides context about what's loading. Disabled interactions prevent double-clicks.

---

### 🟡 Issue #29: Stats Cards Lack Visual Interest
**Location**: `.stat` cards in stats grid
**Problem**: Stats are functional but bland. No visual hierarchy between label and value. All cards look identical.

**Current Code** (app.css:1050-1120):
```css
.stat {
  background: linear-gradient(135deg, rgba(88, 166, 255, 0.06) 0%, transparent 100%), var(--surface-alt);
  border: 1px solid rgba(148, 163, 184, 0.2);
  /* ... */
  min-height: 96px;
}

.stat .label {
  font-size: var(--fs-11);
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 2.5px; /* Too wide */
  font-weight: 800;
}

.stat .value {
  font-weight: var(--weight-black);
  font-size: var(--fs-36);
  /* ... */
}
```

**Fix**:
```css
.stat {
  background:
    linear-gradient(135deg, rgba(88, 166, 255, 0.08) 0%, rgba(34, 211, 238, 0.04) 100%),
    var(--surface);
  border: 2px solid rgba(88, 166, 255, 0.2); /* Thicker border */
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 110px; /* Increase from 96px */
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--space-sm);
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05); /* Inner highlight */
}

/* Colored accent bar at top */
.stat::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent) 0%, var(--accent-400) 100%);
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.stat:hover::before {
  opacity: 1;
  box-shadow: 0 0 16px var(--accent);
}

/* Stat-specific colors */
.stat:nth-child(1)::before {
  background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%); /* Blue */
}

.stat:nth-child(2)::before {
  background: linear-gradient(90deg, #a78bfa 0%, #8b5cf6 100%); /* Purple */
}

.stat:nth-child(3)::before {
  background: linear-gradient(90deg, #22d3ee 0%, #06b6d4 100%); /* Cyan */
}

.stat:nth-child(4)::before {
  background: linear-gradient(90deg, #ec4899 0%, #db2777 100%); /* Pink */
}

.stat .label {
  font-size: var(--fs-xs); /* 11px */
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1.5px; /* Reduce from 2.5px */
  font-weight: var(--weight-bold); /* 700 instead of 800 */
  margin-bottom: 0;
  opacity: 0.8;
}

.stat .value {
  font-weight: var(--weight-black); /* 900 */
  font-size: clamp(28px, 3vw, 40px); /* Responsive size */
  color: var(--fg);
  letter-spacing: -1.5px;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  font-family: ui-monospace, 'SF Mono', 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, monospace;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); /* Add depth */
}

/* Hover effect */
.stat:hover {
  border-color: rgba(88, 166, 255, 0.4);
  background:
    linear-gradient(135deg, rgba(88, 166, 255, 0.12) 0%, rgba(34, 211, 238, 0.06) 100%),
    var(--surface);
  transform: translateY(-4px) scale(1.02);
  box-shadow:
    0 8px 28px rgba(88, 166, 255, 0.35),
    0 0 40px rgba(88, 166, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.stat:hover .value {
  transform: scale(1.05);
  text-shadow: 0 2px 8px rgba(88, 166, 255, 0.4);
}
```

**Rationale**: Colored accent bars create visual differentiation. Inner highlights and text shadows add depth. Responsive value sizing works on all screens. Hover effects make stats feel interactive.

---

### 🟢 Issue #30: Transition Timing Inconsistencies
**Location**: Various transition durations throughout CSS
**Problem**: Some elements use 0.2s, others 0.3s, some 0.4s. No systematic approach to motion.

**Current Code**: Mixed transition timings

**Fix**:
```css
:root {
  /* Motion system - consistent easing and duration */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1); /* Quick feedback */
  --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1); /* Default */
  --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1); /* Deliberate */
  --transition-enter: 300ms cubic-bezier(0, 0, 0.2, 1); /* Entrances */
  --transition-exit: 200ms cubic-bezier(0.4, 0, 1, 1); /* Exits */

  /* Easing curves */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1); /* Standard */
  --ease-in: cubic-bezier(0.4, 0, 1, 1); /* Deceleration */
  --ease-out: cubic-bezier(0, 0, 0.2, 1); /* Acceleration */
  --ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Bounce */
}

/* Application */
button,
.interactive {
  transition: all var(--transition-base);
}

button:hover {
  transition: all var(--transition-fast); /* Quick response */
}

.modal,
dialog {
  animation-duration: var(--transition-enter);
  animation-timing-function: var(--ease-out);
}

.modal.closing,
dialog.closing {
  animation-duration: var(--transition-exit);
  animation-timing-function: var(--ease-in);
}

.toast {
  transition:
    opacity var(--transition-base),
    transform var(--transition-base) var(--ease-default);
}

.stat,
.card {
  transition: all var(--transition-base);
}

.stat:hover,
.card:hover {
  transition: all var(--transition-fast); /* Snappy hover */
}

/* Disable motion for accessibility */
@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-fast: 10ms;
    --transition-base: 10ms;
    --transition-slow: 10ms;
    --transition-enter: 10ms;
    --transition-exit: 10ms;
  }

  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Rationale**: Systematic timing creates rhythm. Fast (150ms) for immediate feedback, base (250ms) for most interactions, slow (400ms) for deliberate motions. Separate enter/exit timings feel natural. Accessibility override respects user preferences.

---

### 🟢 Issue #31: Log Container Scrollbar Styling
**Location**: `#logContainer` custom scrollbar
**Problem**: Scrollbar is functional but doesn't match app aesthetic. Too thin on some browsers.

**Current Code** (app.css:1229-1246):
```css
#logContainer::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

#logContainer::-webkit-scrollbar-track {
  background: var(--surface-alt);
  border-radius: var(--radius-sm);
}

#logContainer::-webkit-scrollbar-thumb {
  background: var(--border-hover);
  border-radius: var(--radius-sm);
}

#logContainer::-webkit-scrollbar-thumb:hover {
  background: var(--focus);
}
```

**Fix**:
```css
/* Modern scrollbar styling */
#logContainer {
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: var(--accent) var(--surface-alt);
}

/* Webkit browsers (Chrome, Safari, Edge) */
#logContainer::-webkit-scrollbar {
  width: 10px; /* Increase from 8px */
  height: 10px;
}

#logContainer::-webkit-scrollbar-track {
  background: var(--surface-alt);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}

#logContainer::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg,
    rgba(88, 166, 255, 0.6) 0%,
    rgba(88, 166, 255, 0.4) 100%
  );
  border-radius: var(--radius-md);
  border: 2px solid var(--surface-alt); /* Creates padding effect */
  transition: background 0.2s ease;
}

#logContainer::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg,
    var(--accent) 0%,
    rgba(88, 166, 255, 0.8) 100%
  );
  box-shadow:
    0 0 8px rgba(88, 166, 255, 0.5),
    inset 0 0 4px rgba(255, 255, 255, 0.2);
}

#logContainer::-webkit-scrollbar-thumb:active {
  background: var(--accent);
}

/* Corner where scrollbars meet */
#logContainer::-webkit-scrollbar-corner {
  background: var(--surface-alt);
}
```

**Rationale**: Wider scrollbar (10px) is easier to grab. Gradient and glow effects match app aesthetic. Border creates padding for cleaner look. Firefox fallback ensures consistency.

---

### 🟡 Issue #32: Percentage Display Typography
**Location**: `.kpi .pct` element showing progress percentage
**Problem**: Font size is responsive (`clamp(80px, 11vw, 104px)`) but can become too small on narrow screens. Letter-spacing is too tight at large sizes.

**Current Code** (app.css:934-946):
```css
.kpi .pct {
  font-size: clamp(80px, 11vw, 104px);
  font-weight: var(--weight-black);
  background: linear-gradient(135deg, #22d3ee 0%, #58a6ff 35%, #a78bfa 70%, #ec4899 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -4px; /* Too tight */
  line-height: 1;
  font-variant-numeric: tabular-nums;
  filter: drop-shadow(0 2px 20px rgba(88, 166, 255, 0.45)) drop-shadow(0 0 40px rgba(34, 211, 238, 0.25));
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Fix**:
```css
.kpi .pct {
  font-size: clamp(72px, 10vw, 96px); /* Reduce max size from 104px to 96px */
  font-weight: var(--weight-black); /* 900 */
  background: linear-gradient(135deg,
    #22d3ee 0%,
    #58a6ff 35%,
    #a78bfa 70%,
    #ec4899 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em; /* More balanced than -4px */
  line-height: 0.9;
  font-variant-numeric: tabular-nums;
  filter:
    drop-shadow(0 4px 24px rgba(88, 166, 255, 0.5))
    drop-shadow(0 0 48px rgba(34, 211, 238, 0.3));
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: gradient-shift 8s ease-in-out infinite; /* Subtle animation */
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

/* Update animation when value changes */
.kpi .pct.updating {
  animation:
    pct-bounce 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55),
    gradient-shift 8s ease-in-out infinite;
}

@keyframes pct-bounce {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
  }
}

/* ETA text below percentage */
.kpi .eta {
  color: var(--muted);
  font-size: var(--fs-sm); /* Increase from 13px to match system */
  font-weight: var(--weight-medium); /* 500 */
  margin-top: var(--space-sm);
  letter-spacing: 0.5px;
}

.kpi .eta span {
  font-weight: var(--weight-semibold); /* 600 - emphasize time value */
  color: var(--fg-secondary);
  font-variant-numeric: tabular-nums;
}
```

**Rationale**: Smaller max size (96px) prevents overwhelming the layout. Em-based letter-spacing scales with font size. Gradient animation adds visual interest without distraction. Bounce animation on update provides feedback.

---

## Summary of Issues

| Category          | Critical (🔴) | High (🟡) | Medium (🟢) | Total  |
|-------------------|---------------|-----------|-------------|--------|
| Layout & Grid     | 3             | 2         | 1           | 6      |
| Typography        | 1             | 2         | 0           | 3      |
| Component Spacing | 1             | 4         | 2           | 7      |
| Visual Hierarchy  | 1             | 2         | 1           | 4      |
| Interaction       | 0             | 2         | 0           | 2      |
| Responsive        | 0             | 0         | 2           | 2      |
| Empty States      | 0             | 1         | 1           | 2      |
| Accessibility     | 0             | 1         | 1           | 2      |
| Polish            | 0             | 2         | 2           | 4      |
| **TOTAL**         | **6**         | **16**    | **10**      | **32** |

---

## Actionable Fix Plan

### Phase 1: Critical Fixes (Impact: High, Effort: Medium) - Priority 1
**Goal**: Fix major layout imbalances and component visibility issues
**Time Estimate**: 3-4 hours

1. **Fix Grid Layout Balance** (Issue #1)
   - Update `main` grid columns to `minmax(420px, 480px) minmax(600px, 1fr)`
   - Add max-width: 1400px
   - Test on various screen sizes

2. **Resize Progress Ring** (Issue #4)
   - Change `--ring-size` to `clamp(240px, 28vw, 300px)`
   - Reduce `--ring-max` to 300px
   - Adjust `.center` container padding

3. **Improve Primary Button Prominence** (Issue #15)
   - Increase button size to 56px height
   - Add uppercase text-transform
   - Strengthen box-shadow
   - Make secondary buttons more subdued

4. **Enhance Status Badges** (Issue #16)
   - Increase border to 2px
   - Add gradient backgrounds
   - Implement pulse animations
   - Improve color vibrancy

5. **Redesign File Drop Zone** (Issue #20)
   - Increase border thickness to 3px
   - Add radial gradient background
   - Implement pulsing hover animation
   - Add large folder emoji in empty state

6. **Fix Filter Button Group** (Issue #13)
   - Convert to segmented control design
   - Remove gaps, use background container
   - Add subtle separators
   - Strengthen active state

**Validation**: Test all critical fixes together, ensure no regressions

---

### Phase 2: High-Impact Spacing & Typography (Impact: Medium-High, Effort: Low-Medium) - Priority 2
**Goal**: Improve readability, visual rhythm, and spacing consistency
**Time Estimate**: 2-3 hours

1. **Standardize Section Padding** (Issue #2)
   - Apply different padding to Configuration vs Status panels
   - Ensure consistent spacing throughout

2. **Improve Typography Scale** (Issue #7)
   - Replace incremental font sizes with clear scale
   - Increase base font to 15px
   - Update all text elements

3. **Fix Section Headers** (Issue #6)
   - Unify header styling across all sections
   - Remove gradient underline, use full-width border
   - Increase margin-bottom

4. **Enhance File Card Layout** (Issue #10)
   - Increase icon size to 72px
   - Add more gap spacing (24px)
   - Add minimum height

5. **Improve Action Button Spacing** (Issue #11)
   - Increase margins around .actions container
   - Add spacing after primary button

6. **Redesign Toolbar** (Issue #12)
   - Convert to CSS Grid layout
   - Ensure perfect alignment
   - Add background container

7. **Fix Autoscroll Alignment** (Issue #14)
   - Use inline-flex with align-items: center
   - Add padding and hover state

**Validation**: Review all text sizes and spacing on actual content

---

### Phase 3: Visual Refinement & Polish (Impact: Medium, Effort: Low) - Priority 3
**Goal**: Add polish, improve empty states, enhance micro-interactions
**Time Estimate**: 2-3 hours

1. **Standardize Border Radius** (Issue #18)
   - Update radius scale (4px → 6px → 10px → 14px → 18px → 24px)
   - Apply consistently across all elements
   - Ensure nested elements use smaller radii

2. **Implement Shadow System** (Issue #27)
   - Replace all shadow definitions with 5-level system
   - Add colored accent shadows
   - Apply layered shadows

3. **Enhance Hover States** (Issue #19)
   - Increase lift amount to 3px
   - Add glow effects
   - Improve scale animations

4. **Add Loading States** (Issue #28)
   - Improve spinner visibility (20px)
   - Add skeleton loading to file card
   - Implement stat loading state

5. **Improve Stats Cards** (Issue #29)
   - Add colored accent bars
   - Implement stat-specific colors
   - Add text shadows for depth

6. **Enhance Log Container** (Issue #23, #31)
   - Add empty state message and icon
   - Improve scrollbar styling with gradient
   - Make wider (10px)

7. **Fix Percentage Display** (Issue #32)
   - Adjust letter-spacing to -0.02em
   - Add gradient shift animation
   - Implement bounce on update

**Validation**: Test all interactions and animations

---

### Phase 4: Accessibility & Responsive (Impact: Medium, Effort: Low-Medium) - Priority 4
**Goal**: Ensure WCAG compliance and mobile optimization
**Time Estimate**: 2 hours

1. **Improve Color Contrast** (Issue #25)
   - Use `--fg` for labels instead of `--fg-secondary`
   - Test contrast ratios
   - Validate in both themes

2. **Enhance Focus Indicators** (Issue #26)
   - Increase outline to 3px
   - Add glow rings on buttons
   - Implement skip links

3. **Optimize Container Width** (Issue #21)
   - Reduce max-width to 1400px
   - Add responsive padding
   - Test on various screen sizes

4. **Fix Sticky Header** (Issue #22)
   - Reduce top gap to 16px
   - Add scroll detection
   - Mobile optimization (flush to top)

5. **Standardize Motion Timing** (Issue #30)
   - Implement transition system (fast/base/slow)
   - Apply consistently
   - Add reduced-motion override

**Validation**: Full accessibility audit with screen reader, keyboard-only navigation, contrast checker

---

### Phase 5: Component-Specific Refinements (Impact: Low-Medium, Effort: Low) - Priority 5
**Goal**: Fine-tune individual components
**Time Estimate**: 1-2 hours

1. **Improve Progress Ring Container** (Issue #3)
   - Remove flex: 1
   - Adjust padding and min-height
   - Add max-height constraint

2. **Optimize Stats Grid** (Issue #5)
   - Constrain card width (120-180px)
   - Center grid with justify-content
   - Add top margin

3. **Fix File Drop Zone Buttons** (Issue #9)
   - Increase gap to 24px
   - Make "Choose File" more prominent
   - Subdued "Recent" button

4. **Improve Text Contrast** (Issue #8)
   - Implement placeholder state for file name
   - Use muted color and italic style
   - Bold actual filename

5. **Fix Empty Stats** (Issue #24)
   - Replace "—" with "N/A" or "0"
   - Use data attribute approach
   - Improve JavaScript

6. **Enhance Idle Progress Ring** (Issue #17)
   - Reduce grayscale to 0.3
   - Increase opacity to 0.6
   - Add breathing animation

**Validation**: Review each component in isolation and in context

---

## Implementation Notes

### Code Organization
- Create backup of `styles/app.css` before making changes
- Consider breaking CSS into logical sections with clear comments
- Test each phase independently before moving to next

### Browser Testing
- Chrome/Edge (Chromium)
- Firefox
- Safari (if possible)
- Test on actual mobile devices, not just devtools

### Performance Considerations
- Monitor CSS file size (should stay under 150KB)
- Minimize use of expensive properties (filter, backdrop-filter)
- Test animations on lower-end devices

### Accessibility Validation
- Use axe DevTools or WAVE for automated checks
- Manual keyboard navigation testing
- Screen reader testing (NVDA, JAWS, or VoiceOver)
- Color contrast validation with tools like Contrast Checker

### Version Control
- Commit after each phase
- Use descriptive commit messages: "Phase 1: Fix critical layout and visibility issues"
- Tag final version: `git tag design-refinement-v1.0`

---

## Tools & Resources

**Design Testing**:
- Chrome DevTools - Inspect layouts, test responsive
- Firefox DevTools - Grid inspector, accessibility panel
- Polypane - Multi-viewport testing

**Accessibility**:
- axe DevTools - Automated accessibility testing
- WAVE - Web accessibility evaluation tool
- Contrast Checker - Color contrast validation
- NVDA / JAWS - Screen reader testing

**Performance**:
- Lighthouse - Performance audit
- Chrome DevTools Performance panel
- CSS Stats - CSS analysis tool

**Code Quality**:
- CSS Validator - W3C CSS validation
- Prettier - Code formatting
- Can I Use - Browser compatibility

---

## Expected Outcomes

After implementing all fixes:

1. **Visual Hierarchy**: Clear distinction between primary actions, sections, and content
2. **Balanced Layout**: Harmonious proportions between Configuration and Status panels
3. **Professional Polish**: Consistent spacing, shadows, borders, and transitions
4. **Excellent Usability**: Clear hover states, strong focus indicators, intuitive interactions
5. **Accessibility**: WCAG AA compliant, keyboard navigable, screen reader friendly
6. **Responsive**: Works beautifully from 320px mobile to 4K displays
7. **Performance**: Smooth animations, no jank, fast load times
8. **Maintainability**: Systematic design tokens, consistent patterns, well-documented

The GUI will feel professional, polished, and purpose-built rather than generic or rushed.

---

**Document Version**: 1.0
**Author**: Frontend Design Analysis
**Next Review**: After Phase 3 completion