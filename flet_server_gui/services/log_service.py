"""
Log Service for Flet Server GUI
Real-time server log integration and management
"""

import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class LogEntry:
    """Data structure for log entries with metadata"""
    
    def __init__(self, timestamp: datetime, level: str, component: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.component = component
        self.message = message
        self.id = f"{timestamp.isoformat()}_{hash(message) % 1000000}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'component': self.component,
            'message': self.message
        }
    
    @classmethod
    def from_line(cls, line: str, component: str = "Server") -> Optional['LogEntry']:
        """Parse a log line into a LogEntry"""
        try:
            # Basic log parsing - could be enhanced for specific formats
            parts = line.strip().split(' - ', 2)
            if len(parts) >= 3:
                timestamp_str = parts[0]
                level = parts[1]
                message = parts[2]
                
                # Try to parse timestamp
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
                except ValueError:
                    timestamp = datetime.now()
                
                return cls(timestamp, level, component, message)
        except Exception as e:
            logger.debug(f"Failed to parse log line: {line} - {e}")
            
        # Return basic entry if parsing fails
        return cls(datetime.now(), "INFO", component, line.strip())

class LogService:
    """
    Real-time server log monitoring and management service.
    NO mock data - reads actual server logs and provides real-time updates.
    """
    
    def __init__(self):
        """Initialize with real log file monitoring"""
        self.log_files = self._discover_log_files()
        self.log_history: List[LogEntry] = []
        self.max_history = 10000  # Keep last 10k entries
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.update_callbacks: List[Callable[[LogEntry], None]] = []
        self.log_queue = Queue()
        
        # File monitoring state
        self.file_positions: Dict[str, int] = {}
        self.last_check = datetime.now()
        
        logger.info(f"✅ Log service initialized with {len(self.log_files)} log files")
    
    def _discover_log_files(self) -> List[Path]:
        """Discover available log files in the system"""
        log_files = []
        
        # Common log file locations
        search_paths = [
            "logs/",
            "python_server/logs/",
            "api_server/logs/",
            "./",
            "../logs/"
        ]
        
        log_patterns = [
            "server.log",
            "backup_server.log", 
            "api_server.log",
            "gui.log",
            "*.log"
        ]
        
        for search_path in search_paths:
            path = Path(search_path)
            if path.exists():
                for pattern in log_patterns:
                    if '*' in pattern:
                        log_files.extend(path.glob(pattern))
                    else:
                        log_file = path / pattern
                        if log_file.exists():
                            log_files.append(log_file)
        
        # Remove duplicates and ensure all files exist
        unique_files = []
        seen = set()
        for file_path in log_files:
            abs_path = file_path.resolve()
            if abs_path not in seen and abs_path.exists():
                unique_files.append(abs_path)
                seen.add(abs_path)
        
        logger.info(f"Discovered log files: {[str(f) for f in unique_files]}")
        return unique_files
    
    def start_monitoring(self) -> bool:
        """Start real-time log monitoring"""
        if self.monitoring_active:
            logger.warning("Log monitoring already active")
            return True
        
        if not self.log_files:
            logger.warning("No log files found to monitor")
            return False
        
        try:
            # Initialize file positions
            for log_file in self.log_files:
                self.file_positions[str(log_file)] = log_file.stat().st_size
            
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
            self.monitor_thread.start()
            
            logger.info("✅ Real-time log monitoring started")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start log monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop real-time log monitoring"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        logger.info("✅ Log monitoring stopped")
    
    def _monitor_logs(self):
        """Background thread for monitoring log files"""
        while self.monitoring_active:
            try:
                self._check_log_files()
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"❌ Error in log monitoring: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _check_log_files(self):
        """Check log files for new content"""
        for log_file in self.log_files:
            try:
                file_path = str(log_file)

                # Check if file still exists
                if not log_file.exists():
                    continue

                current_size = log_file.stat().st_size
                last_position = self.file_positions.get(file_path, 0)

                if current_size > last_position:
                    # Read new content
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()

                    # Process new lines
                    component = log_file.stem.replace('_', ' ').title()
                    for line in new_lines:
                        if line.strip():
                            if entry := LogEntry.from_line(line, component):
                                self._add_log_entry(entry)

                    # Update position
                    self.file_positions[file_path] = current_size

            except Exception as e:
                logger.error(f"❌ Error reading log file {log_file}: {e}")
    
    def _add_log_entry(self, entry: LogEntry):
        """Add a new log entry and notify callbacks"""
        # Add to history (with size limit)
        self.log_history.append(entry)
        if len(self.log_history) > self.max_history:
            self.log_history = self.log_history[-self.max_history:]

        # Add to queue for GUI updates
        try:
            self.log_queue.put_nowait(entry)
        except Exception:
            pass  # Queue full, skip update

        # Notify callbacks
        for callback in self.update_callbacks:
            try:
                callback(entry)
            except Exception as e:
                logger.error(f"❌ Error in log update callback: {e}")
    
    def get_recent_logs(self, limit: int = 100, level_filter: Optional[str] = None) -> List[LogEntry]:
        """Get recent log entries with optional filtering"""
        logs = self.log_history[-limit:] if limit > 0 else self.log_history
        
        if level_filter:
            logs = [entry for entry in logs if entry.level.upper() == level_filter.upper()]
        
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about current logs"""
        if not self.log_history:
            return {
                'total_entries': 0,
                'levels': {},
                'components': {},
                'oldest_entry': None,
                'newest_entry': None
            }
        
        levels = {}
        components = {}
        
        for entry in self.log_history:
            levels[entry.level] = levels.get(entry.level, 0) + 1
            components[entry.component] = components.get(entry.component, 0) + 1
        
        return {
            'total_entries': len(self.log_history),
            'levels': levels,
            'components': components,
            'oldest_entry': min(self.log_history, key=lambda x: x.timestamp).timestamp.isoformat(),
            'newest_entry': max(self.log_history, key=lambda x: x.timestamp).timestamp.isoformat(),
            'monitoring_active': self.monitoring_active,
            'log_files_count': len(self.log_files)
        }
    
    def add_update_callback(self, callback: Callable[[LogEntry], None]):
        """Add callback for real-time log updates"""
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)
            logger.debug("✅ Log update callback added")
    
    def remove_update_callback(self, callback: Callable[[LogEntry], None]):
        """Remove log update callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
            logger.debug("✅ Log update callback removed")
    
    def get_pending_updates(self) -> List[LogEntry]:
        """Get pending log updates from queue"""
        updates = []
        try:
            while True:
                entry = self.log_queue.get_nowait()
                updates.append(entry)
        except Empty:
            pass
        return updates
    
    def clear_logs(self) -> bool:
        """Clear log history (not the actual files)"""
        try:
            self.log_history.clear()
            # Clear the queue
            while not self.log_queue.empty():
                try:
                    self.log_queue.get_nowait()
                except Empty:
                    break
            
            logger.info("✅ Log history cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear logs: {e}")
            return False
    
    def export_logs(self, file_path: str, limit: Optional[int] = None) -> bool:
        """Export logs to a file"""
        try:
            logs_to_export = self.log_history[-limit:] if limit else self.log_history
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Log Export - {datetime.now().isoformat()}\n")
                f.write(f"# Total entries: {len(logs_to_export)}\n\n")
                
                for entry in sorted(logs_to_export, key=lambda x: x.timestamp):
                    f.write(f"{entry.timestamp.isoformat()} - {entry.level} - {entry.component} - {entry.message}\n")
            
            logger.info(f"✅ Logs exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to export logs: {e}")
            return False
    
    def search_logs(self, query: str, case_sensitive: bool = False) -> List[LogEntry]:
        """Search through log entries"""
        if not query:
            return []
        
        if not case_sensitive:
            query = query.lower()
        
        results = []
        for entry in self.log_history:
            message = entry.message if case_sensitive else entry.message.lower()
            component = entry.component if case_sensitive else entry.component.lower()
            
            if query in message or query in component:
                results.append(entry)
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    def add_custom_log_entry(self, level: str, component: str, message: str):
        """Add a custom log entry (for GUI actions, etc.)"""
        entry = LogEntry(datetime.now(), level, component, message)
        self._add_log_entry(entry)
        logger.info(f"Custom log entry added: {level} - {component} - {message}")