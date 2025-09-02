#!/usr/bin/env python3
"""
File Operations Manager
Consolidates file management operations and file filtering UI.
Eliminates file-related manager duplication following Duplication Mindset principles.

Unified Responsibilities:
- File operations (download, verify, upload, cleanup)  
- File UI filtering and searching
- File storage statistics and management
- Database integration for file records

Follows Single Responsibility Principle: ONE manager for ALL file-related concerns.
Uses Flet framework patterns for UI filtering instead of custom implementations.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import sys
import os
import shutil
import flet as ft
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    from python_server.server.database import DatabaseManager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("[WARNING] Database integration not available for file operations")

# Import our unified filter manager
from .unified_filter_manager import UnifiedFilterManager, FilterDataType


class FileOperation(Enum):
    """File operation types for tracking and logging"""
    DOWNLOAD = "download"
    VERIFY = "verify"
    UPLOAD = "upload"
    CLEANUP = "cleanup"
    DELETE = "delete"


class FileOperationsManager:
    """
    Unified manager for all file operations and UI filtering.
    Consolidates file_manager.py and file_filter_manager.py responsibilities.
    """
    
    def __init__(self, page: ft.Page, received_files_path: str = "received_files", toast_manager=None):
        self.page = page
        self.received_files_path = received_files_path
        self.toast_manager = toast_manager
        
        # Database manager for file records
        self.db_manager = None
        
        # Ensure received files directory exists
        os.makedirs(self.received_files_path, exist_ok=True)
        
        # Initialize database connection if available
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = DatabaseManager()
                print("[INFO] File manager database connection established")
            except Exception as e:
                print(f"[WARNING] File manager database initialization failed: {e}")
        
        # Unified filter manager for file filtering UI
        self.filter_manager = UnifiedFilterManager(page, FilterDataType.FILES, toast_manager)
        
        # Current file data for filtering
        self._current_files = []
        
        # Operation history for tracking
        self._operation_history = []
    
    # =====================
    # File Operations API
    # =====================
    
    def download_file(self, file_info: Dict[str, Any], destination_path: str) -> bool:
        """Download/copy a file to specified destination"""
        try:
            filename = file_info.get('filename')
            if not filename:
                self._log_operation(FileOperation.DOWNLOAD, filename, False, "No filename provided")
                return False
            
            source_path = os.path.join(self.received_files_path, filename)
            
            if not os.path.exists(source_path):
                self._log_operation(FileOperation.DOWNLOAD, filename, False, f"Source file does not exist: {source_path}")
                return False
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy file to destination
            shutil.copy2(source_path, destination_path)
            self._log_operation(FileOperation.DOWNLOAD, filename, True, f"File copied to: {destination_path}")
            
            # Show success feedback
            if self.toast_manager:
                self.toast_manager.show_success(f"Downloaded: {filename}")
            
            return True
            
        except Exception as e:
            self._log_operation(FileOperation.DOWNLOAD, filename, False, f"Failed to download file: {e}")
            if self.toast_manager:
                self.toast_manager.show_error(f"Download failed: {str(e)}")
            return False
    
    def verify_file(self, file_info: Dict[str, Any]) -> bool:
        """Verify file integrity and existence"""
        try:
            filename = file_info.get('filename')
            expected_size = file_info.get('size', 0)
            
            if not filename:
                self._log_operation(FileOperation.VERIFY, filename, False, "No filename provided")
                return False
            
            file_path = os.path.join(self.received_files_path, filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                self._log_operation(FileOperation.VERIFY, filename, False, f"File does not exist: {filename}")
                return False
            
            # Check file size
            actual_size = os.path.getsize(file_path)
            if expected_size > 0 and actual_size != expected_size:
                error_msg = f"File size mismatch for {filename}: expected {expected_size}, got {actual_size}"
                self._log_operation(FileOperation.VERIFY, filename, False, error_msg)
                return False
            
            # Additional integrity checks could be added here (checksums, etc.)
            self._log_operation(FileOperation.VERIFY, filename, True, f"File verification passed: {filename}")
            
            if self.toast_manager:
                self.toast_manager.show_success(f"Verified: {filename}")
            
            return True
            
        except Exception as e:
            self._log_operation(FileOperation.VERIFY, filename, False, f"Failed to verify file: {e}")
            if self.toast_manager:
                self.toast_manager.show_error(f"Verification failed: {str(e)}")
            return False
    
    def upload_file_to_storage(self, file_path: str, client_name: str = "system") -> bool:
        """Upload a file to server storage"""
        try:
            if not os.path.exists(file_path):
                self._log_operation(FileOperation.UPLOAD, file_path, False, f"Source file does not exist: {file_path}")
                return False
            
            filename = os.path.basename(file_path)
            destination_path = os.path.join(self.received_files_path, filename)
            
            # Copy file to storage
            shutil.copy2(file_path, destination_path)
            
            # Record in database if available
            if self.db_manager:
                try:
                    file_stats = os.stat(destination_path)
                    self.db_manager.add_file_record({
                        'filename': filename,
                        'size': file_stats.st_size,
                        'client_name': client_name,
                        'upload_time': datetime.now(),
                        'file_path': destination_path
                    })
                except Exception as e:
                    print(f"[WARNING] Could not record file in database: {e}")
            
            self._log_operation(FileOperation.UPLOAD, filename, True, f"File uploaded to storage: {filename}")
            
            # Refresh file list for filtering
            self._refresh_file_data()
            
            if self.toast_manager:
                self.toast_manager.show_success(f"Uploaded: {filename}")
            
            return True
            
        except Exception as e:
            self._log_operation(FileOperation.UPLOAD, file_path, False, f"Failed to upload file: {e}")
            if self.toast_manager:
                self.toast_manager.show_error(f"Upload failed: {str(e)}")
            return False
    
    def cleanup_old_files_by_age(self, days_threshold: int) -> Dict[str, Any]:
        """Clean up files older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_threshold)
            deleted_files = []
            total_size_freed = 0
            
            for filename in os.listdir(self.received_files_path):
                file_path = os.path.join(self.received_files_path, filename)
                
                if os.path.isfile(file_path):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted_files.append({
                                'filename': filename,
                                'size': file_size,
                                'modified_date': file_mtime.isoformat()
                            })
                            total_size_freed += file_size
                            
                            # Remove from database if available
                            if self.db_manager:
                                try:
                                    self.db_manager.delete_file_record(filename)
                                except Exception as e:
                                    print(f"[WARNING] Could not remove {filename} from database: {e}")
                                    
                        except Exception as e:
                            print(f"[WARNING] Could not delete file {filename}: {e}")
            
            result = {
                'deleted_count': len(deleted_files),
                'total_size_freed': total_size_freed,
                'deleted_files': deleted_files,
                'days_threshold': days_threshold
            }
            
            self._log_operation(FileOperation.CLEANUP, f"{len(deleted_files)} files", True, 
                              f"Cleanup completed: {len(deleted_files)} files removed, {total_size_freed} bytes freed")
            
            # Refresh file list for filtering
            self._refresh_file_data()
            
            if self.toast_manager:
                self.toast_manager.show_success(f"Cleanup: {len(deleted_files)} files removed")
            
            return result
            
        except Exception as e:
            self._log_operation(FileOperation.CLEANUP, "batch", False, f"Failed to cleanup old files: {e}")
            if self.toast_manager:
                self.toast_manager.show_error(f"Cleanup failed: {str(e)}")
            return {
                'deleted_count': 0,
                'total_size_freed': 0,
                'deleted_files': [],
                'error': str(e)
            }
    
    def delete_file(self, filename: str) -> bool:
        """Delete a specific file"""
        try:
            file_path = os.path.join(self.received_files_path, filename)
            
            if not os.path.exists(file_path):
                self._log_operation(FileOperation.DELETE, filename, False, f"File not found: {filename}")
                return False
            
            # Get file size before deletion for logging
            file_size = os.path.getsize(file_path)
            
            # Remove file
            os.remove(file_path)
            
            # Remove from database if available
            if self.db_manager:
                try:
                    self.db_manager.delete_file_record(filename)
                except Exception as e:
                    print(f"[WARNING] Could not remove {filename} from database: {e}")
            
            self._log_operation(FileOperation.DELETE, filename, True, 
                              f"File deleted: {filename} ({self._format_file_size(file_size)})")
            
            # Refresh file list for filtering
            self._refresh_file_data()
            
            if self.toast_manager:
                self.toast_manager.show_success(f"Deleted: {filename}")
            
            return True
            
        except Exception as e:
            self._log_operation(FileOperation.DELETE, filename, False, f"Failed to delete file: {e}")
            if self.toast_manager:
                self.toast_manager.show_error(f"Delete failed: {str(e)}")
            return False
    
    def get_file_content(self, filename: str) -> bytes:
        """Get file content for preview"""
        try:
            file_path = os.path.join(self.received_files_path, filename)
            
            if not os.path.exists(file_path):
                print(f"[ERROR] File not found: {filename}")
                return b''
            
            with open(file_path, 'rb') as f:
                content = f.read()
                
            print(f"[SUCCESS] Read {len(content)} bytes from {filename}")
            return content
            
        except Exception as e:
            print(f"[ERROR] Failed to read file content: {e}")
            return b''
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_files = 0
            total_size = 0
            file_types = {}
            
            for filename in os.listdir(self.received_files_path):
                file_path = os.path.join(self.received_files_path, filename)
                
                if os.path.isfile(file_path):
                    total_files += 1
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    # Track file types
                    extension = filename.split('.')[-1].lower() if '.' in filename else 'no_extension'
                    file_types[extension] = file_types.get(extension, 0) + 1
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_formatted': self._format_file_size(total_size),
                'file_types': file_types,
                'storage_path': self.received_files_path
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get storage stats: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'total_size_formatted': '0 B',
                'file_types': {},
                'storage_path': self.received_files_path,
                'error': str(e)
            }
    
    # =====================
    # File Filtering UI API
    # =====================
    
    def create_file_filter_controls(self, on_filter_change_callback: Callable) -> ft.Column:
        """Create file filtering UI controls using unified filter manager"""
        return self.filter_manager.create_search_controls(on_filter_change_callback)
    
    def set_file_data_for_filtering(self, files: List[Any]) -> None:
        """Set file data for filtering operations"""
        self._current_files = files
        self.filter_manager.set_data(files)
    
    def get_filtered_files(self) -> List[Any]:
        """Get currently filtered file list"""
        return self.filter_manager.get_filtered_data()
    
    def reset_file_filters(self) -> None:
        """Reset all file filters to default state"""
        self.filter_manager.reset_filters()
    
    def get_file_filter_stats(self) -> Dict[str, Any]:
        """Get file filtering statistics"""
        return self.filter_manager.get_filter_stats()
    
    # =====================
    # Utility Methods
    # =====================
    
    def _refresh_file_data(self):
        """Refresh file data for filtering after operations"""
        try:
            # Get current files from storage
            files = []
            for filename in os.listdir(self.received_files_path):
                file_path = os.path.join(self.received_files_path, filename)
                
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    files.append({
                        'filename': filename,
                        'size': file_stats.st_size,
                        'date_received': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        'file_path': file_path
                    })
            
            # Update filter manager data
            self.set_file_data_for_filtering(files)
            
        except Exception as e:
            print(f"[ERROR] Failed to refresh file data: {e}")
    
    def _log_operation(self, operation: FileOperation, target: str, success: bool, message: str):
        """Log file operations for tracking and debugging"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation.value,
            'target': target,
            'success': success,
            'message': message
        }
        
        self._operation_history.append(log_entry)
        
        # Keep only last 100 operations
        if len(self._operation_history) > 100:
            self._operation_history = self._operation_history[-100:]
        
        # Print to console
        status = "SUCCESS" if success else "ERROR"
        print(f"[{status}] {operation.value.upper()}: {message}")
    
    def _format_file_size(self, size: int) -> str:
        """Format file size to human-readable format"""
        if not size or size == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get recent file operation history"""
        return self._operation_history.copy()
    
    def get_file_list(self) -> List[Dict[str, Any]]:
        """Get list of all files in storage"""
        try:
            files = []
            for filename in os.listdir(self.received_files_path):
                file_path = os.path.join(self.received_files_path, filename)
                
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    files.append({
                        'filename': filename,
                        'size': file_stats.st_size,
                        'size_formatted': self._format_file_size(file_stats.st_size),
                        'date_received': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        'date_modified': datetime.fromtimestamp(file_stats.st_mtime),
                        'file_path': file_path,
                        'extension': filename.split('.')[-1].lower() if '.' in filename else 'no_extension'
                    })
            
            return sorted(files, key=lambda f: f['date_modified'], reverse=True)
            
        except Exception as e:
            print(f"[ERROR] Failed to get file list: {e}")
            return []


# Factory function for easy creation
def create_file_operations_manager(page: ft.Page, received_files_path: str = "received_files", toast_manager=None) -> FileOperationsManager:
    """Create a unified file operations manager"""
    return FileOperationsManager(page, received_files_path, toast_manager)
