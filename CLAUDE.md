# Client-Server Encrypted Backup Framework - Development Guide

**Last Updated**: January 11, 2025

## Project Overview

The Client-Server Encrypted Backup Framework (CyberBackup 3.0) is a comprehensive encrypted file backup system with dual-GUI architecture and robust security. The project features:

- **Security Layer**: RSA-1024 for key exchange and AES-256-CBC for file encryption
- **Backend**: Python BackupServer with SQLite database and network listener (port 1256)
- **Desktop GUI**: FletV2 native application with Material Design 3 for administrators
- **Web GUI**: JavaScript interface via API Server (port 9090) for end-user backups
- **Protocol**: Custom binary protocol with CRC32 verification for data integrity
- **Architecture**: Dual-GUI system with integrated server and shared database
- **Search**: Global search functionality with breadcrumb navigation for efficient data discovery

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
│   ├── main.py                # Application entry point (~1000 lines, NavigationRail architecture)
│   ├── start_with_server.py   # Launcher with integrated BackupServer
│   ├── views/                 # Feature views (dashboard, clients, files, analytics, logs, settings)
│   ├── utils/                 # ~6000 lines across 19 modules (ServerBridge, formatters, UI components)
│   ├── components/            # Reusable UI components (global_search, breadcrumb, context_menu, filter_controls)
│   ├── theme.py               # Enhanced Material Design 3 theme with Windows 11 integration
│   ├── archive/               # Archived experimental/deprecated code (excluded from analysis)
│   │   ├── phase0/            # Legacy components and tests
│   │   ├── deprecated_views/  # Old experimental views
│   │   └── redundant_utilities/ # Consolidated utility modules
│   ├── docs/                  # Comprehensive technical documentation
│   ├── important_docs/        # Development plans and completion summaries
│   ├── consolidation_plan_2025/ # Consolidation strategy and reports
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

### Components: `FletV2/components/`
- `global_search.py`: Global search with keyboard shortcuts (Ctrl+K) and indexed data discovery
- `breadcrumb.py`: Navigation breadcrumb trail for contextual awareness
- `context_menu.py`: Right-click context menus for all views
- `filter_controls.py`: Advanced filtering UI components
- `enhanced_data_table.py`: High-performance data tables with sorting/filtering (archived)
- `log_card.py`: Log entry display component

### Utilities: `FletV2/utils/`
- `formatters.py`: Data formatting utilities (as_float, as_int, format_timestamp) - 246 lines
- `ui_components.py`: Reusable UI components and builders - consolidated ~1000 lines
- `async_helpers.py`: Async/await patterns and concurrent operations
- `global_shortcuts.py`: Desktop keyboard shortcuts (Ctrl+K search, navigation) - 525 lines
- `keyboard_handlers.py`: Advanced keyboard event handling - 538 lines
- `user_feedback.py`: Snackbar and dialog helpers - 181 lines
- `display_scaling.py`: Windows 11 DPI awareness and scaling - 462 lines
- `windows_integration.py`: Native Windows features integration - 486 lines
- `dashboard_loading_manager.py`: Performance-optimized dashboard loading
- `loading_states.py`: Loading state management and indicators
- `task_manager.py`: Background task execution and management
- `data_export.py`: CSV/JSON export functionality
- And 7 more specialized modules

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
- **`FletV2/consolidation_plan_2025/`**: Major consolidation strategy and completion reports

### Quick FletV2 Reference
- **Framework**: Flet 0.28.3 with Material Design 3
- **Pattern**: View-based architecture with `create_*_view()` functions
- **Theme**: Enhanced theme system with Windows 11 integration (theme.py)
- **Principle**: Use Flet built-ins over custom solutions (Flet Simplicity Principle)

### Keyboard Shortcuts
The application supports comprehensive keyboard navigation:
- **Ctrl+K**: Open global search (search across clients, files, logs, analytics)
- **Ctrl+F**: Quick filter in current view
- **Ctrl+R**: Refresh current view
- **Ctrl+E**: Export current data
- **Arrow Keys**: Navigate through lists and tables
- **Enter**: Activate selected item
- **Escape**: Close dialogs or cancel operations

### Global Search
The global search feature (activated with Ctrl+K) provides:
- **Indexed Search**: Fast searching across all data types
- **Real-time Results**: Results update as you type
- **Contextual Navigation**: Click results to navigate to specific views
- **Breadcrumb Integration**: Track your navigation path
- **Performance**: Optimized with debounced input and indexed data structures

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
8. **Code Organization**:
   - Keep experimental code in `archive/` folders
   - Document major changes in `important_docs/`
   - Use consolidation plans for large refactorings
9. **Performance**:
   - Profile before optimizing
   - Use ListView for large datasets
   - Implement lazy loading where appropriate
10. **Keyboard Navigation**: Support Ctrl+K for global search, standard shortcuts for common actions

## Troubleshooting

### Common Issues

1. **Network Listener Not Starting**: Ensure `server_instance.start()` is called in startup scripts
2. **Database Locking**: Concurrent access is handled through file-level locking
3. **UTF-8 Issues**: The system includes UTF-8 bootstrap for Windows compatibility
4. **Import Errors**: Always use `flet_venv` virtual environment located at workspace root
5. **Performance Issues**:
   - Check if archive folders are being indexed by VS Code (should be excluded)
   - Verify global search is using indexed data, not full scans
   - Ensure ListView is used for large datasets
6. **Global Search Not Working**: Press Ctrl+K to activate, ensure focus is on the main window

### Debugging

- Server logs are available in `server.log` and the enhanced logging system
- FletV2 includes verbose diagnostic options via environment variables
- Network protocol issues can be debugged through the binary protocol implementation
- Performance profiling tools available in `FletV2/tests/desktop_performance.py`
- Use breadcrumb component to track navigation state

### Environment Variables

For FletV2 integration:
```bash
# Windows PowerShell
$env:CYBERBACKUP_DISABLE_INTEGRATED_GUI = "1"
$env:CYBERBACKUP_DISABLE_GUI = "1"
$env:FLET_V2_DEBUG = "true"
```

### VS Code Configuration

The project is configured to exclude archive folders from analysis:
```json
"python.analysis.ignore": ["**/archive/**", "FletV2/archive/**", "**/_legacy/**"]
```
This improves IDE performance and reduces noise from deprecated code.

## Archive Organization

The `FletV2/archive/` folder contains deprecated and experimental code for reference:

### `archive/phase0/`
Legacy code from Phase 0 development:
- `components/`: Experimental data tables and filter controls
- `tests/`: Old test suites (async patterns, business logic, integration)
- `views/`: Stub implementations and experimental views

### `archive/deprecated_views/`
Old view implementations replaced by current production code:
- `dashboard_exp.py`: Experimental dashboard (replaced by current dashboard.py)
- `database_pro_exp.py`: Old database view (replaced by optimized ListView version)
- `enhanced_logs_exp.py`: Experimental log viewer

### `archive/redundant_utilities/`
Consolidated utility modules:
- `dialog_builder_legacy_multi_dialogs.py`: Old multi-dialog system
- `performance_deprecated_async_utils.py`: Deprecated async patterns
- `placeholder_mode_indicator_mock_ui.py`: Mock UI components
- `real_server_client_http_client_stub.py`: HTTP client stub
- `server_mediated_operations_state_wrappers.py`: Old state wrappers
- `task_manager_background_executor.py`: Old task execution system
- `tri_style_components_experimental_styling.py`: Old tri-style theme system
- `ui_helpers_badges_formatters_legacy.py`: Legacy formatting helpers
- `atomic_state.py`, `simple_state.py`, `memory_manager.py`: State management experiments
- `theme_original_backup.py`: Original 978-line theme before simplification

### `archive/obsolete_launchers/`
Old startup scripts:
- `count_lines.py`, `emergency_gui.py`, `launch_modularized.py`
- Performance benchmarking and validation scripts

### `archive/enhanced_data_table_unused/`
High-performance data table component (770 lines) - archived as ListView proved more efficient for the use case

### Why Archive Instead of Delete?
- **Historical Reference**: Understanding past architectural decisions
- **Code Reuse**: Potentially useful patterns for future features
- **Documentation**: Shows evolution of the codebase
- **Reversal**: Easy to restore if needed

**Important**: Archive folders are excluded from VS Code analysis, git diffs should generally avoid them, and they should not be imported in production code.

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

## Recent Updates

### January 11, 2025 - Global Search Feature
- **Global Search**: Added comprehensive global search with Ctrl+K shortcut
  - Searches across clients, files, logs, and analytics
  - Real-time indexed search with performance optimizations
  - Integrated breadcrumb navigation for context awareness
- **Performance**: Removed experimental components causing lag (~1100 lines of unused code)
- **Import Refactoring**: Cleaned up import statements across all views
- **Code Cleanup**: Removed `global_search_simple.py` and `global_search_minimal.py` experiments

### January 10, 2025 - Performance and Navigation
- **Breadcrumb Component**: Enhanced navigation with contextual breadcrumb trail
- **Global Search v2**: Improved search performance and UI responsiveness
- **View Enhancements**: Updated analytics, database, and logs views with better navigation
- **Documentation**: Added performance analysis and fix summaries

### January 9, 2025 - Analytics Enhancement
- **Analytics View**: Major enhancement with 650+ line expansion
  - Advanced data visualization and trending analysis
  - Client activity patterns and backup success metrics
  - Storage utilization insights
- **Database View**: Performance improvements with ListView optimization
- **Archive Organization**: Moved deprecated components to structured archive folders
  - Phase 0 legacy tests and components
  - Experimental async patterns
  - State manager code (eliminated in favor of simple state)

### January 7-8, 2025 - Major Consolidation
- **Code Reduction**: Removed ~8000 lines of deprecated/redundant code
- **Archive Structure**: Organized archive into clear categories:
  - `archive/phase0/`: Legacy components and experimental code
  - `archive/deprecated_views/`: Old view implementations
  - `archive/redundant_utilities/`: Consolidated utility modules
  - `archive/obsolete_launchers/`: Old startup scripts
- **Theme Simplification**: Reduced theme.py from 978 to streamlined implementation
  - Eliminated tri-style system complexity
  - Enhanced Material Design 3 integration
  - Windows 11 native theming support
- **Utility Consolidation**:
  - Added `formatters.py` (246 lines) for safe type conversion
  - Added `display_scaling.py` (462 lines) for DPI awareness
  - Added `windows_integration.py` (486 lines) for native features
  - Added `keyboard_handlers.py` (538 lines) for advanced input
  - Consolidated `ui_components.py` from multiple scattered implementations
- **State Management**: Eliminated StateManager in favor of simple atomic state
  - Added `atomic_state.py`, `simple_state.py`, `memory_manager.py`
  - Removed 1036-line state_manager.py complexity
- **VS Code Integration**: Updated settings.json to exclude archive folders from analysis

### January 4-6, 2025 - Foundation Work
- **Database View**: Refactored to use ListView for optimal performance
- **Theme System**: Complete overhaul with Windows 11 integration
- **Documentation**: Comprehensive docs/ folder with ARCHITECTURE.md, GETTING_STARTED.md, DEVELOPMENT_WORKFLOWS.md
- **Flet 0.28.3**: Updated to latest Flet version with Material Design 3
- **Testing Infrastructure**: Added accessibility, performance, and workflow tests

### Key Metrics
- **Lines Removed**: ~8000+ lines of legacy/experimental code
- **Lines Added**: ~6000+ lines of production-ready features and documentation
- **Archive Items**: 20+ deprecated files and modules moved to archive
- **Active Utilities**: 19 focused utility modules (down from scattered implementations)
- **Performance**: Global search and navigation significantly improved
