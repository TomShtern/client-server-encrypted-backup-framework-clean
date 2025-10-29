# AutoCompleteSelectEvent

In Flet, the `AutoCompleteSelectEvent` is an event that is triggered when a user selects a suggestion from the dropdown list of an `AutoComplete` control.

You can handle this event by assigning a function to the `on_select` property of the `ft.AutoComplete` control.

The `AutoCompleteSelectEvent` object, passed to your event handler, provides the following key property:
*   **`selection`**: This property holds the `AutoCompleteSuggestion` object that was selected by the user.

Additionally, the `AutoComplete` control itself has a `selected_index` property, which is the index of the selected suggestion within the `suggestions` list. This property is read-only and becomes available after a selection has been made.

Here's a basic example of how to use `AutoCompleteSelectEvent`:

```python
import flet as ft

def main(page: ft.Page):
    def on_autocomplete_select(e: ft.AutoCompleteSelectEvent):
        # Access the selected suggestion object
        selected_suggestion = e.selection
        print(f"Selected suggestion key: {selected_suggestion.key}")
        print(f"Selected suggestion value: {selected_suggestion.value}")

        # Access the selected index from the control
        print(f"Selected index: {e.control.selected_index}")

        page.add(ft.Text(f"You selected: {selected_suggestion.value}"))

    page.add(
        ft.AutoComplete(
            suggestions=[
                ft.AutoCompleteSuggestion(key="apple", value="Apple"),
                ft.AutoCompleteSuggestion(key="banana", value="Banana"),
                ft.AutoCompleteSuggestion(key="cherry", value="Cherry"),
            ],
            on_select=on_autocomplete_select,
            hint_text="Type a fruit...",
        )
    )

ft.app(target=main)
```