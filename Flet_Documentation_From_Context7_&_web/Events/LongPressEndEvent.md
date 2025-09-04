# LongPressEndEvent

`LongPressEndEvent` in Flet is an event that occurs when a long press gesture ends. It is typically associated with controls that support long press interactions, such as `Container`.

This event provides several properties that describe the state of the pointer when the long press ended:
*   **`global_x`**: The x-coordinate of the pointer's global position on the screen.
*   **`global_y`**: The y-coordinate of the pointer's global position on the screen.
*   **`local_x`**: The x-coordinate of the pointer's local position relative to the control that received the event.
*   **`local_y`**: The y-coordinate of the pointer's local position relative to the control that received the event.
*   **`velocity_x`**: The x-component of the pointer's velocity when it stopped contacting the screen.
*   **`velocity_y`**: The y-component of the pointer's velocity when it stopped contacting the screen.

You would typically handle this event by assigning a function to the `on_long_press_end` property of a control.
