# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


You have access to a "think" tool that provides a dedicated space for structured reasoning. Using this tool significantly improves your performance on complex tasks. 

## When to use the think tool 
Before taking any action or responding to the user after receiving tool results, use the think tool as a scratchpad to: 
- List the specific rules that apply to the current request 
- Check if all required information is collected 
- Verify that the planned action complies with all policies 
- Iterate over tool results for correctness 
- Analyze complex information from web searches or other tools 
- Plan multi-step approaches before executing them 

## How to use the think tool effectively 
When using the think tool: 
1. Break down complex problems into clearly defined steps 
2. Identify key facts, constraints, and requirements 
3. Check for gaps in information and plan how to fill them 
4. Evaluate multiple approaches before choosing one 
5. Verify your reasoning for logical errors or biases




## Project Overview

A **4-layer Client-Server Encrypted Backup Framework** implementing secure file transfer with RSA-1024 + AES-256-CBC encryption. The system is fully functional with evidence of successful file transfers in `src/server/received_files/`.

### Architecture Layers

1. **Web UI** (`src/client/NewGUIforClient.html`) - Browser-based file selection interface
2. **Flask API Bridge** (`cyberbackup_api_server.py`) - **CRITICAL INTEGRATION LAYER** - HTTP API server (port 9090) that coordinates between UI and native client, manages subprocess lifecycles
3. **C++ Client** (`src/client/client.cpp`) - Native encryption engine with binary protocol (runs as subprocess)
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
# RECOMMENDED: One-click startup (builds C++ client, starts all services, opens browser)
python one_click_build_and_run.py

# Manual startup (if needed):
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Start Python server (MUST start first) - port 1256
python -m src.server.server

# 3. Start Flask API Bridge - port 9090  
python cyberbackup_api_server.py

# 4. Access Web UI at http://127.0.0.1:9090/
```

### System Health Verification
```bash
# Check all services are running
netstat -an | findstr ":9090\|:1256"  # Both ports should show LISTENING
tasklist | findstr "python"           # Should show multiple Python processes

# Verify file transfers
dir "src\server\received_files"       # Check for actual transferred files
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

## Current System Status (2025-08-01)

**✅ FULLY OPERATIONAL** - All 4 layers working with proven end-to-end file transfers  
**🔧 RECENTLY FIXED (2025-08-01)**: API server startup issue in one-click script resolved

### Key Achievements
- **Complete Integration**: Web UI → Flask API → C++ Client → Python Server chain working
- **Socket Communication**: 25-second timeout fixes prevent subprocess termination
- **Protocol Compliance**: RSA-1024 X.509 format (160-byte) + AES-256-CBC encryption
- **Windows Compatibility**: Socket TIME_WAIT and Unicode encoding issues resolved
- **Performance Optimized**: Web GUI enhanced with DOM caching and resource management

### System Capabilities
1. **Web Interface Upload**: Users can browse to http://127.0.0.1:9090/, select files, register usernames, and upload files
2. **Real-Time Server Monitoring**: Server GUI shows live user registrations and file transfers as they happen  
3. **Secure Encryption**: RSA-1024 key exchange followed by AES-256-CBC file encryption
4. **Multi-User Support**: Multiple users can register and upload files concurrently
5. **File Integrity Verification**: CRC32 checksums ensure uploaded files match originals
6. **Cross-Layer Integration**: All 4 architectural layers working seamlessly
7. **Windows Console Compatibility**: All Unicode encoding issues resolved for stable operation
8. **Process Management**: Robust subprocess handling with timeout protection and proper cleanup


## Quick Troubleshooting Guide

### Common Issues & Solutions

#### System Won't Start
```bash
# Check port conflicts
netstat -an | findstr ":9090\|:1256"

# Kill existing processes
taskkill /f /im python.exe
taskkill /f /im EncryptedBackupClient.exe

# Restart with one-click script
python one_click_build_and_run.py
```

#### "Connection Refused" in Browser
- **Issue**: Flask API server (port 9090) not running
- **Solution**: Check both servers are running: `tasklist | findstr "python"`
- **Windows TIME_WAIT**: Wait 30-60 seconds if recently restarted, or use cleanup commands above

#### One-Click Script API Server Won't Start (RESOLVED 2025-08-01)
- **Issue**: `one_click_build_and_run.py` runs but API server fails to start
- **Root Cause**: Subprocess output capture caused pipe blocking + syntax error in API server
- **Fix Applied**: Removed subprocess pipe capture, added process health monitoring, fixed syntax error
- **Status**: ✅ **RESOLVED** - Enhanced error diagnostics now provide specific troubleshooting guidance

#### File Transfers Fail
- **Verify endpoint**: Check `src/server/received_files/` for actual files (exit codes are unreliable)
- **Protocol issues**: Ensure using latest `build/Release/EncryptedBackupClient.exe`
- **Configuration**: Verify `transfer.info` has exactly 3 lines: `server:port`, `username`, `filepath`

#### Build Failures
- **vcpkg required**: Must use `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"`
- **Missing dependencies**: Run `pip install -r requirements.txt` (flask-cors commonly missing)

### Emergency Recovery
```bash
# Complete system reset
taskkill /f /im python.exe
taskkill /f /im EncryptedBackupClient.exe
del transfer.info
python one_click_build_and_run.py
```

## Additional Resources

### Technical Implementation Details
- **`.github/copilot-instructions.md`**: In-depth subprocess management patterns, binary protocol specifications, and security implementation details
- **Evidence of Success**: Check `src/server/received_files/` directory for actual file transfers (multiple test files demonstrate working system)

