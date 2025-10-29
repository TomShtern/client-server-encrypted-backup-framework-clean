"""
Display Scaling Utilities for Desktop Applications

This module provides display scaling and DPI awareness utilities for Windows 11
desktop applications, supporting 4K displays and multi-monitor setups.

Compatible with Flet 0.28.3 and Windows 11 desktop applications.
"""

import logging
import platform
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

import flet as ft

logger = logging.getLogger(__name__)


class DisplayScale(Enum):
    """Common display scale factors"""
    SCALE_100 = 1.0
    SCALE_125 = 1.25
    SCALE_150 = 1.5
    SCALE_175 = 1.75
    SCALE_200 = 2.0
    SCALE_225 = 2.25
    SCALE_250 = 2.5
    SCALE_300 = 3.0
    SCALE_350 = 3.5
    SCALE_400 = 4.0


@dataclass
class DisplayInfo:
    """Display monitor information"""
    index: int
    width: int
    height: int
    dpi: int
    scale_factor: float
    is_primary: bool
    device_name: str


@dataclass
class ScalingConfig:
    """Display scaling configuration"""
    scale_factor: float
    base_font_size: float
    scaled_font_size: float
    base_spacing: float
    scaled_spacing: float
    base_icon_size: float
    scaled_icon_size: float


class DisplayScaler:
    """
    Display scaling manager for desktop applications

    Features:
    - Automatic DPI detection
    - 4K display support
    - Multi-monitor support
    - Dynamic scaling adjustment
    - Font and UI element scaling
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.displays: list[DisplayInfo] = []
        self.primary_display: DisplayInfo | None = None
        self.current_config: ScalingConfig | None = None
        self.scaling_callbacks: list[Callable[[ScalingConfig], None]] = []

        # Initialize display detection
        self._detect_displays()

    def _detect_displays(self):
        """Detect connected displays and their properties"""
        try:
            if platform.system() == "Windows":
                self._detect_windows_displays()
            else:
                # Fallback for non-Windows systems
                self._detect_generic_displays()

            logger.info(f"Detected {len(self.displays)} display(s)")
            for display in self.displays:
                logger.debug(f"Display {display.index}: {display.width}x{display.height} @ {display.dpi} DPI (scale: {display.scale_factor})")

        except Exception as e:
            logger.error(f"Failed to detect displays: {e}")
            self._create_fallback_display()

    def _detect_windows_displays(self):
        """Detect displays on Windows using Windows API"""
        try:
            import win32api
            import win32con
            import win32gui
            import win32print

            # Enumerate connected monitors
            raw_monitors = win32api.EnumDisplayMonitors()
            monitors: list[DisplayInfo] = []

            for index, (handle, _hdc, _rect) in enumerate(raw_monitors):
                monitor_info = cast(dict[str, Any], cast(Any, win32api.GetMonitorInfo)(handle))
                device_name = monitor_info.get("Device", "")

                # Calculate DPI for this monitor
                create_dc_func = cast(Any, getattr(win32print, "CreateDC", None))
                if create_dc_func:
                    hdc_monitor = create_dc_func("DISPLAY", device_name, None, None)
                else:
                    hdc_monitor = cast(Any, win32gui.CreateDC)("DISPLAY", device_name, None)
                if hdc_monitor:
                    dpi_x = win32print.GetDeviceCaps(hdc_monitor, win32con.LOGPIXELSX)
                    delete_dc_func = getattr(win32print, "DeleteDC", None)
                    if delete_dc_func:
                        cast(Any, delete_dc_func)(hdc_monitor)
                    else:
                        win32gui.DeleteDC(hdc_monitor)
                else:
                    dpi_x = 96  # Default DPI fallback

                scale_factor = dpi_x / 96.0  # 96 DPI is 100% scaling

                # Monitor dimensions
                monitor_rect = monitor_info.get("Monitor", [0, 0, 800, 600])
                width = monitor_rect[2] - monitor_rect[0]
                height = monitor_rect[3] - monitor_rect[1]

                monitors.append(
                    DisplayInfo(
                        index=index,
                        width=width,
                        height=height,
                        dpi=dpi_x,
                        scale_factor=scale_factor,
                        is_primary=monitor_info.get("Flags", 0) & 1 != 0,
                        device_name=device_name or "Unknown"
                    )
                )

            self.displays = monitors

            # Find primary display
            for display in self.displays:
                if display.is_primary:
                    self.primary_display = display
                    break

        except ImportError:
            # pywin32 not available, fallback to basic detection
            logger.warning("pywin32 not available, using basic display detection")
            self._detect_windows_basic()
        except Exception as e:
            logger.error(f"Windows display detection failed: {e}")
            self._create_fallback_display()

    def _detect_windows_basic(self):
        """Basic Windows display detection without pywin32"""
        try:
            # Try to get system metrics
            import ctypes
            user32 = ctypes.windll.user32

            # Get screen dimensions
            width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
            height = user32.GetSystemMetrics(1)  # SM_CYSCREEN

            # Get DPI
            hdc = user32.GetDC(0)
            if hdc:
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                user32.ReleaseDC(0, hdc)
                scale_factor = dpi / 96.0
            else:
                dpi = 96
                scale_factor = 1.0

            # Create primary display info
            self.primary_display = DisplayInfo(
                index=0,
                width=width,
                height=height,
                dpi=dpi,
                scale_factor=scale_factor,
                is_primary=True,
                device_name="Primary Display"
            )

            self.displays = [self.primary_display]

        except Exception as e:
            logger.error(f"Basic Windows display detection failed: {e}")
            self._create_fallback_display()

    def _detect_generic_displays(self):
        """Generic display detection for non-Windows systems"""
        try:
            # Try to get display info from page
            if hasattr(self.page, 'window') and self.page.window:
                width = getattr(self.page.window, 'width', 1920)
                height = getattr(self.page.window, 'height', 1080)
            else:
                width, height = 1920, 1080

            # Assume standard DPI
            dpi = 96
            scale_factor = 1.0

            self.primary_display = DisplayInfo(
                index=0,
                width=width,
                height=height,
                dpi=dpi,
                scale_factor=scale_factor,
                is_primary=True,
                device_name="Generic Display"
            )

            self.displays = [self.primary_display]

        except Exception as e:
            logger.error(f"Generic display detection failed: {e}")
            self._create_fallback_display()

    def _create_fallback_display(self):
        """Create fallback display information"""
        self.primary_display = DisplayInfo(
            index=0,
            width=1920,
            height=1080,
            dpi=96,
            scale_factor=1.0,
            is_primary=True,
            device_name="Fallback Display"
        )
        self.displays = [self.primary_display]

    def get_optimal_scale_factor(self) -> float:
        """Get the optimal scale factor for the primary display"""
        if not self.primary_display:
            return 1.0

        scale = self.primary_display.scale_factor

        # Round to nearest standard scale factor
        standard_scales = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
        closest_scale = min(standard_scales, key=lambda x: abs(x - scale))

        # Only use standard scale if it's close enough (within 10%)
        if abs(scale - closest_scale) / scale < 0.1:
            return closest_scale
        else:
            return scale

    def create_scaling_config(
        self,
        base_font_size: float = 14.0,
        base_spacing: float = 8.0,
        base_icon_size: float = 24.0
    ) -> ScalingConfig:
        """Create scaling configuration for the current display"""
        scale_factor = self.get_optimal_scale_factor()

        config = ScalingConfig(
            scale_factor=scale_factor,
            base_font_size=base_font_size,
            scaled_font_size=base_font_size * scale_factor,
            base_spacing=base_spacing,
            scaled_spacing=base_spacing * scale_factor,
            base_icon_size=base_icon_size,
            scaled_icon_size=base_icon_size * scale_factor
        )

        self.current_config = config
        return config

    def apply_scaling_to_page(self, config: ScalingConfig | None = None):
        """Apply display scaling to the page"""
        if config is None:
            config = self.create_scaling_config()

        try:
            # Update page font settings
            if hasattr(self.page, 'font_family'):
                self.page.font_family = "Segoe UI Variable"

            # Apply scaling to window if available
            if hasattr(self.page, 'window') and self.page.window:
                base_width, base_height = 1200, 800
                scaled_width = int(base_width * config.scale_factor)
                scaled_height = int(base_height * config.scale_factor)

                self.page.window.width = scaled_width
                self.page.window.height = scaled_height
                self.page.window.min_width = int(800 * config.scale_factor)
                self.page.window.min_height = int(600 * config.scale_factor)

            logger.info(f"Applied display scaling: {config.scale_factor:.2f}x (font: {config.scaled_font_size:.1f}px)")

        except Exception as e:
            logger.error(f"Failed to apply scaling to page: {e}")

    def scale_font_size(self, base_size: float) -> float:
        """Scale a font size for the current display"""
        if not self.current_config:
            return base_size
        return base_size * self.current_config.scale_factor

    def scale_spacing(self, base_spacing: float) -> float:
        """Scale spacing for the current display"""
        if not self.current_config:
            return base_spacing
        return base_spacing * self.current_config.scale_factor

    def scale_icon_size(self, base_size: float) -> float:
        """Scale an icon size for the current display"""
        if not self.current_config:
            return base_size
        return base_size * self.current_config.scale_factor

    def scale_dimension(self, base_dimension: float) -> float:
        """Scale any dimension for the current display"""
        if not self.current_config:
            return base_dimension
        return base_dimension * self.current_config.scale_factor

    def create_responsive_padding(self, base_padding: ft.margin) -> ft.margin:
        """Create responsive padding for the current display"""
        if not self.current_config:
            return base_padding

        scale = self.current_config.scale_factor
        return ft.margin.only(
            left=base_padding.left * scale if base_padding.left else None,
            top=base_padding.top * scale if base_padding.top else None,
            right=base_padding.right * scale if base_padding.right else None,
            bottom=base_padding.bottom * scale if base_padding.bottom else None
        )

    def register_scaling_callback(self, callback: Callable[[ScalingConfig], None]):
        """Register a callback to be called when scaling changes"""
        self.scaling_callbacks.append(callback)

    def notify_scaling_change(self):
        """Notify all registered callbacks of scaling change"""
        if self.current_config:
            for callback in self.scaling_callbacks:
                try:
                    callback(self.current_config)
                except Exception as e:
                    logger.error(f"Error in scaling callback: {e}")

    def get_display_info_for_monitoring(self) -> dict[str, Any]:
        """Get display information for monitoring and diagnostics"""
        if not self.primary_display:
            return {}

        return {
            "total_displays": len(self.displays),
            "primary_display": {
                "resolution": f"{self.primary_display.width}x{self.primary_display.height}",
                "dpi": self.primary_display.dpi,
                "scale_factor": self.primary_display.scale_factor,
                "device_name": self.primary_display.device_name
            },
            "current_config": {
                "scale_factor": self.current_config.scale_factor if self.current_config else 1.0,
                "font_size": self.current_config.scaled_font_size if self.current_config else 14.0,
                "spacing": self.current_config.scaled_spacing if self.current_config else 8.0,
                "icon_size": self.current_config.scaled_icon_size if self.current_config else 24.0
            }
        }


def setup_display_scaling(page: ft.Page) -> DisplayScaler | None:
    """
    Setup display scaling for the application

    Args:
        page: Flet page instance

    Returns:
        DisplayScaler instance if successful, None otherwise
    """
    try:
        scaler = DisplayScaler(page)
        config = scaler.create_scaling_config()
        scaler.apply_scaling_to_page(config)

        logger.info("✅ Display scaling initialized successfully")
        return scaler

    except Exception as e:
        logger.error(f"Failed to setup display scaling: {e}")
        return None


def create_responsive_control(
    base_control: ft.Control,
    scaler: DisplayScaler,
    scale_properties: list[str] | None = None
) -> ft.Control:
    """
    Create a responsive control that adapts to display scaling

    Args:
        base_control: Base Flet control to make responsive
        scaler: DisplayScaler instance
        scale_properties: List of properties to scale (width, height, font_size, etc.)

    Returns:
        Responsive control
    """
    if scale_properties is None:
        scale_properties = ["width", "height", "font_size", "size", "spacing"]

    try:
        # Apply scaling to specified properties
        for prop in scale_properties:
            if hasattr(base_control, prop):
                current_value = getattr(base_control, prop)
                if isinstance(current_value, (int, float)):
                    scaled_value = scaler.scale_dimension(current_value)
                    setattr(base_control, prop, scaled_value)

        return base_control

    except Exception as e:
        logger.error(f"Failed to create responsive control: {e}")
        return base_control


def get_optimized_dimensions_for_display(
    scaler: DisplayScaler,
    base_width: int,
    base_height: int
) -> tuple[int, int]:
    """
    Get optimized dimensions for the current display

    Args:
        scaler: DisplayScaler instance
        base_width: Base width
        base_height: Base height

    Returns:
        Tuple of (scaled_width, scaled_height)
    """
    if not scaler.current_config:
        return base_width, base_height

    scale = scaler.current_config.scale_factor
    return int(base_width * scale), int(base_height * scale)
