# Running Tests

## Issue
When running tests from the project root directory, you might encounter the following error:
```
An error occurred: No module named 'utils.debug_setup'
```

This happens because the Python path is not correctly set up to find the `utils` module which is located inside the `FletV2` directory.

## Solutions

### Option 1: Run tests from the FletV2 directory
```bash
cd FletV2
python -m tests.integration.test_logs_integration
```

### Option 2: Use the run_tests.py script from project root
```bash
python FletV2/run_tests.py
```

### Option 3: Set PYTHONPATH manually
```bash
cd FletV2
PYTHONPATH=. python -m tests.integration.test_logs_integration
```

### Option 4: Use the fletv2_import_fix.py module
Add this import at the top of your script before importing any FletV2 modules:
```python
import fletv2_import_fix  # This will fix the import paths
from utils.debug_setup import setup_terminal_debugging
```

## Running All Tests
To run all tests, use:
```bash
cd FletV2
python -m unittest discover tests
```

Or from the project root:
```bash
python FletV2/run_tests.py
```

## Test Structure
- Unit tests: `FletV2/tests/unit/`
- Integration tests: `FletV2/tests/integration/`
- Test utilities: `FletV2/tests/integration_utils.py`

The tests use a mock database by default. To run tests with a real server, set the appropriate environment variables.