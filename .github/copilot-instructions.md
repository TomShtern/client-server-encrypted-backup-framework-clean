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
requests  process management   + transfer.info     Custom Binary TCP   Material Design 3
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
- **Problem Management**: Make sure you are not causing more problems than you solve. **Make sure you are not creating new problems instead of solving of solving them.**
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
    - User-level: `%USERPROFILE%\.qwen.settings.json` (on Windows; equivalently `~/.qwen/.settings.json`)
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
- **VS Code Release Notes**: To view the release notes of the latest VS Code update:
  1. Use the "Show release notes" command in VS Code (open the Command Palette with Ctrl + Shift + P and run Show release notes) to view the latest update notes inside the editor.
  2. Or view them online at https://code.visualstudio.com/updates.
- **Flet GUI Integration Troubleshooting**: When integrating the Python server and SQLite3 database into the FletV2 GUI and encountering issues such as broken navigation or views not displaying:
  - Use ultrathink to systematically analyze the issues and identify the root causes.
  - Prioritize fixing the problems while ensuring not to introduce further issues or break existing functionality. The system was working before the integration, so focus on changes made during the integration process.
  - Employ all appropriate tools to diagnose and resolve the issues effectively.
- **VS Code Language Server**: Be aware that VS Code language server analysis might show errors from temporary chat editing buffers that are not present in the actual saved files. Always verify the actual saved file for errors.
- **Virtual Environment**: When working in the `flet_venv` virtual environment, ensure that the environment is activated before running any Python scripts.
- **Flet GUI State**: When the Flet GUI shows loaded data briefly before breaking and exhibiting navigation and glitching issues, use ultrathink to find the root cause and fix it without introducing new problems.
- **Playwright MCP**: When using Playwright MCP, run the Flet GUI in webview mode to take screenshots and automatically verify fixes.
- **Context7 MCP**: When unsure about anything Flet-related, use context7 MCP to get official, up-to-date context. If context7 does not provide an answer, perform web searches.
- **Running `main.py`**: When running `main.py` directly, ensure the file has an `if __name__ == "__main__":` block to actually call `main()` or start the app. Use `ft.app(target=main)` inside the `if __name__ == "__main__":` block.
- **Async Setup Functions**: When calling `setup_func()` for a view, check if it's an async coroutine. If it is, use `await setup_func()` to ensure it's properly awaited.
- **Flet Launch Verification**: After launching the Flet app, verify that the Flet backend server process is running and that the WebSocket endpoint is available. Check for WebSocket connection failures in the browser console.
- **Environment Flags Check**: When launching the Flet GUI, check the environment flags `CYBERBACKUP_DISABLE_GUI` and `INTEGRATED_GUI` to ensure they are correctly configured and not interfering with Flet's internal spawning when using WEB_BROWSER mode.
- **Lazy Server Initialization**: When using lazy server initialization, ensure that the `BackupServer` instance is created in the main thread to avoid `ValueError: signal only works in main thread of the main interpreter`.
- **GUI-Only Standalone Mode**: Be aware that the GUI may start in GUI-only standalone mode without the server bridge if `main.py` is run directly. In this mode, data operations will show empty states. Use `python start_with_server.py` for full server integration.
- **Embedded GUI Conflicts**: The embedded GUI in `BackupServer` should be disabled to prevent conflicts when running the Flet GUI with the server integration.
- **Inline Diagnostics Panel**: Implement an inline diagnostics panel for non-dashboard view load failures in `main.py` to prevent blank/gray screens. Track the most recent view loading error using the `_last_view_error` attribute.
- **Navigation Smoke Test**: Implement a navigation smoke test that automatically cycles through every view and logs success or any captured errors. To run the smoke test, launch the app with the environment variable `FLET_NAV_SMOKE=1`.
- **Dashboard Update Guard**: When updating the dashboard, add a guard to prevent updating controls that aren't yet attached to the page. This prevents errors during the initial data refresh.
- **Dashboard Loading**: The dashboard view should load correctly after the GUI initializes. If the dashboard is not loading, ensure that the `navigate_to("dashboard")` call is present at the end of the `initialize()` method and that the `initialize()` method is being called successfully. Debug output should be added to the `_perform_view_loading` method to identify any issues during view switching. Sentry SDK initialization should be disabled temporarily to rule out any crashes during module import.
- **`setup_func` Callability**: When calling `setup_func()` , add a defensive guard ensuring `setup_func` is callable before invoking it. If in an async context, handle coroutine functions while keeping changes minimal and avoiding alterations to existing behavior.
- **Database View Glitches**: If the app starts having fatal glitches after navigating to the database page, ensure that `database_table.update()` is not called before the table is attached to the page.
- **Problematic Charts**: Be aware that the analytics view has chart components (`LineChart`, `BarChart`, `PieChart`) that are complex Flet controls and may cause issues. If the analytics page is broken, these may be the cause. Replace them with simpler UI primitives if necessary.
- **Initial `state_manager.py` Errors**: If the application hangs during state manager initialization, check for corrupted Python code or syntax errors in the `state_manager.py` file, particularly within the docstring.
- **Circular Import Deadlocks**: Circular import deadlocks can occur when the `setup_terminal_debugging()` function, called at module import time in `state_manager.py`, triggers an import of the dashboard module, which then imports `state_manager` again. To prevent this, avoid calling `setup_terminal_debugging()` at the module level in `state_manager.py`.
- **Analytics Page Issues**: If the analytics page breaks the GUI, it's likely due to issues with the Flet chart components (`LineChart`, `BarChart`, `PieChart`). Replace them with simpler UI primitives if necessary.
- **Navigation and View Loading**: If navigation breaks and views don't load, check for async/await issues in setup functions, and ensure the Flet app is properly initialized and the server bridge is connected. Ensure `page.on_connect` is being called, and if not, call `navigate_to("dashboard")` directly after initialization. The `initialize()` method should be called successfully.
- **Database Page Issues**: If the database page breaks the GUI, it's likely due to issues with the `ft.DataTable` component. Replace `ft.DataTable` with a simpler `ListView` of `Cards`.
- **Analyze Before Changing**: Before making any changes, analyze the code for potential issues and use ultrathink to identify the root cause of problems before attempting fixes.
- **Avoid Assumptions**: Before making changes, ensure a thorough understanding of the code and the problem to be solved. Don't assume anything, verify everything.
- **Flet Component Instability**: Be aware that complex Flet components like `ft.DataTable`, `LineChart`, `BarChart`, and `PieChart` might be unstable in Flet version 0.28.3 and can cause browser crashes. If encountering issues with these components, consider replacing them with simpler UI primitives.
- **Database View Blocking**: Avoid making synchronous server calls during view construction. Instead, use placeholder data and load data asynchronously after the view is attached.
- **Database View Async Data Loading**: When implementing asynchronous data loading in database and analytics views, ensure that the data is fetched and loaded after the view is attached, preventing UI blocking and improving responsiveness. Initialize with placeholder data to provide immediate feedback to the user.
- **Flet GUI Launch in Webview Mode**: Use Playwright MCP to launch the Flet GUI in webview mode to take screenshots and automatically verify fixes.
- **Debug Prints Preservation**: Save the important debug prints that will help in the future for similar problems, but remove excessive debug statements that clutter the code.
- **Docstring Position**: Ensure that the docstring is the first statement after the function definition to avoid parsing errors.
- **Module-Level Code**: Avoid calling functions with potential side effects, especially those that might trigger imports, at the module level. These calls can lead to circular import deadlocks.
- **Asynchronous Data Loading**: When facing issues with UI freezing or crashing, particularly in the database and analytics pages, the root cause is often synchronous calls to the server bridge during view construction.
  - **Solution**: Apply an asynchronous data loading pattern:
    1.  **Fast View Construction**: Construct the view quickly with placeholder data.
    2.  **Lazy Data Loading**: After the view is attached (typically within `setup_subscriptions`), initiate an asynchronous call to fetch the actual data.
    3.  **Defensive Updates**: Ensure that updates to the UI are performed only after verifying that the relevant controls are attached to the page.
- **Flet Component Instability**: Certain Flet components, including `ft.DataTable`, `LineChart`, `BarChart`, and `PieChart`, may be unstable in version 0.28.3 and can cause browser crashes. If encountering issues with these components, consider replacing them with simpler UI primitives such as `ListView` or `Card`.
- **View Loading Issues**: When debugging issues with view loading, start by checking if the `page.on_connect` handler is being called. If it is not, ensure that the `navigate_to()` method is called directly after initialization. Add debug output to the `_perform_view_loading` method to identify any issues during view switching. Temporarily disable Sentry SDK initialization to rule out any crashes during module import.
- **Circular Import Deadlocks**: Circular import deadlocks can occur when the `setup_terminal_debugging()` function, called at module import time in `state_manager.py`, triggers an import of the dashboard module, which then imports `state_manager` again. To prevent this, avoid calling `setup_terminal_debugging()` at the module level in `state_manager.py`.
- **Fault Isolation**: When debugging complex issues, isolate the fault by commenting out sections of code, especially during view construction. Use incremental development to identify the minimum amount of code that is necessary to cause the error.
- **Log Analysis**: When analyzing logs, be aware that VS Code language server analysis might show errors from temporary chat editing buffers that are not present in the actual saved files. Always verify the actual saved file for errors.

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
    [self.client_exe, "--batch"],