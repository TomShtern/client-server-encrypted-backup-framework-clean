

# Flet 0.28.3: The AI Coding Agent's Handbook for Flawless Applications

## Objective

This document provides a comprehensive set of guidelines, best practices, and anti-patterns for an AI coding agent to generate high-quality, robust, and maintainable Flet 0.28.3 applications. Adherence to these principles will ensure the resulting code is efficient, error-resistant, and leverages the full potential of the Flet framework.

## Core Tenets of Flet Development

Understanding these fundamental principles is paramount for effective Flet programming.

1.  **Imperative UI with Explicit Updates**: Flet employs an imperative UI paradigm. Modifications to control properties (e.g., `text.value = "new text"`) are not automatically reflected in the user interface. The developer must explicitly trigger an update.
    *   **Best Practice**: For changes to a specific, already-rendered control, use `control.update()`. This is more performant as it targets only the modified control.
    *   **Usage**: `control.update()` is called on the control instance whose properties have changed.
    *   **Alternative**: `page.update()` refreshes the entire page (or the relevant subtree). Use this when multiple, disparate controls have been modified, or for initial UI setup via `page.add()`. Overuse of `page.update()` for single-control changes can lead to unnecessary rendering work.
    *   **Example**:
        ```python
        import flet as ft

        def main(page: ft.Page):
            txt = ft.Text("Hello")
            page.add(txt) # Initial add, UI updates automatically

            def change_text(e):
                txt.value = "World"
                txt.update() # CORRECT: Update only the changed control

            page.add(ft.ElevatedButton("Change", on_click=change_text))
        ft.app(target=main)
        ```

2.  **Single-Threaded UI with Asynchronous Concurrency**: The Flet UI runs on a single main thread. Long-running synchronous operations (e.g., network requests, file I/O, heavy computations) executed in this thread will freeze the entire application UI, leading to an unresponsive user experience.
    *   **Best Practice**: Offload long-running tasks using Python's `asyncio` library. Define event handlers as `async def` and use `await` for non-blocking operations.
    *   **Example**:
        ```python
        import flet as ft
        import asyncio

        def main(page: ft.Page):
            status = ft.Text("Ready")
            page.add(status)

            async def long_task(e):
                status.value = "Working..."
                status.update()
                await asyncio.sleep(5) # Non-blocking wait
                status.value = "Done!"
                status.update()

            page.add(ft.ElevatedButton("Start Task", on_click=long_task))
        ft.app(target=main)
        ```
    *   **Avoid**: `time.sleep()`, blocking network calls, or heavy CPU-bound work directly in synchronous event handlers.

3.  **Control Hierarchy and Instance Management**: The Flet UI is structured as a tree of controls, with `ft.Page` as the root. To interact with or modify a control, you must maintain a reference to its specific instance that has been added to this tree.
    *   **Best Practice**: Define control instances that need to be modified later in a scope accessible to their event handlers (e.g., as attributes of a main app class or variables in the `main` function).
    *   **Pitfall**: Creating a new instance of a control within an event handler and modifying it will not affect the control already displayed on the page.
    *   **Example**:
        ```python
        import flet as ft

        def main(page: ft.Page):
            # CORRECT: Store reference
            display_text = ft.Text("Initial")
            page.add(display_text)

            def modify_text(e):
                display_text.value = "Modified Correctly" # Modifies existing instance
                display_text.update()

            # INCORRECT:
            # def modify_text_wrong(e):
            #     new_text = ft.Text("This is a new, unseen instance")
            #     new_text.update() # Has no effect on the original display_text

            page.add(ft.ElevatedButton("Modify", on_click=modify_text))
        ft.app(target=main)
        ```

## Project Initialization and Structure

*   **Python Version**: Flet requires Python 3.9 or newer.
*   **Dependency Management**: Always use a virtual environment.
    *   **Venv**: `python3 -m venv .venv && source .venv/bin/activate && pip install 'flet[all]'`
    *   **Poetry**: `poetry init --dev-dependency='flet[all]' --python='>=3.9' --no-interaction && poetry install --no-root`
    *   **uv**: `uv init && uv add 'flet[all]' --dev`
*   **Basic Application Structure**:
    ```python
    import flet as ft

    def main(page: ft.Page):
        # Page setup (optional)
        page.title = "My App"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.window_width = 400
        page.window_height = 600
        page.theme_mode = ft.ThemeMode.LIGHT # or DARK, or SYSTEM

        # UI Controls
        greeting = ft.Text("Hello, Flet!")
        page.add(greeting)

        # Event Handlers (defined before or after controls that use them, as long as they are in scope)
        def button_clicked(e):
            greeting.value = "Button Clicked!"
            greeting.update() # or page.update()

        page.add(ft.ElevatedButton("Click Me", on_click=button_clicked))

    if __name__ == "__main__":
        ft.app(target=main) # Runs in native window
        # For web: ft.app(target=main, view=ft.AppView.WEB_BROWSER)
    ```
*   **Running the Application**:
    *   Native OS window: `flet run your_app.py`
    *   Web browser: `flet run --web your_app.py`
    *   Using Poetry: `poetry run flet run your_app.py`
    *   Using uv: `uv run flet run your_app.py`

## UI Construction and Layout Best Practices

1.  **Common Control Properties**: Most Flet controls share these properties.
    *   `visible: bool` (default `True`): Control visibility.
    *   `disabled: bool` (default `False`): Control interactivity.
    *   `data: any`: Arbitrary user data attached to the control.
    *   `tooltip: str | ft.Tooltip`: Tooltip text or a `Tooltip` control.
    *   `width: float | None`, `height: float | None`: Control dimensions.
    *   `bgcolor: str | ft.colors`: Background color.
    *   `padding: ft.padding.PaddingValue`: Internal spacing.
    *   `margin: ft.margin.MarginValue`: External spacing (often simulated via parent spacing or a wrapping `Container`'s padding).
    *   `expand: bool | int`: Whether the control expands to fill available space in a `Column` or `Row`.
    *   `key: str | int`: Unique identifier for the control, crucial for dynamic lists.

2.  **Layout Containers**:
    *   `ft.Column`: Arranges children vertically. Use `alignment`, `spacing`, `horizontal_alignment`.
    *   `ft.Row`: Arranges children horizontally. Use `alignment`, `spacing`, `vertical_alignment`.
    *   `ft.Container`: A versatile container that can hold one child. Useful for applying `padding`, `margin` (via its own `padding` if nested), `bgcolor`, `border`, `border_radius`, and `alignment` to its content.
    *   `ft.Stack`: Overlays children. Use `top`, `left`, `right`, `bottom` to position children within the stack.
    *   `ft.ListView`: For scrollable lists of controls. Use `controls`, `spacing`, `padding`, `auto_scroll`. For performance with many items, ensure items have unique `key`s.

3.  **Spacing and Alignment**:
    *   `page.spacing`: Vertical spacing between controls directly added to the page (which acts like a `Column`).
    *   `page.padding`: Padding around the content of the page.
    *   `Column.spacing`, `Row.spacing`: Spacing between children of the `Column`/`Row`.
    *   `Column.alignment`, `Row.alignment`: Alignment of children along the main axis.
    *   `Column.horizontal_alignment`, `Row.vertical_alignment`: Alignment of children along the cross axis.
    *   `Container.padding`: Internal spacing within the `Container`.
    *   To simulate `margin` around a control, wrap it in a `Container` and apply `padding` to the outer `Container`.

4.  **Responsive Design**:
    *   **`ft.ResponsiveRow`**: The primary tool for responsive grids.
        *   Children specify `col` property: `col={"sm": 6, "md": 4, "xl": 3}` (12-column grid).
        *   `run_spacing`: Spacing between wrapped rows.
        *   **Example**:
            ```python
            page.add(
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(ft.Text("Item 1"), col={"sm": 12, "md": 6}, bgcolor=ft.colors.BLUE_100, padding=10),
                        ft.Container(ft.Text("Item 2"), col={"sm": 12, "md": 6}, bgcolor=ft.colors.GREEN_100, padding=10),
                    ]
                )
            )
            ```
    *   **`page.on_resize` Event**: For dynamic adjustments based on window size.
        *   Access `page.window_width` and `page.window_height`.
        *   **Example**:
            ```python
            def main(page: ft.Page):
                status = ft.Text()
                page.on_resize = lambda e: status.update(value=f"Size: {page.window_width}x{page.window_height}")
                page.add(status)
            ft.app(target=main)
            ```

5.  **Theming**:
    *   **Best Practice**: Use `page.theme` and `page.dark_theme` to define consistent styles.
    *   **Color Scheme**: Utilize `ft.ColorScheme` with built-in colors (e.g., `primary`, `secondary`, `surface`, `on_primary`) for consistency across light/dark modes.
    *   **Fonts**: Set `font_family` in the theme.
    *   **Example**:
        ```python
        def main(page: ft.Page):
            page.theme = ft.Theme(
                color_scheme_seed=ft.colors.INDIGO, # Generates a scheme
                # Or define explicitly:
                # color_scheme=ft.ColorScheme(primary=ft.colors.BLUE, secondary=ft.colors.GREEN),
                font_family="Arial"
            )
            page.add(ft.Text("Themed Text", style=ft.TextThemeStyle.HEADLINE_MEDIUM))
            page.add(ft.ElevatedButton("Themed Button"))
        ft.app(target=main)
        ```
    *   **Avoid**: Hardcoding hex color values or font names directly on controls unless absolutely necessary for a specific override.

6.  **Keys for Dynamic Lists**:
    *   **Rule**: When adding controls dynamically to a `ListView`, `Column`, or `Row` where items can be added, removed, or reordered, each item *must* have a unique and stable `key`.
    *   **Why**: Flet uses keys to efficiently identify and update controls. Without keys, Flet may reuse control instances incorrectly, leading to UI bugs and performance issues.
    *   **Example**:
        ```python
        def main(page: ft.Page):
            lv = ft.ListView()
            item_counter = 0

            def add_item(e):
                nonlocal item_counter
                lv.controls.append(
                    ft.ListTile(
                        key=str(item_counter), # Unique key
                        title=ft.Text(f"Item {item_counter}"),
                        on_click=lambda e, key=item_counter: print(f"Clicked {key}")
                    )
                )
                item_counter += 1
                lv.update() # or page.update()

            page.add(ft.ElevatedButton("Add Item", on_click=add_item), lv)
        ft.app(target=main)
        ```

## Handling User Interaction and State Management

1.  **Event Handlers**:
    *   **Signature**: Event handlers must accept one argument, typically `e` (the event object), even if unused.
        *   Correct: `def handle_click(e):` or `async def handle_click(e):`
        *   Incorrect: `def handle_click():`
    *   **Asynchronous Handlers**: Use `async def` if the handler performs any `await`able operations.
    *   **UI Updates**: If an event handler modifies the UI, it must call `control.update()` or `page.update()`.
    *   **Error Handling**: Wrap code in event handlers that might raise exceptions with `try...except` blocks to prevent application crashes and provide user feedback.
        *   **Example**:
            ```python
            def risky_action(e):
                try:
                    # code that might fail
                    result = 1 / 0
                except ZeroDivisionError:
                    print("Cannot divide by zero")
                    # Optionally update UI to show error
                except Exception as ex:
                    print(f"An error occurred: {ex}")
            ```

2.  **State Management Patterns**:
    *   **Simple Apps (Local State)**: For very simple applications, state can be held in local variables within the `main` function.
        *   **Example**: Counter app where the count is a variable in `main`.
    *   **Moderate Complexity (Centralized State Class/Dictionary)**:
        *   Create a class or a dictionary to hold the application's state.
        *   Pass this state object or parts of it to functions/methods that build UI or handle events.
        *   **Example**:
            ```python
            import flet as ft

            class AppState:
                def __init__(self):
                    self.items = []
                    self.input_text = ""

            def main(page: ft.Page):
                state = AppState()
                text_field = ft.TextField(label="New Item", on_change=lambda e: setattr(state, 'input_text', e.control.value))
                list_view = ft.ListView()

                def add_item(e):
                    if state.input_text:
                        state.items.append(state.input_text)
                        list_view.controls.append(ft.ListTile(title=ft.Text(state.input_text)))
                        list_view.update()
                        text_field.value = ""
                        text_field.update()

                page.add(text_field, ft.ElevatedButton("Add", on_click=add_item), list_view)
            ft.app(target=main)
            ```
    *   **High Complexity (Custom Controls/Components)**:
        *   For larger apps, encapsulate UI and logic into reusable custom control classes. These classes can manage their own internal state and expose methods for interaction.
        *   **Example**:
            ```python
            class UserCard(ft.Container):
                def __init__(self, name: str, email: str, on_delete_callback):
                    super().__init__()
                    self.name = name
                    self.email = email
                    self.on_delete_callback = on_delete_callback
                    self.padding = 10
                    self.margin = ft.margin.only(bottom=10)
                    self.bgcolor = ft.colors.GREY_200
                    self.content = ft.Column([
                        ft.Text(self.name, weight=ft.FontWeight.BOLD),
                        ft.Text(self.email),
                        ft.ElevatedButton("Delete", on_click=self.delete_user)
                    ])

                def delete_user(self, e):
                    self.on_delete_callback(self) # Pass self or an identifier

            # Usage in main:
            # def delete_card_handler(card_to_delete):
            #     page.controls.remove(card_to_delete)
            #     page.update()
            #
            # page.add(UserCard("John Doe", "john@example.com", delete_card_handler))
            ```
    *   **Avoid Global State for UI**: Relying on global variables for UI-related state can make code hard to debug and maintain. Prefer passing state explicitly or using classes.

## Performance and Memory Management

1.  **Efficient UI Updates**:
    *   **`control.update()`**: Use for updating a single, specific control after its properties change. This is the most efficient way to update the UI.
    *   **`page.update()`**: Use when multiple, unrelated controls have been modified, or after a batch operation affecting many parts of the UI. It triggers a broader diff and update cycle.
    *   **Batching Control Additions**:
        *   **Inefficient**: Multiple calls to `page.add()` in a loop.
            ```python
            # Inefficient
            for i in range(100):
                page.add(ft.Text(f"Item {i}")) # Each add() triggers an update
            ```
        *   **Efficient**: Append to `page.controls` (or a container's `controls`) and then call `update()` once.
            ```python
            # Efficient
            new_controls = [ft.Text(f"Item {i}") for i in range(100)]
            page.controls.extend(new_controls)
            page.update() # Single update
            ```

2.  **Preventing Memory Leaks**:
    *   **Dynamic Control Removal**: When you remove a control from the UI tree (e.g., `page.controls.remove(some_control)` or `list_view.controls.pop(index)`), Flet handles the cleanup on the client-side (Flutter).
    *   **Python-Side References**: Ensure your Python code does not hold onto strong references to removed controls in data structures (like lists or dictionaries) if those references are no longer needed and might prevent Python's garbage collector from reclaiming memory. This is especially relevant if the controls or their event handlers capture large amounts of data in closures.
        *   **Example**: If you maintain a list of all dynamically created cards and their associated data, ensure you also remove items from this list when the card is removed from the UI.
    *   **Event Handlers in Dynamic Controls**: If an event handler of a dynamically created control captures a reference to a large object, be mindful of this when the control is removed. While Flet removes the UI element, the Python closure might still hold references. In complex scenarios, you might need to design your handlers to be more stateless or explicitly clear references.

3.  **`ListView` Optimization**:
    *   **Unique Keys**: As mentioned, always provide unique `key`s for items. This is crucial for `ListView` to efficiently manage its children.
    *   **`item_extent`**: If all items in a `ListView` have a known, fixed height (or width for horizontal lists), setting `item_extent` can significantly improve scrolling performance by allowing `ListView` to calculate the total scrollable extent without measuring every item.
        *   **Example**: `lv = ft.ListView(item_extent=50)` if each item is 50 logical pixels tall.
    *   **Virtualization**: For extremely large datasets (thousands of items), consider implementing your own virtualization (only rendering items currently visible or near the viewport) if `ListView`'s performance is still not sufficient, though Flet's `ListView` is generally well-optimized.

## Advanced Topics and Robustness

1.  **Navigation**:
    *   **`page.views` and `page.go(route)`**: For multi-page applications, Flet provides a routing system.
        *   `page.views` is a list of `View` objects.
        *   Each `View` has a `route` (e.g., "/settings") and `controls`.
        *   `page.go("/settings")` changes the current view.
        *   Handle `page.on_view_pop` for back button behavior.
        *   **Example**:
            ```python
            def main(page: ft.Page):
                def view_pop_handler(view):
                    page.views.pop()
                    page.update()

                page.on_view_pop = view_pop_handler

                def route_change_handler(route):
                    page.views.clear()
                    if page.route == "/":
                        page.views.append(ft.View("/", [ft.Text("Home"), ft.ElevatedButton("Go to Settings", on_click=lambda _: page.go("/settings"))]))
                    elif page.route == "/settings":
                        page.views.append(ft.View("/settings", [ft.Text("Settings"), ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/"))]))
                    page.update()

                page.on_route_change = route_change_handler
                page.go(page.route) # Initial route
            ft.app(target=main)
            ```
    *   **Conditional Rendering**: For simpler navigation or tab-like interfaces, you can conditionally show/hide `Container`s or `Column`s based on application state.

2.  **Error Handling**:
    *   **Local `try...except`**: Wrap specific operations that might fail (e.g., file operations, network requests, parsing user input).
    *   **Global `page.on_error`**: Assign a function to `page.on_error` to catch unhandled exceptions that occur during the Flet application's lifecycle. This can be used for logging or displaying a generic error message to the user.
        *   **Example**:
            ```python
            def main(page: ft.Page):
                def on_error_handler(e):
                    print(f"Unhandled Flet error: {e}")
                    # Optionally show a user-friendly snackbar or dialog
                    page.snack_bar = ft.SnackBar(content=ft.Text("An unexpected error occurred."))
                    page.snack_bar.open = True
                    page.update()

                page.on_error = on_error_handler
                # ... rest of the app
            ft.app(target=main)
            ```

3.  **Page Lifecycle Events**:
    *   **`page.on_connect`**: Triggered when a new client session starts (especially relevant for web apps). Use for session-specific initializations.
    *   **`page.on_disconnect`**: Triggered when a client session ends. Crucial for cleaning up resources (e.g., database connections, subscriptions) associated with that session to prevent memory leaks and resource exhaustion on the server.
    *   **Example**:
        ```python
        def main(page: ft.Page):
            def on_connect_handler(e):
                print(f"Client connected: {e.client_id}")
                # Initialize session data, start background tasks for this client

            def on_disconnect_handler(e):
                print(f"Client disconnected: {e.client_id}")
                # Clean up resources for this client

            page.on_connect = on_connect_handler
            page.on_disconnect = on_disconnect_handler
            # ... UI ...
        ft.app(target=main, view=ft.AppView.WEB_BROWSER) # Important for web
        ```

4.  **Platform Considerations**:  WE ARE USING WINDOWS 11, SO NOT SURE IF ITS RELEVANT!
    *   **Linux**: Ensure system dependencies for Flutter are installed if you encounter issues. Refer to Flet's Linux setup guide.
    *   **Mobile (APK/IPA)**: Building mobile apps can have specific challenges.
        *   Ensure Flutter SDK is correctly configured and accessible to Flet CLI.
        *   Be prepared for longer build times.
        *   Test on real devices or emulators.
        *   Common issues include blank screens (often due to build errors or missing native dependencies) or crashes. Check Flet CLI logs and Flutter build logs.
    *   **WSL (Windows Subsystem for Linux)**: If developing on WSL, you might need to configure display forwarding or use the `--web` view mode if native window display issues arise. Flet's documentation has troubleshooting steps for "cannot open display" errors.

5.  **Modularity and Custom Controls**:
    *   **Encapsulation**: Group related UI elements and their logic into reusable components. This can be as simple as a function that returns a Flet control, or as complex as a class inheriting from a Flet control.
    *   **Custom Control Class Example (Revisited)**:
        ```python
        class TaskItem(ft.ListTile):
            def __init__(self, task_text: str, on_complete_callback, on_delete_callback):
                super().__init__()
                self.task_text = task_text
                self.on_complete_callback = on_complete_callback
                self.on_delete_callback = on_delete_callback
                self.title = ft.Text(self.task_text)
                self.trailing = ft.Row([
                    ft.IconButton(ft.icons.CHECK, on_click=self.mark_complete),
                    ft.IconButton(ft.icons.DELETE, on_click=self.delete_task),
                ])

            def mark_complete(self, e):
                self.on_complete_callback(self) # Pass self or an ID
                # Example: self.title.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                # self.update()

            def delete_task(self, e):
                self.on_delete_callback(self) # Pass self or an ID

        # In main:
        # tasks_list_view = ft.ListView()
        #
        # def handle_task_complete(task_item: TaskItem):
        #     print(f"Task '{task_item.task_text}' completed.")
        #     # task_item.title.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
        #     # task_item.update()
        #     # Or remove from list:
        #     # if task_item in tasks_list_view.controls:
        #     #     tasks_list_view.controls.remove(task_item)
        #     #     tasks_list_view.update()
        #
        # def handle_task_delete(task_item: TaskItem):
        #     if task_item in tasks_list_view.controls:
        #         tasks_list_view.controls.remove(task_item)
        #         tasks_list_view.update()
        #
        # tasks_list_view.controls.append(TaskItem("Learn Flet", handle_task_complete, handle_task_delete))
        # page.add(tasks_list_view)
        ```
    *   This approach makes the main application cleaner and individual components easier to manage and test.

## Common Pitfalls and Anti-Patterns (AI Directives)

The AI coding agent MUST avoid the following:

1.  **Forgetting `update()`**: Never modify a control's property after its initial `page.add()` without subsequently calling `control.update()` or `page.update()`.
2.  **Blocking UI Thread**: Do not perform long-running synchronous operations (like `time.sleep()`, blocking I/O, heavy computation) directly in synchronous event handlers. Use `async/await`.
3.  **Incorrect Event Handler Signature**: Always define event handlers with the `e` parameter: `def handler(e):` or `async def handler(e):`.
4.  **Modifying New Control Instances**: When intending to update an existing UI element, ensure you are modifying the control instance that is already part of the page tree, not a newly created instance.
5.  **Hardcoding Styles**: Avoid hardcoding colors (`#RRGGBB`), font sizes, or font families directly on controls. Use Flet's theming system (`page.theme`, `ft.colors`).
6.  **Neglecting Memory in Dynamic UIs**: When dynamically adding and removing many controls with event handlers, be mindful of Python-side references to prevent potential memory leaks, although Flet handles client-side cleanup upon removal from the UI tree.
7.  **Inefficient Batch Updates**: Avoid multiple consecutive calls to `page.add()` for adding several controls. Instead, use `page.controls.extend()` followed by a single `page.update()`.
8.  **Omitting Keys in Dynamic Lists**: Always provide a unique and stable `key` for each item in a dynamically generated list of controls (e.g., within a `ListView`).
9.  **Ignoring Platform-Specific Issues**: Be aware of potential build or runtime issues on different platforms (Linux, mobile, WSL) and refer to Flet documentation for troubleshooting.
10. **Poor Error Handling**: Do not let exceptions from event handlers crash the application silently or abruptly. Implement `try...except` blocks for critical operations.
11. **Using `page.update()` when `control.update()` suffices**: For targeted changes to a single control, prefer `control.update()` for better performance. Reserve `page.update()` for broader updates or when multiple controls are changed.
12. **Misusing `padding` and `margin`**: Remember `padding` is inside a control's border. "Margin" is typically achieved via `spacing` in parent containers or by wrapping a control in another `Container` and applying `padding` to the wrapper.

By internalizing these directives, the AI coding agent will be well-equipped to generate Flet 0.28.3 code that is not only functional but also adheres to industry best practices for performance, maintainability, and robustness.