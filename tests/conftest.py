"""Pytest configuration: provide a fallback flet shim if real flet not installed."""
import sys
from pathlib import Path
import importlib.util

try:
    import flet  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    # Load flet_shim via spec to avoid relative import issues when tests directory not a package
    shim_path = Path(__file__).parent / 'flet_shim.py'
    spec = importlib.util.spec_from_file_location('flet', shim_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore
    sys.modules['flet'] = module

# Ensure repository root and flet_server_gui package path are on sys.path
ROOT = Path(__file__).parent.parent
pkg_path = ROOT / 'flet_server_gui'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(pkg_path) not in sys.path:
    sys.path.insert(0, str(pkg_path))
