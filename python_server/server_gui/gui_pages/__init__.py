# In file: gui_pages/__init__.py

"""
gui_pages package.

This package contains all the page modules for the Enhanced Server GUI.
Each module defines a class that inherits from the BasePage and represents
a major view in the application (e.g., Dashboard, Clients, Settings).

This __init__.py file makes the directory a Python package, which is crucial
for the relative imports used within the page modules to find the main
EnhancedServerGUI application class and its custom widgets.
"""

# In gui_pages/__init__.py
try:
    from .dashboard import DashboardPage
    from .clients import ClientsPage
    from .analytics import AnalyticsPage
    from .files import FilesPage
    from .logs import LogsPage
    from .settings import SettingsPage
except ImportError as e:
    # Graceful fallback for missing dependencies
    print(f"[WARNING] GUI pages import error: {e}")
    # Define dummy classes to prevent crashes
    class DashboardPage:
        def __init__(self, *args, **kwargs): pass
    class ClientsPage:
        def __init__(self, *args, **kwargs): pass
    class AnalyticsPage:
        def __init__(self, *args, **kwargs): pass
    class FilesPage:
        def __init__(self, *args, **kwargs): pass
    class LogsPage:
        def __init__(self, *args, **kwargs): pass
    class SettingsPage:
        def __init__(self, *args, **kwargs): pass