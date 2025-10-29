# DragUpdateEvent

In Flet, the `DragUpdateEvent` is an event object that provides details about a pointer's movement during a drag operation. It is typically used with `GestureDetector` controls to track continuous drag movements.

The `DragUpdateEvent` object has the following properties:
*   **`delta_x`**: The change in the x-coordinate of the pointer's position since the last update.
*   **`delta_y`**: The change in the y-coordinate of the pointer's position since the last update.
*   **`local_x`**: The x-coordinate of the pointer's local position within the coordinate system of the event receiver.
*   **`local_y`**: The y-coordinate of the pointer's local position within the coordinate system of the event receiver.
*   **`global_x`**: The x-coordinate of the pointer's global position on the screen.
*   **`global_y`**: The y-coordinate of the pointer's global position on the screen.
*   **`primary_delta`**: The amount the pointer has moved along its primary axis since the previous update.
*   **`timestamp`**: The recorded timestamp of the event.

You can use `DragUpdateEvent` with `GestureDetector`'s `on_horizontal_drag_update` or `on_vertical_drag_update` event handlers to respond to continuous dragging. Flet also provides a `drag_interval` property for `GestureDetector` to throttle these update events, which can be useful for performance in web and mobile applications.