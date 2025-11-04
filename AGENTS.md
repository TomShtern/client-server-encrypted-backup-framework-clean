# Client-Server Encrypted Backup Framework - AGENTS Documentation

## Project Overview

CyberBackup 3.0 is a comprehensive encrypted file backup system with dual-GUI architecture and robust security. The framework enables secure file transfers between clients and a backup server with end-to-end encryption and verification.

### Key Features

- **Security Layer**: RSA-1024 for key exchange and AES-256-CBC for file encryption
- **Backend**: Python BackupServer with SQLite database and network listener (port 1256)
- **Desktop GUI**: FletV2 native application with Material Design 3 for administrators
- **Web GUI**: JavaScript interface via API Server (port 9090) for end-user backups
- **Protocol**: Custom binary protocol with CRC32 verification for data integrity
- **Architecture**: Dual-GUI system with integrated server and shared database

### Core Architecture

#### Two-GUI Architecture

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
```

## Building and Running

### Quick Start

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

## Development Conventions

### Security Implementation
- Use AES-256-CBC for file encryption with zero IV (as per protocol specification)
- RSA-1024 for key exchange using PKCS1_OAEP padding
- CRC32 verification for data integrity
- Filename validation to prevent path traversal attacks
- Client authentication and session management

### Database Operations
- Use SQLite with connection pooling for better performance
- Implement automatic migrations on startup
- Use atomic file operations for safe storage
- Support file-level locking for concurrent access

### Protocol Implementation
- Custom binary protocol with structured message handling
- Multi-packet file transfer reassembly
- Duplicate packet detection and handling
- Connection timeout and session management

### Logging and Monitoring
- Structured logging with dual output (console + file)
- Performance metrics collection
- System monitoring integration (CPU, memory, disk usage)
- Error tracking with Sentry integration

### Code Structure
- Follow modular design with clear separation of concerns
- Use type hints for better code maintainability
- Implement retry mechanisms for transient failures
- Follow defensive programming practices

## Key Components

### Server Components
- **BackupServer**: Main server class handling client connections and protocol messages
- **RequestHandler**: Processes all client protocol requests
- **FileTransferManager**: Manages file transfer operations
- **DatabaseManager**: Handles SQLite database interactions
- **NetworkServer**: Manages TCP network layer

### Client Components
- **C++ Client**: Binary protocol implementation for file transfers
- **API Server**: Flask-based bridge for web GUI integration
- **FletV2 GUI**: Native desktop application for administration

### Security Components
- **Crypto Implementation**: Uses PyCryptodome for encryption
- **Key Management**: Automatic RSA key generation and AES session key handling
- **Protocol Security**: Secure key exchange mechanisms