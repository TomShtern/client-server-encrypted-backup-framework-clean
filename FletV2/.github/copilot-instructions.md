---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

# FletV2 – AI Coding Agent Instructions (December 2025)

## 🎯 Project Overview
**FletV2** is a production-ready Flet desktop application for encrypted backup server management. The codebase exemplifies "Framework Harmony" - maximizing Flet's built-in capabilities while avoiding over-engineering.

**Current Status**: ✅ **OPTIMIZED** - Major architectural improvements completed (server bridge: 2,743→316 lines, UI performance: already optimal)

## 🏗️ Core Architecture (Current State)

### Application Structure
```
main.py (1,035 lines)           # FletV2App(ft.Row) with NavigationRail + AnimatedSwitcher
├── Entry: create_server_bridge() → auto-detects real server or falls back to mock
├── Navigation: ft.NavigationRail.on_change → _load_view() (no custom routing)
├── Content: ft.AnimatedSwitcher with view functions
└── Theme: setup_modern_theme() Material Design 3 integration

views/ (8 files, ~1,000 lines each)  # Function-based view creators
├── create_<name>_view(server_bridge, page, state_manager=None) -> ft.Control
├── dashboard.py    # Server status, metrics, quick actions
├── clients.py      # Client management with real-time updates
├── files.py        # File browser, download, verification
├── database.py      # Database tables and statistics
├── analytics.py    # Real-time charts and performance metrics
├── logs.py         # Log viewer with export and filtering
└── settings.py      # App configuration (large: 2,319 lines - modularization opportunity)

utils/ (18 files, core optimized)    # Framework-aligned utilities
├── server_bridge.py (316 lines)     # ✅ OPTIMIZED: Clean delegation pattern
├── state_manager.py (887 lines)     # Reactive cross-view state management
├── mock_database_simulator.py       # Thread-safe mock backend
├── debug_setup.py                   # Enhanced logging with terminal debugging
├── user_feedback.py                  # Dialogs, snackbars, error handling
└── ui_components.py (1,467 lines)   # Reusable Material Design 3 components
```

### Data Flow & Integration Points
1. **Server Integration**: `ServerBridge` → real server OR mock database (seamless fallback)
2. **State Propagation**: `StateManager` → reactive updates across views
3. **UI Updates**: `control.update()` for UI changes; only use `page.update()` for themes/dialogs/overlays
4. **Async Operations**: `page.run_task()` for background work, `aiofiles` for I/O

## ⭐ Golden Patterns

### Control Updates & Performance
- **Control updates:** Use `control.update()` for UI changes; only use `page.update()` for UI changes; only use `page.update()` for themes/dialogs/overlays
- **Control access:** Use `ft.Ref` for control references, never deep index chains
- **Performance hierarchy:** 1. `control.update()` (best), 2. `ft.update_async()` (good), 3. `page.update()` (acceptable only for themes)
- **Never loop `page.update()`:** Prefer granular control updates; target <16ms for 60fps responsiveness

### Navigation & Layout
- **Navigation:** Only use `NavigationRail.on_change` → `_load_view` (see `main.py`). No custom routing
- **Layout:** Use `expand=True` and standard Flet containers (Row, Column, etc.)
- **Theme inheritance:** Use `ft.Colors` and `theme.py` helpers; avoid hard-coded colors

### View Lifecycle Management
- **View disposal:** All views must implement a `dispose()` method to clean up subscriptions, async tasks, and overlays (e.g., remove FilePicker from `page.overlay`). Main app must call dispose before switching views
- **FilePicker lifecycle:** Only one FilePicker per view instance. Store on state, add to overlay if not present, remove on dispose. Always reference via state object
- **Control lifecycle:** Controls must be attached to page before updating. Defer subscriptions until view is constructed and added. Views should return a tuple `(content, dispose, setup_subscriptions)`. `setup_subscriptions()` calls must execute **after** the view is updated and attached to the page to prevent "Text Control must be added to the page first" errors. `setup_subscriptions()` calls must execute **after** the view is updated and attached to the page to prevent "Text Control must be added to the page first" errors.

### State Management & Progress
- **Progress tracking:** For long-running operations (export, backup), use StateManager's `start_progress`, `update_progress`, and `clear_progress`. UI indicators should bind to progress states for granular feedback
- **Event deduplication:** StateManager must deduplicate events to prevent duplicate notifications and unnecessary UI updates
- **State Manager null checks:** When `state_manager` is optional in view creation, add null checks before calling methods on it. If `state_manager` is `None`, fall back to using `server_bridge` directly or skip state management operations

### Async & Error Handling
- **Async patterns:** Use small async handlers and `page.run_task()` for background work. Avoid blocking the UI
- **Error boundaries:** Graceful degradation when components fail; show user-friendly error messages

## 🚀 Essential Development Workflows

### ServerBridge API Reference
**Creation**: `from utils.server_bridge import create_server_bridge`
**Mode Detection**: Automatically falls back to mock mode when no real server detected
**Return Format**: All methods return normalized `{success, data, mode}` dicts

**Core Methods**:
```python
# Client Management
get_all_clients_from_db() → List[Dict]  # {id, client_id, name, status, last_seen, files_count, total_size}
get_clients_async() → List[Dict]        # Async version

# File Operations
get_files() → List[Dict]                # All files
get_client_files(client_id) → List[Dict] # Files for specific client
delete_file(file_id) → Dict             # Delete with cascade
download_file(file_id) → bytes/Path     # Mock writes temp files

# Database Operations
get_database_info() → Dict              # Schema, table stats
get_table_data(table) → List[Dict]      # Table contents
update_row(table, id, data) → Dict      # Row updates
delete_row(table, id) → Dict            # Row deletion with integrity

# System Status
get_server_status_async() → Dict        # Health, uptime, connections
get_system_status() → Dict              # CPU, memory, disk
get_logs() → List[Dict]                 # Recent log entries
```

**Mock Mode Features**:
- Persistent state across operations (`mock_data_store.json`)
- Referential integrity enforcement (cascading deletes)
- Realistic data generation with faker
- Thread-safe operations for concurrent access

### Quick Start Commands
```bash
# Development (hot reload)
flet run -r main.py

# Production mode
python main.py

# Debug mode (verbose logging)
set FLET_V2_DEBUG=true && python python main.py  # Windows
export FLET_V2_DEBUG=true && python main.py  # Unix

# Performance validation
python quick_performance_validation.py

# Search patterns efficiently
rg "page\.update\(\)" --type py          # Find page updates
rg "create_.*_view" views/               # Find view creators
rg "server_bridge\." utils/              # Find server bridge usage
```

### Code Quality & Testing
```bash
# Static analysis
pyright                                  # Type checking
pylint main.py views/ utils/             # Code quality

# Testing (avoid automated UI tests - they don't work well with Flet)
python -m pytest tests/ -v              # Run existing tests
# Manual testing preferred: run app and test views manually

# Performance benchmarking
python performance_benchmark.py         # Full benchmark suite
```

### Debugging Patterns
- **Control Lifecycle Issues**: Ensure controls attached to page before `.update()`. Views should return a tuple `(content, dispose, setup_subscriptions)`. `setup_subscriptions()` calls must execute **after** the view is updated and attached to the page.
- **JSON Validation**: `python -m json.tool <file>` to validate config files
- **Fast Search**: Use `rg` (ripgrep) for pattern searching across codebase
- **State Issues**: Check `FLET_V2_DEBUG=true` for detailed state change logs
- **Lint**: `pyright`, `pylint main.py views/ utils/`. Always fix all errors and warnings
- **Tests**: `python -m pytest tests -v` (manual smoke preferred for UI). **Avoid running tests; Flet UI is not testable by standard frameworks.**
- **Codacy**: **Codacy checks are currently ignored. DO NOT USE CODACY.**
- **Search**: Use ripgrep (rg) to search for patterns more efficiently

## 🔧 Gotchas & Invariants
- Flet API names are case-sensitive
- Controls must be attached to the page before updating. Defer subscriptions until view is constructed and added
- Theme inheritance first; avoid hard-coded colors. Use `ft.Colors` and `theme.py` helpers
- Never loop `page.update()`; prefer granular control updates

## 🔐 Security & Config
- Load secrets via env vars in `config.py`. Never print secrets; warn in debug if missing
- **GitHub Personal Access Token**: Treat `.claude.json` tokens as CRITICAL secrets
- **Secure handling**: Use environment variables, never hardcode secrets
- **Environment Variables**: Set `GITHUB_PERSONAL_ACCESS_TOKEN` before running Flet apps
- **Best Practices**: Use `.env` files for dev, repository secrets for CI, rotate regularly

## 🐛 Debugging & Search
- Use ripgrep (rg) for fast code search. For JSON errors, fix structure and validate (`python -m json.tool <file>`)
- **"Text Control must be added to the page first"**: Flet control lifecycle issue. Defer subscription setup until after view construction. Views should return a tuple `(content, dispose, setup_subscriptions)`. `setup_subscriptions()` calls must execute **after** the view is updated and attached to the page.
- **JSON parsing errors**: Ensure valid structure including opening brace `{` for objects
- **"Unknown property 'globs' will be ignored"**: Check configuration files for typos
- **State Manager null checks**: Handle gracefully when `state_manager` is `None`

## 📝 Examples
- View skeleton: `views/<name>.py` → `def create_<name>_view(server_bridge, page, state_manager=None) -> ft.Control`
- Reference: `main.py`, `views/settings.py`, `views/logs.py`, `utils/server_bridge.py`, `theme.py`

## 🚀 Recent Enhancements (2025-09)
- **FilePicker lifecycle**: Only one per view, removed on dispose
- **Progress tracking**: Use StateManager for granular progress in export/backup flows
- **Event deduplication**: StateManager prevents duplicate notifications
- **View disposal**: All views must clean up subscriptions, async tasks, overlays
- **API normalization**: All server bridge methods return `{success, data, mode}`
- **`page.update()` → `control.update()` Conversion**: ✅ **COMPLETED** - Codebase already optimized
- **Settings.py Refactoring**: Settings view is now config-driven, state-heavy logic moved to `settings_state.py`, import/export via `utils/settings_io`, validators centralized in `utils/validators`, and action bar modularized in `utils/action_buttons`.
    - **Settings Modularization**: The settings logic has been further modularized, with `settings_io.py` merged into `settings_state.py`, and a validator registry added to `validators.py`.
- **Control Update Fixes**: Modified all view functions to return a tuple `(content, dispose, setup_subscriptions)` instead of calling update methods during construction. Moved `setup_subscriptions()` calls to execute **after** the view is updated and attached to the page.
- **Icon Fix**: Replaced `ft.Icons.DATABASE` with `ft.Icons.STORAGE` in `database.py`.
- **Control Lifecycle**: Ensure controls are attached to the page before updating. Views should return a tuple `(content, dispose, setup_subscriptions)`. `setup_subscriptions()` calls must execute **after** the view is updated and attached to the page.
- **DataTable Column Initialization**: DataTable was initialized with empty columns `columns=[]`, causing Flet to throw "columns must contain at minimum one visible DataColumn". Initialize DataTable with default columns.
- **Empty Data Handling**: Always ensure at least one column exists in DataTable, even when no data is available.

## ❌ What NOT to do
- Do not use custom routers, overlays, or state managers outside Flet's built-ins
- Do not use Codacy checks (currently ignored)
- Do not hardcode colors, secrets, or control references
- Do not break the code or remove functionality when fixing problems

## 📚 References
- See `main.py`, `views/settings.py`, `views/logs.py`, `utils/server_bridge.py`, `theme.py` for canonical patterns

## 🎯 Performance Optimization Summary

**Status**: ✅ **ACHIEVED** - The codebase has already been optimized. All instances of `page.update()` are used correctly for dialog creation, overlay additions, theme changes, snackbar operations, and error fallbacks. The development team has correctly implemented `control.update()` for performance-critical operations and strategically used `page.update()` only when necessary.

**Original Goal**: Achieve 10x faster UI update performance and smoother user interactions by converting `page.update()` calls to `control.update()`. ✅ **This optimization has already been implemented.**

**Decision Tree Followed**:
```
Found page.update() →
├─ Is it in user_feedback.py? → KEEP (dialogs need page updates)
├─ Is it creating/showing dialogs? → KEEP
├─ Is it changing themes? → KEEP
├─ Is it adding to page.overlay? → KEEP
└─ Everything else → CONVERT to control.update()
```

**Findings (2025-09-16)**: A comprehensive analysis revealed that the codebase is already optimized, using `control.update()` where appropriate and `page.update()` only for dialogs, overlays, and theme changes. No changes are required. The 10x performance benefit is already in place.