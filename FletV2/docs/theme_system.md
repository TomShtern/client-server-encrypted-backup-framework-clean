# FletV2 Theme System

## Overview

The FletV2 application includes a comprehensive theme system that supports multiple themes with light and dark variants. This document describes the theme system architecture and usage.

## Theme Structure

### Theme Definition

Themes are defined in `theme.py` and consist of:

1. **Color Definitions**: Light and dark color schemes
2. **Component Styles**: Specific styling for Flet components
3. **Theme Objects**: Complete Flet Theme objects for light and dark modes

### Available Themes

1. **Teal Theme** - Professional & Balanced
   - Primary color: Teal
   - Secondary color: Purple
   - Tertiary color: Orange

2. **Purple Theme** - Bold & Dynamic
   - Primary color: Purple
   - Secondary color: Orange
   - Tertiary color: Teal

## Theme API

### Theme Application

```python
from theme import setup_default_theme, apply_theme_to_page, toggle_theme_mode

# Apply default theme to a page
setup_default_theme(page)

# Apply a specific theme to a page
apply_theme_to_page(page, "Teal")

# Toggle between light and dark modes
toggle_theme_mode(page)
```

### Color Tokens

The theme system provides color tokens for consistent styling:

```python
from theme import TOKENS

# Access color tokens
primary_color = TOKENS['primary']
secondary_color = TOKENS['secondary']
```

### Theme Constants

```python
from theme import THEMES, DEFAULT_THEME_NAME

# Access available themes
available_themes = list(THEMES.keys())

# Access default theme name
default_theme = DEFAULT_THEME_NAME
```

## Implementation Details

### Color Schemes

Each theme defines both light and dark color schemes:

```python
# Light color scheme
teal_light_colors = {
    "primary": "#38A298",
    "on_primary": "#FFFFFF",
    "primary_container": "#B9F6F0",
    "on_primary_container": "#00201D",
    # ... other colors
}

# Dark color scheme
teal_dark_colors = {
    "primary": "#82D9CF",
    "on_primary": "#003732",
    "primary_container": "#00504A",
    "on_primary_container": "#B9F6F0",
    # ... other colors
}
```

### Component Styling

Themes can define specific styles for components:

```python
# Button style for teal theme
teal_elevated_button_style = ft.ButtonStyle(
    color={
        ft.ControlState.DEFAULT: ft.Colors.ON_PRIMARY,
    },
    bgcolor={
        ft.ControlState.DEFAULT: teal_light_colors["primary"],
        ft.ControlState.HOVERED: teal_light_colors["primary"],
        ft.ControlState.PRESSED: teal_light_colors["primary"],
    }
)
```

### Theme Objects

Complete theme objects are created for both light and dark modes:

```python
TealTheme = ft.Theme(
    color_scheme=ft.ColorScheme(**teal_light_colors),
    font_family="Inter",
    elevated_button_theme=ft.ElevatedButtonTheme(
        foreground_color=ft.Colors.ON_PRIMARY,
        bgcolor=teal_light_colors["primary"]
    )
)

TealDarkTheme = ft.Theme(
    color_scheme=ft.ColorScheme(**teal_dark_colors),
    font_family="Inter",
    elevated_button_theme=ft.ElevatedButtonTheme(
        foreground_color=ft.Colors.ON_PRIMARY,
        bgcolor=teal_dark_colors["primary"]
    )
)
```

## Usage in Views

Views should use Flet's built-in theme support rather than hardcoding colors:

### Correct Usage

```python
# Use Flet's built-in color constants
text = ft.Text("Hello", color=ft.Colors.PRIMARY)

# Use theme-based styling
button = ft.ElevatedButton("Click me")
```

### Incorrect Usage

```python
# Avoid hardcoding colors
text = ft.Text("Hello", color="#38A298")  # Bad
```

## Best Practices

1. **Use Flet's Native Colors**: Leverage `ft.Colors` constants for consistency
2. **Theme Compatibility**: Use theme-aware components that adapt to light/dark modes
3. **Color Tokens**: Access colors through the TOKENS system for consistency
4. **Component Themes**: Define component-specific themes in the theme file
5. **Text Themes**: Use consistent typography through text theme definitions
6. **Accessibility**: Ensure sufficient contrast in both light and dark modes
7. **Testing**: Test UI in both light and dark modes

## Adding New Themes

To add a new theme:

1. Define light and dark color schemes
2. Create component-specific styles
3. Create Flet Theme objects
4. Add the theme to the THEMES dictionary
5. Update DEFAULT_THEME_NAME if needed
6. Test the theme in all views

Example:

```python
# Define color schemes
new_light_colors = {
    "primary": "#FF0000",
    "on_primary": "#FFFFFF",
    # ... other colors
}

new_dark_colors = {
    "primary": "#FF6666",
    "on_primary": "#000000",
    # ... other colors
}

# Create theme objects
NewTheme = ft.Theme(color_scheme=ft.ColorScheme(**new_light_colors))
NewDarkTheme = ft.Theme(color_scheme=ft.ColorScheme(**new_dark_colors))

# Add to THEMES dictionary
THEMES["New"] = (NewTheme, NewDarkTheme)
```