# ScaleEndEvent

`Flet ScaleEndEvent` is an event in the Flet UI framework that is triggered when a scaling gesture concludes. It provides details about the state of the gesture at the moment it ends.

The `ScaleEndEvent` class includes the following properties:
*   `pointer_count`: This property indicates the number of pointers (e.g., fingers on a touchscreen) that were being tracked by the gesture recognizer when the scaling gesture finished.
*   `velocity_x`: This represents the x-component of the velocity of the last pointer to leave the screen.
*   `velocity_y`: This represents the y-component of the velocity of the last pointer to leave the screen.

This event is part of a set of scaling-related events in Flet, which also includes `ScaleStartEvent` (when a scaling gesture begins) and `ScaleUpdateEvent` (which provides updates as the scaling gesture progresses).
