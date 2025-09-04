# PageMediaData

In the Flet framework, `PageMediaData` is a type that provides details about the application's media environment, specifically the screen or window where the Flet app is running. It is analogous to `MediaQueryData` in Flutter, the underlying UI framework that powers Flet.

You can access `PageMediaData` through the `media` property of a `Page` object. This data typically includes read-only properties such as the `width` and `height` of the web page or the content area of a native OS window containing the Flet app. These properties are often used within the `page.on_resized` event handler to respond to changes in the application's display dimensions.
