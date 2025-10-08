#!/usr/bin/env python3
"""
Analytics View - Data Visualization Dashboard
Shows backup statistics with charts and metrics.
"""

import asyncio
import os
import sys
from collections.abc import Coroutine
from contextlib import suppress
from typing import Any, Callable

import flet as ft

# Path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import Shared.utils.utf8_solution as _  # noqa: F401

# Import neumorphic and glassmorphic theme utilities
try:
    from theme import (
        PRONOUNCED_NEUMORPHIC_SHADOWS,
        MODERATE_NEUMORPHIC_SHADOWS,
        SUBTLE_NEUMORPHIC_SHADOWS,
        GLASS_STRONG,
        GLASS_MODERATE,
        GLASS_SUBTLE,
    )
except ImportError:
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []
    SUBTLE_NEUMORPHIC_SHADOWS = []
    GLASS_STRONG = {"blur": 15, "bg_opacity": 0.12, "border_opacity": 0.2}
    GLASS_MODERATE = {"blur": 12, "bg_opacity": 0.10, "border_opacity": 0.15}
    GLASS_SUBTLE = {"blur": 10, "bg_opacity": 0.08, "border_opacity": 0.12}

def create_analytics_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create analytics view with charts and metrics.

    Returns:
        tuple: (main_container, dispose_func, setup_subscriptions_async_func)
            - main_container: The main UI control for the analytics view
            - dispose_func: Cleanup function (synchronous)
            - setup_subscriptions_async_func: Async setup function for data loading
    """

    # State variables for live updates
    auto_refresh_enabled = True
    refresh_task = None

    # Initialize with placeholder data (will load async in setup_subscriptions)
    metrics = {'total_backups': 0, 'total_storage_gb': 0, 'success_rate': 0.0, 'avg_backup_size_gb': 0.0}
    backup_trend_data = []
    client_storage_data = []
    file_type_data = []

    # UI References for targeted updates
    total_backups_ref = ft.Ref[ft.Text]()
    total_storage_ref = ft.Ref[ft.Text]()
    success_rate_ref = ft.Ref[ft.Text]()
    avg_size_ref = ft.Ref[ft.Text]()
    trend_chart_ref = ft.Ref[ft.Container]()
    storage_chart_ref = ft.Ref[ft.Container]()
    file_type_chart_ref = ft.Ref[ft.Container]()
    last_update_ref = ft.Ref[ft.Text]()
    refresh_button_ref = ft.Ref[ft.IconButton]()
    metrics_row_ref = ft.Ref[ft.ResponsiveRow]()
    # Chart title refs
    trend_title_ref = ft.Ref[ft.Text]()
    file_type_title_ref = ft.Ref[ft.Text]()
    storage_title_ref = ft.Ref[ft.Text]()
    # Chart subtitle refs (e.g., "Sample data" or "No data")
    trend_subtitle_ref = ft.Ref[ft.Text]()
    file_type_subtitle_ref = ft.Ref[ft.Text]()
    storage_subtitle_ref = ft.Ref[ft.Text]()
    # Period selector state
    period_days = 7
    # Flags tracking whether chart data is sample/placeholder
    trend_is_sample = False
    storage_is_sample = False
    types_is_sample = False

    # Metric card helper with enhanced neumorphic styling
    def create_metric_card(title: str, value: str, icon: str, color: str, value_ref: Any | None = None, is_empty: bool = False) -> ft.Container:
        if is_empty:
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.GREY, size=24),
                            width=56,
                            height=56,
                            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREY),
                            border_radius=28,
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(title, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREY),
                    ], spacing=12),
                    ft.Text("No data", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY),
                    ft.Text("Server not connected", size=10, color=ft.Colors.GREY),
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                border_radius=16,
                bgcolor=ft.Colors.SURFACE,
                shadow=MODERATE_NEUMORPHIC_SHADOWS,
                expand=True,
            )

        # Enhanced glassmorphic icon container
        icon_container = ft.Container(
            content=ft.Icon(icon, color=color, size=28),
            width=56,
            height=56,
            bgcolor=ft.Colors.with_opacity(0.15, color),
            border_radius=28,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, color)),
        )

        # Value text with reference for live updates
        value_text = ft.Text(
            value,
            size=32,
            weight=ft.FontWeight.BOLD,
            color=color,
            ref=value_ref,
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    icon_container,
                    ft.Text(title, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                ], spacing=12),
                value_text,
            ], spacing=12),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            # Enhanced shadows and glow for metric cards
            shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,
            border=ft.border.all(1, ft.Colors.with_opacity(0.15, color)),  # Subtle colored border glow
            expand=True,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

    # Metric cards row with refs for live updates
    # Don't show empty state unless server_bridge is None
    metrics_empty = False  # We'll show real data even if zeros
    metrics_row = ft.ResponsiveRow([
        ft.Container(
            create_metric_card(
                "Total Backups",
                str(metrics['total_backups']),
                ft.Icons.BACKUP,
                ft.Colors.BLUE_400,
                total_backups_ref,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card(
                "Total Storage",
                f"{metrics['total_storage_gb']:.2f} GB",
                ft.Icons.STORAGE,
                ft.Colors.GREEN_400,
                total_storage_ref,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card(
                "Success Rate",
                f"{metrics['success_rate']:.1f}%",
                ft.Icons.CHECK_CIRCLE,
                ft.Colors.PURPLE_400,
                success_rate_ref,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card(
                "Avg Backup Size",
                f"{metrics['avg_backup_size_gb']:.2f} GB",
                ft.Icons.PIE_CHART,
                ft.Colors.AMBER_400,
                avg_size_ref,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
    ], spacing=16, ref=metrics_row_ref)

    # Backup trend chart with glassmorphic container
    backup_trend_bars = ft.Column([
        ft.Row([
            ft.Container(
                width=40,
                height=max(1, int(val * 3)) if backup_trend_data else 20,  # Scale height
                bgcolor=ft.Colors.BLUE_400,
                border_radius=4,
                tooltip=f"Day {i+1}: {val} backups" if backup_trend_data else "",
            )
            for i, val in enumerate(backup_trend_data[:7] if backup_trend_data else [10, 20, 15, 25, 30, 22, 28])
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ft.Row([
            ft.Text(f"{i+1}", size=10, color=ft.Colors.GREY)
            for i in range(7)
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
    ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER, ref=trend_chart_ref)

    # Storage by client chart with refs
    # Start with empty bars; will be populated when real data arrives
    storage_bars = ft.Column([], spacing=16, ref=storage_chart_ref)

    # File type distribution chart with refs
    colors = [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
    default_labels = ['Documents', 'Images', 'Videos', 'Other']
    default_values = [40, 30, 20, 10]

    # Simple circular progress indicators instead of PieChart
    file_type_viz = ft.Column([
        ft.Row([
            ft.Column([
                ft.ProgressRing(value=val/100, color=color, width=80, height=80, stroke_width=8),
                ft.Text(label, size=12, text_align=ft.TextAlign.CENTER),
                ft.Text(f"{val}%", size=10, color=ft.Colors.GREY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
            for (val, label), color in zip(
                zip(
                    file_type_data or default_values,
                    file_type_data and len(file_type_data) >= 4
                    and ['Custom1', 'Custom2', 'Custom3', 'Custom4']
                    or default_labels
                ),
                colors
            )
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True),
    ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER, ref=file_type_chart_ref)

    # Enhanced hover effect with dramatic neumorphic depth and scale
    def _panel_hover(e: ft.HoverEvent):
        # Dramatic hover interaction: scale, glow, and shadow lift
        with suppress(Exception):
            ctl = e.control
            if e.data == "true":
                # Hover state: dramatic lift with glow and scale
                ctl.border = ft.border.all(2, ft.Colors.with_opacity(0.35, ft.Colors.WHITE))
                ctl.shadow = PRONOUNCED_NEUMORPHIC_SHADOWS
                ctl.scale = 1.02
            else:
                # Base state: strong glassmorphic presence
                ctl.border = ft.border.all(2, ft.Colors.with_opacity(0.25, ft.Colors.WHITE))
                ctl.shadow = MODERATE_NEUMORPHIC_SHADOWS
                ctl.scale = 1.0
            safe_update(ctl)

    charts_row = ft.ResponsiveRow([
        # Backup trends - Enhanced Glassmorphic + Neumorphic container with blue accent
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Backup Trends", size=18, weight=ft.FontWeight.W_600, ref=trend_title_ref),
                    ft.Container(expand=True),
                    ft.Text("", size=11, color=ft.Colors.GREY, ref=trend_subtitle_ref),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=backup_trend_bars,  # Always mount the ref control
                    height=300,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.TRANSPARENT,
                ),
            ], spacing=12),
            padding=24,
            border_radius=20,
            bgcolor=ft.Colors.SURFACE,  # Force dark surface to remove gray wash
            # Removed gradient to avoid any gray/lightening effect; pure transparent panel
            border=ft.border.all(2, ft.Colors.with_opacity(0.25, ft.Colors.WHITE)),
            shadow=MODERATE_NEUMORPHIC_SHADOWS,  # Start with moderate for dramatic hover
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_hover=_panel_hover,
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            col={"sm": 12, "md": 12, "lg": 8}
        ),
        # File type distribution - Enhanced Glassmorphic container with purple accent
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("File Type Distribution", size=18, weight=ft.FontWeight.W_600, ref=file_type_title_ref),
                    ft.Container(expand=True),
                    ft.Text("", size=11, color=ft.Colors.GREY, ref=file_type_subtitle_ref),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=file_type_viz,  # Always mount the ref control
                    height=300,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.TRANSPARENT,
                ),
            ], spacing=12),
            padding=24,
            border_radius=20,
            bgcolor=ft.Colors.SURFACE,  # Force dark surface to remove gray wash
            # Removed gradient to avoid any gray/lightening effect; pure transparent panel
            border=ft.border.all(2, ft.Colors.with_opacity(0.25, ft.Colors.WHITE)),
            shadow=MODERATE_NEUMORPHIC_SHADOWS,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_hover=_panel_hover,
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            col={"sm": 12, "md": 12, "lg": 4}
        ),
    ], spacing=16)

    # Storage by client - Enhanced Glassmorphic container with green accent
    storage_row = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Storage by Client", size=18, weight=ft.FontWeight.W_600, ref=storage_title_ref),
                ft.Container(expand=True),
                ft.Text("", size=11, color=ft.Colors.GREY, ref=storage_subtitle_ref),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(
                content=storage_bars,  # Always mount the ref control
                height=300,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.TRANSPARENT,
            ),
        ], spacing=12),
        padding=24,
        border_radius=20,
    bgcolor=ft.Colors.SURFACE,  # Force dark surface to remove gray wash
        # Removed gradient to avoid any gray/lightening effect; pure transparent panel
        border=ft.border.all(2, ft.Colors.with_opacity(0.25, ft.Colors.WHITE)),
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        on_hover=_panel_hover,
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
    )

    # Auto-refresh toggle handler
    def toggle_auto_refresh(e):
        """Toggle auto-refresh on/off."""
        nonlocal auto_refresh_enabled
        auto_refresh_enabled = not auto_refresh_enabled

        if refresh_button_ref.current:
            refresh_button_ref.current.icon = (
                ft.Icons.PAUSE_CIRCLE if auto_refresh_enabled else ft.Icons.PLAY_CIRCLE
            )
            refresh_button_ref.current.tooltip = (
                "Pause auto-refresh" if auto_refresh_enabled else "Resume auto-refresh"
            )
            safe_update(refresh_button_ref.current)

    # Last update timestamp
    last_update_text = ft.Text(
        "Not updated yet",
        size=12,
        color=ft.Colors.OUTLINE,
        ref=last_update_ref,
    )

    # Auto-refresh buttons
    refresh_button = ft.IconButton(
        icon=ft.Icons.PAUSE_CIRCLE,
        tooltip="Pause auto-refresh (updates every 10s)",
        on_click=toggle_auto_refresh,
        ref=refresh_button_ref,
    )

    refresh_now_ref = ft.Ref[ft.IconButton]()

    async def refresh_now_click(e):
        # Directly await reload to avoid un-awaited coroutine warnings
        await load_analytics_data_async()

    refresh_now_button = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Refresh now",
        on_click=refresh_now_click,
        ref=refresh_now_ref,
    )

    # Time period selector
    async def on_period_change(e: ft.ControlEvent):
        nonlocal period_days
        mapping = {"7d": 7, "30d": 30, "90d": 90, "all": -1}
        try:
            sel = list(e.control.selected)[0] if e.control.selected else "7d"
            period_days = mapping.get(sel, 7)
        except Exception:
            period_days = 7
        # Trigger refresh (server currently ignores period, but UI stays responsive)
        await load_analytics_data_async()

    period_selector = ft.Row([
        ft.Text("Time Period:", size=14, weight=ft.FontWeight.W_500),
        ft.SegmentedButton(
            segments=[
                ft.Segment(value="7d", label=ft.Text("7 Days")),
                ft.Segment(value="30d", label=ft.Text("30 Days")),
                ft.Segment(value="90d", label=ft.Text("90 Days")),
                ft.Segment(value="all", label=ft.Text("All Time")),
            ],
            selected={"7d"},
            on_change=on_period_change,
        ),
    ], spacing=12)

    # Main content
    content = ft.Column([
        # Header with auto-refresh controls
        ft.Row([
            ft.Text("Analytics Dashboard", size=28, weight=ft.FontWeight.BOLD),
            ft.Row([
                last_update_text,
                refresh_button,
                refresh_now_button,
                period_selector,
            ], spacing=12),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),

        # Metrics
        metrics_row,

        # Charts
        charts_row,

        # Storage
        storage_row,
    ], spacing=20, expand=True, scroll="auto")

    main_container = ft.Container(
        content=content,
        padding=24,
        expand=True,
    )

    async def load_analytics_data_async() -> None:
        """Load analytics data from server and update UI controls (async version - NON-BLOCKING)."""
        nonlocal metrics, backup_trend_data, client_storage_data, file_type_data, period_days

        import logging
        logger = logging.getLogger(__name__)
        logger.info("🔵 [ANALYTICS] load_analytics_data_async STARTED")

        if not server_bridge:
            # No server bridge available, keep placeholder data
            logger.warning("🔴 [ANALYTICS] No server_bridge available!")
            return

        try:
            logger.info("🔵 [ANALYTICS] Calling server_bridge.get_analytics_data_async()...")
            # Fetch analytics data from server - use async method
            server_data = await server_bridge.get_analytics_data_async()
            logger.info(f"🔵 [ANALYTICS] Server response: {server_data}")

            if not isinstance(server_data, dict) or not server_data.get('success'):
                # Server call failed, keep placeholder data
                logger.warning(f"🔴 [ANALYTICS] Server call failed or returned non-success: {server_data}")
                return

            data = server_data.get('data', {})
            logger.info(f"🔵 [ANALYTICS] Extracted data: {data}")

            # Update metrics
            metrics = {
                'total_backups': data.get('total_backups', 0),
                'total_storage_gb': data.get('total_storage_gb', 0.0),
                'success_rate': data.get('success_rate', 0.0),
                'avg_backup_size_gb': data.get('avg_backup_size_gb', 0.0)
            }
            logger.info(f"🔵 [ANALYTICS] Updated metrics: {metrics}")

            # Update chart data
            backup_trend_data = data.get('backup_trend') or []
            client_storage_data = data.get('client_storage') or []
            file_type_data = data.get('file_type_distribution') or []
            trend_is_sample = False
            storage_is_sample = False
            types_is_sample = False

            # If server doesn't provide chart data, generate placeholder visuals
            if not backup_trend_data:
                # Generate sample trend based on total backups and selected period
                total_backups = metrics['total_backups']
                if total_backups > 0:
                    import random
                    period_len = 7 if period_days in (-1, 7) else (30 if period_days == 30 else (90 if period_days == 90 else 7))
                    base = max(1, total_backups // max(1, period_len))
                    backup_trend_data = [max(0, base + random.randint(-max(1, base//2), max(1, base//2))) for _ in range(period_len)]
                    trend_is_sample = True

            if not client_storage_data and metrics['total_storage_gb'] > 0:
                # Distribute storage across 4 mock clients
                total_storage = metrics['total_storage_gb']
                import random
                weights = [random.random() for _ in range(4)]
                total_weight = sum(weights)
                client_storage_data = [round((w/total_weight) * total_storage, 2) for w in weights]
                storage_is_sample = True

            if not file_type_data and metrics['total_backups'] > 0:
                # Mock file type distribution
                file_type_data = [40, 30, 20, 10]  # Documents, Images, Videos, Other
                types_is_sample = True

            logger.info(f"🔵 [ANALYTICS] Chart data - trends: {backup_trend_data}, storage: {client_storage_data}, types: {file_type_data}")

            # Update UI with targeted refs for better performance
            logger.info("🔵 [ANALYTICS] Calling update_ui_with_refs()...")
            await update_ui_with_refs()
            logger.info("🟢 [ANALYTICS] load_analytics_data_async COMPLETED SUCCESSFULLY")

        except Exception as ex:
            # Log error but don't crash the UI
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"🔴 [ANALYTICS] Failed to load analytics data: {ex}", exc_info=True)

    def safe_update(control):
        """Safely update a control only if it's attached to the page."""
        with suppress(AssertionError, AttributeError):
            if control and hasattr(control, 'page') and control.page:
                control.update()

    async def update_ui_with_refs() -> None:
        """Update UI using refs for targeted updates."""
        # Update metric cards using refs
        if trend_title_ref.current:
            trend_title_ref.current.value = "Backup Trends" if backup_trend_data else "No Backup Trends"
            safe_update(trend_title_ref.current)
        if file_type_title_ref.current:
            file_type_title_ref.current.value = "File Type Distribution" if file_type_data else "No File Type Distribution"
            safe_update(file_type_title_ref.current)
        if storage_title_ref.current:
            storage_title_ref.current.value = "Storage by Client" if client_storage_data else "No Client Storage Data"
            safe_update(storage_title_ref.current)

        if total_backups_ref.current:
            total_backups_ref.current.value = str(metrics['total_backups'])
            safe_update(total_backups_ref.current)

        if total_storage_ref.current:
            total_storage_ref.current.value = f"{metrics['total_storage_gb']:.2f} GB"
            safe_update(total_storage_ref.current)

        if success_rate_ref.current:
            success_rate_ref.current.value = f"{metrics['success_rate']:.1f}%"
            safe_update(success_rate_ref.current)

        if avg_size_ref.current:
            avg_size_ref.current.value = f"{metrics['avg_backup_size_gb']:.2f} GB"
            safe_update(avg_size_ref.current)

        # Update trend chart with improved bars
        if trend_chart_ref.current and backup_trend_data:
            # Show up to last 12 periods for readability
            last_count = min(12, len(backup_trend_data))
            data_slice = backup_trend_data[-last_count:]
            max_val = max(data_slice) if data_slice else 1
            new_bars = ft.Row([
                ft.Container(
                    width=24,
                    height=max(10, int((val / max_val) * 200)),
                    bgcolor=ft.Colors.BLUE_400,
                    border_radius=6,
                    tooltip=f"Day {len(backup_trend_data)-last_count + i + 1}: {val} backups",
                )
                for i, val in enumerate(data_slice)
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END)

            # Labels to match bars
            from datetime import datetime, timedelta
            # Build day-of-week labels ending today
            labels = []
            for i in range(last_count):
                dt = datetime.now() - timedelta(days=(last_count - 1 - i))
                labels.append(dt.strftime('%a'))
            new_labels = ft.Row([ft.Text(lbl, size=10, color=ft.Colors.GREY) for lbl in labels], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

            # Replace both bars (index 0) and labels (index 1)
            if len(trend_chart_ref.current.controls) >= 2:
                trend_chart_ref.current.controls[0] = new_bars
                trend_chart_ref.current.controls[1] = new_labels
            else:
                # Fallback: replace entire controls list
                trend_chart_ref.current.controls = [new_bars, new_labels]
            safe_update(trend_chart_ref.current)

        # Update storage chart
        if storage_chart_ref.current and client_storage_data:
            colors = [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
            # Prevent division by zero: ensure max_storage is never 0
            max_storage = max(client_storage_data[:4], default=0) or 1

            new_storage_bars = [
                ft.Row([
                    ft.Text(f"Client {i+1}", size=12, width=80),
                    ft.Container(
                        content=ft.ProgressBar(
                            value=val/max_storage,
                            color=colors[i % len(colors)],
                            bgcolor=ft.Colors.with_opacity(0.2, colors[i % len(colors)])
                        ),
                        expand=True,
                    ),
                    ft.Text(f"{val:.2f} GB", size=12, width=80, text_align=ft.TextAlign.RIGHT),
                ], spacing=12)
                for i, val in enumerate(client_storage_data[:4])
            ]

            storage_chart_ref.current.controls = new_storage_bars
            safe_update(storage_chart_ref.current)

        # Update file type chart
        if file_type_chart_ref.current and file_type_data:
            colors = [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
            labels = ['Documents', 'Images', 'Videos', 'Other']

            new_rings = ft.Row([
                ft.Column([
                    ft.ProgressRing(
                        value=val/100,
                        color=colors[i % len(colors)],
                        width=80,
                        height=80,
                        stroke_width=8
                    ),
                    ft.Text(labels[i], size=12, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{val}%", size=10, color=ft.Colors.GREY),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
                for i, val in enumerate(file_type_data[:4])
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True)

            file_type_chart_ref.current.controls[0] = new_rings
            safe_update(file_type_chart_ref.current)

        # Update subtitles and last refresh timestamp
        if trend_subtitle_ref.current:
            trend_subtitle_ref.current.value = "(sample)" if trend_is_sample else ("" if backup_trend_data else "(no data)")
            safe_update(trend_subtitle_ref.current)
        if file_type_subtitle_ref.current:
            file_type_subtitle_ref.current.value = "(sample)" if types_is_sample else ("" if file_type_data else "(no data)")
            safe_update(file_type_subtitle_ref.current)
        if storage_subtitle_ref.current:
            storage_subtitle_ref.current.value = "(sample)" if storage_is_sample else ("" if client_storage_data else "(no data)")
            safe_update(storage_subtitle_ref.current)

        # Update last refresh timestamp
        if last_update_ref.current:
            from datetime import datetime
            last_update_ref.current.value = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
            safe_update(last_update_ref.current)

    async def auto_refresh_loop():
        """Auto-refresh loop that runs every 10 seconds."""
        while True:
            await asyncio.sleep(10)  # Refresh every 10 seconds
            if auto_refresh_enabled:
                await load_analytics_data_async()

    def dispose():
        """Cleanup - cancel refresh task."""
        nonlocal refresh_task
        if refresh_task and not refresh_task.done():
            refresh_task.cancel()

    async def setup_subscriptions():
        """Setup - Initial data load and start auto-refresh loop."""
        nonlocal refresh_task

        import logging
        logger = logging.getLogger(__name__)
        logger.info("🟡 [ANALYTICS] setup_subscriptions STARTED")

        # CRITICAL: Delay to ensure view is fully attached to page AND AnimatedSwitcher transition completed
        # Total delay chain: main.py (250ms) + this (500ms) = 750ms total
        # This prevents "Control must be added to page first" errors
        await asyncio.sleep(0.5)  # Increased from 0.2 to 0.5 seconds for robust page attachment
        logger.info("🟡 [ANALYTICS] Delay completed, calling load_analytics_data_async...")

        # Initial data load
        await load_analytics_data_async()
        logger.info("🟡 [ANALYTICS] Initial data load completed")

        # Start auto-refresh loop (updates every 10 seconds)
        logger.info("🟡 [ANALYTICS] Starting auto-refresh loop...")
        refresh_task = asyncio.create_task(auto_refresh_loop())
        logger.info("🟢 [ANALYTICS] setup_subscriptions COMPLETED")

    return main_container, dispose, setup_subscriptions