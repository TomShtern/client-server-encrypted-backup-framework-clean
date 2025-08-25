#!/usr/bin/env python3
"""
UI Widgets Package

Consolidated UI widget components for the Flet Server GUI:
- buttons.py: Button factory and configurations
- cards.py: Status and information display cards  
- tables.py: Advanced data tables with filtering/sorting
- charts.py: Performance monitoring charts
- file_preview.py: File preview components
- widgets.py: Dashboard widgets with enhanced interactions
"""

from .buttons import (
    ButtonConfig,
    ActionButtonFactory
)

from .cards import (
    ClientStatsCard,
    ServerStatusCard,
    ActivityLogCard,
    EnhancedStatsCard,
    DatabaseStatsCard,
    create_client_stats_card,
    create_server_status_card,
    create_activity_log_card,
    create_enhanced_stats_card,
    create_database_stats_card
)

from .tables import (
    SortDirection,
    FilterOperator,
    ColumnFilter,
    ColumnSort,
    TableColumn,
    TableAction,
    EnhancedDataTable,
    create_enhanced_data_table
)

from .charts import (
    MetricThreshold,
    ChartSettings,
    EnhancedPerformanceCharts,
    EnhancedBarChart,
    EnhancedLineChart,
    EnhancedPieChart,
    create_enhanced_performance_charts,
    create_bar_chart,
    create_line_chart,
    create_pie_chart
)

from .file_preview import (
    FilePreview,
    FilePreviewManager,
    create_file_preview,
    create_file_preview_manager
)

from .widgets import (
    WidgetSize,
    DashboardWidget,
    StatisticWidget,
    ActivityFeedWidget,
    create_stat_widget,
    create_activity_widget,
    create_dashboard_widget
)

__all__ = [
    # Button components
    'ButtonConfig',
    'ActionButtonFactory',
    
    # Card components
    'ClientStatsCard',
    'ServerStatusCard', 
    'ActivityLogCard',
    'EnhancedStatsCard',
    'DatabaseStatsCard',
    'create_client_stats_card',
    'create_server_status_card',
    'create_activity_log_card',
    'create_enhanced_stats_card',
    'create_database_stats_card',
    
    # Table components
    'SortDirection',
    'FilterOperator',
    'ColumnFilter',
    'ColumnSort',
    'TableColumn',
    'TableAction',
    'EnhancedDataTable',
    'create_enhanced_data_table',
    
    # Chart components
    'MetricThreshold',
    'ChartSettings',
    'EnhancedPerformanceCharts',
    'EnhancedBarChart',
    'EnhancedLineChart',
    'EnhancedPieChart',
    'create_enhanced_performance_charts',
    'create_bar_chart',
    'create_line_chart',
    'create_pie_chart',
    
    # File preview components
    'FilePreview',
    'FilePreviewManager',
    'create_file_preview',
    'create_file_preview_manager',
    
    # Widget components
    'WidgetSize',
    'DashboardWidget',
    'StatisticWidget',
    'ActivityFeedWidget',
    'create_stat_widget',
    'create_activity_widget',
    'create_dashboard_widget'
]