"""
File Management Actions

Pure business logic for file operations, independent of UI concerns.
"""

from typing import List, Dict, Any, Optional
from .base_action import BaseAction, ActionResult
import asyncio
import os
import hashlib
from pathlib import Path


class FileActions(BaseAction):
    """
    Handles all file-related business operations.
    
    This class encapsulates file management logic without UI dependencies,
    making it easily testable and reusable.
    """
    
    async def delete_file(self, file_id: str) -> ActionResult:
        """
        Delete a single file from server and filesystem.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            ActionResult with operation outcome
        """
        try:
            success = await self.server_bridge.delete_file(file_id)
            if success:
                return ActionResult.success_result(
                    data={'file_id': file_id, 'action': 'delete'},
                    metadata={'operation_type': 'file_delete', 'permanent': True}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Failed to delete file {file_id}",
                    error_code="DELETE_FAILED"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error deleting file {file_id}: {str(e)}",
                error_code="DELETE_EXCEPTION"
            )
    
    async def delete_multiple_files(self, file_ids: List[str]) -> ActionResult:
        """
        Delete multiple files with parallel execution and progress tracking.
        
        Args:
            file_ids: List of file IDs to delete
            
        Returns:
            ActionResult with batch operation outcome
        """
        if not file_ids:
            return ActionResult.error_result("No files specified for deletion")
        
        # Execute deletions in parallel for better performance
        tasks = [self.delete_file(file_id) for file_id in file_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ActionResult.error_result(
                    error_message=f"File {file_ids[i]} deletion failed: {str(result)}",
                    error_code="DELETE_EXCEPTION"
                ))
            else:
                processed_results.append(result)
        
        return ActionResult.from_results(processed_results)
    
    async def download_file(self, file_id: str, destination_path: str) -> ActionResult:
        """
        Download a file to specified location.
        
        Args:
            file_id: Unique identifier for the file
            destination_path: Local path where file should be saved
            
        Returns:
            ActionResult with download outcome
        """
        try:
            # Get file metadata first
            file_info = await self.server_bridge.get_file_details(file_id)
            if not file_info:
                return ActionResult.error_result(
                    error_message=f"File {file_id} not found",
                    error_code="FILE_NOT_FOUND"
                )
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Download file content
            file_content = await self.server_bridge.get_file_content(file_id)
            if file_content is None:
                return ActionResult.error_result(
                    error_message=f"Failed to retrieve content for file {file_id}",
                    error_code="CONTENT_RETRIEVAL_FAILED"
                )
            
            # Write to destination
            with open(destination_path, 'wb') as f:
                f.write(file_content)
            
            return ActionResult.success_result(
                data={
                    'file_id': file_id,
                    'destination_path': destination_path,
                    'file_size': len(file_content),
                    'file_name': file_info.get('name', 'unknown')
                },
                metadata={'operation_type': 'file_download'}
            )
            
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Download failed for file {file_id}: {str(e)}",
                error_code="DOWNLOAD_EXCEPTION"
            )
    
    async def download_multiple_files(self, file_ids: List[str], destination_dir: str) -> ActionResult:
        """
        Download multiple files to specified directory.
        
        Args:
            file_ids: List of file IDs to download
            destination_dir: Directory where files should be saved
            
        Returns:
            ActionResult with batch download outcome
        """
        if not file_ids:
            return ActionResult.error_result("No files specified for download")
        
        # Create destination directory
        os.makedirs(destination_dir, exist_ok=True)
        
        # Create download tasks
        tasks = []
        for file_id in file_ids:
            # Use file_id as filename for now, could be improved with actual filename
            destination_path = os.path.join(destination_dir, f"file_{file_id}")
            tasks.append(self.download_file(file_id, destination_path))
        
        # Execute downloads in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ActionResult.error_result(
                    error_message=f"File {file_ids[i]} download failed: {str(result)}",
                    error_code="DOWNLOAD_EXCEPTION"
                ))
            else:
                processed_results.append(result)
        
        return ActionResult.from_results(processed_results)
    
    async def verify_file_integrity(self, file_id: str) -> ActionResult:
        """
        Verify file integrity using checksum validation.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            ActionResult with verification outcome
        """
        try:
            # Get file metadata including stored checksum
            file_info = await self.server_bridge.get_file_details(file_id)
            if not file_info:
                return ActionResult.error_result(
                    error_message=f"File {file_id} not found",
                    error_code="FILE_NOT_FOUND"
                )
            
            stored_checksum = file_info.get('checksum')
            if not stored_checksum:
                return ActionResult.error_result(
                    error_message=f"No checksum available for file {file_id}",
                    error_code="CHECKSUM_MISSING"
                )
            
            # Get file content and calculate checksum
            file_content = await self.server_bridge.get_file_content(file_id)
            if file_content is None:
                return ActionResult.error_result(
                    error_message=f"Failed to retrieve content for file {file_id}",
                    error_code="CONTENT_RETRIEVAL_FAILED"
                )
            
            # Calculate SHA-256 checksum
            calculated_checksum = hashlib.sha256(file_content).hexdigest()
            
            # Compare checksums
            is_valid = calculated_checksum == stored_checksum
            
            return ActionResult.success_result(
                data={
                    'file_id': file_id,
                    'is_valid': is_valid,
                    'stored_checksum': stored_checksum,
                    'calculated_checksum': calculated_checksum,
                    'file_size': len(file_content)
                },
                metadata={
                    'operation_type': 'file_verification',
                    'algorithm': 'sha256'
                }
            )
            
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Verification failed for file {file_id}: {str(e)}",
                error_code="VERIFICATION_EXCEPTION"
            )
    
    async def verify_multiple_files(self, file_ids: List[str]) -> ActionResult:
        """
        Verify integrity of multiple files in parallel.
        
        Args:
            file_ids: List of file IDs to verify
            
        Returns:
            ActionResult with batch verification outcome
        """
        if not file_ids:
            return ActionResult.error_result("No files specified for verification")
        
        # Execute verifications in parallel
        tasks = [self.verify_file_integrity(file_id) for file_id in file_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        valid_files = 0
        invalid_files = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ActionResult.error_result(
                    error_message=f"File {file_ids[i]} verification failed: {str(result)}",
                    error_code="VERIFICATION_EXCEPTION"
                ))
            else:
                processed_results.append(result)
                if result.success and result.data.get('is_valid'):
                    valid_files += 1
                else:
                    invalid_files += 1
        
        combined_result = ActionResult.from_results(processed_results)
        
        # Add verification summary to metadata
        if combined_result.metadata is None:
            combined_result.metadata = {}
        combined_result.metadata.update({
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'total_verified': len(file_ids)
        })
        
        return combined_result
    
    async def export_file_list(self, file_ids: List[str], export_format: str = 'csv') -> ActionResult:
        """
        Export file metadata in specified format.
        
        Args:
            file_ids: List of file IDs to export (empty list = export all)
            export_format: Export format ('csv', 'json', 'xlsx')
            
        Returns:
            ActionResult with exported data
        """
        try:
            # Get file data
            if file_ids:
                files_data = []
                for file_id in file_ids:
                    file_data = await self.server_bridge.get_file_details(file_id)
                    if file_data:
                        files_data.append(file_data)
            else:
                files_data = await self.server_bridge.get_all_files()
            
            if not files_data:
                return ActionResult.error_result("No file data to export")
            
            # Format data based on export type
            if export_format.lower() == 'csv':
                exported_data = self._format_files_as_csv(files_data)
            elif export_format.lower() == 'json':
                exported_data = self._format_files_as_json(files_data)
            else:
                return ActionResult.error_result(f"Unsupported export format: {export_format}")
            
            return ActionResult.success_result(
                data=exported_data,
                metadata={
                    'format': export_format,
                    'file_count': len(files_data),
                    'export_timestamp': str(asyncio.get_event_loop().time())
                }
            )
            
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Export failed: {str(e)}",
                error_code="EXPORT_EXCEPTION"
            )
    
    def _format_files_as_csv(self, files_data: List[Dict]) -> str:
        """Format file data as CSV string."""
        if not files_data:
            return ""
        
        # Get headers from first file
        headers = list(files_data[0].keys())
        csv_lines = [','.join(headers)]
        
        # Add data rows
        for file_data in files_data:
            row = [str(file_data.get(header, '')) for header in headers]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    def _format_files_as_json(self, files_data: List[Dict]) -> str:
        """Format file data as JSON string."""
        import json
        return json.dumps(files_data, indent=2, default=str)
    
    async def cleanup_old_files(self, days_threshold: int = 30) -> ActionResult:
        """
        Clean up old files from the server based on age threshold.
        
        Args:
            days_threshold: Number of days after which files are considered old
            
        Returns:
            ActionResult with cleanup results and metadata
        """
        try:
            if not self.server_bridge or not hasattr(self.server_bridge, 'db_manager') or not self.server_bridge.db_manager:
                return ActionResult.error_result(
                    error_message="Database connection not available",
                    error_code="DB_CONNECTION_ERROR"
                )

            # Get all files from database
            all_files = self.server_bridge.db_manager.get_all_files()
            if not all_files:
                return ActionResult.success_result(
                    data={'cleaned_files': 0, 'days_threshold': days_threshold, 'total_files': 0},
                    metadata={'operation_type': 'file_cleanup', 'reason': 'no_files_found'}
                )

            # Calculate cutoff date
            import os
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            
            files_to_cleanup = []
            for file_info in all_files:
                try:
                    # Check if file exists in received_files directory
                    received_files_path = os.path.join('received_files', file_info[1])  # filename is at index 1
                    if os.path.exists(received_files_path):
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(received_files_path))
                        if file_mtime < cutoff_date:
                            files_to_cleanup.append((file_info[0], file_info[1], received_files_path))  # id, filename, path
                except (OSError, IndexError) as e:
                    # Skip files that can't be accessed or have malformed data
                    continue

            # Clean up old files
            cleaned_count = 0
            for file_id, filename, file_path in files_to_cleanup:
                try:
                    # Remove from file system
                    os.remove(file_path)
                    # Remove from database
                    self.server_bridge.db_manager.delete_file(file_id)
                    cleaned_count += 1
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Failed to cleanup file {filename}: {e}")
                    continue

            return ActionResult.success_result(
                data={
                    'cleaned_files': cleaned_count,
                    'days_threshold': days_threshold,
                    'total_files': len(all_files),
                    'eligible_for_cleanup': len(files_to_cleanup)
                },
                metadata={'operation_type': 'file_cleanup', 'cutoff_date': cutoff_date.isoformat()}
            )
            
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Cleanup failed: {str(e)}",
                error_code="CLEANUP_EXCEPTION"
            )

    async def get_file_details(self, file_id: str) -> ActionResult:
        """
        Get detailed information about a specific file.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            ActionResult with file details
        """
        try:
            # Get file details from server bridge
            file_data = await self.server_bridge.get_file_details(file_id)
            if file_data:
                return ActionResult.success_result(
                    data=file_data,
                    metadata={'file_id': file_id, 'operation_type': 'file_details'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"File {file_id} not found",
                    error_code="FILE_NOT_FOUND"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting file details for {file_id}: {str(e)}",
                error_code="FILE_DETAILS_EXCEPTION"
            )

    async def get_file_content(self, file_id: str) -> ActionResult:
        """
        Get content of a specific file.
        
        Args:
            file_id: Unique identifier for the file
            
        Returns:
            ActionResult with file content
        """
        try:
            # Get file content from server bridge
            file_content = await self.server_bridge.get_file_content(file_id)
            if file_content is not None:
                return ActionResult.success_result(
                    data=file_content,
                    metadata={'file_id': file_id, 'operation_type': 'file_content'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"File {file_id} content not available",
                    error_code="FILE_CONTENT_UNAVAILABLE"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting file content for {file_id}: {str(e)}",
                error_code="FILE_CONTENT_EXCEPTION"
            )

    # NOTE: File upload functionality is intentionally NOT implemented in the Flet GUI.
    # File uploads are handled by the C++ client with JavaScript web GUI.
    # This server management GUI only handles downloaded files, not uploads.