"""Components package initializer.

This package intentionally avoids importing component modules at import time
to prevent pulling in controls that rely on APIs missing in Flet 0.28.x
(e.g., ``ft.UserControl``).  Import components explicitly from their modules,
for example ``from FletV2.components.log_card import LogCard``.
"""

__all__: list[str] = []
