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
from flet_server_gui.components.database_table_renderer import DatabaseTableRenderer

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
        
        # Initialize table renderer with database view reference
        self.table_renderer = DatabaseTableRenderer(server_bridge, self.button_factory, page)
        # Set database view reference for button callbacks
        self.table_renderer.database_view = self
        
        # Set action handlers in button factory
        self.button_factory.actions["DatabaseActionHandlers"] = self.action_handlers
        
        # Also set in the base component for backward compatibility
        self.actions = {
            "DatabaseActionHandlers": self.action_handlers
        }
        
        # UI Components
        self.selected_table = None
        self.table_selector = None
        self.table_content = None
        self.stats_cards = None
        self.refresh_button = None
        self.bulk_actions_row = None
        self.select_all_checkbox = None
        
        # Data
        self.selected_rows = []
        self.current_table_data = []
        
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
        
        # Database controls - Use direct buttons instead of factory for better reliability
        db_controls = ft.Row([
            ft.ElevatedButton(
                "Backup Database",
                icon=ft.Icons.BACKUP,
                on_click=self.backup_database,
                tooltip="Create database backup"
            ),
            ft.ElevatedButton(
                "Optimize Database", 
                icon=ft.Icons.SPEED,
                on_click=self.optimize_database,
                tooltip="Optimize database performance"
            ),
            ft.ElevatedButton(
                "Analyze Database", 
                icon=ft.Icons.ANALYTICS,
                on_click=self.analyze_database,
                tooltip="Analyze database statistics"
            ),
            ft.ElevatedButton(
                "Execute Query", 
                icon=ft.Icons.PLAY_ARROW,
                on_click=self.show_query_dialog,
                tooltip="Execute custom SQL query"
            ),
        ], spacing=10)
        
        # Apply hitbox fixes to action buttons
        for control in db_controls.controls:
            if isinstance(control, ft.ElevatedButton):
                control = ResponsiveLayoutFixes.fix_button_hitbox(control)
        
        # Apply hitbox fixes to action buttons
        for control in db_controls.controls:
            if isinstance(control, ft.ElevatedButton):
                control = ResponsiveLayoutFixes.fix_button_hitbox(control)
        
        # Row selection controls
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            on_change=self._on_select_all
        )
        
        # Bulk actions row
        self.bulk_actions_row = ft.Row([
            ft.Text("Row Actions:", weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Delete Selected",
                icon=ft.Icons.DELETE,
                on_click=self._bulk_delete_rows,
                visible=False
            ),
            ft.ElevatedButton(
                "Export Selected",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._bulk_export_rows,
                visible=False
            ),
        ], spacing=10)
        
        # Table content area using new renderer (initially empty)
        self.table_content = self.table_renderer.get_table_container()
        
        # Create the table content container that we'll update
        self.table_content_container = ft.Container(
            content=self.table_content,
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE
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
            # Selection controls
            ft.Row([
                self.select_all_checkbox,
                ft.VerticalDivider(width=20),
            ], alignment=ft.MainAxisAlignment.START),
            self.bulk_actions_row,
            self.table_content_container,
        ], spacing=20, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        
        # Apply windowed mode compatibility
        main_content = ResponsiveLayoutFixes.create_windowed_layout_fix(content)
        
        # Apply theme consistency
        apply_theme_consistency(self.page)
        
        # Defer data loading until page is ready
        # This avoids "Control must be added to the page first" errors
        if hasattr(self.page, 'after_render_callbacks'):
            self.page.after_render_callbacks.append(self.refresh_database)
        else:
            # Fallback: try to refresh after a short delay using page update
            import threading
            import time
            def delayed_refresh():
                time.sleep(0.1)  # Small delay to ensure controls are added
                if hasattr(self, 'page') and self.page:
                    try:
                        self.refresh_database()
                        self.page.update()
                    except Exception:
                        # If page update fails, that's OK - controls might not be ready yet
                        pass
            threading.Thread(target=delayed_refresh, daemon=True).start()
        
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
            
            # Force update the stats cards if they're added to the page
            try:
                if self.stats_cards.page:
                    self.stats_cards.update()
            except Exception:
                # Control not yet added to page, that's OK
                pass
            
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
                icon = "👥"  # Person icon
            elif 'file' in table_name.lower():
                icon = "📄"  # Document icon
            elif 'log' in table_name.lower():
                icon = "📝"  # Memo icon
            else:
                icon = "📊"  # Chart icon
            
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
        """Load and display table content using new table renderer."""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self._show_error("Database not available")
                return
            
            # Get table content
            columns, rows = self.server_bridge.data_manager.db_manager.get_table_content(table_name)
            
            if not columns:
                self._show_error(f"Table '{table_name}' is empty or cannot be read")
                return
            
            # Convert rows to list of dictionaries for table renderer
            table_data = []
            for row in rows[:50]:  # Limit to first 50 rows for performance
                row_dict = {col: row.get(col, '') for col in columns}
                table_data.append(row_dict)
            
            # Store current table data for bulk operations
            self.current_table_data = table_data
            
            # Update table using new renderer
            self.table_renderer.update_table_data(
                table_data=table_data,
                table_name=table_name,
                columns=columns,
                on_row_select=self._on_row_selected,
                selected_rows=self.selected_rows
            )
            
            # Update the existing table content container
            new_table_content = self.table_renderer.get_table_container()
            self.table_content_container.content = new_table_content
            self.table_content = new_table_content
            
            # Update selection UI
            self._update_bulk_actions_visibility()
            
            # Force page update to refresh the UI
            if self.page:
                self.page.update()
            
            print(f"[INFO] Loaded {len(rows)} rows from table '{table_name}'")
            
        except Exception as e:
            self._show_error(f"Failed to load table '{table_name}': {str(e)}")
            print(f"[ERROR] Failed to load table content: {e}")
    
    def backup_database(self, e):
        """Handle database backup."""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self._backup_database_async)
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
            self.page.run_task(self._optimize_database_async)
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
            self.page.run_task(self._analyze_database_async)
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
    
    def show_query_dialog(self, e):
        """Show custom SQL query dialog."""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self._show_query_dialog_async)
        else:
            # Check if we're in an async context
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(self.action_handlers.show_query_dialog())
            except RuntimeError:
                # No event loop running, skip async task creation
                pass
    
    def _on_select_all(self, e):
        """Handle select all checkbox changes."""
        try:
            if e.control.value:  # Select all
                self.table_renderer.select_all_rows()
                self.selected_rows = self.table_renderer.selected_rows.copy()
            else:  # Deselect all
                self.table_renderer.deselect_all_rows()
                self.selected_rows.clear()
            
            self._update_bulk_actions_visibility()
            if self.page:
                self.page.update()
            
        except Exception as ex:
            self._show_error(f"Error in selection: {str(ex)}")
    
    def _on_row_selected(self, e):
        """Handle individual row selection from table."""
        try:
            # Extract row_id and selection state from the event
            row_id = e.data
            selected = e.control.value if hasattr(e.control, 'value') else False
            
            if selected:
                if row_id not in self.selected_rows:
                    self.selected_rows.append(row_id)
            else:
                if row_id in self.selected_rows:
                    self.selected_rows.remove(row_id)
            
            # Update select all checkbox state
            self._update_select_all_checkbox()
            self._update_bulk_actions_visibility()
            
            if self.page:
                self.page.update()
            
        except Exception as ex:
            self._show_error(f"Error in row selection: {str(ex)}")
    
    def _update_select_all_checkbox(self):
        """Update select all checkbox based on current selection state."""
        try:
            if not self.select_all_checkbox:
                return
            
            total_rows = len(self.current_table_data)
            selected_count = len(self.selected_rows)
            
            if selected_count == 0:
                self.select_all_checkbox.value = False
            elif selected_count == total_rows:
                self.select_all_checkbox.value = True
            else:
                self.select_all_checkbox.value = None  # Indeterminate state
        except Exception:
            pass  # Ignore errors in checkbox updates
    
    def _update_bulk_actions_visibility(self):
        """Update visibility of bulk action buttons"""
        try:
            has_selections = len(self.selected_rows) > 0
            
            if self.bulk_actions_row and len(self.bulk_actions_row.controls) > 1:
                # Show/hide bulk action buttons (skip the label)
                for i, control in enumerate(self.bulk_actions_row.controls):
                    if i > 0 and isinstance(control, ft.ElevatedButton):
                        control.visible = has_selections
                
                # Force page update to show visibility changes
                if self.page:
                    self.page.update()
        except Exception:
            pass  # Ignore errors in bulk action updates
    
    def _bulk_delete_rows(self, e):
        """Handle bulk delete action for selected rows."""
        try:
            if not self.selected_rows:
                self._show_error("No rows selected")
                return
            
            # Use action handlers for bulk delete
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self.action_handlers.bulk_delete_rows(self.selected_rows))
            else:
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self.action_handlers.bulk_delete_rows(self.selected_rows))
                except RuntimeError:
                    pass
            
            # Clear selection after action
            self.selected_rows.clear()
            self._update_bulk_actions_visibility()
            
        except Exception as ex:
            self._show_error(f"Error in bulk delete: {str(ex)}")
    
    def _bulk_export_rows(self, e):
        """Handle bulk export action for selected rows."""
        try:
            if not self.selected_rows:
                self._show_error("No rows selected")
                return
            
            # Use action handlers for bulk export
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self.action_handlers.bulk_export_rows(self.selected_rows, self.selected_table))
            else:
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self.action_handlers.bulk_export_rows(self.selected_rows, self.selected_table))
                except RuntimeError:
                    pass
            
        except Exception as ex:
            self._show_error(f"Error in bulk export: {str(ex)}")
    
    def show_row_details(self, row_id: str, row_data: Dict[str, Any]):
        """Show detailed view of database row - called by table renderer."""
        try:
            # Use action handlers for row details
            if hasattr(self.page, 'run_task'):
                async def show_details_wrapper():
                    await self.action_handlers.show_row_details(row_id, row_data)
                self.page.run_task(show_details_wrapper)
            else:
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self.action_handlers.show_row_details(row_id, row_data))
                except RuntimeError:
                    pass
        except Exception as ex:
            self._show_error(f"Error showing row details: {str(ex)}")
    
    def edit_row(self, row_id: str, row_data: Dict[str, Any]):
        """Edit database row - called by table renderer."""
        try:
            # Use action handlers for row editing
            if hasattr(self.page, 'run_task'):
                async def edit_row_wrapper():
                    await self.action_handlers.edit_row(row_id, row_data)
                self.page.run_task(edit_row_wrapper)
            else:
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self.action_handlers.edit_row(row_id, row_data))
                except RuntimeError:
                    pass
        except Exception as ex:
            self._show_error(f"Error editing row: {str(ex)}")
    
    def delete_row(self, row_id: str, row_data: Dict[str, Any]):
        """Delete database row - called by table renderer."""
        try:
            # Use action handlers for row deletion
            if hasattr(self.page, 'run_task'):
                async def delete_row_wrapper():
                    await self.action_handlers.delete_row(row_id, row_data)
                self.page.run_task(delete_row_wrapper)
            else:
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self.action_handlers.delete_row(row_id, row_data))
                except RuntimeError:
                    pass
        except Exception as ex:
            self._show_error(f"Error deleting row: {str(ex)}")
    
    async def _backup_database_async(self):
        """Async wrapper for backup database."""
        await self.action_handlers.backup_database()
    
    async def _optimize_database_async(self):
        """Async wrapper for optimize database."""
        await self.action_handlers.optimize_database()
    
    async def _analyze_database_async(self):
        """Async wrapper for analyze database."""
        await self.action_handlers.analyze_database()
    
    async def _show_query_dialog_async(self):
        """Async wrapper for show query dialog."""
        await self.action_handlers.show_query_dialog()
