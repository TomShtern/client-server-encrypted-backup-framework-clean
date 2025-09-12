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
from utils.dialog_consolidation_helper import show_success_message, show_error_message
from utils.server_mediated_operations import create_server_mediated_operations, timestamp_processor

logger = get_logger(__name__)

def create_dashboard_view(
    server_bridge: Optional[ServerBridge], 
    page: ft.Page, 
    state_manager: StateManager
) -> ft.Control:
    """
    Create dashboard view with clean, maintainable implementation.
    Follows successful patterns from clients.py and analytics.py.
    """
    logger.info("Creating dashboard view")
    
    # Initialize modular server-mediated operations utility
    server_ops = create_server_mediated_operations(state_manager, page)
    
    # --- State Management - Now handled by state_manager ---
    activity_filter = "All"
    
    # State variables for dashboard data
    system_metrics_data = {}
    server_status_data = {}
    activity_data = []
    is_loading = False
    last_updated = None
    
    # --- UI Control References ---
    server_status_text = ft.Text("Unknown", size=14, weight=ft.FontWeight.BOLD)
    server_port_text = ft.Text("", size=12, color=ft.Colors.GREY_600)
    uptime_text = ft.Text("", size=12, color=ft.Colors.GREY_600)
    clients_count_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    files_count_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    transfers_count_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    storage_used_text = ft.Text("0 GB", size=28, weight=ft.FontWeight.BOLD)
    
    cpu_progress = ft.ProgressBar(value=0.0, width=150)
    memory_progress = ft.ProgressBar(value=0.0, width=150)
    disk_progress = ft.ProgressBar(value=0.0, width=150)
    cpu_text = ft.Text("0%", size=12)
    memory_text = ft.Text("0.0 / 0.0 GB (0.0%)", size=11, font_family="monospace")
    disk_text = ft.Text("0.0 / 0.0 GB (0.0%)", size=11, font_family="monospace")
    
    activity_list = ft.ListView(expand=True, spacing=8, padding=ft.padding.only(top=8))
    last_updated_text = ft.Text("Never", size=12, color=ft.Colors.GREY_600)
    
    start_server_btn = ft.ElevatedButton("Start Server", icon=ft.Icons.PLAY_ARROW, on_click=lambda e: page.run_task(start_server_action), style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE))
    stop_server_btn = ft.ElevatedButton("Stop Server", icon=ft.Icons.STOP, on_click=lambda e: page.run_task(stop_server_action), style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color=ft.Colors.WHITE), disabled=True)

    # --- Helper Functions ---
    def format_time_ago(dt_obj: datetime) -> str:
        if not dt_obj:
            return ""
        diff = datetime.now() - dt_obj
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        minutes = seconds / 60
        if minutes < 60:
            return f"{int(minutes)}m ago"
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)}h ago"
        days = hours / 24
        return f"{int(days)}d ago"

    # --- Modular Server-Mediated Data Functions ---
    async def load_server_status():
        """Load server status using modular operations utility"""
        return await server_ops.load_data_operation(
            state_key="server_status",
            server_operation="get_server_status_async",
            fallback_data=generate_mock_server_status()
        )

    def generate_mock_server_status() -> Dict[str, Any]:
        return {"running": True, "port": 8080, "uptime_seconds": 3600 * 12 + 1800, "clients_connected": 3, "total_files": 127, "total_transfers": 45, "storage_used_gb": 2.4}

    async def load_system_metrics():
        """Load system metrics using psutil"""
        nonlocal system_metrics_data
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            system_metrics_data = {
                "cpu_percent": cpu_percent, "memory_percent": memory.percent, "disk_percent": disk.percent,
                "memory_used_gb": memory.used / (1024**3), "memory_total_gb": memory.total / (1024**3),
                "disk_used_gb": disk.used / (1024**3), "disk_total_gb": disk.total / (1024**3),
            }
        except Exception as e:
            logger.error(f"Failed to load system metrics: {e}")
            system_metrics_data = {
                "cpu_percent": 25.0, "memory_percent": 68.0, "disk_percent": 45.0,
                "memory_used_gb": 10.9, "memory_total_gb": 16.0,
                "disk_used_gb": 230.4, "disk_total_gb": 512.0,
            }
        finally:
            update_system_metrics_ui()
        
        # Return the data for use in refresh_dashboard
        return system_metrics_data

    async def load_activity_data():
        """Load activity data using modular operations utility"""
        return await server_ops.load_data_operation(
            state_key="recent_activity",
            server_operation="get_recent_activity_async",
            fallback_data=generate_mock_activity(),
            data_processor=timestamp_processor
        )

    def generate_mock_activity() -> list:
        now = datetime.now()
        return [
            {"timestamp": now - timedelta(minutes=5), "type": "client_connect", "message": "Client 192.168.1.105 connected"},
            {"timestamp": now - timedelta(minutes=12), "type": "file_transfer", "message": "File backup_2025_01.zip transferred"},
            {"timestamp": now - timedelta(minutes=25), "type": "backup_complete", "message": "Backup job completed (127 files)"},
            {"timestamp": now - timedelta(hours=1, minutes=15), "type": "system_check", "message": "System health check passed"},
            {"timestamp": now - timedelta(hours=2, minutes=48), "type": "client_disconnect", "message": "Client 192.168.1.102 disconnected"},
            {"timestamp": now - timedelta(days=1, hours=3), "type": "error", "message": "Failed to connect to update server"},
        ]

    # --- Reactive UI Update Functions ---
    def update_server_status_ui(data, _):
        """Reactive callback for server status changes"""
        nonlocal server_status_data
        server_status_data = data or {}
        
        if not server_status_data:
            return
            
        running = server_status_data.get("running", False)
        if running:
            server_status_text.value, server_status_text.color = "Running", ft.Colors.GREEN
            server_port_text.value = f"Port: {server_status_data.get('port', 'N/A')}"
            uptime_seconds = server_status_data.get("uptime_seconds", 0)
            hours, minutes = uptime_seconds // 3600, (uptime_seconds % 3600) // 60
            uptime_text.value = f"Uptime: {hours}h {minutes}m"
            start_server_btn.disabled, stop_server_btn.disabled = True, False
        else:
            server_status_text.value, server_status_text.color = "Stopped", ft.Colors.RED
            server_port_text.value, uptime_text.value = "", ""
            start_server_btn.disabled, stop_server_btn.disabled = False, True
        
        clients_count_text.value = str(server_status_data.get("clients_connected", 0))
        files_count_text.value = str(server_status_data.get("total_files", 0))
        transfers_count_text.value = str(server_status_data.get("total_transfers", 0))
        storage_used_text.value = f"{server_status_data.get('storage_used_gb', 0):.1f} GB"
        
        # Use individual control updates for better performance
        for control in [server_status_text, server_port_text, uptime_text, start_server_btn, 
                       stop_server_btn, clients_count_text, files_count_text, transfers_count_text, storage_used_text]:
            control.update()

    def update_system_metrics_ui():
        cpu_percent = system_metrics_data.get("cpu_percent", 0)
        mem_percent = system_metrics_data.get("memory_percent", 0)
        disk_percent = system_metrics_data.get("disk_percent", 0)
        
        cpu_progress.value, memory_progress.value, disk_progress.value = cpu_percent / 100, mem_percent / 100, disk_percent / 100
        cpu_text.value = f"{cpu_percent:.1f}%"
        mem_used, mem_total = system_metrics_data.get("memory_used_gb", 0), system_metrics_data.get("memory_total_gb", 0)
        memory_text.value = f"{mem_used:.1f}/{mem_total:.1f} GB ({mem_percent:.1f}%)"
        disk_used, disk_total = system_metrics_data.get("disk_used_gb", 0), system_metrics_data.get("disk_total_gb", 0)
        disk_text.value = f"{disk_used:.1f}/{disk_total:.1f} GB ({disk_percent:.1f}%)"
        page.update(cpu_progress, memory_progress, disk_progress, cpu_text, memory_text, disk_text)

    def update_activity_ui():
        nonlocal activity_data
        activity_list.controls.clear()
        
        filtered_activities = activity_data
        if activity_filter != "All":
            filter_map = {"Clients": ["client_connect", "client_disconnect"], "Files": ["file_transfer", "backup_complete"], "System": ["system_check", "error"]}
            types_to_show = filter_map.get(activity_filter, [])
            filtered_activities = [a for a in activity_data if a.get("type") in types_to_show]

        if not filtered_activities:
            activity_list.controls.append(ft.Text("No activities for this filter.", text_align=ft.TextAlign.CENTER, color=ft.Colors.GREY_500, italic=True))
        
        for activity in sorted(filtered_activities, key=lambda x: x.get("timestamp"), reverse=True):
            act_type = activity.get("type", "unknown")
            icon, color, bgcolor = ft.Icons.INFO, ft.Colors.GREY, ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE)

            if act_type == "client_connect": icon, color = ft.Icons.PERSON_ADD, ft.Colors.GREEN
            elif act_type == "client_disconnect": icon, color = ft.Icons.PERSON_REMOVE, ft.Colors.ORANGE
            elif act_type == "file_transfer": icon, color = ft.Icons.FILE_DOWNLOAD, ft.Colors.BLUE
            elif act_type == "backup_complete": icon, color, bgcolor = ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_800, ft.Colors.with_opacity(0.08, ft.Colors.GREEN)
            elif act_type == "system_check": icon, color = ft.Icons.HEALTH_AND_SAFETY, ft.Colors.PURPLE
            elif act_type == "error": icon, color, bgcolor = ft.Icons.ERROR_OUTLINE, ft.Colors.RED_700, ft.Colors.with_opacity(0.08, ft.Colors.RED)
            
            activity_list.controls.append(ft.ListTile(
                leading=ft.Icon(icon, color=color, size=20),
                title=ft.Text(activity.get("message", ""), size=13),
                subtitle=ft.Text(format_time_ago(activity.get("timestamp")), size=11, color=ft.Colors.GREY_600),
                content_padding=ft.padding.symmetric(horizontal=16, vertical=4),
                bgcolor=bgcolor, border_radius=8
            ))
        activity_list.update()

    # --- Main Refresh & Actions ---
    async def refresh_dashboard():
        nonlocal is_loading, last_updated, server_status_data, system_metrics_data, activity_data
        if is_loading: return
        is_loading = True
        try:
            # Load all data concurrently
            server_status_result, _, activity_result = await asyncio.gather(
                load_server_status(), 
                load_system_metrics(), 
                load_activity_data()
            )
            
            # Update our data variables with the results
            server_status_data = server_status_result or {}
            activity_data = activity_result or []
            
            last_updated = datetime.now()
            last_updated_text.value = f"Updated: {last_updated.strftime('%H:%M:%S')}"
            last_updated_text.update()
            if state_manager:
                state_manager.update("dashboard_data", {"server_status": server_status_data, "system_metrics": system_metrics_data, "activity": activity_data})
        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")
            show_error_message(page, f"Failed to refresh dashboard: {str(e)}")
        finally:
            is_loading = False

    async def start_server_action():
        """Start server using modular action operation"""
        result = await server_ops.action_operation(
            action_name="start_server",
            server_operation="start_server_async",
            operation_data={"action": "start"},
            success_message="Server started successfully",
            error_message="Failed to start server",
            refresh_keys=["server_status", "recent_activity"]
        )
        return result

    async def stop_server_action():
        """Stop server using modular action operation"""
        result = await server_ops.action_operation(
            action_name="stop_server",
            server_operation="stop_server_async",
            operation_data={"action": "stop"},
            success_message="Server stopped successfully",
            error_message="Failed to stop server",
            refresh_keys=["server_status", "recent_activity"]
        )
        return result

    # --- UI Layout Construction ---
    def create_stat_card(title: str, value_control: ft.Control, icon: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([ft.Row([
                ft.Container(content=ft.Icon(icon, size=32, color=color), bgcolor=ft.colors.with_opacity(0.1, color), border_radius=50, padding=8),
                ft.Column([value_control, ft.Text(title, size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD)], spacing=2, tight=True)
            ], alignment=ft.MainAxisAlignment.START, spacing=16)], spacing=8),
            bgcolor=ft.Colors.SURFACE, border=ft.border.all(1, ft.colors.with_opacity(0.12, ft.Colors.ON_SURFACE)),
            border_radius=16, padding=24, expand=True, shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, offset=ft.Offset(0, 2), color=ft.colors.with_opacity(0.1, ft.Colors.BLACK)),
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT), animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_hover=lambda e: animate_card_hover(e.control, e.data == "true")
        )

    def animate_card_hover(card: ft.Container, is_hovering: bool):
        card.scale = 1.02 if is_hovering else 1.0
        card.shadow.blur_radius = 16 if is_hovering else 8
        card.shadow.spread_radius = 2 if is_hovering else 0
        card.update()

    def create_metric_row(label: str, progress: ft.ProgressBar, text: ft.Text) -> ft.Column:
        text.text_align = ft.TextAlign.RIGHT
        return ft.Column([ft.Row([
            ft.Text(label, size=14, weight=ft.FontWeight.W_500, width=60),
            progress,
            ft.Container(content=text, expand=True),
        ], alignment=ft.MainAxisAlignment.START, spacing=12)], spacing=4)

    filter_buttons = {}
    def on_filter_click(e):
        nonlocal activity_filter
        selected_filter = e.control.data
        if activity_filter == selected_filter: return
        activity_filter = selected_filter
        for text, button in filter_buttons.items():
            is_selected = text == activity_filter
            button.selected = is_selected
        page.update(*filter_buttons.values())
        update_activity_ui()

    def create_filter_button(text: str) -> ft.Chip:
        chip = ft.Chip(
            label=ft.Text(text), data=text, selected=text == activity_filter,
            on_select=on_filter_click, show_checkmark=False,
            selected_color=ft.colors.PRIMARY,
        )
        filter_buttons[text] = chip
        return chip

    header_row = ft.Row([
        ft.Row([ft.Icon(ft.Icons.DASHBOARD, size=28, color=ft.Colors.PRIMARY), ft.Text("Server Dashboard", size=24, weight=ft.FontWeight.BOLD)], spacing=12),
        ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Refresh Dashboard", icon_size=24, icon_color=ft.Colors.PRIMARY, on_click=lambda e: page.run_task(refresh_dashboard), style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: ft.colors.with_opacity(0.1, ft.Colors.PRIMARY), ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT}, shape=ft.CircleBorder(), padding=12))
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    server_status_card = ft.Container(content=ft.Column([
        ft.Row([ft.Icon(ft.Icons.DNS, size=24, color=ft.Colors.BLUE), ft.Text("Server Control", size=16, weight=ft.FontWeight.BOLD)], spacing=8),
        ft.Divider(height=1), ft.Column([server_status_text, server_port_text, uptime_text], spacing=4), ft.Container(height=8),
        ft.Row([start_server_btn, stop_server_btn], spacing=12)
    ], spacing=8), bgcolor=ft.Colors.SURFACE, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=12, padding=20)
    
    stats_row = ft.ResponsiveRow([
        ft.Column([create_stat_card("Active Clients", clients_count_text, ft.Icons.PEOPLE, ft.Colors.BLUE)], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([create_stat_card("Total Files", files_count_text, ft.Icons.FOLDER, ft.Colors.GREEN)], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([create_stat_card("Transfers", transfers_count_text, ft.Icons.SWAP_HORIZ, ft.Colors.ORANGE)], col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([create_stat_card("Storage Used", storage_used_text, ft.Icons.STORAGE, ft.Colors.PURPLE)], col={"sm": 12, "md": 6, "lg": 3})
    ])
    
    system_metrics_card = ft.Container(content=ft.Column([
        ft.Row([ft.Icon(ft.Icons.MEMORY, size=20, color=ft.Colors.BLUE), ft.Text("System Metrics", size=16, weight=ft.FontWeight.BOLD)], spacing=8),
        ft.Divider(height=1), create_metric_row("CPU", cpu_progress, cpu_text), create_metric_row("Memory", memory_progress, memory_text), create_metric_row("Disk", disk_progress, disk_text)
    ], spacing=12), bgcolor=ft.Colors.SURFACE, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=12, padding=20)
    
    activity_card = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.TIMELINE, size=20, color=ft.Colors.BLUE), ft.Text("Recent Activity", size=16, weight=ft.FontWeight.BOLD)], spacing=8),
            ft.Row([create_filter_button(t) for t in ["All", "Clients", "Files", "System"]], spacing=8),
            ft.Divider(height=1, margin=ft.margin.only(top=4)),
            ft.Container(content=activity_list, expand=True)
        ], spacing=4),
        bgcolor=ft.Colors.SURFACE, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=12, padding=20, expand=True
    )
    
    main_content = ft.ResponsiveRow([
        ft.Column([server_status_card, system_metrics_card], col={"sm": 12, "md": 12, "lg": 4}, spacing=20),
        ft.Column([activity_card], col={"sm": 12, "md": 12, "lg": 8})
    ], spacing=20)
    
    footer_row = ft.Row([ft.Icon(ft.Icons.UPDATE, size=16, color=ft.Colors.GREY), last_updated_text], spacing=8)
    
    main_view = ft.Column([
        header_row, ft.Divider(), stats_row, ft.Container(height=20),
        main_content, ft.Container(height=16), footer_row
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0, padding=ft.padding.symmetric(horizontal=24, vertical=12))
    
    # --- Setup Reactive Subscriptions ---
    def setup_reactive_subscriptions():
        """Setup reactive UI updates using modular operations utility"""
        # Server status subscription
        server_ops.create_reactive_subscription("server_status", update_server_status_ui)
        
        # Activity data subscription  
        def update_activity_ui(data, _):
            nonlocal activity_data
            activity_data = data or []
            
            if activity_data is None:
                return
            activity_list.controls.clear()
            
            filtered_activities = activity_data
            if activity_filter != "All":
                filter_map = {
                    "Clients": ["client_connect", "client_disconnect"], 
                    "Files": ["file_transfer", "backup_complete"], 
                    "System": ["system_check", "error"]
                }
                types_to_show = filter_map.get(activity_filter, [])
                filtered_activities = [a for a in activity_data if a.get("type") in types_to_show]

            if not filtered_activities:
                activity_list.controls.append(ft.Text("No activities for this filter.", 
                    text_align=ft.TextAlign.CENTER, color=ft.Colors.GREY_500, italic=True))
            
            for activity in sorted(filtered_activities, key=lambda x: x.get("timestamp"), reverse=True):
                act_type = activity.get("type", "unknown")
                icon = ft.Icons.PERSON if "client" in act_type else ft.Icons.FILE_COPY if "file" in act_type else ft.Icons.SYSTEM_UPDATE_ALT
                color = ft.Colors.GREEN if "connect" in act_type else ft.Colors.RED if "error" in act_type else ft.Colors.BLUE
                
                activity_list.controls.append(ft.ListTile(
                    leading=ft.Icon(icon, color=color, size=20),
                    title=ft.Text(activity.get("message", ""), size=13),
                    subtitle=ft.Text(format_time_ago(activity.get("timestamp")), size=11, color=ft.Colors.GREY_600)
                ))
            
            activity_list.update()
        
        server_ops.create_reactive_subscription("recent_activity", update_activity_ui)
        
        # Loading indicator subscription  
        loading_indicator = ft.Text("Loading...", size=12, color=ft.Colors.GREY_600, visible=False)
        server_ops.create_loading_subscription(loading_indicator, ["server_status", "recent_activity"])
    
    # --- Initial Data Load with Batch Operations ---
    async def initial_data_load():
        """Load all dashboard data using batch operations for better performance"""
        operations = [
            {
                'state_key': 'server_status',
                'server_operation': 'get_server_status_async',
                'fallback_data': generate_mock_server_status()
            },
            {
                'state_key': 'recent_activity',
                'server_operation': 'get_recent_activity_async',
                'fallback_data': generate_mock_activity(),
                'data_processor': timestamp_processor
            }
        ]
        
        results = await server_ops.batch_load_operations(operations)
        logger.info(f"Dashboard initial load completed: {len([r for r in results.values() if r.get('success')])} successful operations")
    
    # Setup subscriptions and load initial data
    setup_reactive_subscriptions()
    page.run_task(initial_data_load)
    
    return main_view