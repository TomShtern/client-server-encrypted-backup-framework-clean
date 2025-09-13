# ScaleStartEvent

In Flet, the `ScaleStartEvent` is an event in the Flet UI framework that is triggered when a scaling gesture begins. It is part of a series of events that handle multi-touch scaling, which also includes `ScaleUpdateEvent` (for ongoing scaling) and `ScaleEndEvent` (when the scaling gesture finishes).

The `ScaleStartEvent` object provides information about the initial state of the scaling gesture. Key properties of the `ScaleStartEvent` include:
*   **`focal_point_x`**: The x-component of the focal point of the pointers (e.g., fingers) in contact with the screen.
*   **`focal_point_y`**: The y-component of the focal point of the pointers in contact with the screen.
*   **`local_focal_point_x`**: The x-component of the focal point relative to the control that received the event.
*   **`local_focal_point_y`**: The y-component of the focal point relative to the control that received the event.
*   **`pointer_count`**: The number of pointers (e.g., fingers) currently being tracked by the gesture recognizer.
*   **`control`**: The Flet control that triggered the event.
*   **`data`**: Arbitrary data attached to the event.
*   **`name`**: The name of the event.
*   **`page`**: The Flet page on which the event occurred.
*   **`target`**: The target of the event.
*   **`timestamp`**: The time the event occurred.

These properties allow developers to capture the starting conditions of a scaling interaction, which can then be used to implement custom scaling logic for UI elements.
