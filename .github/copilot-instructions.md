---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

# CyberBackup Framework - AI Coding Agent Instructions

## Architecture Overview
This is a **4-layer encrypted backup system** with hybrid web-to-native architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server
  ↓           ↓                    ↓                     ↓
HTTP      RealBackupExecutor    --batch mode       Custom Binary
requests  process management   + transfer.info     Custom Binary TCP Protocol
```

**Critical Understanding**: Flask API Bridge (`cyberbackup_api_server.py` + `real_backup_executor.py`) is the coordination hub. Web UI communicates ONLY with Flask API, never directly with C++ client or Python server.

**Key Client Components**:
- **Web Client**: Single 8000+ line HTML file with modular JavaScript classes (ApiClient, FileManager, App, ThemeManager, ParticleSystem, etc.)
- **C++ Client**: Production-ready executable with RSA/AES encryption, CRC verification, and --batch mode for subprocess integration
- **Both clients** connect to the same Python server but through different pathways (web→Flask→C++→server vs direct C++→server)

## CyberBackup — concise AI agent instructions

Purpose: help an AI coding agent be productive quickly. Read linked files before changing behavior.

High-level agent contract:
- Inputs: code, tests, and repository files; environment is Windows with vcpkg/CMake and Python 3.13+ available when running build scripts.
- Outputs: minimal, runnable changes (small patches or docs), tests or smoke-checks demonstrating the change, and a short verification note showing build/tests status.
- Error modes: missing C++ build artifacts, port conflicts (9090/1256), transfer.info race conditions. Always surface these explicitly when proposing changes.

- Big picture (read these first): `api_server/cyberbackup_api_server.py`, `api_server/real_backup_executor.py`, `python_server/server/server.py`, `scripts/one_click_build_and_run.py`, `Shared/utils/unified_config.py`, `Shared/utils/file_lifecycle.py`, `client/transfer.info`.

- Additional reference docs: read `CLAUDE.md` and `GEMINI.md` in the repo for agent-specific notes and past assistant interactions before making behavioral changes.

- Architecture (short): Web UI ↔ Flask API bridge (9090) → spawns C++ client (build/Release) in --batch mode → Python backup server listens on 1256. The Flask bridge is the coordination hub.

- Critical patterns to preserve:
    - transfer.info is a legacy 3-line file (server:port, username, absolute filepath). Many modules search common locations (see `Shared/utils/unified_config.py`).
    - Subprocess invocation: C++ client must run with `--batch` and cwd set to directory containing `transfer.info` (see `RealBackupExecutor` in `api_server/real_backup_executor.py`).
    - Use the file lifecycle helpers (`Shared/utils/file_lifecycle.py` / SynchronizedFileManager) to avoid race conditions when creating or copying `transfer.info`.

- Quick developer workflows (examples found in repo):
    - Fast start (recommended & canonical launcher): `scripts/one_click_build_and_run.py` (located at `scripts/one_click_build_and_run.py`) — this script is the canonical launcher for building and starting the full system, running checks, and creating `transfer.info` when missing.
    - Manual: start server first `python python_server/server/server.py` (port 1256), then API `python api_server/cyberbackup_api_server.py` (port 9090).
    - C++ build: use vcpkg toolchain: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"` then `cmake --build build --config Release` (output: `build/Release/EncryptedBackupClient.exe`).

- Tests and verification to run (repo examples): `tests/integration/test_complete_flow.py`, `tests/test_direct_executor.py`, `tests/test_web_gui_fix.py`. Always verify actual files show up in `server/received_files/` and compare SHA256 hashes.

- Project-specific gotchas (mention before edits):
    - Missing `--batch` or wrong cwd causes client to hang. Don't rely on subprocess exit code alone—verify file receipt.
    - Multiple legacy `transfer.info` locations exist; prefer using `unified_config` helpers.
    - Port conflicts: check ports 9090 and 1256 before starting services.

- When changing integration code, run the minimal smoke test: start server, start API, generate a small test file and run the executor path (or use `one_click_build_and_run.py`). Update tests under `tests/` accordingly.

If anything here is unclear or you'd like more detail on a specific file (example: exact RealBackupExecutor flow or transfer.info lifecycle), tell me which file and I'll expand the section.
# 3. Build C++ client (after any C++ changes)

## TECH STACK
- Python 3.13+
- vcpkg/CMake for C++ builds

## DEVELOPMENT ENVIRONMENT

- Editor/IDE: Feature-rich environment with GitHub Copilot, Inline Chat, and AI code actions for Python.
- GitHub Copilot: Use Copilot Chat for high-level design and contextual code snippets. Utilize inline completions, next-edit suggestions, code generation and test generation.
- Inline Chat: Use for in-context code edits and questions.
- Python Analysis: Strict Python analysis (python.analysis.typeCheckingMode = "strict") should be used to catch type issues early. Pair with AI code actions to fix type errors.
- C/C++ Tooling: Enhanced colorization and workspace parsing control for native client build and debugging.
- Terminal: Integrated terminal for running build scripts (e.g., `scripts/one_click_build_and_run.py`) and tests. Integrated terminal with smooth scrolling, copy-on-selection, automation profile.
- Remote SSH: Support for remote development to run builds on remote Linux targets.
- Exclusions & watchers: Files/folders excluded from search and watchers (build, logs, received_files, etc.) to reduce noise.
- Notebook and testing helpers: Notebook improvements, consolidated run button, test/code lenses for generating tests.
- Misc AI & assistant settings: Local models/servers configured (Gemini/Copilot models), advanced next-edit suggestions and agent behavior.

## DEBUGGING

- Check ports 9090 and 1256 for conflicts before starting services.

## CODING TOOLS & LIBRARIES

- AI code actions for Python (python.analysis.aiCodeActions): Auto-generate docstrings, implement abstract classes, generate symbols, refactor format strings.
  - Recommended configuration:
    ````jsonc
    {
    	// Safe / recommended (non-intrusive) actions
    	"generateDocstring": true,            // adds docstrings for functions/classes
    	"implementAbstractClasses": true,     // scaffold missing abstract methods
    	"generateSymbol": true,               // create stubs for referenced-but-missing symbols
    	"convertFormatString": true,          // convert %/.format to f-strings
    	"addMissingImports": true,            // suggest/add missing imports
    	"organizeImports": true,              // sort/remove unused imports
    	"suggestTypeAnnotations": true,       // propose type annotations

    	// Conservative: don't auto-fix types or apply potentially breaking edits without review
    	"fixTypeErrors": false               // set true only after manual review
    	// Optional aggressive helpers (uncomment if you want more automatic edits)
    	// "autoApplyEdits": false,           // if supported by your extension: whether edits auto-apply
    	// "fixLintIssues": false,            // auto-fix lint issues (may be intrusive)
    	// "applyRefactorings": false         // enable to allow automated refactorings
    }
    ````
- Consider using sequential thinking mcp server after every 3-5 tool calls to organize thoughts and enhance reasoning.

## WORKFLOW & RELEASE RULES
- Before running integration tests (tests/integration/*), use strict Python analysis and AI code actions to fix type and lint issues.
- After decomposing each God Component into its single-responsibility classes, refactor the original God Component class to act as a Facade. It should instantiate the new classes and delegate public method calls to them, providing a single, stable interface for the application.

## TESTS AND VERIFICATION
- Run `scripts/one_click_build_and_run.py` in the integrated terminal to smoke-test the full pipeline.

## VIRTUAL ENVIRONMENT
- To activate the `flet_venv` virtual environment in PowerShell, use the following command within the project directory:
```powershell
& .\flet_venv\Scripts\Activate.ps1
```
- Alternatively, use the full absolute path:
```powershell
& C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\flet_venv\Scripts\Activate.ps1
```
- To deactivate the virtual environment:
```powershell
deactivate
```

## PYTHON ANALYSIS CONFIGURATION

- To avoid "End of file expected" errors in `pyrightconfig.json`, ensure the file contains valid JSON with a single root object. Merge any duplicate or misplaced configurations into a single, well-formed JSON structure. Example:

```json
{
  "typeCheckingMode": "standard",
  "include": ["python_server", "api_server", "Shared", "scripts", "Database", "."],
  "exclude": [
    "tests/",
    "test/",
    "**/tests/",
    "**/test/", 
    "test_*.py",
    "*_test.py",
    "**/test_*.py",
    "**/*_test.py",
    "venv",
    "kivy_venv_new",
    "__pycache__",
    ".git"
  ],
  "reportMissingImports": true,
  "reportUnusedVariable": true,
  "reportUnknownMemberType": true,
  "reportUnboundVariable": true,
  "venvPath": "C:\\Users\\tom7s\\Desktopp\\Claude_Folder_2\\Client_Server_Encrypted_Backup_Framework",
  "venv": "kivy_venv_new",
  "stubPath": "stubs"
}
```

## MARKDOWN FORMAT

- This project uses GitHub Flavored Markdown (GFM) for documentation. GFM features include:
    - Headings with `#`
    - Bullet and numbered lists
    - Code blocks with syntax highlighting (e.g., ```python)
    - Tables with pipe separators (`|`)
    - Bold (`**`) and italic (`*`) text
    - Links and references

### Types of Markdown

Markdown is a lightweight markup language for formatting text. There are several variants (flavors) with different features. Here's an overview:

#### Common Markdown Types/Flavors
1. **Standard Markdown** (Original by John Gruber, 2004)
   - Basic syntax: headers, lists, links, emphasis, code blocks.
   - No tables, strikethrough, or advanced features.

2. **GitHub Flavored Markdown (GFM)**
   - Extends standard Markdown with GitHub-specific features.
   - Includes: tables, task lists, strikethrough, fenced code blocks with syntax highlighting, autolinks, and more.
   - Widely used on GitHub, GitLab, and similar platforms.

3. **CommonMark**
   - A standardized specification (2014) for consistent Markdown parsing.
   - Aims to be unambiguous and compatible with most implementations.
   - Supports basic features; extensions for tables, etc., are separate.

4. **MultiMarkdown**
   - Adds features like tables, footnotes, citations, and metadata.
   - Used for academic and technical writing.

5. **Markdown Extra** (PHP Markdown Extra)
   - Extends standard Markdown with tables, definition lists, footnotes, and abbreviations.
   - Popular in static site generators like Jekyll.

6. **Other Variants**
   - **Pandoc Markdown**: Supports complex features like citations, cross-references, and multiple output formats.
   - **R Markdown**: For R programming, includes code execution and output embedding.
   - **Dialects**: Platform-specific like Reddit's or Stack Overflow's (similar to GFM).

#### How to Identify Which Type You're Using
- **Check Features**: Look for specific syntax in your file.
  - Tables (`| Header |`): Likely GFM, MultiMarkdown, or Markdown Extra.
  - Strikethrough (`~~text~~`): GFM or CommonMark with extensions.
  - Task lists (`- [x] Item`): GFM.
  - Fenced code blocks with language (````python`): GFM or CommonMark.
- **Context/Platform**: 
  - GitHub/GitLab repos: Usually GFM.
  - Static sites (e.g., Jekyll): Markdown Extra.
  - Academic tools: MultiMarkdown or Pandoc.
- **Parser/Renderer**: The tool processing the Markdown determines support (e.g., GitHub's renderer uses GFM).
- **File Extension**: All use `.md`, but content reveals the flavor.
- **Test Parsing**: Use online tools like Dillinger or Markdown parsers to see what renders.

The project's specified format is GitHub Flavored Markdown (GFM), as indicated by its use of tables, fenced code blocks with language specifiers, and other GFM-specific features. While it could be parsed by other Markdown processors (e.g., CommonMark or MultiMarkdown) with varying levels of support, GFM should be preferred. If you encounter parsing issues, check for GFM-specific syntax.