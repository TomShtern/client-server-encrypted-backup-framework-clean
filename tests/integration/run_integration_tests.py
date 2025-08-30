#!/usr/bin/env python3
"""
Integration Test Runner for CyberBackup 3.0
==========================================

This script runs all integration tests for the complete API → C++ client → server flow.
It provides comprehensive testing with detailed reporting and cleanup.

Usage:
    python tests/integration/run_integration_tests.py [options]

Options:
    --quick         Run only basic integration tests
    --performance   Include performance tests
    --errors        Include error scenario tests
    --all           Run all test suites (default)
    --verbose       Verbose output
    --report        Generate detailed test report
"""

import unittest
import sys
import os
import time
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List
import subprocess

# Setup standardized import paths
from Shared.path_utils import setup_imports
setup_imports()

from Shared.logging_utils import setup_dual_logging


class IntegrationTestRunner:
    """Comprehensive integration test runner"""
    
    def __init__(self, verbose: bool = False, generate_report: bool = False):
        self.verbose = verbose
        self.generate_report = generate_report
        self.test_results: Dict[str, Any] = {}
        self.start_time = time.time()
        
        # Setup logging
        self.logger, self.log_file = setup_dual_logging(
            logger_name="integration_test_runner",
            server_type="integration-runner",
            console_level=20 if not verbose else 10,
            file_level=10
        )
        
        self.logger.info("Integration Test Runner initialized")
    
    def run_test_suite(self, test_module: str, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite and return results"""
        self.logger.info(f"Running test suite: {suite_name}")
        
        # Discover and run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_module)
        
        # Custom test result to capture detailed information
        result = unittest.TestResult()
        
        start_time = time.time()
        suite.run(result)
        duration = time.time() - start_time
        
        # Compile results
        suite_results = {
            'suite_name': suite_name,
            'module': test_module,
            'duration': duration,
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1),
            'failure_details': [{'test': str(test), 'traceback': traceback} 
                              for test, traceback in result.failures],
            'error_details': [{'test': str(test), 'traceback': traceback} 
                            for test, traceback in result.errors]
        }
        
        self.logger.info(f"Suite {suite_name} completed: "
                        f"{result.testsRun} tests, "
                        f"{len(result.failures)} failures, "
                        f"{len(result.errors)} errors")
        
        return suite_results
    
    def run_basic_tests(self) -> Dict[str, Any]:
        """Run basic integration tests"""
        return self.run_test_suite(
            'tests.integration.test_complete_flow',
            'Basic Integration Tests'
        )
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance integration tests"""
        return self.run_test_suite(
            'tests.integration.test_performance_flow',
            'Performance Integration Tests'
        )
    
    def run_error_scenario_tests(self) -> Dict[str, Any]:
        """Run error scenario tests"""
        return self.run_test_suite(
            'tests.integration.test_error_scenarios',
            'Error Scenario Tests'
        )
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met for running tests"""
        self.logger.info("Checking test prerequisites...")
        
        # Check if required files exist
        required_files = [
            project_root / "cyberbackup_api_server.py",
            project_root / "python_server" / "server" / "server.py",
            project_root / "build" / "Release" / "EncryptedBackupClient.exe"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            self.logger.error("Missing required files:")
            for file_path in missing_files:
                self.logger.error(f"  - {file_path}")
            return False
        
        # Check if ports are available
        import socket
        required_ports = [9090, 1256]
        
        for port in required_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
            except OSError:
                self.logger.warning(f"Port {port} is already in use - tests may conflict")
        
        self.logger.info("Prerequisites check completed")
        return True
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        
        # Calculate overall statistics
        total_tests = sum(result.get('tests_run', 0) for result in self.test_results.values())
        total_failures = sum(result.get('failures', 0) for result in self.test_results.values())
        total_errors = sum(result.get('errors', 0) for result in self.test_results.values())
        total_skipped = sum(result.get('skipped', 0) for result in self.test_results.values())
        
        overall_success_rate = (total_tests - total_failures - total_errors) / max(total_tests, 1)
        
        # Generate report
        report = []
        report.append("=" * 80)
        report.append("CYBERBACKUP 3.0 INTEGRATION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Duration: {total_duration:.2f} seconds")
        report.append("")
        
        # Overall summary
        report.append("OVERALL SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tests Run: {total_tests}")
        report.append(f"Passed: {total_tests - total_failures - total_errors}")
        report.append(f"Failed: {total_failures}")
        report.append(f"Errors: {total_errors}")
        report.append(f"Skipped: {total_skipped}")
        report.append(f"Success Rate: {overall_success_rate:.1%}")
        report.append("")
        
        # Suite-by-suite breakdown
        report.append("SUITE BREAKDOWN")
        report.append("-" * 40)
        
        for suite_name, results in self.test_results.items():
            report.append(f"\n{suite_name}:")
            report.append(f"  Duration: {results.get('duration', 0):.2f}s")
            report.append(f"  Tests: {results.get('tests_run', 0)}")
            report.append(f"  Failures: {results.get('failures', 0)}")
            report.append(f"  Errors: {results.get('errors', 0)}")
            report.append(f"  Success Rate: {results.get('success_rate', 0):.1%}")
            
            # Show failure details if any
            if results.get('failure_details'):
                report.append("  Failures:")
                for failure in results['failure_details']:
                    report.append(f"    - {failure['test']}")
            
            if results.get('error_details'):
                report.append("  Errors:")
                for error in results['error_details']:
                    report.append(f"    - {error['test']}")
        
        # Recommendations
        report.append("\nRECOMMENDATIONS")
        report.append("-" * 40)
        
        if overall_success_rate >= 0.95:
            report.append("✅ Excellent! Integration tests are passing reliably.")
        elif overall_success_rate >= 0.80:
            report.append("⚠️  Good, but some issues detected. Review failed tests.")
        else:
            report.append("❌ Significant issues detected. Immediate attention required.")
        
        if total_failures > 0:
            report.append(f"• Address {total_failures} test failures")
        
        if total_errors > 0:
            report.append(f"• Fix {total_errors} test errors")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, report: str):
        """Save test report to file"""
        report_file = project_root / "tests" / "integration" / "test_report.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Also save JSON results
        json_file = project_root / "tests" / "integration" / "test_results.json"
        with open(json_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'results': self.test_results,
                'summary': {
                    'total_tests': sum(r.get('tests_run', 0) for r in self.test_results.values()),
                    'total_failures': sum(r.get('failures', 0) for r in self.test_results.values()),
                    'total_errors': sum(r.get('errors', 0) for r in self.test_results.values()),
                    'overall_success_rate': sum(r.get('success_rate', 0) for r in self.test_results.values()) / max(len(self.test_results), 1)
                }
            }, f, indent=2)
        
        self.logger.info(f"Test report saved to: {report_file}")
        self.logger.info(f"Test results saved to: {json_file}")


def main():
    """Main entry point for integration test runner"""
    parser = argparse.ArgumentParser(description='Run CyberBackup 3.0 integration tests')
    parser.add_argument('--quick', action='store_true', 
                       help='Run only basic integration tests')
    parser.add_argument('--performance', action='store_true',
                       help='Include performance tests')
    parser.add_argument('--errors', action='store_true',
                       help='Include error scenario tests')
    parser.add_argument('--all', action='store_true', default=True,
                       help='Run all test suites (default)')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--report', action='store_true',
                       help='Generate detailed test report')
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = IntegrationTestRunner(verbose=args.verbose, generate_report=args.report)
    
    # Check prerequisites
    if not runner.check_prerequisites():
        print("❌ Prerequisites check failed. Cannot run integration tests.")
        return 1
    
    print("🚀 Starting CyberBackup 3.0 Integration Tests...")
    print("=" * 60)
    
    # Determine which test suites to run
    run_basic = args.quick or args.all
    run_performance = args.performance or args.all
    run_errors = args.errors or args.all
    
    # Run test suites
    try:
        if run_basic:
            print("📋 Running Basic Integration Tests...")
            runner.test_results['basic'] = runner.run_basic_tests()
        
        if run_performance:
            print("⚡ Running Performance Tests...")
            runner.test_results['performance'] = runner.run_performance_tests()
        
        if run_errors:
            print("🔥 Running Error Scenario Tests...")
            runner.test_results['errors'] = runner.run_error_scenario_tests()
        
        # Generate and display report
        report = runner.generate_test_report()
        print("\n" + report)
        
        if args.report:
            runner.save_report(report)
        
        # Determine exit code based on results
        total_failures = sum(r.get('failures', 0) for r in runner.test_results.values())
        total_errors = sum(r.get('errors', 0) for r in runner.test_results.values())
        
        if total_failures == 0 and total_errors == 0:
            print("✅ All integration tests passed!")
            return 0
        else:
            print(f"❌ Integration tests completed with {total_failures} failures and {total_errors} errors")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠️  Integration tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Integration test runner failed: {e}")
        return 1


if __name__ == '__main__':  # pragma: no cover - manual execution helper
    main()
