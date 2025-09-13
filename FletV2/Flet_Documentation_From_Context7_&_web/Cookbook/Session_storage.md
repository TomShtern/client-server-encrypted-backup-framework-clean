# Session storage

Flet provides an API for storing key-value data in a user's session on the server side. This data is transient and is not preserved between app restarts.

You can perform the following operations with session storage:
*   **Writing data**: Use `page.session.set("key", value)` to store strings, numbers, booleans, or lists.
*   **Reading data**: Use `value = page.session.get("key")` to retrieve data, which is automatically converted back to its original type.
*   **Checking key existence**: Use `page.session.contains_key("key")` to see if a key exists.
*   **Getting all keys**: Use `page.session.get_keys()` to retrieve all stored keys.
*   **Removing a value**: Use `page.session.remove("key")` to delete a specific key-value pair.
*   **Clearing storage**: Use `page.session.clear()` to remove all data from the session storage.
