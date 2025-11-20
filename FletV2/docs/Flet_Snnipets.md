## Flet 0.28.3 Quick Snippets & Best Practices

This compact cheat-sheet (Flet 0.28.3) summarizes the most important controls, idioms, recommended patterns, anti-patterns, and recovery tips for building desktop-first Flet apps. It's based on the official Flet docs (Context7 `/flet-dev/flet`) and the project's FletV2 conventions.

Keep this file short and practical — use it as your daily reference when building views, background tasks, or interactive components.

---

### Core concepts (one-liners)
- Page lifecycle: `page` is the root UI object. Use `page.theme`, `page.dark_theme`, `page.theme_mode` to control look-and-feel.
- Background tasks: use `page.run_task(coro)` to start background coroutines tied to the page lifecycle (cancellable in `dispose` / `will_unmount`).
- References: use `ft.Ref[T]()` for dynamic controls and call `ref.current.update()` (or control.update()) to refresh a small part of the UI.
- Virtual lists: `ft.ListView` with `semantic_child_count` and `cache_extent` for large/virtualized lists.
- Tables: `ft.DataTable` for small/medium tabular data; for huge sets prefer ListView + server pagination.
- Animations: `ft.AnimatedSwitcher` and control implicit animations (`animate`, `animate_opacity`) for microinteractions.

---

### Essential controls & methods (frequently used)
- ft.Ref[T](): typed reference holder for controls. Use when you need targeted updates.
- page.run_task(coro): run background coroutine; cancel by toggling a flag in `dispose()` or stopping the coroutine loop.
- ft.ListView(expand=1, semantic_child_count=..., cache_extent=...): virtualized list control.
- ft.DataTable(columns=[...], rows=[...], on_sort=..., on_select_changed=...): tabular UI with events.
- ft.ProgressBar(value=0.0): show 0.0–1.0 progress for CPU/Mem/Disk visualizations.
- ft.AnimatedSwitcher(content=..., transition=..., duration=...): smooth content swaps.
- ft.Container(theme=ft.Theme(...), theme_mode=ft.ThemeMode.DARK): nested theme overrides.
- page.update() vs control.update(): Prefer control.update() for specific control refresh; use page.update() for global layout changes.

---

### Good practices (recommended)
1. Use ft.Ref for dynamic controls
   - Create refs for hero numbers, progress bars, ListView, DataTable references.
   - Update only the control that changed: ref.current.value = 'x'; ref.current.update()

2. Keep expensive work off the UI thread
   - If server or CPU-bound work is synchronous, call it via the event loop executor:
     - `loop = asyncio.get_event_loop(); await loop.run_in_executor(None, sync_fn)`
   - Use page.run_task() for long-running coroutines so the page manages lifecycle.

3. Batch updates when populating large lists
   - Append controls in batches and call page.update() periodically (e.g., every 200–500 items).

4. Prefer Flet native controls
   - Use `ListView` and `DataTable` instead of custom heavy widgets. They provide virtualization and built-in features.

5. Theme & tokens
   - Set `page.theme` and `page.dark_theme` at startup. Use token constants (semantic colors) not hardcoded hex values.

6. Asynchronous server calls supporting sync/async methods
   - Detect coroutine functions with `asyncio.iscoroutinefunction(meth)` and `await` them; otherwise run them in an executor.

7. Use `page.run_task(refresh_loop)` not `asyncio.create_task` in Flet views
   - `page.run_task` ties the coroutine to page lifecycle; the task will be stopped when the page is closed.

---

### Anti-patterns (what to avoid) and recovery
- Blocking work on UI thread
  - Symptom: UI freezes / app is unresponsive during heavy operations.
  - Cause: calling CPU-heavy or blocking network calls directly in event handlers.
  - Fix: move to `await loop.run_in_executor(None, sync_fn)` or make server methods async and await them.

- Overusing `page.update()` for micro updates
  - Symptom: poor performance, full UI reflows.
  - Cause: calling `page.update()` when only one small control changed.
  - Fix: use `ref.current.update()` or `control.update()` for targeted refreshes.

- Creating coroutines but never awaiting them
  - Symptom: tasks never run or raise warnings; memory leaks.
  - Fix: pass coroutine to `page.run_task(coro)` or `await` explicitly inside an async handler.

- Using `asyncio.run()` inside event handlers
  - Symptom: RuntimeError (event loop running) or nested loop problems.
  - Fix: use `await` inside async functions or run synchronous code in executor.

- Global mutable UI state
  - Symptom: conflicting updates from multiple views, hard-to-trace bugs.
  - Fix: prefer `StateManager` (repository pattern) or pass refs and use callbacks to sync state.

---

### Patterns for ServerBridge / sync-or-async call handling
Small helper pattern to call a server method that may be sync or async:

```python
import asyncio

async def safe_call(server, method_name, *args, **kwargs):
    meth = getattr(server, method_name, None)
    if meth is None:
        raise AttributeError(f"Server missing method: {method_name}")
    if asyncio.iscoroutinefunction(meth):
        return await meth(*args, **kwargs)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: meth(*args, **kwargs))
```

Recovery tips: always wrap calls with try/except and present a non-blocking error via `page.snack_bar` or helper `show_error_message(page, msg)`.

---

### Performance tips (practical)
- Use `ListView(semantic_child_count=..., cache_extent=...)` for large datasets. Set `item_extent` when possible.
- For huge lists, build rows in a worker and send them in chunks; use page.run_task to schedule background assembly.
- Avoid frequent layout-changing animations on containers that hold many children. Prefer opacity/scale microanimations for small items.

---

### Accessibility & keyboard UX
- Provide `semantics_label` for icons, main numbers, charts.
- Ensure tab order: header actions first, then primary content, list rows focusable.
- Keyboard shortcuts: hook into `page.on_keyboard` for global shortcuts and ensure actions are reachable by Enter/Space.

---

### Testing tips (flet.testing.tester)
- Use `from flet.testing.tester import Tester` and run the view inside `with Tester() as tester:`.
- Use `tester.wait_for(seconds)` to let background tasks run and `tester.page` to access the page object.
- Tests should use a `DummyBridge` with deterministic data and avoid real network I/O.

Small test pattern:

```python
from flet.testing.tester import Tester
from views.dashboard_new import create_dashboard_view

def test_dashboard_renders():
    bridge = DummyBridge()
    with Tester() as tester:
        page = tester.page
        control, dispose, setup = create_dashboard_view(bridge, page, None)
        page.add(control)
        setup()
        tester.wait_for(0.2)
        assert "Clients" in page.controls[0].to_string()
        dispose()
```

---

### Small snippets (copy/paste)
- Run background loop safely:

```python
async def refresh_loop():
    stopped = False
    while not stopped:
        await refresh_data()
        await asyncio.sleep(5)

# start
page.run_task(refresh_loop)
```

- Use refs for progress:

```python
cpu_ref = ft.Ref[ft.ProgressBar]()
cpu_ref.current.value = usage / 100.0
cpu_ref.current.update()
```

---

### Final quick checklist
- Use `ft.Ref` + `control.update()` for targeted updates.  (YES)
- Use `page.run_task()` for background tasks.  (YES)
- Offload sync/blocking work to executor.  (YES)
- Avoid page.update() for micro changes.  (YES)
- Use ListView virtualization for long lists.  (YES)
- Provide accessibility labels and keyboard hooks.  (YES)

---

References
- Official Flet docs (Context7): `/flet-dev/flet` (controls, theming, async cookbook, ListView, DataTable, AnimatedSwitcher, refs)

Created for the FletV2 project — keep this file under 500 LOC and update when you upgrade Flet.

---

### Theming & Nested Themes (deep dive)
- Use `page.theme` and `page.dark_theme` to set global palettes. Prefer `color_scheme_seed` or `ft.ColorScheme` to derive semantic tokens.
- Nested theme overrides: any `Container` or control can accept a `theme=` and `theme_mode=` to create micro-areas with different color schemes (great for focal cards or side panels).
- Semantic tokens to prefer: primary, secondary, surface, surface_variant, background, error, on_surface, on_primary. Use these instead of raw hex colors.
- Light/dark mode: detect user preference via `page.theme_mode = ft.ThemeMode.SYSTEM` and provide toggle in Settings that switches `page.theme_mode` then `page.update()`.
- Keep contrast in mind: verify foreground/background contrast for key text and hero numbers (>4.5:1 recommended).

Snippet — nested theme card:

```python
card = ft.Container(
      theme=ft.Theme(color_scheme_seed=ft.Colors.PINK),
      theme_mode=ft.ThemeMode.LIGHT,
      content=ft.Column([ft.Text('Focal card'), ft.ElevatedButton('Action')]),
)
```

### Animations & Microinteractions
- Use `ft.AnimatedSwitcher` for swapping content (panels, hero values) with transitions (SCALE, SLIDE, FADE).
- Implicit animations: set `animate_opacity`, `animate_transform`, or `animate` on controls to animate property changes. Keep durations 100–400ms.
- Avoid animating layout-heavy properties (width/height) frequently — prefer opacity/scale transforms which are cheaper.
- Use `on_animation_end` hooks for chaining UI updates or starting follow-ups.

Example — AnimatedSwitcher:

```python
switcher = ft.AnimatedSwitcher(content=first, transition=ft.AnimatedSwitcherTransition.SCALE, duration=250)
switcher.content = second
page.update()
```

### DataTable — advanced usage
- Use `DataTable` for medium-size tables. For very large datasets, implement server-side pagination or switch to `ListView` virtualization.
- Enable selectable rows (`show_checkbox_column=True`) and handle `on_select_changed` on `DataRow`.
- Sorting: use `DataColumn(on_sort=...)` and update `data_table.sort_column_index` / `sort_ascending`.
- Row events: `on_tap` on `DataRow` receives the event with `e.control.index` — use it to open detail panels.
- Accessibility: provide semantic labels or hidden Text descriptions for complex cells.

Snippet — server-side pagination pattern (high-level):

```python
# fetch page N -> build rows -> data_table.rows = rows; data_table.update()
```

### page.run_task patterns (safe background tasks)
- Start background loops with `page.run_task(coro)` — Flet ties task to page lifecycle.
- Cancellation: use a `self._running` flag checked by the loop and set it False in `dispose()` or `will_unmount()`.
- Exception handling: wrap loop body in try/except and surface short errors via `page.snack_bar` or `show_error_message`.
- Avoid `asyncio.create_task()` inside views — it escapes page lifecycle and may leak tasks.

Robust background loop template:

```python
async def refresh_loop():
      try:
            while self.running:
                  try:
                        await refresh_data()
                  except Exception as ex:
                        logger.exception('refresh failed')
                        show_error_message(page, 'Refresh failed')
                  await asyncio.sleep(POLL_INTERVAL)
      finally:
            # cleanup if needed
            pass

page.run_task(refresh_loop)
```

### Refs & control patterns (practical)
- Use typed refs: `ft.Ref[ft.Text]()` or `ft.Ref[ft.ListView]()` to keep direct references.
- Use `ref.current` only after the control has been added to the page. Guard null checks in complex flows.
- Focus management: `await ref.current.focus()` inside async handlers to move keyboard focus.
- Isolated custom controls: implement `is_isolated()` returning True so the control manages its own updates via `self.update()`.

### ListView & large-lists (performance)
- Virtualization: `ListView` renders on-demand. Use `semantic_child_count` and `cache_extent` for better semantics and smoother scrolling.
- item_extent: set a fixed `item_extent` when item heights are uniform — large perf win.
- Batching: append controls in batches and call `page.update()` every N items to avoid floods.
- auto_scroll: use `auto_scroll=True` for chat-like streams, and `lv.controls.append()` then `lv.update()` for targeted changes.

### Colors, Icons & Tokens
- Use `ft.Colors` constants and `Icons` (e.g., `ft.Icons.REFRESH`, `ft.Icons.PLAY_ARROW`) instead of ad-hoc strings.
- Maintain a small token module in your project with semantic names: PRIMARY, SUCCESS, WARNING, SURFACE, SURFACE_ELEVATED.
- Use `page.theme` to set `color_scheme_seed` and derive all tokens.

### Testing patterns (expanded)
- Unit tests with `flet.testing.tester.Tester`: run views headlessly with `with Tester() as tester:`. Use `tester.page.run_task()` for long-running coroutines in tests.
- Use `DummyBridge` for deterministic server data. Avoid real network I/O.
- Use `tester.wait_for(seconds)` to let background tasks run. Prefer short waits (0.05–0.5s) and deterministic signals where possible.
- Integration tests: use `ft.app` in a test process or CI job, or run `flet` integration harness shown in the official repo for golden screenshots.

### Common errors & the right way (quick guide)
- Error: UI freeze during sync server call
   - Wrong: calling long sync method directly in on_click
   - Right: `await loop.run_in_executor(None, sync_call)` or make it async and `await`.

- Error: page.update() overused -> sluggish UI
   - Wrong: calling `page.update()` for every small change
   - Right: use `ref.current.update()` or `control.update()` for targeted refreshes.

- Error: tasks leak after page closed
   - Wrong: `asyncio.create_task(loop())` inside view
   - Right: `page.run_task(loop)` and use a running flag to exit loop in `dispose()`.

- Error: AttributeError for ref.current
   - Wrong: using `ref.current` before control is added to the page
   - Right: check `if ref.current is None: return` or only access refs after page.add(control) and page.update()

- Error: FilePicker Zenity failure on Linux
   - Wrong: assuming native dialog always available
   - Right: require and document Zenity for Linux desktop builds or fall back to browser mode for uploads.

---

References (official snippets used)
- `/flet-dev/flet` — theming, async cookbook, controls, ListView, DataTable, FilePicker, animations, testing snippets

