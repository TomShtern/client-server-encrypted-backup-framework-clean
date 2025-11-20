# Flet Dashboard Implementation Prompt — 2025-09-29

Purpose
- Provide a concise, complete prompt an AI coding agent can use to implement a production-ready Flet dashboard that fits into this repository (FletV2). The generated dashboard must integrate with the existing `ServerBridge`, `StateManager`, theme, and Flet 0.28.3 desktop idioms used across the codebase.

Goal for the agent
- Produce a `create_dashboard_view(server_bridge, page, state_manager) -> (ft.Control, dispose, setup)` function in `FletV2/views/` that:
  - Uses Flet 0.28.3 idioms and the project's helper modules (theme, ui_components, user_feedback).
  - Returns a tuple: (root_control, dispose_callable, setup_subscriptions_callable). This matches repository conventions.
  - The GUI will be passed a live server object (not HTTP/API). The view should call methods
    on that server object directly (function calls). Do NOT implement network/API fallbacks.
    Only allow a development-time placeholder mode that displays simple "lorem ipsum" text
    when a real server object is intentionally not provided. This placeholder mode must be
    explicitly enabled and documented; do not invent or use alternate fallback bridges.
  - Is performant, testable, accessible, and uses theme TOKENS.

Important context (must be respected)
- Flet version: 0.28.3 (desktop-first). Use desktop properties (window sizing, NavigationRail, ResponsiveRow) where appropriate. See `FletV2/important_docs/Flet_0_28_3_Desktop_GUI_Excellence_Guide.md` and `FletV2/important_docs/FLET_DESKTOP_GUIDE.md`.
 - Server bridge contract: UI must call `ServerBridge` methods. The bridge is expected to be a live, in-process server object passed to the view; do NOT implement automatic fallback or mock bridges inside the view. Any mock/dummy bridge should be used only by tests (see `Final_ServerBridge07092025.md`). Do NOT bypass ServerBridge.
- View signature convention: function should accept (server_bridge, page, state_manager) and return tuple `(ft.Control, dispose, setup_subscriptions)`.
- Update pattern: prefer ft.Ref and control.update() for local updates (10x perf). Use page.run_task() for long-running tasks and run blocking I/O in executor.
- Flet-style components: prefer Flet-native controls and small composition over complex custom controls (see `Flet_Style_Components_Documentation.md`).

Contract: inputs, outputs, error modes
- Inputs:
  - server_bridge: ServerBridge (a live server object passed into the view). The view will
    invoke functions on this object directly (e.g., `server.get_system_status()`); these are
    NOT HTTP/API calls. The server object may provide sync or async methods; the view must
    handle both. Only in explicit development/no-server mode may `server_bridge` be None,
    and in that case the UI must use a single simple 'lorem ipsum' placeholder for textual
    content — do not implement multi-mode fallbacks or mock bridges unless explicitly asked.
  - page: ft.Page
  - state_manager: StateManager | None (can be used to subscribe/publish app state)
- Outputs:
  - root ft.Control (Container/Column) to be inserted into the app content area
  - dispose(): cancel background tasks, unsubscribe state_manager callbacks, cleanup resources
  - setup_subscriptions(): start background polling/refresh tasks, attach StateManager subscriptions
- Error modes:
  - If server calls fail, the UI shows non-blocking error notifications (snackbar) and enters a clear error state or shows last-known data where appropriate. Do NOT implement automatic fallback to mock bridges or alternate in-view bridges when production server calls fail.
  - If `server_bridge` is None, this must be an explicit development/testing mode. In that special case the view should display a single, clearly labelled "lorem ipsum" placeholder for textual areas and must disable interactive actions. Do not implement multi-mode fallbacks or in-view mock servers; tests should use `DummyBridge` (see below) instead.

Data shapes (examples)
- System status (from `server_bridge.get_system_status()`): {
    'success': True,
    'data': {
        'running': bool,
        'clients_connected': int,
        'total_files': int,
        'storage_used_gb': float,
        'uptime_seconds': int,
        'cpu_usage': int (0-100),
        'memory_usage': int (0-100),
    }
  }
- Clients list (from `server_bridge.get_clients()`): {'success': True, 'data': [ { 'id': bytes|str, 'name': str, 'status': str, 'last_seen': str }, ... ]}
- Activity entries: list of dicts with { 'time': ISO8601, 'client': str, 'action': str, 'status': 'Complete'|'In Progress'|'Error' }

High-level UI layout (recommended)
1. Header / Title area
   - Page title, last-refresh timestamp, one-line status pill (connected/disconnected)
   - Primary action buttons: Refresh, Export Report, Settings
2. Hero metrics row (responsive)
   - Total clients, Active transfers, Storage used (GB/%), Server uptime
   - Each as a compact hero card with a big number (ft.Text), small delta and an icon
3. Performance row
   - CPU, Memory, Disk usage as ProgressBars with numeric labels
4. Activity stream (ListView)
   - Virtualized ListView with semantic child count and auto_scroll
   - Each entry: client, action, time, small status pill, optional action menu
5. Recent files/operations table (DataTable or ListView)
   - Paginated or virtualized; supports quick filter and export
6. Footer / debug area (collapsed by default)
   - Small area for last API error, quick logs

UX & Interaction patterns
- Refresh behavior
  - Manual: Refresh button triggers an async refresh_data() that uses `await page.run_task()` patterns.
  - Auto: Optional background refresh loop started in setup_subscriptions (configurable by environment variable). Use `page.run_task(refresh_loop)` not asyncio.create_task when page supports it.
- Loading & Empty states
  - Show skeletons or placeholder text while data is loading. Show empty states with actions (e.g., "No clients connected — open Clients view").
- Actions
  - Card click drills into details (navigate or open drawer). Use `page.route` or a callback to open detail view.
- Accessibility
  - Use apply_semantics/semantics_label where available and consistent focus order. Provide keyboard shortcuts for primary actions.

Performance rules (strict)
- Use ft.Ref for all dynamic text and progress controls. Avoid searching the control tree.
- Call control.update() for each control after mutation. Avoid page.update() except for complex layout changes.
- Use ListView with `semantic_child_count` and `cache_extent` for large lists.
- Run heavy work in thread-pool via `await asyncio.get_event_loop().run_in_executor(None, sync_fn)`.

State manager integration
- If `state_manager` is provided, subscribe to keys like 'server_status', 'clients', 'activities' and update UI via callbacks.
- On dispose(), unsubscribe all state_manager listeners.

Background polling pattern (example)
- `async def refresh_loop():`
    while not stopped:
        await refresh_data()
        await asyncio.sleep(POLLING_INTERVAL)
- Start with `page.run_task(refresh_loop)` in `setup_subscriptions()` and cancel in `dispose()`.

Logging & user feedback
- Use `utils.user_feedback.show_success_message(page, msg)` and `show_error_message` for toasts/snackbars.
- Log detailed failures with logger.debug() / logger.exception() where available.

Tests to include (automated)
- Unit/component tests (Flet Tester):
  - `test_create_dashboard_view_returns_tuple` — ensures signature and types
  - `test_update_data_with_dummy_bridge` — uses `DummyBridge` in tests to verify UI updates hero metrics and progress bars
  - `test_refresh_loop_runs_and_updates` — simulate a couple of refresh cycles with flet.testing.tester.Tester
- Integration test:
  - Start Flet app with a test `DummyBridge()` (or a real `ServerBridge()` in an integrated environment) and assert that key controls show expected values after setup_subscriptions runs.

Files to create / modify
- New view file: `FletV2/views/dashboard_new.py` (or overwrite `views/dashboard.py` after review)
- Add tests: `FletV2/test_dashboard_new.py` (minimal unit tests using flet.testing.tester)
- Small helper (if needed): `FletV2/utils/dashboard_helpers.py` — normalization functions, uptime formatter, color maps

Implementation steps (sequential thinking)
1. Create the function skeleton with signature and explicit return tuple. Add module-level imports and path-bootstrapping consistent with repository style.
2. Create ft.Refs for all dynamic controls (hero numbers, progress bars, list views, status text).
3. Implement `get_server_data()` that calls `server_bridge.get_system_status()` safely via `safe_server_call` pattern. Normalize payload into expected keys.
4. Implement `update_data()` that writes into refs and calls control.update() for each mutated control.
5. Implement `refresh_data()` coroutine that wraps `get_server_data()` with thread-pool if necessary and handles errors with `show_error_message`.
6. Implement `refresh_loop()` and ensure cancellation via `dispose()`.
7. Wire header actions and drill-in navigation handlers.
8. Add `setup_subscriptions()` to start background task and register `state_manager` listeners (if provided).
9. Add `dispose()` that cancels tasks and removes subscriptions.
10. Add unit tests using `flet.testing.tester.Tester` to validate public contract.

Edge cases and assumptions
- Assume `server_bridge` methods may return either legacy dict (`{'success': True, 'data': {...}}`) or direct dict data. Normalization must handle both.
 - Assume sometimes `server_bridge` returns non-dict (None) — treat as missing data/placeholder and handle gracefully (show placeholder or last-known data, and surface a non-blocking error message). Do NOT implement an in-view mock or alternate bridge to replace the server.
- Avoid putting heavy work at module import time.
- Avoid reliance on global mutable state; keep state local to the view and use `state_manager` for cross-view sync.

Acceptance criteria (what "done" looks like)
- The view function exists and returns (control, dispose, setup) with correct types.
 - The view shows hero metrics, progress bars, and an activity stream populated from the provided `ServerBridge` (use `DummyBridge` in tests) without errors.
- Background refresh loop runs without blocking the UI and can be stopped by `dispose()`.
- All dynamic updates use refs + control.update(), not page.update().
 - Tests pass locally using the project's virtualenv (`flet_venv`).

How to run & verify locally
```powershell
# from repo root
cd FletV2
# (activate flet_venv first)
# run the app in browser/dev mode
& ..\flet_venv\Scripts\python.exe main.py
# run the dashboard unit tests
& ..\flet_venv\Scripts\python.exe -m pytest FletV2/test_dashboard_new.py -q
```

Deliverable for the AI agent (concise checklist)
- [ ] Create `create_dashboard_view(server_bridge, page, state_manager)` in `FletV2/views/dashboard_new.py` following this prompt
- [ ] Implement safe server calls and normalization helpers
- [ ] Use ft.Ref and control.update() for all dynamic updates
- [ ] Implement background refresh with page.run_task and graceful cancellation
- [ ] Add 2–3 unit tests using flet.testing.tester
- [ ] Ensure fallback mode (ServerBridge with no real server) shows realistic mock values

Notes for reviewers
- Prefer small, readable functions (each helper < 120 LOC) and keep the module < 500 LOC.
- If advanced charts are requested later, add them in a separate module to avoid inflating the main dashboard file.

References (use as authoritative)
- `FletV2/important_docs/Flet_0_28_3_Desktop_GUI_Excellence_Guide.md`
- `FletV2/important_docs/FLET_DESKTOP_GUIDE.md`
- `FletV2/important_docs/Final_ServerBridge07092025.md`
- `FletV2/important_docs/Flet_Style_Components_Documentation.md`
- `FletV2/important_docs/DashBoard_Design_Freamework_Agnostic_guide.md`

---

Generated by sequential reasoning on 2025-09-29. This file is intended to be the single authoritative prompt passed to an AI coding agent to generate a new repository-compatible dashboard view.

## Additions: concrete implementation guidance, API contracts, examples

Below are concrete, copy-pasteable items and focused recipes gathered from Flet official docs and curated examples (Flet 0.28.3, Python 3.13.5). Use these directly in the generated view and tests.

### 1) Concrete ServerBridge API (required)
Include these methods on the `ServerBridge` used by the UI. Implementations should accept either sync or async calls; UI must handle both patterns.

- get_system_status() -> dict | {'success': bool, 'data': {...}}  # primary dashboard payload
- get_clients() -> dict | {'success': True, 'data': [ {id, name, status, last_seen}, ... ]}
- get_activities(limit: int = 100) -> dict | {'success': True, 'data': [{time, client, action, status}, ...]}
- get_files(page: int = 1, per_page: int = 50) -> dict
- subscribe_events(callback) -> subscription_handle  # Optional: server push events (function-calls)
- unsubscribe_events(handle)

Notes for implementers:
- These are direct function calls on the provided server object — NOT network/API calls. Handle both
  synchronous and awaitable (async) methods. The view should detect coroutine functions (asyncio.iscoroutinefunction)
  and `await` them or call them directly accordingly.
- Each method may return either a raw payload dict or the envelope {'success': True, 'data': {...}}; normalize both.
- If a method raises, the view should present a concise, non-blocking user error message (snackbar) and log the
  exception. Do NOT implement alternate fallback bridges. If the server object is absent by explicit dev choice,
  show a single, clearly-labeled 'lorem ipsum' placeholder for textual areas and disable interactive actions.

Coroutine detection snippet (copy-paste):

```python
import asyncio

async def safe_call(server, method_name, *args, **kwargs):
  """Call a server method that may be sync or async. Returns normalized dict or raises."""
  meth = getattr(server, method_name, None)
  if meth is None:
    raise AttributeError(f"Server missing method: {method_name}")
  # If it's an async function, await it; otherwise call directly (run in executor if blocking)
  if asyncio.iscoroutinefunction(meth):
    return await meth(*args, **kwargs)
  # sync method - call directly but keep UI thread safe by offloading heavy work
  loop = asyncio.get_event_loop()
  return await loop.run_in_executor(None, lambda: meth(*args, **kwargs))
```

### 2) DummyBridge sample (copy-paste for tests)
Use this in unit tests and integration harnesses to provide deterministic data.

```python
class DummyBridge:
  def get_system_status(self):
    return {
      'success': True,
      'data': {
        'running': True,
        'clients_connected': 3,
        'total_files': 128,
        'storage_used_gb': 12.5,
        'uptime_seconds': 12345,
        'cpu_usage': 12,
        'memory_usage': 34,
        'activities': [
          {'time': '2025-09-29T14:00:00Z', 'client': 'client-a', 'action': 'send_file', 'status': 'Complete'},
        ],
      }
    }

  def get_clients(self):
    return {'success': True, 'data': [{'id': 'a', 'name': 'client-a', 'status': 'online', 'last_seen': '2025-09-29T14:00:00Z'}]}

  def get_activities(self, limit=50):
    return {'success': True, 'data': []}
```

### 3) Theming & Tokens (Material 3 foundation)
Use Flet's Theme system and `color_scheme_seed` to create consistent Material 3 palettes. Prefer nested `ft.Container(theme=...)` overrides for micro-areas.

Example (page-level and nested overrides):

```python
page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

# Local override for a card
card = ft.Container(
  theme=ft.Theme(color_scheme=ft.ColorScheme(primary=ft.Colors.PINK)),
  content=ft.Text('Card with override')
)
```

Guidelines:
- Keep a small token file (theme tokens) with semantic tokens: primary, surface, success, warn, error, neutral, surface_elevated.
- Avoid hard-coded hex values in views — reference tokens.

### 4) Neumorphism recipe (structure)
Neumorphism can be simulated by layering containers with subtle shadowing and soft colors. Use slightly raised and inset containers to create the tactile effect.

Implementation notes (Flet):
- Use `ft.Container` with `border_radius` and `bgcolor` set to a neutral surface token.
- Add two shadows/emulated offsets: one light at -2, -2 and one dark at 2, 2 to simulate indent/extrude. Flet supports `ft.BoxShadow` on many controls; if unavailable, use `elevation` and subtle border.

Example:

```python
neumorphic = ft.Container(
  content=ft.Text('Neumo card'),
  padding=16,
  border_radius=12,
  bgcolor=ft.Colors.SURFACE,
  shadow=ft.BoxShadow(offset=ft.Offset(2, 2), blur_radius=8, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
)
```

If `ft.BoxShadow` is not available on a platform, fallback to `bgcolor` + `border` with subtle highlights.

### 5) Glassmorphism recipe (focal point)
Glassmorphism in Flet is achieved by translucent backgrounds and bright borders. Native backdrop-blur is not always available, so prefer the visual illusion: semi-transparent background + subtle border + elevated shadow.

Example:

```python
glass_card = ft.Container(
  content=ft.Column([ft.Text('Important metric'), ft.Text('42')]),
  padding=16,
  border_radius=14,
  bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
  border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
  shadow=ft.BoxShadow(blur_radius=12, offset=ft.Offset(0, 6), color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
)
```

Note: On dark themes invert the opacity and border colors accordingly.

### 6) Material 3 components & microinteractions (foundation)
Use Flet built-in controls (ElevatedButton, IconButton, DataTable, ProgressBar, ListView, AnimatedSwitcher). For microinteractions:

- Use implicit animations: `container.animate = ft.Animation(duration, curve)` or property-specific like `container.animate_opacity = 300`.
- Use `ft.AnimatedSwitcher` for content transitions (scale, fade, slide).
- Use `on_animation_end` to chain interactions or update metrics.

Examples (from Flet cookbook):

```python
# AnimatedSwitcher
sw = ft.AnimatedSwitcher(content=container1, transition=ft.AnimatedSwitcherTransition.SCALE, duration=500)

# Container implicit animation
box = ft.Container(width=100, height=100, bgcolor=ft.Colors.BLUE)
box.animate_opacity = 300
box.opacity = 0
box.update()
```

### 7) Microinteraction guidelines (practical)
- Keep animations short (100–400ms) and meaningful (feedback, state change).
- Avoid animating layout-heavy properties frequently (reflows are expensive).
- Use AnimatedSwitcher for swapping panels; use opacity/scale for emphasis.

### 8) Accessibility checklist (must-haves)
- Provide `semantics_label` for icons and important numbers.
- Ensure color contrast > 4.5:1 for primary text over backgrounds (use tokens tuned for contrast).
- Keyboard focus: primary actions reachable via Tab and triggers via Enter/Space.
- Provide ARIA-like textual descriptions for dense charts (hidden Text or accessible description strings).

### 9) Performance & scale budgets (practical)
- Use `ft.Ref` for dynamic controls and call `control.update()` on the specific control.
- Use ListView with `semantic_child_count` and `cache_extent` for large lists (500+ entries).
- Limit background polling default to 5s; allow operator to increase it.
- Avoid expensive per-row Python logic inside the UI thread; move heavy aggregation to worker threads or the server.

### 10) Testing snippets (flet.testing.tester)
Use a headless tester to validate view construction and a couple of refresh cycles. Example pattern:

```python
from flet.testing.tester import Tester
from views.dashboard_new import create_dashboard_view

def test_dashboard_constructs_and_updates():
  bridge = DummyBridge()
  with Tester() as tester:
    page = tester.page
    control, dispose, setup = create_dashboard_view(bridge, page, None)
    page.add(control)
    # start background subscriptions (runs in tester loop)
    setup()
    # allow loop to run a couple cycles
    tester.wait_for(0.2)
    # assert some text exists
    assert 'Clients' in page.controls[0].to_string()
    dispose()
```

Notes:
- If your tests run into EventLoop issues, prefer using `tester.page.run_task()` and the tester's timing utilities.

### 11) CI snippet (GitHub Actions)
Run lint and tests in the venv. Minimal job:

```yaml
name: python-ci
on: [push, pull_request]
jobs:
  test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Setup Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.11' # Match CI environment; adapt to 3.13 when available
    - name: Install deps
    run: python -m pip install -r requirements.txt
    - name: Lint
    run: python -m ruff check .
    - name: Run tests
    run: python -m pytest -q
```

### 12) Run & verify locally (copyable)
PowerShell commands (from repo root):

```powershell
cd FletV2
& ..\flet_venv\Scripts\Activate.ps1
& ..\flet_venv\Scripts\python.exe main.py
# or run tests
& ..\flet_venv\Scripts\python.exe -m pytest -q
```

### 13) Acceptance criteria (expanded & measurable)
- `create_dashboard_view` exists and returns `(control, dispose, setup)` and types validate.
- With `DummyBridge`, calling `setup()` must update hero metrics within 2 seconds (testable with `Tester`).
- `dispose()` cancels background tasks and unsubscribes state_manager listeners.
- All dynamic updates use `ft.Ref` + `control.update()` (spot-check in code review).
- Visual: hero cards, progress bars, activity list present and responsive.

---

## Flet GUI Design Schematic — refined (keep all three styles)

Keep the original three-style intent but make the division of responsibilities concrete and implementable in Flet:

- Material Design 3 (Foundation): Buttons, text, forms, primary color system, and interaction states. Implement via `page.theme = ft.Theme(color_scheme_seed=...)` and `ft.ElevatedButton`, `ft.IconButton`, and Material tokens.
- Neumorphism (Structure): Background panels and large baseplates implemented using `ft.Container` with `border_radius`, subtle `shadow` and neutral `bgcolor`. Use shallow shadows and complementary tones from theme tokens.
- Glassmorphism (Focal): Floating cards and modals implemented using semi-transparent `bgcolor` with high corner radius, subtle border, and elevated shadow. Use `ft.Container` and token-aware opacity helpers.

Small example composition:

```python
# Page theme
page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)

# Neumorphic base
base_panel = ft.Container(bgcolor=page.theme.color_scheme.surface_variant, padding=20, border_radius=16, shadow=ft.BoxShadow(...))

# Glass focal card
focus_card = ft.Container(bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE), border_radius=14, border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)))

# Use Material buttons inside
focus_card.content = ft.Column([ft.Text('Metric'), ft.ElevatedButton('Details')])
```

---

## Flet 0.28.3 reference snippets (quick lookup)

Below are short, copy-pasteable reference notes for common Flet 0.28.3 controls and APIs. Each item is one line (name) plus 1–2 sentences explaining common usage or important notes — useful as a quick reference while implementing the dashboard.

- `page.theme` / `page.dark_theme`: Configure app-wide light/dark themes using `ft.Theme` and `color_scheme_seed`. Use nested `ft.Container(theme=...)` overrides for micro-areas.
- `ft.Ref[T]`: Typed references to controls (e.g., `ft.Ref[ft.Text]()`); use `ref.current` to read/update controls and call `control.update()` for local refreshes.
- `page.run_task(coro)`: Run background async tasks tied to the page lifecycle (preferred over asyncio.create_task in Flet views). Cancel them in `dispose()`.
- `asyncio.iscoroutinefunction(func)`: Detect whether a server method is async; `await` it if True, otherwise run sync calls in an executor to avoid blocking the UI thread.
- `ft.ListView`: Virtualized, efficient list control; use `expand=True`, `semantic_child_count` and `cache_extent` for large lists and append controls incrementally.
- `ft.AnimatedSwitcher`: Smoothly animate content swaps (fade/scale/slide). Provide `transition` and `duration` to tune microinteractions for 100–400ms ranges.
- `ft.Container.animate_opacity` / `container.animate`: Implicit animation helpers to animate property changes (opacity, size, color) without manual animation loops.
- `ft.ProgressBar`: Simple progress indicator supporting `value` (0.0-1.0) and custom labels; use for CPU/memory/disk visualizations with numeric text alongside.
- `ft.DataTable`: Tabular control with `DataColumn` and `DataRow`/`DataCell`. Good for small-to-medium tables; for very large tables prefer virtualized ListView or server-side pagination.
- `ft.ElevatedButton` / `ft.IconButton`: Material 3 action controls — use icon buttons for compact actions (refresh, export) and ElevatedButton for primary CTAs.
- `ft.Toast` / Snackbar via `page.snack_bar` or helper wrappers: Show non-blocking feedback for success/error; prefer short messages and no blocking dialogs for transient errors.
- `ft.Offset`, `ft.BoxShadow`: Use for neumorphism shadows (small light and dark offsets); `BoxShadow` supports blur and color opacity for subtle depth.
- `ft.ThemeMode` and `ft.ColorScheme`: Use `ThemeMode.DARK` for nested dark sections and define semantic tokens in a small token file for consistency.
- `ft.app` / `ft.run` / `ft.app_async`: App entry helpers — `ft.app(target=main)` or `ft.run(main)` launches the Flet app; use `view=ft.AppView.WEB_BROWSER` for browser dev mode.

These snippets are intended as a compact cheat-sheet; for full details consult the official Flet docs (https://flet.dev/docs) or the project's Context7 doc excerpts added earlier.