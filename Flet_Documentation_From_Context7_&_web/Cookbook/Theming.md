# Theming

In Flet, you can configure the visual theme for your application and its controls.

### App-wide Themes

You can set themes for the entire application using the `theme` and `dark_theme` properties of the `Page` control. These properties accept a `Theme` object and define the look for the app in light and dark modes, respectively.

For example, you can set a green-based theme for light mode and a blue-based theme for dark mode like this:

```python
page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
```

### Nested Themes

Flet also allows you to apply different themes to specific parts of your application or override certain theme styles for individual controls. Some container controls have `theme` and `theme_mode` properties.

*   `theme`: Overrides specific styles from the parent theme.
*   `theme_mode`: Applies a completely new, unique theme to all controls within that container, ignoring the parent's theme mode.

Here is an example demonstrating nested themes:

```python
import flet as ft

def main(page: ft.Page):
    # App-wide theme (Yellow)
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.YELLOW,
    )

    page.add(
        # A button using the default page theme
        ft.Container(
            content=ft.ElevatedButton("Page theme button"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=20,
            width=300,
        ),
        # A button with an overridden primary color (Pink)
        ft.Container(
            theme=ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.PINK)),
            content=ft.ElevatedButton("Inherited theme button"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=20,
            width=300,
        ),
        # A button within a container that has its own unique dark theme (Indigo)
        ft.Container(
            theme=ft.Theme(color_scheme_seed=ft.Colors.INDIGO),
            theme_mode=ft.ThemeMode.DARK,
            content=ft.ElevatedButton("Unique theme button"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=20,
            width=300,
        ),
    )

ft.app(main)
```
