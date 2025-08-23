# AI Agent Guide: Building Material Design 3 GUIs with Flet (Enhanced)

This guide provides AI coding agents with essential context and best practices for creating modern, correct, and visually appealing desktop GUIs using Flet and Material Design 3 (M3).

**Core Principle:** Flet uses Material Design 3 by default. Do not search for or try to install separate "Material Design" libraries. All necessary components and theming are built-in.

## 1. Theming: The Foundation of M3

The visual identity of an M3 application is controlled through the `page.theme` and `page.dark_theme` objects.

### 1.1. Theme Activation and Mode

Material 3 is enabled by default. The `page.theme_mode` property controls whether the app displays in light, dark, or system-defined mode.

**Action:** Set the `theme_mode` early. A good default is `ft.ThemeMode.SYSTEM`.

```python
import flet as ft

def main(page: ft.Page):
    # M3 is the default, but explicit is better than implicit.
    page.theme = ft.Theme(use_material3=True, color_scheme_seed="blue")
    page.dark_theme = ft.Theme(use_material3=True, color_scheme_seed="blue")
    page.theme_mode = ft.ThemeMode.SYSTEM # Or LIGHT, DARK
    # ... rest of the app
```

### 1.2. The Easy Method: `color_scheme_seed`

This is the **strongly preferred method** for theming. It leverages M3's dynamic color feature to generate a complete, harmonious, and accessible color palette from a single color. This is the fastest way to a professional-looking app.

**Action:** Always start with a `color_scheme_seed`. Do not define colors manually unless the user provides a strict, multi-color brand guide.

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Easy M3 Theming"
    page.theme = ft.Theme(color_scheme_seed="indigo")
    page.dark_theme = ft.Theme(color_scheme_seed="orange")
    page.theme_mode = ft.ThemeMode.SYSTEM

    page.add(ft.FilledButton(text="Themed Button"))
    page.update()

ft.app(main)
```

### 1.3. The Advanced Method: `ColorScheme`

Only use this for surgical overrides when a seed color isn't sufficient. It's powerful but can easily lead to a visually inconsistent UI if not used with care.

**Action:** If you must use `ColorScheme`, combine it with a `color_scheme_seed` to maintain overall harmony. Override only the colors the user explicitly specifies.

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Advanced M3 Theming"

    page.theme = ft.Theme(
        color_scheme_seed="cyan", # Start with a seed for a consistent base
        color_scheme=ft.ColorScheme( # Then, override specific parts
            primary=ft.colors.PINK_ACCENT_400,
        )
    )

    page.add(ft.FilledButton(text="Custom Button"))
    page.update()

ft.app(main)
```

## 2. Control References: Using `Ref`s

To build interactive applications, you need to reference controls. The **best practice** in Flet is to use `Ref` objects. This is more robust and scalable than using simple variables.

**Action:** Use `ft.Ref[ControlType]()` to create a reference. Assign it to the `ref` property of a control. Access the control instance via `my_ref.current`.

```python
import flet as ft

def main(page: ft.Page):
    # 1. Create references
    first_name = ft.Ref[ft.TextField]()
    last_name = ft.Ref[ft.TextField]()
    greetings = ft.Ref[ft.Column]()

    def btn_click(e):
        # 2. Access controls via .current
        greetings.current.controls.append(
            ft.Text(f"Hello, {first_name.current.value} {last_name.current.value}!")
        )
        first_name.current.value = ""
        last_name.current.value = ""
        page.update()
        first_name.current.focus()

    # 3. Assign references to controls
    page.add(
        ft.TextField(ref=first_name, label="First name", autofocus=True),
        ft.TextField(ref=last_name, label="Last name"),
        ft.ElevatedButton("Say hello!", on_click=btn_click),
        ft.Column(ref=greetings),
    )

ft.app(main)
```

## 3. Layout and Structure

M3 emphasizes clean, spacious, and adaptive layouts.

**Action:**
1.  **Use `ft.ResponsiveRow` for adaptive layouts** that work on different window sizes.
2.  Use `ft.Card` or `ft.Container` with `padding` and `border_radius` to group related controls. M3 uses a default radius; only override if necessary.
3.  Use `alignment` and `spacing` properties to create clean layouts. Avoid manual positioning.
4.  Wrap the main content of your page in `ft.SafeArea` to avoid OS interfaces on mobile, which is good practice for responsive design.

### Example: A Responsive M3 Card Layout

```python
import flet as ft

def main(page: ft.Page):
    page.title = "M3 Layout"
    page.theme = ft.Theme(color_scheme_seed="purple")

    # Use SafeArea for content that should avoid system intrusions
    page.add(ft.SafeArea(
        ft.ResponsiveRow(
            [
                ft.Card(
                    col={"sm": 12, "md": 6, "lg": 4},
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("User Profile", style=ft.TextThemeStyle.TITLE_LARGE),
                            ft.TextField(label="Name"),
                            ft.TextField(label="Email"),
                            ft.FilledButton(text="Save")
                        ])
                    )
                ),
                # ... other cards
            ]
        )
    ))
    page.update()

ft.app(main)
```

## 4. Component Usage and Subtleties

**Action:** Prefer M3 components and use them semantically.

*   **Buttons:** Use `ft.FilledButton` (high emphasis), `ft.FilledTonalButton` (medium emphasis), `ft.OutlinedButton` (medium emphasis), or `ft.TextButton` (low emphasis). Avoid the generic `ft.ElevatedButton` unless a shadowed, high-contrast button is specifically required.
*   **Navigation:** Use `ft.NavigationBar` for 3-5 top-level mobile destinations. For desktop, prefer the `ft.NavigationRail`, which is designed for the larger form factor.
*   **App Bar:** Use `ft.AppBar` for the top application bar. Set `center_title=False` for a standard M3 desktop look.
*   **Icons:** Use icons from `ft.icons`. M3 has a specific, clean icon style that is matched by this library.

## 5. User Feedback

Good GUIs provide feedback. Use these tools for appropriate scenarios.

*   **`ft.SnackBar`:** For temporary, non-interruptive messages (e.g., "Email sent").
*   **`ft.AlertDialog`:** For critical information that requires user confirmation (e.g., "Delete this file?").

```python
import flet as ft

def main(page: ft.Page):
    def show_snackbar(e):
        page.snack_bar = ft.SnackBar(ft.Text("Item saved!"), open=True)
        page.update()

    def show_alert(e):
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm deletion"),
            content=ft.Text("Are you sure you want to delete this item?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda _: print("Deleted!")),
                ft.TextButton("No", on_click=lambda _: print("Cancelled!")),
            ],
        )
        page.dialog.open = True
        page.update()

    page.add(
        ft.FilledButton("Save Item", on_click=show_snackbar),
        ft.OutlinedButton("Delete Item", on_click=show_alert)
    )

ft.app(main)
```

By following these enhanced principles, you will generate Flet GUI code that is robust, scalable, and visually consistent with modern Material Design 3 standards.