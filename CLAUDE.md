# Client-Server Encrypted Backup Framework - Development Guide

## Project Overview

The Client-Server Encrypted Backup Framework (CyberBackup 3.0) is a comprehensive encrypted file backup system with dual-GUI architecture and robust security. The project features:

- **Security Layer**: RSA-1024 for key exchange and AES-256-CBC for file encryption
- **Backend**: Python BackupServer with SQLite database and network listener (port 1256)
- **Desktop GUI**: FletV2 native application with Material Design 3 for administrators
- **Web GUI**: JavaScript interface via API Server (port 9090) for end-user backups
- **Protocol**: Custom binary protocol with CRC32 verification for data integrity
- **Architecture**: Dual-GUI system with integrated server and shared database

## Architecture

### Two-GUI Architecture

**1. FletV2 Desktop GUI** (Server Administration)
- Native desktop application for administrators
- Direct Python method calls via ServerBridge (no network overhead)
- Real-time monitoring, client/file management, analytics
- Integrated BackupServer with network listener on port 1256
- Material Design 3 with enhanced Windows 11 integration

**2. JavaScript Web GUI** (End-User Backups)
- Browser-based interface for backup operations
- API Server (port 9090) launches C++ client subprocess
- File upload, progress tracking, backup history
- Connects to BackupServer via C++ client binary protocol

Both systems share the same SQLite database (`defensive.db`) with file-level locking for safe concurrent access.

## Critical Architecture Notes

### Network Listener Requirement

⚠️ **CRITICAL**: The BackupServer network listener on port 1256 **must be started** for C++ client backups to work.

- **Correct**: `server_instance.start()` is called in `FletV2/start_with_server.py` (line 78)
- **Verified**: Console output shows "Network server started - ready for client connections"
- **Impact**: Without this, C++ clients cannot connect and all backups fail

This was a critical bug fixed in January 2025. The server instance was being created but the network listener thread was never launched.

### Shared Database

Both FletV2 GUI and API Server access the same SQLite database (`defensive.db`) using file-level locking for safe concurrent access.

## Project Structure

```
├── FletV2/                     # Modern desktop GUI (Material Design 3)
│   ├── main.py                # Application entry point
│   ├── start_with_server.py   # Launcher with integrated BackupServer
│   ├── views/                 # Feature views (dashboard, clients, files, etc.)
│   ├── utils/                 # ServerBridge, UI components, utilities
│   ├── components/            # Reusable UI components (search, breadcrumb, etc.)
│   ├── theme.py               # Enhanced theme system with Windows 11 integration
│   ├── docs/                  # Comprehensive technical documentation
│   └── CLAUDE.md              # FletV2-specific development guide
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
├── tests/                     # Test suite
├── docs/                      # Project documentation
├── build/                     # Build artifacts
├── client/                    # Client executable output
├── third_party/               # External libraries
├── build.bat                  # Main build script
├── clean.bat                  # Cleanup script
└── transfer.info              # Client configuration
```

## Technology Stack

### Backend (Python)
- **Framework**: Custom Python server with threading
- **Crypto**: PyCryptodome (AES-256-CBC, RSA-1024)
- **Database**: SQLite with custom connection pooling
- **Networking**: Custom binary protocol with Boost.Asio for C++ client
- **Logging**: Custom structured logging with dual output (console + file)

### Frontend (FletV2)
- **Framework**: Flet 0.28.3
- **Design**: Material Design 3 with enhanced theming and Windows 11 integration
- **Architecture**: ServerBridge pattern for direct method calls to backend
- **Components**: Custom UI components with reactive patterns
- **Utilities**: ~6000 lines across 19 utility modules (formatters, ui_components, async_helpers, etc.)

### C++ Client
- **Language**: C++17
- **Networking**: Boost.Asio
- **Crypto**: Crypto++
- **Build System**: CMake with vcpkg for dependencies

## Building and Running

### Prerequisites
- Windows with MSVC Build Tools
- Python 3.9+ (3.13.5 recommended)
- Boost.Asio library
- vcpkg for C++ dependencies

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

### Building the Client
```batch
.\build.bat
```

### Client Configuration
Configure client settings in `transfer.info`:
```
127.0.0.1:1256
your_username
path\to\file\to\backup.txt
```

## Development Patterns

### ServerBridge Pattern

The FletV2 GUI communicates with the BackupServer through a ServerBridge pattern:

```python
# ServerBridge provides clean API surface for the FletV2 GUI
# - Direct delegation pattern to real server
# - Consistent structured returns: {'success': bool, 'data': Any, 'error': str}
# - Data format conversion between BackupServer and FletV2 formats
# - Error handling with structured responses
# - No mock data (returns empty data if server unavailable)
```

### Direct Integration vs API Layer

The FletV2 GUI connects directly to the BackupServer instance, bypassing the network layer:

```python
# No API call overhead - direct method calls on server object
server_instance = BackupServer()
app = main.FletV2App(page, real_server=server_instance)
```

### Data Conversion

The system handles data format conversion between the server and GUI:

```python
def convert_backupserver_client_to_fletv2(client_data: dict[str, Any]) -> dict[str, Any]:
    """Convert BackupServer client format to FletV2 expected format."""
    # Implementation handles field mapping and type conversion
```

## Key Files and Components

### Core Server: `python_server/server/server.py`
- BackupServer class with client management
- Database integration with connection pooling
- Network protocol handling
- File storage and verification

### GUI Application: `FletV2/main.py`
- FletV2App class implementing the main interface (~1000 lines)
- NavigationRail for view switching
- ServerBridge integration
- Global shortcuts and keyboard navigation

### Server Integration: `FletV2/start_with_server.py`
- Server initialization and lifecycle management
- Main thread execution with signal handling
- Integration with Flet GUI
- Environment variable setup

### Server Bridge: `FletV2/utils/server_bridge.py`
- Clean delegation to BackupServer methods
- Structured response format
- Data normalization utilities
- No mock data fallbacks (real server only)

### Utilities: `FletV2/utils/`
- `formatters.py`: Data formatting utilities (as_float, as_int, format_timestamp)
- `ui_components.py`: Reusable UI components
- `async_helpers.py`: Async/await patterns
- `global_shortcuts.py`: Desktop keyboard shortcuts
- `user_feedback.py`: Snackbar and dialog helpers
- And 14 more specialized modules

### API Server: `api_server/cyberbackup_api_server.py`
- Flask-based web API
- C++ client subprocess management
- Connection to BackupServer via network protocol

### C++ Client: `Client/cpp/client.cpp`
- Binary protocol implementation
- File encryption and transmission
- Connection to BackupServer

## FletV2 Development

For detailed FletV2 GUI development, see:
- **`FletV2/CLAUDE.md`**: FletV2-specific patterns, anti-patterns, and critical rules
- **`FletV2/docs/ARCHITECTURE.md`**: Comprehensive architecture documentation
- **`FletV2/docs/GETTING_STARTED.md`**: Setup and quick start guide
- **`FletV2/docs/DEVELOPMENT_WORKFLOWS.md`**: Testing, deployment, and workflow documentation

### Quick FletV2 Reference
- **Framework**: Flet 0.28.3 with Material Design 3
- **Pattern**: View-based architecture with `create_*_view()` functions
- **Theme**: Enhanced theme system with Windows 11 integration (theme.py)
- **Principle**: Use Flet built-ins over custom solutions (Flet Simplicity Principle)

## Testing

Run the consolidated test suite:
```python
python tests\consolidated_tests.py
```

FletV2 specific tests:
```bash
cd FletV2
pytest tests/
```

## Configuration

Edit `transfer.info` to configure:
- Server address and port
- Username for authentication
- File path to backup

## Development Conventions

1. **Error Handling**: Use structured responses with success/error fields
2. **Logging**: Follow established patterns with appropriate log levels
3. **Database**: Use connection pooling for thread safety
4. **Threading**: Implement proper locks for shared resources
5. **Testing**: Include retry logic for transient failures
6. **Security**: Maintain encryption standards throughout transmission and storage
7. **Flet Development**: Follow Flet Simplicity Principle (use built-ins, avoid over-engineering)

## Troubleshooting

### Common Issues

1. **Network Listener Not Starting**: Ensure `server_instance.start()` is called in startup scripts
2. **Database Locking**: Concurrent access is handled through file-level locking
3. **UTF-8 Issues**: The system includes UTF-8 bootstrap for Windows compatibility
4. **Import Errors**: Always use `flet_venv` virtual environment located at workspace root

### Debugging

- Server logs are available in `server.log` and the enhanced logging system
- FletV2 includes verbose diagnostic options via environment variables
- Network protocol issues can be debugged through the binary protocol implementation

### Environment Variables

For FletV2 integration:
```bash
# Windows PowerShell
$env:CYBERBACKUP_DISABLE_INTEGRATED_GUI = "1"
$env:CYBERBACKUP_DISABLE_GUI = "1"
$env:FLET_V2_DEBUG = "true"
```

## Deployment

### FletV2 Desktop Application
```bash
cd FletV2
flet build windows              # Build Windows executable
# Output: build/windows/FletV2.exe

# Options:
flet build windows --verbose --build-number 1.0 --company "CyberBackup"
```

### C++ Client
```batch
.\build.bat    # Builds C++ client with Boost.Asio and Crypto++
# Output: client/backup_client.exe
```

### Full System Deployment
1. Build C++ client: `build.bat`
2. Build FletV2 GUI: `cd FletV2 && flet build windows`
3. Package both executables with `defensive.db` and `transfer.info`
4. Distribute as standalone Windows application

## Recent Updates (January 2025)

- **Database View**: Refactored to use ListView for optimal performance
- **Formatters Module**: Added utility functions for safe type conversion
- **Theme System**: Enhanced with Windows 11 integration and display scaling
- **Consolidation**: Organized archive folders, cleaned up legacy code
- **Documentation**: Comprehensive docs/ folder with ARCHITECTURE.md, GETTING_STARTED.md, DEVELOPMENT_WORKFLOWS.md
- **Flet 0.28.3**: Updated to latest Flet version with Material Design 3
