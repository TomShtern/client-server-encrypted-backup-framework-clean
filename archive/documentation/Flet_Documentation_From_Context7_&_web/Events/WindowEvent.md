# WindowEvent

In Flet, `WindowEvent` is a class that represents events related to the application window. It allows you to respond to various actions or changes concerning the window itself, such as closing, resizing, or gaining/losing focus.

Key aspects of `WindowEvent` in Flet:
*   **Type Property**: The `WindowEvent` object has a `type` property, which is an enumeration of type `WindowEventType`. This property indicates the specific type of window event that has occurred (e.g., `WindowEventType.CLOSE`, `WindowEventType.RESIZE`).
*   **Handling Window Events**: You can register an event handler for window events using `page.window.on_event()` or `page.on_window_event`. This handler will receive a `WindowEvent` object when a relevant window event occurs.
*   **Preventing Window Closure**: A common use case for `WindowEvent` is to intercept the native close signal of the window. By setting `page.window.prevent_close = True`, you can prevent the window from closing immediately. You can then handle the `WindowEventType.CLOSE` event to perform custom actions, such as saving user data or confirming exit, before programmatically closing the window using `page.window.destroy()`.
*   **Properties**: Besides the `type`, a `WindowEvent` object also contains properties like `control`, `data`, `name`, `page`, and `target`, providing more context about the event.

`WindowEvent` is part of Flet's comprehensive event handling system, which allows applications to react to various user interactions and system events.
