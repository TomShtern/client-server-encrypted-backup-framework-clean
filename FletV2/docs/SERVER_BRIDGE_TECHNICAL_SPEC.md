# FletV2 Server Bridge Technical Specification

## Overview

The Server Bridge is a critical component of the FletV2 architecture that provides a unified interface between the GUI and backend server operations. It implements a dual-mode system supporting both real server connections and persistent mock data for development.

## Architecture

### Dual-Mode Design

```
ServerBridge
├── Live Mode (Real Server)
│   ├── Direct function calls to real server
│   ├── Real-time data from actual operations
│   └── Authentic server responses
└── Fallback Mode (Mock Data)
    ├── Persistent mock data generation
    ├── Realistic data simulation
    └── Disk persistence for consistency
```

### Initialization

```python
class ServerBridge:
    def __init__(self, real_server_instance: Optional[BackupServer] = None):
        self.real_server = real_server_instance
        
        if self.real_server:
            print("[ServerBridge] Initialized in LIVE mode, connected to the real server.")
        else:
            print("[ServerBridge] Initialized in FALLBACK mode. Will use persistent mock data.")
            
        # Initialize consolidated mock data generator with persistence
        self.mock_generator = MockDataGenerator(num_clients=45, persist_to_disk=True)
```

## Core Principles

### 1. Operation Routing
Every operation follows a standardized pattern:
1. Check if real server is available and supports the operation
2. Attempt real server operation with proper error handling
3. Fall back to mock data if real server fails or is unavailable
4. Return standardized response format

### 2. Standardized Responses
All operations return consistent response format:
```python
{
    'success': bool,           # Operation success status
    'message': str,            # Human-readable message
    'mode': str,              # 'real' or 'mock'
    'timestamp': float,        # Unix timestamp of response
    'data': Any,              # Optional data payload
    # Additional fields based on operation type
}
```

### 3. Error Handling
Comprehensive error handling with graceful degradation:
- Try real server operation first
- Catch and log all exceptions
- Fall back to mock data on any failure
- Return consistent error responses

## API Coverage

### Client Management
- `get_all_clients_from_db()` / `get_clients_async()`
- `disconnect_client(client_id)` / `disconnect_client_async(client_id)`
- `resolve_client(client_id)`
- `get_client_details(client_id)`
- `delete_client(client_id)`

### File Management
- `get_client_files(client_id)` / `get_client_files_async(client_id)`
- `get_files()` / `get_files_async()`
- `delete_file(file_id)` / `delete_file_async(file_id)`
- `download_file(file_id, destination_path)` / `download_file_async(file_id, destination_path)`
- `verify_file(file_id)` / `verify_file_async(file_id)`

### Database Operations
- `get_database_info()` / `get_database_info_async()`
- `get_table_data(table_name)` / `get_table_data_async(table_name)`
- `update_row(table_name, row_id, updated_data)`
- `delete_row(table_name, row_id)`

### Server Status
- `get_server_status()` / `get_server_status_async()`
- `get_system_status()`
- `get_recent_activity()` / `get_recent_activity_async()`
- `start_server_async()` / `stop_server_async()`

### Logging
- `get_logs()`
- `test_connection()` / `test_connection_async()`

## Mock Data System

### Features
- Thread-safe operations with proper locking
- Referential integrity with cascading operations
- Persistent storage to disk between sessions
- Realistic data generation with time-based changes
- Comprehensive mock data for all system components

### Data Structures

```python
@dataclass
class MockClient:
    id: str
    name: str
    ip_address: str
    status: str  # connected, disconnected, error
    last_seen: datetime
    files_count: int
    total_size: int
    connection_time: Optional[datetime] = None
    version: str = "1.0.0"
    platform: str = "unknown"

@dataclass
class MockFile:
    id: str
    client_id: str
    name: str
    path: str
    size: int
    hash: str
    created: datetime
    modified: datetime
    status: str  # uploaded, verified, error
    backup_count: int = 1
    last_backup: Optional[datetime] = None
```

### Persistence
- JSON-based storage with proper serialization
- Automatic loading/saving of state
- Referential integrity maintained across sessions
- Thread-safe file operations

## Integration Patterns

### View Integration
Views use server-mediated operations through utility patterns:

```python
# Data loading (3 lines instead of 30+)
await server_ops.load_data_operation(
    state_key="clients",
    server_operation="get_clients_async",
    fallback_data=mock_data
)

# User actions (4 lines instead of 20+)
await server_ops.action_operation(
    action_name="delete_client",
    server_operation="delete_client_async",
    operation_data=client_data,
    success_message="Client deleted successfully",
    refresh_keys=["clients", "files"]
)
```

### State Management Integration
Server bridge integrates with state manager for persistent updates:

```python
async def server_mediated_update(self, key: str, value: Any, server_operation: str = None):
    """Update state through server bridge for persistence"""
    if self.server_bridge and server_operation:
        try:
            # Call server operation if specified
            server_method = getattr(self.server_bridge, server_operation, None)
            if server_method:
                result = await server_method() if asyncio.iscoroutinefunction(server_method) else server_method()
                
                # Update state with server result if successful
                if isinstance(result, dict) and result.get('success'):
                    await self.update_async(key, result.get('data', value), source=f"server_{server_operation}")
                    return result
                else:
                    # Fallback to direct state update
                    await self.update_async(key, value, source="server_fallback")
                    return {'success': True, 'mode': 'fallback'}
            else:
                await self.update_async(key, value, source="server_fallback")
        except Exception as e:
            logger.error(f"Server operation {server_operation} failed: {e}")
            await self.update_async(key, value, source="server_error")
            return {'success': False, 'error': str(e)}
    else:
        # Direct state update when no server bridge available
        await self.update_async(key, value, source="direct")
        return {'success': True, 'mode': 'direct'}
```

## Performance Considerations

### 1. Direct Access
- No caching to prevent stale data issues
- Immediate UI updates after modifications
- Direct data access for optimal performance

### 2. Async Operations
- Non-blocking operations for UI responsiveness
- Parallel execution where appropriate
- Proper error handling in async contexts

### 3. Memory Efficiency
- Minimal memory footprint
- Proper cleanup of resources
- Efficient data structures

## Testing and Validation

### 1. Unit Testing
- Individual method testing for both real and mock modes
- Edge case validation with error conditions
- Performance benchmarking

### 2. Integration Testing
- End-to-end server communication validation
- Mock data consistency testing
- Cross-operation referential integrity

### 3. Compatibility Testing
- Backward compatibility with legacy interfaces
- Drop-in server integration validation
- Mock/Real mode parity verification

## Best Practices

### 1. Error Resilience
- Always provide graceful fallbacks
- Log all errors for debugging
- Return consistent response formats
- Handle edge cases appropriately

### 2. Performance Optimization
- Use direct access patterns
- Minimize unnecessary operations
- Implement proper async/await patterns
- Avoid blocking operations in UI thread

### 3. Code Maintainability
- Follow consistent naming conventions
- Use clear, descriptive method names
- Implement proper documentation
- Maintain clean separation of concerns

## Future Enhancements

### 1. Advanced Features
- Plugin architecture for extensible operations
- Advanced analytics and monitoring
- Offline mode with local caching

### 2. Performance Improvements
- Connection pooling for real server operations
- Advanced caching strategies
- Optimized data serialization

### 3. Security Enhancements
- Authentication and authorization
- Encrypted data transmission
- Audit logging and compliance

This technical specification provides a comprehensive overview of the Server Bridge system, detailing its architecture, implementation patterns, and integration with other components of the FletV2 application.