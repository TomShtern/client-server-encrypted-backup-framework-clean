# Encrypting sensitive data

Flet provides built-in utility methods for encrypting and decrypting sensitive text data, which are suitable for use within a Flet application. These methods leverage the Fernet implementation from the `cryptography` package, utilizing AES 128-bit encryption with PBKDF2 for key derivation.

Here's how you can use Flet's `encrypt` and `decrypt` functions:

```python
import os
import flet as ft
from flet.security import encrypt, decrypt

def main(page: ft.Page):
    page.title = "Flet Encryption Example"

    # IMPORTANT: The secret key should be securely managed,
    # e.g., loaded from environment variables, a secure vault, or a configuration file
    # and NEVER hardcoded in production.
    # For this example, we'll use a placeholder.
    # In a real application, you might get it like:
    # secret_key = os.getenv("MY_APP_SECRET_KEY")
    # If MY_APP_SECRET_KEY is not set, generate a random one for demonstration.
    secret_key = os.getenv("MY_APP_SECRET_KEY")
    if not secret_key:
        print("MY_APP_SECRET_KEY environment variable not found. Generating a random key for demonstration.")
        # Generate a random key for demonstration purposes if not set
        # In a real app, you'd generate this once and store it securely.
        from cryptography.fernet import Fernet
        secret_key = Fernet.generate_key().decode()
        print(f"Generated secret key (for demo): {secret_key}")

    plain_text_input = ft.TextField(label="Enter text to encrypt", width=400)
    encrypted_text_output = ft.TextField(label="Encrypted Text", read_only=True, width=400)
    decrypted_text_output = ft.TextField(label="Decrypted Text", read_only=True, width=400)

    def encrypt_data(e):
        plain_text = plain_text_input.value
        if plain_text:
            try:
                encrypted_data = encrypt(plain_text, secret_key)
                encrypted_text_output.value = encrypted_data
                page.update()
            except Exception as ex:
                encrypted_text_output.value = f"Encryption error: {ex}"
                page.update()

    def decrypt_data(e):
        encrypted_data = encrypted_text_output.value
        if encrypted_data:
            try:
                decrypted_text = decrypt(encrypted_data, secret_key)
                decrypted_text_output.value = decrypted_text
                page.update()
            except Exception as ex:
                decrypted_text_output.value = f"Decryption error: {ex}"
                page.update()

    page.add(
        plain_text_input,
        ft.ElevatedButton("Encrypt", on_click=encrypt_data),
        encrypted_text_output,
        ft.ElevatedButton("Decrypt", on_click=decrypt_data),
        decrypted_text_output,
    )

if __name__ == "__main__":
    ft.app(target=main)
```

**Key Considerations:**

*   **Secret Key Management**: The `secret_key` is crucial. Anyone with access to this key can decrypt your data. It should never be hardcoded in your application. Best practices include loading it from environment variables, a secure configuration management system, or a dedicated key vault.
*   **Data Type**: Flet's `encrypt` function accepts strings only. If you need to encrypt objects (like dictionaries or lists), you must first serialize them (e.g., to JSON or XML) before encryption.
*   **Project-Specific Encryption**: Your project context mentions RSA-1024 and AES-256-CBC. While Flet's built-in encryption uses AES-128 Fernet, if your application requires strict adherence to AES-256-CBC or RSA-1024 for specific data flows (like the file transfer protocol), you would typically use the `cryptography` library's lower-level APIs or a library like PyCryptodome directly. However, for general sensitive data within the Flet application's scope (e.g., storing user preferences or tokens locally), Flet's built-in methods are often sufficient and more convenient.
