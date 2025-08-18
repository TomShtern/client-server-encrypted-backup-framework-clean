# -*- coding: utf-8 -*-
"""
base_page.py - A powerful Abstract Base Class for all GUI pages.

This module defines a feature-rich blueprint that all content pages must implement.
It provides not only a contract for the controller but also a toolkit of helper
methods to ensure a consistent, professional, and "fancy" look and feel across
the entire application, drastically reducing boilerplate code in child pages.
"""
from __future__ import annotations
import abc
from typing import TYPE_CHECKING, Dict, Any

# --- Widget Toolkit Import ---
try:
    import ttkbootstrap as ttk
except ImportError:
    from tkinter import ttk

# --- Constants Namespace Import (Definitive Pattern) ---
try:
    from ttkbootstrap import constants
except ImportError:
    from tkinter import constants

# This is the standard, professional pattern for breaking circular dependencies.
if TYPE_CHECKING:
    from ..ServerGUI import ServerGUI  # Import the full class for type analysis


class BasePage(ttk.Frame, abc.ABC):
    """
    An abstract base class providing a common toolkit for all pages.

    This class enforces a consistent structure and provides helper methods
    for creating styled, common UI elements like headers and placeholders.
    It has no knowledge of window management; it is a pure content container.
    """

    def __init__(self, parent: ttk.Frame, controller: 'ServerGUI') -> None:
        """
        Initializes the page frame.

        Args:
            parent (ttk.Frame): The parent widget (the main content area).
            controller ('ServerGUI'): The main application controller instance.
                The string forward reference hint establishes a verifiable
                architectural contract with the ServerGUI class.
        """
        super().__init__(parent, style='TFrame')
        self.controller: 'ServerGUI' = controller

    def _create_page_header(self, title: str, icon_name: str) -> ttk.Frame:
        """Creates a standardized, styled header for the page."""
        header_frame = ttk.Frame(self, style='TFrame', padding=(5, 10))
        header_frame.pack(side=constants.TOP, fill=constants.X)
        
        icon = self.controller.asset_manager.get_icon(icon_name, size=(32, 32))
        ttk.Label(header_frame, image=icon).pack(side=constants.LEFT, padx=(0, 10))
        
        ttk.Label(header_frame, text=title, font=('Segoe UI', 18, 'bold')).pack(side=constants.LEFT, anchor='w')
        
        return header_frame

    def _create_separator(self) -> ttk.Separator:
        """Creates a standardized horizontal separator."""
        separator = ttk.Separator(self, orient=constants.HORIZONTAL)
        separator.pack(side=constants.TOP, fill=constants.X, pady=10, padx=5)
        return separator

    def _create_placeholder(self, text: str, icon_name: str) -> ttk.Frame:
        """Creates a standardized, centered placeholder message."""
        placeholder_frame = ttk.Frame(self, style='TFrame')
        
        icon = self.controller.asset_manager.get_icon(icon_name, size=(64, 64))
        icon_label = ttk.Label(placeholder_frame, image=icon, style='secondary.TLabel')
        icon_label.pack(pady=(0, 10))
        
        text_label = ttk.Label(placeholder_frame, text=text, font=('Segoe UI', 12, 'italic'), style='secondary.TLabel')
        text_label.pack()
        
        return placeholder_frame

    # --- Public API for Controller ---

    def on_show(self) -> None:
        """
        [Overrideable] Called by the controller just before the page is shown.
        Subclasses can use this to refresh data.
        """
        pass

    @abc.abstractmethod
    def handle_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """
        [Required] Called by the controller to pass updates from the backend.
        """
        pass