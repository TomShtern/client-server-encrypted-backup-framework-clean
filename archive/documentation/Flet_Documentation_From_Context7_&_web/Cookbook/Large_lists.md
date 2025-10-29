# Large lists

When building applications with Flet that need to display large lists of items, using `Column` and `Row` controls can lead to a lagging user interface because they render all items at once, even those not currently visible.

For better performance with hundreds or thousands of items, Flet provides two main controls that render items on demand:

*   **ListView**: This control displays items sequentially in a vertical (default) or horizontal list. To optimize scrolling performance, you can either set a fixed height for all items using the `item_extent` property or set `first_item_prototype=True` to make all items have the same extent as the first one.

*   **GridView**: This control is used for arranging items in a scrollable grid. It is significantly more performant than using a `Row` or `Column` with wrapping enabled. You can configure the grid layout by specifying a fixed number of rows/columns (`runs_count`) or by setting a maximum tile size (`max_extent`), which allows the number of columns or rows to adjust automatically. The `child_aspect_ratio` property can be used to control the shape of the grid tiles.

### Batch Updates for Large Lists

When adding a very large number of controls (e.g., thousands) to a `ListView` or `GridView`, sending them all at once in a single `page.update()` call can result in a large data transfer that may slow down the application's initial rendering.

A better approach is to add the controls in batches and call `page.update()` multiple times. For example, you can add 500 items, call `page.update()`, add the next 500, and so on. This improves the user experience by showing results progressively.

In some cases, the data for a large number of controls might exceed the default WebSocket message size limit (1 MB). If this happens, you can increase the limit by setting the `FLET_WS_MAX_MESSAGE_SIZE` environment variable to a larger value, for example, `8000000` for 8 MB.
