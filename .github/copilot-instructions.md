# Client-Server Encrypted Backup Framework – AI Agent Guide

## System Architecture

**Dual-GUI encrypted backup system** with three independent paths to the same BackupServer:

```
FletV2 Desktop GUI (admin) → ServerBridge → BackupServer (port 1256) ← C++ Client
                                                ↑
Web GUI (end-users) → Flask API Server (port 9090) → RealBackupExecutor → C++ Client
                                                ↓
                              SQLite defensive.db (shared)
```

- **FletV2 Desktop**: Admin interface with direct Python method calls via ServerBridge (no HTTP)
- **Web GUI**: End-user backup interface via Flask API spawning C++ client subprocesses
- **C++ Client**: Binary protocol implementation for encrypted file transfers
- **BackupServer**: Python server with TCP listener on port 1256, handles protocol messages
- **Database**: SQLite `defensive.db` with file-level locking for concurrent access

## Critical Integration Points

### The Network Listener Problem (January 2025 Fix)
**MUST call `server_instance.start()`** in `FletV2/start_with_server.py` (line 78) or C++ clients cannot connect. The BackupServer creates a NetworkServer daemon thread that listens on port 1256. Without this call, the system appears to run but all file transfers fail silently.

### Protocol Version Lock
Protocol version **3** is hardcoded in both client and server. Changes require:
1. Update `python_server/server/protocol.py` constants (REQ_*/RESP_* codes)
2. Update `Client/include/ProtocolEnums.h` matching definitions
3. Rebuild C++ client: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake" && cmake --build build --config Release`
4. Update tests in `tests/test_protocol.py`

### ServerBridge Pattern (FletV2 Only)
- Direct delegation to BackupServer Python methods (no API layer)
- Normalizes responses to `{"success": bool, "data": ..., "error": str}`
- Mock mode (`utils/mock_database_simulator.py`) returns empty structures, not fabricated data
- Auto-detects real server via `/health` check when `REAL_SERVER_URL` set

## Essential Workflows

### Launch Commands
```bash
# Recommended: Full system (builds C++ client, starts all services)
python scripts/one_click_build_and_run.py

# FletV2 GUI only (for UI dev)
python FletV2/start_with_server.py
# OR use VS Code task: "Run FletV2 App(Desktop mode-NO browser) with Server (PS1)"

# Flask API bridge only (for web GUI dev)
python api_server/cyberbackup_api_server.py
```

### Build System
C++ client requires vcpkg toolchain. Missing this causes cryptic linker errors:
```bash
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"
cmake --build build --config Release
```

### Testing Strategy
```bash
# Protocol/database tests (fast)
pytest tests/test_protocol.py tests/test_comprehensive_database.py tests/test_async_patterns.py

# Code quality
ruff check FletV2 Shared python_server api_server  # Linting
pyright                                              # Type checking
python -m compileall FletV2/main.py                 # Syntax validation

# GUI smoke test: manual after UI changes (navigate Dashboard → Clients → Files → Database → Analytics)
```
## FletV2 Development Patterns

### Async/Sync Integration Rule
**99% of GUI freezes** come from blocking calls in async functions. Dashboard deadlock (Oct 2024) was caused by `server_bridge.is_connected()` in async context.

```python
# ❌ WRONG - Freezes UI
async def load_data():
    result = server_bridge.get_clients()  # BLOCKS event loop

# ✅ CORRECT - Use executor
from FletV2.utils.async_helpers import run_sync_in_executor
async def load_data():
    result = await run_sync_in_executor(server_bridge.get_clients)
```

### View Architecture (5-Section Pattern)
All views follow: Data Fetching → Business Logic → UI Components → Event Handlers → Main View
- See `FletV2/architecture_guide.md` for full pattern
- Use `ft.Ref[ft.ControlType]()` for controls referenced before `build()`.
- Every `setup_fn` needs matching `dispose_fn` (cancel tasks, remove overlays, unsubscribe)

### UI Update Hierarchy
1. **Prefer** `control.update()` (fastest, targeted)
2. **Use** `page.update()` only for themes/dialogs/overlays
3. **Never** loop `page.update()` - causes 16ms+ frame times

### Flet 0.28.3 Limitations
- No `SelectableText` - use `ft.Text(selectable=True)`
- No `ft.Colors.SURFACE_VARIANT` - use `ft.Colors.SURFACE` or `ft.Colors.GREY_100`
- No `Dropdown(height=...)` - parameter not supported
- Icons: use `SAVE_OUTLINED` not `SAVE_AS_OUTLINE`, `DATASET` not `DATABASE`
## Data & Protocol Contracts

### Binary Protocol Structure
- **Frame**: 16-byte UUID | 1-byte version | 2-byte opcode (LE) | 4-byte payload size (LE) | payload | CRC32
- **Encryption**: RSA-1024 (OAEP-SHA256) for key exchange, AES-256-CBC for files (zero IV per spec)
- **Checksum**: Linux `cksum` algorithm (NOT standard CRC-32)

### Transfer Configuration (`transfer.info`)
Exactly 3 lines (no empty lines):
```
127.0.0.1:1256
username
C:\absolute\path\to\file.ext
```

### Database Schema
- `clients`: id, client_id (UUID), name, created_at, last_seen, total_files, total_bytes
- `files`: id, client_id FK, path_hash, original_name, size_bytes, checksum_crc32, stored_at
- `transfers`: id, file_id FK, status, started_at, completed_at, duration_ms, failure_reason
- Connection via `DatabaseManager.get_connection()` with retry decorator for `sqlite3.OperationalError`
- Files stored in `python_server/server/received_files/` with hashed names
## Configuration & Environment

### Required Environment Variables (set by launchers)
```bash
PYTHONNOUSERSITE=1                      # Prevent user site-packages conflicts
CYBERBACKUP_DISABLE_INTEGRATED_GUI=1   # Use FletV2 instead of embedded server GUI
FLET_V2_DEBUG=1                         # Verbose GUI logging
FLET_DASHBOARD_DEBUG=1                  # Dashboard-specific logging (use sparingly - performance hit)
```

### UTF-8 Bootstrap Requirement
**First import** in entry files must be `Shared.utils.utf8_solution` to configure Windows console encoding. Missing this causes:
- UnicodeEncodeError when printing logs
- GUI display corruption with non-ASCII characters
- Applies to: `FletV2/main.py`, `python_server/server/server.py`, `api_server/cyberbackup_api_server.py`
## Common Pitfalls

1. **Port 1256 conflicts**: Stale Python processes hold the socket. Kill before restart: `taskkill /f /im python.exe`
2. **Missing network listener**: Verify "Network server started" in logs. See "Network Listener Problem" above.
3. **Protocol version mismatch**: Update both `protocol.py` and `ProtocolEnums.h`, rebuild C++ client.
4. **Async freeze**: Never call sync ServerBridge methods from async code without executor wrapper.
5. **Mock mode confusion**: Check `server_bridge.is_real()` before destructive operations.
6. **Theme token changes**: Preserve neumorphic/glassmorphism tokens in `FletV2/theme.py` - QA depends on them.

## Code Quality Standards

### Structured Logging
Use `Shared/logging_config.py` for all logging. Avoid `print()` except for startup messages:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Client connected", extra={"client_id": uuid_str, "ip": addr})
```

### Type Safety
- Run `pyright` before committing (config in `pyrightconfig.json`)
- `python_server/` excluded from type checking due to dynamic protocol handling

### File Organization
Legacy TkInter GUI (40k+ lines) archived to `_legacy/server_gui/` (Jan 2025). Do not modify.

## ServerBridge API Reference

### Core Methods
All methods return `{"success": bool, "data": Any, "error": str}` structure.

**Client Operations:**
```python
get_all_clients_from_db() -> dict  # Returns list of clients with UUID conversion
get_clients_async() -> dict        # Async variant
get_client_by_id(client_id: str) -> dict
add_client(client_data: dict) -> dict
delete_client(client_id: str) -> dict
update_client(client_id: str, data: dict) -> dict
disconnect_client(client_id: str) -> dict
```

**File Operations:**
```python
get_files() -> dict                 # All files
get_client_files(client_id: str) -> dict
delete_file(file_id: str) -> dict
download_file(file_id: str) -> bytes | Path  # Returns temp path in mock mode
verify_file(file_id: str) -> dict
```

**Database Operations:**
```python
get_database_info() -> dict         # Schema, table stats, size
get_table_data(table_name: str) -> dict
update_row(table: str, id: str, data: dict) -> dict
delete_row(table: str, id: str) -> dict
add_row(table: str, data: dict) -> dict
```

**Server Status:**
```python
get_server_status_async() -> dict   # Health, uptime, active connections
get_system_status() -> dict         # CPU, memory, disk metrics
get_analytics_data() -> dict        # Aggregated statistics
start_server() -> dict              # Control operations
stop_server() -> dict
test_connection() -> dict
```

**Logs:**
```python
get_logs(offset: int = 0, limit: int = 100) -> dict
get_log_stats() -> dict
clear_logs() -> dict
export_logs(format: str) -> dict
```

### Data Conversion Utilities
Located in `FletV2/utils/server_bridge.py`:

```python
# UUID conversions (BackupServer uses BLOB format)
blob_to_uuid_string(blob: bytes) -> str
uuid_string_to_blob(uuid_str: str) -> bytes

# Format normalization for FletV2
convert_backupserver_client_to_fletv2(client: dict) -> dict
convert_backupserver_file_to_fletv2(file: dict) -> dict
```

**Example - Client Data Flow:**
```python
# BackupServer format (raw SQLite)
{"id": b'\x12\x34...', "name": "Client1", "files_count": 5}

# After conversion (FletV2 format)
{"id": "12345678-1234-...", "name": "Client1", "files_count": 5,
 "status": "Active", "ip_address": "192.168.1.1"}
```

## Database Operation Patterns

### Connection Management
Always use context managers:

```python
from python_server.server.database import DatabaseManager

db_manager = DatabaseManager()

# ✅ CORRECT - Auto-closes connection
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    results = cursor.fetchall()
    conn.commit()  # For writes

# ❌ WRONG - Leaks connections
conn = db_manager.get_connection()
cursor = conn.cursor()
# ... forgot to close
```

### Retry Pattern
All database operations use retry decorator for `sqlite3.OperationalError`:

```python
from functools import wraps
import time

@retry(max_attempts=3, backoff_base=0.5, exceptions=(sqlite3.OperationalError,))
def my_database_operation():
    with db_manager.get_connection() as conn:
        # Operation here
        pass
```

**Why:** SQLite locks database during writes. Retry handles concurrent access automatically.

### Transaction Patterns
```python
# Single statement - auto-commit via context manager
with db_manager.get_connection() as conn:
    conn.execute("INSERT INTO clients VALUES (?, ?)", (id, name))

# Multiple statements - manual transaction
with db_manager.get_connection() as conn:
    conn.execute("INSERT INTO clients ...")
    conn.execute("INSERT INTO files ...")
    conn.commit()  # Atomic - both or neither
```

### Connection Pooling Metrics
Database maintains connection pool (default: 5 connections):
- Monitor via `DatabaseManager.get_pool_metrics()`
- Connections auto-cleaned after 1 hour idle
- Emergency connections created if pool exhausted

## C++ Client Integration Patterns

### Subprocess Execution (API Server Path)
Flask API spawns C++ client as subprocess:

```python
from api_server.real_backup_executor import RealBackupExecutor

executor = RealBackupExecutor(
    client_exe="build/Release/EncryptedBackupClient.exe",
    server_ip="127.0.0.1",
    server_port=1256
)

# Execute backup
result = executor.execute_backup(
    username="user1",
    file_path="C:\\path\\to\\file.txt"
)

# Check result
if result['success']:
    print(f"File transferred: {result['file_path']}")
```

### Transfer Configuration Generation
`transfer.info` MUST be exactly 3 lines:

```python
def generate_transfer_info(server_ip: str, server_port: int,
                          username: str, file_path: str):
    with open("transfer.info", "w", encoding="utf-8") as f:
        f.write(f"{server_ip}:{server_port}\n")  # Line 1
        f.write(f"{username}\n")                 # Line 2
        f.write(f"{file_path}\n")                # Line 3
    # NO empty lines, NO extra content
```

### Batch Mode Requirement
C++ client MUST be launched with `--batch` flag in subprocess:

```python
# ✅ CORRECT
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

## View Lifecycle Management

### Standard View Pattern
```python
def create_my_view(server_bridge, page, state_manager=None):
    """
    Standard view creation pattern.

    Returns:
        tuple: (content_control, dispose_fn, setup_fn)
    """
    # 1. Local state
    data_ref = ft.Ref[ft.Column]()
    subscriptions = []

    # 2. Data fetching
    async def load_data():
        result = await run_sync_in_executor(server_bridge.get_data)
        if result['success']:
            update_ui(result['data'])

    # 3. Event handlers
    def on_refresh(e):
        page.run_task(load_data)

    # 4. Dispose function - REQUIRED
    def dispose_fn():
        # Cancel tasks
        for sub in subscriptions:
            state_manager.unsubscribe(sub)
        # Remove overlays
        if hasattr(page, 'overlay'):
            page.overlay.clear()

    # 5. Setup function - Called AFTER view attached
    def setup_fn():
        page.run_task(load_data)
        if state_manager:
            sub = state_manager.subscribe('event', on_event)
            subscriptions.append(sub)

    # 6. Build UI
    content = ft.Column(
        ref=data_ref,
        controls=[...]
    )

    return content, dispose_fn, setup_fn
```

### FilePicker Lifecycle
One FilePicker per view instance:

```python
# ✅ CORRECT
class MyView:
    def __init__(self):
        self.file_picker = ft.FilePicker(on_result=self.on_files_selected)

    def setup(self, page):
        # Add to overlay once
        if self.file_picker not in page.overlay:
            page.overlay.append(self.file_picker)
        page.update()

    def dispose(self):
        # Remove from overlay
        if self.file_picker in page.overlay:
            page.overlay.remove(self.file_picker)
```

## Error Handling Conventions

### Structured Error Responses
All methods follow consistent error pattern:

```python
# Success case
{"success": True, "data": {...}, "error": None}

# Error case
{"success": False, "data": None, "error": "Descriptive error message"}

# Partial success (e.g., some operations failed)
{"success": True, "data": {...}, "error": "Warning: 2 operations failed"}
```

### Exception Hierarchy
```python
ServerError              # Base class
├── ProtocolError       # Protocol violations
├── ClientError         # Client state issues
├── FileError           # File operation failures
└── DatabaseError       # Database operation failures
```

### Error Handling in Views
```python
async def handle_operation():
    try:
        result = await run_sync_in_executor(server_bridge.operation)

        if not result['success']:
            # Show error to user
            show_snackbar(page, result['error'], error=True)
            return

        # Handle success
        update_ui(result['data'])
        show_snackbar(page, "Operation completed")

    except Exception as e:
        logger.exception("Unexpected error")
        show_snackbar(page, f"Error: {str(e)}", error=True)
```

## Performance Considerations

### UI Update Batching
```python
# ❌ WRONG - Multiple page.update() calls
for item in items:
    control.controls.append(create_item(item))
    page.update()  # SLOW - triggers rerender each time

# ✅ CORRECT - Batch updates
controls_to_add = [create_item(item) for item in items]
control.controls.extend(controls_to_add)
control.update()  # Single update
```

### Connection Pool Sizing
- Default: 5 connections (adequate for most workloads)
- Increase for high concurrency: `DatabaseManager(pool_size=10)`
- Monitor pool exhaustion via metrics

### Async Task Management
```python
# ❌ WRONG - Blocking async function
async def load_data():
    result = server_bridge.get_data()  # Blocks event loop

# ✅ CORRECT - Non-blocking
async def load_data():
    result = await run_sync_in_executor(server_bridge.get_data)
```

## Real-World Task Examples

### Task: Add New Client via GUI
```python
async def add_client_handler(e):
    client_data = {
        "name": name_field.value,
        "ip_address": ip_field.value,
        "platform": platform_dropdown.value
    }

    result = await run_sync_in_executor(
        server_bridge.add_client, client_data
    )

    if result['success']:
        # Refresh client list
        await refresh_clients()
        show_snackbar(page, f"Client {client_data['name']} added")
    else:
        show_snackbar(page, result['error'], error=True)
```

### Task: Download File from Backup
```python
async def download_file_handler(file_id: str):
    # Get file info first
    file_info = await run_sync_in_executor(
        server_bridge.get_file_by_id, file_id
    )

    if not file_info['success']:
        show_snackbar(page, "File not found", error=True)
        return

    # Download to temp location
    result = await run_sync_in_executor(
        server_bridge.download_file, file_id
    )

    if result['success']:
        # result['data'] contains file path
        show_snackbar(page, f"Downloaded to {result['data']}")
```

### Task: Query Database Directly
```python
from python_server.server.database import DatabaseManager

db = DatabaseManager()

with db.get_connection() as conn:
    cursor = conn.cursor()

    # Get clients with > 100 files
    cursor.execute("""
        SELECT c.*, COUNT(f.id) as file_count
        FROM clients c
        LEFT JOIN files f ON f.client_id = c.id
        GROUP BY c.id
        HAVING file_count > 100
    """)

    results = cursor.fetchall()
```

### Task: Execute C++ Backup from Python
```python
from api_server.real_backup_executor import RealBackupExecutor

executor = RealBackupExecutor(
    client_exe="build/Release/EncryptedBackupClient.exe"
)

result = executor.execute_backup(
    username="admin",
    file_path=r"C:\sensitive_data.xlsx"
)

if result['success']:
    print(f"Backup completed in {result['duration_ms']}ms")
    print(f"File stored as: {result['stored_filename']}")
```