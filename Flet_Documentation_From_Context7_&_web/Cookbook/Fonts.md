# Fonts

In Flet, you can use both system fonts and imported fonts.

**System Fonts**

You can use any font installed on your computer by referencing its name. For example:

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text("This is Consolas font", font_family="Consolas"))

ft.app(target=main)
```

**Importing Fonts**

You can import fonts from a URL or from your application's assets directory.

To do this, you set the `page.fonts` property to a dictionary where the keys are the font family names and the values are the paths to the font files. You can then apply these fonts globally using a theme or to individual controls.

Here is an example that loads the "Kanit" font from a URL and "Open Sans" from local assets:

```python
import flet as ft

def main(page: ft.Page):
    page.fonts = {
        "Kanit": "https://raw.githubusercontent.com/google/fonts/main/ofl/kanit/Kanit-Bold.ttf",
        "Open Sans": "/fonts/OpenSans-Regular.ttf",
    }

    page.theme = ft.Theme(font_family="Kanit")

    page.add(
        ft.Text("This is Kanit font, the default font for the page"),
        ft.Text("This is Open Sans font", font_family="Open Sans"),
    )

ft.app(target=main, assets_dir="assets")
```

**Static and Variable Fonts**

Currently, Flet only supports static fonts. However, you can use tools like `fonttools` to create static instances of variable fonts at specific weights.
