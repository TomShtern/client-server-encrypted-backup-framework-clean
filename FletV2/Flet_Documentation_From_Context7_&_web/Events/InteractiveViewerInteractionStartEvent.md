# InteractiveViewerInteractionStartEvent

The `Flet InteractiveViewerInteractionStartEvent` is an event that fires in the Flet framework when a user begins a pan or scale gesture on an `InteractiveViewer` control.

Here's a breakdown of what that means:

*   **`InteractiveViewer`**: This is a Flet control that allows users to pan (move around), zoom in and out, and potentially rotate its content. It's useful for displaying large images, maps, or other content that might not fit entirely on the screen at once.
*   **`on_interaction_start`**: This is an event handler property of the `InteractiveViewer` control. You can assign a function to this property, and that function will be called whenever the user starts an interaction (pan or scale) with the `InteractiveViewer`.
*   **`InteractiveViewerInteractionStartEvent`**: This is the type of event object that is passed as an argument to the `on_interaction_start` event handler function. It contains information about the interaction that just started.

According to the Flet documentation, `InteractiveViewerInteractionStartEvent` is a dataclass that inherits from `ScaleStartEvent`. It provides information about the focal point of the interaction in both global and local coordinates.

In essence, if you want to perform an action (e.g., log the start of an interaction, change a UI element) as soon as a user begins to pan or zoom content within an `InteractiveViewer` in your Flet application, you would use the `on_interaction_start` event and handle the `InteractiveViewerInteractionStartEvent`.
