"""
Windows 11 Integration Utilities for Desktop Applications

This module provides Windows 11 specific integration features including:
- System theme detection and automatic switching
- Native Windows color scheme support
- Desktop font optimization
- 4K display scaling support
- Windows 11 Mica/acrylic effect simulation

Compatible with Flet 0.28.3 and Windows 11 desktop applications.
"""

import logging
import platform
from dataclasses import dataclass
from enum import Enum
from typing import Any

import flet as ft

logger = logging.getLogger(__name__)


class WindowsTheme(Enum):
    """Windows system theme enumeration"""
    LIGHT = "light"
    DARK = "dark"
    UNKNOWN = "unknown"


class WindowsColorScheme(Enum):
    """Windows color scheme enumeration"""
    DEFAULT = "default"
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    PINK = "pink"
    RED = "red"
    YELLOW = "yellow"
    CUSTOM = "custom"


@dataclass
class WindowsThemeInfo:
    """Windows theme information"""
    theme: WindowsTheme
    color_scheme: WindowsColorScheme
    accent_color: str
    background_color: str
    text_color: str
    system_font_size: float
    display_scale: float


class WindowsThemeDetector:
    """Detect Windows 11 system theme settings"""

    @staticmethod
    def is_windows_11() -> bool:
        """Check if running on Windows 11"""
        try:
            version = platform.version()
            # Windows 11 version starts with "10.0.22000" or higher
            major, minor, build = map(int, version.split('.')[:3])
            return major == 10 and minor == 0 and build >= 22000
        except Exception:
            return False

    @staticmethod
    def get_system_theme() -> WindowsTheme:
        """Get current Windows system theme"""
        try:
            if not WindowsThemeDetector.is_windows_11():
                # Fallback for Windows 10 or earlier
                return WindowsTheme.LIGHT

            # Try to read Windows registry for theme preference
            import winreg

            try:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                ) as key:
                    # AppsUseLightTheme: 0 = dark, 1 = light
                    apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return WindowsTheme.LIGHT if apps_use_light_theme else WindowsTheme.DARK
            except (FileNotFoundError, OSError):
                # Fallback method if registry access fails
                return WindowsTheme.LIGHT

        except Exception as e:
            logger.warning(f"Failed to detect Windows theme: {e}")
            return WindowsTheme.UNKNOWN

    @staticmethod
    def get_system_colors() -> dict[str, str]:
        """Get Windows system colors"""
        try:
            if not WindowsThemeDetector.is_windows_11():
                return WindowsThemeDetector._get_fallback_colors()

            # Try to get accent color from Windows
            import winreg

            colors = {}
            try:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent"
                ) as key:
                    accent_color, _ = winreg.QueryValueEx(key, "AccentColorMenu")
                    # Convert Windows ABGR to hex RGB
                    r = (accent_color >> 16) & 0xFF
                    g = (accent_color >> 8) & 0xFF
                    b = accent_color & 0xFF
                    colors["accent"] = f"#{r:02x}{g:02x}{b:02x}"
            except (FileNotFoundError, OSError):
                colors["accent"] = "#0078D4"  # Windows default blue

            return colors

        except Exception as e:
            logger.warning(f"Failed to get Windows system colors: {e}")
            return WindowsThemeDetector._get_fallback_colors()

    @staticmethod
    def _get_fallback_colors() -> dict[str, str]:
        """Get fallback colors for non-Windows or error cases"""
        return {
            "accent": "#0078D4",  # Windows default blue
            "background": "#F3F3F3",
            "text": "#000000"
        }

    @staticmethod
    def get_display_scaling() -> float:
        """Get Windows display scaling factor"""
        try:
            import ctypes
            user32 = ctypes.windll.user32

            # Get monitor DPI
            hdc = user32.GetDC(0)
            if hdc:
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                user32.ReleaseDC(0, hdc)
                return dpi / 96.0  # 96 DPI is 100% scaling
            return 1.0
        except Exception:
            return 1.0

    @staticmethod
    def get_system_font_info() -> dict[str, Any]:
        """Get Windows system font information"""
        try:
            # Try to get Segoe UI Variable information
            return {
                "family": "Segoe UI Variable",
                "size": 14.0,
                "weight": "normal"
            }
        except Exception:
            return {
                "family": "Arial",
                "size": 14.0,
                "weight": "normal"
            }


class WindowsThemeProvider:
    """
    Windows 11 themed color provider for Flet applications

    Provides Windows 11 native color schemes and styling
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_theme: WindowsTheme | None = None
        self.system_colors: dict[str, str] = {}
        self.custom_color_schemes: dict[WindowsColorScheme, dict[str, str]] = {}

        # Initialize Windows color schemes
        self._init_color_schemes()

        # Detect and apply system theme
        self._detect_and_apply_system_theme()

    def _init_color_schemes(self):
        """Initialize Windows 11 color schemes"""

        # Light theme schemes
        self.custom_color_schemes[WindowsColorScheme.DEFAULT] = {
            "primary": "#0078D4",
            "secondary": "#106EBE",
            "tertiary": "#6B9BD1",
            "surface": "#F3F2F1",
            "background": "#FFFFFF",
            "error": "#C50F1F",
            "on_primary": "#FFFFFF",
            "on_secondary": "#FFFFFF",
            "on_surface": "#000000",
            "on_background": "#000000",
            "on_error": "#FFFFFF",
        }

        self.custom_color_schemes[WindowsColorScheme.BLUE] = {
            "primary": "#0078D4",
            "secondary": "#106EBE",
            "tertiary": "#6B9BD1",
            "surface": "#F3F2F1",
            "background": "#FFFFFF",
            "error": "#C50F1F",
            "on_primary": "#FFFFFF",
            "on_secondary": "#FFFFFF",
            "on_surface": "#000000",
            "on_background": "#000000",
            "on_error": "#FFFFFF",
        }

        self.custom_color_schemes[WindowsColorScheme.GREEN] = {
            "primary": "#107C10",
            "secondary": "#0E5E0E",
            "tertiary": "#4E8B4E",
            "surface": "#F3F2F1",
            "background": "#FFFFFF",
            "error": "#C50F1F",
            "on_primary": "#FFFFFF",
            "on_secondary": "#FFFFFF",
            "on_surface": "#000000",
            "on_background": "#000000",
            "on_error": "#FFFFFF",
        }

        # Dark theme schemes
        self.dark_color_schemes = {
            WindowsColorScheme.DEFAULT: {
                "primary": "#0078D4",
                "secondary": "#106EBE",
                "tertiary": "#4FC3F7",
                "surface": "#1E1E1E",
                "background": "#0C0C0C",
                "error": "#E74856",
                "on_primary": "#FFFFFF",
                "on_secondary": "#FFFFFF",
                "on_surface": "#FFFFFF",
                "on_background": "#FFFFFF",
                "on_error": "#FFFFFF",
            }
        }

    def _detect_and_apply_system_theme(self):
        """Detect and apply Windows system theme"""
        try:
            # Get system theme
            self.current_theme = WindowsThemeDetector.get_system_theme()
            self.system_colors = WindowsThemeDetector.get_system_colors()

            # Apply theme to Flet page
            self._apply_theme_to_page()

            logger.info(f"Applied Windows theme: {self.current_theme.value}")

        except Exception as e:
            logger.error(f"Failed to apply Windows theme: {e}")

    def _apply_theme_to_page(self):
        """Apply detected theme to Flet page"""
        if self.current_theme == WindowsTheme.DARK:
            self.page.theme_mode = ft.ThemeMode.DARK
            colors = self.dark_color_schemes.get(WindowsColorScheme.DEFAULT, {})
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            colors = self.custom_color_schemes.get(WindowsColorScheme.DEFAULT, {})

        # Override system colors with Windows accent color if available
        if "accent" in self.system_colors:
            colors["primary"] = self.system_colors["accent"]

        # Create custom theme
        self.page.theme = ft.Theme(
            color_scheme_seed=colors.get("primary", "#0078D4"),
            use_material3=True
        )

    def create_mica_effect(self, opacity: float = 0.8) -> ft.BoxDecoration:
        """Create a Windows 11 Mica-like effect"""
        if self.current_theme == WindowsTheme.DARK:
            # Dark Mica effect
            return ft.BoxDecoration(
                color=ft.Colors.with_opacity(opacity, "#202020"),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        ft.Colors.with_opacity(opacity, "#2C2C2C"),
                        ft.Colors.with_opacity(opacity * 0.7, "#1C1C1C"),
                    ]
                ),
                border_radius=8,
            )
        else:
            # Light Mica effect
            return ft.BoxDecoration(
                color=ft.Colors.with_opacity(opacity, "#F3F3F3"),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        ft.Colors.with_opacity(opacity, "#FFFFFF"),
                        ft.Colors.with_opacity(opacity * 0.8, "#F0F0F0"),
                    ]
                ),
                border_radius=8,
            )

    def create_acrylic_effect(self, blur_amount: int = 10) -> ft.BoxDecoration:
        """Create a Windows 11 Acrylic-like effect"""
        if self.current_theme == WindowsTheme.DARK:
            # Dark Acrylic effect
            return ft.BoxDecoration(
                color=ft.Colors.with_opacity(0.7, "#2C2C2C"),
                border=ft.border.all(1, ft.Colors.with_opacity(0.2, "#FFFFFF")),
                border_radius=8,
            )
        else:
            # Light Acrylic effect
            return ft.BoxDecoration(
                color=ft.Colors.with_opacity(0.5, "#FFFFFF"),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, "#000000")),
                border_radius=8,
            )

    def get_optimized_font_size(self, base_size: float) -> float:
        """Get font size optimized for Windows display scaling"""
        scaling = WindowsThemeDetector.get_display_scaling()
        return base_size * scaling

    def get_window_optimized_size(self, base_width: int, base_height: int) -> tuple[int, int]:
        """Get window size optimized for Windows display scaling"""
        scaling = WindowsThemeDetector.get_display_scaling()
        return int(base_width * scaling), int(base_height * scaling)

    def setup_window_for_windows_11(self, width: int = 1200, height: int = 800):
        """Setup window properties for Windows 11"""
        if not hasattr(self.page, 'window') or not self.page.window:
            return

        try:
            # Get optimized window size
            optimized_width, optimized_height = self.get_window_optimized_size(width, height)

            # Set window properties
            self.page.window.width = optimized_width
            self.page.window.height = optimized_height
            self.page.window.min_width = int(800 * scaling if (scaling := WindowsThemeDetector.get_display_scaling()) else 800)
            self.page.window.min_height = int(600 * scaling if scaling else 600)

            # Enable Windows 11 features if available
            if WindowsThemeDetector.is_windows_11():
                # Try to enable modern window styling
                self.page.window.title_bar_hidden = False
                self.page.window.title_bar_buttons_hidden = False

        except Exception as e:
            logger.warning(f"Failed to setup Windows 11 window properties: {e}")

    def create_windows_11_button_style(self, is_primary: bool = False) -> ft.ButtonStyle:
        """Create Windows 11 style button"""
        if self.current_theme == WindowsTheme.DARK:
            if is_primary:
                return ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY,
                    elevation=2,
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8)
                )
            else:
                return ft.ButtonStyle(
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
                    color=ft.Colors.ON_SURFACE,
                    elevation=0,
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)
                )
        else:
            if is_primary:
                return ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY,
                    elevation=1,
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8)
                )
            else:
                return ft.ButtonStyle(
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
                    color=ft.Colors.ON_SURFACE,
                    elevation=0,
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    overlay_color=ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE)
                )

    def enable_theme_change_monitoring(self):
        """Enable monitoring for Windows theme changes"""
        if not WindowsThemeDetector.is_windows_11():
            return

        # This would require a more sophisticated implementation
        # For now, just log that monitoring is requested
        logger.info("Windows theme change monitoring requested (implementation needed)")


def setup_windows_11_integration(page: ft.Page) -> WindowsThemeProvider | None:
    """
    Setup Windows 11 integration for the application

    Args:
        page: Flet page instance

    Returns:
        WindowsThemeProvider instance if on Windows, None otherwise
    """
    try:
        if platform.system() != "Windows":
            logger.info("Not running on Windows, skipping Windows 11 integration")
            return None

        if not WindowsThemeDetector.is_windows_11():
            logger.info("Not running on Windows 11, using standard theme integration")
            return None

        # Create Windows theme provider
        theme_provider = WindowsThemeProvider(page)

        # Setup window properties
        theme_provider.setup_window_for_windows_11()

        # Enable theme monitoring
        theme_provider.enable_theme_change_monitoring()

        logger.info("✅ Windows 11 integration initialized successfully")
        return theme_provider

    except Exception as e:
        logger.error(f"Failed to setup Windows 11 integration: {e}")
        return None


def get_windows_11_optimized_theme() -> ft.Theme:
    """
    Get a Windows 11 optimized theme

    Returns:
        Flet Theme optimized for Windows 11
    """
    try:
        if platform.system() == "Windows" and WindowsThemeDetector.is_windows_11():
            system_theme = WindowsThemeDetector.get_system_theme()
            colors = WindowsThemeDetector.get_system_colors()

            primary_color = colors.get("accent", "#0078D4")

            return ft.Theme(
                color_scheme_seed=primary_color,
                use_material3=True,
                theme_mode=ft.ThemeMode.DARK if system_theme == WindowsTheme.DARK else ft.ThemeMode.LIGHT
            )
        else:
            # Fallback theme for non-Windows systems
            return ft.Theme(
                color_scheme_seed="#0078D4",
                use_material3=True
            )

    except Exception:
        # Ultimate fallback
        return ft.Theme(
            color_scheme_seed="#0078D4",
            use_material3=True
        )
