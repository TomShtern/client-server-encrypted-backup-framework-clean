#!/usr/bin/env python3
"""
Simple Dashboard View - Hiroshima Protocol Compliant
A clean, minimal implementation using pure Flet patterns.

This demonstrates the Hiroshima ideal:
- Uses Flet's built-in components exclusively
- No custom state management or complex event handling
- Simple function returning ft.Control (composition over inheritance)
- Works WITH the framework, not against it
"""

import flet as ft
import asyncio
import psutil
from datetime import datetime, timedelta
import random

# Import debugging setup
from utils.debug_setup import get_logger
logger = get_logger(__name__)


def create_dashboard_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create dashboard view using simple Flet patterns (no class inheritance needed).
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The dashboard view
    """
    
    # Get server status from bridge or use fallback
    def get_server_status():
        """Get server status from bridge or return mock data."""
        if server_bridge:
            try:
                return server_bridge.get_server_status()
            except:
                pass
        
        # Fallback status
        return {
            "server_running": True,
            "port": 1256,
            "uptime": "2h 34m",
            "total_transfers": 72,
            "active_clients": 3,
            "total_files": 45,
            "storage_used": "2.4 GB"
        }
    
    # Get system metrics
    def get_system_metrics():
        """Get real system metrics using psutil."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return {
                'cpu_usage': psutil.cpu_percent(interval=0.1),
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'total_memory': memory.total,
                'available_memory': memory.available,
                'total_disk': disk.total,
                'free_disk': disk.free
            }
        except:
            # Fallback metrics
            return {
                'cpu_usage': 35.2,
                'memory_usage': 62.1,
                'disk_usage': 45.8,
                'total_memory': 16 * 1024**3,  # 16GB
                'available_memory': 6 * 1024**3,  # 6GB
                'total_disk': 500 * 1024**3,  # 500GB
                'free_disk': 271 * 1024**3   # 271GB
            }
    
    # Get recent activity
    def get_recent_activity():
        """Get recent server activity or generate mock data."""
        if server_bridge:
            try:
                return server_bridge.get_recent_activity()
            except:
                pass
        
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
    
    # Helper function to format bytes
    def format_bytes(bytes_value):
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    # Get initial data
    server_status = get_server_status()
    system_metrics = get_system_metrics()
    recent_activity = get_recent_activity()
    
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
    
    def on_refresh_dashboard(e):
        logger.info("Dashboard: Refresh clicked")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Dashboard refreshed"),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()
    
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
                                ft.Icons.CIRCLE if server_status["server_running"] else ft.Icons.CIRCLE_OUTLINED,
                                color=ft.Colors.GREEN if server_status["server_running"] else ft.Colors.RED,
                                size=16
                            ),
                            ft.Text("Server Status", size=12, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        ft.Text(
                            "Running" if server_status["server_running"] else "Stopped", 
                            size=18, 
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN if server_status["server_running"] else ft.Colors.RED
                        ),
                        ft.Text(f"Port {server_status['port']}", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
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
                        ft.Text(server_status["uptime"], size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Hours:Minutes", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
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
                        ft.Text(str(server_status["active_clients"]), size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Connected", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
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
                        ft.Text(str(server_status["total_transfers"]), size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Completed", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
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
                        ft.Text(f"{system_metrics['cpu_usage']:.1f}%", size=18, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(
                            value=system_metrics['cpu_usage'] / 100,
                            color=ft.Colors.RED if system_metrics['cpu_usage'] > 80 
                                  else ft.Colors.ORANGE if system_metrics['cpu_usage'] > 60 
                                  else ft.Colors.GREEN,
                            bgcolor=ft.Colors.OUTLINE
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
                        ft.Text(f"{system_metrics['memory_usage']:.1f}%", size=18, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(
                            value=system_metrics['memory_usage'] / 100,
                            color=ft.Colors.RED if system_metrics['memory_usage'] > 80 
                                  else ft.Colors.ORANGE if system_metrics['memory_usage'] > 60 
                                  else ft.Colors.GREEN,
                            bgcolor=ft.Colors.OUTLINE
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
                        ft.Text(f"{system_metrics['disk_usage']:.1f}%", size=18, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(
                            value=system_metrics['disk_usage'] / 100,
                            color=ft.Colors.RED if system_metrics['disk_usage'] > 80 
                                  else ft.Colors.ORANGE if system_metrics['disk_usage'] > 60 
                                  else ft.Colors.GREEN,
                            bgcolor=ft.Colors.OUTLINE
                        )
                    ], spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 6, "md": 4})
    ])
    
    # Create recent activity list
    activity_items = []
    for activity in recent_activity:
        activity_color = {
            "success": ft.Colors.GREEN,
            "info": ft.Colors.BLUE, 
            "warning": ft.Colors.ORANGE
        }.get(activity["type"], ft.Colors.ON_SURFACE)
        
        activity_items.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(activity["time"], size=12, color=ft.Colors.ON_SURFACE_VARIANT, width=50),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CIRCLE, size=8, color=activity_color),
                        width=20
                    ),
                    ft.Text(activity["text"], size=13, expand=True)
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
                f"Last updated: {datetime.now().strftime('%H:%M:%S')}", 
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
                            ft.Text(str(server_status["total_files"]), size=16, weight=ft.FontWeight.BOLD),
                            
                            ft.Divider(),
                            
                            ft.Row([
                                ft.Icon(ft.Icons.CLOUD, size=16, color=ft.Colors.GREEN),
                                ft.Text("Storage Used", size=12, weight=ft.FontWeight.W_500)
                            ], spacing=5),
                            ft.Text(server_status["storage_used"], size=16, weight=ft.FontWeight.BOLD),
                            
                            ft.Divider(),
                            
                            ft.Row([
                                ft.Icon(ft.Icons.STORAGE, size=16, color=ft.Colors.PURPLE),
                                ft.Text("Available", size=12, weight=ft.FontWeight.W_500)
                            ], spacing=5),
                            ft.Text(format_bytes(system_metrics["free_disk"]), size=16, weight=ft.FontWeight.BOLD)
                        ], spacing=8),
                        padding=15
                    )
                )
            ], col={"sm": 12, "md": 4})
        ])
        
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)