# Flet Desktop Guide — Framework-first patterns (Flet 0.28.3)

Purpose
- A concise guide for AI agents and contributors to build desktop/laptop apps using Flet the right way. Keep interfaces idiomatic, minimal, and maintainable.

Principles (the Flet way)
- Use Flet controls and layout primitives; avoid manual layout math.
- Compose small reusable Pagelets or control subclasses instead of giant views.
- Always run long-running tasks off the UI thread (page.run_task / threads).
- Prefer built-in navigation (Views, NavigationRail, Tabs) for desktop UX.
- Use theme tokens and centralized ThemeManager for consistent styling.
- Use ListView/DataTable for large datasets and virtualized patterns.

Key components and usage
- Page / AppBar: top-level.
- NavigationRail / Tabs + Views: primary navigation.
- Column / Row / Container / Pagelet: layout composition.
- ListView / DataTable: lists and tables (use controller/cache).
- Dialogs / SnackBar / BottomSheet: overlays via page methods.

State & event idioms
- Update control properties in event handlers; call control.update() for local updates.
- Keep per-component state inside the component, not global singletons.
- Use page.on_route_change and Views for route-based navigation.

Background tasks & I/O
- Use page.run_task(async_fn) for coroutines.
- For blocking I/O, use threads and notify the page when done.
- Provide cancellation tokens and show progress indicators.

Performance & large data
- Use ListView with controllers and append items in chunks.
- Avoid creating thousands of heavy controls at once.

Testing
- Use flet.testing.tester.Tester for unit/component tests.
- Simulate clicks, keystrokes, and route changes for integration tests.

Accessibility
- Use SemanticsService to set roles/labels for non-trivial controls.

Anti-patterns to avoid
- Manual pixel math for layout.
- Blocking UI thread.
- Hardcoded theme colors instead of tokens.
- Overly complex custom controls when composition suffices.

Small idiomatic examples
- App skeleton, Pagelet, background task, and ListView examples (see `.ai_snippets` in repo for copy-paste-ready snippets).

Where to add new UI code in this repo
- `flet_server_gui/views/` — add focused views (dashboard, logs, clients)
- `flet_server_gui/components/` — small Pagelets and reusable components
- `flet_server_gui/managers/` — non-UI logic (view_manager, theme_manager, navigation_manager)

Quick checklist for generated code
- Keep each component < 300 LOC.
- No blocking calls in event handlers.
- Use theme TOKENS for colors.
- Use `page.run_task()` for async work.

Last updated: 2025-09-03

## Verbatim Context7 excerpts (high-value, copy-paste)

Add these exact excerpts when you need precise, framework-approved patterns.

1) ListView performance / API (use `item_extent` / `first_item_prototype` or fixed sizes when possible):

```
flet.ListView:
	__init__(*
		controls: List[Control] = None,
		*, 
		spacing: Optional[float] = None,
		padding: Optional[Union[float, Padding]] = None,
		auto_scroll: bool = False,
		extend_body: bool = False,
		horizontal: bool = False,
		width: Optional[Union[int, float]] = None,
		height: Optional[Union[int, float]] = None,
		...
		cache_extent: Optional[float] = None,
		add_semantic_indexes: bool = False,
		semantic_child_count: Optional[int] = None,
		restoration_id: Optional[str] = None
)

Methods:
	scroll_to_item(index: int, alignment: float = 0.0, duration: int = 0, curve: Curve = Curve.LINEAR)
```

2) Page overlay management (use page methods instead of custom modal systems):

```
page.open_banner()
page.close_banner()
page.open_dialog()
page.close_dialog()
page.open_bottom_sheet()
page.close_bottom_sheet()
```

3) Pagelet signature (use Pagelet for small reusable sections):

```
flet.Pagelet:
	__init__(self, content: ft.Control, *, width: Optional[float] = None, height: Optional[float] = None, padding: Optional[Union[int, float, ft.Padding]] = None, margin: Optional[Union[int, float, ft.Margin]] = None, bgcolor: Optional[str] = None, border_radius: Optional[Union[int, float, ft.BorderRadius]] = None, alignment: Optional[ft.Alignment] = None, data=None, on_click=None, key: Optional[str] = None, expand: Optional[Union[bool, int]] = None, opacity: Optional[float] = None, offset: Optional[ft.Offset] = None, scale: Optional[ft.Scale] = None, rotate: Optional[ft.Rotate] = None, skew: Optional[ft.Skew] = None, tilt: Optional[ft.Tilt] = None, shadow: Optional[ft.BoxShadow] = None, blur: Optional[ft.Blur] = None, translate: Optional[ft.Translate] = None, on_hover: Optional[Callable] = None, visible: bool = True, disabled: bool = False, data_transfer_size: int = 0)
```

4) SemanticsService skeleton (accessibility):

```
class SemanticsService:
		def __init__(self, page):
				self.page = page

		def set_semantics(self, control, label=None, hint=None, tooltip=None, onChanged=None, onDismiss=None, onAction=None, onScrollDown=None, onScrollUp=None, onScrollLeft=None, onScrollRight=None, currentValue=None, minValue=None, maxValue=None, platform=None, excludeSemantics=None, customSemantics=None):
				pass

		def clear_semantics(self, control):
				pass
```

5) Tester API highlights (use Tester for UI tests):

```
flet.testing.tester.Tester
	__init__(target: Callable[[Page], None], **kwargs)
	get_control(control_id: str, parent: Control | None = None) -> Control
	tap(control: Control)
	send_key_event(control: Control, key: str, **kwargs)
	route_change(route: str)
	wait_for_animation(duration: float = 0.1)
	get_page() -> Page
	run_test(test_func: Callable[[], None])
```

Notes
- These excerpts are verbatim Context7 material and safe to paste into docs or generated code as guidance. Keep them intact to avoid deviating from framework expectations.

