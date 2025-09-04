# Read and write files

The Flet documentation page explains how to read and write files in Flet applications. It highlights the use of two environment variables, `FLET_APP_STORAGE_DATA` and `FLET_APP_STORAGE_TEMP`, to access application-specific data and temporary storage paths, respectively. These paths can be retrieved using `os.getenv()`.

To write data to a file, you can use Python's built-in `open()` function with the "w" mode, and to read from an existing file, use the "r" mode. The page also provides an example of a counter application that persists its value by writing it to a file in the app's data storage directory and reading it upon launch. Additionally, the `os` module can be used for other file operations like renaming, deleting, and listing files.
