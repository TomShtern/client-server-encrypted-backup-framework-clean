# TimePickerEntryModeChangeEvent

The `Flet TimePickerEntryModeChangeEvent` is an event that is triggered in the Flet framework when the entry mode of a `TimePicker` dialog changes. This typically occurs when a user switches between the clock dial input and the text input fields within the time picker.

When you attach an event handler to the `on_entry_mode_change` property of a `TimePicker` control, the handler receives an argument of type `TimePickerEntryModeChangeEvent`. This event object provides access to the new entry mode through its `entry_mode` property.

The `entry_mode` property is an enumeration of type `TimePickerEntryMode`, which can have the following values:
*   **`DIAL`**: The user picks the time from a clock dial. This mode allows switching to text input.
*   **`DIAL_ONLY`**: The user can only pick the time from a clock dial, and the mode cannot be switched.
*   **`INPUT`**: The user types the time into text fields. This mode allows switching to the clock dial.
*   **`INPUT_ONLY`**: The user can only type the time into text fields, and the mode cannot be switched.

Here's an example of how to use `on_entry_mode_change` with a Flet `TimePicker`:

```python
import flet as ft

def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def handle_entry_mode_change(e):
        # The 'entry_mode' property of the event object contains the new mode
        page.add(ft.Text(f"TimePicker Entry mode changed to: {e.entry_mode}"))

    time_picker = ft.TimePicker(
        confirm_text="Confirm",
        help_text="Pick your time slot",
        on_entry_mode_change=handle_entry_mode_change,
    )

    page.add(
        ft.ElevatedButton(
            "Pick time",
            icon=ft.Icons.ACCESS_TIME,
            on_click=lambda _: page.open(time_picker),
        )
    )

ft.app(target=main)
```
