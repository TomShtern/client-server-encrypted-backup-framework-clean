#!/usr/bin/env python3
"""
Live Log Monitor for CyberBackup 3.0
Provides real-time monitoring of server log files with filtering and colored output
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import threading


# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


def colorize_log_level(line: str, use_colors: bool = True) -> str:
    """Add colors to log lines based on log level"""
    if not use_colors:
        return line
    
    line_upper = line.upper()
    
    if " DEBUG " in line_upper:
        return f"{Colors.DIM}{Colors.BRIGHT_BLACK}{line}{Colors.RESET}"
    elif " INFO " in line_upper:
        return f"{Colors.CYAN}{line}{Colors.RESET}"
    elif " WARNING " in line_upper:
        return f"{Colors.YELLOW}{line}{Colors.RESET}"
    elif " ERROR " in line_upper:
        return f"{Colors.RED}{line}{Colors.RESET}"
    elif " CRITICAL " in line_upper:
        return f"{Colors.BOLD}{Colors.BRIGHT_RED}{line}{Colors.RESET}"
    else:
        return line


def get_log_files(logs_dir: str = "logs") -> List[Dict]:
    """Get all available log files with metadata"""
    logs_path = Path(logs_dir)
    if not logs_path.exists():
        return []
    
    log_files = []
    for log_file in logs_path.glob("*.log"):
        if log_file.name.startswith("latest-"):
            continue  # Skip latest symlinks
        
        # Determine server type
        if "api-server" in log_file.name:
            server_type = "API Server"
            color = Colors.BLUE
        elif "backup-server" in log_file.name:
            server_type = "Backup Server"  
            color = Colors.GREEN
        else:
            server_type = "Unknown"
            color = Colors.WHITE
        
        try:
            stat = log_file.stat()
            log_files.append({
                'path': str(log_file),
                'name': log_file.name,
                'server_type': server_type,
                'color': color,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'exists': True
            })
        except OSError:
            continue
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: x['modified'], reverse=True)
    return log_files


def follow_file(file_path: str, lines_from_end: int = 50):
    """Generator that yields new lines from a file as they're added"""
    file_path_obj = Path(file_path)
    
    # Read existing lines if requested
    if lines_from_end > 0 and file_path_obj.exists():
        try:
            with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                if (lines := f.readlines()):
                    # Yield the last N lines
                    for line in lines[-lines_from_end:]:
                        yield line.rstrip('\n\r')
        except Exception as e:
            yield f"[ERROR] Could not read existing content: {e}"
    
    # Follow new lines
    last_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
    
    while True:
        try:
            if file_path_obj.exists():
                current_size = file_path_obj.stat().st_size
                if current_size > last_size:
                    with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(last_size)
                        for line in f:
                            yield line.rstrip('\n\r')
                    last_size = current_size
                elif current_size < last_size:
                    # File was truncated or recreated
                    last_size = 0
                    yield "[INFO] Log file was truncated or recreated"
            
            time.sleep(0.1)  # Small delay to avoid high CPU usage
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            yield f"[ERROR] Error following file: {e}"
            time.sleep(1)


def monitor_single_file(file_path: str, server_type: str, color: str, 
                       filter_level: Optional[str] = None, 
                       filter_keywords: Optional[List[str]] = None,
                       show_colors: bool = True,
                       tail_lines: int = 50):
    """Monitor a single log file"""
    filter_keywords = filter_keywords or []
    
    print(f"{color}[{server_type}] Monitoring: {file_path}{Colors.RESET}")
    print(f"{Colors.DIM}Filter Level: {filter_level or 'All'}, Keywords: {filter_keywords or 'None'}{Colors.RESET}")
    print("-" * 80)
    
    try:
        for line in follow_file(file_path, tail_lines):
            # Apply level filter
            if filter_level:
                level_found = False
                line_upper = line.upper()
                if filter_level.upper() == "DEBUG" and any(level in line_upper for level in [" DEBUG ", " INFO ", " WARNING ", " ERROR ", " CRITICAL "]):
                    level_found = True
                elif filter_level.upper() == "INFO" and any(level in line_upper for level in [" INFO ", " WARNING ", " ERROR ", " CRITICAL "]):
                    level_found = True
                elif filter_level.upper() == "WARNING" and any(level in line_upper for level in [" WARNING ", " ERROR ", " CRITICAL "]):
                    level_found = True
                elif filter_level.upper() == "ERROR" and any(level in line_upper for level in [" ERROR ", " CRITICAL "]):
                    level_found = True
                elif filter_level.upper() == "CRITICAL" and " CRITICAL " in line_upper:
                    level_found = True
                
                if not level_found:
                    continue
            
            # Apply keyword filter
            if filter_keywords and all(keyword.lower() not in line.lower() for keyword in filter_keywords):
                continue
            
            # Format and display line
            timestamp = datetime.now().strftime('%H:%M:%S')
            if show_colors:
                colored_line = colorize_log_level(line, show_colors)
                print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {color}[{server_type[:3]}]{Colors.RESET} {colored_line}")
            else:
                print(f"[{timestamp}] [{server_type[:3]}] {line}")
                
    except KeyboardInterrupt:
        print(f"\n{color}[{server_type}] Monitoring stopped{Colors.RESET}")


def monitor_multiple_files(log_files: List[Dict], 
                          filter_level: Optional[str] = None,
                          filter_keywords: Optional[List[str]] = None,
                          show_colors: bool = True,
                          tail_lines: int = 50):
    """Monitor multiple log files concurrently"""
    print(f"{Colors.BOLD}Starting multi-file log monitoring...{Colors.RESET}")
    print(f"Files: {len(log_files)}")
    for lf in log_files:
        print(f"  - {lf['color']}{lf['server_type']}: {lf['name']}{Colors.RESET}")
    print("-" * 80)
    
    threads = []
    
    try:
        for log_file in log_files:
            thread = threading.Thread(
                target=monitor_single_file,
                args=(log_file['path'], log_file['server_type'], log_file['color'], 
                      filter_level, filter_keywords, show_colors, tail_lines),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads (they run indefinitely until KeyboardInterrupt)
        while any(t.is_alive() for t in threads):
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.BOLD}Stopping all monitors...{Colors.RESET}")


def list_log_files():
    """List all available log files"""
    log_files = get_log_files()
    
    if not log_files:
        print("No log files found in logs/ directory")
        return
    
    print(f"{Colors.BOLD}Available Log Files:{Colors.RESET}")
    print()
    
    for i, lf in enumerate(log_files, 1):
        size_mb = lf['size'] / (1024 * 1024)
        modified_str = lf['modified'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{i:2d}. {lf['color']}{lf['server_type']:<15}{Colors.RESET} {lf['name']}")
        print(f"     Path: {lf['path']}")
        print(f"     Size: {size_mb:.2f} MB, Modified: {modified_str}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Live Log Monitor for CyberBackup 3.0")
    
    # File selection
    parser.add_argument('--file', '-f', type=str, help='Specific log file to monitor')
    parser.add_argument('--server', '-s', choices=['api', 'backup', 'both'], default='both',
                       help='Server type to monitor (default: both)')
    parser.add_argument('--latest', '-l', action='store_true', 
                       help='Monitor the most recent log files')
    
    # Monitoring options
    parser.add_argument('--follow', action='store_true', default=True,
                       help='Follow log files for new content (default: True)')
    parser.add_argument('--tail', '-n', type=int, default=50,
                       help='Number of lines to show from end of file (default: 50)')
    
    # Filtering options
    parser.add_argument('--level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Filter by minimum log level')
    parser.add_argument('--keywords', '-k', nargs='+', help='Filter by keywords')
    
    # Display options
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--list', action='store_true', help='List available log files and exit')
    
    args = parser.parse_args()
    
    # Handle list command
    if args.list:
        list_log_files()
        return
    
    # Disable colors on Windows if requested or if not a terminal
    show_colors = not args.no_color and sys.stdout.isatty()
    
    # Get available log files
    all_log_files = get_log_files()
    
    if not all_log_files:
        print("No log files found in logs/ directory")
        print("Make sure the servers have been started at least once to generate log files.")
        return
    
    # Select files to monitor
    files_to_monitor = []
    
    if args.file:
        # Monitor specific file
        file_path = Path(args.file)
        if file_path.exists():
            server_type = "Custom"
            color = Colors.WHITE
            if "api-server" in str(file_path):
                server_type = "API Server"
                color = Colors.BLUE
            elif "backup-server" in str(file_path):
                server_type = "Backup Server"
                color = Colors.GREEN
            
            files_to_monitor.append({
                'path': str(file_path),
                'server_type': server_type,
                'color': color
            })
        else:
            print(f"File not found: {args.file}")
            return
    else:
        # Filter by server type
        for lf in all_log_files:
            if args.server == 'both':
                files_to_monitor.append(lf)
            elif args.server == 'api' and 'api-server' in lf['name']:
                files_to_monitor.append(lf)
            elif args.server == 'backup' and 'backup-server' in lf['name']:
                files_to_monitor.append(lf)
        
        # If latest flag is set, only keep the most recent file per server type
        if args.latest:
            api_files = [f for f in files_to_monitor if 'api-server' in f['name']]
            backup_files = [f for f in files_to_monitor if 'backup-server' in f['name']]
            
            files_to_monitor = []
            if api_files:
                files_to_monitor.append(api_files[0])  # Already sorted by newest first
            if backup_files:
                files_to_monitor.append(backup_files[0])
    
    if not files_to_monitor:
        print("No matching log files found")
        return
    
    # Start monitoring
    if len(files_to_monitor) == 1:
        lf = files_to_monitor[0]
        monitor_single_file(
            lf['path'], lf['server_type'], lf['color'],
            args.level, args.keywords, show_colors, args.tail
        )
    else:
        monitor_multiple_files(
            files_to_monitor, args.level, args.keywords, show_colors, args.tail
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.BOLD}Log monitoring stopped{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)