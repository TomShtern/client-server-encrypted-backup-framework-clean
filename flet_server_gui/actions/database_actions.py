"""
Database Management Actions

Pure business logic for database operations, independent of UI concerns.
"""

from typing import Dict, Any, Optional, List
from .base_action import BaseAction, ActionResult
import asyncio
import time


class DatabaseActions(BaseAction):
    """
    Handles all database management operations.
    
    This class encapsulates database business logic without UI dependencies,
    making it easily testable and reusable.
    """
    
    async def backup_database(self, backup_path: Optional[str] = None) -> ActionResult:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional path for backup file
            
        Returns:
            ActionResult with backup operation outcome
        """
        try:
            # Use server bridge to perform database backup
            backup_result = await self.server_bridge.backup_database(backup_path)
            
            if backup_result:
                return ActionResult.make_success(
                    data={
                        'action': 'backup_database',
                        'backup_path': backup_path or 'default',
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'database_backup',
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message="Database backup failed",
                    error_code="BACKUP_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error during database backup: {str(e)}",
                error_code="BACKUP_EXCEPTION"
            )
    
    async def optimize_database(self) -> ActionResult:
        """
        Optimize database performance and reclaim space.
        
        Returns:
            ActionResult with optimization outcome
        """
        try:
            optimization_result = await self.server_bridge.optimize_database()
            
            if optimization_result:
                return ActionResult.make_success(
                    data={
                        'action': 'optimize_database',
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'database_optimization',
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message="Database optimization failed",
                    error_code="OPTIMIZATION_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error during database optimization: {str(e)}",
                error_code="OPTIMIZATION_EXCEPTION"
            )
    
    async def analyze_database(self) -> ActionResult:
        """
        Analyze database integrity and statistics.
        
        Returns:
            ActionResult with analysis results
        """
        try:
            analysis_result = await self.server_bridge.analyze_database()
            
            if analysis_result:
                return ActionResult.make_success(
                    data={
                        'action': 'analyze_database',
                        'analysis_results': analysis_result,
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'database_analysis',
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message="Database analysis failed",
                    error_code="ANALYSIS_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error during database analysis: {str(e)}",
                error_code="ANALYSIS_EXCEPTION"
            )
    
    async def execute_sql_query(self, query: str) -> ActionResult:
        """
        Execute a SQL query on the database.
        
        Args:
            query: SQL query to execute
            
        Returns:
            ActionResult with query results
        """
        try:
            if not query or not query.strip():
                return ActionResult.error_result(
                    error_message="SQL query cannot be empty",
                    error_code="EMPTY_QUERY"
                )
            
            query_result = await self.server_bridge.execute_sql_query(query)
            
            return ActionResult.make_success(
                data={
                    'action': 'execute_sql_query',
                    'query': query,
                    'results': query_result,
                    'timestamp': time.time(),
                },
                metadata={
                    'operation_type': 'sql_execution',
                    'query_length': len(query),
                    'timestamp': time.time(),
                },
            )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error executing SQL query: {str(e)}",
                error_code="SQL_EXECUTION_EXCEPTION"
            )
    
    async def get_database_stats(self) -> ActionResult:
        """
        Get database statistics and metadata.
        
        Returns:
            ActionResult with database statistics
        """
        try:
            stats = await self.server_bridge.get_database_stats()
            
            return ActionResult.make_success(
                data={
                    'action': 'get_database_stats',
                    'stats': stats,
                    'timestamp': time.time(),
                },
                metadata={
                    'operation_type': 'database_stats',
                    'timestamp': time.time(),
                },
            )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error retrieving database stats: {str(e)}",
                error_code="STATS_EXCEPTION"
            )
    
    async def refresh_database_connection(self) -> ActionResult:
        """
        Refresh the database connection.
        
        Returns:
            ActionResult with refresh outcome
        """
        try:
            refresh_result = await self.server_bridge.refresh_database_connection()
            
            if refresh_result:
                return ActionResult.make_success(
                    data={
                        'action': 'refresh_database_connection',
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'database_refresh',
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message="Database connection refresh failed",
                    error_code="REFRESH_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error refreshing database connection: {str(e)}",
                error_code="REFRESH_EXCEPTION"
            )
    
    async def delete_database_rows(self, table_name: str, row_ids: List[str]) -> ActionResult:
        """
        Delete multiple rows from a database table.
        
        Args:
            table_name: Name of the table
            row_ids: List of row IDs to delete
            
        Returns:
            ActionResult with deletion outcome
        """
        try:
            if not row_ids:
                return ActionResult.error_result(
                    error_message="No rows specified for deletion",
                    error_code="NO_ROWS_SPECIFIED"
                )
            
            deletion_result = await self.server_bridge.delete_database_rows(table_name, row_ids)
            
            if deletion_result:
                return ActionResult.make_success(
                    data={
                        'action': 'delete_database_rows',
                        'table_name': table_name,
                        'deleted_count': len(row_ids),
                        'row_ids': row_ids,
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'database_row_deletion',
                        'table_name': table_name,
                        'row_count': len(row_ids),
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Failed to delete rows from {table_name}",
                    error_code="ROW_DELETION_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error deleting database rows: {str(e)}",
                error_code="ROW_DELETION_EXCEPTION"
            )
    
    async def export_database_table(self, table_name: str, export_format: str = "csv") -> ActionResult:
        """
        Export a database table to file.
        
        Args:
            table_name: Name of the table to export
            export_format: Export format (csv, json)
            
        Returns:
            ActionResult with export outcome
        """
        try:
            export_result = await self.server_bridge.export_database_table(table_name, export_format)
            
            if export_result:
                return ActionResult.make_success(
                    data={
                        'action': 'export_database_table',
                        'table_name': table_name,
                        'export_format': export_format,
                        'export_path': export_result.get('path'),
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'database_table_export',
                        'table_name': table_name,
                        'format': export_format,
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Failed to export table {table_name}",
                    error_code="TABLE_EXPORT_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error exporting database table: {str(e)}",
                error_code="TABLE_EXPORT_EXCEPTION"
            )
