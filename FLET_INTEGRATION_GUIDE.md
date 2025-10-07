# Flet 0.28.3 Integration Guide: Python Server + SQLite3 + Async GUI
## The Definitive Guide to Solving Integration Issues

**Target Environment**: Python 3.13.5 + Flet 0.28.3 + SQLite3
**Last Updated**: January 2025
**Purpose**: Solve integration freezes, gray screens, and async/sync boundary issues

---

## 🎯 Executive Summary: The "OHHHH!" Moment

### The Root Cause of Your Integration Issues

**99% of Flet integration freezes come from one mistake**:

> **Calling `await` on synchronous methods or not using `run_in_executor` for blocking operations**

When you `await` something that isn't a coroutine, Python's event loop **blocks forever** waiting for a coroutine that will never arrive. This causes:
- Permanent UI freeze (gray screen)
- No error messages
- No logs
- No recovery
- Application becomes completely unresponsive

### The Golden Rule

```python
# ❌ WRONG - Causes permanent freeze
async def load_data():
    result = await bridge.get_database_info()  # If this isn't async, FREEZE!

# ✅ CORRECT - Non-blocking async
async def load_data():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_database_info)
```

**Why This Happens**:
1. Flet is async-first (runs on asyncio event loop)
2. Your server/database methods are synchronous (blocking)
3. When async Flet code calls sync methods directly → event loop blocks
4. When you `await` non-async methods → event loop blocks **forever**

**The Fix**: Wrap ALL synchronous server/database calls with `run_in_executor`

---

## 🚨 Critical Integration Rules (Non-Negotiable)

### Rule 1: NEVER Block the Event Loop

```python
# ❌ WRONG - Blocks event loop
async def button_click(e):
    time.sleep(5)  # UI freezes for 5 seconds
    page.update()

# ✅ CORRECT - Non-blocking
async def button_click(e):
    await asyncio.sleep(5)  # UI stays responsive
    page.update()
```

### Rule 2: ALWAYS Use run_in_executor for Sync Operations

```python
# ❌ WRONG - Direct sync call in async context
async def fetch_clients():
    clients = server.get_clients()  # Blocks event loop
    return clients

# ✅ CORRECT - Wrapped with run_in_executor
async def fetch_clients():
    loop = asyncio.get_running_loop()
    clients = await loop.run_in_executor(None, server.get_clients)
    return clients
```

### Rule 3: Use page.loop and page.executor (NOT asyncio.get_running_loop() everywhere)

```python
# ❌ WRONG - Creating new loop
async def load_data(page):
    loop = asyncio.new_event_loop()  # Creates conflicting loop

# ✅ CORRECT - Use page's existing loop
async def load_data(page):
    loop = page.loop  # or asyncio.get_running_loop()
    result = await loop.run_in_executor(page.executor, sync_function)
```

### Rule 4: Update UI After State Changes

```python
# ❌ WRONG - No update call
def change_text(e):
    text_field.value = "New value"  # Change not reflected

# ✅ CORRECT - Call update()
def change_text(e):
    text_field.value = "New value"
    page.update()  # or text_field.update()
```

### Rule 5: Never Call asyncio.run() Inside Flet

```python
# ❌ WRONG - Event loop already running
async def button_click(e):
    result = asyncio.run(some_async_function())  # RuntimeError!

# ✅ CORRECT - Just await it
async def button_click(e):
    result = await some_async_function()
```

---

## 🔄 Async/Sync Boundary Management

### Understanding Flet's Event Loop Model

Flet 0.21+ is **async-first**:
- Main app runs in asyncio event loop
- Event handlers can be sync OR async
- Sync handlers run in ThreadPoolExecutor
- Async handlers run as asyncio Tasks

### The ServerBridge Pattern

Your `ServerBridge` wraps a synchronous `BackupServer`. Here's the correct pattern:

```python
class ServerBridge:
    def __init__(self, server):
        self.server = server  # Synchronous BackupServer instance

    # ❌ WRONG - Marked as async but isn't
    async def get_clients(self):
        return self.server.get_clients()  # Still sync, misleading!

    # ✅ CORRECT - Synchronous method (honest about what it is)
    def get_clients(self):
        """Synchronous wrapper - use with run_in_executor"""
        return self.server.get_clients()
```

### Calling ServerBridge from Flet Views

```python
# ❌ WRONG PATTERN 1 - Awaiting non-async method
async def load_clients():
    result = await bridge.get_clients()  # FREEZE if get_clients isn't async!

# ❌ WRONG PATTERN 2 - Blocking async function
async def load_clients():
    result = bridge.get_clients()  # Blocks event loop

# ✅ CORRECT PATTERN - run_in_executor
async def load_clients():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_clients)
    # Now we can safely process result
    if result and result.get('success'):
        clients = result['data']
        update_ui(clients)
```

### Universal Template for Sync→Async Conversion

```python
# Template for ANY synchronous operation in Flet
async def async_wrapper_for_sync_operation():
    """Universal pattern for integrating sync code with Flet."""
    loop = asyncio.get_running_loop()

    try:
        # Wrap synchronous call
        result = await loop.run_in_executor(
            None,  # Use default executor
            sync_function,  # Your sync function
            arg1, arg2  # Any arguments
        )

        # Process result
        return result

    except Exception as e:
        logger.error(f"Async wrapper error: {e}")
        return None
```

### Real-World Example: Database View Setup

```python
# ❌ WRONG - From your codebase (causes freeze)
async def load_database_info_async():
    try:
        # This freezes if get_database_info isn't truly async
        result = await bridge.get_database_info_async()

# ✅ CORRECT - Fixed version
async def load_database_info_async():
    try:
        loop = asyncio.get_running_loop()

        # Wrap synchronous bridge method
        result = await loop.run_in_executor(None, bridge.get_database_info)

        if result and result.get('success'):
            db_info = result['data']
            # Update UI components
            connection_status.value = "Connected"
            connection_status.update()

    except Exception as e:
        logger.error(f"Failed to load database info: {e}")
        connection_status.value = f"Error: {e}"
        connection_status.update()
```

---

## 💾 Database Integration Patterns (SQLite3)

### The Fundamental Problem

SQLite3 operations are **synchronous and blocking**:
- File I/O operations
- Lock acquisition
- Query execution
- Transaction commits

Flet's event loop is **asynchronous and non-blocking**:
- Must never wait for I/O
- Needs immediate responsiveness
- Runs on single thread

**Solution**: Offload database operations to thread pool

### Pattern 1: Direct run_in_executor (Recommended for Simple Cases)

```python
import asyncio
import sqlite3

async def fetch_data_from_database(page):
    """Simple pattern for one-off database queries."""
    loop = asyncio.get_running_loop()

    def _sync_db_query():
        conn = sqlite3.connect('database.db')
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients")
            return cursor.fetchall()
        finally:
            conn.close()

    # Run blocking database operation in thread pool
    result = await loop.run_in_executor(None, _sync_db_query)
    return result
```

### Pattern 2: DatabaseBridge Class (Recommended for Complex Apps)

```python
class DatabaseBridge:
    """Async wrapper for synchronous database operations."""

    def __init__(self, db_manager, page):
        self.db_manager = db_manager  # Synchronous DatabaseManager
        self.page = page

    async def get_clients_async(self):
        """Fetch all clients asynchronously."""
        loop = asyncio.get_running_loop()

        def _fetch():
            # Call synchronous database method
            return self.db_manager.get_all_clients()

        return await loop.run_in_executor(None, _fetch)

    async def add_client_async(self, name, public_key):
        """Add client asynchronously."""
        loop = asyncio.get_running_loop()

        def _add():
            return self.db_manager.add_client(name, public_key)

        return await loop.run_in_executor(None, _add)

    async def query_async(self, query, params=None):
        """Execute arbitrary query asynchronously."""
        loop = asyncio.get_running_loop()

        def _query():
            conn = sqlite3.connect(self.db_manager.db_path)
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
            finally:
                conn.close()

        return await loop.run_in_executor(None, _query)
```

### Pattern 3: Using page.run_task for Background Operations

```python
class DataLoader(ft.UserControl):
    def __init__(self, server_bridge):
        super().__init__()
        self.bridge = server_bridge
        self.data = []

    def did_mount(self):
        """Called when control is added to page."""
        # Start background data loading
        self.page.run_task(self.load_data_background)

    async def load_data_background(self):
        """Background task to load data periodically."""
        while True:
            try:
                loop = asyncio.get_running_loop()

                # Load data from database
                result = await loop.run_in_executor(
                    None,
                    self.bridge.get_latest_data
                )

                if result:
                    self.data = result
                    self.update()  # Update this control only

                # Wait before next refresh
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Background load error: {e}")
                await asyncio.sleep(60)  # Retry after longer delay
```

### Connection Pooling with Async

```python
import concurrent.futures
import sqlite3

class AsyncDatabasePool:
    """Thread-safe database connection pool for Flet."""

    def __init__(self, db_path, max_workers=5):
        self.db_path = db_path
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="db-worker"
        )

    async def execute(self, query, params=None):
        """Execute query asynchronously."""
        loop = asyncio.get_running_loop()

        def _execute():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return dict-like rows
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.fetchall()
            finally:
                conn.close()

        return await loop.run_in_executor(self.executor, _execute)

    async def execute_many(self, query, params_list):
        """Execute multiple queries in batch."""
        loop = asyncio.get_running_loop()

        def _execute_many():
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
            finally:
                conn.close()

        return await loop.run_in_executor(self.executor, _execute_many)

    def shutdown(self):
        """Clean shutdown of thread pool."""
        self.executor.shutdown(wait=True)
```

### Error Handling for Database Operations

```python
async def safe_database_operation(page, bridge):
    """Comprehensive error handling pattern."""

    # Show loading state
    loading_indicator.visible = True
    error_message.visible = False
    page.update()

    try:
        loop = asyncio.get_running_loop()

        # Attempt database operation
        result = await loop.run_in_executor(
            None,
            bridge.get_database_info
        )

        if result and result.get('success'):
            # Process successful result
            data = result['data']
            display_data(data)

        else:
            # Handle business logic error
            error_msg = result.get('error', 'Unknown error')
            error_message.value = f"Operation failed: {error_msg}"
            error_message.visible = True

    except sqlite3.OperationalError as e:
        # Database locked or other SQLite error
        error_message.value = f"Database error: {e}"
        error_message.visible = True
        logger.error(f"SQLite error: {e}")

    except Exception as e:
        # Unexpected error
        error_message.value = f"Unexpected error: {e}"
        error_message.visible = True
        logger.exception("Unexpected database operation error")

    finally:
        # Always hide loading indicator
        loading_indicator.visible = False
        page.update()
```

---

## 🎨 State Management Patterns

### page.update() vs control.update()

**Use `page.update()`** when:
- Multiple controls changed
- Layout changes
- Theme changes
- Initial page setup

**Use `control.update()`** when:
- Single control changed
- Performance-critical updates
- Inside custom controls
- Isolated control state

```python
# ❌ INEFFICIENT - Multiple page updates
def update_multiple_controls(e):
    control1.value = "New value"
    page.update()
    control2.value = "Another value"
    page.update()
    control3.value = "Third value"
    page.update()

# ✅ EFFICIENT - Batch update
def update_multiple_controls(e):
    control1.value = "New value"
    control2.value = "Another value"
    control3.value = "Third value"
    page.update()  # Single update for all changes

# ✅ ALSO GOOD - Targeted updates for isolated controls
def update_single_control(e):
    status_indicator.value = "Updated"
    status_indicator.color = "green"
    status_indicator.update()  # Only this control re-renders
```

### Reactive State Pattern

```python
class StatefulView:
    """Pattern for managing view state."""

    def __init__(self, page, bridge):
        self.page = page
        self.bridge = bridge
        self.state = {
            'loading': False,
            'data': [],
            'error': None
        }
        self.controls = {}  # Store references to controls

    def _update_state(self, **kwargs):
        """Update state and trigger UI refresh."""
        self.state.update(kwargs)
        self._render()

    def _render(self):
        """Re-render UI based on current state."""
        if self.state['loading']:
            self.controls['loading'].visible = True
            self.controls['content'].visible = False
            self.controls['error'].visible = False
        elif self.state['error']:
            self.controls['loading'].visible = False
            self.controls['content'].visible = False
            self.controls['error'].visible = True
            self.controls['error'].value = str(self.state['error'])
        else:
            self.controls['loading'].visible = False
            self.controls['content'].visible = True
            self.controls['error'].visible = False
            # Update content with data
            self._update_content_controls(self.state['data'])

        self.page.update()

    async def load_data(self):
        """Load data with state management."""
        self._update_state(loading=True, error=None)

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, self.bridge.get_data)

            if result and result.get('success'):
                self._update_state(loading=False, data=result['data'])
            else:
                self._update_state(
                    loading=False,
                    error=result.get('error', 'Unknown error')
                )
        except Exception as e:
            self._update_state(loading=False, error=str(e))
```

### State Synchronization with Server

```python
class ServerSyncedState:
    """Keep UI state synchronized with server state."""

    def __init__(self, page, bridge):
        self.page = page
        self.bridge = bridge
        self.sync_interval = 10  # seconds
        self.running = False

    def start_sync(self):
        """Start background synchronization."""
        self.running = True
        self.page.run_task(self._sync_loop)

    def stop_sync(self):
        """Stop background synchronization."""
        self.running = False

    async def _sync_loop(self):
        """Background sync loop."""
        while self.running:
            try:
                await self._sync_once()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Sync error: {e}")
                await asyncio.sleep(self.sync_interval * 2)

    async def _sync_once(self):
        """Perform single sync operation."""
        loop = asyncio.get_running_loop()

        # Fetch latest state from server
        result = await loop.run_in_executor(
            None,
            self.bridge.get_server_state
        )

        if result and result.get('success'):
            # Update UI with new state
            self._apply_state(result['data'])

    def _apply_state(self, state):
        """Apply server state to UI."""
        # Update controls based on state
        # Call page.update() once at the end
        pass
```

---

## 🧵 Threading and Concurrency Patterns

### Flet's Threading Model

1. **Main Thread**: Runs asyncio event loop (Flet UI)
2. **Thread Pool**: Executes sync event handlers and run_in_executor tasks
3. **Background Tasks**: Async coroutines via page.run_task()

### When to Use Each Approach

| Operation Type | Use This Pattern | Example |
|---------------|------------------|---------|
| UI Event Handler (simple) | Sync function | `def button_click(e): ...` |
| UI Event Handler (with I/O) | Async function | `async def button_click(e): ...` |
| Background periodic task | `page.run_task()` | Auto-refresh, polling |
| Blocking sync call from async | `run_in_executor` | Database, file I/O |
| CPU-intensive work | `asyncio.to_thread()` | Image processing, computation |

### Pattern: Background Task Management

```python
class BackgroundTaskManager:
    """Manage background tasks with proper lifecycle."""

    def __init__(self, page):
        self.page = page
        self.tasks = {}  # task_id -> asyncio.Task

    def start_task(self, task_id, coro):
        """Start a background task."""
        if task_id in self.tasks:
            self.stop_task(task_id)

        task = self.page.run_task(coro)
        self.tasks[task_id] = task
        return task

    def stop_task(self, task_id):
        """Stop a background task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if not task.done():
                task.cancel()
            del self.tasks[task_id]

    def stop_all(self):
        """Stop all background tasks."""
        for task_id in list(self.tasks.keys()):
            self.stop_task(task_id)

# Usage
task_manager = BackgroundTaskManager(page)

async def auto_refresh_data():
    while True:
        await load_latest_data()
        await asyncio.sleep(30)

task_manager.start_task('auto_refresh', auto_refresh_data())
```

### Pattern: Thread-Safe UI Updates

```python
class ThreadSafeUIUpdater:
    """Update UI safely from any thread."""

    def __init__(self, page):
        self.page = page
        self.update_queue = []
        self.lock = threading.Lock()

    def schedule_update(self, update_func):
        """Schedule UI update from any thread."""
        with self.lock:
            self.update_queue.append(update_func)

        # Trigger processing on main thread
        self.page.run_task(self._process_updates())

    async def _process_updates(self):
        """Process all queued updates."""
        with self.lock:
            updates = self.update_queue.copy()
            self.update_queue.clear()

        for update_func in updates:
            try:
                update_func()
            except Exception as e:
                logger.error(f"UI update error: {e}")

        self.page.update()

# Usage from background thread
def background_worker():
    result = compute_something()

    def update_ui():
        result_label.value = str(result)

    ui_updater.schedule_update(update_ui)
```

---

## ❌ Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Blocking with time.sleep()

```python
# ❌ WRONG - Freezes entire UI
async def delayed_action(e):
    time.sleep(5)  # UI completely frozen
    page.add(ft.Text("Delayed text"))
    page.update()

# ✅ CORRECT - Non-blocking delay
async def delayed_action(e):
    await asyncio.sleep(5)  # UI stays responsive
    page.add(ft.Text("Delayed text"))
    page.update()
```

### Anti-Pattern 2: Calling asyncio.run() in Event Loop

```python
# ❌ WRONG - RuntimeError
async def button_click(e):
    result = asyncio.run(fetch_data())  # Event loop already running!

# ✅ CORRECT - Just await
async def button_click(e):
    result = await fetch_data()
```

### Anti-Pattern 3: Awaiting Non-Async Functions

```python
# ❌ WRONG - Permanent freeze
async def load_data():
    # If get_clients() is sync, this FREEZES FOREVER
    result = await bridge.get_clients()

# ✅ CORRECT - Check if actually async or use run_in_executor
async def load_data():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_clients)
```

### Anti-Pattern 4: Direct Database Calls in Async Context

```python
# ❌ WRONG - Blocks event loop
async def fetch_records():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records")  # Blocking I/O
    return cursor.fetchall()

# ✅ CORRECT - Offload to thread pool
async def fetch_records():
    loop = asyncio.get_running_loop()

    def _fetch():
        conn = sqlite3.connect('db.db')
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM records")
            return cursor.fetchall()
        finally:
            conn.close()

    return await loop.run_in_executor(None, _fetch)
```

### Anti-Pattern 5: Excessive page.update() Calls

```python
# ❌ WRONG - 1000 page updates
for item in range(1000):
    page.add(ft.Text(str(item)))
    page.update()  # Very slow!

# ✅ CORRECT - Batch updates
items = [ft.Text(str(i)) for i in range(1000)]
page.add(*items)
page.update()  # Single update

# ✅ EVEN BETTER - Use ListView for large lists
list_view = ft.ListView(
    controls=[ft.Text(str(i)) for i in range(1000)],
    expand=True
)
page.add(list_view)
page.update()
```

### Anti-Pattern 6: Forgetting to Call update()

```python
# ❌ WRONG - Changes not reflected
def change_color(e):
    button.color = "red"  # No visual change

# ✅ CORRECT - Call update()
def change_color(e):
    button.color = "red"
    button.update()  # or page.update()
```

### Anti-Pattern 7: Creating New Event Loops

```python
# ❌ WRONG - Conflicts with Flet's loop
async def do_something(page):
    loop = asyncio.new_event_loop()  # DON'T!
    asyncio.set_event_loop(loop)

# ✅ CORRECT - Use existing loop
async def do_something(page):
    loop = asyncio.get_running_loop()  # or page.loop
```

### Anti-Pattern 8: UI Updates from Non-UI Threads

```python
# ❌ WRONG - Thread safety violation
def background_thread():
    result = compute()
    page.add(ft.Text(result))  # NOT THREAD SAFE!
    page.update()

# ✅ CORRECT - Use page.run_task
def background_thread():
    result = compute()

    async def update_ui():
        page.add(ft.Text(result))
        page.update()

    page.run_task(update_ui)
```

### Anti-Pattern 9: Sync Event Handler with Async Calls

```python
# ❌ WRONG - Can't await in sync function
def button_click(e):
    data = await fetch_data()  # SyntaxError!

# ✅ CORRECT - Make handler async
async def button_click(e):
    data = await fetch_data()
```

### Anti-Pattern 10: Not Handling Async Exceptions

```python
# ❌ WRONG - Silent failure
async def risky_operation():
    await might_fail()  # Exception gets lost

# ✅ CORRECT - Proper error handling
async def risky_operation():
    try:
        await might_fail()
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        error_dialog.open = True
        page.update()
```

---

## 🔍 Diagnostic Checklist

### When Your Flet App Freezes

1. **Check for blocking operations**:
   ```python
   # Search codebase for:
   - time.sleep()
   - synchronous database calls without run_in_executor
   - synchronous file I/O in async functions
   - long-running loops without await points
   ```

2. **Verify async/await usage**:
   ```python
   # Add diagnostic logging
   async def suspect_function():
       print("🔴 [DEBUG] Function starting")
       await asyncio.sleep(0.1)
       print("🔴 [DEBUG] After sleep")
       result = await operation()
       print(f"🔴 [DEBUG] Result: {result}")
       # If logs stop, the line above is the freeze point
   ```

3. **Check if methods are actually async**:
   ```python
   import inspect

   # Validate coroutines
   async def validate_async():
       result = potentially_async_function()

       if inspect.iscoroutine(result):
           data = await result
       else:
           # NOT a coroutine - will freeze if you await it!
           print(f"❌ ERROR: {result} is not a coroutine!")
           # Use run_in_executor instead
   ```

4. **Monitor event loop health**:
   ```python
   async def check_event_loop():
       loop = asyncio.get_running_loop()
       print(f"Loop running: {loop.is_running()}")
       print(f"Loop closed: {loop.is_closed()}")

       # Check for slow tasks
       loop.set_debug(True)  # Enable asyncio debug mode
   ```

5. **Test with minimal reproduction**:
   ```python
   import flet as ft

   async def main(page: ft.Page):
       async def test_operation(e):
           print("Starting test")
           await asyncio.sleep(1)
           print("Test completed")
           page.add(ft.Text("Success!"))
           page.update()

       page.add(ft.ElevatedButton("Test", on_click=test_operation))

   ft.app(target=main)
   ```

### Debugging Freeze Points

```python
# Add strategic logging to find freeze location
async def debug_view_setup():
    print("🔴 [SETUP] Starting")

    print("🔴 [SETUP] About to sleep")
    await asyncio.sleep(0.5)
    print("🔴 [SETUP] Sleep completed")  # If this prints, sleep works

    print("🔴 [SETUP] Loading database info")
    await load_database_info()
    print("🔴 [SETUP] Database info loaded")  # If this doesn't print, freeze is in load_database_info

    print("🔴 [SETUP] Loading table data")
    await load_table_data()
    print("🔴 [SETUP] Table data loaded")

    print("🔴 [SETUP] Setup complete")

# The last printed message shows where the freeze occurs
```

### Common Freeze Signatures

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Gray screen, no logs | Awaiting non-async method | Use run_in_executor |
| Freeze during data load | Blocking database call | Wrap with run_in_executor |
| UI frozen during operation | time.sleep() in async code | Use asyncio.sleep() |
| "RuntimeError: Event loop" | asyncio.run() called | Just await, don't run() |
| No UI updates | Forgot page.update() | Add update() calls |
| Slow rendering | Too many update() calls | Batch updates |

---

## 📋 Quick Reference Card

### Async Integration Cheat Sheet

```python
# ✅ UNIVERSAL PATTERN - Copy and modify for your needs
async def flet_async_operation_template(page, sync_method, *args):
    """Template for integrating sync operations with Flet."""

    # 1. Show loading state
    loading_spinner.visible = True
    page.update()

    try:
        # 2. Get event loop
        loop = asyncio.get_running_loop()

        # 3. Run sync operation in thread pool
        result = await loop.run_in_executor(
            None,  # Default executor
            sync_method,  # Your synchronous function
            *args  # Arguments to pass
        )

        # 4. Process result
        if result:
            # Update UI with result
            display_result(result)

    except Exception as e:
        # 5. Handle errors
        logger.error(f"Operation failed: {e}")
        show_error_message(str(e))

    finally:
        # 6. Hide loading state
        loading_spinner.visible = False
        page.update()
```

### Decision Tree

```
Need to call server/database method from Flet?
│
├─ Is the method async (returns coroutine)?
│  ├─ YES → Just await it
│  │         async def handler():
│  │             result = await async_method()
│  │
│  └─ NO → Use run_in_executor
│            async def handler():
│                loop = asyncio.get_running_loop()
│                result = await loop.run_in_executor(None, sync_method)
│
UI needs to update?
│
├─ Multiple controls changed?
│  └─ YES → page.update()
│
└─ Single control changed?
   └─ YES → control.update()
```

### Essential Imports

```python
# Core Flet
import flet as ft

# Async support
import asyncio
import inspect  # For iscoroutine()

# Threading
import threading
import concurrent.futures

# Database
import sqlite3

# Logging
import logging
logger = logging.getLogger(__name__)
```

### Validation Checklist

Before deploying, verify:

- [ ] NO `time.sleep()` in async functions (use `asyncio.sleep()`)
- [ ] NO `asyncio.run()` inside Flet app (just `await`)
- [ ] ALL sync database calls wrapped with `run_in_executor`
- [ ] ALL server bridge sync methods wrapped when called from async
- [ ] ALL state changes followed by `update()` call
- [ ] ALL async event handlers declared with `async def`
- [ ] ALL exceptions in async code have try/except handlers
- [ ] NO direct UI updates from non-UI threads
- [ ] Large lists use `ListView` not `Column`
- [ ] Background tasks use `page.run_task()`

---

## 🎓 Educational Insights

### ★ Insight 1: Why run_in_executor Exists ─────────────────────────

Python's asyncio was designed for I/O-bound concurrency, but not all libraries are async-ready. `run_in_executor` bridges this gap by:

1. Running sync code in a thread pool (ThreadPoolExecutor)
2. Wrapping the result in an awaitable Future
3. Allowing the event loop to stay responsive while waiting

This is **the official Python pattern** for mixing sync and async code. It's not a workaround—it's the intended solution.

**Key Insight**: `run_in_executor(None, func)` uses the default thread pool. For CPU-intensive tasks, create a dedicated ProcessPoolExecutor instead.

### ★ Insight 2: Flet's Async Evolution ─────────────────────────

Flet versions:
- **Pre-0.21**: Sync-only, all handlers in threads
- **0.21+**: Async-first, can mix sync and async
- **0.28.3**: Mature async support with `page.loop` and `page.executor`

Your integration issues likely stem from mixing old sync patterns with new async architecture. The solution: embrace async fully and use `run_in_executor` for legacy sync code.

### ★ Insight 3: The Event Loop Contract ─────────────────────────

When you `await` something, you're making a promise:
> "This will yield control back to the event loop periodically"

If you `await` a non-coroutine or a blocking operation, you **break this contract**. The event loop waits forever because the promised "yielding" never happens.

**This is why you get permanent freezes with no error messages**—Python is still technically running, just blocked waiting for a coroutine that will never yield.

---

## 🚀 Migration Guide: Fixing Your Codebase

### Step 1: Identify All Sync Server/Database Calls

```bash
# Search for direct server bridge calls in async functions
grep -r "await bridge\." FletV2/views/
grep -r "await server\." FletV2/views/
```

### Step 2: Create Async Wrappers

```python
# In server_bridge.py or new async_bridge.py

class AsyncServerBridge:
    """Async wrapper for synchronous ServerBridge."""

    def __init__(self, sync_bridge):
        self.bridge = sync_bridge

    async def get_clients(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.bridge.get_clients)

    async def get_database_info(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.bridge.get_database_info)

    async def get_table_data(self, table_name):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.bridge.get_table_data, table_name)

    # Add wrappers for ALL server bridge methods used from async context
```

### Step 3: Update View Functions

```python
# OLD CODE (causes freeze)
async def load_database_info_async():
    result = await bridge.get_database_info_async()  # If this isn't truly async, FREEZE!

# NEW CODE (fixed)
async def load_database_info_async():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.get_database_info)
    # Process result...

# OR using AsyncServerBridge
async_bridge = AsyncServerBridge(bridge)

async def load_database_info_async():
    result = await async_bridge.get_database_info()  # Now truly async
    # Process result...
```

### Step 4: Add Diagnostic Logging

```python
# Add to all async view setup functions
async def setup():
    logger.info("🔴 [SETUP] Starting async setup")

    logger.info("🔴 [SETUP] Loading data 1")
    await load_data_1()
    logger.info("🔴 [SETUP] Data 1 completed")

    logger.info("🔴 [SETUP] Loading data 2")
    await load_data_2()
    logger.info("🔴 [SETUP] Data 2 completed")

    logger.info("🔴 [SETUP] Setup complete")
```

### Step 5: Test Systematically

1. Test each view individually
2. Verify all setup logs complete
3. Check for gray screens or freezes
4. Monitor terminal for freeze points
5. Fix any remaining blocking operations

---

## 📚 Additional Resources

### Official Flet Documentation
- [Async Apps Guide](https://flet.dev/docs/getting-started/async-apps/)
- [Flet Controls Reference](https://flet.dev/docs/controls/)
- [Page Class Documentation](https://flet.dev/docs/controls/page/)

### Python Asyncio
- [Official Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [asyncio Event Loop](https://docs.python.org/3/library/asyncio-eventloop.html)
- [asyncio Tasks and Coroutines](https://docs.python.org/3/library/asyncio-task.html)

### SQLite3 Async Patterns
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite library
- [SQLite3 Python Docs](https://docs.python.org/3/library/sqlite3.html)

### Community Resources
- [Flet GitHub Issues](https://github.com/flet-dev/flet/issues)
- [Flet Discord Community](https://discord.gg/dzWXP8SHG8)
- Stack Overflow: Search for "flet async" or "flet freeze"

---

## 🎯 Conclusion: Your Action Plan

### Immediate Fixes

1. **Find all `await bridge.method()` calls**
   - If `bridge.method()` is synchronous, wrap with `run_in_executor`

2. **Replace all `time.sleep()` with `asyncio.sleep()`**
   - In async functions only

3. **Add diagnostic logging**
   - Before and after each async operation
   - Identify freeze points

4. **Verify update() calls**
   - After every UI state change

### Long-Term Improvements

1. **Create AsyncServerBridge wrapper class**
   - Properly wraps all sync methods
   - Clear async API for views

2. **Implement proper error handling**
   - Try/except in all async functions
   - Show user-friendly error messages

3. **Add loading states**
   - Visual feedback during operations
   - Better UX

4. **Profile performance**
   - Identify slow operations
   - Optimize batch updates

### Success Criteria

✅ No gray screens or permanent freezes
✅ All setup logs complete successfully
✅ UI stays responsive during data loading
✅ Error messages display properly
✅ Background tasks run without blocking

---

**Remember**: When in doubt, wrap it with `run_in_executor`. It's better to be explicit and safe than implicit and frozen.

Good luck with your integration! 🚀
