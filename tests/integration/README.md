# Integration Tests for CyberBackup 3.0

This directory contains comprehensive integration tests for the complete API → C++ client → server flow.

## Overview

The integration tests validate the entire end-to-end workflow:

```
Web UI → Flask API (9090) → C++ Client (subprocess) → Python Server (1256) → File Storage
```

## Test Suites

### 1. Basic Integration Tests (`test_complete_flow.py`)
- **Purpose**: Validate core functionality works end-to-end
- **Coverage**:
  - Small file transfers (< 1KB)
  - Medium file transfers (~64KB) 
  - Large file transfers (~1MB)
  - Concurrent transfers
  - Error handling for invalid files
  - Server connection failures
  - Observability integration
  - Health endpoint validation

### 2. Performance Tests (`test_performance_flow.py`)
- **Purpose**: Validate performance characteristics and resource usage
- **Coverage**:
  - Transfer speed benchmarks
  - Memory usage monitoring
  - Concurrent load testing
  - Resource cleanup verification
  - Performance degradation detection

### 3. Error Scenario Tests (`test_error_scenarios.py`)
- **Purpose**: Validate error handling and edge cases
- **Coverage**:
  - Network failures and timeouts
  - Invalid input handling (malformed JSON, missing fields)
  - Corrupted file uploads
  - Resource exhaustion scenarios
  - Server shutdown during transfers
  - Rate limiting and rapid requests

## Quick Start

### Run All Tests
```bash
# From project root
python tests/integration/run_integration_tests.py --all --verbose --report
```

### Run Specific Test Suites
```bash
# Basic tests only
python tests/integration/run_integration_tests.py --quick

# Performance tests
python tests/integration/run_integration_tests.py --performance

# Error scenario tests  
python tests/integration/run_integration_tests.py --errors
```

### Run Individual Test Files
```bash
# Basic integration tests
python -m unittest tests.integration.test_complete_flow -v

# Performance tests
python -m unittest tests.integration.test_performance_flow -v

# Error scenario tests
python -m unittest tests.integration.test_error_scenarios -v
```

## Prerequisites

Before running integration tests, ensure:

1. **Build System**: C++ client is built
   ```bash
   # Build the C++ client
   mkdir build && cd build
   cmake .. && cmake --build . --config Release
   ```

2. **Dependencies**: Python dependencies installed
   ```bash
   pip install -r requirements.txt
   ```

3. **Ports Available**: Ports 9090 (API) and 1256 (backup server) are free

4. **File Structure**: Required files exist:
   - `cyberbackup_api_server.py`
   - `src/server/server.py`
   - `build/Release/EncryptedBackupClient.exe`

## Test Infrastructure

### IntegrationTestFramework
The base framework provides:
- **Server Management**: Automatic startup/shutdown of API and backup servers
- **Port Management**: Availability checking and conflict detection
- **File Management**: Test file creation and cleanup
- **Health Monitoring**: Server health verification
- **Logging**: Comprehensive test logging

### Test Data Management
- Test files are created in `tests/integration/test_data/`
- Received files are stored in `received_files/`
- All test files are automatically cleaned up after tests
- File integrity is verified using SHA256 hashes

## Test Results and Reporting

### Console Output
Tests provide real-time progress and results:
```
🚀 Starting CyberBackup 3.0 Integration Tests...
📋 Running Basic Integration Tests...
⚡ Running Performance Tests...
🔥 Running Error Scenario Tests...
```

### Detailed Reports
When using `--report` flag:
- **Text Report**: `tests/integration/test_report.txt`
- **JSON Results**: `tests/integration/test_results.json`

### Report Contents
- Overall test statistics
- Suite-by-suite breakdown
- Performance metrics
- Failure/error details
- Recommendations for fixes

## Understanding Test Results

### Success Criteria
- **Excellent**: ≥95% success rate
- **Good**: ≥80% success rate  
- **Needs Attention**: <80% success rate

### Common Issues and Solutions

#### Port Conflicts
```
Error: Port 9090 is already in use
Solution: Stop existing services or change port configuration
```

#### Missing C++ Client
```
Error: build/Release/EncryptedBackupClient.exe not found
Solution: Build the C++ client first
```

#### Server Startup Failures
```
Error: Backup server failed to start
Solution: Check logs for specific error, ensure database is accessible
```

#### File Transfer Failures
```
Error: File not received by server
Solution: Check network connectivity, server logs, and file permissions
```

## Performance Benchmarks

### Expected Performance (Reference System)
- **Small files (1KB)**: <30 seconds, >100 B/s
- **Medium files (64KB)**: <60 seconds, >1000 B/s  
- **Large files (1MB)**: <120 seconds, >5000 B/s
- **Memory usage**: <100MB growth for large files
- **Concurrent transfers**: 3 simultaneous transfers should complete

### Performance Monitoring
Tests automatically collect:
- Transfer duration and speed
- Memory usage patterns
- Resource cleanup efficiency
- System resource utilization

## Extending the Tests

### Adding New Test Cases
1. Create test method in appropriate test class
2. Use framework helper methods for setup
3. Follow naming convention: `test_descriptive_name`
4. Include proper assertions and cleanup

### Adding New Test Suites
1. Create new test file in `tests/integration/`
2. Extend `IntegrationTestFramework` if needed
3. Add to `run_integration_tests.py`
4. Update this README

### Custom Test Scenarios
```python
def test_custom_scenario(self):
    """Test custom scenario"""
    # Create test data
    test_file = self.framework.create_test_file(size, pattern)
    
    # Perform operations
    self.framework._perform_file_transfer(test_file, username)
    
    # Verify results
    received_file = self.framework.find_received_file(filename, username)
    self.assertIsNotNone(received_file)
```

## Troubleshooting

### Debug Mode
Run with maximum verbosity:
```bash
python tests/integration/run_integration_tests.py --all --verbose
```

### Check Logs
Integration test logs are in `logs/integration-test-*.log`

### Manual Verification
1. Start servers manually
2. Check health endpoints:
   - `http://localhost:9090/health`
   - `http://localhost:9090/api/observability/health`
3. Verify file transfers manually through web UI

### Common Debug Steps
1. Verify all prerequisites are met
2. Check port availability
3. Review server startup logs
4. Test individual components separately
5. Check file permissions and disk space

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Integration Tests
  run: |
    python tests/integration/run_integration_tests.py --all --report
    
- name: Upload Test Results
  uses: actions/upload-artifact@v3
  with:
    name: integration-test-results
    path: tests/integration/test_*.json
```

### Exit Codes
- `0`: All tests passed
- `1`: Some tests failed
- `130`: Tests interrupted by user

## Contributing

When adding new integration tests:
1. Follow existing patterns and conventions
2. Include comprehensive error handling
3. Add appropriate documentation
4. Test on multiple environments
5. Update this README if needed

For questions or issues with integration tests, check the project documentation or create an issue.
