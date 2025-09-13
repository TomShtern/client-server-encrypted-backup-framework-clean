# HoverEvent

In Flet, the `HoverEvent` class represents an event that occurs when a mouse pointer interacts with a control, specifically when it hovers over or enters/exits the control's area. This allows you to create interactive UI elements that respond to mouse movements.

### `HoverEvent` Properties

The `HoverEvent` object, passed to your event handler, provides detailed information about the mouse pointer's position and movement:
*   **`delta_x`**: The x-component of the distance in logical pixels the pointer moved since the last hover event.
*   **`delta_y`**: The y-component of the distance in logical pixels the pointer moved since the last hover event.
*   **`global_x`**: The x-component of the pointer's global position on the screen.
*   **`global_y`**: The y-component of the pointer's global position on the screen.
*   **`local_x`**: The x-component of the pointer's position relative to the control it's hovering over.
*   **`local_y`**: The y-component of the pointer's position relative to the control it's hovering over.
*   **`timestamp`**: The timestamp when the event occurred.

### Handling Hover Events

You can handle hover events using the `GestureDetector` control, which provides specific event handlers for mouse pointer interactions:
*   **`on_enter`**: Triggered when the mouse pointer enters the control's area.
*   **`on_hover`**: Triggered continuously while the mouse pointer is hovering over the control.
*   **`on_exit`**: Triggered when the mouse pointer leaves the control's area.

These event handlers receive a `HoverEvent` object as an argument.

### Example

Here's a basic example demonstrating how to use `on_enter`, `on_exit`, and `on_hover` with a `Container` wrapped in a `GestureDetector` to change its appearance and display hover information:

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Flet HoverEvent Example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    hover_info_text = ft.Text("Hover over the box!", size=16)

    def on_box_enter(e: ft.HoverEvent):
        e.control.content.bgcolor = ft.colors.BLUE_200
        e.control.content.border = ft.border.all(2, ft.colors.BLUE_700)
        hover_info_text.value = "Mouse entered!"
        page.update()

    def on_box_exit(e: ft.HoverEvent):
        e.control.content.bgcolor = ft.colors.GREY_200
        e.control.content.border = ft.border.all(1, ft.colors.GREY_500)
        hover_info_text.value = "Mouse exited!"
        page.update()

    def on_box_hover(e: ft.HoverEvent):
        hover_info_text.value = (
            f"Hovering: Local({e.local_x:.0f}, {e.local_y:.0f}), "
            f"Global({e.global_x:.0f}, {e.global_y:.0f})"
        )
        page.update()

    hover_box = ft.GestureDetector(
        content=ft.Container(
            width=200,
            height=100,
            bgcolor=ft.colors.GREY_200,
            border=ft.border.all(1, ft.colors.GREY_500),
            alignment=ft.alignment.center,
            content=ft.Text("Hover Me!"),
            border_radius=ft.border_radius.all(10),
        ),
        on_enter=on_box_enter,
        on_exit=on_box_exit,
        on_hover=on_box_hover,
    )

    page.add(
        hover_box,
        ft.Container(height=20), # Spacer
        hover_info_text,
    )

if __name__ == "__main__":
    ft.app(target=main)
```
