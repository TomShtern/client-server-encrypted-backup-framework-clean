# Client GUI - Files Inventory

**Updated:** November 17, 2025 | **Total Files:** 27 | **Active Code:** ~225 KB | **Metadata:** Comprehensive scanning completed

---

## ✅ ACTIVE FILES (In Use)

### 📄 HTML Entry Point (1 file)

| File | Size | Modified |
|------|------|----------|
| NewGUIforClient.html | 17.7 KB | Nov 16 04:51 |

#### NewGUIforClient.html
**Main application entry point (CANONICAL)**

Pure vanilla ES6 single-page application that loads CSS from `styles/app.css` and JavaScript from `scripts/app.js`. Includes all required DOM elements: status display, file input, progress indicators, connection metrics, logs panel, theme toggle.

**How It Works:**
- Integrates with CyberBackup API server via HTTP/WebSocket for encrypted file transfer
- Real-time progress tracking with Material Design-inspired UI
- Dark/light theme support with ARIA accessibility
- Responsive layout supporting desktop and mobile

**Metadata:** 17690 bytes; created Nov 16 04:51; last accessed Nov 17 18:03

---

### 🎨 Stylesheets (2 files)

| File                    | Size    | Modified     |
|-------------------------|---------|--------------|
| styles/app.css          | 34.1 KB | Nov 17 08:48 |
| styles/enhancements.css | 17.9 KB | Nov 17 08:30 |

#### styles/app.css
**Master design system & unified stylesheet (SINGLE SOURCE OF TRUTH)**

Implements complete Material Design 3 theme with CSS custom properties for colors, spacing (8px–64px scale), typography (11px–74px scale), shadows (5-level hierarchy), and animations.

**What It Contains:**
- Base styles and 100+ component styles (header, forms, buttons, file cards, status badges, progress ring, logs)
- Responsive breakpoints (1200px/768px)
- Motion design with cubic-bezier easing
- 11 keyframe animations (slideDown, pulse, fadeInUp, etc.)
- Theme variables, sticky headers with glassmorphic blur
- Input floating labels with validation icons
- Button gradients with ripple effects
- File drop zones with drag-over states
- Progress rings with animated gradient text
- Stats grids with staggered animations

**Metadata:** 34907 bytes; created Nov 17 06:39; last modified Nov 17 08:48

---

#### styles/enhancements.css
**Layout refinement & activity logs UI (precise spacing overrides)**

Uses `!important` overrides to achieve pixel-perfect alignment for the two-column desktop grid layout.

**What It Customizes:**
- Two-column grid: fixed 400px left sidebar + flexible right column
- Activity logs toolbar with three-column grid (search 2fr + filters auto + controls max-content)
- Search input with magnifying glass icon
- Filter pills with semantic color-coding (blue/orange/red)
- 34px height controls with custom webkit scrollbar styling (8px, rounded)
- Header padding reduced by 66%
- Drop zone height matched to status panel (437px)
- Compressed section margins
- Responsive fallbacks at 1024px and 640px breakpoints

**Metadata:** 18286 bytes; created Nov 17 08:20; last modified Nov 17 08:30

---

### 📦 JavaScript Modules (16 files, ~120 KB)

#### Root Level Scripts (3 files)

| File                        | Size    | Modified     |
|-----------------------------|---------|--------------|
| scripts/app.js              | 42.3 KB | Nov 15 13:35 |
| scripts/enhancements.js     | 35.6 KB | Nov 15 23:39 |
| scripts/validate-modules.js | 5.9 KB  | Nov 08 15:03 |

##### scripts/app.js
**Main application orchestrator (CORE CONTROLLER)**

Application class managing all subsystems: API client, state store, socket.io, UI managers. Handles complete lifecycle from connection establishment through cleanup.

**Core Responsibilities:**
- Connection establishment → file selection → backup execution → progress monitoring → cleanup
- Error boundaries with user-friendly messages
- Dual polling loops: general status (12s) + job status (2.5s) + WebSocket instant updates
- RAF-batched rendering with change detection (only re-renders changed sections)
- Custom error recovery and focus trap for modals
- Keyboard shortcuts (Ctrl+K, Ctrl+U)
- Performance optimization throughout

**Metadata:** 42327 bytes; created Nov 14 20:33; last modified Nov 15 13:35

---

##### scripts/enhancements.js
**Professional UI polish & interactive features**

Provides visual enhancements beyond core functionality with animations, validation, and advanced interactions.

**Features:**
- Sidebar collapsibility, hover effects, button ripple effects
- Progress ring animations
- Input validation (server address IP:PORT, username) with real-time visual feedback
- File type icons with badges, floating labels
- Drag-and-drop preview with metadata
- Canvas-based speed chart showing real-time transfer rates
- Light/dark theme toggle with smooth animations
- Log filtering/search with debouncing and export
- Background animated particles (responsive sizing)
- Auto-initializes on DOM ready

**Metadata:** 35583 bytes; created Nov 15 01:37; last modified Nov 15 23:39

---

##### scripts/validate-modules.js
**Development utility for module validation**

Recursively scans project for `.js` files and validates all ES6 modules for dependency integrity.

**What It Checks:**
- Validates ES6 import/export syntax correctness
- Checks all imports resolve to actual files
- Verifies external CDN dependencies exist in package.json
- Reports detailed error/warning summary with file paths

**Metadata:** 5884 bytes; created Nov 08 15:03; modified Nov 08 15:03

---

#### Services Layer (8 files)

| File                                   | Size    | Modified     |
|----------------------------------------|---------|--------------|
| scripts/services/api-client.js         | 3.97 KB | Nov 08 02:15 |
| scripts/services/socket-client.js      | 3.38 KB | Nov 08 21:24 |
| scripts/services/connection-monitor.js | 3.02 KB | Nov 08 21:24 |
| scripts/services/file-manager.js       | 5.27 KB | Nov 16 02:42 |
| scripts/services/advanced-settings.js  | 3.81 KB | Nov 08 01:02 |
| scripts/services/theme-manager.js      | 1.35 KB | Nov 08 15:34 |
| scripts/services/log-store.js          | 2.09 KB | Nov 08 02:15 |
| scripts/services/connection-metrics.js | 680 B   | Nov 08 00:05 |

##### scripts/services/api-client.js
**HTTP REST client (API communication layer)**

Timeout-protected (20s default) request wrapper with normalized response handling.

**API Methods:**
- `healthCheck()` – Verifies server connectivity
- `connect()` – POST /api/connect with validation
- `startBackup()` – FormData file upload to /api/start_backup
- `getStatus()` – Polls /api/status for progress
- Control commands: pause, resume, stop
- Comprehensive error handling with descriptive messages

**Metadata:** 3972 bytes; created Nov 07 23:58; last modified Nov 08 02:15

---

##### scripts/services/socket-client.js
**WebSocket real-time client (Socket.IO wrapper)**

Manages real-time communication for progress updates and status notifications.

**Capabilities:**
- Lazy-loads Socket.IO from CDN
- Auto-reconnection (8s max delay)
- Handles events: connect, disconnect, status, progress, file_receipt
- Tracks current job ID and requests status on reconnect
- Real-time progress streaming with phase/byte info
- Server confirmations of file receipt/verification

**Metadata:** 3384 bytes; created Nov 08 00:43; last modified Nov 08 21:24

---

##### scripts/services/connection-monitor.js
**Background health checker (periodic ping service)**

Executes configurable interval health checks without blocking the UI.

**How It Works:**
- Configurable ping intervals (7s default)
- Prevents duplicate in-flight requests
- Measures latency via `performance.now()`
- Handles multi-format responses (backup_server/api_server/status fields)
- Evaluates connection quality: excellent <80ms | good <150ms | fair <300ms | poor >300ms
- Extracts optional system metrics (CPU, memory)
- Callback pattern for state updates
- Supports manual `forcePing()`

**Metadata:** 3023 bytes; created Nov 08 16:56; last modified Nov 08 21:24

---

##### scripts/services/file-manager.js
**File selection & recent files manager (drag-drop enabled)**

Manages file selection, validation, and recent file tracking with localStorage persistence.

**Features:**
- Handles file input changes and drag-drop events
- Stores up to 5 recent files with metadata (name, size, type, modified)
- Updates filename/size/type display with animation
- Validates dropped files and prevents default behavior
- Provides screen reader announcements
- Clear functionality with accessibility updates

**Metadata:** 5268 bytes; created Nov 09 13:20; last modified Nov 16 02:42

---

##### scripts/services/advanced-settings.js
**User settings manager (localStorage persistence)**

Persists configurable backup parameters with validation and fallback defaults.

**Manages:**
- Chunk size (1–256 MB) with clamping
- Retry limit (0–20 attempts)
- Safe numeric parsing and validation
- Reset to defaults with toast notification
- Loads saved settings on init with fallback
- Listens for blur events to validate/persist
- Aria-invalid feedback for invalid inputs

**Metadata:** 3809 bytes; created Nov 08 00:42; last modified Nov 08 01:02

---

##### scripts/services/theme-manager.js
**Theme switcher (light/dark mode persistence)**

Manages application theme switching with localStorage persistence.

**Functionality:**
- Toggles CSS classes on document root (theme-dark/theme-light)
- Saves preference to localStorage for cross-session retention
- Updates toggle button text and aria-label dynamically
- Loads saved theme on init with dark mode fallback

**Metadata:** 1346 bytes; created Nov 08 15:34; modified Nov 08 15:34

---

##### scripts/services/log-store.js
**In-memory event log manager (filtering & export)**

Manages application event logs with filtering, rendering, and export capabilities.

**Features:**
- Circular buffer of log entries (max 500) with timestamp/level/phase
- Normalizes levels (info/warn/error)
- Filters logs by level (all, info, warn, error)
- Auto-scroll to latest entries during active operations
- Efficient rendering to DOM with data attributes
- Plain text export with ISO timestamps

**Metadata:** 2094 bytes; created Nov 07 23:58; last modified Nov 08 02:15

---

##### scripts/services/connection-metrics.js
**Connection quality evaluator (latency assessment)**

Utility for evaluating connection quality based on latency measurements.

**Evaluation:**
- Maps latency thresholds to quality levels
- Incorporates optional success rate for nuanced assessment
- Returns human-readable quality descriptions with visual indicators (● bullets)

**Metadata:** 680 bytes; created Nov 08 00:00; modified Nov 08 00:05

---

#### State Management (1 file)

| File                                   | Size    | Modified     |
|----------------------------------------|---------|--------------|
| scripts/state/state-store.js           | 3.07 KB | Nov 08 15:24 |

##### scripts/state/state-store.js
**Reactive state store (batching & diffing)**

Minimal reactive state management with efficient batching and shallow diffing.

**How It Works:**
- Snapshot pattern with read-only state preventing mutations
- Queues updates using RAF for efficient batching
- Shallow equality diffing (top-level only)
- Multiple subscriber support with unsubscribe functions
- Immediate updates bypass batching for urgent changes
- Mutation method for complex state transformations
- Microtask notifications for consistency
- Error handling with logging to prevent cascading failures

**Metadata:** 3069 bytes; created Nov 08 15:24; modified Nov 08 15:24

---

#### UI Layer (2 files)

| File                                   | Size    | Modified     |
|----------------------------------------|---------|--------------|
| scripts/ui/accessibility.js            | 841 B   | Nov 08 02:15 |
| scripts/ui/toasts.js                   | 1.19 KB | Nov 08 02:15 |

##### scripts/ui/accessibility.js
**Screen reader announcer (ARIA live region)**

Provides accessible announcements for screen reader users via ARIA live regions.

**Features:**
- Writes to ARIA live region for screen reader announcement
- Batches announcements into sequential queue
- Clears previous message before announcing new
- 120ms delay between announcements to prevent audio glitching
- Proper RAF/setTimeout timing for accessibility

**Metadata:** 841 bytes; created Nov 07 23:59; modified Nov 08 02:15

---

##### scripts/ui/toasts.js
**Toast notification system (auto-dismiss)**

Temporary user feedback messages with automatic dismissal and accessibility.

**Features:**
- Creates elements with role="status" and aria-live="polite"
- Supports types: info, warn, error, success
- Auto-dismisses after 4s (configurable)
- Returns cleanup function for programmatic dismissal
- CSS transitions with fallback setTimeout
- Prevents memory leaks
- Clear all method for batch dismissal

**Metadata:** 1186 bytes; created Nov 07 23:57; modified Nov 08 02:15

---

#### Utilities (3 files)

| File                                   | Size    | Modified     |
|----------------------------------------|---------|--------------|
| scripts/utils/dom.js                   | 5.44 KB | Nov 15 05:11 |
| scripts/utils/formatters.js            | 3.27 KB | Nov 08 19:07 |
| scripts/utils/performance-optimizer.js | 7.02 KB | Nov 14 20:32 |

##### scripts/utils/dom.js
**DOM element cache & safe operations (centralized selectors)**

Centralized DOM element cache and utility functions for safe DOM operations.

**Utilities Provided:**
- Element cache with getter functions (throws on missing elements)
- `safeExecute()` wrapper for error suppression and logging
- Visibility detection (offsetWidth/offsetHeight > 0, not hidden)
- `addCleanupListener()` adds listeners and returns removal function
- Debounce implementation for high-frequency handlers
- Throttle implementation for frequency limiting
- Safe querySelector utilities

**Metadata:** 5435 bytes; created Nov 15 02:42; last modified Nov 15 05:11

---

##### scripts/utils/formatters.js
**Display formatting utilities (human-readable values)**

Formatting utilities for displaying human-readable values throughout the app.

**Formatters:**
- **Bytes:** KB/MB/GB/TB with smart precision (0-2 decimals)
- **Speed:** bytes-per-second using same unit system with "/s" suffix
- **Duration:** readable format (e.g., "2h 30m", "45s") with zero-padding
- **Latency:** milliseconds with "ms" suffix, fallback "—"
- **Percentage:** clamps values 0-100%
- **Server Address:** extracts host:port, defaults to 1256
- **Null Handling:** fallback "—" for invalid values

**Metadata:** 3266 bytes; created Nov 08 15:05; last modified Nov 08 19:07

---

##### scripts/utils/performance-optimizer.js
**Advanced performance tools (RAF batching & DOM optimization)**

Advanced performance optimization tools for smooth, efficient rendering.

**Tools Provided:**
- RAF batching for DOM updates in single animation frame
- RAF debounce/throttle with animation frame-based timing
- DOM batcher separating reads/writes to prevent layout recalculation
- Smooth counter animates numeric changes with easing
- Intersection Observer factory for lazy loading
- Performance measurement with console logging
- Exports global instances for app-wide use

**Metadata:** 7015 bytes; created Nov 14 20:32; modified Nov 14 20:32

---

### 📋 Configuration & Documentation (4 files)

| File               | Size    | Modified     |
|--------------------|---------|--------------|
| package.json       | 1.58 KB | Nov 08 15:15 |
| README.md          | 5.76 KB | Nov 14 23:03 |
| CLAUDE.md          | 16.1 KB | Nov 17 18:51 |
| FILES_INVENTORY.md | 3.43 KB | Nov 17 18:51 |

##### package.json
**NPM project configuration**

Project metadata, scripts, and dependencies for the CyberBackup web GUI.

**Configuration:**
- Project name: cyberbackup-web-gui, version 1.0.0
- Scripts: `npm run dev` (with CORS), `npm run validate`, `npm run check`
- Dependencies: socket.io-client v4.7.5
- Dev dependencies: http-server v14.1.1
- Node requirement: >=16.0.0
- ES6 module support enabled

**Metadata:** 1579 bytes; created Nov 08 15:15; modified Nov 08 15:15

---

##### README.md
**User-facing documentation**

Public documentation for users and developers getting started with the Client GUI.

**Contains:**
- Feature overview and quick-start guide
- Prerequisites and installation steps
- Project structure and npm scripts
- API integration points (HTTP/WebSocket)
- Troubleshooting section
- Browser support: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

**Metadata:** 5763 bytes; created Nov 08 15:04; last modified Nov 14 23:03

---

##### CLAUDE.md
**Developer guide for AI assistants**

Comprehensive architecture and development guide for Claude Code and AI agents.

**Covers:**
- System architecture overview and design patterns
- All JavaScript services documented with API contracts
- HTTP endpoints and WebSocket events
- DOM element requirements
- Lifecycle documentation
- Performance targets and common pitfalls
- Best practices for extension and modification

**Metadata:** 16122 bytes; created Nov 15 00:44; last modified Nov 17 18:51

---

##### FILES_INVENTORY.md
**Internal file manifest (this file)**

Comprehensive inventory of active vs archived files, architecture documentation, and organization guidelines.

**Sections:**
- Active files with detailed descriptions and metadata
- Archive documentation with deprecation notes
- Architecture principles and design patterns
- Maintenance guidelines (DO/DON'T rules)
- Common tasks and quick reference

**Metadata:** 3428 bytes; created Nov 15 03:19; last modified Nov 17 18:51

---

### 🛠️ Tooling & Assets (3 files)

| File                        | Size    | Modified     |
|-----------------------------|---------|--------------|
| start_client_gui.py         | 2.94 KB | Nov 09 14:54 |
| favicon.svg                 | 1.13 KB | Aug 15 20:55 |
| .claude/settings.local.json | 436 B   | Nov 15 01:15 |

##### start_client_gui.py
**One-click HTTP server launcher (Python)**

Python launcher script that starts the development HTTP server and automatically opens the browser.

**What It Does:**
- Finds a free port starting from 8080 using socket binding
- Creates custom SimpleHTTPRequestHandler:
  - Serves files from Client-gui directory
  - Sets MIME type `application/javascript` for `.js` files (required for ES6 modules)
  - Adds cache-control headers to prevent caching issues
  - Suppresses HTTP server logs for cleaner output
- Starts server on `localhost:port` in main thread
- Auto-opens browser to `http://localhost:port/NewGUIforClient.html` after 1s delay
- Handles Ctrl+C gracefully for shutdown

**Metadata:** 2937 bytes; created Nov 09 13:39; modified Nov 09 14:54

---

##### favicon.svg
**Browser tab icon (64×64 SVG)**

Lightweight SVG icon displayed in browser tabs, bookmarks, and address bar.

**Design:**
- Teal to cyan linear gradient as primary visual element
- 64×64 viewBox with scalable vector graphics
- Provides visual recognition in browser tabs and bookmarks
- No rasterization needed

**Metadata:** 1131 bytes; created Aug 15 20:54; modified Aug 15 20:55

---

##### .claude/settings.local.json
**Claude Code editor settings**

Local configuration for AI assistant development environment.

**Purpose:**
- Claude Code editor workspace settings
- Local preferences for development

**Metadata:** 436 bytes; created Nov 15 01:15; modified Nov 15 01:15

---

### 📊 Runtime Artifacts (1 file)

| File       | Size     | Modified     |
|------------|----------|--------------|
| appmap.log | 282.5 KB | Nov 17 08:00 |

##### appmap.log
**Activity log (debugging artifact)**

Timestamped records of application behavior, errors, state changes, and system events.

**Purpose:**
- Generated by the application logging system (`services/log-store.js`)
- Helps diagnose issues in development and production
- Provides historical record of application events
- Grows as the app runs; can be cleaned with `npm run clean`

**Metadata:** 282515 bytes; created Nov 09 13:33; last modified Nov 17 08:00

---

## 📊 STATISTICS

### Code Metrics
| Metric                      | Value                 | Details                                                         |
|-----------------------------|-----------------------|-----------------------------------------------------------------|
| **Total Active Files**      | 27                    | HTML(1) + CSS(2) + JS(16) + Config(4) + Tools(3) + Artifacts(1) |
| **Total Code Size**         | ~227 KB               | Excludes node_modules                                           |
| **JavaScript Modules**      | 16                    | Services(8) + Root(3) + State(1) + UI(2) + Utils(3)             |
| **Lines of Code (Approx.)** | ~5,500                | Average 350 LOC per JS file                                     |
| **Largest File**            | app.js                | 42.3 KB (main orchestrator)                                     |
| **Smallest File**           | connection-metrics.js | 680 B (utility)                                                 |
| **Last Modified**           | Nov 17 2025           | app.css (08:48), CLAUDE.md (18:51)                              |

### Dependency Tree
```
NewGUIforClient.html (entry)
├─ styles/app.css (master design system)
├─ styles/enhancements.css (layout refinements)
└─ scripts/app.js (main controller)
   ├─ services/api-client.js (HTTP REST)
   ├─ services/socket-client.js (WebSocket)
   ├─ services/connection-monitor.js (health checks)
   ├─ services/file-manager.js (file selection)
   ├─ services/advanced-settings.js (user config)
   ├─ services/theme-manager.js (light/dark)
   ├─ services/log-store.js (event logging)
   ├─ services/connection-metrics.js (quality eval)
   ├─ state/state-store.js (reactive state)
   ├─ ui/toasts.js (notifications)
   ├─ ui/accessibility.js (ARIA announcer)
   ├─ utils/dom.js (element cache)
   ├─ utils/formatters.js (display formatting)
   └─ utils/performance-optimizer.js (optimization)

scripts/enhancements.js (standalone)
└─ Provides: UI polish, animations, validation, charts
```

---

## 📦 ARCHIVED FILES (Not In Use)

**Location:** `archived/` folder

**Content (DO NOT USE):**
- **HTML:** wireframe_v4.html, enhanced-gui.html, standalone-gui.html, index.html, index-dev.html, file-type-demo.html
- **CSS (17 files):** All merged into `styles/app.css`
  - Animations, components, layouts, microinteractions, modern, optimized, performance, professional, theme, enhanced-* variants
- **Assets:** desktop_view.png, initial_state.png
- **Docs:** GUI_FINALIZATION_SUMMARY.md

**Reason:** Single canonical architecture (NewGUIforClient.html + app.css) eliminates duplication and prevents confusion.

---

## ⚙️ ARCHITECTURE PRINCIPLES

### Single Source of Truth
- **HTML:** `NewGUIforClient.html` (only entry point)
- **CSS:** `app.css` (complete design system + components)
- **JS:** `scripts/app.js` (main controller) + modular services

### File Organization
```
Client-gui/
├── [CANONICAL] NewGUIforClient.html ──────┐
├── [STYLES] styles/app.css                 ├─ ACTIVE FILES
├── [SCRIPTS] scripts/ (16 modules)         │  (DO NOT MODIFY ARCHIVED)
├── [CONFIG] package.json, README.md        │
├── [TOOLS] start_client_gui.py             │
├── [ASSETS] favicon.svg                    │
├── [DOCS] CLAUDE.md, FILES_INVENTORY.md   ├─ (This inventory)
├── [LOGS] appmap.log                       │
└── archived/ ──────────────────────────────┴─ DEPRECATED (DO NOT USE)
   └── (17 archived CSS + 6 archived HTML + screenshots + historical docs)
```

### Design Patterns
1. **ES6 Modules:** No build step required; uses native browser ES6 import/export
2. **Service Layer:** Decoupled business logic (API, WebSocket, file ops) from presentation
3. **Reactive State:** Minimal state store with batched updates and shallow diffing
4. **Performance First:** RAF batching, debouncing, DOM read/write separation, smooth animations
5. **Accessibility:** ARIA labels, screen reader support, keyboard navigation, live regions
6. **Theme System:** CSS custom properties for light/dark mode with localStorage persistence

---

## ✅ GUIDELINES FOR MAINTENANCE

### DO ✅
- Edit **app.css** for style changes (single source of truth)
- Add new services to **scripts/services/** for new business logic
- Update **app.js** for application flow changes
- Modify **NewGUIforClient.html** for DOM structure changes
- Run `npm run validate` to check module integrity

### DON'T ❌
- **DO NOT** use archived HTML files—they lack current features
- **DO NOT** add new CSS files—edit app.css directly
- **DO NOT** create duplicate styling—consolidate into app.css
- **DO NOT** modify archived files—they're deprecated
- **DO NOT** break the service layer abstraction—keep API/WebSocket logic separate

### Common Tasks
```bash
# Development
npm run dev                    # Start with CORS enabled
npm run validate             # Check all module imports
npm run check                # Full validation

# Launch
python start_client_gui.py   # One-click server + browser open
npm run build                # (If build step added)
```

---

## 🎯 BIG PICTURE

The Client-gui is a **self-contained, modular web application** providing end-users an interface to upload encrypted file backups. It communicates with the CyberBackup API Server (port 9090) via:
- **HTTP REST** for initial connection, backup commands, status polling
- **WebSocket (Socket.IO)** for real-time progress updates

The codebase is **organized for maintainability**: services handle business logic, UI modules handle presentation, utilities provide reusable helpers, and the state store provides reactive state management. CSS is unified (app.css) for single-source-of-truth design consistency. All files support the canonical HTML entry point with zero redundancy.
