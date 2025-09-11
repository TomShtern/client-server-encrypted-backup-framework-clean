#!/usr/bin/env python3
"""
Dashboard View for FletV2
Clean, framework-harmonious implementation following successful patterns.
Optimized for visual appeal and maintainability at ~600 LOC.
"""

import flet as ft
import asyncio
import psutil
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)

def create_dashboard_view(
    server_bridge: Optional[ServerBridge], 
    page: ft.Page, 
    state_manager: Optional[StateManager] = None
) -> ft.Control:
    """
    Create dashboard view with clean, maintainable implementation.
    Follows successful patterns from clients.py and analytics.py.
    """
    logger.info("Creating dashboard view")
    
    # State Management - Simple and Direct
    server_status_data = {}
    system_metrics_data = {}
    activity_data = []
    is_loading = False
    last_updated = None
    
    # UI Control References
    server_status_text = ft.Text("Unknown", size=14, weight=ft.FontWeight.BOLD)
    server_port_text = ft.Text("", size=12, color=ft.Colors.GREY_600)
    uptime_text = ft.Text("", size=12, color=ft.Colors.GREY_600)
    clients_count_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    files_count_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    transfers_count_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    storage_used_text = ft.Text("0 GB", size=28, weight=ft.FontWeight.BOLD)
    
    cpu_progress = ft.ProgressBar(value=0.0, width=200)
    memory_progress = ft.ProgressBar(value=0.0, width=200)
    disk_progress = ft.ProgressBar(value=0.0, width=200)
    cpu_text = ft.Text("0%", size=12)
    memory_text = ft.Text("0%", size=12)
    disk_text = ft.Text("0%", size=12)
    
    activity_list = ft.ListView(expand=True, spacing=8, padding=16)
    last_updated_text = ft.Text("Never", size=12, color=ft.Colors.GREY_600)
    
    start_server_btn = ft.ElevatedButton(
        "Start Server",
        icon=ft.Icons.PLAY_ARROW,
        on_click=lambda e: page.run_task(start_server_action),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE
        )
    )
    
    stop_server_btn = ft.ElevatedButton(
        "Stop Server",
        icon=ft.Icons.STOP,
        on_click=lambda e: page.run_task(stop_server_action),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE
        ),
        disabled=True
    )
    
    # Core Data Functions
    async def load_server_status():
        """Load server status from server bridge with fallback."""
        nonlocal server_status_data
        
        try:
            if server_bridge:
                try:
                    server_status_data = await server_bridge.get_server_status_async()
                    logger.info("Loaded server status from bridge")
                except Exception as e:
                    logger.warning(f"Server bridge failed, using mock data: {e}")
                    server_status_data = generate_mock_server_status()
            else:
                server_status_data = generate_mock_server_status()
                
            update_server_status_ui()
            
        except Exception as e:
            logger.error(f"Failed to load server status: {e}")
            server_status_data = {"running": False, "error": str(e)}
            update_server_status_ui()

    def generate_mock_server_status() -> Dict[str, Any]:
        """Generate mock server status for development/fallback."""
        return {
            "running": True,
            "port": 8080,
            "uptime_seconds": 3600 * 12 + 1800,  # 12.5 hours
            "clients_connected": 3,
            "total_files": 127,
            "total_transfers": 45,
            "storage_used_gb": 2.4
        }

    async def load_system_metrics():
        """Load system metrics using psutil."""
        nonlocal system_metrics_data
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            system_metrics_data = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "memory_total_gb": memory.total / (1024**3),
                "disk_total_gb": disk.total / (1024**3)
            }
            
            update_system_metrics_ui()
            
        except Exception as e:
            logger.error(f"Failed to load system metrics: {e}")
            # Fallback to mock metrics
            system_metrics_data = {
                "cpu_percent": 25.0,
                "memory_percent": 68.0,
                "disk_percent": 45.0,
                "memory_total_gb": 16.0,
                "disk_total_gb": 512.0
            }
            update_system_metrics_ui()

    async def load_activity_data():
        """Load recent activity data."""
        nonlocal activity_data
        
        try:
            if server_bridge:
                try:
                    activity_data = await server_bridge.get_recent_activity_async()
                except Exception:
                    activity_data = generate_mock_activity()
            else:
                activity_data = generate_mock_activity()
                
            update_activity_ui()
            
        except Exception as e:
            logger.error(f"Failed to load activity: {e}")
            activity_data = []
            update_activity_ui()

    def generate_mock_activity() -> list:
        """Generate mock activity data."""
        now = datetime.now()
        return [
            {
                "timestamp": (now - timedelta(minutes=5)).strftime("%H:%M"),
                "type": "client_connect",
                "message": "Client 192.168.1.105 connected"
            },
            {
                "timestamp": (now - timedelta(minutes=12)).strftime("%H:%M"),
                "type": "file_transfer",
                "message": "File backup_2025_01.zip transferred successfully"
            },
            {
                "timestamp": (now - timedelta(minutes=25)).strftime("%H:%M"),
                "type": "backup_complete",
                "message": "Backup job completed (127 files, 2.4 GB)"
            },
            {
                "timestamp": (now - timedelta(minutes=35)).strftime("%H:%M"),
                "type": "system_check",
                "message": "System health check completed successfully"
            },
            {
                "timestamp": (now - timedelta(minutes=48)).strftime("%H:%M"),
                "type": "client_disconnect",
                "message": "Client 192.168.1.102 disconnected"
            }
        ]

    def update_server_status_ui():
        """Update server status UI elements."""
        running = server_status_data.get("running", False)
        
        if running:
            server_status_text.value = "Running"
            server_status_text.color = ft.Colors.GREEN
            
            port = server_status_data.get("port", "Unknown")
            server_port_text.value = f"Port: {port}"
            
            uptime_seconds = server_status_data.get("uptime_seconds", 0)
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            uptime_text.value = f"Uptime: {hours}h {minutes}m"
            
            start_server_btn.disabled = True
            stop_server_btn.disabled = False
        else:
            server_status_text.value = "Stopped"
            server_status_text.color = ft.Colors.RED
            server_port_text.value = ""
            uptime_text.value = ""
            
            start_server_btn.disabled = False
            stop_server_btn.disabled = True
        
        # Update stats
        clients_count_text.value = str(server_status_data.get("clients_connected", 0))
        files_count_text.value = str(server_status_data.get("total_files", 0))
        transfers_count_text.value = str(server_status_data.get("total_transfers", 0))
        storage_used_text.value = f"{server_status_data.get('storage_used_gb', 0):.1f} GB"
        
        # Update controls
        server_status_text.update()
        server_port_text.update()
        uptime_text.update()
        clients_count_text.update()
        files_count_text.update()
        transfers_count_text.update()
        storage_used_text.update()
        start_server_btn.update()
        stop_server_btn.update()

    def update_system_metrics_ui():
        """Update system metrics UI elements."""
        cpu_percent = system_metrics_data.get("cpu_percent", 0)
        memory_percent = system_metrics_data.get("memory_percent", 0)
        disk_percent = system_metrics_data.get("disk_percent", 0)
        
        cpu_progress.value = cpu_percent / 100
        memory_progress.value = memory_percent / 100
        disk_progress.value = disk_percent / 100
        
        cpu_text.value = f"{cpu_percent:.1f}%"
        memory_text.value = f"{memory_percent:.1f}%"
        disk_text.value = f"{disk_percent:.1f}%"
        
        cpu_progress.update()
        memory_progress.update()
        disk_progress.update()
        cpu_text.update()
        memory_text.update()
        disk_text.update()

    def update_activity_ui():
        """Update activity list UI."""
        activity_list.controls.clear()
        
        for activity in activity_data:
            activity_type = activity.get("type", "unknown")
            
            # Activity type icon
            if activity_type == "client_connect":
                icon = ft.Icons.PERSON_ADD
                color = ft.Colors.GREEN
            elif activity_type == "client_disconnect":
                icon = ft.Icons.PERSON_REMOVE
                color = ft.Colors.ORANGE
            elif activity_type == "file_transfer":
                icon = ft.Icons.FILE_DOWNLOAD
                color = ft.Colors.BLUE
            elif activity_type == "backup_complete":
                icon = ft.Icons.BACKUP
                color = ft.Colors.GREEN
            elif activity_type == "system_check":
                icon = ft.Icons.HEALTH_AND_SAFETY
                color = ft.Colors.PURPLE
            else:
                icon = ft.Icons.INFO
                color = ft.Colors.GREY
            
            activity_tile = ft.ListTile(
                leading=ft.Icon(icon, color=color, size=20),
                title=ft.Text(activity.get("message", ""), size=13),
                subtitle=ft.Text(activity.get("timestamp", ""), size=11, color=ft.Colors.GREY_600),
                content_padding=ft.Padding(8, 4, 8, 4)
            )
            
            activity_list.controls.append(activity_tile)
        
        activity_list.update()

    async def refresh_dashboard():
        """Refresh all dashboard data."""
        nonlocal is_loading, last_updated
        
        if is_loading:
            return
            
        is_loading = True
        
        try:
            # Load all data in parallel for better performance
            await asyncio.gather(
                load_server_status(),
                load_system_metrics(),
                load_activity_data()
            )
            
            last_updated = datetime.now()
            last_updated_text.value = f"Updated: {last_updated.strftime('%H:%M:%S')}"
            last_updated_text.update()
            
            # Update state manager
            if state_manager:
                state_manager.update("dashboard_data", {
                    "server_status": server_status_data,
                    "system_metrics": system_metrics_data,
                    "activity": activity_data
                })
                
        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")
            show_error_message(page, f"Failed to refresh dashboard: {str(e)}")
        finally:
            is_loading = False

    # Server Action Functions
    async def start_server_action():
        """Start server action."""
        try:
            if server_bridge:
                result = await server_bridge.start_server_async()
                if result.get("success", False):
                    show_success_message(page, "Server started successfully")
                else:
                    show_error_message(page, f"Failed to start server: {result.get('message', 'Unknown error')}")
            else:
                show_success_message(page, "Mock server started (demo mode)")
            
            # Refresh dashboard after action
            await refresh_dashboard()
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            show_error_message(page, f"Failed to start server: {str(e)}")

    async def stop_server_action():
        """Stop server action."""
        try:
            if server_bridge:
                result = await server_bridge.stop_server_async()
                if result.get("success", False):
                    show_success_message(page, "Server stopped successfully")
                else:
                    show_error_message(page, f"Failed to stop server: {result.get('message', 'Unknown error')}")
            else:
                show_success_message(page, "Mock server stopped (demo mode)")
            
            # Refresh dashboard after action
            await refresh_dashboard()
            
        except Exception as e:
            logger.error(f"Failed to stop server: {e}")
            show_error_message(page, f"Failed to stop server: {str(e)}")

    # UI Layout Construction
    def create_stat_card(title: str, value_control: ft.Control, icon: str, color: ft.colors) -> ft.Container:
        """Create a statistics card."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=32, color=color),
                    ft.Column([
                        value_control,
                        ft.Text(title, size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD)
                    ], spacing=2, tight=True)
                ], alignment=ft.MainAxisAlignment.START, spacing=12)
            ], spacing=8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            padding=20,
            expand=True
        )

    def create_metric_row(label: str, progress: ft.ProgressBar, text: ft.Text) -> ft.Column:
        """Create a system metric row."""
        return ft.Column([
            ft.Row([
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, width=80),
                progress,
                text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=12)
        ], spacing=4)

    # Header section
    header_row = ft.Row([
        ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh dashboard",
            on_click=lambda e: page.run_task(refresh_dashboard)
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Server status section
    server_status_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SERVER, size=24, color=ft.Colors.BLUE),
                ft.Text("Server Status", size=16, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            ft.Divider(height=1),
            ft.Column([
                server_status_text,
                server_port_text,
                uptime_text
            ], spacing=4),
            ft.Container(height=8),
            ft.Row([start_server_btn, stop_server_btn], spacing=12)
        ], spacing=8),
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=12,
        padding=20
    )
    
    # Statistics cards
    stats_row = ft.ResponsiveRow([
        ft.Column([
            create_stat_card("Active Clients", clients_count_text, ft.Icons.PEOPLE, ft.Colors.BLUE)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_stat_card("Total Files", files_count_text, ft.Icons.FOLDER, ft.Colors.GREEN)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_stat_card("Transfers", transfers_count_text, ft.Icons.SWAP_HORIZ, ft.Colors.ORANGE)
        ], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_stat_card("Storage Used", storage_used_text, ft.Icons.STORAGE, ft.Colors.PURPLE)
        ], col={"sm": 12, "md": 6, "lg": 3})
    ])
    
    # System metrics section
    system_metrics_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.COMPUTER, size=20, color=ft.Colors.BLUE),
                ft.Text("System Metrics", size=16, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            ft.Divider(height=1),
            create_metric_row("CPU", cpu_progress, cpu_text),
            create_metric_row("Memory", memory_progress, memory_text),
            create_metric_row("Disk", disk_progress, disk_text)
        ], spacing=12),
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=12,
        padding=20
    )
    
    # Recent activity section
    activity_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.TIMELINE, size=20, color=ft.Colors.BLUE),
                ft.Text("Recent Activity", size=16, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            ft.Divider(height=1),
            ft.Container(content=activity_list, height=200)
        ], spacing=12),
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=12,
        padding=20,
        expand=True
    )
    
    # Main layout
    main_content = ft.ResponsiveRow([
        ft.Column([server_status_card], col={"sm": 12, "md": 12, "lg": 4}),
        ft.Column([system_metrics_card], col={"sm": 12, "md": 12, "lg": 4}),
        ft.Column([activity_card], col={"sm": 12, "md": 12, "lg": 4})
    ], spacing=20)
    
    footer_row = ft.Row([
        ft.Icon(ft.Icons.UPDATE, size=16, color=ft.Colors.GREY),
        last_updated_text
    ], spacing=8)
    
    main_view = ft.Column([
        header_row,
        ft.Divider(),
        stats_row,
        ft.Container(height=20),  # Spacing
        main_content,
        ft.Container(height=16),  # Spacing
        footer_row
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
    
    # Initialize dashboard
    page.run_task(refresh_dashboard)
    
    return main_view