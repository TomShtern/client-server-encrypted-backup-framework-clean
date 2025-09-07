# FletV2_Architecture_Blueprint.md
## Desktop GUI Architecture Using Pure Flet Patterns

`★ Architectural Philosophy ─────────────────────────────────────`
Leverage Flet's built-in power - NavigationRail for routing, ResponsiveRow for layouts, DataTable for data, Theme for styling. The framework does the heavy lifting, we compose simple, elegant solutions.
`─────────────────────────────────────────────────`

---

## 🏛️ CORE ARCHITECTURAL PRINCIPLES

### 1. **Flet-Native First (The Golden Rule)**
```python
# ✅ CORRECT: Use Flet's built-in capabilities
ft.NavigationRail(on_change=switch_view)     # Not custom routing
ft.ResponsiveRow([...])                      # Not custom responsive system
ft.DataTable(columns=[...], rows=[...])     # Not custom table components
page.theme = ft.Theme(color_scheme=...)      # Not custom theme managers

# ❌ WRONG: Fighting the framework
class CustomNavigationManager:               # Framework already provides this
class ResponsiveLayoutSystem:               # Framework already provides this
class DataTableBuilder:                     # Framework already provides this
```

### 2. **Component Hierarchy (Keep It Simple)**
```
Application (ft.Row)
├── NavigationRail (ft.NavigationRail)
├── VerticalDivider (ft.VerticalDivider) 
└── ContentArea (ft.Container with expand=True)
    └── CurrentView (ft.Column/Row with native controls)
```

### 3. **Update Granularity (Performance Critical)**
```python
# ✅ CORRECT: Precise updates
status_text.value = "Connected"
status_text.update()                    # Only this control updates

# ✅ CORRECT: Multiple control updates
await ft.update_async(control1, control2, control3)

# ❌ WRONG: Expensive full page updates
page.update()                          # Updates entire page tree
```

---

## 🎯 APPLICATION STRUCTURE

### Main Application Class
```python
class FletV2App(ft.Row):
    """
    Desktop application following pure Flet patterns
    
    Architecture:
    - Single ft.Row container (horizontal layout)
    - NavigationRail for view switching (no custom routing)
    - Dynamic content area using Container with expand=True
    - All styling through page.theme (no custom theme managers)
    """
    
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.state_manager = StateManager(page)
        self.server_bridge = EnhancedServerBridge()
        
        # Configure window using Flet's native properties
        self._setup_window()
        
        # Apply theme using Flet's built-in system
        self._setup_theme()
        
        # Build UI using native Flet components
        self._build_ui()
    
    def _setup_window(self):
        """Configure window using Flet's native window properties"""
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.window.min_width = 1024
        self.page.window.min_height = 768
        self.page.window.resizable = True
        self.page.title = "Backup Server Management"
    
    def _setup_theme(self):
        """Apply theme using Flet's built-in theme system"""
        # Import from existing theme.py (source of truth)
        from theme import setup_default_theme
        setup_default_theme(self.page)
    
    def _build_ui(self):
        """Build UI using pure Flet components"""
        # Navigation using built-in NavigationRail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
                ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Clients"),
                ft.NavigationRailDestination(icon=ft.Icons.FOLDER, label="Files"),
                ft.NavigationRailDestination(icon=ft.Icons.STORAGE, label="Database"),
                ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, label="Analytics"),
                ft.NavigationRailDestination(icon=ft.Icons.LIST_ALT, label="Logs"),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            on_change=self._on_navigation_change
        )
        
        # Content area using native Container
        self.content_area = ft.Container(
            expand=True,
            padding=20,
            content=ft.Text("Loading...")  # Initial state
        )
        
        # Main layout using native Row
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1),
            self.content_area
        ]
        
        # Load initial view
        self._load_view("dashboard")
    
    def _on_navigation_change(self, e):
        """Handle navigation using simple view switching"""
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        selected_view = view_names[e.control.selected_index]
        self._load_view(selected_view)
    
    def _load_view(self, view_name: str):
        """Load view using function-based approach"""
        view_content = self._create_view(view_name)
        self.content_area.content = view_content
        self.content_area.update()  # Precise update, not page.update()
    
    def _create_view(self, view_name: str) -> ft.Control:
        """Factory for views using function-based pattern"""
        if view_name == "dashboard":
            from views.dashboard import create_dashboard_view
            return create_dashboard_view(self.state_manager, self.server_bridge, self.page)
        elif view_name == "clients":
            from views.clients import create_clients_view
            return create_clients_view(self.state_manager, self.server_bridge, self.page)
        # ... other views
        else:
            return ft.Text(f"View '{view_name}' not implemented yet")
```

---

## 📋 VIEW ARCHITECTURE PATTERN

### Function-Based View Pattern (MANDATORY)
```python
# views/dashboard.py
def create_dashboard_view(
    state_manager: StateManager, 
    server_bridge: EnhancedServerBridge, 
    page: ft.Page
) -> ft.Control:
    """
    Pure function-based view following Flet patterns
    
    Benefits:
    - No class complexity
    - Easy testing
    - Clean dependency injection
    - Flet-native composition
    """
    
    # Create UI components using native Flet controls
    server_status_cards = _create_server_status_section(state_manager)
    client_overview = _create_client_overview_section(state_manager)
    quick_actions = _create_quick_actions_section(server_bridge, page)
    
    # Layout using ResponsiveRow (native responsive system)
    return ft.Column([
        ft.Text("Server Dashboard", size=24, weight=ft.FontWeight.BOLD),
        
        # Status cards using native ResponsiveRow
        ft.ResponsiveRow([
            ft.Column([server_status_cards], col={"sm": 12, "md": 8}),
            ft.Column([quick_actions], col={"sm": 12, "md": 4})
        ]),
        
        ft.Divider(height=20),
        
        # Client overview using native components
        client_overview
    ], expand=True, scroll=ft.ScrollMode.AUTO)

def _create_server_status_section(state_manager: StateManager) -> ft.Control:
    """Create status cards using native Card components"""
    
    # Status cards using built-in Card and ResponsiveRow
    cpu_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MEMORY, color=ft.Colors.BLUE),
                    ft.Text("CPU Usage", weight=ft.FontWeight.BOLD)
                ]),
                ft.Text("Loading...", id="cpu_value", size=20)
            ])
        )
    )
    
    memory_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.STORAGE, color=ft.Colors.GREEN),
                    ft.Text("Memory", weight=ft.FontWeight.BOLD)
                ]),
                ft.Text("Loading...", id="memory_value", size=20)
            ])
        )
    )
    
    # Subscribe to state changes for real-time updates
    def on_server_status_change(new_status):
        if "cpu_usage" in new_status:
            cpu_card.content.content.controls[1].value = f"{new_status['cpu_usage']:.1f}%"
            cpu_card.update()
        
        if "memory_usage" in new_status:
            memory_card.content.content.controls[1].value = f"{new_status['memory_usage']:.1f}%"
            memory_card.update()
    
    state_manager.subscribe("server_status", on_server_status_change)
    
    return ft.ResponsiveRow([
        ft.Column([cpu_card], col={"sm": 12, "md": 6}),
        ft.Column([memory_card], col={"sm": 12, "md": 6})
    ])

def _create_client_overview_section(state_manager: StateManager) -> ft.Control:
    """Create client overview using native DataTable"""
    
    # Use built-in DataTable (no custom table components)
    client_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client ID")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Last Seen")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[]  # Will be populated by state subscription
    )
    
    def on_clients_change(new_clients):
        """Update table when clients change"""
        client_table.rows.clear()
        
        for client in new_clients[:5]:  # Show top 5 on dashboard
            client_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(client.get("client_id", "Unknown"))),
                    ft.DataCell(ft.Text(client.get("status", "Unknown"), 
                                      color=_get_status_color(client.get("status")))),
                    ft.DataCell(ft.Text(client.get("last_activity", "Never"))),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.INFO, tooltip="View Details"))
                ])
            )
        
        client_table.update()  # Precise update
    
    state_manager.subscribe("clients", on_clients_change)
    
    return ft.Column([
        ft.Text("Active Clients", size=18, weight=ft.FontWeight.BOLD),
        ft.Container(content=client_table, expand=True)
    ])

def _get_status_color(status: str) -> str:
    """Get color for status using Flet's semantic colors"""
    status_colors = {
        "Connected": ft.Colors.GREEN,
        "Registered": ft.Colors.BLUE,
        "Offline": ft.Colors.RED_400
    }
    return status_colors.get(status, ft.Colors.GREY)
```

---

## 🎨 UI COMPONENT PATTERNS

### Data Display Components
```python
# Use native Flet components instead of custom ones

# ✅ CORRECT: Native DataTable
def create_data_table(data: List[Dict], columns: List[str]) -> ft.DataTable:
    return ft.DataTable(
        columns=[ft.DataColumn(ft.Text(col)) for col in columns],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get(col, ""))))
                for col in columns
            ])
            for row in data
        ],
        border=ft.border.all(1, ft.Colors.OUTLINE)
    )

# ✅ CORRECT: Native Cards in ResponsiveRow
def create_metric_cards(metrics: Dict[str, Any]) -> ft.ResponsiveRow:
    cards = []
    for key, value in metrics.items():
        card = ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text(key.replace("_", " ").title(), weight=ft.FontWeight.BOLD),
                    ft.Text(str(value), size=18)
                ])
            )
        )
        cards.append(ft.Column([card], col={"sm": 12, "md": 6, "lg": 3}))
    
    return ft.ResponsiveRow(cards)

# ✅ CORRECT: Native Charts (if available) or simple progress indicators
def create_system_metrics(cpu: float, memory: float, disk: float) -> ft.Control:
    return ft.Column([
        ft.Text("System Metrics", size=18, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([
            ft.Column([
                ft.ProgressBar(value=cpu/100, color=ft.Colors.BLUE),
                ft.Text(f"CPU: {cpu:.1f}%")
            ], col={"sm": 12, "md": 4}),
            ft.Column([
                ft.ProgressBar(value=memory/100, color=ft.Colors.GREEN),
                ft.Text(f"Memory: {memory:.1f}%")
            ], col={"sm": 12, "md": 4}),
            ft.Column([
                ft.ProgressBar(value=disk/100, color=ft.Colors.ORANGE),
                ft.Text(f"Disk: {disk:.1f}%")
            ], col={"sm": 12, "md": 4})
        ])
    ])
```

### Form and Input Components
```python
# ✅ CORRECT: Native form controls
def create_settings_form() -> ft.Control:
    return ft.Column([
        ft.Text("Server Settings", size=18, weight=ft.FontWeight.BOLD),
        
        # Native TextField with validation
        ft.TextField(
            label="Server Port",
            value="1256",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: validate_port(e)
        ),
        
        # Native Dropdown
        ft.Dropdown(
            label="Log Level",
            options=[
                ft.dropdown.Option("DEBUG"),
                ft.dropdown.Option("INFO"),
                ft.dropdown.Option("WARNING"),
                ft.dropdown.Option("ERROR")
            ],
            value="INFO"
        ),
        
        # Native Switch
        ft.Row([
            ft.Text("Enable Real-time Updates"),
            ft.Switch(value=True, on_change=lambda e: toggle_realtime(e))
        ]),
        
        # Native buttons
        ft.Row([
            ft.FilledButton("Save Settings", on_click=save_settings),
            ft.OutlinedButton("Reset to Defaults", on_click=reset_settings)
        ])
    ])
```

---

## ⚡ STATE MANAGEMENT INTEGRATION

### View-State Connection Pattern
```python
def create_clients_view(state_manager: StateManager, server_bridge, page) -> ft.Control:
    """Clients view with state management integration"""
    
    # Create UI components
    client_table = ft.DataTable(columns=[...], rows=[])
    status_cards = create_metric_cards({})
    
    # State subscription for automatic updates
    def on_clients_update(new_clients):
        # Update table rows
        update_client_table(client_table, new_clients)
        
        # Update status cards
        metrics = calculate_client_metrics(new_clients)
        update_metric_cards(status_cards, metrics)
    
    def on_server_status_update(new_status):
        # Update connection indicator
        update_connection_status(connection_indicator, new_status.get("connected", False))
    
    # Subscribe to relevant state changes
    state_manager.subscribe("clients", on_clients_update)
    state_manager.subscribe("server_status", on_server_status_update)
    
    # Action handlers using server bridge
    def on_disconnect_client(client_id):
        async def disconnect():
            success = await server_bridge.disconnect_client(client_id)
            if success:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Client disconnected"),
                    bgcolor=ft.Colors.GREEN
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Failed to disconnect client"),
                    bgcolor=ft.Colors.RED
                )
            page.snack_bar.open = True
            page.update()  # Only for snack_bar
        
        page.run_task(disconnect)
    
    return ft.Column([
        ft.Text("Client Management", size=24, weight=ft.FontWeight.BOLD),
        status_cards,
        ft.Divider(),
        client_table
    ], expand=True)
```

---

## 🚀 PERFORMANCE OPTIMIZATION PATTERNS

### Efficient Update Strategies
```python
# ✅ CORRECT: Granular updates
def update_single_metric(control: ft.Text, new_value: str):
    if control.value != new_value:  # Only update if changed
        control.value = new_value
        control.update()

# ✅ CORRECT: Batch updates for multiple controls
async def update_server_metrics(cpu_control, memory_control, disk_control, metrics):
    cpu_control.value = f"{metrics['cpu']:.1f}%"
    memory_control.value = f"{metrics['memory']:.1f}%"
    disk_control.value = f"{metrics['disk']:.1f}%"
    
    # Update all at once
    await ft.update_async(cpu_control, memory_control, disk_control)

# ✅ CORRECT: Smart polling with visibility checks
class ViewManager:
    def __init__(self, page: ft.Page):
        self.current_view = None
        self.page = page
    
    def set_current_view(self, view_name: str):
        self.current_view = view_name
        # Only poll data for visible view
        self._start_view_specific_polling(view_name)
    
    def _start_view_specific_polling(self, view_name: str):
        if view_name == "dashboard":
            # Poll server status every 5 seconds
            self.page.run_task(self._poll_server_status)
        elif view_name == "clients":
            # Poll client data every 10 seconds
            self.page.run_task(self._poll_client_data)
```

### Memory Management
```python
# ✅ CORRECT: Clean up subscriptions when views change
def cleanup_view_subscriptions(state_manager: StateManager, view_name: str):
    """Remove subscriptions for views no longer active"""
    if view_name not in state_manager.active_views:
        state_manager.unsubscribe_all(view_name)

# ✅ CORRECT: Lazy loading for large datasets
def create_paginated_table(data: List[Dict], page_size: int = 50) -> ft.Control:
    current_page = 0
    
    def load_page(page_num: int):
        start_idx = page_num * page_size
        end_idx = start_idx + page_size
        return data[start_idx:end_idx]
    
    def next_page(e):
        nonlocal current_page
        current_page += 1
        update_table_data(load_page(current_page))
    
    def prev_page(e):
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            update_table_data(load_page(current_page))
    
    return ft.Column([
        create_data_table(load_page(0), ["col1", "col2", "col3"]),
        ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=prev_page),
            ft.Text(f"Page {current_page + 1}"),
            ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=next_page)
        ])
    ])
```

---

## 🎯 ARCHITECTURAL SUCCESS METRICS

### Code Quality Metrics
- ✅ **No custom routing**: Use `ft.NavigationRail.on_change`
- ✅ **No custom layouts**: Use `ft.ResponsiveRow` + `expand=True`
- ✅ **No custom tables**: Use `ft.DataTable`
- ✅ **No custom themes**: Use `page.theme` and `theme.py`
- ✅ **Function-based views**: Max 400 lines per view file
- ✅ **Precise updates**: Use `control.update()` not `page.update()`

### Performance Metrics
- ✅ **<100ms UI response**: State changes update UI within 100ms
- ✅ **Smooth scrolling**: Large lists use pagination or virtualization
- ✅ **Memory efficient**: Clean up subscriptions and unused components
- ✅ **Real-time ready**: WebSocket integration without blocking UI

### Maintainability Metrics
- ✅ **Single responsibility**: Each file has one clear purpose
- ✅ **Dependency injection**: Views receive dependencies as parameters
- ✅ **Pure functions**: Views are functions that return ft.Control
- ✅ **State decoupling**: UI components don't directly call APIs

---

## 📋 IMPLEMENTATION CHECKLIST

### Core Architecture
- [ ] Main app as single ft.Row with NavigationRail
- [ ] Function-based views returning ft.Control
- [ ] State management with automatic UI updates
- [ ] Theme system using page.theme only

### Component Standards
- [ ] All data tables use ft.DataTable
- [ ] All layouts use ft.ResponsiveRow + expand=True
- [ ] All forms use native ft.TextField, ft.Dropdown, etc.
- [ ] All cards use ft.Card with ft.Container content

### Performance Standards
- [ ] Precise updates with control.update()
- [ ] Batch updates for multiple controls
- [ ] Smart polling based on view visibility
- [ ] Subscription cleanup when views change

### Production Readiness
- [ ] Clear separation of mock vs production data
- [ ] Error handling with user-friendly feedback
- [ ] Loading states for all async operations
- [ ] Responsive design across window sizes

---

**The Architecture Goal:** Every UI element leverages Flet's native capabilities. No custom framework components. Maximum elegance with minimal code. The framework does the work, we compose the solution.

---

*This architecture ensures FletV2 works WITH Flet's natural patterns, achieving professional results through framework harmony rather than framework fighting.*