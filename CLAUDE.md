# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A **5-layer Client-Server Encrypted Backup Framework** implementing secure file transfer with RSA-1024 + AES-256-CBC encryption. **✅ FULLY OPERATIONAL** - 72+ successful transfers in `received_files/`.

### Architecture & Data Flow
**Web UI** → **Flask API (9090)** → **C++ Client** → **Python Server (1256)** → **File Storage**

1. **Web UI** (`Client/Client-gui/NewGUIforClient.html`) - 8000+ line SPA with professional UI enhancements, tooltips, real-time progress
2. **Flask API Bridge** (`api_server/cyberbackup_api_server.py`) - HTTP API server (port 9090), WebSocket broadcasting, subprocess management
3. **C++ Client** (`Client/cpp/client.cpp`) - Native encryption engine, RSA-1024 + AES-256-CBC, binary protocol, requires `--batch` mode
4. **Python Server** (`python_server/server/server.py`) - Multi-threaded TCP server (port 1256), file decryption, storage in `received_files/`
5. **Server Management GUI** (`python_server/server_gui/ServerGUI.py`) - Tkinter-based administration interface

## Core Technical Implementation

### Critical Integration Pattern
**RealBackupExecutor** manages subprocess execution:
1. Generate `transfer.info` (3 lines: `server:port`, `username`, `filepath`)
2. Launch C++ client: `subprocess.Popen([client_exe, "--batch"], cwd=working_dir)`
3. Monitor stdout/stderr for progress parsing
4. **FileReceiptProgressTracker** watches `received_files/` for ground truth completion

### Multi-Layer Progress Monitoring
- **Layer 0**: FileReceiptProgressTracker - File appears → immediate 100% (HIGHEST PRIORITY)
- **Layer 1**: StatisticalProgressTracker - Parse C++ stdout with `progress_config.json` calibration
- **Layer 2**: TimeBasedEstimator - File size-based time estimation with historical data
- **Layer 3**: BasicProcessingIndicator - Fallback spinner for UI activity
- **CallbackMultiplexer** - Routes progress to correct job handlers, eliminates race conditions

### Protocol & Security
- **Custom TCP Protocol**: 23-byte headers, protocol version 3, ports 1256/9090
- **Request Codes**: REQ_REGISTER(1025), REQ_SEND_FILE(1028), RESP_FILE_CRC(1603)
- **Encryption**: RSA-1024 key exchange + AES-256-CBC file encryption + CRC32 verification
- **Critical Verification**: File presence in `received_files/` is ONLY reliable success indicator (exit codes unreliable)

## Essential Commands

### Build & Run System
```bash
# CRITICAL: Build C++ client with vcpkg toolchain
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build --config Release  # Output: build/Release/EncryptedBackupClient.exe

# Start system (RECOMMENDED)
python scripts/one_click_build_and_run.py  # Full build + deploy + launch
python scripts/launch_gui.py              # Quick start API server + browser

# Manual service startup
python python_server/server/server.py        # Port 1256 (START FIRST)
python api_server/cyberbackup_api_server.py  # Port 9090
python python_server/server_gui/__main__.py   # Server GUI (optional)

# Dependencies
pip install -r requirements.txt  # Critical: flask-cors, flask-socketio, watchdog, sentry-sdk
```

### System Health & Testing
```bash
# Verify system status
netstat -an | findstr ":9090\\|:1256"  # Both ports LISTENING
tasklist | findstr "python"           # Multiple Python processes
dir "received_files"                  # Check actual transferred files

# Testing (test complete web→API→C++→server chain)
python tests/test_gui_upload.py              # Full integration test
python scripts/testing/master_test_suite.py  # Comprehensive suite
python scripts/testing/quick_validation.py   # Quick validation
python scripts/test_emoji_support.py         # Unicode/emoji support

# Emergency recovery
taskkill /f /im python.exe && taskkill /f /im EncryptedBackupClient.exe
del transfer.info && python scripts/one_click_build_and_run.py
```

## Critical Configuration & Patterns

### Required Configuration
- **transfer.info**: Exactly 3 lines: `server:port`, `username`, `filepath` (must be in C++ client working directory)
- **--batch flag**: CRITICAL for subprocess execution (prevents hanging)
- **vcpkg toolchain**: Required for C++ builds (boost, cryptopp, zlib, sentry-native)
- **Dependencies**: flask-cors, flask-socketio, watchdog, sentry-sdk, psutil

### Integration Patterns
```python
# Subprocess management pattern
subprocess.Popen([client_exe, "--batch"], cwd=transfer_info_dir, 
                stdin=PIPE, stdout=PIPE, stderr=PIPE)

# File verification pattern (CRITICAL)
verify_file_in_received_files_dir()  # PRIMARY verification
compare_sha256_hashes()              # Integrity check
check_network_activity_port_1256()   # Connection verification
```

### Security Vulnerabilities (Active Issues)
- **Static IV**: Zero IV allows pattern analysis (HIGH PRIORITY)
- **No HMAC**: CRC32 provides no tampering protection (MEDIUM PRIORITY) 
- **Deterministic encryption**: Same plaintext produces same ciphertext

### Known Issues & Verification
- **False Success**: Zero exit code ≠ successful transfer (always check `received_files/`)
- **Port Conflicts**: Ensure 9090/1256 are free (Windows TIME_WAIT: wait 30-60s)
- **Success Verification**: File presence in `received_files/` is ONLY reliable indicator

## System Status & UTF-8 Support

**✅ FULLY OPERATIONAL** - All 5 layers working, 72+ successful transfers in `received_files/`

### UTF-8 Unicode Support
**Complete solution** for international filenames (Hebrew + emoji support):
```python
# Entry point scripts - add ONE line:
import Shared.utils.utf8_solution  # Auto-enables UTF-8 for subprocess operations

# Now all subprocess calls use UTF-8 automatically:
result = subprocess.run([exe, "--batch"], capture_output=True)  # Hebrew+emoji works!
```
**Components**: `Shared/utils/utf8_solution.py`, Windows UTF-8 console (CP 65001), environment vars `PYTHONIOENCODING=utf-8`

## Troubleshooting & Recovery

### Common Issues
- **System Won't Start**: Usually code issues - check running processes
- **Connection Refused**: Flask API (9090) not running, API server closes on code changes
- **File Transfers Fail**: Check `received_files/` for actual files (exit codes unreliable), verify `transfer.info` 3-line format
- **Build Failures**: Missing vcpkg toolchain or flask-cors dependencies
- **Windows TIME_WAIT**: Wait 30-60s after restart for port release

### Emergency Recovery
```bash
taskkill /f /im python.exe && taskkill /f /im EncryptedBackupClient.exe
del transfer.info && python scripts/one_click_build_and_run.py
```

## Critical Race Condition Analysis

### ✅ RESOLVED: Global Singleton Race Condition
**Problem**: API server uses global singleton `backup_executor` shared across concurrent requests, causing progress updates routed to wrong clients.

**Solution**: CallbackMultiplexer system routes progress callbacks to correct job handlers:
- Maintains per-job handlers in thread-safe dictionary
- Routes progress updates to all active job handlers
- Eliminates race condition by multiplexing instead of overwriting callbacks

### File Receipt Override System (2025-08-03)
**FileReceiptProgressTracker** provides ground truth completion by monitoring server's `received_files/` in real-time:
- **Real-Time Monitoring**: Uses watchdog library with polling fallback
- **File Stability Detection**: Ensures files completely written before signaling completion
- **Progress Override**: Immediately signals 100% when file appears on server
- **Location**: `src/api/real_backup_executor.py` (lines 473-663)

## Additional Resources

### Documentation Files
- **`TECHNICAL_DIAGRAMS.md`**: Detailed ASCII architecture diagrams extracted from this file
- **`UI_Enhancement_Documentation.md`**: Professional UI enhancement suite documentation
- **`refactoring_report.md`**: Comprehensive refactoring work and technical debt analysis
- **`Shared/unified_monitor.py`**: Unified file monitoring system
- **Evidence of Success**: Check `received_files/` for actual transfers (67+ files demonstrate production usage)