# WebviewScrollEvent

The `Flet WebviewScrollEvent` is an event in the Flet framework that fires when a `WebView` control is scrolled. This event provides the current scroll position within the web content.

**Properties of `WebviewScrollEvent`:**
The `WebviewScrollEvent` class has the following properties:
*   `x`: The x-coordinate of the scroll position.
*   `y`: The y-coordinate of the scroll position.

**Platform Limitations:**
It's important to note that many `WebView` events and functionalities, including scrolling methods like `scroll_to()` and `scroll_by()`, are primarily supported on Android, iOS, and macOS platforms. While not explicitly stated for `WebviewScrollEvent` itself, it's likely subject to similar platform constraints.

**How to use `WebviewScrollEvent`:**

1.  **Install `flet-webview`:** First, ensure you have the `flet-webview` package installed, as the `WebView` control is an extension to Flet. You can install it using pip:
    ```bash
    pip install flet-webview
    ```

2.  **Create a `WebView` control:** Import `WebView` from `flet_webview` and add it to your Flet page.

3.  **Attach an event handler:** Assign a function to the `on_scroll` property of the `WebView` control. This function will be called whenever the webview is scrolled, and it will receive a `WebviewScrollEvent` object as an argument.

**Example:**

```python
import flet as ft
from flet_webview import WebView

def main(page: ft.Page):
    page.title = "Flet WebView Scroll Event Example"

    def on_webview_scroll(e: ft.WebviewScrollEvent):
        # Access the scroll coordinates from the event object
        print(f"WebView Scrolled: x={e.x}, y={e.y}")
        # You can update UI elements based on scroll position here
        scroll_status_text.value = f"Scroll Position: x={e.x}, y={e.y}"
        page.update()

    scroll_status_text = ft.Text("Scroll Position: N/A")

    webview_control = WebView(
        url="https://flet.dev",  # Replace with any URL you want to load
        expand=True,
        on_scroll=on_webview_scroll  # Attach the scroll event handler
    )

    page.add(
        scroll_status_text,
        webview_control
    )

ft.app(target=main)
```
