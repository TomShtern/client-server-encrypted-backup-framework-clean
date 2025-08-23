# theme_m3.py
# Expanded Material-3 style design tokens for your Flet app.
# Generated from your logo (favicon.svg). Replace hex values if you want different shades.
import flet as ft

# Design tokens (explicit roles)
TOKENS = {
    # Primary: blue → purple gradient (use these colors for gradients, accents, icons)
    "primary_gradient": ["#A8CBF3", "#7C5CD9"],  # light blue to purple
    "primary": "#7C5CD9",  # fallback solid primary (purple)
    "on_primary": "#FFFFFF",
    # Secondary: orange (top arrow)
    "secondary": "#FCA651",
    "on_secondary": "#000000",
    # Tertiary: pink-ish (bottom arrow) — distinct from error red
    "tertiary": "#AB6DA4",
    "on_tertiary": "#FFFFFF",
    # Containers (teal for the "file page" background)
    "container": "#38A298",
    "on_container": "#FFFFFF",
    # Surface tones (suggested): neutral surfaces compatible with M3
    "surface": "#F6F8FB",            # main surface (light)
    "surface_variant": "#E7EDF7",    # subtle variant
    "surface_dark": "#0F1720",       # main dark surface suggestion
    "background": "#FFFFFF",
    "on_background": "#000000",
    "outline": "#666666",
    # Error
    "error": "#B00020",
    "on_error": "#FFFFFF"
}

def create_theme(use_material3: bool = True, dark: bool = False) -> ft.Theme:
    """Return a Flet Theme using the tokens above.
    This creates a full Material color scheme using all custom tokens.
    We also expose the token palette for direct use."""
    
    # Create base theme with primary color as seed
    seed = TOKENS.get("primary") or TOKENS["primary_gradient"][0]
    theme = ft.Theme(
        use_material3=use_material3,
        color_scheme_seed=seed,
        font_family="Inter"
    )
    
    # Override with custom color scheme if available
    if hasattr(ft, 'ColorScheme'):
        # Create a custom color scheme using all the defined tokens
        custom_scheme = ft.ColorScheme(
            primary=TOKENS.get("primary", "#7C5CD9"),
            on_primary=TOKENS.get("on_primary", "#FFFFFF"),
            secondary=TOKENS.get("secondary", "#FCA651"),
            on_secondary=TOKENS.get("on_secondary", "#000000"),
            tertiary=TOKENS.get("tertiary", "#AB6DA4"),
            on_tertiary=TOKENS.get("on_tertiary", "#FFFFFF"),
            primary_container=TOKENS.get("container", "#38A298"),
            on_primary_container=TOKENS.get("on_container", "#FFFFFF"),
            secondary_container=TOKENS.get("container", "#38A298"),
            on_secondary_container=TOKENS.get("on_container", "#FFFFFF"),
            tertiary_container=TOKENS.get("container", "#38A298"),
            on_tertiary_container=TOKENS.get("on_container", "#FFFFFF"),
            surface=TOKENS.get("surface", "#F6F8FB") if not dark else TOKENS.get("surface_dark", "#0F1720"),
            on_surface=TOKENS.get("on_background", "#000000") if not dark else "#FFFFFF",
            surface_variant=TOKENS.get("surface_variant", "#E7EDF7"),
            on_surface_variant=TOKENS.get("outline", "#666666"),
            outline=TOKENS.get("outline", "#666666"),
            error=TOKENS.get("error", "#B00020"),
            on_error=TOKENS.get("on_error", "#FFFFFF"),
        )
        
        # Apply the custom color scheme
        theme.color_scheme = custom_scheme
        
        # For dark theme, adjust some colors
        if dark:
            dark_scheme = ft.ColorScheme(
                primary=TOKENS.get("primary", "#7C5CD9"),
                on_primary=TOKENS.get("on_primary", "#FFFFFF"),
                secondary=TOKENS.get("secondary", "#FCA651"),
                on_secondary=TOKENS.get("on_secondary", "#000000"),
                tertiary=TOKENS.get("tertiary", "#AB6DA4"),
                on_tertiary=TOKENS.get("on_tertiary", "#FFFFFF"),
                primary_container=TOKENS.get("container", "#38A298"),
                on_primary_container=TOKENS.get("on_container", "#FFFFFF"),
                secondary_container=TOKENS.get("container", "#38A298"),
                on_secondary_container=TOKENS.get("on_container", "#FFFFFF"),
                tertiary_container=TOKENS.get("container", "#38A298"),
                on_tertiary_container=TOKENS.get("on_container", "#FFFFFF"),
                surface=TOKENS.get("surface_dark", "#0F1720"),
                on_surface="#FFFFFF",
                surface_variant=TOKENS.get("surface_variant", "#E7EDF7"),
                on_surface_variant=TOKENS.get("outline", "#666666"),
                outline=TOKENS.get("outline", "#666666"),
                error=TOKENS.get("error", "#B00020"),
                on_error=TOKENS.get("on_error", "#FFFFFF"),
            )
            theme.color_scheme = dark_scheme
    
    return theme

# Helper: make linear gradient for containers/buttons
def linear_gradient(colors=None, begin=ft.alignment.top_left, end=ft.alignment.bottom_right, stops=None):
    if colors is None:
        colors = TOKENS["primary_gradient"]
    return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)

# Small helpers for consistent components
def gradient_button(content, width=220, height=48, on_click=None, radius=12):
    """Return a Container that behaves like a Filled/Gradient button."""
    c = ft.Container(
        width=width,
        height=height,
        content=ft.Row([content], alignment=ft.MainAxisAlignment.CENTER),
        border_radius=ft.border_radius.all(radius),
        gradient=linear_gradient(),
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        animate_scale=180
    )
    return c

def surface_container(child, padding=12, radius=12, elevation=2):
    return ft.Card(content=child, elevation=elevation, border_radius=ft.border_radius.all(radius))