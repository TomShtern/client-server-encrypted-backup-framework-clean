"""
Purpose: Database browser view
Logic: Database browsing, table viewing, and database management operations
UI: Database statistics, table selector, and table content display
"""

#!/usr/bin/env python3
"""
Database Browser View
Shows actual database tables and content from the backup server database.
"""

import flet as ft
from typing import List, Dict, Any, Optional

# Existing imports
from flet_server_gui.core.client_management import ClientManagement
from flet_server_gui.core.file_management import FileManagement
from flet_server_gui.ui.widgets.cards import DatabaseStatsCard
from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
from flet_server_gui.components.base_component import BaseComponent
from flet_server_gui.components.database_action_handlers import DatabaseActionHandlers

# Enhanced components imports
from flet_server_gui.ui.widgets import (
    EnhancedButton,
    EnhancedCard,
    EnhancedTable,
    EnhancedWidget,
    EnhancedButtonConfig,
    ButtonVariant,
    CardVariant,
    TableSize,
    WidgetSize,
    WidgetType
)

# Layout fixes imports
from flet_server_gui.ui.layouts.responsive_fixes import ResponsiveLayoutFixes
from flet_server_gui.ui.unified_theme_system import ThemeConsistencyManager, apply_theme_consistency
from flet_server_gui.ui.unified_theme_system import TOKENS



class DatabaseView(BaseComponent):
    """Database browser view with actual database content and management capabilities."""
    
    def __init__(self, server_bridge: "ServerBridge", dialog_system, toast_manager, page):
        # Initialize parent BaseComponent
        super().__init__(page, dialog_system, toast_manager)
        
        # Initialize theme consistency manager
        self.theme_manager = ThemeConsistencyManager(page)
        
        self.server_bridge = server_bridge
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.page = page
        
        # Initialize action handlers
        self.action_handlers = DatabaseActionHandlers(server_bridge, dialog_system, toast_manager, page)
        self.action_handlers.set_data_changed_callback(self.refresh_database)
        
        # Initialize button factory
        self.button_factory = ActionButtonFactory(self, server_bridge, page)
        
        # Set action handlers in button factory
        self.button_factory.actions["DatabaseActionHandlers"] = self.action_handlers
        
        # UI Components
        self.selected_table = None
        self.table_selector = None
        self.table_content = None
        self.stats_cards = None
        self.refresh_button = None
        
    def build(self) -> ft.Control:
        """Build the database browser view."""
        
        # Header - Apply responsive layout fixes
        header = ft.Row([
            ft.Text("Database Browser", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.IconButton(
                ft.Icons.REFRESH, 
                tooltip="Refresh Database", 
                on_click=self.refresh_database
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Apply hitbox fixes to the refresh button
        if len(header.controls) > 1 and isinstance(header.controls[1], ft.IconButton):
            header.controls[1] = ResponsiveLayoutFixes.fix_button_hitbox(header.controls[1])
        
        # Database stats (will be populated dynamically) - Apply responsive layout fixes
        self.stats_cards = ft.ResponsiveRow([], spacing=20)
        
        # Table selector - Apply responsive layout fixes
        self.table_selector = ft.Dropdown(
            label="Select Table",
            width=300,
            on_change=self.on_table_select,
            options=[]  # Will be populated by refresh
        )
        
        # Database controls - Apply responsive layout fixes
        db_controls = ft.Row([
            self.button_factory.create_action_button(
                "database_backup",
                lambda: []
            ),
            self.button_factory.create_action_button(
                "database_optimize", 
                lambda: []
            ),
            self.button_factory.create_action_button(
                "database_analyze", 
                lambda: []
            ),
            self.button_factory.create_action_button(
                "database_execute_query", 
                lambda: []
            ),
        ], spacing=10)
        
        # Apply hitbox fixes to action buttons
        for control in db_controls.controls:
            if isinstance(control, ft.ElevatedButton):
                control = ResponsiveLayoutFixes.fix_button_hitbox(control)
        
        # Table content area (scrollable) - Apply responsive layout fixes
        self.table_content = ft.Container(
            content=ft.Text("Select a table to view its contents", 
                          style=ft.TextThemeStyle.BODY_LARGE),
            height=400,
            # Let theme handle border color automatically,
            border_radius=8,
            padding=20,
        )
        
        # Apply clipping fixes to table content
        self.table_content = ResponsiveLayoutFixes.create_clipping_safe_container(
            self.table_content
        )
        
        # Main content - Apply responsive layout fixes
        content = ft.Column([
            header,
            ft.Divider(),
            self.stats_cards,
            ft.Divider(),
            ft.Row([
                self.table_selector,
                ft.VerticalDivider(width=20),
                db_controls,
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=20),  # Spacer
            ft.Text("Table Contents", style=ft.TextThemeStyle.TITLE_LARGE),
            self.table_content,
        ], spacing=20, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        
        # Apply windowed mode compatibility
        main_content = ResponsiveLayoutFixes.create_windowed_layout_fix(content)
        
        # Apply theme consistency
        apply_theme_consistency(self.page)
        
        # Load data immediately
        self.refresh_database()
        
        return main_content
    
    def refresh_database(self, e=None):
        """Refresh database information and table list."""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self._show_error("Database not available")
                return
            
            # Get database statistics
            stats = self.server_bridge.data_manager.db_manager.get_database_stats()
            self._update_stats_cards(stats)
            
            # Get table names
            table_names = self.server_bridge.data_manager.db_manager.get_table_names()
            self._update_table_selector(table_names)
            
            print(f"[INFO] Database refreshed - found {len(table_names)} tables")
            
        except Exception as e:
            self._show_error(f"Failed to refresh database: {str(e)}")
            print(f"[ERROR] Database refresh failed: {e}")
    
    def _update_stats_cards(self, stats: Dict[str, Any]):
        """Update the database statistics cards."""
        self.stats_cards.controls.clear()
        
        # Total clients card
        self.stats_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON, size=32, color=TOKENS['primary']),
                        ft.Text("Clients", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(str(stats.get('total_clients', 0)), 
                               style=ft.TextThemeStyle.DISPLAY_MEDIUM, 
                               weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            )
        )
        
        # Total files card
        self.stats_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FOLDER, size=32, color=TOKENS['secondary']),
                        ft.Text("Files", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(str(stats.get('total_files', 0)), 
                               style=ft.TextThemeStyle.DISPLAY_MEDIUM, 
                               weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            )
        )
        
        # Verified files card
        self.stats_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.VERIFIED, size=32, color=TOKENS['secondary']),
                        ft.Text("Verified", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(str(stats.get('verified_files', 0)), 
                               style=ft.TextThemeStyle.DISPLAY_MEDIUM, 
                               weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            )
        )
        
        # Database size card
        db_size_mb = stats.get('database_size_bytes', 0) / (1024 * 1024)
        self.stats_cards.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.STORAGE, size=32, color=TOKENS['primary']),
                        ft.Text("DB Size", style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.Text(f"{db_size_mb:.1f} MB", 
                               style=ft.TextThemeStyle.DISPLAY_MEDIUM, 
                               weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=20,
                ),
                col={"sm": 6, "md": 3},
                elevation=2
            )
        )
    
    def _update_table_selector(self, table_names: List[str]):
        """Update the table selector dropdown."""
        self.table_selector.options.clear()
        
        for table_name in table_names:
            # Add icon based on table name
            if 'client' in table_name.lower():
                icon = "נ‘₪"
            elif 'file' in table_name.lower():
                icon = "נ“"
            elif 'log' in table_name.lower():
                icon = "נ“‹"
            else:
                icon = "נ—‚ן¸"
            
            self.table_selector.options.append(
                ft.dropdown.Option(
                    key=table_name,
                    text=f"{icon} {table_name}"
                )
            )
        
        # Auto-select first table if available
        if table_names:
            self.table_selector.value = table_names[0]
            self.selected_table = table_names[0]
            self.load_table_content(table_names[0])
    
    def on_table_select(self, e):
        """Handle table selection."""
        selected = e.control.value
        if selected:
            self.selected_table = selected
            self.load_table_content(selected)
    
    def load_table_content(self, table_name: str):
        """Load and display table content."""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self._show_error("Database not available")
                return
            
            # Get table content
            columns, rows = self.server_bridge.data_manager.db_manager.get_table_content(table_name)
            
            if not columns:
                self.table_content.content = ft.Text(
                    f"Table '{table_name}' is empty or cannot be read",
                    color=TOKENS['outline']
                )
                self.table_content.update()
                return
            
            # Create data table
            data_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)) 
                    for col in columns
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(row.get(col, '')), selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS))
                        for col in columns
                    ])
                    for row in rows[:50]  # Limit to first 50 rows for performance
                ],
                # Let theme handle border colors automatically,
                border_radius=8,
                # Let theme handle grid line colors automatically,
                # Let theme handle grid line colors automatically,
            )
            
            # Status text
            status_text = ft.Text(
                f"Showing {min(len(rows), 50)} of {len(rows)} rows from '{table_name}'",
                size=12,
                color=TOKENS['outline']
            )
            
            # Update table content
            self.table_content.content = ft.Column([
                status_text,
                data_table
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            
            # Update will be handled by parent component
            print(f"[INFO] Loaded {len(rows)} rows from table '{table_name}'")
            
        except Exception as e:
            self._show_error(f"Failed to load table '{table_name}': {str(e)}")
            print(f"[ERROR] Failed to load table content: {e}")
    
    def backup_database(self, e):
        """Handle database backup."""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self.action_handlers.backup_database())
        else:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(self.action_handlers.backup_database())
            except RuntimeError:
                # No event loop running, skip async task creation
                pass
    
    def optimize_database(self, e):
        """Handle database optimization."""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self.action_handlers.optimize_database())
        else:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(self.action_handlers.optimize_database())
            except RuntimeError:
                # No event loop running, skip async task creation
                pass
    
    def analyze_database(self, e):
        """Handle database analysis."""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self.action_handlers.analyze_database())
        else:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(self.action_handlers.analyze_database())
            except RuntimeError:
                # No event loop running, skip async task creation
                pass
    
    def _show_error(self, message: str):
        """Show error message to user."""
        if self.toast_manager:
            self.toast_manager.show_error(message)
        else:
            print(f"[ERROR] {message}")
    
    def _show_success(self, message: str):
        """Show success message to user."""
        if self.toast_manager:
            self.toast_manager.show_success(message)
        else:
            print(f"[SUCCESS] {message}")
