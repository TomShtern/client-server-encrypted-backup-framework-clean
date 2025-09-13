# WebviewConsoleMessageEvent

The `Flet WebviewConsoleMessageEvent` is an event argument type used in the Flet framework, specifically with the `WebView` control.

It is triggered when a console message is logged within the `WebView` component. This typically occurs when JavaScript code running inside the webview uses functions like `console.log()`, `console.warn()`, or `console.error()`.

The `on_console_message` event handler of the `WebView` control receives an argument of type `WebviewConsoleMessageEvent`.

**Key characteristics:**
*   **Purpose:** Allows your Flet application to capture and react to messages logged by the web content displayed in the `WebView`.
*   **Platform Support:** This event is currently supported only on Android, iOS, and macOS platforms.
