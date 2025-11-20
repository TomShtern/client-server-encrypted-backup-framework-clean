# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<system_tools>

# 💻 SYSTEM_TOOL_INVENTORY

### 🛠 CORE UTILITIES: Search, Analysis & Refactoring

*High-performance tools for file operations and code intelligence.*
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

## Project Context

CyberBackup 3.0: Encrypted file backup system with Python server, FletV2 desktop GUI, and web API bridge. C++ client connects via binary protocol. SQLite database for metadata, encrypted files stored locally.

**Core Architecture:**
- **Python Backup Server** (port 1256): Handles C++ client connections, file transfers, encryption
- **FletV2 Desktop GUI**: Admin interface with Material Design 3, direct server method calls
- **API Server** (port 9090): Flask bridge for web GUI (stable, production-ready)
  - _Note: C++ replacement was prototyped but archived at `_archive/cpp_api_server_prototype/`_
- **C++ Client**: Binary protocol, AES-256-CBC encryption, RSA-1024 key exchange
- **SQLite Database**: `defensive.db` with connection pooling

## Recent Critical Changes

1. **Shared Reorganized**: Utilities now in subdirectories - `config/`, `filesystem/`, `validation/`, `logging/`, `monitoring/`
2. **Unified Configuration**: Use `Shared/config/unified_config.py` (replaces fragmented config sources)
3. **Memory Management**: Use `Shared/filesystem/memory_efficient_file_transfer.py` (prevents leaks)
4. **C++ API Server**: Experimental prototype archived at `_archive/cpp_api_server_prototype/` (see ARCHIVE_README.md)
   - Active API server is Flask-based at `api_server/cyberbackup_api_server.py`
5. **Fixed Issues**: 42 bugs documented in `docs/reports/CODE_ISSUES_AND_FIXES.md`

## Critical File Locations

**Core Server:**
- [python_server/server/server.py](python_server/server/server.py) - Main backup server
- [python_server/server/file_transfer.py](python_server/server/file_transfer.py) - Transfer management
- [python_server/server/database.py](python_server/server/database.py) - Database with connection pooling
- [python_server/server/client_manager.py](python_server/server/client_manager.py) - Client state management
- [python_server/server/request_handlers.py](python_server/server/request_handlers.py) - Protocol message handlers

**GUI:**
- [FletV2/main.py](FletV2/main.py) - Desktop GUI entry point
- [FletV2/server_adapter.py](FletV2/server_adapter.py) - ServerBridge for direct server calls
- [FletV2/scripts/start_with_server.py](FletV2/scripts/start_with_server.py) - Launcher with integrated server
- [api_server/cyberbackup_api_server.py](api_server/cyberbackup_api_server.py) - Current web API (being replaced)

**Shared Utilities (Reorganized into subdirectories):**
- [Shared/config/unified_config.py](Shared/config/unified_config.py) - Unified configuration manager
- [Shared/filesystem/memory_efficient_file_transfer.py](Shared/filesystem/memory_efficient_file_transfer.py) - Memory-bounded transfers
- [Shared/validation/validation_utils.py](Shared/validation/validation_utils.py) - Centralized validators
- [Shared/logging/logging_utils.py](Shared/logging/logging_utils.py) - Logging with rotation
- [Shared/utils/utf8_solution.py](Shared/utils/utf8_solution.py) - UTF-8 bootstrap
- [Shared/crc.py](Shared/crc.py) - Unified CRC32 implementation

**Configuration:**
- `config/config.json` - Base configuration (committed)
- `config.local.json` - Local overrides (gitignored)
- Environment variables - Highest precedence

## Non-Negotiable Rules

### 1. Configuration Access
```python
# ✅ ALWAYS use unified config manager
from Shared.config.unified_config import load_unified_config
config = load_unified_config()
port = config.server.port

# ❌ NEVER read JSON files directly
with open('config.json') as f:  # WRONG!
    config = json.load(f)
```

### 2. Async/Sync in Flet (Most Common Bug)
```python
# ❌ WRONG - Freezes UI permanently
async def load_data(self):
    clients = self.server_bridge.get_clients()  # BLOCKS EVENT LOOP!

# ✅ CORRECT - Use executor
from FletV2.utils.async_helpers import run_sync_in_executor
async def load_data(self):
    clients = await run_sync_in_executor(self.server_bridge.get_clients)
```

**Rule**: ALL sync `server_bridge.*()` calls in async functions MUST use `run_in_executor`

### 3. Time Measurement
```python
# ❌ WRONG - System clock can change
start = time.time()
duration = time.time() - start

# ✅ CORRECT - Monotonic for durations
start = time.monotonic()
duration = time.monotonic() - start
```

**Rule**: Use `time.monotonic()` for ALL durations, timeouts, and performance measurements

### 4. Resource Cleanup
```python
# ✅ ALWAYS use context managers
with db_manager.get_connection() as conn:
    cursor.execute("SELECT * FROM clients")

# ✅ ALWAYS use finally for cleanup
temp_file = None
try:
    temp_file = create_temp_file()
    process(temp_file)
finally:
    if temp_file:
        temp_file.unlink()
```

### 5. Validation Before Use
```python
# ❌ WRONG - Use before validation
client_id = data[:16]
self.process_client(client_id)
if client_id == b'\x00' * 16:  # Too late!
    return

# ✅ CORRECT - Validate first
client_id = data[:16]
if client_id == b'\x00' * 16:
    return
self.process_client(client_id)
```

### 6. Error Handling (No Silent Failures)
```python
# ❌ WRONG - Swallows errors
try:
    critical_operation()
except Exception:
    pass  # WHAT WENT WRONG?!

# ✅ CORRECT - Log and handle
try:
    critical_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    cleanup_partial_state()
    raise
```

## Critical Anti-Patterns (From Fixed Bugs)

### ❌ Race Conditions
```python
# ❌ WRONG - Check-then-act without lock
if client_id not in self.clients:
    self.clients[client_id] = Client(...)

# ✅ CORRECT - Atomic operation
with self.lock:
    if client_id not in self.clients:
        self.clients[client_id] = Client(...)
```

### ❌ Resource Leaks
Common leaks fixed in this codebase:
1. Database connections not returned to pool
2. File handles not closed in exception paths
3. Task references not removed from tracking dicts
4. Temporary files not deleted on error

**Solution**: Context managers + finally blocks everywhere

### ❌ God Classes
- Keep files under 500 lines (1000 max for views)
- Keep functions under 100 lines
- One responsibility per module
- Extract utilities to separate files

## Common Patterns in This Codebase

### Configuration Pattern
```python
from Shared.config.unified_config import load_unified_config

config = load_unified_config()
server_host = config.server.host
api_port = config.api_server.port
```

**Precedence**: Environment variables → config.local.json → config/config.json → .env files

### Validation Pattern
```python
from FletV2.utils.validators import validate_port

is_valid, error_msg = validate_port(port_input)
if not is_valid:
    logger.warning(f"Validation failed: {error_msg}")
    return {"success": False, "error": error_msg}
```

All validators return: `tuple[bool, str]` (is_valid, error_message)

### Database Pattern
```python
# Standard query pattern
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    results = cursor.fetchall()
# Connection auto-returned to pool

# Parallel queries for performance
async def load_data(self):
    loop = asyncio.get_running_loop()
    clients, files = await asyncio.gather(
        loop.run_in_executor(None, bridge.get_clients),
        loop.run_in_executor(None, bridge.get_files)
    )
```

### Error Handling Pattern
```python
# Low-level: Raise specific exceptions
def read_packet(self, socket):
    try:
        data = socket.recv(self.buffer_size)
        if not data:
            raise ConnectionError("Client disconnected")
        return data
    except socket.timeout:
        logger.warning("Socket read timeout")
        raise
    except OSError as e:
        logger.error(f"Socket error: {e}")
        raise ConnectionError(f"Failed to read: {e}") from e

# Mid-level: Handle expected, propagate unexpected
def process_request(self, client):
    try:
        packet = self.read_packet(client.socket)
        return self.parse_packet(packet)
    except ConnectionError:
        logger.info(f"Client {client.id} disconnected")
        self.cleanup_client(client)
        return None
    except Exception:
        logger.error(f"Unexpected error: {client.id}", exc_info=True)
        raise

# Top-level: Final safety net
def main():
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        server.shutdown()
    except Exception:
        logger.critical("Server crashed", exc_info=True)
        sys.exit(1)
```

### UI Update Pattern (Flet)
```python
# ✅ CORRECT - Targeted update
async def update_status(self):
    status = await run_sync_in_executor(bridge.get_status)
    self.status_text.value = status
    await asyncio.sleep(0)  # Yield to event loop
    self.status_text.update()  # Update only this control

# ❌ WRONG - Global update
async def update_status(self):
    status = await run_sync_in_executor(bridge.get_status)
    self.status_text.value = status
    self.page.update()  # Redraws ENTIRE page!
```

### View Lifecycle Pattern (Flet)
All FletV2 views must return a tuple with lifecycle functions:
```python
def create_my_view(server_bridge, page, state_manager=None):
    """Standard view creation pattern."""
    subscriptions = []

    # Dispose - cleanup resources
    def dispose_fn():
        for sub in subscriptions:
            state_manager.unsubscribe(sub)
        if hasattr(page, 'overlay'):
            page.overlay.clear()

    # Setup - called AFTER view attached to page
    def setup_fn():
        page.run_task(load_data)
        if state_manager:
            sub = state_manager.subscribe('event', on_event)
            subscriptions.append(sub)

    content = ft.Column(controls=[...])
    return content, dispose_fn, setup_fn
```

**Rule**: `setup_fn()` must execute AFTER view is attached to page to prevent "Control must be added to the page first" errors.

### Memory-Efficient Transfer Pattern
```python
from Shared.filesystem.memory_efficient_file_transfer import get_transfer_manager

# Create transfer with bounds checking
transfer_mgr = get_transfer_manager()
success = transfer_mgr.create_transfer(client_id, filename, total_packets, size)

# Add packets with automatic cleanup
success = transfer_mgr.add_packet(client_id, filename, packet_num, chunk_data)

# Monitor health
stats = transfer_mgr.get_statistics()
logger.info(f"Active transfers: {stats['active_transfers']}, Memory: {stats['current_memory_mb']}MB")
```

## Flet 0.28.3 Limitations

When working with FletV2, be aware of these API differences:
- No `SelectableText` - use `ft.Text(selectable=True)`
- No `ft.Colors.SURFACE_VARIANT` - use `ft.Colors.SURFACE` or `ft.Colors.GREY_100`
- No `Dropdown(height=...)` - parameter not supported
- No `ft.Positioned` - use `expand=True` on filling overlay layers within Stack
- Icons: use `SAVE_OUTLINED` not `SAVE_AS_OUTLINE`, `DATASET` not `DATABASE`

## UTF-8 Bootstrap Requirement

**First import** in entry files must be `Shared.utils.utf8_solution` to configure Windows console encoding:
```python
# Must be FIRST import
import Shared.utils.utf8_solution  # noqa: F401
```

Missing this causes `UnicodeEncodeError` when printing logs and GUI display corruption with non-ASCII characters. Required in: `FletV2/main.py`, `python_server/server/server.py`, `api_server/cyberbackup_api_server.py`

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PYTHONNOUSERSITE=1` | Prevent user site-packages conflicts | - |
| `CYBERBACKUP_DISABLE_INTEGRATED_GUI=1` | Use FletV2 instead of embedded server GUI | - |
| `FLET_V2_DEBUG=1` | Verbose GUI logging | - |
| `FLET_DASHBOARD_DEBUG=1` | Dashboard-specific logging (performance hit) | - |
| `REAL_SERVER_URL` | API base URL for real server mode | Mock mode |
| `BACKUP_SERVER_TOKEN` | Bearer token for API auth | - |

## Development Workflow

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure (edit config.local.json or set env vars)
# Launch GUI + Server
python FletV2/scripts/start_with_server.py

# One-click build and run (builds C++ client, starts all services)
python scripts/one_click_build_and_run.py

# Development with hot reload
flet run -r FletV2/main.py
```

### Code Quality
```bash
# Lint and format
ruff check FletV2 Shared python_server api_server
ruff format FletV2 Shared python_server api_server

# Type checking
pyright

# Run tests
pytest tests/

# Validate configuration
python -c "from Shared.config.unified_config import load_unified_config; \
           config = load_unified_config(); \
           print('Config loaded successfully')"
```

### Pre-Commit Checklist
- [ ] No sync calls in async functions without `run_in_executor`
- [ ] Database connections use context managers
- [ ] All external calls wrapped in try-except with logging
- [ ] Validation before processing untrusted input
- [ ] Resources cleaned up in finally blocks
- [ ] Use `time.monotonic()` for durations
- [ ] Use unified config manager for all config access
- [ ] No `page.update()` where `control.update()` works
- [ ] All functions have docstrings
- [ ] No debug print statements (use logger)

## Logging Standards

- **DEBUG**: Protocol details, packet parsing, reassembly
- **INFO**: Client connect/disconnect, file transfers, startup/shutdown
- **WARNING**: Recoverable errors, validation failures, retries
- **ERROR**: Failed operations, database errors, crypto failures
- **CRITICAL**: System failures, startup failures, security violations

```python
# Use structured logging
logger.info(f"Client {client_id.hex()} connected from {address}")
logger.warning(f"Validation failed for {filename}: {error}")
logger.error(f"Database operation failed: {e}", exc_info=True)
```

## Protocol Essentials

**Binary Frame** (little-endian):
```
[16 bytes] Client UUID
[1 byte]   Protocol Version (3)
[2 bytes]  Opcode
[4 bytes]  Payload Length
[N bytes]  Payload Data
[4 bytes]  CRC32 (entire frame)
```

**Critical Rules**:
1. All multi-byte integers are little-endian
2. UUID is exactly 16 bytes (binary, not string)
3. CRC32 covers entire frame including header
4. Max payload: 16MB + 1KB overhead
5. Version checked before processing (min: 2, max: 4, compatible: [3])

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| UI freeze | Check for sync calls in async without `run_in_executor` |
| Memory leak | Check transfer manager stats, ensure cleanup in finally blocks |
| Database lock | Use connection pooling context manager pattern |
| Config not loading | Check precedence: env vars > config.local.json > config.json |
| C++ client can't connect | Verify `server_instance.start()` called and port 1256 open |
| Race condition | Add locking around check-then-act patterns |
| Invalid time calculations | Use `time.monotonic()` not `time.time()` |

## Common Commands

```bash
# Database
python scripts/migrate_database.py
python scripts/validate_database.py

# C++ Client Build
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build --config Release

# Run single test
pytest tests/test_protocol.py -v
pytest tests/test_protocol.py::test_specific_function -v

# Find unused code
ruff check --select F401,F841 .

# Kill stale Python processes (port conflicts)
taskkill /f /im python.exe
```

## C++ Client Subprocess Pattern

When spawning C++ client from Python, **always use batch mode**:
```python
# ✅ CORRECT - Non-interactive mode
process = subprocess.Popen(
    ["EncryptedBackupClient.exe", "--batch"],
    cwd=client_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# ❌ WRONG - Will hang waiting for user input
process = subprocess.Popen(["EncryptedBackupClient.exe"], ...)
```

## Architecture Decision Records

### Why Unified Config Manager?
**Problem**: 4 config sources (config.json, config.local.json, .env, FletV2/.env) with conflicts
**Solution**: Single manager with clear precedence
**Impact**: Fixed configuration-related runtime issues

### Why Memory-Efficient Transfer Manager?
**Problem**: Unbounded memory growth, abandoned transfer leaks
**Solution**: LRU eviction, weak references, automatic cleanup
**Impact**: Prevents memory leaks documented in issue analysis

### Why `time.monotonic()`?
**Problem**: System clock changes caused negative durations
**Solution**: Monotonic clock immune to clock adjustments
**Impact**: Fixed timing bugs in network_server.py and database.py

### Why RLock Not Lock?
**Problem**: Deadlocks when methods call other methods holding locks
**Solution**: Reentrant locks allow same thread to acquire multiple times
**Impact**: Safe recursive locking in TransferManager

## Integration Points

**FletV2 → Server**: Direct method calls via ServerBridge (no HTTP)
**Web GUI → Server**: HTTP REST API via Flask (migrating to C++)
**C++ Client → Server**: Binary protocol on port 1256
**All Components → Database**: SQLite with connection pooling

**Security**:
- RSA-1024 (PKCS1_OAEP) for key exchange
- AES-256-CBC for file encryption
- CRC32 for integrity verification
- Input validation before processing

## External Dependencies

**Python**: PyCryptodome (crypto), Flet (GUI), Flask (API), psutil (monitoring)
**C++**: Drogon (new API server), SQLiteCpp (database), nlohmann/json (parsing)
**Build**: CMake, vcpkg (C++ package management)

## Performance Targets

- Database queries: Parallelize with asyncio.gather (3x improvement achieved)
- UI updates: Use targeted `control.update()` not `page.update()`
- File transfers: Stream in 64KB chunks, bounded memory
- Transfer manager: Default 10 concurrent, 100MB per transfer, configurable

---

**Version**: CyberBackup 3.0
**Last Updated**: 2025-11-20
**Status**: Production-ready Python stack, C++ API server in development

**Key Documents**:
- [docs/reports/CODE_ISSUES_AND_FIXES.md](docs/reports/CODE_ISSUES_AND_FIXES.md) - 42 fixed issues
- [_archive/cpp_api_server_prototype/CPP_API_SERVER_MIGRATION_PLAN.md](_archive/cpp_api_server_prototype/CPP_API_SERVER_MIGRATION_PLAN.md) - Archived C++ API prototype
- [docs/reference/flet/](docs/reference/flet/) - Consolidated Flet 0.28.3 documentation (18 files)
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Detailed FletV2 patterns and ServerBridge API

## Recent Updates

- **Shared reorganized**: Subdirectories for config/, filesystem/, validation/, logging/, monitoring/
- **Unified config**: Use `Shared/config/unified_config.py` (replaces fragmented config sources)
- **Memory management**: Use `Shared/filesystem/memory_efficient_file_transfer.py` (prevents leaks)
- **Log rotation**: Implemented in `Shared/logging/logging_utils.py` (max 6 files, 700MB)
- **Flet docs**: Consolidated at `docs/reference/flet/` (18 files for Flet 0.28.3)
- **Web GUI**: Production-ready at `api_server/web_ui/NewGUIforClient.html`
- **Archive**: Legacy code moved to `_archive/` directory
- **Scripts organized**: `scripts/` has subdirectories for debugging/, diagnostics/, maintenance/, etc.
