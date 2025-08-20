# Type stubs for kivymd.app
from typing import Any, Optional
from kivy.app import App

class MDApp(App):
    theme_cls: Any
    def __init__(self, **kwargs: Any) -> None: ...
    def build(self) -> Any: ...