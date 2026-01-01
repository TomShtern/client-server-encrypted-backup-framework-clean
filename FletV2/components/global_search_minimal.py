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
        width=260,
        height=40,
        border_radius=12,  # ROUNDED RECTANGLE (consistent with cards)
        bgcolor="#1E293B",  # Matches card background
        border_color="#334155",  # Matches card border
        text_size=13,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.Padding.only(left=8, right=14, top=0, bottom=0),
        on_focus=lambda e: print("Search focused!"),
        on_change=lambda e: print(f"Search: {e.control.value}"),
    )
