# Navigation and routing

Navigation and routing in Flet allow you to organize your application's user interface into virtual pages or "views" and navigate between them. This is a fundamental feature for creating applications.

Here are the core concepts:

### Page Route

The page route is a string that represents the current view. It always starts with a `/`. If no route is specified, the default route is `/`. You can access the current route using the `page.route` property.

### Handling Route Changes

You can respond to changes in the route by defining an event handler for the `page.on_route_change` event. This handler is triggered whenever the route changes programmatically.

Here is an example of how to handle route changes:

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text(f"Initial route: {page.route}"))

    def route_change(e: ft.RouteChangeEvent):
        page.add(ft.Text(f"New route: {e.route}"))

    page.on_route_change = route_change
    page.update()

ft.app(main)
```

You can also change the route programmatically by setting the `page.route` property. The `page.go(route)` method is a convenient helper that updates the route and calls the `on_route_change` handler for you.

### Page Views

A Flet `Page` can hold a stack of `View` objects in its `page.views` list. The last view in this list is the one that is currently visible to the user. This list of views effectively represents the navigation history of the application.

To navigate to a new "page," you add a new `ft.View` to the end of the `page.views` list. To go back, you pop the last view from the list.

### Building Views on Route Change

The recommended practice is to have a single function, typically your `on_route_change` handler, that is responsible for clearing and rebuilding the `page.views` list based on the current `page.route`. This ensures that the navigation history is always a direct function of the current route.

Here is a complete example demonstrating navigation between two views:

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Routes Example"

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Flet app"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.ElevatedButton("Visit Store", on_click=lambda _: page.go("/store")),
                ],
            )
        )
        if page.route == "/store":
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(title=ft.Text("Store"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(main)
```

### Route Templates

For more complex routing scenarios, Flet provides the `TemplateRoute` utility. This allows you to define routes with parameters, similar to what you might find in web frameworks like Express.js (e.g., `/account/:account_id/orders/:order_id`).
