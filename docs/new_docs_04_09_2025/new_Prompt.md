# PROMPT FOR CODING AGENT — FIX, STABILIZE & POLISH `flet_server_gui`

**Goal (short):**  
Make the Flet desktop GUI stable and polished: fix runtime exceptions, make server connectivity explicit and reliable in the UI, stabilize tables and renderers, fix navigation/resize/theme issues, and add small UX features (server status pill, activity-log detail popup, working notifications/help, consistent M3 theming and animations). Prefer Flet native controls when appropriate and keep changes minimal, well-tested, and modular.

---

## Top-level plan (priority order — do this in sequence)

1. **Bridge & connection API parity** — add missing APIs and connection callbacks.
  
2. **Table renderer contract** — implement base table manager/renderer interfaces used by views.
  
3. **Toast/snackbar manager** — centralize snackbars and inject into views.
  
4. **Server status UI** — implement a pill chip that shows ONLINE/OFFLINE (animated) and integrates with existing top-right icons.
  
5. **Fix crashing flows** — FilesView select_all, missing methods, and any AttributeError traces.
  
6. **Navigation & routing sync** — centralize navigation updates so highlight always matches route.
  
7. **Layout, theme, responsiveness fixes** — fix clipping, hitbox issues, settings window-mode layout, theme inconsistencies.
  
8. **UX polish: activity-log popup, notifications/help panel, dashboard offline placeholders, spinner skeletons**.
  
9. **Tests & CI** — add unit tests for bridge and renderer interfaces; run existing tests.
  

---

## Concrete tasks & exact file-level edits (copy/paste friendly)

### 1) Add/standardize server connection API (utils/)

**Files to edit/create**

- `utils/server_bridge.py` — ensure public API includes:
  
  - `get_clients() -> list[dict]`
    
  - `get_files() -> list[dict]`
    
  - `is_server_running() -> bool`
    
  - `get_notifications() -> list[dict]`
    
  - `register_connection_callback(cb: Callable[[bool], None]) -> None`
    
- `utils/simple_server_bridge.py` — ensure same minimal API for tests/mocks.
  
- `utils/server_connection_manager.py` — fire registered callbacks when status changes; expose `is_connected()`.
  

**Why:** GUI calls these names; patching here avoids ripping UI.

**Pseudo-patch** (illustrative):

```python
# utils/server_bridge.py
class ServerBridge:
    def __init__(self, ...):
        self._connected = False
        self._conn_callbacks = []

    def get_clients(self):
        return self.server_data_manager.get("clients") or []

    def get_files(self):
        return self.server_data_manager.get("files") or []

    def is_server_running(self):
        return self._connected

    def register_connection_callback(self, cb):
        self._conn_callbacks.append(cb)

    def _set_connected(self, value):
        self._connected = value
        for cb in self._conn_callbacks: cb(value)
```

**Acceptance:** `python -c "from flet_server_gui.utils.server_bridge import ServerBridge; b=ServerBridge(); print(b.get_clients(), b.get_files(), b.is_server_running())"` returns lists/False with no exception.

---

### 2) Implement base table manager/renderer & adapt renderers (components/)

**Files to edit/create**

- `components/base_table_manager.py` (exists) — extend to expose `update_table_data(columns, rows)`, `select_all_rows()`, `get_selected()`, `clear_selection()`.
  
- `components/client_table_renderer.py` & `components/file_table_renderer.py` — migrate to inherit base manager and implement `update_table_data` calls.
  
- `ui/widgets/tables.py` — ensure DataTable wrappers use the base manager API.
  

**Key details**

- Use `ft.DataTable` for moderate datasets; add pagination when row count > 300.
  
- All UI update methods must be called on the Flet main thread — use `page.call_later(...)` or `page.run_task(...)` when bridging background IO to UI updates.
  

**Pseudo-patch snippet**:

```python
# components/base_table_manager.py
class BaseTableManager:
    def __init__(self, page, container): 
        self.page = page
        self.container = container
        self.datatable = ft.DataTable(columns=[], rows=[])
    def update_table_data(self, columns, rows):
        self.datatable.columns = [ft.DataColumn(ft.Text(c)) for c in columns]
        self.datatable.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(x))) for x in r]) for r in rows]
        self.page.update()
    def select_all_rows(self):
        # maintain selected set
        ...
```

**Acceptance:** invoking `select_all_rows()` from `components/file_action_handlers.py` does not raise AttributeError.

---

### 3) Add ToastManager and inject into views (utils/ & components/)

**Files to edit/create**

- `utils/toast_manager.py` (new) or add in `utils/helpers.py`.
  
- Inject instance into views when `main.py` constructs screens. Example injection location: where `core` managers and `server_bridge` are created in `main.py`.
  

**Code sketch**:

```python
class ToastManager:
    def __init__(self, page): self.page = page
    def show(self, text, duration=3000):
        self.page.snack_bar = ft.SnackBar(ft.Text(text)); self.page.snack_bar.open = True; self.page.update()
```

**Acceptance:** calling `self.toast_manager.show("x")` from `components/files.py` shows a snack and never raises `AttributeError`.

---

### 4) Server status pill + top-right integration (ui/navigation.py, ui/widgets/buttons.py)

**Files to edit**

- `ui/navigation.py` or `ui/__init__.py` where the top app bar is defined.
  
- `ui/widgets/buttons.py` to create a shared `StatusPill` component.
  

**Behavior**

- Place a pill to the left of theme/notifications/help icons. Text: `ONLINE` / `OFFLINE`. Color: green/red. Animated transition when state changes. Tooltip: `Server connected` / `No server`.
  
- Source-of-truth: `utils/server_connection_manager.is_connected()` + callbacks via `register_connection_callback`.
  

**Pseudo**

```python
pill = StatusPill(page, bridge.is_server_running())
def on_conn(is_online):
    pill.set_state(is_online)
bridge.register_connection_callback(on_conn)
```

**Acceptance:** GUI started with no server → pill shows OFFLINE/red; when server connects (or simulate callback) pill animates to ONLINE/green.

---

### 5) Fix FilesView select_all & missing toast_manager

**Files to inspect/edit**

- `components/file_action_handlers.py`, `components/file_table_renderer.py`, `components/file_details.py`, and view code where `FilesView` is implemented (search `FilesView`).

**Fix steps**

- Replace direct calls to `self.table_renderer.select_all_rows()` with try-except fallback that logs and calls compatible API. But better: implement method in renderer.
  
- Ensure `FilesView.__init__` receives `toast_manager` and sets `self.toast_manager`.
  

**Acceptance:** pressing Select All no longer throws `FilesView`/`FileTableRenderer` attribute errors.

---

### 6) Navigation & route highlight sync (ui/navigation.py + main.py)

**Files to edit**

- `ui/navigation.py` (NavigationRail or side nav).
  
- `main.py` where route changes are performed.
  

**Fix**

- Create `navigate_to(route_name)` helper used everywhere. It must:
  
  1. call `page.go(route_name)` or update the main content container,
    
  2. set `navigation.selected_index = index_for(route_name)`,
    
  3. `page.update()`.
    
- Register `page.on_route_change` to call `navigation.set_selected_index_from_route()`.
  

**Acceptance:** switching tabs from any in-app control or side nav always updates the side nav highlight.

---

### 7) Settings layout bug (settings/)

**Files to edit**

- `settings/settings_form_generator.py`, `settings/settings_change_manager.py`, and the view in `ui` that shows settings.

**Fix**

- Use responsive containers: wrap settings content in `ft.Scrollable` and use `layouts/breakpoint_manager.py` utilities to choose single- or two-column layouts based on page width. Merge “top settings configuration” into bottom import/export block per your note.

**Acceptance:** settings visible and usable in windowed mode (not full-screen); controls reflow.

---

### 8) Hitbox / clickable offsets

**Files to inspect**

- UI files using `Stack` or absolute positioning: search for `Stack(`, `overlay`, or `positioned` usage. Suspects: `ui/layouts/responsive.py`, `components/control_panel_card.py`, `ui/widgets/*`.

**Fix**

- Replace overlapping `Stack` layers that block pointer events with `Row/Column` and proper `z-index`/`alignment`. Set `expand` and `padding` rather than negative margins. Temporarily enable `page.debug=True` to visually inspect layout bounds.

**Acceptance:** clickable area matches visual element.

---

### 9) Dashboard & analytics placeholders

**Files**

- `components/enhanced_components.py`, `ui/widgets/charts.py`, `services/monitoring.py`, `core/server_operations.py`.

**Fix**

- Replace dev mock values with:
  
  - If `is_server_running() is False`: show a consistent offline placeholder: “No data — server offline”.
    
  - When online: subscribe to `server_monitoring_manager` updates and animate metric changes with `motion_utils`.
    
- Ensure Start/Stop/Restart buttons are disabled when no server.
  

**Acceptance:** dashboard shows offline placeholders without misleading failure messages when server is absent.

---

### 10) Activity log detail popup & notifications

**Files**

- `services/log_service.py`, `ui/dialogs.py`, `ui/navigation.py` (top-right actions), `utils/server_data_manager.py`.

**Fix**

- Activity log rows truncated; add `on_click` if row clicked → open `ft.AlertDialog` or `BottomSheet` with full message, timestamp, severity, optional JSON payload and a copy button.
  
- Hook notifications icon to `server_bridge.get_notifications()` and open a right-side `Drawer` with the list.
  

**Acceptance:** clicking a log entry opens a popup with full content; notifications panel opens.

---

## Tests & verification (run these locally / include in commit)

1. **Unit tests to add**
  
  - `tests/test_server_bridge_api.py` — assert `get_clients`, `get_files`, `is_server_running`, `register_connection_callback` exist and behave with the `simple_server_bridge`.
    
  - `tests/test_base_table_manager.py` — instantiate `BaseTableManager` with a dummy `page` object (or Flet test harness) and call `update_table_data` / `select_all_rows`.
    
2. **Integration smoke**
  
  - Run `final_verification.py` after changes; it should run without raising AttributeError in UI flows referenced earlier (files view select all, start/stop server buttons, navigation switching).
3. **Manual checks**
  
  - Start GUI without server: confirm pill shows OFFLINE, dashboard shows placeholders, server control buttons disabled. Open Files/Clients — no exceptions. Click activity row — dialog shows.
    
  - Start the server (or simulate `bridge._set_connected(True)`): pill animates to ONLINE, dashboard populates (if server exists) or shows a retry spinner.
    
4. **Performance**
  
  - Load 1,000 fake file rows (create test fixture in `defensive.db` or using `server_data_manager` mock) and confirm table either paginates or remains responsive (limit default 300 rows per page).

---

## commit guidance & commit structure

- Keep changes small & focused:
  
  - PR 1: **Server bridge API** + tests (small)
    
  - PR 2: **BaseTableManager** + client/file renderers + tests
    
  - PR 3: **ToastManager** + injection + select_all fixes
    
  - PR 4: **Topbar status pill** + notifications/help
    
  - PR 5: **Theme & responsive settings fixes** + layout fixes
    
  - PR 6: **Dashboard & activity log improvements**
    
- Each commit must include:
  
  - Short changelog
    
  - How to run tests & final_verification
    
  - Short GIFs/screenshots (or instructions to run the final_verification smoke script)
    
  - Security note (see below) if crypto code appears
    

---

## Error triage rubric (how agent should proceed if blocked)

- If a view/renderer raises AttributeError: add a compatibility wrapper implementing the expected method that calls the newer API and log a TODO for cleanup.
  
- If a change impacts UX heavily, prefer toggled behavior behind a `settings` flag (e.g., enable new pagination by default but allow rollback).
  
- If the Flet version lacks an API (e.g., `AnimatedSwitcher`), fallback gracefully: simple show/hide with `page.update()` and note in PR.
  

---

## Final instructions for the agent (strict)

- Run existing tests first and report failures. Fix failing tests only if they’re directly related to the files modified; otherwise document failures.
  
- Make each PR atomic with tests passing. If any fix requires changing multiple modules, break into PRs as suggested.
  
- Add inline comments where you add temporary compatibility wrappers with `# TODO: remove when all callers migrated` and link the PR number(s) in the comment.
  

---