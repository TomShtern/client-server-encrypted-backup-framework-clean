# CyberBackup Pro - AI Coding Agent Instructions

## Architecture Overview
This is a 4-component encrypted backup system with a unique web-based architecture:

1. **Web UI** (`src/client/NewGUIforClient.html`) - Browser-based cyberpunk interface
2. **API Bridge** (`cyberbackup_api_server.py`) - Flask server bridging web UI to native client
3. **C++ Client** (`src/client/client.cpp`) - Command-line backup engine (RSA+AES encryption)
4. **Python Server** (`server/server.py`) - Backup storage server with custom TCP protocol

**Key Insight**: The web UI never talks directly to the C++ client or server - all communication flows through the Flask API bridge.

```
Web UI → Flask API → C++ Client (subprocess) → Python Server
        ↓                    ↓                    ↓
   HTTP API calls      transfer.info +
                      --batch flag        Custom TCP
                                        (Binary Protocol)
```

## Build System & Dependencies

### C++ Build System
- **CMake + vcpkg**: Uses vcpkg for dependency management with specific toolchain
- **Key Dependencies**: `boost-asio`, `boost-beast`, `cryptopp`, `zlib` (defined in `vcpkg.json`)
- **Build Commands**:
  ```bash
  cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"
  cmake --build build --config Release
  ```
- **Output**: `build/Release/EncryptedBackupClient.exe`
- **Windows Defines**: `WIN32_LEAN_AND_MEAN`, `NOMINMAX`, `_WIN32_WINNT=0x0601`

### Python Dependencies
- **Core**: `cryptography>=3.4.0`, `flask`, `flask-cors`, `psutil`
- **Crypto**: Uses both `cryptography` and `pycryptodome` for compatibility
- **GUI**: `tkinter` for server GUI

**Critical**: Always use vcpkg toolchain file - builds fail without it.

## Development Workflow

### Starting the System
1. **Full System**: `python launch_gui.py` (starts API server + opens browser)
2. **Server Only**: `python server/server.py` (starts backup server on port 1256)
3. **API Only**: `python cyberbackup_api_server.py` (starts bridge on port 9090)
4. **C++ Build**: `cmake --build build --config Release` (after vcpkg setup)

### Testing Strategy
- **Integration Tests**: `python tests/test_gui_upload.py` - tests complete chain
- **Server Tests**: `python tests/test_upload.py` - direct server testing
- **Build Validation**: `python scripts/master_test_suite.py` - comprehensive testing
- **Real File Verification**: All tests check actual file transfers in `server/received_files/`

### Debugging Patterns
- **Client Logs**: Monitor `client_debug.log` for C++ process activity
- **Server Logs**: Monitor `server.log` for server-side protocol activity
- **API Logs**: Flask console output shows request/response flow
- **Network Monitoring**: `RealBackupExecutor` checks active connections on port 1256

## Custom Protocol Implementation

### Binary Protocol Details
- **Request Codes**: `REQ_REGISTER(1025)`, `REQ_SEND_PUBLIC_KEY(1026)`, `REQ_SEND_FILE(1028)`, etc.
- **Response Codes**: `RESP_REG_OK(1600)`, `RESP_PUBKEY_AES_SENT(1602)`, `RESP_FILE_CRC(1603)`, etc.
- **Header Format**: 23-byte headers with UUID + version + code + payload_size
- **CRC Verification**: Uses Linux `cksum` compatible CRC32 algorithm
- **Version**: Both client and server use protocol version 3

### Message Structure
```cpp
// RequestHeader (23 bytes)
uint8_t  client_id[16];    // UUID (all zeros on registration)
uint8_t  version;          // Protocol version (3)
uint16_t code;             // Request type (little-endian)
uint32_t payload_size;     // Payload length (little-endian)
```

## Critical Code Patterns

### Process Integration Pattern
```python
# RealBackupExecutor launches C++ client with batch mode
self.backup_process = subprocess.Popen(
    [self.client_exe, "--batch"],  # Batch mode prevents hanging
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=os.path.dirname(os.path.abspath(self.client_exe))
)

# Monitor client_debug.log for real progress
def _monitor_client_log(self, log_file, timeout=300):
    # Parse log for status updates, completion indicators
    # Look for: 'connecting', 'registered', 'encrypting', 'complete'
```

### Configuration Management
```python
# transfer.info format (generated per operation)
def _generate_transfer_info(self, server_ip, server_port, username, file_path):
    with open("transfer.info", 'w') as f:
        f.write(f"{server_ip}:{server_port}\n")  # Line 1: server
        f.write(f"{username}\n")                 # Line 2: username
        f.write(f"{file_path}\n")                # Line 3: file path
```

### Status Synchronization Pattern
```python
# API server bridges C++ process status to web UI
backup_status = {
    'connected': check_backup_server_status(),
    'backing_up': process.poll() is None,
    'progress': parse_progress_from_log(),
    'file_size': os.path.getsize(file_path),
    'verification': verify_file_transfer()
}
```

### File Verification Pattern
```python
# Multi-layer verification in RealBackupExecutor
def _verify_file_transfer(self, original_file, username):
    verification = {
        'transferred': False,
        'size_match': False,
        'hash_match': False,
        'received_file': None
    }
    
    # Check server/received_files/ for actual transferred files
    # Compare file sizes and SHA256 hashes
    # Verify network activity occurred on port 1256
```

## Security Implementation

### Hybrid Encryption System
```cpp
// C++ Client (RSAWrapper.cpp, AESWrapper.cpp)
1. Generate RSA-1024 keypair (DER format)
2. Server sends RSA-encrypted AES-256 key
3. File encrypted with AES-256-CBC
4. Transport uses Base64 encoding over TCP
```

### Key Management
- **RSA Keys**: Generated via `generate_rsa_keys.py` in DER format
- **AES Keys**: 256-bit keys generated per session by server
- **Storage**: Client keys in `data/priv.key`, server keys in memory
- **Transport**: RSA public keys sent as 160-byte DER-encoded blobs

### CRC Verification
```cpp
// Uses Linux cksum compatible algorithm
uint32_t _calculate_crc(const bytes& data) {
    uint32_t crc = 0;
    for (byte b : data) {
        crc = (CRC32_TABLE[(crc >> 24) ^ b] ^ (crc << 8)) & 0xFFFFFFFF;
    }
    // Process data length into CRC
    // Return ~crc & 0xFFFFFFFF
}
```

## File Organization

### Source Code Structure
```
src/
├── client/
│   ├── main.cpp              # Entry point with --batch mode support
│   ├── client.cpp            # Core client logic (1490 lines)
│   ├── WebServerBackend.cpp  # HTTP API for HTML GUI
│   └── NewGUIforClient.html  # Cyberpunk web interface
├── wrappers/
│   ├── RSAWrapper.cpp        # Crypto++ RSA implementation
│   ├── AESWrapper.cpp        # Crypto++ AES implementation
│   └── Base64Wrapper.cpp     # Base64 encoding/decoding
└── utils/
    └── CompressionWrapper.cpp # Optional compression
```

### Server Components
```
server/
├── server.py           # Main server (973 lines)
├── protocol.py         # Binary protocol definitions
├── database.py         # SQLite client/file tracking
├── file_transfer.py    # File storage logic
├── client_manager.py   # Session management
├── network_server.py   # TCP socket handling
└── received_files/     # Stored encrypted files
```

### Configuration System
```
config/
├── default.json        # Base configuration
├── development.json    # Dev overrides
└── production.json     # Production settings

# Runtime configuration
transfer.info          # Generated per backup operation
me.info               # Client identity (optional)
```

## Performance & Connection Management

### Connection Limits
- **Max Concurrent Clients**: 50 (configurable via `MAX_CONCURRENT_CLIENTS`)
- **Socket Timeouts**: 60 seconds (`CLIENT_SOCKET_TIMEOUT`)
- **Session Timeouts**: 10 minutes (`CLIENT_SESSION_TIMEOUT`)
- **Semaphore Control**: `threading.Semaphore(MAX_CONCURRENT_CLIENTS)`

### Polling & Updates
- **GUI Status Polling**: Every 500ms to `/api/status`
- **Log Monitoring**: Real-time parsing of `client_debug.log`
- **Maintenance Tasks**: Every 60 seconds (cleanup, stats)
- **File Transfer Chunks**: 64KB chunks (`chunk_size: 65536`)

## Common Gotchas & Critical Issues

### Build System Issues
- **vcpkg Toolchain**: Build fails without `CMAKE_TOOLCHAIN_FILE` specification
- **Windows Defines**: Must include `WIN32_LEAN_AND_MEAN`, `NOMINMAX` for Boost compatibility
- **CMake Version**: Requires CMake 3.15+ with policy `CMP0167 NEW` for Boost

### Process Integration Issues
- **Executable Path**: `RealBackupExecutor` tries multiple paths: `build/Release/`, `client/`, etc.
- **Batch Mode**: Must use `--batch` flag to prevent C++ client from waiting for user input
- **Working Directory**: C++ client must run from directory containing `transfer.info`
- **Log Monitoring**: Progress parsing depends on specific log messages in `client_debug.log`

### Configuration Issues
- **transfer.info Generation**: Must be created per operation with exact 3-line format
- **Port Conflicts**: API server (9090), backup server (1256) - check availability
- **File Paths**: Use absolute paths to avoid working directory issues

### Network & Protocol Issues
- **Connection Verification**: Check port 1256 connectivity before starting transfers
- **Protocol Version**: Client and server must both use version 3
- **Binary Format**: All multi-byte values use little-endian format
- **CRC Calculation**: Must match Linux `cksum` algorithm exactly

### Testing & Verification Issues
- **Real File Transfers**: Always verify files actually appear in `server/received_files/`
- **Hash Verification**: Compare SHA256 hashes of original vs transferred files
- **Network Activity**: Verify actual TCP connections to port 1256 during transfers
- **Process Exit Codes**: Zero exit code doesn't guarantee successful transfer

## Integration Testing Pattern
```python
# Always test the complete chain
def test_full_backup_chain():
    1. Start backup server (python server/server.py)
    2. Start API server (python cyberbackup_api_server.py)
    3. Create test file with unique content signature
    4. Upload via web API (/api/start_backup)
    5. Monitor process execution and logs
    6. Verify file appears in server/received_files/
    7. Compare file hashes for integrity
    8. Check network activity and exit codes
```

When modifying this system, always test the complete web→API→C++→server chain. Component isolation testing misses critical integration issues. The real verification happens through actual file transfers and hash comparison, not just API responses.
