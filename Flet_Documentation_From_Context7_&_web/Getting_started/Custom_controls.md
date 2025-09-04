# Custom controls

In Flet, you can create your own reusable UI components by creating custom controls. This is a powerful feature that allows you to encapsulate UI and logic, making your apps more organized and scalable. The core concept revolves around the `ft.UserControl` class.

### Key Concepts for Creating Custom Controls

To create a custom control, you combine existing Flet controls into a new Python class that inherits from `ft.UserControl`. This class can have its own properties and methods, just like any other Python object.

Here are the essential steps:

1.  **Inherit from `ft.UserControl`**: Your custom class must inherit from `ft.UserControl` to gain the necessary functionality.
2.  **Implement the `build()` method**: This is the only required method. It must return a single control or a list of controls that make up the UI of your component. Flet calls this method automatically when your control is added to the page.
3.  **Manage State**: Store the state of your control (e.g., a counter's value, text from an input field) in instance variables (e.g., `self.value`).
4.  **Handle Events**: Define methods within your class to handle events from the child controls, such as a button click.
5.  **Call `self.update()`**: When the state of your control changes, you must call `self.update()` within your class methods. This tells Flet to re-run the `build()` method and push the changes to the UI.

---

### Example: A Reusable Counter Control

Here is a complete example of a custom counter control that demonstrates these concepts.

```python
import flet as ft
import time

class Counter(ft.UserControl):
    def __init__(self, initial_count=0):
        # Call the constructor of the parent class
        super().__init__()
        # Initialize the state
        self.counter = initial_count

    def build(self):
        # The build method returns the UI for the control
        self.text_field = ft.TextField(value=str(self.counter), text_align=ft.TextAlign.RIGHT, width=100)

        return ft.Row(
            [
                ft.IconButton(ft.icons.REMOVE, on_click=self.minus_click),
                self.text_field,
                ft.IconButton(ft.icons.ADD, on_click=self.plus_click),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def minus_click(self, e):
        # Update the state
        self.counter -= 1
        self.text_field.value = str(self.counter)
        # Push the UI update
        self.update()

    def plus_click(self, e):
        # Update the state
        self.counter += 1
        self.text_field.value = str(self.counter)
        # Push the UI update
        self.update()

def main(page: ft.Page):
    page.title = "Custom Counter Control"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Add instances of the custom control to the page
    page.add(
        Counter(),
        Counter(initial_count=10),
    )

if __name__ == "__main__":
    ft.app(target=main)
```

#### How it Works:

1.  **`Counter(ft.UserControl)`**: We define a `Counter` class that inherits from `ft.UserControl`.
2.  **`__init__(self, ...)`**: The constructor initializes the state, in this case, the `self.counter` variable. It calls `super().__init__()` to properly initialize the parent `UserControl`.
3.  **`build(self)`**: This method constructs the UI using a `Row` that contains two `IconButton` controls and a `TextField`. This UI is what will be rendered wherever you use `<Counter />`.
4.  **`minus_click` and `plus_click`**: These methods handle the `on_click` events from the buttons. They modify the `self.counter` state, update the value of the `TextField`, and then critically, call `self.update()` to make the changes visible on the page.
5.  **`main(page: ft.Page)`**: In the main application, we can now create instances of our `Counter` control just like any built-in Flet control and add them to the page.
