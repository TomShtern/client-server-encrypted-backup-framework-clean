# Client-Server Encrypted Backup Framework - Claude Instructions

## Project Context

CyberBackup 3.0: Encrypted file backup system with Python server, FletV2 desktop GUI, and web API bridge. C++ client connects via binary protocol. SQLite database for metadata, encrypted files stored locally.

**Core Architecture:**
- **Python Backup Server** (port 1256): Handles C++ client connections, file transfers, encryption
- **FletV2 Desktop GUI**: Admin interface with Material Design 3, direct server method calls
- **API Server** (port 9090): Flask bridge for web GUI (C++ replacement in progress at `cpp_api_server/`)
- **C++ Client**: Binary protocol, AES-256-CBC encryption, RSA-1024 key exchange
- **SQLite Database**: `defensive.db` with connection pooling

## Recent Critical Changes (2025-11-07)

1. **Unified Configuration**: Use `Shared.unified_config_manager.py` (replaces fragmented config sources)
2. **Memory Management**: Use `Shared.utils.memory_efficient_file_transfer.py` (prevents leaks)
3. **C++ API Server**: In development at `cpp_api_server/` (will replace Flask, see `docs/CPP_API_SERVER_MIGRATION_PLAN.md`)
4. **Fixed Issues**: 42 bugs documented in `CODE_ISSUES_AND_FIXES.md` and `FUNCTIONAL_ISSUES_REPORT.md`

## Critical File Locations

**Core Server:**
- [python_server/server/server.py](python_server/server/server.py) - Main backup server
- [python_server/server/file_transfer.py](python_server/server/file_transfer.py) - Transfer management
- [python_server/server/database.py](python_server/server/database.py) - Database with connection pooling

**GUI:**
- [FletV2/main.py](FletV2/main.py) - Desktop GUI entry point
- [FletV2/server_adapter.py](FletV2/server_adapter.py) - ServerBridge for direct server calls
- [api_server/cyberbackup_api_server.py](api_server/cyberbackup_api_server.py) - Current web API (being replaced)

**Shared Utilities:**
- [Shared/unified_config_manager.py](Shared/unified_config_manager.py) - Unified configuration
- [Shared/utils/memory_efficient_file_transfer.py](Shared/utils/memory_efficient_file_transfer.py) - Memory-bounded transfers
- [Shared/utils/validation_utils.py](Shared/utils/validation_utils.py) - Centralized validators

**Configuration:**
- `config.json` - Base configuration (committed)
- `config.local.json` - Local overrides (gitignored)
- Environment variables - Highest precedence

## Non-Negotiable Rules

### 1. Configuration Access
```python
# ✅ ALWAYS use unified config manager
from Shared.unified_config_manager import load_unified_config
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
from Shared.unified_config_manager import load_unified_config

config = load_unified_config()
server_host = config.server.host
api_port = config.api_server.port
```

**Precedence**: Environment variables → config.local.json → config.json → .env files

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

### Memory-Efficient Transfer Pattern
```python
from Shared.utils.memory_efficient_file_transfer import get_transfer_manager

# Create transfer with bounds checking
transfer_mgr = get_transfer_manager()
success = transfer_mgr.create_transfer(client_id, filename, total_packets, size)

# Add packets with automatic cleanup
success = transfer_mgr.add_packet(client_id, filename, packet_num, chunk_data)

# Monitor health
stats = transfer_mgr.get_statistics()
logger.info(f"Active transfers: {stats['active_transfers']}, Memory: {stats['current_memory_mb']}MB")
```

## Development Workflow

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure (edit config.local.json or set env vars)
# Launch GUI + Server
pwsh -File FletV2/start_with_server.ps1

# Or manual start
python FletV2/start_with_server.py
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
python -c "from Shared.unified_config_manager import get_unified_config_manager; \
           errors = get_unified_config_manager().validate_configuration(); \
           print('Valid' if not errors else errors)"
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

# Build C++ (API server)
cmake -B cpp_api_server/build -S cpp_api_server
cmake --build cpp_api_server/build --config Release

# Build C++ (client)
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build --config Release

# Find unused code
ruff check --select F401,F841 .
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
**Last Updated**: 2025-11-07
**Status**: Production-ready Python stack, C++ API server in development

**Key Documents**:
- [CODE_ISSUES_AND_FIXES.md](CODE_ISSUES_AND_FIXES.md) - 42 fixed issues
- [FUNCTIONAL_ISSUES_REPORT.md](FUNCTIONAL_ISSUES_REPORT.md) - Issue analysis
- [docs/CPP_API_SERVER_MIGRATION_PLAN.md](docs/CPP_API_SERVER_MIGRATION_PLAN.md) - Migration details
