#!/usr/bin/env python3
"""
Purpose: Analytics & charts view
Logic: Data aggregation and metrics calculation
UI: Performance charts, statistics, and analytical displays
"""

import flet as ft

# Existing imports
from flet_server_gui.core.server_operations import ServerOperations
from flet_server_gui.components.base_component import BaseComponent

# Enhanced components imports
from flet_server_gui.ui.widgets import (
    EnhancedButton,
    EnhancedCard,
    EnhancedChart,
    EnhancedWidget,
    EnhancedButtonConfig,
    ButtonVariant,
    CardVariant,
    ChartType,
    WidgetSize,
    WidgetType
)

# Layout fixes imports
from flet_server_gui.ui.layouts.responsive_fixes import ResponsiveLayoutFixes
# Unified theme system - consolidated theme functionality
from flet_server_gui.ui.unified_theme_system import ThemeConsistencyManager, apply_theme_consistency, TOKENS


class AnalyticsView(BaseComponent):
    def __init__(self, page: ft.Page, server_bridge=None, dialog_system=None, toast_manager=None):
        # Initialize parent BaseComponent
        super().__init__(page, dialog_system, toast_manager)
        
        # Initialize theme consistency manager
        self.theme_manager = ThemeConsistencyManager(page)
        
        self.page = page
        self.server_bridge = server_bridge
        self.server_ops = ServerOperations(server_bridge) if server_bridge else None
        self.controls = []
        
        # Initialize the enhanced performance charts
        self.performance_charts = None
        if server_bridge:
            from flet_server_gui.ui.widgets.charts import EnhancedPerformanceCharts
            self.performance_charts = EnhancedPerformanceCharts(server_bridge, page)
        
        print("[INFO] AnalyticsView initialized with real performance monitoring")
        
    def build(self):
        """Build the analytics view with real performance monitoring"""
        # Header with enhanced styling - Apply responsive layout fixes
        header = ft.Row([
            ft.Icon(ft.Icons.AUTO_GRAPH, size=28),
            ft.Text("Analytics & Performance", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh Data",
                on_click=self._refresh_analytics
            )
        ], spacing=12, alignment=ft.MainAxisAlignment.START)
        
        # Apply hitbox fixes to the refresh button
        if len(header.controls) > 3 and isinstance(header.controls[3], ft.IconButton):
            header.controls[3] = ResponsiveLayoutFixes.fix_button_hitbox(header.controls[3])
        
        # Build content based on availability of performance charts
        if self.performance_charts:
            # Use the enhanced performance monitoring system
            content = ft.Column([
                header,
                ft.Divider(),
                
                # Real-time performance monitoring dashboard
                self.performance_charts.build(),
                
                # Additional analytics sections
                self._build_system_summary(),
                self._build_historical_trends()
                
            ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        else:
            # Fallback content when server bridge is not available
            content = ft.Column([
                header,
                ft.Divider(),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.WARNING_AMBER, size=48, color=TOKENS['secondary']),
                            ft.Text("Server Connection Required", style=ft.TextThemeStyle.HEADLINE_SMALL),
                            ft.Text("Analytics requires an active server connection to display real-time performance data.",
                                   style=ft.TextThemeStyle.BODY_MEDIUM, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                text="Check Connection",
                                icon=ft.Icons.REFRESH,
                                on_click=self._check_connection
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                        padding=40,
                        alignment=ft.alignment.center
                    )
                ),
                # Show basic system info even without server bridge
                self._build_basic_system_info()
            ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Apply responsive layout fixes
        content = ResponsiveLayoutFixes.create_clipping_safe_container(
            content
        )
        
        container = ft.Container(
            content=content,
            padding=20,
            expand=True
        )
        
        # Apply windowed mode compatibility
        main_container = ResponsiveLayoutFixes.create_windowed_layout_fix(container)
        
        # Apply theme consistency
        apply_theme_consistency(self.page)
        
        # Schedule chart initialization after the container is added to the page
        if self.performance_charts:
            # Use a small delay to ensure the charts are mounted
            import asyncio
            async def delayed_init():
                await asyncio.sleep(0.1)
                self.initialize_charts()
            
            if hasattr(self.page, 'run_task'):
                self.page.run_task(delayed_init)
        
        return main_container
        
    def update_data(self):
        """Update analytics data with real implementations"""
        if self.performance_charts:
            # The performance charts handle their own real-time updates
            print("[INFO] Analytics data updating via performance charts")
        elif self.server_ops:
            # Fallback data update without charts
            try:
                metrics = self.server_ops.get_system_metrics()
                print(f"[INFO] Analytics data updated: CPU {metrics.get('cpu_percent', 0):.1f}%")
            except Exception as e:
                print(f"[WARNING] Failed to update analytics data: {e}")
        else:
            print("[WARNING] No server connection available for analytics updates")
    
    def _build_system_summary(self) -> ft.Container:
        """Build system summary section"""
        return ft.Container(
            content=ft.Column([
                ft.Text("System Summary", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.Text("Real-time system performance monitoring with threshold alerts and interactive charts.",
                       style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=TOKENS['secondary'], size=16),
                        ft.Text("Enhanced monitoring active", style=ft.TextThemeStyle.BODY_SMALL)
                    ], spacing=8),
                    padding=ft.padding.only(top=8)
                )
            ], spacing=8),
            padding=16,
            border_radius=8,
            # Let theme handle background color automatically
        )
    
    def _build_historical_trends(self) -> ft.Container:
        """Build historical trends section"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Historical Trends", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.Text("Performance data is collected and stored for trend analysis.",
                       style=ft.TextThemeStyle.BODY_MEDIUM, color=TOKENS['outline']),
                ft.Row([
                    self._create_trend_stat("Peak CPU", "--", ft.Icons.TRENDING_UP, TOKENS['primary']),
                    self._create_trend_stat("Avg Memory", "--", ft.Icons.MEMORY, TOKENS['secondary']),
                    self._create_trend_stat("Max Network", "--", ft.Icons.NETWORK_CHECK, TOKENS['primary'])
                ], spacing=16)
            ], spacing=12),
            padding=16,
            border_radius=8,
            # Let theme handle background color automatically,
            margin=ft.margin.only(top=16)
        )
    
    def _create_trend_stat(self, label: str, value: str, icon, color) -> ft.Container:
        """Create a trend statistic display"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=20),
                ft.Text(label, style=ft.TextThemeStyle.LABEL_SMALL),
                ft.Text(value, style=ft.TextThemeStyle.BODY_MEDIUM, weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=12,
            border_radius=6,
            expand=True
        )
    
    def _build_basic_system_info(self) -> ft.Container:
        """Build basic system info when server bridge is not available"""
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            memory_total = psutil.virtual_memory().total // (1024**3)  # GB
            
            info_items = [
                f"CPU Cores: {cpu_count}",
                f"Total Memory: {memory_total} GB",
                f"Platform: {psutil.os.name}"
            ]
        except Exception:
            info_items = ["System information unavailable"]
        
        return ft.Container(
            content=ft.Column([
                ft.Text("System Information", style=ft.TextThemeStyle.TITLE_MEDIUM, weight=ft.FontWeight.BOLD),
                *[ft.Text(f"ג€¢ {item}", style=ft.TextThemeStyle.BODY_MEDIUM) for item in info_items]
            ], spacing=8),
            padding=16,
            border_radius=8,
            # Let theme handle border color automatically,
            margin=ft.margin.only(top=16)
        )
    
    def _refresh_analytics(self, e):
        """Refresh analytics data"""
        print("[INFO] Refreshing analytics data...")
        self.update_data()
        if self.performance_charts:
            # Trigger a refresh of the performance charts
            pass
    
    def _check_connection(self, e):
        """Check server connection status"""
        if self.server_bridge:
            print("[INFO] Server bridge is available")
        else:
            print("[WARNING] No server bridge connection")
    
    def initialize_charts(self):
        """Initialize charts after they are added to the page"""
        if self.performance_charts:
            self.performance_charts.initialize_updates()
