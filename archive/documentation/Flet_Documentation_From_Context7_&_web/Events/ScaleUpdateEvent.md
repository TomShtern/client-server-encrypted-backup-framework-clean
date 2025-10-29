# ScaleUpdateEvent

In Flet, `ScaleUpdateEvent` is a class that represents an event triggered during a scaling gesture, such as pinching in or out on a touchscreen. It provides various properties to describe the state of the scaling gesture.

Key properties of the `ScaleUpdateEvent` include:
*   **`focal_point_x`** and **`focal_point_y`**: The x and y components of the focal point of the pointers (e.g., fingers) in contact with the screen.
*   **`focal_point_delta_x`** and **`focal_point_delta_y`**: The change in the x and y components of the gesture's focal point since the previous update.
*   **`local_focal_point_x`** and **`local_focal_point_y`**: Similar to `focal_point_x` and `focal_point_y`, but in the local coordinate space of the event receiver.
*   **`pointer_count`**: The number of pointers currently being tracked by the gesture recognizer.
*   **`horizontal_scale`**: The scaling factor implied by the average horizontal distance between the pointers.
*   **`vertical_scale`**: The scaling factor implied by the average vertical distance between the pointers.
*   **`scale`**: The overall scaling factor implied by the average distance between the pointers. This value is of type `float`.
