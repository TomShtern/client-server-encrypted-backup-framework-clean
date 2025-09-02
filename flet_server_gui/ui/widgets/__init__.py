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

# New Flet-style components
from .buttons import (
    Button,
    FilledButton,
    OutlinedButton,
    TextButton,
    IconButton,
    FloatingActionButton,
    create_filled_button,
    create_outlined_button,
    create_text_button,
    create_icon_button,
    create_floating_action_button,
    create_primary_button,
    create_secondary_button
)

from .cards import (
    Card,
    StatisticCard,
    DataTableCard,
    create_basic_card,
    create_statistic_card,
    create_data_table_card,
    create_info_card,
    create_notification_card
)

from .dialogs import (
    Dialog,
    AlertDialog,
    ConfirmDialog,
    create_info_dialog,
    create_success_dialog,
    create_warning_dialog,
    create_error_dialog,
    create_confirmation_dialog,
    create_progress_dialog,
    create_input_dialog
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
    'Button',
    'FilledButton',
    'OutlinedButton',
    'TextButton',
    'IconButton',
    'FloatingActionButton',
    'create_filled_button',
    'create_outlined_button',
    'create_text_button',
    'create_icon_button',
    'create_floating_action_button',
    'create_primary_button',
    'create_secondary_button',
    
    # Card components
    'Card',
    'StatisticCard',
    'DataTableCard',
    'create_basic_card',
    'create_statistic_card',
    'create_data_table_card',
    'create_info_card',
    'create_notification_card',
    
    # Dialog components
    'Dialog',
    'AlertDialog',
    'ConfirmDialog',
    'create_info_dialog',
    'create_success_dialog',
    'create_warning_dialog',
    'create_error_dialog',
    'create_confirmation_dialog',
    'create_progress_dialog',
    'create_input_dialog',
    
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