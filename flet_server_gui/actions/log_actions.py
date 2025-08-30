"""
Log Management Actions

Pure business logic for log operations, independent of UI concerns.
"""

from typing import Dict, Any, Optional, List
from .base_action import BaseAction, ActionResult
import asyncio
import time
from datetime import datetime


class LogActions(BaseAction):
    """
    Handles all log management operations.
    
    This class encapsulates log business logic without UI dependencies,
    making it easily testable and reusable.
    """
    
    def __init__(self, server_bridge, log_service=None):
        """
        Initialize log actions with both server bridge and log service.
        
        Args:
            server_bridge: Server integration interface
            log_service: Log service for direct log operations
        """
        super().__init__(server_bridge)
        self.log_service = log_service
    
    async def export_logs(self, 
                         filter_level: str = "ALL",
                         filter_component: str = "ALL", 
                         search_query: str = "",
                         export_format: str = "txt") -> ActionResult:
        """
        Export logs with filtering options.
        
        Args:
            filter_level: Log level filter (ALL, INFO, WARN, ERROR)
            filter_component: Component filter
            search_query: Text search query
            export_format: Export format (txt, json, csv)
            
        Returns:
            ActionResult with export outcome
        """
        try:
            if self.log_service:
                # Use log service for direct log operations
                export_result = await self.log_service.export_logs(
                    filter_level=filter_level,
                    filter_component=filter_component,
                    search_query=search_query,
                    export_format=export_format
                )
            else:
                # Fallback to server bridge
                export_result = await self.server_bridge.export_logs(
                    filter_level=filter_level,
                    filter_component=filter_component,
                    search_query=search_query,
                    export_format=export_format
                )
            
            if export_result:
                return ActionResult.make_success(
                    data={
                        'action': 'export_logs',
                        'filter_level': filter_level,
                        'filter_component': filter_component,
                        'search_query': search_query,
                        'export_format': export_format,
                        'export_path': export_result.get('path'),
                        'log_count': export_result.get('count', 0),
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'log_export',
                        'format': export_format,
                        'filtered': filter_level != "ALL" or filter_component != "ALL" or search_query,
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message="Log export failed",
                    error_code="EXPORT_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error exporting logs: {str(e)}",
                error_code="EXPORT_EXCEPTION"
            )
    
    async def clear_logs(self, confirm: bool = False) -> ActionResult:
        """
        Clear the log display or log storage.
        
        Args:
            confirm: Confirmation that user wants to clear logs
            
        Returns:
            ActionResult with clear operation outcome
        """
        try:
            if not confirm:
                return ActionResult.error_result(
                    error_message="Log clearing requires confirmation",
                    error_code="CONFIRMATION_REQUIRED"
                )
            
            if self.log_service:
                # Use log service for direct log operations
                clear_result = await self.log_service.clear_logs()
            else:
                # Fallback to server bridge
                clear_result = await self.server_bridge.clear_logs()
            
            if clear_result:
                return ActionResult.make_success(
                    data={
                        'action': 'clear_logs',
                        'timestamp': time.time(),
                    },
                    metadata={
                        'operation_type': 'log_clear',
                        'timestamp': time.time(),
                    },
                )
            else:
                return ActionResult.error_result(
                    error_message="Log clearing failed",
                    error_code="CLEAR_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error clearing logs: {str(e)}",
                error_code="CLEAR_EXCEPTION"
            )
    
    async def refresh_logs(self) -> ActionResult:
        """
        Refresh the log display to show latest entries.
        
        Returns:
            ActionResult with refresh outcome
        """
        try:
            if self.log_service:
                # Use log service for direct log operations
                refresh_result = await self.log_service.refresh_logs()
                log_count = len(refresh_result) if isinstance(refresh_result, list) else 0
            else:
                # Fallback to server bridge
                refresh_result = await self.server_bridge.refresh_logs()
                log_count = refresh_result.get('count', 0) if isinstance(refresh_result, dict) else 0
            
            return ActionResult.make_success(
                data={
                    'action': 'refresh_logs',
                    'log_count': log_count,
                    'timestamp': time.time(),
                },
                metadata={
                    'operation_type': 'log_refresh',
                    'timestamp': time.time(),
                },
            )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error refreshing logs: {str(e)}",
                error_code="REFRESH_EXCEPTION"
            )
    
    async def get_log_statistics(self) -> ActionResult:
        """
        Get log statistics and metadata.
        
        Returns:
            ActionResult with log statistics
        """
        try:
            if self.log_service:
                stats = await self.log_service.get_log_statistics()
            else:
                stats = await self.server_bridge.get_log_statistics()
            
            return ActionResult.make_success(
                data={
                    'action': 'get_log_statistics',
                    'stats': stats,
                    'timestamp': time.time(),
                },
                metadata={
                    'operation_type': 'log_statistics',
                    'timestamp': time.time(),
                },
            )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error retrieving log statistics: {str(e)}",
                error_code="STATS_EXCEPTION"
            )
    
    async def filter_logs(self, 
                         level: Optional[str] = None,
                         component: Optional[str] = None,
                         search_term: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> ActionResult:
        """
        Filter logs based on various criteria.
        
        Args:
            level: Log level filter
            component: Component filter
            search_term: Text search term
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            ActionResult with filtered logs
        """
        try:
            filter_params = {
                'level': level,
                'component': component,
                'search_term': search_term,
                'start_time': start_time,
                'end_time': end_time
            }
            
            # Remove None values
            filter_params = {k: v for k, v in filter_params.items() if v is not None}
            
            if self.log_service:
                filtered_logs = await self.log_service.filter_logs(**filter_params)
            else:
                filtered_logs = await self.server_bridge.filter_logs(**filter_params)
            
            return ActionResult.make_success(
                data={
                    'action': 'filter_logs',
                    'filters': filter_params,
                    'logs': filtered_logs,
                    'log_count': len(filtered_logs) if isinstance(filtered_logs, list) else 0,
                    'timestamp': time.time(),
                },
                metadata={
                    'operation_type': 'log_filter',
                    'filter_count': len(filter_params),
                    'timestamp': time.time(),
                },
            )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error filtering logs: {str(e)}",
                error_code="FILTER_EXCEPTION"
            )
    
    async def search_logs(self, query: str, case_sensitive: bool = False) -> ActionResult:
        """
        Search logs for specific text.
        
        Args:
            query: Search query
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            ActionResult with search results
        """
        try:
            if not query or not query.strip():
                return ActionResult.error_result(
                    error_message="Search query cannot be empty",
                    error_code="EMPTY_QUERY"
                )
            
            if self.log_service:
                search_results = await self.log_service.search_logs(query, case_sensitive)
            else:
                search_results = await self.server_bridge.search_logs(query, case_sensitive)
            
            return ActionResult.make_success(
                data={
                    'action': 'search_logs',
                    'query': query,
                    'case_sensitive': case_sensitive,
                    'results': search_results,
                    'result_count': len(search_results) if isinstance(search_results, list) else 0,
                    'timestamp': time.time(),
                },
                metadata={
                    'operation_type': 'log_search',
                    'query_length': len(query),
                    'case_sensitive': case_sensitive,
                    'timestamp': time.time(),
                },
            )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error searching logs: {str(e)}",
                error_code="SEARCH_EXCEPTION"
            )
    
    async def get_recent_logs(self, count: int = 100) -> ActionResult:
        """
        Get the most recent log entries.
        
        Args:
            count: Number of recent logs to retrieve
            
        Returns:
            ActionResult with recent logs
        """
        try:
            if count <= 0:
                return ActionResult.error_result(
                    error_message="Log count must be positive",
                    error_code="INVALID_COUNT"
                )
            
            if self.log_service:
                recent_logs = await self.log_service.get_recent_logs(count)
            else:
                recent_logs = await self.server_bridge.get_recent_logs(count)
            
            return ActionResult.make_success(
                data={
                    'action': 'get_recent_logs',
                    'requested_count': count,
                    'logs': recent_logs,
                    'actual_count': len(recent_logs) if isinstance(recent_logs, list) else 0,
                    'timestamp': time.time(),
                },
                metadata={
                    'operation_type': 'log_recent',
                    'requested_count': count,
                    'timestamp': time.time(),
                },
            )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error retrieving recent logs: {str(e)}",
                error_code="RECENT_LOGS_EXCEPTION"
            )
