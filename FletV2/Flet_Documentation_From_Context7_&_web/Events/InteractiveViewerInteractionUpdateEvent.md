# InteractiveViewerInteractionUpdateEvent

The `Flet InteractiveViewerInteractionUpdateEvent` is an event class within the Flet framework that is triggered by the `InteractiveViewer` control. This event provides detailed information about ongoing user interactions such as panning, zooming, and rotating content within the `InteractiveViewer`.

The `InteractiveViewer` control itself enables users to manipulate its child content through gestures, making it suitable for applications displaying maps, images, or graphs.

Key properties of the `InteractiveViewerInteractionUpdateEvent` include:
*   **`pointer_count`**: Indicates the number of active pointers (e.g., fingers) involved in the gesture.
*   **`global_focal_point`**: The central point of the interaction in global screen coordinates.
*   **`local_focal_point`**: The central point of the interaction in the local coordinate system of the `InteractiveViewer`.
*   **`scale`**: Represents the overall scaling factor resulting from the interaction.
*   **`horizontal_scale`**: The scaling factor specifically along the horizontal axis.
*   **`vertical_scale`**: The scaling factor specifically along the vertical axis.
*   **`rotation`**: The rotational change applied to the content.

This event is fired at an interval specified by the `interaction_update_interval` property of the `InteractiveViewer`, allowing developers to monitor and respond to continuous interaction updates.
