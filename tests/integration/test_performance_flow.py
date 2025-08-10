#!/usr/bin/env python3
"""
Performance Integration Tests for API → C++ Client → Server Flow
===============================================================

This test suite focuses on performance aspects of the complete flow:
- Transfer speed benchmarks
- Memory usage monitoring
- Concurrent load testing
- Resource cleanup verification
- Timeout and reliability testing
"""

import unittest
import os
import sys
import time
import tempfile
import threading
import requests
import psutil
import gc
from pathlib import Path
from typing import Dict, Any, List, Tuple
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.test_complete_flow import IntegrationTestFramework
from Shared.observability import get_metrics_collector, get_system_monitor


class PerformanceTestFramework(IntegrationTestFramework):
    """Extended framework for performance testing"""
    
    def __init__(self):
        super().__init__()
        self.performance_data: Dict[str, List[float]] = {}
        self.system_monitor = get_system_monitor()
        
    def start_performance_monitoring(self):
        """Start system performance monitoring"""
        if not self.system_monitor.running:
            self.system_monitor.start()
    
    def record_performance_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        if metric_name not in self.performance_data:
            self.performance_data[metric_name] = []
        self.performance_data[metric_name].append(value)
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for all performance metrics"""
        summary = {}
        for metric_name, values in self.performance_data.items():
            if values:
                summary[metric_name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'stdev': statistics.stdev(values) if len(values) > 1 else 0.0
                }
        return summary
    
    def measure_transfer_performance(self, test_file: Path, username: str) -> Dict[str, float]:
        """Measure performance metrics for a file transfer"""
        file_size = test_file.stat().st_size
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        # Perform transfer
        self._perform_file_transfer(test_file, username, timeout=300)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        duration = end_time - start_time
        memory_delta = end_memory - start_memory
        transfer_rate = file_size / duration if duration > 0 else 0
        
        metrics = {
            'duration_seconds': duration,
            'file_size_bytes': file_size,
            'transfer_rate_bps': transfer_rate,
            'memory_delta_bytes': memory_delta,
            'memory_efficiency': file_size / max(memory_delta, 1)  # Avoid division by zero
        }
        
        # Record metrics
        for metric_name, value in metrics.items():
            self.record_performance_metric(metric_name, value)
        
        return metrics


class TestTransferPerformance(unittest.TestCase):
    """Test transfer performance characteristics"""
    
    @classmethod
    def setUpClass(cls):
        """Setup performance test infrastructure"""
        cls.framework = PerformanceTestFramework()
        if not cls.framework.setup_infrastructure():
            raise unittest.SkipTest("Failed to setup performance test infrastructure")
        cls.framework.start_performance_monitoring()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup and report performance results"""
        performance_summary = cls.framework.get_performance_summary()
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        for metric_name, stats in performance_summary.items():
            print(f"\n{metric_name}:")
            print(f"  Count: {stats['count']}")
            print(f"  Min: {stats['min']:.2f}")
            print(f"  Max: {stats['max']:.2f}")
            print(f"  Mean: {stats['mean']:.2f}")
            print(f"  Median: {stats['median']:.2f}")
            print(f"  StdDev: {stats['stdev']:.2f}")
        
        cls.framework.teardown_infrastructure()
    
    def test_small_file_performance(self):
        """Test performance with small files (1KB)"""
        test_file = self.framework.create_test_file(1024, "PERF_SMALL")
        username = "perf_small_user"
        
        metrics = self.framework.measure_transfer_performance(test_file, username)
        
        # Performance assertions
        self.assertLess(metrics['duration_seconds'], 30, "Small file transfer took too long")
        self.assertGreater(metrics['transfer_rate_bps'], 100, "Transfer rate too slow")
        
        # Memory efficiency check
        self.assertLess(metrics['memory_delta_bytes'], 50 * 1024 * 1024, 
                       "Memory usage too high for small file")
    
    def test_medium_file_performance(self):
        """Test performance with medium files (64KB)"""
        test_file = self.framework.create_test_file(65536, "PERF_MEDIUM")
        username = "perf_medium_user"
        
        metrics = self.framework.measure_transfer_performance(test_file, username)
        
        # Performance assertions
        self.assertLess(metrics['duration_seconds'], 60, "Medium file transfer took too long")
        self.assertGreater(metrics['transfer_rate_bps'], 1000, "Transfer rate too slow")
        
        # Memory efficiency should be reasonable
        self.assertLess(metrics['memory_delta_bytes'], 100 * 1024 * 1024,
                       "Memory usage too high for medium file")
    
    def test_large_file_performance(self):
        """Test performance with large files (1MB)"""
        test_file = self.framework.create_test_file(1048576, "PERF_LARGE")
        username = "perf_large_user"
        
        metrics = self.framework.measure_transfer_performance(test_file, username)
        
        # Performance assertions
        self.assertLess(metrics['duration_seconds'], 120, "Large file transfer took too long")
        self.assertGreater(metrics['transfer_rate_bps'], 5000, "Transfer rate too slow")
        
        # Memory efficiency is critical for large files
        self.assertGreater(metrics['memory_efficiency'], 0.5,
                          "Memory efficiency too low for large file")
    
    def test_multiple_file_performance(self):
        """Test performance with multiple sequential transfers"""
        file_sizes = [1024, 4096, 16384, 65536]  # Various sizes
        transfer_times = []
        
        for i, size in enumerate(file_sizes):
            test_file = self.framework.create_test_file(size, f"PERF_MULTI_{i}")
            username = f"perf_multi_user_{i}"
            
            start_time = time.time()
            self.framework._perform_file_transfer(test_file, username)
            duration = time.time() - start_time
            
            transfer_times.append(duration)
            self.framework.record_performance_metric('sequential_transfer_time', duration)
        
        # Check that performance doesn't degrade significantly
        if len(transfer_times) > 1:
            first_half_avg = statistics.mean(transfer_times[:len(transfer_times)//2])
            second_half_avg = statistics.mean(transfer_times[len(transfer_times)//2:])
            
            # Second half shouldn't be more than 50% slower than first half
            self.assertLess(second_half_avg, first_half_avg * 1.5,
                           "Performance degraded significantly over multiple transfers")


class TestConcurrentPerformance(unittest.TestCase):
    """Test concurrent transfer performance"""
    
    @classmethod
    def setUpClass(cls):
        """Setup concurrent performance test infrastructure"""
        cls.framework = PerformanceTestFramework()
        if not cls.framework.setup_infrastructure():
            raise unittest.SkipTest("Failed to setup concurrent performance test infrastructure")
        cls.framework.start_performance_monitoring()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup concurrent performance tests"""
        cls.framework.teardown_infrastructure()
    
    def test_concurrent_small_files(self):
        """Test concurrent transfer of small files"""
        num_concurrent = 3
        file_size = 4096
        
        results = self._run_concurrent_transfers(num_concurrent, file_size, "concurrent_small")
        
        # All transfers should succeed
        self.assertEqual(len(results), num_concurrent)
        for result in results:
            self.assertTrue(result['success'], f"Concurrent transfer failed: {result.get('error')}")
        
        # Check timing
        durations = [r['duration'] for r in results if 'duration' in r]
        if durations:
            max_duration = max(durations)
            self.assertLess(max_duration, 60, "Concurrent small file transfers took too long")
    
    def test_concurrent_medium_files(self):
        """Test concurrent transfer of medium files"""
        num_concurrent = 2
        file_size = 32768
        
        results = self._run_concurrent_transfers(num_concurrent, file_size, "concurrent_medium")
        
        # All transfers should succeed
        self.assertEqual(len(results), num_concurrent)
        for result in results:
            self.assertTrue(result['success'], f"Concurrent transfer failed: {result.get('error')}")
        
        # Check timing
        durations = [r['duration'] for r in results if 'duration' in r]
        if durations:
            max_duration = max(durations)
            self.assertLess(max_duration, 120, "Concurrent medium file transfers took too long")
    
    def test_resource_cleanup(self):
        """Test that resources are properly cleaned up after transfers"""
        initial_memory = psutil.Process().memory_info().rss
        initial_handles = len(psutil.Process().open_files())
        
        # Perform several transfers
        for i in range(5):
            test_file = self.framework.create_test_file(8192, f"CLEANUP_TEST_{i}")
            username = f"cleanup_user_{i}"
            self.framework._perform_file_transfer(test_file, username)
        
        # Force garbage collection
        gc.collect()
        time.sleep(2)  # Allow cleanup to complete
        
        final_memory = psutil.Process().memory_info().rss
        final_handles = len(psutil.Process().open_files())
        
        # Memory growth should be reasonable
        memory_growth = final_memory - initial_memory
        self.assertLess(memory_growth, 100 * 1024 * 1024,  # 100MB
                       f"Excessive memory growth: {memory_growth / 1024 / 1024:.1f}MB")
        
        # File handles should not leak significantly
        handle_growth = final_handles - initial_handles
        self.assertLess(handle_growth, 10, f"File handle leak detected: {handle_growth}")
    
    def _run_concurrent_transfers(self, num_concurrent: int, file_size: int, 
                                 test_prefix: str) -> List[Dict[str, Any]]:
        """Run multiple concurrent file transfers"""
        threads = []
        results = []
        results_lock = threading.Lock()
        
        def transfer_worker(worker_id: int):
            try:
                test_file = self.framework.create_test_file(
                    file_size, f"{test_prefix}_{worker_id}"
                )
                username = f"{test_prefix}_user_{worker_id}"
                
                start_time = time.time()
                self.framework._perform_file_transfer(test_file, username)
                duration = time.time() - start_time
                
                with results_lock:
                    results.append({
                        'worker_id': worker_id,
                        'success': True,
                        'duration': duration,
                        'file_size': file_size
                    })
                    
            except Exception as e:
                with results_lock:
                    results.append({
                        'worker_id': worker_id,
                        'success': False,
                        'error': str(e)
                    })
        
        # Start concurrent transfers
        for i in range(num_concurrent):
            thread = threading.Thread(target=transfer_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all transfers to complete
        for thread in threads:
            thread.join(timeout=300)  # 5 minute timeout per thread
        
        return results


if __name__ == '__main__':
    # Run performance tests with verbose output
    unittest.main(verbosity=2)
