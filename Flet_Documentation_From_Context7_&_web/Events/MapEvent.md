# MapEvent

In Flet, `MapEvent` is a class that represents a generic event occurring on a `Map` control. It provides detailed information about the state of the map when an event is triggered.

The `Map` control, which is part of the `flet-map` package, exposes an `on_event` property. When any map-related event occurs (such as zooming, panning, or rotation), the `on_event` handler is invoked, and a `MapEvent` object is passed as an argument.

Key properties of the `MapEvent` class include:
*   **`center`**: The geographical coordinates (latitude and longitude) of the map's center at the time of the event.
*   **`max_zoom`**: The maximum zoom level allowed for the map.
*   **`min_zoom`**: The minimum zoom level allowed for the map.
*   **`rotation`**: The rotation of the map's camera in degrees.
*   **`source`**: Indicates the origin of the event, such as user interaction or programmatic changes.
*   **`zoom`**: The current zoom level of the map.

While `MapEvent` provides general information, Flet also offers more specific event types for map interactions, such as `MapTapEvent`, `MapPointerEvent`, and `MapPositionChangeEvent`, which can be used for more granular control over user interactions like taps, long presses, and pointer movements.

To use the `Map` control and its events, you need to add `flet-map` as a dependency to your Flet project.
