"""
Purpose: Core file management operations and data processing
Logic: Handles all file-related business operations including CRUD operations, bulk actions, integrity verification, download/export, and file cleanup
UI: None - pure business logic
Dependencies: ServerBridge for file data access, typing for type hints, asyncio for async operations, hashlib for integrity checks, os/pathlib for file operations
"""

import asyncio
import hashlib
import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class FileData:
    """File data structure"""
    file_id: str
    filename: str
    size: int
    checksum: Optional[str] = None
    client: Optional[str] = None
    upload_time: Optional[str] = None
    content_type: Optional[str] = None


class FileManagement:
    """
    Core file management class handling all file-related business operations.
    
    This class provides comprehensive file management functionality
    without UI dependencies, making it suitable for various client interfaces.
    """
    
    def __init__(self, server_bridge):
        """
        Initialize file management with server bridge dependency.
        
        Args:
            server_bridge: Server integration interface
        """
        self.server_bridge = server_bridge
        
    async def get_all_files(self) -> Dict[str, Any]:
        """
        Get all files from the server.
        
        Returns:
            Dictionary containing file list and metadata
        """
        try:
            files = self.server_bridge.get_all_files()
            
            # Convert to standardized format if needed
            standardized_files = []
            for file_obj in files:
                if hasattr(file_obj, '__dict__'):
                    # Convert object to dict
                    file_dict = file_obj.__dict__
                else:
                    file_dict = file_obj
                    
                standardized_files.append(file_dict)
            
            return {
                'success': True,
                'data': standardized_files,
                'metadata': {
                    'file_count': len(standardized_files),
                    'operation_type': 'get_all_files'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting files: {str(e)}',
                'error_code': 'GET_FILES_EXCEPTION'
            }
    
    async def get_file_details(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific file.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            Dictionary containing file details
        """
        try:
            # Try to get file details directly if method exists
            if hasattr(self.server_bridge, 'get_file_details'):
                file_data = await self.server_bridge.get_file_details(file_id)
            else:
                # Fallback to getting all files and filtering
                all_files = self.server_bridge.get_all_files()
                file_data = None
                for file_obj in all_files:
                    if hasattr(file_obj, 'file_id') and file_obj.file_id == file_id:
                        file_data = file_obj.__dict__ if hasattr(file_obj, '__dict__') else file_obj
                        break
                    elif isinstance(file_obj, dict) and file_obj.get('file_id') == file_id:
                        file_data = file_obj
                        break
                    elif hasattr(file_obj, 'filename') and file_obj.filename == file_id:  # Some systems use filename as ID
                        file_data = file_obj.__dict__ if hasattr(file_obj, '__dict__') else file_obj
                        break
            
            if file_data:
                return {
                    'success': True,
                    'data': file_data if isinstance(file_data, dict) else file_data.__dict__,
                    'metadata': {'file_id': file_id, 'operation_type': 'file_details'}
                }
            else:
                return {
                    'success': False,
                    'error': f'File {file_id} not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting file details for {file_id}: {str(e)}',
                'error_code': 'FILE_DETAILS_EXCEPTION'
            }

    async def get_file_content(self, file_id: str) -> Dict[str, Any]:
        """
        Get content of a specific file.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            Dictionary containing file content
        """
        try:
            # Try to get file content directly if method exists
            if hasattr(self.server_bridge, 'get_file_content'):
                file_content = self.server_bridge.get_file_content(file_id)
            else:
                # Try to read from received_files directory
                received_files_path = os.path.join('received_files', file_id)
                if os.path.exists(received_files_path):
                    with open(received_files_path, 'rb') as f:
                        file_content = f.read()
                else:
                    file_content = None
                    
            if file_content is not None:
                return {
                    'success': True,
                    'data': file_content,
                    'metadata': {
                        'file_id': file_id, 
                        'operation_type': 'file_content',
                        'content_size': len(file_content)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'File {file_id} content not available',
                    'error_code': 'FILE_CONTENT_UNAVAILABLE'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting file content for {file_id}: {str(e)}',
                'error_code': 'FILE_CONTENT_EXCEPTION'
            }
    
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a single file from server and filesystem.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Get file info first for metadata
            file_info_result = await self.get_file_details(file_id)
            file_info = file_info_result.get('data', {}) if file_info_result.get('success') else {}
            
            success = self.server_bridge.delete_file(file_info)
            if success:
                return {
                    'success': True,
                    'data': {'file_id': file_id, 'action': 'delete', 'filename': file_info.get('filename', file_id)},
                    'metadata': {'operation_type': 'file_delete', 'permanent': True}
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to delete file {file_id}',
                    'error_code': 'DELETE_FAILED'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error deleting file {file_id}: {str(e)}',
                'error_code': 'DELETE_EXCEPTION'
            }
    
    async def delete_multiple_files(self, file_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple files with parallel execution and progress tracking.
        
        Args:
            file_ids: List of file IDs to delete
            
        Returns:
            Dictionary containing batch operation results
        """
        if not file_ids:
            return {
                'success': False,
                'error': 'No files specified for deletion',
                'error_code': 'NO_FILES_SPECIFIED'
            }
        
        # Execute deletions in parallel for better performance
        tasks = [self.delete_file(file_id) for file_id in file_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        successful_deletes = 0
        failed_deletes = 0
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_deletes += 1
                errors.append(f'File {file_ids[i]} deletion failed: {str(result)}')
            elif result.get('success'):
                successful_deletes += 1
            else:
                failed_deletes += 1
                errors.append(f'File {file_ids[i]}: {result.get("error", "Unknown error")}')
        
        return {
            'success': failed_deletes == 0,
            'data': {
                'total_files': len(file_ids),
                'successful_deletes': successful_deletes,
                'failed_deletes': failed_deletes,
                'action': 'bulk_delete'
            },
            'metadata': {
                'operation_type': 'bulk_file_delete',
                'errors': errors if errors else None
            }
        }
    
    async def download_file(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """
        Download a file to specified location.
        
        Args:
            file_id: Unique identifier for the file
            destination_path: Local path where file should be saved
            
        Returns:
            Dictionary containing download result
        """
        try:
            # Get file metadata first
            file_info_result = await self.get_file_details(file_id)
            if not file_info_result.get('success'):
                return {
                    'success': False,
                    'error': f'File {file_id} not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            file_info = file_info_result['data']
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Get file content
            content_result = await self.get_file_content(file_id)
            if not content_result.get('success'):
                return {
                    'success': False,
                    'error': f'Failed to retrieve content for file {file_id}',
                    'error_code': 'CONTENT_RETRIEVAL_FAILED'
                }
            
            file_content = content_result['data']
            
            # Write to destination
            with open(destination_path, 'wb') as f:
                f.write(file_content)
            
            return {
                'success': True,
                'data': {
                    'file_id': file_id,
                    'destination_path': destination_path,
                    'file_size': len(file_content),
                    'file_name': file_info.get('filename', 'unknown')
                },
                'metadata': {'operation_type': 'file_download'}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Download failed for file {file_id}: {str(e)}',
                'error_code': 'DOWNLOAD_EXCEPTION'
            }
    
    async def download_multiple_files(self, file_ids: List[str], destination_dir: str) -> Dict[str, Any]:
        """
        Download multiple files to specified directory.
        
        Args:
            file_ids: List of file IDs to download
            destination_dir: Directory where files should be saved
            
        Returns:
            Dictionary containing batch download results
        """
        if not file_ids:
            return {
                'success': False,
                'error': 'No files specified for download',
                'error_code': 'NO_FILES_SPECIFIED'
            }
        
        # Create destination directory
        os.makedirs(destination_dir, exist_ok=True)
        
        # Create download tasks
        tasks = []
        for file_id in file_ids:
            # Get file details to use actual filename
            file_info_result = await self.get_file_details(file_id)
            if file_info_result.get('success'):
                filename = file_info_result['data'].get('filename', f'file_{file_id}')
            else:
                filename = f'file_{file_id}'
            
            destination_path = os.path.join(destination_dir, filename)
            tasks.append(self.download_file(file_id, destination_path))
        
        # Execute downloads in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_downloads = 0
        failed_downloads = 0
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_downloads += 1
                errors.append(f'File {file_ids[i]} download failed: {str(result)}')
            elif result.get('success'):
                successful_downloads += 1
            else:
                failed_downloads += 1
                errors.append(f'File {file_ids[i]}: {result.get("error", "Unknown error")}')
        
        return {
            'success': failed_downloads == 0,
            'data': {
                'total_files': len(file_ids),
                'successful_downloads': successful_downloads,
                'failed_downloads': failed_downloads,
                'destination_dir': destination_dir,
                'action': 'bulk_download'
            },
            'metadata': {
                'operation_type': 'bulk_file_download',
                'errors': errors if errors else None
            }
        }
    
    async def verify_file_integrity(self, file_id: str) -> Dict[str, Any]:
        """
        Verify file integrity using checksum validation.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            Dictionary containing verification result
        """
        try:
            # Get file metadata including stored checksum
            file_info_result = await self.get_file_details(file_id)
            if not file_info_result.get('success'):
                return {
                    'success': False,
                    'error': f'File {file_id} not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            file_info = file_info_result['data']
            stored_checksum = file_info.get('checksum')
            
            if not stored_checksum:
                return {
                    'success': False,
                    'error': f'No checksum available for file {file_id}',
                    'error_code': 'CHECKSUM_MISSING'
                }
            
            # Get file content and calculate checksum
            content_result = await self.get_file_content(file_id)
            if not content_result.get('success'):
                return {
                    'success': False,
                    'error': f'Failed to retrieve content for file {file_id}',
                    'error_code': 'CONTENT_RETRIEVAL_FAILED'
                }
            
            file_content = content_result['data']
            
            # Calculate SHA-256 checksum
            calculated_checksum = hashlib.sha256(file_content).hexdigest()
            
            # Compare checksums
            is_valid = calculated_checksum == stored_checksum
            
            return {
                'success': True,
                'data': {
                    'file_id': file_id,
                    'is_valid': is_valid,
                    'stored_checksum': stored_checksum,
                    'calculated_checksum': calculated_checksum,
                    'file_size': len(file_content),
                    'filename': file_info.get('filename', file_id)
                },
                'metadata': {
                    'operation_type': 'file_verification',
                    'algorithm': 'sha256'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Verification failed for file {file_id}: {str(e)}',
                'error_code': 'VERIFICATION_EXCEPTION'
            }
    
    async def verify_multiple_files(self, file_ids: List[str]) -> Dict[str, Any]:
        """
        Verify integrity of multiple files in parallel.
        
        Args:
            file_ids: List of file IDs to verify
            
        Returns:
            Dictionary containing batch verification results
        """
        if not file_ids:
            return {
                'success': False,
                'error': 'No files specified for verification',
                'error_code': 'NO_FILES_SPECIFIED'
            }
        
        # Execute verifications in parallel
        tasks = [self.verify_file_integrity(file_id) for file_id in file_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_verifications = 0
        failed_verifications = 0
        valid_files = 0
        invalid_files = 0
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_verifications += 1
                errors.append(f'File {file_ids[i]} verification failed: {str(result)}')
            elif result.get('success'):
                successful_verifications += 1
                if result['data'].get('is_valid'):
                    valid_files += 1
                else:
                    invalid_files += 1
            else:
                failed_verifications += 1
                errors.append(f'File {file_ids[i]}: {result.get("error", "Unknown error")}')
        
        return {
            'success': failed_verifications == 0,
            'data': {
                'total_files': len(file_ids),
                'successful_verifications': successful_verifications,
                'failed_verifications': failed_verifications,
                'valid_files': valid_files,
                'invalid_files': invalid_files,
                'action': 'bulk_verify'
            },
            'metadata': {
                'operation_type': 'bulk_file_verification',
                'errors': errors if errors else None
            }
        }
    
    async def export_file_list(self, file_ids: Optional[List[str]] = None, export_format: str = 'csv') -> Dict[str, Any]:
        """
        Export file metadata in specified format.
        
        Args:
            file_ids: List of file IDs to export (None = export all)
            export_format: Export format ('csv', 'json')
            
        Returns:
            Dictionary containing exported data
        """
        try:
            # Get file data
            if file_ids:
                files_data = []
                for file_id in file_ids:
                    file_result = await self.get_file_details(file_id)
                    if file_result.get('success') and file_result.get('data'):
                        files_data.append(file_result['data'])
            else:
                all_files_result = await self.get_all_files()
                if all_files_result.get('success'):
                    files_data = all_files_result['data']
                else:
                    return {
                        'success': False,
                        'error': f'Failed to get file data: {all_files_result.get("error")}',
                        'error_code': 'DATA_RETRIEVAL_FAILED'
                    }
            
            if not files_data:
                return {
                    'success': False,
                    'error': 'No file data to export',
                    'error_code': 'NO_DATA_TO_EXPORT'
                }
            
            # Format data based on export type
            if export_format.lower() == 'csv':
                exported_data = self._format_files_as_csv(files_data)
            elif export_format.lower() == 'json':
                exported_data = self._format_files_as_json(files_data)
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
                    'file_count': len(files_data),
                    'export_timestamp': str(asyncio.get_event_loop().time())
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}',
                'error_code': 'EXPORT_EXCEPTION'
            }
    
    def _format_files_as_csv(self, files_data: List[Dict]) -> str:
        """Format file data as CSV string."""
        if not files_data:
            return ""
        
        # Get all unique headers from all files
        headers = set()
        for file_data in files_data:
            headers.update(file_data.keys())
        headers = sorted(list(headers))
        
        csv_lines = [','.join(headers)]
        
        # Add data rows
        for file_data in files_data:
            row = [str(file_data.get(header, '')) for header in headers]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    def _format_files_as_json(self, files_data: List[Dict]) -> str:
        """Format file data as JSON string."""
        return json.dumps(files_data, indent=2, default=str)
    
    async def cleanup_old_files(self, days_threshold: int = 30) -> Dict[str, Any]:
        """
        Clean up old files from the server based on age threshold.
        
        Args:
            days_threshold: Number of days after which files are considered old
            
        Returns:
            Dictionary containing cleanup results and metadata
        """
        try:
            if not self.server_bridge or not hasattr(self.server_bridge, 'data_manager'):
                return {
                    'success': False,
                    'error': 'Database connection not available',
                    'error_code': 'DB_CONNECTION_ERROR'
                }

            # Get all files from database
            all_files_result = await self.get_all_files()
            if not all_files_result.get('success') or not all_files_result['data']:
                return {
                    'success': True,
                    'data': {'cleaned_files': 0, 'days_threshold': days_threshold, 'total_files': 0},
                    'metadata': {'operation_type': 'file_cleanup', 'reason': 'no_files_found'}
                }

            all_files = all_files_result['data']

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            
            files_to_cleanup = []
            for file_info in all_files:
                try:
                    # Check if file exists in received_files directory
                    filename = file_info.get('filename', file_info.get('name', ''))
                    if not filename:
                        continue
                        
                    received_files_path = os.path.join('received_files', filename)
                    if os.path.exists(received_files_path):
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(received_files_path))
                        if file_mtime < cutoff_date:
                            files_to_cleanup.append((
                                file_info.get('file_id', filename), 
                                filename, 
                                received_files_path
                            ))
                except (OSError, TypeError, ValueError) as e:
                    # Skip files that can't be accessed or have malformed data
                    continue

            # Clean up old files
            cleaned_count = 0
            cleanup_errors = []
            
            for file_id, filename, file_path in files_to_cleanup:
                try:
                    # Remove from file system
                    os.remove(file_path)
                    
                    # Remove from database if method available
                    if hasattr(self.server_bridge, 'delete_file'):
                        self.server_bridge.delete_file({'filename': filename, 'file_id': file_id})
                    elif hasattr(self.server_bridge, 'data_manager') and hasattr(self.server_bridge.data_manager, 'delete_file'):
                        self.server_bridge.data_manager.delete_file(file_id)
                        
                    cleaned_count += 1
                except Exception as e:
                    # Log error but continue with other files
                    cleanup_errors.append(f'Failed to cleanup file {filename}: {e}')
                    continue

            return {
                'success': True,
                'data': {
                    'cleaned_files': cleaned_count,
                    'days_threshold': days_threshold,
                    'total_files': len(all_files),
                    'eligible_for_cleanup': len(files_to_cleanup),
                    'cleanup_errors': len(cleanup_errors)
                },
                'metadata': {
                    'operation_type': 'file_cleanup', 
                    'cutoff_date': cutoff_date.isoformat(),
                    'errors': cleanup_errors if cleanup_errors else None
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Cleanup failed: {str(e)}',
                'error_code': 'CLEANUP_EXCEPTION'
            }

    def get_file_statistics(self, files_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Calculate file statistics.
        
        Args:
            files_data: Optional list of file data (if None, gets all files)
            
        Returns:
            Dictionary containing file statistics
        """
        try:
            if files_data is None:
                all_files_result = asyncio.run(self.get_all_files())
                if not all_files_result.get('success'):
                    return {'total_files': 0, 'total_size': 0, 'total_size_formatted': '0 B'}
                files_data = all_files_result['data']
            
            total_files = len(files_data)
            total_size = 0
            file_types = {}
            clients = set()
            
            for file_data in files_data:
                # Calculate size
                size = file_data.get('size', 0)
                if isinstance(size, (int, float)):
                    total_size += size
                elif isinstance(size, str) and size.isdigit():
                    total_size += int(size)
                
                # Count file types
                filename = file_data.get('filename', '')
                if '.' in filename:
                    ext = filename.split('.')[-1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                
                # Count unique clients
                client = file_data.get('client')
                if client:
                    clients.add(client)
            
            # Format size
            total_size_formatted = self._format_file_size(total_size)
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_formatted': total_size_formatted,
                'file_types': file_types,
                'unique_clients': len(clients),
                'average_file_size': total_size / total_files if total_files > 0 else 0
            }
            
        except Exception as e:
            return {
                'total_files': 0,
                'total_size': 0,
                'total_size_formatted': '0 B',
                'error': str(e)
            }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    # File upload functionality is intentionally NOT implemented in the server GUI.
    # File uploads are handled by the C++ client with JavaScript web GUI.
    # This server management GUI only handles downloaded/received files, not uploads.
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage-related statistics."""
        try:
            received_files_dir = 'received_files'
            if not os.path.exists(received_files_dir):
                return {
                    'directory_exists': False,
                    'total_files': 0,
                    'total_size': 0,
                    'total_size_formatted': '0 B'
                }
            
            total_files = 0
            total_size = 0
            
            for filename in os.listdir(received_files_dir):
                file_path = os.path.join(received_files_dir, filename)
                if os.path.isfile(file_path):
                    total_files += 1
                    total_size += os.path.getsize(file_path)
            
            return {
                'directory_exists': True,
                'total_files': total_files,
                'total_size': total_size,
                'total_size_formatted': self._format_file_size(total_size),
                'directory_path': os.path.abspath(received_files_dir)
            }
            
        except Exception as e:
            return {
                'directory_exists': False,
                'error': str(e),
                'total_files': 0,
                'total_size': 0,
                'total_size_formatted': '0 B'
            }