# FletV2 - Modern Desktop GUI for CyberBackup 3.0

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flet](https://img.shields.io/badge/Flet-0.28.3-green.svg)](https://flet.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

FletV2 is the modern desktop GUI component of the Client-Server Encrypted Backup Framework (CyberBackup 3.0). Built with Flet 0.28.3 and Material Design 3, it provides a native, high-performance interface for server administration and monitoring.

## 🎯 Project Overview

FletV2 serves as the **Desktop GUI** in a dual-GUI architecture:
- **FletV2 Desktop GUI**: Native desktop application for administrators
- **JavaScript Web GUI**: Browser-based interface for end-user backups

### Key Features

- ✅ **Material Design 3**: Modern, accessible interface with enhanced theming
- ✅ **Dual Architecture**: ServerBridge integration + network protocol support
- ✅ **Real-time Monitoring**: Live dashboard with metrics and activity tracking
- ✅ **Database Management**: Full CRUD operations with SQLite integration
- ✅ **Client Management**: Monitor and manage connected backup clients
- ✅ **File Operations**: Browse, search, and manage backed-up files
- ✅ **Enhanced Theming**: Unified theme system with gradients and animations
- ✅ **Performance Optimized**: Async operations and efficient UI updates

## 🏗️ Architecture

### Core Components

```
FletV2/
├── main.py                    # Application entry point
├── start_with_server.py       # Server integration launcher
├── theme.py                   # Unified theme system
├── views/                     # Feature views
│   ├── dashboard.py           # System overview & monitoring
│   ├── clients.py             # Client management
│   ├── database_pro.py        # Database operations
│   ├── files.py               # File browser & management
│   └── ...
├── utils/                     # Core utilities
│   ├── server_bridge.py       # Server communication layer
│   ├── ui_components.py       # Reusable UI components
│   ├── async_helpers.py       # Async operation utilities
│   └── ...
├── components/                # UI building blocks
│   ├── filter_controls.py     # Search & filter components
│   ├── global_search.py       # Global search functionality
│   └── ...
└── tests/                     # Comprehensive test suite
```

### Design Patterns

#### 1. **ServerBridge Pattern**
Direct communication with the backup server without network overhead:

```python
# Direct method calls on server object
app = main.FletV2App(page, real_server=server_instance)

# Structured responses
result = {'success': bool, 'data': Any, 'error': str}
```

#### 2. **View-Based Architecture**
Each major feature is implemented as a separate view:

```python
def create_dashboard_view(server_bridge, page, state_manager):
    # Returns (view_control, dispose_function, setup_function)
    return root, dispose, setup
```

#### 3. **Unified Theme System**
Single source of truth for styling with Material Design 3:

```python
from FletV2.theme import (
    setup_sophisticated_theme,
    create_modern_card,
    themed_button
)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Flet 0.28.3
- Windows 10/11 (primary development platform)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Client_Server_Encrypted_Backup_Framework/FletV2
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv ../flet_venv
   ../flet_venv/Scripts/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Option 1: Standalone GUI (Development)
```bash
cd FletV2
../flet_venv/Scripts/python main.py
```

#### Option 2: Integrated with Server (Production)
```bash
cd FletV2
../flet_venv/Scripts/python start_with_server.py
```

#### Option 3: One-Click Launch (Complete System)
```bash
python scripts/one_click_build_and_run.py
```

## 📱 User Interface

### Navigation Structure

The application uses a **NavigationRail** for primary navigation:

1. **🏠 Dashboard**: System overview, metrics, and recent activity
2. **👥 Clients**: Connected clients and their status
3. **💾 Database**: Database management and operations
4. **📁 Files**: File browser and backup management
5. **📋 Logs**: System logs and debugging information
6. **⚙️ Settings**: Application configuration

### Key Views

#### Dashboard View
- Real-time system metrics (CPU, memory, uptime)
- Connected clients summary
- Recent activity feed
- Server status monitoring

#### Clients View
- List of registered clients
- Connection status indicators
- Client management operations
- Search and filter capabilities

#### Database View
- Table browser with native DataTable
- Full CRUD operations
- Data export (CSV, JSON)
- Search and pagination

#### Files View
- Hierarchical file browser
- File metadata and properties
- Backup status tracking
- Search and filtering

## 🎨 Theming and Styling

### Unified Theme System

The project uses a consolidated theme system that provides:

- **Enhanced Gradients**: 7 pre-defined gradient types
- **Material Design 3**: Native Flet components with semantic colors
- **Animations**: GPU-accelerated hover effects and transitions
- **Neumorphic Components**: Subtle depth and modern appearance

### Usage Examples

```python
# Setup theme
setup_sophisticated_theme(page, theme_mode="system")

# Create themed components
card = create_modern_card(content, elevation=3)
button = themed_button("Click me", on_click=handler, variant="filled")
metric = create_metric_card("Active Users", "1,234", "+12.5%")

# Gradient components
gradient_btn = create_gradient_button("Action", on_click, "primary")
enhanced_card = create_enhanced_card(content, "success")
```

### Color System

```python
# Semantic color mapping
colors = {
    "primary": ft.Colors.PRIMARY,
    "success": ft.Colors.SUCCESS,
    "warning": ft.Colors.WARNING,
    "error": ft.Colors.ERROR,
    "info": ft.Colors.TERTIARY
}
```

## 🔧 Development

### Project Structure

```
FletV2/
├── main.py                     # Application entry point
├── start_with_server.py        # Server integration
├── theme.py                    # Unified theme system
│
├── views/                      # Feature views
│   ├── dashboard.py            # System dashboard
│   ├── clients.py              # Client management
│   ├── database_pro.py         # Database operations
│   ├── files.py                # File management
│   ├── logs.py                 # Log viewer
│   └── settings.py             # Settings panel
│
├── utils/                      # Core utilities
│   ├── server_bridge.py        # Server communication
│   ├── database_manager.py     # Database operations
│   ├── ui_components.py        # Reusable UI components
│   ├── async_helpers.py        # Async utilities
│   ├── state_manager.py        # State management
│   └── user_feedback.py        # Notifications & dialogs
│
├── components/                 # UI building blocks
│   ├── filter_controls.py      # Search & filters
│   ├── global_search.py        # Global search
│   ├── breadcrumb.py          # Navigation breadcrumbs
│   └── context_menu.py        # Context menus
│
├── tests/                      # Test suite
│   ├── test_dashboard.py       # Dashboard tests
│   ├── test_clients.py         # Client tests
│   ├── test_database.py        # Database tests
│   └── integration/            # Integration tests
│
└── docs/                       # Documentation
    ├── API_REFERENCE.md        # API documentation
    ├── COMPONENT_GUIDE.md      # Component usage
    └── DEVELOPMENT.md          # Development guide
```

### Development Guidelines

#### 1. **View Development**
Each view follows this pattern:

```python
def create_view_name(
    server_bridge: Any,
    page: ft.Page,
    state_manager: Any
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]:
    """Create a view.

    Returns:
        (view_control, dispose_function, setup_function)
    """

    # Build UI components
    content = build_view_content()

    # Setup event handlers
    def setup():
        # Initialize data loading
        pass

    def dispose():
        # Cleanup resources
        pass

    return content, dispose, setup
```

#### 2. **Server Communication**
Use ServerBridge for all server interactions:

```python
async def fetch_data():
    result = await _call_bridge(server_bridge, "method_name", *args)
    if result.get("success"):
        return result.get("data")
    else:
        raise Exception(result.get("error"))
```

#### 3. **Async Operations**
Use run_in_executor for blocking operations:

```python
from FletV2.utils.async_helpers import run_sync_in_executor

async def perform_operation():
    result = await run_sync_in_executor(blocking_function, *args)
    return result
```

#### 4. **Error Handling**
Follow structured error handling patterns:

```python
try:
    result = await server_operation()
    if not result.get("success"):
        show_error_message(page, result.get("error"))
        return
    # Process successful result
except Exception as e:
    show_error_message(page, f"Operation failed: {e}")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_dashboard.py

# Run with coverage
python -m pytest tests/ --cov=FletV2 --cov-report=html
```

### Test Structure

```
tests/
├── unit/                       # Unit tests
│   ├── test_theme.py          # Theme system tests
│   ├── test_async_helpers.py  # Async utilities tests
│   └── test_ui_components.py  # UI components tests
│
├── integration/               # Integration tests
│   ├── test_dashboard.py      # Dashboard integration
│   ├── test_clients.py        # Client management tests
│   └── test_database.py       # Database operations tests
│
└── performance/               # Performance tests
    └── test_ui_performance.py # UI performance tests
```

### Writing Tests

```python
import pytest
import flet as ft
from FletV2.views.dashboard import create_dashboard_view

class TestDashboardView:
    def test_create_dashboard_view(self):
        """Test dashboard view creation."""
        page = ft.Page()
        server_bridge = None

        view, dispose, setup = create_dashboard_view(
            server_bridge, page, None
        )

        assert isinstance(view, ft.Control)
        assert callable(dispose)
        assert callable(setup)
```

## 📚 API Reference

### Core Classes

#### FletV2App
Main application class that manages views and navigation.

```python
class FletV2App:
    def __init__(self, page: ft.Page, server_bridge=None):
        """Initialize the application.

        Args:
            page: Flet page instance
            server_bridge: Optional server bridge for server integration
        """
```

#### ServerBridge
Communication layer between GUI and backup server.

```python
class ServerBridge:
    def get_dashboard_summary(self) -> dict:
        """Get dashboard summary data.

        Returns:
            dict: {'success': bool, 'data': Any, 'error': str}
        """

    def get_clients(self) -> dict:
        """Get registered clients.

        Returns:
            dict: {'success': bool, 'data': List[Client], 'error': str}
        """
```

### Utility Functions

#### Theme System
```python
def setup_sophisticated_theme(page: ft.Page, theme_mode: str = "system")
def create_modern_card(content: ft.Control, elevation: int = 2) -> ft.Container
def themed_button(text: str, on_click=None, variant: str = "filled") -> ft.Button
def create_metric_card(title: str, value: str, change: str = None) -> ft.Container
```

#### UI Components
```python
def create_action_button(text: str, on_click, icon=None, primary=True)
def create_search_bar(on_change, placeholder="Search...")
def create_filter_dropdown(label: str, options: list, on_change)
def create_status_pill(status: str, variant: str = "filled")
```

#### Async Helpers
```python
async def run_sync_in_executor(func: Callable, *args) -> Any
async def safe_server_call(bridge, method_name: str, *args) -> dict
def create_async_fetch_function(method_name: str, empty_default=None)
```

## 🐛 Troubleshooting

### Common Issues

#### 1. **UI Not Rendering**
**Symptoms**: Gray screen or missing content
**Solutions**:
- Check control attachment with `is_control_attached()`
- Ensure proper async/await patterns
- Verify theme setup completion

#### 2. **Server Connection Issues**
**Symptoms**: "Server not connected" messages
**Solutions**:
- Verify server bridge initialization
- Check server startup in integrated mode
- Ensure proper error handling

#### 3. **Database Operations Failing**
**Symptoms**: Database errors or timeouts
**Solutions**:
- Check SQLite database file permissions
- Verify connection pooling configuration
- Use async operations for database calls

#### 4. **Performance Issues**
**Symptoms**: Slow UI updates or lag
**Solutions**:
- Use `run_sync_in_executor` for blocking operations
- Implement proper loading states
- Optimize data fetching patterns

### Debug Mode

Enable debug mode for detailed logging:

```bash
export FLET_DEBUG=1
export FLET_DASHBOARD_DEBUG=1
python main.py
```

### Logging

The application uses structured logging:

```python
from FletV2.utils.debug_setup import get_logger

logger = get_logger(__name__)
logger.info("Operation completed successfully")
logger.error(f"Operation failed: {error}")
```

## 🤝 Contributing

### Development Setup

1. **Fork and clone** the repository
2. **Create a virtual environment**:
   ```bash
   python -m venv flet_venv
   flet_venv/Scripts/activate
   ```
3. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   ```
4. **Run tests** to ensure everything works:
   ```bash
   python -m pytest tests/
   ```

### Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** for all functions
- Write **comprehensive docstrings**
- Add **unit tests** for new features
- Use **meaningful variable names**

### Commit Messages

Use conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** and add tests

3. **Run the test suite**:
   ```bash
   python -m pytest tests/
   ```

4. **Update documentation** if needed

5. **Submit pull request** with clear description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flet Team**: For the excellent cross-platform UI framework
- **Material Design**: For the design system and guidelines
- **Python Community**: For the robust ecosystem and libraries

## 📞 Support

- **Documentation**: Check the `docs/` directory for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for help and ideas

---

**Built with ❤️ using Flet 0.28.3 and Material Design 3**