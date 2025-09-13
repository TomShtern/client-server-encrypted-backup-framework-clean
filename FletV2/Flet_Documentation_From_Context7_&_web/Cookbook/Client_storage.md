# Client storage

Flet's client storage API allows storing key-value data persistently on the client side. For desktop apps, this uses JSON files.

To write data, you can use `page.client_storage.set("key", "value")` for strings, numbers, booleans, and lists. When reading data with `page.client_storage.get("key")`, the value is automatically converted back to its original type.

Other useful functions include:
*   `page.client_storage.contains_key("key")` to check if a key exists.
*   `page.client_storage.get_keys("key-prefix.")` to retrieve all keys with a specific prefix.
*   `page.client_storage.remove("key")` to delete a specific key-value pair.
*   `page.client_storage.clear()` to remove all preferences for all Flet apps run by the same user.

It's recommended to use unique prefixes for storage keys (e.g., `{company}.{product}.`) to distinguish settings between different applications. Additionally, developers are responsible for encrypting sensitive data before storing it in client storage to prevent unauthorized access or tampering.
