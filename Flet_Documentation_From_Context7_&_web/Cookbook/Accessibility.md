# Accessibility

The Flet framework, based on Flutter, offers first-class support for accessibility, leveraging the underlying operating system's features.

Key accessibility features include:
*   **Screen Readers**: Flet supports screen readers like JAWs & NVDA on desktop (macOS and Windows).
*   **Text Semantics**: You can override the default semantics of a `Text` control using the `Text.semantics_label` property.
*   **Button Semantics**: Buttons with text automatically generate proper semantics. For `IconButton`, `FloatingActionButton`, and `PopupMenuButton`, the `tooltip` property can be used to add screen reader semantics.
*   **Input Control Semantics**: `TextField.label` and `Dropdown.label` properties are used to add screen reader semantics to these controls.
*   **Custom Semantics**: For specific accessibility requirements, the `Semantics` control can be utilized.
*   **Debugging Semantics**: Flet provides a semantics debugger that can be enabled by setting `page.show_semantics_debugger` to `True`. This displays an overlay showing the accessibility information reported by the framework. A keyboard shortcut, such as `CTRL+S`, can be implemented to conveniently toggle this debugger during development.
