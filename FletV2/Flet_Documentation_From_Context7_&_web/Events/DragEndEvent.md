# DragEndEvent

The `Flet DragEndEvent` is an event class in the Flet framework that provides information about the state of a pointer when it stops contacting the screen after a drag operation.

This event is part of Flet's drag-and-drop functionality, which typically involves `Draggable` controls (the elements being dragged) and `DragTarget` controls (the areas where elements can be dropped).

Key properties of the `DragEndEvent` class include:
*   `primary_velocity`: The velocity of the pointer along its primary axis when it stopped contacting the screen, measured in logical pixels per second.
*   `velocity_x`: The x-component of the pointer's velocity when it stopped contacting the screen.
*   `velocity_y`: The y-component of the pointer's velocity when it stopped contacting the screen.

Other related events in Flet's drag-and-drop system include `DragStartEvent` (when a drag operation begins), `DragUpdateEvent` (during the drag operation), and `DragTargetEvent` (related to the drag target).