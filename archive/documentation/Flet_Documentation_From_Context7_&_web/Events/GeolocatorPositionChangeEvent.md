# GeolocatorPositionChangeEvent

The `GeolocatorPositionChangeEvent` is a specific event object within the Flet framework, used in conjunction with the `flet-geolocator` extension to handle changes in a device's geographical position.

Key details about `GeolocatorPositionChangeEvent`:
*   **Purpose**: It serves as the argument passed to the event handler for the `on_position_change` event of the `Geolocator` control. This event is triggered whenever the device's location changes.
*   **Properties**: The `GeolocatorPositionChangeEvent` class contains two primary properties:
    *   `latitude`: The latitude of the new position in degrees.
    *   `longitude`: The longitude of the new position in degrees.
*   **Usage**: To utilize geolocation features in Flet, you first need to install the `flet-geolocator` package (e.g., using `pip install flet-geolocator`). The `Geolocator` control itself is non-visual and should be added to the `page.overlay` list in your Flet application.
*   **Cross-Platform Compatibility**: The `flet-geolocator` extension is built upon the `geolocator` Dart/Flutter package, ensuring its functionality across multiple platforms, including macOS, Windows, iOS, Android, and web environments.
