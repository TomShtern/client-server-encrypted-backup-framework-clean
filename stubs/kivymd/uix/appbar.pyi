# Type stubs for kivymd.uix.appbar
from typing import Any, Optional, Callable
from kivy.uix.widget import Widget

class MDTopAppBar(Widget):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class MDTopAppBarTitle(Widget):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...

class MDTopAppBarLeadingButtonContainer(Widget):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class MDTopAppBarTrailingButtonContainer(Widget):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class MDActionTopAppBarButton(Widget):
    icon: str
    on_release: Optional[Callable[..., Any]]
    def __init__(self, **kwargs: Any) -> None: ...