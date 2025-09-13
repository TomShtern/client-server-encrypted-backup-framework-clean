# FilePickerResultEvent

The `FilePickerResultEvent` in Flet is an event object that is triggered when a file picker dialog, initiated by the `FilePicker` control, is closed. This event allows your Flet application to react to the user's selection (or cancellation) from the native file system dialog.

Key aspects of `FilePickerResultEvent`:

*   **Purpose**: It provides the results of file selection, file saving, or directory selection operations performed using the `FilePicker` control.
*   **Event Handler**: You typically attach a function to the `on_result` property of a `FilePicker` instance. This function will receive a `FilePickerResultEvent` object as its argument when the dialog closes.
*   **Properties**: The `FilePickerResultEvent` object has the following important properties:
    *   `path`: This property is used when the `save_file()` or `get_directory_path()` methods of `FilePicker` are called. It contains the selected file path or directory path as a string. If the dialog was canceled, this property will be `None`.
    *   `files`: This property is used when the `pick_files()` method of `FilePicker` is called. It contains a list of `FilePickerFile` objects, each representing a file selected by the user. If the dialog was canceled, this property will be `None`. A `FilePickerFile` object typically includes the file's `name` and `path`.

**Example Usage**:

```python
import flet as ft

def main(page: ft.Page):
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_files_text.value = ", ".join([f.name for f in e.files])
            # You can access the full path of the first selected file like this:
            # first_file_path = e.files[0].path
        else:
            selected_files_text.value = "Selection cancelled!"
        selected_files_text.update()

    file_picker = ft.FilePicker(on_result=pick_files_result)
    selected_files_text = ft.Text()

    page.overlay.append(file_picker) # It's recommended to add FilePicker to page.overlay

    page.add(
        ft.Column(
            [
                ft.ElevatedButton(
                    "Pick files",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: file_picker.pick_files(allow_multiple=True),
                ),
                selected_files_text,
            ]
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
```