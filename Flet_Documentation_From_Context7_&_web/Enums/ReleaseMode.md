# ReleaseMode

The `ReleaseMode` enum in Flet defines how audio resources are handled after playback. It has the following values:

*   **LOOP**: Keeps buffered data and plays it again after completion, creating a loop. When using this mode, calling the `stop()` method is not sufficient to release the resources.
*   **RELEASE**: Releases all resources, similar to calling `Audio.release()` method. In Android, this is particularly useful as the media player is resource-intensive. Data will be buffered again when needed (e.g., if it's a remote file, it will be downloaded again). In iOS and macOS, it functions similarly to the `stop()` method.
*   **STOP**: Stops audio playback but keeps all resources intact. This mode is useful if you intend to play the audio again later.
