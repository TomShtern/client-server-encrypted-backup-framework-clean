#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ApplicationMonitor - Extracted from main.py God Component
Handles background monitoring, resource tracking, and system health checks.
"""

import asyncio
import sys
import os
from typing import Set, Optional, Dict, Any, Callable
from datetime import datetime

# Import utf8_solution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
safe_print = print
try:
    from Shared.utils.utf8_solution import safe_print
except ImportError:
    pass


class ApplicationMonitor:
    """
    Manages background monitoring, resource tracking, and system health.
    
    Extracted from main.py (lines 843-917, 151-233) to follow Single Responsibility Principle.
    This class is responsible ONLY for monitoring and resource management.
    """
    
    def __init__(self, server_bridge: Any = None):
        self.server_bridge = server_bridge
        
        # Resource management
        self._background_tasks: Set[asyncio.Task] = set()
        self._monitor_task: Optional[asyncio.Task] = None
        self._is_shutting_down = False
        
        # Monitor configuration
        self.monitor_interval = 5  # seconds
        self.resource_warning_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85
        }
        
        # Status tracking
        self.last_server_status: Dict[str, Any] = {}
        self.last_resource_check = None
        
        # Callback system for status updates
        self.status_callbacks: list[Callable] = []
        self.resource_callbacks: list[Callable] = []
        self.error_callbacks: list[Callable] = []
    
    def add_status_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add callback for server status updates."""
        self.status_callbacks.append(callback)
    
    def add_resource_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add callback for resource monitoring updates."""
        self.resource_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[str, Exception], None]) -> None:
        """Add callback for error notifications."""
        self.error_callbacks.append(callback)
    
    def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if not self._monitor_task or self._monitor_task.done():
            self._is_shutting_down = False
            self._monitor_task = self._track_task(asyncio.create_task(self._monitor_loop()))
            safe_print("[INFO] Application monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        self._is_shutting_down = True
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            safe_print("[INFO] Application monitoring stopped")
    
    async def dispose(self) -> None:
        """Dispose of all monitoring resources."""
        safe_print("[INFO] Disposing application monitor resources...")
        await self._cancel_all_tasks()
        
        # Clear callbacks
        self.status_callbacks.clear()
        self.resource_callbacks.clear()
        self.error_callbacks.clear()
        
        safe_print("[INFO] Application monitor disposed successfully")
    
    def _track_task(self, task: asyncio.Task) -> asyncio.Task:
        """Track an async task for cleanup."""
        if not self._is_shutting_down:
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        return task
    
    async def _cancel_all_tasks(self) -> None:
        """Cancel all background tasks gracefully."""
        self._is_shutting_down = True
        
        # Cancel main monitor task first
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                safe_print(f"[WARNING] Error cancelling monitor task: {e}")
        
        # Cancel all other background tasks
        if self._background_tasks:
            safe_print(f"[INFO] Cancelling {len(self._background_tasks)} background tasks...")
            for task in list(self._background_tasks):
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            self._background_tasks.clear()
    
    async def _monitor_loop(self) -> None:
        """
        Main monitoring loop with proper resource management and meaningful functionality.
        Extracted from main.py lines 843-917.
        """
        safe_print("[INFO] Starting application monitor loop...")
        
        while not self._is_shutting_down:
            try:
                # Check if we should continue monitoring
                if self._is_shutting_down:
                    break
                
                # Monitor server status
                await self._check_server_status()
                
                # Monitor system resources
                await self._check_system_resources()
                
                # Update active views with monitoring data
                await self._update_view_monitoring()
                
                # Wait for next cycle, but check for shutdown
                await self._sleep_with_shutdown_check(self.monitor_interval)
                    
            except asyncio.CancelledError:
                safe_print("[INFO] Monitor loop cancelled")
                break
            except Exception as e:
                safe_print(f"[ERROR] Monitor loop error: {e}")
                self._notify_error_callbacks("Monitor loop error", e)
                # Use longer delay on errors
                await self._sleep_with_shutdown_check(10)
        
        safe_print("[INFO] Monitor loop stopped")
    
    async def _check_server_status(self) -> None:
        """Check and update server status."""
        try:
            if hasattr(self.server_bridge, 'get_server_status'):
                server_status = await self.server_bridge.get_server_status()
                if server_status:
                    # Store status for comparison
                    status_changed = server_status != self.last_server_status
                    self.last_server_status = server_status.copy()
                    
                    # Notify callbacks if status changed
                    if status_changed:
                        for callback in self.status_callbacks:
                            try:
                                callback(server_status)
                            except Exception as e:
                                safe_print(f"[WARNING] Status callback error: {e}")
                                
        except Exception as e:
            safe_print(f"[DEBUG] Server status check failed: {e}")
    
    async def _check_system_resources(self) -> None:
        """Check system resources and notify if thresholds exceeded."""
        try:
            import psutil
            
            resource_data = {
                'cpu_percent': psutil.cpu_percent(interval=None),
                'memory': psutil.virtual_memory(),
                'timestamp': datetime.now()
            }
            
            # Check thresholds and log warnings
            cpu_percent = resource_data['cpu_percent']
            memory_percent = resource_data['memory'].percent
            
            if cpu_percent > self.resource_warning_thresholds['cpu_percent']:
                safe_print(f"[WARNING] High CPU usage: {cpu_percent:.1f}%")
                
            if memory_percent > self.resource_warning_thresholds['memory_percent']:
                safe_print(f"[WARNING] High memory usage: {memory_percent:.1f}%")
            
            # Update last check time
            self.last_resource_check = datetime.now()
            
            # Notify resource callbacks
            for callback in self.resource_callbacks:
                try:
                    callback(resource_data)
                except Exception as e:
                    safe_print(f"[WARNING] Resource callback error: {e}")
                        
        except ImportError:
            # psutil not available, skip resource monitoring
            pass
        except Exception as e:
            safe_print(f"[DEBUG] Resource monitoring failed: {e}")
    
    async def _update_view_monitoring(self) -> None:
        """Update views with monitoring data if they support it."""
        # This will be called by the main app to update specific views
        # Left as a hook for the main application to implement
        pass
    
    async def _sleep_with_shutdown_check(self, duration: int) -> None:
        """Sleep for duration seconds while checking for shutdown."""
        for _ in range(duration):
            if self._is_shutting_down:
                break
            await asyncio.sleep(1)
    
    def _notify_error_callbacks(self, context: str, error: Exception) -> None:
        """Notify error callbacks of an error."""
        for callback in self.error_callbacks:
            try:
                callback(context, error)
            except Exception as e:
                safe_print(f"[WARNING] Error callback failed: {e}")
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """
        Get monitoring statistics.
        
        Returns:
            Dict with current monitoring stats
        """
        return {
            'is_monitoring': not self._is_shutting_down and self._monitor_task and not self._monitor_task.done(),
            'background_tasks': len(self._background_tasks),
            'last_server_status': self.last_server_status.copy(),
            'last_resource_check': self.last_resource_check,
            'monitor_interval': self.monitor_interval,
            'thresholds': self.resource_warning_thresholds.copy()
        }
    
    def set_monitor_interval(self, seconds: int) -> None:
        """Set the monitoring interval in seconds."""
        if seconds > 0:
            self.monitor_interval = seconds
            safe_print(f"[INFO] Monitor interval set to {seconds} seconds")
    
    def set_resource_thresholds(self, cpu_percent: int = None, memory_percent: int = None) -> None:
        """Set resource warning thresholds."""
        if cpu_percent is not None and 0 < cpu_percent <= 100:
            self.resource_warning_thresholds['cpu_percent'] = cpu_percent
        
        if memory_percent is not None and 0 < memory_percent <= 100:
            self.resource_warning_thresholds['memory_percent'] = memory_percent
        
        safe_print(f"[INFO] Resource thresholds updated: {self.resource_warning_thresholds}")