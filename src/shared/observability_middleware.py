#!/usr/bin/env python3
"""
Observability Middleware for CyberBackup 3.0
Provides Flask middleware, decorators, and integration helpers
"""

import time
import functools
import threading
from typing import Callable, Any, Dict, Optional
from flask import Flask, request, g, jsonify
from .observability import (
    get_metrics_collector, get_system_monitor, create_structured_logger,
    TimedOperation, StructuredLogger
)
import logging
import uuid


class FlaskObservabilityMiddleware:
    """Flask middleware for automatic request/response observability"""
    
    def __init__(self, app: Flask, component_name: str = "api-server"):
        self.app = app
        self.component_name = component_name
        self.logger = create_structured_logger(component_name, logging.getLogger(__name__))
        self.metrics = get_metrics_collector()
        
        # Register middleware
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)
        
        # Add observability endpoints
        self._register_observability_endpoints()
        
    def _before_request(self):
        """Called before each request"""
        g.start_time = time.time()
        g.trace_id = str(uuid.uuid4())[:8]
        g.request_logger = self.logger.with_trace(g.trace_id)
        
        # Log request start
        g.request_logger.info(
            f"Request started: {request.method} {request.path}",
            operation="http_request",
            context={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get('User-Agent', ''),
                "content_length": request.content_length or 0
            }
        )
        
        # Record request metric
        self.metrics.record_counter(
            "http.requests.total",
            tags={
                "method": request.method,
                "endpoint": request.endpoint or "unknown"
            }
        )
        
    def _after_request(self, response):
        """Called after each request"""
        if hasattr(g, 'start_time') and hasattr(g, 'request_logger'):
            duration_ms = (time.time() - g.start_time) * 1000
            
            # Log request completion
            g.request_logger.info(
                f"Request completed: {request.method} {request.path} -> {response.status_code}",
                operation="http_request",
                duration_ms=duration_ms,
                context={
                    "status_code": response.status_code,
                    "response_size": len(response.get_data()) if response.get_data() else 0
                }
            )
            
            # Record timing and status metrics
            self.metrics.record_timer(
                "http.request.duration",
                duration_ms,
                tags={
                    "method": request.method,
                    "endpoint": request.endpoint or "unknown",
                    "status_code": str(response.status_code)
                }
            )
            
            # Record status code counter
            self.metrics.record_counter(
                "http.responses.total",
                tags={
                    "method": request.method,
                    "endpoint": request.endpoint or "unknown",
                    "status_code": str(response.status_code)
                }
            )
            
        return response
        
    def _teardown_request(self, exception):
        """Called when request context is torn down"""
        if exception and hasattr(g, 'request_logger'):
            g.request_logger.error(
                f"Request failed with exception: {exception}",
                operation="http_request",
                error_code=type(exception).__name__,
                context={"exception_str": str(exception)}
            )
            
            # Record error metric
            self.metrics.record_counter(
                "http.errors.total",
                tags={
                    "method": request.method,
                    "endpoint": request.endpoint or "unknown",
                    "error_type": type(exception).__name__
                }
            )
            
    def _register_observability_endpoints(self):
        """Register observability endpoints"""
        
        @self.app.route('/api/observability/health')
        def health_check():
            """Health check endpoint"""
            system_monitor = get_system_monitor()
            latest_metrics = system_monitor.get_latest_metrics()
            
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "component": self.component_name,
                "uptime_seconds": time.time() - getattr(self.app, '_start_time', time.time())
            }
            
            if latest_metrics:
                health_status["system"] = {
                    "cpu_percent": latest_metrics.cpu_percent,
                    "memory_percent": latest_metrics.memory_percent,
                    "disk_free_gb": latest_metrics.disk_free_gb,
                    "active_connections": latest_metrics.active_connections
                }
                
                # Simple health checks
                if latest_metrics.cpu_percent > 90:
                    health_status["status"] = "degraded"
                    health_status["warnings"] = health_status.get("warnings", [])
                    health_status["warnings"].append("High CPU usage")
                    
                if latest_metrics.memory_percent > 90:
                    health_status["status"] = "degraded"
                    health_status["warnings"] = health_status.get("warnings", [])
                    health_status["warnings"].append("High memory usage")
                    
            return jsonify(health_status)
            
        @self.app.route('/api/observability/metrics')
        def metrics_summary():
            """Metrics summary endpoint"""
            window_seconds = request.args.get('window', 300, type=int)
            summaries = self.metrics.get_all_summaries(window_seconds)
            
            return jsonify({
                "window_seconds": window_seconds,
                "timestamp": time.time(),
                "metrics": summaries
            })
            
        @self.app.route('/api/observability/system')
        def system_metrics():
            """System metrics endpoint"""
            system_monitor = get_system_monitor()
            window_seconds = request.args.get('window', 300, type=int)
            metrics_history = system_monitor.get_metrics_history(window_seconds)
            
            return jsonify({
                "window_seconds": window_seconds,
                "timestamp": time.time(),
                "metrics_count": len(metrics_history),
                "latest": metrics_history[-1].__dict__ if metrics_history else None,
                "history": [m.__dict__ for m in metrics_history[-10:]]  # Last 10 samples
            })


def observe_operation(operation_name: str, component: str = "unknown"):
    """Decorator for observing function operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = create_structured_logger(component, logging.getLogger(func.__module__))
            metrics = get_metrics_collector()
            
            with TimedOperation(operation_name, logger, tags={"function": func.__name__}):
                try:
                    result = func(*args, **kwargs)
                    metrics.record_counter(f"operation.{operation_name}.success")
                    return result
                except Exception as e:
                    metrics.record_counter(f"operation.{operation_name}.failure", 
                                         tags={"error_type": type(e).__name__})
                    logger.error(f"Operation {operation_name} failed: {e}",
                               operation=operation_name,
                               error_code=type(e).__name__)
                    raise
                    
        return wrapper
    return decorator


def observe_async_operation(operation_name: str, component: str = "unknown"):
    """Decorator for observing async function operations"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = create_structured_logger(component, logging.getLogger(func.__module__))
            metrics = get_metrics_collector()
            
            start_time = time.time()
            logger.info(f"Starting async {operation_name}", operation=operation_name)
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                metrics.record_timer(f"operation.{operation_name}.duration", duration_ms)
                metrics.record_counter(f"operation.{operation_name}.success")
                
                logger.info(f"Completed async {operation_name}",
                          operation=operation_name,
                          duration_ms=duration_ms)
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                metrics.record_timer(f"operation.{operation_name}.duration", duration_ms,
                                   tags={"success": "false"})
                metrics.record_counter(f"operation.{operation_name}.failure",
                                     tags={"error_type": type(e).__name__})
                
                logger.error(f"Async operation {operation_name} failed: {e}",
                           operation=operation_name,
                           duration_ms=duration_ms,
                           error_code=type(e).__name__)
                raise
                
        return wrapper
    return decorator


class BackgroundMetricsReporter:
    """Background thread for periodic metrics reporting"""
    
    def __init__(self, interval_seconds: float = 60.0, component: str = "metrics-reporter"):
        self.interval_seconds = interval_seconds
        self.component = component
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.logger = create_structured_logger(component, logging.getLogger(__name__))
        
    def start(self):
        """Start background metrics reporting"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._report_loop, daemon=True)
        self.thread.start()
        self.logger.info("Background metrics reporting started")
        
    def stop(self):
        """Stop background metrics reporting"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        self.logger.info("Background metrics reporting stopped")
        
    def _report_loop(self):
        """Main reporting loop"""
        while self.running:
            try:
                self._report_metrics()
            except Exception as e:
                self.logger.error(f"Metrics reporting failed: {e}")
                
            time.sleep(self.interval_seconds)
            
    def _report_metrics(self):
        """Report current metrics"""
        metrics = get_metrics_collector()
        system_monitor = get_system_monitor()
        
        # Get summaries
        metric_summaries = metrics.get_all_summaries(window_seconds=self.interval_seconds)
        system_metrics = system_monitor.get_latest_metrics()
        
        # Log summary
        self.logger.info(
            "Periodic metrics report",
            operation="metrics_report",
            context={
                "metric_types": len(metric_summaries),
                "system_cpu": system_metrics.cpu_percent if system_metrics else None,
                "system_memory": system_metrics.memory_percent if system_metrics else None,
                "interval_seconds": self.interval_seconds
            }
        )
        
        # Record reporting metric
        metrics.record_counter("metrics.reports.generated")


def setup_observability_for_flask(app: Flask, component_name: str = "api-server") -> FlaskObservabilityMiddleware:
    """Setup complete observability for a Flask application"""
    # Store start time
    app._start_time = time.time()
    
    # Setup middleware
    middleware = FlaskObservabilityMiddleware(app, component_name)
    
    # Start system monitoring
    system_monitor = get_system_monitor()
    if not system_monitor.running:
        system_monitor.start()
        
    # Start background metrics reporting
    reporter = BackgroundMetricsReporter(component=f"{component_name}-reporter")
    reporter.start()
    
    # Store references for cleanup
    app._observability_middleware = middleware
    app._metrics_reporter = reporter
    
    return middleware
