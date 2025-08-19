# -*- coding: utf-8 -*-
"""
settings.py - The Application and Server Settings page.

This page provides a user-friendly interface for configuring server behavior,
application appearance, and user feedback preferences. It features real-time
validation and interactive controls for a superior user experience.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING, Dict, Any, Union, cast

try:
    import ttkbootstrap as ttk
    from ttkbootstrap import constants
    from ttkbootstrap.tooltip import ToolTip
    from ttkbootstrap.scrolled import ScrolledFrame
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    from tkinter import ttk, constants
    TTKBOOTSTRAP_AVAILABLE = False
    ToolTip = None
    ScrolledFrame = None

from .base_page import BasePage

if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI

class SettingsPage(BasePage):
    """A page for managing application and server settings."""

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        super().__init__(parent, controller)
        self.setting_vars: Dict[str, Union[tk.StringVar, tk.IntVar, tk.BooleanVar]] = {}
        self._create_widgets()
        self._load_settings_into_ui()

    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the settings page."""
        self._create_page_header("Settings", "gear-fill")
        self._create_separator()

        # Use a scrolled frame for future-proofing as more settings are added
        if TTKBOOTSTRAP_AVAILABLE and ScrolledFrame is not None:
            scrolled_frame = ScrolledFrame(self, autohide=True)
            scrolled_frame.pack(fill=constants.BOTH, expand=True, padx=10, pady=(0, 10))
            container = scrolled_frame.container
        else:
            # Fallback to regular frame with scrollbar if ttkbootstrap not available
            container = ttk.Frame(self)
            container.pack(fill=constants.BOTH, expand=True, padx=10, pady=(0, 10))

        # --- Settings Sections for Logical Grouping (Layer 3) ---
        self._create_network_settings(container).pack(fill=constants.X, expand=True, pady=(0, 15))
        self._create_storage_settings(container).pack(fill=constants.X, expand=True, pady=(0, 15))
        self._create_application_settings(container).pack(fill=constants.X, expand=True, pady=(0, 15))
        
        # --- Save Button ---
        save_frame = ttk.Frame(self)
        save_frame.pack(fill=constants.X, padx=10, pady=10)
        self.save_button = ttk.Button(save_frame, text=" Save Settings", command=self._save_settings, style='success.TButton', image=self.controller.asset_manager.get_icon('check-circle-fill'), compound=constants.LEFT)
        self.save_button.pack(side=constants.RIGHT)

    def _create_setting_row(self, parent: Union[ttk.Frame, ttk.Labelframe], key: str, label: str, tooltip: str, widget_type: str, **kwargs: Any) -> None:
        """Helper factory to create a consistent setting row."""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=constants.X, pady=5)
        
        # Label with tooltip
        label_frame = ttk.Frame(row_frame)
        label_frame.pack(side=constants.LEFT, anchor=constants.W, ipadx=5, ipady=5, fill=constants.Y)
        label_widget = ttk.Label(label_frame, text=label, width=20)
        label_widget.pack(side=constants.LEFT)
        info_icon = ttk.Label(label_frame, image=self.controller.asset_manager.get_icon('info-circle'), cursor="question_arrow")
        info_icon.pack(side=constants.LEFT, padx=5)
        if TTKBOOTSTRAP_AVAILABLE and ToolTip is not None:
            ToolTip(info_icon, text=tooltip, bootstyle="info")
        # Note: Fallback tooltip could be added here using tkinter's built-in mechanisms

        # Input Widget
        var: Union[tk.StringVar, tk.IntVar, tk.BooleanVar]
        if widget_type == 'entry':
            var = tk.StringVar()
            widget = ttk.Entry(row_frame, textvariable=var, **kwargs)
        elif widget_type == 'spinbox':
            var = tk.IntVar()
            widget = ttk.Spinbox(row_frame, textvariable=var, **kwargs)
        elif widget_type == 'switch':
            var = tk.BooleanVar()
            if TTKBOOTSTRAP_AVAILABLE:
                # For ttkbootstrap, use bootstyle parameter (type: ignore for static analysis)
                widget = ttk.Checkbutton(row_frame, variable=var, bootstyle="success-round-toggle", **kwargs)  # type: ignore[call-arg]
            else:
                # Fallback to regular checkbutton for tkinter
                widget = ttk.Checkbutton(row_frame, variable=var, **kwargs)
        elif widget_type == 'combobox':
            var = tk.StringVar()
            widget = ttk.Combobox(row_frame, textvariable=var, state='readonly', **kwargs)
        elif widget_type == 'path':
            var = tk.StringVar()
            path_frame = ttk.Frame(row_frame)
            widget = ttk.Entry(path_frame, textvariable=var, **kwargs)
            widget.pack(side=constants.LEFT, fill=constants.X, expand=True)
            browse_btn = ttk.Button(path_frame, text="Browse...", style='info.Outline.TButton', command=lambda v=var: self._browse_directory(v))
            browse_btn.pack(side=constants.LEFT, padx=(5,0))
            path_frame.pack(side=constants.LEFT, fill=constants.X, expand=True)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")

        if widget_type != 'path':
            widget.pack(side=constants.LEFT, fill=constants.X, expand=True)
        
        self.setting_vars[key] = var

    def _create_network_settings(self, parent: ttk.Frame) -> ttk.Labelframe:
        frame = ttk.Labelframe(parent, text=" Network Configuration ", padding=15)
        vcmd = (self.register(self._validate_numeric), '%P') # For real-time validation

        self._create_setting_row(frame, 'port', "Server Port", "The port the server listens on for client connections.", 'spinbox', from_=1024, to=65535, validate='key', validatecommand=vcmd)
        self._create_setting_row(frame, 'max_clients', "Max Clients", "Maximum number of simultaneous client connections.", 'spinbox', from_=1, to=1000, validate='key', validatecommand=vcmd)
        self._create_setting_row(frame, 'session_timeout', "Session Timeout (s)", "Seconds of inactivity before a client is disconnected.", 'spinbox', from_=10, to=3600, validate='key', validatecommand=vcmd)
        return frame

    def _create_storage_settings(self, parent: ttk.Frame) -> ttk.Labelframe:
        frame = ttk.Labelframe(parent, text=" Storage & Maintenance ", padding=15)
        self._create_setting_row(frame, 'storage_dir', "Storage Directory", "The root folder where all backup files are stored.", 'path')
        self._create_setting_row(frame, 'maintenance_interval', "Maintenance (s)", "Interval in seconds to run cleanup tasks.", 'spinbox', from_=60, to=86400)
        self._create_setting_row(frame, 'disk_warning_gb', "Disk Warning (GB)", "Show a warning banner when free disk space is below this value.", 'spinbox', from_=1, to=100)
        return frame

    def _create_application_settings(self, parent: ttk.Frame) -> ttk.Labelframe:
        frame = ttk.Labelframe(parent, text=" Application Appearance & Feedback ", padding=15)
        themes = self.controller.root.style.theme_names()
        self._create_setting_row(frame, 'theme', "Theme", "Changes the application's visual theme.", 'combobox', values=sorted(themes))
        self._create_setting_row(frame, 'audio_enabled', "Audio Cues", "Enable sound effects for key server events.", 'switch')
        return frame
    
    def _validate_numeric(self, value_if_allowed: str) -> bool:
        """Real-time validation function for numeric entry fields (Feature #11)."""
        return value_if_allowed.isdigit() or not value_if_allowed

    def _browse_directory(self, var: tk.StringVar) -> None:
        """Opens a folder selection dialog and updates the variable."""
        if directory := filedialog.askdirectory(initialdir=var.get()):
            var.set(directory)
            
    def _load_settings_into_ui(self) -> None:
        """Populates the UI widgets with values from the settings dictionary."""
        for key, var in self.setting_vars.items():
            value = self.controller.settings.get(key)
            if value is not None:
                try:
                    # Explicitly cast to handle the Any type from settings
                    if isinstance(var, tk.StringVar):
                        cast(tk.StringVar, var).set(str(value))
                    elif isinstance(var, tk.IntVar):
                        cast(tk.IntVar, var).set(int(value))
                    elif isinstance(var, tk.BooleanVar):
                        cast(tk.BooleanVar, var).set(bool(value))
                    else:
                        var.set(value)  # type: ignore
                except (tk.TclError, ValueError) as e:
                    print(f"[WARNING] Could not set UI value for setting '{key}': {e}")
        
    def _save_settings(self) -> None:
        """Gathers values from UI, saves them, and applies them to the server."""
        try:
            for key, var in self.setting_vars.items():
                # Get the value with proper type handling
                value = var.get()  # type: ignore
                self.controller.settings[key] = value

            # Apply theme change immediately
            if theme_var := self.setting_vars.get('theme'):
                theme_value = theme_var.get()  # type: ignore
                if isinstance(theme_value, str):
                    self.controller.change_theme(theme_value)

            # Apply settings to the running server instance
            if self.controller.server:
                self.controller.server.apply_settings(self.controller.settings)
                self.controller.show_toast("Settings applied to running server.", "info")

            self.controller.show_toast("Settings saved successfully!", "success")
            self.controller.play_sound('success')
        except Exception as e:
            self.controller.show_toast(f"Error saving settings: {e}", "error")
            self.controller.play_sound('failure')

    def handle_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """Settings page does not typically react to real-time server updates."""
        _ = update_type, data  # Explicitly mark as used to avoid linting warnings