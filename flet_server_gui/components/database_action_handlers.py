#!/usr/bin/env python3
"""
Database Action Handlers Component
Handles all database-related actions including backup, optimize, analyze, and table operations.
"""

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable
from flet_server_gui.utils.server_bridge import ServerBridge


class DatabaseActionHandlers:
    """Handles all database-related actions and operations"""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page: ft.Page):
        self.server_bridge = server_bridge
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.page = page
        
        # Callbacks for parent component
        self.on_data_changed: Optional[Callable] = None
    
    def set_data_changed_callback(self, callback: Callable):
        """Set callback for when data changes and refresh is needed"""
        self.on_data_changed = callback
    
    async def backup_database(self) -> bool:
        """Backup database with confirmation"""
        def confirm_backup():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_backup())
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_backup())
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        # Show confirmation dialog
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title="Confirm Database Backup",
                message="Are you sure you want to backup the database? This will create a copy of the current database state."
            )
            if confirmed:
                confirm_backup()
        else:
            confirm_backup()
    
    async def _perform_backup(self) -> bool:
        """Actually perform the database backup"""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                return False
            
            # Show progress dialog
            self.dialog_system.show_info_dialog(
                title="Database Backup",
                message="Backing up database..."
            )
            
            # Perform backup
            backup_path = self.server_bridge.data_manager.db_manager.backup_database_to_file()
            
            # Close progress dialog
            self._close_dialog()
            
            self.toast_manager.show_success(f"Database backed up to: {backup_path}")
            print(f"[INFO] Database backed up to: {backup_path}")
            
            if self.on_data_changed:
                await self.on_data_changed()
                
            return True
            
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Backup failed: {str(e)}")
            print(f"[ERROR] Database backup failed: {e}")
            return False
    
    async def optimize_database(self) -> bool:
        """Optimize database with confirmation"""
        def confirm_optimize():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_optimize())
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_optimize())
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        # Show confirmation dialog
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title="Confirm Database Optimization",
                message="Are you sure you want to optimize the database? This will reclaim unused space and improve performance."
            )
            if confirmed:
                confirm_optimize()
        else:
            confirm_optimize()
    
    async def _perform_optimize(self) -> bool:
        """Actually perform the database optimization"""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                return False
            
            # Show progress dialog
            self.dialog_system.show_info_dialog(
                title="Database Optimization",
                message="Optimizing database..."
            )
            
            # Perform optimization
            result = self.server_bridge.data_manager.db_manager.optimize_database()
            
            # Close progress dialog
            self._close_dialog()
            
            space_saved = result.get('space_saved_mb', 0)
            if result.get('vacuum_performed', False):
                self.toast_manager.show_success(f"Database optimized successfully! Space saved: {space_saved:.1f} MB")
            else:
                self.toast_manager.show_info("Database optimization completed (no vacuum needed)")
            
            if self.on_data_changed:
                await self.on_data_changed()
                
            return True
            
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Optimization failed: {str(e)}")
            print(f"[ERROR] Database optimization failed: {e}")
            return False
    
    async def analyze_database(self) -> bool:
        """Analyze database with confirmation"""
        def confirm_analyze():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_analyze())
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_analyze())
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        # Show confirmation dialog
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title="Confirm Database Analysis",
                message="Are you sure you want to analyze the database? This will check for integrity issues and provide statistics."
            )
            if confirmed:
                confirm_analyze()
        else:
            confirm_analyze()
    
    async def _perform_analyze(self) -> bool:
        """Actually perform the database analysis"""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                return False
            
            # Show progress dialog
            self.dialog_system.show_info_dialog(
                title="Database Analysis",
                message="Analyzing database..."
            )
            
            # Perform analysis
            result = self.server_bridge.data_manager.db_manager.analyze_database()
            
            # Close progress dialog
            self._close_dialog()
            
            if result.get('integrity_check_passed', True):
                self.toast_manager.show_success("Database analysis completed successfully!")
            else:
                self.toast_manager.show_warning("Database analysis completed with issues found")
            
            # Show detailed results in a dialog
            details = []
            if 'table_count' in result:
                details.append(f"Tables: {result['table_count']}")
            if 'row_count' in result:
                details.append(f"Total Rows: {result['row_count']}")
            if 'file_size_mb' in result:
                details.append(f"File Size: {result['file_size_mb']:.1f} MB")
            if 'space_used_mb' in result:
                details.append(f"Space Used: {result['space_used_mb']:.1f} MB")
            
            if details:
                self.dialog_system.show_info_dialog(
                    title="Database Analysis Results",
                    message="\\n".join(details)
                )
            
            if self.on_data_changed:
                await self.on_data_changed()
                
            return True
            
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Analysis failed: {str(e)}")
            print(f"[ERROR] Database analysis failed: {e}")
            return False
    
    async def refresh_database(self) -> bool:
        """Refresh database view"""
        try:
            if self.on_data_changed:
                await self.on_data_changed()
            self.toast_manager.show_success("Database view refreshed")
            return True
        except Exception as e:
            self.toast_manager.show_error(f"Refresh failed: {str(e)}")
            return False
    
    async def execute_sql_query(self, query: str) -> bool:
        """Execute a SQL query and display results"""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                return False
            
            # Show progress dialog
            self.dialog_system.show_info_dialog(
                title="Executing Query",
                message="Executing SQL query..."
            )
            
            # Get database connection and execute query
            conn = self.server_bridge.data_manager.db_manager.connection_pool.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # If it's a SELECT query, fetch results
                if query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    # Close progress dialog
                    self._close_dialog()
                    
                    # Display results in a dialog
                    if rows:
                        # Format results for display
                        result_text = f"Query executed successfully. Found {len(rows)} rows.\n\n"
                        if columns:
                            result_text += "\t".join(columns) + "\n"
                            result_text += "-" * 50 + "\n"
                        
                        for row in rows[:20]:  # Limit to first 20 rows for display
                            result_text += "\t".join(str(cell) for cell in row) + "\n"
                        
                        if len(rows) > 20:
                            result_text += f"\n... and {len(rows) - 20} more rows"
                        
                        self.dialog_system.show_info_dialog(
                            title="Query Results",
                            message=result_text
                        )
                    else:
                        self.dialog_system.show_info_dialog(
                            title="Query Results",
                            message="Query executed successfully. No rows returned."
                        )
                else:
                    # For non-SELECT queries, commit and show success message
                    conn.commit()
                    self._close_dialog()
                    self.toast_manager.show_success("Query executed successfully")
                
                # Refresh database view
                if self.on_data_changed:
                    await self.on_data_changed()
                
                return True
            
            finally:
                # Return connection to pool
                self.server_bridge.data_manager.db_manager.connection_pool.return_connection(conn)
        
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Query execution failed: {str(e)}")
            print(f"[ERROR] SQL query execution failed: {e}")
            return False
    
    def _close_dialog(self):
        """Close the current dialog"""
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog'):
            if self.dialog_system.current_dialog:
                self.dialog_system.current_dialog.open = False
                self.page.update()