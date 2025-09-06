# CLAUDE.md - FletV2 Development Guide
This file provides Claude and Claude Code comprehensive guidance for working with FletV2 - a clean, framework-harmonious Flet desktop application that demonstrates proper Flet patterns and best practices.
Claude and Claude Code will adhere and reference this file for all FletV2-related development tasks.

**CRITICAL**: We work exclusively with `FletV2/` directory. The `flet_server_gui/` is obsolete, over-engineered, and kept only as reference of what NOT to do.
 you should reference the `important_docs/` folder for component usage examples and documentation.
---

## ⚙️ Essential Configuration

### UTF-8 Support
```python
# ALWAYS import this in any Python file that deals with subprocess or console I/O
import Shared.utils.utf8_solution
```

## 🎯 CORE PRINCIPLES: Framework Harmony

### **The FletV2 Way - Work WITH Flet, Not Against It**

**Primary Directive**: Favor Flet's built-in features over custom, over-engineered solutions. Do not reinvent the wheel.

#### **Scale Test**: 
Be highly suspicious of any custom solution that exceeds 1000 lines. A 3000+ line custom system is an anti-pattern when a 50-250 line native Flet solution exists with full feature parity(or almost full parity).

#### **Framework Fight Test**: 
Work WITH the framework, not AGAINST it. If your solution feels complex, verbose, or like a struggle, you are fighting the framework. Stop and find the simpler, intended Flet way.

#### **Built-in Checklist**:
- Can `ft.NavigationRail` handle navigation?
- Can `expand=True` and `ResponsiveRow` solve layout?
- Can `control.update()` replace `page.update()`?
- Does a standard Flet control already do 90% of what you need?

---

## ⚡ POWER DIRECTIVES: Maximum Impact Code Generation

### **Critical Framework Compliance (Flet 0.28.3 + Python 3.13.5)**

1. **Always use `control.update()` instead of `page.update()` to achieve 10x performance and eliminate UI flicker.**

2. **Leverage `ft.ResponsiveRow` and `expand=True` as your primary layout mechanism, eliminating the need for complex custom responsive systems.**

3. **Use `ft.NavigationRail.on_change` for navigation, completely removing the need for custom routing managers.**

4. **Prefer `ft.Theme` and `ft.ColorScheme` for styling, avoiding any custom theming logic over 50 lines.**

5. **Implement async event handlers using `async def` and `await ft.update_async()` to prevent UI blocking.**

6. **Use `page.run_task()` for background operations instead of creating custom threading or async management.**

7. **Always provide a fallback in server bridge initialization to ensure graceful degradation.**

8. **Utilize Flet's built-in `ThemeMode` for theme switching instead of creating custom theme toggle mechanisms.**

9. **Replace custom icon management with Flet's native `ft.Icons` enum, which provides comprehensive icon support.**

10. **Design views as pure function-based components that return `ft.Control`, avoiding complex class-based view systems.**

### **Performance & Anti-Pattern Guards**

11. **If your custom solution exceeds 1000 lines, you are fighting the framework - stop and find the Flet-native approach.**

12. **Prefer semantic color tokens like `ft.Colors.PRIMARY` over hardcoded hex values to ensure theme compatibility.**

13. **Use `ft.DataTable` for tabular data instead of building custom table components from scratch.**

14. **Implement error handling using `page.snack_bar` with built-in Flet colors for consistent user feedback.**

15. **Leverage `ft.TextTheme` for consistent typography across your entire application.**

### **Architectural Enforcement**

16. **Structure your desktop app as a single `ft.Row` with a `NavigationRail` and dynamic content area.**

17. **Create a modular `theme.py` as the single source of truth for all styling and theming logic.**

18. **Use `page.run_thread()` for operations that might block, ensuring responsive UI.**

19. **Design components with a maximum of ~400 lines(you dont have to, but its recommended estimates), forcing modularity and readability.**

20. **Always provide a simple, function-based fallback for every dynamic loading mechanism.**

### **Python 3.13.5 & Flet 0.28.3 Optimizations**

21. **Use `page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)` for instant Material 3 theming without custom color management.**

22. **Leverage `page.adaptive = True` for platform-specific UI rendering when targeting multiple platforms.**

23. **Use `ft.run(main, view=ft.AppView.WEB_BROWSER)` for development hot reload - identical runtime to desktop with instant updates.**

24. **Implement `page.theme_mode = ft.ThemeMode.SYSTEM` to automatically respect user system preferences.**

25. **Use `ft.SafeArea` to handle platform-specific UI constraints automatically.**

**Core Philosophy**: "Let Flet do the heavy lifting. Your job is to compose, not reinvent."

---

## 🏗️ FletV2 ARCHITECTURE PATTERNS

### **Main Application Structure (CANONICAL)**

```python
# FletV2/main.py - The correct desktop app pattern
class FletV2App(ft.Row):
    """Clean desktop app using pure Flet patterns."""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        
        # ✅ Simple window configuration
        page.window_min_width = 1024
        page.window_min_height = 768
        page.window_resizable = True
        page.title = "Backup Server Management"
        
        # ✅ Use theme.py (source of truth)
        from theme import setup_default_theme
        setup_default_theme(page)
        
        # ✅ Simple NavigationRail (no custom managers)
        self.nav_rail = ft.NavigationRail(
            destinations=[...],
            on_change=self._on_navigation_change  # Simple callback
        )
        
        # ✅ Auto-resizing content area
        self.content_area = ft.Container(expand=True)
        
        # ✅ Pure Flet layout
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1),
            self.content_area
        ]
    
    def _on_navigation_change(self, e):
        """Simple navigation - no complex routing."""
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        selected_view = view_names[e.control.selected_index]
        self._load_view(selected_view)
    
    def _load_view(self, view_name: str):
        """Load view using simple function calls."""
        if view_name == "dashboard":
            from views.dashboard import create_dashboard_view
            content = create_dashboard_view(self.server_bridge, self.page)
        # ... other views
        
        self.content_area.content = content
        self.content_area.update()  # Precise update, not page.update()
```

### **View Creation Pattern (MANDATORY)**

```python
# views/dashboard.py - Correct view pattern
def create_dashboard_view(server_bridge, page: ft.Page) -> ft.Control:
    """Create dashboard view using pure Flet patterns."""
    
    # ✅ Simple data loading with fallback
    def get_server_status():
        if server_bridge:
            try:
                return server_bridge.get_server_status()
            except Exception as e:
                logger.warning(f"Server bridge failed: {e}")
        return {"server_running": True, "clients": 3, "files": 72}  # Mock fallback
    
    # ✅ Event handlers using closures
    def on_start_server(e):
        logger.info("Start server clicked")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Server start command sent"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()  # Only for snack_bar
    
    # ✅ Return pure Flet components
    return ft.Column([
        ft.Text("Server Dashboard", size=24, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([
            ft.Column([
                ft.Card(content=ft.Text(f"Active Clients: {status['clients']}"))
            ], col={"sm": 6, "md": 3})
            # ... more cards
        ]),
        ft.FilledButton("Start Server", on_click=on_start_server, icon=ft.Icons.PLAY_ARROW)
    ], expand=True, scroll=ft.ScrollMode.AUTO)
```

### **Theme System (SOURCE OF TRUTH)**

```python
# theme.py - Proper Flet theming
def setup_default_theme(page: ft.Page) -> None:
    """Set up theme using Flet's native system."""
    # ✅ Use Flet's built-in theme system
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#38A298",
            secondary="#7C5CD9",
            surface="#F0F4F8",
            background="#F8F9FA"
        ),
        font_family="Inter"
    )
    
    # ✅ Dark theme support
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#82D9CF",
            secondary="#D0BCFF",
            surface="#1A2228",
            background="#12181C"
        ),
        font_family="Inter"
    )
    
    page.theme_mode = ft.ThemeMode.SYSTEM

def toggle_theme_mode(page: ft.Page) -> None:
    """Toggle theme mode using Flet built-ins."""
    page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
    page.update()
```

---

## ❌ FRAMEWORK-FIGHTING ANTI-PATTERNS (NEVER DO THESE)

### **🚨 IMMEDIATE RED FLAGS**
1. **Custom NavigationManager classes** → Use `ft.NavigationRail.on_change`
2. **Custom responsive systems** → Use `expand=True` + `ResponsiveRow`
3. **Custom theme managers** → Use `page.theme` and `theme.py`
4. **Complex routing systems** → Use simple view switching
5. **`page.update()` abuse** → Use `control.update()` for precision
6. **God components >500 lines** → Decompose into focused functions

### **🚨 INVALID FLET APIS (RUNTIME ERRORS)**
```python
# ❌ WRONG - These don't exist in Flet 0.28.3:
ft.MaterialState.DEFAULT    # ❌ MaterialState doesn't exist
ft.Expanded()              # ❌ Use expand=True instead
ft.Colors.SURFACE_VARIANT  # ❌ Use ft.Colors.SURFACE instead
ft.UserControl             # ❌ Inherit from ft.Control instead

# ✅ CORRECT - Verified working APIs:
ft.Colors.PRIMARY, ft.Colors.SURFACE, ft.Colors.ERROR
ft.Icons.DASHBOARD, ft.Icons.SETTINGS, ft.Icons.PLAY_ARROW
ft.ResponsiveRow, ft.NavigationRail, ft.Card
```

---

## ✅ CORRECT FLET PATTERNS (ALWAYS USE THESE)

### **Data Display Patterns**

```python
# ✅ For tabular data: ft.DataTable
clients_table = ft.DataTable(
    columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Status"))],
    rows=[
        ft.DataRow(cells=[
            ft.DataCell(ft.Text(client["id"])),
            ft.DataCell(ft.Text(client["status"], color=ft.Colors.GREEN))
        ]) for client in clients_data
    ],
    border=ft.border.all(1, ft.Colors.OUTLINE)
)

# ✅ For metrics: ft.LineChart
cpu_chart = ft.LineChart(
    data_series=[
        ft.LineChartData(
            data_points=[ft.LineChartDataPoint(x, cpu_values[x]) for x in range(len(cpu_values))],
            color=ft.Colors.BLUE,
            curved=True
        )
    ],
    expand=True
)

# ✅ For responsive layouts: ft.ResponsiveRow
metrics_cards = ft.ResponsiveRow([
    ft.Column([
        ft.Card(content=ft.Text(f"CPU: {cpu}%"))
    ], col={"sm": 12, "md": 6, "lg": 3})
    for cpu in cpu_values
])
```

### **Form/Settings Patterns**

```python
# ✅ Use ft.Tabs for categories
settings_tabs = ft.Tabs([
    ft.Tab(text="Server", icon=ft.Icons.SETTINGS, content=server_form),
    ft.Tab(text="Theme", icon=ft.Icons.PALETTE, content=theme_form)
], expand=True)

# ✅ Built-in form controls with validation
username_field = ft.TextField(
    label="Username",
    on_change=lambda e: validate_field(e)
)

def validate_field(e):
    if len(e.control.value) < 3:
        e.control.error_text = "Too short"
    else:
        e.control.error_text = None
    e.control.update()  # Precise update
```

### **Async Patterns (CRITICAL)**

```python
# ✅ CORRECT: Async event handlers
async def on_fetch_data(e):
    # Show progress immediately
    progress_ring.visible = True
    await progress_ring.update_async()
    
    # Background operation
    data = await fetch_data_async()
    
    # Update UI
    results_text.value = data
    progress_ring.visible = False
    await ft.update_async(results_text, progress_ring)  # Batch update

# ✅ Background tasks
page.run_task(monitor_server_async)

# ❌ WRONG: Blocking operations
def on_fetch_data_blocking(e):
    data = requests.get(url)  # ❌ Blocks UI
    self.page.update()       # ❌ Full page refresh
```

---

## 🚀 PERFORMANCE & BEST PRACTICES

### **File Size Standards (ENFORCE STRICTLY)**
- **View files**: 200-500 lines maximum
- **Component files**: 100-400 lines maximum  
- **If >600 lines**: MANDATORY refactoring required(probably, not always)
- **Single responsibility**: Each file has ONE clear purpose

### **UI Update Performance**

```python
# ✅ CORRECT: Precise updates (10x performance improvement)
def update_status(status_control, new_status):
    status_control.value = new_status
    status_control.update()  # Only this control

# ✅ For multiple controls: Batch updates
await ft.update_async(control1, control2, control3)

# ❌ WRONG: Full page updates (performance killer)
def update_status_wrong(self):
    self.status.value = "New status"
    self.page.update()  # Updates entire page!
```

### **Layout Best Practices**

```python
# ✅ CORRECT: Responsive, flexible layouts
ft.ResponsiveRow([
    ft.Column([
        ft.Card(content=dashboard_content, expand=True)
    ], col={"sm": 12, "md": 8}, expand=True),
    
    ft.Column([
        ft.Card(content=sidebar_content)
    ], col={"sm": 12, "md": 4})
])

# ❌ WRONG: Fixed dimensions (breaks on resize)
ft.Container(width=800, height=600, content=dashboard_content)

# ✅ CORRECT: Auto-scaling
ft.Container(content=dashboard_content, expand=True, padding=20)
```

---

## 🛠️ DEVELOPMENT WORKFLOW

### **Terminal Debugging Setup (PRODUCTION READY)**

```python
# STEP 1: Import at top of main.py (before other imports)
from utils.debug_setup import setup_terminal_debugging, get_logger
logger = setup_terminal_debugging(logger_name="FletV2.main")

# STEP 2: Use throughout your application
def create_dashboard_view(server_bridge, page: ft.Page) -> ft.Control:
    logger.info("Creating dashboard view")
    
    def on_button_click(e):
        logger.debug("Button clicked")
        try:
            result = some_operation()
            logger.info(f"Operation successful: {result}")
        except Exception as ex:
            logger.error(f"Operation failed: {ex}", exc_info=True)
```

### **Error Handling & User Feedback**

```python
# ✅ CORRECT: Centralized user feedback
def show_user_message(page, message, is_error=False):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.ERROR if is_error else ft.Colors.GREEN
    )
    page.snack_bar.open = True
    page.update()

def safe_operation(page):
    try:
        result = complex_operation()
        logger.info(f"Operation completed: {result}")
        show_user_message(page, "Operation completed successfully!")
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        show_user_message(page, f"Failed: {str(e)}", is_error=True)
```

### **Server Bridge Pattern (Robust Fallback)**

```python
# ✅ CORRECT: Automatic fallback system
try:
    from utils.server_bridge import ModularServerBridge as ServerBridge
    BRIDGE_TYPE = "Full Server Bridge"
except Exception as e:
    logger.warning(f"Full bridge failed: {e}")
    from utils.simple_server_bridge import SimpleServerBridge as ServerBridge
    BRIDGE_TYPE = "Simple Bridge (Fallback)"

# This ensures GUI always works even if full server unavailable
```

---

## 📋 CODE QUALITY CHECKLIST

### **Before Writing ANY Code**
- [ ] Does Flet provide this functionality built-in?
- [ ] Am I duplicating existing functionality?
- [ ] Will this file exceed 600 lines? (If yes, decompose first)
- [ ] Am I using hardcoded dimensions instead of `expand=True`?
- [ ] Am I using `page.update()` when `control.update()` would work?

### **Validation Checklist for New Code**
- [ ] **Framework harmony**: Uses Flet built-ins, not custom replacements
- [ ] **Single responsibility**: File has ONE clear purpose
- [ ] **No hardcoded dimensions**: Uses `expand=True`, responsive patterns
- [ ] **Async operations**: Long operations use async patterns
- [ ] **Error handling**: Proper user feedback for failures
- [ ] **Terminal debugging**: Uses logger instead of print()
- [ ] **Accessibility**: Includes tooltip, semantics_label where appropriate

### **The Ultimate Quality Test**
Before committing ANY code, ask:
1. "Does Flet already provide this functionality?"
2. "Can a new developer understand this file's purpose in <2 minutes?"
3. "Am I working WITH Flet patterns or fighting them?"

If any answer is unclear, STOP and refactor.

---

## 🎯 PROJECT CONTEXT

### **Current Architecture Status**
- **✅ FletV2/**: Clean, framework-harmonious implementation (USE THIS)
- **❌ flet_server_gui/**: Obsolete, over-engineered (REFERENCE ONLY)
- **System**: 5-layer encrypted backup framework with GUI management:
    - Client: cpp
    - API Server: python api server for the client web-gui
    - Client gui: javascript, tailwindcss web-gui
    - Server: python
    - server GUI: FletV2 desktop/laptop(NOT mobile/tablet/web) app for management
    - database: SQLite3
    - Bridge: ServerBridge for communication
    - Utils: Shared utilities

### **Key FletV2 Files**
```
FletV2/
├── main.py                    # Clean desktop app (~300 lines)
├── theme.py                   # Source of truth for theming
├── views/                     # Simple view functions (<400 lines each)
│   ├── dashboard.py          # Server dashboard
│   ├── clients.py            # Client management
│   ├── files.py              # File browser
│   ├── database.py           # Database viewer
│   ├── analytics.py          # Analytics charts
│   ├── logs.py               # Log viewer
│   └── settings.py           # Configuration
└── utils/                     # Helper utilities
    ├── debug_setup.py        # Terminal debugging
    ├── server_bridge.py      # Full server integration
    └── simple_server_bridge.py # Fallback bridge
```

### **Launch Commands**
```bash
# FletV2 Desktop (Production/Testing)
cd FletV2 && python main.py

# FletV2 Development with Hot Reload (RECOMMENDED for development)
# Uses desktop for instant hot reload - identical runtime to desktop
cd FletV2
flet run -r main.py

# Alternative: Command-line hot reload
cd FletV2 && flet run --web main.py

# System integration testing (only after FletV2 is complete, and the user approved)
python scripts/one_click_build_and_run.py
```

### **Development Workflow (Desktop Apps)**
  ★ Insight ─────────────────────────────────────
  Hot Reload Validation: The WEB_BROWSER view for desktop development is a Flet best practice - it provides identical runtime behavior to native desktop while enabling instant hot reload. The workflow is: develop in browser → test in native desktop → deploy as desktop app.
  ─────────────────────────────────────────────────
**Recommended Pattern**: Develop in browser → Test in native desktop → Deploy as desktop app
- **Browser development**: Instant hot reload, identical Flet runtime, browser dev tools available
- **Native testing**: Final validation of desktop-specific features, window management, OS integration
- **Both modes**: Run the exact same Flet application code - no differences in functionality

---

## 🔧 SEARCH & DEVELOPMENT TOOLS

You have access to ast-grep for syntax-aware searching:
- **Structural matching**: `ast-grep --lang python -p 'class $NAME($BASE)'`
- **Fallback to ripgrep**: Only when ast-grep isn't applicable
- **Never use basic grep**: ripgrep is always better for codebase searches (basic grep when other tools fail)

---

## 💡 KEY INSIGHTS

**★ Framework Enlightenment**: Desktop resizable apps with navigation are trivial in Flet. The entire application can be ~700 lines instead of 10,000+ lines of framework-fighting code(not really, but to illustrate the point).

**★ The Semi-Nuclear Protocol**: When refactoring complex code, analyze first to understand TRUE intentions, then rebuild with simple Flet patterns while preserving valuable business logic, achieving feature parity.

**★ Performance Secret**: Replacing `page.update()` with `control.update()` can improve performance by 10x+ and eliminate UI flicker.

**The FletV2 directory is the CANONICAL REFERENCE** for proper Flet desktop development. When in doubt, follow its examples exactly.