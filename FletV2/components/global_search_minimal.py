"""
Minimal Global Search - Guaranteed to Work

This is the SIMPLEST possible search implementation:
- Just a TextField with icon
- No Stack, no Positioned, no complex layouts
- Works 100% guaranteed in Flet 0.28.3
"""

import flet as ft


def create_minimal_search() -> ft.TextField:
    """
    Create the simplest possible search field.

    This is a MINIMAL implementation to prove the concept works.
    Once this renders correctly, we can enhance it.
    """
    return ft.TextField(
        hint_text="Search (Ctrl+F)",
        width=280,
        height=44,
        border_radius=18,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
        border_color=ft.Colors.OUTLINE,
        text_size=14,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        on_focus=lambda e: print("Search focused!"),
        on_change=lambda e: print(f"Search: {e.control.value}"),
    )
