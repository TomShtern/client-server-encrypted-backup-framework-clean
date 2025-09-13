# ContainerTapEvent

In Flet, `ContainerTapEvent` is a specific event object that provides detailed information when a user taps on a `Container` control. It is a subclass of `TapEvent`.

When a `Container` is tapped, an event handler can be assigned to its `on_tap_down` property, and the argument passed to this handler will be an instance of `ContainerTapEvent`.

Key properties of `ContainerTapEvent` include:
*   **`global_x`**: The x-coordinate of the tap relative to the entire page.
*   **`global_y`**: The y-coordinate of the tap relative to the entire page.
*   **`local_x`**: The x-coordinate of the tap relative to the `Container` itself.
*   **`local_y`**: The y-coordinate of the tap relative to the `Container` itself.

**Usage Example:**

To capture a tap event on a `Container` and access its coordinates, you would typically use the `on_tap_down` event handler:

```python
import flet as ft

def main(page: ft.Page):
    def on_container_tap(e: ft.ContainerTapEvent):
        print(f"Container tapped at global: ({e.global_x}, {e.global_y}), "
              f"local: ({e.local_x}, {e.local_y})")
        page.add(ft.Text(f"Tapped at: ({e.local_x}, {e.local_y})"))

    page.add(
        ft.Container(
            content=ft.Text("Tap me!"),
            width=200,
            height=200,
            bgcolor=ft.colors.BLUE_GREY_700,
            alignment=ft.alignment.center,
            on_tap_down=on_container_tap, # Use on_tap_down for ContainerTapEvent
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
```

**Important Considerations:**

*   **`on_tap_down` vs. `on_click`**: Prior to Flet version 0.22.0, the `on_click` event on a `Container` might have provided `ContainerTapEvent` properties. However, this functionality was moved to `on_tap_down`. If you need tap coordinates, always use `on_tap_down`.
*   **`ink` property**: If the `Container`'s `ink` property is set to `True`, the event argument for `on_tap_down` will be a generic `ControlEvent` with empty data, not a `ContainerTapEvent`.