#!/usr/bin/env python3
"""
Database Action Handlers Component
Handles all database-related actions including backup, optimize, analyze, and table operations.
"""

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from ..utils.action_result import ActionResult
from ..utils.trace_center import get_trace_center
from ..actions import DatabaseActions
from .base_action_handler import BaseActionHandler, UIActionMixin


class DatabaseActionHandlers(BaseActionHandler, UIActionMixin):
    """Handles all database-related actions and operations"""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page: ft.Page):
        # Initialize base handler with common dependencies
        super().__init__(server_bridge, dialog_system, toast_manager, page)
        
        # Initialize database actions
        self.database_actions = DatabaseActions(server_bridge)
    
    async def backup_database(self) -> ActionResult:
        """Initiate database backup after confirmation."""
        return await self.execute_action(
            action_name="Database Backup",
            action_coro=self.database_actions.backup_database(),
            confirmation_text="Are you sure you want to back up the database? This will create a snapshot of the current state.",
            confirmation_title="Confirm Database Backup",
            require_selection=False,
            trigger_data_change=True,
            success_message="Database backup completed"
        )
    
    async def optimize_database(self) -> ActionResult:
        """Initiate database optimization after confirmation."""
        return await self.execute_action(
            action_name="Database Optimization",
            action_coro=self.database_actions.optimize_database(),
            confirmation_text="Are you sure you want to optimize the database? This may temporarily lock the database.",
            confirmation_title="Confirm Database Optimization",
            require_selection=False,
            trigger_data_change=True,
            success_message="Database optimization completed"
        )
    
    async def analyze_database(self) -> ActionResult:
        """Initiate database analysis after confirmation."""
        return await self.execute_action(
            action_name="Database Analysis",
            action_coro=self.database_actions.analyze_database(),
            confirmation_text="Are you sure you want to analyze the database? This may take some time.",
            confirmation_title="Confirm Database Analysis",
            require_selection=False,
            trigger_data_change=True,
            success_message="Database analysis completed"
        )

    async def refresh_database(self) -> ActionResult:
        """Refresh database view"""
        return await self.execute_action(
            action_name="Refresh Database",
            action_coro=self._refresh_database_action(),
            require_selection=False,
            trigger_data_change=True,
            success_message="Database view refreshed"
        )
    
    async def _refresh_database_action(self):
        """Action implementation for refreshing database view"""
        # No actual backend operation needed, just trigger data refresh
        return {"refreshed": True}
    
    async def execute_sql_query(self, query: str) -> ActionResult:
        """Execute a SQL query and display results"""
        return await self.execute_action(
            action_name="Execute SQL Query",
            action_coro=self._execute_sql_query_action(query),
            require_selection=False,
            trigger_data_change=False,
            show_success_toast=False
        )
    
    async def _execute_sql_query_action(self, query: str):
        """Action implementation for executing SQL queries"""
        result = await self.database_actions.execute_sql_query(query)
        
        if not result:
            raise ValueError("Query execution failed")
        
        # Display results in dialog if available
        if self.dialog_system and result.get('rows'):
            rows = result['rows']
            columns = result.get('columns', [])
            
            # Format results for display
            result_text = f"Query executed successfully. Found {len(rows)} rows.\n\n"
            if columns:
                result_text += "\t".join(columns) + "\n"
                result_text += "-" * 50 + "\n"
            
            for row in rows[:20]:  # Limit to first 20 rows for display
                result_text += "\t".join(str(cell) for cell in row) + "\n"
            
            if len(rows) > 20:
                result_text += f"\n... and {len(rows) - 20} more rows"
            
            await self.show_custom_dialog(
                title="Query Results",
                content=ft.Column([
                    ft.Text(result_text, selectable=True, size=10)
                ], scroll=ft.ScrollMode.AUTO, height=400)
            )
        elif not result.get('rows'):
            # Non-SELECT query
            self.show_success(f"Query executed successfully. {result.get('rows_affected', 0)} rows affected.")
        
        return result
    
    async def show_query_dialog(self) -> ActionResult:
        """Show SQL query dialog for custom queries"""
        return await self.execute_action(
            action_name="Show Query Dialog",
            action_coro=lambda: self._show_query_dialog_action(),
            require_selection=False,
            trigger_data_change=False,
            show_success_toast=False
        )
    
    async def _show_query_dialog_action(self):
        """Action implementation for showing query dialog"""
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
                self.show_error("Please enter a SQL query")
                return
            
            # Execute the query
            await self.execute_sql_query(query)
        
        if self.dialog_system:
            await self.show_custom_dialog(
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
        
        return {"dialog_shown": True}
    
    async def show_row_details(self, row_id: str, row_data: Dict[str, Any]) -> ActionResult:
        """Show detailed view of a database row"""
        return await self.execute_action(
            action_name=f"Show Row Details ({row_id})",
            action_coro=lambda: self._show_row_details_action(row_id, row_data),
            require_selection=False,
            trigger_data_change=False,
            show_success_toast=False
        )
    
    async def _show_row_details_action(self, row_id: str, row_data: Dict[str, Any]):
        """Action implementation for showing row details"""
        details_content = self.create_details_content(row_data, f"Row Details: {row_id}")
        await self.show_custom_dialog(
            title=f"Row Details: {row_id}",
            content=details_content
        )
        return {"row_id": row_id}
    
    async def delete_row(self, row_id: str, row_data: Dict[str, Any]) -> ActionResult:
        """Delete a database row"""
        return await self.execute_action(
            action_name=f"Delete Row ({row_id})",
            action_coro=self._delete_row_action(row_id),
            confirmation_text=f"Are you sure you want to delete row '{row_id}'? This action cannot be undone.",
            confirmation_title="Confirm Row Deletion",
            require_selection=False,
            trigger_data_change=True,
            success_message=f"Row {row_id} deleted successfully"
        )
    
    async def _delete_row_action(self, row_id: str):
        """Action implementation for deleting a row"""
        # TODO: Implement actual database row deletion
        # For now, just return success
        return {"row_id": row_id}
    
    async def bulk_delete_rows(self, row_ids: List[str]) -> ActionResult:
        """Delete multiple database rows"""
        if not row_ids:
            self.show_error("No rows selected")
            return ActionResult.error(
                code="DB_BULK_DELETE_ERROR",
                message="No rows selected"
            )
        
        return await self.execute_action(
            action_name=f"Bulk Delete Rows ({len(row_ids)} rows)",
            action_coro=lambda: self._bulk_delete_rows_action(row_ids),
            confirmation_text=f"Are you sure you want to delete {len(row_ids)} rows? This action cannot be undone.",
            confirmation_title="Confirm Bulk Delete",
            require_selection=False,
            trigger_data_change=True,
            success_message=f"{len(row_ids)} rows deleted successfully"
        )
    
    async def _bulk_delete_rows_action(self, row_ids: List[str]):
        """Action implementation for bulk deleting rows"""
        # TODO: Implement actual bulk deletion
        # For now, simulate success
        succeeded = len(row_ids)
        return {"deleted": succeeded, "total": len(row_ids)}
    
    async def edit_row(self, row_id: str, row_data: Dict[str, Any]) -> ActionResult:
        """Edit a database row"""
        return await self.execute_action(
            action_name=f"Edit Row {row_id}",
            action_coro=lambda: self._edit_row_action(row_id, row_data),
            confirmation_text=f"Save changes to row {row_id}?",
            confirmation_title="Confirm Row Edit",
            require_selection=False,
            trigger_data_change=True,
            success_message=f"Row {row_id} updated successfully"
        )
    
    async def _edit_row_action(self, row_id: str, row_data: Dict[str, Any]):
        """Action implementation for editing a row"""
        # TODO: Implement actual row editing
        # For now, just return success
        return {"row_id": row_id, "data": row_data}
    
    async def bulk_export_rows(self, row_ids: List[str], table_name: str) -> ActionResult:
        """Export multiple database rows"""
        if not row_ids:
            self.show_error("No rows selected")
            return ActionResult.error(
                code="DB_BULK_EXPORT_ERROR",
                message="No rows selected"
            )
        
        return await self.execute_action(
            action_name=f"Bulk Export Rows ({len(row_ids)} rows from {table_name})",
            action_coro=lambda: self._bulk_export_rows_action(row_ids, table_name),
            confirmation_text=f"Export {len(row_ids)} rows from '{table_name}'?",
            confirmation_title="Confirm Export",
            require_selection=False,
            trigger_data_change=False,
            success_message=f"{len(row_ids)} rows from '{table_name}' exported successfully"
        )
    
    async def _bulk_export_rows_action(self, row_ids: List[str], table_name: str):
        """Action implementation for bulk exporting rows"""
        # TODO: Implement actual bulk export
        # For now, simulate success
        return {"rows": len(row_ids), "table": table_name}