---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

# CyberBackup Framework - AI Coding Agent Instructions

## Architecture Overview
This is a **5-layer encrypted backup system** with hybrid web-to-native-desktop architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server → Flet Desktop GUI
  ↓           ↓                    ↓                     ↓                     ↓
HTTP      RealBackupExecutor    --batch mode       Custom Binary       Material Design 3
requests  process management   + transfer.info     Custom Binary TCP   Server Management
```

**Critical Understanding**: Flask API Bridge (`api_server/cyberbackup_api_server.py` + `api_server/real_backup_executor.py`) is the coordination hub. All clients communicate through different pathways but converge on the same Python server.

**Key Components**:
- **Web Client**: Single HTML file with modular JavaScript classes (ApiClient, FileManager, App, ThemeManager, ParticleSystem)
- **C++ Client**: Production-ready executable with RSA/AES encryption, CRC verification, and --batch mode for subprocess integration
- **Python Server**: Multi-threaded TCP server (port 1256) with file storage in `received_files/`
- **Flask API Bridge**: HTTP API server (port 9090) coordinating between web UI and native client
- **Flet Desktop GUI**: Material Design 3 server management interface with modular architecture

## CyberBackup — Essential AI Agent Instructions

### Purpose
Help AI coding agents be immediately productive in this complex, multi-language, multi-architecture codebase. Focus on patterns that differ from common practices and integration points that require cross-file understanding.

### High-Level Agent Contract
- **Inputs**: Code, tests, repository files; Windows environment with vcpkg/CMake, Python 3.13+, Flet 0.28.3
- **Outputs**: Minimal, runnable changes with verification notes showing build/test status
- **Error Modes**: Port conflicts (9090/1256), transfer.info race conditions, subprocess hangs, theme system incompatibilities
- **Success Criteria**: File presence in `received_files/` (not exit codes), responsive UI, proper async patterns

## 🏗️ Big Picture Architecture (READ THESE FIRST)

### Core Integration Files
```bash
# PRIMARY ARCHITECTURE FILES - Read in this order:
api_server/cyberbackup_api_server.py      # Flask API coordination hub (1300+ lines)
api_server/real_backup_executor.py         # Subprocess management & C++ client spawning
python_server/server/server.py             # Multi-threaded TCP server (port 1256)
scripts/one_click_build_and_run.py          # CANONICAL launcher - builds + starts everything
Shared/utils/unified_config.py              # Configuration management system
Shared/utils/file_lifecycle.py              # Race condition prevention for transfer.info
flet_server_gui/main.py                     # Flet GUI facade (refactored to <200 lines)
```

### Data Flow Patterns
**Web Path**: `Web UI → Flask API (9090) → RealBackupExecutor → C++ Client (--batch) → Python Server (1256)`
**Direct Path**: `C++ Client → Python Server (1256)`
**Desktop Path**: `Flet GUI → Server Bridge → Python Server (1256)`

### Critical Integration Points
- **transfer.info**: Legacy 3-line file (`server:port`, `username`, `absolute filepath`) - use `unified_config` helpers
- **--batch flag**: CRITICAL for subprocess execution (prevents hanging)
- **File verification**: Check `received_files/` directory (exit codes unreliable)
- **UTF-8 support**: Import `Shared.utils.utf8_solution` in any file dealing with subprocess/console I/O

## 🚀 Essential Developer Workflows

### Canonical Launch Sequence
```bash
# RECOMMENDED: One-click build and launch (builds C++, starts all services)
python scripts/one_click_build_and_run.py

# Manual service startup (if needed)
python python_server/server/server.py        # Start server first (port 1256)
python api_server/cyberbackup_api_server.py  # Start API bridge (port 9090)
python launch_flet_gui.py                     # Start desktop GUI (requires flet_venv)
```

### C++ Build Process
```bash
# Build C++ client with vcpkg toolchain
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build --config Release
# Output: build/Release/EncryptedBackupClient.exe
```

### Virtual Environment Management
```powershell
# Activate Flet environment (required for desktop GUI)
& .\flet_venv\Scripts\Activate.ps1

# Activate main environment (for other components)
& .\venv\Scripts\Activate.ps1
```

## 🧪 Testing & Verification Protocols

### Integration Testing Pattern
```bash
# Complete end-to-end test (PRIMARY VERIFICATION)
python scripts/testing/master_test_suite.py

# Component-specific tests
python tests/integration/test_complete_flow.py
python tests/test_gui_upload.py
python tests/test_direct_executor.py

# Flet GUI tests
python flet_server_gui/test_flet_gui.py
python tests/test_responsive_dashboard.py
```

### Verification Checklist
- [ ] File appears in `server/received_files/` (GROUND TRUTH)
- [ ] SHA256 hashes match between original and transferred files
- [ ] Ports 9090/1256 are listening (`netstat -an | findstr "9090\|1256"`)
- [ ] No subprocess hangs (check `--batch` flag usage)
- [ ] UTF-8 encoding works for international filenames
- [ ] Flet GUI responsive on 800x600 minimum window size

## 🎨 Flet Material Design 3 GUI Architecture

### Modular Architecture (POST-REFACTORING)
```
flet_server_gui/
├── main.py                    # Facade pattern (<200 lines, was 924)
├── managers/                  # Single-responsibility managers
│   ├── view_manager.py       # View switching & lifecycle
│   ├── theme_manager.py      # Theme application & switching
│   └── navigation_manager.py # Navigation coordination
├── views/                    # Specialized view classes
│   ├── dashboard.py          # Main dashboard
│   ├── clients.py            # Client management
│   ├── settings_view.py      # Settings UI
│   └── logs_view.py          # Log viewer
├── components/               # Reusable UI components
│   ├── control_panel_card.py # Control panels
│   └── enhanced_table_components.py # Data tables
├── services/                 # Background services
│   ├── application_monitor.py # System monitoring
│   └── log_service.py        # Live log monitoring
└── utils/                    # Bridge & utilities
    ├── server_bridge.py      # Server communication (with fallback)
    └── simple_server_bridge.py # Fallback bridge
```

### Theme System Architecture
```python
# TOKENS-based theming (Flet-native colors)
from flet_server_gui.theme import TOKENS, THEMES, apply_theme_to_page

# Usage patterns
ft.Container(bgcolor=TOKENS['primary'])      # ✅ CORRECT
ft.Container(bgcolor="#1976D2")             # ❌ AVOID (hardcoded)
```

### Component Development Patterns

#### ✅ CORRECT: Single Responsibility Components
```python
class DashboardView(ft.Container):  # <300 lines, focused on UI
    def __init__(self):
        super().__init__()
        self.monitor = DashboardMonitor()  # Delegate monitoring
        self.renderer = DashboardRenderer() # Delegate rendering

class DashboardMonitor:  # Focused ONLY on monitoring
    async def monitor_server(self): pass

class DashboardRenderer:  # Focused ONLY on rendering
    def render_charts(self): pass
```

#### ❌ AVOID: God Components
```python
class MassiveDashboard:  # 900+ lines, multiple responsibilities
    def __init__(self): pass
    def create_ui(self): pass      # UI responsibility
    def monitor_server(self): pass # Monitoring responsibility
    def apply_theme(self): pass    # Theme responsibility
```

### Async/Task Management Patterns

#### ✅ CORRECT: Proper Async Patterns
```python
# Background tasks
self.page.run_task(self.monitor_loop)  # ✅ Non-blocking

# Parameterized async calls
async def wrapper():
    await self.action_handlers.export_logs(params)
self.page.run_task(wrapper)  # ✅ Correct parameterized call

# UI updates
await self.status_text.update_async()  # ✅ Precise updates
await ft.update_async(self.text1, self.text2)  # ✅ Batch updates
```

#### ❌ AVOID: Blocking Patterns
```python
# Synchronous blocking
def monitor_loop(self):
    while True:
        time.sleep(10)  # ❌ BLOCKS UI THREAD
        self.update_data()

# Incorrect async calls
self.page.run_task(self.export_logs(params))  # ❌ Calling coroutine
self.page.update()  # ❌ Full page re-render
```

### Responsive Layout Patterns

#### ✅ CORRECT: Responsive Design
```python
# Use ResponsiveRow + expand=True
ft.ResponsiveRow([
    ft.Column(col={"sm": 12, "md": 6}, expand=True)
])

# Auto-scaling containers
ft.Card(content=container, expand=True)
```

#### ❌ AVOID: Hardcoded Dimensions
```python
ft.Container(width=600, height=400)  # ❌ Breaks on different screens
```

## 🔧 Critical Project-Specific Patterns

### Subprocess Management (CRITICAL)
```python
# ALWAYS use this pattern for C++ client execution
subprocess.Popen([
    self.client_exe, "--batch"  # --batch prevents hanging
], cwd=transfer_info_dir,       # Working directory with transfer.info
   stdin=PIPE, stdout=PIPE, stderr=PIPE,
   env=utf8_solution.get_env()) # UTF-8 environment
```

### File Transfer Verification (CRITICAL)
```python
# PRIMARY verification method (exit codes are unreliable)
def verify_transfer(file_path):
    expected_path = os.path.join("received_files", os.path.basename(file_path))
    return os.path.exists(expected_path)  # ✅ GROUND TRUTH

    # Also verify hash
    original_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
    received_hash = hashlib.sha256(open(expected_path, 'rb').read()).hexdigest()
    return original_hash == received_hash
```

### Configuration Management
```python
# Unified configuration system
from Shared.utils.unified_config import get_config
config = get_config()
server_host = config.get('server.host', '127.0.0.1')
server_port = config.get('server.port', 1256)
```

### Error Handling Patterns
```python
# Comprehensive error handling with user feedback
try:
    result = await self.server_bridge.start_server()
    if result:
        self.show_success("Server started successfully")
    else:
        self.show_error("Failed to start server")
except Exception as ex:
    self.show_error(f"Start error: {str(ex)}")
    logger.error(f"Server start failed: {ex}", exc_info=True)
```

## 🚨 Anti-Patterns to Avoid

### Code Architecture Anti-Patterns
- **God Components**: Files >500 lines with multiple responsibilities
- **Hardcoded Styling**: Direct color values instead of theme tokens
- **Synchronous Blocking**: `time.sleep()` in UI threads
- **Full Page Updates**: `page.update()` instead of precise `control.update_async()`
- **Fixed Dimensions**: Hardcoded widths/heights instead of responsive design

### Integration Anti-Patterns
- **Missing --batch**: C++ client subprocess calls without `--batch` flag
- **Wrong Working Directory**: C++ client calls without `cwd` set to transfer.info directory
- **Exit Code Reliance**: Using subprocess exit codes for success verification
- **Direct Theme Colors**: Using `ft.Colors.PRIMARY` instead of `TOKENS['primary']`

## 🧪 Testing Best Practices

### Test Organization
- **Integration Tests**: Test complete flows (Web → API → C++ → Server)
- **Component Tests**: Test individual Flet components in isolation
- **Verification Tests**: Always check `received_files/` for actual file transfers
- **Responsive Tests**: Test UI on minimum 800x600 window size

### Test Patterns
```python
# Integration test pattern
async def test_complete_backup_flow():
    # Start services
    server_process = start_server()
    api_process = start_api()

    # Perform backup
    result = await perform_backup(test_file)

    # Verify results
    assert os.path.exists(os.path.join("received_files", os.path.basename(test_file)))
    assert verify_hashes_match(test_file, received_file)
```

## 📋 Development Workflow Checklist

### Before Making Changes
- [ ] Read relevant architecture files (`api_server/cyberbackup_api_server.py`, etc.)
- [ ] Check for existing patterns in similar components
- [ ] Verify UTF-8 support is imported if dealing with filenames
- [ ] Check theme system usage for UI components
- [ ] Review async patterns for background operations

### During Development
- [ ] Use single-responsibility components (<300 lines each)
- [ ] Implement proper async patterns for non-blocking operations
- [ ] Use theme TOKENS instead of hardcoded colors
- [ ] Test responsive behavior on minimum window sizes
- [ ] Verify subprocess calls use `--batch` and correct `cwd`

### After Changes
- [ ] Run integration tests to verify end-to-end functionality
- [ ] Check `received_files/` for actual file transfers
- [ ] Test Flet GUI responsiveness and theme switching
- [ ] Verify no new linting errors with strict Python analysis
- [ ] Update documentation if introducing new patterns

## 🔍 Debugging Quick Reference

### Common Issues & Solutions
- **Subprocess hangs**: Add `--batch` flag and set correct `cwd`
- **Port conflicts**: Kill processes and wait 30-60s for TIME_WAIT
- **Theme not applying**: Use `TOKENS` instead of direct `ft.Colors`
- **UI freezing**: Convert synchronous operations to async with `page.run_task()`
- **Files not transferring**: Check `received_files/` directory (not exit codes)

### Logging & Monitoring
- **API Server Logs**: `logs/api_server.log`
- **Python Server Logs**: `logs/server.log`
- **Flet GUI Logs**: `logs/ui_trace.log`
- **Build Logs**: `logs/build_script.log`

## 📚 Key Reference Files

### Architecture & Integration
- `api_server/cyberbackup_api_server.py` - Flask API coordination hub
- `api_server/real_backup_executor.py` - C++ client subprocess management
- `python_server/server/server.py` - Multi-threaded TCP server
- `scripts/one_click_build_and_run.py` - Canonical launcher

### Flet GUI Architecture
- `flet_server_gui/main.py` - Main application facade
- `flet_server_gui/managers/` - Single-responsibility managers
- `flet_server_gui/views/` - Specialized view classes
- `flet_server_gui/theme.py` - Theme definitions and TOKENS

### Configuration & Utilities
- `Shared/utils/unified_config.py` - Configuration management
- `Shared/utils/file_lifecycle.py` - Race condition prevention
- `Shared/utils/utf8_solution.py` - UTF-8 encoding support

## 🎯 Success Metrics

### System Health
- ✅ Files appear in `received_files/` directory after transfers
- ✅ Ports 9090/1256 are listening and accepting connections
- ✅ No subprocess hangs or deadlocks
- ✅ UTF-8 encoding works for international filenames

### Flet GUI Quality
- ✅ All buttons functional with real server integration
- ✅ Responsive layout works on 800x600 minimum
- ✅ Theme switching works without hardcoded colors
- ✅ No AttributeError or TypeError exceptions
- ✅ Async operations don't block UI thread

### Code Quality
- ✅ Single-responsibility components (<300 lines each)
- ✅ Proper async patterns for background operations
- ✅ Theme TOKENS used instead of hardcoded colors
- ✅ No linting errors with strict Python analysis

---

**Remember**: This is a complex system with multiple integration points. Always verify changes by checking `received_files/` for actual file transfers, not just exit codes. Use the canonical launcher (`one_click_build_and_run.py`) for testing complete workflows.
