# FletV2 Getting Started Guide

Welcome to the FletV2 Desktop GUI! This guide will help you quickly understand the project structure, set up your development environment, and start contributing to the codebase.

## 🎯 Quick Overview

FletV2 is the modern desktop GUI component of CyberBackup 3.0, built with Flet 0.28.3 and Material Design 3. It provides a native interface for server administration with features like real-time monitoring, client management, and database operations.

### Key Benefits
- **Modern UI**: Material Design 3 with enhanced theming
- **Performance**: Async operations keep UI responsive
- **Modular**: View-based architecture for easy development
- **Integrates**: Direct server communication via ServerBridge
- **Tested**: Comprehensive test suite

## 🚀 Quick Start (5 minutes)

### Prerequisites Check
```bash
# Check Python version (requires 3.9+)
python --version

# Check if Git is installed
git --version
```

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd Client_Server_Encrypted_Backup_Framework

# Navigate to FletV2 directory
cd FletV2

# Create virtual environment
python -m venv ../flet_venv

# Activate virtual environment (Windows)
../flet_venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Option 1: Quick test (standalone GUI)
python main.py

# Option 2: With server integration (production-like)
python start_with_server.py
```

### 3. Verify Installation
You should see the FletV2 desktop application launch with:
- NavigationRail with multiple views (Dashboard, Clients, Database, etc.)
- Material Design 3 interface
- Professional styling with gradients and animations

**🎉 Congratulations!** You now have a running FletV2 application.

## 📁 Project Structure Overview

```
FletV2/
├── main.py                    # Application entry point
├── start_with_server.py       # Server integration launcher
├── theme.py                   # Unified theme system
│
├── views/                     # Main feature views
│   ├── dashboard.py           # System overview
│   ├── clients.py             # Client management
│   ├── database_pro.py        # Database operations
│   ├── files.py               # File management
│   └── settings.py            # Settings panel
│
├── utils/                     # Core utilities
│   ├── server_bridge.py       # Server communication
│   ├── ui_components.py       # Reusable UI components
│   ├── async_helpers.py       # Async operations
│   └── state_manager.py       # State management
│
├── components/                # UI building blocks
│   ├── filter_controls.py     # Search & filters
│   ├── global_search.py       # Global search
│   └── breadcrumb.py         # Navigation
│
├── tests/                     # Test suite
├── docs/                      # Documentation
└── archive/                   # Archived code
```

## 🔍 Understanding the Codebase

### Core Concepts

#### 1. **View-Based Architecture**
Each feature is implemented as an independent view:

```python
# Example from views/dashboard.py
def create_dashboard_view(
    server_bridge: Any,
    page: ft.Page,
    state_manager: Any
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """
    Returns: (view_control, dispose_function, setup_function)
    """
    # 1. Build UI components
    content = build_ui()

    # 2. Setup data loading
    async def setup():
        await load_dashboard_data()

    # 3. Cleanup resources
    def dispose():
        cleanup()

    return content, dispose, setup
```

**Key Pattern**: Every view follows the same pattern - return (content, dispose, setup)

#### 2. **ServerBridge Communication**
Clean API for server communication:

```python
# Example usage in any view
async def fetch_data():
    # Structured response: {success, data, error}
    result = await _call_bridge(server_bridge, "get_dashboard_summary")

    if result.get("success"):
        return result.get("data")
    else:
        show_error_message(page, result.get("error"))
```

**Key Pattern**: All server calls return structured responses with success/data/error

#### 3. **Async-First Design**
Keep UI responsive with async operations:

```python
from FletV2.utils.async_helpers import run_sync_in_executor

async def perform_operation():
    # Execute blocking operation in thread pool
    result = await run_sync_in_executor(blocking_function)
    return result
```

**Key Pattern**: Use `run_sync_in_executor` for blocking operations

#### 4. **Unified Theme System**
Consistent styling with Material Design 3:

```python
from FletV2.theme import (
    setup_sophisticated_theme,
    create_modern_card,
    themed_button
)

# Setup theme once at startup
setup_sophisticated_theme(page, theme_mode="system")

# Create themed components
card = create_modern_card(content)
button = themed_button("Click me", on_click=handler)
```

**Key Pattern**: Use theme functions for consistent styling

## 🛠️ Development Workflow

### 1. **Creating a New View**

Step 1: Create the view file
```python
# views/my_new_feature.py
import flet as ft
from FletV2.utils.async_helpers import _call_bridge
from FletV2.theme import create_modern_card, themed_button

def create_my_feature_view(server_bridge, page, state_manager):
    """Create my new feature view."""

    # Build UI components
    title = ft.Text("My New Feature", size=24, weight=ft.FontWeight.BOLD)
    description = ft.Text("This is my awesome new feature!")

    content = ft.Column([
        title,
        description,
        themed_button("Test Action", on_click=test_action),
    ])

    # Wrap in card
    view = create_modern_card(content)

    # Setup function
    async def setup():
        await load_feature_data()

    # Dispose function
    def dispose():
        pass

    return view, dispose, setup

# Test action handler
async def test_action(e):
    # Show success message
    e.page.show_snack_bar(
        ft.SnackBar(ft.Text("Action executed!"))
    )
```

Step 2: Register the view in main.py
```python
# In main.py, add to view creation function
elif view_name == "my_feature":
    return create_my_feature_view(server_bridge, page, state_manager)
```

Step 3: Add navigation button
```python
# In main.py NavigationRail destinations
ft.NavigationRailDestination(
    icon=ft.Icons.STAR,
    selected_icon=ft.Icons.STAR,
    label_content=ft.Text("My Feature")
),
```

### 2. **Adding Server Communication**

Step 1: Add method to ServerBridge
```python
# utils/server_bridge.py
def get_my_feature_data(self) -> dict:
    """Get data for my feature."""
    if not self.real_server:
        return {'success': False, 'data': None, 'error': 'Server not connected'}

    try:
        data = self.real_server.get_my_feature_data()
        return {'success': True, 'data': data, 'error': None}
    except Exception as e:
        return {'success': False, 'data': None, 'error': str(e)}
```

Step 2: Create async fetch function
```python
# In your view file
async def load_feature_data():
    result = await _call_bridge(server_bridge, "get_my_feature_data")
    if result.get("success"):
        # Update UI with data
        update_ui_with_data(result.get("data"))
    else:
        show_error_message(page, result.get("error"))
```

### 3. **Creating Reusable Components**

Step 1: Create component file
```python
# components/my_custom_component.py
import flet as ft
from FletV2.theme import create_modern_card, themed_button

def create_my_component(data, on_action=None):
    """Create a reusable component."""

    # Component content
    content = ft.Column([
        ft.Text(data.get('title', 'Untitled')),
        themed_button(
            "Action" if on_action else "Default Action",
            on_click=on_action or default_action,
            variant="outlined"
        )
    ])

    # Wrap in card
    return create_modern_card(content)

def default_action(e):
    """Default action handler."""
    e.page.show_snack_bar(ft.SnackBar(ft.Text("Default action!")))
```

Step 2: Use in views
```python
# In any view file
from FletV2.components.my_custom_component import create_my_component

# Create component
component = create_my_component(
    data={'title': 'My Component'},
    on_action=my_action_handler
)
```

## 🧪 Testing Your Changes

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_dashboard.py

# Run with coverage
python -m pytest tests/ --cov=FletV2 --cov-report=html
```

### Writing Tests
```python
# tests/test_my_feature.py
import pytest
import flet as ft
from FletV2.views.my_feature import create_my_feature_view

class TestMyFeature:
    def test_create_my_feature_view(self):
        """Test that view creation returns correct types."""
        page = ft.Page()
        server_bridge = None

        view, dispose, setup = create_my_feature_view(
            server_bridge, page, None
        )

        assert isinstance(view, ft.Control)
        assert callable(dispose)
        assert callable(setup)

    async def test_my_action(self):
        """Test my action handler."""
        page = ft.Page()

        # Create mock event
        event = ft.FletAppMockEvent()
        event.page = page

        # Call handler
        await test_action(event)

        # Verify result
        assert page.snack_bar is not None
```

### Testing Manually
```bash
# Quick manual testing
python main.py

# Test with server integration
python start_with_server.py

# Test specific features
# 1. Check Dashboard loads and displays data
# 2. Navigate between views
# 3. Test interactive elements
# 4. Verify error handling
```

## 🎨 Working with the Theme System

### Using Theme Functions

#### Basic Components
```python
from FletV2.theme import create_modern_card, themed_button, create_metric_card

# Cards
card = create_modern_card(content, elevation=3)

# Buttons
filled_btn = themed_button("Filled", variant="filled")
outlined_btn = themed_button("Outlined", variant="outlined")
text_btn = themed_button("Text", variant="text")

# Metric cards
metric = create_metric_card("Active Users", "1,234", "+5%", icon=ft.Icons.PEOPLE)
```

#### Enhanced Components
```python
from FletV2.theme import (
    create_gradient_button,
    create_enhanced_card,
    create_gradient
)

# Gradient buttons
gradient_btn = create_gradient_button(
    "Click me",
    on_click=handler,
    gradient_type="primary",
    icon=ft.Icons.STAR
)

# Enhanced cards
enhanced_card = create_enhanced_card(
    content,
    gradient_background="success",
    hover_effect=True
)

# Custom gradients
custom_gradient = create_gradient("warning")
container = ft.Container(
    content=ft.Text("Custom gradient"),
    gradient=custom_gradient
)
```

#### Theme Setup
```python
# In main.py or view setup
from FletV2.theme import setup_sophisticated_theme

# Setup theme
setup_sophisticated_theme(page, theme_mode="system")

# Toggle theme mode
from FletV2.theme import toggle_theme_mode
toggle_theme_mode(page)
```

### Color System
```python
from FletV2.theme import get_brand_color

# Use semantic colors
primary_color = get_brand_color("primary")
success_color = get_brand_color("success")
warning_color = get_brand_color("warning")

# Apply to components
button = ft.ElevatedButton(
    "Click me",
    bgcolor=primary_color
)
```

## 🔧 Common Development Tasks

### 1. **Adding Database Operations**

```python
# Add to ServerBridge
def get_table_data(self, table_name: str, limit: int = 100) -> dict:
    """Get data from table."""
    try:
        data = self.real_server.get_table_data(table_name, limit)
        return {'success': True, 'data': data, 'error': None}
    except Exception as e:
        return {'success': False, 'data': None, 'error': str(e)}

# Use in view
async def load_table_data(table_name: str):
    result = await _call_bridge(server_bridge, "get_table_data", table_name)
    if result.get("success"):
        return result.get("data")
    else:
        raise Exception(result.get("error"))
```

### 2. **Creating Filter Controls**

```python
from FletV2.components.filter_controls import create_advanced_filter_panel

# Create filter panel
filters = {
    'status': ['active', 'inactive', 'all'],
    'date_range': ['today', 'week', 'month', 'all']
}

def on_filter_change(filter_values):
    # Apply filters
    apply_filters_to_data(filter_values)

filter_panel = create_advanced_filter_panel(filters, on_filter_change)
```

### 3. **Adding Search Functionality**

```python
from FletV2.utils.ui_components import create_search_bar

def on_search_change(search_term):
    # Filter data based on search
    filtered_data = filter_data_by_search(current_data, search_term)
    update_display(filtered_data)

search_bar = create_search_bar(
    on_change=on_search_change,
    placeholder="Search items..."
)
```

### 4. **Implementing Real-time Updates**

```python
# Add periodic updates to view setup
async def setup():
    await load_initial_data()
    start_periodic_updates()

def start_periodic_updates():
    async def update_loop():
        while not disposed:
            try:
                # Fetch latest data
                new_data = await fetch_latest_data()

                # Update UI if data changed
                if has_data_changed(new_data, current_data):
                    update_display(new_data)
                    current_data = new_data

            except Exception as e:
                logger.error(f"Update failed: {e}")

            # Wait before next update
            await asyncio.sleep(30)  # Update every 30 seconds

    # Start update loop
    page.run_task(update_loop)
```

## 🚫 Common Pitfalls & Solutions

### 1. **Import Errors**
**Problem**: Module imports fail
```python
# ❌ Wrong
from utils.server_bridge import ServerBridge

# ✅ Correct
from FletV2.utils.server_bridge import ServerBridge
```

**Solution**: Always use relative imports from the FletV2 package root.

### 2. **Async/await Issues**
**Problem**: UI freezing during operations
```python
# ❌ Wrong - blocks UI thread
def on_click(e):
    data = server_bridge.get_data()  # Blocks!
    update_ui(data)

# ✅ Correct - non-blocking
async def on_click(e):
    data = await run_sync_in_executor(server_bridge.get_data)
    update_ui(data)
```

### 3. **Memory Leaks**
**Problem**: Views not properly disposed
```python
# ✅ Correct - proper cleanup
def dispose():
    nonlocal disposed, update_task
    disposed = True

    # Cancel background tasks
    if update_task and not update_task.done():
        update_task.cancel()

    # Clear references
    server_bridge = None
    page = None
```

### 4. **State Management**
**Problem**: UI not updating when data changes
```python
# ✅ Correct - explicit UI updates
def update_display(data):
    # Update UI controls
    list_view.controls = [create_item_card(item) for item in data]

    # Force UI update
    page.update()
```

### 5. **Error Handling**
**Problem**: Unhandled exceptions crash the app
```python
# ✅ Correct - graceful error handling
async def perform_operation():
    try:
        result = await _call_bridge(server_bridge, "operation")
        if not result.get("success"):
            show_error_message(page, result.get("error"))
            return
        process_success(result.get("data"))
    except Exception as e:
        logger.exception("Operation failed")
        show_error_message(page, f"Operation failed: {e}")
```

## 🔍 Debugging Tips

### 1. **Enable Debug Mode**
```bash
export FLET_DEBUG=1
export FLET_DASHBOARD_DEBUG=1
python main.py
```

### 2. **Logging**
```python
import logging
from FletV2.utils.debug_setup import get_logger

logger = get_logger(__name__)
logger.info("Debug information")
logger.error(f"Error: {e}")
```

### 3. **Check Control Attachment**
```python
# Verify UI controls are properly attached
def update_ui(data):
    if not isinstance(list_view, ft.Column):
        logger.error("List view is not a Column")
        return

    # Update controls
    list_view.controls = [create_card(item) for item in data]
    list_view.update()  # Explicit update
```

### 4. **Test ServerBridge Communication**
```python
# Test server bridge responses
def test_server_bridge():
    bridge = ServerBridge(real_server=None)
    result = bridge.get_dashboard_summary()

    assert result['success'] is False
    assert 'Server not connected' in result['error']
```

## 📚 Learning Resources

### Code Structure
- **README.md**: Project overview and setup
- **ARCHITECTURE.md**: Detailed technical architecture
- **THEME_GUIDE.md**: Theme system documentation
- **Code comments**: Extensive inline documentation

### Flet Documentation
- [Flet Framework](https://flet.dev)
- [Material Design 3](https://material.io/design)
- [Flet Controls](https://flet.dev/docs/controls)

### Best Practices
- Always use async/await for operations that might block
- Implement proper cleanup in dispose functions
- Use structured error responses
- Follow the view creation pattern
- Write tests for new features

## 🤝 Contributing

### Development Process
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Develop** your feature following the patterns
4. **Test** thoroughly with manual and automated tests
5. **Document** any new functionality
6. **Submit** a pull request with clear description

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Add comprehensive docstrings
- Write unit tests for new features
- Use meaningful variable and function names

### Commit Messages
```
feat: Add new dashboard metric view
fix: Resolve memory leak in client view
docs: Update API reference
style: Format code with black
refactor: Simplify theme system
test: Add integration tests for database
```

## ❓ Getting Help

### Documentation
- Check this Getting Started Guide
- Read ARCHITECTURE.md for technical details
- Review existing code for patterns
- Check THEME_GUIDE.md for styling

### Development Issues
- Verify your setup follows the Quick Start guide
- Check import paths are correct
- Ensure async operations use run_sync_in_executor
- Test with minimal reproducible examples

### Community
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Code comments for implementation details

---

**Ready to start coding?** Begin by exploring the existing views in the `views/` directory to understand the patterns, then create your first feature following the examples in this guide!