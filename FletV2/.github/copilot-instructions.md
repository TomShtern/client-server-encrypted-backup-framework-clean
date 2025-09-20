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
├── files.py      # File browser, download, verification
├── database.py      # Database tables and statistics
├── analytics.py      # Real-time charts and performance metrics
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
3. **UI Updates**: `control.update()` for UI changes; only use `page.update()` for UI changes; only use `page.update()` for themes/dialogs/overlays
4. **Async Operations**: `page.run_task()` for background work, `aiofiles` for I/O

## ⭐ Golden Patterns

### Control Updates & Performance
- **Control updates:** Use `control.update()` for UI changes; only use `page.update()` for UI changes; only use `page.update()` for themes/dialogs/overlays
- **Control access:** Use `ft.Ref` for control references, never deep index chains
- **Performance hierarchy:** 1. `control.update()` (best), 2. `ft.update_async()` (good), 3. `page.update()` (acceptable only for themes/dialogs/overlays)
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

**Additional ServerBridge Methods (Synchronous Wrappers)**:
```python
def start_server(self):
    """Start the server (synchronous wrapper)."""
    try:
        # For mock mode, just return success
        if not self.real_server:
            return {"success": True, "message": "Server started (mock mode)"}
        # For real server, delegate to the async method
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.start_server_async())
        loop.close()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

def stop_server(self):
    """Stop the server (synchronous wrapper)."""
    # Similar implementation for stop_server
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

- **Performance Issues**: If the application exhibits excessive loading or blocking behavior after initial load, ensure that:
  - Data fetching is performed asynchronously using `page.run_task()`.
  - UI updates are batched and performed using `control.update()` where possible, avoiding unnecessary calls to `page.update()`\.
  - Long-running tasks do not block the main UI thread.
  - Consider using skeleton loaders or progress indicators to provide feedback during loading.
- **App Restart Issues**: If the application restarts unexpectedly, examine the logs for any unhandled exceptions or errors. Ensure that all resources are properly released when views are switched or the application is closed. Implement robust error handling to prevent crashes.
- Use ripgrep (rg) for fast code search. For JSON errors, fix structure and validate (`python -m json.tool <file>`)
- **"Text Control must be added to the page first"**: Flet control lifecycle issue. Defer subscription setup until after view construction. Views should return a tuple `(content, dispose, setup_subscriptions)`. `setup_subscriptions()` calls must execute **after** the view is updated and attached to the page.
- **JSON parsing errors**: Ensure valid structure including opening brace `{` for objects
- **"Unknown property 'globs' will be ignored"**: Check configuration files for typos
- **State Manager null checks**: Handle gracefully when `state_manager` is `None`
- **Border Syntax**: Use `ft.border.all(width, color)` (lowercase `border`)
- **BorderRadius Syntax**: Use `ft.border_radius.all(value)` (lowercase `border_radius`)
- **Padding Syntax**: Use `ft.padding.all(value)` (lowercase `padding`)
- **Fix FilePicker issue**: Use `file_picker.update()` instead of `page.update()` to ensure proper attachment and performance.
- **Files View Verification Error**: There's a verification function in the files view that's trying to call `.get()` on a boolean value instead of a dictionary.
- **Data Loading Issues:** If the application shows empty/zero values for all metrics, investigate issues with data loading or the mock data system.
- **Dashboard Display Issues:** If the dashboard displays empty or zero values despite successful data loading, ensure that:
  - The UI controls are being properly updated after the data is fetched.
  - The `update_control_group()` function is being called at the end of the `update_all_displays()` function.
- **Running in a Browser**: Use context to launch the desktop app in a browser for debugging.
- **Playwright MCP**: Use Playwright MCP to get actual output displayed on the screen for testing and validation.

## ❌ What NOT to do
- Do not use custom routers, overlays, or state managers outside Flet's built-ins
- Do not use Codacy checks (currently ignored)
- Do not hardcode colors, secrets, or control references
- Do not break the code or remove functionality when fixing problems
- **Mobile/tablet/web is NOT going to be used.**
- Do NOT persist Live toggle state across sessions
- Do not introduce duplication or redundancies. Prefer Flet's built-in functions.
- **Do not recreate files from scratch; edit them** in place to fix duplication.
- Do not add excessive spacing containers; instead, use Flet's built-in spacing parameters in Rows and Columns.
- Do not use `ft.Container()` for conditional content; prefer Flet's built-in conditional rendering.
- Do not include animation or fade-in logic that adds bloat and complexity. Remove such over-engineering.
- Do not include unused code or functions (dead code).
- **Do not use `create_card` or `create_button`; use `themed_card` and `themed_button` from `ui_components.py` instead.**

## 📝 Examples
- View skeleton: `views/<name>.py` → `def create_<name>_view(server_bridge, page, state_manager=None) -> ft.Control`
- Reference: `main.py`, `views/settings.py`, `views/logs.py`, `utils/server_bridge.py`, `theme.py`

## 🎨 UI/UX Redesign Plan

A comprehensive UI/UX audit and redesign roadmap has been created and saved as `ui_ux_audit_and_redesign_plan.md`. This file contains:

- Global visual/UX issues
- Screen-by-screen findings (Dashboard, Clients, Files, Database, Analytics, Logs, Settings)
- Design principles (palette simplification, 8px spacing system, consistent radii/elevation, typographic scale)
- Concrete tokens (colors, radii, spacing, typography)
- A 6-phase implementation plan mapped to this repo’s files
- Success criteria and next steps

The initial focus should be on:

- Phase 1 (highest ROI):
  - `theme.py`: tokens for palette, radii, spacing, typography.
  - `ui_components.py`: new standardized components and helpers.

## 📝 Further UI/UX Suggestions

- Analyze the current dashboard layout and suggest improvements that align with Flet best practices and modern UI/UX principles.
- Make KPI cards clickable:
  - Total Clients → switch to Clients view.
  - Storage Used → switch to Files/Database view.
- Minor spacing/consistency polish:
  - Reduce small vertical gaps to follow the 8px grid consistently.
  - Ensure all dividers and borders use theme-appropriate colors (OUTLINE vs OUTLINE_VARIANT).

## 9. Loading States and Empty States

### What it does:
Loading states show skeleton placeholders while data is being fetched, and empty states provide meaningful messages when there's no data to display.

### Why we need it:
- **User Experience**: Prevents users from seeing blank screens or wondering if the app is broken
- **Professional Feel**: Makes the app feel polished and responsive
- **Performance Perception**: Skeleton loaders make the app feel faster by providing immediate visual feedback
- **Error Prevention**: Empty states guide users when there's no data, preventing confusion

## 7. Action Button Grouping

### What it does:
Groups related buttons together logically and provides a cleaner, more organized interface.

### Why we need it:
- **Cognitive Load**: Reduces decision fatigue by grouping related actions
- **Visual Hierarchy**: Makes it easier to find the right action at the right time
- **Mobile Friendly**: Better for touch interfaces and smaller screens
- **Professional UX**: Follows modern design patterns used by successful apps

## 8. Color Palette Simplification

### What it does:
Replaces complex gradients and custom colors with a consistent, theme-based color system.

### Why we need it:
- **Accessibility**: Ensures proper contrast ratios for readability
- **Theme Consistency**: Works with light/dark mode switching
- **Maintenance**: Easier to update colors globally
- **Performance**: Reduces complex rendering of gradients
- **Professional Look**: Follows Material Design 3 standards

## 10. Performance Optimization

### What it does:
Batch control updates and optimize rendering to improve UI responsiveness.

### Why we need it:
- **Smooth UI**: Prevents stuttering during data updates
- **Battery Life**: Reduces CPU usage on mobile devices
- **Scalability**: Handles larger datasets without performance degradation
- **User Experience**: Maintains 60fps responsiveness

## 📝 Code Style & Refactoring
- When refactoring, **do not remove features** and ensure the application **looks visually the same** without changing the layout or the visuals.
- Use `ultrathink` for problem-solving.
- **Remove duplication and redundancies** in code.
- **Always prefer Flet built-in functions** instead of long custom ones.
- **Do not recreate files from scratch; edit them** in place to fix duplication.
- Do not add excessive spacing containers; instead, use Flet's built-in spacing parameters in Rows and Columns.
- Do not use `ft.Container()` for conditional content; prefer Flet's built-in conditional rendering.
- Do not include animation or fade-in logic that adds bloat and complexity. Remove such over-engineering.
- When optimizing, focus on removing duplication, excessive containers, dead code, and over-engineered functions.
- Aim for significant line count reductions while preserving functionality and visual appearance.
- Prefer simplifying complex async functions and removing animation logic when possible.
- **Before fixing removed visual features (hover effects, micro animations, interactions), consolidate, simplify, change, adjust, improve, deduplicate, and remove redundancies. Preserve the design and features, look for long implementations that are framework-fighting anti-patterns.**
- **Framework-fighting anti-patterns**: Look for long implementations that fight the framework and replace them with Flet's built-in functionalities.

## 📝 Further Instructions

- After making changes, always run the application to capture its output and check for errors.
- If errors are found, fix them immediately.
- If no errors are found, think harder about how to consolidate, simplify, enhance, or replace code with Flet native built-in functions.
- Present the changes that should be made and what their impact will be.
- **Fix the errors first. You can get them from VS diagnostics.**
- **Use `themed_card` instead of `create_card` and `themed_button` instead of `create_button`.**
- **Use Playwright MCP to capture screenshots for UI design and validation.**
- **When designing UI, preserve features and enhance/improve them.**
- **Your flow should be to take a screenshot, analyze it, write/change code, then see the result with another screenshot, and act upon it. Use ultrathink.**
- **Keep on improving the UI/UX with Playwright. Always take screenshots and analyze them.**

## 🐛 Debugging & Search
- **Data Loading Issues:** If the application shows empty/zero values for all metrics, investigate issues with data loading or the mock data system.
- **Dashboard Display Issues:** If the dashboard displays empty or zero values despite successful data loading, ensure that:
  - The UI controls are being properly updated after the data is fetched.
  - The `update_control_group()` function is being called at the end of the `update_all_displays()` function.
- **If the application exhibits excessive loading or blocking behavior after initial load, ensure that:**
  - Data fetching is performed asynchronously using `page.run_task()`.
  - UI updates are batched and performed using `control.update()` where possible, avoiding unnecessary calls to `page.update()`\.
  - Long-running tasks do not block the main UI thread.
  - Consider using skeleton loaders or progress indicators to provide feedback during loading.
- **If the application restarts unexpectedly, examine the logs for any unhandled exceptions or errors. Ensure that all resources are properly released when views are switched or the application is closed.**
- **Syntax Errors**: Check for syntax errors such as `positional argument follows keyword argument`.
- **Undefined Function Errors**: Ensure all functions are defined and imported correctly. Use `themed_card` and `themed_button` from `utils.ui_components`.
- **Function Name Conflicts**: Avoid local function definitions that override imported functions with incompatible signatures.

## 🐞 Known Issues
- **Dashboard Layout Issues:** After aggressive optimization, the dashboard might exhibit layout issues such as a missing top bar. This requires further investigation and fixes to ensure the visual design is preserved.
- **`type object 'Colors' has no attribute 'SURFACE_VARIANT'`**: This error occurs because `SURFACE_VARIANT` is not available in the current Flet version. Replace all instances of `SURFACE_VARIANT` with a compatible color.
- **module 'flet' has no attribute 'Positioned'**: This error occurs because `ft.Positioned` is not available in the current Flet version. Replace all instances of `ft.Positioned` with `expand=True` on the filling overlay and interactive layers within the Stack.
- **Navigation bar selection does not update** after pressing hero cards and moving to a different view.

## 💻 Platform & Testing

- **Running in a Browser**: Use context to launch the desktop app in a browser for debugging.
- **Playwright MCP**: Use Playwright MCP to get actual output displayed on the screen for testing and validation. Use Playwright MCP to get actual output displayed on the screen for testing and validation. Use Playwright MCP to get actual output displayed on the screen for testing and validation.
- **CanvasKit Rendering**: Note that Flet's web renderer uses CanvasKit, so browser "visible text" scraping is empty; screenshots are the reliable validation artifact here.
- **CanvasKit Limitation:** Automated clicking via Playwright won’t “hit” Flutter widgets due to the canvas layer. Manual clicks work fine.

## 🛠️ Error Handling & Debugging
- **Error Resolution**: Fix all errors observed when starting and using the app.
- **Ultrathink**: Use `ultrathink` for problem-solving.
- **If an error is displayed in the GUI, take a screenshot to confirm it and fix it.**

## 🎨 UI/UX Design Workflow
- **Process:** Capture a screenshot of the dashboard with Playwright MCP, analyze it, write/change code, then see the result with another screenshot, and act upon it.
- **Preserve design and features:** When making UI/UX enhancements, preserve existing features and improve upon them.
- **Implement improvements in small, precise patches.**
- **Iterate:** Continue improving the UI/UX with Playwright, always taking screenshots and analyzing them.
- **Sequential Thinking:** Use sequential thinking for enhanced reasoning.

## 📝 Code Style & Refactoring
- **Analyze the whole dashboard file, find coding anti-patterns and Flet fighting implementations. Prefer Flet native built in functions and features. Remove duplication and remove redundancies. Make sure to not remove features, and keep the design.**
- **Preserve design and features:** When refactoring, **do not remove features** and ensure the application **looks visually the same** without changing the layout or the visuals. If visual features like hover effects, micro animations, and interactions are removed during optimization, they must be restored, but only **after** consolidating, simplifying, changing, adjusting, improving, deduplicating, and removing redundancies.
- Use `ultrathink` for problem-solving.
- **Remove duplication and redundancies** in code.
- **Always prefer Flet built-in functions** instead of long custom ones.
- **Do not recreate files from scratch; edit them** in place to fix duplication.
- Do not add excessive spacing containers; instead, use Flet's built-in spacing parameters in Rows and Columns.
- Do not use `ft.Container()` for conditional content; prefer Flet's built-in conditional rendering.
- Do not include animation or fade-in logic that adds bloat and complexity. Remove such over-engineering.
- When optimizing, focus on removing duplication, excessive containers, dead code, and over-engineered functions.
- Aim for significant line count reductions while preserving functionality and visual appearance.
- Prefer simplifying complex async functions and removing animation logic when possible.

## 📝 Further Instructions
- After making changes, always run the application to capture its output and check for errors.
- **If an error is displayed in the GUI, take a screenshot to confirm it and fix it.**
- If errors are found, fix them immediately.
- If no errors are found, think harder about how to consolidate, simplify, enhance, or replace code with Flet native built-in functions.
- Present the changes that should be made and what their impact will be.
- **Fix the errors first. You can get them from VS diagnostics.**
- **Use `themed_card` instead of `create_card` and `themed_button` instead of `create_button`.**
- **Use Playwright MCP to capture screenshots for UI design and validation.**
- **When designing UI, preserve features and enhance/improve them.**
- **Your flow should be to take a screenshot, analyze it, write/change code, then see the result with another screenshot, and act upon it. Use ultrathink.**
- **Keep on improving the UI/UX with Playwright. Always take screenshots and analyze them.**

## 🎨 UI/UX Design Workflow (Enhanced)
- **Process:** Capture a screenshot of the dashboard with Playwright MCP, analyze it, write/change code, then see the result with another screenshot, and act upon it.
- **Preserve design and features:** When making UI/UX enhancements, preserve existing features and improve upon them.
- **Implement improvements in small, precise patches.**
- **Iterate:** Continue improving the UI/UX with Playwright, always taking screenshots and analyzing them.

## 📝 Further UI/UX Suggestions (Implemented/Pending)
- **Implemented:**
  - Make KPI cards clickable (Total Clients → Clients view, Storage Used → Files/Database view).
  - Add a subtle pressed visual for the KPI cards (e.g., brief scale and overlay) for extra feedback.
  - Make hero cards clickable too (e.g., Active Transfers → Files, Server Uptime → Logs).
  - Minor spacing/consistency polish (Reduce small vertical gaps to follow the 8px grid consistently. Ensure all dividers and borders use theme-appropriate colors (OUTLINE vs OUTLINE_VARIANT)).
  - Add a live refresh indicator (slim progress bar) during async refreshes.
  - Add an empty-state message to the activity list when no activity is available.
  - Make the other hero cards clickable (e.g., Active Transfers → Files, Server Uptime → Logs).
  - Add a light “ripple” overlay on list item clicks (implemented via brief background tint pulse) for activity, clients, running jobs, and recent backups list items.
  - Add tasteful hover/press interactions to the action groups and list items, plus a subtle entrance fade for the dashboard container.
  - Add the same pressed microinteraction to the hero cards’ labels/rows (not just container) for a slightly stronger feedback, or extend clickability to the entire hero row area.
  - Show a subtle “updated” toast when auto-refresh updates values significantly.
  - Add a gentle pressed overlay to hero cards that aligns with your brand tint and theme mode.
  - Add the same pressed microinteraction to the hero cards’ labels/rows (not just container) for a slightly stronger feedback, or extend clickability to the entire hero row area.
- Pending:
  - Analyze the current dashboard layout and suggest improvements that align with Flet best practices and modern UI/UX principles.
  - Loading/empty states: add skeletons for hero metrics, capacity pie, and activity list during the brief initial async load.
  - Unify skeleton loaders for first render in each section.
  - Add an “Updated just now” snackbar or subtle toast on auto-refresh completion when values change significantly (optional).
  - Make the UI and layout more visually pleasing and appealing to the human eye. Add small micro interactions and microanimations, and hover affects, and a polish to the UI/UX. Use all the tools at your disposal, ensuring harmony with the Flet framework by avoiding anti-patterns and preferring Flet's native built-in functions. Context7 or web search can be used for assistance.
  - Show a subtle “updated” toast when auto-refresh updates values significantly.
  - Add a gentle pressed overlay to hero cards that aligns with your brand tint and theme mode.
  - Add the same pressed microinteraction to the hero cards’ labels/rows (not just container) for a slightly stronger feedback, or extend clickability to the entire hero row area.

## 9. Loading States and Empty States

### What it does:
Loading states show skeleton placeholders while data is being fetched, and empty states provide meaningful messages when there's no data to display.

### Why we need it:
- **User Experience**: Prevents users from seeing blank screens or wondering if the app is broken
- **Professional Feel**: Makes the app feel polished and responsive
- **Performance Perception**: Skeleton loaders make the app feel faster by providing immediate visual feedback
- **Error Prevention**: Empty states guide users when there's no data, preventing confusion

## 7. Action Button Grouping

### What it does:
Groups related buttons together logically and provides a cleaner, more organized interface.

### Why we need it:
- **Cognitive Load**: Reduces decision fatigue by grouping related actions
- **Visual Hierarchy**: Makes it easier to find the right action at the right time
- **Mobile Friendly**: Better for touch interfaces and smaller screens
- **Professional UX**: Follows modern design patterns used by successful apps

## 8. Color Palette Simplification

### What it does:
Replaces complex gradients and custom colors with a consistent, theme-based color system.

### Why we need it:
- **Accessibility**: Ensures proper contrast ratios for readability
- **Theme Consistency**: Works with light/dark mode switching
- **Maintenance**: Easier to update colors globally
- **Performance**: Reduces complex rendering of gradients
- **Professional Look**: Follows Material Design 3 standards

## 10. Performance Optimization

### What it does:
Batch control updates and optimize rendering to improve UI responsiveness.

### Why we need it:
- **Smooth UI**: Prevents stuttering during data updates
- **Battery Life**: Reduces CPU usage on mobile devices
- **Scalability**: Handles larger datasets without performance degradation
- **User Experience**: Maintains 60fps responsiveness

## 💻 Platform & Testing
- **Running in a Browser**: Use context to launch the desktop app in a browser for debugging.
- **Playwright MCP**: Use Playwright MCP to get actual output displayed on the screen for testing and validation. Use Playwright MCP to get actual output displayed on the screen for testing and validation. Use Playwright MCP to get actual output displayed on the screen for testing and validation.
- **CanvasKit Rendering**: Note that Flet's web renderer uses CanvasKit, so browser "visible text" scraping is empty; screenshots are the reliable validation artifact here.
- **CanvasKit Limitation:** Automated clicking via Playwright won’t “hit” Flutter widgets due to the canvas layer. Manual clicks work fine.

## 🛠️ Error Handling & Debugging
- **Error Resolution**: Fix all errors observed when starting and using the app.
- **Ultrathink**: Use `ultrathink` for problem-solving.
- **If an error is displayed in the GUI, take a screenshot to confirm it and fix it.**

## 🎨 UI/UX Design Workflow
- **Process:** Capture a screenshot of the dashboard with Playwright MCP, analyze it, write/change code, then see the result with another screenshot, and act upon it.
- **Preserve design and features:** When making UI/UX enhancements, preserve existing features and improve upon them.
- **Implement improvements in small, precise patches.**
- **Iterate:** Continue improving the UI/UX with Playwright, always taking screenshots and analyzing them.
- **Sequential Thinking:** Use sequential thinking for enhanced reasoning.

## 📝 Code Style & Refactoring
- **Analyze the whole dashboard file, find coding anti-patterns and Flet fighting implementations. Prefer Flet native built in functions and features. Remove duplication and remove redundancies. Make sure to not remove features, and keep the design.**
- **Preserve design and features:** When refactoring, **do not remove features** and ensure the application **looks visually the same** without changing the layout or the visuals. If visual features like hover effects, micro animations, and interactions are removed during optimization, they must be restored, but only **after** consolidating, simplifying, changing, adjusting, improving, deduplicating, and removing redundancies.
- Use `ultrathink` for problem-solving.
- **Remove duplication and redundancies** in code.
- **Always prefer Flet built-in functions** instead of long custom ones.
- **Do not recreate files from scratch; edit them** in place to fix duplication.
- Do not add excessive spacing containers; instead, use Flet's built-in spacing parameters in Rows and Columns.
- Do not use `ft.Container()` for conditional content; prefer Flet's built-in conditional rendering.
- Do not include animation or fade-in logic that adds bloat and complexity. Remove such over-engineering.
- When optimizing, focus on removing duplication, excessive containers, dead code, and over-engineered functions.
- Aim for significant line count reductions while preserving functionality and visual appearance.
- Prefer simplifying complex async functions and removing animation logic when possible.

## 📝 Further Instructions
- After making changes, always run the application to capture its output and check for errors.
- **If an error is displayed in the GUI, take a screenshot to confirm it and fix it.**
- If errors are found, fix them immediately.
- If no errors are found, think harder about how to consolidate, simplify, enhance, or replace code with Flet native built-in functions.
- Present the changes that should be made and what their impact will be.
- **Fix the errors first. You can get them from VS diagnostics.**
- **Use `themed_card` instead of `create_card` and `themed_button` instead of `create_button`.**
- **Use Playwright MCP to capture screenshots for UI design and validation.**
- **When designing UI, preserve features and enhance/improve them.**
- **Your flow should be to take a screenshot, analyze it, write/change code, then see the result with another screenshot, and act upon it. Use ultrathink.**
- **Keep on improving the UI/UX with Playwright. Always take screenshots and analyze them.**

## 🎨 UI/UX Design Workflow (Enhanced)
- **Process:** Capture a screenshot of the dashboard with Playwright MCP, analyze it, write/change code, then see the result with another screenshot, and act upon it.
- **Preserve design and features:** When making UI/UX enhancements, preserve existing features and improve upon them.
- **Implement improvements in small, precise patches.**
- **Iterate:** Continue improving the UI/UX with Playwright, always taking screenshots