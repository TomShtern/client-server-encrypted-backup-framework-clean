# OnReorderEvent

In Flet, `OnReorderEvent` is an event type specifically used with the `ReorderableListView` control. This event fires when a child control within a `ReorderableListView` has been dragged to a new location, indicating that the application should update the order of its items.

The `OnReorderEvent` object provides two key pieces of information:
*   `old_index`: The original index (position) of the reordered control.
*   `new_index`: The new index (position) of the reordered control after it has been dragged.

The `ReorderableListView` control enables users to reorder its child elements by dragging a handle. In addition to `on_reorder`, there are other related events:
*   `on_reorder_start`: Fires when an item drag operation begins.
*   `on_reorder_end`: Fires when the dragged item is dropped.

This functionality is available in Flet versions 0.27.0 and newer.
