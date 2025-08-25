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
        Import clients from a file (JSON or CSV format).
        
        Args:
            file_path: Path to the file containing client data
            
        Returns:
            ActionResult with import results
        """
        try:
            # Validate file exists
            import os
            if not os.path.exists(file_path):
                return ActionResult.error_result(
                    error_message=f"Import file not found: {file_path}",
                    error_code="FILE_NOT_FOUND"
                )
            
            # Determine file format by extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.json':
                client_data_list = await self._parse_json_import_file(file_path)
            elif file_extension == '.csv':
                client_data_list = await self._parse_csv_import_file(file_path)
            else:
                return ActionResult.error_result(
                    error_message=f"Unsupported file format: {file_extension}. Supported formats: .json, .csv",
                    error_code="UNSUPPORTED_FORMAT"
                )
            
            if not client_data_list:
                return ActionResult.error_result(
                    error_message="No valid client data found in import file",
                    error_code="NO_DATA_FOUND"
                )
            
            # Validate required fields
            validation_result = self._validate_client_data(client_data_list)
            if not validation_result['valid']:
                return ActionResult.error_result(
                    error_message=f"Data validation failed: {validation_result['errors']}",
                    error_code="VALIDATION_FAILED",
                    metadata={'validation_details': validation_result}
                )
            
            # Import clients through server bridge
            imported_count = self.server_bridge.import_clients_from_data(client_data_list)
            
            if imported_count > 0:
                return ActionResult.success_result(
                    data={
                        'imported_clients': imported_count,
                        'total_clients_in_file': len(client_data_list),
                        'file_path': file_path,
                        'file_format': file_extension[1:]  # Remove the dot
                    },
                    metadata={
                        'operation_type': 'client_import',
                        'import_timestamp': asyncio.get_event_loop().time(),
                        'skipped_clients': len(client_data_list) - imported_count
                    }
                )
            else:
                return ActionResult.error_result(
                    error_message="No clients were imported (they may already exist)",
                    error_code="IMPORT_FAILED",
                    metadata={
                        'total_clients_in_file': len(client_data_list),
                        'possible_cause': 'clients_already_exist'
                    }
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Client import failed: {str(e)}",
                error_code="CLIENT_IMPORT_EXCEPTION",
                metadata={'file_path': file_path, 'exception_type': type(e).__name__}
            )
    
    async def _parse_json_import_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse JSON client import file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of client data dictionaries
        """
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # Direct list of clients
                return data
            elif isinstance(data, dict):
                if 'clients' in data:
                    # Wrapper with 'clients' key
                    return data['clients']
                else:
                    # Single client object
                    return [data]
            else:
                raise ValueError("JSON file must contain a list of clients or a single client object")
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse JSON file: {str(e)}")
    
    async def _parse_csv_import_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse CSV client import file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of client data dictionaries
        """
        try:
            import csv
            
            clients = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # Auto-detect CSV dialect
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                
                reader = csv.DictReader(f, dialect=dialect)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Clean up field names (strip whitespace, lowercase)
                    cleaned_row = {}
                    for key, value in row.items():
                        if key:  # Skip None keys
                            clean_key = key.strip().lower()
                            clean_value = value.strip() if value else ""
                            
                            # Map common CSV column variations to standard names
                            if clean_key in ['name', 'client_name', 'clientname']:
                                cleaned_row['name'] = clean_value
                            elif clean_key in ['public_key', 'public_key_pem', 'pubkey', 'public_key_data']:
                                cleaned_row['public_key_pem'] = clean_value
                            elif clean_key in ['aes_key', 'aes_key_hex', 'aeskey', 'aes_key_data']:
                                cleaned_row['aes_key_hex'] = clean_value
                            else:
                                # Keep original key for any other fields
                                cleaned_row[clean_key] = clean_value
                    
                    if cleaned_row.get('name'):  # Only add rows with a name
                        clients.append(cleaned_row)
            
            return clients
            
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
    
    def _validate_client_data(self, client_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate client data for import.
        
        Args:
            client_data_list: List of client data dictionaries
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        valid_clients = []
        
        for i, client_data in enumerate(client_data_list):
            client_errors = []
            client_warnings = []
            
            # Check required fields
            name = client_data.get('name', '').strip()
            if not name:
                client_errors.append(f"Client {i+1}: Missing required 'name' field")
            elif len(name) > 255:
                client_errors.append(f"Client {i+1}: Name too long (max 255 characters)")
            elif not name.replace('_', '').replace('-', '').replace(' ', '').isalnum():
                client_warnings.append(f"Client {i+1}: Name contains special characters that may cause issues")
            
            # Validate public key if provided
            public_key_pem = client_data.get('public_key_pem', '').strip()
            if public_key_pem:
                if not self._validate_pem_format(public_key_pem):
                    client_warnings.append(f"Client {i+1}: Public key does not appear to be valid PEM format")
            
            # Validate AES key if provided
            aes_key_hex = client_data.get('aes_key_hex', '').strip()
            if aes_key_hex:
                try:
                    bytes.fromhex(aes_key_hex)
                    # Check if it's a reasonable length for AES key
                    key_bytes = len(aes_key_hex) // 2
                    if key_bytes not in [16, 24, 32]:  # AES-128, AES-192, AES-256
                        client_warnings.append(f"Client {i+1}: AES key length ({key_bytes} bytes) is not standard (16, 24, or 32 bytes)")
                except ValueError:
                    client_errors.append(f"Client {i+1}: AES key is not valid hexadecimal")
            
            if not client_errors:
                valid_clients.append(client_data)
            
            errors.extend(client_errors)
            warnings.extend(client_warnings)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'valid_client_count': len(valid_clients),
            'total_client_count': len(client_data_list)
        }
    
    def _validate_pem_format(self, pem_data: str) -> bool:
        """
        Basic validation of PEM format.
        
        Args:
            pem_data: PEM formatted string
            
        Returns:
            True if appears to be valid PEM format
        """
        try:
            lines = pem_data.strip().split('\n')
            if len(lines) < 3:
                return False
            
            # Check for PEM markers
            first_line = lines[0].strip()
            last_line = lines[-1].strip()
            
            return (
                first_line.startswith('-----BEGIN ') and 
                first_line.endswith('-----') and
                last_line.startswith('-----END ') and
                last_line.endswith('-----')
            )
        except:
            return False