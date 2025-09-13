# File picker

This document provides a guide on how to use the `FilePicker` control in Flet applications to handle file selection on desktop platforms (macOS, Windows, Linux).

### File Picker Functionality

The `FilePicker` control can open three types of native OS dialogs:
*   **Pick files**: Allows users to select one or more files. You can specify which file types are allowed.
*   **Save file**: Lets the user choose a directory and enter a file name for saving.
*   **Get directory**: Enables the selection of a directory.

For Linux desktop apps, `Zenity` must be installed.

### Implementation

To use the file picker, it is recommended to add it to the `page.overlay` collection to avoid affecting the app's layout. You can then trigger the dialogs using methods like `pick_files()`, `save_file()`, and `get_directory_path()`. The results of the dialog are captured through the `on_result` event handler.

Here is a simple example of how to add and trigger a file picker:

```python
import flet as ft

def main(page: ft.Page):
    def on_dialog_result(e: ft.FilePickerResultEvent):
        print("Selected files:", e.files)
        print("Selected file or directory:", e.path)

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()

    page.add(
        ft.ElevatedButton(
            "Choose files...",
            on_click=lambda _: file_picker.pick_files(allow_multiple=True)
        )
    )

ft.app(target=main)
```
