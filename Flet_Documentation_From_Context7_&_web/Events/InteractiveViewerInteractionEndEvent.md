# InteractiveViewerInteractionEndEvent

The `Flet InteractiveViewerInteractionEndEvent` is an event in the Flet framework that is triggered when a user concludes an interaction, such as a pan or scale gesture, on an `InteractiveViewer` control.

Key details about this event:
*   **Trigger**: It fires specifically when the user releases their pan or scale gesture on the `InteractiveViewer`.
*   **Handler**: The `InteractiveViewer` control has an `on_interaction_end` event handler that receives an argument of type `InteractiveViewerInteractionEndEvent`.
*   **Inheritance**: The `InteractiveViewerInteractionEndEvent` class is related to `ScaleEndEvent`, indicating its connection to scaling gestures.
*   **Related Events**: Other events associated with `InteractiveViewer` interactions include `on_interaction_start` (when a gesture begins) and `on_interaction_update` (during a gesture).

This event allows developers to execute specific code or logic once a user has finished manipulating the content within an `InteractiveViewer`.
