# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A **4-layer Client-Server Encrypted Backup Framework** implementing secure file transfer with RSA-1024 + AES-256-CBC encryption. The system is fully functional with evidence of successful file transfers in `src/server/received_files/`.

### Architecture Layers

1. **Web UI** (`src/client/NewGUIforClient.html`) - Browser-based file selection interface
2. **Flask API Bridge** (`cyberbackup_api_server.py`) - HTTP API server (port 9090) that coordinates between UI and native client
3. **C++ Client** (`src/client/client.cpp`) - Native encryption engine with binary protocol
4. **Python Server** (`src/server/server.py`) - Multi-threaded backup storage server (port 1256)

### Data Flow
```
Web UI → Flask API (9090) → C++ Client (subprocess) → Python Server (1256) → File Storage
```

## Essential Commands

### Building the C++ Client
```bash
# Configure with vcpkg
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"

# Build
cmake --build build --config Release

# Output: build/Release/EncryptedBackupClient.exe
```

### Running the System
```bash
# 1. Install Python dependencies
pip install -r requirements.txt
pip install flask-cors  # Often missing

# 2. Start Python server (Layer 4) - runs on port 1256
python -m src.server.server

# 3. Start Flask API Bridge (Layer 2) - runs on port 9090  
python cyberbackup_api_server.py

# 4. Access Web UI (Layer 1)
# Open: src/client/NewGUIforClient.html in browser

# OR: Use the one-click script (recommended)
python one_click_build_and_run.py
```

### Testing
```bash
# Comprehensive test suite
python scripts/testing/master_test_suite.py

# Quick validation
python scripts/testing/quick_validation.py

# Individual component tests
cd tests && python test_upload.py

# Validate specific fixes
python scripts/testing/validate_null_check_fixes.py
python scripts/testing/validate_server_gui.py
```

## Critical Operating Knowledge

### Configuration Requirements
- **transfer.info**: Must contain exactly 3 lines: `server:port`, `username`, `filepath`
- **Working Directory**: C++ client MUST run from directory containing `transfer.info`
- **Batch Mode**: Use `--batch` flag to prevent C++ client hanging in subprocess

### Verification Points
- **Success Verification**: Check `src/server/received_files/` for actual file transfers (exit codes are unreliable)
- **Port Availability**: Ensure ports 9090 and 1256 are free
- **Dependencies**: Flask-cors is commonly missing from fresh installs

### Known Issues
- C++ client hangs without `--batch` flag when run as subprocess
- Windows console encoding issues with some validation scripts (use one-click Python script instead)

## Architecture Details

### Core Components
- **Real Backup Executor** (`src/api/real_backup_executor.py`): Manages C++ client subprocess execution with synchronized file handling
- **Network Server** (`src/server/network_server.py`): Multi-threaded TCP server handling encrypted file transfers  
- **Crypto Wrappers** (`src/wrappers/`): RSA/AES encryption abstractions for C++ client
- **Protocol Implementation**: 23-byte binary headers + encrypted payload with CRC32 verification
- **Shared Utils** (`src/shared/utils/`): Common utilities including file lifecycle management, error handling, and process monitoring

### Key Integration Points
- **Subprocess Communication**: Flask API → RealBackupExecutor → C++ client (with `--batch` flag)
- **File Lifecycle**: SynchronizedFileManager prevents race conditions in file creation/cleanup
- **Error Propagation**: Status flows back through all 4 layers to web UI
- **Configuration**: Centralized through `transfer.info` and various JSON configs

### Security Considerations
- **Current Encryption**: RSA-1024 + AES-256-CBC (functional but has known vulnerabilities)
- **Vulnerabilities**: Fixed IV in AES, CRC32 instead of HMAC, deterministic encryption
- **Access Control**: Basic username-based identification (not true authentication)

### Development Workflow
1. Always verify file transfers by checking `src/server/received_files/` directory
2. Use `--batch` flag for all C++ client subprocess calls
3. Test complete integration chain through all 4 layers
4. Monitor ports 9090 and 1256 for conflicts
5. Check both `build/Release/` and `client/` directories for executables

### Recent Improvements (2025-07-27)
- **Import Issues RESOLVED**: All relative import issues have been fixed with proper package structure
- **Module Structure**: Added `__init__.py` files for proper Python package organization
- **One-Click Script**: Python version (`one_click_build_and_run.py`) now works reliably
- **Cross-Package Imports**: Fixed imports between `src/api/`, `src/shared/utils/`, and `src/server/`
- **Server Module Execution**: Use `python -m src.server.server` for proper module execution

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
