# OnScrollEvent

In Flet, the `OnScrollEvent` is a powerful mechanism for receiving notifications when the scroll position of a scrollable control changes. This allows developers to implement various interactive features, such as infinite scrolling, lazy loading, or custom scroll indicators.

### Controls Supporting `OnScrollEvent`

The `on_scroll` event handler is available for the following Flet controls:
*   `ft.Page`
*   `ft.View`
*   `ft.Column`
*   `ft.Row`
*   `ft.ListView`
*   `ft.GridView`

### `OnScrollEvent` Properties

When an `on_scroll` event fires, the event handler receives an `ft.OnScrollEvent` object, which contains detailed information about the scroll state:

*   **`event_type`** (`str`): Describes the type of scroll event that occurred. Possible values include:
    *   `"start"`: The control has begun scrolling.
    *   `"update"`: The control's scroll position has changed.
    *   `"end"`: The control has stopped scrolling.
    *   `"user"`: The user has changed their scrolling direction.
    *   `"over"`: The control attempted to scroll beyond its bounds.
*   **`pixels`** (`float`): The current scroll position in logical pixels.
*   **`min_scroll_extent`** (`float`): The minimum valid scroll position in pixels.
*   **`max_scroll_extent`** (`float`): The maximum valid scroll position in pixels.
*   **`viewport_dimension`** (`float`): The extent of the viewport.
*   **`scroll_delta`** (`float`): The distance scrolled in logical pixels since the last update. This property is only available when `event_type` is `"update"`.
*   **`direction`** (`str`): The direction of user scrolling. This property is only available when `event_type` is `"user"`. Possible values are `"idle"`, `"forward"`, or `"reverse"`.
*   **`overscroll`** (`float`): The number of logical pixels the scrollable avoided scrolling due to being out of bounds. This property is only available when `event_type` is `"over"`.
*   **`velocity`** (`float`): The velocity at which the scroll position was changing when an overscroll event occurred. This property is only available when `event_type` is `"over"`.

### Example Usage

To use `OnScrollEvent`, you attach a function to the `on_scroll` property of a scrollable control. The function will be called whenever a scroll event occurs, receiving an `ft.OnScrollEvent` object as its argument.

```python
import flet as ft

def main(page: ft.Page):
    def on_column_scroll(e: ft.OnScrollEvent):
        # Print various properties of the scroll event
        print(f"Type: {e.event_type}, Pixels: {e.pixels}, "
              f"Min Extent: {e.min_scroll_extent}, Max Extent: {e.max_scroll_extent}")
        if e.event_type == "update":
            print(f"Scroll Delta: {e.scroll_delta}")
        if e.event_type == "user":
            print(f"Direction: {e.direction}")
        if e.event_type == "over":
            print(f"Overscroll: {e.overscroll}, Velocity: {e.velocity}")

    # Create a Column control with scrolling enabled and an on_scroll handler
    scrollable_column = ft.Column(
        spacing=10,
        height=300,  # Give it a fixed height to enable scrolling
        width=200,
        scroll=ft.ScrollMode.ALWAYS, # Always show scrollbar
        on_scroll=on_column_scroll, # Attach the event handler
        border=ft.border.all(1, ft.colors.BLUE_GREY_200)
    )

    # Add some content to the column to make it scrollable
    for i in range(50):
        scrollable_column.controls.append(ft.Text(f"Item {i}", key=str(i)))

    page.add(
        ft.Container(
            content=scrollable_column,
            padding=10,
            border_radius=5
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
```
