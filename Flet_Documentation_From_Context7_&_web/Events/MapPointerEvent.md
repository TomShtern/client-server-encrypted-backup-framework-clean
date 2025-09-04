# MapPointerEvent

In Flet, `MapPointerEvent` is an event class specifically designed to handle pointer interactions (such as mouse clicks, touches, or pen input) with the `Map` control.

When a pointer interacts with a Flet `Map` control, a `MapPointerEvent` object is generated, providing detailed information about the interaction.

Key properties of the `MapPointerEvent` include:
*   **`coordinates`**: This property provides the geographical coordinates (latitude and longitude) on the map where the pointer made contact. The value is of type `MapLatitudeLongitude`.
*   **`device_type`**: This indicates the type of input device that generated the event, such as a mouse or a touch screen. The value is of type `PointerDeviceType`.
*   **`global_x`** and **`global_y`**: These represent the x and y coordinates of the pointer in global screen coordinates.

The `Map` control exposes several event handlers that utilize `MapPointerEvent` to allow developers to respond to user interactions:
*   **`on_pointer_down`**: Triggered when a pointer is pressed down on the map.
*   **`on_pointer_up`**: Triggered when a pointer is released from the map.
*   **`on_pointer_cancel`**: Triggered when a pointer interaction is canceled.

Other related events for the `Map` control include `on_tap`, `on_long_press`, `on_secondary_tap`, `on_hover`, and `on_position_change`, which provide different types of interaction data.

To use the `Map` control and its associated events in your Flet application, you need to include `flet-map` as a dependency in your project.
