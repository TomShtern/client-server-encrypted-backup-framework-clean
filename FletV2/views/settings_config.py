#!/usr/bin/env python3
"""
Configuration for Settings sections used to build the UI dynamically.
Separated from views/settings.py to avoid circular imports.
"""

import flet as ft

SETTINGS_CONFIG = {
    "server": {
        "title": "Server Configuration",
        "icon": ft.Icons.DNS,
        "subsections": [
            {
                "title": "Network Settings",
                "color": ft.Colors.PRIMARY,
                "fields": [
                    {"type": "text", "key": "port", "label": "Server Port", "default": 1256, "validator": "validate_port", "data_type": int, "width": 200, "keyboard": ft.KeyboardType.NUMBER, "icon": ft.Icons.ROUTER},
                    {"type": "text", "key": "host", "label": "Server Host", "default": "127.0.0.1", "width": 300, "icon": ft.Icons.COMPUTER},
                ]
            },
            {
                "title": "Client Management",
                "color": ft.Colors.SECONDARY,
                "fields": [
                    {"type": "text", "key": "max_clients", "label": "Maximum Clients", "default": 50, "validator": "validate_max_clients", "data_type": int, "width": 200, "keyboard": ft.KeyboardType.NUMBER, "icon": ft.Icons.PEOPLE},
                    {"type": "text", "key": "timeout", "label": "Connection Timeout", "default": 30, "validator": "validate_timeout", "data_type": int, "width": 200, "keyboard": ft.KeyboardType.NUMBER, "suffix": "seconds"},
                ]
            },
            {
                "title": "Performance Settings",
                "color": ft.Colors.TERTIARY,
                "fields": [
                    {"type": "text", "key": "buffer_size", "label": "Buffer Size", "default": 4096, "validator": "validate_file_size", "data_type": int, "width": 200, "keyboard": ft.KeyboardType.NUMBER, "suffix": "bytes"},
                    {"type": "dropdown", "key": "log_level", "label": "Log Level", "default": "INFO", "options": [("DEBUG", "Debug - Detailed information"), ("INFO", "Info - General information"), ("WARNING", "Warning - Warning messages"), ("ERROR", "Error - Error messages only")], "width": 250},
                ]
            },
            {
                "title": "SSL/TLS Security",
                "color": ft.Colors.ERROR,
                "fields": [
                    {"type": "switch", "key": "enable_ssl", "label": "Enable SSL/TLS", "default": False},
                    {"type": "text", "key": "ssl_cert_path", "label": "SSL Certificate Path", "default": "", "width": 400, "icon": ft.Icons.SECURITY},
                    {"type": "text", "key": "ssl_key_path", "label": "SSL Private Key Path", "default": "", "width": 400, "icon": ft.Icons.KEY},
                ]
            }
        ]
    },
    "gui": {
        "title": "GUI Configuration",
        "icon": ft.Icons.PALETTE,
        "subsections": [
            {
                "title": "Appearance",
                "color": ft.Colors.PRIMARY,
                "fields": [
                    {"type": "dropdown", "key": "theme_mode", "label": "Theme Mode", "default": "system", "options": [("light", "Light Theme"), ("dark", "Dark Theme"), ("system", "System Default")], "width": 200},
                    {"type": "dropdown", "key": "color_scheme", "label": "Color Scheme", "default": "blue", "options": [("blue", "Blue"), ("green", "Green"), ("purple", "Purple"), ("red", "Red")], "width": 200},
                ]
            },
            {
                "title": "Layout",
                "color": ft.Colors.SECONDARY,
                "fields": [
                    {"type": "switch", "key": "auto_resize", "label": "Auto Resize Window", "default": True},
                    {"type": "switch", "key": "always_on_top", "label": "Always on Top", "default": False},
                    {"type": "text", "key": "window_width", "label": "Window Width", "default": 1200, "data_type": int, "width": 150, "keyboard": ft.KeyboardType.NUMBER, "suffix": "px"},
                    {"type": "text", "key": "window_height", "label": "Window Height", "default": 800, "data_type": int, "width": 150, "keyboard": ft.KeyboardType.NUMBER, "suffix": "px"},
                ]
            }
        ]
    },
    "monitoring": {
        "title": "Monitoring Configuration",
        "icon": ft.Icons.MONITOR,
        "subsections": [
            {
                "title": "System Monitoring",
                "color": ft.Colors.PRIMARY,
                "fields": [
                    {"type": "switch", "key": "enabled", "label": "Enable Monitoring", "default": True},
                    {"type": "slider", "key": "refresh_interval", "label": "Refresh Interval", "default": 5.0, "min": 1.0, "max": 60.0, "divisions": 59, "suffix": "s"},
                    {"type": "slider", "key": "cpu_threshold", "label": "CPU Alert Threshold", "default": 80.0, "min": 0.0, "max": 100.0, "divisions": 100, "suffix": "%"},
                    {"type": "slider", "key": "memory_threshold", "label": "Memory Alert Threshold", "default": 85.0, "min": 0.0, "max": 100.0, "divisions": 100, "suffix": "%"},
                ]
            }
        ]
    },
    "logging": {
        "title": "Logging Configuration",
        "icon": ft.Icons.DESCRIPTION,
        "subsections": [
            {
                "title": "Log Settings",
                "color": ft.Colors.PRIMARY,
                "fields": [
                    {"type": "switch", "key": "enabled", "label": "Enable Logging", "default": True},
                    {"type": "dropdown", "key": "level", "label": "Log Level", "default": "INFO", "options": [("DEBUG", "Debug"), ("INFO", "Info"), ("WARNING", "Warning"), ("ERROR", "Error")], "width": 200},
                    {"type": "text", "key": "file_path", "label": "Log File Path", "default": "logs/server.log", "width": 400, "icon": ft.Icons.FOLDER},
                    {"type": "text", "key": "max_size", "label": "Max File Size", "default": "10MB", "width": 150, "suffix": "MB"},
                ]
            }
        ]
    },
    "security": {
        "title": "Security Configuration",
        "icon": ft.Icons.SECURITY,
        "subsections": [
            {
                "title": "Authentication",
                "color": ft.Colors.PRIMARY,
                "fields": [
                    {"type": "switch", "key": "require_auth", "label": "Require Authentication", "default": False},
                    {"type": "text", "key": "api_key", "label": "API Key", "default": "", "width": 300, "icon": ft.Icons.KEY},
                ]
            }
        ]
    },
    "backup": {
        "title": "Backup Configuration",
        "icon": ft.Icons.BACKUP,
        "subsections": [
            {
                "title": "Backup Settings",
                "color": ft.Colors.PRIMARY,
                "fields": [
                    {"type": "switch", "key": "auto_backup", "label": "Auto Backup", "default": True},
                    {"type": "text", "key": "backup_path", "label": "Backup Directory", "default": "backups/", "width": 400, "icon": ft.Icons.FOLDER},
                    {"type": "text", "key": "retention_days", "label": "Retention Days", "default": 30, "data_type": int, "width": 150, "keyboard": ft.KeyboardType.NUMBER, "suffix": "days"},
                ]
            }
        ]
    }
}
