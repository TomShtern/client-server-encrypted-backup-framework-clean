"""Ultra-minimal database view stub for testing browser crash issue."""

from typing import Any

import flet as ft


def create_database_view(server_bridge: Any, page: ft.Page, state_manager: Any = None) -> tuple:
    """Absolute minimal database view - just text to test if complexity is the issue."""

    # Create the simplest possible container
    content = ft.Container(
        content=ft.Column([
            ft.Text("Database View - Minimal Test", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("If you can see this, the browser doesn't crash with minimal content."),
            ft.Text("This proves the issue is content complexity, not navigation."),
        ], spacing=10),
        padding=20,
    )

    def dispose() -> None:
        """No resources to clean up."""
        pass

    async def setup() -> None:
        """No setup needed."""
        pass

    return content, dispose, setup
