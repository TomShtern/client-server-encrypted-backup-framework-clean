# Client-Server Encrypted Backup Framework

A comprehensive encrypted file backup system with dual-GUI architecture and robust security.

## Overview

CyberBackup 3.0 provides a complete encrypted backup solution featuring:

- **Security Layer**: RSA-1024 for key exchange and AES-256-CBC for file encryption
- **Backend**: Python BackupServer with SQLite database and network listener (port 1256)
- **Desktop GUI**: FletV2 native application with Material Design 3 for administrators
- **Web GUI**: JavaScript interface via API Server (port 9090) for end-user backups
- **Protocol**: Custom binary protocol with CRC32 verification for data integrity
- **Architecture**: Dual-GUI system with integrated server and shared database

### Two-GUI Architecture

**1. FletV2 Desktop GUI** (Server Administration)
- Native desktop application for administrators
- Direct Python method calls via ServerBridge (no network overhead)
- Real-time monitoring, client/file management, analytics
- Integrated BackupServer with network listener on port 1256
- Material Design 3 with Neumorphism and Glassmorphism styling

**2. JavaScript Web GUI** (End-User Backups)
- Browser-based interface for backup operations
- API Server (port 9090) launches C++ client subprocess
- File upload, progress tracking, backup history
- Connects to BackupServer via C++ client binary protocol

Both systems share the same SQLite database (`defensive.db`) with file-level locking for safe concurrent access.

## Quick Start

### Launching the System

**Option 1: One-Click Launch (Recommended)**
```bash
python scripts/one_click_build_and_run.py
```
This will:
1. Build the C++ client
2. Launch FletV2 Desktop GUI with integrated BackupServer
3. Launch API Server for C++ client web GUI
4. Verify all components are running

**Option 2: Manual FletV2 Launch**
```bash
cd FletV2
../flet_venv/Scripts/python start_with_server.py
```
Launches native desktop window with full server integration.

**Option 3: Development Mode**
```bash
# Terminal 1: Start BackupServer + FletV2 GUI
cd FletV2
../flet_venv/Scripts/python start_with_server.py

# Terminal 2: Start API Server (for C++ client web GUI)
python api_server/cyberbackup_api_server.py
```

### Prerequisites
- Windows with MSVC Build Tools
- Python 3.x
- Boost.Asio library

### Building the Client
```batch
.\build.bat
```

### Running the System
1. Start the server:
   ```batch
   .\start_server.bat
   ```

2. Configure client settings in `transfer.info`:
   ```
   127.0.0.1:1256
   your_username
   path\to\file\to\backup.txt
   ```

3. Run the client:
   ```batch
   .\start_client.bat
   ```

## Critical Architecture Notes

### Network Listener Requirement

⚠️ **CRITICAL**: The BackupServer network listener on port 1256 **must be started** for C++ client backups to work.

- **Correct**: `server_instance.start()` is called in `FletV2/start_with_server.py` (line 78)
- **Verified**: Console output shows "Network server started - ready for client connections"
- **Impact**: Without this, C++ clients cannot connect and all backups fail

This was a critical bug fixed in January 2025. The server instance was being created but the network listener thread was never launched.

### Shared Database

Both FletV2 GUI and API Server access the same SQLite database (`defensive.db`) using file-level locking for safe concurrent access.

## ⚠️ Critical Architecture Notes

### Network Listener Requirement

**CRITICAL**: The BackupServer network listener on port 1256 **must be started** for C++ client backups to work.

- ✅ **Verified Fixed**: `server_instance.start()` is called in `FletV2/start_with_server.py` (line 78)
- ✅ **Console Confirmation**: Look for "Network server started - ready for client connections"
- ⚠️ **Impact if Missing**: C++ clients cannot connect and all backups fail silently

This was a critical bug fixed in January 2025. The server instance was being created but the network listener daemon thread was never launched. Without this call, the system appears to run normally but file transfers fail with connection errors.

### Shared Database

Both FletV2 GUI and API Server access the same SQLite database (`defensive.db`) using file-level locking for safe concurrent access. No conflicts occur because:
- SQLite handles concurrent reads automatically
- Writes use transactions with proper locking
- Both processes use the same DatabaseManager with connection pooling

### Legacy Code Archive

The legacy TkInter GUI (40,000+ lines) has been archived to `_legacy/server_gui/` as of January 2025. It is preserved for historical reference but should not be used in new development. See `_legacy/README.md` for details.

## Project Structure

```
├── FletV2/                     # Modern desktop GUI (Material Design 3)
│   ├── main.py                # Application entry point
│   ├── start_with_server.py   # Launcher with integrated BackupServer
│   ├── views/                 # Feature views (dashboard, clients, files, etc.)
│   ├── utils/                 # ServerBridge, state management, UI components
│   └── theme.py               # Tri-style design system
├── python_server/             # Core backup server
│   └── server/
│       ├── server.py          # BackupServer with network listener
│       ├── database.py        # SQLite integration
│       ├── protocol.py        # Binary protocol implementation
│       └── network_server.py  # TCP network layer
├── api_server/                # Flask bridge for C++ client web GUI
│   └── cyberbackup_api_server.py
├── Client/                    # C++ backup client
│   ├── src/                   # Client source code
│   └── include/               # Protocol definitions
├── Shared/                    # Cross-cutting utilities
│   ├── logging_config.py      # Structured logging
│   └── utils/                 # UTF-8 bootstrap, retry logic, metrics
├── scripts/                   # Build and deployment scripts
│   └── one_click_build_and_run.py  # Complete system launcher
├── _legacy/                   # Archived legacy code
│   └── server_gui/            # TkInter GUI (deprecated Jan 2025)
├── tests/             # Test suite
├── docs/              # Documentation
├── build/             # Build artifacts
├── client/            # Client executable output
├── third_party/       # External libraries
├── build.bat          # Main build script
├── clean.bat          # Cleanup script
└── transfer.info      # Client configuration
```

## Features

- **Modern GUI**: File-based web interface with real-time progress
- **Secure Protocol**: Binary protocol with proper error handling
- **File Integrity**: CRC32 verification for transferred files
- **Key Management**: Automatic RSA key generation and storage
- **Progress Tracking**: Real-time transfer statistics
- **Error Recovery**: Automatic retry mechanisms

## Configuration

Edit `transfer.info` to configure:
- Server address and port
- Username for authentication
- File path to backup

## Testing

Run the consolidated test suite:
```python
python tests\consolidated_tests.py
```

## Development

The project uses:
- **Build System**: Custom batch files with MSVC
- **Crypto**: Crypto++ library for encryption
- **Networking**: Boost.Asio for cross-platform networking
- **GUI**: Modern web-based interface

## License

See project documentation for license information.
