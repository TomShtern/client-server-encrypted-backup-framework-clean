# Flet Integration Quick Fix Guide
## Immediate Actions to Unfreeze Your Application

**Target**: Fix UI freezes in FletV2 views caused by async/sync boundary issues
**Time to Fix**: 15-30 minutes
**Difficulty**: Easy - Find and replace pattern

---

## 🎯 The Problem (From Your CLAUDE.md)

> **Root Cause**: Calling `await` on synchronous ServerBridge methods causes Python's event loop to block **forever**, freezing the entire Flet GUI with no error messages.

### Symptoms You're Experiencing

- ✅ View loads successfully (setup function starts)
- ✅ Terminal shows "Setting up [view] (async)"
- ✅ Logs show "All update functions completed"
- ❌ Browser shows gray screen or empty view
- ❌ GUI navigation becomes unresponsive
- ❌ No Python exceptions raised
- ❌ No error messages in terminal
- ❌ Logs stop abruptly at freeze point

---

## 🔧 The Fix: 3-Step Pattern

### Step 1: Identify Problematic Code

Search your codebase for this pattern:

```python
# ❌ THIS CAUSES PERMANENT FREEZE
async def load_something():
    result = await bridge.some_method()  # If some_method isn't truly async, FREEZE!
```

### Step 2: Apply the Universal Fix

Replace with this pattern:

```python
# ✅ THIS WORKS - NON-BLOCKING
async def load_something():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.some_method)
```

### Step 3: Verify the Fix

Add diagnostic logging to confirm:

```python
async def load_something():
    print("🔴 [DEBUG] Starting load_something")

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bridge.some_method)

    print("🔴 [DEBUG] Completed load_something")  # This should print now!
```

---

## 📝 Specific Fixes for Your Codebase

### Fix 1: database_simple.py - Database Info Loading

**Location**: `FletV2/views/database_simple.py:672-678`

**BEFORE (Causes Freeze)**:
```python
async def load_database_info_async() -> None:
    """Load database connection info from server."""
    try:
        # ❌ WRONG: Awaiting sync method causes freeze
        result = await bridge.get_database_info_async()

        if result and result.get('success'):
            # Process result...
```

**AFTER (Fixed)**:
```python
async def load_database_info_async() -> None:
    """Load database connection info from server."""
    try:
        # ✅ CORRECT: Use run_in_executor for sync bridge methods
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_database_info)

        if result and result.get('success'):
            # Process result...
```

**Why This Works**: `bridge.get_database_info` is a synchronous method. By using `run_in_executor`, we run it in a thread pool and wrap the result in an awaitable Future, keeping the event loop responsive.

---

### Fix 2: database_simple.py - Table Data Loading

**Location**: `FletV2/views/database_simple.py:738-744`

**BEFORE (Causes Freeze)**:
```python
async def load_table_data_async() -> None:
    """Load data for currently selected table."""
    try:
        # ❌ WRONG: Awaiting sync method causes freeze
        result = await bridge.get_table_data_async(current_table)

        if result and result.get('success'):
            # Process result...
```

**AFTER (Fixed)**:
```python
async def load_table_data_async() -> None:
    """Load data for currently selected table."""
    try:
        # ✅ CORRECT: Use run_in_executor for sync bridge methods
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_table_data, current_table)

        if result and result.get('success'):
            # Process result...
```

---

### Fix 3: Universal Pattern for ALL Views

**Search Pattern**: Find all instances in your views

```bash
# From project root
grep -rn "await bridge\." FletV2/views/
```

**Replace ALL instances with this pattern**:

```python
# BEFORE
result = await bridge.any_method(args)

# AFTER
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(None, bridge.any_method, args)
```

**Note**: If method has multiple arguments:

```python
# Multiple arguments - separate with commas
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(
    None,
    bridge.method_name,
    arg1,
    arg2,
    arg3
)
```

---

## 🏗️ Alternative Approach: Create Async Bridge Wrapper

If you have many bridge methods, create a wrapper once instead of fixing each call:

**Create**: `FletV2/utils/async_bridge.py`

```python
"""Async wrapper for synchronous ServerBridge."""

import asyncio
from typing import Any, Dict


class AsyncServerBridge:
    """Wraps synchronous ServerBridge methods to make them truly async."""

    def __init__(self, sync_bridge):
        """
        Initialize with synchronous ServerBridge instance.

        Args:
            sync_bridge: The synchronous ServerBridge instance
        """
        self.bridge = sync_bridge

    async def _run_sync(self, method, *args, **kwargs):
        """Helper to run synchronous methods asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: method(*args, **kwargs)
        )

    # Database methods
    async def get_database_info(self) -> Dict[str, Any]:
        """Get database connection info asynchronously."""
        return await self._run_sync(self.bridge.get_database_info)

    async def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """Get table data asynchronously."""
        return await self._run_sync(self.bridge.get_table_data, table_name)

    async def get_table_list(self) -> Dict[str, Any]:
        """Get list of tables asynchronously."""
        return await self._run_sync(self.bridge.get_table_list)

    # Client methods
    async def get_clients(self) -> Dict[str, Any]:
        """Get all clients asynchronously."""
        return await self._run_sync(self.bridge.get_clients)

    async def add_client(self, name: str, public_key: str) -> Dict[str, Any]:
        """Add client asynchronously."""
        return await self._run_sync(self.bridge.add_client, name, public_key)

    async def delete_client(self, client_id: str) -> Dict[str, Any]:
        """Delete client asynchronously."""
        return await self._run_sync(self.bridge.delete_client, client_id)

    # File methods
    async def get_files(self, client_id: str = None) -> Dict[str, Any]:
        """Get files asynchronously."""
        return await self._run_sync(self.bridge.get_files, client_id)

    # Settings methods
    async def get_settings(self) -> Dict[str, Any]:
        """Get server settings asynchronously."""
        return await self._run_sync(self.bridge.get_settings)

    async def update_settings(self, settings: dict) -> Dict[str, Any]:
        """Update server settings asynchronously."""
        return await self._run_sync(self.bridge.update_settings, settings)

    # Add more methods as needed...
```

**Then Update Your Views**:

```python
# At top of view file
from FletV2.utils.async_bridge import AsyncServerBridge

# In view creation
def create_database_view(page, bridge):
    # Wrap synchronous bridge with async version
    async_bridge = AsyncServerBridge(bridge)

    async def load_data():
        # Now this is truly async!
        result = await async_bridge.get_database_info()

    # Rest of view code...
```

---

## ✅ Validation Checklist

After applying fixes, verify:

### 1. All Setup Logs Complete

```python
async def setup():
    print("🔴 [SETUP] Starting")
    await load_data_1()
    print("🔴 [SETUP] Data 1 loaded")  # Should print
    await load_data_2()
    print("🔴 [SETUP] Data 2 loaded")  # Should print
    print("🔴 [SETUP] Complete")  # Should print
```

**Expected**: All log messages appear in terminal

### 2. No Gray Screens

- Open each view in browser
- Verify content displays (not gray/empty)
- Check browser DevTools console for errors

### 3. UI Stays Responsive

- Click navigation items
- UI should respond immediately
- No freezing or hanging

### 4. Background Tasks Work

```python
# Test background updates
async def periodic_refresh():
    while True:
        print("🔄 Refreshing...")
        await load_latest_data()
        await asyncio.sleep(30)  # NOT time.sleep()!

page.run_task(periodic_refresh)
```

**Expected**: Logs appear every 30 seconds, UI stays responsive

---

## 🐛 Debugging Remaining Issues

### Issue: Still Getting Gray Screens

**Check**:
1. Did you import asyncio?
   ```python
   import asyncio  # Add at top of file
   ```

2. Are you using `asyncio.sleep()` not `time.sleep()`?
   ```python
   # ❌ WRONG
   await asyncio.sleep(1)  # If you forgot to import asyncio

   # ✅ CORRECT
   import asyncio
   await asyncio.sleep(1)
   ```

3. Are ALL bridge calls wrapped?
   ```bash
   # Find any remaining unwrapped calls
   grep -rn "await bridge\." FletV2/views/ | grep -v "run_in_executor"
   ```

### Issue: RuntimeError: Event loop is closed

**Cause**: Trying to create new event loop

**Fix**: Use existing loop
```python
# ❌ WRONG
loop = asyncio.new_event_loop()

# ✅ CORRECT
loop = asyncio.get_running_loop()
# or
loop = page.loop
```

### Issue: Terminal Shows "asyncio:XXX Task was destroyed but it is pending!"

**Cause**: Background task not properly cancelled

**Fix**: Proper cleanup
```python
class MyView:
    def __init__(self):
        self.background_task = None

    async def start_background_task(self):
        self.background_task = asyncio.create_task(self.periodic_update())

    def cleanup(self):
        if self.background_task and not self.background_task.done():
            self.background_task.cancel()

    async def periodic_update(self):
        try:
            while True:
                await self.load_data()
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            # Task was cancelled, clean exit
            pass
```

---

## 📊 Testing Procedure

### Step-by-Step Testing

1. **Start Fresh**
   ```bash
   # Kill any running instances
   # Start server and GUI clean
   python FletV2/start_with_server.py
   ```

2. **Test Each View**
   - Dashboard → Should load metrics
   - Clients → Should load client list
   - Files → Should load file list
   - Database → Should load table list
   - Settings → Should load settings

3. **Check Terminal Logs**
   - Look for ALL setup completion logs
   - No freeze points
   - No error messages

4. **Verify Interactivity**
   - Click buttons
   - Change tabs
   - Refresh data
   - All should be responsive

5. **Monitor Memory**
   - Open Task Manager / Activity Monitor
   - Check for memory leaks
   - CPU should be low when idle

---

## 🎯 Success Criteria

### Before Fix
- ❌ Gray screens
- ❌ Frozen UI
- ❌ Incomplete setup logs
- ❌ No error messages (just hangs)

### After Fix
- ✅ All views load correctly
- ✅ UI stays responsive
- ✅ All setup logs complete
- ✅ Background tasks work
- ✅ Navigation works smoothly

---

## 📚 Key Takeaways

1. **Never await synchronous methods** - Use `run_in_executor`
2. **Never use time.sleep()** in async code - Use `asyncio.sleep()`
3. **Never call asyncio.run()** inside Flet - The loop is already running
4. **Always add diagnostic logging** - Makes debugging 100x easier
5. **Always call page.update()** - After changing UI state

---

## 🆘 Still Stuck?

### Emergency Diagnostic Script

Create `test_async.py`:

```python
"""Minimal reproduction test for async issues."""

import flet as ft
import asyncio


def create_sync_function():
    """Simulates your synchronous ServerBridge method."""
    import time
    time.sleep(0.5)  # Simulate database query
    return {"success": True, "data": "Test data"}


async def main(page: ft.Page):
    page.title = "Async Test"

    status = ft.Text("Status: Not started")
    page.add(status)

    async def test_wrong_pattern(e):
        """This will freeze if create_sync_function isn't async."""
        status.value = "Status: Testing WRONG pattern..."
        status.color = "red"
        page.update()

        try:
            # ❌ This will freeze!
            # result = await create_sync_function()  # Uncomment to see freeze

            status.value = "Status: Would freeze here!"
            page.update()
        except Exception as ex:
            status.value = f"Status: Error - {ex}"
            page.update()

    async def test_correct_pattern(e):
        """This works correctly."""
        status.value = "Status: Testing CORRECT pattern..."
        status.color = "blue"
        page.update()

        try:
            # ✅ This works!
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, create_sync_function)

            status.value = f"Status: Success! {result}"
            status.color = "green"
            page.update()
        except Exception as ex:
            status.value = f"Status: Error - {ex}"
            status.color = "red"
            page.update()

    page.add(
        ft.Row([
            ft.ElevatedButton("Test WRONG Pattern", on_click=test_wrong_pattern),
            ft.ElevatedButton("Test CORRECT Pattern", on_click=test_correct_pattern),
        ])
    )


if __name__ == "__main__":
    ft.app(target=main)
```

**Run**: `python test_async.py`

**Expected**:
- "Test CORRECT Pattern" button works → Shows "Success!"
- "Test WRONG Pattern" button (if uncommented) → Freezes gray screen

If the CORRECT pattern works in this test but not in your app, the issue is elsewhere (likely in data processing, not async boundary).

---

## 📞 Get Help

If you're still experiencing issues after applying these fixes:

1. **Check the main guide**: `FLET_INTEGRATION_GUIDE.md` (comprehensive patterns)
2. **Enable debug mode**: Add `asyncio.get_running_loop().set_debug(True)` at app start
3. **Add extensive logging**: Before/after every async operation
4. **Isolate the issue**: Test each view individually
5. **Check Flet version**: Ensure you're on 0.28.3 (`pip show flet`)

---

**Remember**: 99% of Flet freezes are from awaiting non-async methods. Fix that, and you fix everything.

Good luck! 🚀
