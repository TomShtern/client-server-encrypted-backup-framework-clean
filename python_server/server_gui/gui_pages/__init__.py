# -*- coding: utf-8 -*-
"""
gui_pages - A package containing all content pages for the Server GUI.

Each module in this package defines a class that inherits from `BasePage`
and is responsible for rendering one of the main views in the application
(e.g., Dashboard, Clients, Settings).
"""

from .base_page import BasePage

__all__ = ["BasePage"]