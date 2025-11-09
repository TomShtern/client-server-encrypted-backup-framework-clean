#!/usr/bin/env python3
"""
pytest configuration for FletV2

Configures Python path for tests to use absolute imports (from FletV2.module import ...)
without requiring manual sys.path manipulation in test files.
"""

import sys
from pathlib import Path

# Add FletV2 root and repository root to sys.path for tests
flet_v2_root = Path(__file__).parent.absolute()
repo_root = flet_v2_root.parent.absolute()

for path in (str(flet_v2_root), str(repo_root)):
    if path not in sys.path:
        sys.path.insert(0, path)

print("[pytest] Configured paths:")
print(f"  - FletV2 root: {flet_v2_root}")
print(f"  - Repo root: {repo_root}")
