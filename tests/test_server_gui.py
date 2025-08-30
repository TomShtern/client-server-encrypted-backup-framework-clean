#!/usr/bin/env python3
"""Pytest-friendly smoke test placeholder for legacy interactive ServerGUI.

Converted from manual script to a skip-aware test so full suite can run headless.
"""
import pytest

try:  # attempt dynamic import only when running this test
    from Shared.path_utils import setup_imports  # type: ignore
    setup_imports()
    from ServerGUI import ServerGUI  # type: ignore
except Exception as e:  # pragma: no cover - environment dependent
    ServerGUI = None  # type: ignore
    _import_error = str(e)
else:
    _import_error = None


@pytest.mark.skipif(ServerGUI is None, reason="ServerGUI not importable in headless test environment")
def test_server_gui_smoke():
    gui = ServerGUI()
    # Only verify initialize returns bool / does not raise.
    if hasattr(gui, "initialize"):
        try:
            result = gui.initialize()
        except Exception:
            pytest.fail("ServerGUI.initialize raised an exception")
        assert isinstance(result, bool)
