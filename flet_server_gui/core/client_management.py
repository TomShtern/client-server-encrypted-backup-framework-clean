"""
Purpose: Core client management operations and data processing
Logic: Handles all client-related business operations including CRUD operations, bulk actions, import/export, and client statistics
UI: None - pure business logic
Dependencies: ServerBridge for client data access, typing for type hints, asyncio for async operations, json/csv for data export/import
"""

import asyncio
import json
import csv
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ClientData:
    """Client data structure"""
    client_id: str
    name: str
    public_key_pem: Optional[str] = None
    aes_key_hex: Optional[str] = None
    status: str = "unknown"
    last_seen: Optional[str] = None
    files_count: int = 0


class ClientManagement:
    """
    Core client management class handling all client-related business operations.
    
    This class provides comprehensive client management functionality
    without UI dependencies, making it suitable for various client interfaces.
    """
    
    def __init__(self, server_bridge):
        """
        Initialize client management with server bridge dependency.
        
        Args:
            server_bridge: Server integration interface
        """
        self.server_bridge = server_bridge
        
    async def get_all_clients(self) -> Dict[str, Any]:
        """
        Get all clients from the server.
        
        Returns:
            Dictionary containing client list and metadata
        """
        try:
            clients = self.server_bridge.get_all_clients()

            # Convert to standardized format if needed
            standardized_clients = []
            for client in clients:
                client_dict = client.__dict__ if hasattr(client, '__dict__') else client
                standardized_clients.append(client_dict)

            return {
                'success': True,
                'data': standardized_clients,
                'metadata': {
                    'client_count': len(standardized_clients),
                    'operation_type': 'get_all_clients'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting clients: {str(e)}',
                'error_code': 'GET_CLIENTS_EXCEPTION'
            }
    
    async def get_client_details(self, client_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Dictionary containing client details
        """
        try:
            # Try to get client details directly if method exists
            if hasattr(self.server_bridge, 'get_client_details'):
                client_data = await self.server_bridge.get_client_details(client_id)
            else:
                # Fallback to getting all clients and filtering
                all_clients = self.server_bridge.get_all_clients()
                client_data = None
                for client in all_clients:
                    if hasattr(client, 'client_id') and client.client_id == client_id:
                        client_data = client.__dict__ if hasattr(client, '__dict__') else client
                        break
                    elif isinstance(client, dict) and client.get('client_id') == client_id:
                        client_data = client
                        break
            
            if client_data:
                return {
                    'success': True,
                    'data': client_data if isinstance(client_data, dict) else client_data.__dict__,
                    'metadata': {'client_id': client_id, 'operation_type': 'client_details'}
                }
            else:
                return {
                    'success': False,
                    'error': f'Client {client_id} not found',
                    'error_code': 'CLIENT_NOT_FOUND'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting client details for {client_id}: {str(e)}',
                'error_code': 'CLIENT_DETAILS_EXCEPTION'
            }

    async def get_client_files(self, client_id: str) -> Dict[str, Any]:
        """
        Get list of files uploaded by a specific client.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Dictionary containing client files list
        """
        try:
            # Get all files and filter by client
            all_files = self.server_bridge.get_all_files()
            client_files = []
            
            for file_obj in all_files:
                if hasattr(file_obj, 'client') and file_obj.client == client_id:
                    client_files.append(file_obj.__dict__ if hasattr(file_obj, '__dict__') else file_obj)
                elif isinstance(file_obj, dict) and file_obj.get('client') == client_id:
                    client_files.append(file_obj)
            
            return {
                'success': True,
                'data': client_files,
                'metadata': {
                    'client_id': client_id, 
                    'file_count': len(client_files),
                    'operation_type': 'client_files'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting files for client {client_id}: {str(e)}',
                'error_code': 'CLIENT_FILES_EXCEPTION'
            }
    
    async def disconnect_client(self, client_id: str) -> Dict[str, Any]:
        """
        Disconnect a single client from the server.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Dictionary containing operation result
        """
        try:
            if success := self.server_bridge.disconnect_client(client_id):
                return {
                    'success': True,
                    'data': {'client_id': client_id, 'action': 'disconnect'},
                    'metadata': {'operation_type': 'client_disconnect'}
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to disconnect client {client_id}',
                    'error_code': 'DISCONNECT_FAILED'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error disconnecting client {client_id}: {str(e)}',
                'error_code': 'DISCONNECT_EXCEPTION'
            }
    
    async def disconnect_multiple_clients(self, client_ids: List[str]) -> Dict[str, Any]:
        """
        Disconnect multiple clients with parallel execution and progress tracking.
        
        Args:
            client_ids: List of client IDs to disconnect
            
        Returns:
            Dictionary containing batch operation results
        """
        if not client_ids:
            return {
                'success': False,
                'error': 'No clients specified for disconnection',
                'error_code': 'NO_CLIENTS_SPECIFIED'
            }
        
        # Execute disconnections in parallel for better performance
        tasks = [self.disconnect_client(client_id) for client_id in client_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        successful_disconnects = 0
        failed_disconnects = 0
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_disconnects += 1
                errors.append(f'Client {client_ids[i]} disconnect failed: {str(result)}')
            elif result.get('success'):
                successful_disconnects += 1
            else:
                failed_disconnects += 1
                errors.append(f'Client {client_ids[i]}: {result.get("error", "Unknown error")}')
        
        return {
            'success': failed_disconnects == 0,
            'data': {
                'total_clients': len(client_ids),
                'successful_disconnects': successful_disconnects,
                'failed_disconnects': failed_disconnects,
                'action': 'bulk_disconnect'
            },
            'metadata': {
                'operation_type': 'bulk_client_disconnect',
                'errors': errors or None
            }
        }
    
    async def delete_client(self, client_id: str) -> Dict[str, Any]:
        """
        Permanently delete a client record.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Dictionary containing operation result
        """
        try:
            if success := self.server_bridge.delete_client(client_id):
                return {
                    'success': True,
                    'data': {'client_id': client_id, 'action': 'delete'},
                    'metadata': {'operation_type': 'client_delete', 'permanent': True}
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to delete client {client_id}',
                    'error_code': 'DELETE_FAILED'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error deleting client {client_id}: {str(e)}',
                'error_code': 'DELETE_EXCEPTION'
            }
    
    async def delete_multiple_clients(self, client_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple client records with parallel execution.
        
        Args:
            client_ids: List of client IDs to delete
            
        Returns:
            Dictionary containing batch operation results
        """
        if not client_ids:
            return {
                'success': False,
                'error': 'No clients specified for deletion',
                'error_code': 'NO_CLIENTS_SPECIFIED'
            }
        
        # Execute deletions in parallel
        tasks = [self.delete_client(client_id) for client_id in client_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        successful_deletes = 0
        failed_deletes = 0
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_deletes += 1
                errors.append(f'Client {client_ids[i]} deletion failed: {str(result)}')
            elif result.get('success'):
                successful_deletes += 1
            else:
                failed_deletes += 1
                errors.append(f'Client {client_ids[i]}: {result.get("error", "Unknown error")}')
        
        return {
            'success': failed_deletes == 0,
            'data': {
                'total_clients': len(client_ids),
                'successful_deletes': successful_deletes,
                'failed_deletes': failed_deletes,
                'action': 'bulk_delete'
            },
            'metadata': {
                'operation_type': 'bulk_client_delete',
                'errors': errors or None
            }
        }
    
    async def export_clients(self, client_ids: Optional[List[str]] = None, export_format: str = 'csv') -> Dict[str, Any]:
        """
        Export client data in specified format.
        
        Args:
            client_ids: List of client IDs to export (None = export all)
            export_format: Export format ('csv', 'json')
            
        Returns:
            Dictionary containing exported data
        """
        try:
            # Get client data
            if client_ids:
                clients_data = []
                for client_id in client_ids:
                    client_result = await self.get_client_details(client_id)
                    if client_result.get('success') and client_result.get('data'):
                        clients_data.append(client_result['data'])
            else:
                all_clients_result = await self.get_all_clients()
                if all_clients_result.get('success'):
                    clients_data = all_clients_result['data']
                else:
                    return {
                        'success': False,
                        'error': f'Failed to get client data: {all_clients_result.get("error")}',
                        'error_code': 'DATA_RETRIEVAL_FAILED'
                    }
            
            if not clients_data:
                return {
                    'success': False,
                    'error': 'No client data to export',
                    'error_code': 'NO_DATA_TO_EXPORT'
                }
            
            # Format data based on export type
            if export_format.lower() == 'csv':
                exported_data = self._format_clients_as_csv(clients_data)
            elif export_format.lower() == 'json':
                exported_data = self._format_clients_as_json(clients_data)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported export format: {export_format}',
                    'error_code': 'UNSUPPORTED_FORMAT'
                }
            
            return {
                'success': True,
                'data': exported_data,
                'metadata': {
                    'format': export_format,
                    'client_count': len(clients_data),
                    'export_timestamp': str(asyncio.get_event_loop().time())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}',
                'error_code': 'EXPORT_EXCEPTION'
            }
    
    def _format_clients_as_csv(self, clients_data: List[Dict]) -> str:
        """Format client data as CSV string."""
        if not clients_data:
            return ""
        
        # Get all unique headers from all clients
        headers = set()
        for client in clients_data:
            headers.update(client.keys())
        headers = sorted(list(headers))
        
        csv_lines = [','.join(headers)]
        
        # Add data rows
        for client in clients_data:
            row = [str(client.get(header, '')) for header in headers]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    def _format_clients_as_json(self, clients_data: List[Dict]) -> str:
        """Format client data as JSON string."""
        return json.dumps(clients_data, indent=2, default=str)
    
    async def import_clients(self, file_path: str) -> Dict[str, Any]:
        """
        Import clients from a file (JSON or CSV format).
        
        Args:
            file_path: Path to the file containing client data
            
        Returns:
            Dictionary containing import results
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'Import file not found: {file_path}',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            # Determine file format by extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.json':
                client_data_list = self._parse_json_import_file(file_path)
            elif file_extension == '.csv':
                client_data_list = self._parse_csv_import_file(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file format: {file_extension}. Supported formats: .json, .csv',
                    'error_code': 'UNSUPPORTED_FORMAT'
                }
            
            if not client_data_list:
                return {
                    'success': False,
                    'error': 'No valid client data found in import file',
                    'error_code': 'NO_DATA_FOUND'
                }
            
            # Validate required fields
            validation_result = self._validate_client_data(client_data_list)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f'Data validation failed: {", ".join(validation_result["errors"])}',
                    'error_code': 'VALIDATION_FAILED',
                    'metadata': {'validation_details': validation_result}
                }
            
            # Import clients through server bridge
            imported_count = self.server_bridge.import_clients_from_data(client_data_list)
            
            if imported_count > 0:
                return {
                    'success': True,
                    'data': {
                        'imported_clients': imported_count,
                        'total_clients_in_file': len(client_data_list),
                        'file_path': file_path,
                        'file_format': file_extension[1:]  # Remove the dot
                    },
                    'metadata': {
                        'operation_type': 'client_import',
                        'import_timestamp': str(asyncio.get_event_loop().time()),
                        'skipped_clients': len(client_data_list) - imported_count,
                        'warnings': validation_result.get('warnings', [])
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'No clients were imported (they may already exist)',
                    'error_code': 'IMPORT_FAILED',
                    'metadata': {
                        'total_clients_in_file': len(client_data_list),
                        'possible_cause': 'clients_already_exist'
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Client import failed: {str(e)}',
                'error_code': 'CLIENT_IMPORT_EXCEPTION',
                'metadata': {'file_path': file_path, 'exception_type': type(e).__name__}
            }
    
    def _parse_json_import_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse JSON client import file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data['clients'] if 'clients' in data else [data]
            else:
                raise ValueError("JSON file must contain a list of clients or a single client object")

        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON format: {str(e)}') from e
        except Exception as e:
            raise ValueError(f'Failed to parse JSON file: {str(e)}') from e
    
    def _parse_csv_import_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV client import file."""
        try:
            clients = []

            with open(file_path, 'r', encoding='utf-8') as f:
                # Auto-detect CSV dialect
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)

                reader = csv.DictReader(f, dialect=dialect)

                for row_num, row in enumerate(reader, start=2):
                    # Skip empty rows
                    if not any(row.values()):
                        continue

                    # Clean up field names and values
                    cleaned_row = {}
                    for key, value in row.items():
                        if key:
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
                                cleaned_row[clean_key] = clean_value

                    if cleaned_row.get('name'):
                        clients.append(cleaned_row)

            return clients

        except Exception as e:
            raise ValueError(f'Failed to parse CSV file: {str(e)}') from e
    
    def _validate_client_data(self, client_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate client data for import."""
        errors = []
        warnings = []
        valid_clients = []

        for i, client_data in enumerate(client_data_list):
            client_errors = []
            client_warnings = []

            # Check required fields
            name = client_data.get('name', '').strip()
            if not name:
                client_errors.append(f'Client {i+1}: Missing required "name" field')
            elif len(name) > 255:
                client_errors.append(f'Client {i+1}: Name too long (max 255 characters)')
            elif not name.replace('_', '').replace('-', '').replace(' ', '').isalnum():
                client_warnings.append(f'Client {i+1}: Name contains special characters that may cause issues')

            if public_key_pem := client_data.get('public_key_pem', '').strip():
                if not self._validate_pem_format(public_key_pem):
                    client_warnings.append(f'Client {i+1}: Public key does not appear to be valid PEM format')

            if aes_key_hex := client_data.get('aes_key_hex', '').strip():
                try:
                    bytes.fromhex(aes_key_hex)
                    key_bytes = len(aes_key_hex) // 2
                    if key_bytes not in [16, 24, 32]:  # AES-128, AES-192, AES-256
                        client_warnings.append(f'Client {i+1}: AES key length ({key_bytes} bytes) is not standard (16, 24, or 32 bytes)')
                except ValueError:
                    client_errors.append(f'Client {i+1}: AES key is not valid hexadecimal')

            if not client_errors:
                valid_clients.append(client_data)

            errors.extend(client_errors)
            warnings.extend(client_warnings)

        return {
            'valid': not errors,
            'errors': errors,
            'warnings': warnings,
            'valid_client_count': len(valid_clients),
            'total_client_count': len(client_data_list),
        }
    
    def _validate_pem_format(self, pem_data: str) -> bool:
        """Basic validation of PEM format."""
        try:
            lines = pem_data.strip().split('\n')
            if len(lines) < 3:
                return False
            
            first_line = lines[0].strip()
            last_line = lines[-1].strip()
            
            return (
                first_line.startswith('-----BEGIN ') and 
                first_line.endswith('-----') and
                last_line.startswith('-----END ') and
                last_line.endswith('-----')
            )
        except Exception:
            return False
    
    async def get_client_stats(self) -> Dict[str, Any]:
        """
        Get statistical information about clients.
        
        Returns:
            Dictionary containing client statistics
        """
        try:
            all_clients_result = await self.get_all_clients()
            if not all_clients_result.get('success'):
                return {
                    'success': False,
                    'error': f'Failed to get client data: {all_clients_result.get("error")}',
                    'error_code': 'STATS_DATA_ERROR'
                }
            
            all_clients = all_clients_result['data']
            
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
            
            return {
                'success': True,
                'data': stats,
                'metadata': {'calculated_at': str(asyncio.get_event_loop().time())}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to calculate client stats: {str(e)}',
                'error_code': 'STATS_CALCULATION_FAILED'
            }