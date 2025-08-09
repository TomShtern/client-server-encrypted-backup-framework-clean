#!/usr/bin/env python3
"""
File Receipt Monitor - Server-side file receipt detection and broadcasting
Monitors the received_files directory for new file arrivals and broadcasts
notifications to connected clients via WebSocket.
"""

import logging
import os
import time
import threading
import hashlib
from pathlib import Path
from typing import Callable, Dict, Any, Optional, Tuple

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

# Configure logging for this module
logger = logging.getLogger(__name__)


class FileReceiptEventHandler(FileSystemEventHandler):
    """Handle filesystem events for file receipt monitoring with job-specific awareness"""
    
    def __init__(self, broadcast_callback: Callable[[str, Dict[str, Any]], None]):
        self.broadcast_callback = broadcast_callback
        self.file_states = {}  # Track file states to detect completion
        
        # --- NEW: Job-specific tracking ---
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.jobs_lock = threading.Lock()
        # --- END NEW ---
        
        self.monitoring_lock = threading.Lock()

    def register_job(self, filename: str, job_id: str, expected_size: int, expected_hash: str, completion_callback: Callable, failure_callback: Callable):
        """Register a new file transfer job to be monitored."""
        with self.jobs_lock:
            self.jobs[filename] = {
                "job_id": job_id,
                "expected_size": expected_size,
                "expected_hash": expected_hash.lower(),
                "completion_callback": completion_callback,
                "failure_callback": failure_callback,
                "start_time": time.time()
            }
        logger.info(f"Job '{job_id}' registered for file '{filename}' (Size: {expected_size}, Hash: {expected_hash[:8]}...).")

    def _get_job_by_filepath(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Safely retrieve job details by filename."""
        with self.jobs_lock:
            return self.jobs.get(file_path.name)

    def _cleanup_job(self, filename: str):
        """Remove a job from the tracking dictionary."""
        with self.jobs_lock:
            if filename in self.jobs:
                del self.jobs[filename]
                logger.info(f"Job for file '{filename}' cleaned up.")

        
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        file_path = Path(str(event.src_path))
        print(f"[FILE_RECEIPT] File created: {file_path.name}")
        
        # Start monitoring this file for completion
        with self.monitoring_lock:
            self.file_states[str(file_path)] = {
                "created_time": time.time(),
                "last_size": 0,
                "last_modified": time.time(),
                "stable_count": 0,
                "notified_received": False,
                "notified_complete": False
            }
        
        # Immediate notification of file receipt
        self._broadcast_file_event("file_received", file_path, {
            "status": "created",
            "timestamp": time.time()
        })
        
        # Start stability monitoring thread
        stability_thread = threading.Thread(
            target=self._monitor_file_stability,
            args=(file_path,),
            daemon=True,
            name=f"StabilityMonitor-{file_path.name}"
        )
        stability_thread.start()
    
    def _monitor_file_stability(self, file_path: Path, stability_threshold: float = 2.0):
        """Monitor a file for completion using multi-factor verification (size, stability, hash)."""
        job = self._get_job_by_filepath(file_path)
        if not job:
            logger.debug(f"No job registered for '{file_path.name}', ignoring.")
            return

        job_id = job['job_id']
        expected_size = job['expected_size']
        logger.info(f"[Job {job_id}] Starting verification for '{file_path.name}'. Expecting {expected_size} bytes.")

        last_size = -1
        last_modified = -1
        
        while True:
            try:
                if not file_path.exists():
                    logger.warning(f"[Job {job_id}] File '{file_path.name}' disappeared during monitoring.")
                    job['failure_callback']("File disappeared during transfer.")
                    self._cleanup_job(file_path.name)
                    return

                current_size = file_path.stat().st_size

                # 1. Size Check
                if current_size > expected_size:
                    logger.error(f"[Job {job_id}] FAILED: File '{file_path.name}' exceeded expected size ({current_size} > {expected_size}).")
                    job['failure_callback']("File size exceeded expected value.")
                    self._cleanup_job(file_path.name)
                    return

                if current_size < expected_size:
                    if current_size != last_size:
                        logger.debug(f"[Job {job_id}] Progress for '{file_path.name}': {current_size} / {expected_size} bytes.")
                        last_size = current_size
                    time.sleep(0.25) # Wait for more data
                    continue
                
                # At this point, current_size == expected_size
                logger.info(f"[Job {job_id}] Size match for '{file_path.name}' ({expected_size} bytes). Now checking for stability.")

                # 2. Stability Check
                if last_modified == -1:
                    last_modified = file_path.stat().st_mtime
                
                time.sleep(stability_threshold)

                current_modified = file_path.stat().st_mtime
                if current_modified != last_modified:
                    logger.debug(f"[Job {job_id}] File '{file_path.name}' is still being modified. Resetting stability check.")
                    last_modified = current_modified
                    continue

                logger.info(f"[Job {job_id}] File '{file_path.name}' is stable. Proceeding to hash verification.")

                # 3. Hash Verification
                calculated_hash = self._calculate_file_hash(file_path)
                expected_hash = job['expected_hash']
                logger.info(f"[Job {job_id}] Expected hash: {expected_hash}, Calculated hash: {calculated_hash}")

                if calculated_hash == expected_hash:
                    logger.info(f"[Job {job_id}] SUCCESS: Hash verification passed for '{file_path.name}'.")
                    job['completion_callback']()
                else:
                    logger.error(f"[Job {job_id}] FAILED: Hash mismatch for '{file_path.name}'.")
                    job['failure_callback']("File content is corrupt (hash mismatch).")
                
                # Finalize and clean up
                self._cleanup_job(file_path.name)
                return

            except Exception as e:
                logger.error(f"[Job {job_id}] Error monitoring {file_path.name}: {e}", exc_info=True)
                job['failure_callback'](f"An unexpected error occurred during file verification: {e}")
                self._cleanup_job(file_path.name)
                return
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"[FILE_RECEIPT] Error calculating hash for {file_path.name}: {e}")
            return ""
    
    def _broadcast_file_event(self, event_type: str, file_path: Path, data: Dict[str, Any]):
        """Broadcast file event to connected clients"""
        try:
            event_data = {
                "event_type": event_type,
                "filename": file_path.name,
                "filepath": str(file_path),
                **data
            }
            
            print(f"[FILE_RECEIPT] Broadcasting {event_type}: {file_path.name}")
            self.broadcast_callback(event_type, event_data)
            
        except Exception as e:
            print(f"[FILE_RECEIPT] Error broadcasting event: {e}")


class FileReceiptMonitor:
    """
    Server-side file receipt monitor with real-time notifications
    Watches the received_files directory and broadcasts file receipt events
    """
    
    def __init__(self, watched_directory: str, broadcast_callback: Callable[[str, Dict[str, Any]], None]):
        self.watched_directory = Path(watched_directory)
        self.broadcast_callback = broadcast_callback
        self.observer = None
        self.event_handler: Optional[FileReceiptEventHandler] = None
        self.monitoring_active = False
        
        # Ensure watched directory exists
        self.watched_directory.mkdir(parents=True, exist_ok=True)

    def register_job(self, filename: str, job_id: str, expected_size: int, expected_hash: str, completion_callback: Callable, failure_callback: Callable):
        """Public method to register a new file transfer job."""
        if self.event_handler:
            self.event_handler.register_job(filename, job_id, expected_size, expected_hash, completion_callback, failure_callback)
        else:
            logger.error("Cannot register job: monitoring is not active.")

    def start_monitoring(self):
        """Start monitoring the received files directory"""
        if self.monitoring_active:
            print("[FILE_RECEIPT] Monitoring already active")
            return
        
        try:
            self.event_handler = FileReceiptEventHandler(self.broadcast_callback)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.watched_directory),
                recursive=False
            )
            
            self.observer.start()
            self.monitoring_active = True
            
            print(f"[FILE_RECEIPT] Started monitoring {self.watched_directory}")
            
        except Exception as e:
            print(f"[FILE_RECEIPT] Failed to start monitoring: {e}")
            self.monitoring_active = False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.monitoring_active:
            return
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5.0)
            
            self.monitoring_active = False
            print("[FILE_RECEIPT] Stopped monitoring")
            
        except Exception as e:
            print(f"[FILE_RECEIPT] Error stopping monitor: {e}")
    
    def check_file_receipt(self, filename: str) -> Dict[str, Any]:
        """Manually check if a file has been received"""
        try:
            file_path = self.watched_directory / filename
            
            if not file_path.exists():
                return {
                    "received": False,
                    "filename": filename,
                    "message": "File not found in received directory"
                }
            
            # File exists - get details
            stat_info = file_path.stat()
            file_hash = self._calculate_file_hash(file_path)
            
            return {
                "received": True,
                "filename": filename,
                "filepath": str(file_path),
                "size": stat_info.st_size,
                "modified_time": stat_info.st_mtime,
                "hash": file_hash,
                "message": "File successfully received"
            }
            
        except Exception as e:
            return {
                "received": False,
                "filename": filename,
                "error": str(e),
                "message": f"Error checking file receipt: {e}"
            }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"[FILE_RECEIPT] Error calculating hash for {file_path.name}: {e}")
            return ""
    
    def list_received_files(self) -> Dict[str, Any]:
        """List all files in the received directory"""
        try:
            files = []
            
            if self.watched_directory.exists():
                for file_path in self.watched_directory.iterdir():
                    if file_path.is_file():
                        stat_info = file_path.stat()
                        files.append({
                            "filename": file_path.name,
                            "size": stat_info.st_size,
                            "modified_time": stat_info.st_mtime,
                            "age_seconds": time.time() - stat_info.st_mtime
                        })
            
            return {
                "success": True,
                "files": files,
                "total_files": len(files),
                "directory": str(self.watched_directory)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error listing received files: {e}"
            }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "watched_directory": str(self.watched_directory),
            "directory_exists": self.watched_directory.exists(),
            "observer_alive": self.observer.is_alive() if self.observer else False
        }


# Global instance for use by the Flask API
_global_monitor: Optional[FileReceiptMonitor] = None


def get_file_receipt_monitor() -> Optional[FileReceiptMonitor]:
    """Get the global file receipt monitor instance"""
    return _global_monitor


def initialize_file_receipt_monitor(received_files_dir: str, broadcast_callback: Callable[[str, Dict[str, Any]], None]) -> FileReceiptMonitor:
    """Initialize the global file receipt monitor"""
    global _global_monitor
    
    if _global_monitor:
        _global_monitor.stop_monitoring()
    
    _global_monitor = FileReceiptMonitor(received_files_dir, broadcast_callback)
    _global_monitor.start_monitoring()
    
    return _global_monitor


def stop_file_receipt_monitor():
    """Stop the global file receipt monitor"""
    global _global_monitor
    
    if _global_monitor:
        _global_monitor.stop_monitoring()
        _global_monitor = None