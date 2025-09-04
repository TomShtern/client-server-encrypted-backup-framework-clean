# FletV2 Utility Modules

## Overview

The FletV2 application includes several utility modules that provide common functionality across the application. This document describes each utility module and its API.

## Debug Setup (`utils/debug_setup.py`)

Provides centralized logging and debugging functionality.

### Functions

#### `setup_terminal_debugging(log_level: int = logging.DEBUG, logger_name: Optional[str] = None) -> logging.Logger`

Set up centralized terminal debugging for the application.

Parameters:
- `log_level` (int): Logging level (default: DEBUG)
- `logger_name` (str, optional): Name for the logger (default: calling module name)

Returns:
- `logging.Logger`: Configured logger instance

#### `get_logger(name: str) -> logging.Logger`

Create a configured logger for consistent logging across the application.

Parameters:
- `name` (str): Name of the logger, typically `__name__`

Returns:
- `logging.Logger`: Configured logger instance

### Features

- Centralized logging configuration
- Global exception handling with full traceback logging
- Consistent log format with timestamps
- Module-specific logger instances

## Server Bridge (`utils/server_bridge.py`)

Provides production-ready server communication.

### Class: `ModularServerBridge`

#### `__init__(self, host: str = "127.0.0.1", port: int = 1256)`

Initialize modular server bridge.

Parameters:
- `host` (str): Server host
- `port` (int): Server port

#### Methods

All methods follow the common server bridge interface. See `docs/server_bridge_api.md` for details.

## Simple Server Bridge (`utils/simple_server_bridge.py`)

Provides fallback server communication with mock data.

### Class: `SimpleServerBridge`

#### `__init__(self)`

Initialize simple server bridge.

#### Methods

All methods follow the common server bridge interface. See `docs/server_bridge_api.md` for details.

## Factory Functions

Both server bridge modules include factory functions for easy instantiation:

```python
# Create modular server bridge
from utils.server_bridge import create_modular_server_bridge
bridge = create_modular_server_bridge(host="127.0.0.1", port=1256)

# Create simple server bridge
from utils.simple_server_bridge import create_simple_server_bridge
bridge = create_simple_server_bridge()
```

## Best Practices

### Logging

1. **Use `get_logger`**: Create module-specific loggers using `get_logger(__name__)`
2. **Appropriate Log Levels**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
3. **Structured Messages**: Include relevant context in log messages
4. **Exception Logging**: Use `exc_info=True` for exception logging

### Server Communication

1. **Graceful Degradation**: Handle server communication failures gracefully
2. **Fallback Data**: Provide consistent mock data when server is unavailable
3. **Consistent Interface**: Maintain the same interface across all server bridge implementations
4. **Error Handling**: Catch and log all exceptions in server communication methods

### Factory Functions

1. **Consistent Naming**: Use `create_*` naming convention for factory functions
2. **Error Handling**: Handle initialization errors in factory functions
3. **Return Types**: Return appropriate object instances or None on failure