# Settings View Enhancement Plan

## Current State

The Settings view now displays correctly with 6 tabs using a manual tab implementation. The current implementation includes:
- Server, Interface, Monitoring, Logging, Security, and Backup tabs
- Text fields, dropdowns, and switches for configuration
- Basic field dependencies (TLS fields disable when SSL off)
- Live theme changes when Interface settings are modified
- Status bar showing connection mode

---

## Enhancement Categories

### Phase 1: Visual Polish (Low Risk)

These changes improve appearance without touching core functionality.

#### 1.1 Section Card Improvements
**Current:** Plain cards with left border accent
**Enhancement:** Add subtle elevation and hover state

```python
# Before
ft.Container(
    content=ft.Column([hdr, *rows], spacing=0),
    bgcolor=ft.Colors.SURFACE,
    border_radius=10,
    border=ft.border.only(left=ft.BorderSide(3, ft.Colors.PRIMARY), ...),
)

# After - add shadow and hover effect
ft.Container(
    content=ft.Column([hdr, *rows], spacing=0),
    bgcolor=ft.Colors.SURFACE,
    border_radius=10,
    shadow=ft.BoxShadow(
        spread_radius=1,
        blur_radius=4,
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        offset=ft.Offset(0, 2),
    ),
    border=ft.border.only(left=ft.BorderSide(3, ft.Colors.PRIMARY), ...),
    animate=ft.animation.Animation(150, "easeOut"),
)
```

#### 1.2 Tab Bar Styling
**Current:** Simple underline indicator
**Enhancement:** Add hover states and smoother transitions

```python
# Add ink_color and animate properties
ft.Container(
    content=ft.Row([icon, text], spacing=6),
    padding=ft.padding.symmetric(horizontal=16, vertical=10),
    border=ft.border.only(bottom=ft.BorderSide(2, color)),
    on_click=...,
    ink=True,
    ink_color=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),  # Subtle ripple
    animate=ft.animation.Animation(200, "easeInOut"),  # Smooth transitions
)
```

#### 1.3 Form Field Alignment
**Current:** Fixed widths causing uneven alignment
**Enhancement:** Use responsive widths with `expand` properly

```python
# Better row layout
ft.Row([
    ft.Container(
        content=ft.Text(label, size=13, weight=ft.FontWeight.W_500),
        width=160,  # Consistent label width
    ),
    ft.Container(
        content=control,
        expand=True,  # Take remaining space
    ),
], vertical_alignment=ft.CrossAxisAlignment.CENTER)
```

#### 1.4 Typography Hierarchy
**Current:** Basic text sizing
**Enhancement:** Use theme text styles for consistency

```python
# Section headers
ft.Text(title, size=14, weight=ft.FontWeight.W_600)

# Field labels
ft.Text(label, size=13, weight=ft.FontWeight.W_500)

# Descriptions/hints
ft.Text(hint, size=12, color=ft.Colors.GREY_600, italic=True)
```

---

### Phase 2: Functional Improvements (Medium Risk)

These changes add new features requiring careful testing.

#### 2.1 Persist Settings to Config File
**Current:** Settings reset on app restart
**Enhancement:** Save to `config.local.json` via unified config manager

```python
from Shared.config.unified_config import load_unified_config, save_config

def on_save(e):
    config = load_unified_config()

    # Update config from data dict
    config.server.port = data["server"]["port"]
    config.server.host = data["server"]["host"]
    # ... map all fields

    save_config(config, "config.local.json")
    update_status("Settings saved!")
```

#### 2.2 Load Settings on Startup
**Current:** Always shows DEFAULT_SETTINGS
**Enhancement:** Load from config file in `setup()` function

```python
async def setup():
    try:
        config = load_unified_config()

        # Populate data dict from config
        data["server"]["port"] = config.server.port
        data["server"]["host"] = config.server.host
        # ... map all fields

        refresh_controls()
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
```

#### 2.3 Input Validation
**Current:** No validation, invalid values accepted
**Enhancement:** Add real-time validation with visual feedback

```python
def text_field_validated(section, key, label, width=None, validator=None):
    field = ft.TextField(
        label=label,
        width=width,
        on_change=lambda e: validate_and_update(e, section, key, validator),
    )

    def validate_and_update(e, sec, key, validator):
        value = e.control.value

        if validator:
            is_valid, error_msg = validator(value)
            if not is_valid:
                e.control.error_text = error_msg
                e.control.border_color = ft.Colors.ERROR
            else:
                e.control.error_text = None
                e.control.border_color = None
            e.control.update()

        # Only update data if valid
        if not e.control.error_text:
            data[sec][key] = value

    return field

# Validators
def validate_port(value):
    try:
        port = int(value)
        if 1 <= port <= 65535:
            return True, None
        return False, "Port must be 1-65535"
    except:
        return False, "Must be a number"

def validate_path(value):
    if not value or len(value) < 2:
        return False, "Path required"
    return True, None
```

#### 2.4 File Picker for Path Fields
**Current:** Manual text entry for paths
**Enhancement:** Add browse button using FilePicker service

```python
def path_field(section, key, label, pick_type="folder"):
    field = ft.TextField(label=label, expand=True)

    file_picker = ft.FilePicker(
        on_result=lambda e: handle_pick_result(e, field, section, key)
    )
    page.overlay.append(file_picker)

    def browse_click(e):
        if pick_type == "folder":
            file_picker.get_directory_path()
        else:
            file_picker.pick_files()

    return ft.Row([
        field,
        ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            on_click=browse_click,
            tooltip="Browse...",
        ),
    ], expand=True)
```

---

### Phase 3: UX Improvements (Medium Risk)

These changes improve user experience.

#### 3.1 Unsaved Changes Indicator
**Current:** No indication of unsaved changes
**Enhancement:** Track dirty state and show indicator

```python
is_dirty = False
original_data = None

def setup():
    nonlocal original_data
    original_data = copy.deepcopy(data)

def on_field_change(e):
    nonlocal is_dirty
    is_dirty = data != original_data
    update_save_button_state()

def update_save_button_state():
    save_button.disabled = not is_dirty
    save_button.text = "Save*" if is_dirty else "Save"
    save_button.update()
```

#### 3.2 Confirm Discard on Navigation
**Current:** Can navigate away losing changes
**Enhancement:** Show confirmation dialog

```python
def can_navigate_away():
    if not is_dirty:
        return True

    # Show confirmation dialog
    def handle_response(result):
        if result == "discard":
            is_dirty = False
            navigate_away()
        elif result == "save":
            on_save(None)
            navigate_away()
        # "cancel" - do nothing

    show_confirm_dialog(
        "Unsaved Changes",
        "You have unsaved changes. What would you like to do?",
        ["Discard", "Save", "Cancel"],
        handle_response
    )
    return False
```

#### 3.3 Section-Level Reset
**Current:** Reset button resets all settings
**Enhancement:** Add reset button per section

```python
def section(title, icon, rows, section_key):
    def reset_section(e):
        # Reset just this section to defaults
        data[section_key] = copy.deepcopy(DEFAULT_SETTINGS[section_key])
        refresh_section_controls(section_key)
        update_status(f"{title} reset to defaults")

    header = ft.Row([
        ft.Icon(icon, size=18, color=ft.Colors.PRIMARY),
        ft.Text(title, size=14, weight=ft.FontWeight.W_600),
        ft.Container(expand=True),
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=16,
            tooltip=f"Reset {title}",
            on_click=reset_section,
        ),
    ])
    # ...
```

#### 3.4 Keyboard Navigation
**Current:** Mouse-only tab switching
**Enhancement:** Support arrow keys and hotkeys

```python
def handle_keyboard(e: ft.KeyboardEvent):
    if e.key == "Tab" and e.shift:
        # Shift+Tab = previous tab
        switch_tab((current_tab - 1) % len(tab_contents))
    elif e.key == "Tab":
        # Tab = next tab (when focus on tab bar)
        pass  # Default behavior
    elif e.ctrl and e.key == "s":
        # Ctrl+S = Save
        on_save(None)
    elif e.ctrl and e.key == "r":
        # Ctrl+R = Reset
        on_reset(None)

page.on_keyboard_event = handle_keyboard
```

---

### Phase 4: Integration Improvements (Higher Risk)

These changes require integration with other components.

#### 4.1 ServerBridge Integration
**Current:** Offline mode only
**Enhancement:** Read/write server settings when connected

```python
async def load_from_server():
    if not server_bridge:
        return

    try:
        result = await run_sync_in_executor(server_bridge.get_server_config)
        if result.get("success"):
            server_config = result["data"]
            # Update data dict from server response
            data["server"]["port"] = server_config.get("port", 1256)
            # ...
            refresh_controls()
    except Exception as e:
        logger.error(f"Failed to load from server: {e}")

async def save_to_server():
    if not server_bridge:
        return

    try:
        result = await run_sync_in_executor(
            lambda: server_bridge.update_server_config(data["server"])
        )
        if result.get("success"):
            update_status("Settings saved to server")
        else:
            update_status(f"Error: {result.get('error')}")
    except Exception as e:
        update_status(f"Save failed: {e}")
```

#### 4.2 Real-Time Theme Preview
**Current:** Theme changes apply to whole app immediately
**Enhancement:** Preview in settings view first, then apply on save

```python
# Create a preview container that uses local theme
preview_theme = ft.Theme(...)

def update_preview(color_scheme):
    preview_theme.color_scheme_seed = COLOR_SEEDS.get(color_scheme, "#3B82F6")
    preview_container.update()

def apply_theme_on_save():
    # Only apply to page.theme when saving
    page.theme = preview_theme
    page.update()
```

---

## Implementation Priority

| Priority | Enhancement               | Risk   | Effort | Value  |
|----------|---------------------------|--------|--------|--------|
| 1        | Section card shadows      | Low    | 1hr    | Medium |
| 2        | Form field alignment      | Low    | 1hr    | High   |
| 3        | Persist settings          | Medium | 2hr    | High   |
| 4        | Load settings on startup  | Medium | 1hr    | High   |
| 5        | Input validation          | Medium | 2hr    | High   |
| 6        | Unsaved changes indicator | Medium | 1hr    | Medium |
| 7        | File picker for paths     | Medium | 2hr    | Medium |
| 8        | Section-level reset       | Low    | 1hr    | Low    |
| 9        | Keyboard navigation       | Low    | 1hr    | Low    |
| 10       | Confirm discard dialog    | Medium | 1hr    | Medium |
| 11       | ServerBridge integration  | High   | 4hr    | High   |

---

## Testing Checklist

After each enhancement, verify:

- [ ] Settings view loads without errors
- [ ] All 6 tabs are visible and clickable
- [ ] Tab switching works correctly
- [ ] Form controls are interactive
- [ ] Theme changes apply correctly
- [ ] Field dependencies work (TLS, API key)
- [ ] Desktop mode works
- [ ] No console errors

---

## Risk Mitigation

### Before Making Changes
1. Create a backup of working `settings.py`
2. Test in isolation before integrating
3. Make one change at a time
4. Commit after each successful change

### If Something Breaks
1. Revert to the working backup
2. Identify what broke by comparing diffs
3. Re-apply changes incrementally

---

## Don't Do List

Avoid these patterns that caused the original issue:

| Don't                          | Do Instead                       |
|--------------------------------|----------------------------------|
| `ft.Colors.ON_SURFACE_VARIANT` | `ft.Colors.GREY_600`             |
| `ft.Colors.OUTLINE_VARIANT`    | `ft.Colors.OUTLINE`              |
| `ft.Colors.SURFACE_VARIANT`    | `ft.Colors.SURFACE`              |
| Complex observable patterns    | Simple state dict                |
| `ft.Tabs` control              | Manual tabs with containers      |
| Untested color constants       | Verify in `ft.Colors` enum first |

---

**Created**: 2025-12-28
**Target Flet Version**: 0.80.0
