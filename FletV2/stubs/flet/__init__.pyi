# Type stubs for Flet 0.28.3 - Core Types
from typing import Any, Optional, List, Dict, Callable, Union
from enum import Enum

class Page:
    # Window properties
    window_width: Optional[int]
    window_height: Optional[int]
    window_min_width: Optional[int]
    window_min_height: Optional[int]
    window_resizable: Optional[bool]
    title: str
    
    # Theme and visual
    theme: Optional[Any]
    dark_theme: Optional[Any]
    theme_mode: Optional[Any]
    visual_density: Optional[Any]
    padding: Optional[Any]
    
    # Event handling
    on_keyboard_event: Optional[Callable[..., Any]]
    
    # Overlays
    overlay: Optional[List[Any]]
    
    # Methods
    def update(self) -> None: ...
    def add(self, *controls: Any) -> None: ...
    def remove(self, control: Any) -> None: ...

class Control:
    # Common properties
    content: Optional[Any]
    selected_index: Optional[int]
    extended: Optional[bool]
    
    # Animation properties
    transition: Optional[Any]
    duration: Optional[int]
    reverse_duration: Optional[int]
    switch_in_curve: Optional[Any]
    switch_out_curve: Optional[Any]
    
    # Layout properties
    expand: Optional[Union[bool, int]]
    leading: Optional[Any]
    controls: Optional[List[Any]]
    
    # Methods
    def update(self) -> None: ...

class Container(Control):
    bgcolor: Optional[str]
    border_radius: Optional[int]
    padding: Optional[Any]
    margin: Optional[Any]
    shadow: Optional[Any]

class AnimatedSwitcher(Control):
    pass

class NavigationRail(Control):
    on_change: Optional[Callable[..., Any]]
    destinations: Optional[List[Any]]

class Column(Control):
    spacing: Optional[int]
    scroll: Optional[Any]

class Row(Control):
    spacing: Optional[int]

class ResponsiveRow(Control):
    pass

class TextField(Control):
    label: Optional[str]
    value: Optional[str]
    on_change: Optional[Callable[..., Any]]
    error_text: Optional[str]

class ElevatedButton(Control):
    text: Optional[str]
    on_click: Optional[Callable[..., Any]]

class FilledButton(Control):
    text: Optional[str]
    on_click: Optional[Callable[..., Any]]

class Text(Control):
    value: Optional[str]
    size: Optional[int]
    weight: Optional[Any]

class Icon(Control):
    name: Optional[str]
    size: Optional[int]

# Enums and constants
class Colors:
    PRIMARY: str
    SECONDARY: str
    ERROR: str
    SURFACE: str
    GREEN: str
    
class Icons:
    DASHBOARD: str
    PEOPLE: str
    FOLDER: str
    SETTINGS: str
    
class FontWeight:
    BOLD: Any
    
class ScrollMode:
    AUTO: Any
    
class ThemeMode:
    SYSTEM: Any
    LIGHT: Any
    DARK: Any

# Functions
def run(target: Callable[[Page], None], **kwargs: Any) -> None: ...

# Type aliases
AppView = Any
Theme = Any
ColorScheme = Any
VisualDensity = Any
Padding = Any