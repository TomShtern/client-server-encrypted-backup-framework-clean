# Type stubs for kivymd.uix.selectioncontrol
from typing import Any, Optional, Callable
from kivy.uix.widget import Widget

class MDSwitch(Widget):
    active: bool
    on_active: Optional[Callable[..., Any]]
    def __init__(self, **kwargs: Any) -> None: ...