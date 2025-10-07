
# Client-Server Encrypted Backup Framework - Claude Instructions

After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.

When given a very long task, so it may be beneficial to plan out your work clearly. It's encouraged to spend your entire output context working on the task - just make sure you don't run out of context with significant uncommitted work. Continue working systematically until you have completed this task.

After completing a task that involves tool use, provide a quick summary of the work you've done.

IMPORTANT: For extremely important AI guidance, rules, and data please consult the `#file:AI-Context` folder. Additional important documentation and design reference materials are in the `#file:important_docs` folder. Use `AI-Context` first for critical decisions.

## Project Overview

This is a comprehensive encrypted file backup system that implements a robust client-server architecture with strong security measures. The project features:

- **Security Layer**: RSA-1024 for key exchange and AES-256-CBC for file encryption
- **Backend**: Python server with SQLite database for storage and management
- **Frontend**: Modern Flet-based GUI with Material Design 3, Neumorphism, and Glassmorphism styling
- **Protocol**: Custom binary protocol with CRC32 verification for data integrity
- **Architecture**: Client-server model with cross-platform compatibility

## Project Structure & Components

### Core Architecture
- **python_server/**: Python-based server implementation with SQLite database
- **FletV2/**: Modern desktop GUI built with Flet framework
- **Shared/**: Common utilities, logging, and configuration modules
- **Client/**: C++ client application (binary protocol implementation)

### FletV2 GUI Architecture
- **main.py**: Application entry point with sophisticated state management
- **views/**: Modular view components (dashboard, clients, files, database, analytics, etc.)
- **theme.py**: Advanced tri-style design system (Material 3, Neumorphism, Glassmorphism)
- **utils/**: Server bridge, state management, and utility functions
- **config.py**: Configuration and constants for the GUI application

### Server Architecture
- **server.py**: Main backup server with client management and encryption
- **database.py**: SQLite integration with client/file tracking
- **protocol.py**: Custom binary protocol implementation
- **network_server.py**: Network communication layer

## Key Features & Capabilities

### Security Features
- RSA-1024 key exchange for secure session establishment
- AES-256-CBC encryption for file data protection
- CRC32 verification for data integrity
- Secure key management with automatic generation and storage

### GUI Features
- **Dashboard**: Real-time metrics with interactive cards and performance gauges
- **Client Management**: View and manage registered backup clients
- **File Management**: Browse, search, and manage backed up files
- **Database Management**: Direct database access and record management
- **Settings Management**: Comprehensive configuration with server integration
- **Advanced Styling**: Material Design 3 with neumorphic and glassmorphic effects
- **Responsive Design**: Adaptive layout for different screen sizes

### Server Features
- Multi-client support with concurrent connections
- Automated session timeout and cleanup
- Database integrity checks and maintenance
- Comprehensive logging with dual output (console + file)
- Performance monitoring and metrics collection

## FletV2 GUI Architecture Details

### 🚨 CRITICAL: Flet Async/Sync Integration (January 2025)

**MANDATORY READING**: See [FLET_INTEGRATION_GUIDE.md](FLET_INTEGRATION_GUIDE.md) and [FLET_QUICK_FIX_GUIDE.md](FLET_QUICK_FIX_GUIDE.md) for comprehensive async/sync integration patterns.

#### The Golden Rule: NEVER Await Synchronous Methods

**99% of Flet freezes come from one mistake**: `await`ing synchronous methods blocks the event loop **forever**.

```python
# ❌ WRONG - Causes permanent freeze (gray screen, no errors, no recovery)
async def load_data():
    result = await bridge.get_database_info()  # If sync, FREEZE!

# ✅ CORRECT - Use run_in_executor for ALL synchronous server/database calls
async def load_data():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_database_info)
```

#### Critical Integration Patterns

1. **ServerBridge Methods are SYNCHRONOUS** - Always wrap with `run_in_executor`:
   ```python
   loop = asyncio.get_running_loop()
   result = await loop.run_in_executor(None, bridge.method_name, arg1, arg2)
   ```

2. **NEVER use `time.sleep()` in async code** - Use `asyncio.sleep()`:
   ```python
   # ❌ WRONG: await asyncio.sleep(1) if you used time.sleep
   # ✅ CORRECT:
   await asyncio.sleep(1)  # Non-blocking
   ```

3. **ALWAYS call `page.update()` or `control.update()`** after state changes

4. **NEVER call `asyncio.run()` inside Flet** - event loop is already running

5. **Use diagnostic logging** to find freeze points:
   ```python
   async def debug_function():
       print("🔴 [DEBUG] Starting")
       await operation()
       print("🔴 [DEBUG] Completed")  # If this doesn't print, freeze is in operation()
   ```

**Quick Fix**: Search for `await bridge.` and wrap all calls with `run_in_executor` (see FLET_QUICK_FIX_GUIDE.md for step-by-step instructions).

### 🚨 CRITICAL: Server Integration Architecture (October 1, 2025)

**The BackupServer does NOT have an API.** All communication is via **direct Python method calls**:

1. **Server-Launched Mode** ([start_with_server.py](FletV2/start_with_server.py)):
   - BackupServer creates instance of itself
   - Passes `self` as Python object to FletV2App
   - GUI calls server methods directly: `server.get_clients()`, `server.add_file()`, etc.
   - **Zero network overhead** - in-memory Python calls only

2. **Standalone GUI Mode** ([start_gui_only.py](FletV2/start_gui_only.py)):
   - GUI launches without server instance (`FLET_GUI_ONLY_MODE=1`)
   - All views show empty states (no data)
   - Used for GUI development and testing only

3. **ServerBridge Pattern** ([server_bridge.py](FletV2/utils/server_bridge.py)):
   - **NOT an API client** - it's a thin delegation wrapper
   - Direct method delegation: `bridge.get_clients()` → `server.get_clients()`
   - Data format conversion (BackupServer ↔ FletV2 formats)
   - Structured error handling with `{'success': bool, 'data': Any, 'error': str}`
   - **NO HTTP, NO REST, NO API CALLS** - pure Python method delegation
   - **⚠️ CRITICAL**: All bridge methods are SYNCHRONOUS - wrap with `run_in_executor` when calling from async code

### ServerBridge Integration
The ServerBridge acts as the primary interface between the GUI and the backend server. Key components include:

- **Direct Method Delegation**: Calls real server methods directly (not API endpoints)
- **Data Conversion**: Converts between BackupServer and FletV2 data formats (BLOB UUIDs ↔ strings)
- **Error Handling**: Provides structured responses for server operations
- **Async Support**: Implements both synchronous and asynchronous operations via executors

### State Management System
The enhanced StateManager provides reactive state management with:

- **State Synchronization**: Keeps UI components synchronized with server data
- **Async Updates**: Supports server-mediated state updates
- **Loading States**: Tracks operation loading states
- **Progress Tracking**: Monitors operation progress
- **Error States**: Manages and displays error states
- **Event Broadcasting**: Sends events across different parts of the application
- **Retry Mechanism**: Handles operation retries with exponential backoff

### UI Components Framework
The GUI uses a streamlined component system with:

- **Framework-Harmonious Components**: Uses Flet's built-in components rather than complex custom implementations
- **Themed Components**: Consistent styling using the advanced theme system
- **Smart Data Display**: DataTables and data visualization components
- **Responsive Layouts**: Uses Flet's ResponsiveRow for adaptive layouts
- **Status Indicators**: Various status pill and indicator types for different states
- **Action Buttons**: Consistent styling for primary and secondary actions

### View Architecture
Each view follows a consistent pattern:

- **Create Function**: Returns the view container, dispose function, and setup function
- **Server Integration**: Uses server_bridge for data operations
- **State Management**: Integrates with StateManager for reactive updates
- **Resource Cleanup**: Includes proper disposal of resources and subscriptions

### Theme and Styling System
The advanced theme system implements a tri-style design:

- **Material Design 3**: Core design language with semantic colors
- **Neumorphism**: Soft shadows and depth effects (40-45% intensity)
- **Glassmorphism**: Translucent elements with blur effects (20-30% intensity)
- **Pre-computed Constants**: Performance-optimized shadow and styling constants
- **Animation Support**: GPU-accelerated animations for smooth interactions

## Detailed View Components

### Dashboard View
The main dashboard view features:

- **Metric Cards**: Interactive cards with real-time data and navigation support
- **Performance Gauges**: Circular progress indicators with status displays
- **Activity Stream**: Timeline-based activity display with status indicators
- **Status Monitoring**: Dual status indicators for GUI and server connection
- **Theme Controls**: Integrated theme switching with multiple options

### Clients View
The clients management view provides:

- **Data Table**: Display of client information with sorting and filtering
- **CRUD Operations**: Full Create, Read, Update, Delete functionality
- **Status Indicators**: Visual status representation for connection states
- **Search and Filter**: Client filtering by name, ID, and status
- **Context Menus**: Action menus for each client record

### Database View
The database management view includes:

- **Table Browser**: Dynamic table browsing with schema detection
- **Record Management**: Full CRUD operations on database records
- **Export Functionality**: JSON export of table data
- **Status Indicators**: Visual representation of database status
- **Search and Filter**: Record filtering and search capabilities

### Settings View
The settings management view provides:

- **Tabbed Interface**: Organized settings into logical groups (Server, Interface, Monitoring, Logging, Security, Backup)
- **Validation**: Client-side validation for settings values
- **Import/Export**: Settings import/export functionality
- **Reset Functionality**: Reset to default settings
- **Server Integration**: Save/load settings from the server

## Development Conventions

### Code Style
- Follow Python PEP 8 standards with Ruff linting
- Use type hints for all function signatures
- Maintain comprehensive docstrings for all modules and classes
- Implement structured logging with context information

### Architecture Patterns
- **ServerBridge Pattern**: Interface between GUI and backend server
- **State Management**: Reactive UI updates via dedicated state manager
- **Modular Design**: Separate view components with consistent API patterns
- **Async Integration**: Proper handling of synchronous and asynchronous operations
- **Framework Harmony**: Use Flet's built-in components rather than complex custom implementations

### Error Handling
- Implement comprehensive exception handling with graceful degradation
- Use structured logging for debugging and monitoring
- Provide user-friendly error messages in GUI
- Include automated crash reporting and diagnostics

## Building and Running

### Prerequisites
- Python 3.8+ with standard development tools
- Visual Studio Build Tools for C++ client compilation
- Git for version control
- SQLite for database storage

### Setup Commands
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up Flet virtual environment (if needed)
python -m venv flet_venv
flet_venv\Scripts\activate
pip install -r requirements.txt

# Build C++ client (Windows)
.\build.bat

# Run the server
python -m python_server.server.server

# Run the GUI
python -m FletV2.main
```

### Launcher Modes

**Server-Launched Mode (Integrated)** - `python FletV2/start_with_server.py`:
```python
# Creates BackupServer instance
server_instance = BackupServer()
# Passes server as Python object to GUI
app = FletV2App(page, real_server=server_instance)
# GUI calls server.get_clients(), server.add_file(), etc. directly
```

**Standalone GUI Mode** - `python FletV2/start_gui_only.py`:
```python
# Sets FLET_GUI_ONLY_MODE=1 environment variable
# Launches GUI without server instance
app = FletV2App(page, real_server=None)
# All views show empty states with "Server not connected" messages
```

### Environment Variables
- `FLET_GUI_ONLY_MODE`: Enable GUI-only mode without server connection (empty states)
- `CYBERBACKUP_DISABLE_INTEGRATED_GUI`: Disable embedded server GUI
- `DASHBOARD_REFRESH_INTERVAL`: Set dashboard refresh interval in seconds
- `FLET_V2_DEBUG`: Enable debug mode for additional logging

## Testing and Quality Assurance

### Test Strategy
- Integration tests for server-client communication
- Unit tests for encryption and protocol implementations
- GUI component tests for UI interactions
- End-to-end tests for backup workflow

### Quality Tools
- Ruff for linting and formatting
- Pyright for type checking
- MyPy for additional type verification
- Comprehensive logging for debugging

## Special Considerations for Claude

### Security Context
- Always prioritize secure handling of encryption keys and credentials
- Follow security best practices when modifying crypto implementations
- Ensure all file operations maintain data integrity
- Verify that any new features maintain the end-to-end encryption model

### GUI Development
- Maintain consistency with the tri-style design system (Material 3, Neumorphism, Glassmorphism)
- Use the provided theme utilities for styling components
- Implement proper state management for reactive UI updates
- Follow the established navigation and view switching patterns
- Prefer Flet's built-in components over complex custom implementations

### Server Integration
- **CRITICAL**: Server has NO API - use direct Python method calls via ServerBridge
- ServerBridge is a thin delegation wrapper, not an API client
- All operations are in-memory Python calls: `bridge.get_clients()` → `server.get_clients()`
- Implement proper error handling for server method calls (not network operations)
- Ensure thread safety when calling server methods from GUI thread
- Data format conversion handled by ServerBridge (BLOB UUIDs ↔ strings)

### 🚨 CRITICAL: Flet Async/Sync Integration Pattern (January 2025)

**Root Cause of UI Freezes**: Calling `await` on non-existent async methods or non-coroutine objects causes Python's event loop to block **forever**, freezing the entire Flet GUI with no error messages.

#### ❌ WRONG Pattern - Causes Permanent Freeze

```python
# WRONG - These methods don't exist or aren't async!
async def load_data():
    result = await bridge.get_database_info_async()  # ❌ Method doesn't exist
    result = await bridge.get_table_data_async(table)  # ❌ Returns None, not coroutine
    # Event loop blocks here forever waiting for coroutine
```

**What Happens**:
1. Python tries to `await` a non-coroutine object or non-existent method
2. Event loop blocks indefinitely waiting for a coroutine that never arrives
3. GUI freezes completely - no error messages, no logs, no recovery
4. Application becomes unresponsive and must be force-killed
5. Terminal logs stop abruptly at the freeze point

**Symptoms**:
- View loads successfully (setup function starts)
- Terminal shows "Setting up [view] (async)"
- Logs stop completely after "All update functions completed"
- Browser shows gray screen or empty view
- GUI navigation becomes unresponsive
- No Python exceptions raised
- No error messages in terminal

#### ✅ CORRECT Pattern - Non-Blocking Async

```python
# CORRECT - Wrap sync methods with run_in_executor
async def load_data():
    loop = asyncio.get_running_loop()

    # Run synchronous server bridge methods in thread pool
    result = await loop.run_in_executor(None, bridge.get_database_info)
    result = await loop.run_in_executor(None, bridge.get_table_data, table_name)

    # ✅ Event loop stays responsive while waiting for thread pool
```

**Why This Works**:
1. `loop.run_in_executor(None, func, *args)` runs synchronous `func` in default thread pool executor
2. Returns an awaitable `Future` that the event loop can monitor
3. Event loop remains responsive while thread pool executes sync code
4. No blocking - GUI stays interactive during data loading
5. Proper async integration between Flet (async) and ServerBridge (sync)

**When to Use**:
- **ALWAYS** when calling ServerBridge methods from async Flet view functions
- **ALWAYS** when mixing synchronous backend code with async GUI code
- **ALWAYS** in view setup functions that load data from server
- **ALWAYS** in event handlers that need server data

#### Reference Implementation

**Fixed Example** (database_simple.py:672-678):
```python
async def load_database_info_async() -> None:
    """Load database connection info from server."""
    try:
        # CRITICAL FIX: Use run_in_executor for sync server bridge methods
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_database_info)

        if result and result.get('success'):
            # Process result...
```

**Fixed Example** (database_simple.py:738-744):
```python
async def load_table_data_async() -> None:
    """Load data for currently selected table."""
    try:
        # CRITICAL FIX: Use run_in_executor for sync server bridge methods
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_table_data, current_table)

        if result and result.get('success'):
            # Process result...
```

#### Diagnostic Pattern for Async Freezes

**Add Strategic Logging** to identify freeze points:
```python
async def setup() -> None:
    print("🔴 [SETUP] Starting async setup")

    print("🔴 [SETUP] About to sleep")
    await asyncio.sleep(0.5)
    print("🔴 [SETUP] Sleep completed")

    print("🔴 [SETUP] Loading data 1")
    await load_data_1()
    print("🔴 [SETUP] Data 1 loaded")

    print("🔴 [SETUP] Loading data 2")
    await load_data_2()  # If freeze happens, this line won't print
    print("🔴 [SETUP] Data 2 loaded")
```

**Investigation Steps**:
1. Check terminal logs for last printed message before freeze
2. Identify the `await` statement that never completes
3. Verify the awaited function returns a coroutine (use `inspect.iscoroutine()`)
4. If awaiting ServerBridge method, wrap with `run_in_executor`
5. Test fix and verify all setup logs complete

#### Universal Checklist for Flet Views

**Before Creating Any Async View Function**:
- [ ] ALL ServerBridge calls wrapped with `loop.run_in_executor(None, bridge.method, *args)`
- [ ] NO direct `await bridge.method()` calls (bridge methods are SYNC, not ASYNC)
- [ ] Diagnostic logging added to track async flow (print statements at each step)
- [ ] Test in browser DevTools with Network tab open (check for freeze/hang)
- [ ] Verify terminal shows ALL setup completion logs

**Validation Test**:
```python
# Quick test - add this to any async function
import inspect

async def my_async_function():
    result = some_bridge_call()

    # Validate it's actually a coroutine before awaiting
    if inspect.iscoroutine(result):
        data = await result
    else:
        # ❌ NOT a coroutine - will cause freeze if you await it!
        print(f"ERROR: {result} is not a coroutine, use run_in_executor!")
```

#### Related Documentation
- Flet Async Patterns: https://flet.dev/docs/guides/python/async-apps
- Python asyncio: https://docs.python.org/3/library/asyncio-task.html
- ThreadPoolExecutor: https://docs.python.org/3/library/concurrent.futures.html

### Database Operations

**CRITICAL: Database Best Practices (Updated January 10, 2025)**

#### Connection Pool Management
- **Always use finally blocks**: Ensure connections are returned to pool even on exceptions
- **Track all connections**: Including emergency connections created during pool exhaustion
- **Use time.monotonic() for durations**: NEVER use time.time() for age/duration calculations
  - `time.time()` is affected by system clock changes (NTP, DST)
  - `time.monotonic()` is clock-independent and designed for elapsed time
  - Example: `age = time.monotonic() - info.created_time`
- **Prevent double-return**: Use flags to track if connection already handled in error paths
- **Example pattern**:
```python
conn_returned = False
try:
    conn = self.connection_pool.get_connection()
    # ... operations
    return result
except Exception:
    with suppress(Exception):
        conn.close()
    conn_returned = True
    raise
finally:
    if conn and not conn_returned:
        with suppress(Exception):
            self.connection_pool.return_connection(conn)
```

#### Transaction Handling
- **Use transaction() context manager**: For atomic multi-step operations
- **Check for nested transactions**: Use `conn.in_transaction` before BEGIN
- **Example**:
```python
with self.db_manager.transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE ID = ?", (client_id,))
    cursor.execute("DELETE FROM files WHERE ClientID = ?", (client_id,))
    # Automatic commit or rollback on exception
```

#### Thread Safety
- **Always protect shared state with locks**: Caches, connection tracking, metrics
- **Use threading.Lock**: For cache read/write operations
- **Example**:
```python
with self._cache_lock:
    if self._cache['data'] and not_expired:
        return self._cache['data']
```

#### Query Correctness
- **Verify column names in WHERE clauses**: Common bug - using ID instead of ClientID
- **Always use parameterized queries**: NEVER string interpolation for values
- **Validate table/column names**: If dynamically constructed, use whitelists
- **Example bug to avoid**:
```python
# WRONG - searches by file ID instead of client ID
"SELECT * FROM files WHERE ID = ?"
# CORRECT - searches by client ID
"SELECT * FROM files WHERE ClientID = ?"
```

#### Resource Leak Prevention
- **Track emergency connections**: Store in dict, clean up on shutdown
- **Validate connections before return**: Test with "SELECT 1", handle errors
- **Close connections on validation failure**: Don't return bad connections to pool
- **Clean up partial operations**: Remove incomplete backup files, temp data

#### Error Handling
- **Catch specific exceptions**: sqlite3.OperationalError, sqlite3.DatabaseError
- **Use contextlib.suppress()**: For cleanup operations that may fail
- **Log with appropriate levels**: DEBUG for protocol, INFO for operations, WARNING for recoverable errors
- **Return structured responses**: `{'success': bool, 'data': Any, 'error': str}`

#### Performance Patterns
- **Use COUNT(*) for counting**: Not len(get_all_records())
- **Implement caching with TTL**: 30-second cache for frequently-accessed stats
- **Create appropriate indexes**: On frequently queried columns
- **Use executemany()**: For bulk inserts (10-100x faster)

#### Common Pitfalls to Avoid
1. **❌ Mixed time bases**: Using both time.time() and time.monotonic()
2. **❌ Untracked resources**: Emergency connections, temporary files
3. **❌ Race conditions**: Unprotected cache access in multi-threaded code
4. **❌ Wrong column names**: ID vs ClientID in WHERE clauses
5. **❌ Nested transaction errors**: Not checking if already in transaction
6. **❌ Connection leaks**: Not returning connections in all code paths
7. **❌ Inaccurate metrics**: Reporting attempted operations as successful
8. **❌ Missing validation**: Assuming WAL mode or other features work

#### Schema Patterns
- Use the existing DatabaseManager for all database interactions
- Follow the established schema patterns for client and file records
- Understand CASCADE behavior: Deleting client deletes all associated files
- Include appropriate error handling for database operations
- Foreign key constraints are enforced - maintain referential integrity

### Performance Considerations
- Optimize for frequent UI updates with minimal redraw operations
- Use targeted updates rather than full page refreshes
- Implement efficient data processing for large file transfers
- Consider memory usage when handling large datasets in GUI
- Use GPU-accelerated animations for smooth interactions

### Code Quality
- Maintain the high code quality standards already established
- Use proper type hints and comprehensive error handling
- Follow the existing patterns for logging and diagnostics
- Ensure all new code is well-documented with docstrings

### Logging Standards (October 2025)
The codebase follows strict logging level standards documented in [server.py:82-97](python_server/server/server.py#L82):

**Level Usage**:
- **DEBUG**: Protocol details, packet parsing, reassembly status, detailed state changes (verbose diagnostics)
- **INFO**: Client connections/disconnections, file transfers, successful operations, startup/shutdown (important events)
- **WARNING**: Recoverable errors, validation failures, retries, deprecated usage (needs attention but non-blocking)
- **ERROR**: Failed operations, database errors, crypto failures, network issues (prevents specific operations)
- **CRITICAL**: System failures, startup failures, security violations (system-wide problems)

**Best Practices**:
1. Use DEBUG for verbose info disabled in production by default
2. Use INFO for events that help understand system flow
3. Use WARNING for issues that don't stop operation
4. Include relevant context (client name, file name, operation type) in all messages
5. Avoid duplicate logging (don't log same event at multiple levels)
6. Never use `print()` for diagnostics - always use `logger` methods

### Input Validation Pattern
All user-facing methods must validate inputs before database operations:
```python
# Example from add_client() - server.py:681-707
if not isinstance(name, str) or len(name) == 0:
    return self._format_response(False, error="Invalid name")
if len(name) > MAX_CLIENT_NAME_LENGTH:
    return self._format_response(False, error=f"Name too long (max {MAX_CLIENT_NAME_LENGTH})")
if '\x00' in name or '\n' in name:
    return self._format_response(False, error="Invalid characters")
```

### Constants Management
- Never duplicate constants - import from config.py
- Use descriptive constant names: `DEFAULT_LOG_LINES_LIMIT` not magic number `100`
- Document constant purpose inline: `SETTINGS_FILE = "server_settings.json"  # Settings persistence file`
- Group related constants together (Logging, Settings, Protocol, etc.)

### Code Simplicity & Pragmatism (January 2025)
**CRITICAL: Optimization Philosophy for This Project**

This project is designed for **50-500 users maximum** at small-to-medium scale. All implementation decisions should prioritize:

1. **Simplicity over sophistication**
   - Favor straightforward solutions that "just work"
   - Avoid over-engineering for edge cases that won't occur at this scale
   - SQLite can handle millions of rows - don't optimize prematurely

2. **Pragmatic data retention**
   - Current metrics: 60-second samples, 7-day retention = ~10,000 points/metric
   - Database size: ~1.5 MB after 7 days (negligible)
   - **This is appropriate** - SQLite handles this effortlessly
   - **Don't reduce unless user explicitly requests it**

3. **Avoid unnecessary complexity**
   - If a feature works reliably, leave it alone
   - Don't add configuration knobs "just in case"
   - Trust SQLite's capabilities at this scale

4. **When in doubt, ask about scale**
   - If implementing something that might be "too much", verify with user
   - User prefers simple, working solutions over complex, "enterprise" ones
   - Example: "Is 10,000 data points too much?" → No, it's tiny for SQLite

5. **Retry patterns**
   - Retry decorator is available (server.py:131-185) for transient failures
   - Apply it incrementally to methods that actually encounter errors
   - Don't preemptively add retries everywhere - add where needed

6. **Performance at this scale**
   - 500 users × typical usage = trivial load for SQLite
   - No need for connection pooling beyond basic implementation
   - No need for caching beyond simple 30-second TTL for stats
   - No need for sharding, replication, or distributed systems

**Key Takeaway**: Build for the actual use case (50-500 users), not imaginary enterprise scale. Simple, reliable code beats complex, "scalable" code every time at this scale.

## Critical Coding Patterns & Anti-Patterns (January 2025)

### ✅ Required Patterns - ALWAYS Follow These

#### 1. **Centralized Validation Pattern**
**Rule**: Never duplicate validation logic. Create a single validation method and reuse it.

**Example - Client Name Validation**:
```python
def _validate_client_name(self, name: str) -> tuple[bool, str]:
    """Centralized client name validation."""
    if not name or not isinstance(name, str):
        return False, "Client name is required and must be a string"
    if len(name) > MAX_CLIENT_NAME_LENGTH:
        return False, f"Client name too long (max {MAX_CLIENT_NAME_LENGTH} chars)"
    if any(c in name for c in ('\x00', '\n', '\r', '\t')):
        return False, "Client name contains invalid characters"
    return True, ""

# Then use it everywhere:
is_valid, error_msg = self._validate_client_name(name)
if not is_valid:
    return self._format_response(False, error=error_msg)
```

**Location**: server.py:857-877 (reference implementation)

#### 2. **Database-First Deletion Pattern**
**Rule**: For operations that modify both database AND memory, ALWAYS modify database first, then memory.

**Why**: If database fails, memory is still consistent. Reverse order creates phantom records.

**Pattern**:
```python
# CORRECT - Database first
success = self.db_manager.delete_client(client_id_bytes)
if not success:
    return self._format_response(False, error="Database deletion failed")

# THEN remove from memory (only if DB succeeded)
with self.clients_lock:
    if client := self.clients.pop(client_id_bytes, None):
        self.clients_by_name.pop(client.name, None)
```

**Location**: server.py:1002-1020 (reference implementation)

#### 3. **Universal Retry Decorator Pattern**
**Rule**: ALL database operations MUST have retry protection for `sqlite3.OperationalError`.

**Why**: Multi-threaded access (GUI + network + maintenance) causes database locks. Retry prevents crashes.

**Pattern**:
```python
@retry(max_attempts=3, backoff_base=0.5, exceptions=(sqlite3.OperationalError,))
def any_database_method(self, ...):
    """Method that accesses database."""
    # Database operation here
```

**Apply to**: ALL methods that call `self.db_manager.*` or execute SQL queries

**Locations**:
- Decorator definition: server.py:139-186
- Applied to 16 methods: server.py (search for `@retry`)

#### 4. **Comprehensive Health Check Pattern**
**Rule**: Health checks must VALIDATE critical states, not just READ them.

**Pattern**:
```python
# Don't just read metrics - VALIDATE them
if not pool_status.get('cleanup_thread_alive', False):
    health_data['errors'].append("Connection pool cleanup thread is dead")
    health_data['status'] = 'degraded'

# Check for resource leaks
if hasattr(pool, 'emergency_connections'):
    leak_count = len(pool.emergency_connections)
    if leak_count > 0:
        health_data['errors'].append(f"{leak_count} emergency connections leaked")
        health_data['status'] = 'degraded'
```

**Location**: server.py:1920-1932 (reference implementation)

#### 5. **Rate Limiting Pattern**
**Rule**: Resource-intensive operations (exports, large queries) need per-resource rate limiting.

**Pattern**:
```python
# Per-resource rate limiting (not global)
session_key = f"resource_{identifier}"
with self._rate_limit_lock:
    current_time = time.time()
    last_access = self._last_access_time.get(session_key, 0)

    if current_time - last_access < MIN_INTERVAL:
        remaining = MIN_INTERVAL - (current_time - last_access)
        return self._format_response(False, error=f"Rate limit: wait {remaining:.1f}s")

    self._last_access_time[session_key] = current_time
```

**Locations**:
- Log export: server.py:2431-2442
- Database export: server.py:1458-1471

### ❌ Anti-Patterns - NEVER Do These

#### 1. **❌ Memory-First Deletion**
```python
# WRONG - Creates phantom records on DB failure
with self.clients_lock:
    self.clients.pop(client_id_bytes, None)
success = self.db_manager.delete_client(client_id_bytes)  # May fail!
```

#### 2. **❌ Duplicate Validation Logic**
```python
# WRONG - Validation duplicated in 4 places
if len(name) > MAX_CLIENT_NAME_LENGTH:
    return error  # Repeated everywhere!
```

#### 3. **❌ Unprotected Database Operations**
```python
# WRONG - No retry protection
def get_data(self):
    return self.db_manager.query()  # Will crash on database lock!
```

#### 4. **❌ Passive Health Checks**
```python
# WRONG - Just reading status without validation
health_data['cleanup_thread'] = pool_status.get('cleanup_thread_alive')
# What if it's False? No action taken!
```

#### 5. **❌ Global Rate Limiting**
```python
# WRONG - Single rate limit for all resources
if current_time - self._last_export < 10:
    return error  # Blocks unrelated exports!
```

### 🔧 Refactoring Checklist

When adding new database operations:
- [ ] Apply `@retry` decorator with `sqlite3.OperationalError`
- [ ] Use centralized validation (create helper if needed)
- [ ] Follow database-first pattern for dual updates
- [ ] Add rate limiting if resource-intensive
- [ ] Update health checks with validation logic
- [ ] Add metrics collection (`metrics_collector.record_*`)
- [ ] Use structured logging (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- [ ] Return consistent format: `_format_response(success, data, error)`

### 📚 Reference Implementations

**Perfect Examples to Copy**:
1. **Validation**: `_validate_client_name()` - server.py:857-877
2. **Database-First**: `delete_client()` - server.py:999-1023
3. **Retry Pattern**: Any method with `@retry` decorator
4. **Health Check**: `get_server_health()` - server.py:1877-1938
5. **Rate Limiting**: `get_table_data()` - server.py:1458-1471

**Code to Learn From**:
- Retry decorator: server.py:139-186
- Metrics collection: server.py:168-172, 644-668
- Connection pooling: database.py (reference for thread safety)
- Structured responses: `_format_response()` - server.py:849-855

## Troubleshooting

### Common Issues
- GUI freezing during server communication: Check for blocking operations
- Client connection failures: Verify protocol compatibility and network settings
- Database lock issues: Ensure proper transaction handling and connection cleanup
- GUI styling inconsistencies: Follow established theme patterns

### Debugging
- Enable detailed logging with `--verbose` or environment variables
- Use the ServerBridge test methods to verify server functionality
- Check the server.log and enhanced log files for error details
- Use the built-in diagnostic tools in the GUI for system monitoring

## Future Development

### Planned Enhancements
- Enhanced analytics and reporting features
- Improved backup scheduling and automation
- Advanced file versioning and recovery options
- Additional GUI themes and customization options

### Architecture Considerations
- Scalability for larger client deployments
- Additional encryption algorithms support
- Cloud storage integration options
- Advanced monitoring and alerting systems