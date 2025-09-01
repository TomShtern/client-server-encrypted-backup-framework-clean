"""
Purpose: Advanced system integration and monitoring tools
Logic: File integrity checks, session management, system monitoring
No Direct UI: Core business logic only, UI components call these methods
"""

"""
System Integration Tools for Flet Server GUI
Advanced system management tools including file integrity verification and client session management
Phase 7.3 Implementation: Professional system administration features
"""

import flet as ft
import os
import hashlib
from .theme_compatibility import TOKENS
import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class FileIntegrityResult:
    """Result of file integrity check"""
    filepath: str
    expected_hash: Optional[str]
    actual_hash: str
    size: int
    modified_time: datetime
    status: str  # "valid", "corrupted", "missing", "unknown"
    error: Optional[str] = None

@dataclass
class ClientSession:
    """Extended client session information"""
    client_id: str
    ip_address: str
    connection_time: datetime
    last_activity: datetime
    files_transferred: int
    bytes_transferred: int
    status: str  # "active", "idle", "disconnected"
    client_info: Dict[str, Any]
    session_duration: timedelta = None

class FileIntegrityManager:
    """
    Advanced file integrity verification and repair system.
    Provides comprehensive file validation and corruption detection.
    """
    
    def __init__(self, server_bridge, storage_directory: str = "received_files"):
        """Initialize file integrity manager"""
        self.server_bridge = server_bridge
        self.storage_directory = storage_directory
        self.integrity_database_file = "file_integrity.json"
        
        # Load or initialize integrity database
        self.integrity_database: Dict[str, Dict] = self._load_integrity_database()
        
        # Scan state
        self.scanning_active = False
        self.scan_progress = 0
        self.scan_results: List[FileIntegrityResult] = []
        
        # UI components
        self.progress_bar = ft.ProgressBar(value=0, visible=False)
        self.results_table = None
        self.scan_status = ft.Text("Ready to scan", size=12)
        
        logger.info("ג… File integrity manager initialized")
    
    def create_integrity_tools(self) -> ft.Container:
        """Create file integrity verification tools UI"""
        
        # Control panel
        control_panel = ft.Row([
            ft.ElevatedButton(
                text="Quick Scan",
                icon=ft.icons.scanner,
                on_click=self._start_quick_scan,
                bgcolor=TOKENS['primary']
            ),
            ft.ElevatedButton(
                text="Full Scan",
                icon=ft.icons.manage_search,
                on_click=self._start_full_scan,
                bgcolor=TOKENS['secondary']
            ),
            ft.ElevatedButton(
                text="Repair Issues",
                icon=ft.icons.build,
                on_click=self._repair_files,
                bgcolor=TOKENS["secondary"],
                disabled=True
            ),
            ft.Container(expand=1),
            ft.ElevatedButton(
                text="Export Report",
                icon=ft.icons.file_download,
                on_click=self._export_integrity_report
            )
        ])
        
        # Progress section
        progress_section = ft.Container(
            content=ft.Column([
                self.scan_status,
                self.progress_bar
            ]),
            padding=10,
            bgcolor=TOKENS["surface_variant"],
            border_radius=8,
            visible=True
        )
        
        # Results section
        results_section = self._create_results_table()
        
        # Statistics panel
        stats_panel = self._create_stats_panel()
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "File Integrity Verification",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=TOKENS["primary"]
                ),
                ft.Text(
                    "Verify and repair file corruption in the backup storage",
                    size=14,
                    color=TOKENS["outline"]
                ),
                ft.Divider(height=20),
                control_panel,
                ft.Divider(),
                progress_section,
                ft.Divider(),
                stats_panel,
                ft.Divider(),
                results_section
            ], spacing=10),
            padding=20,
            expand=True
        )
    
    def _create_results_table(self) -> ft.Container:
        """Create table for integrity scan results"""
        
        self.results_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("File", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Last Modified", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            border=ft.border.all(1, TOKENS["outline"]),
            border_radius=8
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Scan Results", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.results_table,
                    height=300,
                    scroll=ft.ScrollMode.AUTO
                )
            ]),
            expand=True
        )
    
    def _create_stats_panel(self) -> ft.Container:
        """Create statistics panel"""
        
        return ft.Container(
            content=ft.Row([
                self._create_stat_card("Total Files", "0", ft.icons.folder, TOKENS["primary"]),
                self._create_stat_card("Valid Files", "0", ft.icons.check_circle, TOKENS["secondary"]),
                self._create_stat_card("Corrupted", "0", ft.icons.error, TOKENS["error"]),
                self._create_stat_card("Missing", "0", ft.icons.help, TOKENS["secondary"])
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            bgcolor=TOKENS["surface_variant"],
            padding=15,
            border_radius=8
        )
    
    def _create_stat_card(self, title: str, value: str, icon, color) -> ft.Card:
        """Create a statistics card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=32, color=color),
                    ft.Text(title, size=12, text_align=ft.TextAlign.CENTER),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=color, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=120,
                padding=15
            )
        )
    
    def _start_quick_scan(self, e):
        """Start quick integrity scan (recently modified files)"""
        if not self.scanning_active:
            self.scanning_active = True
            self.scan_status.value = "Starting quick scan..."
            self.progress_bar.visible = True
            self.progress_bar.value = 0
            
            # Update UI
            self.scan_status.update()
            self.progress_bar.update()
            
            # Start scan in background
            threading.Thread(target=self._perform_quick_scan, daemon=True).start()
            logger.info("נ” Quick integrity scan started")
    
    def _start_full_scan(self, e):
        """Start full integrity scan (all files)"""
        if not self.scanning_active:
            self.scanning_active = True
            self.scan_status.value = "Starting full scan..."
            self.progress_bar.visible = True
            self.progress_bar.value = 0
            
            # Update UI
            self.scan_status.update()
            self.progress_bar.update()
            
            # Start scan in background
            threading.Thread(target=self._perform_full_scan, daemon=True).start()
            logger.info("נ” Full integrity scan started")
    
    def _perform_quick_scan(self):
        """Perform quick scan (last 24 hours)"""
        try:
            storage_path = Path(self.storage_directory)
            if not storage_path.exists():
                self.scan_status.value = "Storage directory not found"
                self.scanning_active = False
                return
            
            # Find recently modified files
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_files = []
            
            for file_path in storage_path.rglob("*"):
                if file_path.is_file():
                    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if modified_time > cutoff_time:
                        recent_files.append(file_path)
            
            self._scan_files(recent_files, "Quick Scan")
            
        except Exception as ex:
            logger.error(f"ג Error in quick scan: {ex}")
            self.scan_status.value = f"Scan error: {ex}"
        finally:
            self.scanning_active = False
            self.progress_bar.visible = False
            self.scan_status.update()
            self.progress_bar.update()
    
    def _perform_full_scan(self):
        """Perform full integrity scan"""
        try:
            storage_path = Path(self.storage_directory)
            if not storage_path.exists():
                self.scan_status.value = "Storage directory not found"
                self.scanning_active = False
                return
            
            # Find all files
            all_files = [f for f in storage_path.rglob("*") if f.is_file()]
            self._scan_files(all_files, "Full Scan")
            
        except Exception as ex:
            logger.error(f"ג Error in full scan: {ex}")
            self.scan_status.value = f"Scan error: {ex}"
        finally:
            self.scanning_active = False
            self.progress_bar.visible = False
            self.scan_status.update()
            self.progress_bar.update()
    
    def _scan_files(self, file_list: List[Path], scan_type: str):
        """Scan a list of files for integrity"""
        self.scan_results.clear()
        total_files = len(file_list)
        
        for i, file_path in enumerate(file_list):
            if not self.scanning_active:
                break
            
            # Update progress
            progress = (i + 1) / total_files
            self.progress_bar.value = progress
            self.scan_status.value = f"{scan_type}: {i + 1}/{total_files} - {file_path.name}"
            
            # Check file integrity
            result = self._check_file_integrity(file_path)
            self.scan_results.append(result)
            
            # Update UI periodically
            if i % 10 == 0:
                self.progress_bar.update()
                self.scan_status.update()
        
        # Update results table
        self._update_results_table()
        self._update_stats_panel()
        
        self.scan_status.value = f"{scan_type} complete: {len(self.scan_results)} files checked"
        logger.info(f"ג… {scan_type} completed: {len(self.scan_results)} files")
    
    def _check_file_integrity(self, file_path: Path) -> FileIntegrityResult:
        """Check integrity of a single file"""
        try:
            if not file_path.exists():
                return FileIntegrityResult(
                    filepath=str(file_path),
                    expected_hash=None,
                    actual_hash="",
                    size=0,
                    modified_time=datetime.now(),
                    status="missing"
                )
            
            # Calculate current hash
            actual_hash = self._calculate_file_hash(file_path)
            file_size = file_path.stat().st_size
            modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Check against stored hash
            file_key = str(file_path.relative_to(self.storage_directory))
            stored_info = self.integrity_database.get(file_key, {})
            expected_hash = stored_info.get("hash")
            
            if expected_hash is None:
                # First time seeing this file
                status = "unknown"
                # Store hash for future reference
                self.integrity_database[file_key] = {
                    "hash": actual_hash,
                    "size": file_size,
                    "created": datetime.now().isoformat(),
                    "last_checked": datetime.now().isoformat()
                }
            elif expected_hash == actual_hash:
                status = "valid"
                # Update last checked time
                self.integrity_database[file_key]["last_checked"] = datetime.now().isoformat()
            else:
                status = "corrupted"
                logger.warning(f"ג ן¸ File corruption detected: {file_path}")
            
            return FileIntegrityResult(
                filepath=str(file_path),
                expected_hash=expected_hash,
                actual_hash=actual_hash,
                size=file_size,
                modified_time=modified_time,
                status=status
            )
            
        except Exception as ex:
            logger.error(f"ג Error checking file {file_path}: {ex}")
            return FileIntegrityResult(
                filepath=str(file_path),
                expected_hash=None,
                actual_hash="",
                size=0,
                modified_time=datetime.now(),
                status="error",
                error=str(ex)
            )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _update_results_table(self):
        """Update the results table with scan results"""
        rows = []

        for result in self.scan_results[-50:]:  # Show last 50 results
            # Status indicator with color
            if result.status == "corrupted":
                status_cell = ft.DataCell(ft.Row([
                    ft.Icon(ft.icons.error, color=TOKENS["error"], size=16),
                    ft.Text("Corrupted", color=TOKENS["error"])
                ]))
            elif result.status == "missing":
                status_cell = ft.DataCell(ft.Row([
                    ft.Icon(ft.icons.help, color=TOKENS["secondary"], size=16),
                    ft.Text("Missing", color=TOKENS["secondary"])
                ]))
            elif result.status == "valid":
                status_cell = ft.DataCell(ft.Row([
                    ft.Icon(ft.icons.check_circle, color=TOKENS["secondary"], size=16),
                    ft.Text("Valid", color=TOKENS["secondary"])
                ]))
            else:
                status_cell = ft.DataCell(ft.Row([
                    ft.Icon(ft.icons.info, color=TOKENS["primary"], size=16),
                    ft.Text("Unknown", color=TOKENS["primary"])
                ]))

            # Action buttons
            actions = []
            if result.status == "corrupted":
                actions.extend(
                    (
                        ft.IconButton(
                            icon=ft.icons.refresh,
                            tooltip="Verify Again",
                            on_click=lambda e, path=result.filepath: self._reverify_file(
                                path
                            ),
                        ),
                        ft.IconButton(
                            icon=ft.icons.delete,
                            tooltip="Delete Corrupted File",
                            on_click=lambda e, path=result.filepath: self._delete_corrupted_file(
                                path
                            ),
                        ),
                    )
                )
            actions_cell = ft.DataCell(ft.Row(actions))

            row = ft.DataRow([
                ft.DataCell(ft.Text(Path(result.filepath).name, size=12)),
                status_cell,
                ft.DataCell(ft.Text(f"{result.size:,} bytes", size=12)),
                ft.DataCell(ft.Text(result.modified_time.strftime("%Y-%m-%d %H:%M"), size=12)),
                actions_cell
            ])

            rows.append(row)

        self.results_table.rows = rows
        self.results_table.update()
    
    def _update_stats_panel(self):
        """Update statistics panel with current scan results"""
        stats = {
            "total": len(self.scan_results),
            "valid": len([r for r in self.scan_results if r.status == "valid"]),
            "corrupted": len([r for r in self.scan_results if r.status == "corrupted"]),
            "missing": len([r for r in self.scan_results if r.status == "missing"])
        }
        
        # Update stat cards (this is simplified - in a real implementation,
        # you'd need to properly update the card text values)
        logger.info(f"נ“ Scan statistics: {stats}")
    
    def _repair_files(self, e):
        """Attempt to repair corrupted files"""
        corrupted_files = [r for r in self.scan_results if r.status == "corrupted"]
        
        if not corrupted_files:
            logger.info("ג„¹ן¸ No corrupted files to repair")
            return
        
        logger.info(f"נ”§ Attempting to repair {len(corrupted_files)} corrupted files")
        # TODO: Implement file repair logic (restore from backup, re-download, etc.)
    
    def _export_integrity_report(self, e):
        """Export integrity scan report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integrity_report_{timestamp}.json"
            
            report_data = {
                "scan_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_files": len(self.scan_results),
                    "storage_directory": self.storage_directory
                },
                "statistics": {
                    "valid_files": len([r for r in self.scan_results if r.status == "valid"]),
                    "corrupted_files": len([r for r in self.scan_results if r.status == "corrupted"]),
                    "missing_files": len([r for r in self.scan_results if r.status == "missing"]),
                    "unknown_files": len([r for r in self.scan_results if r.status == "unknown"])
                },
                "results": [asdict(result) for result in self.scan_results]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"ג… Integrity report exported: {filename}")
            
        except Exception as ex:
            logger.error(f"ג Error exporting integrity report: {ex}")
    
    def _reverify_file(self, filepath: str):
        """Re-verify a specific file"""
        file_path = Path(filepath)
        result = self._check_file_integrity(file_path)
        
        # Update results
        for i, existing_result in enumerate(self.scan_results):
            if existing_result.filepath == filepath:
                self.scan_results[i] = result
                break
        
        self._update_results_table()
        logger.info(f"נ” Re-verified file: {filepath} -> {result.status}")
    
    def _delete_corrupted_file(self, filepath: str):
        """Delete a corrupted file after confirmation"""
        # TODO: Add confirmation dialog
        try:
            Path(filepath).unlink()
            logger.info(f"נ—‘ן¸ Deleted corrupted file: {filepath}")
            
            # Remove from results
            self.scan_results = [r for r in self.scan_results if r.filepath != filepath]
            self._update_results_table()
            
        except Exception as ex:
            logger.error(f"ג Error deleting file {filepath}: {ex}")
    
    def _load_integrity_database(self) -> Dict[str, Dict]:
        """Load file integrity database"""
        try:
            if os.path.exists(self.integrity_database_file):
                with open(self.integrity_database_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as ex:
            logger.warning(f"ג ן¸ Could not load integrity database: {ex}")
        
        return {}
    
    def _save_integrity_database(self):
        """Save file integrity database"""
        try:
            with open(self.integrity_database_file, 'w', encoding='utf-8') as f:
                json.dump(self.integrity_database, f, indent=2, default=str)
        except Exception as ex:
            logger.error(f"ג Error saving integrity database: {ex}")


class AdvancedClientSessionManager:
    """
    Advanced client session management with detailed monitoring and control.
    Provides comprehensive client analytics and session control.
    """
    
    def __init__(self, server_bridge):
        """Initialize advanced session manager"""
        self.server_bridge = server_bridge
        self.session_history: List[ClientSession] = []
        self.monitoring_active = False
        
        # UI components
        self.sessions_table = None
        self.session_stats = {}
        
        logger.info("ג… Advanced client session manager initialized")
    
    def create_session_manager(self) -> ft.Container:
        """Create advanced session management UI"""
        
        # Control panel
        control_panel = ft.Row([
            ft.ElevatedButton(
                text="Refresh Sessions",
                icon=ft.icons.refresh,
                on_click=self._refresh_sessions,
                bgcolor=TOKENS["primary"]
            ),
            ft.ElevatedButton(
                text="Start Monitoring",
                icon=ft.icons.monitor,
                on_click=self._toggle_monitoring,
                bgcolor=TOKENS["secondary"]
            ),
            ft.Container(expand=1),
            ft.ElevatedButton(
                text="Export Sessions",
                icon=ft.icons.file_download,
                on_click=self._export_session_data
            )
        ])
        
        # Statistics panel
        stats_panel = self._create_session_stats_panel()
        
        # Sessions table
        sessions_table = self._create_sessions_table()
        
        # Session details panel
        details_panel = self._create_session_details_panel()
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Advanced Client Session Management",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=TOKENS["primary"]
                ),
                ft.Text(
                    "Monitor, analyze, and manage client connections and sessions",
                    size=14,
                    color=TOKENS["outline"]
                ),
                ft.Divider(height=20),
                control_panel,
                ft.Divider(),
                stats_panel,
                ft.Divider(),
                sessions_table,
                ft.Divider(),
                details_panel
            ], spacing=10),
            padding=20,
            expand=True
        )
    
    def _create_session_stats_panel(self) -> ft.Container:
        """Create session statistics panel"""
        return ft.Container(
            content=ft.Row([
                self._create_stat_card("Active Sessions", "0", ft.icons.people, TOKENS["secondary"]),
                self._create_stat_card("Total Connections", "0", ft.icons.timeline, TOKENS["primary"]),
                self._create_stat_card("Data Transferred", "0 MB", ft.icons.cloud_upload, TOKENS["secondary"]),
                self._create_stat_card("Avg Session Time", "0 min", ft.icons.timer, TOKENS["tertiary"])
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            bgcolor=TOKENS["surface_variant"],
            padding=15,
            border_radius=8
        )
    
    def _create_stat_card(self, title: str, value: str, icon, color) -> ft.Card:
        """Create a statistics card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=32, color=color),
                    ft.Text(title, size=12, text_align=ft.TextAlign.CENTER),
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=color, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=140,
                padding=15
            )
        )
    
    def _create_sessions_table(self) -> ft.Container:
        """Create sessions data table"""
        
        self.sessions_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("IP Address", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Connected", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Files", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Data", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            border=ft.border.all(1, TOKENS["outline"]),
            border_radius=8
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Client Sessions", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.sessions_table,
                    height=300,
                    scroll=ft.ScrollMode.AUTO
                )
            ]),
            expand=True
        )
    
    def _create_session_details_panel(self) -> ft.Container:
        """Create session details panel"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Session Details", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Select a session to view detailed information", size=12, color=TOKENS["outline"])
            ]),
            height=150,
            bgcolor=TOKENS["surface_variant"],
            padding=15,
            border_radius=8
        )
    
    def _refresh_sessions(self, e):
        """Refresh client sessions data"""
        try:
            # Get current client data from server bridge
            clients = self.server_bridge.get_clients()
            
            # Convert to session objects
            sessions = []
            for client in clients:
                session = ClientSession(
                    client_id=client.get('id', ''),
                    ip_address=client.get('ip', ''),
                    connection_time=datetime.fromisoformat(client.get('connect_time', datetime.now().isoformat())),
                    last_activity=datetime.now(),
                    files_transferred=client.get('files_count', 0),
                    bytes_transferred=client.get('total_size', 0),
                    status="active" if client.get('connected', False) else "disconnected",
                    client_info=client
                )
                sessions.append(session)
            
            self.session_history = sessions
            self._update_sessions_table()
            logger.info(f"ג… Refreshed {len(sessions)} client sessions")
            
        except Exception as ex:
            logger.error(f"ג Error refreshing sessions: {ex}")
    
    def _update_sessions_table(self):
        """Update sessions table with current data"""
        rows = []

        for session in self.session_history:
            # Status indicator
            if session.status == "active":
                status_cell = ft.DataCell(ft.Row([
                    ft.Icon(ft.icons.circle, color=TOKENS["secondary"], size=12),
                    ft.Text("Active", color=TOKENS["secondary"], size=12)
                ]))
            else:
                status_cell = ft.DataCell(ft.Row([
                    ft.Icon(ft.icons.circle, color=TOKENS["outline"], size=12),
                    ft.Text("Disconnected", color=TOKENS["outline"], size=12)
                ]))

            # Action buttons
            actions = [
                ft.IconButton(
                    icon=ft.icons.info,
                    tooltip="View Details",
                    on_click=lambda e, s=session: self._show_session_details(s)
                )
            ]

            if session.status == "active":
                actions.append(ft.IconButton(
                    icon=ft.icons.close,
                    tooltip="Disconnect",
                    on_click=lambda e, s=session: self._disconnect_session(s)
                ))

            row = ft.DataRow(
                [
                    ft.DataCell(ft.Text(f"{session.client_id[:8]}...", size=12)),
                    ft.DataCell(ft.Text(session.ip_address, size=12)),
                    status_cell,
                    ft.DataCell(
                        ft.Text(
                            session.connection_time.strftime("%H:%M:%S"), size=12
                        )
                    ),
                    ft.DataCell(ft.Text(str(session.files_transferred), size=12)),
                    ft.DataCell(
                        ft.Text(f"{session.bytes_transferred // 1024} KB", size=12)
                    ),
                    ft.DataCell(ft.Row(actions)),
                ]
            )

            rows.append(row)

        self.sessions_table.rows = rows
        self.sessions_table.update()
    
    def _toggle_monitoring(self, e):
        """Toggle session monitoring"""
        if self.monitoring_active:
            self.monitoring_active = False
            e.control.text = "Start Monitoring"
            e.control.bgcolor = TOKENS["secondary"]
        else:
            self.monitoring_active = True
            e.control.text = "Stop Monitoring"
            e.control.bgcolor = TOKENS["error"]
            asyncio.create_task(self._monitor_sessions())  # ✅ NON-BLOCKING: Use async task instead of thread
        
        e.control.update()
        logger.info(f"{'ג… Started' if self.monitoring_active else 'ג¹ן¸ Stopped'} session monitoring")
    
    async def _monitor_sessions(self):
        """Monitor sessions in background and schedule UI updates safely."""
        while self.monitoring_active:
            try:
                # Get data in background thread (safe)
                sessions_data = self._get_sessions_data_blocking()
                
                # Schedule UI update on the main Flet thread
                if hasattr(self, 'page') and self.page:
                    self.page.run_threadsafe(self._update_sessions_with_data, sessions_data)
                
                await asyncio.sleep(10)  # ✅ NON-BLOCKING: Update every 10 seconds
            except Exception as ex:
                logger.error(f"ג Error in session monitoring: {ex}")
                await asyncio.sleep(30)  # ✅ NON-BLOCKING: Wait longer on error
    
    def _get_sessions_data_blocking(self):
        """Get sessions data in a thread-safe way (ADDED: thread-safe helper)"""
        try:
            # Get current client data from server bridge (safe in background thread)
            clients = self.server_bridge.get_clients()
            
            # Convert to session objects
            sessions = []
            for client in clients:
                session = ClientSession(
                    client_id=client.get('id', ''),
                    ip_address=client.get('ip', ''),
                    connection_time=datetime.fromisoformat(client.get('connect_time', datetime.now().isoformat())),
                    last_activity=datetime.now(),
                    files_transferred=client.get('files_count', 0),
                    bytes_transferred=client.get('total_size', 0),
                    status="active" if client.get('connected', False) else "disconnected",
                    client_info=client
                )
                sessions.append(session)
            
            return sessions
        except Exception as ex:
            logger.error(f"ג Error getting sessions data: {ex}")
            return []
    
    def _update_sessions_with_data(self, sessions_data):
        """Update sessions with data (ADDED: main thread UI update)"""
        try:
            self.session_history = sessions_data
            self._update_sessions_table()
            logger.info(f"ג… Updated {len(sessions_data)} client sessions")
        except Exception as ex:
            logger.error(f"ג Error updating sessions UI: {ex}")
    
    def _show_session_details(self, session: ClientSession):
        """Show detailed session information"""
        logger.info(f"נ“‹ Showing details for session: {session.client_id}")
        # TODO: Implement session details dialog
    
    def _disconnect_session(self, session: ClientSession):
        """Disconnect a client session"""
        try:
            if success := self.server_bridge.disconnect_client(session.client_id):
                session.status = "disconnected"
                self._update_sessions_table()
                logger.info(f"ג… Disconnected client session: {session.client_id}")
            else:
                logger.warning(f"ג ן¸ Failed to disconnect client: {session.client_id}")
        except Exception as ex:
            logger.error(f"ג Error disconnecting session: {ex}")
    
    def _export_session_data(self, e):
        """Export session data to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_data_{timestamp}.json"
            
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_sessions": len(self.session_history)
                },
                "sessions": [asdict(session) for session in self.session_history]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"ג… Session data exported: {filename}")
            
        except Exception as ex:
            logger.error(f"ג Error exporting session data: {ex}")


class SystemIntegrationTools:
    """
    Combined system integration tools manager.
    Provides unified access to file integrity and session management tools.
    """
    
    def __init__(self, server_bridge):
        """Initialize system integration tools"""
        self.server_bridge = server_bridge
        self.file_integrity = FileIntegrityManager(server_bridge)
        self.session_manager = AdvancedClientSessionManager(server_bridge)
        
        logger.info("ג… System integration tools initialized")
    
    def create_integration_tools_view(self) -> ft.Container:
        """Create unified system integration tools view"""
        
        # Tab-based interface
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="File Integrity",
                    icon=ft.icons.verified,
                    content=self.file_integrity.create_integrity_tools()
                ),
                ft.Tab(
                    text="Session Manager", 
                    icon=ft.icons.people,
                    content=self.session_manager.create_session_manager()
                )
            ]
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.integration_instructions, size=32, color=TOKENS["primary"]),
                    ft.Text(
                        "System Integration Tools",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=TOKENS["primary"]
                    )
                ]),
                ft.Text(
                    "Advanced system administration and maintenance tools",
                    size=14,
                    color=TOKENS["outline"]
                ),
                ft.Divider(height=20),
                tabs
            ]),
            padding=20,
            expand=True
        )
    
    def get_file_integrity_manager(self) -> FileIntegrityManager:
        """Get file integrity manager instance"""
        return self.file_integrity
    
    def get_session_manager(self) -> AdvancedClientSessionManager:
        """Get session manager instance"""  
        return self.session_manager
