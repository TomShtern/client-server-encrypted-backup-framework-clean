# MainAxisAlignment

The `MainAxisAlignment` enum in Flet defines how children widgets should be placed along the main axis of a `Row` or `Column` layout.

It has the following values:

*   **`START`**: Places the children as close to the start of the main axis as possible.
*   **`END`**: Places the children as close to the end of the main axis as possible.
*   **`CENTER`**: Places the children as close to the middle of the main axis as possible.
*   **`SPACE_BETWEEN`**: Distributes the free space evenly between the children. The first child is at the start, and the last child is at the end.
*   **`SPACE_AROUND`**: Distributes the free space evenly between the children, with half of that space before the first child and after the last child.
*   **`SPACE_EVENLY`**: Distributes the free space evenly between the children, as well as before the first child and after the last child.

**Usage Example:**

You can set the `alignment` property of `ft.Row` or `ft.Column` to one of these `MainAxisAlignment` values.

```python
import flet as ft

def main(page: ft.Page):
    def items(count):
        items = []
        for i in range(1, count + 1):
            items.append(
                ft.Container(
                    content=ft.Text(value=str(i)),
                    alignment=ft.alignment.center,
                    width=50,
                    height=50,
                    bgcolor=ft.Colors.AMBER_500,
                )
            )
        return items

    def column_with_alignment(align: ft.MainAxisAlignment):
        return ft.Column(
            [
                ft.Text(str(align), size=10),
                ft.Container(
                    content=ft.Column(items(3), alignment=align),
                    bgcolor=ft.Colors.AMBER_100,
                    height=400,
                ),
            ]
        )

    page.add(
        ft.Row(
            [
                column_with_alignment(ft.MainAxisAlignment.START),
                column_with_alignment(ft.MainAxisAlignment.CENTER),
                column_with_alignment(ft.MainAxisAlignment.END),
                column_with_alignment(ft.MainAxisAlignment.SPACE_BETWEEN),
                column_with_alignment(ft.MainAxisAlignment.SPACE_AROUND),
                column_with_alignment(ft.MainAxisAlignment.SPACE_EVENLY),
            ],
            spacing=30,
            alignment=ft.MainAxisAlignment.START,
        )
    )

ft.run(main)
```
