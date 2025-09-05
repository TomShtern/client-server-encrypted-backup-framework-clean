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
from utils.user_feedback import show_success_message, show_error_message, show_info_message
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
    
    # Essential ft.Ref for controls requiring dynamic styling (KEEP - 5 refs)
    cpu_progress_bar_ref = ft.Ref[ft.ProgressBar]()
    memory_progress_bar_ref = ft.Ref[ft.ProgressBar]()
    disk_progress_bar_ref = ft.Ref[ft.ProgressBar]()
    server_status_text_ref = ft.Ref[ft.Text]()
    server_status_icon_ref = ft.Ref[ft.Icon]()
    
    # Direct control references for simple text updates (OPTIMIZED)
    last_updated_text = ft.Text(f"Last updated: {datetime.now().strftime('%H:%M:%S')}", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    uptime_text = ft.Text("2h 34m", size=18, weight=ft.FontWeight.BOLD)
    active_clients_text = ft.Text("3", size=18, weight=ft.FontWeight.BOLD)
    total_transfers_text = ft.Text("72", size=18, weight=ft.FontWeight.BOLD)
    cpu_usage_text = ft.Text("45.2%", size=18, weight=ft.FontWeight.BOLD)
    memory_usage_text = ft.Text("67.8%", size=18, weight=ft.FontWeight.BOLD)
    disk_usage_text = ft.Text("34.1%", size=18, weight=ft.FontWeight.BOLD)
    
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
            
            # Update server status (KEEP - requires dynamic styling)
            if server_status.get("server_running", False):
                server_status_text_ref.current.value = "Running"
                server_status_text_ref.current.color = ft.Colors.GREEN
                server_status_icon_ref.current.color = ft.Colors.GREEN
            else:
                server_status_text_ref.current.value = "Stopped"
                server_status_text_ref.current.color = ft.Colors.RED
                server_status_icon_ref.current.color = ft.Colors.RED
            
            # Update simple text fields (OPTIMIZED - direct access)
            uptime_text.value = server_status.get("uptime", "0h 0m")
            active_clients_text.value = str(server_status.get("active_clients", 0))
            total_transfers_text.value = str(server_status.get("total_transfers", 0))
            
            # Update system metrics with progress bars (KEEP - requires dynamic styling)
            cpu_value = system_metrics.get('cpu_usage', 0.0)
            cpu_usage_text.value = f"{cpu_value:.1f}%"
            cpu_progress_bar_ref.current.value = cpu_value / 100
            if cpu_value > 80:
                cpu_progress_bar_ref.current.color = ft.Colors.RED
            elif cpu_value > 60:
                cpu_progress_bar_ref.current.color = ft.Colors.ORANGE
            else:
                cpu_progress_bar_ref.current.color = ft.Colors.GREEN
            
            memory_value = system_metrics.get('memory_usage', 0.0)
            memory_usage_text.value = f"{memory_value:.1f}%"
            memory_progress_bar_ref.current.value = memory_value / 100
            if memory_value > 80:
                memory_progress_bar_ref.current.color = ft.Colors.RED
            elif memory_value > 60:
                memory_progress_bar_ref.current.color = ft.Colors.ORANGE
            else:
                memory_progress_bar_ref.current.color = ft.Colors.GREEN
            
            disk_value = system_metrics.get('disk_usage', 0.0)
            disk_usage_text.value = f"{disk_value:.1f}%"
            disk_progress_bar_ref.current.value = disk_value / 100
            if disk_value > 80:
                disk_progress_bar_ref.current.color = ft.Colors.RED
            elif disk_value > 60:
                disk_progress_bar_ref.current.color = ft.Colors.ORANGE
            else:
                disk_progress_bar_ref.current.color = ft.Colors.GREEN
            
            # Update last updated timestamp
            last_updated_text.value = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
            
            # Update only essential refs (5 instead of 12)
            server_status_text_ref.current.update()
            server_status_icon_ref.current.update()
            cpu_progress_bar_ref.current.update()
            memory_progress_bar_ref.current.update()
            disk_progress_bar_ref.current.update()
            
            # Update direct controls (7 controls)
            uptime_text.update()
            active_clients_text.update()
            total_transfers_text.update()
            cpu_usage_text.update()
            memory_usage_text.update()
            disk_usage_text.update()
            last_updated_text.update()
            
        except Exception as e:
            logger.error(f"Failed to update dashboard UI: {e}")
    
    # Quick action handlers
    def on_start_server(e):
        logger.info("Dashboard: Start server clicked")
        show_success_message(page, "Server start command sent")
    
    def on_stop_server(e):
        logger.info("Dashboard: Stop server clicked")
        show_info_message(page, "Server stop command sent")
    
    def on_refresh_dashboard(e):
        logger.info("Dashboard: Refresh clicked")
        
        async def async_refresh():
            try:
                # Simulate async operation
                await asyncio.sleep(ASYNC_DELAY)
                # Update UI with current data
                update_dashboard_ui()
                show_info_message(page, "Dashboard refreshed")
                logger.info("Dashboard data refreshed")
            except Exception as e:
                logger.error(f"Error in refresh handler: {e}")
                show_error_message(page, "Error refreshing dashboard")
        
        # Run async operation
        page.run_task(async_refresh)
    
    def on_backup_now(e):
        logger.info("Dashboard: Backup now clicked")
        show_info_message(page, "Backup job queued")
    
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
                        uptime_text
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
                        active_clients_text
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
                        total_transfers_text
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
                        cpu_usage_text,
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
                        memory_usage_text,
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
                        disk_usage_text,
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
                    ft.Container(
                        content=ft.Text(activity_time.strftime("%H:%M"), size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        width=60,
                        alignment=ft.alignment.center_right
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CIRCLE, size=8, color=activity_color),
                        width=24,
                        alignment=ft.alignment.center
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
    main_view = ft.Column([
        # Header with title and last updated
        ft.Row([
            ft.Icon(ft.Icons.DASHBOARD, size=24),
            ft.Text("Server Dashboard", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            last_updated_text
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
                                content=ft.Column(activity_items, spacing=0, scroll=ft.ScrollMode.AUTO),
                                expand=True,
                                border=ft.border.all(1, ft.Colors.OUTLINE),
                                border_radius=8,
                                bgcolor=ft.Colors.SURFACE,
                                padding=5
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
    
    # Schedule initial data load after controls are added to page
    def schedule_initial_load():
        """Schedule initial data load with retry mechanism."""
        async def delayed_load():
            # Wait a bit for controls to be attached
            await asyncio.sleep(0.1)
            # Check if controls are attached before proceeding
            if (cpu_progress_bar_ref.current and 
                hasattr(cpu_progress_bar_ref.current, 'page') and 
                cpu_progress_bar_ref.current.page is not None):
                update_dashboard_ui()
            else:
                # Retry once more after a longer delay
                await asyncio.sleep(0.2)
                if (cpu_progress_bar_ref.current and 
                    hasattr(cpu_progress_bar_ref.current, 'page') and 
                    cpu_progress_bar_ref.current.page is not None):
                    update_dashboard_ui()
                else:
                    logger.warning("Controls still not attached, skipping initial load")
        page.run_task(delayed_load)
    
    # Also provide a trigger for manual loading if needed
    def trigger_initial_load():
        """Trigger initial data load manually."""
        update_dashboard_ui()
    
    # Schedule the initial load
    schedule_initial_load()
    
    # Wrap the dashboard view in a container to properly attach the trigger function
    dashboard_container = ft.Container(
        content=main_view,
        expand=True
    )
    
    # Export the trigger function so it can be called externally
    dashboard_container.trigger_initial_load = trigger_initial_load
    
    return dashboard_container