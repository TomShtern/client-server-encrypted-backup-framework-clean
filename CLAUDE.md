# CLAUDE.md - FletV2 Development Guide

**CRITICAL CONTEXT**: Expert Flet 0.28.3 + Python 3.13.5 engineer working exclusively with `FletV2/` directory. The `flet_server_gui/` is obsolete reference.

**SYSTEM**: 5-layer encrypted backup framework with production-grade desktop GUI management interface.

---

## 🎯 STRATEGIC CODE GENERATION DIRECTIVES

### **Immediate Decision Framework**
Before writing ANY code, apply this hierarchy:

1. **Framework First**: Does Flet 0.28.3 provide this natively? Use built-in solution.
2. **Scale Check**: Will custom solution exceed 500 lines? Find simpler approach.
3. **Performance Priority**: Use `control.update()` over `page.update()` (10x performance gain).
4. **Error Prevention**: Import `Shared.utils.utf8_solution` for subprocess/console operations.

### **High-Level Architecture Principles**

```python
# ✅ CORRECT PATTERN: Single ft.Row with NavigationRail + dynamic content
class FletV2App(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.expand = True
        self.controls = [nav_rail, ft.VerticalDivider(width=1), content_area]
```

### **Low-Level Implementation Rules**

1. **View Creation**: Always return `ft.Control` from pure functions
2. **State Management**: Use structured returns `{'success': bool, 'error': str, 'data': any}`
3. **Async Operations**: Prefer `page.run_task()` over custom threading
4. **Error Handling**: All operations must handle success/failure gracefully
5. **Refs for Updates**: Use `ft.Ref[ControlType]()` for precise UI updates

---

## ⚡ FRAMEWORK HARMONY ENFORCEMENT

### **The Flet Way vs Framework Fighting**

| ✅ FRAMEWORK HARMONY                | ❌ FRAMEWORK FIGHTING         |
|------------------------------------|---------------------------------|
| `ft.NavigationRail.on_change`      | Custom routing classes          |
| `ft.ResponsiveRow` + `expand=True` | Custom responsive systems       |
| `page.theme = ft.Theme()`          | Custom theme managers >50 lines |
| `ft.DataTable`                     | Custom table components         |
| `control.update()`                 | `page.update()` abuse           |

### **Critical API Verification (Flet 0.28.3)**

```python
# ✅ VERIFIED WORKING:
ft.Colors.PRIMARY, ft.Icons.DASHBOARD, ft.ResponsiveRow, ft.NavigationRail
ft.Theme, ft.ColorScheme, ft.ThemeMode.SYSTEM, ft.SafeArea

# ❌ RUNTIME ERRORS:
ft.MaterialState.DEFAULT, ft.Expanded(), ft.Colors.SURFACE_VARIANT, ft.UserControl
```

flet 0.28.3 is the ONLY supported version. Always verify APIs against official docs.
flet_server_gui/ is obsolete. Use FletV2/ exclusively.
flet issues are common; always check context7 for workarounds, and proper usage.
flet common issues: Flet uses Icons (capitalized) not icons (lowercase).
---

## 🏗️ ARCHITECTURE BLUEPRINT

### **Project Structure (FletV2/)**
```
├── main.py                    # Desktop app entry point (~900 lines max)
├── theme.py                   # Material 3 theme system
├── config.py                  # Configuration constants
├── views/                     # Function-based view modules (~400 lines each)
│   ├── dashboard.py, clients.py, files.py, database.py
│   ├── analytics.py, logs.py, settings.py
└── utils/                     # Infrastructure modules
    ├── server_bridge.py       # Server integration with fallbacks
    ├── state_manager.py       # Reactive state with subscriptions
    ├── user_feedback.py       # Unified success/error messaging
    └── [18 other specialized utilities]
```

### **Server Bridge Pattern (Production-Grade)**

```python
class ServerBridge:
    def __init__(self, real_server_instance=None):
        self.real_server = real_server_instance

    def get_clients(self):
        if self.real_server:
            return self.real_server.get_clients()  # Direct call
        return MockDataGenerator.generate_clients()  # Fallback

# Usage: Development: bridge = create_server_bridge()
#        Production: bridge = create_server_bridge(BackupServer())
```

---

## 🎨 ESSENTIAL PATTERNS & TEMPLATES

### **Complete View Template with All Features**

```python
def create_view_name(server_bridge, page: ft.Page, state_manager=None):
    import Shared.utils.utf8_solution  # UTF-8 support
    from utils.user_feedback import show_success_message, show_error_message

    # Refs for precise updates (10x performance)
    loading_ref = ft.Ref[ft.ProgressRing]()
    table_ref = ft.Ref[ft.DataTable]()
    status_ref = ft.Ref[ft.Text]()

    # Data loading with fallback
    def get_data():
        if server_bridge:
            try:
                return server_bridge.get_data()
            except Exception:
                pass
        return {"fallback": "data"}

    # Complete async handler with error handling & loading states
    async def on_action(e):
        loading_ref.current.visible = True
        loading_ref.current.update()
        try:
            result = await state_manager.server_mediated_update(
                key="action_key", value={"data": "value"},
                server_operation="server_method", param1, param2
            )
            if result.get('success'):
                show_success_message(page, "Operation completed")
                await refresh_data()
            else:
                show_error_message(page, f"Failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            show_error_message(page, f"Error: {str(e)}")
        finally:
            loading_ref.current.visible = False
            loading_ref.current.update()

    # Data table with action buttons
    def create_action_buttons(item_id):
        return ft.Row([
            ft.IconButton(ft.Icons.EDIT, on_click=lambda e: edit_item(item_id)),
            ft.IconButton(ft.Icons.DELETE, on_click=lambda e: delete_item(item_id))
        ], spacing=5)

    data_table = ft.DataTable(
        ref=table_ref,
        columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Status")), ft.DataColumn(ft.Text("Actions"))],
        rows=[ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(item.get('id', '')))),
            ft.DataCell(ft.Text(str(item.get('status', '')))),
            ft.DataCell(create_action_buttons(item.get('id')))
        ]) for item in get_data()]
    )

    # State manager subscription for reactive updates
    def update_table(new_data):
        if table_ref.current:
            table_ref.current.rows = [/* updated rows */]
            table_ref.current.update()

    state_manager.subscribe("data_key", update_table)

    # Complete responsive UI with all elements
    return ft.Column([
        # Header with status
        ft.Row([
            ft.Text("View Title", size=28, weight=ft.FontWeight.BOLD),
            ft.ProgressRing(ref=loading_ref, visible=False, width=20, height=20),
            ft.Text("Ready", ref=status_ref, size=12)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        # Responsive content
        ft.ResponsiveRow([
            ft.Column([data_table], col={"sm": 12, "md": 8}),
            ft.Column([
                ft.FilledButton("Primary Action", on_click=on_action),
                ft.OutlinedButton("Secondary Action")
            ], col={"sm": 12, "md": 4})
        ]),
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=20)
```

### **Enhanced State Manager with Server Operations**

```python
async def server_mediated_update(self, key: str, value: Any, server_operation: str = None, *args, **kwargs):
    if not server_operation or not self.server_bridge:
        await self.update_async(key, value, source="direct")
        return {'success': True, 'mode': 'direct'}

    server_method = getattr(self.server_bridge, server_operation, None)
    if not server_method:
        await self.update_async(key, value, source="server_fallback")
        return {'success': False, 'error': f'method {server_operation} not found'}

    try:
        result = await server_method(*args, **kwargs) if asyncio.iscoroutinefunction(server_method) else server_method(*args, **kwargs)
        if not isinstance(result, dict):
            result = {'success': bool(result), 'data': result}
        if result.get('success'):
            await self.update_async(key, result.get('data', value))
        return result
    except Exception as e:
        await self.update_async(key, value, source="server_error")
        return {'success': False, 'error': str(e)}
```

---

## 🎯 DEVELOPMENT WORKFLOW

### **Essential Configuration**
```python
import Shared.utils.utf8_solution  # ALWAYS for subprocess/console I/O
from utils.server_bridge import create_server_bridge
from utils.state_manager import create_state_manager
from utils.user_feedback import show_success_message, show_error_message
```

### **Launch Commands & Code Quality**
```bash
# Development: cd FletV2 && flet run -r main.py
# Production: cd FletV2 && python main.py
```

**Code Quality Checklist:**
- [ ] Flet built-in solution used? [ ] File <500 lines? [ ] `control.update()` vs `page.update()`?
- [ ] Async patterns for long operations? [ ] Error handling with user feedback? [ ] UTF-8 import for subprocess?

---

## 🚨 ANTI-PATTERNS & ERROR PREVENTION

### **Immediate Red Flags**
1. **Custom Navigation Systems** → Use `ft.NavigationRail.on_change`
2. **God Components >500 lines** → Decompose into focused functions
3. **`page.update()` overuse** → Use `control.update()` for precision
4. **Missing UTF-8 imports** → Always import `Shared.utils.utf8_solution` for subprocess operations
5. **Unsafe result handling** → Use `.get()` patterns for structured returns

### **Common Error Patterns & 5-Second Fixes**

| **Error Pattern** | **Instant Fix** |
|------------------|-----------------|
| `AttributeError: 'NoneType' object has no attribute 'update'` | Add `if ref.current:` check |
| `RuntimeError: asyncio.run() cannot be called from a running event loop` | Use `page.run_task()` instead |
| `UnicodeDecodeError` in subprocess | Import `Shared.utils.utf8_solution` |
| UI not updating after data change | Use `control.update()` on specific ref |
| Changes not reflecting in development | Restart with `flet run -r main.py` |

---

## 🚀 PRODUCTIVITY ACCELERATORS

### **Performance Profiling & Debugging**

```python
# Instant performance monitoring decorator
def profile_operation(operation_name):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start
                print(f"{'⚠️ SLOW' if elapsed > 0.1 else '✅ FAST'}: {operation_name} took {elapsed:.3f}s")
                return result
            except Exception as e:
                print(f"❌ ERROR: {operation_name} failed after {time.time() - start:.3f}s: {e}")
                raise
        return wrapper
    return decorator

# State debugging (add to state manager)
def debug_state(self, key=None):
    if key:
        value = self.state.get(key, "NOT_FOUND")
        print(f"🔍 STATE[{key}] = {value}")
    else:
        print("🔍 FULL STATE:")
        for k, v in self.state.items():
            print(f"    {k}: {type(v).__name__} = {str(v)[:100]}")
```

### **Memory Management & Resource Cleanup**

```python
# Cleanup pattern for long-running apps
class ViewManager:
    def __init__(self):
        self.active_subscriptions = []
        self.background_tasks = set()

    def add_subscription(self, key, callback):
        self.active_subscriptions.append((key, callback))
        state_manager.subscribe(key, callback)

    def cleanup(self):
        for key, callback in self.active_subscriptions:
            state_manager.unsubscribe(key, callback)
        self.active_subscriptions.clear()
        for task in self.background_tasks:
            if not task.done():
                task.cancel()

# Weak reference pattern for memory leak prevention
import weakref
def create_safe_handler(page_ref, control_ref):
    def handler(e):
        page, control = page_ref(), control_ref()
        if page and control:
            control.update()
    return handler
```

### **Production Setup**

```python
# Environment detection & configuration
class Config:
    IS_DEVELOPMENT = os.getenv("FLET_ENV", "development") == "development"
    IS_PRODUCTION = not IS_DEVELOPMENT

# Production logging
def setup_production_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()]
    )
    return logging.getLogger("FletV2")

# Hot reload optimization for development
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        ft.run(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
    else:
        ft.run(target=main, view=ft.AppView.FLET_APP)
```

---

## 📋 QUICK REFERENCE

### **Theme & Error Handling**
```python
# Theme setup
page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN, use_material3=True)
page.theme_mode = ft.ThemeMode.SYSTEM

# Standard error handling pattern
try:
    result = await operation()
    if result.get('success'):
        show_success_message(page, "Success")
    else:
        show_error_message(page, f"Failed: {result.get('error')}")
except Exception as e:
    show_error_message(page, f"Error: {str(e)}")
```

### **Performance Benchmarks**
- **UI Update**: <16ms (60fps) | **Data Loading**: <200ms for <1000 items | **Memory**: <100MB | **Startup**: <2s

---

## 💡 STRATEGIC INSIGHTS

**★ Framework Enlightenment**: Modern desktop applications achieve sophisticated UI in ~900 lines of clean Flet code vs 10,000+ lines of framework-fighting complexity.

**★ Performance Multiplier**: `control.update()` vs `page.update()` = 10x+ performance improvement with zero UI flicker.

**★ Production Readiness**: Direct server integration enables zero-configuration dev-to-production transition.

**★ Error Resilience**: Structured returns with `.get()` patterns eliminate AttributeError crashes.

---

**STATUS**: Production-Ready Desktop Application with Bulletproof CRUD Infrastructure

**CORE PHILOSOPHY**: "Let Flet do the heavy lifting. Your job is to compose, not reinvent."