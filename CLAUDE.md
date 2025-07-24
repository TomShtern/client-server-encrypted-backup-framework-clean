# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Client-Server Encrypted Backup Framework** implementing secure file transfer with RSA-1024 + AES-256-CBC encryption. The system uses a unique 4-component architecture:

1. **Web UI** (`src/client/NewGUIforClient.html`) - Browser-based cyberpunk interface
2. **API Bridge** (`cyberbackup_api_server.py`) - Flask server bridging web UI to native client
3. **C++ Client** (`src/client/client.cpp`) - Command-line backup engine (RSA+AES encryption)
4. **Python Server** (`server/server.py`) - Backup storage server with custom TCP protocol

**Critical Architecture Note**: The web UI never talks directly to the C++ client or server - all communication flows through the Flask API bridge:

```
Web UI → Flask API → C++ Client (subprocess) → Python Server
        ↓                    ↓                    ↓
   HTTP API calls      transfer.info +
                      --batch flag        Custom TCP
                                        (Binary Protocol)
```

## Common Development Commands

### Build System
```bash
# Configure CMake (first time or after dependency changes)
.\scripts\configure_cmake.bat

# Build the client (CRITICAL: Must use vcpkg toolchain)
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg\scripts\buildsystems\vcpkg.cmake"
cmake --build build --config Release

# Output: build/Release/EncryptedBackupClient.exe
```

### Server Operations
```bash
# Start full system (API server + browser GUI)
python launch_gui.py

# Start backup server only (port 1256)
python server/server.py

# Start API bridge only (port 9090)
python cyberbackup_api_server.py

# Start entire system
.\start_system.bat
```

### Testing
```bash
# Run comprehensive test suite
python scripts/master_test_suite.py

# Integration tests (tests complete web→API→C++→server chain)
python tests/test_gui_upload.py

# Direct server testing
python tests/test_upload.py

# Build validation
python tests/test_client.py
```

### Key Generation
```bash
# Generate RSA keys for testing
python scripts/generate_rsa_keys.py

# Generate working keys for specific configurations
python scripts/create_working_keys.py
```

### Configuration Management
```bash
# Manage configurations
python config_manager.py

# Validate server GUI
python scripts/validate_server_gui.py
```

## Architecture Overview

### Client Architecture (C++)
- **Entry Point**: `src/client/main.cpp`
- **Core Logic**: `src/client/client.cpp` (1.6K lines, handles connection, encryption, file transfer)
- **Web GUI**: `src/client/NewGUIforClient.html` served by `src/client/WebServerBackend.cpp`
- **Crypto Wrappers**: `src/wrappers/` (RSA, AES, Base64 implementations using Crypto++)
- **Configuration**: Uses `data/transfer.info` for connection settings

### Server Architecture (Python)
- **Entry Point**: `server/server.py`
- **Network Layer**: `server/network_server.py` (socket management)
- **Protocol Handler**: `server/protocol.py` (message parsing, command handling)
- **File Management**: `server/file_transfer.py` (stores files in `server/received_files/`)
- **Client Management**: `server/client_manager.py` (session tracking, authentication)
- **GUI**: `server/ServerGUI.py` (modern Tkinter interface)
- **Configuration**: `config/default.json`, `config/development.json`, `config/production.json`

### Data Flow
1. **Client GUI** (HTML/JS) → **WebServerBackend** (C++) → **Client Core** (C++)
2. **Client** encrypts files (AES-256-CBC) + encrypts AES key (RSA-1024) → **Network Protocol**
3. **Server** receives encrypted data → **File Transfer** module → `server/received_files/`
4. **Server GUI** displays transfer progress and client statistics

## Key Configuration Files

### Client Configuration
- `data/transfer.info`: Server connection details (host:port, username, file path)
- `data/me.info`: Client identity and key information
- `vcpkg.json`: C++ dependencies (boost-asio, boost-beast, cryptopp, zlib)

### Server Configuration
- `config/default.json`: Default server settings (port 1256, file storage paths)
- `config/development.json`: Development environment overrides
- `config/production.json`: Production environment settings

## Important Implementation Details

### Critical Process Integration Pattern
The system relies on subprocess execution of the C++ client:
```python
# RealBackupExecutor launches C++ client with --batch mode
self.backup_process = subprocess.Popen(
    [self.client_exe, "--batch"],  # Batch mode prevents hanging
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=os.path.dirname(os.path.abspath(self.client_exe))
)
```

### Protocol Specification
- **Binary Protocol**: Custom message format with CRC32 verification
- **Request Codes**: REQ_REGISTER (1025), REQ_SEND_PUBLIC_KEY (1026), REQ_SEND_FILE (1028)
- **Response Codes**: RESP_REGISTER_OK (1600), RESP_PUBKEY_AES_SENT (1602)
- **Client/Server Version**: Both use version 3
- **Header Format**: 23-byte headers with UUID + version + code + payload_size

### Encryption Stack
- **RSA-1024**: Used for AES key exchange and client authentication
- **AES-256-CBC**: Used for bulk file encryption
- **Base64**: Used for safe transport of binary data over text protocols
- **CRC32**: Used for file integrity verification

### Build Dependencies
- **Client**: Requires MSVC Build Tools, vcpkg, CMake 3.15+
- **Server**: Requires Python 3.x with cryptography, pycryptodome, tkinter
- **External Libraries**: Boost.Asio/Beast, Crypto++, ZLIB

### File Structure Patterns
- **Headers**: `include/` directory with subdirectories for `client/`, `wrappers/`, `utils/`
- **Source**: `src/` directory mirroring header structure
- **Build Output**: `build/` for CMake artifacts, `client/` for executable
- **Data Storage**: `server/received_files/` for uploaded files, `data/` for client data

## Testing Framework

The project uses a comprehensive testing approach:

- **Master Test Suite**: `scripts/master_test_suite.py` - Runs all tests including build, crypto, server, GUI, API, and integration tests
- **Individual Tests**: `tests/` directory contains specific test files for different components
- **Integration Tests**: Test real file transfers between client and server
- **Error Handling Tests**: Validate proper error handling and recovery

## Development Workflow

1. **Initial Setup**: Run `scripts/configure_cmake.bat` to bootstrap vcpkg and configure build
2. **Build**: Use `cmake --build build --config Release` to compile client
3. **Test**: Run `python scripts/master_test_suite.py` to validate all components
4. **Development**: Use configuration files in `config/` for different environments
5. **Deployment**: Use `scripts/deploy_production.bat` for production deployment

## Security Considerations

- RSA keys are generated with 1024-bit length (configurable)
- AES encryption uses 256-bit keys with CBC mode
- All file transfers are encrypted end-to-end
- CRC32 verification ensures file integrity
- Client authentication uses RSA public/private key pairs

## Performance Notes

- File transfers use configurable chunk sizes (default 64KB)
- Compression is available via `CompressionWrapper` 
- Server supports up to 50 concurrent clients (configurable)
- GUI updates are throttled to prevent performance issues during large transfers

## Critical Build & Runtime Requirements

### Build System Requirements
- **vcpkg Toolchain**: Build fails without `CMAKE_TOOLCHAIN_FILE` specification
- **Windows Defines**: Must include `WIN32_LEAN_AND_MEAN`, `NOMINMAX` for Boost compatibility
- **CMake Version**: Requires CMake 3.15+ with policy `CMP0167 NEW` for Boost

### Runtime Requirements
- **Batch Mode**: Must use `--batch` flag to prevent C++ client from waiting for user input
- **Working Directory**: C++ client must run from directory containing `transfer.info`
- **Port Availability**: API server (9090), backup server (1256) - check availability before starting

### Debugging Patterns
- **Client Logs**: Monitor `client_debug.log` for C++ process activity
- **Server Logs**: Monitor `server.log` for server-side protocol activity
- **API Logs**: Flask console output shows request/response flow
- **Network Monitoring**: `RealBackupExecutor` checks active connections on port 1256

## File Verification Pattern
Always verify complete transfers through multiple layers:
```python
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