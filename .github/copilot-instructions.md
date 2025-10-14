---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

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
- **Metrics Collector**: Records counter/timer data for retries and throughput; inspect when diagnosing network issues.
- **Retry Decorator**: Wraps unstable I/O, logging attempts with context for postmortems.
- **Theme Toolkit**: Supplies neumorphic/glass presets; avoid ad-hoc styling.
- **DB Manager**: Manages pooled SQLite connections; request via `db_manager.get_connection()` only.
- **Log Viewer (`enhanced_logs.py`):** Implements a sophisticated log viewer with neomorphic Material 3 design, featuring advanced search, filtering, pagination. Key components include `LogCard`, `NeomorphicShadows`, and a dataclass-based `LogsViewState`.
- **EnhancedSettingsState (`settings.py`):** The `EnhancedSettingsState` is now embedded within `settings.py`, consolidating settings functionality into a single file. It manages application settings, including loading, saving, exporting, importing, and backing up settings. It supports persistence via `ServerBridge` or local file, JSON/INI export, and validation. Utilities like `action_buttons.py` and `settings_io.py` interact with `EnhancedSettingsState` via structural protocols (duck typing) to avoid tight coupling.

## Launch Playbook
- Execute `FletV2/start_with_server.ps1` to configure env vars and start TCP server + GUI in order.
- Verify GUI at `http://localhost:8570`; ensure TCP server listening on `127.0.0.1:1256`.
- Watch for mock bridge banner—indicates real server unreachable; disable destructive actions.
- Remove stale `transfer.info` files to prevent wrong payload ingestion.
- Stop stack through VS Code task manager or `Stop-Process -Name "python" -Force`.

## Build & Tooling
- Python: run `ruff check`, `ruff format --check`, `pytest -vv` from repo root.
- C++ client: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release`.
- GUI lint: `flet_venv\Scripts\python.exe -m pylint FletV2 Shared python_server api_server`.
- Integration smoke: PowerShell launcher → walk Dashboard → Clients → Files → Database → Analytics.
- Codacy MCP: trigger `codacy_cli_analyze` post-edit to track lint/security insights once server available.
- MCP Server: To add an MCP server, update the workspace MCP configuration file `mcp.json`. Back up the original file by creating a `.bak` copy before modifying it. The `mcp.json` file should contain a structured `mcpServers` configuration. Example:
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
```
When adding an MCP server, prefer the simple mapping format in `mcp.json`:
```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest"]
  }
}
```
The workspace linter may flag the `mcpServers` property as invalid for this project's schema. If necessary, register the MCP server globally using the VS Code CLI: `code --add-mcp '{"name":"chrome-devtools","command":"npx","args":["chrome-devtools-mcp@latest"]}'` (or with the `-y` flag). On Windows, the MCP server command may require a `cmd /c` wrapper to execute `npx`. **Therefore, on Windows, the MCP server command must use a `cmd /c` wrapper to execute `npx`. Example:**
```json
{
  "chrome-devtools": {
    "command": "cmd",
    "args": ["/c", "npx", "-y", "chrome-devtools-mcp@latest"]
  }
}
```
**After registering or configuring an MCP server, VS Code must be restarted for the changes to take effect.**
- Factory CLI: To install Factory CLI on Windows, use the following command in PowerShell: `irm https://app.factory.ai/cli/windows | iex`. Ensure that `C:\Users\<your_user>\bin` is added to your PATH environment variable so the `droid` command is available in new shells. **After installation, ensure that `C:\Users\<your_user>\bin` is added to your PATH environment variable. The environment path may need to be set every time a new shell is opened.**
- For consistent code analysis, configure a `pyrightconfig.json` file with include/extraPaths, exclusions, and basic checking. Clean `settings.json` to only manage interpreter and terminal integration, removing conflicting Pylance analysis settings.

## Environment Matrix
- `PYTHONNOUSERSITE=1`: strips user site-packages, preventing `pydantic_core` conflicts.
- `FLET_NAV_SMOKE=1`: activates navigation smoke suite verifying view transitions.
- `FLET_DASHBOARD_DEBUG=1`: increases logging for dashboard metrics refresh cycles.
- `FLET_V2_DEBUG=1`: surfaces theming diagnostics; disable when performing performance measurements.
- Set variables before launching Python; PowerShell scripts already front-load them.
- The `claude-code.environmentVariables` setting in VS Code is an array of environment variable strings in the format `"KEY=VALUE"`. These variables are made available to the Claude Code extension during execution. Example: `["PYTHONNOUSERSITE=1", "FLET_NAV_SMOKE=1", "FLET_DASHBOARD_DEBUG=1", "FLET_V2_DEBUG=1", "CYBERBACKUP_DISABLE_INTEGRATED_GUI=1"]`
- **Flet 0.28.3 is installed inside the `flet_venv` venv; ensure all necessary packages exist within this environment.**

## Flet View Lifecycle
- Factories return `(control, dispose_fn, setup_fn)`; never call `.update()` during construction.
- After `AnimatedSwitcher` transitions, `await asyncio.sleep(0.25)` before mutating controls to guarantee attachment.
- Guard optional `server_bridge` usage; the mock fallback will lack certain methods.
- Replace DataTable and chart controls with ListView + Card compositions for stability.
- Tint ListView via surrounding `ft.Container(bgcolor=...)` since ListView has no `bgcolor` property.
- Swap unsupported icons (e.g., `ft.Icons.DATABASE`) for `ft.Icons.DATASET` or other supported glyphs.
- Use `page.run_task` to offload long operations and update controls via refs to avoid blocking UI thread.
- Cancel background tasks and unregister event listeners inside `dispose` to prevent leaks.
- Truncate lengthy values in cards to maintain consistent layout and avoid overflows.
- When using `page.run_task()`, ensure you are passing the coroutine function itself (e.g., `page.run_task(my_async_function)`) and not the result of calling the function (e.g., NOT `page.run_task(my_async_function())`). Passing the result will lead to an `AssertionError`.
- **Always pass the coroutine function itself (e.g., `page.run_task(my_async_function)`) and not the result of calling the function (e.g., NOT `page.run_task(my_async_function())` or `page.run_task(lambda: async_func())`).**
- **Avoid awaiting synchronous ServerBridge methods in asynchronous contexts to prevent GUI freezes.**
- **Never use `time.sleep()` in async contexts to prevent UI freezes.**
- **Ensure that the ListView control is added to the page before attempting to update it, especially when using asynchronous operations. This prevents `ListView Control must be added to the page first` errors.**
- **When using `create_logs_view` in `enhanced_logs.py`, ensure the correct return type annotation is used: `tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]`. This requires importing `Coroutine` from the `typing` module.**
- **When using `page.run_task` in `settings.py`'s `_schedule` function, ensure the function adheres to its `-> None` return type by not returning anything in either branch. The coroutine should still be scheduled correctly.**
- **Add null checks before accessing control attributes, especially when dealing with optional controls. For example, when updating the `disabled` property of a TextField in `settings.py`, check if the control and its page are not None before calling `control.update()`. Use `if control and isinstance(control, ft.TextField):` and `if control.page:` for safety.**

## Theme & Styling
- Reuse `theme.py` constants such as `PRONOUNCED_NEUMORPHIC_SHADOWS`, `GLASS_MODERATE`, and gradient helpers.
- Primary surfaces target 40–45% shadow intensity; secondary elements sit around 20–30%.
- Glass overlays perform best with blur 10–14px and opacity 0.08–0.18.
- Avoid unsupported colors (`ft.Colors.SURFACE_VARIANT`); rely on `SURFACE` or `ON_SURFACE_VARIANT` equivalents.
- New controls must hook into theme change broadcasts via state manager.
- Centralize hover/press animations using shared helpers to keep behavior uniform.
- Include breakpoint, theme mode, and control identifiers in styling logs during debugging.
- Maintain accessibility guidelines: color contrast, focus indicators, and keyboard navigation cues.

## Protocol & Networking
- Request headers: 16-byte UUID, 1-byte version, 2-byte opcode (little-endian), 4-byte payload length, payload, CRC32.
- Response headers: 1-byte version, 2-byte status code, 4-byte payload length, payload, optional checksum.
- Update Python and C++ enum definitions together to prevent silent incompatibilities.
- TCP server runs worker pool; keep handler work non-blocking to maintain throughput.
- `retry` decorator logs attempts via `metrics_collector.record_counter`; inspect metrics for persistent failures.
- Structured logging should capture `client_id`, `opcode`, `file_path`, and durations for postmortems.
- Use shared buffer utilities for endian-safe parsing instead of manual slicing.
- Document protocol version bumps in commit messages and release notes.
- Ensure analytics dashboards reflect any new opcodes or response codes added.

## Database Discipline
- Acquire connections exclusively through `db_manager.get_connection()` to leverage pooling.
- Persist timestamps using `time.monotonic()` and convert to display strings within GUI converters.
- Encapsulate write operations in explicit transactions, guaranteeing commits or rollbacks.
- Update migrations, fixtures, and GUI forms together when schema evolves.
- Sanitize data transfer objects by converting BLOB UUIDs to strings before delivering to UI.
- Monitor pool metrics; prolonged high utilization implies leaked cursors or long-running queries.
- Use parameterized SQL statements to preserve audit trails and prevent injection bugs.
- Record schema changes within database change logs and communicate to dependent teams.

## Transfer Pipeline
- `transfer.info` requires exactly three UTF-8 lines: `host:port`, username, absolute path.
- Template:
```
127.0.0.1:1256
DemoUser
C:\\Backups\\payload.bin
```
- `RealBackupExecutor` writes the file with `\n` separators; altering format prevents the client from parsing inputs.
- Confirm file existence before launching the native client to avoid silent no-ops.
- Launch using `Popen_utf8` for consistent stdout/stderr capture.
- Remove stale `transfer.info` artifacts between runs to prevent mismatched payloads.
- Isolate batch jobs into unique temp directories to avoid race conditions.
- Inspect native client exit codes and propagate structured errors to bridge and GUI layers.

## Bridge Behavior
- `server_bridge` reports `.success`, `.data`, `.error`; never assume success without checking flag.
- Use `.is_real()` or equivalent guards before calling server-only methods.
- Run `setup_subscriptions()` after page attachment; cache unsubscribe handles for disposal.
- Show user-facing banners when mock fallback activates so actions reflect offline status.
- Keep converters in sync with server payload shape to avoid serialization mismatches.
- Wrap async bridge calls with cancellation to avoid updates on disposed controls.
- Publish telemetry via state manager for analytics and logging views.
- Document new endpoints or fields in API references and extend integration tests accordingly.

## Testing & QA
- Default PR gate: `ruff check`, `ruff format --check`, `pytest`, `cmake --build build --config Release`, `python -m compileall FletV2/main.py`.
- GUI smoke: launch via PowerShell script and traverse Dashboard → Clients → Files → Database → Analytics watching for freezes.
- E2E backup: send sample file, confirm presence in `received_files/` and metadata entry in SQLite.
- Validate SHA-256 hashes before/after transfer to ensure integrity through encryption pipeline.
- Force transient failures to observe `retry` metrics and ensure final error clarity.
- Stress database pool with concurrent jobs to confirm connections return promptly.
- Test mock fallback by running GUI without server; verify warnings show and destructive actions disable.
- Time analytics view setup to ensure data loads post-attachment to avoid `Column Control` errors.
- Log results in relevant fix reports (`FletV2_Fix_Verification_Report.md`, etc.) for traceability.
- When Codacy MCP becomes available, rerun security analysis and archive findings.

## Troubleshooting
- **Blank or gray view**: confirm control attachment, hide overlays, await `setup` completion.
- **Pydantic import error**: environment contamination; relaunch via PowerShell script with isolated venv.
- **Port 1256 busy**: terminate stray Python processes before starting server.
- **Analytics failing**: move data fetching into `setup` and guard asynchronous updates.
- **Database view freeze**: maintain ListView approach and text truncation safeguards.
- **Native client hang**: examine `transfer.info`, verify protocol version alignment, ensure network reachability.
- **Mock fallback active**: server offline; disable destructive UI actions and surface warning banner.
- **Retry storms**: review logs and metrics for repeated failures; escalate if upstream service degraded.
- **ListView tint needed**: wrap in `ft.Container` rather than relying on nonexistent `bgcolor`.
- **Icon missing**: choose supported glyphs such as `ft.Icons.DATASET`.
- **Layout overflow**: truncate strings or move to chips to maintain card sizing.
- **Build drift**: rerun `scripts/one_click_build_and_run.py` after C++ or protocol modifications.
- **Expected class but received "(...) -> TextControl"**: Ensure the correct control type is being passed and that the factory is returning the expected type. Review control constructors and return types.
- **`try/except Exception: pass`**: Replace with `with contextlib.suppress(Exception):` for cleaner error handling.
- **Bare `except:` clauses**: Replace with `except Exception:` for better error specificity.
- **`sum(1 for ...)`**: Replace with `len([...])` for counting operations.
- **`page.update()`**: Always pass the coroutine function itself (e.g., `page.run_task(my_async_function)`) and not the result of calling the function (e.g., NOT `page.run_task(my_async_function())` or `page.run_task(lambda: my_async_function())`). Passing the result will lead to an `AssertionError`.
- **`AttributeError: type object 'Icons' has no attribute 'SAVE_AS_OUTLINE'`**: This error indicates that the specified Flet icon `SAVE_AS_OUTLINE` is not available in the current Flet version (0.28.3). Replace it with `ft.Icons.SAVE_OUTLINED`. Verify icon availability in the target Flet version.
- **`AttributeError: module 'flet' has no attribute 'SelectableText'`**: When using `SelectableText`, use `ft.Text` with `selectable=True` instead.
- **`Dropdown.__init__() got an unexpected keyword argument 'height'`**: Remove the `height` parameter from the `ft.Dropdown` constructor.
- When using `ft.TextField`, avoid setting the `height` parameter, as it is not supported in Flet 0.28.3.
- **`TypeError: Text.__init__() got an unexpected keyword argument 'text_style'`**: In Flet 0.28.3, the `text_style` parameter is not supported in the `ft.Text` constructor. Use direct properties like `size=14` instead of `text_style=ft.TextStyle(size=14)`.
- **`ListView Control must be added to the page first`**: This error indicates that you are trying to update a ListView before it has been added to the page. Ensure that the ListView control is added to the page, especially when using asynchronous operations.
- **When encountering `Type "Task[None]" is not assignable to return type "None"` in `settings.py`, ensure the `_schedule` function adheres to its `-> None` return type by not returning anything in either branch. The coroutine should still be scheduled correctly.**
- **Optional member access errors**: Add null checks for `control` before accessing `control.error_text` and `control.page`. Use `if control and hasattr(control, "error_text"):` instead of `if hasattr(control, "error_text"):`.
- **Uninitialized `status_text`**: Properly initialize `status_text` as an `ft.Text` object instead of `None`. Update the type annotation from `ft.Text | None = None` to `ft.Text = ft.Text(...)`.
- **Sudden influx of code analysis errors**: This often indicates a change in IDE settings, linter configurations, or extension updates. Check for stricter type checking or new static analysis tools. Address import resolution issues, attribute access problems, and optional/None safety by adding null checks, fixing imports, and adding type ignores where necessary. **Inconsistent code analysis results in VS Code can be caused by language server state inconsistency, type checking/linting configuration conflicts, extension conflicts, or memory-related issues.** To address this:
    - Standardize configuration files (e.g., `*.pylintrc`, `pyproject.toml`, `setup.cfg`, `.flake8`).
    - Ensure a clear extension setup in VS Code by verifying Python linting and analysis settings. Avoid conflicting settings.
    - Restart VS Code with a clean environment: close VS Code, delete temporary directories (`.vscode/.ropeproject/`, `.vscode/.pylint.d/`, ``), and restart VS Code with extensions disabled (`code --disable-extensions .`). Re-enable essential extensions one by one.
    - Create a consistent validation process by adding a command to your project that runs the same validation tools used in VS Code (e.g., `python -m ruff check .`, `python -m pyright`).
    - Check for memory issues by monitoring the Output panel for memory warnings. Increase memory limits for extensions or run heavier analysis tools on-demand.
- **Errors from temporary VS Code editing snapshots:** Errors with paths like `chat-editing-snapshot-text-model:/c%3A/...` or `git:/c%3A/...` indicate temporary snapshots or git diff views, not real file errors. Real file errors would show paths like `c:\Users\tom7s\...`. Close the chat editing session, reload VS Code, and run the linter to verify the actual files.

## Operational Checklists
- Pre-commit: lint, tests, C++ build, GUI smoke, documentation sync.
- Pre-release: full E2E transfer validation, documentation refresh, environment verification.
- Incident response: gather logs, SQLite snapshot, `transfer.info`, binary payload, and CLI outputs.
- Protocol changes: rebuild native client, update converters, bump version constants, notify stakeholders.
- Schema updates: adjust migrations, fixtures, GUI forms, analytics expectations.
- Launcher tweaks: document modifications in `FletV2_Fix_Verification_Report.md` and commit notes.
- Archive logs between runs to segment investigations cleanly.
- Communicate progress via repo issues and project status channels.
- **Prioritize fixes for async safety, memory leaks, security vulnerabilities, and performance bottlenecks.**
- **Ensure no changes are made that could break the system or the code.**
- **Before addressing errors or flaws, always present a summary of the identified issues for review and approval.**

## Command Reference
- Launch stack: `cd FletV2 && .\start_with_server.ps1`.
- Start Flask bridge: `python api_server/cyberbackup_api_server.py`.
- Run TCP server: `python python_server/server/server.py`.
- Execute native client: `build/Release/EncryptedBackupClient.exe --batch`.
- Rebuild C++ client: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release`.
- Lint Python modules: `flet_venv\Scripts\python.exe -m pylint FletV2 Shared python_server api_server`.
- Run tests: `pytest tests/ -vv`.
- Kill stray Python: `Stop-Process -Name "python" -Force` (PowerShell).
- Download a file from a URL: `mkdir -p "$(dirname ~/.claude/commands/code-review.md)" && curl -o ~/.claude/commands/code-review.md https://claudecodecommands.directory/api/download/code-review`.
- Download a file from a URL: `mkdir -p "$(dirname ~/.claude/commands/update-claudemd.md)" && curl -o ~/.claude/commands/update-claudemd.md https://claudecodecommands.directory/api/download/update-claudemd.md`.
- The `update-claudemd.md` file is a Claude Code command that automatically updates `CLAUDE.md` documentation files based on recent git changes. It analyzes Git status, code changes, configuration updates, and API changes to generate an updated `CLAUDE.md` file.
- Install Factory CLI (Windows): `irm https://app.factory.ai/cli/windows | iex`.
- **Creating a Git Bundle:**
  ```bash
  cd C:\path\to\YourProject
  # Create a bundle with all refs (branches, tags)
  git bundle create ..\YourProject.bundle --all
  # Verify the bundle
  git bundle verify ..\YourProject.bundle
  ```
  Example usage within the project:
  ```bash
  cd C:\path\to\YourProject
  git bundle create Client_Server_Encrypted_Backup_Framework.bundle --all
  git bundle verify Client_Server_Encrypted_Backup_Framework.bundle
  ```

## Communication & Hygiene
- Issues should cite component, command invoked, commit hash, environment flags, and log excerpts.
- PRs must summarize architecture touchpoints, regressions mitigated, and validation performed.
- Keep inline comments succinct; reference this guide for broader explanations.
- Update knowledge-base artifacts (`FletV2_*_Report.md`, analytics summaries) when applying fixes.
- Uphold architecture guardrails—no bypassing pooling or bridging layers without consensus.
- Record Codacy or security scan results once MCP tooling returns.
- Track launcher/environment adjustments in commit logs and shared documentation.
- Provide reproducible scripts for new diagnostics to support teammates.
- **Prioritize fixes for async safety, memory leaks, security vulnerabilities, and performance bottlenecks.**

## Metrics & Telemetry
- Enable structured logging via `Shared.logging_config` to capture `client_id`, opcodes, durations, and CRC outcomes.
- Ship metrics to `metrics_collector`; inspect retry counters and timers after load tests.
- Persist GUI analytics snapshots in `FletV2/logs/` for regression comparisons.
- Chart refresh cadence controlled by state manager; adjust intervals via `FLET_NAV_SMOKE` toggles.
- Correlate TCP throughput with database write timings to spot bottlenecks.
- Archive incident logs alongside SQLite snapshots for forensic parity.
- **Track the number of `print()` statements and `page.update()` calls; aim to reduce these significantly.**

## Security Posture
- Rotate RSA key pairs through documented scripts; never commit private keys.
- Validate AES cipher paths use 256-bit keys with fresh IV per payload chunk.
- Verify CRC32 before decrypting to avoid wasting cycles on corrupted data.
- Isolate secrets in environment variables; sanitize logs to avoid leaking paths or credentials.
- Run `codacy_cli_analyze` with security plugins once dependencies change.
- Document threat model assumptions in `security_notes.md`; revisit after protocol updates.
- **Never store sensitive settings in plaintext. Encrypt credentials and sensitive data.**

## Deployment & Ops
- Prefer PowerShell launchers for Windows hygiene; Linux/macOS require analogous shell scripts.
- Maintain task definitions (`.vscode/tasks.json`) so teammates can start stack uniformly.
- Pin Python dependencies via `requirements.txt`; regenerate hashes when libraries update.
- Keep CMake presets aligned with vcpkg manifests aligned with vcpkg manifests to prevent drift in C++ builds.
- Schedule routine cleanup of `python_server/server/received_files/` in staging environments.
- Monitor port usage (`netstat -ano`) before launches to avoid conflicts.

## Documentation & Knowledge Base
- Sync changes with `FletV2_Fix_Verification_Report.md` and related postmortem files.
- Update onboarding briefs inside `AI-Context/` when workflows evolve.
- Mirror crucial diagrams in `important_docs/` for cross-agent consistency.
- Record protocol version bumps with rationale in `Protocol_Change_Log.md`.
- Summarize release outcomes in `FletV2_Completion_Summary.md` with validation evidence.
- Keep analytics tuning notes inside `ANALYTICS_VIEW_FIXES.md` for quick reference.

## Active Risks
- GUI relies on Windows-specific UTF-8 bootstrap; validate alternative OS paths before porting.
- TCP server defers heavy work to pool; any blocking handler risks cascading stalls.
- SQLite concurrency limits require disciplined transaction scopes to avoid lock storms.
- Mock bridge lacks destructive operations; ensure UI guards remain accurate.
- RSA-1024 may require upgrade roadmap; document migration plan ahead of compliance reviews.
- Dashboard metrics can lag if state manager subscribers fail to dispose cleanly.
- **Memory leaks in `enhanced_logs.py` can lead to resource exhaustion. Implement a mechanism to limit log storage.**
- **Awaiting synchronous `ServerBridge` methods in async contexts will freeze the GUI.**
- **Using `time.sleep()` in async contexts will freeze the UI.**
- **Files exceeding 1000 LOC, specifically `views/enhanced_logs.py`, `views/database_pro.py`, and `views/dashboard.py`, and `main.py` require decomposition to improve maintainability.**
- **The project has 572 TODO/FIXME comments across 97 files, indicating areas needing attention and potential improvements. However, a recent analysis found only a small number of actual TODO comments within the FletV2 project itself. The original analysis may have included comments from build system dependencies.**
- **Inconsistent Code Analysis:** Inconsistent code analysis results in VS Code can be caused by language server state inconsistency, type checking/linting configuration conflicts, extension conflicts, or memory-related issues.**
- **String literals passed to `scroll` instead of `ft.ScrollMode`**: The following files use string literals for the `scroll` property instead of `ft.ScrollMode`: `FletV2/main.py:1002`, `FletV2/views/clients.py:295, 433, 494`, `FletV2/views/files.py:373`, `FletV2/views/database_pro.py:1242, 1317`, `FletV2/views/dashboard_stub.py:62`, `FletV2/views/experimental.py:140`, `FletV2/utils/dialog_builder.py:171`, `FletV2/sophisticated_dashboard_demo.py:390`, `FletV2/theme_usage_examples.py:269`, `FletV2/tests/test_production_fix.py:93`, `FletV2/tests/test_rebuild_approach.py:102, 115`.
- **`ft.TextStyle` uses unsupported `background_color`**: The `ft.TextStyle` in `FletV2/components/log_card.py:332` uses the unsupported `background_color` keyword; use `bgcolor` instead.
- **Blocking `time.sleep()` calls**: Blocking `time.sleep()` calls persist in Flet flows (`FletV2/server_with_fletv2_gui.py:166, 179`; `FletV2/fletv2_gui_manager.py:290`) and supporting examples/tests (`FletV2/tests/test_async_patterns.py:28, 45, 191`; `FletV2/performance_benchmark.py:146`; `FletV2/quick_performance_validation.py:33, 43`). Avoid `time.sleep()` in Flet.
- **Direct imports without the required relative→absolute fallback still exist in several helper modules**: `action_buttons.py` imports `theme`/`ui_components` using plain module names instead of the `try` relative / `except ImportError` absolute pattern mandated in the guide; `dialog_builder.py` pulls `theme` the same way. These will fail whenever the package isn’t on `sys.path` exactly as expected.
- **Test helpers mirror the same issue**: `test_logs_integration.py` (and similar test files) reach into `utils.*` and `views.*` with absolute imports, again skipping the fallback structure the instructions require.
- **The `settings.py` file is completely broken and needs to be re-implemented fully.**
- **The `run_integrated_server` module is missing. Implement `find_available_port` directly in the `start_integrated_gui.py` file to eliminate the external dependency. Use Python's `socket` module to check port availability by attempting to bind to ports incrementally.**

## Quick Diagnostics
- `python python_server/server/server.py --dry-run` verifies protocol bindings without client traffic.
- `python FletV2/debug_dashboard.py` renders dashboard controls against mock data.
- `python scripts/check_db.py` inspects SQLite health and schema drift.
- `cmake --build build --config Release --target EncryptedBackupClient` isolates client rebuilds.
- `pytest tests/test_protocol.py -vv` focuses on handshake validations.
- `tar -tzf logs_bundle.tar.gz` confirms incident archive contents before handoff.

## Persistent Reminders
- Three-line `transfer.info`, UTF-8 bootstrap first, PowerShell launcher always, pooled DB access, synchronized protocol definitions.
- Avoid UI updates before controls attach; rely on `setup` coroutine and refs.
- Keep structured logs/metrics to accelerate incident response.
- Rebuild binaries after protocol edits to prevent handshake drift.
- Validate via lint → build → tests → GUI smoke → transfer before shipping.
- Update this guide whenever architecture or workflows evolve.
- Analytics: Confirm charts render after a few navigations
- **Avoid using `print()` statements for logging; use proper logging mechanisms instead.**
- **Minimize full-page redraws (`page.update()`) by updating individual controls.**
- **Decompose files exceeding 1000 lines of code.**
- **Flet 0.28.3 is installed inside the `flet_venv` venv; ensure all necessary packages exist within this environment.**

## Coding Style
- Simplify conditional expressions using the `or` operator where appropriate to improve code conciseness and readability (e.g., `expansion_icon or ft.Container(width=0)`). Run linting tools like Ruff to confirm no new issues are introduced after applying such changes.
- Use `with contextlib.suppress(Exception):` instead of `try/except Exception: pass` for cleaner error handling.
- Use `except Exception:` instead of bare `except:` clauses for better error specificity.
- Use `len([...])` instead of `sum(1 for ...)` for counting operations.
- **`page.run_task()`**: Always pass the coroutine function itself (e.g., `page.run_task(my_async_function)`) and not the result of calling the function (e.g., NOT `page.run_task(my_async_function())` or `page.run_task(lambda: my_async_function())`). Passing the result will lead to an `AssertionError`.
- **`AttributeError: type object 'Icons' has no attribute 'SAVE_AS_OUTLINE'`**: This error indicates that the specified Flet icon `SAVE_AS_OUTLINE` is not available in the current Flet version (0.28.3). Replace it with `ft.Icons.SAVE_OUTLINED`. Verify icon availability in the target Flet version.
- **`
- **`AttributeError: module 'flet' has no attribute 'SelectableText'`**: When using `SelectableText`, use `ft.Text` with `selectable=True` instead.
- **`Dropdown.__init__() got an unexpected keyword argument 'height'`**: Remove the `height` parameter from the `ft.Dropdown` constructor.
- When using `ft.TextField`, avoid setting the `height` parameter, as it is not supported in Flet 0.28.3.
- **`TypeError: Text.__init__() got an unexpected keyword argument 'text_style'`**: In Flet 0.28.3, the `text_style` parameter is not supported in the `ft.Text` constructor. Use direct properties like `size=14` instead of `text_style=ft.TextStyle(size=14)`.