#!/usr/bin/env python3
"""
Database Action Handlers Component
Handles all database-related actions including backup, optimize, analyze, and table operations.
"""

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable
from flet_server_gui.utils.server_bridge import ServerBridge
from flet_server_gui.utils.action_result import ActionResult
from flet_server_gui.utils.trace_center import get_trace_center
from flet_server_gui.services.confirmation_service import ConfirmationService
from flet_server_gui.actions.database_actions import DatabaseActions
from .base_action_handler import BaseActionHandler, UIActionMixin


class DatabaseActionHandlers(BaseActionHandler, UIActionMixin):
    """Handles all database-related actions and operations"""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page: ft.Page):
        # Initialize base handler with common dependencies
        super().__init__(server_bridge, dialog_system, toast_manager, page)
        
        # Initialize database actions for business logic
        self.database_actions = DatabaseActions(server_bridge)

    async def backup_database(self) -> ActionResult:
        """Initiate database backup after confirmation (async task scheduled)."""
        def schedule():
            self._close_dialog()
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_backup())
            else:
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_backup())
                except RuntimeError:
                    pass
        if self.dialog_system:
            cs = ConfirmationService(self.dialog_system)
            confirm = await cs.confirm(
                title="Confirm Database Backup",
                message="Are you sure you want to back up the database? This will create a snapshot of the current state.",
                proceed_code="DB_BACKUP_STARTED",
                proceed_message="Database backup started",
                cancel_message="Database backup cancelled"
            )
            cid = get_trace_center().new_correlation_id()
            if confirm.code == "CANCELLED":
                return ActionResult.cancelled(code="DB_BACKUP_CANCELLED", message=confirm.message, correlation_id=cid)
            schedule()
            return ActionResult.info(code="DB_BACKUP_STARTED", message="Database backup started", correlation_id=cid)
        schedule()
        cid = get_trace_center().new_correlation_id()
        return ActionResult.info(code="DB_BACKUP_STARTED", message="Database backup started", correlation_id=cid)
    
    async def _perform_backup(self) -> ActionResult:
        """Actually perform the database backup"""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                cid = get_trace_center().new_correlation_id()
                return ActionResult.error(code="DB_BACKUP_ERROR", message="Database not available", correlation_id=cid)
            
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
            get_trace_center().emit(type="DB_BACKUP", level="INFO", message="backup completed", meta={"path": backup_path})
            
            if self.on_data_changed:
                await self.on_data_changed()
            cid = get_trace_center().new_correlation_id()
            return ActionResult.make_success(code="DB_BACKUP_OK", message="Database backup completed", data={"backup_path": backup_path}, correlation_id=cid)
            
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Backup failed: {str(e)}")
            get_trace_center().emit(type="DB_BACKUP", level="ERROR", message="backup failed", meta={"error": str(e)})
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_BACKUP_ERROR", message=f"Backup failed: {e}", correlation_id=cid)
    
    async def optimize_database(self) -> ActionResult:
        """Initiate database optimization after confirmation."""
        def schedule():
            self._close_dialog()
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_optimize())
            else:
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_optimize())
                except RuntimeError:
                    pass
        if self.dialog_system:
            cs = ConfirmationService(self.dialog_system)
            confirm = await cs.confirm(
                title="Confirm Database Optimization",
                message="Are you sure you want to optimize the database? This may temporarily lock the database.",
                proceed_code="DB_OPTIMIZE_STARTED",
                proceed_message="Database optimization started",
                cancel_message="Database optimization cancelled"
            )
            cid = get_trace_center().new_correlation_id()
            if confirm.code == "CANCELLED":
                return ActionResult.cancelled(code="DB_OPTIMIZE_CANCELLED", message=confirm.message, correlation_id=cid)
            schedule()
            return ActionResult.info(code="DB_OPTIMIZE_STARTED", message="Database optimization started", correlation_id=cid)
        schedule()
        cid = get_trace_center().new_correlation_id()
        return ActionResult.info(code="DB_OPTIMIZE_STARTED", message="Database optimization started", correlation_id=cid)
    
    async def _perform_optimize(self) -> ActionResult:
        """Actually perform the database optimization"""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                cid = get_trace_center().new_correlation_id()
                return ActionResult.error(code="DB_OPTIMIZE_ERROR", message="Database not available", correlation_id=cid)
            
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
            from flet_server_gui.services.confirmation_service import ConfirmationService
            
            if self.on_data_changed:
                await self.on_data_changed()
            code = "DB_OPTIMIZE_OK" if result.get('vacuum_performed', False) else "DB_OPTIMIZE_NOOP"
            cid = get_trace_center().new_correlation_id()
            return ActionResult.make_success(code=code, message="Database optimization completed", data=result, correlation_id=cid)
            
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Optimization failed: {str(e)}")
            get_trace_center().emit(type="DB_OPTIMIZE", level="ERROR", message="optimize failed", meta={"error": str(e)})
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_OPTIMIZE_ERROR", message=f"Optimization failed: {e}", correlation_id=cid)
    
    async def analyze_database(self) -> ActionResult:
        """Initiate database analysis after confirmation."""
        def schedule():
            self._close_dialog()
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_analyze())
            else:
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_analyze())
                except RuntimeError:
                    pass
        if self.dialog_system:
            cs = ConfirmationService(self.dialog_system)
            confirm = await cs.confirm(
                title="Confirm Database Analysis",
                message="Are you sure you want to analyze the database? This may take some time.",
                proceed_code="DB_ANALYZE_STARTED",
                proceed_message="Database analysis started",
                cancel_message="Database analysis cancelled"
            )
            cid = get_trace_center().new_correlation_id()
            if confirm.code == "CANCELLED":
                return ActionResult.cancelled(code="DB_ANALYZE_CANCELLED", message=confirm.message, correlation_id=cid)
            schedule()
            return ActionResult.info(code="DB_ANALYZE_STARTED", message="Database analysis started", correlation_id=cid)
        schedule()
        cid = get_trace_center().new_correlation_id()
        return ActionResult.info(code="DB_ANALYZE_STARTED", message="Database analysis started", correlation_id=cid)

    async def _perform_analyze(self) -> ActionResult:
        """Perform database analysis work."""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                cid = get_trace_center().new_correlation_id()
                return ActionResult.error(code="DB_ANALYZE_ERROR", message="Database not available", correlation_id=cid)
            if self.dialog_system:
                self.dialog_system.show_info_dialog(title="Database Analysis", message="Analyzing database...")
            result = self.server_bridge.data_manager.db_manager.analyze_database()
            self._close_dialog()
            if result.get('integrity_check_passed', True):
                self.toast_manager.show_success("Database analysis completed successfully")
            else:
                self.toast_manager.show_warning("Database analysis completed with issues found")
            if self.dialog_system:
                details_parts = []
                for key in ["table_count", "row_count", "file_size_mb", "space_used_mb"]:
                    if key in result:
                        val = result[key]
                        if key.endswith('_mb'):
                            details_parts.append(f"{key.replace('_',' ').title()}: {val:.1f} MB")
                        else:
                            details_parts.append(f"{key.replace('_',' ').title()}: {val}")
                if details_parts:
                    self.dialog_system.show_info_dialog(title="Analysis Details", message="\n".join(details_parts))
            if self.on_data_changed:
                await self.on_data_changed()
            code = "DB_ANALYZE_OK" if result.get('integrity_check_passed', True) else "DB_ANALYZE_ISSUES"
            cid = get_trace_center().new_correlation_id()
            return ActionResult.make_success(code=code, message="Database analysis completed", data=result, correlation_id=cid)
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Analysis failed: {e}")
            get_trace_center().emit(type="DB_ANALYZE", level="ERROR", message="analyze failed", meta={"error": str(e)})
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_ANALYZE_ERROR", message=f"Analysis failed: {e}", correlation_id=cid)
    
    async def refresh_database(self) -> ActionResult:
        """Refresh database view"""
        try:
            if self.on_data_changed:
                await self.on_data_changed()
            self.toast_manager.show_success("Database view refreshed")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.make_success(code="DB_REFRESH_OK", message="Database view refreshed", correlation_id=cid)
        except Exception as e:
            self.toast_manager.show_error(f"Refresh failed: {str(e)}")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_REFRESH_ERROR", message=f"Refresh failed: {e}", correlation_id=cid)
    
    async def execute_sql_query(self, query: str) -> ActionResult:
        """Execute a SQL query and display results"""
        try:
            if not self.server_bridge.data_manager.db_manager:
                self.toast_manager.show_error("Database not available")
                return ActionResult.error(code="DB_QUERY_ERROR", message="Database not available")
            
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
                
                cid = get_trace_center().new_correlation_id()
                return ActionResult.make_success(code="DB_QUERY_OK", message="Query executed", data={"row_count": len(rows) if query.strip().upper().startswith("SELECT") else None}, correlation_id=cid)
            
            finally:
                # Return connection to pool
                self.server_bridge.data_manager.db_manager.connection_pool.return_connection(conn)
        
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Query execution failed: {str(e)}")
            get_trace_center().emit(type="DB_QUERY", level="ERROR", message="query failed", meta={"error": str(e)})
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_QUERY_ERROR", message=f"Query failed: {e}", correlation_id=cid)
    
    async def show_query_dialog(self) -> ActionResult:
        """Show SQL query dialog for custom queries"""
        try:
            # Create a simple query input dialog
            query_input = ft.TextField(
                label="SQL Query",
                multiline=True,
                min_lines=3,
                max_lines=6,
                hint_text="Enter SQL query...",
                width=500
            )
            
            async def on_execute():
                query = query_input.value.strip()
                if not query:
                    self.toast_manager.show_error("Please enter a SQL query")
                    return
                
                self._close_dialog()
                await self.execute_sql_query(query)
            
            if self.dialog_system:
                self.dialog_system.show_custom_dialog(
                    title="Execute SQL Query",
                    content=ft.Column([
                        ft.Text("Enter your SQL query below:", weight=ft.FontWeight.BOLD),
                        query_input,
                        ft.Text("Note: Queries are limited to 20 rows for display", size=11, color=ft.Colors.GREY)
                    ], spacing=10),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: self._close_dialog()),
                        ft.ElevatedButton("Execute", on_click=lambda e: self.page.run_task(on_execute()))
                    ]
                )
            
            cid = get_trace_center().new_correlation_id()
            return ActionResult.make_success(code="DB_QUERY_DIALOG", message="Query dialog shown", correlation_id=cid)
        except Exception as e:
            self.toast_manager.show_error(f"Failed to show query dialog: {str(e)}")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_QUERY_DIALOG_ERROR", message=f"Failed to show query dialog: {e}", correlation_id=cid)
    
    async def show_row_details(self, row_id: str, row_data: Dict[str, Any]) -> ActionResult:
        """Show detailed view of a database row"""
        try:
            details_content = [
                ft.Row(
                    [
                        ft.Text(
                            f"{key.replace('_', ' ').title()}:",
                            weight=ft.FontWeight.BOLD,
                            expand=1,
                        ),
                        ft.Text(str(value), selectable=True, expand=2),
                    ]
                )
                for key, value in row_data.items()
            ]
            if self.dialog_system:
                self.dialog_system.show_custom_dialog(
                    title=f"Row Details: {row_id}",
                    content=ft.Column(details_content, scroll=ft.ScrollMode.AUTO),
                    actions=[
                        ft.TextButton("Close", on_click=lambda e: self._close_dialog())
                    ]
                )

            cid = get_trace_center().new_correlation_id()
            return ActionResult.make_success(code="DB_ROW_DETAILS", message="Row details shown", data={"row_id": row_id}, correlation_id=cid)
        except Exception as e:
            self.toast_manager.show_error(f"Failed to show row details: {str(e)}")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_ROW_DETAILS_ERROR", message=f"Failed to show row details: {e}", correlation_id=cid)
    
    async def edit_row(self, row_id: str, row_data: Dict[str, Any]) -> ActionResult:
        """Edit a database row"""
        try:
            # Create edit form for row data
            edit_fields = {}
            form_content = []
            
            for key, value in row_data.items():
                if key.lower() in ['id', 'created_at', 'updated_at']:  # Skip non-editable fields
                    continue
                
                field = ft.TextField(
                    label=key.replace('_', ' ').title(),
                    value=str(value) if value is not None else "",
                    width=400
                )
                edit_fields[key] = field
                form_content.append(field)
            
            async def on_save():
                # Collect updated values
                updated_data = {}
                for key, field in edit_fields.items():
                    updated_data[key] = field.value
                
                self._close_dialog()
                
                # Implement actual database update using DatabaseActions
                try:
                    # Use the database actions to perform the update
                    result = await self.database_actions.update_database_row(row_id, updated_data, row_data.get('table', 'default'))
                    
                    if getattr(result, 'success', False):
                        self.toast_manager.show_success(f"Row {row_id} updated successfully")
                        if self.on_data_changed:
                            await self.on_data_changed()
                    else:
                        error_msg = getattr(result, 'message', 'Update failed')
                        self.toast_manager.show_error(f"Failed to update row: {error_msg}")
                        
                except AttributeError:
                    # DatabaseActions doesn't have update_database_row method yet
                    raise NotImplementedError("Row editing requires DatabaseActions.update_database_row method to be implemented")
                except Exception as e:
                    self.toast_manager.show_error(f"Failed to update row: {str(e)}")
                    raise
            
            if self.dialog_system:
                self.dialog_system.show_custom_dialog(
                    title=f"Edit Row: {row_id}",
                    content=ft.Column(form_content, scroll=ft.ScrollMode.AUTO),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: self._close_dialog()),
                        ft.ElevatedButton("Save", on_click=lambda e: self.page.run_task(on_save()))
                    ]
                )
            
            cid = get_trace_center().new_correlation_id()
            return ActionResult.make_success(code="DB_ROW_EDIT_DIALOG", message="Edit dialog shown", data={"row_id": row_id}, correlation_id=cid)
        except Exception as e:
            self.toast_manager.show_error(f"Failed to edit row: {str(e)}")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_ROW_EDIT_ERROR", message=f"Failed to edit row: {e}", correlation_id=cid)
    
    async def delete_row(self, row_id: str, row_data: Dict[str, Any]) -> ActionResult:
        """Delete a database row"""
        try:
            cs = ConfirmationService(self.dialog_system)
            confirm = await cs.confirm(
                title="Confirm Row Deletion",
                message=f"Are you sure you want to delete row '{row_id}'? This action cannot be undone.",
                proceed_code="DB_ROW_DELETE_OK",
                proceed_message="Row deletion started",
                cancel_message="Row deletion cancelled"
            )
            cid = get_trace_center().new_correlation_id()
            if confirm.code == "CANCELLED":
                return ActionResult.cancelled(code="DB_ROW_DELETE_CANCELLED", message=confirm.message, correlation_id=cid)
            
            # Implement actual database row deletion using DatabaseActions
            try:
                # Infer table name from row_data or use default
                table_name = row_data.get('table') or row_data.get('table_name') or 'default'
                
                # Use DatabaseActions to perform the deletion
                result = await self.database_actions.delete_database_rows(table_name, [row_id])
                
                if getattr(result, 'success', False):
                    self.toast_manager.show_success(f"Row {row_id} deleted successfully")
                    if self.on_data_changed:
                        await self.on_data_changed()
                    
                    data = getattr(result, 'data', {}) or {}
                    return ActionResult.make_success(
                        code="DB_ROW_DELETE_OK", 
                        message="Row deleted", 
                        data={"row_id": row_id, "table": table_name, "deleted_count": data.get('deleted_count', 1)}, 
                        correlation_id=cid
                    )
                else:
                    error_msg = getattr(result, 'message', 'Deletion failed')
                    self.toast_manager.show_error(f"Failed to delete row: {error_msg}")
                    return ActionResult.error(code="DB_ROW_DELETE_ERROR", message=f"Failed to delete row: {error_msg}", correlation_id=cid)
                    
            except Exception as delete_error:
                self.toast_manager.show_error(f"Failed to delete row: {str(delete_error)}")
                return ActionResult.error(code="DB_ROW_DELETE_ERROR", message=f"Failed to delete row: {delete_error}", correlation_id=cid)
        except Exception as e:
            self.toast_manager.show_error(f"Failed to delete row: {str(e)}")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_ROW_DELETE_ERROR", message=f"Failed to delete row: {e}", correlation_id=cid)
    
    async def bulk_delete_rows(self, row_ids: List[str]) -> ActionResult:
        """Delete multiple database rows. Returns partial if some succeed.
        Codes: DB_BULK_DELETE_OK, DB_BULK_DELETE_PARTIAL, DB_BULK_DELETE_CANCELLED"""
        try:
            if not row_ids:
                self.toast_manager.show_error("No rows selected")
                return ActionResult.error(code="DB_BULK_DELETE_ERROR", message="No rows selected")
            cs = ConfirmationService(self.dialog_system)
            confirm = await cs.confirm(
                title="Confirm Bulk Delete",
                message=f"Are you sure you want to delete {len(row_ids)} rows? This action cannot be undone.",
                proceed_code="DB_BULK_DELETE_STARTED",
                proceed_message="Bulk row deletion started",
                cancel_message="Bulk delete cancelled"
            )
            cid = get_trace_center().new_correlation_id()
            if confirm.code == "CANCELLED":
                return ActionResult.cancelled(code="DB_BULK_DELETE_CANCELLED", message=confirm.message, correlation_id=cid)
            
            # Implement actual bulk deletion using DatabaseActions
            total = len(row_ids)
            succeeded = 0
            failed = 0
            failed_items = []
            
            # Group rows by table if they contain table info, otherwise use default
            table_groups = {}
            for row_id in row_ids:
                if isinstance(row_id, dict):
                    table = row_id.get('table', 'default')
                    actual_id = row_id.get('id', row_id.get('row_id', str(row_id)))
                    table_groups.setdefault(table, []).append(actual_id)
                else:
                    table_groups.setdefault('default', []).append(str(row_id))
            
            # Process deletions per table
            for table_name, ids in table_groups.items():
                try:
                    result = await self.database_actions.delete_database_rows(table_name, ids)
                    
                    if getattr(result, 'success', False):
                        data = getattr(result, 'data', {}) or {}
                        deleted_count = data.get('deleted_count', len(ids))
                        succeeded += deleted_count
                        
                        # Track any that weren't deleted
                        if deleted_count < len(ids):
                            failed += len(ids) - deleted_count
                            for i, row_id in enumerate(ids[deleted_count:], deleted_count):
                                failed_items.append({"id": row_id, "table": table_name, "error": "Not deleted"})
                    else:
                        # All in this table failed
                        failed += len(ids)
                        error_msg = getattr(result, 'message', 'Deletion failed')
                        for row_id in ids:
                            failed_items.append({"id": row_id, "table": table_name, "error": error_msg})
                            
                except Exception as e:
                    # All in this table failed due to exception
                    failed += len(ids)
                    for row_id in ids:
                        failed_items.append({"id": row_id, "table": table_name, "error": str(e)})
            
            # Update UI state if any succeeded
            if succeeded > 0 and self.on_data_changed:
                await self.on_data_changed()
            
            # Return appropriate result based on success/failure counts
            if failed == 0:
                self.toast_manager.show_success(f"{succeeded} rows deleted successfully")
                return ActionResult.make_success(
                    code="DB_BULK_DELETE_OK", 
                    message="Rows deleted", 
                    data={"deleted": succeeded, "total": total}, 
                    correlation_id=cid
                )
            elif succeeded > 0:
                self.toast_manager.show_warning(f"{succeeded} rows deleted, {failed} failed")
                return ActionResult.make_partial(
                    code="DB_BULK_DELETE_PARTIAL", 
                    message="Partial row deletion", 
                    data={"deleted": succeeded, "failed": failed, "total": total}, 
                    failed=failed_items,
                    correlation_id=cid
                )
            else:
                self.toast_manager.show_error("All row deletions failed")
                return ActionResult.error(
                    code="DB_BULK_DELETE_ERROR", 
                    message="All deletions failed", 
                    data={"failed": failed, "total": total},
                    correlation_id=cid
                )
        except Exception as e:
            self.toast_manager.show_error(f"Failed to delete rows: {str(e)}")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_BULK_DELETE_ERROR", message=f"Failed to delete rows: {e}", correlation_id=cid)
    
    async def bulk_export_rows(self, row_ids: List[str], table_name: str) -> ActionResult:
        """Export multiple database rows.
        Codes: DB_BULK_EXPORT_OK, DB_BULK_EXPORT_ERROR"""
        try:
            if not row_ids:
                self.toast_manager.show_error("No rows selected")
                return ActionResult.error(code="DB_BULK_EXPORT_ERROR", message="No rows selected")
            cs = ConfirmationService(self.dialog_system)
            confirm = await cs.confirm(
                title="Confirm Export",
                message=f"Export {len(row_ids)} rows from '{table_name}'?",
                proceed_code="DB_BULK_EXPORT_STARTED",
                proceed_message="Bulk export started",
                cancel_message="Bulk export cancelled"
            )
            cid = get_trace_center().new_correlation_id()
            if confirm.code == "CANCELLED":
                return ActionResult.cancelled(code="DB_BULK_EXPORT_CANCELLED", message=confirm.message, correlation_id=cid)
            
            # Implement actual bulk export using DatabaseActions
            try:
                # Use DatabaseActions to export the table
                result = await self.database_actions.export_database_table(table_name, export_format='csv')
                
                if getattr(result, 'success', False):
                    data = getattr(result, 'data', {}) or {}
                    export_path = data.get('export_path')
                    
                    self.toast_manager.show_success(f"{len(row_ids)} rows from '{table_name}' exported successfully")
                    
                    return ActionResult.make_success(
                        code="DB_BULK_EXPORT_OK", 
                        message="Rows exported", 
                        data={
                            "rows_requested": len(row_ids), 
                            "table": table_name,
                            "export_path": export_path,
                            "export_format": "csv"
                        }, 
                        correlation_id=cid
                    )
                else:
                    error_msg = getattr(result, 'message', 'Export failed')
                    self.toast_manager.show_error(f"Failed to export rows: {error_msg}")
                    return ActionResult.error(
                        code="DB_BULK_EXPORT_ERROR", 
                        message=f"Failed to export rows: {error_msg}", 
                        correlation_id=cid
                    )
                    
            except Exception as export_error:
                self.toast_manager.show_error(f"Failed to export rows: {str(export_error)}")
                return ActionResult.error(
                    code="DB_BULK_EXPORT_ERROR", 
                    message=f"Failed to export rows: {export_error}", 
                    correlation_id=cid
                )
        except Exception as e:
            self.toast_manager.show_error(f"Failed to export rows: {str(e)}")
            cid = get_trace_center().new_correlation_id()
            return ActionResult.error(code="DB_BULK_EXPORT_ERROR", message=f"Failed to export rows: {e}", correlation_id=cid)
    
    def _close_dialog(self):
        """Close the current dialog"""
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog') and self.dialog_system.current_dialog:
            self.dialog_system.current_dialog.open = False
            self.page.update()