# FletV2 Server Bridge API Documentation

## Overview

The FletV2 application uses a server bridge pattern to communicate with the backend server. This document describes the API methods available in both the `ModularServerBridge` (production) and `SimpleServerBridge` (fallback) implementations.

## Common Interface

Both server bridge implementations provide the same interface to ensure compatibility:

### Initialization

```python
# Production bridge
from utils.server_bridge import ModularServerBridge
bridge = ModularServerBridge(host="127.0.0.1", port=1256)

# Fallback bridge
from utils.simple_server_bridge import SimpleServerBridge
bridge = SimpleServerBridge()
```

### Methods

#### `get_clients() -> List[Dict[str, Any]]`

Returns a list of client dictionaries with the following structure:
```python
{
    "client_id": str,          # Unique client identifier
    "address": str,            # Client IP address and port
    "status": str,             # Connection status ("Connected", "Registered", "Offline")
    "connected_at": str,       # Connection timestamp (ISO format)
    "last_activity": str       # Last activity timestamp (ISO format)
}
```

#### `get_files() -> List[Dict[str, Any]]`

Returns a list of file dictionaries with the following structure:
```python
{
    "file_id": str,            # Unique file identifier
    "filename": str,           # Name of the file
    "size": int,               # File size in bytes
    "uploaded_at": str,        # Upload timestamp (ISO format)
    "client_id": str           # ID of the client that uploaded the file
}
```

#### `get_database_info() -> Dict[str, Any]`

Returns database information:
```python
{
    "status": str,             # Database status ("Connected", "Disconnected")
    "tables": int,             # Number of tables
    "records": int,            # Total number of records
    "size": str                # Database size (human-readable format)
}
```

#### `get_logs() -> List[Dict[str, Any]]`

Returns a list of log entries:
```python
{
    "id": int,                 # Log entry ID
    "timestamp": str,          # Log timestamp (ISO format)
    "level": str,              # Log level ("INFO", "WARNING", "ERROR", etc.)
    "component": str,          # Component that generated the log
    "message": str             # Log message
}
```

#### `get_server_status() -> Dict[str, Any]`

Returns server status information:
```python
{
    "server_running": bool,    # Whether the server is running
    "port": int,               # Server port
    "uptime": str,             # Server uptime (human-readable format)
    "total_transfers": int,    # Total number of file transfers
    "active_clients": int,     # Number of currently connected clients
    "total_files": int,        # Total number of files
    "storage_used": str        # Storage used (human-readable format)
}
```

#### `get_recent_activity() -> List[Dict[str, Any]]`

Returns recent server activity:
```python
{
    "time": str,               # Activity time (HH:MM format)
    "text": str,               # Activity description
    "type": str                # Activity type ("success", "info", "warning")
}
```

#### `disconnect_client(client_id: str) -> bool`

Disconnects a client from the server.

Parameters:
- `client_id` (str): ID of the client to disconnect

Returns:
- `bool`: True if successful, False otherwise

#### `delete_client(client_id: str) -> bool`

Deletes a client from the server.

Parameters:
- `client_id` (str): ID of the client to delete

Returns:
- `bool`: True if successful, False otherwise

#### `is_connected() -> bool`

Checks if the server bridge is connected to the server.

Returns:
- `bool`: True if connected, False otherwise

## Implementation Differences

### ModularServerBridge

- Makes actual HTTP requests to the server
- Uses the `requests` library for communication
- Falls back to mock data if server is unreachable
- Supports real-time data updates

### SimpleServerBridge

- Returns mock data for all methods
- No network communication
- Used as a fallback when the server is unavailable
- Provides consistent data structure for UI development

## Error Handling

Both implementations include comprehensive error handling:

- Network errors are caught and logged
- Fallback data is provided when server communication fails
- All methods return consistent data structures even in error conditions