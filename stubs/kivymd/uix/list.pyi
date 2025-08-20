# Type stubs for kivymd.uix.list
from typing import Any
from kivy.uix.widget import Widget

class MDList(Widget):
    def __init__(self, **kwargs: Any) -> None: ...

class MDListItem(Widget):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class MDListItemHeadlineText(Widget):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...

class MDListItemSupportingText(Widget):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...

class MDListItemTrailingIcon(Widget):
    icon: str
    def __init__(self, **kwargs: Any) -> None: ...

class MDListItemTrailingSupportingText(Widget):
    text: str
    def __init__(self, **kwargs: Any) -> None: ...