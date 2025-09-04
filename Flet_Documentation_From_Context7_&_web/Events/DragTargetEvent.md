# DragTargetEvent

The `Flet DragTargetEvent` is a crucial component in handling drag-and-drop operations within the Flet framework. It is an event class that provides details about a draggable control interacting with a `DragTarget`.

Key properties of the `DragTargetEvent` include:
*   **`src_id`**: This is the unique control ID of the `Draggable` control that initiated the drag operation and was dropped onto the `DragTarget`. You can use `page.get_control(e.src_id)` to retrieve the actual `Control` object of the draggable.
*   **`x`**: The x-coordinate of the global position where the pointer event occurred on the draggable.
*   **`y`**: The y-coordinate of the global position where the pointer event occurred on the draggable.

`DragTargetEvent` instances are passed to various event handlers of a `DragTarget` control, allowing you to define behavior at different stages of a drag-and-drop interaction:
*   **`on_will_accept`**: This event fires when a draggable control is dragged over the `DragTarget`. The `data` field of the event indicates whether the draggable and the target belong to the same `group`, which determines if the target will accept the drop.
*   **`on_move`**: This event is triggered when a draggable control moves within the boundaries of the `DragTarget`.
*   **`on_accept`**: This is the primary event that fires when an "acceptable" draggable (i.e., one belonging to the same `group` as the `DragTarget`) is successfully dropped onto the target.