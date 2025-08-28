# Views package for Flet Server GUI

# Import all view classes
from .dashboard import DashboardView
from .clients import ClientsView
from .files import FilesView
from .analytics import AnalyticsView
from .logs_view import LogsView
from .settings_view import SettingsView
from .database import DatabaseView
from flet_server_gui.ui.layouts.responsive_fixes import ResponsiveLayoutFixes, fix_content_clipping, fix_button_clickable_areas, ensure_windowed_compatibility


# Export all view classes
__all__ = [
    "DashboardView",
    "ClientsView", 
    "FilesView",
    "AnalyticsView",
    "LogsView",
    "SettingsView",
    "DatabaseView"
]