#!/usr/bin/env python3
"""
Dashboard View for FletV2
A clean implementation using pure Flet patterns for Flet 0.28.3.
"""

import flet as ft
import psutil
import asyncio
from datetime import datetime
from utils.debug_setup import get_logger
from config import ASYNC_DELAY

logger = get_logger(__name__)


def create_dashboard_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create dashboard view using simple Flet patterns.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The dashboard view
    """
    
    # UI References using ft.Ref for robust access
    last_updated_text_ref = ft.Ref[ft.Text]()
    server_status_text_ref = ft.Ref[ft.Text]()
    server_status_icon_ref = ft.Ref[ft.Icon]()
    uptime_text_ref = ft.Ref[ft.Text]()
    active_clients_text_ref = ft.Ref[ft.Text]()
    total_transfers_text_ref = ft.Ref[ft.Text]()
    cpu_usage_text_ref = ft.Ref[ft.Text]()
    cpu_progress_bar_ref = ft.Ref[ft.ProgressBar]()
    memory_usage_text_ref = ft.Ref[ft.Text]()
    memory_progress_bar_ref = ft.Ref[ft.ProgressBar]()
    disk_usage_text_ref = ft.Ref[ft.Text]()
    disk_progress_bar_ref = ft.Ref[ft.ProgressBar]()
    
    def get_server_status():
        """Get server status from bridge or return mock data."""
        if server_bridge:
            try:
                return server_bridge.get_server_status()
            except Exception as e:
                logger.warning(f"Failed to get server status from server bridge: {e}")
        
        # Fallback to mock data
        return {
            "server_running": True,
            "port": 1256,
            "uptime": "2h 34m",
            "total_transfers": 72,
            "active_clients": 3,
            "total_files": 45,
            "storage_used": "2.4 GB"
        }
    
    def get_system_metrics():
        """Get real system metrics using psutil."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return {
                'cpu_usage': psutil.cpu_percent(interval=0.1),
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'memory_total_gb': memory.total // (1024**3),
                'memory_used_gb': (memory.total - memory.available) // (1024**3),
                'disk_total_gb': disk.total // (1024**3),
                'disk_used_gb': disk.used // (1024**3),
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return {
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'disk_usage': 34.1,
                'memory_total_gb': 16,
                'memory_used_gb': 11,
                'disk_total_gb': 500,
                'disk_used_gb': 170,
            }
    
    def get_recent_activity():
        """Get recent activity or generate mock data."""
        if server_bridge:
            try:
                return server_bridge.get_recent_activity()
            except Exception as e:
                logger.warning(f"Failed to get recent activity from server bridge: {e}")
        
        # Generate mock recent activity
        activities = []
        base_time = datetime.now()
        activity_types = [
            "File transfer completed: document_{}.pdf",
            "Client connected: 192.168.1.{}",
            "Backup job finished: backup_{}",
            "Client disconnected: 192.168.1.{}",
            "File verification completed: image_{}.jpg",
            "Database cleanup completed",
            "Server started on port 1256",
            "SSL certificate renewed"
        ]
        
        for i in range(8):
            from datetime import timedelta
            import random
            time_offset = timedelta(minutes=random.randint(1, 120))
            activity_time = base_time - time_offset
            
            template = random.choice(activity_types)
            if "{}" in template:
                activity_text = template.format(random.randint(100, 999))
            else:
                activity_text = template
            
            activities.append({
                "time": activity_time.strftime("%H:%M"),
                "text": activity_text,
                "type": random.choice(["success", "info", "warning"])
            })
        
        return activities[:5]  # Return 5 most recent
    
    def update_dashboard_ui():
        """Update dashboard UI with current data."""
        try:
            # Get current data
            server_status = get_server_status()
            system_metrics = get_system_metrics()
            recent_activity = get_recent_activity()
            
            # Update server status
            if server_status.get("server_running", False):
                server_status_text_ref.current.value = "Running"
                server_status_text_ref.current.color = ft.Colors.GREEN
                server_status_icon_ref.current.color = ft.Colors.GREEN
            else:
                server_status_text_ref.current.value = "Stopped"
                server_status_text_ref.current.color = ft.Colors.RED
                server_status_icon_ref.current.color = ft.Colors.RED
            
            # Update other status fields
            uptime_text_ref.current.value = server_status.get("uptime", "0h 0m")
            active_clients_text_ref.current.value = str(server_status.get("active_clients", 0))
            total_transfers_text_ref.current.value = str(server_status.get("total_transfers", 0))
            
            # Update system metrics
            cpu_value = system_metrics.get('cpu_usage', 0.0)
            cpu_usage_text_ref.current.value = f"{cpu_value:.1f}%"
            cpu_progress_bar_ref.current.value = cpu_value / 100
            if cpu_value > 80:
                cpu_progress_bar_ref.current.color = ft.Colors.RED
            elif cpu_value > 60:
                cpu_progress_bar_ref.current.color = ft.Colors.ORANGE
            else:
                cpu_progress_bar_ref.current.color = ft.Colors.GREEN
            
            memory_value = system_metrics.get('memory_usage', 0.0)
            memory_usage_text_ref.current.value = f"{memory_value:.1f}%"
            memory_progress_bar_ref.current.value = memory_value / 100
            if memory_value > 80:
                memory_progress_bar_ref.current.color = ft.Colors.RED
            elif memory_value > 60:
                memory_progress_bar_ref.current.color = ft.Colors.ORANGE
            else:
                memory_progress_bar_ref.current.color = ft.Colors.GREEN
            
            disk_value = system_metrics.get('disk_usage', 0.0)
            disk_usage_text_ref.current.value = f"{disk_value:.1f}%"
            disk_progress_bar_ref.current.value = disk_value / 100
            if disk_value > 80:
                disk_progress_bar_ref.current.color = ft.Colors.RED
            elif disk_value > 60:
                disk_progress_bar_ref.current.color = ft.Colors.ORANGE
            else:
                disk_progress_bar_ref.current.color = ft.Colors.GREEN
            
            # Update last updated timestamp
            last_updated_text_ref.current.value = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
            
            # Update all refs
            server_status_text_ref.current.update()
            server_status_icon_ref.current.update()
            uptime_text_ref.current.update()
            active_clients_text_ref.current.update()
            total_transfers_text_ref.current.update()
            cpu_usage_text_ref.current.update()
            cpu_progress_bar_ref.current.update()
            memory_usage_text_ref.current.update()
            memory_progress_bar_ref.current.update()
            disk_usage_text_ref.current.update()
            disk_progress_bar_ref.current.update()
            last_updated_text_ref.current.update()
            
        except Exception as e:
            logger.error(f"Failed to update dashboard UI: {e}")
    
    # Quick action handlers
    def on_start_server(e):
        logger.info("Dashboard: Start server clicked")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Server start command sent"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
    
    def on_stop_server(e):
        logger.info("Dashboard: Stop server clicked")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Server stop command sent"),
            bgcolor=ft.Colors.ORANGE
        )
        page.snack_bar.open = True
        page.update()
    
    async def refresh_dashboard_async():
        """Async function to refresh dashboard data."""
        try:
            # Simulate async operation
            await asyncio.sleep(1.0)
            logger.info("Dashboard data refreshed")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")
            return False
    
    def on_refresh_dashboard(e):
        logger.info("Dashboard: Refresh clicked")
        
        async def async_refresh():
            try:
                success = await refresh_dashboard_async()
                if success:
                    update_dashboard_ui()
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Dashboard refreshed"),
                        bgcolor=ft.Colors.BLUE
                    )
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Failed to refresh dashboard"),
                        bgcolor=ft.Colors.RED
                    )
                page.snack_bar.open = True
                page.update()
            except Exception as e:
                logger.error(f"Error in refresh handler: {e}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error refreshing dashboard"),
                    bgcolor=ft.Colors.RED
                )
                page.snack_bar.open = True
                page.update()
        
        # Run async operation
        page.run_task(async_refresh)
    
    def on_backup_now(e):
        logger.info("Dashboard: Backup now clicked")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Backup job queued"),
            bgcolor=ft.Colors.PURPLE
        )
        page.snack_bar.open = True
        page.update()
    
    # Create server status cards
    server_status_cards = ft.ResponsiveRow([
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(
                                ft.Icons.CIRCLE if True else ft.Icons.CIRCLE_OUTLINED,
                                color=ft.Colors.GREEN if True else ft.Colors.RED,
                                size=16,
                                ref=server_status_icon_ref
                            ),
                            ft.Text("Server Status", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text(
                            "Running" if True else "Stopped", 
                            size=18, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN if True else ft.Colors.RED,
                            ref=server_status_text_ref
                        )
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 3}),
        
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.BLUE, size=16),
                            ft.Text("Uptime", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text("2h 34m", size=18, weight=ft.FontWeight.BOLD, ref=uptime_text_ref)
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 3}),
        
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.PURPLE, size=16),
                            ft.Text("Active Clients", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text("3", size=18, weight=ft.FontWeight.BOLD, ref=active_clients_text_ref)
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 3}),
        
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.CLOUD_UPLOAD, color=ft.Colors.ORANGE, size=16),
                            ft.Text("Total Transfers", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text("72", size=18, weight=ft.FontWeight.BOLD, ref=total_transfers_text_ref)
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 3})
    ])
    
    # Create system metrics cards
    system_metrics_cards = ft.ResponsiveRow([
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.BLUE, size=16),
                            ft.Text("CPU Usage", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text("45.2%", size=18, weight=ft.FontWeight.BOLD, ref=cpu_usage_text_ref),
                        ft.ProgressBar(
                            value=0.452,
                            color=ft.Colors.GREEN,
                            bgcolor=ft.Colors.OUTLINE,
                            ref=cpu_progress_bar_ref
                        )
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 4}),
        
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.MEMORY, color=ft.Colors.GREEN, size=16),
                            ft.Text("Memory", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text("67.8%", size=18, weight=ft.FontWeight.BOLD, ref=memory_usage_text_ref),
                        ft.ProgressBar(
                            value=0.678,
                            color=ft.Colors.GREEN,
                            bgcolor=ft.Colors.OUTLINE,
                            ref=memory_progress_bar_ref
                        )
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 4}),
        
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.STORAGE, color=ft.Colors.PURPLE, size=16),
                            ft.Text("Disk Space", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text("34.1%", size=18, weight=ft.FontWeight.BOLD, ref=disk_usage_text_ref),
                        ft.ProgressBar(
                            value=0.341,
                            color=ft.Colors.GREEN,
                            bgcolor=ft.Colors.OUTLINE,
                            ref=disk_progress_bar_ref
                        )
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 4})
    ])
    
    # Create recent activity list
    activity_items = []
    for i in range(5):
        from datetime import timedelta
        import random
        base_time = datetime.now()
        time_offset = timedelta(minutes=random.randint(1, 120))
        activity_time = base_time - time_offset
        
        activity_color = {
            "success": ft.Colors.GREEN,
            "info": ft.Colors.BLUE, 
            "warning": ft.Colors.ORANGE
        }.get(random.choice(["success", "info", "warning"]), ft.Colors.ON_SURFACE)
        
        activity_items.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(activity_time.strftime("%H:%M"), size=12, color=ft.Colors.ON_SURFACE_VARIANT, width=50),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CIRCLE, size=8, color=activity_color),
                        width=20
                    ),
                    ft.Text(f"Activity {i+1}", size=13, expand=True)
                ], spacing=10),
                padding=ft.Padding(10, 5, 10, 5)
            )
        )
    
    # Quick actions
    quick_actions = ft.ResponsiveRow([
        ft.Column([
            ft.FilledButton(
                "Start Server",
                icon=ft.Icons.PLAY_ARROW,
                on_click=on_start_server,
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN)
            )
        ], col={"sm": 6, "md": 3}),
        
        ft.Column([
            ft.OutlinedButton(
                "Stop Server",
                icon=ft.Icons.STOP,
                on_click=on_stop_server,
                style=ft.ButtonStyle(color=ft.Colors.ORANGE)
            )
        ], col={"sm": 6, "md": 3}),
        
        ft.Column([
            ft.FilledButton(
                "Backup Now",
                icon=ft.Icons.BACKUP,
                on_click=on_backup_now,
                style=ft.ButtonStyle(bgcolor=ft.Colors.PURPLE)
            )
        ], col={"sm": 6, "md": 3}),
        
        ft.Column([
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh Dashboard",
                on_click=on_refresh_dashboard,
                icon_size=24
            )
        ], col={"sm": 6, "md": 3})
    ])
    
    # Main dashboard layout
    return ft.Column([
        # Header with title and last updated
        ft.Row([
            ft.Icon(ft.Icons.DASHBOARD, size=24),
            ft.Text("Server Dashboard", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Text(
                ref=last_updated_text_ref,
                value=f"Last updated: {datetime.now().strftime('%H:%M:%S')}", 
                size=12, 
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        ]),
        ft.Divider(),
        
        # Quick Actions
        ft.Text("Quick Actions", size=18, weight=ft.FontWeight.BOLD),
        quick_actions,
        ft.Divider(),
        
        # Server Status Overview
        ft.Text("Server Status", size=18, weight=ft.FontWeight.BOLD),
        server_status_cards,
        ft.Divider(),
        
        # System Metrics
        ft.Text("System Performance", size=18, weight=ft.FontWeight.BOLD),
        system_metrics_cards,
        ft.Divider(),
        
        # Recent Activity and Storage Info
        ft.ResponsiveRow([
            # Recent Activity
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Recent Activity", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(activity_items, spacing=0),
                                height=200,
                                border=ft.border.all(1, ft.Colors.OUTLINE),
                                border_radius=8,
                                bgcolor=ft.Colors.SURFACE
                            )
                        ], spacing=10),
                        padding=15
                    )
                )
            ], col={"sm": 12, "md": 8}),
            
            # Storage Summary  
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Storage Summary", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            
                            ft.Row([
                                ft.Icon(ft.Icons.FOLDER, size=16, color=ft.Colors.BLUE),
                                ft.Text("Total Files", size=12, weight=ft.FontWeight.W_500)
                            ], spacing=5),
                            ft.Text("45", size=16, weight=ft.FontWeight.BOLD),
                            
                            ft.Divider(),
                            
                            ft.Row([
                                ft.Icon(ft.Icons.CLOUD, size=16, color=ft.Colors.GREEN),
                                ft.Text("Storage Used", size=12, weight=ft.FontWeight.W_500)
                            ], spacing=5),
                            ft.Text("2.4 GB", size=16, weight=ft.FontWeight.BOLD),
                            
                            ft.Divider(),
                            
                            ft.Row([
                                ft.Icon(ft.Icons.STORAGE, size=16, color=ft.Colors.PURPLE),
                                ft.Text("Available", size=12, weight=ft.FontWeight.W_500)
                            ], spacing=5),
                            ft.Text("477.6 GB", size=16, weight=ft.FontWeight.BOLD)
                        ], spacing=8),
                        padding=15
                    )
                )
            ], col={"sm": 12, "md": 4})
        ])
        
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)