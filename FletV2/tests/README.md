# FletV2 Tests

This directory contains unit tests for the FletV2 application.

## Running Tests

To run all tests, execute the following command from the FletV2 directory:

```bash
python run_tests.py
```

## Test Structure

- `test_theme.py` - Tests for the theme module
- `test_server_bridge.py` - Tests for the server bridge implementations

## Test Coverage

The tests cover:

1. Theme application and management
2. Server bridge functionality
3. Data structure validation
4. Error handling

## Adding New Tests

To add new tests:

1. Create a new test file with the naming pattern `test_*.py`
2. Import the necessary modules
3. Create test classes that inherit from `unittest.TestCase`
4. Add test methods that start with `test_`
5. Run the tests to ensure they pass