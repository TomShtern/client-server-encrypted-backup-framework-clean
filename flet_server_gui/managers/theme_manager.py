#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ThemeManager - Extracted from main.py God Component
Handles theme switching, application, and theme-related UI components.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import utf8_solution for proper encoding handling
safe_print = print  # Default fallback
try:
    from Shared.utils.utf8_solution import safe_print
except ImportError:
    pass

import flet as ft
from typing import Optional, Dict, Any, Callable


class ThemeManager:
    """
    Manages application theming and theme-related UI components.
    
    Extracted from main.py (lines 677-709) to follow Single Responsibility Principle.
    This class is responsible ONLY for theme management - no view switching, no monitoring.
    """
    
    def __init__(self, page: ft.Page, themes: Dict[str, tuple], default_theme_name: str):
        self.page = page
        self.themes = themes
        self.default_theme_name = default_theme_name
        self.current_theme_name = None
        
        # Theme UI components
        self.theme_dropdown: Optional[ft.Dropdown] = None
        self.theme_toggle_button: Optional[ft.IconButton] = None
        
        # Theme change callbacks
        self.theme_change_callbacks: list[Callable] = []
        
        # Initialize theme system
        self._initialize_theme_system()
    
    def _initialize_theme_system(self) -> None:
        """Initialize the theme system with saved or default theme."""
        # Load saved theme or use default
        saved_theme = self.page.client_storage.get("theme_name") or self.default_theme_name
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.apply_theme(saved_theme)
    
    def create_theme_dropdown(self, width: int = 120) -> ft.Dropdown:
        """
        Create theme dropdown component.
        
        Args:
            width: Width of the dropdown component
            
        Returns:
            ft.Dropdown: Theme selection dropdown
        """
        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            options=[ft.dropdown.Option(name) for name in self.themes.keys()],
            value=self.current_theme_name,
            on_change=self._on_theme_dropdown_change,
            width=width,
        )
        return self.theme_dropdown
    
    def create_theme_toggle_button(self, tooltip: str = "Toggle Theme (Light/Dark/System)") -> ft.IconButton:
        """
        Create theme toggle button component.
        
        Args:
            tooltip: Tooltip text for the button
            
        Returns:
            ft.IconButton: Theme toggle button
        """
        self.theme_toggle_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip=tooltip,
            on_click=self._on_theme_toggle
        )
        self._update_theme_icon()
        return self.theme_toggle_button
    
    def add_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback to be called when theme changes."""
        self.theme_change_callbacks.append(callback)
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        Apply selected light and dark themes.
        
        Args:
            theme_name: Name of theme to apply
            
        Returns:
            bool: True if theme was applied successfully, False otherwise
        """
        if theme_name in self.themes:
            try:
                light_theme, dark_theme = self.themes[theme_name]
                self.page.theme = light_theme
                self.page.dark_theme = dark_theme
                self.current_theme_name = theme_name
                
                # Update UI components
                if self.theme_dropdown:
                    self.theme_dropdown.value = theme_name
                
                # Save theme preference
                self.page.client_storage.set("theme_name", theme_name)
                
                # Update page
                self.page.update()
                
                # Notify callbacks
                for callback in self.theme_change_callbacks:
                    try:
                        callback(theme_name)
                    except Exception as e:
                        safe_print(f"[WARNING] Theme change callback error: {e}")
                
                return True
                
            except Exception as e:
                safe_print(f"[ERROR] Failed to apply theme '{theme_name}': {e}")
                return False
        else:
            safe_print(f"[WARNING] Unknown theme name: {theme_name}")
            return False
    
    def toggle_theme_mode(self) -> None:
        """Toggle between light, dark, and system theme modes."""
        current_mode = self.page.theme_mode
        
        if current_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
        elif current_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        else:  # SYSTEM
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self._update_theme_icon()
        self.page.update()
        
        # Notify callbacks with mode change
        mode_name = self.page.theme_mode.name.lower()
        for callback in self.theme_change_callbacks:
            try:
                callback(f"mode_{mode_name}")
            except Exception as e:
                safe_print(f"[WARNING] Theme mode change callback error: {e}")
    
    def _update_theme_icon(self) -> None:
        """Update the theme toggle button icon based on current theme mode."""
        if not self.theme_toggle_button:
            return
            
        mode = self.page.theme_mode
        if mode == ft.ThemeMode.DARK:
            self.theme_toggle_button.icon = ft.Icons.LIGHT_MODE
        elif mode == ft.ThemeMode.LIGHT:
            self.theme_toggle_button.icon = ft.Icons.WB_SUNNY
        else:  # SYSTEM
            self.theme_toggle_button.icon = ft.Icons.SETTINGS_BRIGHTNESS
    
    def _on_theme_dropdown_change(self, e: ft.ControlEvent) -> None:
        """Handle theme dropdown change event."""
        selected_theme_name = e.control.value
        if selected_theme_name:
            self.apply_theme(selected_theme_name)
    
    def _on_theme_toggle(self, e: ft.ControlEvent) -> None:
        """Handle theme toggle button click event."""
        self.toggle_theme_mode()
    
    def get_current_theme_name(self) -> Optional[str]:
        """Get the current theme name."""
        return self.current_theme_name
    
    def get_current_theme_mode(self) -> ft.ThemeMode:
        """Get the current theme mode."""
        return self.page.theme_mode
    
    def get_available_themes(self) -> list[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())
    
    def reset_to_default_theme(self) -> bool:
        """Reset to the default theme."""
        return self.apply_theme(self.default_theme_name)
    
    def get_theme_info(self) -> Dict[str, Any]:
        """
        Get current theme information.
        
        Returns:
            Dict with theme information
        """
        return {
            'current_theme_name': self.current_theme_name,
            'current_theme_mode': self.page.theme_mode.name.lower(),
            'available_themes': self.get_available_themes(),
            'default_theme': self.default_theme_name
        }
    
    def dispose(self) -> None:
        """Clean up theme manager resources."""
        # Clear callbacks
        self.theme_change_callbacks.clear()
        
        # Clear references to UI components
        self.theme_dropdown = None
        self.theme_toggle_button = None