# ScrollMode

The `ScrollMode` enum in Flet defines how scrolling is handled for scrollable controls. It determines whether a scrollbar is visible and when it appears.

Here are the possible values for `ScrollMode`:
*   **`None`**: The control is non-scrollable, and its content may overflow if it exceeds the available space.
*   **`AUTO`**: Scrolling is enabled, and the scrollbar is only shown when scrolling actually occurs.
*   **`ADAPTIVE`**: Scrolling is enabled, and the scrollbar is always shown when the application is running as a web or desktop app.
*   **`ALWAYS`**: Scrolling is enabled, and the scrollbar is always visible.
*   **`HIDDEN`**: Scrolling is enabled, but the scrollbar itself is always hidden.

`ScrollMode` can be applied to various Flet controls that support scrolling, such as `Page`, `View`, `Column`, `Row`, `ListView`, and `GridView`.
