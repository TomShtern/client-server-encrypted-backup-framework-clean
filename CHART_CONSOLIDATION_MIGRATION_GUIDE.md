# Chart Consolidation Migration Guide

## Overview

This guide shows how to migrate from the duplicated chart architecture to the new unified chart system. The consolidation eliminates code duplication while preserving all existing functionality.

## New Architecture

**Created Services:**
- `flet_server_gui/services/chart_types.py` - Unified type definitions
- `flet_server_gui/services/analytics_utilities.py` - Extracted utility functions  
- `flet_server_gui/services/chart_service.py` - Interface standardization layer

## Migration Steps

### 1. Update Import Statements

**Before (scattered imports):**
```python
# Old way - imports from multiple files
from flet_server_gui.ui.widgets.charts import ChartType, EnhancedPerformanceCharts
from flet_server_gui.ui.widgets.enhanced_charts import ChartSize, create_line_chart
from flet_server_gui.views.analytics import MetricType, format_metric_value
```

**After (unified imports):**
```python
# New way - consolidated imports
from flet_server_gui.services.chart_types import ChartType, ChartSize, ChartConfiguration
from flet_server_gui.services.analytics_utilities import MetricType, format_metric_value, MetricData
from flet_server_gui.services.chart_service import ChartService, create_line_chart, create_performance_chart
```

### 2. Update Chart Creation

**Before (inconsistent interfaces):**
```python
# Performance charts - complex setup
from flet_server_gui.ui.widgets.charts import EnhancedPerformanceCharts
performance_charts = EnhancedPerformanceCharts(server_bridge, page)
chart_control = performance_charts.build()

# Enhanced charts - different interface
from flet_server_gui.ui.widgets.enhanced_charts import create_line_chart
line_chart = create_line_chart(page, "Title", data, x_key="x", y_key="y")
chart_control = line_chart.get_control()
```

**After (unified interface):**
```python
# All charts use the same interface
from flet_server_gui.services.chart_service import ChartService

service = ChartService.get_instance()

# Performance chart
performance_chart = service.create_performance_chart(page, server_bridge, title="Performance")
performance_control = performance_chart.build()

# Line chart  
line_chart = service.create_enhanced_chart(page, ChartType.LINE, data, "Title")
line_control = line_chart.build()
```

### 3. Update Analytics View

**File:** `flet_server_gui/views/analytics.py`

**Before (utility functions mixed with view logic):**
```python
# Remove these utility functions from analytics.py - now in analytics_utilities.py
def format_metric_value(value: float, unit: str, precision: int = 2) -> str:
def calculate_time_boundaries(time_range: AnalyticsTimeRange) -> Tuple[datetime, datetime]:
def create_sample_metric_data(metric_type: MetricType, value: float, unit: str) -> MetricData:

class AnalyticsView(BaseComponent):
    def __init__(self, page: ft.Page, server_bridge=None, dialog_system=None, toast_manager=None):
        # ... existing initialization ...
        # Performance charts initialization
        if server_bridge:
            from flet_server_gui.ui.widgets.charts import EnhancedPerformanceCharts
            self.performance_charts = EnhancedPerformanceCharts(server_bridge, page)
```

**After (clean separation):**
```python
# Import utilities from service layer
from flet_server_gui.services.analytics_utilities import (
    format_metric_value, calculate_time_boundaries, create_sample_metric_data,
    MetricType, AnalyticsTimeRange, MetricData
)
from flet_server_gui.services.chart_service import ChartService

class AnalyticsView(BaseComponent):
    def __init__(self, page: ft.Page, server_bridge=None, dialog_system=None, toast_manager=None):
        # ... existing initialization ...
        
        # Use unified chart service
        self.chart_service = ChartService.get_instance()
        self.performance_chart = None
        if server_bridge:
            self.performance_chart = self.chart_service.create_performance_chart(
                page, server_bridge, chart_id="analytics_performance"
            )
```

### 4. Update Chart Configuration

**Before (scattered configuration classes):**
```python
# Different config classes in different files
from flet_server_gui.ui.widgets.charts import ChartSettings, MetricThreshold
from flet_server_gui.ui.widgets.enhanced_charts import EnhancedChartConfig
```

**After (unified configuration):**
```python
from flet_server_gui.services.chart_types import (
    ChartConfiguration, PerformanceChartSettings, MetricThreshold,
    create_chart_configuration
)

# Create standardized configuration
config = create_chart_configuration(
    chart_id="my_chart",
    chart_type=ChartType.LINE,
    title="My Chart",
    size=ChartSize.LARGE
)
```

### 5. Data Processing Updates

**Before (utility functions scattered):**
```python
# Direct usage in views
def _process_metrics(self, raw_data):
    # Inline processing logic
    formatted = []
    for item in raw_data:
        value_str = f"{item['value']:.2f} {item['unit']}"
        formatted.append(value_str)
    return formatted
```

**After (use service utilities):**
```python
from flet_server_gui.services.analytics_utilities import MetricData, aggregate_metric_data, DataAggregation
from flet_server_gui.services.chart_service import ChartService

def _process_metrics(self, raw_data):
    # Convert to MetricData objects
    metrics = [
        MetricData(
            metric_id=item['id'],
            metric_type=MetricType[item['type']], 
            value=item['value'],
            unit=item['unit'],
            timestamp=item['timestamp']
        ) for item in raw_data
    ]
    
    # Use service for processing
    chart_service = ChartService.get_instance()
    chart_points = chart_service.process_metric_data(metrics, DataAggregation.AVERAGE)
    
    return chart_points
```

## File Updates Required

### High Priority - Core Files

1. **`flet_server_gui/views/analytics.py`**
   - Remove utility functions (lines 104-192)
   - Update imports to use service layer
   - Update chart initialization to use ChartService

2. **Files using ChartType enum:**
   - Update imports to use `flet_server_gui.services.chart_types.ChartType`
   - Remove local ChartType definitions

3. **Files using enhanced charts:**
   - Update to use `ChartService.create_enhanced_chart()`
   - Replace direct imports from enhanced_charts.py

### Medium Priority - Integration Files

4. **Performance monitoring integrations:**
   - Update to use unified performance chart creation
   - Migrate threshold configurations to new format

5. **Dashboard views using multiple chart types:**
   - Migrate to use single ChartService instance
   - Standardize chart configuration approach

### Low Priority - Optional Enhancements

6. **Add theme integration:**
   ```python
   from flet_server_gui.services.chart_service import initialize_chart_service
   
   # In main app initialization:
   chart_service = initialize_chart_service(theme_manager)
   ```

7. **Enable real-time chart updates:**
   ```python
   # For performance charts
   chart.start_real_time_updates(data_source_function)
   ```

## Benefits After Migration

### Eliminated Duplication
- **ChartType enum**: Removed from 3 files, now in 1 location
- **Configuration classes**: Consolidated into unified structure  
- **Utility functions**: Extracted from view layer to service layer
- **Chart creation**: Single interface for all chart types

### Improved Maintainability
- **Single source of truth** for chart types and configurations
- **Consistent interfaces** across all chart implementations
- **Better separation of concerns** between views and chart logic
- **Centralized chart management** with registry pattern

### Enhanced Functionality  
- **Theme integration** built into chart service
- **Real-time updates** supported across all chart types
- **Performance optimizations** in unified data processing
- **Error handling** consistent across chart implementations

### Preserved Functionality
- **All existing chart types** still supported
- **Performance monitoring** maintains full capabilities
- **Enhanced chart features** preserved in unified interface
- **Backward compatibility** through convenience functions

## Testing After Migration

1. **Verify chart rendering** - All existing charts display correctly
2. **Test interactive features** - Zoom, pan, hover still work
3. **Validate performance monitoring** - Real-time updates functional
4. **Check theme integration** - Charts respond to theme changes
5. **Test error handling** - Graceful fallbacks for unsupported types

## Rollback Plan

If issues occur during migration:

1. **Keep old files temporarily** until migration validated
2. **Use git branches** for incremental migration
3. **Test each file update** before moving to next
4. **Maintain import compatibility** during transition period

The new architecture provides a solid foundation for future chart enhancements while eliminating the maintenance burden of duplicated code.