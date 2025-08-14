#!/usr/bin/env python3
"""
Unified File Monitor for CyberBackup 3.0
=========================================

This module provides a single, robust, and efficient file monitoring and verification system.
It replaces the two separate monitoring systems that previously existed in the api_server and python_server.

Features:
- Unifies progress reporting and final verification into one system.
- Uses a ThreadPoolExecutor to prevent thread proliferation when checking multiple files.
- Provides detailed, job-specific callbacks for progress and completion.
- Uses watchdog for efficient, real-time file system eventing.
- Verifies files based on size, stability (last modification time), and SHA256 hash.
"""

import logging
import os
import time
import threading
import hashlib
from pathlib import Path
from typing import Callable, Dict, Any, Optional, Union, TYPE_CHECKING, List
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    ObserverType = Observer
    EventHandlerType = FileSystemEventHandler
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    ObserverType = None
    EventHandlerType = None

logger = logging.getLogger(__name__)

class UnifiedFileMonitor:
    """
    A unified, thread-safe file monitor that handles both progress and final verification.
    """

    def __init__(self, watched_directory: str, max_workers: int = 10) -> None:
        self.watched_directory = Path(watched_directory)
        self.max_workers = max_workers
        
        self.observer: Optional[Any] = None
        self.event_handler: Optional[Any] = None
        self.monitoring_active = False
        
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.jobs_lock = threading.Lock()
        
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix='FileCheck')

        # Ensure watched directory exists
        self.watched_directory.mkdir(parents=True, exist_ok=True)

    def start_monitoring(self) -> None:
        """Starts the file system observer."""
        if self.monitoring_active:
            logger.warning("Monitoring is already active.")
            return
        
        if not WATCHDOG_AVAILABLE:
            logger.warning("Cannot start file monitoring: 'watchdog' library is not installed. File monitoring will be disabled.")
            return

        self.monitoring_active = True
        self.event_handler = self._create_event_handler()
        if Observer is not None:
            self.observer = Observer()
            if self.observer is not None and self.event_handler is not None:
                self.observer.schedule(self.event_handler, str(self.watched_directory), recursive=False)
        
        try:
            if self.observer is not None:
                self.observer.start()
                logger.info(f"UnifiedFileMonitor started watching directory: {self.watched_directory}")
        except Exception as e:
            logger.critical(f"Failed to start watchdog observer: {e}")
            self.monitoring_active = False

    def stop_monitoring(self) -> None:
        """Stops the file system observer and shuts down the thread pool."""
        if not self.monitoring_active:
            return
            
        if self.observer is not None:
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
            except Exception as e:
                logger.error(f"Error stopping watchdog observer: {e}")

        self.executor.shutdown(wait=True)
        self.monitoring_active = False
        logger.info("UnifiedFileMonitor has stopped.")

    def register_job(self, filename: str, job_id: str, expected_size: int, expected_hash: str, 
                     completion_callback: Optional[Callable[..., None]] = None, 
                     failure_callback: Optional[Callable[..., None]] = None, 
                     callback: Optional[Callable[..., None]] = None) -> None:
        """
        Register a new file transfer job to be monitored.

        Args:
            filename (str): The name of the file to watch for.
            job_id (str): The unique ID of the backup job.
            expected_size (int): The expected final size of the file in bytes.
            expected_hash (str): The expected SHA256 hash of the file.
            completion_callback (Callable): Callback for successful completion.
            failure_callback (Callable): Callback for failure cases.
            callback (Callable): Legacy single callback (for backward compatibility).
        """
        # Handle callback compatibility - prefer dual callbacks, fallback to single
        if completion_callback is not None or failure_callback is not None:
            callbacks = {
                "completion_callback": completion_callback,
                "failure_callback": failure_callback
            }
        elif callback is not None:
            # Legacy single callback mode
            callbacks = {"callback": callback}
        else:
            raise ValueError("At least one callback must be provided")

        with self.jobs_lock:
            self.jobs[filename] = {
                "job_id": job_id,
                "expected_size": expected_size,
                "expected_hash": expected_hash.lower(),
                "callbacks": callbacks,
                "start_time": time.time(),
                "status": "registered"
            }
        logger.info(f"Job '{job_id}' registered for file '{filename}' (Size: {expected_size}, Hash: {expected_hash[:8]}...).")
        # Immediately check if the file already exists
        file_path = self.watched_directory / filename
        if file_path.exists():
            logger.info(f"File '{filename}' already exists. Submitting for verification.")
            self.executor.submit(self._verify_file, file_path)

    def _create_event_handler(self) -> Optional[Any]:
        """Creates the watchdog event handler instance."""
        
        if not WATCHDOG_AVAILABLE or FileSystemEventHandler is None:
            return None
            
        # Only define the Handler class when watchdog is available
        class Handler(FileSystemEventHandler):
            def __init__(self, monitor_instance: 'UnifiedFileMonitor') -> None:
                super().__init__()
                self.monitor = monitor_instance

            def on_created(self, event: Any) -> None:
                if not event.is_directory:
                    logger.debug(f"File created event for: {event.src_path}")
                    self.monitor.executor.submit(self.monitor._verify_file, Path(event.src_path))
            
            def on_modified(self, event: Any) -> None:
                if not event.is_directory:
                    logger.debug(f"File modified event for: {event.src_path}")
                    self.monitor.executor.submit(self.monitor._verify_file, Path(event.src_path))

        return Handler(self)

    def _invoke_callback(self, job: Dict[str, Any], status: str, **kwargs: Any) -> None:
        """
        Invoke the appropriate callback based on the job's callback configuration.
        
        Args:
            job (Dict): The job dictionary containing callback information.
            status (str): The status - 'complete', 'failure', 'progress', etc.
            **kwargs: Additional data to pass to the callback.
        """
        callbacks = job["callbacks"]
        
        if "completion_callback" in callbacks and "failure_callback" in callbacks:
            # Dual callback mode
            if status == "complete":
                if callbacks["completion_callback"] is not None:
                    callbacks["completion_callback"]({**kwargs, "status": status})
            elif status == "failure":
                if callbacks["failure_callback"] is not None:
                    callbacks["failure_callback"]({**kwargs, "status": status})
            elif status == "progress":
                # For progress, call completion callback (following original pattern)
                if callbacks["completion_callback"] is not None:
                    callbacks["completion_callback"]({**kwargs, "status": status})
        elif "callback" in callbacks:
            # Legacy single callback mode
            if callbacks["callback"] is not None:
                callbacks["callback"]({**kwargs, "status": status})
        else:
            logger.warning(f"[Job {job['job_id']}] No valid callback found for status: {status}")

    def _verify_file(self, file_path: Path) -> None:
        """The core file verification logic, designed to run in a thread pool."""
        filename = file_path.name
        job: Optional[Dict[str, Any]] = None
        
        with self.jobs_lock:
            if filename in self.jobs:
                # Avoid multiple concurrent checks for the same file
                if self.jobs[filename].get("status") in ["verifying", "completed", "failed"]:
                    return
                self.jobs[filename]["status"] = "verifying"
                job = self.jobs[filename]

        if job is None:
            logger.debug(f"No registered job found for file '{filename}'. Ignoring.")
            return

        try:
            # 1. Wait for size to match
            self._wait_for_size_match(file_path, job)

            # 2. Wait for stability
            self._wait_for_stability(file_path, job)

            # 3. Verify hash
            self._verify_hash(file_path, job)

        except Exception as e:
            logger.error(f"[Job {job['job_id']}] Verification failed for '{filename}': {e}")
            self._invoke_callback(job, "failure", reason=str(e))
            with self.jobs_lock:
                if filename in self.jobs:
                    self.jobs[filename]["status"] = "failed"
        finally:
            # Clean up the job registration after processing
            with self.jobs_lock:
                if filename in self.jobs:
                    del self.jobs[filename]
                    logger.info(f"Job for file '{filename}' cleaned up.")

    def _wait_for_size_match(self, file_path: Path, job: Dict[str, Any]) -> None:
        """Waits until the file size matches the expected size."""
        expected_size = job["expected_size"]
        last_reported_size = -1

        while True:
            if not file_path.exists():
                raise FileNotFoundError(f"File '{file_path.name}' disappeared during transfer.")
            
            current_size = file_path.stat().st_size
            if current_size != last_reported_size:
                self._invoke_callback(job, "progress", bytes_transferred=current_size, total_bytes=expected_size)
                last_reported_size = current_size

            if current_size > expected_size:
                raise IOError(f"File size ({current_size}) exceeded expected size ({expected_size}).")
            
            if current_size == expected_size:
                logger.info(f"[Job {job['job_id']}] Size match for '{file_path.name}' ({expected_size} bytes).")
                return
            
            time.sleep(0.2) # Poll for size changes

    def _wait_for_stability(self, file_path: Path, job: Dict[str, Any], stability_delay: float = 1.0) -> None:
        """Waits until the file has not been modified for a certain delay."""
        logger.info(f"[Job {job['job_id']}] Checking file stability for '{file_path.name}'.")
        last_modified = file_path.stat().st_mtime
        while True:
            time.sleep(stability_delay)
            current_modified = file_path.stat().st_mtime
            if current_modified == last_modified:
                logger.info(f"[Job {job['job_id']}] File '{file_path.name}' is stable.")
                return
            last_modified = current_modified

    def _verify_hash(self, file_path: Path, job: Dict[str, Any]) -> None:
        """Calculates and verifies the file's SHA256 hash."""
        expected_hash = job["expected_hash"]
        
        logger.info(f"[Job {job['job_id']}] Verifying hash for '{file_path.name}'.")
        self._invoke_callback(job, "progress", phase="VERIFYING")

        calculated_hash = self._calculate_sha256(file_path)
        
        if calculated_hash == expected_hash:
            logger.info(f"[Job {job['job_id']}] SUCCESS: Hash verification passed for '{file_path.name}'.")
            self._invoke_callback(job, "complete", verified=True)
            with self.jobs_lock:
                if file_path.name in self.jobs:
                    self.jobs[file_path.name]["status"] = "completed"
        else:
            raise ValueError(f"Hash mismatch. Expected {expected_hash}, got {calculated_hash}.")

    @staticmethod
    def _calculate_sha256(file_path: Path) -> str:
        """Calculates the SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def check_file_receipt(self, filename: str) -> Dict[str, Any]:
        """
        Check if a specific file has been received and return receipt information.
        
        Args:
            filename (str): The name of the file to check.
            
        Returns:
            Dict[str, Any]: Receipt information including received status, size, timestamp, etc.
        """
        file_path = self.watched_directory / filename
        
        if not file_path.exists():
            return {
                'received': False,
                'error': f'File {filename} not found in {self.watched_directory}'
            }
        
        try:
            stat_info = file_path.stat()
            file_info = {
                'received': True,
                'filename': filename,
                'size': stat_info.st_size,
                'timestamp': stat_info.st_mtime,
                'modified_time': time.ctime(stat_info.st_mtime),
                'path': str(file_path.absolute())
            }
            
            # Check if there's an active job for this file with verification info
            with self.jobs_lock:
                if filename in self.jobs:
                    job = self.jobs[filename]
                    file_info.update({  # type: ignore
                        'job_id': job.get('job_id'),
                        'status': job.get('status'),
                        'expected_size': job.get('expected_size'),
                        'expected_hash': job.get('expected_hash'),
                        'verified': job.get('status') == 'completed'
                    })
                else:
                    # File exists but no active job - it was received previously
                    file_info['verified'] = None  # Unknown verification status
                    
            return file_info
            
        except Exception as e:
            logger.error(f"Error checking file receipt for {filename}: {e}")
            return {
                'received': False,
                'error': f'Error accessing file {filename}: {str(e)}'
            }

    def list_received_files(self) -> Dict[str, Any]:
        """
        List all files that have been received in the monitored directory.
        
        Returns:
            Dict[str, Any]: Information about all received files.
        """
        try:
            if not self.watched_directory.exists():
                return {
                    'success': False,
                    'error': f'Monitored directory {self.watched_directory} does not exist',
                    'files': []
                }
            
            files_info: List[Dict[str, Any]] = []
            total_size = 0
            
            # Scan all files in the monitored directory
            for file_path in self.watched_directory.iterdir():
                if file_path.is_file():
                    try:
                        stat_info = file_path.stat()
                        file_info = {
                            'filename': file_path.name,
                            'size': stat_info.st_size,
                            'timestamp': stat_info.st_mtime,
                            'modified_time': time.ctime(stat_info.st_mtime),
                            'path': str(file_path.absolute())
                        }
                        
                        # Add job information if available
                        with self.jobs_lock:
                            if file_path.name in self.jobs:
                                job = self.jobs[file_path.name]
                                file_info.update({  # type: ignore
                                    'job_id': job.get('job_id'),
                                    'status': job.get('status'),
                                    'expected_size': job.get('expected_size'),
                                    'expected_hash': job.get('expected_hash'),
                                    'verified': job.get('status') == 'completed'
                                })
                            else:
                                file_info['verified'] = None
                        
                        files_info.append(file_info)
                        total_size += stat_info.st_size
                        
                    except Exception as e:
                        logger.error(f"Error reading file {file_path.name}: {e}")
                        # Still include the file but with error info
                        files_info.append({
                            'filename': file_path.name,
                            'error': str(e),
                            'verified': False
                        })
            
            # Sort files by modification time (newest first)
            files_info.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            return {
                'success': True,
                'files': files_info,
                'total_files': len(files_info),
                'total_size': total_size,
                'directory': str(self.watched_directory.absolute())
            }
            
        except Exception as e:
            logger.error(f"Error listing received files: {e}")
            return {
                'success': False,
                'error': f'Error listing files: {str(e)}',
                'files': []
            }

    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get the current status of the file monitoring system.
        
        Returns:
            Dict[str, Any]: Monitoring status information.
        """
        try:
            with self.jobs_lock:
                active_jobs = len(self.jobs)
                jobs_info: List[Dict[str, Any]] = []
                for filename, job in self.jobs.items():
                    jobs_info.append({
                        'filename': filename,
                        'job_id': job.get('job_id'),
                        'status': job.get('status'),
                        'expected_size': job.get('expected_size'),
                        'start_time': job.get('start_time'),
                        'runtime': time.time() - job.get('start_time', time.time())
                    })
            
            # Count total files in directory
            total_files = 0
            directory_size = 0
            if self.watched_directory.exists():
                try:
                    for file_path in self.watched_directory.iterdir():
                        if file_path.is_file():
                            total_files += 1
                            directory_size += file_path.stat().st_size
                except Exception as e:
                    logger.warning(f"Error counting files in directory: {e}")
            
            return {
                'monitoring_active': self.monitoring_active,
                'watchdog_available': WATCHDOG_AVAILABLE,
                'watched_directory': str(self.watched_directory.absolute()),
                'directory_exists': self.watched_directory.exists(),
                'active_jobs': active_jobs,
                'jobs_info': jobs_info,
                'total_files_in_directory': total_files,
                'directory_size': directory_size,
                'max_workers': self.max_workers,
                'observer_running': self.observer is not None and self.observer.is_alive() if self.observer else False
            }
            
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {
                'monitoring_active': False,
                'error': f'Error getting status: {str(e)}'
            }

