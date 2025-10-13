# Flet 0.28.3 Compliance Findings – Scroll/Async Pass

## ScrollMode Enum Violations (Ref: §2.3)
- `FletV2/main.py:1002` uses `scroll="always"`; switch to `ft.ScrollMode.ALWAYS`.
- `FletV2/views/clients.py:295, 433, 494` pass string literals to `scroll`; replace with `ft.ScrollMode.AUTO`.
- `FletV2/views/files.py:373` sets `scroll="auto"`; should use `ft.ScrollMode.AUTO`.
- `FletV2/views/database_pro.py:1242, 1317` apply `scroll="auto"`; convert to enum values.
- `FletV2/views/experimental.py:140` assigns `scroll="auto"`; use `ft.ScrollMode.AUTO`.
- `FletV2/views/dashboard_stub.py:62` still uses `scroll="auto"`; update to enum.
- `FletV2/utils/dialog_builder.py:171` configures dialog column with `scroll="auto"`; switch to enum.
- `FletV2/sophisticated_dashboard_demo.py:390` keeps `scroll="auto"`; change to enum for compatibility.
- `FletV2/tests/test_rebuild_approach.py:102, 115`, `FletV2/tests/test_production_fix.py:93`, and `FletV2/theme_usage_examples.py:269` rely on string `scroll` values; update test/examples to enums to stay aligned with runtime expectations.

## TextStyle Background Color Misuse (Ref: §3.1)
- `FletV2/components/log_card.py:332` calls `ft.TextStyle(background_color=...)`; `TextStyle` does not support `background_color`. Replace with a surrounding container using `bgcolor` or similar approach.

## Blocking time.sleep Calls (Ref: Quick Reference & §7)
- `FletV2/fletv2_gui_manager.py:290` blocks the UI via `time.sleep(2)` inside Flet flow.
- `FletV2/server_with_fletv2_gui.py:166, 179` use `time.sleep(...)` while updating Flet UI.
- `FletV2/quick_performance_validation.py:33, 43` simulate latency with `time.sleep`; prefer `asyncio.sleep` or run in executor.
- `FletV2/tests/test_async_patterns.py:28, 45, 191` rely on `time.sleep` in async scenarios; update to async-friendly patterns per guide.
- `FletV2/tests/performance_benchmark.py:146` sleeps synchronously; swap for `asyncio.sleep` or executor usage to mirror production guidance.

## page.run_task Misuse (Ref: project instructions & §7)
- `FletV2/views/files.py:294` invokes `page.run_task(save_file(event))`, passing the coroutine result instead of the callable. Pass the function (optionally via lambda capturing the event) without executing it eagerly.
- `FletV2/views/files.py:350` wraps `_verify_file_async` in `lambda`; the reference doc warns against using lambda wrappers. Use a partial or define a small async closure and pass it directly.
- `FletV2/views/clients.py:329, 370, 427, 488` call `page.run_task(<async_fn>(event))`, triggering the coroutine immediately. Update these handlers to pass callable references that accept the event via closure.
- `FletV2/utils/user_feedback.py:63` schedules `page.run_task(lambda: on_confirm(e))`; refactor to pass the coroutine function directly while preserving arguments.

## Import Pattern Deviation (Ref: §11.2.1)
- `FletV2/start_integrated_gui.py:90-124` loads utilities with `from utils...` inside try/except without a relative-first import. Rework to attempt relative imports (`from .utils...`) first, then fall back to `FletV2.utils...` as outlined in the reference document.
