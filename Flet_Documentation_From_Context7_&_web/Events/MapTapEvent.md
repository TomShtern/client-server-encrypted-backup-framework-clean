# MapTapEvent

In Flet, `MapTapEvent` is an event specifically designed to handle user interactions (taps or clicks) on a `Map` control. It provides detailed information about where on the map the interaction occurred.

To use the `Map` control and its associated events, you typically need to install the `flet-map` extension:
```bash
pip install flet-map
```
Then, you can import it in your Flet application, often aliased as `map` for convenience.

The `MapTapEvent` class has several key properties that provide context about the tap:
*   **`coordinates`**: This property returns the geographical latitude and longitude where the tap occurred on the map. This is particularly useful for placing markers or performing actions based on a specific location.
*   **`global_x`**, **`global_y`**: These represent the X and Y coordinates of the tap relative to the entire screen.
*   **`local_x`**, **`local_y`**: These provide the X and Y coordinates of the tap relative to the `Map` control itself.
*   **`name`**: This property indicates the type of tap event, such as `"tap"` (for a regular click), `"long_press"` (for a long press), or `"secondary_tap"` (often corresponding to a right-click).

You can attach an event handler to the `Map` control to listen for these events. The handler function will receive a `MapTapEvent` object as an argument, allowing you to access its properties and implement custom logic.

**Example of handling `MapTapEvent`:**

```python
import flet as ft
import flet_map as map
import random

def main(page: ft.Page):
    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    circle_layer_ref = ft.Ref[map.CircleLayer]()

    def handle_map_event(e: map.MapTapEvent):
        print(f"Map Event: {e.name} at Coordinates: {e.coordinates}")
        if e.name == "tap":
            # Add a marker on a regular tap
            marker_layer_ref.current.markers.append(
                map.Marker(
                    content=ft.Icon(ft.icons.LOCATION_ON, color=ft.colors.RED_500),
                    coordinates=e.coordinates,
                )
            )
        elif e.name == "long_press":
            # Add a circle marker on a long press
            circle_layer_ref.current.circles.append(
                map.CircleMarker(
                    radius=random.randint(5, 10),
                    coordinates=e.coordinates,
                    color=ft.colors.random_color(),
                    border_color=ft.colors.random_color(),
                    border_stroke_width=4,
                )
            )
        page.update()

    page.add(
        ft.Text("Click anywhere on the map to add a Marker, long-press to add a CircleMarker."),
        map.Map(
            expand=True,
            initial_center=map.MapLatitudeLongitude(15, 10),
            initial_zoom=4.2,
            # The on_event property is used to capture various map events, including taps
            on_event=handle_map_event,
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    subdomains=["a", "b", "c"],
                ),
                map.MarkerLayer(ref=marker_layer_ref, markers=[]),
                map.CircleLayer(ref=circle_layer_ref, circles=[]),
            ],
            interaction_configuration=map.MapInteractionConfiguration(
                flags=map.MapInteractiveFlag.ALL
            )
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
```
