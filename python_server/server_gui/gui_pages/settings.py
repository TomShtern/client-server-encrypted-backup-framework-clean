# In file: gui_pages/settings.py

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.constants import *  # Import all tkinter constants (BOTH, LEFT, RIGHT, etc.)
import json
from typing import TYPE_CHECKING, Dict, Any

# Conditional imports for type checking
if TYPE_CHECKING:
    from ..ServerGUI import EnhancedServerGUI

# Import base class and custom widgets
try:
    from ..ServerGUI import BasePage, CustomTooltip
except ImportError:
    # Fallback for different import paths
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from ServerGUI import BasePage, CustomTooltip
    except ImportError:
        # Define minimal fallbacks
        class BasePage:
            def __init__(self, parent, app, **kwargs): pass
        class CustomTooltip:
            def __init__(self, *args, **kwargs): pass

class SettingsPage(BasePage):
    """A page for configuring server and GUI settings."""

    def __init__(self, parent: tk.Widget, app: EnhancedServerGUI, **kwargs: Any) -> None:
        super().__init__(parent, app, **kwargs)

        self.setting_vars: Dict[str, tk.StringVar] = {}
        self.gui_setting_vars: Dict[str, tk.Variable] = {}

        self._create_widgets()
        self._load_settings_to_ui()

    def _create_widgets(self) -> None:
        """Create and lay out all widgets for the settings page."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Use a notebook to separate server and GUI settings
        notebook = ttk.Notebook(self, bootstyle='primary')
        notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # --- Server Settings Tab ---
        server_tab = ttk.Frame(notebook, style='primary.TFrame', padding=15)
        server_tab.columnconfigure(1, weight=1)
        self._create_server_settings_content(server_tab)
        notebook.add(server_tab, text=' ⚙️ Server Configuration ')

        # --- GUI Settings Tab ---
        gui_tab = ttk.Frame(notebook, style='primary.TFrame', padding=15)
        gui_tab.columnconfigure(1, weight=1)
        self._create_gui_settings_content(gui_tab)
        notebook.add(gui_tab, text=' 🎨 Appearance & Behavior ')

        # --- Action Buttons ---
        action_frame = ttk.Frame(self, style='primary.TFrame')
        action_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Button(action_frame, text="💾 Save and Apply Settings", command=self._save_and_apply, bootstyle='success').pack(side=RIGHT)
        ttk.Button(action_frame, text="↩️ Reset to Defaults", command=self._reset_defaults, bootstyle='danger-outline').pack(side=RIGHT, padx=10)


    def _create_server_settings_content(self, parent: ttk.Frame) -> None:
        """Create the input fields for server operational settings."""
        # Define settings with their label, type, and a tooltip
        server_settings_spec = {
            'port': ("Server Port:", "numeric", "The network port the server will listen on. Default: 1256."),
            'storage_dir': ("Storage Directory:", "path", "The folder where all backed-up files will be stored."),
            'max_clients': ("Maximum Clients:", "numeric", "The maximum number of concurrent client connections."),
            'session_timeout': ("Session Timeout (min):", "numeric", "Minutes of inactivity before a client session is timed out."),
            'maintenance_interval': ("Maintenance Interval (sec):", "numeric", "How often the server performs cleanup tasks, in seconds."),
        }
        
        row = 0
        for key, (label_text, input_type, tooltip_text) in server_settings_spec.items():
            label = ttk.Label(parent, text=label_text, style='primary.TLabel')
            label.grid(row=row, column=0, sticky=W, pady=8, padx=(0, 20))
            
            var = tk.StringVar()
            self.setting_vars[key] = var
            
            if input_type == "path":
                entry_frame = ttk.Frame(parent, style='primary.TFrame')
                entry_frame.grid(row=row, column=1, sticky=EW, pady=8)
                entry = ttk.Entry(entry_frame, textvariable=var, style='primary.TEntry')
                entry.pack(side=LEFT, fill=X, expand=True)
                browse_btn = ttk.Button(entry_frame, text="...", command=lambda v=var: self._browse_directory(v), bootstyle='secondary-outline', width=4)
                browse_btn.pack(side=LEFT, padx=(5,0))
                CustomTooltip(entry, tooltip_text)
            else: # numeric or text
                entry = ttk.Entry(parent, textvariable=var, style='primary.TEntry')
                entry.grid(row=row, column=1, sticky=EW, pady=8)
                CustomTooltip(entry, tooltip_text)

            row += 1

    def _create_gui_settings_content(self, parent: ttk.Frame) -> None:
        """Create the controls for GUI-specific settings."""
        # Theme Selector
        ttk.Label(parent, text="Theme:", style='primary.TLabel').grid(row=0, column=0, sticky=W, pady=8, padx=(0, 20))
        theme_var = tk.StringVar()
        self.gui_setting_vars['theme'] = theme_var
        theme_combo = ttk.Combobox(parent, textvariable=theme_var, state="readonly", bootstyle='secondary',
                                   values=['cyborg', 'superhero', 'darkly', 'solar', 'litera', 'cosmo'])
        theme_combo.grid(row=0, column=1, sticky=EW, pady=8)
        CustomTooltip(theme_combo, "Changes the visual theme of the application. Requires restart.")

        # Audio Cues
        ttk.Label(parent, text="Audio Cues:", style='primary.TLabel').grid(row=1, column=0, sticky=W, pady=8, padx=(0, 20))
        audio_var = tk.BooleanVar()
        self.gui_setting_vars['audio_cues'] = audio_var
        audio_check = ttk.Checkbutton(parent, variable=audio_var, text="Enable sound notifications for key events", bootstyle='primary-round-toggle')
        audio_check.grid(row=1, column=1, sticky=W, pady=8)
        CustomTooltip(audio_check, "Play sounds for events like backup success or failure.")


    def _browse_directory(self, var: tk.StringVar) -> None:
        """Open a dialog to choose a directory."""
        directory = filedialog.askdirectory(mustexist=True, title="Select Storage Directory")
        if directory:
            var.set(directory)

    def _load_settings_to_ui(self) -> None:
        """Load the current settings from the app instance into the UI widgets."""
        for key, var in self.setting_vars.items():
            var.set(str(self.app.settings.get(key, '')))
            
        for key, var in self.gui_setting_vars.items():
            var.set(self.app.settings.get(key, ''))

    def _save_and_apply(self) -> None:
        """Save the settings from the UI back to the app and the config file."""
        # Update server settings
        for key, var in self.setting_vars.items():
            self.app.settings[key] = var.get()

        # Update GUI settings
        for key, var in self.gui_setting_vars.items():
            self.app.settings[key] = var.get()
        
        # Validate and convert numeric types
        try:
            self.app.settings['port'] = int(self.app.settings['port'])
            self.app.settings['max_clients'] = int(self.app.settings['max_clients'])
            self.app.settings['session_timeout'] = int(self.app.settings['session_timeout'])
            self.app.settings['maintenance_interval'] = int(self.app.settings['maintenance_interval'])
        except (ValueError, TypeError):
            self.app.show_toast("Invalid number in one of the server settings fields.", "danger")
            return
            
        # Save to file
        self.app._save_settings()

        # Apply to running server if possible
        if self.app.server and self.app.server.running:
            try:
                self.app.server.apply_settings(self.app.settings)
                self.app.show_toast("Settings saved and applied to running server.", "success")
            except Exception as e:
                self.app.show_toast(f"Error applying settings: {e}", "danger")
        else:
            self.app.show_toast("Settings saved successfully.", "success")
            
        self.app.show_toast("Theme change will apply on next restart.", "info")


    def _reset_defaults(self) -> None:
        """Reset all settings to their default values."""
        # This requires re-initializing the settings and then reloading them
        # Note: this will discard any unsaved changes.
        self.app.settings = self.app._load_settings(force_defaults=True)
        self._load_settings_to_ui()
        self.app.show_toast("Settings have been reset to default values. Save to confirm.", "warning")

    def on_show(self) -> None:
        """Called when the page is displayed. Ensures UI reflects current settings."""
        self._load_settings_to_ui()