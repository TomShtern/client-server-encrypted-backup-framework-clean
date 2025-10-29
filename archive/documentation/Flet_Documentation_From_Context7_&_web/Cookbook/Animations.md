# Animations

Flet offers a straightforward way to add animations to your application, primarily through "implicit animations." You can also incorporate more complex animations using specialized controls.

### Implicit Animations

With implicit animations, you can animate a control's property to a target value. When the target value changes, Flet automatically animates the property from the old value to the new one over a specified duration.

To enable implicit animations, you can set a control's `animate_*` properties. The available properties for most controls are:

*   `animate_opacity`
*   `animate_rotation`
*   `animate_scale`
*   `animate_offset`
*   `animate_position`
*   `animate` (for `Container` controls)

#### Configuring Animations

You can configure these `animate_*` properties in a few ways:

*   **Boolean:** Setting it to `True` enables the animation with a default duration of 1000 milliseconds and a linear curve.
*   **Integer:** Providing an integer value enables the animation with that duration in milliseconds and a linear curve.
*   **`animation.Animation` Class:** For more control, you can use an instance of the `animation.Animation` class to specify both the `duration` (in milliseconds) and the `curve`.

For example:
`animate_rotation=ft.animation.Animation(duration=300, curve="bounceOut")`

Flet supports various animation curves like `bounceOut`, `easeOutCubic`, and `linear` (the default). You can find a full list of possible curve values in the Flutter documentation.

#### Example: Opacity Animation

Here is a basic example from the Flet documentation that animates the opacity of a container when a button is clicked:

```python
import flet as ft
import time

def main(page: ft.Page):
    c = ft.Container(
        width=150,
        height=150,
        bgcolor="blue",
        border_radius=10,
        animate_opacity=300,
    )

    def animate_opacity(e):
        c.opacity = 0 if c.opacity == 1 else 1
        c.update()

    page.add(
        c,
        ft.ElevatedButton("Animate opacity", on_click=animate_opacity),
    )

ft.app(target=main)
```

In this example, the `animate_opacity` property of the container is set to `300`, meaning the opacity change will be animated over 300 milliseconds.

#### Animation End Callback

Flet controls with `animate_*` properties also have an `on_animation_end` event handler. This event is triggered when an animation completes and can be used to chain multiple animations together.

### Other Animation Controls

For more advanced scenarios, Flet provides specialized animation controls:

*   **`AnimatedSwitcher`**: A control that creates a cross-fade animation when its content is changed.
*   **`Lottie`**: Displays an animation from a Lottie file, which can be loaded from a URL or a local file.
*   **`Rive`**: Displays an animation from a Rive file, also loadable from a URL or a local file.
