# Keyboard shortcuts

Flet enables you to capture global keyboard events to create shortcuts and enhance user productivity. This is accomplished by implementing the `page.on_keyboard_event` handler.

### Handling Keyboard Events

The `on_keyboard_event` handler receives a `KeyboardEvent` object which contains the following properties:

*   `key`: A string representing the key that was pressed (e.g., `A`, `Enter`, `F5`).
*   `shift`: A boolean that is `True` if the "Shift" key was pressed.
*   `ctrl`: A boolean that is `True` if the "Control" key was pressed.
*   `alt`: A boolean that is `True` if the "Alt" (or "Option") key was pressed.
*   `meta`: A boolean that is `True` if the "Command" key was pressed.

### Example Implementation

Here is a basic example of how to set up a keyboard event handler in a Flet application:

```python
import flet as ft

def main(page: ft.Page):
    
    def on_keyboard(e: ft.KeyboardEvent):
        # Display the pressed key and any modifier keys
        key_info.value = (
            f"Key: {e.key}, Shift: {e.shift}, "
            f"Ctrl: {e.ctrl}, Alt: {e.alt}, Meta: {e.meta}"
        )
        page.update()

    # Assign the handler to the page's on_keyboard_event property
    page.on_keyboard_event = on_keyboard

    # Add text controls to display the event information
    page.add(
        ft.Text("Press any key to see the event details."),
        key_info := ft.Text()
    )

ft.app(target=main)
```

In this example, the `on_keyboard` function is defined to handle keyboard events. It updates a `Text` control with information about the pressed key and any active modifier keys. This function is then assigned to the `page.on_keyboard_event` property, linking it to the page's keyboard events. When a key is pressed, the `on_keyboard` function is called, and the UI is updated to show the details of the `KeyboardEvent`.
