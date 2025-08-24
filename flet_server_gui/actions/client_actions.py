"""
Client Management Actions

Pure business logic for client operations, independent of UI concerns.
"""

from typing import List, Dict, Any
from .base_action import BaseAction, ActionResult
import asyncio


class ClientActions(BaseAction):
    """
    Handles all client-related business operations.
    
    This class encapsulates client management logic without UI dependencies,
    making it easily testable and reusable.
    """
    
    async def disconnect_client(self, client_id: str) -> ActionResult:
        """
        Disconnect a single client from the server.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with operation outcome
        """
        try:
            success = await self.server_bridge.disconnect_client(client_id)
            if success:
                return ActionResult.success_result(
                    data={'client_id': client_id, 'action': 'disconnect'},
                    metadata={'operation_type': 'client_disconnect'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Failed to disconnect client {client_id}",
                    error_code="DISCONNECT_FAILED"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error disconnecting client {client_id}: {str(e)}",
                error_code="DISCONNECT_EXCEPTION"
            )
    
    async def disconnect_multiple_clients(self, client_ids: List[str]) -> ActionResult:
        """
        Disconnect multiple clients with parallel execution and progress tracking.
        
        Args:
            client_ids: List of client IDs to disconnect
            
        Returns:
            ActionResult with batch operation outcome
        """
        if not client_ids:
            return ActionResult.error_result("No clients specified for disconnection")
        
        # Execute disconnections in parallel for better performance
        tasks = [self.disconnect_client(client_id) for client_id in client_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ActionResult.error_result(
                    error_message=f"Client {client_ids[i]} disconnect failed: {str(result)}",
                    error_code="DISCONNECT_EXCEPTION"
                ))
            else:
                processed_results.append(result)
        
        return ActionResult.from_results(processed_results)
    
    async def delete_client(self, client_id: str) -> ActionResult:
        """
        Permanently delete a client record.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with operation outcome
        """
        try:
            success = await self.server_bridge.delete_client(client_id)
            if success:
                return ActionResult.success_result(
                    data={'client_id': client_id, 'action': 'delete'},
                    metadata={'operation_type': 'client_delete', 'permanent': True}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Failed to delete client {client_id}",
                    error_code="DELETE_FAILED"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error deleting client {client_id}: {str(e)}",
                error_code="DELETE_EXCEPTION"
            )
    
    async def delete_multiple_clients(self, client_ids: List[str]) -> ActionResult:
        """
        Delete multiple client records with parallel execution.
        
        Args:
            client_ids: List of client IDs to delete
            
        Returns:
            ActionResult with batch operation outcome
        """
        if not client_ids:
            return ActionResult.error_result("No clients specified for deletion")
        
        # Execute deletions in parallel
        tasks = [self.delete_client(client_id) for client_id in client_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ActionResult.error_result(
                    error_message=f"Client {client_ids[i]} deletion failed: {str(result)}",
                    error_code="DELETE_EXCEPTION"
                ))
            else:
                processed_results.append(result)
        
        return ActionResult.from_results(processed_results)
    
    async def export_clients(self, client_ids: List[str], export_format: str = 'csv') -> ActionResult:
        """
        Export client data in specified format.
        
        Args:
            client_ids: List of client IDs to export (empty list = export all)
            export_format: Export format ('csv', 'json', 'xlsx')
            
        Returns:
            ActionResult with exported data or file path
        """
        try:
            # Get client data from server bridge
            if client_ids:
                clients_data = []
                for client_id in client_ids:
                    client_data = await self.server_bridge.get_client_details(client_id)
                    if client_data:
                        clients_data.append(client_data)
            else:
                clients_data = await self.server_bridge.get_all_clients()
            
            if not clients_data:
                return ActionResult.error_result("No client data to export")
            
            # Format data based on export type
            if export_format.lower() == 'csv':
                exported_data = self._format_clients_as_csv(clients_data)
            elif export_format.lower() == 'json':
                exported_data = self._format_clients_as_json(clients_data)
            else:
                return ActionResult.error_result(f"Unsupported export format: {export_format}")
            
            return ActionResult.success_result(
                data=exported_data,
                metadata={
                    'format': export_format,
                    'client_count': len(clients_data),
                    'export_timestamp': str(asyncio.get_event_loop().time())
                }
            )
            
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Export failed: {str(e)}",
                error_code="EXPORT_EXCEPTION"
            )
    
    def _format_clients_as_csv(self, clients_data: List[Dict]) -> str:
        """Format client data as CSV string."""
        if not clients_data:
            return ""
        
        # Get headers from first client
        headers = list(clients_data[0].keys())
        csv_lines = [','.join(headers)]
        
        # Add data rows
        for client in clients_data:
            row = [str(client.get(header, '')) for header in headers]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    def _format_clients_as_json(self, clients_data: List[Dict]) -> str:
        """Format client data as JSON string."""
        import json
        return json.dumps(clients_data, indent=2, default=str)
    
    async def get_client_stats(self) -> ActionResult:
        """
        Get statistical information about clients.
        
        Returns:
            ActionResult with client statistics
        """
        try:
            all_clients = await self.server_bridge.get_all_clients()
            
            stats = {
                'total_clients': len(all_clients),
                'active_clients': len([c for c in all_clients if c.get('status') == 'connected']),
                'inactive_clients': len([c for c in all_clients if c.get('status') != 'connected']),
                'clients_by_status': {}
            }
            
            # Count clients by status
            for client in all_clients:
                status = client.get('status', 'unknown')
                stats['clients_by_status'][status] = stats['clients_by_status'].get(status, 0) + 1
            
            return ActionResult.success_result(
                data=stats,
                metadata={'calculated_at': str(asyncio.get_event_loop().time())}
            )
            
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Failed to calculate client stats: {str(e)}",
                error_code="STATS_CALCULATION_FAILED"
            )

    async def get_client_details(self, client_id: str) -> ActionResult:
        """
        Get detailed information about a specific client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with client details
        """
        try:
            # Get client details from server bridge
            client_data = await self.server_bridge.get_client_details(client_id)
            if client_data:
                return ActionResult.success_result(
                    data=client_data,
                    metadata={'client_id': client_id, 'operation_type': 'client_details'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Client {client_id} not found",
                    error_code="CLIENT_NOT_FOUND"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting client details for {client_id}: {str(e)}",
                error_code="CLIENT_DETAILS_EXCEPTION"
            )

    async def get_client_files(self, client_id: str) -> ActionResult:
        """
        Get list of files uploaded by a specific client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with client files list
        """
        try:
            # Get all files and filter by client
            all_files = await self.server_bridge.get_file_list()
            client_files = [f for f in all_files if f.get('client') == client_id]
            
            return ActionResult.success_result(
                data=client_files,
                metadata={
                    'client_id': client_id, 
                    'file_count': len(client_files),
                    'operation_type': 'client_files'
                }
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting files for client {client_id}: {str(e)}",
                error_code="CLIENT_FILES_EXCEPTION"
            )

    async def import_clients(self, file_path: str) -> ActionResult:
        """
        Import clients from a file.
        
        Args:
            file_path: Path to the file containing client data
            
        Returns:
            ActionResult with import results
        """
        try:
            # This would be implemented based on server bridge capabilities
            # For now, return a placeholder result
            return ActionResult.success_result(
                data={'imported_clients': 0, 'file_path': file_path},
                metadata={'operation_type': 'client_import', 'implemented': False}
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Client import failed: {str(e)}",
                error_code="CLIENT_IMPORT_EXCEPTION"
            )