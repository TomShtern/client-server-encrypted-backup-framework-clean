# Assets

This document explains how to include and use assets like images, fonts, and other files in a Flet application.

To use assets, you need to:
1.  Create a directory (by default, it's named `assets`) in your project to store your asset files.
2.  When you run your Flet app using `ft.app()`, specify the path to your assets directory with the `assets_dir` parameter.
3.  You can then reference assets in your controls using a path relative to the `assets_dir`.

For example, to display an image located at `assets/images/sample.png`, you would use:

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Image(src="images/sample.png")
    )

ft.app(main, assets_dir="assets")
```
