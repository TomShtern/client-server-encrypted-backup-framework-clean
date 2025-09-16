#!/usr/bin/env python3
"""
Enhanced Settings View for FletV2
Optimized responsive design with comprehensive server bridge integration, Material Design 3 styling, and enhanced interactivity.
"""

import flet as ft
from typing import Optional
import asyncio
import contextlib
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from views.settings_state import EnhancedSettingsState
from utils.ui_components import (
    create_modern_card,
    build_settings_field,
    create_status_header,
)
from views.settings_config import SETTINGS_CONFIG
from utils.action_buttons import create_enhanced_action_buttons
from utils.validators import (
    VALIDATORS,
    validate_port,
    validate_max_clients,
    validate_monitoring_interval,
    validate_file_size,
    validate_timeout,
)

# UTF-8 support
import sys
import os
# Add parent directory to path to access Shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with contextlib.suppress(ImportError):
    import Shared.utils.utf8_solution
with contextlib.suppress(ImportError):
    from utils import utf8_patch

logger = get_logger(__name__)




# Validators imported from utils.validators













# Settings configuration now imported from views.settings_config

def create_settings_section(section_name: str, state: "EnhancedSettingsState") -> ft.Control:
    """Create a settings section UI from SETTINGS_CONFIG.

    Builds a modern card with configured subsections and fields using shared UI components.
    """
    if section_name not in SETTINGS_CONFIG:
        return ft.Text(f"Unknown settings section: {section_name}", color=ft.Colors.ERROR)

    config = SETTINGS_CONFIG[section_name]

    subsection_containers: list[ft.Control] = []

    for subsection in config.get("subsections", []):
        fields: list[ft.Control] = []

        for field_config in subsection.get("fields", []):
            # Annotate section for the builder
            fc = dict(field_config)
            fc["section"] = section_name
            control = build_settings_field(fc, state)

            if control is not None:
                fields.append(
                    ft.ResponsiveRow([
                        ft.Column([control], col={"sm": 12, "md": 12}),
                    ], spacing=10)
                )

        # Create subsection container
        subsection_container = ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([
                    ft.Text(subsection.get("title", ""), size=16, weight=ft.FontWeight.W_600, color=subsection.get("color", ft.Colors.PRIMARY)),
                    *fields
                ], spacing=10, col={"sm": 12, "md": 12}),
            ], spacing=10),
            padding=ft.Padding(15, 10, 15, 10),
            bgcolor=ft.Colors.with_opacity(0.05, subsection.get("color", ft.Colors.PRIMARY)),
            border_radius=8,
        )
        subsection_containers.append(subsection_container)

    # Return modern card with all subsections
    return create_modern_card(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(config.get("icon"), size=24, color=ft.Colors.PRIMARY),
                ft.Text(config.get("title", section_name.title()), size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            *subsection_containers
        ], spacing=20),
        elevation="elevated",
        hover_effect=True,
        padding=20,
        return_type="container"
    )



def create_settings_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    state_manager: StateManager
) -> ft.Control:
    """
    Create enhanced settings view with comprehensive server bridge integration and Material Design 3 styling.
    """
    logger.info("Creating enhanced settings view with server bridge integration")

    # Initialize enhanced state management
    settings_state = EnhancedSettingsState(page, server_bridge, state_manager)

    # Status display helper
    status_container, update_status_display = create_status_header(server_bridge, settings_state)

    # Subscribe to state changes for reactive status updates
    # Defer subscription setup until view is added to page to prevent "Control must be added to page first" error
    # State-managed subscriptions
    def on_loading_change(loading_states, old_states):
        if loading_states.get("settings_save") or loading_states.get("settings_load"):
            update_status_display()
    settings_state.init_subscriptions(state_manager, on_loading_change)

    # Enhanced action buttons with responsive layout
    action_buttons = create_enhanced_action_buttons(settings_state)

    # Create enhanced tabs with responsive content
    enhanced_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color=ft.Colors.PRIMARY,
        label_color=ft.Colors.PRIMARY,
        unselected_label_color=ft.Colors.ON_SURFACE_VARIANT,
        tabs=[
            ft.Tab(
                text="Server",
                icon=ft.Icons.DNS,
                content=ft.Container(
                    content=ft.Column([
                        create_settings_section("server", settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Interface",
                icon=ft.Icons.PALETTE,
                content=ft.Container(
                    content=ft.Column([
                        create_settings_section("gui", settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Monitoring",
                icon=ft.Icons.MONITOR_HEART,
                content=ft.Container(
                    content=ft.Column([
                        create_settings_section("monitoring", settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Logging",
                icon=ft.Icons.ARTICLE,
                content=ft.Container(
                    content=ft.Column([
                        create_settings_section("logging", settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Security",
                icon=ft.Icons.SECURITY,
                content=ft.Container(
                    content=ft.Column([
                        create_settings_section("security", settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
            ft.Tab(
                text="Backup",
                icon=ft.Icons.BACKUP,
                content=ft.Container(
                    content=ft.Column([
                        create_settings_section("backup", settings_state)
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=10,
                    expand=True
                )
            ),
        ],
        expand=True,
        scrollable=True,
    )

    # Build main view with responsive layout and enhanced Material Design 3 styling
    main_view = ft.Column([
        # Enhanced header with responsive status display
        ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, size=28, color=ft.Colors.PRIMARY),
                        ft.Text("Settings", size=28, weight=ft.FontWeight.BOLD),
                    ], spacing=10)
                ], col={"sm": 12, "md": 6}),
                ft.Column([
                    status_container
                ], col={"sm": 12, "md": 6}, alignment=ft.MainAxisAlignment.END),
            ]),
            padding=ft.Padding(20, 20, 20, 10),
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.PRIMARY),
        ),
        ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

        # Enhanced action buttons with responsive layout
        ft.Container(
            content=action_buttons,
            padding=ft.Padding(20, 10, 20, 10),
        ),

        # Enhanced tabs with responsive content
        ft.Container(
            content=enhanced_tabs,
            expand=True,
            padding=ft.Padding(10, 0, 10, 10),
        ),

    ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

    # Load settings asynchronously with enhanced error handling
    async def load_settings_with_status():
        try:
            success = await settings_state.load_settings_async()
            update_status_display()
            if success:
                logger.info("Settings loaded successfully")
            else:
                logger.warning("Settings load completed with issues")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            if state_manager:
                state_manager.add_notification("Failed to load settings", "error")

    # Modified return to make dispose accessible
    main_view.dispose = settings_state.dispose

    # Run setup after view is constructed
    page.run_task(load_settings_with_status)

    # Subscriptions are initialized via settings_state.init_subscriptions above

    return main_view
