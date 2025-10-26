### Install Flet with uv

Source: https://docs.flet.dev/getting-started/installation

Command to install Flet and its dependencies using the `uv` package manager. The `[all]` extra installs all optional dependencies.

```shell
uv add 'flet[all]'
```

--------------------------------

### Create and Navigate Project Directory

Source: https://docs.flet.dev/getting-started/installation

Commands to create a new directory for a Flet project and change into it. This is the first step in setting up a new Flet application environment.

```shell
mkdir my-app
cd my-app
```

--------------------------------

### Initialize Project with Poetry

Source: https://docs.flet.dev/getting-started/installation

Command to initialize a new Python project with Poetry, a dependency management tool. It sets up project metadata and Python version requirements.

```shell
poetry init --python=">=3.10" --no-interaction
```

--------------------------------

### Install Flet with Poetry

Source: https://docs.flet.dev/getting-started/installation

Command to add Flet and its dependencies to a project managed by Poetry. This command integrates Flet into the project's `pyproject.toml`.

```shell
poetry add 'flet[all]'
```

--------------------------------

### Initialize and Activate Virtual Environment with uv

Source: https://docs.flet.dev/getting-started/installation

Steps to initialize a Python project with uv, create a virtual environment, and activate it. uv is a fast package and project manager for Python.

```shell
uv init --python=">=3.10"
uv venv
source .venv/bin/activate
```

--------------------------------

### Initialize and Activate Virtual Environment with venv

Source: https://docs.flet.dev/getting-started/installation

Instructions to create and activate a Python virtual environment using the built-in `venv` module. This isolates project dependencies.

```shell
python -m venv .venv
source .venv/bin/activate
```

--------------------------------

### Verify Flet Installation with uv

Source: https://docs.flet.dev/getting-started/installation

Commands to check the installed Flet version or run the Flet doctor utility using `uv`. This confirms a successful installation.

```shell
uv run flet --version
# or
uv run flet doctor
```

--------------------------------

### Start-aligned Drawer Example

Source: https://docs.flet.dev/controls/navigationdrawer

Demonstrates how to create a NavigationDrawer aligned to the start (left) of the page with multiple destinations and event handlers.

```APIDOC
## Start-aligned Drawer Example

### Description
This example shows how to create a Flet NavigationDrawer that slides in from the left side of the screen. It includes customizable destinations, an `on_dismiss` event handler, and an `on_change` event handler to track the selected item.

### Code
```python
import flet as ft

def main(page: ft.Page):
    def handle_dismissal(e: ft.Event[ft.NavigationDrawer]):
        print("Drawer dismissed!")

    def handle_change(e: ft.Event[ft.NavigationDrawer]):
        print(f"Selected Index changed: {e.control.selected_index}")
        page.pop_dialog() # Close the dialog after selection

    drawer = ft.NavigationDrawer(
        on_dismiss=handle_dismissal,
        on_change=handle_change,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Item 1",
                icon=ft.Icons.DOOR_BACK_DOOR_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.DOOR_BACK_DOOR),
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                icon=ft.Icon(ft.Icons.MAIL_OUTLINED),
                label="Item 2",
                selected_icon=ft.Icons.MAIL,
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icon(ft.Icons.PHONE_OUTLINED),
                label="Item 3",
                selected_icon=ft.Icons.PHONE,
            ),
        ],
    )

    page.add(
        ft.Button(
            content="Show drawer",
            on_click=lambda e: page.show_dialog(drawer),
        )
    )

ft.run(main)
```
```

--------------------------------

### Verify Flet Installation with Poetry

Source: https://docs.flet.dev/getting-started/installation

Commands to check the installed Flet version or run the Flet doctor utility within a Poetry-managed environment. This verifies Flet's integration into the project.

```shell
poetry run flet --version
# or
poetry run flet doctor
```

--------------------------------

### Main Flet Application Setup for Solitaire

Source: https://docs.flet.dev/tutorials/solitaire

Sets up the main Flet application by defining the 'main' function, which initializes the Flet Page and adds an instance of the Solitaire game to it. The ft.run() function then starts the Flet application, displaying the Solitaire game.

```python
import flet as ft
from solitaire import Solitaire

def main(page: ft.Page):

   solitaire = Solitaire()

   page.add(solitaire)

ft.run(main)

```

--------------------------------

### Upgrade Flet with uv

Source: https://docs.flet.dev/getting-started/installation

Command to upgrade Flet to its latest version using `uv`. This ensures you have the most recent features and bug fixes.

```shell
uv add 'flet[all]' --upgrade
```

--------------------------------

### Upgrade Flet with Poetry

Source: https://docs.flet.dev/getting-started/installation

Command to upgrade Flet to its latest version within a Poetry-managed project. This updates the Flet dependency in `pyproject.toml` and installs the new version.

```shell
poetry add flet[all]@latest
```

--------------------------------

### Install xz Libraries using Homebrew

Source: https://docs.flet.dev/contributing

Installs the xz libraries on macOS using the Homebrew package manager. This is a prerequisite for certain Flet development setups.

```bash
brew install xz
```

--------------------------------

### Flet FilePicker: Pick and Upload Files with Progress

Source: https://docs.flet.dev/controls/filepicker

Shows how to pick multiple files and upload them using Flet's FilePicker, including real-time upload progress indication. This example requires the `flet` library and a server setup for uploads (e.g., `upload_dir`). It displays progress rings for each file being uploaded.

```python
import flet as ft

state = {"picked_files": []}


def main(page: ft.Page):
    prog_bars: dict[str, ft.ProgressRing] = {}

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress

    # add to services
    page.services.append(file_picker := ft.FilePicker(on_upload=on_upload_progress))

    async def handle_files_pick(e: ft.Event[ft.Button]):
        files = await file_picker.pick_files(allow_multiple=True)
        print("Picked files:", files)
        state["picked_files"] = files

        # update progress bars
        upload_button.disabled = len(files) == 0
        prog_bars.clear()
        upload_progress.controls.clear()
        for f in files:
            prog = ft.ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
            prog_bars[f.name] = prog
            upload_progress.controls.append(ft.Row([prog, ft.Text(f.name)]))

    async def handle_file_upload(e: ft.Event[ft.Button]):
        upload_button.disabled = True
        await file_picker.upload(
            files=[
                ft.FilePickerUploadFile(
                    name=file.name,
                    upload_url=page.get_upload_url(f"dir/{file.name}", 60),
                )
                for file in state["picked_files"]
            ]
        )

    page.add(
        ft.Text("test"),
        ft.Button(
            content="Select files...",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=handle_files_pick,
        ),
        upload_progress := ft.Column(),
        upload_button := ft.Button(
            content="Upload",
            icon=ft.Icons.UPLOAD,
            on_click=handle_file_upload,
            disabled=True,
        ),
    )


ft.run(main, upload_dir="examples")

```

--------------------------------

### Install Flet (Shell)

Source: https://docs.flet.dev/index

Command to install the Flet library with all its dependencies, enabling the development of various application types.

```shell
pip install 'flet[all]'
```

--------------------------------

### Install Python Dependencies

Source: https://docs.flet.dev/contributing

Installs all necessary Flet dependencies and sets up the project as an editable package using uv.

```bash
uv sync
```

--------------------------------

### Upgrade Flet with pip

Source: https://docs.flet.dev/getting-started/installation

Command to upgrade Flet to its latest version using pip. This command fetches and installs the newest available version of the Flet package.

```shell
pip install 'flet[all]' --upgrade
```

--------------------------------

### CupertinoAppBar - Basic Example

Source: https://docs.flet.dev/controls/cupertinoappbar

Demonstrates a basic implementation of the CupertinoAppBar with leading, title, and trailing widgets.

```APIDOC
## CupertinoAppBar - Basic Example

### Description
This example shows a simple CupertinoAppBar with a leading icon, a title text, and a trailing icon.

### Method
Not Applicable (Flet Control)

### Endpoint
Not Applicable (Flet Control)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
import flet as ft

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT

    page.appbar = ft.CupertinoAppBar(
        leading=ft.Icon(ft.Icons.PALETTE, color=ft.Colors.ON_SECONDARY),
        title=ft.Text("CupertinoAppBar Example"),
        trailing=ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color=ft.Colors.ON_SECONDARY),
        automatic_background_visibility=False,
        bgcolor=ft.Colors.SECONDARY,
        brightness=ft.Brightness.LIGHT,
    )

    page.add(ft.Text("Body!"))

ft.run(main)
```

### Response
#### Success Response
Not Applicable (Flet Control)

#### Response Example
None
```

--------------------------------

### Programmatic Tab Switch Example

Source: https://docs.flet.dev/controls/tabs

Example demonstrating how to programmatically switch tabs using the `move_to` method.

```APIDOC
## Programmatical Tab switch
```python
import random

import flet as ft


def main(page: ft.Page):
    async def handle_move_to_random(e: ft.Event[ft.FloatingActionButton]):
        # random index, excluding the current one
        i = random.choice([i for i in range(tabs.length) if i != tabs.selected_index])

        await tabs.move_to(
            index=i,
            animation_curve=ft.AnimationCurve.FAST_OUT_SLOWIN,
            animation_duration=ft.Duration(seconds=3),
        )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.MOVE_UP,
        content="Move to a random tab",
        on_click=handle_move_to_random,
    )

    page.add(
        tabs := ft.Tabs(
            length=6,
            selected_index=5,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tab_alignment=ft.TabAlignment.CENTER,
                        tabs=[
                            ft.Tab(label=ft.Text("Tab 1")),
                            ft.Tab(label=ft.Text("Tab 2")),
                            ft.Tab(label=ft.Text("Tab 3")),
                            ft.Tab(label=ft.Text("Tab 4")),
                            ft.Tab(label=ft.Text("Tab 5")),
                            ft.Tab(label=ft.Text("Tab 6")),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Text("Tab 1 content"),
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Text("Tab 2 content"),
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Text("Tab 3 content"),
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Text("Tab 4 content"),
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Text("Tab 5 content"),
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Text("Tab 6 content"),
                                alignment=ft.Alignment.CENTER,
                            ),
                        ],
                    ),
                ],
            ),
        )
    )


ft.run(main)

```
```

--------------------------------

### Load Custom Packages using Micropip

Source: https://docs.flet.dev/publish/web/static-website

Example of loading custom Python packages from PyPI during Flet app startup when running in a Pyodide environment. It utilizes the `micropip` module to install packages like 'regex'. Ensure `requirements.txt` is in the same directory for other package management.

```python
import sys

if sys.platform == "emscripten": # check if run in Pyodide environment
    import micropip
    await micropip.install("regex")
```

--------------------------------

### Verify Flet Installation without uv

Source: https://docs.flet.dev/getting-started/installation

Commands to check the installed Flet version or run the Flet doctor utility directly. This is used when Flet is installed globally or without a specific package manager.

```shell
flet --version
# or
flet doctor
```

--------------------------------

### CircleAvatar Examples

Source: https://docs.flet.dev/controls/circleavatar

Live examples demonstrating various use cases of the CircleAvatar component.

```APIDOC
## Live example: User avatars

```python
import flet as ft

def main(page: ft.Page):
    page.add(
        # a "normal" avatar with background image
        ft.CircleAvatar(
            foreground_image_src="https://avatars.githubusercontent.com/u/5041459?s=88&v=4",
            content=ft.Text("FF"),
        ),
        # avatar with failing foreground image and fallback text
        ft.CircleAvatar(
            foreground_image_src="https://avatars.githubusercontent.com/u/_5041459?s=88&v=4",
            content=ft.Text("FF"),
        ),
        # avatar with icon, aka icon with inverse background
        ft.CircleAvatar(content=ft.Icon(ft.Icons.ABC)),
        # avatar with icon and custom colors
        ft.CircleAvatar(
            content=ft.Icon(ft.Icons.WARNING_ROUNDED),
            color=ft.Colors.YELLOW_200,
            bgcolor=ft.Colors.AMBER_700,
        ),
        # avatar with online status
        ft.Stack(
            width=40,
            height=40,
            controls=[
                ft.CircleAvatar(
                    foreground_image_src="https://avatars.githubusercontent.com/u/5041459?s=88&v=4"
                ),
                ft.Container(
                    content=ft.CircleAvatar(bgcolor=ft.Colors.GREEN, radius=5),
                    alignment=ft.Alignment.BOTTOM_LEFT,
                ),
            ],
        ),
    )

ft.run(main)
```
```

--------------------------------

### CupertinoTimerPicker - Basic Example

Source: https://docs.flet.dev/controls/cupertinotimerpicker

Demonstrates the basic usage of the CupertinoTimerPicker, showing how to initialize it, handle changes, and display the selected time.

```APIDOC
## CupertinoTimerPicker - Basic Example

### Description
This example shows how to use the `CupertinoTimerPicker` to select a time duration. It includes event handling for when the timer value changes and displays the selected time in a formatted string.

### Method
GET (Implicit for UI interaction)

### Endpoint
N/A (Client-side component)

### Parameters

This endpoint does not have explicit path, query, or request body parameters as it's a UI component configuration.

### Request Example
```python
import flet as ft
import time

def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    timer_picker_value_ref = ft.Ref[ft.Text]()

    def handle_timer_picker_change(e: ft.Event[ft.CupertinoTimerPicker]):
        timer_picker_value_ref.current.value = time.strftime(
            "%H:%M:%S", time.gmtime(e.data.in_seconds)
        )
        page.update()

    timer_picker = ft.CupertinoTimerPicker(
        value=300,
        second_interval=10,
        minute_interval=1,
        mode=ft.CupertinoTimerPickerMode.HOUR_MINUTE_SECONDS,
        on_change=handle_timer_picker_change,
    )

    page.add(
        ft.Row(
            tight=True,
            controls=[
                ft.Text("TimerPicker Value:", size=23),
                ft.CupertinoButton(
                    content=ft.Text(
                        ref=timer_picker_value_ref,
                        value="00:01:10",
                        size=23,
                        color=ft.CupertinoColors.DESTRUCTIVE_RED,
                    ),
                    on_click=lambda e: page.show_dialog(
                        ft.CupertinoBottomSheet(
                            content=timer_picker,
                            height=216,
                            padding=ft.Padding.only(top=6),
                        )
                    ),
                ),
            ],
        ),
    )

ft.run(main)
```

### Response

#### Success Response (UI Update)
- **timer_picker_value_ref.current.value** (string) - The formatted time string reflecting the selected duration.

#### Response Example
```
"00:05:00"
```
```

--------------------------------

### DropdownM2 Basic Example

Source: https://docs.flet.dev/controls/dropdownm2

A fundamental example demonstrating the creation and basic functionality of a DropdownM2 with options.

```APIDOC
## Basic Example

A fundamental example demonstrating the creation and basic functionality of a DropdownM2 with options.

### Request Example
```python
import flet as ft


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK

    def handle_button_click(e):
        message.value = f"Dropdown value is:  {dd.value}"
        page.update()

    page.add(
        dd := ft.DropdownM2(
            width=100,
            options=[
                ft.dropdownm2.Option("Red"),
                ft.dropdownm2.Option("Green"),
                ft.dropdownm2.Option("Blue"),
            ],
        ),
        ft.Button(content="Submit", on_click=handle_button_click),
        message := ft.Text(),
    )

ft.run(main)
```
```

--------------------------------

### SnackBar Basic Example

Source: https://docs.flet.dev/controls/snackbar

A simple example demonstrating how to show a basic SnackBar with a text message.

```APIDOC
## SnackBar Basic Example

### Description
This endpoint demonstrates how to display a basic SnackBar with a "Hello, world!" message.

### Method
Not applicable (client-side Flet code)

### Endpoint
Not applicable (client-side Flet code)

### Parameters
None

### Request Example
```python
import flet as ft


def main(page: ft.Page):
    def on_click(e: ft.Event[ft.Button]):
        page.show_dialog(ft.SnackBar(ft.Text("Hello, world!")))

    page.add(ft.Button("Open SnackBar", on_click=on_click))

ft.run(main)
```

### Response
#### Success Response (200)
Displays a SnackBar with the text "Hello, world!"

#### Response Example
(No specific JSON response, visual display of SnackBar)
```

--------------------------------

### Basic Example

Source: https://docs.flet.dev/controls/switch

Demonstrates how to create and use Switch controls with different configurations, including labels, initial values, disabled states, and label positions. It also shows how to collect and display the values of multiple switches.

```APIDOC
## Basic Example

### Description
This example showcases the creation of multiple `ft.Switch` controls with various properties like `label`, `value`, `disabled`, and `label_position`. It includes a button to submit the current values of the switches and display them in a `ft.Text` control.

### Method
N/A (Client-side Flet App)

### Endpoint
N/A (Client-side Flet App)

### Parameters
N/A

### Request Example
```python
import flet as ft

def main(page: ft.Page):
    def handle_button_click(e: ft.Event[ft.Button]):
        message.value = (
            f"Switch values are:  {c1.value}, {c2.value}, {c3.value}, {c4.value}."
        )
        page.update()

    page.add(
        c1 := ft.Switch(label="Unchecked switch", value=False),
        c2 := ft.Switch(label="Checked switch", value=True),
        c3 := ft.Switch(label="Disabled switch", disabled=True),
        c4 := ft.Switch(
            label="Switch with rendered label_position='left'",
            label_position=ft.LabelPosition.LEFT,
        ),
        ft.Button(content="Submit", on_click=handle_button_click),
        message := ft.Text(),
    )

ft.run(main)
```

### Response
N/A (Client-side Flet App)
```

--------------------------------

### FilePicker.pick_files Method Example

Source: https://docs.flet.dev/controls/filepicker

Demonstrates how to use the `pick_files` method to allow users to select one or multiple files from their system.

```APIDOC
## Example: Pick, save, and get directory paths

### Description
This example shows how to use the `FilePicker` control to pick files, save files, and get directory paths.

### Code
```python
import flet as ft

def main(page: ft.Page):
    page.services.append(file_picker := ft.FilePicker())

    async def handle_pick_files(e: ft.Event[ft.Button]):
        files = await file_picker.pick_files(allow_multiple=True)
        selected_files.value = (
            ", ".join(map(lambda f: f.name, files)) if files else "Cancelled!"
        )

    async def handle_save_file(e: ft.Event[ft.Button]):
        save_file_path.value = await file_picker.save_file()

    async def handle_get_directory_path(e: ft.Event[ft.Button]):
        directory_path.value = await file_picker.get_directory_path()

    page.add(
        ft.Row(
            controls=[
                ft.Button(
                    content="Pick files",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=handle_pick_files,
                ),
                selected_files := ft.Text(),
            ]
        ),
        ft.Row(
            controls=[
                ft.Button(
                    content="Save file",
                    icon=ft.Icons.SAVE,
                    on_click=handle_save_file,
                    disabled=page.web,  # disable this button in web mode
                ),
                save_file_path := ft.Text(),
            ]
        ),
        ft.Row(
            controls=[
                ft.Button(
                    content="Open directory",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=handle_get_directory_path,
                    disabled=page.web,  # disable this button in web mode
                ),
                directory_path := ft.Text(),
            ]
        ),
    )

ft.run(main)
```
```

--------------------------------

### Flet Basic Icon Display Example

Source: https://docs.flet.dev/controls/icon

Demonstrates how to display Material and Cupertino icons in Flet. It shows how to set basic properties like color, size, and uses ft.Row to arrange multiple icons. This example requires the 'flet' library.

```python
from typing import cast

import flet as ft


def main(page: ft.Page):
    page.add(
        # material
        ft.Row(
            controls=[
                ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK),
                ft.Icon(ft.Icons.AUDIOTRACK, color=ft.Colors.GREEN_400, size=30),
                ft.Icon(ft.Icons.BEACH_ACCESS, color=ft.Colors.BLUE, size=50),
                ft.Icon(ft.Icons.SETTINGS, color="#c1c1c1"),
            ]
        ),
        # cupertino
        ft.Row(
            controls=[
                ft.Icon(ft.CupertinoIcons.PROFILE_CIRCLED, color=ft.Colors.PINK),
                ft.Icon(
                    icon=cast(ft.CupertinoIcons, ft.CupertinoIcons.random()),
                    color=ft.Colors.GREEN_400,
                    size=30,
                ),
                ft.Icon(
                    icon=cast(ft.CupertinoIcons, ft.CupertinoIcons.random()),
                    color=ft.Colors.BLUE,
                    size=50,
                ),
                ft.Icon(
                    icon=cast(ft.CupertinoIcons, ft.CupertinoIcons.random()),
                    color="#c1c1c1",
                ),
            ]
        ),
    )


if __name__ == "__main__":
    ft.run(main)

```

--------------------------------

### Flet FilePicker: Pick, Save, Get Directory Paths

Source: https://docs.flet.dev/controls/filepicker

Demonstrates how to use Flet's FilePicker to pick single or multiple files, save a file to a specified location, and get the path of a selected directory. Requires the `flet` library. Outputs selected file names or paths to Text controls.

```python
import flet as ft


def main(page: ft.Page):
    page.services.append(file_picker := ft.FilePicker())

    async def handle_pick_files(e: ft.Event[ft.Button]):
        files = await file_picker.pick_files(allow_multiple=True)
        selected_files.value = (
            ", ".join(map(lambda f: f.name, files)) if files else "Cancelled!"
        )

    async def handle_save_file(e: ft.Event[ft.Button]):
        save_file_path.value = await file_picker.save_file()

    async def handle_get_directory_path(e: ft.Event[ft.Button]):
        directory_path.value = await file_picker.get_directory_path()

    page.add(
        ft.Row(
            controls=[
                ft.Button(
                    content="Pick files",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=handle_pick_files,
                ),
                selected_files := ft.Text(),
            ]
        ),
        ft.Row(
            controls=[
                ft.Button(
                    content="Save file",
                    icon=ft.Icons.SAVE,
                    on_click=handle_save_file,
                    disabled=page.web,  # disable this button in web mode
                ),
                save_file_path := ft.Text(),
            ]
        ),
        ft.Row(
            controls=[
                ft.Button(
                    content="Open directory",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=handle_get_directory_path,
                    disabled=page.web,  # disable this button in web mode
                ),
                directory_path := ft.Text(),
            ]
        ),
    )


ft.run(main)

```

--------------------------------

### BottomAppBar Example

Source: https://docs.flet.dev/controls/bottomappbar

A live example demonstrating the usage of the BottomAppBar with a notched FloatingActionButton.

```APIDOC
## BottomAppBar Example

### Description
This example showcases a BottomAppBar with a notched FloatingActionButton, demonstrating custom alignment and content.

### Code Example

```python
import flet as ft

def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        shape=ft.CircleBorder(),
    )
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    page.appbar = ft.AppBar(
        title=ft.Text("Bottom AppBar Demo"),
        center_title=True,
        bgcolor=ft.Colors.GREEN_300,
        automatically_imply_leading=False,
    )
    page.bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.BLUE,
        shape=ft.CircularRectangleNotchShape(),
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.MENU, icon_color=ft.Colors.WHITE),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE),
                ft.IconButton(icon=ft.Icons.FAVORITE, icon_color=ft.Colors.WHITE),
            ]
        ),
    )

    page.add(ft.Text("Body!"))

ft.run(main)
```
```

--------------------------------

### Flutter Command: Add Flet Package

Source: https://docs.flet.dev/controls/markdown

Installs the 'flet' package into a Flutter project using the Flutter CLI. This command should be run from the root directory of your Flutter project.

```bash
flutter pub add flet

```

--------------------------------

### Basic SnackBar Example - Flet

Source: https://docs.flet.dev/controls/snackbar

This snippet shows a basic implementation of the Flet SnackBar, displaying a simple 'Hello, world!' message when a button is clicked. It requires the 'flet' library.

```python
import flet as ft


def main(page: ft.Page):
    def on_click(e: ft.Event[ft.Button]):
        page.show_dialog(ft.SnackBar(ft.Text("Hello, world!")))

    page.add(ft.Button("Open SnackBar", on_click=on_click))


ft.run(main)
```

--------------------------------

### Photo Gallery Example

Source: https://docs.flet.dev/controls/gridview

An example demonstrating how to use GridView to create a photo gallery.

```APIDOC
## Photo Gallery Example

### Description
This example showcases the `GridView` control by creating a responsive photo gallery with dynamically loaded images.

### Method
GET (Implicitly through `ft.run`)

### Endpoint
N/A (Client-side Flet application)

### Code Example
```python
import flet as ft

def main(page: ft.Page):
    page.title = "GridView Example"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 50

    page.add(
        ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
            controls=[
                ft.Image(
                    src=f"https://picsum.photos/150/150?{i}",
                    fit=ft.BoxFit.NONE,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.BorderRadius.all(10),
                )
                for i in range(0, 60)
            ],
        )
    )

ft.run(main)
```

### Response
(This is a client-side example, responses are rendered UI elements)

#### Success Response (UI Rendered)
- A `GridView` control populated with images arranged in a grid.

#### Response Example
(Visual representation of the photo gallery)
```

--------------------------------

### Install uv for Windows

Source: https://docs.flet.dev/contributing

Installs the uv package manager on Windows using PowerShell. Ensure the installation directory is added to the system's PATH.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

--------------------------------

### Run Flet App - main.py

Source: https://docs.flet.dev/tutorials/trolli

Initializes the Flet application, sets the page title, background color, and instantiates the TrelloApp. This is the entry point for the Flet application.

```python
import flet as ft

if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Flet Trello clone"
        page.padding = 0
        page.bgcolor = colors.BLUE_GREY_200
        app = TrelloApp(page)
        page.add(app)
        page.update()

    ft.run(main)
```

--------------------------------

### Android Manifest Meta-data Example

Source: https://docs.flet.dev/publish/android

This snippet shows how Android meta-data configured via Flet CLI or `pyproject.toml` is represented in the `AndroidManifest.xml`. It includes examples of default meta-data.

```xml
<application>
    <meta-data android:name="name_1" android:value="value_1" />
    <meta-data android:name="name_2" android:value="value_2" />
    <meta-data android:name="io.flutter.embedding.android.EnableImpeller" android:value="false" />
</application>

```

--------------------------------

### Flet App Initialization and Configuration

Source: https://docs.flet.dev/tutorials/trolli

Sets up the main Flet page properties such as title, padding, theme, theme mode, page transitions, fonts, and background color. It then instantiates the `TrelloApp` and runs the Flet application, specifying an assets directory for custom fonts.

```python
if __name__ == "__main__":

    def main(page: ft.Page):

        page.title = "Flet Trello clone"
        page.padding = 0
        page.theme = ft.Theme(font_family="Verdana")
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme.page_transitions.windows = "cupertino"
        page.fonts = {"Pacifico": "/Pacifico-Regular.ttf"}
        page.bgcolor = ft.Colors.BLUE_GREY_200
        page.update()
        app = TrelloApp(page)

    ft.run(main, assets_dir="../examples")

```

--------------------------------

### FilePicker.upload Method Example

Source: https://docs.flet.dev/controls/filepicker

Illustrates how to pick files and upload them to a specified URL, with progress tracking.

```APIDOC
## Example: Pick and upload files

### Description
This example demonstrates picking multiple files and uploading them with progress indication.

### Code
```python
import flet as ft

state = {"picked_files": []}

def main(page: ft.Page):
    prog_bars: dict[str, ft.ProgressRing] = {}

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        page.update()

    # add to services
    page.services.append(file_picker := ft.FilePicker(on_upload=on_upload_progress))

    async def handle_files_pick(e: ft.Event[ft.Button]):
        files = await file_picker.pick_files(allow_multiple=True)
        print("Picked files:", files)
        state["picked_files"] = files

        # update progress bars
        upload_button.disabled = len(files) == 0
        prog_bars.clear()
        upload_progress.controls.clear()
        for f in files:
            prog = ft.ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
            prog_bars[f.name] = prog
            upload_progress.controls.append(ft.Row([prog, ft.Text(f.name)]))
        page.update()

    async def handle_file_upload(e: ft.Event[ft.Button]):
        upload_button.disabled = True
        page.update()
        await file_picker.upload(
            files=[
                ft.FilePickerUploadFile(
                    name=file.name,
                    upload_url=page.get_upload_url(f"dir/{file.name}", 60),
                )
                for file in state["picked_files"]
            ]
        )

    page.add(
        ft.Text("test"),
        ft.Button(
            content="Select files...",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=handle_files_pick,
        ),
        upload_progress := ft.Column(),
        upload_button := ft.Button(
            content="Upload",
            icon=ft.Icons.UPLOAD,
            on_click=handle_file_upload,
            disabled=True,
        ),
    )

ft.run(main, upload_dir="examples")
```
```

--------------------------------

### AnimatedSwitcher Examples

Source: https://docs.flet.dev/controls/animatedswitcher

Demonstrates various ways to use AnimatedSwitcher for animating transitions between different content types with different effects.

```APIDOC
## Animated switching between two containers with scale effect

### Description
This example shows how to animate switching between two containers using the SCALE transition effect. It also demonstrates how to apply different transition effects like FADE and ROTATION.

### Method
```python
main(page: ft.Page)
```

### Parameters
*   **page** (ft.Page) - The Flet page object.

### Request Example
```python
import flet as ft

def main(page: ft.Page):
    c1 = ft.Container(
        content=ft.Text("Hello!", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        alignment=ft.Alignment.CENTER,
        width=200,
        height=200,
        bgcolor=ft.Colors.GREEN,
    )
    c2 = ft.Container(
        content=ft.Text("Bye!", size=50),
        alignment=ft.Alignment.CENTER,
        width=200,
        height=200,
        bgcolor=ft.Colors.YELLOW,
    )
    switcher = ft.AnimatedSwitcher(
        content=c1,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=500,
        reverse_duration=100,
        switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
        switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
    )

    def scale(e):
        switcher.content = c2 if switcher.content == c1 else c1
        switcher.transition = ft.AnimatedSwitcherTransition.SCALE
        switcher.update()

    def fade(e):
        switcher.content = c2 if switcher.content == c1 else c1
        switcher.transition = ft.AnimatedSwitcherTransition.FADE
        switcher.update()

    def rotate(e):
        switcher.content = c2 if switcher.content == c1 else c1
        switcher.transition = ft.AnimatedSwitcherTransition.ROTATION
        switcher.update()

    page.add(
        switcher,
        ft.Button("Scale", on_click=scale),
        ft.Button("Fade", on_click=fade),
        ft.Button("Rotate", on_click=rotate),
    )

ft.run(main)
```

### Response
This example does not have a specific success or error response, as it demonstrates UI manipulation within the Flet framework.
```

```APIDOC
## Animate Image switch

### Description
This example demonstrates how to animate switching between images using `AnimatedSwitcher`. Clicking the button replaces the current image with a new one fetched from a URL, with a scale transition.

### Method
```python
main(page: ft.Page)
```

### Parameters
*   **page** (ft.Page) - The Flet page object.

### Request Example
```python
import time
import flet as ft

def main(page: ft.Page):
    def animate(e: ft.Event[ft.Button]):
        switcher.content = ft.Image(
            src=f"https://picsum.photos/200/300?{time.time()}",
            width=200,
            height=300,
        )
        page.update()

    page.add(
        switcher := ft.AnimatedSwitcher(
            content=ft.Image(
                src="https://picsum.photos/200/300",
                width=200,
                height=300,
            ),
            transition=ft.AnimatedSwitcherTransition.SCALE,
            duration=500,
            reverse_duration=100,
            switch_in_curve=ft.AnimationCurve.BOUNCE_OUT,
            switch_out_curve=ft.AnimationCurve.BOUNCE_IN,
        ),
        ft.Button("Animate!", on_click=animate),
    )

ft.run(main)
```

### Response
This example does not have a specific success or error response, as it demonstrates UI manipulation within the Flet framework.
```

```APIDOC
## Animate Image switch buffered

### Description
This example implements a `BufferingSwitcher` that preloads images into a queue and animates switching between them. It fetches images from a URL, converts them to base64, and uses `AnimatedSwitcher` for a smooth transition with buffering.

### Method
```python
async def fill_queue(self)
async def image_to_base64(self, url)
def animate(self, e)
def before_update(self)
def main(page: ft.Page)
```

### Parameters
*   **self** (BufferingSwitcher) - The instance of the BufferingSwitcher.
*   **url** (str) - The URL of the image to convert.
*   **e** - The event object.
*   **page** (ft.Page) - The Flet page object.

### Request Body (for `image_to_base64`)
*   **url** (str) - Required - The URL of the image to fetch.

### Request Example
```python
import base64
import time
import httpx
import flet as ft

class BufferingSwitcher(ft.AnimatedSwitcher):
    image_queue = []

    def __init__(self, image: ft.Image, page: ft.Page):
        super().__init__(image)
        self.transition = ft.AnimatedSwitcherTransition.SCALE
        self.duration = 500
        self.reverse_duration = 100
        self.switch_in_curve = ft.AnimationCurve.EASE_IN
        self.switch_out_curve = ft.AnimationCurve.EASE_OUT
        self.image_queue.append(image)
        self.page = page

    def animate(self, e):
        self.content = ft.Image(
            src_base64=self.image_queue.pop(),
            width=200,
            height=300,
            gapless_playback=True,
        )
        self.update()

    async def fill_queue(self):
        while len(self.image_queue) < 10:
            self.image_queue.append(
                await self.image_to_base64(
                    f"https://picsum.photos/200/300?{time.time()}"
                )
            )

    async def image_to_base64(self, url):
        print("image_to_base64 called")
        response = await httpx.AsyncClient(follow_redirects=True).get(url)
        if response.status_code == 200:
            base64_str = (
                base64.standard_b64encode(response.content).decode("utf-8").strip()
            )
            return base64_str
        else:
            print(f"Image request failed with {response.status_code}")
            return None

    def before_update(self):
        self.page.run_task(self.fill_queue)
        print(len(self.image_queue))

def main(page: ft.Page):
    switcher = BufferingSwitcher(
        ft.Image(
            src=f"https://picsum.photos/200/300?{time.time()}", width=200, height=300
        ),
        page,
    )

    page.add(
        switcher,
        ft.Button("Animate!", on_click=switcher.animate),
    )

ft.run(main)
```

### Response
#### Success Response (200)
*   **base64_str** (str) - The image content encoded in base64.

#### Response Example
```json
{
  "example": "iVBORw0KGgoAAAANSUhEUgAAAPAAAA..."
}
```
```

--------------------------------

### Basic Flet NavigationBar Example

Source: https://docs.flet.dev/controls/navigationbar

Demonstrates the basic implementation of a Flet NavigationBar with three destinations: Explore, Commute, and Favorites. This example sets the page title and adds the navigation bar to the page.

```python
import flet as ft


def main(page: ft.Page):
    page.title = "NavigationBar Example"

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Explore"),
            ft.NavigationBarDestination(icon=ft.Icons.COMMUTE, label="Commute"),
            ft.NavigationBarDestination(
                icon=ft.Icons.BOOKMARK_BORDER,
                selected_icon=ft.Icons.BOOKMARK,
                label="Favorites",
            ),
        ]
    )

    page.add(ft.Text("Body!"))


ft.run(main)
```

--------------------------------

### Configure Replit for Flet App Deployment

Source: https://docs.flet.dev/publish/web/dynamic-website/hosting/replit

These configurations in the `.replit` file disable package installation before running and prevent automatic import guessing, optimizing the deployment process for Flet applications on Replit.

```ini
# Stops the packager from installing packages when running the Repl
disableInstallBeforeRun = true
# Stops the packager from guessing and auto-installing packages, but it still runs to install packages when running the Repl
disableGuessImports = true
```

--------------------------------

### NavigationBar Basic Example

Source: https://docs.flet.dev/controls/navigationbar

A simple implementation of the NavigationBar component in Flet, demonstrating how to add destinations and set up basic page content.

```APIDOC
## NavigationBar Basic Example

### Description
This example shows how to create a basic `NavigationBar` with three destinations: 'Explore', 'Commute', and 'Favorites'. It also includes a simple text element in the page body.

### Method
N/A (This is a Flet UI component example)

### Endpoint
N/A

### Parameters
N/A

### Request Example
```python
import flet as ft

def main(page: ft.Page):
    page.title = "NavigationBar Example"

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Explore"),
            ft.NavigationBarDestination(icon=ft.Icons.COMMUTE, label="Commute"),
            ft.NavigationBarDestination(
                icon=ft.Icons.BOOKMARK_BORDER,
                selected_icon=ft.Icons.BOOKMARK,
                label="Favorites",
            ),
        ]
    )

    page.add(ft.Text("Body!"))

ft.run(main)
```

### Response
N/A
```

--------------------------------

### Flet ExpansionPanelList Basic Example

Source: https://docs.flet.dev/controls/expansionpanellist

Demonstrates the basic usage of Flet's ExpansionPanelList, including adding, removing, and managing panels. It utilizes Python's flet library and requires no external dependencies beyond Flet itself. The example shows how to define panels with headers, content, and interactive delete buttons.

```python
import flet as ft


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT

    def handle_change(e: ft.Event[ft.ExpansionPanelList]):
        print(f"change on panel with index {e.data}")

    def handle_delete(e: ft.Event[ft.IconButton]):
        icon_button = e.control
        tile = icon_button.parent
        panel = tile.parent

        panel_list.controls.remove(panel)
        page.update()

    panel_list = ft.ExpansionPanelList(
        expand_icon_color=ft.Colors.AMBER,
        elevation=8,
        divider_color=ft.Colors.AMBER,
        on_change=handle_change,
        controls=[
            ft.ExpansionPanel(
                # has no header and content - placeholders will be used
                bgcolor=ft.Colors.BLUE_400,
                expanded=True,
            ),
        ],
    )

    colors = [
        ft.Colors.GREEN_500,
        ft.Colors.BLUE_800,
        ft.Colors.RED_800,
    ]

    for i in range(len(colors)):
        bgcolor = colors[i % len(colors)]
        panel_list.controls.append(
            ft.ExpansionPanel(
                bgcolor=bgcolor,
                header=ft.ListTile(title=ft.Text(f"Panel {i}"), bgcolor=bgcolor),
                content=ft.ListTile(
                    bgcolor=bgcolor,
                    title=ft.Text(f"This is in Panel {i}"),
                    subtitle=ft.Text(f"Press the icon to delete panel {i}"),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE,
                        on_click=handle_delete,
                    ),
                ),
            )
        )

    page.add(panel_list)


ft.run(main)

```

--------------------------------

### Flet Column Horizontal Alignment Example

Source: https://docs.flet.dev/controls/column

This Flet code demonstrates how to set the horizontal alignment of controls within a Column using `ft.CrossAxisAlignment`. It shows examples for `START`, `CENTER`, and `END` alignments, illustrating their effect on child elements.

```python
import flet as ft


class ColumnFromHorizontalAlignment(ft.Column):
    def __init__(self, alignment: ft.CrossAxisAlignment):
        super().__init__()
        self.controls = [
            ft.Text(str(alignment), size=16),
            ft.Container(
                bgcolor=ft.Colors.AMBER_100,
                width=100,
                content=ft.Column(
                    controls=self.generate_items(3),
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=alignment,
                ),
            ),
        ]

    @staticmethod
    def generate_items(count: int):
        """Generates a list of custom Containers with length `count`."""
        return [
            ft.Container(
                content=ft.Text(value=str(i)),
                alignment=ft.Alignment.CENTER,
                width=50,
                height=50,
                bgcolor=ft.Colors.AMBER_500,
            )
            for i in range(1, count + 1)
        ]


def main(page: ft.Page):
    page.add(
        ft.Row(
            spacing=30,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ColumnFromHorizontalAlignment(ft.CrossAxisAlignment.START),
                ColumnFromHorizontalAlignment(ft.CrossAxisAlignment.CENTER),
                ColumnFromHorizontalAlignment(ft.CrossAxisAlignment.END),
            ],
        )
    )

ft.run(main)
