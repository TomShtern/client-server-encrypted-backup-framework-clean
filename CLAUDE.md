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
5. **Server Management GUI**: **KivyMD Material Design 3** (`kivymd_gui/main.py`) - Modern server administration interface

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
python scripts/one_click_build_and_run.py  # Full build + deploy + launch
python scripts/launch_gui.py              # Quick start API server + browser

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
python scripts/testing/master_test_suite.py  # Comprehensive suite
python scripts/test_emoji_support.py         # Unicode/emoji support

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

### Security Vulnerabilities (Active Issues)
- **Static IV**: Zero IV allows pattern analysis (HIGH PRIORITY)
- **No HMAC**: CRC32 provides no tampering protection (MEDIUM PRIORITY) 
- **Deterministic encryption**: Same plaintext produces same ciphertext

### Known Issues & Critical Notes
- **Success Verification**: File presence in `received_files/` is ONLY reliable indicator (exit codes unreliable)
- **Port Conflicts**: Ensure 9090/1256 are free (Windows TIME_WAIT: wait 30-60s)

## KivyMD Material Design 3 Server GUI (CRITICAL)

**✅ FULLY OPERATIONAL** - Modern Material Design 3 server administration interface

### Setup & Dependencies
```bash
# CRITICAL: Must use kivy_venv_new virtual environment
.\kivy_venv_new\Scripts\activate

# Core dependencies (STABLE commit for reliability)
pip install git+https://github.com/kivymd/KivyMD.git@d2f7740  # MD3 support, no animation crashes
pip install psutil==7.0.0  # System monitoring (REQUIRED)

# Run KivyMD GUI
python kivymd_gui\main.py
```

### KivyMD 2.0.x API Reference (ESSENTIAL)

#### Critical Import Path Changes
```python
# ✅ CORRECT 2.0.x imports:
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarLeadingButtonContainer, MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem, MDNavigationRailItemIcon, MDNavigationRailItemLabel
from kivymd.uix.selectioncontrol import MDSwitch  # NOT kivymd.uix.switch
from kivymd.uix.textfield import MDTextField, MDTextFieldSupportingText
```

#### MDTopAppBar (Component-Based Architecture)
```python
# ❌ OLD (1.x): 
MDTopAppBar(title="My Title", left_action_items=[...])

# ✅ NEW (2.0.x):
MDTopAppBar(
    MDTopAppBarLeadingButtonContainer(
        MDActionTopAppBarButton(icon="menu", on_release=callback)
    ),
    MDTopAppBarTitle(text="My Title"),
    MDTopAppBarTrailingButtonContainer(
        MDActionTopAppBarButton(icon="refresh", on_release=callback)
    ),
    type="small"  # Options: "small", "medium", "large"
)
```

#### MDNavigationRail (Component-Based Navigation)
```python
# ❌ OLD (1.x): 
MDNavigationRailItem(icon="dashboard", text="Dashboard", on_release=callback)

# ✅ NEW (2.0.x):
nav_item = MDNavigationRailItem(
    MDNavigationRailItemIcon(icon="dashboard"),
    MDNavigationRailItemLabel(text="Dashboard")
)
nav_item.bind(active=lambda instance, value, screen="dashboard": navigate_to_screen(screen) if value else None)
```

#### MDTextField (Component-Based Supporting Text)
```python
# ❌ OLD (1.x): 
MDTextField(helper_text="Default: 1256", ...)

# ✅ NEW (2.0.x):
MDTextField(
    MDTextFieldSupportingText(text="Default: 1256"),
    mode="outlined",
    hint_text="Port number"
)
```

### Critical Initialization Pattern
```python
# MUST import UTF-8 solution early
import Shared.utils.utf8_solution

# Set Material Design 3 theme
self.theme_cls.material_style = "M3"
self.theme_cls.theme_style = "Dark"  # or "Light"
self.theme_cls.primary_palette = "Blue"
```

### Dynamic Updates (2.0.x Compatible)
```python
# Update MDTopAppBarTitle text dynamically
for child in self.top_bar.children:
    if hasattr(child, 'text') and 'Title' in child.__class__.__name__:
        child.text = "New Title"
        break

# Update MDTextFieldSupportingText dynamically
for child in textfield.children:
    if hasattr(child, 'text') and 'SupportingText' in child.__class__.__name__:
        child.text = "New supporting text"
        break
```

### Key Migration Insights (Resolved Issues)
1. **Import Path Migration**: All major components moved in 2.0.x (`topappbar` → `appbar`, `switch` → `selectioncontrol`)
2. **Component Architecture**: Shift from parameter-based to component-based design
3. **Property Cleanup**: Many legacy properties removed (`use_resizeable`, `helper_text`, etc.)
4. **Event Handling**: Changed from direct callbacks to binding patterns
5. **Stable Version**: Always use commit `d2f7740` to avoid animation crashes

### Critical Fixes Applied (2025-08-21)
**✅ FULLY RESOLVED**: All KivyMD 2.0.x compatibility issues fixed, GUI now fully functional
1. **MDFloatingActionButton → MDIconButton**: Replaced deprecated FAB with icon buttons in `files.py` and `logs.py`
2. **MDTextFieldSupportingText Removal**: Component doesn't exist in 2.0.x, replaced with `hint_text` integration in `clients.py` and `settings.py`
3. **MDButtonText Text Property**: Fixed invalid `text=` parameter by setting text via `children[0].text` post-creation
4. **MDSegmentedButtonItem Text Property**: Same pattern applied for segmented button items
5. **Environment Verification**: Must run in `kivy_venv_new` virtual environment, not `.venv`

**Result**: GUI launches successfully with Material Design 3 theme, all screens functional

### VS Code Type Stub Solution (For Development)
**Problem**: KivyMD doesn't ship with type stub files (.pyi), causing Pylance import errors
**Solution**: Custom type stubs created in `stubs/kivymd/` with VS Code configuration:
```json
{
    "python.analysis.stubPath": "./stubs",
    "python.defaultInterpreterPath": "./kivy_venv_new/Scripts/python.exe"
}
```

### Application Structure
```
kivymd_gui/
├── main.py                    # Main application entry point
├── config.json               # Application configuration
├── tokens.json               # Material Design 3 design tokens (NEW)
├── themes/custom_theme.py     # Material Design 3 theme configuration
├── components/               # M3 adapter components (NEW)
│   ├── token_loader.py       # Token system infrastructure
│   ├── md3_button.py         # M3-compliant button adapter
│   ├── md3_card.py           # M3-compliant card adapter
│   └── md3_textfield.py      # M3-compliant text field adapter
├── qa/                       # Automated QA infrastructure (NEW)
│   ├── accessibility_checker.py # WCAG compliance validation
│   └── qa_runner.py          # Complete M3 compliance testing
├── screens/                   # Dashboard, clients, settings screens
└── utils/server_integration.py # Server bridge integration
```

## Material Design 3 Token-Driven Architecture (CRITICAL)

**✅ FULLY IMPLEMENTED** - Professional M3 compliance with automated QA validation

### Core M3 Implementation
```python
# Token-driven component creation (REQUIRED PATTERN)
from kivymd_gui.components import create_md3_button, create_md3_card, get_token_value

# ✅ CORRECT: Use M3 adapters that enforce design tokens
button = create_md3_button("Start Server", variant="filled", tone="primary")
card = create_md3_card(variant="elevated")

# ✅ CORRECT: Access design tokens programmatically  
primary_color = get_token_value('palette.primary')  # "#1976D2"
corner_radius = get_token_value('shape.corner_medium')  # 12dp
```

### Design Token System
- **tokens.json**: Canonical source of truth for ALL design decisions
- **Adapter Layer**: `MD3Button`, `MD3Card`, `MD3TextField` enforce token compliance
- **Automated QA**: WCAG accessibility, touch targets, spacing grid validation
- **Component Factories**: `create_md3_button()`, `create_md3_card()` for consistency

### M3 Compliance Validation
```bash
# Run automated M3 compliance checks
kivy_venv_new/Scripts/python.exe kivymd_gui/qa/test_qa_system.py

# Key validation areas:
# - Color contrast (WCAG AA: 4.5:1 minimum)
# - Touch targets (≥48dp minimum)  
# - Spacing grid (8dp baseline)
# - Motion duration (<300ms for micro-interactions)
# - Component adapter usage (no raw KivyMD widgets)
```

### Critical Implementation Rules
1. **Token-First**: ALL styling MUST come from `tokens.json` via adapters
2. **No Raw KivyMD**: Use `MD3Button` instead of `MDRaisedButton`, etc.
3. **QA Enforcement**: Run `qa_runner.py` before commits to verify compliance
4. **Accessibility Priority**: WCAG AA compliance is non-negotiable

### M3 Implementation Status (2025-08-21)
**COMPLETED ✅**: Full token-driven M3 architecture with automated QA validation
- **Design Tokens**: Centralized `tokens.json` with complete M3 specifications
- **Component Adapters**: `MD3Button`, `MD3Card`, `MD3TextField` with KivyMD 2.0.x compatibility  
- **QA System**: Automated accessibility, touch targets, spacing, motion validation (Score: 82.5/100 - FAIR)
- **Migration Path**: Factory functions and clear migration examples in `kivymd_gui/examples/`

```bash
# Test M3 implementation
kivy_venv_new/Scripts/python.exe kivymd_gui/examples/m3_migration_demo.py

# Run full QA validation
kivy_venv_new/Scripts/python.exe kivymd_gui/qa/test_qa_system.py
```

## Troubleshooting & Recovery

### KivyMD Common Errors & Solutions
```bash
# Error: "No module named 'kivymd.uix.topappbar'"
# Solution: Update import to kivymd.uix.appbar

# Error: "use_resizeable property doesn't exist"
# Solution: Remove use_resizeable parameter from MDNavigationRail

# Error: NavigationRail animation crashes
# Solution: Use stable commit d2f7740

# Emergency Recovery
.\kivy_venv_new\Scripts\activate
pip uninstall kivymd -y
pip install git+https://github.com/kivymd/KivyMD.git@d2f7740
```

### System Recovery
```bash
# System Won't Start - kill processes and restart
taskkill /f /im python.exe && taskkill /f /im EncryptedBackupClient.exe
del transfer.info && python scripts/one_click_build_and_run.py

# Port conflicts (Windows TIME_WAIT: wait 30-60s)
netstat -an | findstr ":9090\\|:1256"
```

### Race Condition Analysis
**✅ RESOLVED**: Global singleton race condition in API server  
**Solution**: CallbackMultiplexer routes progress to correct job handlers, eliminates race conditions

**FileReceiptProgressTracker**: Monitors `received_files/` for ground truth completion with watchdog library

### Documentation Files & Evidence
- **`TECHNICAL_DIAGRAMS.md`**: Architecture diagrams  
- **`UI_Enhancement_Documentation.md`**: UI enhancement documentation
- **`refactoring_report.md`**: Refactoring and technical debt analysis
- **`Shared/unified_monitor.py`**: Unified file monitoring system
- **Evidence of Success**: 72+ files in `received_files/` demonstrate production usage
- **Virtual Environment**: `.\kivy_venv_new\Scripts\activate` (KivyMD setup)
- .\kivy_venv_new\Scripts\Activate.ps1