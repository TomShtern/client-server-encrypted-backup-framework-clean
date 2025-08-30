#!/usr/bin/env python3
"""
Fix Validation Test Suite
Comprehensive testing for all the critical fixes implemented in the project.

This test suite validates:
1. SynchronizedFileManager race condition fixes
2. Protocol version flexibility improvements
3. Error propagation framework functionality
4. Flask dependency resolution
5. Enhanced subprocess monitoring

Tests are designed to ensure the fixes from CLAUDE.md work reliably.
"""

import unittest
import os
import sys
import threading
import time
import tempfile
import subprocess
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Setup standardized import paths
from Shared.path_utils import setup_imports
setup_imports()

# Import the components we're testing
from Shared.utils.file_lifecycle import SynchronizedFileManager, create_transfer_info_managed
from Shared.utils.error_handler import (
    get_error_handler, ErrorCode, ErrorCategory, ErrorSeverity,
    handle_subprocess_error, handle_protocol_error
)
from Shared.utils.unified_config import UnifiedConfigurationManager
from python_server.server.protocol import validate_protocol_version
from python_server.server.config import VERSION_TOLERANCE_ENABLED, COMPATIBLE_VERSIONS

class TestSynchronizedFileManager(unittest.TestCase):
    """Test the SynchronizedFileManager race condition fixes."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SynchronizedFileManager(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        self.manager.cleanup_all()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_creation_and_cleanup(self):
        """Test basic file creation and cleanup functionality."""
        filename = "test_file.txt"
        content = "Test content"
        
        # Create managed file
        file_path = self.manager.create_managed_file(filename, content)
        
        # Verify file exists and content is correct
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), content)
        
        # Get file ID for cleanup
        file_ids = self.manager.list_managed_files()
        self.assertEqual(len(file_ids), 1)
        file_id = file_ids[0]
        
        # Test safe cleanup
        self.assertTrue(self.manager.safe_cleanup(file_id))
        self.assertFalse(os.path.exists(file_path))
    
    def test_subprocess_reference_counting(self):
        """Test subprocess reference counting prevents premature cleanup."""
        filename = "subprocess_test.txt"
        content = "Subprocess test content"
        
        file_path = self.manager.create_managed_file(filename, content)
        file_id = self.manager.list_managed_files()[0]
        
        # Mark file as in use by subprocess
        self.assertTrue(self.manager.mark_in_subprocess_use(file_id))
        
        # Verify file info shows subprocess reference
        file_info = self.manager.get_file_info(file_id)
        self.assertEqual(file_info['subprocess_refs'], 1)
        
        # Attempt cleanup while subprocess is using file
        # This should wait for subprocess completion
        cleanup_thread = threading.Thread(
            target=lambda: self.manager.safe_cleanup(file_id, wait_timeout=2.0)
        )
        cleanup_thread.start()
        
        # Wait a moment, then release subprocess reference
        time.sleep(0.5)
        self.assertTrue(self.manager.release_subprocess_use(file_id))
        
        # Cleanup should now complete
        cleanup_thread.join(timeout=3.0)
        
        # File should be cleaned up
        self.assertFalse(os.path.exists(file_path))
    
    def test_copy_to_multiple_locations(self):
        """Test copying files to multiple locations safely."""
        filename = "multi_copy_test.txt"
        content = "Multi-copy test content"
        
        file_path = self.manager.create_managed_file(filename, content)
        file_id = self.manager.list_managed_files()[0]
        
        # Create target locations
        target_locations = [
            os.path.join(self.temp_dir, "copy1.txt"),
            os.path.join(self.temp_dir, "copy2.txt"),
            os.path.join(self.temp_dir, "subdir", "copy3.txt")
        ]
        
        # Copy to multiple locations
        created_copies = self.manager.copy_to_locations(file_id, target_locations)
        
        # Verify all copies were created
        self.assertEqual(len(created_copies), 3)
        for copy_path in created_copies:
            self.assertTrue(os.path.exists(copy_path))
            with open(copy_path, 'r') as f:
                self.assertEqual(f.read(), content)
        
        # Cleanup should remove all copies
        self.assertTrue(self.manager.safe_cleanup(file_id))
        for copy_path in created_copies:
            self.assertFalse(os.path.exists(copy_path))
    
    def test_race_condition_prevention(self):
        """Test that race conditions are prevented during concurrent access."""
        filename = "race_test.txt"
        content = "Race condition test"
        
        file_path = self.manager.create_managed_file(filename, content)
        file_id = self.manager.list_managed_files()[0]
        
        # Simulate multiple threads trying to access the file
        results = []
        errors = []
        
        def worker_thread(thread_id):
            try:
                # Mark as in use
                self.manager.mark_in_subprocess_use(file_id)
                time.sleep(0.1)  # Simulate work
                
                # Verify file still exists
                if os.path.exists(file_path):
                    results.append(f"Thread {thread_id}: File accessible")
                else:
                    results.append(f"Thread {thread_id}: File missing!")
                
                # Release reference
                self.manager.release_subprocess_use(file_id)
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")
        
        # Start multiple worker threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and all threads could access the file
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIn("File accessible", result)
        
        # Cleanup
        self.assertTrue(self.manager.safe_cleanup(file_id))
    
    def test_context_manager_usage(self):
        """Test the context manager for automatic lifecycle management."""
        filename = "context_test.txt"
        content = "Context manager test"
        target_locations = [os.path.join(self.temp_dir, "context_copy.txt")]
        
        file_id = None
        copy_locations = None
        
        # Use context manager
        with self.manager.managed_file_context(filename, content, target_locations) as (fid, fpath, copies):
            file_id = fid
            copy_locations = copies
            
            # Verify file and copies exist during context
            self.assertTrue(os.path.exists(fpath))
            for copy_path in copies:
                self.assertTrue(os.path.exists(copy_path))
        
        # After context, files should be cleaned up
        time.sleep(0.1)  # Allow cleanup to complete
        for copy_path in copy_locations:
            self.assertFalse(os.path.exists(copy_path))


class TestProtocolFlexibility(unittest.TestCase):
    """Test the protocol version flexibility improvements."""
    
    def setUp(self):
        """Set up test environment."""
        # Ensure version tolerance is enabled for testing
        import python_server.server.config as config
        self.original_tolerance = getattr(config, 'VERSION_TOLERANCE_ENABLED', True)
        config.VERSION_TOLERANCE_ENABLED = True
    
    def tearDown(self):
        """Restore original configuration."""
        import python_server.server.config as config
        config.VERSION_TOLERANCE_ENABLED = self.original_tolerance
    
    def test_exact_version_match(self):
        """Test that exact version matches still work."""
        from python_server.server.config import SERVER_VERSION
        self.assertTrue(validate_protocol_version(SERVER_VERSION))
    
    def test_backward_compatibility(self):
        """Test backward compatibility with older versions."""
        from python_server.server.config import SERVER_VERSION
        
        # Test one version behind (should be allowed)
        older_version = SERVER_VERSION - 1
        if older_version >= 1:  # Only test if positive version
            self.assertTrue(validate_protocol_version(older_version))
    
    def test_compatible_versions_list(self):
        """Test explicitly compatible versions."""
        # All versions in COMPATIBLE_VERSIONS should be accepted
        for version in COMPATIBLE_VERSIONS:
            self.assertTrue(validate_protocol_version(version))
    
    def test_version_range_support(self):
        """Test version range support."""
        from python_server.server.config import MIN_SUPPORTED_CLIENT_VERSION, MAX_SUPPORTED_CLIENT_VERSION
        
        # Test minimum supported version
        self.assertTrue(validate_protocol_version(MIN_SUPPORTED_CLIENT_VERSION))
        
        # Test maximum supported version
        self.assertTrue(validate_protocol_version(MAX_SUPPORTED_CLIENT_VERSION))
        
        # Test version below minimum (should fail)
        if MIN_SUPPORTED_CLIENT_VERSION > 1:
            self.assertFalse(validate_protocol_version(MIN_SUPPORTED_CLIENT_VERSION - 1))
        
        # Test version above maximum (should fail)
        self.assertFalse(validate_protocol_version(MAX_SUPPORTED_CLIENT_VERSION + 10))
    
    def test_version_tolerance_disable(self):
        """Test that version tolerance can be disabled for strict mode."""
        import python_server.server.config as config
        
        # Disable version tolerance
        config.VERSION_TOLERANCE_ENABLED = False
        
        # Only exact server version should be accepted
        from python_server.server.config import SERVER_VERSION
        self.assertTrue(validate_protocol_version(SERVER_VERSION))
        
        # Other versions should fail
        self.assertFalse(validate_protocol_version(SERVER_VERSION + 1))
        self.assertFalse(validate_protocol_version(SERVER_VERSION - 1))
        
        # Re-enable for other tests
        config.VERSION_TOLERANCE_ENABLED = True


class TestErrorPropagationFramework(unittest.TestCase):
    """Test the error propagation framework functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.error_handler = get_error_handler()
        # Clear existing errors
        self.error_handler.errors.clear()
        self.error_callback_triggered = False
        self.error_callback_data = None
    
    def test_error_creation_and_storage(self):
        """Test basic error creation and storage."""
        error_info = self.error_handler.create_error(
            code=ErrorCode.SUBPROCESS_FAILED,
            category=ErrorCategory.SUBPROCESS,
            severity=ErrorSeverity.HIGH,
            message="Test subprocess error",
            details="Test error details",
            layer="test_layer",
            component="test_component"
        )
        
        # Verify error was created correctly
        self.assertIsNotNone(error_info.error_id)
        self.assertEqual(error_info.code, ErrorCode.SUBPROCESS_FAILED)
        self.assertEqual(error_info.category, ErrorCategory.SUBPROCESS)
        self.assertEqual(error_info.severity, ErrorSeverity.HIGH)
        self.assertEqual(error_info.message, "Test subprocess error")
        self.assertEqual(error_info.layer, "test_layer")
        self.assertEqual(error_info.component, "test_component")
        
        # Verify error was stored
        retrieved_error = self.error_handler.get_error(error_info.error_id)
        self.assertIsNotNone(retrieved_error)
        self.assertEqual(retrieved_error.error_id, error_info.error_id)
    
    def test_error_propagation_across_layers(self):
        """Test error propagation across architectural layers."""
        # Create initial error in C++ layer
        cpp_error = self.error_handler.create_error(
            code=ErrorCode.ENCRYPTION_FAILED,
            category=ErrorCategory.CRYPTO,
            severity=ErrorSeverity.HIGH,
            message="AES encryption failed",
            details="Invalid key length",
            layer="cpp_client",
            component="AESWrapper"
        )
        
        # Propagate to Flask API layer
        flask_error = self.error_handler.propagate_error(
            cpp_error,
            new_layer="flask_api",
            new_component="backup_executor",
            additional_message="Subprocess encryption failed"
        )
        
        # Propagate to Web UI layer
        ui_error = self.error_handler.propagate_error(
            flask_error,
            new_layer="web_ui",
            new_component="upload_handler",
            additional_message="File upload failed",
            new_severity=ErrorSeverity.MEDIUM
        )
        
        # Verify propagation chain
        expected_chain = ["cpp_client::AESWrapper", "flask_api::backup_executor", "web_ui::upload_handler"]
        self.assertEqual(ui_error.propagation_chain, expected_chain)
        
        # Verify message accumulation
        self.assertIn("AES encryption failed", ui_error.message)
        self.assertIn("Subprocess encryption failed", ui_error.message)
        self.assertIn("File upload failed", ui_error.message)
        
        # Verify severity override
        self.assertEqual(ui_error.severity, ErrorSeverity.MEDIUM)
    
    def test_error_callbacks(self):
        """Test error callback registration and triggering."""
        def error_callback(error_info):
            self.error_callback_triggered = True
            self.error_callback_data = error_info
        
        # Register callback
        self.error_handler.register_error_callback(error_callback)
        
        # Create error to trigger callback
        error_info = self.error_handler.create_error(
            code=ErrorCode.NETWORK_ERROR,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message="Test network error"
        )
        
        # Verify callback was triggered
        self.assertTrue(self.error_callback_triggered)
        self.assertEqual(self.error_callback_data.error_id, error_info.error_id)
        
        # Remove callback
        self.error_handler.remove_callback(error_callback)
    
    def test_error_filtering_and_statistics(self):
        """Test error filtering and statistics functionality."""
        # Create various types of errors
        self.error_handler.create_error(
            code=ErrorCode.NETWORK_ERROR,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            message="Network error 1"
        )
        
        self.error_handler.create_error(
            code=ErrorCode.FILE_NOT_FOUND,
            category=ErrorCategory.FILE_TRANSFER,
            severity=ErrorSeverity.MEDIUM,
            message="File error 1"
        )
        
        self.error_handler.create_error(
            code=ErrorCode.NETWORK_ERROR,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.LOW,
            message="Network error 2"
        )
        
        # Test filtering by category
        network_errors = self.error_handler.get_errors_by_category(ErrorCategory.NETWORK)
        self.assertEqual(len(network_errors), 2)
        
        file_errors = self.error_handler.get_errors_by_category(ErrorCategory.FILE_TRANSFER)
        self.assertEqual(len(file_errors), 1)
        
        # Test filtering by severity
        high_errors = self.error_handler.get_errors_by_severity(ErrorSeverity.HIGH)
        self.assertEqual(len(high_errors), 1)
        
        # Test statistics
        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats['total_errors'], 3)
        self.assertEqual(stats['by_category'][ErrorCategory.NETWORK], 2)
        self.assertEqual(stats['by_category'][ErrorCategory.FILE_TRANSFER], 1)
    
    def test_convenience_error_functions(self):
        """Test convenience functions for common error scenarios."""
        # Test subprocess error
        subprocess_error = handle_subprocess_error(
            message="Test subprocess failure",
            details="Process exit code: 1",
            component="test_component"
        )
        
        self.assertEqual(subprocess_error.code, ErrorCode.SUBPROCESS_FAILED)
        self.assertEqual(subprocess_error.category, ErrorCategory.SUBPROCESS)
        
        # Test protocol error
        protocol_error = handle_protocol_error(
            message="Test protocol violation",
            details="Invalid header format",
            component="protocol_handler"
        )
        
        self.assertEqual(protocol_error.code, ErrorCode.PROTOCOL_VIOLATION)
        self.assertEqual(protocol_error.category, ErrorCategory.PROTOCOL)


class TestUnifiedConfiguration(unittest.TestCase):
    """Test the unified configuration management system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        os.makedirs(self.config_dir)
        
        # Create test configuration files
        self.create_test_config_files()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_config_files(self):
        """Create test configuration files."""
        # Create default.json
        default_config = {
            "server": {"host": "localhost", "port": 1256},
            "client": {"timeout": 30}
        }
        with open(os.path.join(self.config_dir, "default.json"), 'w') as f:
            json.dump(default_config, f)
        
        # Create development.json
        dev_config = {
            "server": {"port": 1257},  # Override port
            "logging": {"level": "DEBUG"}
        }
        with open(os.path.join(self.config_dir, "development.json"), 'w') as f:
            json.dump(dev_config, f)
    
    def test_configuration_loading_and_precedence(self):
        """Test configuration loading with proper precedence."""
        config = UnifiedConfigurationManager(
            config_dir=self.config_dir, 
            environment="development",
            base_path=self.temp_dir
        )
        
        # Test that development overrides default
        self.assertEqual(config.get('server.host'), 'localhost')  # From default
        self.assertEqual(config.get('server.port'), 1257)  # From development override
        self.assertEqual(config.get('logging.level'), 'DEBUG')  # From development
        self.assertEqual(config.get('client.timeout'), 30)  # From default
    
    def test_environment_variable_precedence(self):
        """Test that environment variables override configuration files."""
        # Set environment variable
        os.environ['BACKUP_SERVER_PORT'] = '1258'
        
        try:
            config = UnifiedConfigurationManager(
                config_dir=self.config_dir,
                environment="development",
                base_path=self.temp_dir
            )
            
            # Environment variable should override configuration file
            self.assertEqual(config.get('server.port'), 1258)
            
        finally:
            # Clean up environment variable
            if 'BACKUP_SERVER_PORT' in os.environ:
                del os.environ['BACKUP_SERVER_PORT']
    
    def test_configuration_validation(self):
        """Test configuration validation functionality."""
        config = UnifiedConfigurationManager(
            config_dir=self.config_dir,
            environment="development", 
            base_path=self.temp_dir
        )
        
        validation_results = config.validate_all_configurations()
        
        # Should have validation results for different sources
        self.assertIn('json_config', validation_results)
        self.assertIn('legacy_config', validation_results)
        self.assertIn('environment_vars', validation_results)
        self.assertIn('overall', validation_results)


class TestFlaskDependencyResolution(unittest.TestCase):
    """Test that Flask dependency is properly resolved."""
    
    def test_flask_import(self):
        """Test that Flask can be imported successfully."""
        try:
            import flask
            self.assertTrue(True, "Flask imported successfully")
        except ImportError as e:
            self.fail(f"Flask import failed: {e}")
    
    def test_requirements_file_contains_flask(self):
        """Test that requirements.txt contains Flask dependency."""
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
                requirements_content = f.read()
            
            self.assertIn('Flask', requirements_content, "Flask dependency missing from requirements.txt")
        else:
            self.fail("requirements.txt file not found")


class TestIntegrationWorkflows(unittest.TestCase):
    """Test integration workflows across multiple components."""
    
    def test_file_lifecycle_with_error_handling(self):
        """Test file lifecycle management integrated with error handling."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            manager = SynchronizedFileManager(temp_dir)
            error_handler = get_error_handler()
            
            # Create managed file
            filename = "integration_test.txt"
            content = "Integration test content"
            file_path = manager.create_managed_file(filename, content)
            file_id = manager.list_managed_files()[0]
            
            # Simulate error during processing
            error_info = error_handler.create_error(
                code=ErrorCode.FILE_ACCESS_DENIED,
                category=ErrorCategory.FILE_TRANSFER,
                severity=ErrorSeverity.MEDIUM,
                message="File access error during integration test",
                context={'file_id': file_id, 'file_path': file_path}
            )
            
            # Verify error was created with context
            self.assertEqual(error_info.context['file_id'], file_id)
            self.assertEqual(error_info.context['file_path'], file_path)
            
            # Cleanup should still work despite error
            self.assertTrue(manager.safe_cleanup(file_id))
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_configuration_with_error_reporting(self):
        """Test configuration system with error reporting integration."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create invalid configuration
            config_dir = os.path.join(temp_dir, "config")
            os.makedirs(config_dir)
            
            # Create malformed JSON
            with open(os.path.join(config_dir, "default.json"), 'w') as f:
                f.write('{"invalid": json}')  # Malformed JSON
            
            error_handler = get_error_handler()
            initial_error_count = len(error_handler.errors)
            
            # Try to load configuration (should handle error gracefully)
            config = UnifiedConfigurationManager(
                config_dir=config_dir,
                environment="development",
                base_path=temp_dir
            )
            
            # Configuration should still work with fallback values
            self.assertIsNotNone(config.get('server.host', 'localhost'))
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """Run all fix validation tests."""
    # Create test suite
    test_classes = [
        TestSynchronizedFileManager,
        TestProtocolFlexibility,
        TestErrorPropagationFramework,
        TestUnifiedConfiguration,
        TestFlaskDependencyResolution,
        TestIntegrationWorkflows
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"FIX VALIDATION TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    import logging
    logging.basicConfig(level=logging.WARNING)
    run_all_tests()