# AudioPositionChangeEvent

The `Flet AudioPositionChangeEvent` is an event triggered by the `Audio` control in the Flet framework. This event fires continuously, typically every 1 second, when an audio file is playing, indicating that the playback position has changed.

**Key details about `AudioPositionChangeEvent`:**
*   **Purpose:** It is primarily used for updating UI elements like progress bars to reflect the current playback position of an audio file.
*   **Trigger:** The event is dispatched via the `on_position_changed` event handler of the `Audio` control.
*   **Information Provided:** The event handler receives an argument of type `AudioPositionChangeEvent`, which contains data about the current audio position, usually in milliseconds.
*   **Usage:** To utilize the `Audio` control and its associated events, you need to include `flet-audio` as a dependency in your Flet project.

The `Audio` control itself is a non-visual component that should be added to the `page.overlay` list in your Flet application.