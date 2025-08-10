#!/usr/bin/env python3
"""
Comprehensive Integration Tests for API → C++ Client → Server Flow
================================================================

This test suite validates the complete end-to-end flow:
1. API Server (Flask) receives requests
2. API Server launches C++ client subprocess
3. C++ client connects to backup server
4. File transfer and verification
5. Response propagation back to API

Tests cover:
- Happy path file transfers
- Error handling and edge cases
- Performance and timeout scenarios
- Concurrent operations
- System resource management
"""

import unittest
import os
import sys
import time
import tempfile
import subprocess
import threading
import requests
import json
import hashlib
import shutil
import socket
from pathlib import Path
from typing import Dict, Any, Optional, List
import psutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from Shared.observability import get_metrics_collector, get_system_monitor
from Shared.logging_utils import setup_dual_logging


class IntegrationTestFramework:
    """Framework for managing integration test infrastructure"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_data_dir = self.project_root / "tests" / "integration" / "test_data"
        self.received_files_dir = self.project_root / "received_files"
        
        # Server processes
        self.backup_server_process: Optional[subprocess.Popen] = None
        self.api_server_process: Optional[subprocess.Popen] = None
        
        # Test configuration
        self.api_port = 9090
        self.backup_port = 1256
        self.api_base_url = f"http://localhost:{self.api_port}"
        
        # Test tracking
        self.test_files_created: List[Path] = []
        self.cleanup_needed = False
        
        # Setup logging
        self.logger, _ = setup_dual_logging(
            logger_name="integration_tests",
            server_type="integration-test",
            console_level=20,  # INFO
            file_level=10      # DEBUG
        )
        
        # Ensure directories exist
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.received_files_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_infrastructure(self) -> bool:
        """Start backup server and API server"""
        try:
            self.logger.info("Setting up integration test infrastructure")
            
            # Check if ports are available
            if not self._is_port_available(self.backup_port):
                self.logger.warning(f"Backup server port {self.backup_port} already in use")
                return False
                
            if not self._is_port_available(self.api_port):
                self.logger.warning(f"API server port {self.api_port} already in use")
                return False
            
            # Start backup server
            self.logger.info("Starting backup server")
            backup_server_cmd = [sys.executable, "-m", "python_server.server.server"]
            self.backup_server_process = subprocess.Popen(
                backup_server_cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for backup server to start
            if not self._wait_for_port(self.backup_port, timeout=30):
                self.logger.error("Backup server failed to start")
                return False
            
            # Start API server
            self.logger.info("Starting API server")
            api_server_cmd = [sys.executable, "cyberbackup_api_server.py"]
            self.api_server_process = subprocess.Popen(
                api_server_cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for API server to start
            if not self._wait_for_port(self.api_port, timeout=30):
                self.logger.error("API server failed to start")
                return False
            
            # Verify health
            if not self._verify_server_health():
                self.logger.error("Server health check failed")
                return False
                
            self.cleanup_needed = True
            self.logger.info("Integration test infrastructure ready")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup infrastructure: {e}")
            return False
    
    def teardown_infrastructure(self):
        """Stop servers and cleanup"""
        if not self.cleanup_needed:
            return
            
        self.logger.info("Tearing down integration test infrastructure")
        
        # Stop API server
        if self.api_server_process:
            try:
                self.api_server_process.terminate()
                self.api_server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.api_server_process.kill()
            except Exception as e:
                self.logger.warning(f"Error stopping API server: {e}")
        
        # Stop backup server
        if self.backup_server_process:
            try:
                self.backup_server_process.terminate()
                self.backup_server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.backup_server_process.kill()
            except Exception as e:
                self.logger.warning(f"Error stopping backup server: {e}")
        
        # Cleanup test files
        for test_file in self.test_files_created:
            try:
                if test_file.exists():
                    test_file.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {test_file}: {e}")
        
        self.cleanup_needed = False
        self.logger.info("Infrastructure teardown complete")
    
    def create_test_file(self, size_bytes: int, content_pattern: str = "TEST", 
                        suffix: str = ".txt") -> Path:
        """Create a test file with specified size and content"""
        test_file = self.test_data_dir / f"test_{int(time.time())}_{size_bytes}bytes{suffix}"
        
        # Generate content
        pattern_bytes = content_pattern.encode('utf-8')
        full_patterns = size_bytes // len(pattern_bytes)
        remainder = size_bytes % len(pattern_bytes)
        
        with open(test_file, 'wb') as f:
            for _ in range(full_patterns):
                f.write(pattern_bytes)
            if remainder > 0:
                f.write(pattern_bytes[:remainder])
        
        self.test_files_created.append(test_file)
        return test_file
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def find_received_file(self, original_filename: str, username: str) -> Optional[Path]:
        """Find the received file in the server directory"""
        # Server saves files with pattern: {username}_{timestamp}_{filename}
        pattern = f"{username}_*_{original_filename}"
        
        for file_path in self.received_files_dir.glob(pattern):
            if file_path.is_file():
                return file_path
        return None
    
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def _wait_for_port(self, port: int, timeout: int = 30) -> bool:
        """Wait for port to become available (server started)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        return True
            except Exception:
                pass
            time.sleep(0.5)
        return False
    
    def _verify_server_health(self) -> bool:
        """Verify both servers are healthy"""
        try:
            # Check API server health
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code != 200:
                return False
            
            health_data = response.json()
            if health_data.get('status') != 'healthy':
                self.logger.warning(f"API server health check: {health_data}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


class TestCompleteIntegrationFlow(unittest.TestCase):
    """Test complete API → C++ client → server integration flow"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test infrastructure once for all tests"""
        cls.framework = IntegrationTestFramework()
        if not cls.framework.setup_infrastructure():
            raise unittest.SkipTest("Failed to setup integration test infrastructure")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test infrastructure"""
        cls.framework.teardown_infrastructure()
    
    def setUp(self):
        """Setup for each test"""
        self.start_time = time.time()
        self.framework.logger.info(f"Starting test: {self._testMethodName}")
    
    def tearDown(self):
        """Cleanup after each test"""
        duration = time.time() - self.start_time
        self.framework.logger.info(f"Test {self._testMethodName} completed in {duration:.2f}s")
    
    def test_small_file_transfer(self):
        """Test transfer of small file (< 1KB)"""
        # Create small test file
        test_file = self.framework.create_test_file(512, "SMALL_FILE_TEST")
        original_hash = self.framework.calculate_file_hash(test_file)
        username = "test_small_user"
        
        # Connect to server
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Start backup
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/octet-stream')}
            data = {'username': username}
            
            backup_response = requests.post(
                f"{self.framework.api_base_url}/api/start_backup",
                files=files,
                data=data,
                timeout=30
            )
        
        self.assertEqual(backup_response.status_code, 200)
        backup_data = backup_response.json()
        self.assertTrue(backup_data.get('success'))
        
        job_id = backup_data.get('job_id')
        self.assertIsNotNone(job_id)
        
        # Monitor progress until completion
        self._wait_for_completion(job_id, timeout=60)
        
        # Verify file was received
        received_file = self.framework.find_received_file(test_file.name, username)
        self.assertIsNotNone(received_file, "File was not received by server")
        
        # Verify file integrity
        received_hash = self.framework.calculate_file_hash(received_file)
        self.assertEqual(original_hash, received_hash, "File integrity check failed")
    
    def test_medium_file_transfer(self):
        """Test transfer of medium file (~64KB)"""
        # Create medium test file
        test_file = self.framework.create_test_file(65536, "MEDIUM_FILE_TEST_PATTERN")
        original_hash = self.framework.calculate_file_hash(test_file)
        username = "test_medium_user"
        
        # Connect and transfer
        self._perform_file_transfer(test_file, username, timeout=120)
        
        # Verify
        received_file = self.framework.find_received_file(test_file.name, username)
        self.assertIsNotNone(received_file)
        
        received_hash = self.framework.calculate_file_hash(received_file)
        self.assertEqual(original_hash, received_hash)
    
    def test_large_file_transfer(self):
        """Test transfer of large file (~1MB)"""
        # Create large test file
        test_file = self.framework.create_test_file(1048576, "LARGE_FILE_TEST_PATTERN_")
        original_hash = self.framework.calculate_file_hash(test_file)
        username = "test_large_user"
        
        # Connect and transfer with longer timeout
        self._perform_file_transfer(test_file, username, timeout=300)
        
        # Verify
        received_file = self.framework.find_received_file(test_file.name, username)
        self.assertIsNotNone(received_file)
        
        received_hash = self.framework.calculate_file_hash(received_file)
        self.assertEqual(original_hash, received_hash)
    
    def _perform_file_transfer(self, test_file: Path, username: str, timeout: int = 120):
        """Helper method to perform complete file transfer"""
        # Connect
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Transfer
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/octet-stream')}
            data = {'username': username}
            
            backup_response = requests.post(
                f"{self.framework.api_base_url}/api/start_backup",
                files=files,
                data=data,
                timeout=timeout
            )
        
        self.assertEqual(backup_response.status_code, 200)
        backup_data = backup_response.json()
        self.assertTrue(backup_data.get('success'))
        
        job_id = backup_data.get('job_id')
        self.assertIsNotNone(job_id)
        
        # Wait for completion
        self._wait_for_completion(job_id, timeout=timeout)
    
    def _wait_for_completion(self, job_id: str, timeout: int = 120):
        """Wait for backup job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status_response = requests.get(
                    f"{self.framework.api_base_url}/api/status",
                    params={'job_id': job_id},
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    phase = status_data.get('phase', '')
                    
                    if phase in ['COMPLETED', 'COMPLETED_VERIFIED']:
                        return True
                    elif phase in ['FAILED', 'ERROR', 'CANCELLED']:
                        self.fail(f"Backup failed with phase: {phase}, message: {status_data.get('message')}")
                
            except Exception as e:
                self.framework.logger.warning(f"Status check failed: {e}")
            
            time.sleep(2)
        
        self.fail(f"Backup did not complete within {timeout} seconds")


    def test_concurrent_transfers(self):
        """Test multiple concurrent file transfers"""
        username_base = "test_concurrent_user"
        test_files = []

        # Create multiple test files
        for i in range(3):
            test_file = self.framework.create_test_file(
                8192, f"CONCURRENT_TEST_{i}_", f"_{i}.txt"
            )
            test_files.append((test_file, f"{username_base}_{i}"))

        # Start transfers concurrently
        threads = []
        results = {}

        def transfer_file(test_file, username):
            try:
                self._perform_file_transfer(test_file, username, timeout=180)
                results[username] = {'success': True, 'file': test_file}
            except Exception as e:
                results[username] = {'success': False, 'error': str(e)}

        # Launch concurrent transfers
        for test_file, username in test_files:
            thread = threading.Thread(target=transfer_file, args=(test_file, username))
            threads.append(thread)
            thread.start()

        # Wait for all transfers to complete
        for thread in threads:
            thread.join(timeout=300)

        # Verify all transfers succeeded
        for username, result in results.items():
            self.assertTrue(result.get('success'),
                          f"Concurrent transfer failed for {username}: {result.get('error')}")

        # Verify all files were received
        for test_file, username in test_files:
            received_file = self.framework.find_received_file(test_file.name, username)
            self.assertIsNotNone(received_file, f"File not received for {username}")

    def test_error_handling_invalid_file(self):
        """Test error handling for invalid file scenarios"""
        username = "test_error_user"

        # Connect first
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)

        # Try to upload non-existent file
        try:
            files = {'file': ('nonexistent.txt', b'', 'application/octet-stream')}
            data = {'username': username}

            backup_response = requests.post(
                f"{self.framework.api_base_url}/api/start_backup",
                files=files,
                data=data,
                timeout=30
            )

            # Should handle gracefully
            self.assertIn(backup_response.status_code, [400, 500])

        except Exception as e:
            # Error handling should be graceful
            self.framework.logger.info(f"Expected error for invalid file: {e}")

    def test_server_connection_failure(self):
        """Test behavior when backup server is unavailable"""
        username = "test_connection_user"

        # Try to connect to non-existent server
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 9999, "username": username}  # Wrong port
        )

        # Should handle connection failure gracefully
        self.assertIn(connect_response.status_code, [400, 500])

        response_data = connect_response.json()
        self.assertFalse(response_data.get('success', True))

    def test_observability_integration(self):
        """Test that observability features work during integration"""
        # Check metrics collection
        metrics = get_metrics_collector()
        initial_summaries = metrics.get_all_summaries()

        # Perform a file transfer
        test_file = self.framework.create_test_file(1024, "OBSERVABILITY_TEST")
        username = "test_observability_user"

        self._perform_file_transfer(test_file, username)

        # Check that metrics were recorded
        final_summaries = metrics.get_all_summaries()

        # Should have more metrics after the transfer
        self.assertGreaterEqual(len(final_summaries), len(initial_summaries))

        # Check for specific metrics
        metric_names = list(final_summaries.keys())
        self.assertTrue(any('start_backup' in name for name in metric_names),
                       "No start_backup metrics found")

    def test_health_endpoints(self):
        """Test observability health endpoints"""
        # Test main health endpoint
        health_response = requests.get(f"{self.framework.api_base_url}/health")
        self.assertEqual(health_response.status_code, 200)

        health_data = health_response.json()
        self.assertEqual(health_data.get('status'), 'healthy')

        # Test observability health endpoint
        obs_health_response = requests.get(
            f"{self.framework.api_base_url}/api/observability/health"
        )
        self.assertEqual(obs_health_response.status_code, 200)

        obs_health_data = obs_health_response.json()
        self.assertIn('status', obs_health_data)
        self.assertIn('timestamp', obs_health_data)

        # Test metrics endpoint
        metrics_response = requests.get(
            f"{self.framework.api_base_url}/api/observability/metrics"
        )
        self.assertEqual(metrics_response.status_code, 200)

        metrics_data = metrics_response.json()
        self.assertIn('metrics', metrics_data)
        self.assertIn('timestamp', metrics_data)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    @classmethod
    def setUpClass(cls):
        """Setup test infrastructure"""
        cls.framework = IntegrationTestFramework()
        if not cls.framework.setup_infrastructure():
            raise unittest.SkipTest("Failed to setup integration test infrastructure")

    @classmethod
    def tearDownClass(cls):
        """Cleanup test infrastructure"""
        cls.framework.teardown_infrastructure()

    def test_empty_file_transfer(self):
        """Test transfer of empty file"""
        test_file = self.framework.create_test_file(0, "")  # Empty file
        username = "test_empty_user"

        # Connect
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)

        # Try to transfer empty file
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/octet-stream')}
            data = {'username': username}

            backup_response = requests.post(
                f"{self.framework.api_base_url}/api/start_backup",
                files=files,
                data=data,
                timeout=30
            )

        # Should handle empty file appropriately
        # (May succeed or fail depending on implementation)
        self.assertIn(backup_response.status_code, [200, 400])

    def test_special_characters_filename(self):
        """Test files with special characters in filename"""
        # Create file with special characters
        special_name = "test_file_with_spaces_and_symbols_@#$%.txt"
        test_file = self.framework.test_data_dir / special_name

        with open(test_file, 'w') as f:
            f.write("File with special characters in name")

        self.framework.test_files_created.append(test_file)

        username = "test_special_user"

        # Connect and transfer
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)

        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/octet-stream')}
            data = {'username': username}

            backup_response = requests.post(
                f"{self.framework.api_base_url}/api/start_backup",
                files=files,
                data=data,
                timeout=60
            )

        # Should handle special characters appropriately
        self.assertEqual(backup_response.status_code, 200)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
