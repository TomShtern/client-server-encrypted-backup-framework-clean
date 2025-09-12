#!/usr/bin/env python3
"""
Unit tests for the theme module.
"""

import unittest
import sys
import os

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import flet as ft
from theme import THEMES, DEFAULT_THEME_NAME, setup_default_theme, toggle_theme_mode, get_current_theme_colors, apply_theme_variant


class TestThemeModule(unittest.TestCase):
    """Test cases for the theme module."""

    def test_themes_dict_structure(self):
        """Test that THEMES dictionary has the expected structure."""
        self.assertIsInstance(THEMES, dict)
        self.assertGreater(len(THEMES), 0)
        
        # Check that each theme has both light and dark variants
        for theme_name, theme_data in THEMES.items():
            self.assertIsInstance(theme_name, str)
            self.assertIsInstance(theme_data, tuple)
            self.assertEqual(len(theme_data), 2)
            light_theme, dark_theme = theme_data
            self.assertIsNotNone(light_theme)
            self.assertIsNotNone(dark_theme)

    def test_default_theme_name(self):
        """Test that DEFAULT_THEME_NAME is valid."""
        self.assertIsInstance(DEFAULT_THEME_NAME, str)
        self.assertIn(DEFAULT_THEME_NAME, THEMES)

    def test_apply_theme_to_page(self):
        """Test applying themes to a page."""
        # Create a mock page
        page = ft.Page()
        
        # Test applying a valid theme
        result = setup_default_theme(page)
        self.assertIsNone(result)  # setup_default_theme returns None
        self.assertIsNotNone(page.theme)
        self.assertIsNotNone(page.dark_theme)

    def test_get_current_theme_colors(self):
        """Test getting current theme colors."""
        # Create a mock page
        page = ft.Page()
        
        # Apply a theme first
        apply_theme_variant(page, DEFAULT_THEME_NAME)
        
        # Get colors
        colors = get_current_theme_colors(page)
        
        # Check that we get the expected color keys
        expected_keys = [
            'primary', 'secondary', 'tertiary', 'error', 'surface', 
            'background', 'on_primary', 'on_secondary', 'on_surface', 
            'on_background', 'outline', 'shadow', 'scrim'
        ]
        
        for key in expected_keys:
            self.assertIn(key, colors)
            # Check that colors are Flet color constants
            self.assertIsInstance(colors[key], str)

    def test_toggle_theme_mode(self):
        """Test toggling theme mode."""
        # Create a mock page
        page = ft.Page()
        
        # Apply a theme first
        apply_theme_variant(page, DEFAULT_THEME_NAME)
        
        # Initially should be SYSTEM or None
        initial_mode = page.theme_mode
        
        # Toggle from SYSTEM/None to LIGHT
        toggle_theme_mode(page)
        self.assertEqual(page.theme_mode, ft.ThemeMode.LIGHT)
        
        # Toggle from LIGHT to DARK
        toggle_theme_mode(page)
        self.assertEqual(page.theme_mode, ft.ThemeMode.DARK)
        
        # Toggle from DARK back to LIGHT
        toggle_theme_mode(page)
        self.assertEqual(page.theme_mode, ft.ThemeMode.LIGHT)


if __name__ == '__main__':
    unittest.main()