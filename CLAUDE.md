# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A **5-layer Client-Server Encrypted Backup Framework** implementing secure file transfer with RSA-1024 + AES-256-CBC encryption. **✅ FULLY OPERATIONAL** - 72+ successful transfers in `received_files/`.

### Architecture & Data Flow
**Web UI** → **Flask API (9090)** → **C++ Client** → **Python Server (1256)** → **File Storage**

1. **Web UI** (`Client/Client-gui/NewGUIforClient.html`) - Professional SPA with real-time progress
2. **Flask API Bridge** (`api_server/cyberbackup_api_server.py`) - HTTP API server (port 9090), WebSocket broadcasting
3. **C++ Client** (`Client/cpp/client.cpp`) - Native encryption engine, requires `--batch` mode
4. **Python Server** (`python_server/server/server.py`) - Multi-threaded TCP server (port 1256), file storage in `received_files/`
5. **Server Management GUI**: **Flet Material Design 3** (`flet_server_gui/main.py`) - Enterprise-grade server administration interface

## Core Technical Implementation

### Critical Integration Pattern
**RealBackupExecutor** manages subprocess execution:
1. Generate `transfer.info` (3 lines: `server:port`, `username`, `filepath`)
2. Launch C++ client: `subprocess.Popen([client_exe, "--batch"], cwd=working_dir)`
3. **FileReceiptProgressTracker** watches `received_files/` for ground truth completion

### Multi-Layer Progress Monitoring
- **Layer 0**: FileReceiptProgressTracker - File appears → immediate 100% (HIGHEST PRIORITY)
- **CallbackMultiplexer** - Routes progress to correct job handlers, eliminates race conditions
- **Layer 1+**: Statistical/Time-based estimators with fallback spinner

### Protocol & Security
- **Custom TCP Protocol**: 23-byte headers, protocol version 3, ports 1256/9090
- **Encryption**: RSA-1024 key exchange + AES-256-CBC + CRC32 verification
- **Critical Verification**: File presence in `received_files/` is ONLY reliable success indicator

## Essential Commands

### Build & Run System
```bash
# CRITICAL: Build C++ client with vcpkg toolchain
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build --config Release  # Output: build/Release/EncryptedBackupClient.exe

# Start system (RECOMMENDED)
python scripts/one_click_build_and_run.py  # Full build + deploy + launch (CANONICAL)
python scripts/launch_gui.py              # Quick start API server + browser

# Additional Launch Options
python launch_flet_gui.py           # Launch Flet server GUI (RECOMMENDED)
python python_server/server_gui/ServerGUI.py  # Launch TKinter server GUI (legacy)
python scripts/start_backup_server.py  # Start backup server standalone
.\start_server_gui.bat                 # Batch file server GUI launcher
.\start_backup_utf8.bat               # UTF-8 optimized backup launcher

# Manual service startup
python python_server/server/server.py        # Port 1256 (START FIRST)
python api_server/cyberbackup_api_server.py  # Port 9090

# Dependencies
pip install -r requirements.txt  # Critical: flask-cors, flask-socketio, watchdog, sentry-sdk
```

### System Health & Testing
```bash
# Verify system status
netstat -an | findstr ":9090\\|:1256"  # Both ports LISTENING
dir "received_files"                  # Check actual transferred files

# Testing (test complete web→API→C++→server chain)
python tests/test_gui_upload.py              # Full integration test
python scripts/testing/master_test_suite.py  # Comprehensive suite (72+ scenarios)
python scripts/testing/quick_validation.py   # Quick system validation
python scripts/test_emoji_support.py         # Unicode/emoji support
python tests/integration/run_integration_tests.py # Complete integration suite
python tests/debug_file_transfer.py          # Debug transfer issues
python tests/focused_boundary_test.py        # Boundary condition testing
python tests/test_performance_flow.py        # Performance benchmarking

# System Maintenance & Diagnostics
python scripts/check_dependencies.py   # Verify all dependencies
python scripts/monitor_logs.py         # Real-time log monitoring  
python scripts/fix_vcpkg_issues.py     # Fix vcpkg build issues

# Emergency recovery
taskkill /f /im python.exe && taskkill /f /im EncryptedBackupClient.exe
del transfer.info && python scripts/one_click_build_and_run.py
```

## UTF-8 Unicode Support (CRITICAL)

**Complete solution** for international filenames (Hebrew + emoji support):
```python
# Entry point scripts - add ONE line:
import Shared.utils.utf8_solution  # Auto-enables UTF-8 for subprocess operations

# Now all subprocess calls use UTF-8 automatically:
result = subprocess.run([exe, "--batch"], capture_output=True)  # Hebrew+emoji works!
```
**Components**: `Shared/utils/utf8_solution.py`, Windows UTF-8 console (CP 65001), environment vars `PYTHONIOENCODING=utf-8`

## Critical Configuration & Patterns

### Required Configuration
- **transfer.info**: Exactly 3 lines: `server:port`, `username`, `filepath`
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
```

### Redundant File Analysis Protocol (CRITICAL FOR DEVELOPMENT)
**Before deleting any file that appears redundant, ALWAYS follow this process**:

1. **Analyze thoroughly**: Read through the "redundant" file completely
2. **Compare functionality**: Check if it contains methods, utilities, or features not present in the "original" file, that could benifit the original file.
3. **Identify valuable code**: Look for:
   - Helper functions or utilities that could be useful
   - Error handling patterns that are more robust
   - Configuration options or constants that might be needed
   - Documentation or comments that provide important context
   - Different implementation approaches that might be superior
4. **Integration decision**: If valuable code is found:
   - Extract and integrate the valuable parts into the primary file
   - Test that the integration works correctly
   - Ensure no functionality is lost
5. **Safe deletion**: Only after successful integration, delete the redundant file

**Why this matters**: "Simple" or "mock" files often contain valuable utilities, edge case handling, or configuration details that aren't obvious at first glance. Premature deletion can result in lost functionality and regression bugs.

**Example**: A "simple" client management component might contain useful date formatting functions or error message templates that the "comprehensive" version lacks.

### Security Vulnerabilities (Active Issues)
- **Static IV**: Zero IV allows pattern analysis (HIGH PRIORITY)
- **No HMAC**: CRC32 provides no tampering protection (MEDIUM PRIORITY) 
- **Deterministic encryption**: Same plaintext produces same ciphertext

### Known Issues & Critical Notes
- **Success Verification**: File presence in `received_files/` is ONLY reliable indicator (exit codes unreliable)
- **Port Conflicts**: Ensure 9090/1256 are free (Windows TIME_WAIT: wait 30-60s)

### Critical Files for AI Development Context
```bash
# These files are essential for understanding system architecture
api_server/cyberbackup_api_server.py    # Flask API coordination hub
api_server/real_backup_executor.py      # Subprocess management patterns  
python_server/server/server.py          # Multi-threaded TCP server
Shared/utils/unified_config.py          # Configuration management
Shared/utils/file_lifecycle.py          # Race condition prevention
scripts/one_click_build_and_run.py      # CANONICAL launcher - primary entry point

# Flet GUI Components (PRIMARY SYSTEM - ENTERPRISE READY)
flet_server_gui/main.py                 # Primary GUI application (PRODUCTION READY)
flet_server_gui/utils/server_bridge.py  # ✅ Complete server integration (Phase 4)
flet_server_gui/utils/settings_manager.py  # ✅ Real configuration management (Phase 5)
flet_server_gui/components/dialog_system.py  # GUI dialog management
flet_server_gui/views/settings_view.py   # ✅ Comprehensive settings UI (Phase 5)
flet_server_gui/views/logs_view.py      # ✅ Real-time log viewer (Phase 5)
flet_server_gui/services/log_service.py # ✅ Live log monitoring service (Phase 5)
flet_server_gui/components/real_performance_charts.py # ✅ Live metrics (Phase 5)
flet_server_gui/components/enhanced_performance_charts.py # ✅ Advanced charts with alerts (Phase 7)
flet_server_gui/components/enhanced_table_components.py # ✅ Professional data tables (Phase 7)
flet_server_gui/components/system_integration_tools.py # ✅ File integrity & session mgmt (Phase 7)

# Legacy TKinter GUIs (FUNCTIONAL BUT REPLACED)
python_server/server_gui/ServerGUI.py   # Legacy TKinter GUI (complex version)
python_server/server_gui/ORIGINAL_serverGUIV1.py  # Legacy TKinter GUI (simple version)
```

## Legacy GUI Systems

### TKinter Server GUIs (Original Legacy)
**Status**: ✅ Functional but replaced by Flet GUI  
**Purpose**: Original server administration interfaces  

#### TKinter GUI Versions
- **Simple Version**: `python_server/server_gui/ORIGINAL_serverGUIV1.py` - Basic functionality
- **Complex Version**: `python_server/server_gui/ServerGUI.py` - Full-featured with analytics, charts, modern widgets

**Features**: Live performance charts (matplotlib), system tray, drag-and-drop, modern dark theme, comprehensive database browser, client management, file operations

**Launch**: `python python_server/server_gui/ServerGUI.py` (standalone mode)

## Flet Material Design 3 GUI (CRITICAL - Current Primary GUI)

**✅ FULLY OPERATIONAL** - Modern Flet-based server GUI with complete TKinter feature parity + enterprise enhancements

**Location**: `flet_server_gui/` - Complete modular Material Design 3 desktop application  
**Launch**: `python launch_flet_gui.py` (requires `flet_venv` virtual environment)  
**Status**: Production-ready with 100% real data integration, zero mock/simulation code

### Critical Flet API Usage Rules (ESSENTIAL)
**MOST IMPORTANT**: Flet has inconsistent naming conventions that cause runtime errors:

```python
# ✅ CORRECT API Usage:
import flet as ft

# Colors: Capital C, capital constants
ft.Colors.PRIMARY, ft.Colors.ERROR, ft.Colors.SURFACE

# Icons: Use ft.Icons.NAME (uppercase)  
ft.Icons.DASHBOARD, ft.Icons.PLAY_ARROW, ft.Icons.SETTINGS

# ❌ WRONG - These cause runtime errors:
ft.colors.PRIMARY       # ❌ No 'colors' attribute
ft.icons.dashboard      # ❌ Should be ft.Icons.DASHBOARD
```

### Responsive Design Pattern
**Standard approach**: Use `ResponsiveRow` + `expand=True`, avoid hardcoded dimensions:

```python
# ✅ CORRECT - Responsive scaling:
ft.Card(content=container, expand=True)  # Auto-scales
ft.ResponsiveRow([
    ft.Column(col={"sm": 12, "md": 6}, controls=[card], expand=True)
])

# ❌ WRONG - Fixed dimensions break on different screen sizes:
ft.Container(width=350, height=400)  # Causes clipping/cramming
```

### Flet Architecture & Key Components
```
flet_server_gui/
├── main.py                    # Main application with Material Design 3 theme
├── launch_flet_gui.py         # Easy launcher with error handling
├── components/               # UI components
│   ├── dialog_system.py       # Complete dialog management
│   ├── comprehensive_client_management.py  # Full client operations
│   ├── comprehensive_file_management.py    # Full file operations  
│   ├── enhanced_performance_charts.py  # Advanced charts with alerts
│   ├── enhanced_table_components.py    # Professional data tables
│   ├── system_integration_tools.py     # File integrity & session mgmt
│   ├── server_status_card.py  # Real-time server monitoring
│   └── control_panel_card.py  # Start/stop/restart controls
├── utils/                    # Infrastructure utilities
│   ├── server_bridge.py       # Complete server integration
│   └── settings_manager.py    # Real configuration management
├── views/                    # Full-screen views
│   ├── settings_view.py       # Comprehensive settings UI
│   └── logs_view.py          # Real-time log viewer
└── services/                 # Background services
    └── log_service.py        # Real-time log monitoring
```

### Key Features
- **Enterprise Architecture**: Professional modular design with clean separation of concerns
- **Native Material Design 3**: Built-in components, perfect text rendering (chosen over KivyMD due to text stacking issues)
- **Real Data Integration**: Direct DatabaseManager connection (17 clients, 14 files), zero mock/simulation code
- **Complete Functionality**: Server operations, analytics, file integrity, session management
- **Responsive Design**: Native ResponsiveRow + expand=True eliminates clipping/cramming issues

### Setup & Launch
```bash
# Setup (one-time)
python -m venv flet_venv
powershell -Command ".\flet_venv\Scripts\Activate.ps1"
pip install flet

# Launch
python launch_flet_gui.py          # Desktop application  
python launch_flet_gui.py --web    # Web browser version
```

### Common Development Issues
```bash
# Critical API errors to avoid:
# ❌ ft.colors.PRIMARY → ✅ ft.Colors.PRIMARY  
# ❌ ft.icons.dashboard → ✅ ft.Icons.DASHBOARD
# ❌ ft.Icons.play_arrow → ✅ ft.Icons.PLAY_ARROW
```

## System Recovery & Troubleshooting
```bash
# System Won't Start - kill processes and restart
taskkill /f /im python.exe && taskkill /f /im EncryptedBackupClient.exe
del transfer.info && python scripts/one_click_build_and_run.py

# Port conflicts (Windows TIME_WAIT: wait 30-60s)
netstat -an | findstr ":9090\\|:1256"
```

## Race Condition Analysis & File Monitoring
**✅ RESOLVED**: Global singleton race condition in API server  
**Solution**: CallbackMultiplexer routes progress to correct job handlers, eliminates race conditions  
**FileReceiptProgressTracker**: Monitors `received_files/` for ground truth completion with watchdog library

## Current Implementation Status (2025-08-25)

**✅ Fully Operational System**:
- **5-layer architecture**: Complete Web UI → Flask API → C++ Client → Python Server → File Storage  
- **72+ successful transfers**: Production evidence in `received_files/`
- **Enterprise Flet GUI**: Material Design 3 server management with real data integration (17 clients, 14 files)
- **Zero mock data**: 100% real server operations, database connections, file system integration

**Key Technical Achievements**:
- **Thread-safe UI**: Fixed async/threading issues, proper background→main thread patterns
- **Responsive design**: Native Flet ResponsiveRow + expand=True eliminates layout issues  
- **API compatibility**: All Flet API naming inconsistencies resolved
- **Race condition fixes**: CallbackMultiplexer eliminates progress tracking conflicts
- **UTF-8 support**: Complete Unicode filename handling (Hebrew + emoji)

## Documentation & Project Evidence
- **`TECHNICAL_DIAGRAMS.md`**: Architecture diagrams  
- **`FLET_GUI_ENHANCEMENT_PROJECT.md`**: Flet GUI implementation progress
- **`refactoring_report.md`**: Refactoring and technical debt analysis
- **`Shared/unified_monitor.py`**: Unified file monitoring system
- **Virtual Environment**: `flet_venv` - Primary for Flet GUI

**Note**: Follow the "Redundant File Analysis Protocol" section before deleting any files - valuable utilities often hidden in "simple" components.