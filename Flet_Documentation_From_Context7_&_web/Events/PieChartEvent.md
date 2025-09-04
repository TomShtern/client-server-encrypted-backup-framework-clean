# PieChartEvent

In Flet, the `PieChartEvent` is an event data instance that is triggered when a section of a `PieChart` control is hovered over or clicked. This event is handled by the `on_chart_event` property of the `PieChart`.

The `PieChartEvent` class provides the following properties to access details about the event:
*   **`section_index`**: This integer indicates the index of the pie chart section that was interacted with. If the event did not occur over any specific section (e.g., hovering over the empty space), its value will be -1.
*   **`type`**: This property specifies the type of interaction that occurred, such as `PointerHoverEvent` when the mouse hovers over a section, or `PointerExitEvent` when it leaves a section.
*   **`local_x`**: This provides the X-coordinate of the event's location relative to the `PieChart` control.
*   **`local_y`**: This provides the Y-coordinate of the event's location relative to the `PieChart` control.

Developers can use these properties within an event handler function to create interactive pie charts, for example, by changing the appearance of a section when it's hovered over.
