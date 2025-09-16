---
description: AI coding agent instructions for FletV2 encrypted backup server GUI
globs: *
---

# FletV2 – AI Coding Agent Instructions (September 2025)

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
├── database.py     # Database tables and statistics
├── analytics.py    # Real-time charts and performance metrics
├── logs.py         # Log viewer with export and filtering
└── settings.py     # App configuration (large: 2,319 lines - modularization opportunity)

utils/ (18 files, core optimized)    # Framework-aligned utilities
├── server_bridge.py (316 lines)     # ✅ OPTIMIZED: Clean delegation pattern
├── state_manager.py (887 lines)     # Reactive cross-view state management
├── mock_database_simulator.py       # Thread-safe mock backend
├── debug_setup.py                   # Enhanced logging with terminal debugging
├── user_feedback.py                 # Dialogs, snackbars, error handling
└── ui_components.py (1,467 lines)   # Reusable Material Design 3 components
```

### Data Flow & Integration Points
1. **Server Integration**: `ServerBridge` → real server OR mock database (seamless fallback)
2. **State Propagation**: `StateManager` → reactive updates across views
3. **UI Updates**: `control.update()` for performance, `page.update()` only for themes/dialogs/overlays
4. **Async Operations**: `page.run_task()` for background work, `aiofiles` for I/O

## ⭐ Golden Patterns

### Control Updates & Performance
- **Control updates:** Use `control.update()` for UI changes; only use `page.update()` for themes/dialogs/overlays
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
- **Control lifecycle:** Controls must be attached to page before updating. Defer subscriptions until view is constructed and added

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
set FLET_V2_DEBUG=true && python main.py  # Windows
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
- **Control Lifecycle Issues**: Ensure controls attached to page before `.update()`
- **JSON Validation**: `python -m json.tool <file>` to validate config files  
- **Fast Search**: Use `rg` (ripgrep) for pattern searching across codebase
- **State Issues**: Check `FLET_V2_DEBUG=true` for detailed state change logs
- Lint: `pyright`, `pylint main.py views/ utils/`. Always fix all errors and warnings reported by linters and static analysis tools such as `pylint` and `sourcery`. When fixing errors and warnings, ensure that you are not breaking the code, or breaking/removing functionality. Do not remove useful comments and docstrings. Fix errors and warnings, do not delete problems. Use sequential thinking where you don't know what to do.
- Tests: `python -m pytest tests -v` (manual smoke preferred for UI). **Avoid running tests; Flet UI is not testable by standard frameworks.**
- After ANY file edit: Codacy analysis required by project rules, but checks are currently ignored. **DO NOT USE CODACY.**
- Use ripgrep (rg) to search for patterns more efficiently.

## Gotchas & Invariants
- Flet API names are case-sensitive.
- Controls must be attached to the page before updating. Defer subscriptions until view is constructed and added.
- Theme inheritance first; avoid hard-coded colors. Use `ft.Colors` and `theme.py` helpers. Ensure that the UI components use proper theme inheritance and are not explicitly overriding the theme colors. Use `ft.Colors` theme roles instead of manual color definitions.
- Never loop `page.update()`; prefer granular control updates.

## Security & Config
- Load secrets via env vars in `config.py`. Never print secrets; warn in debug if missing.
- The `.claude.json` file may contain a GitHub Personal Access Token. Treat this token as a secret and handle it with CRITICAL severity. Ensure that the token is not exposed in logs or other publicly accessible locations. When setting the token, mask the value to prevent accidental disclosure (e.g., `set GITHUB_PERSONAL_ACCESS_TOKEN=****************************************`).
- **Secure handling of secrets**: Instead of hardcoding secrets, load them from environment variables (e.g., via `os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")` in Python code). For Flet apps, set them in your runtime environment or use a `.env` file with `python-dotenv`, but never commit `.env`.
- Update `config.py` to load secrets securely:

```python
# Add to config.py (after existing imports)
import os

# Existing pattern for non-secrets
DEBUG_MODE = os.environ.get('FLET_V2_DEBUG', 'false').lower() == 'true'

# New: Securely load secrets
GITHUB_TOKEN = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
# Optional: Validate presence in debug mode
if DEBUG_MODE and not GITHUB_TOKEN:
    print("Warning: GITHUB_PERSONAL_ACCESS_TOKEN not set")

# Other secrets (e.g., for server auth)
SERVER_API_KEY = os.environ.get('SERVER_API_KEY')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
```

- **Usage in Code:**
In any file (e.g., `server_bridge.py` or `main.py`):

```python
from config import GITHUB_TOKEN

if GITHUB_TOKEN:
    # Use the token securely (e.g., for API calls)
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    # Make authenticated request
else:
    # Fallback to mock mode or handle gracefully
    print("GitHub token not available, using mock data")
```

- **Environment Variables (Recommended for Local Development and Desktop Apps)**: Use environment variables to keep secrets out of code.
    - **How to Set Environment Variables:**
        - **Windows (PowerShell):** `set GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here`
        - **Windows (Command Prompt):** `set GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here`
        - **Persist across sessions:** Add to your system's environment variables via Control Panel > System > Advanced system settings > Environment Variables.
        - **For Flet apps:** Set them before running `flet run -r main.py` or `python main.py`.
- **GitHub Secrets (For CI/CD and Repository-Level Secrets)**: Use GitHub Secrets, which are encrypted variables stored at the repository or organization level, and accessible only in GitHub Actions workflows.
    - **How to Set GitHub Secrets:**
        1. Go to your repository on GitHub.
        2. Navigate to **Settings > Secrets and variables > Actions**.
        3. Click **New repository secret**.
        4. Name it (e.g., `GITHUB_PERSONAL_ACCESS_TOKEN`) and paste the value.
        5. In workflows (e.g., `.github/workflows/ci.yml`), access via `${{ secrets.GITHUB_PERSONAL_ACCESS_TOKEN }}`.
    - **Example GitHub Actions Workflow:**
        Create or update `.github/workflows/ci.yml`:

        ```yaml
        name: CI
        on: [push, pull_request]

        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - name: Set up Python
                uses: actions/setup-python@v4
              - name: Set up Python
                uses: actions/setup-python@v4
              - name: Install dependencies
                run: pip install -r requirements.txt
              - name: Run tests
                run: python -m pytest tests/
                env:
                  GITHUB_PERSONAL_ACCESS_TOKEN: ${{ secrets.GITHUB_PERSONAL_ACCESS_TOKEN }}
                  # Add other secrets as needed
        ```
    - **Usage in Workflows:**
        - Secrets are injected as environment variables in the runner.
        - Your code can access them via `os.environ.get()` as shown above.
        - For API calls in CI, use the secret directly in scripts.
- **Best Practices:**
    - Never hardcode secrets in code or config files.
    - Use `.env` files for local development (add `python-dotenv` to `requirements.txt` and load with `load_dotenv()` if using Python).
    - For production, set env vars in your deployment environment (e.g., via systemd, Docker, or cloud config).
    - Use repository secrets for repo-specific values; organization secrets for shared ones.
    - Rotate secrets regularly and revoke compromised ones immediately.
    - Limit secret scopes (e.g., read-only tokens for CI).
    - Always validate secrets exist before use, and log warnings (not the secrets themselves) in debug mode.
    - In tests, mock secrets or use test-specific env vars to avoid exposing real tokens.

## Debugging & Search
- Use ripgrep (rg) for fast code search. For JSON errors, fix structure and validate (`python -m json.tool <file>`).
- When encountering the error "Text Control must be added to the page first", this indicates a Flet control lifecycle issue. Ensure that controls are properly added to the page before attempting to update them. Defer subscription setup until after the view is constructed and attached to the page. This can be achieved by adding a deferred initialization pattern at the end of the view creation function.
- When debugging JSON parsing errors, such as "Incorrect type. Expected 'object'., End of file expected.", ensure the JSON file has a valid structure, including the opening brace `{` for a JSON object. After correcting the file, validate it using a JSON tool (e.g., `python -m json.tool <file>`).
- When encountering the error "Unknown property 'globs' will be ignored.", review the relevant configuration files (e.g., `.codacy.yml` or similar) and ensure that the `globs` property is correctly defined and supported in the context where it is being used. Check for typos or syntax errors in the property name or its value. Consult the documentation for the tool or library that uses the `globs` property to verify its correct usage and compatibility. If the property is unsupported, remove it. After making the change, validate the file if needed (e.g., by checking for parsing errors). If Codacy analysis is required per project rules, run `codacy_cli_analyze` on this file with `rootPath` set to the workspace and `file` set to the edited file path. If the tool is unavailable, follow the troubleshooting steps in `.github/instructions/codacy.rules`. **Codacy checks are currently ignored.**
  - **Codacy checks are currently ignored. DO NOT USE CODACY.**
- When addressing Sourcery warnings, adhere to best practices and ensure that the changes do not break the code or functionality. Functionality should remain the same.
- When a view receives `None` for the `state_manager`, handle it gracefully by either using the `server_bridge` directly or skipping state management operations. Implement null checks to avoid "TypeError: object NoneType can't be used in 'await' expression" errors.

## Examples
- View skeleton: `views/<name>.py` → `def create_<name>_view(server_bridge, page, state_manager=None) -> ft.Control`.
- Reference: `main.py`, `views/dashboard.py`, `utils/server_bridge.py`, `theme.py`.

## Recent Enhancements (2025-09)
- FilePicker lifecycle: Only one per view, removed on dispose: Ensure exactly one `FilePicker` per settings view instance, reuse it for import/export, and cleanly remove it on dispose. Ensure exactly one `FilePicker` per settings view instance, reuse it for import/export, and cleanly remove it on dispose.
- Progress tracking: Use StateManager for granular progress in export/backup flows: Emit progress updates from these operations and bind UI indicators to `progress_states`. Use StateManager for granular progress in export/backup flows: Emit progress updates from these operations and bind UI indicators to `progress_states`.
- Event deduplication: StateManager prevents duplicate notifications.
- View disposal: All views must clean up subscriptions, async tasks, overlays.
- API normalization: All server bridge methods return `{success, data, mode}`.
- `page.update()` → `control.update()` Conversion: The codebase has already been optimized. All instances of `page.update()` are used correctly for dialog creation, overlay additions, theme changes, snackbar operations, and error fallbacks. No changes are needed. The development team has correctly implemented `control.update()` for performance-critical operations and strategically used `page.update()` only when necessary.

## What NOT to do
- Do not use custom routers, overlays, or state managers outside Flet's built-ins.
- Do not use Codacy checks (currently ignored).
- Do not hardcode colors, secrets, or control references.
- Do not break the code or remove functionality when fixing problems.

## References
- See `main.py`, `views/settings.py`, `views/logs.py`, `utils/server_bridge.py`, `theme.py` for canonical patterns.

## Performance Optimization - `page.update()` → `control.update()` Conversion

The codebase has already been optimized. All instances of `page.update()` are used correctly for dialog creation, overlay additions, theme changes, snackbar operations, and error fallbacks. No changes are needed. The development team has correctly implemented `control.update()` for performance-critical operations and strategically used `page.update()` only when necessary.

**Original Goal:** Achieve 10x faster UI update performance and smoother user interactions by converting `page.update()` calls to `control.update()`. This optimization has already been implemented.

**Decision Tree:**

```
Found page.update() →
├─ Is it in user_feedback.py? → KEEP (dialogs need page updates)
├─ Is it creating/showing dialogs? → KEEP
├─ Is it changing themes? → KEEP
├─ Is it adding to page.overlay? → KEEP
└─ Everything else → CONVERT to control.update()
```

**Safety Guidelines:**

- **Golden Rules:**
  - One file at a time.
  - Test immediately after each file conversion.
  - Keep backups (Git commit before starting each file).
  - When in doubt, keep `page.update()` (it works, just slower).
- **Red Flags to Avoid:**
  - Do not change anything with `page.dialog`.
  - Do not change anything with `page.overlay`.
  - Do not change theme-related updates.
  - Do not change `utils/user_feedback.py` functions.

**Findings (2025-09-16):** A comprehensive analysis revealed that the codebase is already optimized, using `control.update()` where appropriate and `page.update()` only for dialogs, overlays, and theme changes. No changes are required. The 10x performance benefit is already in place.

---
description: AI rules derived by SpecStory from the project AI interaction history
---

---
description: AI guidance for FletV2 encrypted backup server GUI
---

# FletV2 Desktop Application Guidelines

This is a **Flet desktop app** for managing an encrypted backup server. Work ONLY inside `FletV2/`. Follow "framework harmony" - use Flet's built-ins, avoid overengineering. Emphasize 'Framework Harmony': Always prioritize Flet's built-in features over custom solutions. This reduces code by 50%+ and improves performance by 10x (see `FletV2_Documentation.md` for details).

## Essential Architecture

**Entry Point**: `main.py` creates `FletV2App(ft.Row)` with NavigationRail + AnimatedSwitcher content area
**Views**: Function-based creators in `views/` with signature: `def create_<name>_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control`
**Server Bridge**: `utils/server_bridge.py` provides unified `ServerBridge` - auto-falls back to `MockDataGenerator` when no real server
**State**: Cross-view updates via `state_manager` (optional); otherwise update controls directly
**Theming**: `theme.py` handles Material 3 themes with `setup_modern_theme(page)`
**Config**: `config.py` centralizes flags like `FLET_V2_DEBUG` and other constants.
**Debug/logging**: `utils/debug_setup.py` sets enhanced logging + global exception hook.

## Critical Patterns

**Control Access**: Use `ft.Ref`, never deep indexing
```python
cpu_text = ft.Ref[ft.Text]()
# In UI: ft.Text("0%", ref=cpu_text)
# Update: cpu_text.current.value = "35%"; cpu_text.current.update()
```

**Navigation**: NavigationRail.on_change only (see `main.py` `_load_view` mapping)
**Performance**: Prefer `control.update()` over `page.update()`
**Layout**: Use `expand=True` with standard Rows/Columns/Containers

**Performance Update Hierarchy**: 1. `control.update()` (best), 2. `ft.update_async()` (good), 3. `page.update()` (acceptable only for themes). Never use multiple `page.update()` in loops. Target <16ms for 60fps responsiveness.

## ServerBridge API

**Creation**: `from utils/server_bridge import create_server_bridge`
**Client Data**: `get_all_clients_from_db()` returns dicts with `{id, client_id, name, status, last_seen, files_count, total_size}`
**Files**: `get_files()`, `get_client_files(client_id)`, `delete_file()`, `download_file()` (mock mode writes temp files)
**Database**: `get_database_info()`, `get_table_data()`, `update_row()`, `delete_row()`
**Status/Logs**: `get_server_status[_async]`, `get_system_status`, `get_logs`.

## Development Commands

**Run**: `flet run -r main.py` (hot reload) or `python main.py`
**Debug**: Set `FLET_V2_DEBUG=true` for verbose logging
**Test**: `python -m pytest tests -v`. **Avoid running tests; they cannot accurately test Flet implementations.**
**Lint**: `pyright`, `pylint main.py views/ utils/`
**Codacy**: **Codacy checks are currently ignored. DO NOT USE CODACY.**

## Adding Views

1. Create `views/<name>.py` with `create_<name>_view(server_bridge, page, state_manager=None)`
2. Wire into NavigationRail in `main.py` (follow existing pattern)
3. Use `utils/mock_mode_indicator.py` for fallback UI hints

Example: `def create_my_view(server_bridge, page, state_manager=None) -> ft.Control: return ft.Column([...])` - Wire into NavigationRail in `main.py`.

## Code Quality Requirements

**CRITICAL**: After ANY file edit, run `codacy_cli_analyze` with `rootPath` set to workspace and `file` set to edited file path (per `.github/instructions/codacy.instructions.md`). Address any issues immediately. **Codacy checks are currently ignored. DO NOT USE CODACY.**

**References**: See patterns in `main.py`, `views/dashboard.py`, `utils/server_bridge.py`

## FletV2 – Copilot Instructions (project-specific)

This repo implements a clean Flet desktop app for managing an encrypted backup server. Work ONLY inside `FletV2/`. Favor “framework harmony”: use Flet’s built-ins, keep solutions simple, avoid custom infra that duplicates framework features.

### Architecture at a glance
- Entry: `main.py` builds `FletV2App(ft.Row)` with a NavigationRail and an AnimatedSwitcher content area.
- Views: Function-based creators in `views/` with the signature `def create_<name>_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control`.
- Server bridge: `utils/server_bridge.py` exposes a unified `ServerBridge`; without a real server it auto-falls back to `MockDataGenerator` (keep return shapes stable in both modes).
- Theming: `theme.py` defines Material 3 themes and helpers (`setup_modern_theme`, `toggle_theme_mode`).
- Debug/logging: `utils/debug_setup.py` sets enhanced logging + global exception hook.
- Config: `config.py` centralizes flags like `FLET_V2_DEBUG` and other constants.

### Golden patterns
- Views return a single `ft.Control`, focused and readable (~200–600 lines).
- Control access via `ft.Ref`, never deep index-chaining.
  - define: `cpu_text = ft.Ref[ft.Text]()` and `ft.Text("0%", ref=cpu_text)`
  - update: `cpu_text.current.value = "35%"; cpu_text.current.update()`
- Prefer `control.update()` over `page.update()` for performance.
- Navigation uses `NavigationRail.on_change` (see `main.py`); avoid custom routers.
- Layout uses `expand=True` with standard Rows/Columns/Containers.

### ServerBridge quick contract
- Live mode if initialized with `real_server_instance`; else automatic mock mode.
- Clients: `get_all_clients_from_db()/get_clients_async()` return normalized dicts with keys: `id`, `client_id`, `name`, `status`, `last_seen`, `files_count`, `total_size`.
- Files: `get_files[_async]`, `get_client_files(client_id)`, `delete_file[_async]`, `download_file[_async]` (mock writes a small file).
- Database: `get_database_info[_async]`, `get_table_data[_async]`, `update_row`, `delete_row`.
- Status/Logs: `get_server_status[_async]`, `get_system_status`, `get_logs`.
- Create via `from utils.server_bridge import create_server_bridge` (used in `main.py`). `ModularServerBridge` is a thin compatibility shim.

### Developer workflows
- Run app: `flet run -r main.py` or `python main.py`. Set `FLET_V2_DEBUG=true` for verbose logging.
- Tests: `python -m pytest tests -v` (see many focused tests in `tests/`). **Avoid running tests; they cannot accurately test Flet implementations.**
- Type/lint (if available locally): `pyright`, `pylint main.py views/ utils/`.
- Codacy analysis: After edits, run `codacy_cli_analyze` with rootPath set to the workspace and file set to the edited file, as required by the project rules in `.github/instructions/codacy.rules`. If the tool is unavailable, follow the troubleshooting steps in `.github/instructions/codacy.instructions.md` (reset MCP, check Copilot MCP settings, or contact Codacy support). **Codacy checks are currently ignored. DO NOT USE CODACY.**
- Use ripgrep (rg) to search for patterns more efficiently.

### Extending the UI
- Add `views/<name>.py` with `create_<name>_view(server_bridge, page: ft.Page, state_manager=None)`.
- Wire it into NavigationRail handling in `main.py` (follow existing `_load_view` mapping).
- Use `utils/mock_mode_indicator.py` patterns when surfacing fallback/mock context to users.

### Conventions and gotchas
- Cross-view state is optional via `state_manager` (created in `main.py` if present); otherwise update controls directly.
- Respect color/theme APIs from `theme.py`; call `setup_modern_theme(page)` during init.
- Maintain ServerBridge return shapes so views remain stable; mock mode must keep working.

### Examples to reference
- View signatures: `views/dashboard.py` et al.
- Server integration: `utils/server_bridge.py`.
- Theme usage: `theme.py`.
- Logging setup: `utils/debug_setup.py`.

These rules reflect current code, not aspirations. When in doubt, mirror patterns in `main.py`, `views/*`, and `utils/server_bridge.py`.

### Debugging

- When debugging JSON parsing errors, such as "Incorrect type. Expected 'object'., End of file expected.", ensure the JSON file has a valid structure, including the opening brace `{` for a JSON object. After correcting the file, validate it using a JSON tool (e.g., `python -m json.tool <file>`).
- When encountering the error "Unknown property 'globs' will be ignored.", review the relevant configuration files (e.g., `.codacy.yml` or similar) and ensure that the `globs` property is correctly defined and supported in the context where it is being used. Check for typos or syntax errors in the property name or its value. Consult the documentation for the tool or library that uses the `globs` property to verify its correct usage and compatibility. If the property is unsupported, remove it. After making the change, validate the file if needed (e.g., by checking for parsing errors). If Codacy analysis is required per project rules, run `codacy_cli_analyze` on this file with `rootPath` set to the workspace and `file` set to the edited file path. If the tool is unavailable, follow the troubleshooting steps in `.github/instructions/codacy.rules`. **Codacy checks are currently ignored.**
  - **Codacy checks are currently ignored. DO NOT USE CODACY.**
- Always fix all errors and warnings reported by linters and static analysis tools such as `pylint` and `sourcery`. When fixing errors and warnings, ensure that you are not breaking the code, or breaking/removing functionality. Do not remove useful comments and docstrings. Fix errors and warnings, do not delete problems. Use sequential thinking where you don't know what to do.
- When encountering the error "Text Control must be added to the page first", this indicates a Flet control lifecycle issue. Ensure that controls are properly added to the page before attempting to update them.
  - The solution is to defer subscription setup until after the view is constructed and attached to the page. This can be achieved by adding a deferred initialization pattern at the end of the view creation function.
- Ensure that the UI components use proper theme inheritance and are not explicitly overriding the theme colors. Use `ft.Colors` theme roles instead of manual color definitions.
- When addressing Sourcery warnings, adhere to best practices and ensure that the changes do not break the code or functionality. Functionality should remain the same.
- When a view receives `None` for the `state_manager`, handle it gracefully by either using the `server_bridge` directly or skipping state management operations. Implement null checks to avoid "TypeError: object NoneType can't be used in 'await' expression" errors.

### Security Considerations

- The `.claude.json` file may contain a GitHub Personal Access Token. Treat this token as a secret and handle it with CRITICAL severity. Ensure that the token is not exposed in logs or other publicly accessible locations. When setting the token, mask the value to prevent accidental disclosure (e.g., `set GITHUB_PERSONAL_ACCESS_TOKEN=****************************************`).
- **Secure handling of secrets**: Instead of hardcoding secrets, load them from environment variables (e.g., via `os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")` in Python code). For Flet apps, set them in your runtime environment or use a `.env` file with `python-dotenv`, but never commit `.env`.
- Update `config.py` to load secrets securely:

```python
# Add to config.py (after existing imports)
import os

# Existing pattern for non-secrets
DEBUG_MODE = os.environ.get('FLET_V2_DEBUG', 'false').lower() == 'true'

# New: Securely load secrets
GITHUB_TOKEN = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
# Optional: Validate presence in debug mode
if DEBUG_MODE and not GITHUB_TOKEN:
    print("Warning: GITHUB_PERSONAL_ACCESS_TOKEN not set")

# Other secrets (e.g., for server auth)
SERVER_API_KEY = os.environ.get('SERVER_API_KEY')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
```

- **Usage in Code:**
In any file (e.g., `server_bridge.py` or `main.py`):

```python
from config import GITHUB_TOKEN

if GITHUB_TOKEN:
    # Use the token securely (e.g., for API calls)
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    # Make authenticated request
else:
    # Fallback to mock mode or handle gracefully
    print("GitHub token not available, using mock data")
```

- **Environment Variables (Recommended for Local Development and Desktop Apps)**: Use environment variables to keep secrets out of code.
    - **How to Set Environment Variables:**
        - **Windows (PowerShell):** `set GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here`
        - **Windows (Command Prompt):** `set GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here`
        - **Persist across sessions:** Add to your system's environment variables via Control Panel > System > Advanced system settings > Environment Variables.
        - **For Flet apps:** Set them before running `flet run -r main.py` or `python main.py`.
- **GitHub Secrets (For CI/CD and Repository-Level Secrets)**: Use GitHub Secrets, which are encrypted variables stored at the repository or organization level, and accessible only in GitHub Actions workflows.
    - **How to Set GitHub Secrets:**
        1. Go to your repository on GitHub.
        2. Navigate to **Settings > Secrets and variables > Actions**.
        3. Click **New repository secret**.
        4. Name it (e.g., `GITHUB_PERSONAL_ACCESS_TOKEN`) and paste the value.
        5. In workflows (e.g., `.github/workflows/ci.yml`), access via `${{ secrets.GITHUB_PERSONAL_ACCESS_TOKEN }}`.
    - **Example GitHub Actions Workflow:**
        Create or update `.github/workflows/ci.yml`:

        ```yaml
        name: CI
        on: [push, pull_request]

        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - name: Set up Python
                uses: actions/setup-python@v4
              - name: Set up Python
                uses: actions/setup-python@v4
              - name: Install dependencies
                run: pip install -r requirements.txt
              - name: Run tests
                run: python -m pytest tests/
                env:
                  GITHUB_PERSONAL_ACCESS_TOKEN: ${{ secrets.GITHUB_PERSONAL_ACCESS_TOKEN }}
                  # Add other secrets as needed
        ```
    - **Usage in Workflows:**
        - Secrets are injected as environment variables in the runner.
        - Your code can access them via `os.environ.get()` as shown above.
        - For API calls in CI, use the secret directly in scripts.
- **Best Practices:**
    - Never hardcode secrets in code or config files.
    - Use `.env` files for local development (add `python-dotenv` to `requirements.txt` and load with `load_dotenv()` if using Python).
    - For production, set env vars in your deployment environment (e.g., via systemd, Docker, or cloud config).
    - Use repository secrets for repo-specific values; organization secrets for shared ones.
    - Rotate secrets regularly and revoke compromised ones immediately.
    - Limit secret scopes (e.g., read-only tokens for CI).
    - Always validate secrets exist before use, and log warnings (not the secrets themselves) in debug mode.
    - In tests, mock secrets or use test-specific env vars to avoid exposing real tokens.

### Implementation Verification

- When implementing new features or refactoring existing code against a detailed plan, always verify the actual implementation against the planned specifications. This includes:
    - Cross-checking the existence and functionality of specific methods (e.g., `stop_server_async()`, `get_recent_activity_async()`) in relevant files (e.g., `server_bridge.py`).
    - Validating the correct implementation of patterns (e.g., the presence and enforcement of a mandatory `state_manager` in views, the use of reactive updates).
    - Ensuring the creation and integration of new modules or utilities (e.g., `server_mediated_operations.py`, `persistent_mock_store.py`).
    - Confirming the existence of tests and validations for new functionality.
- If discrepancies are found between the plan and the implementation:
    - Update the plan document to accurately reflect the true status of the implementation.
    - Implement any missing elements incrementally, following the original plan as a guide.
    - Prioritize addressing critical missing elements (e.g., security handling, core server bridge methods).
- Documentation, especially progress tracking, must be accurate and consistent with the actual codebase state.
- After making any changes, always run `codacy_cli_analyze` on modified files with `rootPath` set to the workspace and `file` set to the file path, as required by project rules. Address any issues that arise immediately. **Codacy checks are currently ignored.**
  - **Codacy checks are currently ignored. DO NOT USE CODACY.**
- **Do NOT look at the plan to verify. Look at the code and compare it to the plan.**

### Simplification and Prioritization

- When implementing missing features, simplify "enhanced" features (e.g., cascading operations, reactive subscriptions) to achieve basic functionality first, aligning with framework harmony and avoiding over-engineering. Focus on core server bridge methods and basic state management.

#### Phase 1: Server Bridge Infrastructure (Priority: High)
- **Missing/Needs Simplification:**
    - `stop_server_async()`: Not implemented. Replace enhanced version with basic async shutdown simulation.
    - `get_recent_activity_async()`: Not implemented