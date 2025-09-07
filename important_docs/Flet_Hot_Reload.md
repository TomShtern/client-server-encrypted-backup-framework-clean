Title: Running a Flet app (Hot Reload)

URL Source: http://docs.flet.dev/getting-started/running-app/

Markdown Content:
[](https://github.com/flet-dev/flet/edit/main/sdk/python/packages/flet/docs/getting-started/running-app.md "Edit this page")[](https://github.com/flet-dev/flet/raw/main/sdk/python/packages/flet/docs/getting-started/running-app.md "View source of this page")
Flet apps can be executed as either desktop or web applications using the [`flet run`](https://docs.flet.dev/cli/flet-run/) command. Doing so will start the app in a native OS window or a web browser, respectively, with hot reload enabled to view changes in real-time.

Desktop app[#](https://docs.flet.dev/getting-started/running-app/#desktop-app "Permanent link")
-----------------------------------------------------------------------------------------------

To run Flet app as a desktop app, use the following command:

uv pip poetry

```
uv run flet run
```

```
flet run
```

```
poetry run flet run
```

When you run the command without any arguments, `main.py` script in the current directory will be executed, by default.

If you need to provide a different path, use the following command:

uv pip poetry

```
uv run flet run [script]
```

```
flet run [script]
```

```
poetry run flet run [script]
```

Where `[script]` is a relative (ex: `counter.py`) or absolute (ex: `/Users/john/projects/flet-app/main.py`) path to the Python script you want to run.

The app will be started in a native OS window:

*   **macOS**

* * *

[![Image 1: macOS](https://docs.flet.dev/assets/getting-started/counter-app/macos.png)](https://docs.flet.dev/assets/getting-started/counter-app/macos.png)

*   **Windows**

* * *

[![Image 2: Windows](https://docs.flet.dev/assets/getting-started/counter-app/windows.png)](https://docs.flet.dev/assets/getting-started/counter-app/windows.png)

Web app[#](https://docs.flet.dev/getting-started/running-app/#web-app "Permanent link")
---------------------------------------------------------------------------------------

To run Flet app as a web app, use the `--web` (or `-w`) option:

uv pip poetry

```
uv run flet run --web [script]
```

```
flet run --web [script]
```

1.   A fixed port can be specified using `--port` ( or `-p`) option, followed by the port number.

```
poetry run flet run --web [script]
```

1.   A fixed port can be specified using `--port` ( or `-p`) option, followed by the port number.

A new browser window/tab will be opened and the app will be using a random TCP port:

[![Image 3: Web](https://docs.flet.dev/assets/getting-started/counter-app/safari.png)](https://docs.flet.dev/assets/getting-started/counter-app/safari.png)

Web app

Watching for changes[#](https://docs.flet.dev/getting-started/running-app/#watching-for-changes "Permanent link")
-----------------------------------------------------------------------------------------------------------------

By default, Flet will watch the script file that was run and reload the app whenever the contents of this file are modified+saved, but will **not** watch for changes in other files.

To modify this behavior, you can use one or more of these [`flet run`](https://docs.flet.dev/cli/flet-run/) options:

*   `-d` or `--directory` to watch for changes in the `[script]`s directory only
*   `-r` or `--recursive` to watch for changes in the `[script]`s directory and all sub-directories recursively

Example

uv pip poetry

```
uv run flet run --recursive [script]
```

```
flet run --recursive [script]
```

```
poetry run flet run --recursive [script]
```