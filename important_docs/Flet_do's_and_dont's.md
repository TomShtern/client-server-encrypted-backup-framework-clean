Flet Best Practices: Do's and Don'ts (Quick Reference)

This guide provides concise recommendations for working with Flet, highlighting common pitfalls and idiomatic approaches to prevent over-engineering and ensure efficient development.

### UI Updates & State Management

- **DON'T:** Manually re-render UI components or implement complex state propagation logic.
- **DO:** Update control properties directly and call `control.update()` or `page.update()`. Flet's reactive nature efficiently handles UI refreshes.
- **DON'T:** Re-create and re-add entire controls or large sections of your UI when only a small part needs to change.
- **DO:** Directly update the specific properties of the controls that need modification (e.g., `text_control.value = "New Text"`) and then call `control.update()` or `page.update()`. Flet's efficient diffing mechanism minimizes re-rendering.

### Layout & Responsiveness

- **DON'T:** Attempt pixel-perfect positioning or complex manual calculations for responsive layouts.
- **DO:** Leverage Flet's flexible layout controls (`Row`, `Column`, `Container`, `Stack`, `ResponsiveRow`) and their `alignment`, `spacing`, and `expand` properties.

### Event Handling

- **DON'T:** Implement custom event loops or polling for user interactions.
- **DO:** Utilize Flet's extensive set of built-in event handlers (e.g., `on_click`, `on_change`, `on_submit`, `on_resized`, `on_event`) directly on controls.
- **DON'T:** Trigger expensive operations (e.g., API calls, complex calculations) on every rapid user input event (e.g., `on_change` for a `TextField` during typing).
- **DO:** Implement debouncing or throttling logic (at the Python level) for such events to limit the frequency of calls, ensuring a smooth and responsive user experience.

### Theming & Styling

- **DON'T:** Hardcode colors and styles throughout your application, especially for light/dark modes.
- **DO:** Use Flet's `page.theme`, `page.dark_theme`, `color_scheme_seed`, and the `ft.Colors` / `ft.CupertinoColors` enums for consistent Material Design styling and easy theme switching.
- **DON'T:** Only focus on `bgcolor` and `color` for theming, leading to inconsistent typography and component styles.
- **DO:** Leverage Flet's comprehensive theming capabilities by defining `ft.TextTheme` for consistent typography, and customizing `ft.Theme` properties for component-specific styles (e.g., `ElevatedButton` styles) to achieve a unified and professional look.

### Window Management

- **DON'T:** Rely on external libraries or OS-specific calls for basic window control (size, position, title, resizable, always-on-top) or handling window events (close, resize).
- **DO:** Use the `page.window` object and its properties, along with `page.on_resized` and `page.window.on_event` for comprehensive window management.

### Data Modeling

- **DON'T:** Write boilerplate `__init__`, `__repr__`, `__eq__` methods for simple data-holding classes.
- **DO:** Use Python's built-in `dataclasses` module (`@dataclass`) to create clean, concise, and automatically generated data models.

### File Operations & Storage

- **DON'T:** Implement custom file dialogs or platform-specific file selection logic.
- **DO:** Utilize Flet's `FilePicker` control for a cross-platform and integrated way to allow users to select files or directories.
- **DON'T:** Manually manage local storage or session-specific data using external file operations or complex state management.
- **DO:** Use `page.client_storage` for persistent, client-side key-value storage and `page.session` for data that persists only for the current user session.
- **DON'T:** Hardcoding absolute file paths for images, fonts, or other assets, or manually managing their loading.
- **DO:** Utilize Flet's `assets` folder for all application resources. Reference them using relative paths (e.g., `Image(src="images/my_image.png")`), and Flet will handle their packaging and loading efficiently.

### Audio Resource Management

- **DON'T:** Manually handle the release or looping of audio resources in a complex way.
- **DO:** Use the `ReleaseMode` enum (`LOOP`, `RELEASE`, `STOP`) with Flet's audio controls to define how audio resources are managed after playback.

### Advanced UI Patterns

- **DON'T:** Implement complex, manual navigation logic using conditional rendering or managing view stacks yourself.
- **DO:** Use Flet's built-in routing (`page.route`, `page.go()`, `ft.View` stack) for declarative and efficient navigation between different screens/views of your application.
- **DON'T:** Implement manual animation loops or relying on external animation libraries for simple UI transitions.
- **DO:** Leverage Flet's animation capabilities (e.g., `ft.AnimatedSwitcher`, `ft.Container`'s `animate` properties, `ft.Animation` class) for smooth and declarative UI animations.
- **DON'T:** Copy-pasting similar UI code blocks or creating complex functions to generate repetitive UI elements.
- **DO:** Create reusable custom controls by subclassing `ft.Control` or composing existing Flet controls into new classes, promoting modularity and maintainability.
- **DON'T:** Try to access controls by their `id` property or by traversing the control tree manually for updates.
- **DO:** Use `ft.Ref` objects to get direct references to controls, allowing for easy and type-safe manipulation of their properties.
- **DON'T:** Build large, monolithic UI structures within a single function or class, making them difficult to read, maintain, and reuse.
- **DO:** Break down your UI into smaller, self-contained, and reusable components (e.g., custom `ft.Control` subclasses or functions returning `ft.Control` instances). This promotes modularity, testability, and easier collaboration.
- **DON'T:** Implement separate `Text` controls or complex logic to display validation errors for input fields.
- **DO:** Utilize the `error_text` property available on many input controls (e.g., `ft.TextField`, `ft.Dropdown`) to provide immediate, context-aware validation feedback directly below the problematic input.
- **DON'T:** Use `ft.Ref` for every control in your application, which can add unnecessary overhead and complexity.
- **DO:** Reserve `ft.Ref` for controls whose properties or methods you need to access or modify dynamically *after* they have been added to the page. For static or initial setup, direct property assignment is sufficient.

### Performance & Debugging

- **DON'T:** Perform network requests, heavy computations, or file I/O directly within event handlers or the main UI loop. This will freeze your application.
- **DO:** Always wrap such operations in `async` functions and use `await` with Flet's `page.run_task()` or `page.run_thread()` to run them in the background, keeping your UI responsive.
- **DON'T:** Design separate UIs or writing extensive conditional code for different desktop operating systems (Windows, macOS, Linux).
- **DO:** Embrace Flet's Flutter-based rendering, which inherently provides a consistent UI across platforms. Focus on responsive design principles within Flet's layout system rather than platform-specific UI elements.
- **DON'T:** Let unhandled exceptions crash your application silently or providing cryptic error messages to the user.
- **DO:** Implement robust error handling using `try-except` blocks, and provide clear, user-friendly feedback (e.g., using `SnackBar`, `AlertDialog`, or updating status text) for operations that might fail.
- **DON'T:** Relying solely on trial-and-error or adding numerous border colors to debug complex layout problems.
- **DO:** Leverage Flet's visual debugging tools (e.g., `page.show_semantics_debugger` if available, or simply inspecting the control tree structure and properties in your code) to understand how controls are positioned and sized.

✦ I'll add nuanced advice on control lifecycle, component-specific theming, basic accessibility, Python library integration, and hot reload for development. These cover common pitfalls and powerful, often overlooked, Flet features. I will add these five points, categorizing them appropriately.

This guide provides concise recommendations for working with Flet, highlighting common pitfalls and idiomatic approaches to prevent over-engineering and ensure efficient development.

### UI Updates & State Management

- **DON'T:** Manually re-render UI components or implement complex state propagation logic.
- **DO:** Update control properties directly and call `control.update()` or `page.update()`. Flet's reactive nature efficiently handles UI refreshes.
- **DON'T:** Re-create and re-add entire controls or large sections of your UI when only a small part needs to change.
- **DO:** Directly update the specific properties of the controls that need modification (e.g., `text_control.value = "New Text"`) and then call `control.update()` or `page.update()`. Flet's efficient diffing mechanism minimizes re-rendering.
- **DON'T:** Manually manage the `controls` list of a parent control by appending/removing elements and then calling `update()` without considering the control's lifecycle. This can lead to unexpected behavior or performance issues if not done correctly.
- **DO:** Understand that Flet manages the lifecycle of controls added to `page.add()` or a parent control's `controls` list. When dynamically adding or removing controls, ensure you modify the `controls` list of the parent and then call `parent_control.update()` (or `page.update()` if it's a top-level change). For complex dynamic lists, consider `ft.ListView` or `ft.GridView` which are optimized for this.

### Layout & Responsiveness

- **DON'T:** Attempt pixel-perfect positioning or complex manual calculations for responsive layouts.
- **DO:** Leverage Flet's flexible layout controls (`Row`, `Column`, `Container`, `Stack`, `ResponsiveRow`) and their `alignment`, `spacing`, and `expand` properties.

### Event Handling

- **DON'T:** Implement custom event loops or polling for user interactions.
- **DO:** Utilize Flet's extensive set of built-in event handlers (e.g., `on_click`, `on_change`, `on_submit`, `on_resized`, `on_event`) directly on controls.
- **DON'T:** Trigger expensive operations (e.g., API calls, complex calculations) on every rapid user input event (e.g., `on_change` for a `TextField` during typing).
- **DO:** Implement debouncing or throttling logic (at the Python level) for such events to limit the frequency of calls, ensuring a smooth and responsive user experience.

### Theming & Styling

- **DON'T:** Hardcode colors and styles throughout your application, especially for light/dark modes.
- **DO:** Use Flet's `page.theme`, `page.dark_theme`, `color_scheme_seed`, and the `ft.Colors` / `ft.CupertinoColors` enums for consistent Material Design styling and easy theme switching.
- **DON'T:** Only focus on `bgcolor` and `color` for theming, leading to inconsistent typography and component styles.
- **DO:** Leverage Flet's comprehensive theming capabilities by defining `ft.TextTheme` for consistent typography, and customizing `ft.Theme` properties for component-specific styles (e.g., `ElevatedButton` styles) to achieve a unified and professional look.
- **DON'T:** Overriding individual style properties on every instance of a control (e.g., setting `ElevatedButton`'s `bgcolor` and `color` repeatedly).
- **DO:** Define component-specific styles within your `page.theme` (e.g., `page.theme.elevated_button_theme = ft.ElevatedButtonTheme(...)`). This allows for consistent styling across all instances of a control type and simplifies global style changes.

### Window Management

- **DON'T:** Rely on external libraries or OS-specific calls for basic window control (size, position, title, resizable, always-on-top) or handling window events (close, resize).
- **DO:** Use the `page.window` object and its properties, along with `page.on_resized` and `page.window.on_event` for comprehensive window management.

### Data Modeling

- **DON'T:** Write boilerplate `__init__`, `__repr__`, `__eq__` methods for simple data-holding classes.
- **DO:** Use Python's built-in `dataclasses` module (`@dataclass`) to create clean, concise, and automatically generated data models.

### File Operations & Storage

- **DON'T:** Implement custom file dialogs or platform-specific file selection logic.
- **DO:** Utilize Flet's `FilePicker` control for a cross-platform and integrated way to allow users to select files or directories.
- **DON'T:** Manually manage local storage or session-specific data using external file operations or complex state management.
- **DO:** Use `page.client_storage` for persistent, client-side key-value storage and `page.session` for data that persists only for the current user session.
- **DON'T:** Hardcoding absolute file paths for images, fonts, or other assets, or manually managing their loading.
- **DO:** Utilize Flet's `assets` folder for all application resources. Reference them using relative paths (e.g., `Image(src="images/my_image.png")`), and Flet will handle their packaging and loading efficiently.

### Audio Resource Management

- **DON'T:** Manually handle the release or looping of audio resources in a complex way.
- **DO:** Use the `ReleaseMode` enum (`LOOP`, `RELEASE`, `STOP`) with Flet's audio controls to define how audio resources are managed after playback.

### Advanced UI Patterns

- **DON'T:** Implement complex, manual navigation logic using conditional rendering or managing view stacks yourself.
- **DO:** Use Flet's built-in routing (`page.route`, `page.go()`, `ft.View` stack) for declarative and efficient navigation between different screens/views of your application.
- **DON'T:** Implement manual animation loops or relying on external animation libraries for simple UI transitions.
- **DO:** Leverage Flet's animation capabilities (e.g., `ft.AnimatedSwitcher`, `ft.Container`'s `animate` properties, `ft.Animation` class) for smooth and declarative UI animations.
- **DON'T:** Copy-pasting similar UI code blocks or creating complex functions to generate repetitive UI elements.
- **DO:** Create reusable custom controls by subclassing `ft.Control` or composing existing Flet controls into new classes, promoting modularity and maintainability.
- **DON'T:** Try to access controls by their `id` property or by traversing the control tree manually for updates.
- **DO:** Use `ft.Ref` objects to get direct references to controls, allowing for easy and type-safe manipulation of their properties.
- **DON'T:** Build large, monolithic UI structures within a single function or class, making them difficult to read, maintain, and reuse.
- **DO:** Break down your UI into smaller, self-contained, and reusable components (e.g., custom `ft.Control` subclasses or functions returning `ft.Control` instances). This promotes modularity, testability, and easier collaboration.
- **DON'T:** Implement separate `Text` controls or complex logic to display validation errors for input fields.
- **DO:** Utilize the `error_text` property available on many input controls (e.g., `ft.TextField`, `ft.Dropdown`) to provide immediate, context-aware validation feedback directly below the problematic input.
- **DON'T:** Use `ft.Ref` for every control in your application, which can add unnecessary overhead and complexity.
- **DO:** Reserve `ft.Ref` for controls whose properties or methods you need to access or modify dynamically *after* they have been added to the page. For static or initial setup, direct property assignment is sufficient.

### Performance & Debugging

- **DON'T:** Perform network requests, heavy computations, or file I/O directly within event handlers or the main UI loop. This will freeze your application.
- **DO:** Always wrap such operations in `async` functions and use `await` with Flet's `page.run_task()` or `page.run_thread()` to run them in the background, keeping your UI responsive.
- **DON'T:** Design separate UIs or writing extensive conditional code for different desktop operating systems (Windows, macOS, Linux).
- **DO:** Embrace Flet's Flutter-based rendering, which inherently provides a consistent UI across platforms. Focus on responsive design principles within Flet's layout system rather than platform-specific UI elements.
- **DON'T:** Let unhandled exceptions crash your application silently or providing cryptic error messages to the user.
- **DO:** Implement robust error handling using `try-except` blocks, and provide clear, user-friendly feedback (e.g., using `SnackBar`, `AlertDialog`, or updating status text) for operations that might fail.
- **DON'T:** Relying solely on trial-and-error or adding numerous border colors to debug complex layout problems.
- **DO:** Leverage Flet's visual debugging tools (e.g., `page.show_semantics_debugger` if available, or simply inspecting the control tree structure and properties in your code) to understand how controls are positioned and sized.

### Accessibility

- **DON'T:** Neglect accessibility features, making your application difficult for users with disabilities.
- **DO:** Utilize Flet's built-in accessibility properties where available (e.g., `tooltip` for buttons, `semantics_label` for images, `tab_index` for keyboard navigation) to provide a more inclusive user experience.

### Integration with Python Ecosystem

- **DON'T:** Try to force non-UI Python libraries to directly interact with Flet's UI elements in a blocking or non-idiomatic way.
- **DO:** Design clear interfaces between your Flet UI and your backend Python logic. Use Flet's asynchronous capabilities (`page.run_task`, `page.run_thread`) to run long-running Python computations in the background, and update the UI via `page.update()` or `control.update()` when results are ready.

### Development Workflow

- **DON'T:** Constantly restarting your Flet application for every small code change during development.
- **DO:** Leverage Flet's hot reload feature (by running your app with `ft.app(target=main, view=ft.AppView.WEB_BROWSER)` or similar development modes) to see changes instantly without losing application state, significantly speeding up development.