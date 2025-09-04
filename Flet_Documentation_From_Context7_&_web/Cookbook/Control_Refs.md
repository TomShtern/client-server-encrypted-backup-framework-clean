# Control Refs

Flet controls are objects, and their properties are accessed via references (variables) to those objects. As the number of controls and event handlers grows, it becomes challenging to keep all control definitions in one place.

Flet provides a `Ref` utility class, inspired by React, to define a reference to a control.

Here's a summary of the key points:
*   Flet controls are objects, and their properties are accessed via references (variables) to those objects.
*   As the number of controls and event handlers grows, it becomes challenging to keep all control definitions in one place.
*   Flet provides a `Ref` utility class, inspired by React, to define a reference to a control.
*   A typed control reference is defined like `first_name = ft.Ref[ft.TextField]()`.
*   To access the referenced control, use the `Ref.current` property, e.g., `first_name.current.value = ""`.
*   To assign a control to a reference, set the `Control.ref` property, e.g., `ft.TextField(ref=first_name, label="First name", autofocus=True)`.
*   All Flet controls have a `ref` property.
*   Using `Ref` makes the structure of the page clearer in `page.add()` calls.
