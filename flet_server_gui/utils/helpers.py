"""
Purpose: General utility functions
Logic: Data processing, formatting, validation utilities
No UI: Pure utility functions only
"""

#!/usr/bin/env python3
"""
General Utility Functions
Provides helper functions for data processing, formatting, validation, and responsive design.
"""

import flet as ft
from typing import Optional, Dict, Any, List, Union
import os
import json
import re
from datetime import datetime, timedelta
import hashlib


# ============================================================================
# DATA PROCESSING UTILITIES
# ============================================================================

def format_bytes(bytes_value: int, decimal_places: int = 2) -> str:
    """Format bytes to human-readable format."""
    if bytes_value == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(bytes_value)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.{decimal_places}f} {size_names[i]}"


def format_time_ago(timestamp: Union[str, datetime]) -> str:
    """Format timestamp to relative time (e.g., '2 minutes ago')."""
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return "Unknown"
    else:
        dt = timestamp
    
    now = datetime.now()
    diff = now - dt.replace(tzinfo=None)
    
    if diff.total_seconds() < 60:
        return "Just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    # Remove invalid characters for filenames
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    return sanitized


def generate_file_hash(filepath: str, algorithm: str = 'sha256') -> str:
    """Generate hash of file content."""
    hash_func = getattr(hashlib, algorithm)()
    
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception:
        return ""


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_ip(ip: str) -> bool:
    """Validate IP address format."""
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None


def is_valid_port(port: Union[str, int]) -> bool:
    """Validate port number."""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


# ============================================================================
# STRING AND TEXT UTILITIES
# ============================================================================

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Return singular or plural form based on count."""
    if plural is None:
        plural = f"{singular}s"
    return singular if count == 1 else plural


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', s1).lower()


# ============================================================================
# JSON AND SERIALIZATION UTILITIES
# ============================================================================

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback."""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Safely serialize object to JSON string."""
    try:
        return json.dumps(obj, **kwargs)
    except (TypeError, ValueError):
        return "{}"


# ============================================================================
# FILE AND PATH UTILITIES
# ============================================================================

def ensure_directory_exists(path: str) -> bool:
    """Ensure directory exists, creating it if necessary."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return os.path.splitext(filename)[1].lower()


def is_file_type(filename: str, extensions: List[str]) -> bool:
    """Check if file has one of the specified extensions."""
    ext = get_file_extension(filename)
    return ext in [e.lower() for e in extensions]


# ============================================================================
# RESPONSIVE DESIGN UTILITIES (consolidated in layouts/responsive.py)
# ============================================================================

def get_breakpoint(width: float) -> str:
    """Get breakpoint name based on screen width."""
    if width < 576:
        return "xs"  # Extra small devices (phones)
    elif width < 768:
        return "sm"  # Small devices (tablets)
    elif width < 992:
        return "md"  # Medium devices (desktops)
    elif width < 1200:
        return "lg"  # Large devices (large desktops)
    else:
        return "xl"  # Extra large devices


def is_mobile(width: float) -> bool:
    """Check if screen width indicates mobile device."""
    return width < 768


def get_responsive_spacing(width: float) -> int:
    """Get responsive spacing based on screen width."""
    if width < 576:
        return 8    # xs
    elif width < 768:
        return 12   # sm
    elif width < 992:
        return 16   # md
    else:
        return 20   # lg/xl


def get_responsive_padding(width: float) -> ft.Padding:
    """Get responsive padding based on screen width."""
    padding = get_responsive_spacing(width)
    return ft.Padding(padding, padding, padding, padding)


def get_responsive_font_scale(width: float) -> float:
    """Get responsive font scale factor based on screen width."""
    if width < 576:
        return 0.85   # xs
    elif width < 768:
        return 0.92   # sm
    elif width < 992:
        return 1.0    # md (base)
    elif width < 1200:
        return 1.08   # lg
    else:
        return 1.15   # xl


# ============================================================================
# THEME UTILITIES (from utils/theme_utils.py)
# ============================================================================

# Cache for theme tokens to avoid repeated imports
_cached_tokens = None


def get_theme_tokens() -> Dict[str, str]:
    """Get theme tokens with caching for performance."""
    global _cached_tokens
    if _cached_tokens is not None:
        return _cached_tokens

    try:
        from flet_server_gui.managers.theme_manager import TOKENS
        _cached_tokens = TOKENS
        return TOKENS
    except ImportError:
        return {
            "primary_gradient": ["#A8CBF3", "#7C5CD9"],
            "primary": "#7C5CD9",
            "on_primary": "#FFFFFF",
            "secondary": "#FFA500",  # Pure orange as requested
            "on_secondary": "#000000",
            "tertiary": "#AB6DA4",
            "on_tertiary": "#FFFFFF",
            "container": "#38A298",
            "on_container": "#FFFFFF",
            "surface": "#F6F8FB",
            "surface_variant": "#E7EDF7",
            "surface_dark": "#0F1720",
            "background": "#FFFFFF",
            "on_background": "#000000",
            "outline": "#666666",
            "error": "#B00020",
            "on_error": "#FFFFFF",
        }


def get_theme_color(color_name: str, default: str = "#000000") -> str:
    """Get a specific theme color by name."""
    tokens = get_theme_tokens()
    return tokens.get(color_name, default)


def get_primary_color() -> str:
    """Get the primary color."""
    return get_theme_color("primary", "#7C5CD9")


def get_secondary_color() -> str:
    """Get the secondary color."""
    return get_theme_color("secondary", "#FFA500")


def get_tertiary_color() -> str:
    """Get the tertiary color."""
    return get_theme_color("tertiary", "#AB6DA4")


def get_container_color() -> str:
    """Get the container color."""
    return get_theme_color("container", "#38A298")


def get_gradient_colors() -> list:
    """Get the primary gradient colors."""
    tokens = get_theme_tokens()
    return tokens.get("primary_gradient", ["#A8CBF3", "#7C5CD9"])


def get_linear_gradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, stops=None) -> ft.LinearGradient:
    """Create a linear gradient using theme colors."""
    # Use proper Flet theming - simple gradient with theme colors
    colors = get_gradient_colors()
    return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)


def get_gradient_button_style() -> Dict[str, Any]:
    """Get style dictionary for gradient buttons."""
    return {
        "gradient": get_linear_gradient(),
        "border_radius": ft.border_radius.all(12)
    }


def apply_theme_to_component(component: ft.Control, page: ft.Page) -> None:
    """Apply theme colors to a component based on its type and purpose."""
    # This function can be extended to automatically style components
    # based on theme tokens
    pass


def create_themed_button(text: str, icon=None, button_type: str = "filled", **kwargs) -> ft.Control:
    """Create a themed button using the appropriate theme colors."""
    # Use proper Flet theming - standard buttons with theme colors
    
    # Fallback to standard buttons
    if button_type == "filled":
        return ft.FilledButton(text, icon=icon, **kwargs)
    elif button_type == "outlined":
        return ft.OutlinedButton(text, icon=icon, **kwargs)
    else:
        return ft.TextButton(text, icon=icon, **kwargs)