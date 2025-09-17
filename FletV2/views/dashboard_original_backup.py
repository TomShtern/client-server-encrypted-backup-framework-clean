#!/usr/bin/env python3
"""
Dashboard View for FletV2
Optimized responsive dashboard with Material Design 3 styling and enhanced state management.
Follows 2025 design trends with vibrant colors, sophisticated layering, and reactive patterns.
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
from utils.server_mediated_operations import create_server_mediated_operations
from utils.server_mediated_operations import timestamp_processor
from utils.ui_components import create_modern_card, create_modern_button, create_progress_indicator, create_status_chip
from theme import get_brand_color, get_shadow_style

logger = get_logger(__name__)

# Module-level server operations initialization to fix timing issues
server_ops = None

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

    # Initialize server operations immediately to prevent race conditions
    global server_ops
    if server_ops is None:
        server_ops = create_server_mediated_operations(state_manager, page)

    # --- State Management - Now handled by state_manager ---
    activity_filter = "All"

    # State variables for dashboard data
    system_metrics_data = {}
    server_status_data = {}
    activity_data = []
    is_loading = False
    last_updated = None

    # --- Enhanced UI Control References with Material Design 3 ---
    server_status_text = ft.Text("Unknown", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    server_port_text = ft.Text("", size=13, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
    uptime_text = ft.Text("", size=13, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
    # Enhanced metric text controls with Material Design 3 styling
    clients_count_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    files_count_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    transfers_count_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    storage_used_text = ft.Text("0 GB", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)

    # Enhanced Material Design 3 progress indicators with animations
    cpu_progress = ft.ProgressBar(
        value=0.0,
        width=180,
        height=8,
        color=ft.Colors.PRIMARY,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
        border_radius=ft.BorderRadius(4, 4, 4, 4),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    )
    memory_progress = ft.ProgressBar(
        value=0.0,
        width=180,
        height=8,
        color=ft.Colors.TERTIARY,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.TERTIARY),
        border_radius=ft.BorderRadius(4, 4, 4, 4),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    )
    disk_progress = ft.ProgressBar(
        value=0.0,
        width=180,
        height=8,
        color=ft.Colors.SECONDARY,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SECONDARY),
        border_radius=ft.BorderRadius(4, 4, 4, 4),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    )
    cpu_text = ft.Text("0%", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE)
    memory_text = ft.Text("0.0 / 0.0 GB (0.0%)", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE, font_family="monospace")
    disk_text = ft.Text("0.0 / 0.0 GB (0.0%)", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE, font_family="monospace")

    activity_list = ft.ListView(expand=True, spacing=8, padding=ft.padding.only(top=8))
    last_updated_text = ft.Text("Never", size=12, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
    loading_indicator = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False, color=ft.Colors.PRIMARY)

    # Enhanced activity loading row with Material Design 3 styling
    activity_loading_row = ft.Container(
        content=ft.Row([
            loading_indicator,
            ft.Text("Loading dashboard data...", size=13, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
        ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
        visible=False,
        padding=ft.Padding(16, 12, 16, 12),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.OUTLINE),
        border_radius=8,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )

    # Material Design 3 styled buttons
    start_server_btn = create_modern_button(
        "Start Server",
        lambda e: page.run_task(start_server_action),
        ft.Icons.PLAY_ARROW,
        variant="filled",
        color_type="primary"
    )
    stop_server_btn = create_modern_button(
        "Stop Server",
        lambda e: page.run_task(stop_server_action),
        ft.Icons.STOP,
        variant="filled",
        color_type="secondary"
    )

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
        """Reactive callback for server status changes with enhanced state management"""
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

        # Update state manager with current server status
        if state_manager:
            state_manager.update("server_status", server_status_data, source="dashboard_ui")

        # Use simple individual control updates
        for control in [server_status_text, server_port_text, uptime_text, start_server_btn,
                       stop_server_btn, clients_count_text, files_count_text, transfers_count_text, storage_used_text]:
            if hasattr(control, 'update'):
                control.update()

    def update_system_metrics_ui():
        """Enhanced system metrics UI update with improved color coding and animations"""
        cpu_percent = system_metrics_data.get("cpu_percent", 0)
        mem_percent = system_metrics_data.get("memory_percent", 0)
        disk_percent = system_metrics_data.get("disk_percent", 0)

        # Update progress bar values with smooth animations
        cpu_progress.value = cpu_percent / 100
        memory_progress.value = mem_percent / 100
        disk_progress.value = disk_percent / 100

        # Enhanced text formatting
        cpu_text.value = f"{cpu_percent:.1f}%"
        cpu_text.color = ft.Colors.ON_SURFACE
        cpu_text.weight = ft.FontWeight.W_600

        mem_used, mem_total = system_metrics_data.get("memory_used_gb", 0), system_metrics_data.get("memory_total_gb", 0)
        memory_text.value = f"{mem_used:.1f} / {mem_total:.1f} GB ({mem_percent:.1f}%)"
        memory_text.color = ft.Colors.ON_SURFACE
        memory_text.weight = ft.FontWeight.W_500

        disk_used, disk_total = system_metrics_data.get("disk_used_gb", 0), system_metrics_data.get("disk_total_gb", 0)
        disk_text.value = f"{disk_used:.1f} / {disk_total:.1f} GB ({disk_percent:.1f}%)"
        disk_text.color = ft.Colors.ON_SURFACE
        disk_text.weight = ft.FontWeight.W_500

        # Enhanced color coding with Material Design 3 colors
        if cpu_percent > 85:
            cpu_progress.color = ft.Colors.ERROR
        elif cpu_percent > 70:
            cpu_progress.color = ft.Colors.ORANGE
        else:
            cpu_progress.color = ft.Colors.PRIMARY

        if mem_percent > 85:
            memory_progress.color = ft.Colors.ERROR
        elif mem_percent > 70:
            memory_progress.color = ft.Colors.ORANGE
        else:
            memory_progress.color = ft.Colors.TERTIARY

        if disk_percent > 90:
            disk_progress.color = ft.Colors.ERROR
        elif disk_percent > 80:
            disk_progress.color = ft.Colors.ORANGE
        else:
            disk_progress.color = ft.Colors.SECONDARY

        # Use individual control updates for better performance
        for control in [cpu_progress, memory_progress, disk_progress, cpu_text, memory_text, disk_text]:
            if hasattr(control, 'update'):
                control.update()

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
        """Enhanced dashboard refresh with comprehensive state management and loading indicators"""
        nonlocal is_loading, last_updated, server_status_data, system_metrics_data, activity_data
        if is_loading:
            return
        is_loading = True

        try:
            # Set comprehensive loading state
            await state_manager.update_async("loading_states",
                {**state_manager.get("loading_states", {}), "dashboard_refresh": True})

            # Show enhanced loading indicators
            activity_loading_row.visible = True
            loading_indicator.visible = True
            # Safe update - only if control is attached to page
            if hasattr(activity_loading_row, 'page') and activity_loading_row.page:
                activity_loading_row.update()

            # Load all data concurrently with enhanced error handling
            tasks = [
                load_server_status(),
                load_system_metrics(),
                load_activity_data()
            ]

            server_status_result, system_metrics_result, activity_result = await asyncio.gather(
                *tasks, return_exceptions=True
            )

            # Handle individual task results with error resilience
            successful_operations = 0

            if not isinstance(server_status_result, Exception):
                server_status_data = state_manager.get('server_status', {})
                successful_operations += 1
            else:
                logger.error(f"Server status load failed: {server_status_result}")

            if not isinstance(system_metrics_result, Exception):
                successful_operations += 1
            else:
                logger.error(f"System metrics load failed: {system_metrics_result}")

            if not isinstance(activity_result, Exception):
                activity_data = state_manager.get('recent_activity', [])
                successful_operations += 1
            else:
                logger.error(f"Activity data load failed: {activity_result}")

            # Update timestamp and provide user feedback
            last_updated = datetime.now()
            last_updated_text.value = f"Updated: {last_updated.strftime('%H:%M:%S')} ({successful_operations}/3 successful)"
            last_updated_text.update()

            # Update comprehensive dashboard state
            if state_manager:
                await state_manager.update_async("dashboard_data", {
                    "server_status": server_status_data,
                    "system_metrics": system_metrics_data,
                    "activity": activity_data,
                    "last_updated": last_updated,
                    "successful_operations": successful_operations
                }, source="dashboard_refresh")

            # Show success message only if all operations succeeded
            if successful_operations == 3:
                show_success_message(page, "Dashboard refreshed successfully")
            elif successful_operations > 0:
                show_success_message(page, f"Dashboard partially refreshed ({successful_operations}/3 operations successful)")
            else:
                show_error_message(page, "Dashboard refresh failed - all operations failed")

        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")
            show_error_message(page, f"Failed to refresh dashboard: {str(e)}")
        finally:
            is_loading = False
            # Clear loading states
            await state_manager.update_async("loading_states",
                {**state_manager.get("loading_states", {}), "dashboard_refresh": False})
            # Hide loading indicators
            activity_loading_row.visible = False
            loading_indicator.visible = False
            # Safe update - only if control is attached to page
            if hasattr(activity_loading_row, 'page') and activity_loading_row.page:
                activity_loading_row.update()

    async def start_server_action():
        """Enhanced start server action with comprehensive state management and validation"""
        # Guard against uninitialized server_ops
        if server_ops is None:
            show_error_message(page, "Server operations not initialized, please wait...")
            return {'success': False, 'error': 'Operations not initialized'}

        try:
            # Set loading state for server operation
            await state_manager.update_async("loading_states",
                {**state_manager.get("loading_states", {}), "server_start": True})

            # Update UI to show server is starting with enhanced feedback
            server_status_text.value = "Starting..."
            server_status_text.color = ft.Colors.ORANGE
            start_server_btn.disabled = True
            start_server_btn.content.controls[1].value = "Starting..."
            stop_server_btn.disabled = True

            # Use individual control updates for better performance
            server_status_text.update()
            start_server_btn.update()
            stop_server_btn.update()

            result = await server_ops.action_operation(
                action_name="start_server",
                server_operation="start_server_async",
                operation_data={"action": "start"},
                success_message="Server started successfully",
                error_message="Failed to start server",
                refresh_keys=["server_status", "recent_activity"]
            )

            # Enhanced UI update based on result with proper state management
            # Safe result handling to prevent mapping errors
            if result and isinstance(result, dict) and result.get('success'):
                server_status_text.value = "Running"
                server_status_text.color = ft.Colors.GREEN
                start_server_btn.disabled = True
                start_server_btn.content.controls[1].value = "Start Server"
                stop_server_btn.disabled = False
                # Update server status in state
                await state_manager.update_async("server_status",
                    {**state_manager.get("server_status", {}), "running": True}, "server_start_success")
            else:
                server_status_text.value = "Error"
                server_status_text.color = ft.Colors.ERROR
                start_server_btn.disabled = False
                start_server_btn.content.controls[1].value = "Start Server"
                stop_server_btn.disabled = True
                # Safe error message handling
                error_msg = "Unknown error"
                if result and isinstance(result, dict):
                    error_msg = result.get('error', 'Unknown error')
                elif result is None:
                    error_msg = "No response from server"
                show_error_message(page, f"Failed to start server: {error_msg}")

            # Use individual control updates for better performance
            server_status_text.update()
            start_server_btn.update()
            stop_server_btn.update()

            return result

        except Exception as e:
            logger.error(f"Error starting server: {e}")
            show_error_message(page, f"Error starting server: {str(e)}")

            # Enhanced error state reset
            server_status_text.value = "Error"
            server_status_text.color = ft.Colors.ERROR
            start_server_btn.disabled = False
            start_server_btn.content.controls[1].value = "Start Server"
            stop_server_btn.disabled = True

            server_status_text.update()
            start_server_btn.update()
            stop_server_btn.update()

            return {'success': False, 'error': str(e)}
        finally:
            # Always clear loading state
            await state_manager.update_async("loading_states",
                {**state_manager.get("loading_states", {}), "server_start": False})

    async def stop_server_action():
        """Enhanced stop server action with comprehensive state management and validation"""
        # Guard against uninitialized server_ops
        if server_ops is None:
            show_error_message(page, "Server operations not initialized, please wait...")
            return {'success': False, 'error': 'Operations not initialized'}

        try:
            # Set loading state for server operation
            await state_manager.update_async("loading_states",
                {**state_manager.get("loading_states", {}), "server_stop": True})

            # Update UI to show server is stopping with enhanced feedback
            server_status_text.value = "Stopping..."
            server_status_text.color = ft.Colors.ORANGE
            start_server_btn.disabled = True
            stop_server_btn.disabled = True
            stop_server_btn.content.controls[1].value = "Stopping..."

            # Use individual control updates for better performance
            server_status_text.update()
            start_server_btn.update()
            stop_server_btn.update()

            result = await server_ops.action_operation(
                action_name="stop_server",
                server_operation="stop_server_async",
                operation_data={"action": "stop"},
                success_message="Server stopped successfully",
                error_message="Failed to stop server",
                refresh_keys=["server_status", "recent_activity"]
            )

            # Enhanced UI update based on result with proper state management
            if result.get('success'):
                server_status_text.value = "Stopped"
                server_status_text.color = ft.Colors.ERROR
                start_server_btn.disabled = False
                stop_server_btn.disabled = True
                stop_server_btn.content.controls[1].value = "Stop Server"
                # Update server status in state
                await state_manager.update_async("server_status",
                    {**state_manager.get("server_status", {}), "running": False}, "server_stop_success")
            else:
                server_status_text.value = "Error"
                server_status_text.color = ft.Colors.ERROR
                start_server_btn.disabled = True
                stop_server_btn.disabled = False
                stop_server_btn.content.controls[1].value = "Stop Server"
                show_error_message(page, f"Failed to stop server: {result.get('error', 'Unknown error')}")

            # Use individual control updates for better performance
            server_status_text.update()
            start_server_btn.update()
            stop_server_btn.update()

            return result

        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            show_error_message(page, f"Error stopping server: {str(e)}")

            # Enhanced error state reset
            server_status_text.value = "Error"
            server_status_text.color = ft.Colors.ERROR
            start_server_btn.disabled = True
            stop_server_btn.disabled = False
            stop_server_btn.content.controls[1].value = "Stop Server"

            server_status_text.update()
            start_server_btn.update()
            stop_server_btn.update()

            return {'success': False, 'error': str(e)}
        finally:
            # Always clear loading state
            await state_manager.update_async("loading_states",
                {**state_manager.get("loading_states", {}), "server_stop": False})

    # --- Enhanced UI Layout Construction with Material Design 3 ---
    def create_enhanced_metric_card(title: str, value_control: ft.Control, icon: str, color: str) -> ft.Container:
        """Create enhanced metric cards using create_modern_card with sophisticated styling"""
        card_content = ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=32, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=16,
                    padding=12,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=8,
                        offset=ft.Offset(0, 2),
                        color=ft.Colors.with_opacity(0.3, color)
                    )
                ),
                ft.Container(expand=True),  # Spacer
                ft.Column([
                    value_control,
                    ft.Text(title, size=13, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
                ], spacing=4, tight=True, horizontal_alignment=ft.CrossAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=16)

        return create_modern_card(
            content=card_content,
            elevation="elevated",
            hover_effect=True,
            color_accent="primary",
            padding=24,
            return_type="container"
        )

    def create_animated_progress_indicator(label: str, progress_bar: ft.ProgressBar, text_control: ft.Text) -> ft.Container:
        """Create animated progress indicators with Material Design 3 styling"""
        return create_progress_indicator(
            value=progress_bar.value or 0.0,
            label=label,
            color=progress_bar.color,
            show_percentage=True,
            animated=True
        )

    def create_enhanced_metric_row(label: str, progress: ft.ProgressBar, text: ft.Text) -> ft.Container:
        """Create enhanced metric rows with modern styling and animations"""
        text.text_align = ft.TextAlign.RIGHT

        # Enhanced progress bar with smooth animations
        enhanced_progress = ft.ProgressBar(
            value=progress.value,
            width=180,
            color=progress.color,
            bgcolor=ft.Colors.with_opacity(0.1, progress.color),
            height=8,
            border_radius=ft.BorderRadius(4, 4, 4, 4),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                    ft.Container(expand=True),
                    text
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=8),
                enhanced_progress
            ], spacing=0),
            padding=ft.Padding(0, 12, 0, 12),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

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
            selected_color=ft.Colors.PRIMARY,
        )
        filter_buttons[text] = chip
        return chip

    # Enhanced header with Material Design 3 styling
    header_row = ft.Row([
        ft.Row([
            ft.Icon(ft.Icons.DASHBOARD, size=32, color=ft.Colors.PRIMARY),
            ft.Text("Server Dashboard",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ON_SURFACE,
                style=ft.TextThemeStyle.HEADLINE_LARGE)
        ], spacing=16),
        ft.Row([
            ft.Container(
                content=ft.Text(f"Last updated: Never",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    ref=ft.Ref()),
                padding=ft.Padding(12, 6, 12, 6),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.OUTLINE),
                border_radius=8
            ),
            create_modern_button(
                "Refresh",
                lambda e: page.run_task(refresh_dashboard),
                icon=ft.Icons.REFRESH,
                variant="outlined",
                color_type="primary",
                size="medium"
            )
        ], spacing=12)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Enhanced server status card with modern styling
    server_status_card_content = ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.DNS, size=24, color=ft.Colors.PRIMARY),
            ft.Text("Server Control", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        ], spacing=12),
        ft.Divider(height=1, color=ft.Colors.OUTLINE),
        ft.Container(height=8),
        ft.Column([server_status_text, server_port_text, uptime_text], spacing=6),
        ft.Container(height=20),
        ft.ResponsiveRow([
            ft.Column([start_server_btn], col={"xs": 12, "sm": 12, "md": 6}),
            ft.Column([stop_server_btn], col={"xs": 12, "sm": 12, "md": 6})
        ], spacing=16)
    ], spacing=16)

    server_status_card = create_modern_card(
        content=server_status_card_content,
        elevation="elevated",
        hover_effect=True,
        padding=28,
        return_type="container"
    )

    # Enhanced responsive stats row with proper breakpoints
    stats_row = ft.ResponsiveRow([
        ft.Column([
            create_enhanced_metric_card("Active Clients", clients_count_text, ft.Icons.PEOPLE, ft.Colors.BLUE)
        ], col={"xs": 12, "sm": 12, "md": 6, "lg": 3}),  # Mobile: 1 column, Tablet: 2 columns, Desktop: 4 columns
        ft.Column([
            create_enhanced_metric_card("Total Files", files_count_text, ft.Icons.FOLDER, ft.Colors.GREEN)
        ], col={"xs": 12, "sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_enhanced_metric_card("Transfers", transfers_count_text, ft.Icons.SWAP_HORIZ, ft.Colors.ORANGE)
        ], col={"xs": 12, "sm": 12, "md": 6, "lg": 3}),
        ft.Column([
            create_enhanced_metric_card("Storage Used", storage_used_text, ft.Icons.STORAGE, ft.Colors.PURPLE)
        ], col={"xs": 12, "sm": 12, "md": 6, "lg": 3})
    ], spacing=20)  # Enhanced spacing for better visual separation

    # Enhanced system metrics card with animated progress indicators
    system_metrics_card_content = ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.MEMORY, size=24, color=ft.Colors.PRIMARY),
            ft.Text("System Metrics", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        ], spacing=12),
        ft.Divider(height=1, color=ft.Colors.OUTLINE),
        ft.Container(height=8),
        create_enhanced_metric_row("CPU Usage", cpu_progress, cpu_text),
        create_enhanced_metric_row("Memory Usage", memory_progress, memory_text),
        create_enhanced_metric_row("Disk Usage", disk_progress, disk_text)
    ], spacing=16)

    system_metrics_card = create_modern_card(
        content=system_metrics_card_content,
        elevation="elevated",
        hover_effect=True,
        padding=28,
        return_type="container"
    )

    # Enhanced activity card with modern filter design
    activity_card_content = ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.TIMELINE, size=24, color=ft.Colors.PRIMARY),
            ft.Text("Recent Activity", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        ], spacing=12),
        ft.Container(height=8),
        ft.Row([create_filter_button(t) for t in ["All", "Clients", "Files", "System"]], spacing=12),
        ft.Divider(height=1, color=ft.Colors.OUTLINE),
        activity_loading_row,
        ft.Container(content=activity_list, expand=True)
    ], spacing=12)

    activity_card = create_modern_card(
        content=activity_card_content,
        elevation="elevated",
        hover_effect=True,
        padding=28,
        return_type="container"
    )

    # Enhanced responsive main content layout with proper breakpoints
    main_content = ft.ResponsiveRow([
        ft.Column([
            server_status_card,
            ft.Container(height=24),  # Spacing between cards
            system_metrics_card
        ], col={"xs": 12, "sm": 12, "md": 12, "lg": 4}, spacing=0),  # Stack vertically on mobile/tablet
        ft.Column([
            activity_card
        ], col={"xs": 12, "sm": 12, "md": 12, "lg": 8})
    ], spacing=28, expand=True)  # Enhanced spacing for better visual hierarchy

    # Enhanced footer with Material Design 3 styling
    footer_row = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.UPDATE, size=16, color=ft.Colors.ON_SURFACE_VARIANT),
            last_updated_text,
            ft.Container(expand=True),  # Spacer
            ft.Text(f"System Status: Active",
                size=12,
                color=ft.Colors.TERTIARY,
                weight=ft.FontWeight.W_500)
        ], spacing=8),
        padding=ft.Padding(16, 12, 16, 12),
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.OUTLINE),
        border_radius=12,
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE))
    )

    # Enhanced main view with improved spacing and layout
    main_view = ft.Container(
        content=ft.Column([
            header_row,
            ft.Container(height=8),
            ft.Divider(color=ft.Colors.OUTLINE),
            ft.Container(height=20),
            stats_row,
            ft.Container(height=32),  # Enhanced spacing
            main_content,
            ft.Container(height=24),
            footer_row
        ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0),
        padding=ft.padding.symmetric(horizontal=28, vertical=20),  # Enhanced padding
        expand=True,
        alignment=ft.alignment.top_left,
        bgcolor=ft.Colors.SURFACE,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )

    # --- Enhanced Reactive Subscriptions with State Management ---
    def setup_reactive_subscriptions():
        """Setup enhanced reactive UI updates with comprehensive state management"""
        # Enhanced server status subscription with loading state management
        async def enhanced_server_status_update(data, old_data):
            """Enhanced server status update with loading state management"""
            try:
                await state_manager.update_async("loading_states",
                    {**state_manager.get("loading_states", {}), "server_status": False})
                update_server_status_ui(data, old_data)
            except Exception as e:
                logger.error(f"Server status update failed: {e}")

        server_ops.create_reactive_subscription("server_status", enhanced_server_status_update)

        # Enhanced activity data subscription with better error handling
        async def enhanced_activity_update(data, old_data):
            """Enhanced activity update with async support and error handling"""
            nonlocal activity_data
            try:
                activity_data = data or []
                await update_activity_display_async()
                await state_manager.update_async("loading_states",
                    {**state_manager.get("loading_states", {}), "recent_activity": False})
            except Exception as e:
                logger.error(f"Activity update failed: {e}")

        async def update_activity_display_async():
            """Async activity display update with enhanced UI"""
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
                activity_list.controls.append(ft.Container(
                    content=ft.Text("No activities for this filter.",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        italic=True, size=14),
                    padding=ft.Padding(0, 32, 0, 32),
                    alignment=ft.alignment.center
                ))

            for activity in sorted(filtered_activities, key=lambda x: x.get("timestamp"), reverse=True):
                act_type = activity.get("type", "unknown")
                icon, color, bgcolor = ft.Icons.INFO, ft.Colors.GREY, ft.Colors.TRANSPARENT

                if act_type == "client_connect":
                    icon, color = ft.Icons.PERSON_ADD, ft.Colors.GREEN
                elif act_type == "client_disconnect":
                    icon, color = ft.Icons.PERSON_REMOVE, ft.Colors.ORANGE
                elif act_type == "file_transfer":
                    icon, color = ft.Icons.FILE_DOWNLOAD, ft.Colors.BLUE
                elif act_type == "backup_complete":
                    icon, color, bgcolor = ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN, ft.Colors.with_opacity(0.05, ft.Colors.GREEN)
                elif act_type == "system_check":
                    icon, color = ft.Icons.HEALTH_AND_SAFETY, ft.Colors.PURPLE
                elif act_type == "error":
                    icon, color, bgcolor = ft.Icons.ERROR_OUTLINE, ft.Colors.ERROR, ft.Colors.with_opacity(0.05, ft.Colors.ERROR)

                activity_list.controls.append(ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(icon, color=color, size=20),
                        title=ft.Text(activity.get("message", ""), size=13, weight=ft.FontWeight.W_400),
                        subtitle=ft.Text(format_time_ago(activity.get("timestamp")),
                            size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                        content_padding=ft.padding.symmetric(horizontal=16, vertical=6)
                    ),
                    bgcolor=bgcolor,
                    border_radius=8,
                    margin=ft.Margin(0, 2, 0, 2),
                    animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
                ))

            activity_list.update()

        server_ops.create_reactive_subscription("recent_activity", enhanced_activity_update)

        # Enhanced loading indicator subscription with comprehensive state management
        async def update_enhanced_loading_indicator(loading_states, old_states):
            """Enhanced loading indicator with comprehensive state tracking"""
            try:
                # Show indicator if any dashboard operation is loading
                dashboard_loading_keys = ["server_status", "recent_activity", "system_metrics", "dashboard_refresh"]
                is_any_loading = any(loading_states.get(key, False) for key in dashboard_loading_keys)

                activity_loading_row.visible = is_any_loading
                loading_indicator.visible = is_any_loading

                # Update loading text based on active operations
                active_ops = [key for key in dashboard_loading_keys if loading_states.get(key, False)]
                if active_ops:
                    loading_text = f"Loading {', '.join(active_ops)}..."
                    if hasattr(activity_loading_row, 'controls') and activity_loading_row.controls and len(activity_loading_row.controls) > 1:
                        activity_loading_row.controls[1].value = loading_text

                activity_loading_row.update()
            except Exception as e:
                logger.error(f"Enhanced loading subscription callback failed: {e}")

        server_ops.create_reactive_subscription("loading_states", update_enhanced_loading_indicator)

        # Dashboard data subscription for comprehensive updates
        async def on_dashboard_data_change(data, old_data):
            """Handle comprehensive dashboard data changes"""
            try:
                if data and isinstance(data, dict):
                    # Update individual components based on comprehensive data
                    if "system_metrics" in data:
                        await load_system_metrics()
                    if "server_status" in data:
                        update_server_status_ui(data["server_status"], old_data.get("server_status") if old_data else None)
                    logger.debug("Dashboard data synchronized successfully")
            except Exception as e:
                logger.error(f"Dashboard data subscription failed: {e}")

        state_manager.subscribe("dashboard_data", on_dashboard_data_change)

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

    # Setup server operations and subscriptions immediately (using module-level server_ops)
    async def setup_dashboard():
        """Set up server operations and subscriptions using module-level server_ops"""
        global server_ops

        # Ensure server_ops is initialized
        if server_ops is None:
            server_ops = create_server_mediated_operations(state_manager, page)
            logger.info("Server operations initialized in setup_dashboard")

        # Small delay to ensure page attachment
        await asyncio.sleep(0.05)

        # Setup subscriptions and load initial data
        try:
            setup_reactive_subscriptions()
            await initial_data_load()
            logger.info("Dashboard setup completed successfully")
        except Exception as e:
            logger.error(f"Error during dashboard setup: {e}")
            show_error_message(page, f"Dashboard setup failed: {str(e)}")

    # Start dashboard setup in background
    page.run_task(setup_dashboard)

    return main_view