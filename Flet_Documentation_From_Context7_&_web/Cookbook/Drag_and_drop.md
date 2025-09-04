# Drag and drop

This document explains how to implement drag-and-drop functionality in a Flet application.

Here's a summary of the key concepts:

*   **`ft.Draggable`**: This is the control that a user can drag.
*   **`ft.DragTarget`**: This is the control where a `Draggable` can be dropped.
*   **`group`**: Both `Draggable` and `DragTarget` must belong to the same group for the drop to be accepted.
*   **`on_accept`**: This event handler on the `DragTarget` is called when a `Draggable` from the same group is dropped on it. The ID of the source `Draggable` is passed in the event data.

The developer is responsible for updating the state of both the source and destination controls within the `on_accept` handler.

The document also covers more advanced features:

*   **`content_when_dragging`**: This property of `Draggable` allows you to display a different control in its original position while it's being dragged.
*   **`content_feedback`**: This `Draggable` property lets you customize the appearance of the control being dragged under the cursor.
*   **`on_will_accept`**: A `DragTarget` event handler that is triggered when a `Draggable` enters its bounds. This can be used to provide visual feedback, like highlighting the drop zone.
*   **`on_leave`**: A `DragTarget` event handler that is triggered when a `Draggable` leaves its bounds. This can be used to remove any visual feedback.
