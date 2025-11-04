# Client-Server Encrypted Backup Framework - Copilot Instructions

## Project Overview

You are assisting with CyberBackup 3.0, a secure file backup system with dual-GUI architecture. The system includes a Python backup server, FletV2 desktop GUI, web API server, and C++ client with robust encryption and verification.

## Key Technical Context

### Architecture
- **BackupServer**: Python server handling clients on port 1256 (TCP binary protocol)
- **FletV2 GUI**: Desktop admin interface with Material Design 3 (integrated server)
- **API Server**: Flask server for web interface on port 9090
- **C++ Client**: Binary protocol implementation for file transfers
- **Database**: Shared SQLite (`defensive.db`) with connection pooling

### Security Implementation
- RSA-1024 key exchange with PKCS1_OAEP padding
- AES-256-CBC file encryption with zero IV (per protocol spec)
- CRC32 integrity verification
- Binary protocol with structured message handling

## File Structure and Navigation

### Primary Components
- `python_server/server/` - Core server implementation
  - `server.py` - Main server class and startup
  - `request_handlers.py` - Protocol message processing
  - `file_transfer.py` - Multi-packet file transfer management
  - `database.py` - SQLite operations with connection pooling
- `FletV2/` - Desktop GUI with integrated server
  - `start_with_server.py` - GUI launcher with embedded server
- `api_server/` - Web API bridge
  - `cyberbackup_api_server.py` - Flask API implementation

## Code Completion Patterns

### When Suggesting Server Code
- Use the modular RequestHandler pattern for new protocol handlers
- Follow existing exception handling with ProtocolError, ServerError, etc.
- Maintain thread safety with client locks and atomic operations
- Use the existing database manager for data persistence
- Follow the retry decorator pattern for transient failures

### When Suggesting GUI Code
- Use the ServerBridge pattern for FletV2 direct server calls
- Follow Material Design 3 principles in Flet implementations
- Use async patterns to prevent UI blocking
- Maintain consistency between desktop and web interfaces

### When Suggesting Security Code
- Preserve existing AES-256-CBC encryption patterns
- Maintain RSA key exchange implementation with PKCS1_OAEP
- Follow secure file handling with validation and sanitization
- Keep the existing CRC32 verification approach

## Important Implementation Details

### Critical Behaviors
- Network listener must be explicitly started (`server_instance.start()`) for C++ client connectivity
- File transfers use multi-packet protocol with reassembly and duplicate detection
- Database uses connection pooling for concurrent GUI access
- Both GUIs share the same database with file-level locking

### Configuration Files
- `config.json` - System-wide settings
- `transfer.info` - Client connection configuration
- `requirements.txt` - Python dependencies
- `port.info` - Server port configuration (fallback to 1256)

## Common Tasks and Patterns

### Adding New Protocol Requests
1. Define request/response codes in `protocol.py`
2. Add handler method to `RequestHandler` class
3. Register in the `handler_map` dictionary
4. Follow existing error handling patterns
5. Update client to handle new protocol messages

### File Transfer Operations
- Use multi-packet approach with proper reassembly logic
- Implement duplicate packet detection
- Validate filenames for security (path traversal prevention)
- Perform CRC verification after decryption
- Store files atomically with validation

### Database Operations
- Use DatabaseManager for all database interactions
- Implement connection pooling patterns
- Use retry mechanisms for transient failures
- Follow transaction patterns for data consistency

## Error Handling and Logging

### Logging Levels
- DEBUG: Detailed protocol and packet information
- INFO: Connections, transfers, and system events
- WARNING: Recoverable issues and validation problems
- ERROR: Operation failures and system errors
- CRITICAL: System startup failures and security issues

### Common Error Scenarios
- Database lock issues (use connection pooling)
- Network timeout during key exchange
- Invalid file format or encryption issues
- Client authentication failures
- Protocol version mismatch

## Integration Points

### Server-Client Protocol
- Binary protocol with fixed-size fields and null-terminated strings
- Client ID in request headers for authentication
- AES key encrypted with RSA public key during session setup
- Multi-packet file transfers with sequence numbers

### GUI-Server Communication
- FletV2: Direct method calls via ServerBridge (no network overhead)
- Web API: HTTP requests to Flask endpoints
- Both update shared database for consistency

## Troubleshooting Tips

### Connection Issues
- Verify network server is started with `server.start()`
- Check that ports 1256 and 9090 are available
- Confirm client configuration in `transfer.info`

### Database Issues
- Use connection pooling to handle concurrent access
- Check file permissions for database and file storage directories
- Verify database schema matches the application expectations

### Security Issues
- Ensure proper AES key generation and distribution
- Verify RSA key exchange and encryption/decryption
- Validate file integrity with CRC32