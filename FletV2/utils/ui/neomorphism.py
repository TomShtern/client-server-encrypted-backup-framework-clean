"""
Neomorphic design utilities for Flet applications
Flet 0.28.3 Compatible
"""

import flet as ft


class NeomorphicShadows:
    """Professional neomorphic shadow system with elevation levels"""

    @staticmethod
    def get_card_shadows(elevation: str = "medium", page=None) -> list[ft.BoxShadow]:
        """
        Get neomorphic shadows for cards based on elevation level.
        Neomorphism uses dual shadows to create depth perception.
        """
        if page and page.theme:
            # Use theme colors for theme-aware shadows
            light_color = page.theme.color_scheme.surface if hasattr(page.theme, 'color_scheme') else ft.Colors.WHITE
            dark_color = page.theme.color_scheme.shadow if hasattr(page.theme, 'color_scheme') else ft.Colors.BLACK
        else:
            # Fallback to standard colors
            light_color = ft.Colors.WHITE
            dark_color = ft.Colors.BLACK

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
        if page and page.theme and hasattr(page.theme, 'color_scheme'):
            light_color = page.theme.color_scheme.surface
            dark_color = page.theme.color_scheme.shadow
        else:
            light_color = ft.Colors.WHITE
            dark_color = ft.Colors.BLACK

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
        if page and page.theme and hasattr(page.theme, 'color_scheme'):
            dark_color = page.theme.color_scheme.shadow
        else:
            dark_color = ft.Colors.BLACK

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
        if page and page.theme and hasattr(page.theme, 'color_scheme'):
            light_color = page.theme.color_scheme.surface
            dark_color = page.theme.color_scheme.shadow
        else:
            light_color = ft.Colors.WHITE
            dark_color = ft.Colors.BLACK

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