---
description: AI rules derived by SpecStory from the project AI interaction history

---

# Client-Server Encrypted Backup Framework – AI Field Guide

## Mission Snapshot
- Production-grade encrypted backup stack combining Flet 0.28.3 desktop GUI, Flask bridge, Python TCP server, native C++ client, and SQLite database.
- Security pipeline: RSA-1024 handshake seeds AES-256-CBC streams, CRC32 verifies payload integrity, timestamps use `time.monotonic()`, structured logging via `Shared/logging_config`.
- Windows-first deployment: PowerShell launchers prepare environment, activate `flet_venv`, start TCP server, then launch GUI.
- **CRITICAL**: All entry points must import `Shared.utils.utf8_solution` **before anything else** for reliable UTF-8 console I/O on Windows.
- Direct Python method integration: GUI creates BackupServer instance and calls methods directly (no HTTP API overhead).
- Network server runs on TCP 1256 for C++ clients, Flask bridge on HTTP 9090 for web GUI, Flet GUI as desktop app.
- `defensive.db` stores metadata; binary files in `python_server/server/received_files/`.

## Architecture Big Picture
- **Flow**: FletV2 GUI creates BackupServer instance directly → ServerBridge delegates to Python methods → C++ client connects via TCP 1256 → encrypted storage in `defensive.db` and files in `python_server/server/received_files/`.
- **FletV2/**: Feature views (`views/`), shared UI components (`utils/`), ServerBridge for server integration, advanced theming (`theme.py`).
- **python_server/**: BackupServer main class, network layer (`network_server.py`), database pool (`database.py`), protocol handling (`protocol.py`).
- **api_server/**: Flask bridge for C++ client web GUI, REST endpoints for external automation.
- **Client/**: C++ implementation of binary protocol; rebuild when protocol changes.
- **Shared/**: UTF-8 bootstrap, logging config, retry utilities, metrics collection.

## Critical Integration Patterns (Updated October 2025)

### 🚨 CRITICAL: Async/Sync Integration & Deadlock Prevention
**99% of GUI freezes come from blocking calls in async functions**. Dashboard deadlock (24 Oct 2025) was caused by `server_bridge.is_connected()` called from async context.

```python
# ❌ WRONG - Causes deadlock/freeze
async def _apply_snapshot(snapshot):
    status = server_bridge.is_connected()  # BLOCKS EVENT LOOP!

# ❌ ALSO WRONG - Direct await on sync method
async def load_data():
    result = await bridge.get_clients()  # FREEZE if get_clients() is sync!

# ✅ CORRECT - Use run_sync_in_executor for ALL sync server calls
async def load_data():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_clients)

# ✅ BETTER - Use helper from async_helpers
from FletV2.utils.async_helpers import run_sync_in_executor
async def load_data():
    result = await run_sync_in_executor(bridge.get_clients)
```

**Deadlock Prevention Rules:**
1. **NEVER** call `server_bridge.is_connected()` from async functions - it can block
2. **NEVER** call ANY `server_bridge.*()` sync method directly from async code
3. **ALWAYS** wrap with `run_sync_in_executor()` or use `_async` variant
4. **PREFER** snapshot data over live queries (faster, non-blocking)
5. **ADD** `await asyncio.sleep(0)` before `.update()` calls to yield event loop
6. **ServerBridge.is_connected()** now has 1-second cache - still avoid calling from async

**See:** `AI-Context/DASHBOARD_DEADLOCK_FIX_24OCT2025.md` for full post-mortem

### The 5-Section Pattern for Views
All new views must follow the 5-section architecture (see `FletV2/architecture_guide.md`):
1. **Data Fetching** - Async wrappers for ServerBridge calls with `run_in_executor`
2. **Business Logic** - Pure functions for filtering, calculations, exports (testable)
3. **UI Components** - Flet control builders (cards, buttons, containers)
4. **Event Handlers** - User interaction handlers (clicks, changes, form submissions)
5. **Main View** - View composition, lifecycle, and public API

### ServerBridge Direct Method Pattern
- **NO API calls** - ServerBridge delegates directly to BackupServer Python methods
- **Data conversion** - Handles BLOB UUID ↔ string conversions automatically
- **Structured responses** - Always returns `{'success': bool, 'data': Any, 'error': str}`
- **No mock data** - Mock mode returns empty structures, not fabricated data

## Environment & Tooling Essentials
- Python tooling pinned in `flet_venv\`; activate with `flet_venv\Scripts\Activate.ps1` before manual commands.
- Flet version **0.28.3** is required; avoid newer APIs (no `SelectableText`, limited icons). Use `ft.Text(selectable=True)` instead.
- **CRITICAL environment variables** (PowerShell launchers set these automatically):
  - `PYTHONNOUSERSITE=1` - Prevents user-site package conflicts (common source of `pydantic_core` errors)
  - `CYBERBACKUP_DISABLE_INTEGRATED_GUI=1` - Disable server's embedded GUI, use FletV2 instead
  - `FLET_V2_DEBUG=1` - Verbose GUI logging for debugging
  - `FLET_DASHBOARD_DEBUG=1` - Dashboard debugging output
- **Launch workflows**:
  - **Recommended**: `pwsh -File FletV2/start_with_server.ps1` - Starts server + GUI
  - **Development**: `python FletV2/start_with_server.py` - Manual server start
  - **C++ client build**: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release`

## Development Workflow
- **Lint & Format**: `ruff check FletV2 Shared python_server api_server` and `ruff format FletV2 Shared python_server api_server`
- **Type checking**: `pyright` (configured in `pyrightconfig.json`, excludes `python_server/`)
- **Testing**: `pytest tests/` - focus on business logic and protocol tests
- **Syntax validation**: `python -m compileall FletV2/main.py` catches issues linters miss
- **GUI smoke test**: Run PowerShell launcher, navigate Dashboard → Clients → Files → Database → Analytics

## Critical Database Patterns (Updated October 2025)
- **Always use connection pooling**: `with db_manager.get_connection() as conn:`
- **Database-first operations**: Modify database before memory to prevent phantom records
- **Retry decorators**: All database methods must use `@retry` decorator for `sqlite3.OperationalError`
- **Input validation**: Centralized validation patterns (see `server.py` lines 857-877)
- **Time calculations**: Use `time.monotonic()` never `time.time()` for durations

## Data & Protocol Contract
- **Frame layout** (little-endian): 16-byte UUID | 1-byte protocol version | 2-byte opcode | 4-byte payload length | payload bytes | CRC32
- **Protocol sync**: Keep Python (`python_server/server/protocol.py`) and C++ (`Client/include/ProtocolEnums.h`) definitions identical
- **transfer.info**: Exactly three UTF-8 lines - `host:port`, username, absolute file path
- **Database**: `defensive.db` stores metadata; binary files in `python_server/server/received_files/` using hashed naming
- **Schema changes**: Update migrations, GUI converters, and analytics simultaneously

## Key Database Tables
- **clients**: id, client_id (UUID), name, created_at, last_seen, total_files, total_bytes
- **files**: id, client_id FK, path_hash, original_name, size_bytes, checksum_crc32, stored_at
- **transfers**: id, file_id FK, status, started_at, completed_at, duration_ms, failure_reason
- **alerts**: id, severity, component, message, created_at, acknowledged_at
- **telemetry**: retry counters, queue depth, worker_pool metrics for historical analytics

## Flet 0.28.3 Ground Rules
- **ALWAYS call** `page.run_task(my_async_fn)` with the coroutine **function**, never `my_async_fn()` (raises `AssertionError`)
- **NEVER block UI thread**: Replace `time.sleep()` with `await asyncio.sleep()` or schedule via `page.run_task`
- **Use targeted updates**: `control.update()` wherever possible; reserve `page.update()` for global changes (theme, overlays)
- **Attach before updating**: ListView updates before attachment trigger "ListView Control must be added to the page first"
- **Icon availability**: Check `ft.Icons` - use `SAVE_OUTLINED` instead of `SAVE_AS_OUTLINE`, `DATASET` instead of `DATABASE`
- **Avoid unsupported params**: `ft.Dropdown(height=...)` is unsupported; `ResponsiveRow` does NOT support `column_spacing`
- **Proper cleanup**: Every `setup_fn` needs `dispose_fn` that cancels tasks, unsubscribes listeners, removes overlays
- **Theme system**: All tokens in `theme.py` (`PRONOUNCED_NEUMORPHIC_SHADOWS`, `GLASS_MODERATE`) - use them for consistent styling

## Critical Anti-Patterns (Updated October 2025)
- **❌ NEVER await sync methods**: `result = await bridge.get_clients()` causes permanent freeze
- **✅ ALWAYS use run_in_executor**: `result = await loop.run_in_executor(None, bridge.get_clients)`
- **❌ NEVER use `time.sleep()`** in async code: causes UI freeze
- **✅ ALWAYS use `await asyncio.sleep()`** for delays
- **❌ NEVER call `asyncio.run()`** inside Flet: event loop already running
- **✅ ALWAYS add diagnostic logging** to identify freeze points

## View Development Best Practices (October 2025)

### Critical Initialization Patterns:
- **Always initialize all instance attributes in `__init__`** before they're referenced in `build()` or helper methods
- **Use `ft.Ref[ft.ControlType]()` pattern** for controls that need to be referenced before the view is built
- **Prefer dynamic calculation over stored state** for derived values to eliminate state synchronization bugs

### UI Simplification Principles:
- **Simpler is better**: Remove complexity rather than adding it
- **Follow community patterns**: ListTile-style rows, clean section headers, subtle borders
- **One responsibility per component**: Status bars show status, action buttons handle actions

### Space-Efficient Layout Patterns:
- **Horizontal label+control layout**: Use `Row([Container(Text(label), width=fixed), control])` instead of vertical stacking
- **Use tooltips over descriptions**: `control.tooltip = description` instead of separate `Text(description)` control
- **Compact padding values**: ListView `padding=ft.padding.all(10-12)`, field rows `vertical=6-8px`
- **Responsive breakpoints**: Horizontal layout >800px, vertical layout ≤800px

## Common Error Patterns & Solutions
- **UTF-8 corruption**: Verify `Shared.utils.utf8_solution` import is first in the file
- **GUI freeze**: Check for `await bridge.method()` calls - wrap with `run_in_executor`
- **Database locks**: Use `with db_manager.get_connection() as conn:` context managers
- **Protocol mismatch**: Compare Python `OPCODE_*` with `Client/include/ProtocolEnums.h`
- **Mock bridge confusion**: Check `server_bridge.is_real()` before destructive actions
- **AttributeError**: Ensure all attributes initialized in `__init__` before use
- **ListView errors**: Delay updates until after `setup_fn` or guard with `if control.page:`

## Known Flet 0.28.3 Limitations
- **No `SelectableText`**: Use `ft.Text(selectable=True)`
- **No `text_style` parameter**: Set `size`, `weight`, `color` directly on `ft.Text`
- **No `Dropdown(height=...)`**: Remove height parameter
- **No `ResponsiveRow(column_spacing=...)`**: Use only `run_spacing`
- **No `ft.Colors.SURFACE_VARIANT`**: Use `ft.Colors.SURFACE` or `ft.Colors.GREY_100`
- **Missing icons**: Use `SAVE_OUTLINED` instead of `SAVE_AS_OUTLINE`, `DATASET` instead of `DATABASE`

## Security & Compliance
- Never commit private keys or credentials. Key rotation scripts in `scripts/`; document runs in `security_notes.md`
- Store secrets in environment variables; sanitize logs with `StructuredLogger`. Avoid `print()` for debugging
- AES must use 256-bit keys and fresh IV per chunk; verify via integration tests after crypto changes
- After dependency changes, run `codacy_cli_analyze --root-path . --tool trivy` when Codacy MCP is available

## Release & Ops Checklists
- **Pre-commit**: `ruff check`, `ruff format --check`, `pytest -vv`, C++ rebuild, `python -m compileall FletV2/main.py`, GUI smoke test
- **Pre-release**: Full E2E transfer (create `transfer.info`, send file, confirm DB entry and CRC), review analytics, archive logs + SQLite snapshots
- **Incident response**: Collect `server.log`, `defensive.db` copy, `received_files` artifacts, `transfer.info`, GUI logs from `FletV2/logs/`
- **Protocol bump**: Update Python + C++ enums, document in `Protocol_Change_Log.md`, rebuild client, update tests
- **Schema changes**: Sync migrations, DB init scripts, GUI forms, analytics transformers; update `DATABASE_VIEW_FIX_SUMMARY.md`

## Development Tools & Diagnostics
- **Configuration validation**: `python python_server/server/server.py --dry-run`
- **Dashboard testing**: `python FletV2/debug_dashboard.py`
- **Database inspection**: `python scripts/check_db.py`
- **Full flow validation**: `python debug_full_flow.py`
- **UI optimization**: `rg "page\.update" FletV2` to locate heavy UI updates
- **Async pattern testing**: `pytest tests/test_async_patterns.py` to find blocking calls

## Documentation & Code Quality
- Update `FletV2_Fix_Verification_Report.md`, `ANALYTICS_VIEW_FIXES.md`, `Protocol_Change_Log.md` when touching subsystems
- Add architectural notes in `AI-Context/` for major changes
- Keep diagrams in `important_docs/` aligned with code changes
- **Code style**: Use `with contextlib.suppress(Exception):`, avoid bare `except:`, prefer `len()` over generator sums
- **Import patterns**: Use relative→absolute fallback pattern for cross-context compatibility
- **Performance**: Limit `page.update()` usage, log counts to audit regressions

## Styling & UX Standards
- Preserve neumorphic and glassmorphism treatments: use theme helpers, consistent blur (10–14px) and opacity (0.08–0.18)
- Follow 8px spacing grid; prefer Flet native spacing parameters
- Keep KPI cards actionable (dashboard cards navigate to relevant views)
- Maintain accessibility: color contrast, focus indicators, tooltips for truncated text

## Troubleshooting Common Issues
- **Blank/gray view**: Confirm AnimatedSwitcher `setup_fn` executed after attachment; add `await asyncio.sleep(0.25)` post-transition
- **Missing mock banner**: Ensure `server_bridge` publishes state to `StateManager` in `setup_fn`
- **Database view freeze**: Replace DataTable with themed cards; batch updates
- **Native client hang**: Regenerate `transfer.info`, confirm server listening on 1256, verify handshake version
- **Retry storms**: Check `Shared/metrics_collector` output; throttle via retry decorator
- **Analytics showing zeros**: Kick off data fetch with `page.run_task(fetch_fn)`, guard against `None`
- **Large files**: When modifying `views/enhanced_logs.py`, `views/database_pro.py`, `views/dashboard.py`, extract helpers into `utils/`

## ServerBridge API Cheatsheet
- `get_all_clients_from_db()` returns list of dicts; expect keys `id`, `client_id`, `name`, `status`, `last_seen`, `files_count`, `total_size`
- `get_files()` enumerates every record; pass filtering to the view to avoid extra server calls
- `get_client_files(client_id)` is synchronous; wrap in `page.run_task` to keep UI responsive
- `download_file(file_id)` emits bytes; real bridge streams to disk, mock writes into temp directory
- `delete_file(file_id)` cascades to metadata tables; confirm `.success` and refresh UI via `StateManager.publish`
- `get_database_info()` returns schema summary; hydrate DataTable headings from the `columns` list
- `update_table_row(table_name, row_id, payload)` is tolerant of partial payloads but requires matching column names
- `get_logs(offset, limit)` and `get_log_stats()` power the enhanced logs view; mock mode uses JSON fixtures
- `get_server_status_async()` pairs with `get_system_metrics()` to drive dashboard gauges; expect `uptime`, `active_clients`, `queue_depth`
- `start_server()` and `stop_server()` exist for integration testing; no-ops in mock mode but return informative `.message`

## Database Quick Reference
- **Connection pattern**: `with db_manager.get_connection() as conn:`
- **CRUD operations**: Use helper methods in `database.py` - never raw SQL
- **Transaction handling**: Use `conn.execute()` for multiple statements, commit manually
- **UUID handling**: Convert between string and BLOB formats using `blob_to_uuid_string()` and `uuid_string_to_blob()`
- **Time calculations**: Always use `time.monotonic()` for durations, never `time.time()`
- **Retry pattern**: All database methods must use `@retry` decorator for `sqlite3.OperationalError`

## Critical Testing Commands
```bash
# Lint and format
ruff check FletV2 Shared python_server api_server
ruff format FletV2 Shared python_server api_server

# Type checking
pyright  # Respects pyrightconfig.json exclusions

# Protocol testing
pytest tests/test_protocol.py::test_handshake_success -vv

# Database testing
pytest tests/test_comprehensive_database.py -v

# Async pattern validation
pytest tests/test_async_patterns.py -v

# GUI smoke test
pwsh -File FletV2/start_with_server.ps1
```

## Quick Reference Commands

### Development Workflow
```bash
# Start full system (recommended)
pwsh -File FletV2/start_with_server.ps1

# Start GUI only (development mode)
python FletV2/start_with_server.py

# Build C++ client
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build --config Release

# Code quality checks
ruff check FletV2 Shared python_server api_server
ruff format FletV2 Shared python_server api_server
pyright
python -m compileall FletV2/main.py
```

### Environment Setup
```bash
# Activate virtual environment
flet_venv\Scripts\Activate.ps1

# Set critical environment variables
$env:PYTHONNOUSERSITE = "1"
$env:CYBERBACKUP_DISABLE_INTEGRATED_GUI = "1"
$env:FLET_V2_DEBUG = "1"
```

## Final Reminders
- **ALWAYS summarize findings** before large fixes; stakeholders expect quick brief referencing component + command run
- **Re-run lint/tests** after edits even if changes seem trivial; `ruff` catches stray imports quickly
- **Remove temporary prints** and ensure structured logging includes `client_id`, `opcode`, durations
- **Keep Codacy MCP results** attached to PRs once toolchain is restored; for now document attempts if CLI is unavailable
- **Update this guide** whenever workflows, protocol, or architecture boundaries move so future agents inherit accurate playbooks

## Quick Reference Commands

## ServerBridge API Cheatsheet
- `get_all_clients_from_db()` returns list of dicts; expect keys `id`, `client_id`, `name`, `status`, `last_seen`, `files_count`, `total_size`.
- `get_files()` enumerates every record; pass filtering to the view to avoid extra server calls.
- `get_client_files(client_id)` is synchronous; wrap in `page.run_task` to keep UI responsive.
- `download_file(file_id)` emits bytes; real bridge streams to disk, mock writes into temp directory defined in `mock_database_simulator.py`.
- `delete_file(file_id)` cascades to metadata tables; confirm `.success` and refresh UI via `StateManager.publish`.
- `get_database_info()` returns schema summary; hydrate DataTable headings from the `columns` list.
- `update_table_row(table_name, row_id, payload)` is tolerant of partial payloads but requires matching column names.
- `get_logs(offset, limit)` and `get_log_stats()` power the enhanced logs view; mock mode uses JSON fixtures under `FletV2/data/`.
- `get_server_status_async()` pairs with `get_system_metrics()` to drive dashboard gauges; expect `uptime`, `active_clients`, `queue_depth`.
- `start_server()` and `stop_server()` exist for integration testing; no-ops in mock mode but return informative `.message`.

## Database Tables Overview
- `clients`: id, client_id (UUID), name, created_at, last_seen, total_files, total_bytes.
- `files`: id, client_id FK, path_hash, original_name, size_bytes, checksum_crc32, stored_at.
- `transfers`: id, file_id FK, status, started_at, completed_at, duration_ms, failure_reason.
- `alerts`: id, severity, component, message, created_at, acknowledged_at.
- `telemetry`: captures retry counters, queue depth, worker_pool metrics for historical dashboards.
- Use the helper `database_migrations.py` to apply schema upgrades; never hand-edit `defensive.db`.
- When introducing new tables, update ORM-like accessors in `database.py` and converters in `server_bridge.py`.

## Testing Scenarios Worth Automating
- **Handshake regression**: `pytest tests/test_protocol.py::test_handshake_success` ensures RSA/AES pipeline intact.
- **Mock bridge CRUD**: `pytest tests/test_mock_server_bridge.py -k crud` for client/file operations without server.
- **Database smoke**: `pytest tests/test_comprehensive_database.py` verifies pooling, migrations, and stats functions.
- **Async guardrails**: `pytest tests/test_async_patterns.py` catches accidental `time.sleep` usage or missing awaits.
- **GUI snapshot**: use Playwright MCP (once enabled) to capture dashboard after initial load; confirm cards, charts, and banners render.
- **C++ client integration**: after building, run `EncryptedBackupClient.exe --batch tests/artifacts/transfer.info` and check server logs for CRC confirmation.

## Known Error Messages & Resolutions
- `sqlite3.OperationalError: database is locked` → ensure all DB writes run inside `with db_manager.get_connection()` and commit quickly.
- `ValueError: AnimatedSwitcher requires a child control` → view returned `None`; verify `create_*_view` returns actual `ft.Control`.
- `AttributeError: 'NoneType' object has no attribute 'page'` → control updated before attachment; add guard `if control and control.page`.
- `OSError: [WinError 10048] Address already in use` → port 1256 busy; kill stray python instances or adjust `server_port` in config.
- `RuntimeError: Task pending after dispose` → cancel background tasks in `dispose_fn` using stored cancellation tokens.
- `httpx.ConnectError` in real bridge mode → confirm `REAL_SERVER_URL`, TLS settings, and network reachability before retrying.
- `CRC mismatch` in transfer logs → cross-check AES key negotiation, regenerate client binary if protocol version diverges.
- `PermissionError` writing to `received_files` → ensure process has write permissions; PowerShell script sets ACLs during launch.

## Integration & External Dependencies
- Flask bridge listens on HTTP 9090; endpoints defined in `api_server/routes`. Use for REST automation or remote dashboards.
- vcpkg toolchain pinned under `vcpkg/`; run `git submodule update --init` if headers missing.
- Observatory integration uses optional `Shared/observability.py`; when absent, stub classes in `database.py` keep logging silent.
- `scripts/one_click_build_and_run.ps1` orchestrates build + launch; keep it updated when CLI options evolve.
- Playwright MCP and Factory CLI integrations documented in `important_docs/mcp_playbooks.md`; follow those to capture UI evidence for QA.

## MCP & Codacy Expectations
- After every edit, attempt `codacy_cli_analyze --root-path . --file <path>`; if command unavailable, log the failure in PR notes.
- When adding dependencies or touching security-sensitive code, rerun Codacy with `--tool trivy` to surface CVEs.
- MCP server configuration stored in `.vscode/mcp.json`; back up before editing and wrap `npx` commands with `cmd /c` on Windows.
- Capture screenshots via Playwright MCP before and after major UI adjustments to validate visual parity.

## Collaboration Tips
- Document major fixes in the appropriate report file (`FletV2_Critical_Issues_Report.md`, `ASYNC_SYNC_FIX_REPORT.md`, etc.).
- Reference ticket IDs or GitHub issues in comments sparingly; rely on structured logging and commit messages instead of inline TODOs.
- When pairing with other agents, add scratch notes under `AI-Context/` and clean them once the fix lands.
- Use `Duplication_mindset.md` as a reminder of anti-duplication strategy; refactor repeated patterns into utilities promptly.

## Frequently Overlooked Tasks
- Remove stale `transfer.info` between manual runs to avoid replaying outdated jobs.
- Clear `python_server/server/logs/` after large test batches; the enhanced logs view reads newest files only.
- Sync theme updates in `theme.py` with `ui_components.py`; mismatches cause inconsistent neumorphic shadows.
- Track Flet version drift—if upgrading past 0.28.3, audit every view for API changes before deploying.

## Future Enhancement Backlog (Context Only)
- Planned analytics refresh pipeline outlined in `ANALYTICS_VIEW_ENHANCEMENT_SUMMARY.md`.
- Settings re-architecture detailed in `CENTRALIZED_ERROR_BOUNDARY_SYSTEM.md` and `settings_refactor_notes.md` (if present).
- Pending export optimizations captured in `ENHANCED_OUTPUT_IMPLEMENTATION_SUMMARY.md`; review before touching log export routines.


## Final Reminders
- Always summarize findings before large fixes; stakeholders expect a quick brief referencing component + command run.
- Re-run lint/tests after edits even if changes seem trivial; `ruff` catches stray imports quickly.
- Remove temporary prints and ensure structured logging includes `client_id`, `opcode`, durations.
- Keep Codacy MCP results attached to PRs once the toolchain is restored; for now document attempts if the CLI is unavailable.
- Update this guide whenever workflows, protocol, or architecture boundaries move so future agents inherit accurate playbooks.