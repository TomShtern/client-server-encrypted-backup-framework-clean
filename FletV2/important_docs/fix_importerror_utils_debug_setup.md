# Fix: ImportError "No module named 'utils.debug_setup'" in FletV2

This guide explains the exact cause and the precise steps to fix the error when launching the FletV2 GUI.

## Symptom
- GUI shows: `An error occurred: No module named 'utils.debug_setup'`.

## Root cause
- One or more entry files used an unsafe sys.path bootstrap (going two directories up) which removed the `FletV2/` root from `sys.path`. As a result, Python couldn't find `FletV2/utils/debug_setup.py` during early imports.

## Verified fix (applied in repo)
- Added a robust path bootstrap at the top of `FletV2/main.py` which ensures the `FletV2` root is on `sys.path` before any other imports. This matches the documented pattern in `.github/copilot-instructions.md`.
- Confirmed `FletV2/utils/debug_setup.py` and `FletV2/utils/__init__.py` exist and export `setup_terminal_debugging` and `get_logger`.

### The bootstrap snippet now in `FletV2/main.py`
```python
import os
import sys

_here = os.path.abspath(__file__)
_base = os.path.dirname(_here)
if os.path.basename(_base) == "FletV2":
    flet_v2_root = _base
else:
    flet_v2_root = os.path.dirname(_base)  # if file is in a subfolder

if flet_v2_root not in sys.path:
    sys.path.insert(0, flet_v2_root)

# Optional: enable Shared.* imports if Shared is a sibling of FletV2
repo_root = os.path.dirname(flet_v2_root)
if os.path.isdir(os.path.join(repo_root, "Shared")) and repo_root not in sys.path:
    sys.path.insert(0, repo_root)
```

## What you need to do if the issue reappears
1) Ensure you launch from the repo root or the `FletV2/` folder:
   - `python .\FletV2\main.py` (desktop)
   - or use the integrated starter `python .\FletV2\start_integrated_gui.py`.
2) If you create new entry files directly under `FletV2/`, paste the same bootstrap at the very top.
3) If a view or util uses its own `sys.path.insert(...)` lines, remove them and rely on the central bootstrap.

## Sanity check
- From repo root, run the integration tests:
  - Task: "Run FletV2 integration tests" (VS Code)

Expected: no `ImportError` for `utils.debug_setup`.

## Notes
- If you run scripts from other working directories, set `PYTHONPATH` to include the `FletV2` root.
- Avoid star imports and late UTF-8 setup; follow the import order documented in `.github/copilot-instructions.md`.
