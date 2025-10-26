"""
Performance benchmarking for FletV2 experimental views.

This module benchmarks the performance of the experimental views
compared to original implementations, focusing on loading times,
UI responsiveness, and async operation efficiency.
"""

import sys
import os
import time
import asyncio
from unittest.mock import Mock
import statistics

# Add the FletV2 directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from views.enhanced_logs_exp import create_enhanced_logs_view, filter_logs_by_query, calculate_log_statistics
from views.database_pro_exp import create_database_view, filter_records_by_query, sanitize_sensitive_fields
from views.dashboard_exp import create_dashboard_view, calculate_metrics_summary, format_storage_value
from utils.async_helpers_exp import run_sync_in_executor


def benchmark_function_execution(func, *args, iterations=100, **kwargs):
    """Benchmark the execution time of a function."""
    times = []

    for _ in range(iterations):
        start_time = time.perf_counter()
        if asyncio.iscoroutinefunction(func):
            # For async functions, run them in an event loop
            async def run_async():
                return await func(*args, **kwargs)
            asyncio.run(run_async())
        else:
            # For sync functions, call directly
            func(*args, **kwargs)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    return {
        'min': min(times),
        'max': max(times),
        'avg': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0
    }


def simulate_log_data(count=1000):
    """Generate simulated log data for testing."""
    logs = []
    for i in range(count):
        logs.append({
            'time': f'2023-05-{i%30+1:02d} {i%24:02d}:{i%60:02d}:{i%60:02d}',
            'level': ['INFO', 'ERROR', 'WARNING', 'DEBUG'][i % 4],
            'message': f'Test log message number {i}',
            'component': f'Component_{i%5}'
        })
    return logs


def simulate_record_data(count=500):
    """Generate simulated record data for testing."""
    records = []
    for i in range(count):
        records.append({
            'id': i,
            'name': f'Record {i}',
            'email': f'user{i}@example.com',
            'description': f'This is a description for record number {i}. ' * 5,  # Long text for transformation tests
            'aes_key': f'sensitive_key_{i}' if i % 10 == 0 else f'normal_field_{i}'
        })
    return records


def benchmark_enhanced_logs_functions():
    """Benchmark enhanced logs business logic functions."""
    print("Benchmarking enhanced logs functions...")

    # Generate test data
    logs = simulate_log_data(1000)

    # Benchmark filter_logs_by_query
    filter_benchmark = benchmark_function_execution(
        filter_logs_by_query, logs, 'error', iterations=50
    )
    print(f"  filter_logs_by_query: avg={filter_benchmark['avg']:.6f}s, min={filter_benchmark['min']:.6f}s")

    # Benchmark calculate_log_statistics
    stats_benchmark = benchmark_function_execution(
        calculate_log_statistics, logs, iterations=50
    )
    print(f"  calculate_log_statistics: avg={stats_benchmark['avg']:.6f}s, min={stats_benchmark['min']:.6f}s")


def benchmark_database_pro_functions():
    """Benchmark database pro business logic functions."""
    print("Benchmarking database pro functions...")

    # Generate test data
    records = simulate_record_data(500)

    # Benchmark filter_records_by_query
    filter_benchmark = benchmark_function_execution(
        filter_records_by_query, records, 'user', iterations=50
    )
    print(f"  filter_records_by_query: avg={filter_benchmark['avg']:.6f}s, min={filter_benchmark['min']:.6f}s")

    # Benchmark sanitize_sensitive_fields
    sanitize_benchmark = benchmark_function_execution(
        sanitize_sensitive_fields, records, iterations=50
    )
    print(f"  sanitize_sensitive_fields: avg={sanitize_benchmark['avg']:.6f}s, min={sanitize_benchmark['min']:.6f}s")


def benchmark_dashboard_functions():
    """Benchmark dashboard business logic functions."""
    print("Benchmarking dashboard functions...")

    # Benchmark format_storage_value
    format_benchmark = benchmark_function_execution(
        format_storage_value, 1024*1024*2.5, iterations=100  # 2.5 MB
    )
    print(f"  format_storage_value: avg={format_benchmark['avg']:.6f}s, min={format_benchmark['min']:.6f}s")

    # Benchmark calculate_metrics_summary
    dashboard_data = {'data': {'clients_count': 100, 'files_count': 1000, 'total_storage': 1024*1024*100}}  # 100 MB
    system_data = {'data': {'uptime': 3600, 'server_status': 'Connected'}}
    performance_data = {'data': {'cpu_usage': 50.5, 'memory_usage': 60.2}}
    stats_data = {'data': {'backup_success_rate': 95.5, 'active_sessions': 10}}

    metrics_benchmark = benchmark_function_execution(
        calculate_metrics_summary, dashboard_data, system_data, performance_data, stats_data, iterations=100
    )
    print(f"  calculate_metrics_summary: avg={metrics_benchmark['avg']:.6f}s, min={metrics_benchmark['min']:.6f}s")


def benchmark_async_operations():
    """Benchmark async operations and run_sync_in_executor."""
    print("Benchmarking async operations...")

    def mock_sync_operation(x, y):
        # Simulate a small amount of work
        time.sleep(0.001)  # 1ms sleep
        return x + y

    # Benchmark run_sync_in_executor
    async_benchmark = benchmark_function_execution(
        run_sync_in_executor, mock_sync_operation, 5, 10, iterations=50
    )
    print(f"  run_sync_in_executor: avg={async_benchmark['avg']:.6f}s, min={async_benchmark['min']:.6f}s")


def benchmark_view_creation():
    """Benchmark view creation performance."""
    print("Benchmarking view creation...")

    # Create mock page and bridge
    mock_page = Mock()
    mock_bridge = Mock()

    # Mock bridge methods to return simple data
    mock_bridge.get_logs = lambda: {'success': True, 'data': {'logs': []}}
    mock_bridge.get_database_info = lambda: {'success': True, 'data': {}}
    mock_bridge.get_table_names = lambda: {'success': True, 'data': ['clients']}
    mock_bridge.get_table_data = lambda table: {'success': True, 'data': {'columns': [], 'rows': []}}
    mock_bridge.get_dashboard_summary = lambda: {'success': True, 'data': {}}
    mock_bridge.get_system_status = lambda: {'success': True, 'data': {}}
    mock_bridge.get_performance_metrics = lambda: {'success': True, 'data': {}}
    mock_bridge.get_server_statistics = lambda: {'success': True, 'data': {}}
    mock_bridge.get_recent_activity = lambda limit: {'success': True, 'data': []}

    # Benchmark enhanced logs view creation
    def create_enhanced_logs():
        return create_enhanced_logs_view(mock_page, mock_bridge)

    logs_view_benchmark = benchmark_function_execution(
        create_enhanced_logs, iterations=20
    )
    print(f"  Enhanced logs view creation: avg={logs_view_benchmark['avg']:.6f}s, min={logs_view_benchmark['min']:.6f}s")

    # Benchmark database view creation
    def create_database_view_func():
        return create_database_view(mock_page, mock_bridge)

    database_view_benchmark = benchmark_function_execution(
        create_database_view_func, iterations=20
    )
    print(f"  Database view creation: avg={database_view_benchmark['avg']:.6f}s, min={database_view_benchmark['min']:.6f}s")

    # Benchmark dashboard view creation
    def create_dashboard_view_func():
        return create_dashboard_view(mock_page, mock_bridge)

    dashboard_view_benchmark = benchmark_function_execution(
        create_dashboard_view_func, iterations=20
    )
    print(f"  Dashboard view creation: avg={dashboard_view_benchmark['avg']:.6f}s, min={dashboard_view_benchmark['min']:.6f}s")


def run_full_benchmark():
    """Run the complete performance benchmark suite."""
    print("Starting performance benchmarking...")
    print("="*50)

    benchmark_enhanced_logs_functions()
    print()

    benchmark_database_pro_functions()
    print()

    benchmark_dashboard_functions()
    print()

    benchmark_async_operations()
    print()

    benchmark_view_creation()
    print()

    print("="*50)
    print("Performance benchmarking completed!")


if __name__ == "__main__":
    run_full_benchmark()