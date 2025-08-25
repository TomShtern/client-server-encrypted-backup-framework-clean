#!/usr/bin/env python3
"""
UI Widgets Package

Consolidated UI widget components for the Flet Server GUI:
- buttons.py: Button factory and configurations
- cards.py: Status and information display cards  
- tables.py: Advanced data tables with filtering/sorting
- charts.py: Performance monitoring charts
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
    create_client_stats_card,
    create_server_status_card,
    create_activity_log_card,
    create_enhanced_stats_card
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
    create_enhanced_performance_charts
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
    'create_client_stats_card',
    'create_server_status_card',
    'create_activity_log_card',
    'create_enhanced_stats_card',
    
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
    'create_enhanced_performance_charts'
]