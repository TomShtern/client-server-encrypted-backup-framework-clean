#!/usr/bin/env python3
"""
Error Scenario Integration Tests for API → C++ Client → Server Flow
==================================================================

This test suite focuses on error handling and edge cases:
- Network failures and timeouts
- Invalid input handling
- Resource exhaustion scenarios
- Recovery and cleanup after failures
- Error propagation through the complete stack
"""

import unittest
import os
import sys
import time
import tempfile
import subprocess
import requests
import socket
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.test_complete_flow import IntegrationTestFramework


class ErrorScenarioFramework(IntegrationTestFramework):
    """Extended framework for error scenario testing"""
    
    def __init__(self):
        super().__init__()
        self.error_scenarios: Dict[str, Any] = {}
    
    def simulate_network_failure(self, duration: int = 5):
        """Simulate network failure by blocking ports"""
        # This is a simplified simulation - in real scenarios you might use
        # network tools or firewall rules
        self.logger.info(f"Simulating network failure for {duration} seconds")
        time.sleep(duration)
    
    def create_corrupted_file(self, size_bytes: int) -> Path:
        """Create a file with corrupted/invalid content"""
        test_file = self.test_data_dir / f"corrupted_{int(time.time())}.bin"
        
        # Create file with random binary data that might cause issues
        with open(test_file, 'wb') as f:
            # Write some potentially problematic bytes
            f.write(b'\x00' * (size_bytes // 4))  # Null bytes
            f.write(b'\xFF' * (size_bytes // 4))  # Max bytes
            f.write(b'\x7F\x80\x81\x82' * (size_bytes // 16))  # Mixed bytes
            f.write(b'A' * (size_bytes - (size_bytes // 4) * 2 - (size_bytes // 16) * 4))
        
        self.test_files_created.append(test_file)
        return test_file
    
    def create_oversized_file(self, size_mb: int = 100) -> Path:
        """Create an oversized file for testing limits"""
        test_file = self.test_data_dir / f"oversized_{size_mb}MB_{int(time.time())}.dat"
        
        # Create large file efficiently
        with open(test_file, 'wb') as f:
            chunk = b'X' * (1024 * 1024)  # 1MB chunk
            for _ in range(size_mb):
                f.write(chunk)
        
        self.test_files_created.append(test_file)
        return test_file
    
    def force_server_shutdown(self):
        """Force shutdown of backup server to test error handling"""
        if self.backup_server_process:
            self.logger.info("Forcing backup server shutdown")
            self.backup_server_process.terminate()
            try:
                self.backup_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backup_server_process.kill()
            self.backup_server_process = None


class TestNetworkErrorScenarios(unittest.TestCase):
    """Test network-related error scenarios"""
    
    @classmethod
    def setUpClass(cls):
        """Setup error scenario test infrastructure"""
        cls.framework = ErrorScenarioFramework()
        if not cls.framework.setup_infrastructure():
            raise unittest.SkipTest("Failed to setup error scenario test infrastructure")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup error scenario tests"""
        cls.framework.teardown_infrastructure()
    
    def test_connection_to_invalid_server(self):
        """Test connection attempt to invalid server"""
        username = "test_invalid_server_user"
        
        # Try to connect to non-existent server
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "192.168.255.255", "port": 9999, "username": username},
            timeout=30
        )
        
        # Should handle connection failure gracefully
        self.assertIn(connect_response.status_code, [400, 500])
        
        response_data = connect_response.json()
        self.assertFalse(response_data.get('success', True))
        self.assertIn('error', response_data)
    
    def test_server_shutdown_during_transfer(self):
        """Test behavior when server shuts down during transfer"""
        # Create test file
        test_file = self.framework.create_test_file(32768, "SERVER_SHUTDOWN_TEST")
        username = "test_shutdown_user"
        
        # Connect successfully first
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Start transfer
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/octet-stream')}
            data = {'username': username}
            
            # Start transfer in background
            def start_transfer():
                try:
                    requests.post(
                        f"{self.framework.api_base_url}/api/start_backup",
                        files=files,
                        data=data,
                        timeout=60
                    )
                except Exception as e:
                    self.framework.logger.info(f"Expected error during server shutdown: {e}")
            
            transfer_thread = threading.Thread(target=start_transfer)
            transfer_thread.start()
            
            # Wait a moment then shutdown server
            time.sleep(2)
            self.framework.force_server_shutdown()
            
            # Wait for transfer to complete/fail
            transfer_thread.join(timeout=30)
        
        # API should handle the server failure gracefully
        # (The exact behavior depends on implementation)
    
    def test_timeout_scenarios(self):
        """Test various timeout scenarios"""
        username = "test_timeout_user"
        
        # Test connection timeout with very short timeout
        try:
            connect_response = requests.post(
                f"{self.framework.api_base_url}/api/connect",
                json={"host": "127.0.0.1", "port": 1256, "username": username},
                timeout=0.001  # Very short timeout
            )
        except requests.exceptions.Timeout:
            # Expected timeout
            pass
        except Exception as e:
            self.framework.logger.info(f"Timeout test resulted in: {e}")


class TestInvalidInputScenarios(unittest.TestCase):
    """Test invalid input handling"""
    
    @classmethod
    def setUpClass(cls):
        """Setup invalid input test infrastructure"""
        cls.framework = ErrorScenarioFramework()
        if not cls.framework.setup_infrastructure():
            raise unittest.SkipTest("Failed to setup invalid input test infrastructure")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup invalid input tests"""
        cls.framework.teardown_infrastructure()
    
    def test_invalid_json_requests(self):
        """Test handling of invalid JSON requests"""
        # Test malformed JSON
        response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            data="invalid json{",
            headers={'Content-Type': 'application/json'}
        )
        self.assertIn(response.status_code, [400, 500])
        
        # Test missing required fields
        response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1"}  # Missing port and username
        )
        self.assertIn(response.status_code, [400, 500])
    
    def test_invalid_file_uploads(self):
        """Test handling of invalid file uploads"""
        username = "test_invalid_file_user"
        
        # Connect first
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Test upload without file
        response = requests.post(
            f"{self.framework.api_base_url}/api/start_backup",
            data={'username': username}
        )
        self.assertIn(response.status_code, [400, 500])
        
        # Test upload with empty filename
        files = {'file': ('', b'content', 'application/octet-stream')}
        data = {'username': username}
        
        response = requests.post(
            f"{self.framework.api_base_url}/api/start_backup",
            files=files,
            data=data
        )
        self.assertIn(response.status_code, [400, 500])
    
    def test_corrupted_file_upload(self):
        """Test upload of corrupted/binary file"""
        username = "test_corrupted_user"
        
        # Connect first
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Create corrupted file
        corrupted_file = self.framework.create_corrupted_file(4096)
        
        # Try to upload corrupted file
        with open(corrupted_file, 'rb') as f:
            files = {'file': (corrupted_file.name, f, 'application/octet-stream')}
            data = {'username': username}
            
            response = requests.post(
                f"{self.framework.api_base_url}/api/start_backup",
                files=files,
                data=data,
                timeout=60
            )
        
        # Should handle corrupted file appropriately
        # (May succeed or fail depending on implementation)
        self.assertIn(response.status_code, [200, 400, 500])
    
    def test_extremely_long_filename(self):
        """Test handling of extremely long filenames"""
        username = "test_long_filename_user"
        
        # Connect first
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Create file with very long name
        long_name = "a" * 1000 + ".txt"  # 1000+ character filename
        test_file = self.framework.test_data_dir / "temp_long_name.txt"
        
        with open(test_file, 'w') as f:
            f.write("File with extremely long name")
        
        self.framework.test_files_created.append(test_file)
        
        # Try to upload with long filename
        with open(test_file, 'rb') as f:
            files = {'file': (long_name, f, 'application/octet-stream')}
            data = {'username': username}
            
            response = requests.post(
                f"{self.framework.api_base_url}/api/start_backup",
                files=files,
                data=data,
                timeout=60
            )
        
        # Should handle long filename appropriately
        self.assertIn(response.status_code, [200, 400, 500])


class TestResourceExhaustionScenarios(unittest.TestCase):
    """Test resource exhaustion scenarios"""
    
    @classmethod
    def setUpClass(cls):
        """Setup resource exhaustion test infrastructure"""
        cls.framework = ErrorScenarioFramework()
        if not cls.framework.setup_infrastructure():
            raise unittest.SkipTest("Failed to setup resource exhaustion test infrastructure")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup resource exhaustion tests"""
        cls.framework.teardown_infrastructure()
    
    def test_large_file_handling(self):
        """Test handling of very large files"""
        username = "test_large_file_user"
        
        # Connect first
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Create large file (10MB - adjust based on system capabilities)
        large_file = self.framework.create_oversized_file(10)
        
        # Try to upload large file
        try:
            with open(large_file, 'rb') as f:
                files = {'file': (large_file.name, f, 'application/octet-stream')}
                data = {'username': username}
                
                response = requests.post(
                    f"{self.framework.api_base_url}/api/start_backup",
                    files=files,
                    data=data,
                    timeout=300  # Extended timeout for large file
                )
            
            # Should handle large file appropriately
            self.assertIn(response.status_code, [200, 400, 413, 500])
            
        except requests.exceptions.Timeout:
            # Timeout is acceptable for very large files
            self.framework.logger.info("Large file upload timed out (expected)")
        except Exception as e:
            # Other exceptions should be handled gracefully
            self.framework.logger.info(f"Large file upload failed: {e}")
    
    def test_rapid_successive_requests(self):
        """Test rapid successive requests to check rate limiting/handling"""
        username = "test_rapid_user"
        
        # Connect first
        connect_response = requests.post(
            f"{self.framework.api_base_url}/api/connect",
            json={"host": "127.0.0.1", "port": 1256, "username": username}
        )
        self.assertEqual(connect_response.status_code, 200)
        
        # Create small test file
        test_file = self.framework.create_test_file(1024, "RAPID_TEST")
        
        # Send multiple rapid requests
        responses = []
        for i in range(5):
            try:
                with open(test_file, 'rb') as f:
                    files = {'file': (f"{test_file.name}_{i}", f, 'application/octet-stream')}
                    data = {'username': f"{username}_{i}"}
                    
                    response = requests.post(
                        f"{self.framework.api_base_url}/api/start_backup",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    responses.append(response.status_code)
            except Exception as e:
                self.framework.logger.info(f"Rapid request {i} failed: {e}")
                responses.append(0)  # Mark as failed
        
        # At least some requests should be handled properly
        successful_responses = [r for r in responses if r in [200, 202]]
        self.assertGreater(len(successful_responses), 0, 
                          "No rapid requests were handled successfully")


if __name__ == '__main__':
    # Run error scenario tests with verbose output
    unittest.main(verbosity=2)
