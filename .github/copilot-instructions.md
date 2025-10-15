---
description: AI rules derived by SpecStory from the project AI interaction history

---
description: AI rules derived by SpecStory from the project AI interaction history
---

# Client-Server Encrypted Backup Framework – AI Field Guide
## Snapshot
- Production-grade encrypted backup stack combining Flet 0.28.3 GUI, Flask bridge, native C++ client, Python TCP server, and SQLite telemetry.
- Security envelope: RSA-1024 key exchange, AES-256-CBC streaming, CRC32 integrity, monotonic timestamping, structured logging.
- Designed for Windows-first deployments; PowerShell launchers enforce environment hygiene before Python spins up.
- All entry points (`main.py`, `server.py`, `start_with_server.py`, `start_integrated_gui.py`) must import `Shared.utils.utf8_solution` immediately or subprocess I/O degrades on Windows.
- `server_bridge` mediates GUI ↔ server calls and can fall back to a mock bridge when TCP 1256 is unavailable—guards required around async behaviors.
- Expect real server to run on TCP 1256, Flask bridge on HTTP 9090, Flet GUI exposed at http://localhost:8570 when launched via the PowerShell script.
- `defensive.db` stores normalized metadata; binary payloads land inside `python_server/server/received_files/`.
- Keep C++ and Python protocol definitions in sync; mismatches surface as handshake failures without graceful degrade.

## Architecture Flow
- `FletV2` GUI (Flet 0.28.3) → Flask bridge (`api_server`) → TCP server (`python_server/server.py`) → C++ client → encrypted storage in `defensive.db` and file drops in `python_server/server/received_files/`.
- PowerShell launcher seeds env vars, starts TCP server, then spawns GUI; mock bridge activates when TCP 1256 is unavailable.
- RSA-1024 bootstraps AES-256-CBC streams; CRC32 and monotonic timestamps back every payload.

## Directory Map
- `FletV2/`: GUI views, theming, and bridge adapters (`main.py`, `views/`, `utils/server_bridge.py`, `state_manager.py`, `theme.py`).
- `python_server/`: Core TCP server (`server.py`), protocol definitions, database ops, and worker pool wiring.
- `Shared/`: Cross-cutting helpers (`utf8_solution`, logging config, retry utilities, metrics collectors, `flet_log_capture.py`).
- `api_server/`: Flask bridge for HTTP fallback and integration with external tooling.
- `Client/`: Native C++ client implementing the same protocol enums; rebuild after protocol shifts.
- `scripts/` + PowerShell: Launchers, diagnostics, and combined build workflows.

## Component Highlights
- **State Manager**: Broadcasts state changes, theme updates, telemetry; clean up subscriptions in `dispose`.
- **Server Bridge**: Centralizes request/response handling; check `.success` before mutating UI.
# Client-Server Encrypted Backup Framework – AI Field Guide

## Mission Snapshot
- Production-grade encrypted backup stack combining a Flet 0.28.3 desktop GUI, a Flask bridge, a Python TCP server, a native C++ client, and SQLite telemetry.
- Security pipeline: RSA-1024 handshake seeds AES-256-CBC streams, CRC32 verifies payload integrity, timestamps use `time.monotonic()` to avoid clock drift, logging goes through `Shared/logging_config`.
- Windows-first deployment: PowerShell launchers prepare env vars, isolate the `flet_venv` virtual environment, then start the TCP server before launching the GUI.
- Every entry point (`FletV2/main.py`, `python_server/server/server.py`, `FletV2/start_with_server.py`, PowerShell scripts) must import `Shared.utils.utf8_solution` **before anything else** for reliable UTF-8 console I/O on Windows.
- GUI auto-detects server availability through `utils/server_bridge.py`. If TCP 1256 is offline, it falls back to a mock bridge; guard destructive actions and surface offline banners in that scenario.

## Architecture Big Picture
- **Flow**: FletV2 GUI → HTTP bridge in `api_server/` → TCP server (`python_server/server/server.py`) → native client (`Client/`) → encrypted storage in `defensive.db` and binaries under `python_server/server/received_files/`.
- **FletV2/**: feature views (`views/`), shared UI components (`utils/ui_components.py`), state management (`utils/state_manager.py`), theming (`theme.py`), diagnostics (`debug_dashboard.py`).
- **python_server/**: protocol handling (`protocol.py`), network server (`network_server.py`), database layer (`database.py` with robust pooling), file transfer logic, Health API, GUI integration glue.
- **Shared/**: UTF-8 bootstrap, logging setup, retry utilities, metrics collector, cross-cutting observability helpers.
- **api_server/**: Flask fallback for REST integration, used by automation or when the native TCP channel is unavailable.
- **Client/**: C++ implementation of the binary protocol; rebuild after protocol changes to keep enums and framing aligned.

## Directory Speed Tour
- `FletV2/main.py`: App host, NavigationRail, AnimatedSwitcher, theme bootstrap, bridge detection.
- `FletV2/views/*`: Each view exposes `create_<name>_view(server_bridge, page, state_manager)` returning `(control, dispose_fn, setup_fn)`.
- `FletV2/utils/server_bridge.py`: Real vs mock delegation, normalized responses (`success`, `data`, `error`, `mode`).
- `FletV2/utils/state_manager.py`: Event bus, progress tracking, async task scheduling (watch for disposal responsibilities).
- `python_server/server/database.py`: Connection pool with monitoring, DB schema operations, transaction helpers; always use `db_manager.get_connection()`.
- `python_server/server/network_server.py`: TCP listener, worker pool, request dispatching.
- `python_server/server/protocol.py`: Opcode definitions, frame parsing, CRC enforcement. Keep Python and C++ enums consistent.
- `Shared/utils/utf8_solution.py`: Do not remove; required for Windows stdout/stderr reliability.

## Environment & Tooling Essentials
- Python tooling is pinned inside `flet_venv\`; activate with `flet_venv\Scripts\Activate.ps1` before manual commands.
- Flet version **0.28.3** is expected; avoid APIs added later (e.g., no `SelectableText`, limited icon set). Use `ft.Text(selectable=True)` and check `ft.Icons` for availability.
- Required environment variables (PowerShell launch scripts set them):
  - `PYTHONNOUSERSITE=1` to avoid user-site contamination (common source of `pydantic_core` import errors).
  - `FLET_V2_DEBUG=1` for verbose GUI logging; disable for performance tests.
  - `FLET_NAV_SMOKE=1`, `FLET_DASHBOARD_DEBUG=1` to stress view navigation and metrics when diagnosing UI issues.
- Launch stack for smoke testing: `pwsh -File FletV2/start_with_server.ps1`. Script starts TCP server, waits for readiness, then launches GUI at http://localhost:8570.
- Manual commands from repo root:
  - `python python_server/server/server.py` (real TCP server)
  - `python api_server/cyberbackup_api_server.py` (Flask bridge)
  - `flet_venv\Scripts\python.exe FletV2/main.py` (GUI only)
  - `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release` (C++ client)

## Build, Format, Test
- Python lint & format: `ruff check .`, `ruff format --check .`, `flet_venv\Scripts\python.exe -m pylint FletV2 Shared python_server api_server`.
- Type safety: `pyright` (configured to respect repo exclusions once `pyrightconfig.json` is set).
- Unit & integration: `pytest -vv`, `pytest tests/test_protocol.py -vv` for handshake focus, `pytest tests/integration` after DB or protocol changes.
- Bytecode compilation: `python -m compileall FletV2/main.py` catches syntax issues not surfaced in linting.
- GUI validation: run PowerShell launcher and manually traverse Dashboard → Clients → Files → Database → Analytics; watch logs for warnings surfaced by `StateManager`.

## Data & Protocol Contract
- Frame layout (little-endian): 16-byte UUID | 1-byte protocol version | 2-byte opcode | 4-byte payload length | payload bytes | CRC32.
- Responses return version, status code, length, optional payload, optional checksum; maintain parity in `Client/include` and `python_server/server/protocol.py`.
- `transfer.info` must contain exactly three UTF-8 lines: `host:port`, username, absolute file path. `RealBackupExecutor` refuses non-existent paths or malformed files.
- Database: `defensive.db` holds normalized metadata. Binary payloads saved under `python_server/server/received_files/` using the hashed filename scheme.
- When adjusting schema, update migrations, fixture generators, converters delivering data to the GUI, and analytics dashboards simultaneously.

## Flet 0.28.3 Ground Rules
- Always call `page.run_task(my_async_fn)` with the coroutine **function**, never with `my_async_fn()` (raises `AssertionError`).
- Do not block the UI thread. Replace `time.sleep()` with `await asyncio.sleep()` or schedule via `page.run_task`.
- Use `control.update()` wherever possible. Reserve `page.update()` for global changes (theme, overlays) and never call it in tight loops.
- Attach controls before updating them. ListView updates before attachment trigger `ListView Control must be added to the page first`.
- Replace unsupported icons: e.g., `ft.Icons.SAVE_OUTLINED` instead of `SAVE_AS_OUTLINE`, `ft.Icons.DATASET` instead of `DATABASE`.
- Avoid `ft.Dropdown(height=...)`; height parameter is unsupported.
- Pair every `setup_fn` with a `dispose_fn` that cancels tasks, unsubscribes listeners (`StateManager` events, timers), and removes overlays like `FilePicker`.
- Use `ft.Ref` for cross-function control updates; avoid deep indexing or storing page references in module globals.
- Theme tokens live in `theme.py` (`PRONOUNCED_NEUMORPHIC_SHADOWS`, `GLASS_MODERATE`, gradient helpers). Use them to match neumorphic + glass styling.

## Common Breakages & Fix Patterns
- **UTF-8 corruption**: if console output shows mojibake, verify `Shared.utils.utf8_solution` import is first in the file.
- **ResponsiveRow column_spacing**: Flet 0.28.3 `ResponsiveRow` does NOT support `column_spacing` parameter. Use only `run_spacing` for vertical spacing between wrapped rows.
- **ft.Colors.SURFACE_VARIANT**: Does not exist in Flet 0.28.3. Use `ft.Colors.SURFACE` or `ft.Colors.GREY_100` instead. Valid Material 3 colors: `PRIMARY`, `SECONDARY`, `SURFACE`, `PRIMARY_CONTAINER`, `ON_SURFACE_VARIANT`.
- **Mock bridge confusion**: Many operations quietly no-op in mock mode. Check `server_bridge.is_real()` and surface warning banners before destructive actions (delete file, reset DB).
- **Database contention**: Use `DatabaseManager().get_connection()` context managers; never keep a connection past the with-block. Leaked cursors trigger `database is locked` under load.
- **Protocol mismatch**: When handshake fails, compare Python `OPCODE_*` values with `Client/include/ProtocolEnums.h`. Regenerate C++ client if enums diverge.
- **Analytics empty**: Ensure data fetch occurs inside the view `setup_fn` and only after controls attach. Mock mode sometimes returns zeroed metrics until `setup_subscriptions()` runs.
- **GUI freeze**: Occurs when awaiting sync methods or using `time.sleep()` in view code. Convert to async functions + `page.run_task` and use `await asyncio.sleep`.
- **Huge error counts in VS Code**: Usually stale language server state. Restart VS Code, clear `.vscode/.pylint.d/`, rerun `ruff` and `pyright` for authoritative errors.
- **`AttributeError: module 'flet' has no attribute 'SelectableText'`**: Use `ft.Text(selectable=True)`.
- **`TypeError: Text.__init__() got an unexpected keyword argument 'text_style'`**: Set `size`, `weight`, `color` directly on `ft.Text`.
- **`Dropdown.__init__()` height issue**: Remove the `height` keyword.
- **ListView background**: Wrap in `ft.Container(bgcolor=...)` because ListView lacks `bgcolor`.
- **`task` return type warnings**: In `settings.py`, `_schedule` must return `None`. Schedule coroutines without returning the task object.
- **`ListView Control must be added...`**: Delay updates until after `setup_fn` or guard with `if control.page:`.
- **`AttributeError: type object 'Icons' has no attribute 'SAVE_AS_OUTLINE'`**: Replace with `ft.Icons.SAVE_OUTLINED` (existing icon set).
- **`sum(1 for ...)` pattern**: Replace with `len([...])` to satisfy lint guidelines.

## View Development Best Practices (Learned from Settings View Redesign)

### Critical Initialization Patterns:
- **Always initialize all instance attributes in `__init__`** before they're referenced in `build()` or helper methods. Missing attributes cause `AttributeError` at runtime.
  - Example: `_autosave_ref` must be created in `__init__` if referenced in `_build_status_bar()`.
  - Use `ft.Ref[ft.ControlType]()` pattern for controls that need to be referenced before the view is built.

- **Prefer dynamic calculation over stored state** for derived values:
  - ❌ Bad: Store validation errors in `self._settings_errors` and try to keep it synchronized
  - ✅ Good: Calculate `validation_errors = self._collect_validation_errors()` on-the-fly when needed
  - Reason: Eliminates state synchronization bugs and makes code more maintainable

### UI Simplification Principles:
- **Simpler is better**: When redesigning views, remove complexity rather than adding it
  - Heavy gradients, multiple shadows, and complex decorations increase code complexity and maintenance burden
  - Clean borders, subtle backgrounds, and simple layouts are easier to debug and modify

- **Follow community patterns**: Research Flet examples and use established patterns
  - ListTile-style rows for settings (label left/top, control right/below)
  - Clean section headers with simple dividers
  - Subtle borders instead of heavy card decorations
  - Professional apps favor minimalism over decoration

- **One responsibility per component**:
  - Status bars should show status, not duplicate functionality of action buttons
  - Section cards should group related fields, not try to be decorative hero banners
  - Keep validation, display, and data management separate

### Common Redesign Mistakes:
- **Removing UI elements before updating references**: When removing hero banners or complex components, search the entire file for references to their child elements
- **Assuming state exists**: Never reference `self.attribute` without initializing it in `__init__` or checking if it exists
- **Changing too much at once**: Make incremental changes and test after each modification
- **Breaking existing patterns**: If other views use a pattern successfully, reuse it rather than inventing new approaches

### Testing After Changes:
1. Always run `python -m compileall <file>` to catch syntax errors
2. Actually launch the app and navigate to the changed view
3. Check console output for AttributeError or runtime exceptions
4. Test all tabs/sections if the view has multiple states
5. Verify autosave, validation, and other dynamic features still work

### Space-Efficient Layout Patterns (Compact Design):
- **Horizontal label+control layout**: For forms and settings, use `Row([Container(Text(label), width=fixed), control])` instead of vertical `Column([Text(label), control])` stacking
  - Example: `Row([Container(Text("Port", size=13), width=140), TextField(expand=True)], spacing=10)`
  - Saves 30-40px per field by eliminating vertical stacking
  - Fixed label width (120-150px) ensures alignment across all fields

- **Use tooltips over visible descriptions**: Set `control.tooltip = description` instead of adding a separate `Text(description)` control
  - Saves 20-25px per field that has helper text
  - Follows Material Design 3 guidelines for progressive disclosure

- **Compact padding values**: Use smaller padding for space-constrained views
  - ListView: `padding=ft.padding.all(10-12)` instead of 20px
  - Field rows: `vertical=6-8` instead of 14-16px
  - Section margins: `bottom=10-12` instead of 18-20px
  - Icon/text spacing: `spacing=6-10` instead of 12-16px

- **Smaller fonts and icons for secondary elements**:
  - Status text: 11px instead of 12-13px
  - Status icons: 14-16px instead of 18-20px
  - Section headers: 14px instead of 16-18px

- **When to use compact layout**:
  - ✅ Settings views with many fields (need to fit without scrolling)
  - ✅ Forms with 5+ input fields
  - ✅ Dashboard cards with multiple data points
  - ❌ Landing pages or marketing content (needs breathing room)
  - ❌ Single-field dialogs (compact not necessary)

- **Responsive considerations**: Add breakpoints to switch between horizontal and vertical layouts based on window width
  - Horizontal layout: width > 800px
  - Vertical layout: width ≤ 800px (mobile/narrow windows)

## Security & Compliance
- Never commit private keys or credentials. Key rotation scripts live under `scripts/`; document runs in `security_notes.md`.
- Store secrets in environment variables; sanitize logs with `StructuredLogger`. Avoid `print()` for anything beyond quick debugging and remove them before PR.
- AES path must use 256-bit keys and fresh IV per chunk; verify via integration tests after touching crypto modules.
- After editing dependencies or adding new packages, run `codacy_cli_analyze --root-path . --tool trivy` once Codacy MCP becomes available.

## Release & Ops Checklists
- **Pre-commit**: `ruff check`, `ruff format --check`, `pytest -vv`, C++ rebuild, `python -m compileall FletV2/main.py`, GUI smoke.
- **Pre-release**: Full E2E transfer (create `transfer.info`, send file, confirm DB entry and CRC), review analytics dashboards, archive logs + SQLite snapshots.
- **Incident response**: Collect `server.log`, `defensive.db` copy, `received_files` artifacts, `transfer.info`, and GUI logs from `FletV2/logs/`.
- **Protocol bump**: Update Python + C++ enums, document change in `Protocol_Change_Log.md`, rebuild client, update tests, announce to team.
- **Schema changes**: Sync migrations, DB init scripts, GUI forms, analytics transformers; update `DATABASE_VIEW_FIX_SUMMARY.md`.

## Diagnostics Toolkit
- `python python_server/server/server.py --dry-run` validates configuration without accepting traffic.
- `python FletV2/debug_dashboard.py` renders dashboard with mock metrics.
- `python scripts/check_db.py` inspects `defensive.db` integrity and schema drift.
- `python debug_full_flow.py` walks through mock flows for quick manual validation.
- `rg "page\.update" FletV2` locates heavy UI updates to minimize redraws.
- `pytest tests/test_async_patterns.py` highlights lingering blocking calls (watch for `time.sleep`).

## Documentation Hygiene
- Update `FletV2_Fix_Verification_Report.md`, `ANALYTICS_VIEW_FIXES.md`, `Protocol_Change_Log.md`, and `FletV2_Completion_Summary.md` when you touch the corresponding subsystems.
- Add play-by-play notes in `AI-Context/` for architectural shifts so future agents ramp quickly.
- Keep diagrams and specs in `important_docs/` aligned with code changes.

## Styling & UX Expectations
- Preserve neumorphic and glassmorphism treatments: use theme helpers, consistent blur (10–14px) and opacity (0.08–0.18).
- Follow 8px spacing grid; prefer Flet native spacing parameters over filler containers.
- Keep KPI cards actionable (dashboard cards navigate to relevant views). Update `views/dashboard.py` and `views/clients.py` cohesively when altering navigation hooks.
- Maintain accessibility: ensure color contrast using theme palette, keep focus indicators enabled, avoid text truncation without tooltips.

## When Things Go Sideways
- **Blank/gray view**: Confirm AnimatedSwitcher `setup_fn` executed after attachment; add `await asyncio.sleep(0.25)` post-transition before editing controls.
- **Mock banner missing**: `server_bridge` must publish state to `StateManager`; ensure view registers for bridge events in `setup_fn`.
- **Database view freeze**: Replace DataTable with ListView + `themed_card` combos; batch updates to avoid frame drops.
- **Native client hang**: Regenerate `transfer.info`, confirm server listening on 1256, verify handshake version in `protocol.py`.
- **Retry storms**: Check `Shared/metrics_collector` output; throttle operations via retry decorator backoff parameters.
- **Analytics zeros**: Kick off data fetch with `page.run_task(fetch_fn)`, guard against `None`, ensure UI binds to `StateManager` updates.
- **Huge files**: `views/enhanced_logs.py`, `views/database_pro.py`, `views/dashboard.py`, `main.py` exceed 1k LOC. When modifying them, favor extraction of helpers into `utils/` while keeping imports consistent with relative→absolute fallback pattern mandated by the guide.

## Coding Style & Patterns
- Prefer `with contextlib.suppress(Exception):` over bare except-pass.
- Replace bare `except:` with `except Exception as exc:` and log context.
- Avoid deep nesting; break up long coroutines into helpers, especially in view modules.
- Use `len()` for counting, `any()` / `all()` for membership checks instead of generator sums.
- Keep imports using `try: from . import module` / `except ImportError: from module import ...` for cross-context compatibility.
- Limit `page.update()` usage; log counts if you need to audit for performance regressions.

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