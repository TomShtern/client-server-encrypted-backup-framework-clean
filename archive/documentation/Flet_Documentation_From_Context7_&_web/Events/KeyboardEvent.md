# KeyboardEvent

In Flet, the `KeyboardEvent` class is used to handle keyboard input and capture "global" keyboard events within your application.

To utilize keyboard events, you typically assign a handler function to the `page.on_keyboard_event` property. This function will be called whenever a key is pressed, and it receives an instance of the `KeyboardEvent` class as an argument.

The `KeyboardEvent` object provides several properties to determine which key was pressed and if any modifier keys were held down:
*   `key`: A string representing the textual value of the pressed key (e.g., "A", "Enter", "F5").
*   `alt`: A boolean value that is `True` if the Alt (or Option) key was pressed.
*   `ctrl`: A boolean value that is `True` if the Control key was pressed.
*   `meta`: A boolean value that is `True` if the Meta (or Command) key was pressed.
*   `shift`: A boolean value that is `True` if the Shift key was pressed.

**Example of handling keyboard events:**

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Keyboard Event Example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    output_text = ft.Text("Press any key...", size=20)

    def on_keyboard(e: ft.KeyboardEvent):
        output_text.value = (
            f"Key: {e.key}, "
            f"Shift: {e.shift}, "
            f"Ctrl: {e.ctrl}, "
            f"Alt: {e.alt}, "
            f"Meta: {e.meta}"
        )
        page.update()

    page.on_keyboard_event = on_keyboard
    page.add(output_text)
    page.update() # Important: Call page.update() after setting the handler

if __name__ == "__main__":
    ft.app(target=main)
```

In this example, the `on_keyboard` function is triggered every time a key is pressed. It then updates the `output_text` control with information about the pressed key and any active modifier keys. Remember to call `page.update()` after setting the `on_keyboard_event` handler to ensure it's properly registered.
