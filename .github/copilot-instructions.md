---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

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
Be highly suspicious of any custom solution that exceeds 1000 lines. A 3000+ line custom system is an anti-pattern when a 50-450 line native Flet solution exists with full feature parity(or almost full parity). Code files ideally should remain between 600-800 lines, but this is not a hard limit.

#### **Framework Fight Test**: 
Work WITH the framework, not AGAINST it. If your solution feels complex, verbose, or like a struggle, you are fighting the framework. Stop and find the simpler, intended Flet way.

#### **Built-in Checklist**:
- Can `ft.NavigationRail` handle navigation?
- Can `expand=True` and `ResponsiveRow` solve layout?
- Can `control.update()` replace `page.update()`?
- Does a standard Flet control already do 90% of what you need?


### Redundant File Analysis Protocol (CRITICAL FOR DEVELOPMENT)
**Before deleting any file that appears redundant, ALWAYS follow this process**:

1. **Analyze thoroughly**: Read through the "redundant" file completely
2. **Compare functionality**: Check if it contains methods, utilities, or features not present in the "original" file, that could benifit the original file.
3. **Identify valuable code**: Look for:
   - Helper functions or utilities that could be useful
   - Error handling patterns that are more robust
   - Configuration options or constants that might be needed
   - Documentation or comments that provide important context
   - Different implementation approaches that might be superior
4. **Integration decision**: If valuable code is found:
   - Extract and integrate the valuable parts into the primary file
   - Test that the integration works correctly
   - Ensure no functionality is lost
5. **Safe deletion**: Only after successful integration, delete the redundant file

**Why this matters**: "Simple" or "mock" files often contain valuable utilities, edge case handling, or configuration details that aren't obvious at first glance. Premature deletion can result in lost functionality and regression bugs.

**Example**: A "simple" client management component might contain useful date formatting functions or error message templates that the "comprehensive" version lacks.

### When going through massive logs:
On-Disk + Grep/Awk Tools

If you don’t want the overhead:
ripgrep (rg) or ag (silversearcher) – insanely fast search in files.
ast-grep – structured searching if logs have consistent format (JSON logs).
fzf – fuzzy finder, useful when you know part of the error.
Pipe logs through grep | tail -n 50 style workflows.

🔹 Using ripgrep (rg)

Fastest way to pull out the “couple of bad lines.”
Find all ERROR lines:
rg "ERROR" app.log
Show 5 lines of context around each match:
rg -C 5 "Exception" app.log
Search across multiple logs at once:
rg "timeout" /var/logs/
Stream logs + highlight in real time:
tail -f app.log | rg "ERROR"

🔹 Using ast-grep

Best if your logs are structured (e.g., JSON). Lets you query fields instead of regex spaghetti.
Example log (JSON):
{"level": "ERROR", "msg": "Database connection failed", "code": 500}
Find all ERROR-level logs:
sg -p ' { "level": "ERROR", ... } ' logs.json
Find logs with specific error codes:
sg -p ' { "code": 500, ... } ' logs.json
Match only the message field:
sg -p ' { "msg": $MSG } ' logs.json

🚀 Pro tip
Use ripgrep when you’re just scanning for keywords.
Use ast-grep when your logs are JSON or structured, so you can surgically extract only what matters.
Combine them with fzf (if you install it) for interactive filtering.
---

## ⚡ POWER DIRECTIVES: Maximum Impact Code Generation

### **Critical Framework Compliance (Flet 0.28.3 + Python 3.13.5)**

1. **Always use `control.update()` instead of `page.update()` to achieve 10x performance and eliminate UI flicker.**

2. **Leverage `ft.ResponsiveRow` and `expand=True` as your primary layout mechanism, eliminating the need for complex custom responsive systems.**

3. **Use `ft.NavigationRail.on_change` for navigation, completely removing the need for custom routing managers.**

4. **Use `ft.Theme` and `ft.ColorScheme` for styling, avoiding any custom theming logic over 50 lines.**

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
# FletV2/main.py - Modern desktop app with performance optimizations
class FletV2App(ft.Row):
    """
    Enhanced FletV2 desktop app using pure Flet patterns with modern UI and performance optimizations.
    
    Features:
    - Lazy view loading with caching for performance
    - Modern Material Design 3 styling and animations
    - Collapsible navigation rail with keyboard shortcuts
    - State manager integration for reactive updates
    - Background task management
    - Enhanced error handling with graceful fallbacks
    """
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        
        # Performance optimization: lazy view loading and caching
        self._loaded_views = {}  # Cache for loaded views
        self._background_tasks = set()  # Track background tasks
        
        # Initialize state manager for reactive UI updates
        self.state_manager = None
        self._initialize_state_manager()
        
        # Initialize server bridge synchronously for immediate availability
        from utils.server_bridge import create_server_bridge
        self.server_bridge = create_server_bridge()
        
        # Create optimized content area with modern Material Design 3 styling
        self.content_area = ft.Container(
            expand=True,
            padding=ft.Padding(24, 20, 24, 20),  # Material Design 3 spacing standards
            border_radius=ft.BorderRadius(16, 0, 0, 16),  # Modern rounded corners
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE),  # Surface hierarchy
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(140, ft.AnimationCurve.EASE_OUT_CUBIC),  # Modern animation
            content=ft.AnimatedSwitcher(
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=160,
                switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
                switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
                expand=True
            )
        )
        
        # Create collapsible navigation rail with modern styling
        self.nav_rail_extended = True
        self.nav_rail = self._create_navigation_rail()
        
        # Build layout: NavigationRail + content area (pure Flet pattern)
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            self.content_area
        ]
        
        # Set up keyboard shortcuts and page handlers
        page.on_keyboard_event = self._on_keyboard_event
        
        # Load initial dashboard view immediately
        self._load_view("dashboard")
    
    def _create_navigation_rail(self):
        """Create enhanced collapsible navigation rail with modern styling."""
        return ft.Container(
            content=ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                group_alignment=-0.8,
                min_width=68,  # Collapsed width
                min_extended_width=240,  # Extended width
                extended=self.nav_rail_extended,
                bgcolor=ft.Colors.with_opacity(0.98, ft.Colors.SURFACE),
                indicator_color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY),
                indicator_shape=ft.RoundedRectangleBorder(radius=24),
                elevation=6,
                destinations=[
                    ft.NavigationRailDestination(
                        icon=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, size=22,
                                   badge=ft.Badge(small_size=8, bgcolor=ft.Colors.GREEN)),
                        selected_icon=ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.PRIMARY, size=24),
                        label="Dashboard"
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=22),
                        selected_icon=ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.PRIMARY, size=24),
                        label="Clients"
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icon(ft.Icons.FOLDER_OUTLINED, size=22),
                        selected_icon=ft.Icon(ft.Icons.FOLDER, color=ft.Colors.PRIMARY, size=24),
                        label="Files"
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icon(ft.Icons.STORAGE_OUTLINED, size=22),
                        selected_icon=ft.Icon(ft.Icons.STORAGE, color=ft.Colors.PRIMARY, size=24),
                        label="Database"
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icon(ft.Icons.AUTO_GRAPH_OUTLINED, size=22),
                        selected_icon=ft.Icon(ft.Icons.AUTO_GRAPH, color=ft.Colors.PRIMARY, size=24),
                        label="Analytics"
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icon(ft.Icons.ARTICLE_OUTLINED, size=22),
                        selected_icon=ft.Icon(ft.Icons.ARTICLE, color=ft.Colors.PRIMARY, size=24),
                        label="Logs"
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=22),
                        selected_icon=ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.PRIMARY, size=24),
                        label="Settings"
                    ),
                ],
                on_change=self._on_navigation_change,
                leading=ft.Container(
                    content=ft.FloatingActionButton(
                        icon=ft.Icons.MENU_ROUNDED if self.nav_rail_extended else ft.Icons.MENU_OPEN_ROUNDED,
                        mini=True,
                        tooltip="Toggle Navigation Menu",
                        on_click=self._toggle_navigation_rail,
                    ),
                    padding=ft.Padding(8, 16, 8, 8),
                ),
                trailing=ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.BRIGHTNESS_6_ROUNDED,
                        tooltip="Toggle Dark/Light Theme",
                        on_click=self._on_theme_toggle,
                    ),
                    padding=ft.Padding(8, 8, 8, 16),
                )
            ),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(2, 0),
            ),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
            border_radius=ft.BorderRadius(0, 12, 12, 0),
        )
    
    def _on_navigation_change(self, e):
        """Enhanced navigation with lazy loading and caching."""
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        selected_view = view_names[e.control.selected_index] if e.control.selected_index < len(view_names) else "dashboard"
        
        logger.info(f"Navigation switching to: {selected_view}")
        self._load_view(selected_view)
    
    def _load_view(self, view_name: str):
        """Load view with lazy loading, caching, and enhanced error handling."""
        try:
            # Dynamic view loading with state manager integration
            if view_name == "dashboard":
                from views.dashboard import create_dashboard_view
                content = self._create_enhanced_view(create_dashboard_view, view_name)
            elif view_name == "clients":
                from views.clients import create_clients_view
                content = self._create_enhanced_view(create_clients_view, view_name)
            # ... other views following the same pattern
            else:
                # Fallback to dashboard
                from views.dashboard import create_dashboard_view
                content = self._create_enhanced_view(create_dashboard_view, "dashboard")
            
            # Update content using AnimatedSwitcher for smooth transitions
            animated_switcher = self.content_area.content
            animated_switcher.content = content
            animated_switcher.update()  # Precise update, not page.update()
            
        except Exception as e:
            logger.error(f"Failed to load view {view_name}: {e}")
            # Show error view as fallback
            animated_switcher = self.content_area.content
            animated_switcher.content = self._create_error_view(str(e))
            animated_switcher.update()
    
    def _create_enhanced_view(self, view_function, view_name: str):
        """Create view with state manager integration."""
        try:
            # Try with state_manager first
            return view_function(self.server_bridge, self.page, state_manager=self.state_manager)
        except TypeError:
            # Fallback without state_manager for backward compatibility
            return view_function(self.server_bridge, self.page)
    
    def _on_keyboard_event(self, e: ft.KeyboardEvent):
        """Handle keyboard shortcuts for navigation."""
        if not e.ctrl:
            return
        
        shortcuts = {
            "D": 0, "C": 1, "F": 2, "B": 3, "A": 4, "L": 5, "S": 6
        }
        
        if e.key in shortcuts:
            nav_rail = self.nav_rail.content
            nav_rail.selected_index = shortcuts[e.key]
            self._on_navigation_change(type('Event', (), {'control': nav_rail})())
```

### **View Creation Pattern (MANDATORY)**

```python
# views/dashboard.py - Enhanced view pattern with state management and modern styling
def create_dashboard_view(server_bridge, page: ft.Page, state_manager: Optional[StateManager] = None) -> ft.Control:
    """
    Create dashboard view with enhanced infrastructure support and modern styling.
    
    Features:
    - State manager integration for reactive updates
    - Modern 2025 styling with enhanced cards and animations  
    - Sophisticated hover effects and micro-interactions
    - Enhanced error handling and user feedback
    - Real-time data updates when available
    """
    
    from utils.user_feedback import show_success_message, show_error_message
    from theme import create_modern_card, create_modern_button_style
    
    # Essential refs for dynamic styling and interactions
    cpu_progress_bar_ref = ft.Ref[ft.ProgressBar]()
    server_status_text_ref = ft.Ref[ft.Text]()
    start_server_button_ref = ft.Ref[ft.FilledButton]()
    
    # Enhanced data loading with state management integration
    def get_server_status():
        if server_bridge:
            try:
                return server_bridge.get_server_status()
            except Exception as e:
                logger.warning(f"Server bridge failed: {e}")
        return {"server_running": True, "clients": 3, "files": 72}  # Mock fallback
    
    # Modern hover effects with sophisticated animations  
    def handle_card_hover(e, accent_color):
        """Enhanced card hover with depth and shadow animations."""
        try:
            is_hover = e.data == "true"
            e.control.scale = 1.02 if is_hover else 1.0
            e.control.animate_scale = ft.Animation(
                duration=200, 
                curve=ft.AnimationCurve.EASE_OUT_CUBIC
            )
            
            # Enhanced shadow depth
            if hasattr(e.control, 'shadow'):
                e.control.shadow.blur_radius = 16 if is_hover else 8
                
            e.control.update()
        except Exception as ex:
            logger.debug(f"Card hover effect failed: {ex}")
    
    # Enhanced async event handlers with modern UI feedback
    async def on_start_server(e):
        """Start server with enhanced feedback and state management."""
        try:
            # Show immediate visual feedback
            if start_server_button_ref.current:
                start_server_button_ref.current.disabled = True
                start_server_button_ref.current.update()
            
            logger.info("Start server clicked")
            
            # Server operation (simplified for demo)
            result = await asyncio.sleep(1)  # Simulate async operation
            
            # Update state if state manager available
            if state_manager:
                await state_manager.update_state("server_status", {"running": True})
            
            # Show success feedback
            show_success_message(page, "Server started successfully")
            
        except Exception as ex:
            logger.error(f"Start server failed: {ex}")
            show_error_message(page, f"Failed to start server: {ex}")
        finally:
            # Re-enable button
            if start_server_button_ref.current:
                start_server_button_ref.current.disabled = False
                start_server_button_ref.current.update()
    
    # Get current server status
    status = get_server_status()
    
    # Create modern cards with enhanced styling
    def create_status_card(title, value, icon, color, description=""):
        return create_modern_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=32, color=color),
                    ft.Column([
                        ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                        ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD),
                    ], spacing=2, expand=True)
                ], spacing=16),
                ft.Text(description, size=12, color=ft.Colors.ON_SURFACE_VARIANT) if description else ft.Container(),
            ], spacing=8),
            elevation="soft",
            hover_effect=True
        )
    
    # Create system monitoring cards
    system_cards = ft.ResponsiveRow([
        ft.Column([
            create_status_card(
                "Active Clients", 
                status.get('clients', 0), 
                ft.Icons.PEOPLE, 
                ft.Colors.BLUE,
                "Currently connected"
            )
        ], col={"sm": 12, "md": 6, "lg": 3}),
        
        ft.Column([
            create_status_card(
                "Total Files", 
                status.get('files', 0), 
                ft.Icons.FOLDER, 
                ft.Colors.GREEN,
                "Successfully backed up"
            )
        ], col={"sm": 12, "md": 6, "lg": 3}),
        
        ft.Column([
            create_status_card(
                "Server Status", 
                "Running" if status.get('server_running') else "Stopped", 
                ft.Icons.CLOUD, 
                ft.Colors.GREEN if status.get('server_running') else ft.Colors.RED,
                "Current server state"
            )
        ], col={"sm": 12, "md": 6, "lg": 3}),
        
        ft.Column([
            create_status_card(
                "CPU Usage", 
                "45%", 
                ft.Icons.MEMORY, 
                ft.Colors.ORANGE,
                "System resource usage"
            )
        ], col={"sm": 12, "md": 6, "lg": 3}),
    ], spacing=16)
    
    # Enhanced control buttons with modern styling
    control_buttons = ft.Row([
        ft.FilledButton(
            "Start Server",
            icon=ft.Icons.PLAY_ARROW,
            style=create_modern_button_style("primary", "filled"),
            on_click=on_start_server,
            ref=start_server_button_ref
        ),
        ft.OutlinedButton(
            "Stop Server",
            icon=ft.Icons.STOP,
            style=create_modern_button_style("error", "outlined"),
        ),
        ft.TextButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            style=create_modern_button_style("primary", "text"),
        ),
    ], spacing=12)
    
    # Return enhanced dashboard with modern layout
    return ft.Column([
        # Header with modern typography
        ft.Container(
            content=ft.Column([
                ft.Text("Server Dashboard", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Monitor and control your backup server", 
                       size=16, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=4),
            padding=ft.Padding(0, 0, 0, 24)
        ),
        
        # System monitoring cards
        system_cards,
        
        # Control panel
        create_modern_card(
            content=ft.Column([
                ft.Text("Server Controls", size=18, weight=ft.FontWeight.W_600),
                control_buttons,
            ], spacing=16),
            elevation="medium",
            padding=24
        ),
        
        # Real-time updates integration
        ft.Container(height=20),  # Spacer
        
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=20)
```

### **Theme System (SOURCE OF TRUTH)**

```python
# theme.py - Modern 2025 Theme System with Enhanced Visual Effects
def setup_modern_theme(page: ft.Page) -> None:
    """
    Set up 2025 modern theme with vibrant colors, enhanced depth, and layering effects.
    Features Material Design 3 with modern color science and sophisticated visual hierarchy.
    """
    
    # 2025 Vibrant Color Palette
    BRAND_COLORS = {
        "primary": "#3B82F6",        # Vibrant blue
        "secondary": "#8B5CF6",      # Vibrant purple
        "accent_cyan": "#06B6D4",    # Modern cyan
        "accent_emerald": "#10B981", # Fresh emerald
        "surface_elevated": "#F8FAFC", # Elevated surface
        "surface_container": "#F1F5F9", # Container surface
    }
    
    # Enhanced light theme with vibrant color system  
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=BRAND_COLORS["primary"],
            primary_container=BRAND_COLORS["surface_container"],
            secondary=BRAND_COLORS["secondary"],
            tertiary=BRAND_COLORS["accent_emerald"],
            surface=BRAND_COLORS["surface_elevated"],
            background=BRAND_COLORS["surface_elevated"],
            on_primary=ft.Colors.WHITE,
            on_surface=ft.Colors.GREY_900,
        ),
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True  # Enable Material Design 3
    )
    
    # Enhanced dark theme with vibrant colors
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#60A5FA",          # Bright blue for dark
            secondary="#A78BFA",        # Bright purple for dark
            tertiary="#34D399",         # Bright emerald for dark
            surface="#1E293B",          # Dark elevated surface
            background="#1E293B",
            on_primary=ft.Colors.GREY_900,
            on_surface=ft.Colors.GREY_100,
        ),
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True
    )
    
    page.theme_mode = ft.ThemeMode.SYSTEM

# Multiple Theme Variants Support
THEMES = {
    "Teal": {
        "light": ft.Theme(color_scheme=ft.ColorScheme(
            primary="#38A298", secondary="#7C5CD9", surface="#F0F4F8", background="#F8F9FA"
        ), font_family="Inter"),
        "dark": ft.Theme(color_scheme=ft.ColorScheme(
            primary="#82D9CF", secondary="#D0BCFF", surface="#1A2228", background="#12181C"
        ), font_family="Inter")
    },
    "Purple": {
        "light": ft.Theme(color_scheme=ft.ColorScheme(
            primary="#7C5CD9", secondary="#FFA726", surface="#F0F4F8", background="#F8F9FA"
        ), font_family="Inter"),
        "dark": ft.Theme(color_scheme=ft.ColorScheme(
            primary="#D0BCFF", secondary="#FFB868", surface="#1A2228", background="#12181C"
        ), font_family="Inter")
    }
}

# Enhanced Shadow System for 2025 Layering
SHADOW_STYLES = {
    "subtle": ft.BoxShadow(blur_radius=4, offset=ft.Offset(0, 1), 
                          color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
    "soft": ft.BoxShadow(blur_radius=8, offset=ft.Offset(0, 2), 
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
    "medium": ft.BoxShadow(blur_radius=16, offset=ft.Offset(0, 4), 
                          color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK)),
    "elevated": ft.BoxShadow(blur_radius=24, offset=ft.Offset(0, 8), 
                            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
    "primary_glow": ft.BoxShadow(blur_radius=20, offset=ft.Offset(0, 4), 
                                color=ft.Colors.with_opacity(0.3, "#3B82F6")),
}

def create_modern_card(content: ft.Control, elevation: str = "soft", 
                      hover_effect: bool = True, padding: int = 20) -> ft.Container:
    """Create modern card with 2025 styling: enhanced shadows, hover effects."""
    return ft.Container(
        content=content,
        bgcolor=ft.Colors.SURFACE,
        shadow=SHADOW_STYLES[elevation],
        border_radius=16,  # Modern rounded corners
        border=ft.border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.GREY)),
        padding=padding,
        animate=ft.animation.Animation(150, ft.AnimationCurve.EASE_OUT) if hover_effect else None,
    )

def create_modern_button_style(color_type: str = "primary", 
                              variant: str = "filled") -> ft.ButtonStyle:
    """Create modern button style with enhanced states and 2025 color vibrancy."""
    if variant == "filled":
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.PRIMARY,
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.9, ft.Colors.PRIMARY),
            },
            color=ft.Colors.WHITE,
            elevation={ft.ControlState.DEFAULT: 2, ft.ControlState.HOVERED: 6},
            shape=ft.RoundedRectangleBorder(radius=12),
            animation_duration=120,
        )
    elif variant == "outlined":
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
            },
            color=ft.Colors.PRIMARY,
            side=ft.BorderSide(2, ft.Colors.PRIMARY),
            shape=ft.RoundedRectangleBorder(radius=12),
        )

def toggle_theme_mode(page: ft.Page) -> None:
    """Enhanced theme toggle with modern UI feedback."""
    if page.theme_mode == ft.ThemeMode.LIGHT:
        page.theme_mode = ft.ThemeMode.DARK
    elif page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
    
    page.update()  # ONLY acceptable page.update() for theme changes

def apply_theme_variant(page: ft.Page, theme_name: str) -> bool:
    """Apply different theme variant while preserving current theme mode."""
    if theme_name not in THEMES:
        return False
    
    current_mode = page.theme_mode
    theme_data = THEMES[theme_name]
    page.theme = theme_data["light"]
    page.dark_theme = theme_data["dark"]
    page.theme_mode = current_mode
    page.update()
    return True
```

---
### **