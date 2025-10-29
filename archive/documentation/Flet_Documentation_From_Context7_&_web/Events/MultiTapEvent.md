# MultiTapEvent

In Flet, the `MultiTapEvent` is an event that is triggered when a specified number of pointers (e.g., fingers on a touchscreen) simultaneously touch the screen. This event is typically handled using the `GestureDetector` control.

Key aspects of `MultiTapEvent` and its usage:

*   **`GestureDetector` Control**: You attach multi-tap event handlers to a `GestureDetector` control. This control is used to detect various gestures, including multi-taps.
*   **`multi_tap_touches` Property**: This property of the `GestureDetector` specifies the minimum number of pointers required to trigger the `on_multi_tap` event. For example, if you set `multi_tap_touches=2`, the `on_multi_tap` event will fire when two fingers touch the screen at the same time.
*   **`on_multi_tap` Event Handler**: This is the callback function that gets executed when the multi-tap gesture is detected. The event handler receives a `MultiTapEvent` object as an argument.
*   **`MultiTapEvent` Properties**: The `MultiTapEvent` class has a `correct_touches` property, which is `True` if the specified `multi_tap_touches` number of pointers touched the screen.

**Example Usage**:

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Multi-Tap Event Example"

    def handle_multi_tap(e: ft.MultiTapEvent):
        print(f"Multi-tap detected! Correct touches: {e.correct_touches}")
        page.add(ft.Text(f"Multi-tap detected!"))

    page.add(
        ft.GestureDetector(
            content=ft.Container(
                width=300,
                height=300,
                bgcolor=ft.colors.BLUE_GREY_700,
                alignment=ft.alignment.center,
                content=ft.Text("Tap with multiple fingers", color=ft.colors.WHITE),
            ),
            multi_tap_touches=2,  # Set to 2 for a two-finger tap
            on_multi_tap=handle_multi_tap,
        )
    )

ft.app(target=main)
```
