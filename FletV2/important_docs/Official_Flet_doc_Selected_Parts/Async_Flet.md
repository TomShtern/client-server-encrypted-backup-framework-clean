Title: Async apps - Flet

URL Source: http://docs.flet.dev/cookbook/async-apps/

Markdown Content:
[](https://github.com/flet-dev/flet/edit/main/sdk/python/packages/flet/docs/cookbook/async-apps.md "Edit this page")[](https://github.com/flet-dev/flet/raw/main/sdk/python/packages/flet/docs/cookbook/async-apps.md "View source of this page")
Flet app can be written as an async app and use `asyncio` and other Python async libraries. Calling coroutines is naturally supported in Flet, so you don't need to wrap them to run synchronously.

By default, Flet executes control event handlers in separate threads, but sometimes that could be an ineffective usage of CPU or it does nothing while waiting for a HTTP response or executing `sleep()`.

Asyncio, on the other hand, allows implementing concurrency in a single thread by switching execution context between "coroutines". This is especially important for apps that are going to be [published as static websites](https://docs.flet.dev/publish/web/static-website/) using [Pyodide](https://pyodide.org/en/stable/). Pyodide is a Python runtime built as a WebAssembly (WASM) and running in the browser. At the time of writing it doesn't support [threading](https://github.com/pyodide/pyodide/issues/237) yet.

Getting started with async[#](https://docs.flet.dev/cookbook/async-apps/#getting-started-with-async "Permanent link")
---------------------------------------------------------------------------------------------------------------------

You could mark `main()` method of Flet app as `async` and then use any asyncio API inside it:

```
import flet as ft

async def main(page: ft.Page):
    await asyncio.sleep(1)
    page.add(ft.Text("Hello, async world!"))

ft.run(main)
```

You can use `await ft.run_async(main)` if Flet app is part of a larger app and called from `async` code.

Control event handlers[#](https://docs.flet.dev/cookbook/async-apps/#control-event-handlers "Permanent link")
-------------------------------------------------------------------------------------------------------------

Control event handlers could be both sync and `async`.

If a handler does not call any async methods it could be a regular sync method:

```
def page_resize(e):
    print("New page size:", page.window.width, page.window.height)

page.on_resize = page_resize
```

However, if a handler calls async logic it must be async too:

```
async def main(page: ft.Page):

    async def button_click(e):
        await some_async_method()
        page.add(ft.Text("Hello!"))

    page.add(ft.Button("Say hello!", on_click=button_click))

ft.run(main)
```

### Async lambdas[#](https://docs.flet.dev/cookbook/async-apps/#async-lambdas "Permanent link")

There are no async lambdas in Python. It's perfectly fine to have a lambda event handler in async app for simple things:

```
page.on_error = lambda e: print("Page error:", e.data)
```

but you can't have an async lambda, so an async event handler must be used.

Sleeping[#](https://docs.flet.dev/cookbook/async-apps/#sleeping "Permanent link")
---------------------------------------------------------------------------------

To delay code execution in async Flet app you should use [`asyncio.sleep()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.sleep) instead of `time.sleep()`, for example:

```
import asyncio
import flet as ft

def main(page: ft.Page):
    async def button_click(e):
        await asyncio.sleep(1)
        page.add(ft.Text("Hello!"))

    page.add(
        ft.Button("Say hello with delay!", on_click=button_click)
    )

ft.run(main)
```

Threading[#](https://docs.flet.dev/cookbook/async-apps/#threading "Permanent link")
-----------------------------------------------------------------------------------

To run something in the background use [`page.run_task()`](https://docs.flet.dev/controls/page/#flet.Page.run_task "<code class=\"doc-symbol doc-symbol-heading doc-symbol-method\"></code>            <span class=\"doc doc-object-name doc-function-name\">run_task</span>"). For example, "Countdown" custom control which is self-updating on background could be implemented as following:

```
import asyncio
import flet as ft

class Countdown(ft.Text):
    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def did_mount(self):
        self.running = True
        self.page.run_task(self.update_timer)

    def will_unmount(self):
        self.running = False

    async def update_timer(self):
        while self.seconds and self.running:
            mins, secs = divmod(self.seconds, 60)
            self.value = "{:02d}:{:02d}".format(mins, secs)
            self.update()
            await asyncio.sleep(1)
            self.seconds -= 1

def main(page: ft.Page):
    page.add(Countdown(120), Countdown(60))

ft.run(main)
```

[![Image 1](https://docs.flet.dev/img/docs/getting-started/user-control-countdown.gif)](https://docs.flet.dev/img/docs/getting-started/user-control-countdown.gif)