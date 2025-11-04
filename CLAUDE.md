# Client-Server Encrypted Backup Framework - Claude Instructions

## Project Context

You are working with CyberBackup 3.0, a comprehensive encrypted file backup system featuring dual-GUI architecture. This system includes a Python backup server, a FletV2 desktop GUI, and a web API server with security-focused file transfer capabilities.

## Architecture Overview

### System Components
1. **BackupServer** (python_server/server/): Handles client connections on port 1256
2. **FletV2 Desktop GUI** (FletV2/): Modern admin interface with Material Design 3
3. **API Server** (api_server/): Web interface bridge on port 9090
4. **C++ Client**: Binary protocol implementation for file transfers
5. **Database**: SQLite database (`defensive.db`) with connection pooling

### Security Features
- RSA-1024 for key exchange with PKCS1_OAEP padding
- AES-256-CBC for file encryption
- CRC32 verification for data integrity
- Custom binary protocol for secure communication

## Key Directories and Files

### Critical Files
- `python_server/server/server.py`: Main server implementation
- `python_server/server/request_handlers.py`: Protocol request processing
- `python_server/server/file_transfer.py`: Multi-packet file transfer management
- `FletV2/start_with_server.py`: Desktop GUI launcher with integrated server
- `api_server/cyberbackup_api_server.py`: Web API implementation
- `config.json`: System configuration

### Important Directories
- `python_server/server/`: Core server components
- `FletV2/`: Desktop GUI with Material Design 3
- `api_server/`: Web interface components
- `Shared/`: Cross-cutting utilities and common components

## Development Guidelines

### When Working with Server Code
- Always ensure the network listener is started with `server_instance.start()` for C++ client connectivity
- Use the modular structure (RequestHandler, FileTransferManager, DatabaseManager) for new features
- Follow the existing error handling and logging patterns
- Maintain thread safety in shared components

### When Working with GUI Code
- Use ServerBridge pattern for direct method calls in FletV2
- Follow Material Design 3 principles and the existing theme system
- Maintain consistency between desktop and web interfaces
- Use async patterns where appropriate to prevent UI blocking

### When Working with Security Features
- Maintain the existing encryption patterns (AES-256-CBC for files, RSA-1024 for key exchange)
- Follow the secure file handling patterns with atomic operations
- Preserve existing validation and sanitization procedures
- Keep security-related error handling distinct from regular errors

## Code Patterns and Conventions

### Request Handling Pattern
- Use the RequestHandler dispatch pattern for protocol requests
- Follow the existing handler structure with proper error handling
- Maintain the protocol specification for message formats

### Database Operations
- Use the DatabaseManager for all database interactions
- Implement retry mechanisms for transient failures
- Follow the connection pooling patterns
- Use atomic operations for file storage

### Logging Standards
- DEBUG: Protocol details, packet parsing, reassembly status
- INFO: Client connections/disconnections, file transfers, startup/shutdown
- WARNING: Recoverable errors, validation failures, retries
- ERROR: Failed operations, database errors, crypto failures
- CRITICAL: System failures, startup failures, security violations

## Troubleshooting Guidelines

### Common Issues
- If C++ clients can't connect, verify that `server_instance.start()` has been called
- Database locking issues can be resolved using the connection pooling system
- Check that ports 1256 and 9090 are available before starting servers
- Verify that the same database file is used by both GUI components

### Debugging Steps
1. Check server logs for connection and protocol errors
2. Verify database connectivity and permissions
3. Confirm encryption key exchange is working properly
4. Validate binary protocol message formats

## Integration Points

### Server-GUI Communication
- FletV2 uses direct method calls via ServerBridge (no API layer)
- Web GUI communicates through HTTP API endpoints
- Both interfaces access the same database but through different connection paths

### External Dependencies
- PyCryptodome for encryption operations
- SQLite for database storage
- Flet for desktop GUI
- Flask for web API
- psutil for system monitoring