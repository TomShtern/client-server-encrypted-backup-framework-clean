# ScrollEvent

In Flet, there are two main event classes related to scrolling: `OnScrollEvent` and `ScrollEvent`.

The `OnScrollEvent` class provides detailed information about the state and type of a scroll event. Its key properties include:
*   **`direction`**: Indicates the direction of scrolling ("idle", "forward", "reverse"), available when `event_type` is "user".
*   **`event_type`**: A string describing the type of scroll event, such as "start" (scrolling began), "update" (scroll position changed), "end" (scrolling stopped), "user" (user changed scroll direction), or "over" (scrolling attempted beyond bounds).
*   **`pixels`**: The current scroll position in logical pixels.
*   **`min_scroll_extent`**: The minimum scroll position.
*   **`max_scroll_extent`**: The maximum scroll position.
*   **`viewport_dimension`**: The size of the visible scrollable area.
*   **`scroll_delta`**: The distance scrolled during an "update" event, in logical pixels.
*   **`overscroll`**: The number of logical pixels that scrolling was prevented from exceeding bounds, available when `event_type` is "over".
*   **`velocity`**: The velocity of the scroll position change during an "over" event.

The `ScrollEvent` class, on the other hand, provides information related to the pointer's position and scroll delta during a scroll gesture:
*   **`global_x`** and **`global_y`**: The x and y components of the pointer's global position.
*   **`local_x`** and **`local_y`**: The x and y components of the pointer's local position.
*   **`scroll_delta_x`** and **`scroll_delta_y`**: The x and y components of the amount to scroll, in logical pixels.

Typically, `OnScrollEvent` is used when you need to react to the *state* of scrolling (e.g., when scrolling starts, stops, or updates), while `ScrollEvent` might be more relevant for understanding the raw input of a scroll gesture.
