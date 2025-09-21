# Type stubs for Flet 0.28.3 - Enhanced Core Types
from typing import Any, Optional, List, Dict, Callable, Union

# Event types
class ControlEvent:
    control: Any
    data: str
    target: Any

class KeyboardEvent:
    key: str
    shift: bool
    ctrl: bool
    alt: bool
    meta: bool

class OnScrollEvent:
    pixels: float
    min_scroll_extent: float
    max_scroll_extent: float

# Core classes
class Page:
    # Window properties
    window_width: Optional[int]
    window_height: Optional[int]
    window_min_width: Optional[int]
    window_min_height: Optional[int]
    window_resizable: Optional[bool]
    title: str

    # Theme and visual
    theme: Optional['Theme']
    dark_theme: Optional['Theme']
    theme_mode: Optional['ThemeMode']
    visual_density: Optional['VisualDensity']
    padding: Optional['Padding']

    # Event handling
    on_keyboard_event: Optional[Callable[[KeyboardEvent], None]]

    # Overlays
    overlay: List['Control']

    # Additional window and page properties
    adaptive: bool
    window_center: Optional[bool]
    window_maximized: Optional[bool]
    window_frameless: Optional[bool]
    window_prevent_close: Optional[bool]
    window_visible: Optional[bool]

    # Events / handlers
    on_window_event: Optional[Callable[..., Any]]

    # Common overlays
    snack_bar: Optional['SnackBar']
    banner: Optional['Banner']
    # Connection event
    on_connect: Optional[Callable[..., Any]]

    # Methods
    def update(self) -> None: ...
    def add(self, *controls: 'Control') -> None: ...
    def remove(self, control: 'Control') -> None: ...
    def go(self, route: str) -> None: ...
    def show_snack_bar(self, snack_bar: 'SnackBar') -> None: ...
    def run_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any: ...

class Control:
    # Common properties
    content: Optional['Control']
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
    leading: Optional['Control']
    controls: Optional[List['Control']]

    # Visual properties
    visible: Optional[bool]
    disabled: Optional[bool]
    opacity: Optional[float]
    width: Optional[Union[int, float]]
    height: Optional[Union[int, float]]
    animate: Optional[Any]

    # Methods
    def update(self) -> None: ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Container(Control):
    bgcolor: Optional[str]
    border_radius: Optional[Union[int, 'BorderRadius']]
    border: Optional[Any]
    padding: Optional['Padding']
    margin: Optional['Padding']
    shadow: Optional['BoxShadow']
    content: Optional['Control']
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class AnimatedSwitcher(Control):
    content: Optional['Control']
    transition: Optional[Any]
    duration: Optional[int]
    switch_in_curve: Optional[Any]
    switch_out_curve: Optional[Any]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class NavigationRail(Control):
    selected_index: Optional[int]  # Override as Optional to match base
    label_type: Optional['NavigationRailLabelType']
    group_alignment: Optional[float]
    min_width: Optional[int]
    min_extended_width: Optional[int]
    extended: Optional[bool]  # Override as Optional to match base
    bgcolor: Optional[str]
    indicator_color: Optional[str]
    indicator_shape: Optional[Any]
    elevation: Optional[int]
    destinations: Optional[List['NavigationRailDestination']]
    on_change: Optional[Callable[[ControlEvent], None]]
    leading: Optional['Control']
    trailing: Optional['Control']

class NavigationRailDestination:
    icon: Optional['Icon']
    selected_icon: Optional['Icon']
    label: Optional[str]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Column(Control):
    spacing: Optional[Union[int, float]]
    scroll: Optional['ScrollMode']
    controls: Optional[List['Control']]  # Override as Optional to match base
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Row(Control):
    spacing: Optional[Union[int, float]]
    controls: Optional[List['Control']]  # Override as Optional to match base
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class ResponsiveRow(Row):
    col: Optional[Dict[str, Union[int, float]]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class TextField(Control):
    label: Optional[str]
    value: Optional[str]
    hint_text: Optional[str]
    error_text: Optional[str]
    on_change: Optional[Callable[[ControlEvent], None]]
    on_submit: Optional[Callable[[ControlEvent], None]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class ElevatedButton(Control):
    text: Optional[str]
    icon: Optional[str]
    on_click: Optional[Callable[[ControlEvent], None]]
    disabled: Optional[bool]
    style: Optional[Any]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class FilledButton(Control):
    text: Optional[str]
    icon: Optional[str]
    on_click: Optional[Callable[[ControlEvent], None]]
    disabled: Optional[bool]
    style: Optional[Any]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class OutlinedButton(Control):
    text: Optional[str]
    icon: Optional[str]
    on_click: Optional[Callable[[ControlEvent], None]]
    disabled: Optional[bool]
    style: Optional[Any]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class TextButton(Control):
    text: Optional[str]
    icon: Optional[str]
    on_click: Optional[Callable[[ControlEvent], None]]
    disabled: Optional[bool]
    style: Optional[Any]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Text(Control):
    value: Optional[str]
    size: Optional[Union[int, float]]
    weight: Optional['FontWeight']
    color: Optional[str]
    style: Optional[Any]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Icon(Control):
    name: Optional[str]
    size: Optional[Union[int, float]]
    color: Optional[str]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class ProgressBar(Control):
    value: Optional[float]
    color: Optional[str]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class SnackBar(Control):
    content: Optional['Control']
    action: Optional[str]
    on_action: Optional[Callable[[], None]]
    bgcolor: Optional[str]
    open: Optional[bool]
    behavior: Optional['SnackBarBehavior']
    margin: Optional['Margin']
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Banner:
    content: 'Control'
    bgcolor: Optional[str]
    actions: Optional[List['Control']]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

# Supporting classes
class BorderRadius:
    def __init__(self, top_left: int = 0, top_right: int = 0, bottom_left: int = 0, bottom_right: int = 0) -> None: ...

class BoxShadow:
    spread_radius: float
    blur_radius: float
    color: str
    offset: 'Offset'
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Offset:
    x: float
    y: float
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Padding:
    left: float
    top: float
    right: float
    bottom: float
    def __init__(self, left: Union[int, float] = 0, top: Union[int, float] = 0,
                 right: Union[int, float] = 0, bottom: Union[int, float] = 0) -> None: ...

# Enums and constants
class Colors:
    PRIMARY: str
    SECONDARY: str
    ERROR: str
    SURFACE: str
    SURFACE_TINT: str
    OUTLINE: str
    TRANSPARENT: str
    GREEN: str
    BLUE: str
    RED: str
    ORANGE: str
    BLACK: str
    WHITE: str
    ON_SURFACE: str
    ON_SURFACE_VARIANT: str
    INVERSE_SURFACE: str
    ON_INVERSE_SURFACE: str

    @staticmethod
    def with_opacity(opacity: float, color: str) -> str: ...

class Icons:
    DASHBOARD: str
    DASHBOARD_OUTLINED: str
    PEOPLE: str
    PEOPLE_OUTLINE: str
    FOLDER: str
    FOLDER_OUTLINED: str
    STORAGE: str
    STORAGE_OUTLINED: str
    AUTO_GRAPH: str
    AUTO_GRAPH_OUTLINED: str
    ARTICLE: str
    ARTICLE_OUTLINED: str
    SETTINGS: str
    SETTINGS_OUTLINED: str
    PLAY_ARROW: str
    STOP: str
    REFRESH: str
    MENU: str
    MENU_OPEN: str
    MENU_ROUNDED: str
    MENU_OPEN_ROUNDED: str
    BRIGHTNESS_6: str
    BRIGHTNESS_6_ROUNDED: str

class FontWeight:
    BOLD: 'FontWeight'
    W_500: 'FontWeight'
    W_400: 'FontWeight'
    W_600: 'FontWeight'
    W_800: 'FontWeight'
    W_900: 'FontWeight'

class ScrollMode:
    AUTO: 'ScrollMode'
    ALWAYS: 'ScrollMode'
    HIDDEN: 'ScrollMode'

class ThemeMode:
    SYSTEM: 'ThemeMode'
    LIGHT: 'ThemeMode'
    DARK: 'ThemeMode'

class NavigationRailLabelType:
    NONE: 'NavigationRailLabelType'
    SELECTED: 'NavigationRailLabelType'
    ALL: 'NavigationRailLabelType'

class VisualDensity:
    STANDARD: 'VisualDensity'
    COMPACT: 'VisualDensity'
    COMFORTABLE: 'VisualDensity'

# Theme classes
class Theme:
    color_scheme: Optional['ColorScheme']
    visual_density: Optional['VisualDensity']
    text_theme: Optional['TextTheme']
    def __init__(self, **kwargs: Any) -> None: ...

class TextStyle:
    size: Optional[Union[int, float]]
    weight: Optional['FontWeight']
    color: Optional[str]
    def __init__(self, **kwargs: Any) -> None: ...

class TextTheme:
    def __init__(self, **kwargs: Any) -> None: ...

class TextThemeStyle:
    TITLE_MEDIUM: 'TextThemeStyle'
    HEADLINE_MEDIUM: 'TextThemeStyle'
    BODY_SMALL: 'TextThemeStyle'
    BODY_MEDIUM: 'TextThemeStyle'
    LABEL_LARGE: 'TextThemeStyle'
    LABEL_SMALL: 'TextThemeStyle'

class ColorScheme:
    primary: str
    secondary: str
    tertiary: Optional[str]
    surface: str
    background: Optional[str]
    error: Optional[str]
    on_primary: Optional[str]
    on_secondary: Optional[str]
    on_surface: Optional[str]
    on_background: Optional[str]
    def __init__(self, **kwargs: Any) -> None: ...

class ButtonStyle:
    def __init__(self, **kwargs: Any) -> None: ...

class RoundedRectangleBorder:
    def __init__(self, **kwargs: Any) -> None: ...

class ControlState:
    HOVERED: 'ControlState'
    PRESSED: 'ControlState'

class Divider(Control): ...

class ProgressRing(Control):
    width: Optional[Union[int, float]]
    height: Optional[Union[int, float]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

# Additional common controls used by the app
class VerticalDivider(Control):
    width: Optional[Union[int, float]]
    color: Optional[str]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class FloatingActionButton(Control):
    icon: Optional[str]
    mini: Optional[bool]
    tooltip: Optional[str]
    on_click: Optional[Callable[[ControlEvent], None]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Card(Control):
    content: Optional['Control']
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Chip(Control):
    label: Optional[str]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class IconButton(Control):
    icon: Optional[str]
    tooltip: Optional[str]
    on_click: Optional[Callable[[ControlEvent], None]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Badge(Control):
    small_size: Optional[Union[int, float]]
    bgcolor: Optional[str]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class SnackBarBehavior:
    FLOATING: 'SnackBarBehavior'

class Margin:
    def __init__(self, left: Union[int, float] = 0, top: Union[int, float] = 0,
                 right: Union[int, float] = 0, bottom: Union[int, float] = 0) -> None: ...

# Utility namespaces and functions

class padding:
    @staticmethod
    def all(value: Union[int, float]) -> Padding: ...
    @staticmethod
    def symmetric(*, horizontal: Union[int, float] = 0, vertical: Union[int, float] = 0) -> Padding: ...

class margin:
    @staticmethod
    def symmetric(*, horizontal: Union[int, float] = 0, vertical: Union[int, float] = 0) -> Padding: ...

class border:
    @staticmethod
    def all(width: Union[int, float], color: str) -> Any: ...

class alignment:
    center: Any

class animation:
    class Animation:
        def __init__(self, duration: Union[int, float], curve: Any | None = None) -> None: ...

# Top-level animation classes/enums
class Animation:
    def __init__(self, duration: Union[int, float], curve: Any | None = None) -> None: ...

class AnimationCurve:
    EASE_OUT: 'AnimationCurve'
    EASE_OUT_CUBIC: 'AnimationCurve'
    EASE_IN_CUBIC: 'AnimationCurve'

class AnimatedSwitcherTransition:
    FADE: 'AnimatedSwitcherTransition'

# Functions
def run(target: Callable[[Page], None] | Callable[[Page], Any], **kwargs: Any) -> None: ...

# Type aliases
AppView = Any
DARK_MODE: str
LIGHT_MODE: str
class MainAxisAlignment:
    START: 'MainAxisAlignment'
    CENTER: 'MainAxisAlignment'
    SPACE_BETWEEN: 'MainAxisAlignment'
class CrossAxisAlignment:
    START: 'CrossAxisAlignment'
    CENTER: 'CrossAxisAlignment'
Ref = Any
DataTable = Any
Scale = Any
Rotate = Any