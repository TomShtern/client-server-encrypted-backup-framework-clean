#!/usr/bin/env python3
"""
Shared Utilities
Common utility functions used across multiple components.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional


class FormatUtils:
    """Utility functions for data formatting"""
    
    @staticmethod
    def format_file_size(size: int) -> str:
        """Format file size to human-readable format"""
        if not size or size == 0:
            return "0 B"
        
        # Convert bytes to appropriate unit
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    @staticmethod
    def format_time_ago(date_str: str) -> str:
        """Format date to human-readable time ago format"""
        try:
            if not date_str or date_str == "Unknown":
                return "Unknown"
            
            # Parse the datetime string
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Calculate time difference
            diff = now - date_obj.replace(tzinfo=None)
            
            if diff.days > 7:
                return date_obj.strftime("%Y-%m-%d")
            elif diff.days > 0:
                return f"{diff.days}d ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours}h ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes}m ago"
            else:
                return "Just now"
                
        except (ValueError, AttributeError):
            return "Unknown"
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension in lowercase"""
        return filename.split('.')[-1].lower() if '.' in filename else ''


class IconUtils:
    """Utility functions for icons and visual elements"""
    
    @staticmethod
    def get_status_icon(status: str) -> Dict[str, Any]:
        """Get icon and color for status"""
        status_map = {
            "connected": {"icon": ft.Icons.WIFI, "color": ft.Colors.GREEN_600},
            "registered": {"icon": ft.Icons.VERIFIED_USER, "color": ft.Colors.BLUE_600},
            "offline": {"icon": ft.Icons.WIFI_OFF, "color": ft.Colors.ORANGE_600},
            "error": {"icon": ft.Icons.ERROR, "color": ft.Colors.RED_600},
        }
        return status_map.get(status.lower(), {"icon": ft.Icons.HELP, "color": ft.Colors.GREY_600})
    
    @staticmethod
    def get_file_type_icon(filename: str) -> Dict[str, Any]:
        """Get icon and info for file type"""
        extension = FormatUtils.get_file_extension(filename)
        
        type_mappings = {
            'txt': {'icon': '📄', 'name': 'Text', 'color': ft.Colors.BLUE_100},
            'pdf': {'icon': '📕', 'name': 'PDF', 'color': ft.Colors.RED_100},
            'doc': {'icon': '📘', 'name': 'Word', 'color': ft.Colors.BLUE_200},
            'docx': {'icon': '📘', 'name': 'Word', 'color': ft.Colors.BLUE_200},
            'xls': {'icon': '📗', 'name': 'Excel', 'color': ft.Colors.GREEN_200},
            'xlsx': {'icon': '📗', 'name': 'Excel', 'color': ft.Colors.GREEN_200},
            'ppt': {'icon': '📙', 'name': 'PowerPoint', 'color': ft.Colors.ORANGE_200},
            'pptx': {'icon': '📙', 'name': 'PowerPoint', 'color': ft.Colors.ORANGE_200},
            'jpg': {'icon': '🖼️', 'name': 'Image', 'color': ft.Colors.PURPLE_100},
            'jpeg': {'icon': '🖼️', 'name': 'Image', 'color': ft.Colors.PURPLE_100},
            'png': {'icon': '🖼️', 'name': 'Image', 'color': ft.Colors.PURPLE_100},
            'gif': {'icon': '🖼️', 'name': 'Image', 'color': ft.Colors.PURPLE_100},
            'mp4': {'icon': '🎬', 'name': 'Video', 'color': ft.Colors.TEAL_100},
            'avi': {'icon': '🎬', 'name': 'Video', 'color': ft.Colors.TEAL_100},
            'mp3': {'icon': '🎵', 'name': 'Audio', 'color': ft.Colors.PINK_100},
            'wav': {'icon': '🎵', 'name': 'Audio', 'color': ft.Colors.PINK_100},
            'zip': {'icon': '🗜️', 'name': 'Archive', 'color': ft.Colors.GREY_200},
            'rar': {'icon': '🗜️', 'name': 'Archive', 'color': ft.Colors.GREY_200},
            '7z': {'icon': '🗜️', 'name': 'Archive', 'color': ft.Colors.GREY_200},
        }
        
        return type_mappings.get(extension, {'icon': '📄', 'name': 'File', 'color': ft.Colors.GREY_100})


class UIUtils:
    """Utility functions for UI components"""
    
    @staticmethod
    def create_status_chip(status: str) -> ft.Container:
        """Create a status display chip with appropriate styling"""
        status_colors = {
            "connected": ft.Colors.GREEN_600,
            "registered": ft.Colors.BLUE_600,
            "offline": ft.Colors.ORANGE_600,
        }
        
        color = status_colors.get(status.lower(), ft.Colors.GREY_600)
        
        return ft.Container(
            content=ft.Text(
                status.title(),
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            bgcolor=color,
            padding=ft.Padding(4, 2, 4, 2),
            border_radius=4
        )
    
    @staticmethod
    def create_file_type_chip(filename: str) -> ft.Container:
        """Create a file type display chip"""
        file_info = IconUtils.get_file_type_icon(filename)
        
        return ft.Container(
            content=ft.Row([
                ft.Text(file_info['icon'], size=16),
                ft.Text(file_info['name'], size=10, weight=ft.FontWeight.BOLD)
            ], spacing=4, tight=True),
            bgcolor=file_info['color'],
            padding=ft.Padding(4, 2, 4, 2),
            border_radius=4
        )
    
    @staticmethod
    def create_loading_spinner(message: str = "Loading...") -> ft.Container:
        """Create a loading spinner with message"""
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text(message, size=14)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            padding=20
        )
    
    @staticmethod
    def create_empty_state(title: str, description: str, icon: str = ft.Icons.INBOX) -> ft.Container:
        """Create an empty state display"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=64, color=ft.Colors.GREY_400),
                ft.Text(title, weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.GREY_600),
                ft.Text(description, size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            padding=40
        )
    
    @staticmethod
    def create_stats_card(title: str, value: str, subtitle: str = "", 
                         color: str = ft.Colors.PRIMARY) -> ft.Container:
        """Create a statistics card"""
        content = [
            ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=color),
        ]
        
        if subtitle:
            content.append(ft.Text(subtitle, size=10, color=ft.Colors.ON_SURFACE_VARIANT))
        
        return ft.Container(
            content=ft.Column(content, spacing=2, tight=True),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=12,
            border_radius=8,
            width=120
        )


class ValidationUtils:
    """Utility functions for data validation"""
    
    @staticmethod
    def is_valid_filename(filename: str) -> bool:
        """Check if filename is valid"""
        if not filename or len(filename.strip()) == 0:
            return False
        
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        return not any(char in filename for char in invalid_chars)
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing invalid characters"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        sanitized = filename
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        return sanitized.strip()


class AsyncUtils:
    """Utility functions for async operations"""
    
    @staticmethod
    async def run_with_retry(coro, max_retries: int = 3, delay: float = 1.0):
        """Run async operation with retry logic"""
        import asyncio
        
        for attempt in range(max_retries):
            try:
                return await coro
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 30.0):
        """Run async operation with timeout"""
        import asyncio
        
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")


class DataUtils:
    """Utility functions for data manipulation"""
    
    @staticmethod
    def group_by_key(items: List[Dict], key: str) -> Dict[str, List[Dict]]:
        """Group items by a specific key"""
        groups = {}
        for item in items:
            group_key = item.get(key, 'unknown')
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
        return groups
    
    @staticmethod
    def filter_by_keys(items: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter items by multiple key-value pairs"""
        filtered = []
        for item in items:
            match = True
            for key, value in filters.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                filtered.append(item)
        return filtered
    
    @staticmethod
    def sort_by_key(items: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """Sort items by a specific key"""
        return sorted(items, key=lambda x: x.get(key, ''), reverse=reverse)