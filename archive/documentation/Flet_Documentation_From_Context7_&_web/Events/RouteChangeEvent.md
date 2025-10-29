# RouteChangeEvent

In Flet, `RouteChangeEvent` is an event object that is triggered when the application's route changes. This event is crucial for managing navigation and updating the user interface in Flet applications, especially those designed as Single Page Applications (SPAs).

The `RouteChangeEvent` is passed as an argument to the `page.on_route_change` event handler. This handler is the primary place in your Flet application where you define how the UI should respond to route changes.

**When `page.on_route_change` is triggered:**

The `page.on_route_change` event handler fires whenever the route in the URL changes. This can occur due to several actions:
*   A user manually edits the URL in the browser's address bar.
*   A user navigates using the browser's "Back" or "Forward" buttons.
*   Your application programmatically changes the route using `page.go(route)`.

**Purpose and Usage:**

The main purpose of handling `RouteChangeEvent` via `page.on_route_change` is to ensure that the application's view stack (`page.views`) accurately reflects the current URL route. Inside this handler, you typically:
1.  Clear the existing views from `page.views`.
2.  Append new `ft.View` objects to `page.views` based on the `e.route` property of the `RouteChangeEvent`.
3.  Call `page.update()` to refresh the UI.

**Example of `RouteChangeEvent` usage:**

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Flet Routing Example"

    def route_change(e: ft.RouteChangeEvent):
        # The 'e.route' property contains the new route string
        page.views.clear() # Clear existing views
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Home"), bgcolor=ft.colors.BLUE_GREY_700),
                    ft.Text(f"Current route: {e.route}", size=30),
                    ft.ElevatedButton("Go to Store", on_click=lambda _: page.go("/store")),
                ],
            )
        )
        if e.route == "/store":
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(title=ft.Text("Store"), bgcolor=ft.colors.GREEN_700),
                        ft.Text(f"Welcome to the Store! Route: {e.route}", size=30),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        page.update()

    page.on_route_change = route_change
    page.go(page.route) # Initialize the view based on the initial route

ft.app(target=main)
```
