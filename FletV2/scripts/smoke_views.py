#!/usr/bin/env python3
"""
Quick smoke test: import all FletV2 views, instantiate them with minimal mocks,
and run any setup_subscriptions functions to ensure they execute without error.

Run with the project's venv:
  & "./flet_venv/Scripts/python.exe" scripts\smoke_views.py
"""
import asyncio
import importlib
import sys
import traceback
from types import SimpleNamespace
from typing import Any, Callable
import os

# Ensure FletV2 root is on sys.path so `import views.*` works when script runs from scripts/
_script_dir = os.path.dirname(os.path.abspath(__file__))
_flet_root = os.path.dirname(_script_dir)
if _flet_root not in sys.path:
    sys.path.insert(0, _flet_root)

# Also set CWD to FletV2 root to match main.py behavior
try:
    os.chdir(_flet_root)
except Exception:
    pass

# Monkeypatch flet Control.update to a no-op for smoke testing, avoiding "must be added to the page" asserts
try:
    import flet
    from flet.core.control import Control as _FletControl
    if not hasattr(_FletControl, '_smoke_orig_update'):
        _FletControl._smoke_orig_update = _FletControl.update

    def _smoke_update(self, *args, **kwargs):
        # no-op to allow setup_subscriptions to call update() without a real page
        return None

    _FletControl.update = _smoke_update
except Exception:
    # If flet isn't importable in this environment, continue - main app already uses flet
    pass

# Views to test (keeps in sync with main._get_view_config)
VIEW_CONFIGS = {
    "dashboard": ("views.dashboard", "create_dashboard_view"),
    "clients": ("views.clients", "create_clients_view"),
    "files": ("views.files", "create_files_view"),
    "database": ("views.database", "create_database_view"),
    "analytics": ("views.analytics", "create_analytics_view"),
    "logs": ("views.logs", "create_logs_view"),
    "settings": ("views.settings", "create_settings_view"),
}

class PageMock(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.overlay = []
        self.controls = []
        self.theme = SimpleNamespace()
        self._loop = asyncio.get_event_loop()

    def update(self):
        # no-op mock update
        pass

    def open(self, dialog):
        # mimic page.open used by some views
        self.overlay.append(dialog)

    def run_task(self, coro: Callable[..., Any]):
        # schedule a coroutine
        try:
            task = self._loop.create_task(coro()) if callable(coro) else None
            return task
        except Exception:
            # last resort: run synchronously
            return None

async def _maybe_await(result):
    if asyncio.iscoroutine(result):
        await result

async def test_view(module_name: str, func_name: str) -> bool:
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        print(f"[ERROR] Failed to import {module_name}: {e}")
        traceback.print_exc()
        return False

    if not hasattr(module, func_name):
        print(f"[ERROR] {module_name} missing {func_name}")
        return False

    view_func = getattr(module, func_name)

    page = PageMock()
    server_bridge = None
    state_manager = None

    try:
        result = view_func(server_bridge, page, state_manager)
    except Exception as e:
        print(f"[ERROR] {module_name}.{func_name} raised during creation: {e}")
        traceback.print_exc()
        return False

    # Normalize result: could be control, (control, dispose), or (control, dispose, setup_subs)
    setup_cb = None
    if isinstance(result, tuple):
        if len(result) >= 3:
            setup_cb = result[2]
        elif len(result) == 2:
            # no setup_cb
            setup_cb = None
    else:
        setup_cb = getattr(result, '_setup_subscriptions', None)

    # If attribute present on content, prefer that
    if hasattr(result, '_setup_subscriptions') and callable(getattr(result, '_setup_subscriptions')):
        setup_cb = getattr(result, '_setup_subscriptions')

    if setup_cb is None:
        print(f"[OK] {module_name}.{func_name}: created (no setup_subscriptions)")
        return True

    if not callable(setup_cb):
        print(f"[WARN] {module_name}.{func_name}: _setup_subscriptions is present but not callable (type={type(setup_cb).__name__}) - skipping")
        return True

    # Call or await setup_cb safely
    try:
        # Ensure the control and its descendants look "attached" to the mock page so updates don't assert
        def attach_control_recursive(ctrl, page_obj, _seen=None):
            if _seen is None:
                _seen = set()
            try:
                ident = id(ctrl)
                if ident in _seen:
                    return
                _seen.add(ident)
            except Exception:
                pass

            # Try to set the internal mangled page attribute used by flet controls
            try:
                setattr(ctrl, '_Control__page', page_obj)
            except Exception:
                # best-effort
                pass

            # Also set public page attribute if available
            try:
                setattr(ctrl, 'page', page_obj)
            except Exception:
                pass

            # Recurse into common child properties
            for attr in ('content', 'controls', 'rows', 'columns', 'items', 'children'):
                try:
                    child = getattr(ctrl, attr, None)
                    if child is None:
                        continue
                    if isinstance(child, (list, tuple)):
                        for c in child:
                            attach_control_recursive(c, page_obj, _seen=_seen)
                    else:
                        attach_control_recursive(child, page_obj, _seen=_seen)
                except Exception:
                    continue

        try:
            attach_control_recursive(result, page)
        except Exception:
            pass

        if asyncio.iscoroutinefunction(setup_cb):
            await setup_cb()
        else:
            res = setup_cb()
            if asyncio.iscoroutine(res):
                await res
        print(f"[OK] {module_name}.{func_name}: setup_subscriptions executed")
        return True
    except Exception as e:
        print(f"[ERROR] {module_name}.{func_name}: setup_subscriptions failed: {e}")
        traceback.print_exc()
        return False

async def main():
    results = {}
    for view_name, (module_name, func_name) in VIEW_CONFIGS.items():
        print(f"Testing view: {view_name} -> {module_name}.{func_name}")
        ok = await test_view(module_name, func_name)
        results[view_name] = ok

    print("\nSummary:")
    for k, v in results.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")

    failed = [k for k, v in results.items() if not v]
    if failed:
        print("Smoke test FAILED for views:", failed)
        sys.exit(2)
    else:
        print("All views smoke-tested OK")
        sys.exit(0)

if __name__ == '__main__':
    asyncio.run(main())
