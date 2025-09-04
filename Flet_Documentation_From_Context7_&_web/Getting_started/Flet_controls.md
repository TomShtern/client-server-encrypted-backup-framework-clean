# Flet controls

Flet's user interface is built using controls, which are essentially widgets. To be visible, these controls need to be added to a `Page` or nested within other controls. The `Page` acts as the root of a control tree.

Controls are Python classes, and you create instances of them by calling their constructors. For example, to create a text control, you would write:

```python
import flet as ft

t = ft.Text(value="Hello, world!", color="green")
```

To display a control, you add it to the `controls` list of a `Page` and then call `page.update()` to send the changes to the client.

Here is a simple "Hello, world!" example:
```python
import flet as ft

def main(page: ft.Page):
    t = ft.Text(value="Hello, world!", color="green")
    page.controls.append(t)
    page.update()

ft.app(main)
```

You can also modify control properties, and the UI will update on the next `page.update()` call. Some controls, like `Row`, can contain other controls, allowing you to arrange them in a specific layout.

Flet also supports event handlers for user input, such as `on_click` for buttons. This allows you to create interactive applications, like a simple to-do list.

Every control has a `visible` property (defaults to `True`) and a `disabled` property (defaults to `False`). Setting `visible` to `False` prevents the control and its children from being rendered. The `disabled` property is often used with data entry controls and can be propagated to child controls.
