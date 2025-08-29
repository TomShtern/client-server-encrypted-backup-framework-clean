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
**Flask API Bridge as Coordination Hub**: The Flask API Bridge (`cyberbackup_api_server.py` + `real_backup_executor.py`) is the central coordination hub. Web UI communicates ONLY with Flask API, never directly with C++ client or Python server.

**RealBackupExecutor** manages subprocess execution:
1. Generate `transfer.info` (3 lines: `server:port`, `username`, `filepath`)
2. Launch C++ client: `subprocess.Popen([client_exe, "--batch"], cwd=working_dir)`
3. **FileReceiptProgressTracker** watches `received_files/` for ground truth completion

### Architecture Flow Patterns
**Web Client Path**: `Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server`
**Direct Client Path**: `C++ Client → Python Server` (both clients connect to same server via different pathways)

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

# Code Quality & Linting
pyright .                           # Type checking (configured in pyproject.toml)
# Recommended additional linting tools:
# pip install ruff pylint mypy
# ruff check .                      # Fast Python linter
# pylint **/*.py                    # Comprehensive linting
# mypy .                           # Advanced type checking

# Testing (test complete web→API→C++→server chain)
python scripts/testing/master_test_suite.py  # Comprehensive suite (72+ scenarios) - PRIMARY TEST
python tests/test_gui_upload.py              # Full integration test
python tests/integration/run_integration_tests.py # Complete integration suite
python scripts/testing/quick_validation.py   # Quick system validation
python scripts/test_system_working.py        # System validation
python scripts/test_emoji_support.py         # Unicode/emoji support
python tests/debug_file_transfer.py          # Debug transfer issues
python tests/focused_boundary_test.py        # Boundary condition testing
python tests/test_performance_flow.py        # Performance benchmarking

# Validation Scripts
python scripts/testing/validate_null_check_fixes.py  # Null check validation
python scripts/testing/validate_server_gui.py        # GUI validation
python scripts/fix_and_test.py                       # Quick system validation

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
- **Python Dependencies**: See `requirements.txt` - Critical: flask-cors, flask-socketio, watchdog, sentry-sdk, psutil
- **Development Environment**: Python 3.13+, CMake 3.15+, vcpkg for C++ dependencies
- **Virtual Environments**: `flet_venv` for Flet GUI development

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
- **Static IV**: Zero IV allows pattern analysis (LOW PRIORITY)
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

**✅ PRODUCTION READY** - Modern Flet-based server GUI with complete Material Design 3 compliance and full functionality

**Location**: `flet_server_gui/` - Complete modular Material Design 3 desktop application  
**Launch**: `python launch_flet_gui.py` (requires `flet_venv` virtual environment)  
**Status**: 100% VALIDATED - All components operational, all buttons functional, UTF-8 compliant

### **Recent Major Updates (2025-08-26)**
- **✅ Complete Button Functionality**: All dashboard buttons fully operational with real server integration
- **✅ UTF-8 Integration Complete**: International filename support across all entry points
- **✅ Material Design 3 Validated**: 100% API compatibility confirmed, all color/icon constants verified
- **✅ Dual Server Bridge System**: Robust fallback from full ModularServerBridge to SimpleServerBridge
- **✅ Professional Dashboard**: Real-time monitoring, animated activity log, responsive scaling
- **✅ Production Validation**: Comprehensive test suite confirms all functionality working

### **Validation Status - ALL TESTS PASS**
- **IMPORTS**: ✅ PASS - Flet, ThemeManager, DashboardView, ServerBridge all operational
- **API COMPATIBILITY**: ✅ PASS - All ft.Colors.*, ft.Icons.*, ft.Components verified working
- **DASHBOARD FUNCTIONALITY**: ✅ PASS - All button handlers, animations, real-time updates functional

### **Critical Flet Development Patterns (ESSENTIAL)**

#### **1. Verified API Usage - 100% Compatible**
```python
# ✅ VERIFIED WORKING - All tested and confirmed:
import flet as ft

# Colors (all verified available)
ft.Colors.PRIMARY, ft.Colors.ERROR, ft.Colors.SURFACE, ft.Colors.ON_SURFACE
ft.Colors.ON_SURFACE_VARIANT, ft.Colors.OUTLINE, ft.Colors.OUTLINE_VARIANT

# Icons (all verified available)  
ft.Icons.DASHBOARD, ft.Icons.PLAY_ARROW, ft.Icons.STOP, ft.Icons.REFRESH
ft.Icons.SETTINGS, ft.Icons.CHECK_CIRCLE, ft.Icons.ERROR_OUTLINE

# Components (all verified available)
ft.Card, ft.Container, ft.Column, ft.Row, ft.ResponsiveRow
ft.FilledButton, ft.OutlinedButton, ft.TextButton

# ❌ INCOMPATIBLE APIs - These cause runtime errors:
ft.MaterialState.DEFAULT    # ❌ MaterialState doesn't exist
ft.Expanded()              # ❌ Use expand=True on components instead
ft.Colors.SURFACE_VARIANT  # ❌ Use ft.Colors.SURFACE_TINT instead
```

#### **2. Dual Server Bridge System**
```python
# ✅ ROBUST PATTERN - Automatic fallback system:
try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    BRIDGE_TYPE = "Full ModularServerBridge"
except Exception as e:
    from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge as ServerBridge
    BRIDGE_TYPE = "SimpleServerBridge (Fallback)"

# This ensures GUI always works even if full server integration fails
```

#### **3. Async Initialization Pattern**
```python
# ✅ CORRECT - Use page.on_connect for async operations:
async def _on_page_connect(self, e):
    """Start background tasks when page is connected"""
    asyncio.create_task(self.monitor_loop())
    
    if self.current_view == "dashboard" and self.dashboard_view:
        self.dashboard_view.start_dashboard_sync()  # Sync UI setup
        asyncio.create_task(self.dashboard_view.start_dashboard_async())  # Async tasks

# ❌ WRONG - Don't start async tasks immediately in view constructors
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

### Flet Architecture & Key Components ✅ CONSOLIDATED
**STATUS: PRODUCTION READY** - Modern Flet-based Material Design 3 GUI with organized modular structure

**Launch**: `python launch_flet_gui.py` (requires `flet_venv` virtual environment)  
**Features**: Enterprise architecture, real data integration, UTF-8 support, responsive design


### **Button Handler Implementation Pattern**
```python
# ✅ FULLY FUNCTIONAL PATTERN - All dashboard buttons working:
async def _on_start_server(self, e):
    """Handle start server button with real functionality"""
    self.add_log_entry("System", "Starting backup server...", "INFO")
    try:
        success = await self.server_bridge.start_server()
        if success:
            self.add_log_entry("System", "Server started successfully!", "SUCCESS")
            await self._async_update_server_status()
        else:
            self.add_log_entry("System", "Failed to start server", "ERROR")
    except Exception as ex:
        self.add_log_entry("System", f"Start error: {str(ex)}", "ERROR")
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

## Current Implementation Status

**✅ Fully Operational System**:
- **5-layer architecture**: Complete Web UI → Flask API → C++ Client → Python Server → File Storage  
- **72+ successful transfers**: Production evidence in `received_files/`
- **Enterprise Flet GUI**: Material Design 3 server management with real data integration
- **UTF-8 support**: Complete Unicode filename handling (Hebrew + emoji)
- **Thread-safe UI**: Resolved async/threading issues and race condition fixes

## Documentation & Project Evidence
- **`TECHNICAL_DIAGRAMS.md`**: Architecture diagrams  
- **`FLET_GUI_ENHANCEMENT_PROJECT.md`**: Flet GUI implementation progress
- **`refactoring_report.md`**: Refactoring and technical debt analysis
- **`Shared/unified_monitor.py`**: Unified file monitoring system
- **Virtual Environment**: `flet_venv` - Primary for Flet GUI

## Git Workflow & Branching

### Branch Structure
- **Main branch**: `12_06_2025_checkpoint` (use for pull requests)
- **Current branch**: `clean-main` (active development)
- **Files with uncommitted changes**: 
  - `flet_server_gui/components/client_table_renderer.py`
  - `flet_server_gui/components/log_action_handlers.py` 
  - `flet_server_gui/views/clients.py`
  - `flet_server_gui/views/logs_view.py`

### Git Commands
```bash
# Check current status and branch
git status
git branch

# Commit workflow
git add .
git commit -m "descriptive message"

# Create pull requests to main branch
git checkout 12_06_2025_checkpoint  # Switch to main branch for PRs
```

**Note**: Follow the "Redundant File Analysis Protocol" section before deleting any files - valuable utilities often hidden in "simple" components.