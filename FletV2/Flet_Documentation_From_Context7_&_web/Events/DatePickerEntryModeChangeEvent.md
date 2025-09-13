# DatePickerEntryModeChangeEvent

The `DatePickerEntryModeChangeEvent` in Flet is an event that is triggered when the entry mode of a `DatePicker` control changes. This typically occurs when a user switches between the calendar view and the text input field within the date picker dialog.

Key aspects of `DatePickerEntryModeChangeEvent`:
*   **Purpose**: It signals a change in how the user is interacting with the `DatePicker` – either by selecting a date from a visual calendar or by typing it into a text field.
*   **Event Handler**: You can attach a function to the `on_entry_mode_change` property of a `DatePicker` instance. This function will be called when the entry mode changes. The event handler receives an argument of type `DatePickerEntryModeChangeEvent`.
*   **`entry_mode` Property**: The `DatePickerEntryModeChangeEvent` object contains an `entry_mode` property. This property is of type `DatePickerEntryMode` and indicates the new mode that the date picker has switched to (e.g., `DatePickerEntryMode.CALENDAR` or `DatePickerEntryMode.INPUT`).

**Example Usage (Conceptual):**

```python
import flet as ft

def main(page: ft.Page):
    def handle_entry_mode_change(e: ft.DatePickerEntryModeChangeEvent):
        print(f"Date picker entry mode changed to: {e.entry_mode}")
        # You can perform actions based on the new entry mode
        if e.entry_mode == ft.DatePickerEntryMode.INPUT:
            page.add(ft.Text("Switched to input mode!"))
        elif e.entry_mode == ft.DatePickerEntryMode.CALENDAR:
            page.add(ft.Text("Switched to calendar mode!"))

    date_picker = ft.DatePicker(
        on_entry_mode_change=handle_entry_mode_change,
        # Other DatePicker properties
    )

    page.overlay.append(date_picker)

    page.add(
        ft.ElevatedButton(
            "Open Date Picker",
            on_click=lambda _: date_picker.pick_date()
        )
    )

ft.app(target=main)
```

**Note on Older Versions**:
A known bug in Flet version 0.24.1 caused `on_entry_mode_change` to raise an `AttributeError`. This was due to an incorrect way of passing data to the `DatePickerEntryModeChangeEvent` constructor. This issue has since been resolved in newer versions of Flet.