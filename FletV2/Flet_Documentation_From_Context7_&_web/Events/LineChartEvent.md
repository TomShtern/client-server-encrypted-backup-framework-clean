# LineChartEvent

In Flet, `LineChartEvent` is a class that represents events triggered by a `LineChart` control. These events typically occur when a user interacts with the chart, such as hovering over or clicking on a line or a data point.

The `LineChartEvent` object provides the following properties to give details about the interaction:
*   **`type`**: This property indicates the specific type of event that occurred, such as `PointerHoverEvent` (when the pointer hovers over an element) or `PointerExitEvent` (when the pointer leaves an element).
*   **`bar_index`**: This property refers to the index of the line that was interacted with. If no line was hovered, its value is -1.
*   **`spot_index`**: This property indicates the index of the specific data point on the line that was interacted with. If no data point was hovered, its value is -1.

You can use the `on_chart_event` property of a `LineChart` control to define a handler function that will be called when these events occur.
