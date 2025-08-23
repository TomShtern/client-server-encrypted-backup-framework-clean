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
python scripts/one_click_build_and_run.py  # Full build + deploy + launch (CANONICAL)
python scripts/launch_gui.py              # Quick start API server + browser

# Additional Launch Options
python scripts/launch_server_gui.py    # Launch KivyMD server GUI directly  
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

### Security Vulnerabilities (Active Issues)
- **Static IV**: Zero IV allows pattern analysis (HIGH PRIORITY)
- **No HMAC**: CRC32 provides no tampering protection (MEDIUM PRIORITY) 
- **Deterministic encryption**: Same plaintext produces same ciphertext

### Known Issues & Critical Notes
- **Success Verification**: File presence in `received_files/` is ONLY reliable indicator (exit codes unreliable)
- **Port Conflicts**: Ensure 9090/1256 are free (Windows TIME_WAIT: wait 30-60s)

### Critical Files for AI Development Context
```bash
# These files are essential for understanding system architecture (from Copilot instructions)
api_server/cyberbackup_api_server.py    # Flask API coordination hub
api_server/real_backup_executor.py      # Subprocess management patterns  
python_server/server/server.py          # Multi-threaded TCP server
Shared/utils/unified_config.py          # Configuration management
Shared/utils/file_lifecycle.py          # Race condition prevention
scripts/one_click_build_and_run.py      # CANONICAL launcher - primary entry point
```

## KivyMD Material Design 3 Server GUI (CRITICAL)

**✅ FULLY OPERATIONAL** - Modern Material Design 3 server administration interface

### Setup & Dependencies
```bash
# CRITICAL: Must use kivy_venv_new virtual environment
python -m venv kivy_venv_new                    # Create venv (if needed)
.\kivy_venv_new\Scripts\activate                # Activate venv

# Core dependencies (STABLE commit for reliability)
pip install git+https://github.com/kivymd/KivyMD.git@d2f7740  # MD3 support, no animation crashes
pip install psutil==7.0.0                       # System monitoring (REQUIRED)
pip install materialyoucolor==2.0.10            # Material Design 3 color system
pip install kivy==2.3.1                         # Specific Kivy version compatibility

# Alternative: Install all from requirements.txt
pip install -r requirements.txt

# Run KivyMD GUI
python kivymd_gui\main.py
```

### KivyMD 2.0.x API Reference (ESSENTIAL)

#### Key Version Information
- **KivyMD Version**: Commit `d2f7740` (stable, prevents animation crashes)
- **Kivy Version**: 2.3.1 (tested compatibility)
- **Material Design**: Version 3 specification compliance
- **Font System**: Supports Display, Headline, Title, Body, Label styles only

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

### Fixed Text & Unicode Components (CRITICAL)
```python
# ✅ CORRECT: Use MD3Label instead of MDLabel for proper text rendering
from kivymd_gui.components.md3_label import MD3Label, create_md3_label, create_hebrew_label, create_emoji_label

# Basic label with horizontal text rendering
label = MD3Label(text="Server Dashboard", font_style="Title")

# Unicode-optimized components
hebrew_label = create_hebrew_label("שלום עולם")  # Hebrew support
emoji_label = create_emoji_label("🎉 ✅ ❌")     # Emoji support  
mixed_label = create_md3_label("✅ Server | שרת 🎉")  # Auto font selection

# Valid KivyMD 2.0.x font styles ONLY:
# "Display", "Headline", "Title", "Body", "Label"
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

### Critical Fixes Applied (2025-08-21/22) 
**✅ FULLY RESOLVED**: All KivyMD 2.0.x compatibility issues fixed, GUI now fully functional

#### Text Rendering Fix (2025-08-22) - BREAKTHROUGH ACHIEVEMENT
**CRITICAL SUCCESS**: Fixed vertical character stacking issue in KivyMD text rendering after days of debugging
- **Root Cause**: KivyMD's default `text_size=(self.width, None)` was causing character-by-character vertical stacking
- **Solution**: Created `MD3Label` component with `text_size=(None, None)` and rendering protection:
  ```python
  # CRITICAL FIX in MD3Label
  if 'text_size' not in kwargs:
      self.text_size = (None, None)
      Clock.schedule_once(lambda dt: setattr(self, 'text_size', (None, None)), 0.1)
  ```
- **Font Styles Fixed**: Updated all invalid font styles to KivyMD 2.0.x compatible versions:
  - `H1` → `Display`, `H2/H3` → `Headline`, `H4/H5/H6` → `Title`
  - `Body1/Body2` → `Body`, `Caption` → `Label`
- **System-Wide**: Replaced 81 MDLabel instances across 7 screen files with MD3Label
- **Result**: Dashboard text now renders horizontally as intended
- **✅ MAJOR BREAKTHROUGH**: Solved days-long text rendering problem
- **Current Issue**: Text overlapping/stacking in same positions - layout spacing needs adjustment

#### Invalid Role Properties Fix (2025-08-22) - DASHBOARD CRITICAL
**CRITICAL DISCOVERY**: Dashboard vertical text rendering was caused by invalid `role` properties
- **Root Cause**: KivyMD does NOT support `role` properties (`role="small"`, `role="medium"`, `role="large"`)
- **Symptoms**: Invalid role properties cause KivyMD to render text character-by-character vertically instead of horizontally
- **Solution**: Removed ALL invalid `role` properties from dashboard labels in `kivymd_gui/screens/dashboard.py`
- **Key Insight**: Both MD3Label and MDLabel work correctly when role properties are not used
- **CRITICAL RULE**: Never use `role` properties on KivyMD labels - they are NOT valid and break text rendering
- **Files Fixed**: `kivymd_gui/screens/dashboard.py` - removed all `role="small"`, `role="medium"`, `role="large"`
- **Result**: Dashboard now displays text horizontally with proper formatting, no vertical character stacking

#### Unicode & Hebrew/Emoji Support (2025-08-22)
**CRITICAL**: Implemented comprehensive Unicode support for Hebrew text and emoji rendering
- **Font System**: Created `FontConfiguration` class with automatic Windows font detection
- **Registered Fonts**: SegoeUI (Hebrew), SegoeUIEmoji (emoji), Arial (fallback)  
- **Smart Selection**: Automatic font selection based on text content (Hebrew U+0590-U+05FF detection)
- **Components**: Enhanced `MD3Label` with `create_hebrew_label()`, `create_emoji_label()`, `create_unicode_label()`
- **UTF-8 Integration**: Leveraged existing `Shared.utils.utf8_solution` for full Unicode pipeline
- **Test Coverage**: Hebrew text "שלום עולם" and emojis "🎉 ✅ ❌" render as actual characters
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
3. **Text Rendering**: ALWAYS use `MD3Label` instead of `MDLabel` to prevent vertical stacking
4. **Font Styles**: Only use KivyMD 2.0.x compatible styles (Display, Headline, Title, Body, Label)
5. **No Role Properties**: NEVER use `role="small/medium/large"` - they break text rendering
6. **QA Enforcement**: Run `qa_runner.py` before commits to verify compliance
7. **Accessibility Priority**: WCAG AA compliance is non-negotiable

### KivyMD 2.0.x Material Design 3 Best Practices
```python
# ✅ CORRECT: Material Design 3 Component Creation
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText

# ✅ CORRECT: Text Rendering (use MD3Label)
from kivymd_gui.components.md3_label import MD3Label
label = MD3Label(text="Dashboard Status", font_style="Title")  # No role property!

# ✅ CORRECT: Theme Setup for Material Design 3
self.theme_cls.material_style = "M3"
self.theme_cls.theme_style = "Dark"  # or "Light"  
self.theme_cls.primary_palette = "Blue"

# ❌ WRONG: Using raw MDLabel or role properties
from kivymd.uix.label import MDLabel  # Don't use directly
MDLabel(text="Text", role="small")    # Breaks text rendering!
```

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

# CRITICAL Error: Text rendering vertically (character-by-character)
# Root Cause: Invalid role properties (role="small", role="medium", role="large")
# Solution: Remove ALL role properties from KivyMD labels - they are NOT supported
# KivyMD does NOT support role properties and they break text rendering
# Both MD3Label and MDLabel work correctly WITHOUT role properties

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