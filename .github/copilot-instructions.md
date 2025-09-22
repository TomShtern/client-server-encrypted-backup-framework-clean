---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

# CLAUDE.md - FletV2 Development Guide
This file provides Claude and Claude Code comprehensive guidance for working with FletV2 - a clean, framework-harmonious Flet desktop application that demonstrates proper Flet patterns and best practices.
Claude and Claude Code will adhere and reference this file for all FletV2-related development tasks.

**CRITICAL**: We work exclusively with `FletV2/` directory. The `flet_server_gui/` is obsolete, over-engineered, and kept only as reference of what NOT to do.
 you should reference the `important_docs/` folder for component usage examples and documentation.
---

## ⚙️ Essential Configuration

### UTF-8 Support
```python
# ALWAYS import this in any Python file that deals with subprocess or console I/O
import Shared.utils.utf8_solution
```

### Virtual Environments

The `flet_venv` virtual environment is specifically for the Flet-based client application in the `FletV2/` directory, managing its dependencies like Flet 0.28.3 and related UI libraries.

Other virtual environments are for separate components like the server-side, isolating dependencies needed for encryption, networking, or database handling. Check the project directory for venv folders to confirm their specific purpose. For example, the server-side components may have a virtual environment named `server_venv`. In the Client-Server Encrypted Backup Framework, the virtual environment named `venv` is designated for the server-side components. It isolates dependencies for encryption, networking, database handling, and backend logic—separate from the Flet client to avoid conflicts and ensure clean separation of concerns.

### Workspace Setup (VS Code)

When creating a new workspace, especially in VS Code, focus on the `FletV2/` directory to avoid errors. The goal is to work on a specific part of the larger project without cluttering the directory, ensuring changes in the sub-workspace are saved to the main workspace.

**Recommended Workspace Structure:**

Include only the `FletV2/` folder as the workspace root:

-   `FletV2/` (This is the only folder that MUST be included in the workspace.)

**Why this works:**

-   `FletV2` is self-contained and uses local imports.
-   Opening the entire repository can lead to errors due to legacy/obsolete folders and mixed environments.

**Recommended Subfolders/Files inside `FletV2` (included automatically when `FletV2` is the workspace root):**

-   `utils/`, `views/` (Required for imports)
-   `storage/` (Runtime temporary/data)
-   `.vscode/` (Workspace settings)
-   `requirements.txt` (Environment setup)
-   `tests/` (Optional, but recommended for test discovery)
-   `docs/` (Optional, harmless)

**Things to avoid:**

-   Do NOT include anything outside `FletV2` (e.g., old GUI, server-side roots, global venvs, or `.github`).

**Recommended `.code-workspace` file (save next to `FletV2`):**

```json
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    // Keep Pylance focused on this folder only
    "python.analysis.extraPaths": ["."],
    "python.defaultInterpreterPath": "${workspaceFolder}\\flet_venv\\Scripts\\python.exe",
    // Optional: tame indexing if you previously saw huge diagnostics
    "python.analysis.diagnosticMode": "workspace",
    "python.testing.pytestArgs": ["tests"],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
  }
}
```

**Quick Setup Steps:**

1.  **Open Folder:** File > Open Folder… and select `FletV2` (or open the `.code-workspace` file above).
2.  **Create venv:** `python -m venv flet_venv`
3.  **Activate and install:** `pip install -r requirements.txt`
4.  **Run:** `python main.py` (or use a VS Code Run configuration)

**Gotchas:**

-   Don’t open the repository root or add parent folders to the workspace; the existing code-workspace inside FletV2 targets “..” which reintroduces legacy code and errors.
-   Some modules add higher-level paths to `sys.path` defensively; that’s safe even when the parent isn’t included.
-   If you need server-side development later, use a separate workspace to avoid environment and lint noise.
-   If you just want fewer files visible, keep them out of VS Code’s Explorer but still reference them in `extraPaths`.

#### Resolving Imports from Outside FletV2

If your FletV2 project depends on code from other folders in the repository (e.g., `Shared`, `python_server`, `api_server`), follow these steps to ensure VS Code resolves the imports correctly:

**Overall Idea:**

Turn any folder that provides code (shared libraries, utils, AI modules) into an installable Python package, then `pip install -e /path/to/package` inside your `flet_venv`. VS Code + Pylance will then resolve imports no matter which subfolder you open.

**1 — Recommended Layout (use src layout)**

```
Project root (example monorepo):

/big-repo
  /fletv2                # your current workspace (app)
  /shared_utils          # code used by fletv2
    pyproject.toml or setup.py
    /src
      /shared_utils
        __init__.py
        helpers.py
  /ai_config_lib         # optional: same pattern
  requirements.txt
```

FletV2 imports like:

```python
from shared_utils.helpers import do_something
```

**2 — Simple `setup.py` Approach (works everywhere; editable install supported)**

Place this `setup.py` inside `shared_utils/`:

```python
# shared_utils/setup.py
from setuptools import setup, find_packages

setup(
    name="shared_utils",
    version="0.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
)
```

Create `src/shared_utils/__init__.py` and your module files.

Then, from your activated `flet_venv`:

```bash
# from anywhere — activate your flet_venv first
cd C:\path\to\big-repo\shared_utils
pip install -e .
```

Repeat for other shared packages (e.g. `ai_config_lib`).

**3 — Modern `pyproject.toml` (PEP 517/621) — alternate**

If you prefer `pyproject`, minimal `pyproject.toml` with setuptools backend:

```toml
# shared_utils/pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "shared_utils"
version = "0.0.0"
dependencies = []
```

Keep code in `src/shared_utils/...` and `pip install -e .` works the same.

**4 — Install all shared packages from one place (convenient)**

Create `requirements.txt` in repo root:

```
-e ./shared_utils
-e ./ai_config_lib
flet
other-runtime-deps==1.2.3
```

Then in `flet_venv`:

```bash
pip install -r C:\path\to\big-repo\requirements.txt
```

This installs all local packages in editable mode.

**5 — Verify everything works**

Activate venv, then run:

```bash
python -c "import shared_utils; print(shared_utils.__file__)"
python -c "import shared_utils.helpers; print('ok')"
pip list | findstr shared_utils
```

In VS Code:

Ensure `flet_venv` is selected as interpreter.

Restart Pylance: `Ctrl+Shift+P` → `Pylance: Restart Language Server`.
Imports should become resolved and the massive error flood will vanish.

**6 — Notes & Best Practices**

*   Editable install (`-e`) saves you from reinstalling after edits — changes in `src/` are used immediately.

*   Use `src` layout to avoid accidental import-from-root problems.

*   If you have many internal packages, keep a top-level `requirements.txt` listing `-e` references so teammates can `pip install -r`.

*   For CI or production, use non-editable installs (build wheels) or a private index; editable is for development.

*   If packages export CLI tools, add `entry_points` in `setup.py` or `pyproject.toml`.

#### Addressing Type Checking Issues (Pylance/Pyright)

Due to incomplete type stubs in the Flet package, you might encounter numerous "unknown type" errors. While a proper solution involves contributing to or awaiting updates from the Flet project, a temporary workaround is to adjust the `typeCheckingMode` within the `FletV2` workspace. This will enable basic error detection (e.g., undefined names, import issues) while suppressing advanced checks that often trigger false positives with Flet.

**Steps:**

1.  **Edit `pyrightconfig.json`:**
    -   Ensure `"extraPaths"` only includes local paths (e.g., `"./utils"`, `"./views"`) and *excludes* any external or parent paths (e.g., `".."`, `"../Shared"`). **This is a MUST**.
    -   Set `"typeCheckingMode"` to `"basic"` to enable basic error detection and suppress advanced checks.
    -   Add the following paths to `extraPaths`: `"./", "./FletV2", "./Shared", "./python_server", "./api_server"`
    -   Add `"reportGeneralTypeIssues": false`, `"reportUnknownMemberType": false`, `"reportUntypedFunctionDecorator": false` to suppress noisy type errors.

    ```json
    {
      "include": [
        "."
      ],
      "exclude": [
        "**/node_modules",
        "**/__pycache__",
        "**/flet_venv",
        "logs",
        "**/*.log",
        "tests/**",
        "important_docs/**",
        "docs/**",
        "Flet_Documentation_From_Context7_&_web/**",
        "storage/**",
        "**/build/**",
        "**/dist/**",
        "**/theme_original_backup.py",
        "scripts/**"
      ],
      "stubPath": "./stubs",
      "typeCheckingMode": "basic",
      "extraPaths": ["./", "./FletV2", "./Shared", "./python_server", "./api_server"],
      "reportGeneralTypeIssues": false,
      "reportUnknownMemberType": false,
      "reportUntypedFunctionDecorator": false
    }
    ```

2.  **Create a minimal local type stub for Flet:**
    - Create a folder named `stubs` at the root of your project.
    - Inside the `stubs` folder, create a file named `flet.pyi`.

    ```python
    # stubs/flet.pyi
    from typing import Any, Optional, Tuple, Callable, List, Dict

    Page = Any
    Control = Any
    Text = Any
    Icon = Any
    Row = Any
    Column = Any
    Chip = Any
    Padding = Any
    BorderRadius = Any
    AnimatedSwitcher = Any
    AnimationCurve = Any
    BoxShadow = Any
    SnackBar = Any
    ThemeMode = Any
    NavigationRail = Any
    NavigationRailDestination = Any
    FloatingActionButton = Any
    Container = Any
    IconButton = Any
    Icons = Any
    Theme = Any
    Colors = Any
    VerticalDivider = Any
    Animation = Any
    ControlEvent = Any
    KeyboardEvent = Any
    NavigationRailLabelType = Any
    AnimatedSwitcherTransition = Any
    SafeArea = Any
    Optional = Any

    class ServerBridge:
        def add_client(self, *args: Any, **kwargs: Any) -> Any: ...
        def load_settings(self, *args: Any, **kwargs: Any) -> Any: ...
        def save_settings( *args: Any, **kwargs: Any) -> Any: ...
        def disconnect_client(self, *args: Any, **kwargs: Any) -> Any: ...
        def delete_client(self, *args: Any, **kwargs: Any) -> Any: ...
        def download_file(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_table_data(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_logs(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_files(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_clients(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_client_files(self, *args: Any, **kwargs: Any) -> Any: ...
        def delete_file(self, *args: Any, **kwargs: Any) -> Any: ...
        def get_database_info(self, *args: Any, **kwargs: Any) -> Any: ...
        def is_connected(self, *args: Any, **kwargs: Any) -> Any: ...

    class StateManager:
        def __init__(self, *args: Any, **kwargs: Any) -> None: ...
        def set_progress(self, *args: Any, **kwargs: Any) -> Any: ...
        def subscribe_settings(self, *args: Any, **kwargs: Any) -> Any: ...

    def run_task(self, *args: Any, **kwargs: Any) -> Any: ...
    """Flet stub file."""

    """
    This is a minimal stub file for the Flet library. It is intended to silence type errors
    caused by missing type hints in the Flet library. It is not a complete type definition
    for Flet, and should not be used as such.
    """

3.  **Suppress Specific Errors (If Needed):**
    -   Use `# type: ignore` on specific lines or blocks of code where type errors persist and cannot be immediately resolved. This should be used sparingly and with caution (e.g., `# type: ignore[unknown-member]`).

**Additional Recommendations:**

-   **Monitor and Iterate**: After applying, write or edit a small file (e.g., a view in `views/`) and check Pyright's output. If it's still too noisy, we can tweak further (e.g., set more reports to "none").
-   **Best Practices**: Always run `ruff check .` and `mypy .` (as per AGENTS.md) alongside Pyright for complementary linting. Test on a minimal window size (800x600) to catch responsive issues early.

**Important Considerations:**

-   Switching to `"basic"` type checking mode is intended to provide a more productive experience.
-   Be mindful of potential runtime type errors. Thoroughly test your code even with type checking disabled.
-   Prioritize resolving import errors by following the "Resolving Imports from Outside FletV2" guidelines.

#### Linter Configuration (Pylance/Pyright/MyPy/Ruff)

To ensure consistent code quality, configure your linters to exclude unnecessary directories and focus only on your Python code.

**Recommended Configuration:**

*   **Exclusions**: Exclude `.git` files, `vcpkg` directories, and other irrelevant directories from linting.
*   **Inclusions**: Include `FletV2`, `Shared`, and `api_server` directories for linting.
*   **Exclusions for Tests**: Exclude test files named like `test_datatable_pix.py`, `test_fixes.py`, etc.

**Example configurations:**

*   **`.vscode/settings.json`**:
    ```json
    {
        "files.exclude": {
            "**/.git": true,
            "**/__pycache__": true,
            "**/vcpkg": true,
            "**/*.py[cod]": true,
            "**/.mypy_cache": true,
            "**/build": true,
            "**/dist": true,
            "**/.venv": true,
            "**/flet_venv": true,
            "**/node_modules": true,
            "**/logs": true,
            "**/*.log": true,
            "**/tests": true,
            "**/important_docs": true,
            "**/docs": true,
            "**/Flet_Documentation_From_Context7_&_web": true,
            "**/storage": true,
            "**/build": true,
            "**/dist": true,
            "**/theme_original_backup.py": true,
            "**/scripts": true,
            "**/*.git": true,
            "**/test_*.py": true
        },
        "search.exclude": {
            "**/.git": true,
            "**/__pycache__": true,
            "**/vcpkg": true,
            "**/*.py[cod]": true,
            "**/.mypy_cache": true,
            "**/build": true,
            "**/dist": true,
            "**/flet_venv": true,
            "**/node_modules": true,
            "**/logs": true,
            "**/*.log": true,
            "**/tests": true,
            "**/important_docs": true,
            "**/docs": true,
            "**/Flet_Documentation_From_Context7_&_web": true,
            "**/storage": true,
            "**/build": true,
            "**/dist": true,
            "**/theme_original_backup.py": true,
            "**/scripts": true,
            "**/*.git": true,
            "**/test_*.py": true
        },
        "python.analysis.extraPaths": [
            "./FletV2",
            "./Shared",
            "./api_server"
        ]
    }
    ```

*   **`pyproject.toml` (Ruff configuration)**:
    ```toml
    [tool.ruff]
    line-length = 110
    select = ["ALL"]
    ignore = [
        "D203", # One-line docstring should have one blank line before and after
        "D212", # Multi-line docstring summary should start at the first line
        "D213", # Multi-line docstring summary should start at the second line
        "D400", # First line should end with a period
        "D401", # First line should be in imperative mood
        "D403", # First word of the docstring should be properly capitalized
        "E501",
    ]
    exclude = [
        ".git",
        "__pycache__",
        "vcpkg",
        "*.py[cod]",
        ".mypy_cache",
        "build",
        "dist",
        ".venv",
        "flet_venv",
        "node_modules",
        "logs",
        "*.log",
        "tests",
        "important_docs",
        "docs",
        "Flet_Documentation_From_Context7_&_web",
        "storage",
        "build",
        "dist",
        "theme_original_backup.py",
        "scripts",
        "*.git",
        "test_*.py"
    ]
    ```

#### Quick Fix for 1K+ Type Errors (Basic Type Checking)
If facing a large number of type errors while needing to maintain basic type checking, follow these steps:

1.  **Update `pyrightconfig.json`**:
    -   Disable noisy type checking reports:
        -   `"reportGeneralTypeIssues": false`
        -   `"reportOptionalMemberAccess": false`
        -   `"reportUnknownMemberType": false`
        -   `"reportMissingTypeStubs": false`

2.  **Address Remaining Type Errors**:
    -   Example Fix (A): `utf8_solution.py` - Type mismatch:
        ```python
        # Before: return get_display(text)  # Could return bytes or str
        # After: return str(get_display(text))  # Explicit str cast
        ```
    -   Example Fix (B): `capture_baseline_metrics.py` - Missing import:
        ```python
        # Added type ignore for graceful fallback import
        from utils.perf_metrics import get_metrics, reset_metrics  # type: ignore
        ```

## 🎯 CORE PRINCIPLES: Framework Harmony

### **The FletV2 Way - Work WITH Flet, Not Against It**

**Primary Directive**: Favor Flet's built-in features over custom, over-engineered solutions. Do not reinvent the wheel.

#### **Scale Test**: 
Be highly suspicious of any custom solution that exceeds 1000 lines. A 3000+ line custom system is an anti-pattern when a 50-450 line native Flet solution exists with full feature parity(or almost full parity). Code files ideally should remain between 600-800 lines, but this is not a hard limit.

#### **Framework Fight Test**: 
Work WITH the framework, not AGAINST it. If your solution feels complex, verbose, or like a struggle, you are fighting the framework. Stop and find the simpler, intended Flet way.

#### **Built-in Checklist**:
- Can `ft.NavigationRail` handle navigation?
- Can `expand=True` and `ResponsiveRow` solve layout?
- Can `control.update()` replace `page.update()`?
- Does a standard Flet control already do 90% of what you need?

### Error Handling Philosophy

When encountering errors, prioritize fixing them directly without introducing new issues. Avoid removing code as a primary solution; instead, focus on understanding the root cause and implementing a fix that preserves functionality. Utilize sequential thinking, context7 mcp, and web search to aid in problem-solving.

### Redundant File Analysis Protocol (CRITICAL FOR DEVELOPMENT)
**Before deleting any file that appears redundant, ALWAYS follow this process**:

1. **Analyze thoroughly**: Read through the "redundant" file completely
2. **Compare functionality**: Check if it contains methods, utilities, or features not present in the "original" file, that could benifet the original file.
3. **Identify valuable code**: Look for:
   - Helper functions or utilities that could be useful
   - Error handling patterns that are more robust
   - Configuration options or constants that might be needed
   - Documentation or comments that provide important context
   - Different implementation approaches that might be superior
4. **Integration decision**: If valuable code is found:
   - Extract and integrate the valuable parts into the primary file
   - Test that the integration works correctly
   - Ensure no functionality is lost
5. **Safe deletion**: Only after successful integration, delete the redundant file

**Why this matters**: "Simple" or "mock" files often contain valuable utilities, edge case handling, or configuration details that aren't obvious at first glance. Premature deletion can result in lost functionality and regression bugs.

**Example**: A "simple" client management component might contain useful date formatting functions or error message templates that the "comprehensive" version lacks.

### Identifying and Handling .git files

Filenames ending with ".git" (like files.py.git) are usually leftover patch/backup files created by a tool (merge/patch export, editor/IDE backup, or someone accidentally saved a downloaded git patch). They are not the repository .git directory.

How to identify and handle them (Windows / PowerShell):

- Peek at the start of the file — patch headers look like "diff --git a/… b/…" or "From <hash>".
- See if Git tracks it or it’s untracked.
- If it’s just a backup/patch you don’t need, move it out or delete it after verifying.

Commands:
````powershell
# show first 40 lines
Get-Content .\path\to\files.py.git -TotalCount 40

# search for patch markers
Select-String -Path .\path\to\files.py.git -Pattern "diff --git","From ","Index:","***" -SimpleMatch

# check git status for that file
git status --porcelain | Select-String "files.py.git"

# list untracked ignored files
git ls-files --others --exclude-standard | Select-String "files.py.git"

# move to a safe temp folder before deleting
New-Item -ItemType Directory -Path .\temp_backups -Force
Move-Item .\path\to\files.py.git .\temp_backups\
````

If the file looks like a patch and you want to apply it, open it and inspect contents first. If it’s binary or unknown, keep a copy before deleting.

### When going through massive logs:
On-Disk + Grep/Awk Tools

If you don’t want the overhead:
ripgrep (rg) or ag (silversearcher) – insanely fast search in files.
ast-grep – structured searching if logs have consistent format (JSON logs).
fzf – fuzzy finder, useful when you know part of the error.
Pipe logs through grep | tail -n 50 style workflows.

🔹 Using ripgrep (rg)

Fastest way to pull out the “couple of bad lines.”
Find all ERROR lines:
rg "ERROR" app.log
Show 5 lines of context around each match:
rg -C 5 "Exception" app.log
Search across multiple logs at once:
rg "timeout" /var/logs/
Stream logs + highlight in real time:
tail -f app.log | rg "ERROR"

🔹 Using ast-grep

Best if your logs are structured (e.g., JSON). Lets you query fields instead of regex spaghetti.
Example log (JSON):
{"level": "ERROR", "msg": "Database connection failed", "code": 500}
Find all ERROR-level logs:
sg -p ' { "level": "ERROR", ... } ' logs.json
Find logs with specific error codes:
sg -p ' { "code": 500, ... } ' logs.json
Match only the message field:
sg -p ' { "msg": $MSG } ' logs.json

🚀 Pro tip
Use ripgrep when you’re just scanning for keywords.
Use ast-grep when your logs are JSON or structured, so you can surgically extract only what matters.
Combine them with fzf (if you install it) for interactive filtering.
---

## ⚡ POWER DIRECTIVES: Maximum Impact Code Generation

### **Critical Framework Compliance (Flet 0.28.3 + Python 3.13.5)**

1. **Always use `control.update()` instead of `page.update()` to achieve 10x performance and eliminate UI flicker.**

2. **Leverage `ft.ResponsiveRow` and `expand=True` as your primary layout mechanism, eliminating the need for complex custom responsive systems.**

3. **Use `ft.NavigationRail.on_change` for navigation, completely removing the need for custom routing managers.**

4. **Use `ft.Theme` and `ft.ColorScheme` for styling, avoiding any custom theming logic over 50 lines.**

5. **Implement async event handlers using `async def` and `await ft.update_async()` to prevent UI blocking.**

6. **Use `page.run_task()` for background operations instead of creating custom threading or async management.**

7. **Always provide a fallback in server bridge initialization to ensure graceful degradation.**

8. **Utilize Flet's built-in `ThemeMode` for theme switching instead of creating custom theme toggle mechanisms.**

9. **Replace custom icon management with Flet's native `ft.Icons` enum, which provides comprehensive icon support.**

10. **Design views as pure function-based components that return `ft.Control`, avoiding complex class-based view systems.**

### **Performance & Anti-Pattern Guards**

11. **If your custom solution exceeds 1000 lines, you are fighting the framework - stop and find the Flet-native approach.**

12. **Prefer semantic color tokens like `ft.Colors.PRIMARY` over hardcoded hex values to ensure theme compatibility.**

13. **Use `ft.DataTable` for tabular data instead of building custom table components from scratch.**

14. **Implement error handling using `page.snack_bar` with built-in Flet colors for consistent user feedback.**

15. **Leverage `ft.TextTheme` for consistent typography across your entire application.**

### **Architectural Enforcement**

16. **Structure your desktop app as a single `ft.Row` with a `NavigationRail` and dynamic content area.**

17. **Create a modular `theme.py` as the single source of truth for all styling and theming logic.**

18. **Use `page.run_thread()` for operations that might block, ensuring responsive UI.**

19. **Design components with a maximum of ~400 lines(you dont have to, but its recommended estimates), forcing modularity and readability.**

20. **Always provide a simple, function-based fallback for every dynamic loading mechanism.**

### **Python 3.13.5 & Flet 0.28.3 Optimizations**

21. **Use `page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)` for instant Material 3 theming without custom color management.**

22. **Leverage `page.adaptive = True` for platform-specific UI rendering when targeting multiple platforms.**

23. **Use `ft.run(main, view=ft.AppView.WEB_BROWSER)` for development hot reload - identical runtime to desktop with instant updates.**

24. **Implement `page.theme_mode = ft.ThemeMode.SYSTEM` to automatically respect user system preferences.**

25. **Use `ft.SafeArea` to handle platform-specific UI constraints automatically.**

**Core Philosophy**: "Let Flet do the heavy lifting. Your job is to compose, not reinvent."

---

## 🏗️ FletV2 ARCHITECTURE PATTERNS

### **Main Application Structure (CANONICAL)**

```python
# FletV2/main.py - Modern desktop app with performance optimizations
import contextlib # Used for cleaner exception suppression
class FletV2App(ft.Row):
    """
    Enhanced FletV2 desktop app using pure Flet patterns with modern UI and performance optimizations.
    
    Features:
    - Lazy view loading with caching for performance
    - Modern Material Design 3 styling and animations
    - Collapsible navigation rail with keyboard shortcuts
    - State manager integration for reactive updates
    - Background task management
    - Enhanced error handling with graceful fallbacks
    """
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        
        # Performance optimization: lazy view loading and caching
        self._loaded_views = {}  # Cache for loaded views
        self._background_tasks = set()  # Track background tasks
        
        # Initialize state manager for reactive UI updates
        self.state_manager = None
        self._initialize_state_manager()
        
        # Initialize server bridge synchronously for immediate availability
        from utils.server_bridge import create_server_bridge
        
        # Initialize debug setup to avoid errors
        from utils.debug_setup import setup_terminal_debugging
        # ALWAYS import this in any Python file that deals with subprocess or console I/O
        # Import for side effects (UTF-8 configuration)
        import Shared.utils.utf8_solution as _  # Import for UTF-8 side effects # noqa: F401

        # Initialize logging and environment BEFORE any logger usage
        logger = setup_terminal_debugging(logger_name="FletV2.main")
        os.environ.setdefault("PYTHONUTF8", "1")
        
        # Local imports - application modules
        from theme import setup_modern_theme
        from utils.server_bridge import create_server_bridge

        # Import the real server adapter for production use
        try:
            from server_adapter import create_fletv2_server
            real_server_available = True
            logger.info("✅ Real server adapter imported successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Real server adapter not available: {e}")
            real_server_available = False
        
        # Application constants - dynamic based on server availability
        bridge_type = "Real Server Integration (with fallback capability)" if real_server_available else "Mock Server Development Mode"
        if real_server_available:
            logger.info("🚀 Real server integration available - production mode enabled")
        else:
            logger.info("🧪 Using mock server for development")
        
        self.server_bridge = create_server_bridge()
        
        # Create optimized content area with modern Material Design 3 styling
        self.content_area = ft.Container(
            expand=True,
            padding=ft.Padding(24, 20, 24, 20),  # Material Design 3 spacing standards
            border_radius=ft.BorderRadius(16, 0, 0, 16),  # Modern rounded corners
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE),  # Surface hierarchy
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(140, ft.AnimationCurve.EASE_OUT_CUBIC),  # Modern animation
            content=ft.AnimatedSwitcher(
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=160,
                switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
                switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
                expand=True
            )
        )
        
        # Create collapsible navigation rail with modern styling
        self.nav_rail_extended = True
        self.nav_rail = self._create_navigation_rail()
        
        # Build layout: NavigationRail + content area (pure Flet pattern)
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            self.content_area
        ]
        
        # Set up keyboard shortcuts and page handlers
        page.on_keyboard_event = self._on_keyboard_event
        
        # Load initial dashboard view immediately
        self._load_view("dashboard")
    
    def _create_navigation_rail(self) -> ft.Container:
        """Create enhanced collapsible navigation rail with modern UI styling and performance optimizations."""
        return ft.Container(
            content=ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                group_alignment=-0.8,
                min_width=68,  # Collapsed width
                min_extended_width=240,  # Extended width
                extended=self.nav_rail_extended,  # Collapsible functionality
                bgcolor