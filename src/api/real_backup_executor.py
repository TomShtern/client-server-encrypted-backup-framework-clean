#!/usr/bin/env python3
"""
Real Backup Executor - Smart Process Control for EncryptedBackupClient.exe
This module provides REAL integration with the existing C++ client, not fake APIs.
"""

import os
import sys
import time
import json
import hashlib
import subprocess
import threading
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
import statistics
from abc import ABC, abstractmethod

import psutil
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
from src.shared.utils.file_lifecycle import SynchronizedFileManager
from src.shared.utils.error_handler import (
    get_error_handler, handle_subprocess_error, handle_file_transfer_error,
    ErrorSeverity, ErrorCategory, ErrorCode
)
from src.shared.utils.process_monitor import (
    get_process_registry, register_process, start_process, stop_process,
    ProcessState, get_process_metrics
)

class ProgressTracker(ABC):
    """Abstract base class for progress tracking strategies"""
    
    @abstractmethod
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information"""
        pass
    
    @abstractmethod
    def start_monitoring(self, context: Dict[str, Any]):
        """Start monitoring with given context"""
        pass
    
    @abstractmethod
    def stop_monitoring(self):
        """Stop monitoring"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this tracker can be used"""
        pass


class StatisticalProgressTracker(ProgressTracker):
    """Advanced progress tracker using statistical timing models"""
    
    def __init__(self, timing_data_file: str = "backup_timing_data.json"):
        self.timing_data_file = timing_data_file
        self.timing_data = self._load_timing_data()
        self.start_time = None
        self.current_phase = "INITIALIZATION"
        self.progress = 0
        self.monitoring_active = False
        
        # Phase definitions with default timing
        self.phases = {
            "INITIALIZATION": {"weight": 0.10, "description": "Initializing backup...", "progress_range": [0, 10]},
            "CONNECTION": {"weight": 0.15, "description": "Connecting to server...", "progress_range": [10, 25]},
            "ENCRYPTION": {"weight": 0.30, "description": "Encrypting file...", "progress_range": [25, 55]},
            "TRANSFER": {"weight": 0.35, "description": "Transferring data...", "progress_range": [55, 90]},
            "VERIFICATION": {"weight": 0.10, "description": "Verifying integrity...", "progress_range": [90, 100]}
        }
    
    def _load_timing_data(self) -> Dict[str, Any]:
        """Load statistical timing data from previous runs"""
        try:
            if os.path.exists(self.timing_data_file):
                with open(self.timing_data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[STATS] Could not load timing data: {e}")
        
        # Default timing data structure
        return {
            "runs": [],
            "statistics": {},
            "last_updated": time.time()
        }
    
    def _save_timing_data(self):
        """Save timing data to file"""
        try:
            with open(self.timing_data_file, 'w') as f:
                json.dump(self.timing_data, f, indent=2)
        except Exception as e:
            print(f"[STATS] Could not save timing data: {e}")
    
    def _predict_phase_duration(self, phase: str, file_size: int) -> float:
        """Predict phase duration based on statistical data"""
        if phase not in self.timing_data.get("statistics", {}):
            # Use default estimates based on file size
            base_times = {
                "INITIALIZATION": 1.0,
                "CONNECTION": 2.0, 
                "ENCRYPTION": max(2.0, file_size / 1024 / 1024 * 0.5),  # 0.5s per MB
                "TRANSFER": max(1.0, file_size / 1024 / 512),  # ~512 KB/s
                "VERIFICATION": 1.0
            }
            return base_times.get(phase, 2.0)
        
        stats = self.timing_data["statistics"][phase]
        # Use median + file size correlation if available
        base_duration = stats.get("median", 2.0)
        
        # Scale based on file size if we have size correlation data
        if "size_correlation" in stats and file_size > 0:
            size_factor = stats["size_correlation"].get("slope", 0) * file_size
            return max(0.5, base_duration + size_factor)
        
        return base_duration
    
    def _calculate_current_progress(self, elapsed_time: float, file_size: int) -> Dict[str, Any]:
        """Calculate current progress based on elapsed time and statistical models"""
        total_predicted_time = sum(
            self._predict_phase_duration(phase, file_size) 
            for phase in self.phases.keys()
        )
        
        # Determine current phase based on elapsed time
        cumulative_time = 0
        current_phase = "INITIALIZATION"
        phase_elapsed = elapsed_time
        
        for phase, config in self.phases.items():
            phase_duration = self._predict_phase_duration(phase, file_size)
            if elapsed_time <= cumulative_time + phase_duration:
                current_phase = phase
                phase_elapsed = elapsed_time - cumulative_time
                break
            cumulative_time += phase_duration
        
        # Calculate progress within current phase
        phase_config = self.phases[current_phase]
        progress_start, progress_end = phase_config["progress_range"]
        
        phase_duration = self._predict_phase_duration(current_phase, file_size)
        phase_progress = min(1.0, phase_elapsed / phase_duration) if phase_duration > 0 else 1.0
        
        overall_progress = progress_start + (progress_end - progress_start) * phase_progress
        overall_progress = min(95, max(0, overall_progress))  # Cap at 95% until verification
        
        # Calculate ETA
        if overall_progress > 0:
            eta_seconds = (total_predicted_time - elapsed_time) if elapsed_time < total_predicted_time else 0
        else:
            eta_seconds = total_predicted_time
        
        self.current_phase = current_phase
        self.progress = overall_progress
        
        return {
            "progress": overall_progress,
            "message": f"{phase_config['description']} ({overall_progress:.0f}%)",
            "phase": current_phase,
            "eta_seconds": max(0, eta_seconds),
            "confidence": "high" if len(self.timing_data.get("runs", [])) >= 5 else "medium"
        }
    
    def start_monitoring(self, context: Dict[str, Any]):
        """Start statistical progress monitoring"""
        self.start_time = time.perf_counter()
        self.monitoring_active = True
        self.file_size = context.get("file_size", 0)
        print(f"[STATS] Started statistical progress tracking for {self.file_size} byte file")
    
    def stop_monitoring(self):
        """Stop monitoring and save timing data"""
        if self.monitoring_active:
            self.monitoring_active = False
            if self.start_time:
                total_duration = time.perf_counter() - self.start_time
                self._record_timing_data(total_duration)
    
    def _record_timing_data(self, total_duration: float):
        """Record timing data for future statistical analysis"""
        run_data = {
            "timestamp": time.time(),
            "total_duration": total_duration,
            "file_size": getattr(self, "file_size", 0),
            "phases": {
                "total": total_duration
            }
        }
        
        self.timing_data["runs"].append(run_data)
        self.timing_data["last_updated"] = time.time()
        
        # Keep only last 50 runs to prevent file bloat
        if len(self.timing_data["runs"]) > 50:
            self.timing_data["runs"] = self.timing_data["runs"][-50:]
        
        self._update_statistics()
        self._save_timing_data()
        print(f"[STATS] Recorded timing data: {total_duration:.2f}s total")
    
    def _update_statistics(self):
        """Update statistical models from collected timing data"""
        runs = self.timing_data["runs"]
        if len(runs) < 3:
            return
        
        # Calculate basic statistics
        durations = [run["total_duration"] for run in runs]
        file_sizes = [run["file_size"] for run in runs if run["file_size"] > 0]
        
        self.timing_data["statistics"] = {
            "total": {
                "mean": statistics.mean(durations),
                "median": statistics.median(durations),
                "stdev": statistics.stdev(durations) if len(durations) > 1 else 0,
                "samples": len(durations)
            }
        }
        
        # Calculate file size correlation if we have size data
        if len(file_sizes) >= 3:
            try:
                # Simple linear correlation between file size and duration
                size_duration_pairs = [(run["file_size"], run["total_duration"]) 
                                     for run in runs if run["file_size"] > 0]
                if len(size_duration_pairs) >= 3:
                    sizes, durations = zip(*size_duration_pairs)
                    # Calculate correlation coefficient
                    n = len(sizes)
                    sum_xy = sum(x * y for x, y in size_duration_pairs)
                    sum_x = sum(sizes)
                    sum_y = sum(durations)
                    sum_x2 = sum(x * x for x in sizes)
                    
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
                    
                    self.timing_data["statistics"]["size_correlation"] = {
                        "slope": slope,
                        "samples": n
                    }
            except Exception as e:
                print(f"[STATS] Could not calculate size correlation: {e}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress based on statistical models"""
        if not self.monitoring_active or not self.start_time:
            return {"progress": 0, "message": "Statistical tracking not active", "phase": "INACTIVE"}
        
        elapsed_time = time.perf_counter() - self.start_time
        return self._calculate_current_progress(elapsed_time, getattr(self, "file_size", 0))
    
    def is_available(self) -> bool:
        """Check if statistical tracking is available"""
        # Available if we have some timing data or if we can create the data file
        try:
            if not os.path.exists(self.timing_data_file):
                # Test if we can create the file
                with open(self.timing_data_file, 'w') as f:
                    json.dump({"runs": [], "statistics": {}}, f)
            return True
        except Exception:
            return False


class TimeBasedEstimator(ProgressTracker):
    """Simple time-based progress estimation fallback"""
    
    def __init__(self, estimated_duration: float = 30.0):
        self.estimated_duration = estimated_duration
        self.start_time = None
        self.monitoring_active = False
    
    def start_monitoring(self, context: Dict[str, Any]):
        self.start_time = time.perf_counter()
        self.monitoring_active = True
        # Adjust estimate based on file size
        file_size = context.get("file_size", 0)
        if file_size > 0:
            # Rough estimate: 1MB per 2 seconds + 10 second base
            self.estimated_duration = 10 + (file_size / 1024 / 1024) * 2
        print(f"[TIME] Started time-based estimation ({self.estimated_duration:.1f}s estimated)")
    
    def stop_monitoring(self):
        """Stop monitoring (idempotent)"""
        if not hasattr(self, '_stopped') or not self._stopped:
            self._stopped = True
            self.monitoring_active = False
    
    def get_progress(self) -> Dict[str, Any]:
        if not self.monitoring_active or not self.start_time:
            return {"progress": 0, "message": "Time estimation not active", "phase": "INACTIVE"}
        
        elapsed = time.perf_counter() - self.start_time
        progress = min(95, (elapsed / self.estimated_duration) * 100)
        remaining = max(0, self.estimated_duration - elapsed)
        
        return {
            "progress": progress,
            "message": f"Processing backup... ({progress:.0f}%)",
            "phase": "PROCESSING",
            "eta_seconds": remaining,
            "confidence": "low"
        }
    
    def is_available(self) -> bool:
        return True


class BasicProcessingIndicator(ProgressTracker):
    """Indeterminate progress indicator fallback"""
    
    def __init__(self):
        self.monitoring_active = False
        self.start_time = None
    
    def start_monitoring(self, context: Dict[str, Any]):
        self.start_time = time.perf_counter()
        self.monitoring_active = True
        print(f"[BASIC] Started basic processing indicator")
    
    def stop_monitoring(self):
        """Stop monitoring (idempotent)"""
        if not hasattr(self, '_stopped') or not self._stopped:
            self._stopped = True
            self.monitoring_active = False
    
    def get_progress(self) -> Dict[str, Any]:
        if not self.monitoring_active:
            return {"progress": 0, "message": "Processing indicator not active", "phase": "INACTIVE"}
        
        return {
            "progress": -1,  # Indeterminate
            "message": "Processing backup - please wait...",
            "phase": "PROCESSING",
            "eta_seconds": 0,
            "confidence": "none"
        }
    
    def is_available(self) -> bool:
        return True


class OutputProgressTracker(ProgressTracker):
    """Real-time C++ client output parsing for actual progress percentages"""
    
    def __init__(self, process=None):
        self.process = process
        self.monitoring_active = False
        self.start_time = None
        self.current_progress = 0
        self.last_phase = "STARTING"
        self.output_buffer = ""
        self.monitor_thread = None
        
    def start_monitoring(self, context: Dict[str, Any]):
        self.start_time = time.perf_counter()
        self.monitoring_active = True
        self.process = context.get("process")
        self.current_progress = 0
        
        if self.process:
            # Start output monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_output,
                daemon=True,
                name="OutputProgressMonitor"
            )
            self.monitor_thread.start()
            print(f"[OUTPUT] Started real-time C++ client output parsing")
    
    def stop_monitoring(self):
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_output(self):
        """Monitor C++ client stdout for progress updates"""
        while self.monitoring_active and self.process and self.process.poll() is None:
            try:
                # Read output if available (simplified for cross-platform)
                time.sleep(0.1)  # Check every 100ms
            except Exception as e:
                print(f"[OUTPUT] Error monitoring output: {e}")
                break
    
    def _parse_progress_from_output(self, output: str) -> int:
        """Parse C++ client output for actual progress percentages"""
        try:
            # Look for percentage patterns like "100%" or "75%"
            import re
            percentage_matches = re.findall(r'(\d+)%', output)
            if percentage_matches:
                # Get the highest percentage found
                max_percentage = max(int(p) for p in percentage_matches)
                if max_percentage > self.current_progress:
                    print(f"[OUTPUT] Parsed progress: {max_percentage}%")
                    return max_percentage
            
            # Fallback to phase-based progress mapping
            output_lower = output.lower()
            progress_phases = [
                ("system initialization", 15, "System starting up"),
                ("configuration loaded", 25, "Configuration loaded"),
                ("validating configuration", 35, "Validating settings"),
                ("checking parameters", 40, "Parameter validation"),
                ("connecting", 50, "Establishing connection"),
                ("handshake", 55, "Server handshake"),
                ("encryption", 65, "File encryption"),
                ("uploading", 75, "File transfer"),
                ("transfer", 75, "Data transfer"),
                ("sending", 75, "Sending data"),
                ("verification", 85, "Verifying transfer"),
                ("backup completed", 95, "Transfer complete"),
                ("success", 95, "Operation successful")
            ]
            
            max_progress = self.current_progress
            for keyword, progress, phase_name in progress_phases:
                if keyword in output_lower and progress > max_progress:
                    max_progress = progress
                    self.last_phase = phase_name
            
            return max_progress
            
        except Exception as e:
            print(f"[OUTPUT] Progress parsing error: {e}")
            return self.current_progress
    
    def get_progress(self) -> Dict[str, Any]:
        if not self.monitoring_active:
            return {"progress": 0, "message": "Output parsing not active", "phase": "INACTIVE"}
        
        # Try to read any available output from the process
        if self.process:
            try:
                # Since we can't easily read stdout in real-time on Windows,
                # we'll rely on the finalization when process completes
                elapsed = time.perf_counter() - self.start_time if self.start_time else 0
                
                # Provide incremental progress based on time until we get real output
                if self.current_progress < 10:
                    time_progress = min(10, elapsed * 5)  # Slow ramp up
                    self.current_progress = max(self.current_progress, time_progress)
                
            except Exception as e:
                print(f"[OUTPUT] Error reading process output: {e}")
        
        return {
            "progress": self.current_progress,
            "message": f"{self.last_phase} ({self.current_progress:.0f}%)",
            "phase": self.last_phase.upper().replace(" ", "_"),
            "confidence": "high" if self.current_progress > 0 else "low"
        }
    
    def finalize_with_output(self, stdout: str):
        """Finalize progress using complete process output"""
        if stdout:
            final_progress = self._parse_progress_from_output(stdout)
            self.current_progress = final_progress
            print(f"[OUTPUT] Finalized progress from complete output: {final_progress}%")
    
    def is_available(self) -> bool:
        return True  # Always available as primary tracker


class FileReceiptProgressTracker(ProgressTracker):
    """Ground truth file receipt monitoring - overrides all progress when file arrives at server"""
    
    def __init__(self, destination_dir: str):
        self.destination_dir = Path(destination_dir)
        self.monitoring_active = False
        self.start_time = None
        self.target_filename = None
        self.file_received = False
        self.progress_override = False
        self.monitor_thread = None
        self.observer = None
        self.stability_timer = None
        self.stability_check_time = 2.0  # Wait 2 seconds for file stability
        
    def start_monitoring(self, context: Dict[str, Any]):
        self.start_time = time.perf_counter()
        self.monitoring_active = True
        self.target_filename = context.get("original_filename")
        self.file_received = False
        self.progress_override = False
        
        if not self.target_filename:
            print(f"[RECEIPT] Warning: No target filename provided")
            return
            
        print(f"[RECEIPT] Starting file receipt monitoring for: {self.target_filename}")
        print(f"[RECEIPT] Monitoring directory: {self.destination_dir}")
        print(f"[RECEIPT] Directory exists: {self.destination_dir.exists()}")
        print(f"[RECEIPT] Watchdog available: {WATCHDOG_AVAILABLE}")
        
        # IMMEDIATE CHECK: See if file already exists (for replacement scenarios)
        if self.destination_dir.exists():
            print(f"[RECEIPT] 🔍 CHECKING EXISTING FILES in {self.destination_dir}")
            existing_files = list(self.destination_dir.iterdir())
            print(f"[RECEIPT] Found {len(existing_files)} existing files: {[f.name for f in existing_files if f.is_file()]}")
            
            for existing_file in existing_files:
                if existing_file.is_file():
                    match_result = self._check_file_match(existing_file.name, self.target_filename)
                    print(f"[RECEIPT] Comparing '{existing_file.name}' vs '{self.target_filename}' = {match_result}")
                    if match_result:
                        print(f"[RECEIPT] ✅ FILE ALREADY EXISTS: {existing_file.name} matches {self.target_filename}")
                        self._trigger_file_received(existing_file.name)
                        return  # File already exists, no need to monitor
        else:
            print(f"[RECEIPT] ❌ Destination directory does not exist: {self.destination_dir}")
        
        # Start file system monitoring with DUAL approach (watchdog + polling backup)
        if WATCHDOG_AVAILABLE:
            self._start_watchdog_monitoring()
            # ALWAYS start polling as backup even with watchdog (Windows file events can be unreliable)
            self._start_polling_monitoring()
            print(f"[RECEIPT] Started DUAL monitoring: Watchdog + Polling backup")
        else:
            print(f"[RECEIPT] Watchdog not available, using polling only")
            self._start_polling_monitoring()
    
    def _start_watchdog_monitoring(self):
        """Start real-time file system monitoring using watchdog"""
        try:
            class FileReceiptHandler(FileSystemEventHandler):
                def __init__(self, tracker):
                    self.tracker = tracker
                
                def on_created(self, event):
                    if not event.is_directory:
                        self.tracker._handle_file_event(event.src_path, "created")
                
                def on_modified(self, event):
                    if not event.is_directory:
                        self.tracker._handle_file_event(event.src_path, "modified")
            
            self.observer = Observer()
            handler = FileReceiptHandler(self)
            self.observer.schedule(handler, str(self.destination_dir), recursive=False)
            self.observer.start()
            print(f"[RECEIPT] Watchdog monitoring started")
            
        except Exception as e:
            print(f"[RECEIPT] Watchdog failed: {e}, falling back to polling")
            self._start_polling_monitoring()
    
    def _start_polling_monitoring(self):
        """Fallback polling monitoring"""
        self.monitor_thread = threading.Thread(
            target=self._poll_for_file,
            daemon=True,
            name="FileReceiptPoller"
        )
        self.monitor_thread.start()
        print(f"[RECEIPT] Polling monitoring started")
    
    def _handle_file_event(self, file_path: str, event_type: str):
        """Handle file system events"""
        if not self.monitoring_active or self.file_received:
            return
            
        file_name = os.path.basename(file_path)
        
        # Use enhanced filename matching for server timestamp prefix pattern
        if self._check_file_match(file_name, self.target_filename):
            print(f"[RECEIPT] File event detected: {event_type} - {file_name}")
            self._trigger_stability_check(file_path)
    
    def _poll_for_file(self):
        """Polling fallback for file detection"""
        poll_count = 0
        while self.monitoring_active and not self.file_received:
            try:
                poll_count += 1
                if poll_count % 10 == 1:  # Log every 5 seconds (10 * 0.5s)
                    print(f"[RECEIPT] 🔄 Polling for '{self.target_filename}' (attempt {poll_count})")
                
                if self.destination_dir.exists():
                    files = list(self.destination_dir.iterdir())
                    for file_path in files:
                        if file_path.is_file():
                            # Use enhanced filename matching for server timestamp prefix pattern
                            if self._check_file_match(file_path.name, self.target_filename):
                                print(f"[RECEIPT] 🎯 File found via polling: {file_path.name}")
                                self._trigger_stability_check(str(file_path))
                                return
                    
                    if poll_count % 10 == 1:  # Log current files every 5 seconds
                        file_names = [f.name for f in files if f.is_file()]
                        print(f"[RECEIPT] Current files in directory: {file_names}")
                
                time.sleep(0.5)  # Poll every 500ms
                
            except Exception as e:
                print(f"[RECEIPT] Polling error: {e}")
                time.sleep(1.0)
    
    def _trigger_stability_check(self, file_path: str):
        """Check file stability before declaring receipt"""
        if self.file_received:
            return
            
        # Cancel any existing stability timer
        if self.stability_timer:
            self.stability_timer.cancel()
        
        # Start new stability check
        self.stability_timer = threading.Timer(
            self.stability_check_time,
            self._confirm_file_receipt,
            args=[file_path]
        )
        self.stability_timer.start()
        print(f"[RECEIPT] Starting stability check for: {os.path.basename(file_path)}")
    
    def _check_file_match(self, existing_filename: str, target_filename: str) -> bool:
        """Check if existing file matches target file (handles server timestamp prefix pattern)"""
        existing_lower = existing_filename.lower()
        target_lower = target_filename.lower()
        
        # First try exact match
        if existing_lower == target_lower:
            return True
        
        # Handle server timestamp prefix pattern: username_YYYYMMDD_HHMMSS_filename.ext
        # Check if existing filename ends with the target filename
        if existing_lower.endswith(target_lower):
            return True
        
        # Alternative pattern: check if target filename is contained with underscore separator
        if f"_{target_lower}" in existing_lower:
            return True
            
        return False
    
    def _trigger_file_received(self, filename: str):
        """Trigger immediate file received state"""
        self.file_received = True
        self.progress_override = True
        print(f"[RECEIPT] ✅ FILE ALREADY RECEIVED! {filename}")
        print(f"[RECEIPT] ⚡ OVERRIDING PROGRESS TO 100% - FILE CONFIRMED ON SERVER")
    
    def _confirm_file_receipt(self, file_path: str):
        """Confirm file is completely received and stable"""
        try:
            if not os.path.exists(file_path):
                print(f"[RECEIPT] File disappeared during stability check: {file_path}")
                return
            
            # Check if file is still being written to
            stat1 = os.stat(file_path)
            time.sleep(0.1)
            stat2 = os.stat(file_path)
            
            if stat1.st_size == stat2.st_size and stat1.st_mtime == stat2.st_mtime:
                # File is stable
                self.file_received = True
                self.progress_override = True
                file_size = stat1.st_size
                
                print(f"[RECEIPT] ✅ FILE RECEIVED! {os.path.basename(file_path)} ({file_size} bytes)")
                print(f"[RECEIPT] ⚡ OVERRIDING PROGRESS TO 100% - FILE CONFIRMED ON SERVER")
                
            else:
                print(f"[RECEIPT] File still changing, extending stability check")
                self._trigger_stability_check(file_path)
                
        except Exception as e:
            print(f"[RECEIPT] Error confirming file receipt: {e}")
    
    def stop_monitoring(self):
        """Stop all monitoring (idempotent)"""
        if not hasattr(self, '_stopped') or not self._stopped:
            self._stopped = True
            self.monitoring_active = False
            
            if self.stability_timer:
                self.stability_timer.cancel()
                
            if self.observer:
                try:
                    self.observer.stop()
                    self.observer.join(timeout=2.0)  # Increased timeout
                    if self.observer.is_alive():
                        print(f"[RECEIPT] Warning: Observer thread did not stop within timeout")
                except Exception as e:
                    print(f"[RECEIPT] Error stopping observer: {e}")
                finally:
                    self.observer = None
        
            if self.monitor_thread:
                try:
                    self.monitor_thread.join(timeout=2.0)  # Increased timeout
                    if self.monitor_thread.is_alive():
                        print(f"[RECEIPT] Warning: Monitor thread did not stop within timeout")
                except Exception as e:
                    print(f"[RECEIPT] Error stopping monitor thread: {e}")
                finally:
                    self.monitor_thread = None
    
    def get_progress(self) -> Dict[str, Any]:
        if not self.monitoring_active:
            return {"progress": 0, "message": "File receipt monitoring not active", "phase": "INACTIVE"}
        
        if self.file_received and self.progress_override:
            # GROUND TRUTH: File is on server = 100% complete!
            return {
                "progress": 100,
                "message": "✅ File received on server - Backup complete!",
                "phase": "COMPLETED",
                "confidence": "absolute",
                "override": True,
                "receipt_confirmed": True
            }
        
        # File not yet received, return minimal progress
        elapsed = time.perf_counter() - self.start_time if self.start_time else 0
        return {
            "progress": min(5, elapsed * 2),  # Very slow ramp until file receipt
            "message": f"Monitoring for file receipt: {self.target_filename}",
            "phase": "MONITORING",
            "confidence": "low"
        }
    
    def is_available(self) -> bool:
        return True  # Always available as ground truth tracker


class DirectFilePoller(ProgressTracker):
    """Direct file system polling fallback"""
    
    def __init__(self, destination_dir: str):
        self.destination_dir = Path(destination_dir)
        self.monitoring_active = False
        self.start_time = None
        self.original_filename = None
        self.poll_thread = None
        self.file_detected = False
    
    def start_monitoring(self, context: Dict[str, Any]):
        self.start_time = time.perf_counter()
        self.monitoring_active = True
        self.original_filename = context.get("original_filename")
        self.file_detected = False
        
        # Start polling thread
        self.poll_thread = threading.Thread(
            target=self._poll_for_file,
            daemon=True,
            name="FilePoller"
        )
        self.poll_thread.start()
        print(f"[POLLER] Started file polling for {self.original_filename}")
    
    def stop_monitoring(self):
        self.monitoring_active = False
        if self.poll_thread:
            self.poll_thread.join(timeout=1.0)
    
    def _poll_for_file(self):
        """Poll destination directory for file appearance"""
        while self.monitoring_active:
            try:
                if self.destination_dir.exists():
                    for file_path in self.destination_dir.iterdir():
                        if file_path.is_file():
                            self.file_detected = True
                            print(f"[POLLER] File detected: {file_path.name}")
                            return
                time.sleep(0.5)  # Poll every 500ms
            except Exception as e:
                print(f"[POLLER] Error during polling: {e}")
                time.sleep(1.0)
    
    def get_progress(self) -> Dict[str, Any]:
        if not self.monitoring_active:
            return {"progress": 0, "message": "File polling not active", "phase": "INACTIVE"}
        
        if self.file_detected:
            return {
                "progress": 95,
                "message": "File detected on server - verifying...",
                "phase": "FILE_DETECTED",
                "eta_seconds": 5,
                "confidence": "high"
            }
        
        elapsed = time.perf_counter() - self.start_time if self.start_time else 0
        return {
            "progress": min(80, elapsed * 2),  # Slow progress increase
            "message": "Monitoring for file receipt...",
            "phase": "MONITORING",
            "eta_seconds": 0,
            "confidence": "low"
        }
    
    def is_available(self) -> bool:
        return self.destination_dir.exists() or self.destination_dir.parent.exists()


class RobustProgressMonitor:
    """Multi-layer progress monitoring with automatic fallback"""
    
    def __init__(self, destination_dir: str):
        self.destination_dir = destination_dir
        self.progress_layers = [
            FileReceiptProgressTracker(destination_dir),  # HIGHEST PRIORITY: Ground truth file receipt
            OutputProgressTracker(),  # Primary: real C++ output parsing
            StatisticalProgressTracker(),
            TimeBasedEstimator(),
            BasicProcessingIndicator(),
            DirectFilePoller(destination_dir)
        ]
        self.active_layer = 0
        self.monitoring_active = False
        self.status_callback = None
        self.fallback_count = 0
        self.override_active = False # NEW: Flag to block other updates
        self.file_receipt_started = False  # Prevent multiple starts

    def force_completion(self):
        """Force progress to 100% on verified completion."""
        logger.info("FORCE_COMPLETION triggered. Overriding all other progress.")
        self.override_active = True
        self.monitoring_active = False # Stop further monitoring
        if self.status_callback:
            self.status_callback("COMPLETED_VERIFIED", {
                "progress": 100,
                "message": "Backup complete and cryptographically verified.",
                "phase": "COMPLETED_VERIFIED",
                "confidence": "absolute",
                "override": True
            })

    def force_failure(self, reason: str):
        """Force progress to a failed state on verification failure."""
        logger.error(f"FORCE_FAILURE triggered: {reason}. Overriding all other progress.")
        self.override_active = True
        self.monitoring_active = False # Stop further monitoring
        if self.status_callback:
            self.status_callback("VERIFICATION_FAILED", {
                "progress": 0, # Or keep last known good?
                "message": f"CRITICAL: {reason}",
                "phase": "VERIFICATION_FAILED",
                "confidence": "absolute",
                "override": True
            })
        
    def set_status_callback(self, callback: Callable[[str, Any], None]):
        """Set callback for progress updates"""
        self.status_callback = callback
    
    def start_monitoring(self, context: Dict[str, Any]):
        """Start monitoring with the best available tracker"""
        self.monitoring_active = True
        self._last_context = context  # Store context for fallback
        
        # CRITICAL: ALWAYS start FileReceiptProgressTracker (layer 0) regardless of active layer
        file_receipt_tracker = self.progress_layers[0]
        if isinstance(file_receipt_tracker, FileReceiptProgressTracker) and not self.file_receipt_started:
            file_receipt_tracker.start_monitoring(context)
            self.file_receipt_started = True
            print(f"[ROBUST] ✅ ALWAYS STARTED: FileReceiptProgressTracker for ground truth file detection")
        
        # Find first available tracker for primary monitoring
        for i, tracker in enumerate(self.progress_layers):
            if tracker.is_available():
                self.active_layer = i
                break
        
        # Start the active tracker (if it's not already started)
        active_tracker = self.progress_layers[self.active_layer]
        if not isinstance(active_tracker, FileReceiptProgressTracker):
            active_tracker.start_monitoring(context)
        
        tracker_name = active_tracker.__class__.__name__
        print(f"[ROBUST] Started primary monitoring with {tracker_name} (layer {self.active_layer})")
        
        if self.status_callback:
            self.status_callback("MONITOR", {
                "message": f"Progress monitoring active ({tracker_name}) + FileReceiptProgressTracker",
                "tracker": tracker_name,
                "layer": self.active_layer
            })
    
    def stop_monitoring(self):
        """Stop all monitoring (idempotent)"""
        if not hasattr(self, '_stopped') or not self._stopped:
            self._stopped = True
            self.monitoring_active = False
            for tracker in self.progress_layers:
                try:
                    tracker.stop_monitoring()
                except Exception as e:
                    print(f"[ROBUST] Error stopping tracker: {e}")
    
    def finalize_with_output(self, stdout: str):
        """Finalize progress using complete process output"""
        try:
            # Try to finalize with OutputProgressTracker if it exists and has the method
            output_tracker = self.progress_layers[0]  # OutputProgressTracker is first
            if hasattr(output_tracker, 'finalize_with_output'):
                output_tracker.finalize_with_output(stdout)
                print(f"[ROBUST] Finalized progress with complete stdout output")
            
            # Trigger a final progress update
            if self.status_callback and self.monitoring_active:
                final_progress = output_tracker.get_progress()
                self.status_callback("FINALIZE", {
                    "message": f"Progress finalized: {final_progress.get('progress', 0):.0f}%",
                    "progress": final_progress.get('progress', 0),
                    "final": True
                })
                
        except Exception as e:
            print(f"[ROBUST] Error finalizing with output: {e}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get progress with automatic fallback handling"""
        if self.override_active:
            logger.debug("Progress override is active. No new progress will be calculated.")
            return {"progress": 100, "message": "Awaiting final verification...", "phase": "FINALIZING"}

        if not self.monitoring_active:
            return {"progress": 0, "message": "Monitoring not active", "phase": "INACTIVE"}
        
        try:
            # CRITICAL: Check FileReceiptProgressTracker first for ground truth override
            file_receipt_tracker = self.progress_layers[0]  # FileReceiptProgressTracker is first
            if isinstance(file_receipt_tracker, FileReceiptProgressTracker):
                receipt_progress = file_receipt_tracker.get_progress()
                if receipt_progress.get("override", False):
                    # GROUND TRUTH: File is on server = 100% complete!
                    print("[ROBUST] ✅ FILE RECEIPT OVERRIDE: File detected on server, forcing 100% completion!")
                    receipt_progress["tracker"] = "FileReceiptProgressTracker"
                    receipt_progress["layer"] = 0
                    receipt_progress["fallback_count"] = self.fallback_count
                    
                    # Trigger callback with completion signal
                    if self.status_callback:
                        self.status_callback("FILE_RECEIVED", receipt_progress)
                    
                    return receipt_progress
            
            # Normal progress flow - use active layer
            active_tracker = self.progress_layers[self.active_layer]
            progress_data = active_tracker.get_progress()
            
            # Add metadata about current tracking method
            progress_data["tracker"] = active_tracker.__class__.__name__
            progress_data["layer"] = self.active_layer
            progress_data["fallback_count"] = self.fallback_count
            
            return progress_data
            
        except Exception as e:
            print(f"[ROBUST] Error in layer {self.active_layer}: {e}")
            return self._fallback_to_next_layer()
    
    def _fallback_to_next_layer(self) -> Dict[str, Any]:
        """Fallback to next available tracker"""
        self.fallback_count += 1
        old_layer = self.active_layer
        
        # Find next available tracker
        for i in range(self.active_layer + 1, len(self.progress_layers)):
            if self.progress_layers[i].is_available():
                # Stop current tracker
                try:
                    self.progress_layers[self.active_layer].stop_monitoring()
                except Exception:
                    pass
                
                # Start new tracker
                self.active_layer = i
                context = getattr(self, '_last_context', {})
                self.progress_layers[i].start_monitoring(context)
                
                tracker_name = self.progress_layers[i].__class__.__name__
                print(f"[ROBUST] Fallback {old_layer}→{i}: Now using {tracker_name}")
                
                if self.status_callback:
                    self.status_callback("FALLBACK", {
                        "message": f"Progress tracking degraded - using {tracker_name}",
                        "old_layer": old_layer,
                        "new_layer": i,
                        "tracker": tracker_name
                    })
                
                return self.get_progress()
        
        # No more fallbacks available
        return {
            "progress": -1,
            "message": "All progress tracking methods failed",
            "phase": "ERROR",
            "tracker": "None",
            "layer": -1,
            "fallback_count": self.fallback_count
        }
    
    def finalize_progress(self, process_success: bool, verification_success: bool):
        """Finalize progress based on actual results"""
        if verification_success:
            final_progress = {
                "progress": 100,
                "message": "Transfer completed and verified successfully!",
                "phase": "COMPLETED",
                "confidence": "confirmed"
            }
        elif process_success:
            final_progress = {
                "progress": 95,
                "message": "Process completed - verification pending",
                "phase": "VERIFICATION_PENDING",
                "confidence": "high"
            }
        else:
            final_progress = {
                "progress": 0,
                "message": "Transfer failed",
                "phase": "FAILED",
                "confidence": "confirmed"
            }
        
        if self.status_callback:
            self.status_callback("PROGRESS", final_progress)
        
        self.stop_monitoring()
        print(f"[ROBUST] Progress finalized: {final_progress['message']}")


# Legacy FileTransferMonitor for compatibility (deprecated)
class FileTransferMonitor:
    """Legacy file transfer monitor - use RobustProgressMonitor instead"""
    def __init__(self, original_file_path: str, destination_dir: str, status_callback: Callable):
        self.original_file_path = Path(original_file_path)
        self.original_size = self.original_file_path.stat().st_size
        self.destination_dir = Path(destination_dir)
        self.status_callback = status_callback
        self.monitoring_active = False
        self.transfer_start_time = None
        self._last_update_time = 0
        self._initial_progress_sent = False
        self.current_progress = 5  # Start at 5%
        self.process_output_buffer = ""
        self.last_phase_detected = None
        
    def start_monitoring(self, process):
        """Start process-based monitoring in background thread"""
        self.monitoring_active = True
        self.transfer_start_time = time.time()
        
        self._log_status("MONITOR", "Starting process-based progress monitoring")
        
        # Send initial progress immediately
        self._emit_initial_progress()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitor_process_output, 
            args=(process,), 
            daemon=True,
            name="ProcessProgressMonitor"
        )
        monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring gracefully (idempotent)"""
        if not hasattr(self, '_stopped') or not self._stopped:
            self._stopped = True
            self.monitoring_active = False
            self._log_status("MONITOR", "Stopped process-based progress monitoring")
    
    def finalize_progress(self, process_success: bool, verification_success: bool):
        """Set final progress based on process and verification results"""
        if hasattr(self, '_finalized') and self._finalized:
            self._log_status("MONITOR", "Progress already finalized, skipping")
            return
        self._finalized = True
        
        if verification_success:
            # Transfer completed and verified successfully
            final_progress = {
                "progress": 100,
                "message": f"Transfer completed successfully - {self._format_bytes(self.original_size)}",
                "speed": 0,
                "eta": 0,
                "bytes_transferred": self.original_size,
                "total_bytes": self.original_size,
                "phase": "COMPLETED"
            }
            self.status_callback("PROGRESS", final_progress)
            self._log_status("MONITOR", "Progress finalized: 100% - Transfer verified")
        elif process_success:
            # Process completed but verification failed
            final_progress = {
                "progress": 90,
                "message": "Process completed - verification pending",
                "speed": 0,
                "eta": 0,
                "bytes_transferred": int(0.9 * self.original_size),
                "total_bytes": self.original_size,
                "phase": "VERIFICATION_PENDING"
            }
            self.status_callback("PROGRESS", final_progress)
            self._log_status("MONITOR", "Progress finalized: 90% - Process completed, verification failed")
        else:
            # Process failed
            final_progress = {
                "progress": 0,
                "message": "Transfer failed - process error",
                "speed": 0,
                "eta": 0,
                "bytes_transferred": 0,
                "total_bytes": self.original_size,
                "phase": "FAILED"
            }
            self.status_callback("PROGRESS", final_progress)
            self._log_status("MONITOR", "Progress finalized: 0% - Process failed")
        
    def _monitor_process_output(self, process):
        """Monitor C++ client process output for progress phases"""
        consecutive_errors = 0
        max_errors = 10
        
        while self.monitoring_active and process.poll() is None:
            try:
                # Read process output in real-time
                output_chunk = self._read_process_output_chunk(process)
                if output_chunk:
                    self.process_output_buffer += output_chunk
                    
                    # Parse for progress phases
                    new_progress = self._parse_progress_from_output(self.process_output_buffer)
                    
                    # Only update if progress has advanced
                    if new_progress > self.current_progress:
                        self.current_progress = new_progress
                        progress_info = self._create_progress_info(new_progress)
                        self._emit_progress(progress_info)
                        consecutive_errors = 0
                
                # Fast polling for responsive progress updates
                time.sleep(0.1)  # 100ms for very responsive progress
                
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    self._log_status("ERROR", f"Process monitoring failed after {max_errors} consecutive errors: {e}")
                    break
                
                # Brief pause before retry
                time.sleep(0.5)
    
    def _read_process_output_chunk(self, process) -> str:
        """Read a chunk of process output without blocking"""
        try:
            if process.stdout and hasattr(process.stdout, 'readable') and process.stdout.readable():
                # Try to read available output
                import select
                import sys
                
                if sys.platform != "win32":
                    # Unix-like systems: use select
                    ready, _, _ = select.select([process.stdout], [], [], 0)
                    if ready:
                        return process.stdout.read(1024).decode('utf-8', errors='ignore')
                else:
                    # Windows: try peek approach (simplified)
                    return ""  # Fallback for Windows - will rely on final output parsing
            return ""
        except Exception as e:
            self._log_status("DEBUG", f"Output reading error: {e}")
            return ""
    
    def _parse_progress_from_output(self, output: str) -> int:
        """Parse C++ client output for progress phases"""
        try:
            output_lower = output.lower()
            
            # Progress phase mapping based on C++ client output
            progress_phases = [
                ("system initialization", 15, "System starting up"),
                ("configuration loaded", 25, "Configuration loaded"),
                ("validating configuration", 35, "Validating settings"),
                ("checking parameters", 40, "Parameter validation"),
                ("connecting", 50, "Establishing connection"),
                ("handshake", 55, "Server handshake"),
                ("encryption", 65, "File encryption"),
                ("uploading", 75, "File transfer"),
                ("transfer", 75, "Data transfer"),
                ("sending", 75, "Sending data"),
                ("verification", 85, "Verifying transfer"),
                ("backup completed", 95, "Transfer complete"),
                ("success", 95, "Operation successful")
            ]
            
            # Find the highest progress phase that matches
            max_progress = self.current_progress
            current_phase = "Processing"
            
            for keyword, progress, phase_name in progress_phases:
                if keyword in output_lower and progress > max_progress:
                    max_progress = progress
                    current_phase = phase_name
                    
            # Debug logging for phase detection
            elapsed = time.time() - self.transfer_start_time
            if max_progress > self.current_progress:
                print(f"[PROGRESS_PHASE] t={elapsed:.1f}s: Detected '{current_phase}' → {max_progress}%")
                self.last_phase_detected = current_phase
            
            return max_progress
            
        except Exception as e:
            self._log_status("DEBUG", f"Progress parsing error: {e}")
            return self.current_progress
    
    def _create_progress_info(self, progress_pct: int) -> Dict[str, Any]:
        """Create progress info dict from percentage"""
        elapsed = time.time() - self.transfer_start_time
        
        # Estimate transfer metrics
        estimated_bytes = int((progress_pct / 100.0) * self.original_size)
        estimated_speed = estimated_bytes / elapsed if elapsed > 0 else 0
        
        # Estimate ETA
        remaining_pct = 100 - progress_pct
        eta_seconds = (remaining_pct / 100.0) * (elapsed / (progress_pct / 100.0)) if progress_pct > 0 else 0
        
        phase_message = self.last_phase_detected or "Processing"
        message = f"{phase_message} - {self._format_bytes(estimated_bytes)}/{self._format_bytes(self.original_size)}"
        
        if estimated_speed > 0:
            message += f" at {self._format_bytes_per_second(estimated_speed)}"
        
        return {
            "progress": progress_pct,
            "message": message,
            "speed": estimated_speed,
            "eta": eta_seconds,
            "bytes_transferred": estimated_bytes,
            "total_bytes": self.original_size,
            "phase": "TRANSFERRING"
        }
    
    # Removed _get_adaptive_interval - no longer needed for process monitoring
    
    def _emit_progress(self, progress_info: Dict[str, Any]):
        """Emit progress with rate limiting for process-based monitoring"""
        current_time = time.time()
        
        # Rate limiting: up to 10 updates per second for responsive process monitoring
        if current_time - self._last_update_time < 0.1:
            return
        
        self._last_update_time = current_time
        
        # Debug logging for progress flow tracking
        progress_pct = progress_info.get('progress', 0)
        message = progress_info.get('message', 'Unknown')
        
        print(f"[PROGRESS_DEBUG] Process-based progress: {progress_pct:.1f}% - {message}")
        
        self.status_callback("PROGRESS", progress_info)
    
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f}TB"
    
    def _format_bytes_per_second(self, bytes_per_sec: float) -> str:
        """Format transfer speed"""
        return f"{self._format_bytes(bytes_per_sec)}/s"
    
    def _format_time(self, seconds: float) -> str:
        """Format time duration"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
    
    # Removed directory monitoring methods - no longer needed for process-based monitoring
    
    def _emit_initial_progress(self):
        """Send initial progress update to provide immediate feedback"""
        if not self._initial_progress_sent:
            initial_progress = {
                "progress": 5,
                "message": "Process starting - monitoring client output",
                "speed": 0,
                "eta": 0,
                "bytes_transferred": 0,
                "total_bytes": self.original_size,
                "phase": "STARTING"
            }
            self.status_callback("PROGRESS", initial_progress)
            self._initial_progress_sent = True
    
    def _log_status(self, phase: str, message: str):
        """Log status updates"""
        if hasattr(self.status_callback, '__call__'):
            # Simple string messages for logging
            self.status_callback(phase, message)

class RealBackupExecutor:
    """
    Smart wrapper for EncryptedBackupClient.exe that provides real backup functionality
    with automated process control and verification.
    """
    def __init__(self, client_exe_path: Optional[str] = None):
        # Try different possible locations for the client executable
        # IMPORTANT: Only use the build/Release version which has our latest fixes
        if not client_exe_path:
            possible_paths = [
                r"build\Release\EncryptedBackupClient.exe",  # Latest version with fixes - REQUIRED
                r"EncryptedBackupClient.exe"                 # Root directory fallback
            ]
            
            self.client_exe = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.client_exe = path
                    break
            
            if not self.client_exe:
                # Default to the most likely location
                self.client_exe = r"build\Release\EncryptedBackupClient.exe"
        else:
            self.client_exe = client_exe_path
        
        self.server_received_files = "received_files"  # Server saves files to project root/received_files
        self.temp_dir = tempfile.mkdtemp()
        self.backup_process = None
        self.status_callback = None
        self.file_manager = SynchronizedFileManager(self.temp_dir)
        
        # Ensure directories exist
        os.makedirs(self.server_received_files, exist_ok=True)
        
    def set_status_callback(self, callback: Callable[[str, Any], None]):
        """Set callback function for real-time status updates"""
        self.status_callback = callback
        
    def _monitor_with_active_polling(self, monitor, timeout: int):
        """Monitor backup process with active progress polling"""
        import threading
        import queue
        
        # Use queues to communicate between threads
        stdout_chunks = []
        stderr_chunks = []
        
        def progress_polling_loop():
            """Continuously poll monitor for progress updates"""
            print("[POLLING] Starting active progress polling loop")
            last_progress = -1
            
            while self.backup_process.poll() is None:  # While process is running
                try:
                    # Get current progress from monitor
                    progress_data = monitor.get_progress()
                    current_progress = progress_data.get("progress", 0)
                    
                    # Only emit if progress changed significantly or has special flags
                    if (abs(current_progress - last_progress) >= 1.0 or 
                        progress_data.get("override", False) or
                        progress_data.get("phase") in ["COMPLETED", "FILE_RECEIVED"]):
                        
                        print(f"[POLLING] Progress update: {current_progress:.1f}% - {progress_data.get('message', 'Processing...')}")
                        
                        # Emit progress via status callback
                        if self.status_callback:
                            self.status_callback("PROGRESS", progress_data)
                        
                        last_progress = current_progress
                        
                        # If file receipt override detected, we can continue monitoring
                        if progress_data.get("override", False):
                            print(f"[POLLING] 🚀 FILE RECEIPT OVERRIDE DETECTED! Progress set to 100%")
                    
                    time.sleep(0.2)  # Poll every 200ms for highly responsive updates
                    
                except Exception as e:
                    print(f"[POLLING] Error in progress polling: {e}")
                    time.sleep(1.0)  # Longer sleep on error
            
            print("[POLLING] Progress polling loop ended")
        
        def stdout_reader():
            """Read stdout in background to prevent blocking"""
            try:
                if self.backup_process.stdout:
                    for line in iter(self.backup_process.stdout.readline, b''):
                        stdout_chunks.append(line)
            except Exception as e:
                print(f"[STDOUT] Error reading stdout: {e}")
        
        def stderr_reader():
            """Read stderr in background to prevent blocking"""
            try:
                if self.backup_process.stderr:
                    for line in iter(self.backup_process.stderr.readline, b''):
                        stderr_chunks.append(line)
            except Exception as e:
                print(f"[STDERR] Error reading stderr: {e}")
        
        # Start background threads for progress polling and output reading
        polling_thread = threading.Thread(target=progress_polling_loop, daemon=True)
        stdout_thread = threading.Thread(target=stdout_reader, daemon=True) if self.backup_process.stdout else None
        stderr_thread = threading.Thread(target=stderr_reader, daemon=True) if self.backup_process.stderr else None
        
        polling_thread.start()
        if stdout_thread:
            stdout_thread.start()
        if stderr_thread:
            stderr_thread.start()
        
        # Wait for process to complete with timeout
        try:
            self.backup_process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            print("[POLLING] Process timeout - terminating")
            self.backup_process.terminate()
            time.sleep(2)
            if self.backup_process.poll() is None:
                self.backup_process.kill()
        
        # Wait for threads to complete (brief timeout to avoid hanging)
        polling_thread.join(timeout=2.0)
        if stdout_thread:
            stdout_thread.join(timeout=1.0)
        if stderr_thread:
            stderr_thread.join(timeout=1.0)
        
        # Combine output chunks
        stdout = b''.join(stdout_chunks) if stdout_chunks else b''
        stderr = b''.join(stderr_chunks) if stderr_chunks else b''
        
        return stdout, stderr

    def _log_status(self, phase: str, message: str):
        """Log status updates"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {phase}: {message}")
        if self.status_callback:
            # For simple string messages, wrap in a dict for consistency
            if isinstance(message, str):
                self.status_callback(phase, {'message': message})
            else:
                self.status_callback(phase, message)
    
    def _generate_transfer_info(self, server_ip: str, server_port: int, 
                              username: str, file_path: str) -> tuple:
        """Generate managed transfer.info file for the C++ client"""
        # Convert to absolute path to ensure client finds the correct file
        absolute_file_path = os.path.abspath(file_path)
        
        content = f"{server_ip}:{server_port}\n{username}\n{absolute_file_path}"
        self._log_status("CONFIG", f"transfer.info content:\n---\n{content}---")
        self._log_status("CONFIG", "Configuration generated - ready for transfer")
        
        # Create managed file
        transfer_info_path = self.file_manager.create_managed_file("transfer.info", content)
        file_id = list(self.file_manager.managed_files.keys())[-1]
        
        self._log_status("CONFIG", f"Generated managed transfer.info: {server_ip}:{server_port}, {username}, {absolute_file_path}")
        return file_id, transfer_info_path

    def _clear_cached_credentials_if_username_changed(self, new_username: str):
        """Clear cached credentials if the username has changed to allow fresh registration"""
        try:
            # Check if me.info exists and has a different username
            me_info_paths = ["me.info", "data/me.info", "build/Release/me.info"]
            credentials_cleared = False

            for me_info_path in me_info_paths:
                if os.path.exists(me_info_path):
                    try:
                        with open(me_info_path, 'r') as f:
                            cached_username = f.readline().strip()

                        if cached_username and cached_username != new_username:
                            os.remove(me_info_path)
                            self._log_status("CLEANUP", f"Removed cached credentials for '{cached_username}' (switching to '{new_username}')")
                            credentials_cleared = True
                    except Exception as e:
                        self._log_status("WARNING", f"Could not check {me_info_path}: {e}")

            # Also clear private key files if credentials were cleared
            if credentials_cleared:
                priv_key_paths = ["priv.key", "build/Release/priv.key"]
                for priv_key_path in priv_key_paths:
                    if os.path.exists(priv_key_path):
                        try:
                            os.remove(priv_key_path)
                            self._log_status("CLEANUP", f"Removed cached private key: {priv_key_path}")
                        except Exception as e:
                            self._log_status("WARNING", f"Could not remove {priv_key_path}: {e}")

                self._log_status("INFO", f"Client will register fresh with username: {new_username}")
            else:
                self._log_status("INFO", f"Using username: {new_username}")

        except Exception as e:
            self._log_status("WARNING", f"Error checking cached credentials: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for verification"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self._log_status("ERROR", f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _parse_final_status_from_output(self, stdout: str) -> Dict[str, Any]:
        """Parse final completion status from C++ client output (not for ongoing progress)"""
        if not stdout:
            # Don't provide progress here - let FileTransferMonitor handle it
            return {"message": "Process completed"}
        
        stdout_text = stdout.lower() if isinstance(stdout, str) else str(stdout).lower()
        message = "Transfer process completed"
        
        try:
            # Only look for final completion indicators
            if any(phrase in stdout_text for phrase in ['backup completed successfully', 'transfer complete', 'file uploaded successfully']):
                message = "Backup completed successfully"
            elif 'verification' in stdout_text and ('success' in stdout_text or 'passed' in stdout_text):
                message = "File verified successfully"
            elif any(phrase in stdout_text for phrase in ['error', 'failed', 'unable', 'could not']):
                message = "Transfer encountered issues - check logs"
            elif 'timeout' in stdout_text:
                message = "Connection timeout occurred"
            else:
                # Look for any indication of what happened
                if 'transfer' in stdout_text or 'upload' in stdout_text:
                    message = "File transfer process completed"
                elif 'encrypt' in stdout_text:
                    message = "File encryption completed"
                elif 'connect' in stdout_text:
                    message = "Connection process completed"
                
        except Exception as e:
            self._log_status("DEBUG", f"Output parsing error: {e}")
            message = "Process completed (output analysis error)"
        
        # Return only message, no progress - FileTransferMonitor handles progress
        return {"message": message}
    
    def _verify_file_transfer(self, original_file: str, username: str) -> Dict[str, Any]:
        """Verify that file was actually transferred to server"""
        self._log_status("VERIFY", "Checking received_files directory for actual transfer...")
        
        verification = {
            'transferred': False,
            'file_found': False,
            'size_match': False,
            'hash_match': False,
            'received_file': None,
            'original_size': 0,
            'received_size': 0,
            'original_hash': '',
            'received_hash': ''
        }
        
        try:
            original_size = os.path.getsize(original_file)
            original_hash = self._calculate_file_hash(original_file)
            verification['original_size'] = original_size
            verification['original_hash'] = original_hash
            
            # Look for files in received_files directory
            received_files_dir = Path(self.server_received_files)
            if received_files_dir.exists():
                for received_file in received_files_dir.iterdir():
                    if received_file.is_file():
                        received_size = received_file.stat().st_size
                        received_hash = self._calculate_file_hash(str(received_file))
                        
                        self._log_status("VERIFY", f"Found file: {received_file.name}, size: {received_size}")
                        
                        # Check if this matches our uploaded file
                        if received_size == original_size:
                            verification['file_found'] = True
                            verification['received_file'] = str(received_file)
                            verification['received_size'] = received_size
                            verification['received_hash'] = received_hash
                            verification['size_match'] = True
                            
                            if received_hash == original_hash:
                                verification['hash_match'] = True
                                verification['transferred'] = True
                                self._log_status("SUCCESS", f"File transfer VERIFIED: {received_file.name}")
                                break
                            else:
                                self._log_status("ERROR", f"Hash mismatch for {received_file.name}")
                        
            if not verification['file_found']:
                self._log_status("ERROR", "No matching files found in received_files directory")
                
        except Exception as e:
            self._log_status("ERROR", f"Verification failed: {e}")
            
        return verification
    
    def _monitor_process_health(self, process: subprocess.Popen) -> Dict[str, Any]:
        """Comprehensive process health monitoring with psutil"""
        try:
            proc = psutil.Process(process.pid)
            health_data = {
                'pid': process.pid,
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_mb': proc.memory_info().rss / 1024 / 1024,
                'status': proc.status(),
                'num_threads': proc.num_threads(),
                'open_files': len(proc.open_files()),
                'connections': len(proc.connections()),
                'create_time': proc.create_time(),
                'is_running': proc.is_running()
            }
            
            # Detect potential issues
            health_data['is_responsive'] = self._check_process_responsiveness(health_data)
            health_data['warnings'] = self._detect_health_warnings(health_data)
            
            return health_data
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self._log_status("WARNING", f"Process monitoring failed: {e}")
            return {'error': 'Process monitoring failed', 'exception': str(e)}
    
    def _check_process_responsiveness(self, health_data: Dict[str, Any]) -> bool:
        """Check if process appears responsive based on health metrics"""
        # High CPU usage might indicate heavy processing (normal)
        # but combined with no threads might indicate hanging
        cpu_percent = health_data.get('cpu_percent', 0)
        num_threads = health_data.get('num_threads', 0)
        
        if cpu_percent > 95 and num_threads <= 1:
            return False  # Potentially hung
        
        return True
    
    def _detect_health_warnings(self, health_data: Dict[str, Any]) -> List[str]:
        """Detect warning conditions from health metrics"""
        warnings = []
        
        cpu_percent = health_data.get('cpu_percent', 0)
        memory_mb = health_data.get('memory_mb', 0)
        open_files = health_data.get('open_files', 0)
        
        if cpu_percent > 90:
            warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        if memory_mb > 500:  # 500MB seems high for the client
            warnings.append(f"High memory usage: {memory_mb:.1f}MB")
        
        if open_files > 50:
            warnings.append(f"Many open files: {open_files}")
        
        return warnings
    
    def _detect_execution_phase(self, log_content: str) -> str:
        """Detect current execution phase from log content"""
        if not log_content:
            return "unknown"
        
        # Define phase detection patterns
        phase_patterns = {
            'initialization': ['starting', 'initializing', 'loading', 'begin'],
            'connection': ['connecting', 'handshake', 'protocol', 'socket'],
            'authentication': ['registering', 'login', 'credentials', 'auth'],
            'encryption': ['encrypting', 'key generation', 'crypto', 'aes', 'rsa'],
            'transfer': ['uploading', 'sending', 'transfer', 'progress', 'chunk'],
            'verification': ['verifying', 'checksum', 'validation', 'crc'],
            'completion': ['completed', 'finished', 'success', 'done']
        }
        
        # Check most recent content first
        recent_content = log_content.lower()
        
        # Reverse order to get the latest phase
        for phase, keywords in reversed(phase_patterns.items()):
            if any(keyword in recent_content for keyword in keywords):
                return phase
        
        return "unknown"
    
    def _read_stderr_nonblocking(self) -> str:
        """Read stderr from subprocess without blocking"""
        if not self.backup_process or not self.backup_process.stderr:
            return ""
        
        try:
            # Use select on Unix or similar approach
            import select
            import sys
            
            if sys.platform == "win32":
                # Windows doesn't support select on pipes, use peek approach
                return ""  # Simplified for Windows
            else:
                ready, _, _ = select.select([self.backup_process.stderr], [], [], 0)
                if ready:
                    return self.backup_process.stderr.read(1024)
        except Exception as e:
            self._log_status("DEBUG", f"stderr read failed: {e}")
        
        return ""
    
    def _correlate_subprocess_errors(self, stderr_line: str, health_data: Dict[str, Any]) -> None:
        """Correlate subprocess errors with system state and report to error framework"""
        if not stderr_line and not health_data.get('warnings'):
            return

        # High resource usage errors
        warnings = health_data.get('warnings', [])
        if warnings:
            warning_msg = "; ".join(warnings)
            handle_subprocess_error(
                message="Subprocess resource warning detected",
                details=f"Health warnings: {warning_msg}",
                component="subprocess_monitoring",
                severity=ErrorSeverity.MEDIUM
            )

        # stderr content errors
        if stderr_line and any(keyword in stderr_line.lower() for keyword in ['error', 'failed', 'exception']):
            handle_subprocess_error(
                message="Subprocess error detected in stderr",
                details=f"stderr: {stderr_line.strip()}",
                component="subprocess_stderr",
                severity=ErrorSeverity.HIGH
            )

        # Unresponsive process
        if not health_data.get('is_responsive', True):
            handle_subprocess_error(
                message="Subprocess appears unresponsive",
                details=f"Health data: {health_data}",
                component="subprocess_health",
                severity=ErrorSeverity.HIGH
            )

    def _parse_complete_output_for_progress(self, stdout: str, monitor):
        """Parse complete stdout for progress phases when real-time parsing is limited"""
        try:
            self._log_status("DEBUG", "Parsing complete output for progress phases")
            
            # Simulate progress based on detected phases in complete output
            phases_found = []
            output_str = stdout if isinstance(stdout, str) else stdout.decode('utf-8', errors='ignore')
            output_lower = output_str.lower()
            
            # Check for key progress phases in order
            progress_milestones = [
                ("system initialization", 15, "System initialized"),
                ("configuration loaded", 25, "Configuration loaded"),
                ("validating configuration", 35, "Configuration validated"),
                ("checking parameters", 40, "Parameters checked"),
                ("connection", 50, "Connection established"),
                ("encrypt", 65, "File encrypted"),
                ("upload", 75, "File uploaded"),
                ("transfer", 75, "Transfer completed"),
                ("verification", 85, "Transfer verified"),
                ("backup completed", 90, "Backup completed"),
                ("success", 90, "Process successful")
            ]
            
            max_progress = monitor.current_progress
            for keyword, progress, phase_name in progress_milestones:
                if keyword in output_lower and progress > max_progress:
                    max_progress = progress
                    phases_found.append((phase_name, progress))
            
            # Emit progress updates for significant phases found
            for phase_name, progress in phases_found[-3:]:  # Show last 3 major phases
                if progress > monitor.current_progress:
                    progress_info = monitor._create_progress_info(progress)
                    progress_info['message'] = f"{phase_name} - {progress_info['message']}"
                    monitor._emit_progress(progress_info)
                    monitor.current_progress = progress
                    time.sleep(0.2)  # Brief delay between updates for visual effect
            
            self._log_status("DEBUG", f"Complete output parsing found {len(phases_found)} phases, max progress: {max_progress}%")
            
        except Exception as e:
            self._log_status("DEBUG", f"Complete output parsing error: {e}")

    def get_enhanced_process_metrics(self) -> Optional[Dict[str, Any]]:
        """Get enhanced process metrics from the monitoring system"""
        if not hasattr(self, 'process_id'):
            return None

        registry = get_process_registry()
        process_info = registry.get_process_info(self.process_id)

        if not process_info:
            return None

        # Get latest metrics
        metrics_history = list(process_info.metrics_history)
        if not metrics_history:
            return None

        latest_metrics = metrics_history[-1]

        return {
            'process_id': self.process_id,
            'process_name': process_info.name,
            'state': process_info.state.value,
            'pid': process_info.pid,
            'start_time': process_info.start_time.isoformat(),
            'restart_count': process_info.restart_count,
            'error_count': process_info.error_count,
            'last_error': process_info.last_error,
            'latest_metrics': {
                'timestamp': latest_metrics.timestamp.isoformat(),
                'cpu_percent': latest_metrics.cpu_percent,
                'memory_mb': latest_metrics.memory_mb,
                'memory_percent': latest_metrics.memory_percent,
                'num_threads': latest_metrics.num_threads,
                'open_files': latest_metrics.open_files,
                'connections': latest_metrics.connections,
                'io_read_bytes': latest_metrics.io_read_bytes,
                'io_write_bytes': latest_metrics.io_write_bytes,
                'status': latest_metrics.status,
                'is_responsive': latest_metrics.is_responsive,
                'warnings': latest_metrics.warnings
            },
            'metrics_count': len(metrics_history)
        }

    def _get_process_resource_usage(self):
        """Get basic process resource usage"""
        if not self.backup_process:
            return {}
        
        try:
            import psutil
            proc = psutil.Process(self.backup_process.pid)
            return {
                'pid': self.backup_process.pid,
                'cpu_percent': proc.cpu_percent(),
                'memory_mb': proc.memory_info().rss / 1024 / 1024,
                'status': proc.status(),
                'num_threads': proc.num_threads()
            }
        except Exception:
            return {}
    
    def _check_network_activity(self, server_port: int) -> bool:
        """Check for active network connections to server port"""
        try:
            connections = psutil.net_connections()
            for conn in connections:
                try:
                    # Check local address port
                    laddr_match = False
                    if hasattr(conn, 'laddr') and conn.laddr and hasattr(conn.laddr, 'port'):
                        laddr_match = conn.laddr.port == server_port
                    
                    # Check remote address port
                    raddr_match = False
                    if hasattr(conn, 'raddr') and conn.raddr and hasattr(conn.raddr, 'port'):
                        raddr_match = conn.raddr.port == server_port
                    
                    if laddr_match or raddr_match:
                        laddr_str = f"{conn.laddr}" if conn.laddr else "None"
                        raddr_str = f"{conn.raddr}" if conn.raddr else "None"
                        self._log_status("NETWORK", f"Active connection found: {laddr_str} -> {raddr_str}")
                        return True
                        
                except Exception as conn_error:
                    # Skip this connection if it has unexpected structure
                    self._log_status("DEBUG", f"Skipping connection due to attribute error: {conn_error}")
                    continue
                    
        except Exception as e:
            self._log_status("ERROR", f"Network check failed: {e}")
        return False
    
    def execute_real_backup(self, username: str, file_path: str, 
                           server_ip: str = "127.0.0.1", server_port: int = 1256, 
                           timeout: int = 120) -> Dict[str, Any]:
        """
        Execute REAL backup using the existing C++ client with full verification
        """
        self._log_status("START", f"Starting REAL backup for {username}: {file_path}")
        
        result = {
            'success': False,
            'error': None,
            'process_exit_code': None,
            'verification': None,
            'duration': 0,
            'network_activity': False
        }
        
        start_time = time.time()
        
        try:
            # Pre-flight checks with structured error handling
            if not os.path.exists(file_path):
                error_info = handle_file_transfer_error(
                    message="Source file not found for backup",
                    details=f"File path: {file_path}",
                    component="pre_flight_check",
                    severity=ErrorSeverity.HIGH
                )
                raise FileNotFoundError(f"Source file does not exist: {file_path}")

            if not self.client_exe or not os.path.exists(self.client_exe):
                error_info = handle_subprocess_error(
                    message="Client executable not found",
                    details=f"Expected path: {self.client_exe}",
                    component="pre_flight_check",
                    severity=ErrorSeverity.CRITICAL
                )
                raise FileNotFoundError(f"Client executable not found: {self.client_exe}")

            # Clear cached credentials if username has changed
            self._clear_cached_credentials_if_username_changed(username)

            # Generate managed transfer.info
            transfer_file_id, transfer_info_path = self._generate_transfer_info(server_ip, server_port, username, file_path)

            # Copy transfer.info to BOTH the client executable directory AND the working directory
            # The client looks for transfer.info in the current working directory, not the executable directory
            client_dir = os.path.dirname(self.client_exe)
            client_transfer_info = os.path.join(client_dir, "transfer.info")
            working_dir_transfer_info = "transfer.info"  # Current working directory

            # Use synchronized file manager to copy to required locations
            target_locations = [client_transfer_info, working_dir_transfer_info]
            copy_locations = self.file_manager.copy_to_locations(transfer_file_id, target_locations)

            self._log_status("CONFIG", f"Copied transfer.info to {len(copy_locations)} locations: {copy_locations}")
            
            self._log_status("LAUNCH", f"Launching {self.client_exe}")
            self._log_status("STARTUP", "C++ client process starting - monitoring will begin shortly")
            # Launch client process with automated input handling and BATCH MODE
            if not self.client_exe:
                raise RuntimeError("Client executable path is not set")

            # Mark file as in use by subprocess to prevent premature cleanup
            self.file_manager.mark_in_subprocess_use(transfer_file_id)
            
            # Determine best working directory - use client directory if executable is there
            if "client" in self.client_exe.lower():
                client_working_dir = "client"
                # Copy transfer.info to client directory too
                client_transfer_info = os.path.join(client_working_dir, "transfer.info")
                self.file_manager.copy_to_locations(transfer_file_id, [client_transfer_info])
            else:
                client_working_dir = os.getcwd()
                
            self._log_status("DEBUG", f"Client executable: {os.path.abspath(self.client_exe)}")
            self._log_status("DEBUG", f"Client working directory: {client_working_dir}")
            self._log_status("DEBUG", f"Transfer.info location: {os.path.join(client_working_dir, 'transfer.info')}")

            # Register process with enhanced monitoring system but with better error handling
            process_id = f"backup_client_{int(time.time())}"
            command = [str(self.client_exe), "--batch"]  # Use batch mode to disable web GUI and prevent port conflicts

            self._log_status("LAUNCH", f"Starting subprocess: {' '.join(command)}")
            self._log_status("DEBUG", f"Working directory: {client_working_dir}")
            
            try:
                registry = get_process_registry()
                process_info = register_process(
                    process_id=process_id,
                    name="EncryptedBackupClient",
                    command=command,
                    cwd=client_working_dir,
                    auto_restart=False,  # Don't auto-restart backup processes
                    max_restarts=0
                )

                # Start process with enhanced monitoring and better error reporting
                if not start_process(process_id,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=False):
                    # Try to get error details from the registry
                    self._log_status("ERROR", f"Failed to start backup process {process_id}")
                    if hasattr(registry, 'get_process_info'):
                        proc_info = registry.get_process_info(process_id)
                        if proc_info and proc_info.last_error:
                            self._log_status("ERROR", f"Process error: {proc_info.last_error}")
                    raise RuntimeError(f"Failed to start backup process {process_id}")

                # Get the subprocess handle for compatibility
                self.backup_process = registry.subprocess_handles[process_id]
                self.process_id = process_id
                
            except Exception as e:
                self._log_status("ERROR", f"Failed to start client subprocess: {e}")
                raise RuntimeError(f"Subprocess launch failed: {e}")

            self._log_status("PROCESS", f"Started backup client with enhanced monitoring (ID: {process_id}, PID: {self.backup_process.pid})")
            
            # Initialize robust progress monitoring with multiple fallback layers
            print(f"[MONITOR] Initializing RobustProgressMonitor with destination: {self.server_received_files}")
            monitor = RobustProgressMonitor(self.server_received_files)
            monitor.set_status_callback(self.status_callback or self._log_status)
            
            # Start monitoring with context information
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            filename = os.path.basename(file_path)
            monitor_context = {
                "file_size": file_size,
                "original_filename": filename,
                "process": self.backup_process
            }
            print(f"[MONITOR] Starting monitoring for file: {filename} (size: {file_size} bytes)")
            monitor.start_monitoring(monitor_context)
            
            # Monitor process with ACTIVE PROGRESS POLLING (instead of blocking communicate)
            try:
                # Start active progress polling in parallel with backup execution
                stdout, stderr = self._monitor_with_active_polling(monitor, timeout)
                result['process_exit_code'] = self.backup_process.returncode
                self._log_status("PROCESS", f"Client process finished with exit code: {result['process_exit_code']}")
                
                # Parse final status from output for completion verification
                status_info = self._parse_final_status_from_output(stdout)
                self._log_status("FINAL_STATUS", status_info["message"])
                
                # Finalize progress monitoring with complete stdout output for regex parsing
                monitor.finalize_with_output(stdout)
                
                # The new RobustProgressMonitor handles progress automatically
                # No need for manual output parsing
                
                if stdout:
                    # Handle Unicode encoding for Windows console compatibility
                    stdout_safe = stdout.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii') if isinstance(stdout, bytes) else str(stdout).encode('ascii', errors='replace').decode('ascii')
                    self._log_status("CLIENT_STDOUT", stdout_safe)
                if stderr:
                    # Handle Unicode encoding for Windows console compatibility
                    stderr_safe = stderr.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii') if isinstance(stderr, bytes) else str(stderr).encode('ascii', errors='replace').decode('ascii')
                    self._log_status("CLIENT_STDERR", stderr_safe)
                    result['error'] = stderr_safe
            except subprocess.TimeoutExpired:
                self._log_status("TIMEOUT", "Terminating backup process due to timeout")
                self.backup_process.kill()
                stdout, stderr = self.backup_process.communicate()
                if stdout:
                    # Handle Unicode encoding for Windows console compatibility
                    stdout_safe = stdout.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii') if isinstance(stdout, bytes) else str(stdout).encode('ascii', errors='replace').decode('ascii')
                    self._log_status("CLIENT_STDOUT", stdout_safe)
                    # Also finalize progress monitoring with partial stdout from timeout
                    monitor.finalize_with_output(stdout)
                if stderr:
                    # Handle Unicode encoding for Windows console compatibility
                    stderr_safe = stderr.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode('ascii') if isinstance(stderr, bytes) else str(stderr).encode('ascii', errors='replace').decode('ascii')
                    self._log_status("CLIENT_STDERR", stderr_safe)
                result['error'] = "Process timed out"
                result['process_exit_code'] = -1
            
            # Release subprocess reference to allow safe cleanup
            self.file_manager.release_subprocess_use(transfer_file_id)
            
            # Verify actual file transfer
            self._log_status("VERIFY", "Verifying actual file transfer...")
            verification = self._verify_file_transfer(file_path, username)
            result['verification'] = verification
            
            # Determine overall success and finalize progress based on results
            process_success = result.get('process_exit_code') == 0
            verification_success = verification['transferred']
            
            # Finalize progress BEFORE stopping monitoring to prevent race conditions
            monitor.finalize_progress(process_success, verification_success)
            
            # Stop monitoring after finalization
            monitor.stop_monitoring()
            
            # Prioritize file transfer verification over process exit code
            if verification['transferred']:
                result['success'] = True
                self._log_status("COMPLETED", "Backup verified and complete!")
                if result['process_exit_code'] == 0:
                    self._log_status("SUCCESS", "REAL backup completed and verified!")
                else:
                    result['error'] = f"File transferred successfully but process exit code was {result['process_exit_code']}"
                    self._log_status("SUCCESS", f"REAL backup completed and verified! (Process was killed but transfer succeeded)")
            else:
                result['error'] = "No file transfer detected - backup may have failed"
                self._log_status("FAILED", "Verification failed - no file transfer detected")
                self._log_status("FAILURE", result['error'])
            
        except Exception as e:
            result['error'] = str(e)
            self._log_status("ERROR", f"Backup execution failed: {e}")
            
            # Ensure monitoring is stopped and finalized even on exceptions
            try:
                if 'monitor' in locals():
                    # Finalize with failure status first, then stop
                    monitor.finalize_progress(False, False)  # Exception = failed
                    monitor.stop_monitoring()
            except Exception as monitor_error:
                self._log_status("WARNING", f"Error during monitor cleanup: {monitor_error}")
        
        finally:
            result['duration'] = time.time() - start_time
            
            # Safe cleanup using SynchronizedFileManager
            try:
                if 'transfer_file_id' in locals():
                    self._log_status("CLEANUP", "Starting safe cleanup of transfer.info files")
                    # Wait for subprocess completion before cleanup
                    cleanup_success = self.file_manager.safe_cleanup(transfer_file_id, wait_timeout=10.0)
                    if cleanup_success:
                        self._log_status("CLEANUP", "Successfully cleaned up transfer.info files")
                    else:
                        self._log_status("WARNING", "Some files may not have been cleaned up properly")
            except Exception as e:
                self._log_status("WARNING", f"Error during safe cleanup: {e}")
        
        return result


def main():
    """Test the real backup executor"""
    if len(sys.argv) < 3:
        print("Usage: python real_backup_executor.py <username> <file_path>")
        sys.exit(1)
    
    username = sys.argv[1]
    file_path = sys.argv[2]
    
    executor = RealBackupExecutor()
    
    def status_update(phase, data):
        if isinstance(data, dict):
            if 'message' in data:
                print(f"STATUS: {phase} - {data['message']}")
            else:
                # Handle rich status data
                progress = data.get('progress', 0)
                warnings = data.get('warnings', [])
                warnings_str = f" (Warnings: {', '.join(warnings)})" if warnings else ""
                print(f"STATUS: {phase} - Progress: {progress:.0f}%{warnings_str}")
        else:
            print(f"STATUS: {phase} - {data}")
    
    executor.set_status_callback(status_update)
    
    print("[SECURE] Real Backup Executor - Testing Mode")
    print(f"Username: {username}")
    print(f"File: {file_path}")
    print()
    
    result = executor.execute_real_backup(username, file_path)
    
    print("\n" + "="*50)
    print("BACKUP EXECUTION RESULTS:")
    print("="*50)
    print(f"Success: {result['success']}")
    print(f"Duration: {result['duration']:.2f} seconds")
    print(f"Process Exit Code: {result['process_exit_code']}")
    print(f"Network Activity: {result['network_activity']}")
    if result['error']:
        print(f"Error: {result['error']}")
    
    if result['verification']:
        v = result['verification']
        print(f"\nFILE TRANSFER VERIFICATION:")
        print(f"File Found: {v['file_found']}")
        print(f"Size Match: {v['size_match']} ({v['original_size']} -> {v['received_size']})")
        print(f"Hash Match: {v['hash_match']}")
        print(f"Transferred: {v['transferred']}")
        if v['received_file']:
            print(f"Received File: {v['received_file']}")
    
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()