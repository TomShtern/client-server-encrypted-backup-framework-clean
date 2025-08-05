#!/usr/bin/env python3
"""
Shared logging utilities for CyberBackup 3.0
Provides dual output (console + file) with live monitoring capabilities
"""

import os
import sys
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO


def setup_dual_logging_simple(logger_name: str, server_type: str, 
                             console_level: int = logging.INFO,
                             file_level: int = logging.DEBUG) -> tuple[logging.Logger, str]:
    """
    Simplified dual logging setup using separate handlers (no custom TeeHandler).
    This approach is more reliable and avoids potential circular logging issues.
    """
    
    # Generate timestamped log filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    log_filename = f"{server_type}-{timestamp}.log"
    log_file_path = os.path.join("logs", log_filename)
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Set to lowest level
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                         datefmt='%H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler  
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Log initialization message
    logger.info(f"=== {server_type.upper().replace('-', ' ')} LOGGING INITIALIZED ===")
    logger.info(f"Console Level: {logging.getLevelName(console_level)}")
    logger.info(f"File Level: {logging.getLevelName(file_level)}")
    logger.info(f"Log File: {log_file_path}")
    logger.info("=" * 60)
    
    return logger, log_file_path


def setup_dual_logging(
    logger_name: str,
    server_type: str,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    console_format: str = None,
    include_timestamp: bool = True
) -> tuple[logging.Logger, str]:
    """
    Set up dual logging (console + file) for a server.
    Uses the simplified approach with separate handlers for reliability.
    """
    
    # Use the simplified approach
    logger, log_file_path = setup_dual_logging_simple(logger_name, server_type, console_level, file_level)
    
    # Add live monitoring info
    logger.info(f"Live Monitoring: Get-Content {log_file_path} -Wait -Tail 50")
    
    return logger, log_file_path


def create_log_monitor_info(log_file_path: str, server_type: str) -> dict:
    """
    Create monitoring information for a log file.
    
    Args:
        log_file_path: Path to the log file
        server_type: Type of server for display
    
    Returns:
        Dictionary with monitoring commands and info
    """
    
    abs_path = os.path.abspath(log_file_path)
    
    return {
        'file_path': abs_path,
        'server_type': server_type,
        'powershell_cmd': f'Get-Content "{abs_path}" -Wait -Tail 50',
        'python_cmd': f'python scripts/monitor_logs.py --file="{abs_path}" --follow',
        'size_bytes': os.path.getsize(abs_path) if os.path.exists(abs_path) else 0,
        'exists': os.path.exists(abs_path)
    }


def get_all_log_files() -> list:
    """Get information about all current log files"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return []
    
    log_files = []
    for log_file in logs_dir.glob("*.log"):
        if log_file.name.startswith("latest-"):
            continue  # Skip latest symlinks
            
        # Determine server type from filename
        if "api-server" in log_file.name:
            server_type = "API Server"
        elif "backup-server" in log_file.name:
            server_type = "Backup Server"
        else:
            server_type = "Unknown"
        
        log_files.append({
            'path': str(log_file),
            'name': log_file.name,
            'server_type': server_type,
            'size': log_file.stat().st_size,
            'modified': datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: x['modified'], reverse=True)
    return log_files


if __name__ == "__main__":
    # Test the dual logging setup
    print("Testing dual logging setup...")
    
    logger, log_path = setup_dual_logging("test_logger", "test-server")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print(f"\nLog file created at: {log_path}")
    
    # Display monitoring info
    monitor_info = create_log_monitor_info(log_path, "Test Server")
    print(f"PowerShell live monitoring: {monitor_info['powershell_cmd']}")