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
- CMake 3.15+

### vcpkg Setup (Required for C++ Client)

The project uses [vcpkg](https://github.com/microsoft/vcpkg) for C++ dependency management. On a fresh machine, set up vcpkg with:

```powershell
# Clone vcpkg to project root
git clone https://github.com/Microsoft/vcpkg.git
.\vcpkg\bootstrap-vcpkg.bat

# Dependencies are automatically installed via vcpkg.json during CMake configure
```

The project's `vcpkg.json` defines all required dependencies (Crypto++, Boost, etc.) which are installed automatically when you build.

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
│   ├── main.py                 # Application entry point
│   ├── start_with_server.py    # Launcher with integrated BackupServer
│   ├── views/                  # Feature views (dashboard, clients, files, etc.)
│   ├── components/             # Reusable UI components
│   ├── utils/                  # ServerBridge, state management
│   └── theme.py                # Material Design 3 theming
├── python_server/              # Core backup server
│   └── server/
│       ├── server.py           # BackupServer with network listener
│       ├── database.py         # SQLite integration
│       ├── protocol.py         # Binary protocol implementation
│       └── network_server.py   # TCP network layer
├── api_server/                 # Flask bridge for C++ client web GUI
│   ├── cyberbackup_api_server.py
│   └── real_backup_executor.py # C++ subprocess manager
├── Client/                     # C++ backup client
│   ├── cpp/                    # Source files (main.cpp, client.cpp, etc.)
│   └── deps/                   # Crypto wrappers (RSA, AES, CRC)
├── Shared/                     # Cross-cutting utilities (modular subpackages)
│   ├── sentry_config.py        # Sentry error monitoring
│   ├── filesystem/             # UTF-8 handling, file operations, path utils
│   ├── app_logging/            # Enhanced logging, error handling
│   ├── config/                 # Unified configuration management
│   ├── monitoring/             # Performance/process/file monitoring
│   └── validation/             # Client name and data validation
├── config/                     # JSON configuration files
├── data/                       # Runtime data (database, received files, keys)
├── scripts/                    # Build and deployment scripts
│   └── one_click_build_and_run.py
├── tests/                      # Test suite
├── docs/                       # Documentation
├── build/                      # C++ build artifacts
├── vcpkg/                      # C++ package manager
├── build.bat                   # Windows build script
└── requirements.txt            # Python dependencies
```

## Features

- **Modern GUI**: File-based web interface with real-time progress
- **Secure Protocol**: Binary protocol with proper error handling
- **File Integrity**: CRC32 verification for transferred files
- **Key Management**: Automatic RSA key generation and storage
- **Progress Tracking**: Real-time transfer statistics
- **Error Recovery**: Automatic retry mechanisms

## Sentry Error Monitoring

The project includes integrated error monitoring via [Sentry](https://sentry.io) for both Python and C++ components.

### Configuration Files

| Component | File | Lines |
|-----------|------|-------|
| Python | `Shared/sentry_config.py` | DSN, all init settings, helper functions |
| C++ | `Client/cpp/main.cpp` | Lines 37-56 (init + shutdown) |

### What's Captured

- **Errors**: All unhandled exceptions with full stack traces
- **Performance**: Transaction tracing (100% sample rate)
- **Profiling**: Session profiling enabled
- **Logs**: Sent to Sentry dashboard
- **Context**: User PII, request headers, component tags

### Manual Usage (Optional)

```python
from Shared.sentry_config import capture_error, capture_message

# Track custom messages
capture_message("Backup started", level="info", component="gui")

# Track errors with context
capture_error(exception, component="backup", extra_context={"file": "data.txt"})
```

### Dashboard

View errors and performance at: https://sentry.io (login required)

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
- **Build System**: CMake with vcpkg for C++ dependency management
- **Crypto**: Crypto++ (C++), PyCryptodome (Python)
- **Networking**: Boost.Asio (C++), Flask-SocketIO (Python)
- **Desktop GUI**: Flet 0.28+ (Material Design 3)
- **Observability**: Sentry for error monitoring

## License

See project documentation for license information.
