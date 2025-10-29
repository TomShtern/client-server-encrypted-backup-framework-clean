# FilePickerUploadEvent

The `Flet FilePickerUploadEvent` is an event object in the Flet framework that provides real-time progress and status updates during file uploads. It is specifically used with the `FilePicker.on_upload` callback.

When the `FilePicker.upload()` method is invoked, Flet asynchronously begins uploading the files that were previously selected by the user. As each file is uploaded, the `on_upload` callback is triggered, and an instance of `FilePickerUploadEvent` is passed to it.

The `FilePickerUploadEvent` object contains the following key properties:
*   `file_name`: A string representing the name of the file currently being uploaded.
*   `progress`: A float value ranging from `0.0` to `1.0`, indicating the current upload progress for the specific file.
*   `error`: A string that contains an error message if the upload for that file fails. If the upload is successful, this field will be empty or `None`.

The `on_upload` callback is guaranteed to be called at least twice for each file: once with `progress=0.0` when the upload begins, and once with `progress=1.0` when the upload is complete.

To implement file upload functionality with progress tracking in Flet, the general workflow involves:
1.  Creating an instance of `ft.FilePicker` and typically adding it to `page.overlay`.
2.  Using `file_picker.pick_files()` to open a native dialog for the user to select files.
3.  After files are selected (handled by the `FilePicker.on_result` callback, which receives a `FilePickerResultEvent`), calling `file_picker.upload()` to initiate the transfer.
4.  Setting up a function for the `FilePicker.on_upload` callback to process the `FilePickerUploadEvent` and update the UI with the upload status and progress.

You can also specify an `upload_dir` when initializing your Flet application (`ft.app(main, upload_dir="uploads")`) to define the directory where uploaded files will be stored on the server.