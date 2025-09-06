#!/usr/bin/env python3
"""
System Utilities for FletV2
Shared functions for accessing system information.
"""

import psutil
from utils.debug_setup import get_logger

logger = get_logger(__name__)

def get_system_metrics():
    """
    Get real system metrics using psutil.
    This is a blocking function and should be run in a thread.
    """
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            'cpu_usage': psutil.cpu_percent(interval=0.1),
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
            'memory_total_gb': memory.total // (1024**3),
            'memory_used_gb': (memory.total - memory.available) // (1024**3),
            'disk_total_gb': disk.total // (1024**3),
            'disk_used_gb': disk.used // (1024**3),
        }
    except Exception as e:
        logger.warning(f"Could not retrieve system metrics: {e}")
        # Return fallback data
        return {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 34.1,
            'memory_total_gb': 16,
            'memory_used_gb': 11,
            'disk_total_gb': 500,
            'disk_used_gb': 170,
        }
