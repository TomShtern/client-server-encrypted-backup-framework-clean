# theme.py
# This file now contains multiple, selectable themes for the application.

import flet as ft

# ==============================================================================
# THEME 1: "Professional & Balanced" (Teal Primary)
# ==============================================================================

teal_light_colors = {
    "primary": "#38A298", "on_primary": "#FFFFFF", "primary_container": "#B9F6F0", "on_primary_container": "#00201D",
    "secondary": "#7C5CD9", "on_secondary": "#FFFFFF", "secondary_container": "#EADDFF", "on_secondary_container": "#21005D",
    "tertiary": "#FFA726", "on_tertiary": "#000000", "tertiary_container": "#FFE0B2", "on_tertiary_container": "#2A1800",
    "error": "#EF5350", "on_error": "#FFFFFF", "error_container": "#FFDAD6", "on_error_container": "#410002",
    "background": "#F8F9FA", "on_background": "#1C2A35", "surface": "#F0F4F8", "on_surface": "#1C2A35",
    "surface_variant": "#DAE5E7", "on_surface_variant": "#3F484B", "outline": "#6F797B", "outline_variant": "#BFC8CB",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#2F3033", "on_inverse_surface": "#F1F0F4", "inverse_primary": "#A2D2E0",
}

teal_dark_colors = {
    "primary": "#82D9CF", "on_primary": "#003732", "primary_container": "#00504A", "on_primary_container": "#B9F6F0",
    "secondary": "#D0BCFF", "on_secondary": "#381E72", "secondary_container": "#4F378B", "on_secondary_container": "#EADDFF",
    "tertiary": "#FFB868", "on_tertiary": "#482900", "tertiary_container": "#663D00", "on_tertiary_container": "#FFDDB3",
    "error": "#FFB4AB", "on_error": "#690005", "error_container": "#93000A", "on_error_container": "#FFDAD6",
    "background": "#12181C", "on_background": "#E2E2E6", "surface": "#1A2228", "on_surface": "#E2E2E6",
    "surface_variant": "#3F484B", "on_surface_variant": "#BFC8CB", "outline": "#899295", "outline_variant": "#3F484B",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#E2E2E6", "on_inverse_surface": "#1A2228", "inverse_primary": "#38A298",
}

TealTheme = ft.Theme(color_scheme=ft.ColorScheme(**teal_light_colors), font_family="Inter")
TealDarkTheme = ft.Theme(color_scheme=ft.ColorScheme(**teal_dark_colors), font_family="Inter")


# ==============================================================================
# THEME 2: "Bold & Dynamic" (Purple Primary)
# ==============================================================================

purple_light_colors = {
    "primary": "#7C5CD9", "on_primary": "#FFFFFF", "primary_container": "#EADDFF", "on_primary_container": "#21005D",
    "secondary": "#FFA726", "on_secondary": "#000000", "secondary_container": "#FFE0B2", "on_secondary_container": "#2A1800",
    "tertiary": "#38A298", "on_tertiary": "#FFFFFF", "tertiary_container": "#B9F6F0", "on_tertiary_container": "#00201D",
    "error": "#EF5350", "on_error": "#FFFFFF", "error_container": "#FFDAD6", "on_error_container": "#410002",
    "background": "#F8F9FA", "on_background": "#1C2A35", "surface": "#F0F4F8", "on_surface": "#1C2A35",
    "surface_variant": "#DAE5E7", "on_surface_variant": "#3F484B", "outline": "#6F797B", "outline_variant": "#BFC8CB",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#2F3033", "on_inverse_surface": "#F1F0F4", "inverse_primary": "#D0BCFF",
}

purple_dark_colors = {
    "primary": "#D0BCFF", "on_primary": "#381E72", "primary_container": "#4F378B", "on_primary_container": "#EADDFF",
    "secondary": "#FFB868", "on_secondary": "#482900", "secondary_container": "#663D00", "on_secondary_container": "#FFDDB3",
    "tertiary": "#82D9CF", "on_tertiary": "#003732", "tertiary_container": "#00504A", "on_tertiary_container": "#B9F6F0",
    "error": "#FFB4AB", "on_error": "#690005", "error_container": "#93000A", "on_error_container": "#FFDAD6",
    "background": "#12181C", "on_background": "#E2E2E6", "surface": "#1A2228", "on_surface": "#E2E2E6",
    "surface_variant": "#3F484B", "on_surface_variant": "#BFC8CB", "outline": "#899295", "outline_variant": "#3F484B",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#E2E2E6", "on_inverse_surface": "#1A2228", "inverse_primary": "#7C5CD9",
}

PurpleTheme = ft.Theme(color_scheme=ft.ColorScheme(**purple_light_colors), font_family="Inter")
PurpleDarkTheme = ft.Theme(color_scheme=ft.ColorScheme(**purple_dark_colors), font_family="Inter")


# ==============================================================================
# EXPORT A DICTIONARY FOR EASY ACCESS
# ==============================================================================

# This dictionary makes it simple to look up a theme by its name.
THEMES = {
    "Teal": (TealTheme, TealDarkTheme),
    "Purple": (PurpleTheme, PurpleDarkTheme),
}

DEFAULT_THEME_NAME = "Teal"