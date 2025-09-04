# WebviewJavaScriptEvent

In Flet, `WebviewJavaScriptEvent` is an event object that provides details about JavaScript-related events occurring within a `WebView` control.

This event type is typically passed as an argument to event handlers that respond to specific JavaScript interactions. For instance, it is the argument type for the `on_javascript_alert_dialog` event handler, which is triggered when a JavaScript alert dialog is about to be displayed within the `WebView`.

The `WebviewJavaScriptEvent` class contains the following key properties:
*   `message`: A string representing the JavaScript message associated with the event (e.g., the text of an alert dialog).
*   `url`: The URL of the web page where the JavaScript event originated.

To utilize the `WebView` control and its associated JavaScript events in Flet, you need to install the `flet-webview` package. The `WebView` control also allows you to execute JavaScript code within the loaded web page using the `run_javascript()` method and control JavaScript execution via properties like `javascript_enabled` (or the newer `enable_javascript`).
