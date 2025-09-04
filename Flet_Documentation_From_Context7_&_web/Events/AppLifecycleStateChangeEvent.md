# AppLifecycleStateChangeEvent

The `Flet AppLifecycleStateChangeEvent` is an event in the Flet framework that signals a change in the lifecycle state of a Flet application. This allows developers to execute specific logic when the application's state changes, such as when it gains or loses focus, is hidden or shown, or is about to be terminated.

The event object for `AppLifecycleStateChangeEvent` contains a `state` property, which is an enumeration of type `AppLifecycleState`. This enum defines the various possible states of the application's lifecycle:

*   **`HIDE`**: The application has become hidden. This can occur when the application is minimized on desktop.
*   **`INACTIVE`**: The application has lost input focus. Examples include another window gaining focus on desktop.
*   **`RESUME`**: The application gains input focus, meaning it is visible, active, and ready to accept user input.
*   **`SHOW`**: The application is shown, such as when it's unminimized on desktop.

You can attach a handler to the `page.on_app_lifecycle_state_change` property within your Flet application to respond to these state changes.

**Example Usage:**

```python
import flet as ft

def main(page: ft.Page):
    page.title = "App Lifecycle Demo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    status_text = ft.Text("Application Status: Initializing...")
    page.add(status_text)

    def handle_lifecycle_change(e: ft.AppLifecycleStateChangeEvent):
        """
        Handler for application lifecycle state changes.
        """
        new_state = e.data
        status_text.value = f"Application Status: {new_state.value}"
        page.update()

        if new_state == ft.AppLifecycleState.RESUME:
            print("App has resumed and is active.")
            # Perform actions when app becomes active, e.g., refresh data
        elif new_state == ft.AppLifecycleState.PAUSE:
            print("App has paused.")
            # Perform actions when app is paused, e.g., save state
        elif new_state == ft.AppLifecycleState.DETACH:
            print("App is detaching/exiting.")
            # Perform cleanup actions before app fully closes (mobile specific)
            # Note: DETACH might not always fire reliably on all platforms for cleanup.
            # For desktop app close, page.on_close might be more relevant,
            # but AppLifecycleState.DETACH is for the overall app process.
        elif new_state == ft.AppLifecycleState.HIDE:
            print("App is hidden.")
        elif new_state == ft.AppLifecycleState.SHOW:
            print("App is shown.")
        elif new_state == ft.AppLifecycleState.INACTIVE:
            print("App is inactive (lost focus).")


    # Assign the handler to the page's lifecycle event
    page.on_app_lifecycle_state_change = handle_lifecycle_change

    # Initial update to show current status
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
```
