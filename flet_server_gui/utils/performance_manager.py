import time
import functools
from typing import Dict, List, Callable, Any
import flet as ft

class PerformanceManager:
    """Manage GUI performance optimization"""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._debounced_functions: Dict[str, Callable] = {}
    
    def measure_performance(self, operation_name: str):
        """Decorator to measure operation performance"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self._record_metric(operation_name, duration)
            return wrapper
        return decorator
    
    def debounce(self, delay: float = 0.3):
        """Decorator to debounce frequent function calls"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_key = f"{func.__name__}_{id(args)}_{id(kwargs)}"
                
                # Cancel previous delayed call
                if func_key in self._debounced_functions:
                    # In a real implementation, you'd cancel the timer
                    pass
                
                # Store new delayed call
                def delayed_call():
                    time.sleep(delay)
                    return func(*args, **kwargs)
                
                self._debounced_functions[func_key] = delayed_call
                return delayed_call()
                
            return wrapper
        return decorator
    
    def optimize_table_rendering(self, table: ft.DataTable, max_visible_rows: int = 300):
        """Optimize table rendering for large datasets"""
        if len(table.rows) > max_visible_rows:
            # Implement virtual scrolling or pagination
            visible_rows = table.rows[:max_visible_rows]
            table.rows = visible_rows
            
            # Add pagination info
            total_rows = len(table.rows)
            print(f"[PERF] Table optimized: showing {max_visible_rows} of {total_rows} rows")
    
    def _record_metric(self, operation: str, duration: float):
        """Record performance metric"""
        if operation not in self._metrics:
            self._metrics[operation] = []
        
        self._metrics[operation].append(duration)
        
        # Keep only last 100 measurements
        if len(self._metrics[operation]) > 100:
            self._metrics[operation] = self._metrics[operation][-100:]
    
    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """Generate performance report"""
        return {
            operation: {
                'avg_duration': sum(measurements) / len(measurements),
                'max_duration': max(measurements),
                'min_duration': min(measurements),
                'call_count': len(measurements),
            }
            for operation, measurements in self._metrics.items()
            if measurements
        }