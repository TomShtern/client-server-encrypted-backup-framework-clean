# TapEvent

In Flet, a `TapEvent` represents a user's tap action on a control. It is a class that provides detailed information about the tap, such as its coordinates and the type of device that initiated it.

Key properties of a `TapEvent` include:
*   `global_x`: The x-coordinate of the tap in global screen coordinates.
*   `global_y`: The y-coordinate of the tap in global screen coordinates.
*   `local_x`: The x-coordinate of the tap relative to the control that was tapped.
*   `local_y`: The y-coordinate of the tap relative to the control that was tapped.
*   `kind`: The type of device that initiated the event (e.g., mouse, touch).

You typically handle `TapEvent`s by assigning an event handler (a Python function) to a control's tap-related property. For example, while buttons commonly use `on_click`, other controls or more general tap detection can involve `GestureDetector`'s `on_tap` property. When a tap occurs, the assigned event handler function is called, and a `TapEvent` object is passed as an argument to this function, allowing you to access its properties.

After making any changes to the UI within an event handler, you must call `page.update()` to ensure those changes are reflected in the application.
