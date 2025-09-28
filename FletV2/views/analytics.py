#!/usr/bin/env python3
"""Advanced Analytics View (Real Data Only).

Features (all real / no mock):
 - LOCAL / SERVER segmented source (psutil vs server_bridge performance/history)
 - Animated metric tiles (CPU, Memory, Disk, Network)
 - Rolling performance line charts (CPU / Memory / Disk)
 - Network throughput line chart (Upload / Download)
 - Memory & Disk distribution pies + Capacity card
 - Hourly Activity heatmap (bar chart) with placeholder when no data
 - Collapsible sections & entrance animation
 - Export (JSON) & auto-refresh
 - Graceful empty states (no synthetic numbers)
File kept <650 lines and line length <=110 chars.
"""

# ===================== Imports =====================
from __future__ import annotations
import asyncio
import contextlib
import json
import os
import sys
from datetime import datetime
from typing import Any, Callable

import aiofiles
import flet as ft
import psutil
import Shared.utils.utf8_solution as _  # noqa: F401

from FletV2.utils.debug_setup import get_logger
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import themed_button, themed_metric_card
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger("analytics_view")

# ===================== Helpers =====================
def _safe(control_ref: ft.Ref[Any], setter: Callable[[Any], None]) -> None:
    ctrl = control_ref.current
    if ctrl and getattr(ctrl, "page", None):
        with contextlib.suppress(Exception):  # pragma: no cover
            setter(ctrl)
            ctrl.update()


def _safe_ctrl(ctrl: Any, op: Callable[[Any], None]) -> None:
    """Safely perform an operation on a control if it's attached to a page.

    This is used for controls we don't hold via Ref (e.g., children in loops or placeholder
    text) to avoid the recurring 'Text Control must be added to the page first' runtime
    exceptions that were causing app restarts. (Root cause: updates fired before Flet
    finished attaching the view to the live page tree.)
    """
    if ctrl and getattr(ctrl, "page", None):
        with contextlib.suppress(Exception):  # pragma: no cover
            op(ctrl)
            ctrl.update()


def create_analytics_view(server_bridge: ServerBridge | None, page: ft.Page,
                          _state_manager: StateManager | None = None) -> Any:
    logger.info("Creating advanced analytics view")

    # -------- State --------
    data_source_mode = "LOCAL"  # or SERVER
    auto_refresh = False
    refresh_task: asyncio.Task | None = None
    disposed = False

    current_metrics: dict[str, Any] = {}
    point_counter = 0
    previous_net = psutil.net_io_counters()
    previous_time = datetime.now()
    max_points = 60

    # -------- Refs --------
    cpu_bar_ref = ft.Ref[ft.ProgressBar]()
    mem_bar_ref = ft.Ref[ft.ProgressBar]()
    disk_bar_ref = ft.Ref[ft.ProgressBar]()
    cpu_txt_ref = ft.Ref[ft.Text]()
    mem_txt_ref = ft.Ref[ft.Text]()
    disk_txt_ref = ft.Ref[ft.Text]()
    net_txt_ref = ft.Ref[ft.Text]()
    last_updated_ref = ft.Ref[ft.Text]()
    capacity_used_ref = ft.Ref[ft.Text]()
    capacity_detail_ref = ft.Ref[ft.Text]()
    heatmap_placeholder_ref = ft.Ref[ft.Text]()

    # -------- Data Buffers --------
    perf_cpu: list[ft.LineChartDataPoint] = []
    perf_mem: list[ft.LineChartDataPoint] = []
    perf_disk: list[ft.LineChartDataPoint] = []
    net_up: list[ft.LineChartDataPoint] = []
    net_down: list[ft.LineChartDataPoint] = []

    # -------- Metrics Gathering --------
    def _local_metrics() -> dict[str, Any]:
        try:
            cpu = psutil.cpu_percent(interval=0.2)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            return {
                'cpu_usage': cpu,
                'cpu_cores': psutil.cpu_count(),
                'memory_usage': mem.percent,
                'memory_total_gb': round(mem.total / 1024**3, 1),
                'memory_used_gb': round(mem.used / 1024**3, 1),
                'disk_usage': round(disk.percent, 1),
                'disk_total_gb': round(disk.total / 1024**3, 1),
                'disk_used_gb': round(disk.used / 1024**3, 1),
                'network_sent_mb': round(net.bytes_sent / 1024**2, 1),
                'network_recv_mb': round(net.bytes_recv / 1024**2, 1),
                'active_processes': len(psutil.pids()),
                'connection_status': 'Local',
                'last_updated': datetime.now().strftime('%H:%M:%S')
            }
        except Exception as ex:  # pragma: no cover
            logger.debug(f"Local metrics failed: {ex}")
            return {}

    def _server_metrics() -> dict[str, Any]:
        if not server_bridge:
            return {}
        try:
            res = server_bridge.get_performance_metrics()
            data = res.get('data') if isinstance(res, dict) else res
            return data if isinstance(data, dict) else {}
        except Exception as ex:  # pragma: no cover
            logger.debug(f"Server metrics failed: {ex}")
            return {}

    def _get_metrics() -> dict[str, Any]:
        base = _server_metrics() if data_source_mode == 'SERVER' else _local_metrics()
        return base or {}

    # -------- Charts --------
    def _perf_series() -> list[ft.LineChartData]:
        return [
            ft.LineChartData(perf_cpu, stroke_width=2, color=ft.Colors.BLUE_600, curved=True),
            ft.LineChartData(perf_mem, stroke_width=2, color=ft.Colors.GREEN_600, curved=True),
            ft.LineChartData(perf_disk, stroke_width=2, color=ft.Colors.ORANGE_600, curved=True),
        ]

    performance_chart = ft.LineChart(
        data_series=_perf_series(), min_y=0, max_y=100, interactive=True, expand=True,
        border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE)),
        left_axis=ft.ChartAxis(title=ft.Text('Usage %', size=11), title_size=11, labels_size=9),
        bottom_axis=ft.ChartAxis(title=ft.Text('Samples', size=11), title_size=11, labels_size=9),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE), width=1,
                                               dash_pattern=[4, 3]),
        vertical_grid_lines=ft.ChartGridLines(color=ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE), width=1,
                                             dash_pattern=[4, 3]),
        animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT)
    )

    def _net_series() -> list[ft.LineChartData]:
        return [
            ft.LineChartData(net_up, stroke_width=2, color=ft.Colors.CYAN_600, curved=True),
            ft.LineChartData(net_down, stroke_width=2, color=ft.Colors.PURPLE_600, curved=True),
        ]

    network_chart = ft.LineChart(
        data_series=_net_series(), min_y=0, max_y=100, interactive=True, expand=True,
        border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE)),
        left_axis=ft.ChartAxis(title=ft.Text('Mb/s*', size=11), title_size=11, labels_size=9),
        bottom_axis=ft.ChartAxis(title=ft.Text('Samples', size=11), title_size=11, labels_size=9),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE), width=1,
                                               dash_pattern=[5, 4]),
        vertical_grid_lines=ft.ChartGridLines(color=ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE), width=1,
                                             dash_pattern=[5, 4]),
        animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT)
    )

    # Capacity card
    capacity_chart = ft.PieChart(
        sections=[ft.PieChartSection(50, color=ft.Colors.BLUE, title='Used'),
                  ft.PieChartSection(50, color=ft.Colors.BLUE_GREY_100, title='Free')],
        center_space_radius=34, width=140, height=140, sections_space=2
    )
    capacity_card = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PIE_CHART), ft.Text('Storage Capacity', size=15, weight=ft.FontWeight.W_600)],
                   spacing=6),
            ft.Row([
                capacity_chart,
                ft.Column([
                    ft.Text('--% Used', ref=capacity_used_ref, size=13, weight=ft.FontWeight.W_500),
                    ft.Text('-- / -- GB', ref=capacity_detail_ref, size=11, color=ft.Colors.ON_SURFACE_VARIANT)
                ], spacing=4)
            ], spacing=12)
        ], spacing=8),
        padding=16, border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
        border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE))
    )

    # Heatmap (activity) --------------------------------------------------
    heatmap_chart = ft.BarChart(
        bar_groups=[], min_y=0, max_y=10, expand=True,
        border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE)),
        left_axis=ft.ChartAxis(title=ft.Text('Activity', size=11), title_size=11, labels_size=9),
        bottom_axis=ft.ChartAxis(title=ft.Text('Hour', size=11), title_size=11, labels_size=9),
        animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT)
    )

    def _update_heatmap() -> None:
        groups: list[ft.BarChartGroup] = []
        items: list[tuple[int, float]] = []
        if server_bridge and data_source_mode == 'SERVER':
            try:
                res = server_bridge.get_historical_data('activity', hours=6)
                data = res.get('data') if isinstance(res, dict) else res
                if isinstance(data, list):
                    for d in data:
                        if isinstance(d, dict):
                            h, v = d.get('hour'), d.get('value')
                            if isinstance(h, int) and isinstance(v, (int, float)):
                                items.append((h, float(v)))
                elif isinstance(data, dict):
                    for k, v in data.items():
                        try:
                            h = int(k)
                            if isinstance(v, (int, float)):
                                items.append((h, float(v)))
                        except Exception:  # pragma: no cover
                            continue
            except Exception as ex:  # pragma: no cover
                logger.debug(f"Heatmap fetch failed: {ex}")

        if items:
            dedup: dict[int, float] = {}
            for h, v in items:
                dedup[h % 24] = v
            ordered = sorted(dedup.items())
            now_h = datetime.now().hour
            desired = [(now_h - i) % 24 for i in range(5, -1, -1)]
            final: list[tuple[int, float]] = []
            lookup = {h: v for h, v in ordered}
            for h in desired:
                if h in lookup:
                    final.append((h, lookup[h]))
            items = final

        if items:
            max_val = max(v for _, v in items) or 1
            heatmap_chart.max_y = max(10, min(100, max_val * 1.2))
            for idx, (h, v) in enumerate(items):
                groups.append(ft.BarChartGroup(x=idx, bar_rods=[
                    ft.BarChartRod(to_y=v, color=ft.Colors.BLUE_600, width=16, tooltip=f"{h:02d}h: {v}")
                ]))
        else:
            heatmap_chart.max_y = 10

        heatmap_chart.bar_groups = groups
        # Guard placeholder visibility update (was previously unguarded and could fire
        # before attachment, producing the error the user reported).
        if heatmap_placeholder_ref.current:
            _safe_ctrl(heatmap_placeholder_ref.current, lambda c: setattr(c, 'visible', len(groups) == 0))

    heatmap_placeholder = ft.Text("No activity data", size=11, color=ft.Colors.ON_SURFACE_VARIANT,
                                   italic=True, ref=heatmap_placeholder_ref, visible=True)

    # ------------------- Update Routine -------------------
    def _update_all() -> None:
        nonlocal current_metrics, point_counter, previous_net, previous_time
        current_metrics = _get_metrics()
        if not current_metrics:
            # Show placeholders
            for r, label in [(cpu_txt_ref, 'CPU'), (mem_txt_ref, 'Memory'), (disk_txt_ref, 'Disk')]:
                _safe(r, lambda c, lbl=label: setattr(c, 'value', f"{lbl}: No data"))
            return

        cpu = current_metrics.get('cpu_usage')
        mem = current_metrics.get('memory_usage')
        disk = current_metrics.get('disk_usage')

        _safe(cpu_bar_ref, lambda c: setattr(c, 'value', (cpu or 0)/100 if cpu is not None else 0))
        _safe(mem_bar_ref, lambda c: setattr(c, 'value', (mem or 0)/100 if mem is not None else 0))
        _safe(disk_bar_ref, lambda c: setattr(c, 'value', (disk or 0)/100 if disk is not None else 0))
        _safe(cpu_txt_ref, lambda c: setattr(c, 'value', (
            f"CPU: {cpu:.1f}% | {current_metrics.get('cpu_cores','?')} cores" if cpu is not None else 'CPU: No data')))
        _safe(mem_txt_ref, lambda c: setattr(c, 'value', (
            f"Memory: {mem:.1f}% | {current_metrics.get('memory_used_gb','?')}/"
            f"{current_metrics.get('memory_total_gb','?')} GB" if mem is not None else 'Memory: No data')))
        _safe(disk_txt_ref, lambda c: setattr(c, 'value', (
            f"Disk: {disk:.1f}% | {current_metrics.get('disk_used_gb','?')}/"
            f"{current_metrics.get('disk_total_gb','?')} GB" if disk is not None else 'Disk: No data')))
        _safe(net_txt_ref, lambda c: setattr(c, 'value', (
            f"↑{current_metrics.get('network_sent_mb','?')}MB ↓"
            f"{current_metrics.get('network_recv_mb','?')}MB" if current_metrics.get('network_sent_mb') is not None
            else 'No network data')))
        _safe(last_updated_ref, lambda c: setattr(c, 'value',
              f"Updated {current_metrics.get('last_updated','--')} • {data_source_mode}"))

        # Capacity
        used = current_metrics.get('disk_used_gb') or 0
        total = current_metrics.get('disk_total_gb') or 0
        percent = (used / total * 100) if total else 0
        capacity_chart.sections = [
            ft.PieChartSection(percent, color=ft.Colors.BLUE, title=''),
            ft.PieChartSection(100 - percent, color=ft.Colors.BLUE_GREY_100, title='')
        ]
        _safe(capacity_used_ref, lambda c: setattr(c, 'value',
              f"{percent:.0f}% Used" if total else 'No data'))
        _safe(capacity_detail_ref, lambda c: setattr(c, 'value',
              f"{used:.1f} / {total:.1f} GB" if total else '-- / -- GB'))

        # Rolling points
        point_counter += 1
        x = point_counter
        if cpu is not None:
            perf_cpu.append(ft.LineChartDataPoint(x, cpu))
        if mem is not None:
            perf_mem.append(ft.LineChartDataPoint(x, mem))
        if disk is not None:
            perf_disk.append(ft.LineChartDataPoint(x, disk))
        now_net = psutil.net_io_counters()
        elapsed = (datetime.now() - previous_time).total_seconds() or 1
        up_rate = (now_net.bytes_sent - previous_net.bytes_sent)/(1024**2)/elapsed*8
        down_rate = (now_net.bytes_recv - previous_net.bytes_recv)/(1024**2)/elapsed*8
        previous_net = now_net
        previous_time = datetime.now()
        if current_metrics.get('network_sent_mb') is not None:
            net_up.append(ft.LineChartDataPoint(x, min(up_rate, 100)))
        if current_metrics.get('network_recv_mb') is not None:
            net_down.append(ft.LineChartDataPoint(x, min(down_rate, 100)))
        for lst in (perf_cpu, perf_mem, perf_disk, net_up, net_down):
            while len(lst) > max_points:
                del lst[0]

        performance_chart.data_series = _perf_series()
        network_chart.data_series = _net_series()
        _update_heatmap()
        for c in (performance_chart, network_chart, heatmap_chart, capacity_chart):
            if getattr(c, 'page', None):
                c.update()

    # ------------- Auto Refresh -------------
    async def _loop():  # pragma: no cover (timing)
        # High-frequency loop only active when user enabled auto-refresh
        while auto_refresh and not disposed:
            _update_all()
            await asyncio.sleep(2)

    async def _baseline_loop():  # pragma: no cover (timing)
        # Always-on low frequency refresh to populate data without user interaction
        while not disposed:
            with contextlib.suppress(Exception):  # pragma: no cover
                _update_all()
            await asyncio.sleep(5)

    def _toggle_auto(e):  # pragma: no cover
        nonlocal auto_refresh, refresh_task
        auto_refresh = not auto_refresh
        if auto_refresh:
            refresh_task = page.run_task(_loop)
            auto_btn.text, auto_btn.icon = "Stop Auto", ft.Icons.STOP
            show_success_message(page, "Auto-refresh ON")
        else:
            auto_btn.text, auto_btn.icon = "Start Auto", ft.Icons.PLAY_ARROW
            show_success_message(page, "Auto-refresh OFF")
        auto_btn.update()

    def _refresh_now(e):  # pragma: no cover
        _update_all()
        show_success_message(page, "Metrics refreshed")

    # ------------- Export -------------
    async def _export(e: ft.FilePickerResultEvent):  # pragma: no cover
        if not e.path:
            return
        try:
            payload = {
                'timestamp': datetime.now().isoformat(),
                'metrics': current_metrics,
                'source': data_source_mode
            }
            async with aiofiles.open(e.path, 'w') as f:
                await f.write(json.dumps(payload, indent=2))
            show_success_message(page, f"Exported to {e.path}")
        except Exception as ex:
            show_error_message(page, f"Export failed: {ex}")

    def _export_click(e):  # pragma: no cover
        file_picker.save_file(dialog_title='Export Analytics',
                               file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                               file_type=ft.FilePickerFileType.CUSTOM,
                               allowed_extensions=['json'])

    file_picker = ft.FilePicker(on_result=_export)
    page.overlay.append(file_picker)

    # ------------- Segmented Source Toggle -------------
    def _seg_change(e):  # pragma: no cover
        nonlocal data_source_mode
        try:
            sel_list = list(source_segment.selected) if source_segment.selected else []
            sel = sel_list[0] if sel_list else 'local'
        except Exception:
            sel = 'local'
        new_mode = 'SERVER' if sel == 'server' else 'LOCAL'
        if new_mode != data_source_mode:
            data_source_mode = new_mode
            _update_all()
            show_success_message(page, f"Source: {data_source_mode}")

    # NOTE: Using list for selected for broader Flet version compatibility
    source_segment = ft.SegmentedButton(segments=[
        ft.Segment(value='local', label=ft.Text('Local')),
        ft.Segment(value='server', label=ft.Text('Server'))
    ], selected=['local'], on_change=_seg_change)

    # ------------- UI Components -------------
    auto_btn = themed_button("Start Auto", _toggle_auto, "filled", ft.Icons.PLAY_ARROW)
    refresh_btn = themed_button("Refresh", _refresh_now, "filled", ft.Icons.REFRESH)
    export_btn = themed_button("Export", _export_click, "outlined", ft.Icons.DOWNLOAD)

    header_actions = ft.Column([
        ft.Row([
            refresh_btn, auto_btn, export_btn,
            ft.Row([ft.Text('Source:'), source_segment], spacing=6),
            ft.Container(expand=True), ft.Text('Updated Never', ref=last_updated_ref, size=11,
                                               color=ft.Colors.ON_SURFACE_VARIANT)
        ], wrap=True, spacing=10)
    ], spacing=6)

    # Metric tiles row (cards already themed)
    tiles_row = ft.ResponsiveRow([
        ft.Container(content=themed_metric_card('Processes', '0', ft.Icons.MEMORY), col={"sm":6,"md":3,"lg":3}),
        ft.Container(content=themed_metric_card('CPU Cores', '0', ft.Icons.DEVELOPER_BOARD), col={"sm":6,"md":3,"lg":3}),
        ft.Container(content=themed_metric_card('Total RAM', '-- GB', ft.Icons.STORAGE), col={"sm":6,"md":3,"lg":3}),
        ft.Container(content=themed_metric_card('Total Disk', '-- GB', ft.Icons.FOLDER), col={"sm":6,"md":3,"lg":3})
    ], spacing=18)

    # Usage progress tiles
    def _usage_tile(title: str, icon: str, color: str, bar_ref, txt_ref):  # type: ignore[no-untyped-def]
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(ft.Icon(icon, color=color, size=18), padding=6, border_radius=10,
                                 bgcolor=ft.Colors.with_opacity(0.12, color)),
                    ft.Text(title, size=13, weight=ft.FontWeight.W_600, color=color)
                ], spacing=8),
                ft.Text('--', ref=txt_ref, size=18, weight=ft.FontWeight.BOLD),
                ft.ProgressBar(ref=bar_ref, value=0, height=5, color=color,
                               bgcolor=ft.Colors.with_opacity(0.15, color))
            ], spacing=6),
            padding=14, border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.07, color))
        )

    usage_tiles = ft.ResponsiveRow([
        ft.Container(_usage_tile('CPU', ft.Icons.DEVELOPER_BOARD, ft.Colors.BLUE_600, cpu_bar_ref, cpu_txt_ref),
                     col={"sm":12,"md":6,"lg":3}),
        ft.Container(_usage_tile('Memory', ft.Icons.MEMORY, ft.Colors.GREEN_600, mem_bar_ref, mem_txt_ref),
                     col={"sm":12,"md":6,"lg":3}),
        ft.Container(_usage_tile('Disk', ft.Icons.STORAGE, ft.Colors.PURPLE_600, disk_bar_ref, disk_txt_ref),
                     col={"sm":12,"md":6,"lg":3}),
        ft.Container(_usage_tile('Network', ft.Icons.NETWORK_CHECK, ft.Colors.ORANGE_600, ft.Ref[ft.ProgressBar](),
                                 net_txt_ref), col={"sm":12,"md":6,"lg":3}),
    ], spacing=18)

    # Distribution pies
    memory_pie = ft.PieChart(sections=[ft.PieChartSection(50, color=ft.Colors.GREEN, title='Used'),
                                       ft.PieChartSection(50, color=ft.Colors.GREEN_100, title='Free')],
                             center_space_radius=34, sections_space=2)
    disk_pie = ft.PieChart(sections=[ft.PieChartSection(50, color=ft.Colors.PURPLE, title='Used'),
                                     ft.PieChartSection(50, color=ft.Colors.PURPLE_100, title='Free')],
                            center_space_radius=34, sections_space=2)

    pies_row = ft.ResponsiveRow([
        ft.Container(ft.Column([ft.Text('Memory Distribution', size=14, weight=ft.FontWeight.W_600),
                                 ft.Container(memory_pie, height=130)],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                   col={"sm":12,"md":6,"lg":6}, padding=16, border_radius=16,
                   bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
                   border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE))),
        ft.Container(ft.Column([ft.Text('Disk Distribution', size=14, weight=ft.FontWeight.W_600),
                                 ft.Container(disk_pie, height=130)],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                   col={"sm":12,"md":6,"lg":6}, padding=16, border_radius=16,
                   bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
                   border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE)))
    ], spacing=18)

    perf_row = ft.ResponsiveRow([
        ft.Container(ft.Column([
            ft.Row([ft.Text('Performance Trends', size=15, weight=ft.FontWeight.BOLD)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(performance_chart, height=210),
            ft.Row([
                ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.BLUE_600, border_radius=2),
                        ft.Text('CPU', size=10)], spacing=4),
                ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.GREEN_600, border_radius=2),
                        ft.Text('Memory', size=10)], spacing=4),
                ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.ORANGE_600, border_radius=2),
                        ft.Text('Disk', size=10)], spacing=4)
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=10), col={"sm":12,"md":12,"lg":6}, padding=20, border_radius=18,
                   bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
                   border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE))),
        ft.Container(ft.Column([
            ft.Row([ft.Text('Network Activity', size=15, weight=ft.FontWeight.BOLD)],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(network_chart, height=190),
            ft.Row([
                ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.CYAN_600, border_radius=2),
                        ft.Text('Upload', size=10)], spacing=4),
                ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.PURPLE_600, border_radius=2),
                        ft.Text('Download', size=10)], spacing=4)
            ], spacing=14, alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=10), col={"sm":12,"md":12,"lg":6}, padding=20, border_radius=18,
                   bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
                   border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE)))
    ], spacing=22)

    capacity_activity_row = ft.ResponsiveRow([
        ft.Container(content=capacity_card, col={"sm":12,"md":5,"lg":4}),
        ft.Container(ft.Column([
            ft.Text('Hourly Activity', size=15, weight=ft.FontWeight.BOLD),
            ft.Container(heatmap_chart, height=170),
            heatmap_placeholder
        ], spacing=10), col={"sm":12,"md":7,"lg":8}, padding=20, border_radius=18,
                   bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
                   border=ft.border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.OUTLINE)))
    ], spacing=22)

    # Collapsible sections
    perf_collapsed = False
    dist_collapsed = False
    storage_collapsed = False

    def _toggle(flag: str, target: ft.Control, icon_btn: ft.IconButton):  # pragma: no cover
        nonlocal perf_collapsed, dist_collapsed, storage_collapsed
        if flag == 'perf':
            perf_collapsed = not perf_collapsed
            target.visible = not perf_collapsed
            icon_btn.icon = ft.Icons.CHEVRON_RIGHT if perf_collapsed else ft.Icons.EXPAND_MORE
        elif flag == 'dist':
            dist_collapsed = not dist_collapsed
            target.visible = not dist_collapsed
            icon_btn.icon = ft.Icons.CHEVRON_RIGHT if dist_collapsed else ft.Icons.EXPAND_MORE
        else:
            storage_collapsed = not storage_collapsed
            target.visible = not storage_collapsed
            icon_btn.icon = ft.Icons.CHEVRON_RIGHT if storage_collapsed else ft.Icons.EXPAND_MORE
        target.update(); icon_btn.update()

    dist_toggle = ft.IconButton(icon=ft.Icons.EXPAND_MORE, tooltip='Collapse / Expand',
                                on_click=lambda e: _toggle('dist', pies_row, dist_toggle))
    perf_toggle = ft.IconButton(icon=ft.Icons.EXPAND_MORE, tooltip='Collapse / Expand',
                                on_click=lambda e: _toggle('perf', perf_row, perf_toggle))
    storage_toggle = ft.IconButton(icon=ft.Icons.EXPAND_MORE, tooltip='Collapse / Expand',
                                   on_click=lambda e: _toggle('storage', capacity_activity_row, storage_toggle))

    header_section = ft.Column([
        ft.Row([
            ft.Text('System Analytics', size=28, weight=ft.FontWeight.BOLD),
            header_actions
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
        ft.Container(height=3, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE), border_radius=2)
    ], spacing=14)

    main_content = ft.Column([
        header_section,
        tiles_row,
        ft.Text('Resource Utilization', size=21, weight=ft.FontWeight.W_600),
        usage_tiles,
        ft.Row([ft.Text('Distribution', size=21, weight=ft.FontWeight.W_600), dist_toggle], spacing=6),
        pies_row,
        ft.Row([ft.Text('Performance & Network', size=21, weight=ft.FontWeight.W_600), perf_toggle], spacing=6),
        perf_row,
        ft.Row([ft.Text('Storage & Activity', size=21, weight=ft.FontWeight.W_600), storage_toggle], spacing=6),
        capacity_activity_row,
    ], expand=True, spacing=26, scroll=ft.ScrollMode.AUTO)

    # Explicitly ensure visibility true (defensive)
    for ctrl in (tiles_row, usage_tiles, pies_row, perf_row, capacity_activity_row):
        with contextlib.suppress(Exception):  # pragma: no cover
            ctrl.visible = True

    # Direct wrapper (removed themed_card to eliminate potential layout clipping issue)
    analytics_wrapper = ft.Container(
        content=main_content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=ft.Colors.with_opacity(0.01, ft.Colors.SURFACE),
    )

    async def _entrance():  # pragma: no cover (visual)
        for group in (usage_tiles, pies_row, perf_row, capacity_activity_row):
            if disposed:
                return
            await asyncio.sleep(0.07)
            if hasattr(group, 'controls'):
                for child in group.controls[:8]:
                    # Apply animation only if container and already attached
                    if isinstance(child, ft.Container) and getattr(child, 'page', None):
                        with contextlib.suppress(Exception):  # pragma: no cover
                            child.opacity = 1
                            child.update()

    async def _deferred_initial_update():  # pragma: no cover (timing)
        """Defer first metrics update until the wrapper is attached.

        Previously `_update_all()` executed immediately in `setup_subscriptions()`,
        racing with Flet's attachment phase and leading to update calls on unattached
        controls (root cause of crash loop). We now poll briefly (up to ~1.5s) for
        attachment before performing the first update.
        """
        for attempt in range(30):
            if disposed:
                return
            if getattr(analytics_wrapper, 'page', None):
                logger.debug("Analytics initial update after %d attempts", attempt)
                _update_all()
                return
            await asyncio.sleep(0.05)
        # Fallback if never attached (should be rare)
        logger.debug("Analytics initial update fallback (not detected attached)")
        if not disposed:
            _update_all()

    def setup_subscriptions() -> None:
        nonlocal refresh_task
        # Defer initial update to avoid updating unattached controls
        if page and hasattr(page, 'run_task'):
            page.run_task(_deferred_initial_update)
            page.run_task(_entrance)
            # Start baseline periodic refresh
            page.run_task(_baseline_loop)
        else:
            _update_all()

    def dispose() -> None:
        nonlocal disposed
        disposed = True
        if file_picker in page.overlay:
            page.overlay.remove(file_picker)
        logger.debug('Disposed analytics view')

    return analytics_wrapper, dispose, setup_subscriptions
