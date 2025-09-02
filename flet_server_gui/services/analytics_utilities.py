#!/usr/bin/env python3
"""
Analytics Utilities Service - Extracted utility functions and data processing

Purpose: Centralized utility functions for analytics and metrics processing
Logic: Data formatting, time calculations, and metric processing utilities
UI: Display formatting and value presentation utilities
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Tuple, Dict, Any, List, Optional, Union
import math


class MetricType(Enum):
    """Types of metrics for analytics tracking"""
    PERFORMANCE = auto()
    USAGE = auto()
    ERROR_RATE = auto()
    THROUGHPUT = auto()
    LATENCY = auto()
    STORAGE = auto()
    SECURITY = auto()
    CUSTOM = auto()
    
    # Performance-specific metrics
    CPU_USAGE = auto()
    MEMORY_USAGE = auto()
    DISK_USAGE = auto()
    NETWORK_IO = auto()
    TRANSFER_COUNT = auto()
    CLIENT_ACTIVITY = auto()


class AnalyticsTimeRange(Enum):
    """Time range options for analytics data"""
    REAL_TIME = "real_time"
    LAST_5_MINUTES = "5m"
    LAST_15_MINUTES = "15m"
    LAST_HOUR = "1h"
    LAST_4_HOURS = "4h" 
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    CUSTOM = "custom"


class DataAggregation(Enum):
    """Data aggregation methods"""
    SUM = auto()
    AVERAGE = auto()
    MEDIAN = auto()
    MIN = auto()
    MAX = auto()
    COUNT = auto()
    DISTINCT_COUNT = auto()
    STANDARD_DEVIATION = auto()
    PERCENTILE = auto()
    RATE = auto()  # For rate calculations (per second, etc.)


@dataclass
class MetricData:
    """Unified metric data structure with comprehensive metadata"""
    metric_id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    source: Optional[str] = None
    quality_score: float = 1.0  # 0-1 indicating data quality
    
    def format_value(self, precision: int = 2) -> str:
        """Format metric value for display"""
        return format_metric_value(self.value, self.unit, precision)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric data to dictionary for serialization"""
        return {
            "metric_id": self.metric_id,
            "metric_type": self.metric_type.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags,
            "source": self.source,
            "quality_score": self.quality_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricData':
        """Create MetricData from dictionary"""
        return cls(
            metric_id=data["metric_id"],
            metric_type=MetricType[data["metric_type"]],
            value=data["value"],
            unit=data["unit"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            source=data.get("source"),
            quality_score=data.get("quality_score", 1.0)
        )


@dataclass
class AggregatedMetric:
    """Aggregated metric result with statistical information"""
    metric_id: str
    aggregation_method: DataAggregation
    value: float
    unit: str
    time_range: Tuple[datetime, datetime]
    data_points_count: int
    confidence_interval: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Utility Functions

def format_metric_value(value: float, unit: str, precision: int = 2) -> str:
    """
    Format metric value for display with appropriate units and scaling.
    
    Args:
        value: Numeric value to format
        unit: Unit of measurement
        precision: Decimal precision for display
        
    Returns:
        Formatted string for UI display
    """
    # Handle different unit types with human-readable scaling
    if unit.lower() in ['bytes', 'b']:
        return _format_bytes(value, precision)
    
    elif unit in ['%', 'percent'] or unit.lower() == 'percent':
        return f"{value:.{precision}f}%"
    
    elif unit.lower() in ['seconds', 'sec', 's', 'ms', 'milliseconds']:
        return _format_time_duration(value, unit, precision)
    
    elif unit.lower() in ['hz', 'hertz', 'frequency']:
        return _format_frequency(value, precision)
    
    elif unit.lower() in ['count', 'items', 'requests', 'operations']:
        return _format_count(value, precision)
    
    elif unit.lower() in ['rate', 'per_second', '/s']:
        return f"{value:.{precision}f}/s"
    
    else:
        # Default formatting with number scaling for large values
        return _format_generic_number(value, unit, precision)


def _format_bytes(value: float, precision: int) -> str:
    """Format byte values with appropriate scale (B, KB, MB, etc.)"""
    if value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        if abs(value) < 1024:
            return f"{value:.{precision}f} {unit}"
        value /= 1024
    return f"{value:.{precision}f} EB"


def _format_time_duration(value: float, unit: str, precision: int) -> str:
    """Format time duration values"""
    if unit.lower() in ['ms', 'milliseconds']:
        if value >= 1000:
            return f"{value/1000:.{precision}f} sec"
        return f"{value:.{precision}f} ms"
    elif unit.lower() in ['seconds', 'sec', 's']:
        if value >= 60:
            minutes = int(value // 60)
            seconds = value % 60
            return f"{minutes}m {seconds:.{precision}f}s"
        return f"{value:.{precision}f} sec"
    else:
        return f"{value:.{precision}f} {unit}"


def _format_frequency(value: float, precision: int) -> str:
    """Format frequency values"""
    if value >= 1000000:
        return f"{value/1000000:.{precision}f} MHz"
    elif value >= 1000:
        return f"{value/1000:.{precision}f} kHz"
    else:
        return f"{value:.{precision}f} Hz"


def _format_count(value: float, precision: int) -> str:
    """Format count values with appropriate scaling"""
    if value >= 1000000:
        return f"{value/1000000:.{precision}f}M"
    elif value >= 1000:
        return f"{value/1000:.{precision}f}K"
    else:
        return f"{int(value) if value.is_integer() else value:.{precision}f}"


def _format_generic_number(value: float, unit: str, precision: int) -> str:
    """Format generic numbers with scaling for readability"""
    if abs(value) >= 1000000000:
        return f"{value/1000000000:.{precision}f}B {unit}"
    elif abs(value) >= 1000000:
        return f"{value/1000000:.{precision}f}M {unit}"
    elif abs(value) >= 1000:
        return f"{value/1000:.{precision}f}K {unit}"
    else:
        return f"{value:.{precision}f} {unit}"


def calculate_time_boundaries(time_range: AnalyticsTimeRange, custom_start: datetime = None, custom_end: datetime = None) -> Tuple[datetime, datetime]:
    """
    Calculate start and end times for analytics time range.
    
    Args:
        time_range: Time range specification
        custom_start: Custom start time for CUSTOM range
        custom_end: Custom end time for CUSTOM range
        
    Returns:
        Tuple of (start_time, end_time)
    """
    now = datetime.now()
    
    if time_range == AnalyticsTimeRange.REAL_TIME:
        return (now - timedelta(minutes=5), now)
    elif time_range == AnalyticsTimeRange.LAST_5_MINUTES:
        return (now - timedelta(minutes=5), now)
    elif time_range == AnalyticsTimeRange.LAST_15_MINUTES:
        return (now - timedelta(minutes=15), now)
    elif time_range == AnalyticsTimeRange.LAST_HOUR:
        return (now - timedelta(hours=1), now)
    elif time_range == AnalyticsTimeRange.LAST_4_HOURS:
        return (now - timedelta(hours=4), now)
    elif time_range == AnalyticsTimeRange.LAST_24_HOURS:
        return (now - timedelta(days=1), now)
    elif time_range == AnalyticsTimeRange.LAST_7_DAYS:
        return (now - timedelta(days=7), now)
    elif time_range == AnalyticsTimeRange.LAST_30_DAYS:
        return (now - timedelta(days=30), now)
    elif time_range == AnalyticsTimeRange.LAST_90_DAYS:
        return (now - timedelta(days=90), now)
    elif time_range == AnalyticsTimeRange.CUSTOM:
        if custom_start and custom_end:
            return (custom_start, custom_end)
        else:
            # Fallback to last 24 hours if custom range not provided
            return (now - timedelta(days=1), now)
    else:
        # Default to last 24 hours
        return (now - timedelta(days=1), now)


def aggregate_metric_data(metrics: List[MetricData], method: DataAggregation, group_by_time: Optional[timedelta] = None) -> List[AggregatedMetric]:
    """
    Aggregate metric data using specified method.
    
    Args:
        metrics: List of metric data points to aggregate
        method: Aggregation method to apply
        group_by_time: Optional time interval for grouping (e.g., hourly aggregation)
        
    Returns:
        List of aggregated metrics
    """
    if not metrics:
        return []
    
    # Group metrics by type and optionally by time buckets
    grouped_metrics = {}
    
    for metric in metrics:
        key = metric.metric_id
        
        if group_by_time:
            # Round timestamp to time bucket
            bucket_start = _round_to_time_bucket(metric.timestamp, group_by_time)
            key = f"{metric.metric_id}_{bucket_start.isoformat()}"
        
        if key not in grouped_metrics:
            grouped_metrics[key] = []
        grouped_metrics[key].append(metric)
    
    # Apply aggregation method to each group
    aggregated_results = []
    for group_key, group_metrics in grouped_metrics.items():
        aggregated = _apply_aggregation_method(group_metrics, method)
        if aggregated:
            aggregated_results.append(aggregated)
    
    return aggregated_results


def _round_to_time_bucket(timestamp: datetime, bucket_size: timedelta) -> datetime:
    """Round timestamp to time bucket boundary"""
    total_seconds = bucket_size.total_seconds()
    timestamp_seconds = timestamp.timestamp()
    bucket_seconds = int(timestamp_seconds // total_seconds) * total_seconds
    return datetime.fromtimestamp(bucket_seconds)


def _apply_aggregation_method(metrics: List[MetricData], method: DataAggregation) -> Optional[AggregatedMetric]:
    """Apply aggregation method to group of metrics"""
    if not metrics:
        return None
    
    values = [m.value for m in metrics]
    first_metric = metrics[0]
    
    # Calculate aggregated value based on method
    if method == DataAggregation.SUM:
        aggregated_value = sum(values)
    elif method == DataAggregation.AVERAGE:
        aggregated_value = sum(values) / len(values)
    elif method == DataAggregation.MEDIAN:
        sorted_values = sorted(values)
        n = len(sorted_values)
        aggregated_value = sorted_values[n//2] if n % 2 else (sorted_values[n//2-1] + sorted_values[n//2]) / 2
    elif method == DataAggregation.MIN:
        aggregated_value = min(values)
    elif method == DataAggregation.MAX:
        aggregated_value = max(values)
    elif method == DataAggregation.COUNT:
        aggregated_value = len(values)
    elif method == DataAggregation.DISTINCT_COUNT:
        aggregated_value = len(set(values))
    elif method == DataAggregation.STANDARD_DEVIATION:
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        aggregated_value = math.sqrt(variance)
    else:
        aggregated_value = sum(values) / len(values)  # Default to average
    
    # Create time range from first and last metric
    timestamps = [m.timestamp for m in metrics]
    time_range = (min(timestamps), max(timestamps))
    
    return AggregatedMetric(
        metric_id=first_metric.metric_id,
        aggregation_method=method,
        value=aggregated_value,
        unit=first_metric.unit,
        time_range=time_range,
        data_points_count=len(metrics),
        metadata={"aggregation_method": method.name, "source_metrics": len(metrics)}
    )


def create_sample_metric_data(metric_type: MetricType, value: float, unit: str, **kwargs) -> MetricData:
    """
    Create sample metric data for testing and demonstration.
    
    Args:
        metric_type: Type of metric
        value: Metric value
        unit: Unit of measurement
        **kwargs: Additional fields for MetricData
        
    Returns:
        MetricData instance with sample data
    """
    return MetricData(
        metric_id=kwargs.get("metric_id", f"sample_{metric_type.name.lower()}"),
        metric_type=metric_type,
        value=value,
        unit=unit,
        timestamp=kwargs.get("timestamp", datetime.now()),
        metadata=kwargs.get("metadata", {"source": "sample_data"}),
        tags=kwargs.get("tags", ["sample", "demo"]),
        source=kwargs.get("source", "sample_generator"),
        quality_score=kwargs.get("quality_score", 1.0)
    )


def calculate_metric_statistics(metrics: List[MetricData]) -> Dict[str, float]:
    """
    Calculate statistical measures for metric data.
    
    Args:
        metrics: List of metric data points
        
    Returns:
        Dictionary with statistical measures
    """
    if not metrics:
        return {}
    
    values = [m.value for m in metrics]
    n = len(values)
    
    # Basic statistics
    stats = {
        "count": n,
        "sum": sum(values),
        "mean": sum(values) / n,
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values)
    }
    
    # Variance and standard deviation
    mean = stats["mean"]
    variance = sum((x - mean) ** 2 for x in values) / n
    stats["variance"] = variance
    stats["std_dev"] = math.sqrt(variance)
    
    # Percentiles
    sorted_values = sorted(values)
    stats["median"] = sorted_values[n//2] if n % 2 else (sorted_values[n//2-1] + sorted_values[n//2]) / 2
    stats["percentile_25"] = sorted_values[int(n * 0.25)]
    stats["percentile_75"] = sorted_values[int(n * 0.75)]
    stats["percentile_95"] = sorted_values[int(n * 0.95)]
    stats["percentile_99"] = sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1]
    
    return stats


def detect_metric_anomalies(metrics: List[MetricData], threshold_std_devs: float = 2.0) -> List[MetricData]:
    """
    Detect anomalous metric values using standard deviation threshold.
    
    Args:
        metrics: List of metric data points
        threshold_std_devs: Number of standard deviations for anomaly threshold
        
    Returns:
        List of metrics identified as anomalies
    """
    if len(metrics) < 3:
        return []  # Need at least 3 points for anomaly detection
    
    values = [m.value for m in metrics]
    mean = sum(values) / len(values)
    std_dev = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
    
    if std_dev == 0:
        return []  # All values identical, no anomalies
    
    anomalies = []
    threshold = threshold_std_devs * std_dev
    
    for metric in metrics:
        if abs(metric.value - mean) > threshold:
            anomalies.append(metric)
    
    return anomalies


def calculate_metric_trend(metrics: List[MetricData]) -> Dict[str, Any]:
    """
    Calculate trend information for metric data over time.
    
    Args:
        metrics: List of metric data points (should be time-ordered)
        
    Returns:
        Dictionary with trend analysis
    """
    if len(metrics) < 2:
        return {"trend": "insufficient_data"}
    
    # Sort by timestamp
    sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
    values = [m.value for m in sorted_metrics]
    
    # Simple linear trend calculation
    n = len(values)
    x = list(range(n))  # Time index
    
    # Calculate slope (trend)
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    
    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator
    
    # Determine trend direction
    if slope > 0.1:
        trend_direction = "increasing"
    elif slope < -0.1:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"
    
    # Calculate rate of change
    first_value = values[0]
    last_value = values[-1]
    rate_of_change = (last_value - first_value) / first_value * 100 if first_value != 0 else 0
    
    return {
        "trend": trend_direction,
        "slope": slope,
        "rate_of_change": rate_of_change,
        "first_value": first_value,
        "last_value": last_value,
        "time_span": sorted_metrics[-1].timestamp - sorted_metrics[0].timestamp
    }


def validate_metric_data(metric: MetricData) -> List[str]:
    """
    Validate metric data and return list of validation errors.
    
    Args:
        metric: Metric data to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Required fields
    if not metric.metric_id:
        errors.append("Metric ID is required")
    if not metric.unit:
        errors.append("Unit is required")
    
    # Value validation
    if not isinstance(metric.value, (int, float)):
        errors.append("Value must be numeric")
    elif math.isnan(metric.value) or math.isinf(metric.value):
        errors.append("Value cannot be NaN or infinite")
    
    # Timestamp validation
    if not isinstance(metric.timestamp, datetime):
        errors.append("Timestamp must be datetime object")
    elif metric.timestamp > datetime.now() + timedelta(minutes=5):
        errors.append("Timestamp cannot be too far in the future")
    
    # Quality score validation
    if not (0 <= metric.quality_score <= 1):
        errors.append("Quality score must be between 0 and 1")
    
    return errors