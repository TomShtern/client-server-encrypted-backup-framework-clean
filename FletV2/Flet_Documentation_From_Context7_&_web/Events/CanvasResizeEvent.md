# CanvasResizeEvent

The `Flet CanvasResizeEvent` is an event that is triggered when the size of a `Canvas` control changes within a Flet application.

This event object provides the new dimensions of the canvas after the resize operation. It has the following properties:
*   **`height`**: The new height of the canvas.
*   **`width`**: The new width of the canvas.

You can handle this event by setting the `on_resize` property of a `ft.Canvas` control to a callback function. This function will receive an instance of `CanvasResizeEvent` as its argument, allowing you to access the updated `width` and `height`.

Additionally, the `Canvas` control has a `resize_interval` property, which specifies the sampling interval in milliseconds for the `on_resize` event. By default, it's set to 0, meaning the `on_resize` event is called immediately on every size change.