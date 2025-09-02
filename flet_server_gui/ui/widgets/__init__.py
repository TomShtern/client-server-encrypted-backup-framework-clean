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



from .charts import (
    MetricThreshold,
    ChartSettings,
    EnhancedPerformanceCharts,
    EnhancedBarChart,
    EnhancedLineChart,
    EnhancedPieChart,
    create_performance_chart as create_enhanced_performance_charts,
    create_enhanced_bar_chart,
    create_enhanced_line_chart,
    create_enhanced_pie_chart,
    create_bar_chart,
    create_line_chart,
    create_pie_chart,
    format_metric_value,
    ChartType,
    ChartDataPoint,
    MetricType
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

# Enhanced components
from .enhanced_buttons import (
    ButtonVariant,
    ButtonSize,
    ButtonState,
    EnhancedButtonConfig,
    EnhancedButton,
    create_primary_button,
    create_secondary_button,
    create_outline_button,
    create_text_button,
    create_icon_button,
    create_fab_button
)

from .enhanced_cards import (
    CardVariant,
    CardSize,
    EnhancedCardConfig,
    EnhancedCard,
    StatCard,
    DataCard
)

from .enhanced_dialogs import (
    DialogType,
    DialogSize,
    DialogConfig,
    EnhancedDialog,
    EnhancedAlertDialog,
    ConfirmationDialog
)

# Enhanced chart imports now come from the consolidated charts.py
# The enhanced_charts.py components are now integrated into charts.py

from .enhanced_tables import (
    # Core table data structures (absorbed from unified_table_base.py)
    TableSize,
    SortDirection,
    FilterOperator,
    ColumnFilter,
    ColumnSort,
    EnhancedTableColumn,
    TableAction,
    TableConfig,
    
    # Main table class with all absorbed functionality
    EnhancedTable,
    
    # Factory functions for all table types (absorbed from specialized_tables.py)
    create_simple_table,
    create_client_table,
    create_file_table,
    create_database_table,
    create_enhanced_data_table,
    
    # Utility functions (absorbed functionality)
    get_file_statistics,
    
    # Test function
    test_enhanced_tables
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
    
    
    # Chart components (consolidated)
    'MetricThreshold',
    'ChartSettings',
    'EnhancedPerformanceCharts',
    'EnhancedBarChart',
    'EnhancedLineChart',
    'EnhancedPieChart',
    'create_enhanced_performance_charts',
    'create_enhanced_bar_chart',
    'create_enhanced_line_chart',
    'create_enhanced_pie_chart',
    'create_bar_chart',
    'create_line_chart',
    'create_pie_chart',
    'format_metric_value',
    'ChartType',
    'ChartDataPoint',
    'MetricType',
    
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
    'create_dashboard_widget',
    
    # Enhanced dialog components
    'DialogType',
    'DialogSize',
    'DialogConfig',
    'EnhancedDialog',
    'EnhancedAlertDialog',
    'ConfirmationDialog',
    
    # Enhanced button components
    'ButtonVariant',
    'ButtonSize',
    'ButtonState',
    'EnhancedButtonConfig',
    'EnhancedButton',
    'create_primary_button',
    'create_secondary_button',
    'create_outline_button',
    'create_text_button',
    'create_icon_button',
    'create_fab_button',
    
    # Enhanced card components
    'CardVariant',
    'CardSize',
    'EnhancedCardConfig',
    'EnhancedCard',
    'StatCard',
    'DataCard',
    
    # Enhanced chart components (now available from consolidated charts.py via separate imports)
    # 'ChartType', 'ChartSize', 'ChartDataPoint', 'ChartSeries', 
    # 'EnhancedChartConfig', 'EnhancedChart' - available via direct import from .charts
    
    # Enhanced table components (ALL table functionality consolidated)
    'TableSize',
    'SortDirection',
    'FilterOperator',
    'ColumnFilter',
    'ColumnSort',
    'EnhancedTableColumn',
    'TableAction',
    'TableConfig',
    'EnhancedTable',
    'create_simple_table',
    'create_client_table',
    'create_file_table',
    'create_database_table',
    'create_enhanced_data_table',
    'get_file_statistics',
    'test_enhanced_tables'
]