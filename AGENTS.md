# Client-Server Encrypted Backup Framework - AGENTS Documentation

## Build & Test Commands

### C++ Client (Windows)
```bash
.\build.bat                    # Release build
.\build.bat debug             # Debug build
.\build.bat clean             # Clean rebuild
.\build.bat ninja             # Fast Ninja release
cmake --preset release        # Configure release
cmake --build --preset release # Build release
```

### Python System
```bash
python scripts/one_click_build_and_run.py  # Full system launch
cd FletV2 && ../flet_venv/Scripts/python start_with_server.py  # Flet GUI + Server
python api_server/cyberbackup_api_server.py  # API Server only
python FletV2/main.py         # FletV2 desktop app
```

### Lint & Test
```bash
ruff check FletV2 Shared python_server api_server  # Lint
ruff format FletV2 Shared python_server api_server  # Format
pyright                                              # Type check (basic mode)
pytest tests/test_protocol.py -v                    # Single test file
pytest tests/ -k test_method -v                    # Single test across files
pytest tests/test_protocol.py::TestClass::test_method -v  # Specific test
pytest tests/                                        # All tests
```

## Code Style Guidelines

### Python Standards
- **Line length**: 110 chars (ruff config)
- **Import order**: stdlib > 3rd-party > local (isort, enforced by ruff)
- **Type hints**: All public functions (pyright basic mode)
- **Naming**: snake_case for vars/fns, PascalCase for classes
- **Quotes**: Double quotes for strings (ruff format)
- **Logging**: Use `logger` everywhere, NEVER `print()`

### Error Handling & API Contracts
- **Return format**: `{"success": bool, "data": Any, "error": str|None}`
- **ServerBridge**: All methods return normalized dict, never raw exceptions
- **Validation**: Check inputs before processing, prevent path traversal
- **Exceptions**: Catch and normalize to error dicts, never let them escape

### Critical Non-Negotiable Patterns

#### 1. UTF-8 Bootstrap (First Import)
```python
# Entry-point files MUST start with this:
from Shared.filesystem.utf8_solution import configure_utf8
configure_utf8()
# Then all other imports...
```

#### 2. Async/Sync Boundary (GUI Freezes)
```python
from FletV2.utils.async_helpers import run_sync_in_executor

# WRONG - Freezes UI
async def load_data():
    result = server_bridge.get_clients()  # Blocks!

# CORRECT - Non-blocking
async def load_data():
    result = await run_sync_in_executor(server_bridge.get_clients)
```

#### 3. Database Access
```python
# ALWAYS use context managers
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    # Auto-closes on exit
```

#### 4. Timing
```python
start = time.monotonic()  # ✅ Immune to clock changes
# NEVER use time.time() - can go negative!
```

#### 5. Flet UI Updates
```python
control.update()  # ✅ Targeted (fastest, ~1ms)
container.controls.append(item); container.update()  # ✅ Container
page.update()  # ⚠️ Only for themes/dialogs/overlays (slowest, 16ms+)

# ❌ NEVER - Loop with page.update()
for item in items:
    container.controls.append(item)
    page.update()  # DON'T!
```

#### 6. C++ Subprocess
```python
subprocess.Popen(["EncryptedBackupClient.exe", "--batch"], cwd=...)
```

#### 7. View Lifecycle (FletV2)
```python
def create_my_view(server_bridge, page, state_manager=None):
    """Returns (content, dispose_fn, setup_fn)"""
    # 1. State/Refs
    # 2. Data fetching (async with executor)
    # 3. Event handlers
    # 4. dispose_fn() - cleanup subscriptions/overlays
    # 5. setup_fn() - runs AFTER view attached to page
    return content, dispose_fn, setup_fn
```

#### 8. ServerBridge Response Handling
```python
result = await run_sync_in_executor(server_bridge.get_clients)
if result['success']:
    clients = result['data']
    render(clients)
else:
    show_error(result['error'])
```

### File Structure & Size Limits
- **Max file**: 500 lines (views: 1000 max)
- **Max function**: 100 lines
- **Views**: Follow 5-section pattern (see copilot-instructions.md for full template)

### Security Requirements
- **Encryption**: AES-256-CBC (zero IV)
- **Key Exchange**: RSA-1024 OAEP
- **Integrity**: CRC32 on entire frame
- **Validation**: No path traversal, sanitize all inputs

### Theme & UI
- **Colors**: Use `TOKENS['primary']` from theme, NEVER hardcoded colors
- **Components**: Use `themed_card`, `themed_button` from `ui_components.py`
- **Navigation**: Only `ft.NavigationRail.on_change` → `_load_view()`
- **Material Design 3**: Flet 0.28.3 limitations (no `ft.Positioned`, etc.)

### Mock Mode Detection
```python
if server_bridge.is_real():
    # Connected to BackupServer - operations persist
else:
    # Mock mode - returns empty structures, NO persistence
    logger.warning("Running in mock mode")
```

## Pre-Commit Checklist
- [ ] UTF-8 configure_utf8() at top of entry points
- [ ] All sync ServerBridge calls wrapped in run_sync_in_executor
- [ ] Database connections use context managers
- [ ] Durations use time.monotonic() only
- [ ] UI updates use control.update(), avoid page.update() in loops
- [ ] No print() calls - use logger
- [ ] Files under 500 lines (1000 for views)
- [ ] Type hints on public functions
- [ ] Return format {"success": bool, "data": ..., "error": ...}
- [ ] Run ruff check/format and pyright