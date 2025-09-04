Flet is a Python framework that allows you to build cross-platform desktop, web, and mobile applications using Python. When you create a Flet application, it automatically generates a window (for desktop apps) or a web page (for web apps) to display your UI. This guide focuses on managing windows in Flet for desktop applications.

### 1. Basic Window Creation

A Flet application inherently creates a window when run as a desktop app. The core of a Flet application is typically defined within a `main` function that takes a `page` object as an argument. This `page` object represents the content area of your application's window.

Here's a minimal example:

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text("Hello, Flet Window!"))

if __name__ == "__main__":
    ft.app(target=main)
```

When you run this code, a window will appear with the text "Hello, Flet Window!".

### 2. Window Properties

You can control various aspects of your application's window using the `page.window` object. These properties are primarily effective on desktop platforms.

Here are some common window properties you can set:

*   **`width`**: Sets the width of the window in pixels.
*   **`height`**: Sets the height of the window in pixels.
*   **`resizable`**: A boolean indicating whether the user can resize the window. Set to `False` to make it non-resizable.
*   **`title`**: Sets the title displayed in the window's title bar.
*   **`left`**: Defines the horizontal position (x-coordinate) of the window from the left edge of the screen.
*   **`top`**: Defines the vertical position (y-coordinate) of the window from the top edge of the screen.
*   **`full_screen`**: A boolean to switch the window to full-screen mode.
*   **`minimized`**: A boolean to programmatically minimize the window.
*   **`maximized`**: A boolean to programmatically maximize or unmaximize the window.
*   **`frameless`**: A boolean to hide the window's frame (title bar and borders).
*   **`bgcolor`**: Sets the background color of the application window. Can be used with `page.bgcolor = ft.Colors.TRANSPARENT` for transparent windows.
*   **`always_on_top`**: A boolean to keep the window always on top of other windows.
*   **`always_on_bottom`**: A boolean to keep the window always below other windows (Linux and Windows only).
*   **`icon`**: Sets the icon of the app window (Windows only).
*   **`visible`**: A boolean to control the visibility of the window. Useful for starting an app with a hidden window.

**Example of setting window properties:**

```python
import flet as ft

def main(page: ft.Page):
    page.title = "My Custom Flet Window"
    page.window.width = 800
    page.window.height = 600
    page.window.resizable = False
    page.window.always_on_top = True
    page.window.bgcolor = ft.colors.BLUE_GREY_100 # Light grey background for the window frame

    page.add(
        ft.Text("This window has custom properties!", size=20),
        ft.ElevatedButton("Click me!")
    )
    page.update() # Important to update the page to apply changes

if __name__ == "__main__":
    ft.app(target=main)
```

### 3. Window Events

Flet allows you to respond to various window-related events.

*   **`page.on_resized`**: This event handler is triggered when the window is resized. You can use it to adjust your UI dynamically based on the new `page.width` and `page.height`.
*   **`page.window.on_event`**: This is a general event handler for native window events. It can be used to intercept events like the window closing.

**Example of handling window resize and close events:**

```python
import flet as ft

def main(page: ft.Page):
    def on_window_event(e: ft.WindowEvent):
        print(f"Window event: {e.type}")
        if e.type == ft.WindowEventType.CLOSE:
            print("Window is about to close. Performing cleanup...")
            # You can add logic here to save data or confirm exit
            # To prevent close, set page.window.prevent_close = True
            # and then call page.window.destroy() when ready to close.
            page.window.destroy() # Explicitly close the window after cleanup

    def on_page_resized(e):
        print(f"Window resized to: {page.window.width}x{page.window.height}")
        # You can update UI elements here based on new size
        page.update()

    page.title = "Window Events Demo"
    page.window.on_event = on_window_event
    page.on_resized = on_page_resized
    page.window.prevent_close = True # Prevent default close behavior initially [1, 16]

    page.add(
        ft.Text("Resize this window or try to close it!", size=20),
        ft.ElevatedButton("Close Window", on_click=lambda e: page.window.destroy())
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
```

### 4. Advanced Window Management

#### Preventing Window Close

To intercept the native close signal (e.g., when the user clicks the 'X' button), set `page.window.prevent_close = True`. You can then handle the `ft.WindowEventType.CLOSE` event in `page.window.on_event` to perform actions like saving data or asking for confirmation before explicitly calling `page.window.destroy()` to close the window.

#### Multiple Windows

Flet applications typically run as a single window. However, you can open multiple independent windows by running separate Flet applications as subprocesses. Each subprocess will launch its own Flet window.

**Example of opening a second window:**

`main_app.py`:
```python
import flet as ft
import subprocess

def main(page: ft.Page):
    def open_second_window(e):
        # This will run 'second_window.py' in a new process, opening a new window
        subprocess.Popen(["python", "second_window.py"])

    page.title = "Main Window"
    page.add(
        ft.Text("This is the main application window."),
        ft.ElevatedButton("Open Second Window", on_click=open_second_window)
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
```

`second_window.py`:
```python
import flet as ft

def main(page: ft.Page):
    page.title = "Second Window"
    page.window.width = 400
    page.window.height = 300
    page.window.top = 100 # Position it differently
    page.window.left = 900
    page.add(ft.Text("Hello from the second window!"))
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
```
To run this, save both files in the same directory and execute `python main_app.py`.

### 5. Packaging for Windows

Once your Flet application is ready, you can package it into a standalone executable for Windows using the Flet CLI command `flet build windows`. This command requires Visual Studio 2022 with the "Desktop development with C++" workload installed.

```bash
flet build windows
```
