# DragStartEvent

In Flet, the `DragStartEvent` is an event that occurs when a user begins a drag operation on a `Draggable` control. This event provides details about the starting point of the drag.

Key properties of the `DragStartEvent` include:
*   **`local_x`**: The x-coordinate of the pointer's local position within the coordinate system of the event receiver when the drag started.
*   **`local_y`**: The y-coordinate of the pointer's local position within the coordinate system of the event receiver when the drag started.
*   **`global_x`**: The x-coordinate of the pointer's global position when the drag started.
*   **`global_y`**: The y-coordinate of the pointer's global position when the drag started.
*   **`timestamp`**: The timestamp of the original pointer event that initiated the drag.

Flet's drag-and-drop functionality is built around `Draggable` and `DragTarget` controls. When a `Draggable` control is moved and released over a `DragTarget` control that shares the same "group" property, the `on_accept` event handler of the `DragTarget` is triggered. Developers can also customize the visual feedback during a drag operation using properties like `content_when_dragging` and `content_feedback` on the `Draggable` control.