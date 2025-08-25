#!/usr/bin/env python3
"""
Server File Manager
Handles file operations like download, verification, upload, and cleanup.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import sys
import os
import shutil
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    from python_server.server.database import DatabaseManager
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("[WARNING] Database integration not available for file operations")


class ServerFileManager:
    """Manages file operations on the server"""
    
    def __init__(self, received_files_path: str = "received_files"):
        self.received_files_path = received_files_path
        self.db_manager = None
        
        # Ensure received files directory exists
        os.makedirs(self.received_files_path, exist_ok=True)
        
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = DatabaseManager()
                print("[INFO] File manager database connection established")
            except Exception as e:
                print(f"[WARNING] File manager database initialization failed: {e}")
    
    def download_file(self, file_info: Dict[str, Any], destination_path: str) -> bool:
        """Download/copy a file to specified destination"""
        try:
            filename = file_info.get('filename')
            if not filename:
                print("[ERROR] No filename provided for download")
                return False
            
            source_path = os.path.join(self.received_files_path, filename)
            
            if not os.path.exists(source_path):
                print(f"[ERROR] Source file does not exist: {source_path}")
                return False
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy file to destination
            shutil.copy2(source_path, destination_path)
            print(f"[SUCCESS] File copied to: {destination_path}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to download file: {e}")
            return False
    
    def verify_file(self, file_info: Dict[str, Any]) -> bool:
        """Verify file integrity and existence"""
        try:
            filename = file_info.get('filename')
            expected_size = file_info.get('size', 0)
            
            if not filename:
                print("[ERROR] No filename provided for verification")
                return False
            
            file_path = os.path.join(self.received_files_path, filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"[ERROR] File does not exist: {filename}")
                return False
            
            # Check file size
            actual_size = os.path.getsize(file_path)
            if expected_size > 0 and actual_size != expected_size:
                print(f"[ERROR] File size mismatch for {filename}: expected {expected_size}, got {actual_size}")
                return False
            
            # Additional integrity checks could be added here (checksums, etc.)
            
            print(f"[SUCCESS] File verification passed: {filename}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to verify file: {e}")
            return False
    
    def upload_file_to_storage(self, file_path: str, client_name: str = "system") -> bool:
        """Upload a file to server storage"""
        try:
            if not os.path.exists(file_path):
                print(f"[ERROR] Source file does not exist: {file_path}")
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
            
            print(f"[SUCCESS] File uploaded to storage: {filename}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to upload file: {e}")
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
            
            print(f"[SUCCESS] Cleanup completed: {len(deleted_files)} files removed, {total_size_freed} bytes freed")
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to cleanup old files: {e}")
            return {
                'deleted_count': 0,
                'total_size_freed': 0,
                'deleted_files': [],
                'error': str(e)
            }
    
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
    
    def _format_file_size(self, size: int) -> str:
        """Format file size to human-readable format"""
        if not size or size == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
