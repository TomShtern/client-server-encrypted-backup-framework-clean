"""
Python Server GUI Package

This package provides modern GUI components for the backup server including:
- ServerGUI: Main server GUI application
- Modern UI components with consistent theming
- Real-time status monitoring and progress tracking
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, Dict, List, Union
import threading
import time
from datetime import datetime

# Import components that actually exist from ServerGUI module
from .ServerGUI import (
    ModernTheme, 
    CHARTS_AVAILABLE, 
    SYSTEM_MONITOR_AVAILABLE, 
    TRAY_AVAILABLE,
    CALENDAR_AVAILABLE,
    DND_AVAILABLE,
    SERVER_CONTROL_AVAILABLE,
    PROCESS_MONITOR_AVAILABLE,
    BackupServerLike
)

# The ServerGUI class is not yet implemented in ServerGUI.py - create a placeholder
class ServerGUI:
    """Placeholder ServerGUI class for testing and development"""
    def __init__(self, *args, **kwargs):
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def apply_settings(self, settings):
        pass


class ModernCard(tk.Frame):
    """A modern styled card container widget"""
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        self._setup_styling()
        self._create_widgets()
    
    def _setup_styling(self):
        """Apply modern theme styling"""
        self.configure(
            bg=ModernTheme.CARD_BG,
            relief="flat",
            bd=0,
            padx=10,
            pady=10
        )
    
    def _create_widgets(self):
        """Create card content"""
        if self.title:
            title_label = tk.Label(
                self,
                text=self.title,
                bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_PRIMARY,
                font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM, "bold")
            )
            title_label.pack(anchor="w", pady=(0, 5))
        
        # Content frame for user widgets
        self.content_frame = tk.Frame(
            self,
            bg=ModernTheme.CARD_BG
        )
        self.content_frame.pack(fill="both", expand=True)
    
    def add_widget(self, widget, **pack_options):
        """Add a widget to the card content"""
        widget.configure(bg=ModernTheme.CARD_BG)  # type: ignore
        widget.pack(in_=self.content_frame, **pack_options)  # type: ignore


class ModernProgressBar(tk.Frame):
    """A modern styled progress bar widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.progress_value = 0
        self._setup_styling()
        self._create_widgets()
    
    def _setup_styling(self):
        """Apply modern theme styling"""
        self.configure(
            bg=ModernTheme.SECONDARY_BG,
            relief="flat",
            bd=0
        )
    
    def _create_widgets(self):
        """Create progress bar components"""
        # Progress bar container
        self.progress_container = tk.Frame(
            self,
            bg=ModernTheme.ACCENT_BG,
            height=8,
            relief="flat",
            bd=0
        )
        self.progress_container.pack(fill="x", padx=2, pady=2)
        self.progress_container.pack_propagate(False)
        
        # Progress fill
        self.progress_fill = tk.Frame(
            self.progress_container,
            bg=ModernTheme.ACCENT_BLUE,
            height=8
        )
        
        # Progress text
        self.progress_text = tk.Label(
            self,
            text="0%",
            bg=ModernTheme.SECONDARY_BG,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL)
        )
        self.progress_text.pack(pady=(2, 0))
    
    def set_progress(self, value: float, text: Optional[str] = None):
        """Set progress value (0-100)"""
        self.progress_value = max(0, min(100, value))
        
        # Update progress fill width
        if self.progress_value > 0:
            fill_width = (self.progress_value / 100)
            self.progress_fill.place(relwidth=fill_width, relheight=1.0)
        else:
            self.progress_fill.place_forget()
        
        # Update text
        display_text = text or f"{self.progress_value:.0f}%"
        self.progress_text.configure(text=display_text)
        
        # Update color based on progress
        if self.progress_value >= 100:
            self.progress_fill.configure(bg=ModernTheme.SUCCESS)
        elif self.progress_value >= 75:
            self.progress_fill.configure(bg=ModernTheme.ACCENT_BLUE)
        elif self.progress_value >= 50:
            self.progress_fill.configure(bg=ModernTheme.INFO)
        else:
            self.progress_fill.configure(bg=ModernTheme.WARNING)


class ModernStatusIndicator(tk.Frame):
    """A modern styled status indicator widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.status = "unknown"
        self._setup_styling()
        self._create_widgets()
    
    def _setup_styling(self):
        """Apply modern theme styling"""
        self.configure(
            bg=ModernTheme.SECONDARY_BG,
            relief="flat",
            bd=0
        )
    
    def _create_widgets(self):
        """Create status indicator components"""
        # Status indicator dot
        self.status_dot = tk.Label(
            self,
            text="●",
            bg=ModernTheme.SECONDARY_BG,
            fg=ModernTheme.TEXT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, 16)
        )
        self.status_dot.pack(side="left", padx=(0, 5))
        
        # Status text
        self.status_text = tk.Label(
            self,
            text="Unknown",
            bg=ModernTheme.SECONDARY_BG,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM)
        )
        self.status_text.pack(side="left")
    
    def set_status(self, status: str, message: str = ""):
        """Set status (success, warning, error, info, unknown)"""
        self.status = status.lower()
        
        # Update colors based on status
        color_map = {
            "success": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR,
            "info": ModernTheme.INFO,
            "unknown": ModernTheme.TEXT_SECONDARY
        }
        
        color = color_map.get(self.status, ModernTheme.TEXT_SECONDARY)
        self.status_dot.configure(fg=color)
        
        # Update text
        display_text = message or status.title()
        self.status_text.configure(text=display_text)


class ToastNotification:
    """A modern toast notification system"""
    
    _active_toasts: List[tk.Toplevel] = []
    
    def __init__(self, parent: Optional[tk.Widget] = None):
        self.parent = parent or getattr(tk, '_default_root', None)  # type: ignore
    
    @classmethod
    def show(cls, title: str, message: str, duration: int = 3000, 
             notification_type: str = "info", parent: Optional[tk.Widget] = None):
        """Show a toast notification"""
        toast = cls(parent)
        toast._create_toast(title, message, duration, notification_type)
    
    def _create_toast(self, title: str, message: str, duration: int, notification_type: str):
        """Create and display a toast notification"""
        # Create toplevel window
        toast_window = tk.Toplevel(self.parent)  # type: ignore
        toast_window.withdraw()  # Hide initially
        
        # Configure window
        toast_window.overrideredirect(True)
        toast_window.configure(bg=ModernTheme.CARD_BG)
        toast_window.attributes("-alpha", 0.95)  # type: ignore
        toast_window.attributes("-topmost", True)  # type: ignore
        
        # Create content frame
        content_frame = tk.Frame(
            toast_window,
            bg=ModernTheme.CARD_BG,
            padx=15,
            pady=10
        )
        content_frame.pack(fill="both", expand=True)
        
        # Status indicator
        status_colors = {
            "success": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR,
            "info": ModernTheme.INFO
        }
        status_color = status_colors.get(notification_type, ModernTheme.INFO)
        
        status_indicator = tk.Label(
            content_frame,
            text="●",
            bg=ModernTheme.CARD_BG,
            fg=status_color,
            font=(ModernTheme.FONT_FAMILY, 12)
        )
        status_indicator.pack(side="left", padx=(0, 8))
        
        # Text content
        text_frame = tk.Frame(content_frame, bg=ModernTheme.CARD_BG)
        text_frame.pack(side="left", fill="both", expand=True)
        
        title_label = tk.Label(
            text_frame,
            text=title,
            bg=ModernTheme.CARD_BG,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM, "bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")
        
        if message:
            message_label = tk.Label(
                text_frame,
                text=message,
                bg=ModernTheme.CARD_BG,
                fg=ModernTheme.TEXT_SECONDARY,
                font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL),
                anchor="w",
                wraplength=250
            )
            message_label.pack(anchor="w")
        
        # Position toast
        toast_window.update_idletasks()
        window_width = toast_window.winfo_reqwidth()
        window_height = toast_window.winfo_reqheight()
        
        screen_width = toast_window.winfo_screenwidth()
        screen_height = toast_window.winfo_screenheight()
        
        # Calculate position (bottom-right with offset for multiple toasts)
        x = screen_width - window_width - 20
        y = screen_height - window_height - 20 - (len(self._active_toasts) * (window_height + 10))
        
        toast_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        toast_window.deiconify()
        
        # Add to active toasts
        self._active_toasts.append(toast_window)
        
        # Auto-dismiss after duration
        def dismiss_toast():
            try:
                if toast_window in self._active_toasts:
                    self._active_toasts.remove(toast_window)
                toast_window.destroy()
            except:
                pass
        
        toast_window.after(duration, dismiss_toast)
        
        # Allow manual dismissal
        def on_click(event):
            dismiss_toast()
        
        toast_window.bind("<Button-1>", on_click)
        content_frame.bind("<Button-1>", on_click)


class ModernTable(tk.Frame):
    """A modern styled table widget using Treeview"""
    
    def __init__(self, parent, columns: List[str], **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        self._setup_styling()
        self._create_widgets()
    
    def _setup_styling(self):
        """Apply modern theme styling"""
        self.configure(bg=ModernTheme.SECONDARY_BG)
        
        # Configure treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure treeview colors
        style.configure(  # type: ignore
            "Modern.Treeview",
            background=ModernTheme.CARD_BG,
            foreground=ModernTheme.TEXT_PRIMARY,
            fieldbackground=ModernTheme.CARD_BG,
            borderwidth=0,
            relief="flat"
        )
        
        style.configure(  # type: ignore
            "Modern.Treeview.Heading",
            background=ModernTheme.ACCENT_BG,
            foreground=ModernTheme.TEXT_PRIMARY,
            borderwidth=0,
            relief="flat",
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM, "bold")
        )
        
        style.map(  # type: ignore
            "Modern.Treeview",
            background=[("selected", ModernTheme.ACCENT_BLUE)],
            foreground=[("selected", ModernTheme.TEXT_PRIMARY)]
        )
    
    def _create_widgets(self):
        """Create table components"""
        # Create treeview with scrollbar
        tree_frame = tk.Frame(self, bg=ModernTheme.SECONDARY_BG)
        tree_frame.pack(fill="both", expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.columns,
            show="headings",
            style="Modern.Treeview"
        )
        
        # Configure columns
        for col in self.columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="w")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)  # type: ignore
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)  # type: ignore
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def insert_row(self, values: List[Any], **kwargs):
        """Insert a new row into the table"""
        return self.tree.insert("", "end", values=values, **kwargs)
    
    def delete_row(self, item_id: str):
        """Delete a row from the table"""
        self.tree.delete(item_id)
    
    def clear(self):
        """Clear all rows from the table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def get_selected(self):
        """Get selected row data"""
        selection = self.tree.selection()
        return self.tree.item(selection[0])["values"] if selection else None
    
    def set_column_width(self, column: str, width: int):
        """Set column width"""
        self.tree.column(column, width=width)


# Export all components
__all__ = [
    "ServerGUI",
    "ModernTheme", 
    "ModernCard",
    "ModernProgressBar", 
    "ModernStatusIndicator",
    "ToastNotification",
    "ModernTable",
    "CHARTS_AVAILABLE",
    "SYSTEM_MONITOR_AVAILABLE", 
    "TRAY_AVAILABLE",
    "CALENDAR_AVAILABLE",
    "DND_AVAILABLE",
    "SERVER_CONTROL_AVAILABLE",
    "PROCESS_MONITOR_AVAILABLE",
    "BackupServerLike"
]
