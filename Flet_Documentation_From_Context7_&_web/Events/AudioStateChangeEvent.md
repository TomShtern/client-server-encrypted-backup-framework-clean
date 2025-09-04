# AudioStateChangeEvent

The `Flet AudioStateChangeEvent` is an event that fires when the state of an audio player changes within a Flet application. This event is part of the `Audio` control, which is provided by the `flet-audio` extension package.

When an `AudioStateChangeEvent` occurs, the event handler receives an argument of type `AudioStateChangeEvent`. This object contains a `state` property, which indicates the current state of the audio player. The value of this property is of type `AudioState`.

To use the `Audio` control and its associated events, you need to add `flet-audio` as a dependency to your Flet project. The `Audio` control itself is non-visual and should be added to `page.overlay`.

In addition to `on_state_changed`, the Flet `Audio` control also provides other events for monitoring audio playback, such as:
*   `on_duration_changed`: Fires when the audio duration becomes available.
*   `on_loaded`: Fires when an audio file is loaded or buffered.
*   `on_position_changed`: Fires continuously (every 1 second when playing) as the audio playback position changes.
*   `on_seek_complete`: Fires when a seek operation finishes.