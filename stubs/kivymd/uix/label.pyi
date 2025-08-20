# Type stubs for kivymd.uix.label
from typing import Any
from kivy.uix.label import Label

class MDLabel(Label):
    text: str
    halign: str
    theme_text_color: str
    def __init__(self, **kwargs: Any) -> None: ...