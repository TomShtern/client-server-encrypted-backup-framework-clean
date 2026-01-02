## Goals (top-line)

Build a cross-platform, modern, dark-themed GUI for managing an encrypted backup server with: sidebar navigation, client & file management, analytics, database browser, system monitoring, drag-and-drop, system tray, settings, and logs.

---

## Required repos / files to implement

- `python_server/server_gui/ServerGUI.py` — main GUI app

- `python_server/server/gui_integration.py` — integration points with server

- `Shared/utils/process_monitor_gui.py` — process monitor widget 

- Server code interfaces: `python_server/server/server.py`, `python_server/server/server_singleton.py`

## Required 3rd-party packages

- `tkinter` (stdlib; GUI)

- `tkcalendar` (optional: date pickers)

- `tkinterdnd2` (drag & drop)

- `matplotlib` (charts)

- `psutil` (system monitoring)

- `pystray`, `pillow` (system tray icons)

- `sentry-sdk` (error tracking) 

---

## Phase 0 — Project setup (prerequisite)

1. Create project layout and enforce imports/fallbacks.
   
   - Add package structure and `__init__.py` where needed.
   
   - Confirm Python versions and virtualenv.

2. Add dependency list (`requirements.txt`) with the packages above.

---

## Phase 1 — Base UI & Theme

Tasks:

- Create main window with modern dark theme variables (colors, fonts) accessible as `ModernTheme`.

- Implement vertical sidebar navigation with icon placeholders.

- Implement header area with a global search bar.

- Implement a main content area that swaps views based on sidebar selection.  
  Files: `ServerGUI.py`  
  Acceptance criteria:

- App starts and shows sidebar + header + empty content area.

- Theme variables are centralized and used by at least 3 components.

Complexity: Low → Medium

---

## Phase 2 — Dashboard

Tasks:

- Dashboard view that shows server status cards: server running, active clients count, active transfers, CPU/memory snapshot.

- Live Transfers feed (list of in-progress transfers).

- Server control buttons: Start / Stop / Restart (call interface methods).  
  Acceptance criteria:

- Start/Stop buttons call `BackupServer.start()` / `stop()` when a server object is attached(server is always attached to the gui, they are COUPLED).

Complexity: Medium

---

## Phase 3 — Clients & Files management

Clients Tab:

- Tree / table view of clients.

- Right-click context menu (connect, disconnect, inspect).

- Dedicated detail pane that shows selected client metadata, connection info, and actions.

Files Tab:

- Tree / table view of stored files and folder hierarchy.

- Right-click context for download, delete, reveal.

- Drag & drop support to add files to server (use `tkinterdnd2` if available).

- Detail pane for selected file (size, encryption metadata, client owner, date).  
  Acceptance criteria:

- Selection updates detail pane.

- Context menu entries invoke expected callbacks (implemented as stubs if server absent).

- Drag & drop enqueues a file-add action (with confirmation dialog).

Complexity: Medium → High (drag-n-drop + large-tree handling)

---

## Phase 4 — Analytics & Charts

Tasks:

- Analytics tab with date range selectors (use `tkcalendar.DateEntry` if installed; fallback to manual inputs).

- Interactive charts for transfers over time, storage usage, per-client activity (use `matplotlib` embedded in Tkinter).

- Filters: date range + client filter + file type.  
  Acceptance criteria:

- Charts render with real dataset(NEVER use mock data).

- Date range affects data shown.

- Export CSV button for datasets.

Complexity: Medium

---

## Phase 5 — Database Browser & Logs

Database Tab:

- Connect to server DB via `db_manager` interface to list tables and preview rows.

- Basic SQL viewer (read-only) or table selector + paginated preview.

Logs Tab:

- Tail logs with auto-refresh and manual export.

- Search/filter log entries by level and text.  
  Acceptance criteria:

- DB tables list populated with sample table schema when server absent.

- Log tail works on a local file or a mocked stream.

Complexity: Medium

---

## Phase 6 — System Monitoring & Process Widget

Tasks:

- Sidebar system monitor (CPU, RAM percentages) using `psutil` 

- Optional ProcessMonitorWidget integrated into a dedicated panel if `Shared.utils.process_monitor_gui` is implemented.  
  Acceptance criteria:

- Monitor updates every N seconds with live or simulated data.

- If `ProcessMonitorWidget` is missing, a graceful placeholder shows.

Complexity: Low → Medium

---

## Phase 7 — Settings, Tray, and Polishing

Settings:

- Settings tab: server connection parameters, logging levels, Sentry DSN toggle, paths.  
  System Tray:

- Implement system tray behavior using `pystray` + `PIL` for icons(must be utf8); support minimize to tray / restore.  
  Polish:

- Unicode/text icon mapping (utf8).

- Keyboard shortcuts, accessibility labels, responsiveness adjustments (layout resizes).  
  Acceptance criteria:

- Settings persist to config file.

- App can minimize to tray and restore.

- Theme consistent across widgets.

Complexity: Medium → High (tray cross-OS quirks, get it to work on windows first)

---

## Phase 8 — Testing, QA & Deployment

Testing:

- Unit tests for core view controllers and server interface.

- Integration tests for start/stop flows  
  QA:

- Cross-platform smoke tests on Windows(focus on windows) + Linux (macOS optional).  
  Packaging:

- Core flows (start/stop, view clients, download file) validated

Complexity: Medium

---

## Implementation details & rules for implementers

- Always code agaainst the real server, as they are coupled.

- Keep UI logic (Tk widget wiring) separate from business logic (calls to server). Follow MVC-ish separation.

- Use runtime checks for optional libs (`tkcalendar`, `tkinterdnd2`, `matplotlib`, `psutil`, `pystray`) and show clear instructions to the user to install missing packages.

- File locations for main work: `python_server/server_gui/ServerGUI.py` and `python_server/server/gui_integration.py`.

- NEVER write stubs. NEVER use mock data.

---

## Deliverables (for handoff)

1. `ServerGUI.py` — functional GUI implementing all tabs with clean interfaces to server.

2. `gui_integration.py` — concise adapter glue between GUI and server.

3. `requirements.txt` and `README.md` with run/build instructions.

4. Unit and integration tests for core flows.

5. 
