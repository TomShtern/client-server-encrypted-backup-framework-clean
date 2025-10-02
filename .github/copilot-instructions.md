---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

# Client-Server Encrypted Backup Framework - AI Development Guide

This AI Development Guide should be read in conjunction with the `#file:AI-Context` folder (for extremely important documentation, data, information, and rules) and the `#file:important_docs` folder (for important information and documentation).

## 🏗️ System Architecture Overview

This is a **production-grade 5-layer encrypted backup system** with hybrid web-to-native-desktop architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server → Flet Desktop GUI
  ↓           ↓                    ↓                     ↓
HTTP      RealBackupExecutor    --batch mode       Custom Binary TCP   Material Design 3
requests  process management   + transfer.info     Custom Binary TCP   Server Management
```

**Critical Components**:
- **C++ Client**: Production executable with RSA/AES encryption, CRC verification, and `--batch` mode for subprocess integration
- **Flask API Bridge**: HTTP API server (port 9090) coordinating between web UI and native client
- **Python Server**: Multi-threaded TCP server (port 1256) with file storage in `received_files/`
- **Flet Desktop GUI**: Material Design 3 server management interface with modular architecture
- **SQLite3 Database**: Client and file tracking storage

### Build/Lint/Test Commands

#### Python
```bash
# Lint: ruff check . (line-length=110, rules: E,F,W,B,I)
ruff check .

# Format: ruff format .
ruff format .

# Type Check: mypy . (strict mode, Python 3.13.5)
mypy .

# Lint: pylint (configuration via .pylintrc)
pylint

# Test All: pytest tests/
pytest tests/

# Test Single: pytest tests/test_specific_file.py::TestClass::test_method -v
pytest tests/test_specific_file.py::TestClass::test_method -v

# Test Integration: pytest tests/integration/ -v
pytest tests tests/integration/ -v

# Compile all Python files
python -m compileall FletV2/main.py
```

#### C++
```bash
# Build: cmake with vcpkg toolchain
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release

# Format: clang-format -i file.cpp (Google style, 100 cols, 4-space indent, Google style)
clang-format -i file.cpp
```

#### Full System
```bash
# One-Click Build+Run: python scripts/one_click_build_and_run.py
python scripts/one_click_build_and_run.py
```

### Code Style Guidelines

#### Python
- **Imports**: Standard library first, then third-party, then local (alphabetical within groups)
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Types**: Use type hints, strict mypy compliance
- **Line Length**: 110 characters max
- **Error Handling**: Try/except with specific exceptions, log errors with context. Use `contextlib.suppress(Exception)` for concise suppressed-exception blocks.
- **Async**: Use async/await for I/O operations, avoid blocking calls
- **Indentation**: Correct any unexpected indentation issues by ensuring code blocks are properly scoped. Run linters (e.g., `ruff check .`) to verify code style.
- **Sourcery**: Apply only safe, behavior‑preserving refactors (inline immediately-returned vars, simplify empty list comparisons, remove unnecessary casts, safe list comprehension/extend substitutions) and explicitly justify skipping higher‑risk “extract-method” or structural changes that could drop comments or subtly alter flow. Address all sourcery warnings in the `#file:main.py`.
- **Problems View**: The Problems view in VS Code groups problems by source (e.g., extensions, linters) in tree view mode. Multiple groups can appear for the same file if multiple tools are enabled. Use the `problems.defaultViewMode` setting to switch to table view for a flat list. Pylance (Microsoft's Python language server) groups its findings by type in the Problems panel:
    1. **Syntax Errors** - Parse/compilation issues
    2. **Type Errors** - Type checking violations
    3. **Import Issues** - Module resolution problems
    4. **Code Analysis** - Potential bugs or improvements
    5. **Information** - Hints and suggestions

#### C++
- **Style**: Google C++ style with clang-format
- **Indentation**: 4 spaces, no tabs
- **Braces**: Attach to function/class, new line for control statements
- **Pointers**: Left-aligned (*)
- **Includes**: Group by type, alphabetical within groups

#### General
- **UTF-8**: Import `Shared.utils.utf8_solution` in files with subprocess/console I/O
- **Logging**: Use logger instead of print() for debugging
- **File Size**: Keep files under 650 lines, decompose larger files
- **Framework Harmony**: Prefer Flet built-ins over custom solutions
- **Reasoning**: Apply sequential thinking MCP (Meta-Cognitive Programming) as much as possible to identify all problems/issues before attempting fixes. Use websearch and context7 MCP when you need up to date context and docs.
- **Proactivity**: The AI should be proactive in identifying and fixing issues, not just running tests without understanding the results. Use sequential thinking MCP every 5 tool calls to ensure a thorough understanding of the situation before proceeding with fixes.
- **System Integrity**: Make sure you are not breaking the system and removing functionality.
- **Problem Management**: Make sure to not cause more problems than you solve. **Make sure you are not creating new problems instead of solving of solving them.**
- **Data Source**: **ALWAYS USE REAL DATA FROM THE SERVER/DATABASE!** You can, optionally, add also a fallback to placeholder 'loren ipsum' instead of mock data. **NEVER use mock data.**
- **Bug Fixing**: When fixing errors, focus on syntax errors without changing functionality. Ensure that the code remains unbroken and that no new problems are introduced. **Don't assume anything, always make sure.**
- **Code Quality**: Make sure there are no code/functions duplications and no redundencies.
- **Flet Version**: Ensure you are doing things with Flet 0.28.3 idioms in mind. Always avoid costume complex long solutions where there is a Flet native better and simpler way. Use context7 if you are not sure about something, it has instructions for everything.
- **Ruff**: When addressing Ruff issues, ensure you are not breaking the code and not removing functionality, and make sure to not create more problems than you solve.
- **Context7 MCP Usage**: Use context7 MCP more than a few times. When working with Flet, reference the official docs from context7 about version 0.28.3. **Create `Flet_Snnipets.md` to document Flet methods, features, built-in behaviors, anti-patterns, and recovery tips. The total length of the new markdown doc should be shorter than 500 LOC, ideally around 200-350 LOC.** When working with Flet, reference the official docs from context7 about version 0.28.3.
- **Configuration Search**: When asked to find a configuration value (e.g., a timeout), use workspace grep to locate the exact string and its assigned value.
- **settings.local.json**: Ensure the `settings.local.json` file does not contain any duplicate entries in the `"allow"` array.
- **Emergency GUI**: When fixing issues in `emergency_gui.py` related to missing imports or dependencies, define a simple, self-contained stub for the missing function directly in the file. This creates a basic control that matches the expected return signature (e.g., `dashboard_control, dispose_func, setup_func`), ensuring the code runs without external dependencies.
- **Qwen Code Configuration**:
  - `contentGenerator.timeout`: This key is not present in your repository files, but it is referenced repeatedly in Qwen Code issues and the Qwen Code docs as the configuration property to increase the streaming/setup timeout for content generation (i.e., streaming responses).
  - Place a settings file at either:
    - Project-level: `<project-root>/.qwen/settings.json`
    - User-level: `%USERPROFILE%\.qwen\settings.json` (on Windows; equivalently `~/.qwen/settings.json`)
  - The timeout is a request timeout for the content generator (the CLI’s model/API calls).
  - Units: milliseconds (the settings schema says "Request timeout in milliseconds.").
  - Semantics: the maximum wall‑clock time allowed for a single generation request to complete. If a request exceeds this time the client will abort/consider it failed. It’s a total request timeout, not a per‑token inactivity timeout.
  - Value behavior:
    - Any positive integer = timeout in milliseconds (e.g., 30000 = 30 seconds).
    - `0` (or omitted/undefined depending on implementation) — effectively disables the timeout (no client‑side abort).
  - Interaction with `maxRetries`: if a request times out, the client may retry up to `contentGenerator.maxRetries` times (so a short timeout + retries can cause multiple fast retry attempts).
  - Practical recommendation: pick a reasonable timeout for your network and model latency (30_000–60_000 ms is common). If you want no client-side cutoff, keep `0`.
- **Flet GUI Startup**: The Flet GUI should start successfully and run in browser mode by default. If port 8550 is already in use, the application will use port 8551 or 8552. The GUI should be fully operational for managing the encrypted backup system.
- **GUI Access**: The Flet GUI is accessible via a web browser. The application typically runs on port 8550 by default and will use ports 8551/8552 if port 8550 is in use. Navigate to `http://localhost:8550` (or 8551/8552 if port 8550 is in use) to access the GUI.
- **GUI-Only Mode**: When running in GUI-only mode, ensure the `backup_server` parameter is set to `None` when calling `main.main(page, backup_server=None)` to trigger Lorem ipsum placeholder data. The Flet GUI should start successfully and run in browser mode by default. If port 8550 is already in use, the application will use port 8551.
- **Navigation Bar Styling**: When improving the navigation bar's design, adhere to the following specifications:
  - **Layout**:
    - Position: fixed left column (vertical), full-height of app.
    - Width: expanded 260 px, collapsed 72 px.
    - Padding: 16px vertical inside container, 12px horizontal for items.
    - Item spacing: 10 px vertical gap between nav items.
    - Icon size: 22 px for list icons; active icon 24 px with subtle scale animation.
    - Label typography: 14 px medium (FontWeight W_500), single-line ellipsis.
    - Secondary text (badges/labels): 11 px, uppercase, color token outline.
  - **Visuals**:
    - Background: Surface variant slightly elevated. Example token: ft.Colors.SURFACE_VARIANT (dark) with linear gradient subtle top-left to bottom-right or box shadow inner glow (use BoxShadow with small blur).
    - Border radius: 10 px for the container; nav items: 8 px.
    - Active item: Elevated card (bgcolor = ft.Colors.SURFACE_HIGHLIGHT or custom token), left accent bar: 4 px solid accent color (Primary/TINT).
    - Hover: Slight lighten of bg (increase alpha) and soft outer glow ring (BoxShadow with color primary, opacity 0.08). Animated transitions: 120-180ms ease-out.
  - **Icon & label alignment**:
    - Row: icon left, label right.
    - When collapsed: only icon visible, icons centered in a circular container (48x48).
    - Tooltip: show label on hover when collapsed (Flet Tooltip wrapper).
  - **Interactions and behavior**:
    - Collapse/expand button at bottom (arrow icon). Animated width transition (use control.update with small task that animates).
    - Non-blocking: Keep nav z-index low, no modal behavior. Content area should have left padding equal to nav width (update on collapse).
    - Keyboard navigation: items reachable via Tab; add semantic attributes (aria-like text via tooltip and accessible_text on Buttons).
    - Touch targets: min 44x44 px for each item to be mobile-friendly.
  - **Animations**:
    - Hover elevation: 160ms easing.
    - Active selection ripple: use small scale + opacity overlay.
    - Collapse/expand animation: 220ms linear.
  - **Colors (dark theme tokens - map to Flet)**:
    - Surface: ft.Colors.SURFACE (dark).
    - Surface variant / card: ft.Colors.SURFACE_VARIANT.
    - Primary accent: ft.Colors.PRIMARY (or ft.Colors.BLUE_500).
    - Text primary: ft.Colors.ON_SURFACE.
    - Muted: ft.Colors.OUTLINE or ft.Colors.OUTLINE_VARIANT.
    - Danger/destructive: ft.Colors.ERROR.
  - **Accessibility**:
    - Provide tooltips for collapsed state.
    - Use descriptive icons + accessible_text on buttons.
    - Ensure contrast ratios — primary text on surface should meet 4.5:1 where possible.
- **Blank Gray Screens on Analytics and Logs Pages**: If encountering blank gray screens on the analytics and logs pages, investigate the following:
  - **Structural Issues**: The Flet Specialist's extensive modifications may have introduced structural problems preventing proper content rendering.
  - **Ref-Based Updates**: Ensure complex ref-based updates are functioning correctly.
  - **Loading Overlays**: Verify that loading overlays are not blocking content. Ensure overlays are hidden (visible=False and opacity=0) when not loading.
  - **Container/Stack Structure**: Check for issues with the container and stack structures.
  - **Async Loading**: Investigate potential async loading problems with skeleton placeholders.
  - **Overlay or Stack ordering**: A loading overlay may be placed on top of the content and left visible or opaque, blocking user content (most common cause when views show a gray surface only). Ensure that the content is the first child and the overlay is the last child in a Stack (Stack renders children in order; last on top). Example: ensure `Stack(children=[content_container, overlay])` so the overlay is placed above the content only when needed. Toggle the overlay child `visible` and `opacity` instead of only toggling a top-level `visible` flag.
  - **Controls Visibility**: Controls may be set to visible=False or opacity=0 and never re-enabled, possibly via refs or async loading code that never completes or fails silently.
  - **Refs and Deferred Updates**: Code may be updating controls before they are attached, or using controls reference wrongly (e.g., expecting .controls to exist when it's None), so nothing gets added to the UI. Ensure that after any `.controls` modification you call `.update()` on that parent control. Ensure the ref is not None before using; add a small wait (`page.run_task`) to populate after attachment or add safe guards like `if ref.current is None: skip update and log a warning, then schedule a retry`. Wrap dynamic control population in a small function and call it with `page.run_task` or schedule via `page.add_post_frame_frame_callback` equivalent (Flet has `page.add_auto_close`? If not, call `page.update` after adding).
  - **Layout Structure**: Using Container vs Column vs Stack incorrectly may cause scroll or layout to be collapsed to zero height.
  - **Suppressed Exceptions**: Exceptions swallowed by `with contextlib.suppress(Exception)` in critical places, may be hiding the real error (a later AI/engineer should disable suppression to see the real stacktrace while debugging). Replace broad `contextlib.suppress(Exception)` with `logging.exception` to capture real errors during debug.
  - **Logs View Attachment Diagnostic**: Add a small diagnostic log + `page.update` in `logs.py`s `setup_subscriptions` to verify that the Logs view is attaching correctly.
- **Embedded GUI**: To enable the embedded GUI set `CYBERBACKUP_DISABLE_INTEGRATED_GUI=0`. The server checks the environment flag incorrectly; the condition should treat only `'1'` as disable.
- **Data Type Handling in Logs View**: When handling data in the logs view, especially data received from the server, ensure that variables declared as lists are not inadvertently reassigned to dictionaries. Use temporary variables to inspect the server response and normalize the data into a consistent list format before further processing. This avoids static type checker errors and ensures that list operations are performed on valid list objects.
- **Flet GUI Startup**: The Flet GUI is now running! The GUI should now be accessible in the web browser. The application is running with:
  - Embedded GUI disabled (as expected for FletV2)
  - Logging initialized with console and file output
  - The server is ready to accept connections
  The Flet GUI should open automatically in the default web browser. If it doesn't appear, you can typically access it at `http://localhost:8550` (or ports 8551/8552 if 8550 is occupied).
- **FletV2 Analysis**: Before making any changes to `FletV2`, analyze the folder for issues, problems, flaws, wrongs, anti-patterns, and bad practices using context7 MCP for up-to-date official context, documentation, and information to verify that all is going the way it should be going.
- **Database Connection Management**: When updating client information in the database, ensure proper handling of connection acquisition and release, especially when using connection pooling. Mirror the pattern used in the `execute` method for connection management. Add checks for whether connection pooling is enabled (`self.use_pool` and `self.connection_pool`). Use manual connection management (get, use, return) when pooling is enabled, and a direct `sqlite3.connect` context manager when pooling is disabled. Ensure the connection is committed and returned properly to avoid resource leaks or database locks.
- **Codacy Instructions**: When working with `codacy.instructions.md`, ensure that the instructions do not contain references to files or folders that do not exist in the repository (e.g., `#file:AI-Context` or `#file:important_docs`). Remove such references to avoid "File not found" errors. **Ignore the two warnings in codacy instructions. Address the remaining issues. Figure out what caused them to show suddenly and fix them. Make sure you are not braking the code. Ensure functionality stays the same or better. Think harder and check if you solved the problems. If you introduce problems, you must figure out what you did that caused it and fix it.**
- **File and Folder References**: In this project's documentation convention, the syntax `#file:` is used to reference both individual files and folders (e.g., `#file:AI-Context` for the AI-Context folder). There isn't a separate `#folder:` keyword.
- **Pylance AI-Assisted Code Actions**: This refers to the configuration settings for AI-powered code actions in the Python extension (Pylance) for Visual Studio Code. It controls various automated code improvements, such as generating docstrings, adding missing imports, organizing imports, and suggesting type annotations. Each key (e.g., `"generateDocstring": true`) enables or disables specific AI-assisted features. Adjust these settings to customize how the extension assists with code editing. Refer to the VS Code Python extension documentation for more details.
  - **Available Keys and Their Effects**
    - `"generateDocstring"`: Automatically generates docstrings for functions, classes, and methods.
    - `"implementAbstractClasses"`: Suggests implementations for abstract methods in subclasses.
    - `"generateSymbol"`: Creates stubs for referenced but missing symbols (e.g., undefined functions or classes).
    - `"convertFormatString"`: Converts old-style string formatting (e.g., `%` or `.format()`) to f-strings.
    - `"addMissingImports"`: Suggests and adds missing import statements based on code usage.
    - `"organizeImports"`: Sorts and removes unused imports.
    - `"suggestTypeAnnotations"`: Proposes type hints for variables, parameters, and return types.
    - `"fixTypeErrors"`: Automatically fixes detected type errors (use cautiously, as it may introduce changes).
  - **Optional/Advanced Keys (Not in your current config)**
    - `"autoApplyEdits"`: If supported, applies edits automatically without confirmation (set to `false` for manual review).
    - `"fixLintIssues"`: Auto-fixes common linting issues (e.g., style violations).
    - `"applyRefactorings"`: Enables AI-driven code refactorings (e.g., renaming, extracting methods).
  - **Usage Tips**
    - Start with conservative settings (like your current ones) to avoid unwanted changes.
    - Enable `"fixTypeErrors"` only after reviewing suggestions, as it can alter code.
    - These actions appear as lightbulb icons in the editor or via quick fixes (Ctrl+.).
    - For more details, check the Pylance documentation or VS Code Python extension settings. If you enable aggressive options, test your code thoroughly to ensure no regressions.
- **Server Issues**: When addressing the issues outlined in `#file:Server_Issues_01.10.2025.md` and the `#file:server.py`, focus on resolving all identified problems and flaws within the server component of the system. When addressing issues in `server.py`, use context7 and sequential thinking tools. When addressing issues outlined in `#file:Server_Issues_01.10.2025.md`, ensure every problem is covered and ready for prioritization before starting implementation. Search for the `update_row` method.
- **Error Handling**: If new problems or errors arise after recent changes, immediately investigate the cause and fix them, ensuring that the system's functionality remains the same or improves. **Make sure you are not breaking the code.** Ensure functionality stays the same or better. Think harder and check if you solved the problems. If you introduce problems, you **must** figure out what you did that caused it and fix it.
- **Pylance**: When addressing Pylance issues, ensure that the code remains unbroken and that no new problems are introduced. **Don't assume anything, always make sure.**
- **Sourcery**: Apply only safe, behavior‑preserving refactors (inline immediately-returned vars, simplify empty list comparisons, remove unnecessary casts, safe list comprehension/extend substitutions) and explicitly justify skipping higher‑risk “extract-method” or structural changes that could drop comments or subtly alter flow.
- **Task Prioritization from Server Issues Document**: When addressing server issues, prioritize based on the summary in `#file:Server_Issues_01.10.2025.md`. High/Medium-High priority tasks should be addressed first.
- **Server Issues Document Editing**: User has delegated the following responsibilities to the AI regarding the `#file:Server_Issues_01.10.2025.md` document:
  - **Duplicate Removal**: Remove duplicate entries from the document.
  - **Re-numbering**: Re-number items in the document to maintain sequential order after duplicate removal.
  - **Completed Items**: Move items marked with a green checkmark (✅) to a "Completed items" section at the bottom of the document.
  - **Reordering**: Reorder the uncompleted items and renumber them, updating small sections as needed.
- **Issue Prioritization**: When reordering issues in `#file:Server_Issues_01.10.2025.md`, order them from the easiest and most impactful to apply (top) to the hardest and least impactful (bottom). Ensure that the text of each issue is preserved exactly.
- **Database Parameter Handling**: When calling the `execute` method in `database.py`, do not include the `return_cursor` parameter. The method returns a cursor by default, and specifying `return_cursor` is unnecessary and incorrect.

### Key Principles
- **FletV2 First**: Use `FletV2/` directory exclusively (modern implementation)
- **Single Responsibility**: Components <300 lines, focused on one purpose
- **Async Patterns**: Use `page.run_task()` for background operations
- **Theme System**: Use TOKENS instead of hardcoded colors
- **Verification**: Check `received_files/` for actual transfers (not exit codes)
- **Avoid Assumptions**: Always check the current actual state and figure things out from there.
- **Reasoning**: Apply the highest reasoning, take your time.
- **System Integrity**: Make sure you are not breaking the system and removing functionality.
- **Problem Management**: Make sure you are not causing more problems than you are solving.
- **Code Removal**: Remove bad/unused/wrong/not appropriate/falty/duplicated/ redunded /unwanted/unnedded code, if this could be done without braking the system and not changing functionality.

### Testing Strategy
- Integration tests verify end-to-end flows
- Component tests isolate Flet UI elements
- Always verify file presence in `received_files/` directory
- Test responsive layouts on 800x600 minimum window size

### Core Integration Patterns

#### Subprocess Management (CRITICAL)
```python
# Flask API → RealBackupExecutor → C++ client (with --batch flag)
# File Lifecycle: SynchronizedFileManager prevents race conditions
self.backup_process = subprocess.Popen(
    [self.client_exe, "--batch"],  # --batch prevents hanging in subprocess
    stdin=self.PIPE,
    stdout=the self.PIPE,
    stderr=the self.PIPE,
    text=True,
    cwd=os.path.dirname(os.path.abspath(__file__)),  # CRITICAL: Working directory
    env=Shared.utils.utf8_solution.get_env()  # UTF-8 environment
)
```

#### File Transfer Verification (CRITICAL)
Always verify file transfers by checking actual files in `received_files/` directory:
- Compare file sizes
- Compare SHA256 hashes
- Verify network activity on port 1256

#### Configuration Generation Pattern
```python
# transfer.info must be generated per operation (3-line format)
def _generate_transfer_info(self, server_ip, server_port, username, file_path):
    with open("transfer.info", 'w') as f:
        f.write(f"{server_ip}:{server_port}\n")  # Line 1: server endpoint
        f.write(f"{username}\n")                 # Line 2: username
        f.write(f"{file_path}\n")                # Line 3: absolute file path
```

#### Server Issue Resolution

When addressing server issues, prioritize the following based on the summary of unresolved issues and recommendations from `Server_Issues_01.10.2025.md`:

**High / Medium-High Priority Tasks**:

1.  **Settings Validation (`save_settings` & `load_settings`):**
    *   Location: `server.py` (lines ~1650, 2291-2394)
    *   Implement `_validate_settings()` with schema (types, ranges, allowed keys) and call it from both save and load. Reject or fallback to defaults on invalid data.
2.  **Emergency DB Connections Cleanup:**
    *   Location: `server.py` (around line ~310) and `database.py` (lines ~306-317)
    *   Track emergency connections separately and ensure they are closed/returned after use.
3.  **Metrics Integration / Observability:**
    *   Location: Throughout `server.py` (hooks missing), Shared/observability available
    *   Add counters for connections/uploads/downloads and gauges for active clients/transfers; instrument a few high-value code paths.
4.  **Rate Limiting for Log Export:**
    *   Location: `server.py` (around line ~1640 / export logs code)
    *   Track last export timestamp per session and enforce 10s minimum interval.
5.  **Server Shutdown Cleanup (`stop()`):**
    *   Location: `server.py` (lines ~618-628 / `stop()`)
    *   On `stop()`, acquire `clients_lock`, call cleanup on each client, clear `clients` and `clients_by_name`, then proceed with shutdown.
6.  **Client AES Key Access Thread-Safety:**
    *   Location: `` class (lines ~199-204), callers at ~485
    *   Wrap access in `with self.lock:` or equivalent thread-safe getter.
7.  **Atomic Client Creation Race-Window (`add_client`):**
    *   Location: `server.py` (around 712-721)
    *   Use DB transaction or catch unique constraint errors and return friendly error; consider short critical section around memory insert. DB UNIQUE constraint already mitigates it.

**Medium / Medium-Low Priority Tasks**:

8.  **Timeout on File Export Operations:**
    *   Location: `server.py` (`_export_logs_sync()` around 1669)
    *   Read in chunks, enforce maximum allowed size, and fail after configured timeout.
9.  **Centralize `SERVER_VERSION` Usage:**
    *   Location: Multiple files referencing `SERVER_VERSION` with `globals()` checks (lines ~595, 1072, 1330, 1349, 1671)
    *   Import `SERVER_VERSION` from `config.py` everywhere and remove `globals()` checks.
10. **Replace Inline Repeated `asyncio` Imports:**
    *   Location: `server.py` (many async wrappers)
    *   Add `import asyncio` at module top and remove inline imports.
11. **Duplicate/Triple File-Read Logic for Logs:**
    *   Location: `server.py` (lines ~2075-2089 in `get_logs()`)
    *   Extract helper `_read_log_file(filepath, limit)` and reuse.
12. **Partial File Timeout Uses Wrong Time Base (Consistency):**
    *   Location: `server.py` (lines ~237-242) and `file_transfer.py`
    *   Standardize on monotonic time everywhere for these operations.
13. **`get_historical_data()` Uses Mock/Random Data:**
    *   Location: `server.py` (lines ~2014-2051, ~2032-2045)
    *   Add docstring warning that data is mock.
14. **No Input Validation on `get_historical_data()`:**
    *   Location: `server.py` (lines ~2014-2051)
    *   Add `VALID_METRICS` check and range validation for `hours`.
15. **Broad Exception Handlers Used Widely:**
    *   Location: Many places in `server.py` (58 instances)
    *   Replace with targeted exception types where possible; add `exc_info=True` to unexpected captures. Tackle opportunistically when editing related functions.
16. **Ensure `client.last_seen` Updated for Every Request:**
    *   Location: request handlers (note placed around `request_handlers.py:97`)
    *   Call `client.update_last_seen()` centrally in request dispatch before specific handler logic.

**Low Priority / Polish Tasks**:

17. **Response Time Placeholder:**
    *   Location: Issue referenced at line ~1199 (placeholder)
    *   Remove the placeholder.
18. **Retry Logic Refactor (Decorator):**
    *   Location: Multiple methods (get_clients, save_settings, etc.)
    *   Add simple `@retry` decorator with configurable attempts/backoff and apply to DB operations.
19. **Inconsistent Error Response Format Across ServerBridge:**
    *   Location: ServerBridge methods (multiple)
    *   Audit ServerBridge methods and ensure `_format_response(False, error=...)` is always used.
20. **No Timeout for Long-Running Operations:**
    *   Location: `server.py` (related to 8)
    *   Offload to executor with timeout and fail gracefully.
21. **Validate `export_format` Parameter:**
    *   Location: `server.py` (lines 86 and 2182-2185)
    *   Status: Already implemented — no action required.

**Duplicates / Items to Consider Removing**:

*   \#22 (`stop()` missing cleanup) is the same as #5 — merge them.
*   \#23 (historical data mock) is the same as #13 — merge them.
*   \#25 (atomic client creation) overlaps with #7 — consider merging and marking DB-constraint mitigation.
*   \#4 (response time placeholder) and #17 (response time placeholder) appear to reference the same missing metric — treat as single item.

---

# FletV2 Development Guide (Concise)

This AI Development Guide should be read in conjunction with the `#file:AI-Context` folder (for extremely important documentation, data, information, and rules) and the `#file:important_docs` folder (for important information and documentation).

This guide codifies the essential rules to generate high-quality, compatible, and efficient code for this repository, focused on the FletV2 application. It consolidates prior guidance into a single DRY reference.

CRITICAL: Work exclusively in `FletV2/`. The legacy `flet_server_gui/` is obsolete and kept only as a reference for anti-patterns to avoid. When in doubt, prefer Flet built-ins and patterns shown here. See `FletV2/important_docs/` for examples.

**CRITICAL**: Follow these exact import patterns to ensure proper module resolution and avoid import errors.

#### Parent Directory Path Management
```python
# Standard pattern for FletV2 files that need Shared imports
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
```

#### Import Organization (STRICT ORDER)
```python
# 1. Standard library imports (alphabetical)
import asyncio
import contextlib # ADDED: for contextlib.suppress
import logging
import os
import sys
from typing import Any, Callable, Dict, Optional, Set, Tuple, cast

import flet as ft

# 3. Local imports - utilities first
from utils.debug_setup import setup_terminal_debugging

# 4. ALWAYS import UTF-8 solution for subprocess/console I/O
import Shared.utils.utf8_solution as _  # noqa: F401,E402

# 5. Initialize logging BEFORE any logger usage
logger = setup_terminal_debugging(logger_name="module_name")

# 6. Local imports - application modules
from theme import setup_modern_theme
from utils.server_bridge import create_server_bridge
```

#### Import Anti-Patterns (AVOID)
```python
# ❌ WRONG: Star imports
from utils.server_bridge import *

# ❌ WRONG: Delayed UTF-8 import (causes encoding issues)
# Import at top level,