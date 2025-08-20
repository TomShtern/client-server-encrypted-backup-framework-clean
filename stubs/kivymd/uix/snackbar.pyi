# Type stubs for kivymd.uix.snackbar
from typing import Any, Optional
from kivy.uix.widget import Widget

class MDSnackbar(Widget):
    y: Any
    pos_hint: dict[str, Any]
    size_hint_x: Optional[float]
    duration: float
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def open(self) -> None: ...

class MDSnackbarText(Widget):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...