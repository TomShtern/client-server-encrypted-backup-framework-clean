"""
Neomorphic design utilities for Flet applications
Flet 0.28.3 Compatible
"""

import flet as ft


def _resolve_theme_colors(page) -> tuple[str, str]:
    """Return light/dark colors derived from the page theme with safe fallbacks."""
    theme = getattr(page, "theme", None) if page else None
    scheme = getattr(theme, "color_scheme", None) if theme else None

    surface = getattr(scheme, "surface", None) if scheme else None
    shadow = getattr(scheme, "shadow", None) if scheme else None

    light_color = surface or ft.Colors.WHITE
    dark_color = shadow or ft.Colors.BLACK
    return light_color, dark_color


class NeomorphicShadows:
    """Professional neomorphic shadow system with elevation levels"""

    @staticmethod
    def get_card_shadows(elevation: str = "medium", page=None) -> list[ft.BoxShadow]:
        """
        Get neomorphic shadows for cards based on elevation level.
        Neomorphism uses dual shadows to create depth perception.
        """
        light_color, dark_color = _resolve_theme_colors(page)

        if elevation == "low":
            return [
                # Light shadow (top-left) - simulates light source
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, light_color),
                    offset=ft.Offset(-2, -2),
                ),
                # Dark shadow (bottom-right) - creates depth
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.15, dark_color),
                    offset=ft.Offset(2, 2),
                ),
            ]
        elif elevation == "medium":
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.10, light_color),
                    offset=ft.Offset(-3, -3),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.20, dark_color),
                    offset=ft.Offset(3, 3),
                ),
            ]
        else:  # high
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.12, light_color),
                    offset=ft.Offset(-4, -4),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.25, dark_color),
                    offset=ft.Offset(4, 4),
                ),
            ]

    @staticmethod
    def get_hover_shadows(page=None) -> list[ft.BoxShadow]:
        """Enhanced shadows for hover state - more pronounced elevation"""
        light_color, dark_color = _resolve_theme_colors(page)

        return [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=18,
                color=ft.Colors.with_opacity(0.12, light_color),
                offset=ft.Offset(-4, -4),
            ),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=18,
                color=ft.Colors.with_opacity(0.22, dark_color),
                offset=ft.Offset(4, 4),
            ),
        ]

    @staticmethod
    def get_pressed_shadows(page=None) -> list[ft.BoxShadow]:
        """Inset shadows for pressed state - appears pressed into surface"""
        _, dark_color = _resolve_theme_colors(page)

        return [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.15, dark_color),
                offset=ft.Offset(2, 2),
            ),
        ]

    @staticmethod
    def get_button_shadows(page=None) -> list[ft.BoxShadow]:
        """Neomorphic button shadows"""
        light_color, dark_color = _resolve_theme_colors(page)

        return [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.08, light_color),
                offset=ft.Offset(-2, -2),
            ),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.18, dark_color),
                offset=ft.Offset(2, 2),
            ),
        ]
