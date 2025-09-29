#!/usr/bin/env python3
"""
Advanced Dashboard - Phase 1: Real Server Integration & Performance
Implementing async patterns, real-time updates, and enhanced server connectivity
"""

import asyncio
import contextlib
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Callable, Optional

# Path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import flet as ft
import Shared.utils.utf8_solution as _  # noqa: F401

# Setup logging
logger = logging.getLogger(__name__)

def create_dashboard_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None
) -> tuple[ft.Control, Callable, Callable]:
    """Create an advanced dashboard with real server integration and performance optimization."""

    logger.info("Creating dashboard view with enhanced server integration")

    # === PHASE 1: ENHANCED REFS FOR TARGETED UPDATES ===
    # Metric value refs
    clients_count_ref = ft.Ref[ft.Text]()
    files_count_ref = ft.Ref[ft.Text]()
    storage_value_ref = ft.Ref[ft.Text]()
    uptime_value_ref = ft.Ref[ft.Text]()

    # PHASE 4.2: Enhanced circular gauge refs
    storage_progress_ref = ft.Ref[ft.ProgressRing]()
    cpu_progress_ref = ft.Ref[ft.ProgressRing]()
    memory_progress_ref = ft.Ref[ft.ProgressRing]()

    # PHASE 4.2: Performance gauge containers (for accessing additional status refs)
    storage_gauge_container = None
    cpu_gauge_container = None
    memory_gauge_container = None

    # Status and control refs
    last_update_ref = ft.Ref[ft.Text]()
    status_indicator_ref = ft.Ref[ft.Icon]()
    refresh_button_ref = ft.Ref[ft.IconButton]()
    loading_indicator_ref = ft.Ref[ft.ProgressRing]()

    # Activity stream refs
    activity_list_ref = ft.Ref[ft.ListView]()

    # === BACKGROUND TASK MANAGEMENT ===
    _background_task = None
    _disposed = False
    _last_update_time = None

    # === ASYNC SERVER INTEGRATION PATTERNS ===
    async def safe_server_call(method_name: str, *args, **kwargs) -> dict:
        """Safely call server methods with proper async handling."""
        if not server_bridge:
            logger.warning("No server bridge available")
            return {'success': False, 'error': 'No server connection'}

        try:
            method = getattr(server_bridge, method_name, None)
            if method is None:
                return {'success': False, 'error': f'Method {method_name} not available'}

            # Handle both sync and async methods
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                # Run sync methods in executor to avoid blocking UI
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: method(*args, **kwargs))

            # Normalize response format
            if isinstance(result, dict):
                return result
            else:
                return {'success': True, 'data': result}

        except Exception as e:
            logger.error(f"Server call {method_name} failed: {e}")
            return {'success': False, 'error': str(e)}

    async def get_comprehensive_server_data() -> dict:
        """Fetch comprehensive server data using multiple API calls with proper method mapping."""
        data = {}

        # 1. Get dashboard summary (primary source for consolidated metrics)
        dashboard_result = await safe_server_call('get_dashboard_summary_async')
        if dashboard_result.get('success'):
            dashboard_data = dashboard_result.get('data', {})
            data.update(dashboard_data)
            logger.info(f"Dashboard summary data: {dashboard_data}")

        # 2. Get system status (uptime, basic system info)
        system_result = await safe_server_call('get_system_status_async')
        if system_result.get('success'):
            system_data = system_result.get('data', {})
            data.update(system_data)
            logger.info(f"System status data: {system_data}")

        # 3. Get performance metrics (CPU, memory, storage)
        performance_result = await safe_server_call('get_performance_metrics_async')
        if performance_result.get('success'):
            performance_data = performance_result.get('data', {})
            data.update(performance_data)
            logger.info(f"Performance metrics: {performance_data}")

        # 4. Get server statistics (file counts, client stats)
        stats_result = await safe_server_call('get_server_statistics_async')
        if stats_result.get('success'):
            stats_data = stats_result.get('data', {})
            data.update(stats_data)
            logger.info(f"Server statistics: {stats_data}")

        # 5. Get client data (active connections)
        clients_result = await safe_server_call('get_clients_async')
        if clients_result.get('success'):
            clients_data = clients_result.get('data', [])
            data['clients_connected'] = len(clients_data)
            data['active_clients'] = len([c for c in clients_data if c.get('status') in ['online', 'Active', 'connected']])
            logger.info(f"Clients data: {len(clients_data)} total, {data['active_clients']} active")

        # 6. Get recent activity (FIXED: using correct method name)
        activity_result = await safe_server_call('get_recent_activity_async', limit=10)
        if activity_result.get('success'):
            data['recent_activities'] = activity_result.get('data', [])
            logger.info(f"Recent activities: {len(data.get('recent_activities', []))} items")

        # 7. Calculate derived metrics with fallback values
        # Storage percentage calculation
        storage_used = data.get('storage_used_gb', data.get('storage_used', 0))
        storage_total = data.get('storage_total_gb', data.get('storage_total', data.get('storage_capacity', 100)))
        if storage_total > 0:
            data['storage_percentage'] = min(100, (storage_used / storage_total) * 100)
        else:
            data['storage_percentage'] = 0

        # Ensure numeric values for progress bars
        data['cpu_usage'] = max(0, min(100, data.get('cpu_usage', data.get('cpu_percent', 0))))
        data['memory_usage'] = max(0, min(100, data.get('memory_usage', data.get('memory_percent', 0))))

        # Format uptime with multiple possible sources
        uptime_seconds = data.get('uptime_seconds', data.get('uptime', data.get('system_uptime', 0)))
        if uptime_seconds:
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            data['uptime_formatted'] = f"{days}d {hours}h {minutes}m"
        else:
            data['uptime_formatted'] = "Unknown"

        # Ensure total_files count
        if 'total_files' not in data:
            data['total_files'] = data.get('file_count', data.get('files_count', 0))

        logger.info(f"Comprehensive data compiled: {list(data.keys())}")
        return data

    def show_user_feedback(message: str, is_error: bool = False):
        """Show user feedback via snackbar."""
        try:
            if hasattr(page, 'snack_bar'):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=ft.Colors.ERROR if is_error else ft.Colors.PRIMARY
                )
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            logger.error(f"Failed to show user feedback: {e}")

    def set_loading_state(loading: bool):
        """Set loading state across UI components."""
        try:
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = loading
                loading_indicator_ref.current.update()

            if refresh_button_ref.current:
                refresh_button_ref.current.disabled = loading
                refresh_button_ref.current.update()
        except Exception as e:
            logger.debug(f"Error setting loading state: {e}")

    def update_status_indicator(connected: bool):
        """Update connection status indicator."""
        try:
            if status_indicator_ref.current:
                status_indicator_ref.current.name = ft.Icons.CLOUD_DONE if connected else ft.Icons.CLOUD_OFF
                status_indicator_ref.current.color = ft.Colors.GREEN if connected else ft.Colors.RED
                status_indicator_ref.current.update()
        except Exception as e:
            logger.debug(f"Error updating status indicator: {e}")

    def update_dashboard_data(data: dict):
        """Update all dashboard components with new data - optimized with targeted updates."""
        try:
            # Update metric values
            if clients_count_ref.current:
                clients_count_ref.current.value = str(data.get('clients_connected', 0))
                clients_count_ref.current.update()

            if files_count_ref.current:
                files_count_ref.current.value = str(data.get('total_files', 0))
                files_count_ref.current.update()

            if storage_value_ref.current:
                storage_gb = data.get('storage_used_gb', 0)
                storage_value_ref.current.value = f"{storage_gb:.1f} GB"
                storage_value_ref.current.update()

            if uptime_value_ref.current:
                uptime_value_ref.current.value = data.get('uptime_formatted', 'N/A')
                uptime_value_ref.current.update()

            # PHASE 4.2: Update enhanced circular gauges with status indicators
            def update_gauge_with_status(progress_ref, container, value, label):
                """Update circular gauge with status indicators and percentage display."""
                if not progress_ref.current or not container:
                    return
                # Update main progress ring
                progress_ref.current.value = min(1.0, value / 100)
                progress_ref.current.update()

                # Update percentage display
                if hasattr(container, 'percentage_ref') and container.percentage_ref.current:
                    container.percentage_ref.current.value = f"{int(value)}%"
                    container.percentage_ref.current.update()

                # Update status indicators based on threshold
                if hasattr(container, 'get_threshold_status'):
                    icon, color, text = container.get_threshold_status(value)

                    if hasattr(container, 'status_icon_ref') and container.status_icon_ref.current:
                        container.status_icon_ref.current.name = icon
                        container.status_icon_ref.current.color = color
                        container.status_icon_ref.current.update()

                    if hasattr(container, 'status_text_ref') and container.status_text_ref.current:
                        container.status_text_ref.current.value = text
                        container.status_text_ref.current.color = color
                        container.status_text_ref.current.update()

            # Update all performance gauges with enhanced status
            storage_usage = data.get('storage_percentage', 0)
            cpu_usage = data.get('cpu_usage', 0)
            memory_usage = data.get('memory_usage', 0)

            update_gauge_with_status(storage_progress_ref, storage_gauge_container, storage_usage, "Storage")
            update_gauge_with_status(cpu_progress_ref, cpu_gauge_container, cpu_usage, "CPU")
            update_gauge_with_status(memory_progress_ref, memory_gauge_container, memory_usage, "Memory")

            # Update activity stream
            activities = data.get('recent_activities', [])
            update_activity_stream(activities)

            # Update last refresh time
            if last_update_ref.current:
                last_update_ref.current.value = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
                last_update_ref.current.update()

            # Update connection status
            update_status_indicator(True)

        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
            update_status_indicator(False)

    def update_activity_stream(activities: list):
        """PHASE 4.2: Update the premium activity timeline with enhanced data."""
        try:
            if not activity_list_ref.current:
                return

            # Clear existing activities
            activity_list_ref.current.controls.clear()

            # PHASE 4.2: Enhanced activity timeline generation
            recent_activities = activities[:8]  # Limit to 8 for better visual balance

            for i, activity in enumerate(recent_activities):
                is_last_item = (i == len(recent_activities) - 1)

                activity_item = create_activity_item(
                    activity.get('client', 'Unknown Client'),
                    activity.get('action', 'Unknown Action'),
                    activity.get('status', 'Unknown'),
                    activity.get('time', datetime.now().isoformat()),
                    is_last=is_last_item
                )
                activity_list_ref.current.controls.append(activity_item)

            # PHASE 4.2: Enhanced placeholder with premium styling
            if not activities:
                placeholder = ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.TIMELINE,
                                size=32,
                                color=ft.Colors.with_opacity(0.4, ft.Colors.ON_SURFACE)
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.Margin(0, 0, 0, 12)
                        ),
                        ft.Text(
                            "No Recent Activity",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.ON_SURFACE,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            "Activity will appear here as clients connect and perform operations",
                            size=12,
                            color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                            text_align=ft.TextAlign.CENTER
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                    padding=40,
                    alignment=ft.alignment.center
                )
                activity_list_ref.current.controls.append(placeholder)

            activity_list_ref.current.update()

        except Exception as e:
            logger.error(f"Error updating activity stream: {e}")

    async def refresh_dashboard_data():
        """Refresh all dashboard data with proper error handling."""
        try:
            set_loading_state(True)

            # Fetch comprehensive data
            data = await get_comprehensive_server_data()

            if data:
                update_dashboard_data(data)
                nonlocal _last_update_time
                _last_update_time = time.time()
            else:
                # Handle no data scenario
                show_user_feedback("No data received from server", is_error=True)
                update_status_indicator(False)

        except Exception as e:
            logger.error(f"Dashboard refresh failed: {e}")
            show_user_feedback(f"Refresh failed: {str(e)[:50]}...", is_error=True)
            update_status_indicator(False)
        finally:
            set_loading_state(False)

    async def background_refresh_loop():
        """Background task for automatic data refresh."""
        refresh_interval = int(os.environ.get('DASHBOARD_REFRESH_INTERVAL', '5'))  # 5 seconds default

        while not _disposed:
            try:
                await refresh_dashboard_data()
                await asyncio.sleep(refresh_interval)
            except asyncio.CancelledError:
                logger.info("Background refresh loop cancelled")
                break
            except Exception as e:
                logger.error(f"Background refresh error: {e}")
                await asyncio.sleep(refresh_interval * 2)  # Backoff on error

    # === NAVIGATION HANDLERS (PHASE 4.1) ===

    def navigate_to_clients(e):
        """Navigate to clients page - using app's navigation system."""
        try:
            if navigate_callback:
                navigate_callback("clients")
                logger.info("Navigated to clients page")
            else:
                logger.warning("No navigation callback available")
        except Exception as nav_error:
            logger.error(f"Navigation to clients failed: {nav_error}")

    def navigate_to_files(e):
        """Navigate to files page."""
        try:
            if navigate_callback:
                navigate_callback("files")
                logger.info("Navigated to files page")
            else:
                logger.warning("No navigation callback available")
        except Exception as nav_error:
            logger.error(f"Navigation to files failed: {nav_error}")

    def navigate_to_database(e):
        """Navigate to database page."""
        try:
            if navigate_callback:
                navigate_callback("database")
                logger.info("Navigated to database page")
            else:
                logger.warning("No navigation callback available")
        except Exception as nav_error:
            logger.error(f"Navigation to database failed: {nav_error}")

    def navigate_to_analytics(e):
        """Navigate to analytics page."""
        try:
            if navigate_callback:
                navigate_callback("analytics")
                logger.info("Navigated to analytics page")
            else:
                logger.warning("No navigation callback available")
        except Exception as nav_error:
            logger.error(f"Navigation to analytics failed: {nav_error}")

    # === UI COMPONENT BUILDERS ===
    def create_enhanced_metric_card(title: str, value_ref: ft.Ref, icon: str, color: str, on_click=None, destination_hint: str = "") -> ft.Container:
        """PHASE 4.1: Interactive Metric Card - Clickable with navigation and hover states."""

        # Track hover state for visual feedback
        is_hovered = False

        def on_hover_change(e):
            nonlocal is_hovered
            is_hovered = e.data == "true"
            # Update card appearance on hover if clickable
            if on_click:
                container.bgcolor = ft.Colors.with_opacity(0.08, color) if is_hovered else ft.Colors.SURFACE
                container.update()

        # Material Design 3 interactive container
        container = ft.Container(
            content=ft.Column([
                # MD3 Header with proper icon-text relationship
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=20),
                        width=40, height=40,
                        bgcolor=ft.Colors.with_opacity(0.12, color),
                        border_radius=20,  # Circular icon container
                        alignment=ft.alignment.center
                    ),
                    ft.Text(
                        title,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.ON_SURFACE
                    )
                ], spacing=12, alignment=ft.MainAxisAlignment.START),

                # MD3 Primary value with proper typography scale
                ft.Container(
                    content=ft.Text(
                        "Loading...",
                        ref=value_ref,
                        size=32,  # Display Large from MD3 type scale
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.ON_SURFACE
                    ),
                    padding=ft.Padding(0, 8, 0, 0)
                ),

                # MD3 Progress indicator with refined styling
                ft.Container(
                    content=ft.ProgressBar(
                        value=0,
                        color=color,
                        bgcolor=ft.Colors.with_opacity(0.12, color),
                        height=6,
                        border_radius=3
                    ),
                    margin=ft.Margin(0, 8, 0, 0)
                ),

                # PHASE 4.1: Navigation hint for clickable cards
                ft.Container(
                    content=ft.Row([
                        ft.Text(
                            f"Click to view {destination_hint}" if on_click and destination_hint else "",
                            size=11,
                            color=ft.Colors.with_opacity(0.7, color),
                            italic=True
                        ),
                        ft.Icon(
                            ft.Icons.ARROW_FORWARD_IOS,
                            size=12,
                            color=ft.Colors.with_opacity(0.7, color)
                        ) if on_click else ft.Container()
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    visible=bool(on_click),  # Only show if clickable
                    margin=ft.Margin(0, 4, 0, 0)
                )

            ], spacing=8, alignment=ft.MainAxisAlignment.START),

            # MD3 Surface styling with elevation
            padding=24,  # MD3 spacing standard
            border_radius=16,  # MD3 large component radius
            bgcolor=ft.Colors.SURFACE,  # Conservative MD3-style surface
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            width=240,  # Optimized for desktop
            height=180,

            # MD3 interaction states with Phase 4.1 enhancements
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            ),

            # PHASE 4.1: Interactive behaviors
            on_click=on_click or None,
            on_hover=on_hover_change if on_click else None,
            tooltip=f"Click to navigate to {destination_hint}" if on_click and destination_hint else None
        )

        return container

    def create_progress_indicator_card(title: str, progress_ref: ft.Ref, color: str) -> ft.Container:
        """PHASE 4.2: Premium Circular Gauge with Status Thresholds and Micro-animations."""

        # Create additional refs for enhanced status display
        status_icon_ref = ft.Ref[ft.Icon]()
        status_text_ref = ft.Ref[ft.Text]()
        percentage_ref = ft.Ref[ft.Text]()

        def get_threshold_status(value: float) -> tuple[str, str, str]:
            """Determine status based on performance thresholds."""
            if value >= 90:
                return ft.Icons.ERROR, ft.Colors.RED, "Critical"
            elif value >= 75:
                return ft.Icons.WARNING_AMBER, ft.Colors.ORANGE, "High"
            elif value >= 50:
                return ft.Icons.INFO, ft.Colors.BLUE, "Moderate"
            else:
                return ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN, "Optimal"

        # Track hover state for premium interactions
        is_hovered = False

        def on_hover_change(e):
            nonlocal is_hovered
            is_hovered = e.data == "true"
            # Subtle scale and shadow enhancement on hover
            container.scale = 1.02 if is_hovered else 1.0
            if is_hovered:
                container.shadow = ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=12,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                    offset=ft.Offset(0, 6)
                )
            else:
                container.shadow = ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=6,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2)
                )
            container.update()

        # PHASE 4.2: Premium circular gauge container
        container = ft.Container(
            content=ft.Column([
                # Enhanced header with status indicator
                ft.Row([
                    ft.Text(
                        title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.ON_SURFACE
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                ref=status_icon_ref,
                                size=16,
                                color=ft.Colors.GREEN
                            ),
                            ft.Text(
                                "Optimal",
                                ref=status_text_ref,
                                size=11,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREEN
                            )
                        ], spacing=4),
                        opacity=0.8
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # PHASE 4.2: Sophisticated circular gauge design
                ft.Container(
                    content=ft.Stack([
                        # Background arc
                        ft.ProgressRing(
                            value=1.0,
                            color=ft.Colors.with_opacity(0.08, color),
                            stroke_width=10,
                            width=90,
                            height=90
                        ),
                        # Active progress ring with rounded caps
                        ft.ProgressRing(
                            ref=progress_ref,
                            value=0.0,
                            color=color,
                            stroke_width=10,
                            stroke_cap=ft.StrokeCap.ROUND,
                            width=90,
                            height=90,
                            animate_rotation=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT)
                        ),
                        # Center content with value and label
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    "0%",
                                    ref=percentage_ref,
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ON_SURFACE,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.Text(
                                    "Load",
                                    size=11,
                                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                    text_align=ft.TextAlign.CENTER
                                )
                            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                            width=90,
                            height=90,
                            alignment=ft.alignment.center
                        )
                    ], width=90, height=90),
                    alignment=ft.alignment.center,
                    margin=ft.Margin(0, 12, 0, 8)
                ),

                # PHASE 4.2: Enhanced footer with trend indicator
                ft.Row([
                    ft.Text(
                        "Real-time",
                        size=11,
                        color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE)
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.TRENDING_UP,
                                size=12,
                                color=ft.Colors.with_opacity(0.6, color)
                            ),
                            ft.Text(
                                "Live",
                                size=10,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.with_opacity(0.6, color)
                            )
                        ], spacing=2)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=8, alignment=ft.MainAxisAlignment.START),

            # PHASE 4.2: Premium container with enhanced styling and interactions
            padding=18,
            border_radius=16,  # Larger radius for premium feel
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE)),
            width=200,
            height=170,  # Taller for circular gauge
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            on_hover=on_hover_change,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            )
        )

        # Attach additional refs for external updates
        container.status_icon_ref = status_icon_ref
        container.status_text_ref = status_text_ref
        container.percentage_ref = percentage_ref
        container.get_threshold_status = get_threshold_status

        return container

    def create_activity_item(client: str, action: str, status: str, timestamp: Optional[str] = None, is_last: bool = False) -> ft.Container:
        """PHASE 4.2: Premium Activity Timeline Item - Enhanced with connecting lines and micro-animations."""

        # Enhanced status configuration with icons and descriptions
        status_config = {
            'Complete': {
                'color': ft.Colors.GREEN,
                'icon': ft.Icons.CHECK_CIRCLE,
                'description': 'Successfully completed'
            },
            'In Progress': {
                'color': ft.Colors.BLUE,
                'icon': ft.Icons.SYNC,
                'description': 'Currently processing'
            },
            'Error': {
                'color': ft.Colors.RED,
                'icon': ft.Icons.ERROR,
                'description': 'Failed with error'
            },
            'Pending': {
                'color': ft.Colors.ORANGE,
                'icon': ft.Icons.PENDING,
                'description': 'Waiting to start'
            }
        }

        config = status_config.get(status, {
            'color': ft.Colors.GREY,
            'icon': ft.Icons.HELP_OUTLINE,
            'description': 'Unknown status'
        })

        # Enhanced timestamp formatting
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
                date_str = dt.strftime('%m/%d')
                relative_time = f"{(datetime.now() - dt.replace(tzinfo=None)).seconds // 60}m ago"
            except Exception:
                time_str = "Unknown"
                date_str = ""
                relative_time = ""
        else:
            now = datetime.now()
            time_str = now.strftime('%H:%M')
            date_str = now.strftime('%m/%d')
            relative_time = "Just now"

        # Track hover state for interactions
        is_hovered = False

        def on_hover_change(e):
            nonlocal is_hovered
            is_hovered = e.data == "true"
            # Subtle highlight on hover
            container.bgcolor = ft.Colors.with_opacity(0.04, config['color']) if is_hovered else ft.Colors.TRANSPARENT
            container.update()

        # PHASE 4.2: Professional timeline item design
        container = ft.Container(
            content=ft.Row([
                # Timeline indicator column
                ft.Container(
                    content=ft.Column([
                        # Status icon with enhanced design
                        ft.Container(
                            content=ft.Icon(
                                config['icon'],
                                size=18,
                                color=ft.Colors.WHITE
                            ),
                            width=32,
                            height=32,
                            bgcolor=config['color'],
                            border_radius=16,
                            alignment=ft.alignment.center,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=4,
                                color=ft.Colors.with_opacity(0.3, config['color']),
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        # Connecting line (except for last item)
                        ft.Container() if is_last else ft.Container(
                                                    width=2,
                                                    height=0 if is_last else 40,
                                                    bgcolor=ft.Colors.with_opacity(0.2, config['color']),
                                                    margin=ft.Margin(15, 4, 15, 0)
                                                )
                    ], spacing=0),
                    width=60
                ),

                # Content area with enhanced information hierarchy
                ft.Expanded(
                    child=ft.Column([
                        # Primary content row
                        ft.Row([
                            ft.Column([
                                # Client name with emphasis
                                ft.Text(
                                    client,
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.ON_SURFACE
                                ),
                                # Action description
                                ft.Text(
                                    action,
                                    size=13,
                                    color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE),
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                )
                            ], spacing=2, expand=True),

                            # Time and status information
                            ft.Column([
                                ft.Text(
                                    time_str,
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.ON_SURFACE,
                                    text_align=ft.TextAlign.RIGHT
                                ),
                                ft.Text(
                                    relative_time,
                                    size=10,
                                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                    text_align=ft.TextAlign.RIGHT
                                )
                            ], spacing=1, alignment=ft.CrossAxisAlignment.END)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        # Status badge with enhanced design
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    width=4,
                                    height=4,
                                    bgcolor=config['color'],
                                    border_radius=2
                                ),
                                ft.Text(
                                    status,
                                    size=11,
                                    weight=ft.FontWeight.W_500,
                                    color=config['color']
                                ),
                                ft.Text(
                                    f"• {config['description']}",
                                    size=10,
                                    color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                                    italic=True
                                )
                            ], spacing=6),
                            margin=ft.Margin(0, 4, 0, 0)
                        )
                    ], spacing=4, alignment=ft.CrossAxisAlignment.START)
                )
            ], spacing=0),

            # PHASE 4.2: Enhanced container with hover interactions
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=8,
            bgcolor=ft.Colors.TRANSPARENT,
            on_hover=on_hover_change,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            margin=ft.Margin(0, 0, 0, 4)
        )

        return container

    # === UI LAYOUT CONSTRUCTION ===

    # Enhanced header with status indicators
    header = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Text(
                    "SERVER DASHBOARD",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                ft.Icon(
                    ft.Icons.CLOUD_OFF,
                    ref=status_indicator_ref,
                    color=ft.Colors.RED,
                    size=20
                ),
            ], spacing=12),
            ft.Row([
                ft.Container(
                    content=ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ref=loading_indicator_ref,
                    visible=False
                ),
                ft.Text(
                    "Connecting...",
                    ref=last_update_ref,
                    size=12,
                    color=ft.Colors.ON_SURFACE
                ),
                ft.IconButton(
                    ft.Icons.REFRESH,
                    ref=refresh_button_ref,
                    on_click=lambda _: page.run_task(refresh_dashboard_data),
                    tooltip="Refresh dashboard data"
                )
            ], spacing=8)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=20,
        border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.PRIMARY_CONTAINER))
    )

    # PHASE 4.1: Interactive Desktop-Optimized Metrics Layout with Navigation
    # Using golden ratio (1.618) and desktop-first approach + clickable cards
    metrics_row = ft.ResponsiveRow([
        ft.Container(
            create_enhanced_metric_card(
                "Active Clients",
                clients_count_ref,
                ft.Icons.PEOPLE,
                ft.Colors.BLUE,
                on_click=navigate_to_clients,
                destination_hint="clients page"
            ),
            col={"lg": 3, "md": 6, "sm": 12},  # Desktop-first: 4 columns on large screens
            padding=ft.Padding(0, 0, 16, 0)  # Golden ratio spacing: 16px gaps
        ),
        ft.Container(
            create_enhanced_metric_card(
                "Total Files",
                files_count_ref,
                ft.Icons.FOLDER_COPY,
                ft.Colors.GREEN,
                on_click=navigate_to_files,
                destination_hint="files page"
            ),
            col={"lg": 3, "md": 6, "sm": 12},
            padding=ft.Padding(0, 0, 16, 0)
        ),
        ft.Container(
            create_enhanced_metric_card(
                "Storage Used",
                storage_value_ref,
                ft.Icons.STORAGE,
                ft.Colors.ORANGE,
                on_click=navigate_to_database,
                destination_hint="database page"
            ),
            col={"lg": 3, "md": 6, "sm": 12},
            padding=ft.Padding(0, 0, 16, 0)
        ),
        ft.Container(
            create_enhanced_metric_card(
                "System Uptime",
                uptime_value_ref,
                ft.Icons.SCHEDULE,
                ft.Colors.PURPLE,
                on_click=navigate_to_analytics,
                destination_hint="analytics page"
            ),
            col={"lg": 3, "md": 6, "sm": 12},
            padding=ft.Padding(0, 0, 0, 0)  # No right padding on last item
        ),
    ], spacing=0)  # Use container padding instead of run_spacing for precise control

    # PHASE 4.2: Enhanced Performance Layout with Container References
    # Store container references for status updates
    storage_gauge_container = create_progress_indicator_card("Storage Usage", storage_progress_ref, ft.Colors.ORANGE)
    cpu_gauge_container = create_progress_indicator_card("CPU Performance", cpu_progress_ref, ft.Colors.RED)
    memory_gauge_container = create_progress_indicator_card("Memory Usage", memory_progress_ref, ft.Colors.BLUE)

    performance_row = ft.ResponsiveRow([
        ft.Container(
            storage_gauge_container,
            col={"lg": 4, "md": 4, "sm": 12},  # Desktop-optimized: 3 columns
            padding=ft.Padding(0, 0, 16, 0)
        ),
        ft.Container(
            cpu_gauge_container,
            col={"lg": 4, "md": 4, "sm": 12},
            padding=ft.Padding(0, 0, 16, 0)
        ),
        ft.Container(
            memory_gauge_container,
            col={"lg": 4, "md": 4, "sm": 12},
            padding=ft.Padding(0, 0, 0, 0)
        ),
    ], spacing=0)

    # Enhanced activity stream
    activity_list = ft.ListView(
        ref=activity_list_ref,
        spacing=5,
        height=300,
        auto_scroll=True
    )

    activity_container = ft.Container(
        content=ft.Column([
            ft.Text("Recent Activity", size=18, weight=ft.FontWeight.BOLD),
            activity_list
        ], spacing=10),
        padding=20,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE
    )

    # PHASE 2: Premium Desktop Container with Golden Ratio Vertical Hierarchy
    dashboard_container = ft.Column([
        header,

        # Golden ratio spacing: 26px (16 * 1.618) for major sections
        ft.Container(height=26),

        # System Metrics Section with enhanced typography hierarchy
        ft.Container(
            ft.Text("System Metrics", size=24, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
            padding=ft.Padding(0, 0, 0, 16)  # 16px bottom spacing
        ),
        metrics_row,

        # Golden ratio spacing between major sections
        ft.Container(height=26),

        # Performance Section
        ft.Container(
            ft.Text("Performance Monitoring", size=24, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
            padding=ft.Padding(0, 0, 0, 16)
        ),
        performance_row,

        # Golden ratio spacing
        ft.Container(height=26),

        # Activity Section with enhanced styling
        activity_container

    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)  # Use explicit spacing instead of automatic

    # === LIFECYCLE METHODS ===

    def setup_subscriptions():
        """Initialize dashboard with background polling."""
        nonlocal _background_task

        logger.info("Dashboard setup_subscriptions called")
        logger.info(f"Server bridge available: {server_bridge is not None}")
        logger.info(f"Page available: {page is not None}")

        try:
            # FLET 0.28.3 BEST PRACTICES: Use page.run_task() for async operations
            logger.info("Setting up dashboard with proper Flet async patterns")

            # Set initial loading values
            update_status_indicator(False)  # Show disconnected initially
            if last_update_ref.current:
                last_update_ref.current.value = "Loading..."
                last_update_ref.current.update()

            # Use page.run_task() for initial data load (Flet 0.28.3 recommended pattern)
            page.run_task(refresh_dashboard_data)

            # Start background refresh with proper async pattern
            async def safe_background_refresh():
                """Background refresh with error handling and proper async patterns."""
                refresh_interval = 5  # 5 seconds
                while not _disposed:
                    try:
                        await asyncio.sleep(refresh_interval)
                        if not _disposed:
                            await refresh_dashboard_data()
                    except asyncio.CancelledError:
                        logger.info("Background refresh cancelled")
                        break
                    except Exception as e:
                        logger.error(f"Background refresh error: {e}")
                        await asyncio.sleep(refresh_interval * 2)  # Backoff on error

            # Start background task using Flet's recommended approach
            _background_task = page.run_task(safe_background_refresh)
            logger.info("Dashboard async tasks started using page.run_task()")

            # State manager integration
            if state_manager:
                try:
                    # Subscribe to relevant state changes
                    state_manager.subscribe('server_status', lambda data: page.run_task(refresh_dashboard_data))
                    logger.info("Subscribed to state manager updates")
                except Exception as e:
                    logger.warning(f"Failed to subscribe to state manager: {e}")
            else:
                logger.info("No state manager provided")

            logger.info("✅ Dashboard subscriptions initialized successfully")

        except Exception as e:
            logger.error(f"❌ Dashboard setup_subscriptions failed: {e}")
            raise

    def dispose():
        """Cleanup dashboard resources."""
        nonlocal _disposed, _background_task

        _disposed = True

        # Cancel background task
        if _background_task and not _background_task.done():
            _background_task.cancel()
            logger.info("Background refresh task cancelled")

        # Unsubscribe from state manager
        if state_manager:
            try:
                state_manager.unsubscribe_all()
                logger.info("Unsubscribed from state manager")
            except Exception as e:
                logger.warning(f"Failed to unsubscribe from state manager: {e}")

        logger.info("Dashboard disposed")

    return dashboard_container, dispose, setup_subscriptions