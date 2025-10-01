
# Client-Server Encrypted Backup Framework - Claude Instructions

IMPORTANT: For extremely important AI guidance, rules, and data please consult the `#file:AI-Context` folder. Additional important documentation and design reference materials are in the `#file:important_docs` folder. Use `AI-Context` first for critical decisions.

## Project Overview

This is a comprehensive encrypted file backup system that implements a robust client-server architecture with strong security measures. The project features:

- **Security Layer**: RSA-1024 for key exchange and AES-256-CBC for file encryption
- **Backend**: Python server with SQLite database for storage and management
- **Frontend**: Modern Flet-based GUI with Material Design 3, Neumorphism, and Glassmorphism styling
- **Protocol**: Custom binary protocol with CRC32 verification for data integrity
- **Architecture**: Client-server model with cross-platform compatibility

## Project Structure & Components

### Core Architecture
- **python_server/**: Python-based server implementation with SQLite database
- **FletV2/**: Modern desktop GUI built with Flet framework
- **Shared/**: Common utilities, logging, and configuration modules
- **Client/**: C++ client application (binary protocol implementation)

### FletV2 GUI Architecture
- **main.py**: Application entry point with sophisticated state management
- **views/**: Modular view components (dashboard, clients, files, database, analytics, etc.)
- **theme.py**: Advanced tri-style design system (Material 3, Neumorphism, Glassmorphism)
- **utils/**: Server bridge, state management, and utility functions
- **config.py**: Configuration and constants for the GUI application

### Server Architecture
- **server.py**: Main backup server with client management and encryption
- **database.py**: SQLite integration with client/file tracking
- **protocol.py**: Custom binary protocol implementation
- **network_server.py**: Network communication layer

## Key Features & Capabilities

### Security Features
- RSA-1024 key exchange for secure session establishment
- AES-256-CBC encryption for file data protection
- CRC32 verification for data integrity
- Secure key management with automatic generation and storage

### GUI Features
- **Dashboard**: Real-time metrics with interactive cards and performance gauges
- **Client Management**: View and manage registered backup clients
- **File Management**: Browse, search, and manage backed up files
- **Database Management**: Direct database access and record management
- **Settings Management**: Comprehensive configuration with server integration
- **Advanced Styling**: Material Design 3 with neumorphic and glassmorphic effects
- **Responsive Design**: Adaptive layout for different screen sizes

### Server Features
- Multi-client support with concurrent connections
- Automated session timeout and cleanup
- Database integrity checks and maintenance
- Comprehensive logging with dual output (console + file)
- Performance monitoring and metrics collection

## FletV2 GUI Architecture Details

### 🚨 CRITICAL: Server Integration Architecture (October 1, 2025)

**The BackupServer does NOT have an API.** All communication is via **direct Python method calls**:

1. **Server-Launched Mode** ([start_with_server.py](FletV2/start_with_server.py)):
   - BackupServer creates instance of itself
   - Passes `self` as Python object to FletV2App
   - GUI calls server methods directly: `server.get_clients()`, `server.add_file()`, etc.
   - **Zero network overhead** - in-memory Python calls only

2. **Standalone GUI Mode** ([start_gui_only.py](FletV2/start_gui_only.py)):
   - GUI launches without server instance (`FLET_GUI_ONLY_MODE=1`)
   - All views show empty states (no data)
   - Used for GUI development and testing only

3. **ServerBridge Pattern** ([server_bridge.py](FletV2/utils/server_bridge.py)):
   - **NOT an API client** - it's a thin delegation wrapper
   - Direct method delegation: `bridge.get_clients()` → `server.get_clients()`
   - Data format conversion (BackupServer ↔ FletV2 formats)
   - Structured error handling with `{'success': bool, 'data': Any, 'error': str}`
   - **NO HTTP, NO REST, NO API CALLS** - pure Python method delegation

### ServerBridge Integration
The ServerBridge acts as the primary interface between the GUI and the backend server. Key components include:

- **Direct Method Delegation**: Calls real server methods directly (not API endpoints)
- **Data Conversion**: Converts between BackupServer and FletV2 data formats (BLOB UUIDs ↔ strings)
- **Error Handling**: Provides structured responses for server operations
- **Async Support**: Implements both synchronous and asynchronous operations via executors

### State Management System
The enhanced StateManager provides reactive state management with:

- **State Synchronization**: Keeps UI components synchronized with server data
- **Async Updates**: Supports server-mediated state updates
- **Loading States**: Tracks operation loading states
- **Progress Tracking**: Monitors operation progress
- **Error States**: Manages and displays error states
- **Event Broadcasting**: Sends events across different parts of the application
- **Retry Mechanism**: Handles operation retries with exponential backoff

### UI Components Framework
The GUI uses a streamlined component system with:

- **Framework-Harmonious Components**: Uses Flet's built-in components rather than complex custom implementations
- **Themed Components**: Consistent styling using the advanced theme system
- **Smart Data Display**: DataTables and data visualization components
- **Responsive Layouts**: Uses Flet's ResponsiveRow for adaptive layouts
- **Status Indicators**: Various status pill and indicator types for different states
- **Action Buttons**: Consistent styling for primary and secondary actions

### View Architecture
Each view follows a consistent pattern:

- **Create Function**: Returns the view container, dispose function, and setup function
- **Server Integration**: Uses server_bridge for data operations
- **State Management**: Integrates with StateManager for reactive updates
- **Resource Cleanup**: Includes proper disposal of resources and subscriptions

### Theme and Styling System
The advanced theme system implements a tri-style design:

- **Material Design 3**: Core design language with semantic colors
- **Neumorphism**: Soft shadows and depth effects (40-45% intensity)
- **Glassmorphism**: Translucent elements with blur effects (20-30% intensity)
- **Pre-computed Constants**: Performance-optimized shadow and styling constants
- **Animation Support**: GPU-accelerated animations for smooth interactions

## Detailed View Components

### Dashboard View
The main dashboard view features:

- **Metric Cards**: Interactive cards with real-time data and navigation support
- **Performance Gauges**: Circular progress indicators with status displays
- **Activity Stream**: Timeline-based activity display with status indicators
- **Status Monitoring**: Dual status indicators for GUI and server connection
- **Theme Controls**: Integrated theme switching with multiple options

### Clients View
The clients management view provides:

- **Data Table**: Display of client information with sorting and filtering
- **CRUD Operations**: Full Create, Read, Update, Delete functionality
- **Status Indicators**: Visual status representation for connection states
- **Search and Filter**: Client filtering by name, ID, and status
- **Context Menus**: Action menus for each client record

### Database View
The database management view includes:

- **Table Browser**: Dynamic table browsing with schema detection
- **Record Management**: Full CRUD operations on database records
- **Export Functionality**: JSON export of table data
- **Status Indicators**: Visual representation of database status
- **Search and Filter**: Record filtering and search capabilities

### Settings View
The settings management view provides:

- **Tabbed Interface**: Organized settings into logical groups (Server, Interface, Monitoring, Logging, Security, Backup)
- **Validation**: Client-side validation for settings values
- **Import/Export**: Settings import/export functionality
- **Reset Functionality**: Reset to default settings
- **Server Integration**: Save/load settings from the server

## Development Conventions

### Code Style
- Follow Python PEP 8 standards with Ruff linting
- Use type hints for all function signatures
- Maintain comprehensive docstrings for all modules and classes
- Implement structured logging with context information

### Architecture Patterns
- **ServerBridge Pattern**: Interface between GUI and backend server
- **State Management**: Reactive UI updates via dedicated state manager
- **Modular Design**: Separate view components with consistent API patterns
- **Async Integration**: Proper handling of synchronous and asynchronous operations
- **Framework Harmony**: Use Flet's built-in components rather than complex custom implementations

### Error Handling
- Implement comprehensive exception handling with graceful degradation
- Use structured logging for debugging and monitoring
- Provide user-friendly error messages in GUI
- Include automated crash reporting and diagnostics

## Building and Running

### Prerequisites
- Python 3.8+ with standard development tools
- Visual Studio Build Tools for C++ client compilation
- Git for version control
- SQLite for database storage

### Setup Commands
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up Flet virtual environment (if needed)
python -m venv flet_venv
flet_venv\Scripts\activate
pip install -r requirements.txt

# Build C++ client (Windows)
.\build.bat

# Run the server
python -m python_server.server.server

# Run the GUI
python -m FletV2.main
```

### Launcher Modes

**Server-Launched Mode (Integrated)** - `python FletV2/start_with_server.py`:
```python
# Creates BackupServer instance
server_instance = BackupServer()
# Passes server as Python object to GUI
app = FletV2App(page, real_server=server_instance)
# GUI calls server.get_clients(), server.add_file(), etc. directly
```

**Standalone GUI Mode** - `python FletV2/start_gui_only.py`:
```python
# Sets FLET_GUI_ONLY_MODE=1 environment variable
# Launches GUI without server instance
app = FletV2App(page, real_server=None)
# All views show empty states with "Server not connected" messages
```

### Environment Variables
- `FLET_GUI_ONLY_MODE`: Enable GUI-only mode without server connection (empty states)
- `CYBERBACKUP_DISABLE_INTEGRATED_GUI`: Disable embedded server GUI
- `DASHBOARD_REFRESH_INTERVAL`: Set dashboard refresh interval in seconds
- `FLET_V2_DEBUG`: Enable debug mode for additional logging

## Testing and Quality Assurance

### Test Strategy
- Integration tests for server-client communication
- Unit tests for encryption and protocol implementations
- GUI component tests for UI interactions
- End-to-end tests for backup workflow

### Quality Tools
- Ruff for linting and formatting
- Pyright for type checking
- MyPy for additional type verification
- Comprehensive logging for debugging

## Special Considerations for Claude

### Security Context
- Always prioritize secure handling of encryption keys and credentials
- Follow security best practices when modifying crypto implementations
- Ensure all file operations maintain data integrity
- Verify that any new features maintain the end-to-end encryption model

### GUI Development
- Maintain consistency with the tri-style design system (Material 3, Neumorphism, Glassmorphism)
- Use the provided theme utilities for styling components
- Implement proper state management for reactive UI updates
- Follow the established navigation and view switching patterns
- Prefer Flet's built-in components over complex custom implementations

### Server Integration
- **CRITICAL**: Server has NO API - use direct Python method calls via ServerBridge
- ServerBridge is a thin delegation wrapper, not an API client
- All operations are in-memory Python calls: `bridge.get_clients()` → `server.get_clients()`
- Implement proper error handling for server method calls (not network operations)
- Ensure thread safety when calling server methods from GUI thread
- Data format conversion handled by ServerBridge (BLOB UUIDs ↔ strings)

### Database Operations
- Use the existing DatabaseManager for all database interactions
- Follow the established schema patterns for client and file records
- Implement proper transaction handling for data consistency
- Include appropriate error handling for database operations

### Performance Considerations
- Optimize for frequent UI updates with minimal redraw operations
- Use targeted updates rather than full page refreshes
- Implement efficient data processing for large file transfers
- Consider memory usage when handling large datasets in GUI
- Use GPU-accelerated animations for smooth interactions

### Code Quality
- Maintain the high code quality standards already established
- Use proper type hints and comprehensive error handling
- Follow the existing patterns for logging and diagnostics
- Ensure all new code is well-documented with docstrings

### Logging Standards (October 2025)
The codebase follows strict logging level standards documented in [server.py:82-97](python_server/server/server.py#L82):

**Level Usage**:
- **DEBUG**: Protocol details, packet parsing, reassembly status, detailed state changes (verbose diagnostics)
- **INFO**: Client connections/disconnections, file transfers, successful operations, startup/shutdown (important events)
- **WARNING**: Recoverable errors, validation failures, retries, deprecated usage (needs attention but non-blocking)
- **ERROR**: Failed operations, database errors, crypto failures, network issues (prevents specific operations)
- **CRITICAL**: System failures, startup failures, security violations (system-wide problems)

**Best Practices**:
1. Use DEBUG for verbose info disabled in production by default
2. Use INFO for events that help understand system flow
3. Use WARNING for issues that don't stop operation
4. Include relevant context (client name, file name, operation type) in all messages
5. Avoid duplicate logging (don't log same event at multiple levels)
6. Never use `print()` for diagnostics - always use `logger` methods

### Input Validation Pattern
All user-facing methods must validate inputs before database operations:
```python
# Example from add_client() - server.py:681-707
if not isinstance(name, str) or len(name) == 0:
    return self._format_response(False, error="Invalid name")
if len(name) > MAX_CLIENT_NAME_LENGTH:
    return self._format_response(False, error=f"Name too long (max {MAX_CLIENT_NAME_LENGTH})")
if '\x00' in name or '\n' in name:
    return self._format_response(False, error="Invalid characters")
```

### Constants Management
- Never duplicate constants - import from config.py
- Use descriptive constant names: `DEFAULT_LOG_LINES_LIMIT` not magic number `100`
- Document constant purpose inline: `SETTINGS_FILE = "server_settings.json"  # Settings persistence file`
- Group related constants together (Logging, Settings, Protocol, etc.)

## Troubleshooting

### Common Issues
- GUI freezing during server communication: Check for blocking operations
- Client connection failures: Verify protocol compatibility and network settings
- Database lock issues: Ensure proper transaction handling and connection cleanup
- GUI styling inconsistencies: Follow established theme patterns

### Debugging
- Enable detailed logging with `--verbose` or environment variables
- Use the ServerBridge test methods to verify server functionality
- Check the server.log and enhanced log files for error details
- Use the built-in diagnostic tools in the GUI for system monitoring

## Future Development

### Planned Enhancements
- Enhanced analytics and reporting features
- Improved backup scheduling and automation
- Advanced file versioning and recovery options
- Additional GUI themes and customization options

### Architecture Considerations
- Scalability for larger client deployments
- Additional encryption algorithms support
- Cloud storage integration options
- Advanced monitoring and alerting systems