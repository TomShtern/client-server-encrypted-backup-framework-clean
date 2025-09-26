# Type stubs for Flet 0.28.3 - Enhanced Core Types
from collections.abc import Callable
from typing import Any

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
    window_width: int | None
    window_height: int | None
    window_min_width: int | None
    window_min_height: int | None
    window_resizable: bool | None
    title: str

    # Theme and visual
    theme: Theme | None
    dark_theme: Theme | None
    theme_mode: ThemeMode | None
    visual_density: VisualDensity | None
    padding: Padding | None

    # Event handling
    on_keyboard_event: Callable[[KeyboardEvent], None] | None

    # Overlays
    overlay: list[Control]

    # Additional window and page properties
    adaptive: bool
    window_center: bool | None
    window_maximized: bool | None
    window_frameless: bool | None
    window_prevent_close: bool | None
    window_visible: bool | None

    # Events / handlers
    on_window_event: Callable[..., Any] | None

    # Common overlays
    snack_bar: SnackBar | None
    banner: Banner | None
    # Connection event
    on_connect: Callable[..., Any] | None

    # Methods
    def update(self) -> None: ...
    def add(self, *controls: Control) -> None: ...
    def remove(self, control: Control) -> None: ...
    def go(self, route: str) -> None: ...
    def show_snack_bar(self, snack_bar: SnackBar) -> None: ...
    def run_task(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any: ...

class Control:
    # Common properties
    content: Control | None
    selected_index: int | None
    extended: bool | None

    # Animation properties
    transition: Any | None
    duration: int | None
    reverse_duration: int | None
    switch_in_curve: Any | None
    switch_out_curve: Any | None

    # Layout properties
    expand: bool | int | None
    leading: Control | None
    controls: list[Control] | None

    # Visual properties
    visible: bool | None
    disabled: bool | None
    opacity: float | None
    width: int | float | None
    height: int | float | None
    animate: Any | None

    # Methods
    def update(self) -> None: ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Container(Control):
    bgcolor: str | None
    border_radius: int | BorderRadius | None
    border: Any | None
    padding: Padding | None
    margin: Padding | None
    shadow: BoxShadow | None
    content: Control | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class AnimatedSwitcher(Control):
    content: Control | None
    transition: Any | None
    duration: int | None
    switch_in_curve: Any | None
    switch_out_curve: Any | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class NavigationRail(Control):
    selected_index: int | None  # Override as Optional to match base
    label_type: NavigationRailLabelType | None
    group_alignment: float | None
    min_width: int | None
    min_extended_width: int | None
    extended: bool | None  # Override as Optional to match base
    bgcolor: str | None
    indicator_color: str | None
    indicator_shape: Any | None
    elevation: int | None
    destinations: list[NavigationRailDestination] | None
    on_change: Callable[[ControlEvent], None] | None
    leading: Control | None
    trailing: Control | None

class NavigationRailDestination:
    icon: Icon | None
    selected_icon: Icon | None
    label: str | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Column(Control):
    spacing: int | float | None
    scroll: ScrollMode | None
    controls: list[Control] | None  # Override as Optional to match base
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Row(Control):
    spacing: int | float | None
    controls: list[Control] | None  # Override as Optional to match base
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class ResponsiveRow(Row):
    col: dict[str, int | float] | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class TextField(Control):
    label: str | None
    value: str | None
    hint_text: str | None
    error_text: str | None
    on_change: Callable[[ControlEvent], None] | None
    on_submit: Callable[[ControlEvent], None] | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class ElevatedButton(Control):
    text: str | None
    icon: str | None
    on_click: Callable[[ControlEvent], None] | None
    disabled: bool | None
    style: Any | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class FilledButton(Control):
    text: str | None
    icon: str | None
    on_click: Callable[[ControlEvent], None] | None
    disabled: bool | None
    style: Any | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class OutlinedButton(Control):
    text: str | None
    icon: str | None
    on_click: Callable[[ControlEvent], None] | None
    disabled: bool | None
    style: Any | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class TextButton(Control):
    text: str | None
    icon: str | None
    on_click: Callable[[ControlEvent], None] | None
    disabled: bool | None
    style: Any | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Text(Control):
    value: str | None
    size: int | float | None
    weight: FontWeight | None
    color: str | None
    style: Any | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Icon(Control):
    name: str | None
    size: int | float | None
    color: str | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class ProgressBar(Control):
    value: float | None
    color: str | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class SnackBar(Control):
    content: Control | None
    action: str | None
    on_action: Callable[[], None] | None
    bgcolor: str | None
    open: bool | None
    behavior: SnackBarBehavior | None
    margin: Margin | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Banner:
    content: Control
    bgcolor: str | None
    actions: list[Control] | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

# Supporting classes
class BorderRadius:
    def __init__(self, top_left: int = 0, top_right: int = 0, bottom_left: int = 0, bottom_right: int = 0) -> None: ...

class BoxShadow:
    spread_radius: float
    blur_radius: float
    color: str
    offset: Offset
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
    def __init__(self, left: int | float = 0, top: int | float = 0,
                 right: int | float = 0, bottom: int | float = 0) -> None: ...

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
    BOLD: FontWeight
    W_500: FontWeight
    W_400: FontWeight
    W_600: FontWeight
    W_800: FontWeight
    W_900: FontWeight

class ScrollMode:
    AUTO: ScrollMode
    ALWAYS: ScrollMode
    HIDDEN: ScrollMode

class ThemeMode:
    SYSTEM: ThemeMode
    LIGHT: ThemeMode
    DARK: ThemeMode

class NavigationRailLabelType:
    NONE: NavigationRailLabelType
    SELECTED: NavigationRailLabelType
    ALL: NavigationRailLabelType

class VisualDensity:
    STANDARD: VisualDensity
    COMPACT: VisualDensity
    COMFORTABLE: VisualDensity

# Theme classes
class Theme:
    color_scheme: ColorScheme | None
    visual_density: VisualDensity | None
    text_theme: TextTheme | None
    def __init__(self, **kwargs: Any) -> None: ...

class TextStyle:
    size: int | float | None
    weight: FontWeight | None
    color: str | None
    def __init__(self, **kwargs: Any) -> None: ...

class TextTheme:
    def __init__(self, **kwargs: Any) -> None: ...

class TextThemeStyle:
    TITLE_MEDIUM: TextThemeStyle
    HEADLINE_MEDIUM: TextThemeStyle
    BODY_SMALL: TextThemeStyle
    BODY_MEDIUM: TextThemeStyle
    LABEL_LARGE: TextThemeStyle
    LABEL_SMALL: TextThemeStyle

class ColorScheme:
    primary: str
    secondary: str
    tertiary: str | None
    surface: str
    background: str | None
    error: str | None
    on_primary: str | None
    on_secondary: str | None
    on_surface: str | None
    on_background: str | None
    def __init__(self, **kwargs: Any) -> None: ...

class ButtonStyle:
    def __init__(self, **kwargs: Any) -> None: ...

class RoundedRectangleBorder:
    def __init__(self, **kwargs: Any) -> None: ...

class ControlState:
    HOVERED: ControlState
    PRESSED: ControlState

class Divider(Control): ...

class ProgressRing(Control):
    width: int | float | None
    height: int | float | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

# Additional common controls used by the app
class VerticalDivider(Control):
    width: int | float | None
    color: str | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class FloatingActionButton(Control):
    icon: str | None
    mini: bool | None
    tooltip: str | None
    on_click: Callable[[ControlEvent], None] | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Card(Control):
    content: Control | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Chip(Control):
    label: str | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class IconButton(Control):
    icon: str | None
    tooltip: str | None
    on_click: Callable[[ControlEvent], None] | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Badge(Control):
    small_size: int | float | None
    bgcolor: str | None
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class SnackBarBehavior:
    FLOATING: SnackBarBehavior

class Margin:
    def __init__(self, left: int | float = 0, top: int | float = 0,
                 right: int | float = 0, bottom: int | float = 0) -> None: ...

# Utility namespaces and functions

class padding:
    @staticmethod
    def all(value: int | float) -> Padding: ...
    @staticmethod
    def symmetric(*, horizontal: int | float = 0, vertical: int | float = 0) -> Padding: ...

class margin:
    @staticmethod
    def symmetric(*, horizontal: int | float = 0, vertical: int | float = 0) -> Padding: ...

class border:
    @staticmethod
    def all(width: int | float, color: str) -> Any: ...

class alignment:
    center: Any

class animation:
    class Animation:
        def __init__(self, duration: int | float, curve: Any | None = None) -> None: ...

# Top-level animation classes/enums
class Animation:
    def __init__(self, duration: int | float, curve: Any | None = None) -> None: ...

class AnimationCurve:
    EASE_OUT: AnimationCurve
    EASE_OUT_CUBIC: AnimationCurve
    EASE_IN_CUBIC: AnimationCurve

class AnimatedSwitcherTransition:
    FADE: AnimatedSwitcherTransition

# Functions
def run(target: Callable[[Page], None] | Callable[[Page], Any], **kwargs: Any) -> None: ...

# Type aliases
AppView = Any
DARK_MODE: str
LIGHT_MODE: str
class MainAxisAlignment:
    START: MainAxisAlignment
    CENTER: MainAxisAlignment
    SPACE_BETWEEN: MainAxisAlignment
class CrossAxisAlignment:
    START: CrossAxisAlignment
    CENTER: CrossAxisAlignment
Ref = Any
DataTable = Any
Scale = Any
Rotate = Any
