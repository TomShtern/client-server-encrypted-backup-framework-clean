<system_tools>

# 💻 SYSTEM_TOOL_INVENTORY

### 🛠 CORE UTILITIES: Search, Analysis & Refactoring

- **ripgrep** (`rg`) `v14.1.0`
  - **Context:** Primary text search engine.
  - **Capabilities:** Ultra-fast regex search, ignores `.gitignore` by default.
- **fd** (`fd`) `v10.3.0`
  - **Context:** File system traversal.
  - **Capabilities:** User-friendly, fast alternative to `find`.
- **fzf** (`fzf`) `v0.67.0`
  - **Context:** Interactive filtering.
  - **Capabilities:** General-purpose command-line fuzzy finder.
- **tokei** (`tokei`) `v12.1.2`
  - **Context:** Codebase Statistics.
  - **Capabilities:** Rapidly counts lines of code (LOC), comments, and blanks across all languages.
- **ast-grep** (`sg`) `v0.40.0`
  - **Context:** Advanced Refactoring & Linting.
  - **Capabilities:** Structural code search and transformation using Abstract Syntax Trees (AST). Supports precise pattern matching and large-scale automated refactoring beyond regex limitations.
- **bat** (`bat`) `v0.26.0`
  - **Context:** File Reading.
  - **Capabilities:** `cat` clone with automatic syntax highlighting and Git integration.
- **eza** (`eza`) `v0.23.4`
  - **Context:** Directory Listing.
  - **Capabilities:** Modern replacement for `ls` with git status icons and colors.
- **sd** (`sd`) `v1.0.0`
  - **Context:** Text Stream Editing.
  - **Capabilities:** Intuitive find & replace tool (simpler `sed` replacement).
- **jq** (`jq`) `v1.8.1`
  - **Context:** JSON Parsing.
  - **Capabilities:** Command-line JSON processor/filter.
- **yq** (`yq`) `v4.48.2`
  - **Context:** Structured Data Parsing.
  - **Capabilities:** Processor for YAML, TOML, and XML.
- **Semgrep** (`semgrep`) `v1.140.0`
  - **Capabilities:** Polyglot Static Application Security Testing (SAST) and logic checker.

### 🐍 PYTHON EXCLUSIVES: Primary Development Stack

*Environment: 3.13.7*

- **Python** (`python`) `v3.13.7`
  - **Capabilities:** Core language runtime.
- **uv / pip** (`uv`) `Latest`
  - **Capabilities:** Package management. `uv` is the preferred ultra-fast Rust-based installer.
- **Ruff** (`ruff`) `v0.14.1`
  - **Capabilities:** High-performance linter and formatter. Replaces Flake8, isort, and Pylint.
- **Black** (`black`) `Latest`
  - **Capabilities:** Deterministic code formatter.
- **Pyright** (`pyright`) `v1.1.407`
  - **Capabilities:** Static type checker (Strict Mode enabled).

### 🌐 SECONDARY RUNTIMES

- **Node.js** (`node`) `v24.11.1` - JavaScript runtime.
- **Bun** (`bun`) `v1.3.1` - All-in-one JS runtime, bundler, and test runner.
- **Java** (`java`) `JDK 25 & 8` - Java Development Kit.

</system_tools>


# CyberBackup - AI Agent Instructions

> **Read first**: `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`

## System Overview

| Component     | Location                                  | Port |
|---------------|-------------------------------------------|------|
| Flask API     | `api_server/cyberbackup_api_server.py`    | 9090 |
| Python Server | `python_server/server/server.py`          | 1256 |
| Web UI        | `api_server/web_ui/index.html`            | —    |
| C++ Client    | `build/Release/EncryptedBackupClient.exe` | —    |
| FletV2 GUI    | `FletV2/main.py`, `start_with_server.py`  | —    |

**Data paths**: `data/storage/` (files), `data/database/defensive.db`, `logs/`

---

## Critical Rules

1. **UTF-8 first** — `from Shared.filesystem.utf8_solution import configure_utf8; configure_utf8()` before other imports in entrypoints. *Symptom: UnicodeEncodeError*
2. **Start listener** — Call `server_instance.start()` in `start_with_server.py`. *Symptom: C++ clients can't connect*
3. **Async boundary** — Wrap sync calls: `await run_sync_in_executor(fn, *args)`. *Symptom: GUI freeze*
4. **Bridge contract** — All methods return `{"success": bool, "data": Any, "error": str|None}`
5. **Monotonic time** — Use `time.monotonic()` for durations, never `time.time()`
6. **DB context** — `with db_manager.get_connection() as conn:` + `RLock()` for thread safety
7. **Logging** — Use `logger`, never `print()`
8. **Cleanup** — Always `finally` blocks; no silent exception swallowing
9. **C++ subprocess** — `Popen_utf8([exe, "--batch"], cwd=exe_dir)` with valid `transfer.info`
10. **Config** — `get_config(key, default)` from `Shared.config.unified_config`
11. **UI updates** — `control.update()` (fast) over `page.update()` (slow); never in loops

---

## Key Patterns

```python
# Async call pattern (FletV2)
result = await run_sync_in_executor(safe_server_call, bridge, 'get_clients')
if result.get('success'): render(result['data'])

# View signature
def create_X_view(bridge, page, state, search=None) -> (content, dispose_fn, setup_fn)

# State management
state = create_simple_state(page, bridge)
state.get("clients"); state.update("clients", data)
```

**5-Section Pattern**: See `FletV2/docs/architecture_guide.md`

---

## Flet 0.28.3 Gotchas

| Wrong                  | Correct                      |
|------------------------|------------------------------|
| `ft.UserControl`       | Functions returning controls |
| `ft.SelectableText`    | `ft.Text(selectable=True)`   |
| `ft.Icons.DATABASE`    | `ft.Icons.DATASET`           |
| `ft.Expanded()`        | `expand=True` property       |
| `ft.Colors.BACKGROUND` | `ft.Colors.SURFACE`          |

---

## C++ Client

1. **Build**: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake" && cmake --build build --config Release`
2. **transfer.info** (3 lines): `host:port`, `username`, `C:\absolute\path\to\file`
3. **Launch**: `Popen_utf8([exe, "--batch"], cwd=exe_dir)`
4. **Verify**: Exit code 0 + file in `data/storage/` with matching hash

---

## Commands

| Task        | Command                                             |
|-------------|-----------------------------------------------------|
| Full system | `python scripts/one_click_build_and_run.py`         |
| Flet+Server | `python FletV2/start_with_server.py`                |
| Tests       | `pytest tests/`                                     |
| Lint        | `ruff check FletV2 Shared python_server api_server` |

---

## Troubleshooting

| Issue          | Fix                                             |
|----------------|-------------------------------------------------|
| GUI freeze     | Wrap sync in `run_sync_in_executor`             |
| Unicode error  | UTF-8 bootstrap first; use `Popen_utf8`         |
| DB locked      | Context managers + retry with backoff           |
| C++ hangs      | Check `--batch`, `cwd`, `transfer.info` format  |
| Port busy      | `netstat -an | findstr :1256`; kill process     |

---

## Deep Dives

- **Protocol opcodes**: `python_server/server/protocol.py`
- **ServerBridge API**: `FletV2/utils/server_bridge.py`
- **Shared utilities**: `Shared/config/`, `Shared/validation/`, `Shared/filesystem/`
- **Architecture**: `FletV2/docs/architecture_guide.md`, `CLAUDE.md`

---

**Golden Rule**: Test the full chain (GUI → API → C++ → Server → `data/storage/`) and validate file hashes.
