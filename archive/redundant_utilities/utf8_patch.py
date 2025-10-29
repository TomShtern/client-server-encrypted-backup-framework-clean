"""Lightweight UTF-8 environment normalizer.

Replaces previous external Shared.utils.utf8_solution dependency.
Keeps side-effect only behavior so importing it is safe and idempotent.
"""
from __future__ import annotations

import os
import sys

# Force UTF-8 mode where supported (Python 3.11+ respects PYTHONUTF8=1)
os.environ.setdefault("PYTHONUTF8", "1")

# Ensure default encoding queries reflect UTF-8 intent (informational only)
if hasattr(sys, 'getdefaultencoding'):
    _enc = sys.getdefaultencoding()
    # No logging here to avoid importing logging early; silent on mismatch.

__all__ = []
