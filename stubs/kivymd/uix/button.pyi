# Type stubs for kivymd.uix.button
from typing import Any, Optional, Callable
from kivy.uix.button import Button

class MDButton(Button):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class MDButtonText(Button):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...

class MDIconButton(Button):
    icon: str
    theme_icon_color: str
    icon_color: Any
    on_release: Optional[Callable[..., Any]]
    def __init__(self, **kwargs: Any) -> None: ...

class MDFlatButton(Button):
    def __init__(self, **kwargs: Any) -> None: ...

class MDRaisedButton(Button):
    def __init__(self, **kwargs: Any) -> None: ...