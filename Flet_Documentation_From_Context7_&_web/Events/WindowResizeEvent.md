# WindowResizeEvent

In Flet, you can handle window resize events using the `page.on_resized` event handler. This event fires whenever the application window changes its size.

Here's how you can use it:

1.  **`page.on_resized` Event Handler**: Attach a function to `page.on_resized`. This function will be called when the window is resized.
2.  **Accessing Dimensions**: Inside the event handler, you can access the new width and height of the window using `page.width` and `page.height` respectively.
3.  **`WindowResizeEvent`**: While `page.on_resized` directly provides the new `page.width` and `page.height`, the underlying event object for a window resize is `WindowResizeEvent`. This class has `height` and `width` properties that reflect the window's dimensions after the resize.

**Example:**

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Window Resize Event Example"

    def on_window_resized(e):
        # The 'e' object here is a WindowEvent, which can be a WindowResizeEvent
        # You can access the new dimensions directly from page.width and page.height
        # or, if you were to inspect the event object, it would contain the new dimensions.
        print(f"Window resized to: Width={page.width}, Height={page.height}")
        # You can update UI elements based on the new size
        size_text.value = f"Window Size: {int(page.width)}x{int(page.height)}"
        page.update()

    page.on_resized = on_window_resized

    size_text = ft.Text(f"Window Size: {int(page.width)}x{int(page.height)}")
    page.add(size_text)

    # You can also control if the window is resizable
    # page.window.resizable = False # Uncomment to make the window non-resizable

ft.app(target=main)
```

In this example, the `on_window_resized` function is called every time the Flet window is resized. It then prints the new dimensions to the console and updates a `Text` control on the page to display the current window size.

You can also prevent the window from being resizable by setting `page.window.resizable = False`.
