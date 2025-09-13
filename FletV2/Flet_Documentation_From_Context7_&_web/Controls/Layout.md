# Flet Layout Controls

Flet provides a comprehensive set of controls for building application layouts, drawing inspiration from web frameworks like Bootstrap and leveraging the power of Flutter for a consistent cross-platform experience. Here's an overview of the primary layout controls and concepts:

### Core Layout Controls

*   **`Row` and `Column`**: These are the fundamental building blocks for arranging controls. `Row` displays its children in a horizontal array, while `Column` arranges them in a vertical array. You can control alignment and spacing within these controls to structure your UI.
*   **`Container`**: A versatile control that allows you to decorate other controls with backgrounds, borders, padding, and margins. It's essential for styling and positioning elements within your layout.
*   **`Stack`**: This control positions its children on top of each other, which is useful for creating layered effects or overlaying widgets.
*   **`GridView`**: Ideal for displaying large, scrollable 2D arrays of controls, such as image galleries. It's designed for smooth scrolling and can automatically adjust content when the window size changes.
*   **`ListView`**: A scrollable list for arranging controls linearly.

### Specialized Layout Controls

*   **`Card`**: A Material Design panel with rounded corners and a shadow, perfect for grouping related information.
*   **`DataTable`**: Used for displaying data in a structured table with rows and columns.
*   **`Tabs`**: Allows for navigation between different content views using text headers.
*   **`ResponsiveRow`**: This control implements a responsive grid layout, similar to Bootstrap. It allows you to create UIs that adapt to different screen sizes by specifying how many virtual columns a control should span at various breakpoints (e.g., for mobile vs. desktop).
*   **`SafeArea`**: This control ensures its content is not obstructed by operating system elements like notches or status bars.

### Layout Concepts

*   **Control Hierarchy**: Flet UIs are built as a tree of controls. The `Page` is the top-level control, and other controls are nested within it or within other container controls.
*   **Properties**: Controls have various properties to customize their appearance and behavior, such as `width`, `height`, `padding`, `margin`, `alignment`, and `expand`. The `expand` property, for instance, allows a control to fill available space within its parent.
*   **Responsiveness**: Flet supports responsive design through the `ResponsiveRow` control and the ability to dynamically adjust layouts based on screen size. You can define different column spans for various breakpoints to create a fluid user experience across devices.
