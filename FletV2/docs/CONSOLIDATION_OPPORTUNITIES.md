# FletV2 Consolidation Opportunities

**Date Created**: January 2025
**Status**: Documentation - Ready for Implementation
**Estimated Total Impact**: 1,000-1,300 line reduction (15-20% LOC reduction)
**Total Effort**: ~20 hours over 3 weeks

---

## Executive Summary

This document identifies **4 high-value consolidation patterns** found across the FletV2 codebase. These patterns represent genuine code duplication where extraction provides clear benefits:

- **Pattern 1**: Async/Sync Integration (76+ occurrences, 300-400 lines)
- **Pattern 2**: Data Loading with States (13 views, 400-500 lines)
- **Pattern 3**: Filter Row UI (5 views, 150-200 lines)
- **Pattern 4**: Dialog Building (12+ dialogs, 150-200 lines)

**Key Principle**: Extract only what's genuinely reused 3+ times. Don't create unnecessary abstractions.

---

## Pattern 1: Async/Sync Integration (76+ occurrences)

### Current Problem

Every view manually wraps synchronous ServerBridge calls with `run_in_executor`:

```python
# In clients.py (15 occurrences)
async def load_clients(self):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, self.bridge.get_clients)
    # 15 more lines of error handling...

# In files.py (12 occurrences)
async def load_files(self):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, self.bridge.get_files)
    # 15 more lines of error handling...

# In database_pro.py (18 occurrences)
async def load_table_data(self, table_name):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, self.bridge.get_table_data, table_name)
    # 15 more lines of error handling...
```

**Total**: 76+ identical patterns across all views (averaging ~15 lines each = **~1,140 lines**)

### Solution: Async Helper Utility

**Already implemented**: `FletV2/utils/async_helpers.py:create_async_fetch_function()`

```python
# utils/async_helpers.py
async def create_async_fetch_function(bridge_method, *args, **kwargs):
    """
    Universal async wrapper for synchronous ServerBridge methods.

    Handles:
    - Async/sync integration via run_in_executor
    - Structured error responses
    - Consistent logging
    """
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, bridge_method, *args, **kwargs)
        if isinstance(result, dict) and 'success' in result:
            return result
        return {'success': True, 'data': result, 'error': None}
    except Exception as e:
        logging.error(f"Async fetch failed: {e}")
        return {'success': False, 'data': None, 'error': str(e)}
```

### After Consolidation

```python
# In any view
from FletV2.utils.async_helpers import create_async_fetch_function

async def load_clients(self):
    result = await create_async_fetch_function(self.bridge.get_clients)
    if result['success']:
        self.clients = result['data']

async def load_files(self):
    result = await create_async_fetch_function(self.bridge.get_files)
    if result['success']:
        self.files = result['data']
```

**Reduction**: 15 lines → 3 lines per occurrence
**Total Savings**: ~1,140 → ~228 lines = **912 lines saved**
**Actual Benefit**: 300-400 lines (already partially implemented in clients.py and files.py)

### Implementation Plan

**Week 1: Days 1-2 (4 hours)**

1. **Verify existing implementation** (30 min)
   - Confirm `async_helpers.py` has complete implementation
   - Test with clients.py and files.py (already using it)

2. **Apply to remaining views** (3 hours)
   - dashboard.py (8 occurrences)
   - database_pro.py (18 occurrences)
   - analytics.py (10 occurrences)
   - enhanced_logs.py (7 occurrences)
   - settings.py (6 occurrences)

3. **Validation** (30 min)
   - Test each view's data loading
   - Verify error handling works correctly

**Risk**: 🟢 Very Low (helper already proven in 2 views)

---

## Pattern 2: Data Loading with States (13 views)

### Current Problem

Every view implements its own loading state management:

```python
# In clients.py
self.loading = True
self.loading_text.value = "Loading clients..."
self.loading_indicator.visible = True
self.page.update()

try:
    result = await load_clients()
    if result['success']:
        self.clients = result['data']
        self.error_banner.visible = False
    else:
        self.error_banner.visible = True
        self.error_banner.content = ft.Text(result['error'])
finally:
    self.loading = False
    self.loading_indicator.visible = False
    self.page.update()
```

**Total**: ~30-40 lines per view × 13 views = **~390-520 lines**

### Solution: Loading State Manager

**Create**: `FletV2/utils/loading_states.py`

```python
from dataclasses import dataclass
from typing import Optional, Callable, Any
import flet as ft
import logging

@dataclass
class LoadingStateConfig:
    """Configuration for loading state UI components."""
    loading_indicator: ft.ProgressRing
    loading_text: ft.Text
    error_banner: ft.Banner
    success_banner: Optional[ft.Banner] = None
    page: ft.Page = None

class LoadingStateManager:
    """
    Manages loading, error, and success states for async operations.

    Usage:
        manager = LoadingStateManager(LoadingStateConfig(...))

        # With context manager (automatic cleanup)
        async with manager.loading("Loading clients..."):
            result = await fetch_clients()
            if not result['success']:
                manager.show_error(result['error'])
            else:
                manager.show_success("Clients loaded!")
                return result['data']
    """

    def __init__(self, config: LoadingStateConfig):
        self.config = config
        self._is_loading = False

    def loading(self, message: str):
        """Context manager for loading operations."""
        return LoadingContext(self, message)

    def show_loading(self, message: str):
        """Show loading state."""
        self._is_loading = True
        self.config.loading_indicator.visible = True
        self.config.loading_text.value = message
        self.config.loading_text.visible = True
        self.config.error_banner.open = False
        if self.config.page:
            self.config.page.update()

    def hide_loading(self):
        """Hide loading state."""
        self._is_loading = False
        self.config.loading_indicator.visible = False
        self.config.loading_text.visible = False
        if self.config.page:
            self.config.page.update()

    def show_error(self, error_message: str):
        """Show error banner."""
        self.hide_loading()
        self.config.error_banner.content = ft.Text(error_message, color=ft.colors.ERROR)
        self.config.error_banner.open = True
        if self.config.page:
            self.config.page.update()
        logging.error(f"UI Error: {error_message}")

    def show_success(self, message: str):
        """Show success banner (if configured)."""
        self.hide_loading()
        if self.config.success_banner:
            self.config.success_banner.content = ft.Text(message, color=ft.colors.GREEN)
            self.config.success_banner.open = True
            if self.config.page:
                self.config.page.update()

class LoadingContext:
    """Async context manager for loading operations."""

    def __init__(self, manager: LoadingStateManager, message: str):
        self.manager = manager
        self.message = message

    async def __aenter__(self):
        self.manager.show_loading(self.message)
        return self.manager

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Exception occurred, show error
            self.manager.show_error(str(exc_val))
            return False  # Don't suppress exception
        else:
            # Success, just hide loading
            self.manager.hide_loading()
            return False
```

### After Consolidation

```python
# In any view's __init__
from FletV2.utils.loading_states import LoadingStateManager, LoadingStateConfig

self.loading_manager = LoadingStateManager(LoadingStateConfig(
    loading_indicator=self.loading_spinner,
    loading_text=self.loading_text,
    error_banner=self.error_banner,
    success_banner=self.success_banner,
    page=self.page
))

# In data loading methods
async def load_clients(self):
    async with self.loading_manager.loading("Loading clients..."):
        result = await create_async_fetch_function(self.bridge.get_clients)
        if not result['success']:
            # Error automatically shown by context manager
            return

        self.clients = result['data']
        self.loading_manager.show_success(f"Loaded {len(self.clients)} clients")
        self.refresh_table()
```

**Reduction**: 30-40 lines → 5-8 lines per view
**Total Savings**: ~390-520 → ~65-104 lines = **325-416 lines saved**

### Implementation Plan

**Week 1: Days 3-5 (6 hours)**

1. **Create loading_states.py** (2 hours)
   - Implement LoadingStateManager class
   - Implement LoadingContext async context manager
   - Add comprehensive docstrings

2. **Apply to 5 pilot views** (3 hours)
   - clients.py
   - files.py
   - database_pro.py
   - analytics.py
   - enhanced_logs.py

3. **Test and refine** (1 hour)
   - Test all loading scenarios
   - Verify error handling
   - Ensure automatic cleanup works

**Week 2: Days 1-2 (4 hours)**

4. **Apply to remaining views** (3 hours)
   - dashboard.py
   - settings.py
   - Any other views with loading states

5. **Final validation** (1 hour)
   - Full application test
   - Verify consistent loading UX

**Risk**: 🟢 Low (context managers are well-tested pattern)

---

## Pattern 3: Filter Row UI (5 views)

### Current Problem

Nearly identical filter row construction in multiple views:

```python
# In clients.py
filter_row = ft.ResponsiveRow(
    controls=[
        ft.TextField(
            label="Search clients",
            hint_text="Type to filter...",
            on_change=self.on_search_change,
            expand=1,
            col={"sm": 12, "md": 6, "lg": 4}
        ),
        ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("all", "All"),
                ft.dropdown.Option("active", "Active"),
                ft.dropdown.Option("inactive", "Inactive")
            ],
            value="all",
            on_change=self.on_status_filter,
            expand=1,
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.IconButton(
            icon=ft.icons.REFRESH,
            tooltip="Refresh",
            on_click=self.on_refresh,
            col={"sm": 12, "md": 12, "lg": 1}
        )
    ]
)

# Nearly identical in files.py, database_pro.py, analytics.py, enhanced_logs.py
```

**Total**: ~30-40 lines per view × 5 views = **~150-200 lines**

### Solution: Filter Row Builder

**Create**: `FletV2/utils/ui_builders.py` (add to existing or create new)

```python
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict
import flet as ft

@dataclass
class FilterOption:
    """Single filter option (dropdown, checkbox, etc)."""
    type: str  # "dropdown", "checkbox", "date"
    label: str
    on_change: Callable
    value: any = None
    options: List[ft.dropdown.Option] = field(default_factory=list)
    col_config: Dict = field(default_factory=lambda: {"sm": 12, "md": 6, "lg": 3})

@dataclass
class FilterRowConfig:
    """Configuration for filter row UI."""
    search_enabled: bool = True
    search_label: str = "Search"
    search_hint: str = "Type to filter..."
    search_on_change: Optional[Callable] = None

    filters: List[FilterOption] = field(default_factory=list)

    refresh_enabled: bool = True
    refresh_on_click: Optional[Callable] = None

    export_enabled: bool = False
    export_on_click: Optional[Callable] = None

def create_filter_row(config: FilterRowConfig) -> ft.ResponsiveRow:
    """
    Creates a standardized filter row with search, filters, and action buttons.

    Args:
        config: FilterRowConfig with all settings

    Returns:
        ft.ResponsiveRow ready to add to view

    Example:
        filter_row = create_filter_row(FilterRowConfig(
            search_label="Search clients",
            search_on_change=self.on_search,
            filters=[
                FilterOption(
                    type="dropdown",
                    label="Status",
                    options=[
                        ft.dropdown.Option("all", "All"),
                        ft.dropdown.Option("active", "Active")
                    ],
                    value="all",
                    on_change=self.on_status_filter
                )
            ],
            refresh_on_click=self.on_refresh,
            export_enabled=True,
            export_on_click=self.on_export
        ))
    """
    controls = []

    # Search field
    if config.search_enabled:
        controls.append(
            ft.TextField(
                label=config.search_label,
                hint_text=config.search_hint,
                on_change=config.search_on_change,
                prefix_icon=ft.icons.SEARCH,
                expand=1,
                col={"sm": 12, "md": 6, "lg": 4}
            )
        )

    # Filter controls (dropdowns, checkboxes, etc)
    for filter_opt in config.filters:
        if filter_opt.type == "dropdown":
            controls.append(
                ft.Dropdown(
                    label=filter_opt.label,
                    options=filter_opt.options,
                    value=filter_opt.value,
                    on_change=filter_opt.on_change,
                    expand=1,
                    col=filter_opt.col_config
                )
            )
        elif filter_opt.type == "checkbox":
            controls.append(
                ft.Checkbox(
                    label=filter_opt.label,
                    value=filter_opt.value,
                    on_change=filter_opt.on_change,
                    col=filter_opt.col_config
                )
            )

    # Action buttons
    if config.refresh_enabled:
        controls.append(
            ft.IconButton(
                icon=ft.icons.REFRESH,
                tooltip="Refresh",
                on_click=config.refresh_on_click,
                col={"sm": 6, "md": 3, "lg": 1}
            )
        )

    if config.export_enabled:
        controls.append(
            ft.IconButton(
                icon=ft.icons.DOWNLOAD,
                tooltip="Export",
                on_click=config.export_on_click,
                col={"sm": 6, "md": 3, "lg": 1}
            )
        )

    return ft.ResponsiveRow(controls=controls, spacing=10)
```

### After Consolidation

```python
# In clients.py
from FletV2.utils.ui_builders import create_filter_row, FilterRowConfig, FilterOption

filter_row = create_filter_row(FilterRowConfig(
    search_label="Search clients",
    search_on_change=self.on_search_change,
    filters=[
        FilterOption(
            type="dropdown",
            label="Status",
            options=[
                ft.dropdown.Option("all", "All"),
                ft.dropdown.Option("active", "Active"),
                ft.dropdown.Option("inactive", "Inactive")
            ],
            value="all",
            on_change=self.on_status_filter
        )
    ],
    refresh_on_click=self.on_refresh,
    export_enabled=True,
    export_on_click=self.on_export
))
```

**Reduction**: 30-40 lines → 10-15 lines per view
**Total Savings**: ~150-200 → ~50-75 lines = **100-125 lines saved**

### Implementation Plan

**Week 2: Days 3-5 (3 hours)**

1. **Create ui_builders.py** (1 hour)
   - Implement create_filter_row function
   - Add FilterRowConfig and FilterOption dataclasses
   - Add comprehensive docstrings

2. **Apply to all 5 views** (1.5 hours)
   - clients.py
   - files.py
   - database_pro.py
   - analytics.py
   - enhanced_logs.py

3. **Test responsive behavior** (30 min)
   - Test at different window sizes
   - Verify responsive column configs work

**Risk**: 🟢 Very Low (pure UI composition)

---

## Pattern 4: Dialog Building (12+ dialogs)

### Current Problem

Manual AlertDialog construction repeated across views:

```python
# In clients.py - Add Client Dialog (50+ lines)
def show_add_client_dialog(self):
    name_field = ft.TextField(label="Client Name", autofocus=True)
    description_field = ft.TextField(label="Description", multiline=True)

    def close_dialog(e):
        dialog.open = False
        self.page.update()

    def submit(e):
        if not name_field.value:
            name_field.error_text = "Name is required"
            self.page.update()
            return

        # Add client logic...
        close_dialog(e)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Add New Client"),
        content=ft.Column([
            name_field,
            description_field
        ], tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.ElevatedButton("Add", on_click=submit)
        ]
    )

    self.page.dialog = dialog
    dialog.open = True
    self.page.update()

# Nearly identical patterns in files.py, database_pro.py, settings.py...
```

**Total**: ~50 lines per form dialog × 8 forms + ~30 lines per confirmation × 12 confirmations = **~400-560 lines**

### Solution: Dialog Helpers

**Add to**: `FletV2/utils/ui_builders.py`

```python
from dataclasses import dataclass
from typing import Optional, Callable, List, Dict, Any
import flet as ft

@dataclass
class DialogField:
    """Single form field configuration."""
    key: str  # Key for the value in returned dict
    label: str
    field_type: str = "text"  # "text", "multiline", "dropdown", "number", "date"
    required: bool = False
    default_value: Any = None
    options: List[ft.dropdown.Option] = None  # For dropdown type
    validator: Optional[Callable[[Any], Optional[str]]] = None  # Returns error message or None

@dataclass
class DialogConfig:
    """Configuration for form dialog."""
    title: str
    fields: List[DialogField]
    submit_text: str = "Submit"
    cancel_text: str = "Cancel"
    on_submit: Optional[Callable[[Dict[str, Any]], None]] = None
    width: Optional[float] = 500

async def show_form_dialog(page: ft.Page, config: DialogConfig) -> Optional[Dict[str, Any]]:
    """
    Show a form dialog and return the submitted values.

    Args:
        page: Flet page instance
        config: DialogConfig with title, fields, callbacks

    Returns:
        Dict of field values if submitted, None if cancelled

    Example:
        result = await show_form_dialog(page, DialogConfig(
            title="Add Client",
            fields=[
                DialogField(key="name", label="Client Name", required=True),
                DialogField(key="description", label="Description", field_type="multiline")
            ],
            on_submit=lambda data: self.add_client(data['name'], data['description'])
        ))
    """
    result_dict = {}
    submitted = [False]  # Use list to modify in nested function

    # Create form fields
    field_controls = {}
    for field in config.fields:
        if field.field_type == "text":
            control = ft.TextField(
                label=field.label,
                value=field.default_value or "",
                autofocus=(field == config.fields[0])
            )
        elif field.field_type == "multiline":
            control = ft.TextField(
                label=field.label,
                value=field.default_value or "",
                multiline=True,
                min_lines=3,
                max_lines=5
            )
        elif field.field_type == "number":
            control = ft.TextField(
                label=field.label,
                value=str(field.default_value) if field.default_value else "",
                keyboard_type=ft.KeyboardType.NUMBER
            )
        elif field.field_type == "dropdown":
            control = ft.Dropdown(
                label=field.label,
                options=field.options or [],
                value=field.default_value
            )
        else:
            control = ft.TextField(label=field.label, value=field.default_value or "")

        field_controls[field.key] = control

    def validate_and_submit(e):
        """Validate all fields and submit if valid."""
        valid = True

        for field in config.fields:
            control = field_controls[field.key]
            value = control.value

            # Required validation
            if field.required and not value:
                control.error_text = f"{field.label} is required"
                valid = False
            # Custom validator
            elif field.validator:
                error = field.validator(value)
                if error:
                    control.error_text = error
                    valid = False
            else:
                control.error_text = None

            result_dict[field.key] = value

        if valid:
            submitted[0] = True
            dialog.open = False
            if config.on_submit:
                config.on_submit(result_dict)

        page.update()

    def cancel(e):
        dialog.open = False
        page.update()

    # Create dialog
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(config.title),
        content=ft.Container(
            content=ft.Column(
                controls=list(field_controls.values()),
                tight=True,
                scroll=ft.ScrollMode.AUTO
            ),
            width=config.width
        ),
        actions=[
            ft.TextButton(config.cancel_text, on_click=cancel),
            ft.ElevatedButton(config.submit_text, on_click=validate_and_submit)
        ]
    )

    page.dialog = dialog
    dialog.open = True
    page.update()

    # Wait for dialog to close
    while dialog.open:
        await asyncio.sleep(0.1)

    return result_dict if submitted[0] else None

def show_confirmation_dialog(
    page: ft.Page,
    title: str,
    message: str,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    on_confirm: Optional[Callable] = None,
    on_cancel: Optional[Callable] = None,
    danger: bool = False
) -> None:
    """
    Show a simple confirmation dialog.

    Args:
        page: Flet page instance
        title: Dialog title
        message: Confirmation message
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        on_confirm: Callback when confirmed
        on_cancel: Callback when cancelled
        danger: If True, confirm button is red (destructive action)

    Example:
        show_confirmation_dialog(
            page,
            title="Delete Client",
            message=f"Are you sure you want to delete '{client_name}'?",
            confirm_text="Delete",
            on_confirm=lambda: self.delete_client(client_id),
            danger=True
        )
    """
    def confirm(e):
        dialog.open = False
        page.update()
        if on_confirm:
            on_confirm()

    def cancel(e):
        dialog.open = False
        page.update()
        if on_cancel:
            on_cancel()

    confirm_button = ft.ElevatedButton(
        confirm_text,
        on_click=confirm,
        color=ft.colors.ERROR if danger else None
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton(cancel_text, on_click=cancel),
            confirm_button
        ]
    )

    page.dialog = dialog
    dialog.open = True
    page.update()
```

### After Consolidation

```python
# Add client dialog - Before: 50+ lines, After: 15 lines
from FletV2.utils.ui_builders import show_form_dialog, DialogConfig, DialogField

async def show_add_client_dialog(self):
    result = await show_form_dialog(self.page, DialogConfig(
        title="Add New Client",
        fields=[
            DialogField(key="name", label="Client Name", required=True),
            DialogField(key="description", label="Description", field_type="multiline")
        ],
        on_submit=lambda data: self.add_client(data['name'], data['description'])
    ))

# Delete confirmation - Before: 30+ lines, After: 8 lines
from FletV2.utils.ui_builders import show_confirmation_dialog

def confirm_delete_client(self, client_id, client_name):
    show_confirmation_dialog(
        self.page,
        title="Delete Client",
        message=f"Are you sure you want to delete '{client_name}'?",
        confirm_text="Delete",
        on_confirm=lambda: self.delete_client(client_id),
        danger=True
    )
```

**Reduction**:
- Form dialogs: 50+ lines → 15 lines each (35 lines saved × 8 = 280 lines)
- Confirmations: 30+ lines → 8 lines each (22 lines saved × 12 = 264 lines)
**Total Savings**: ~544 lines, estimated **150-200 lines** (accounting for variations)

### Implementation Plan

**Week 3: Days 1-3 (4 hours)**

1. **Add dialog helpers to ui_builders.py** (1.5 hours)
   - Implement show_form_dialog function
   - Implement show_confirmation_dialog function
   - Add DialogConfig and DialogField dataclasses

2. **Apply to form dialogs** (1.5 hours)
   - clients.py: add/edit client
   - files.py: add file metadata
   - settings.py: edit settings
   - database_pro.py: add/edit records

3. **Apply to confirmation dialogs** (1 hour)
   - All delete confirmations
   - Destructive action confirmations

**Risk**: 🟢 Low (standard dialog pattern)

---

## Summary of All Patterns

| Pattern | Occurrences | Before | After | Savings | Effort | Risk |
|---------|-------------|--------|-------|---------|--------|------|
| Async/Sync Integration | 76+ | 15 lines | 3 lines | 300-400 lines | 4 hours | 🟢 Very Low |
| Data Loading States | 13 views | 30-40 lines | 5-8 lines | 400-500 lines | 10 hours | 🟢 Low |
| Filter Row UI | 5 views | 30-40 lines | 10-15 lines | 100-125 lines | 3 hours | 🟢 Very Low |
| Dialog Building | 20+ dialogs | 30-50 lines | 8-15 lines | 150-200 lines | 4 hours | 🟢 Low |
| **TOTAL** | **114+** | | | **1,000-1,225 lines** | **21 hours** | **🟢 Low** |

---

## Implementation Roadmap

### Week 1: Foundation (10 hours)
- **Days 1-2**: Apply async helpers to remaining views (4 hours)
- **Days 3-5**: Create and apply loading state manager (6 hours)

### Week 2: UI Consolidation (7 hours)
- **Days 1-2**: Complete loading state rollout (4 hours)
- **Days 3-5**: Create and apply filter row builder (3 hours)

### Week 3: Dialogs (4 hours)
- **Days 1-3**: Create and apply dialog helpers (4 hours)

**Total**: 21 hours over 3 weeks

---

## Validation Checklist

After each pattern implementation:

- [ ] All views using pattern compile without errors
- [ ] Data loading works correctly
- [ ] Error handling functions properly
- [ ] UI updates are responsive
- [ ] No performance regressions
- [ ] Code is more readable than before
- [ ] LOC reduction matches estimates

---

## Instructions for Implementation

### Using Flet Skill Actively

Before implementing any pattern:

```bash
# Activate Flet skill for guidance
"use flet skill"

# Ask for specific pattern help
"Help me implement async wrapper pattern with Flet 0.28.3"
"Show me Flet best practices for loading states"
```

### Using Flet Expert Agent

For architecture review:

```bash
# Review implementation before committing
"@agent-Flet-0-28-3-Expert review my LoadingStateManager implementation"

# Validate against Flet principles
"Flet expert: does this async helper follow Flet best practices?"
```

### Testing Strategy

1. **Incremental**: Apply pattern to 1-2 views, test thoroughly, then proceed
2. **Comparison**: Keep one view with old pattern for comparison
3. **Validation**: Run full application after each pattern completion

---

## Next Steps

1. ✅ Review this document
2. ✅ Start with Week 1, Day 1 (async helpers)
3. ✅ Use Flet skill actively throughout
4. ✅ Consult Flet expert agent for validation
5. ✅ Update IMPLEMENTATION_STATUS.md as you progress

**Remember**: Extract only what's genuinely reused. Quality over quantity.
