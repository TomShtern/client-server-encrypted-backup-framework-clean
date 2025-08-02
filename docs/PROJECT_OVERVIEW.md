# CyberBackup 3.0 - Comprehensive Project Documentation

## 1. System Architecture Overview

The CyberBackup framework implements a **4-layer secure backup system** with strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Web-Based GUI (NewGUIforClient.html)              │
│  - Modern HTML/CSS/JavaScript interface                    │
│  - Real-time progress visualization                        │
│  - WebSocket communication with API server                 │
└─────────────────────────────────────────────────────────────┘
            ▲
            │ HTTP/WebSocket
            ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Flask API Server (cyberbackup_api_server.py)      │
│  - RESTful endpoints for client interaction                │
│  - WebSocket real-time status broadcasting                 │
│  - Manages connection to backup protocol                   │
│  - Handles file uploads and progress tracking              │
└─────────────────────────────────────────────────────────────┘
            ▲
            │ TCP/IP (Port 1256)
            ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Backup Protocol Handler                           │
│  - Real-time progress reporting                            │
│  - File segmentation and verification                      │
│  - CRC32 integrity checks                                  │
└─────────────────────────────────────────────────────────────┘
            ▲
            │ Encrypted Binary Protocol
            ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Python Backup Server (`src/server/network_server.py`)   │
│  - Handles encrypted file storage                          │
│  - Manages client authentication                           │
│  - Implements server-side encryption                       │
│  - Stores files in received_files/ directory               │
└─────────────────────────────────────────────────────────────┘
```

## 2. Core Components

### 2.1 Client Components
- **C++ Backup Client** (`src/client/main.cpp`)
  - Implements RSA-1024 key exchange and AES-256-CBC encryption
  - Uses Boost.Asio for network communication
  - Handles file segmentation and CRC verification
  - Generates `client/valid_private_key.der` and `client/valid_public_key.der`
  - Batch mode operation for API integration

- **Web GUI** (`src/client/NewGUIforClient.html`)
  - Single-page application interface
  - Real-time progress visualization with percentage and transfer stats
  - WebSocket connection to API server for status updates
  - File selection and upload functionality
  - Configuration management interface

### 2.2 Server Components
- **Python Backup Server** (`src/server/network_server.py`)
  - Implements custom binary protocol with 23-byte request headers (client_id, version, code, payload_size)
  - Manages concurrent client connections with semaphore-based limiting (MAX_CONCURRENT_CLIENTS)
  - Features robust error handling for socket timeouts, protocol violations, and connection errors
  - Uses CRC32 verification for data integrity at protocol level
  - Tracks connection statistics (active connections, uptime, available slots)
  - Implements graceful shutdown with signal handling (SIGINT/SIGTERM)
  - Stores received files in `server/received_files/`

- **Flask API Server** (`cyberbackup_api_server.py`)
  - REST API endpoints (`/api/connect`, `/api/start_backup`, etc.)
  - WebSocket server for real-time status updates
  - Singleton instance management (`src/server/server_singleton.py`)
  - Integrates with C++ client via `RealBackupExecutor`
  - Serves static client assets and configuration files

### 2.3 Security Infrastructure
- **Encryption Pipeline**
  1. RSA-1024 key exchange for session key establishment
  2. AES-256-CBC encryption for file data
  3. CRC32 verification at both protocol and file levels
  4. Secure key storage in DER format
  5. Protocol version validation for backward compatibility

- **Key Management**
  - Automatic key generation during first run
  - Private keys stored client-side only
  - Public keys exchanged during connection setup
  - Key rotation capabilities

## 3. Workflow Process

### 3.1 Backup Execution Sequence
1. **Initialization**
   - Client loads configuration from `transfer.info`
   - Establishes connection to API server (port 9090)
   - Authenticates with username and credentials

2. **Connection Setup**
   - API server validates connection parameters
   - Tests connection to backup server (port 1256)
   - Establishes WebSocket for real-time updates

3. **File Processing**
   - File segmented into chunks
   - Each chunk encrypted with AES-256-CBC
   - CRC32 checksum calculated for verification
   - Encrypted chunks transmitted via binary protocol

4. **Server Processing**
   - Backup server receives encrypted chunks
   - Verifies CRC32 checksums
   - Decrypts chunks using session key
   - Reassembles and stores original file

5. **Completion**
   - Final verification of file integrity
   - Status update via WebSocket
   - Cleanup of temporary files
   - Progress reset to READY state

### 3.2 Real-Time Progress Tracking
- **Progress States**
  - `READY`: System initialized and waiting
  - `CONNECT`: Establishing connection
  - `BACKUP_IN_PROGRESS`: File transfer active
  - `CLEANUP`: Post-transfer operations
  - `COMPLETED`: Successful backup
  - `FAILED`: Error during process

- **Progress Metrics**
  - Percentage complete (0-100%)
  - Current file being processed
  - Bytes transferred vs. total
  - Phase-specific status messages

## 4. Configuration System

### 4.1 Key Configuration Files
- **transfer.info** (Client Configuration)
  ```
  127.0.0.1:1256
  your_username
  path\to\file\to\backup.txt
  ```

- **port.info** (Server Port Configuration)
  ```
  1256
  ```

- **server_gui_settings.json** (GUI Behavior)
  ```json
  {
    "theme": "dark",
    "auto_connect": true,
    "progress_interval": 500
  }
  ```

- **progress_config.json** (Progress Visualization)
  ```json
  {
    "phases": {
      "CONNECT": {"color": "#4CAF50", "weight": 5},
      "BACKUP_IN_PROGRESS": {"color": "#2196F3", "weight": 80},
      "CLEANUP": {"color": "#FF9800", "weight": 15}
    }
  }
  ```

### 4.2 Environment Configuration
- **Build System**
  - CMake with vcpkg integration
  - MSVC compiler for Windows builds
  - Release configuration for production

- **Runtime Dependencies**
  - Python 3.8+ with Flask, SocketIO
  - Crypto++ library for encryption
  - Boost.Asio for networking

## 5. Security Implementation Details

### 5.1 Encryption Protocol
- **Key Exchange**
  - RSA-1024 public/private key pairs
  - Session key encrypted with server's public key
  - Key rotation after each backup session

- **File Encryption**
  - AES-256-CBC mode with random IV
  - 16KB block segmentation
  - PKCS#7 padding for block alignment
  - HMAC-SHA256 for message authentication

- **Data Verification**
  - CRC32 checksum for each file segment
  - End-to-end verification after transfer
  - Automatic retry for failed segments

### 5.2 Security Best Practices
- **Key Management**
  - Private keys never transmitted
  - DER format for secure storage
  - Automatic key generation on first run

- **Protocol Security**
  - Binary protocol prevents common web attacks
  - Session validation with client ID tracking
  - Connection rate limiting via semaphore
  - Protocol version validation (flexible compatibility)
  - Structured error responses (RESP_GENERIC_SERVER_ERROR, etc.)

- **Data Protection**
  - Zero-knowledge architecture
  - Temporary files encrypted during processing
  - Secure cleanup with SynchronizedFileManager
  - Exact byte reading/writing to prevent protocol corruption
  - Connection timeout management (CLIENT_SOCKET_TIMEOUT)

## 6. Development and Testing

### 6.1 Build Process
1. **Prerequisites**
   - Windows with MSVC Build Tools
   - Python 3.8+
   - CMake 3.20+
   - vcpkg

2. **Client Build**
   ```batch
   mkdir build
   cd build
   cmake .. -DCMAKE_TOOLCHAIN_FILE=../vcpkg/scripts/buildsystems/vcpkg.cmake
   cmake --build . --config Release
   ```

3. **Server Setup**
   ```bash
   pip install -r requirements.txt
   ```

### 6.2 Testing Framework
- **Unit Tests** (`tests/`)
  - `test_client.py`: C++ client functionality
  - `test_server.py`: Server protocol handling
  - `test_encryption.py`: Crypto implementation

- **Integration Tests**
  - `test_demo_scenarios.py`: End-to-end workflows
  - `test_progress_reporting.py`: Real-time status
  - `test_transfer_file.txt`: File transfer validation

- **Test Execution**
  ```python
  python test_demo_scenarios.py --all
  ```

## 7. Troubleshooting Guide

### 7.1 Common Issues
- **Connection Failures**
  - Verify backup server is running (port 1256)
  - Check `port.info` configuration
  - Ensure no firewall blocking

- **File Transfer Errors**
  - Validate CRC32 checksums at protocol and file levels
  - Check temporary file permissions and cleanup
  - Verify encryption key integrity
  - Monitor connection statistics for bottlenecks
  - Handle protocol version mismatches gracefully

- **GUI Issues**
  - Confirm WebSocket connection (port 9090)
  - Check browser console for errors
  - Verify static asset paths

### 7.2 Diagnostic Tools
- **API Health Check**
  ```bash
  curl http://localhost:9090/health
  ```
- **Connection Statistics**
  ```python
  # Access via network_server.get_connection_stats()
  {
    'active_connections': 3,
    'max_connections': 10,
    'available_slots': 7,
    'uptime_seconds': 1245
  }
  ```

- **Log Files**
  - `api_server_log.txt`: API server operations
  - `server/received_files/`: Successful transfers
  - Browser developer tools for GUI issues

## 8. Project Structure Reference

```
Client_Server_Encrypted_Backup_Framework/
├── build/                  # C++ build artifacts
├── client/                 # Client keys and status
├── config/                 # Configuration templates
├── docs/                   # Documentation (this file)
├── server/                 # Python backup server runtime (logs, received files)
├── src/
│   ├── client/             # C++ client implementation
│   ├── server/             # Server-side components
│   │   ├── network_server.py  # Core network infrastructure
│   │   ├── config.py         # Server configuration
│   │   └── ServerGUI.py      # Server GUI implementation
│   └── shared/             # Common utilities
├── tests/                  # Test suite
├── vcpkg/                  # Dependency manager
├── .mcp.json               # MCP configuration
├── HOW_To_Run_Project.md   # Setup guide
├── README.md               # Project overview
└── cyberbackup_api_server.py # Main API server
```

## 9. Version Compatibility

- **Client-Server Protocol**
  - Version 3.0 (current)
  - Backward compatible with 2.5+
  - Strict version checking during handshake

- **Dependency Matrix**
  | Component       | Version   | Notes                          |
  |-----------------|-----------|--------------------------------|
  | Python          | 3.8+      | Required for server            |
  | Flask           | 2.0+      | API server framework           |
  | SocketIO        | 5.0+      | Real-time communication        |
  | Boost.Asio      | 1.75+     | Client networking              |
  | Crypto++        | 8.5+      | Encryption implementation      |
