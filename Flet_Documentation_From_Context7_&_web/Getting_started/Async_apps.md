# Async apps

Flet applications can be developed as asynchronous apps, allowing for the use of `asyncio` and other Python asynchronous libraries. This is particularly useful for applications that will be published as static websites using Pyodide, which does not support threading.

To create an async Flet app, you can mark the `main()` method as `async`, which allows you to use any `asyncio` API within it. For example:
```python
import flet as ft
import asyncio

async def main(page: ft.Page):
    await asyncio.sleep(1)
    page.add(ft.Text("Hello, async world!"))

ft.app(main)
```

Control event handlers can be either synchronous or asynchronous. If a handler needs to call async methods, it must be defined as an `async` function.

For delaying execution in an async Flet app, `asyncio.sleep()` should be used instead of `time.sleep()`.

To run background tasks, Flet provides the `page.run_task()` method. The documentation provides an example of a self-updating "Countdown" custom control that runs in the background.
