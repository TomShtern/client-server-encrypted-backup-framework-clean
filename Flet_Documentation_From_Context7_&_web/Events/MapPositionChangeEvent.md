# MapPositionChangeEvent

The `MapPositionChangeEvent` in Flet is an event that is fired when the position of a `Map` control changes, typically due to user interaction like panning or zooming. This event provides details about the new state of the map's view.

To use the `Map` control and its associated events, you need to install the `flet-map` extension, which can be done via pip: `pip install flet-map`.

The `MapPositionChangeEvent` class has the following properties:
*   **`coordinates`**: The geographical coordinates (latitude and longitude) at the center of the map's new view. The value is of type `MapLatitudeLongitude`.
*   **`max_zoom`**: The maximum allowed zoom level of the map.
*   **`min_zoom`**: The minimum allowed zoom level of the map.
*   **`rotation`**: The rotation, in degrees, of the map's camera.

You can handle this event by setting the `on_position_change` property of the `Map` control to a function that accepts a `MapPositionChangeEvent` object as an argument.

**Example Usage:**

```python
import flet as ft
import flet_map as map

def main(page: ft.Page):
    def handle_map_position_change(e: map.MapPositionChangeEvent):
        print(f"Map position changed:")
        print(f"  Coordinates: {e.coordinates.latitude}, {e.coordinates.longitude}")
        print(f"  Min Zoom: {e.min_zoom}")
        print(f"  Max Zoom: {e.max_zoom}")
        print(f"  Rotation: {e.rotation}")

    page.add(
        map.Map(
            expand=True,
            initial_center=map.MapLatitudeLongitude(34.0522, -118.2437), # Los Angeles
            initial_zoom=10,
            layers=[
                map.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                ),
            ],
            on_position_change=handle_map_position_change, # Attach the event handler
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
```
