# Type stubs for kivymd.uix.textfield
from typing import Any, Optional
from kivy.uix.textinput import TextInput

class MDTextField(TextInput):
    mode: str
    text: str
    hint_text: str
    input_filter: Optional[str]
    error: bool
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class MDTextFieldSupportingText(TextInput):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...

class MDTextFieldHintText(TextInput):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...