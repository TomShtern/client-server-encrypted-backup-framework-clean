# LongPressStartEvent

In Flet, `LongPressStartEvent` is an event type that is triggered when a long press gesture is recognized. This occurs when a pointer (such as a mouse cursor or a touch on a screen) remains in contact with the same location for an extended period.

This event is typically used with the `GestureDetector` control, which provides event handlers for various gestures. You can attach a function to the `on_long_press_start` or `on_secondary_long_press_start` properties of a `GestureDetector` to respond when a long press begins.

The `LongPressStartEvent` object provides the following properties, which give details about the location of the long press:
*   `global_x`: The x-coordinate of the pointer's position on the screen.
*   `global_y`: The y-coordinate of the pointer's position on the screen.
*   `local_x`: The x-coordinate of the pointer's position relative to the control that received the event.
*   `local_y`: The y-coordinate of the pointer's position relative to the control that received the event.

There is also a corresponding `LongPressEndEvent`, which is fired when the pointer that initiated the long press is lifted from the screen.
