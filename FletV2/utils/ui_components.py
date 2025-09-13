#!/usr/bin/env python3
"""
Modern UI Components for FletV2
Enhanced 2025 design polish with sophisticated visual elements and accessibility.

Provides polished, reusable components following 2025 UI/UX best practices.
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union
from utils.debug_setup import get_logger

logger = get_logger(__name__)


def create_modern_card(
    content: ft.Control,
    title: Optional[str] = None,
    icon: Optional[str] = None,
    actions: Optional[List[ft.Control]] = None,
    elevation: Union[str, int] = "elevated",  # Enhanced default shadow
    is_dark: bool = False,
    hover_effect: bool = True,
    color_accent: Optional[str] = None,
    width: Optional[float] = None,
    padding: int = 28,  # Enhanced default padding
    return_type: str = "card"  # "container" or "card"
) -> Union[ft.Container, ft.Card]:
    """
    Create a modern card with comprehensive 2025 design standards.

    This unified function combines the styling capabilities from theme.py
    and the structural features from the original ui_components.py.

    Features:
    - Both ft.Container and ft.Card return types
    - Enhanced shadow system with named styles
    - Color accent support with brand colors
    - Dark theme compatibility
    - Optional title, icon, and actions
    - Modern typography and spacing
    - Accessibility support
    - Hover animations

    Args:
        content: Main content control
        title: Optional card title
        icon: Optional icon name (ft.Icons)
        actions: Optional list of action controls
        elevation: Shadow style name ("subtle", "soft", "medium", "elevated", "floating") or numeric elevation
        is_dark: Whether to use dark theme colors
        hover_effect: Enable hover animations
        color_accent: Color accent name for subtle border
        width: Optional fixed width
        padding: Internal padding (default 20)
        return_type: "container" for ft.Container, "card" for ft.Card

    Returns:
        Union[ft.Container, ft.Card]: Modern card component
    """

    # Import shadow helper if available; use theme-native roles for colors
    try:
        from theme import get_shadow_style  # type: ignore
    except ImportError:
        # Fallback if theme functions not available
        def get_shadow_style(style_name, is_dark=False):
            elevation_map = {"subtle": 1, "soft": 2, "medium": 4, "elevated": 6, "floating": 8}
            return elevation_map.get(style_name, 2)

    # Build card content structure
    card_content = []

    # Add title row if title or icon provided
    if title or icon:
        title_controls = []
        if icon:
            title_controls.append(
                ft.Icon(
                    icon,
                    size=24,
                    color=ft.Colors.PRIMARY
                )
            )
            title_controls.append(ft.Container(width=12))  # Spacing

        if title:
            title_controls.append(
                ft.Text(
                    title,
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE,
                    style=ft.TextThemeStyle.TITLE_MEDIUM
                )
            )

        card_content.append(
            ft.Row(
                controls=title_controls,
                alignment=ft.MainAxisAlignment.START
            )
        )
        card_content.append(ft.Container(height=16))  # Spacing

    # Add main content
    card_content.append(content)

    # Add actions if provided
    if actions:
        card_content.extend([
            ft.Container(height=20),  # Spacing
            ft.Row(
                controls=actions,
                alignment=ft.MainAxisAlignment.END,
                spacing=8
            )
        ])

    # Create content column
    content_column = ft.Column(
        controls=card_content,
        spacing=0,
        tight=True
    )

    if return_type == "container":
        # Container-based card using Material 3 theme roles
        if isinstance(elevation, str):
            shadow = get_shadow_style(elevation, is_dark)
        else:
            shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=max(elevation * 2, 4),
                offset=ft.Offset(0, max(elevation // 2, 1)),
                color=ft.Colors.with_opacity(0.12, ft.Colors.SHADOW),
            )

        # Respect current theme: SURFACE adapts to light/dark automatically
        bg_color = ft.Colors.SURFACE

        # Subtle outline using theme role; optional accent only tweaks opacity
        border_color = ft.Colors.OUTLINE
        if color_accent:
            border_color = ft.Colors.with_opacity(0.24, ft.Colors.PRIMARY)

        card = ft.Container(
            content=content_column,
            bgcolor=bg_color,
            shadow=shadow,
            border_radius=20,  # Enhanced modern rounded corners
            border=ft.border.all(1, border_color),
            padding=padding,
            width=width,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT) if hover_effect else None,  # Smoother animation
        )
    else:
        # Card-based component (original ui_components.py style)
        elevation_value = 3 if isinstance(elevation, str) else elevation

        card = ft.Card(
            content=ft.Container(
                content=content_column,
                padding=ft.Padding(padding, padding, padding, padding),
                border_radius=ft.BorderRadius(20, 20, 20, 20)
            ),
            elevation=elevation_value,
            margin=ft.Margin(8, 8, 8, 8),
            width=width
        )

        # Add hover animation
        if hover_effect:
            card.content.animate = ft.Animation(200, ft.AnimationCurve.EASE_OUT)

    return card


def create_stat_card(
    label: str,
    value: str,
    icon: str,
    color: str = ft.Colors.PRIMARY,
    trend: Optional[str] = None,
    trend_color: str = ft.Colors.GREEN
) -> ft.Card:
    """
    Create a modern statistics card with trend indicators.

    Features:
    - Large value display
    - Color-coded icons
    - Optional trend indicators
    - Responsive design
    """

    # Main content
    content_controls = [
        ft.Row([
            ft.Icon(
                icon,
                size=32,
                color=color
            ),
            ft.Container(expand=True),  # Spacer
            ft.Text(
                value,
                size=28,
                weight=ft.FontWeight.W_700,
                color=ft.Colors.ON_SURFACE,
                style=ft.TextThemeStyle.HEADLINE_MEDIUM
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        ft.Container(height=12),

        ft.Row([
            ft.Text(
                label,
                size=14,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ON_SURFACE,
                style=ft.TextThemeStyle.BODY_MEDIUM
            ),
            ft.Container(expand=True)  # Spacer
        ])
    ]

    # Add trend if provided
    if trend:
        content_controls.append(
            ft.Container(
                content=ft.Text(
                    trend,
                    size=12,
                    weight=ft.FontWeight.W_500,
                    color=trend_color,
                    style=ft.TextThemeStyle.LABEL_MEDIUM
                ),
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=ft.Colors.with_opacity(0.1, trend_color),
                border_radius=ft.BorderRadius(12, 12, 12, 12),
                margin=ft.Margin(0, 8, 0, 0)
            )
        )

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=content_controls,
                spacing=0,
                tight=True
            ),
            padding=ft.Padding(20, 16, 20, 16),
            border_radius=ft.BorderRadius(16, 16, 16, 16)
        ),
        elevation=2,
        margin=ft.Margin(4, 4, 4, 4)
    )


def create_modern_button(
    text: str,
    on_click: Callable,
    icon: Optional[str] = None,
    variant: str = "filled",  # "filled", "outlined", "elevated", "text"
    color: str = ft.Colors.PRIMARY,
    color_type: str = "primary",  # "primary", "secondary", "accent_emerald" etc. for theme integration
    size: str = "medium",  # "small", "medium", "large"
    disabled: bool = False,
    loading: bool = False,
    is_dark: bool = False,
    use_theme_colors: bool = True
) -> ft.Control:
    """
    Create a modern button with comprehensive 2025 design standards.

    Enhanced to integrate with theme system from theme.py for consistent styling.

    Features:
    - Multiple variants (filled, outlined, elevated, text)
    - Theme-aware color system
    - Size variants with proper padding
    - Loading states with progress indicators
    - Icon support with proper spacing
    - Enhanced accessibility
    - Integration with brand color system
    """

    # Import theme function for consistent colors
    if use_theme_colors:
        try:
            from theme import get_brand_color, create_modern_button_style
            base_color = get_brand_color(color_type, is_dark)

            # Use theme's enhanced button style if available
            if hasattr(create_modern_button_style, '__call__'):
                try:
                    theme_style = create_modern_button_style(color_type, is_dark, variant)
                except Exception:
                    theme_style = None
            else:
                theme_style = None
        except ImportError:
            base_color = color
            theme_style = None
    else:
        base_color = color
        theme_style = None

    # Size configurations with enhanced padding and spacing
    size_configs = {
        "small": {"padding": ft.Padding(16, 10, 16, 10), "text_size": 14, "icon_size": 18},
        "medium": {"padding": ft.Padding(28, 14, 28, 14), "text_size": 16, "icon_size": 20},  # Enhanced padding
        "large": {"padding": ft.Padding(36, 18, 36, 18), "text_size": 18, "icon_size": 22}  # Enhanced padding
    }

    config = size_configs.get(size, size_configs["medium"])

    # Button content
    button_controls = []

    if loading:
        button_controls.append(
            ft.ProgressRing(width=16, height=16, stroke_width=2)
        )
    elif icon:
        button_controls.append(
            ft.Icon(icon, size=config["icon_size"])
        )

    if loading:
        button_controls.append(ft.Container(width=8))
        button_controls.append(ft.Text("Loading...", size=config["text_size"]))
    else:
        if icon:
            button_controls.append(ft.Container(width=8))
        button_controls.append(
            ft.Text(
                text,
                size=config["text_size"],
                weight=ft.FontWeight.W_600
            )
        )

    button_content = ft.Row(
        controls=button_controls,
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True
    ) if len(button_controls) > 1 else button_controls[0]

    # Create enhanced button style - use theme style if available, otherwise sophisticated fallback
    if theme_style:
        button_style = theme_style
        # Update padding for size if needed
        if hasattr(button_style, 'padding') and button_style.padding:
            button_style.padding = config["padding"]
    else:
        # Enhanced button style with better visual effects
        button_style = ft.ButtonStyle(
            padding=config["padding"],
            shape=ft.RoundedRectangleBorder(radius=20),  # Enhanced border radius
            animation_duration=250,  # Smoother animation
            elevation=4,  # Enhanced elevation
            shadow_color=base_color  # Color-matched shadow
        )

    if variant == "filled":
        return ft.FilledButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )
    elif variant == "outlined":
        return ft.OutlinedButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )
    elif variant == "elevated":
        return ft.ElevatedButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )
    else:  # text
        return ft.TextButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )


def create_floating_action_button(
    icon: str,
    on_click: Callable,
    color_type: str = "primary",
    is_dark: bool = False,
    mini: bool = False,
    tooltip: str = "Quick Action"
) -> ft.FloatingActionButton:
    """
    Create modern floating action button with enhanced shadow and vibrant colors.

    Consolidated from theme.py with enhanced functionality.

    Features:
    - Theme-aware colors
    - Dark mode support
    - Customizable tooltip
    - Smooth animations
    - Mini size variant
    """
    # Import theme function for consistent colors
    try:
        from theme import get_brand_color
        base_color = get_brand_color(color_type, is_dark)
    except ImportError:
        base_color = ft.Colors.PRIMARY

    return ft.FloatingActionButton(
        icon=icon,
        on_click=on_click,
        bgcolor=base_color,
        foreground_color=ft.Colors.WHITE,
        elevation=8,
        shape=ft.CircleBorder(),
        mini=mini,
        tooltip=tooltip,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT_BACK)
    )


def create_progress_indicator(
    value: float,
    label: str,
    color: str = ft.Colors.PRIMARY,
    show_percentage: bool = True,
    height: float = 8,
    animated: bool = True
) -> ft.Container:
    """
    Create a modern progress indicator with smooth animations.

    Features:
    - Smooth progress animations
    - Color coding for different states
    - Optional percentage display
    - Modern rounded design
    """

    # Determine color based on value if not specified
    if color == ft.Colors.PRIMARY and value > 0:
        if value < 0.5:
            display_color = ft.Colors.GREEN
        elif value < 0.8:
            display_color = ft.Colors.ORANGE
        else:
            display_color = ft.Colors.RED
    else:
        display_color = color

    # Progress bar
    progress_bar = ft.ProgressBar(
        value=value,
        color=display_color,
        bgcolor=ft.Colors.with_opacity(0.1, display_color),
        height=height,
        border_radius=ft.BorderRadius(height/2, height/2, height/2, height/2)
    )

    if animated:
        progress_bar.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_OUT)

    # Label and percentage
    label_controls = [
        ft.Text(
            label,
            size=14,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_SURFACE,
            style=ft.TextThemeStyle.BODY_MEDIUM
        )
    ]

    if show_percentage:
        label_controls.append(
            ft.Text(
                f"{value * 100:.1f}%",
                size=14,
                weight=ft.FontWeight.W_600,
                color=display_color,
                style=ft.TextThemeStyle.BODY_MEDIUM
            )
        )

    return ft.Container(
        content=ft.Column([
            ft.Row(
                controls=label_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Container(height=8),
            progress_bar
        ], spacing=0, tight=True),
        padding=ft.Padding(0, 8, 0, 8)
    )


def create_info_chip(
    text: str,
    icon: Optional[str] = None,
    color: str = ft.Colors.PRIMARY,
    variant: str = "filled"  # "filled", "outlined"
) -> ft.Container:
    """
    Create a modern information chip.

    Features:
    - Rounded pill design
    - Icon support
    - Multiple color variants
    - Proper accessibility
    """

    chip_controls = []

    if icon:
        chip_controls.append(
            ft.Icon(
                icon,
                size=16,
                color=ft.Colors.ON_PRIMARY if variant == "filled" else color
            )
        )
        chip_controls.append(ft.Container(width=6))

    chip_controls.append(
        ft.Text(
            text,
            size=12,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_PRIMARY if variant == "filled" else color,
            style=ft.TextThemeStyle.LABEL_MEDIUM
        )
    )

    return ft.Container(
        content=ft.Row(
            controls=chip_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True
        ),
        padding=ft.Padding(12, 6, 12, 6),
        bgcolor=color if variant == "filled" else ft.Colors.with_opacity(0.1, color),
        border=ft.border.all(1, color) if variant == "outlined" else None,
        border_radius=ft.BorderRadius(16, 16, 16, 16),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )


def create_loading_overlay(message: str = "Loading...") -> ft.Container:
    """
    Create a modern loading overlay with blur effect.

    Features:
    - Semi-transparent backdrop
    - Centered loading indicator
    - Custom message support
    - Smooth fade animations
    """
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=48, height=48, stroke_width=4),
            ft.Container(height=16),
            ft.Text(
                message,
                size=16,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ON_SURFACE,
                text_align=ft.TextAlign.CENTER,
                style=ft.TextThemeStyle.BODY_LARGE
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=200,
        height=120,
    bgcolor=ft.Colors.with_opacity(0.92, ft.Colors.SURFACE),
        border_radius=ft.BorderRadius(20, 20, 20, 20),
        padding=ft.Padding(24, 24, 24, 24),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.14, ft.Colors.SHADOW),
            offset=ft.Offset(0, 8),
        ),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    )


# ==============================================================================
# PHASE 2: INTERACTIVE FEEDBACK & ANIMATIONS - Enhanced UI Guide Implementation
# ==============================================================================

def create_interactive_button(text: str, icon: str, on_click: Callable, button_type: str = "primary") -> ft.Container:
    """
    Enhanced button components with hover effects using Flet's built-in animation system.

    Features:
    - Consistent color schemes for primary, secondary, danger states
    - Smooth hover animations using Flet's Animation system
    - Icon + text layout with proper spacing
    - Built-in hover effect through bgcolor animation
    """
    colors = {
        "primary": {"bg": ft.Colors.PRIMARY, "hover": ft.Colors.PRIMARY_CONTAINER},
        "secondary": {"bg": ft.Colors.SURFACE, "hover": ft.Colors.SECONDARY_CONTAINER},
        "danger": {"bg": ft.Colors.ERROR, "hover": ft.Colors.ERROR_CONTAINER}
    }

    def handle_hover(e):
        """Handle hover state changes for interactive feedback."""
        if hasattr(e.control, 'data'):
            if e.data == "true":
                e.control.bgcolor = e.control.data["hover_bg"]
            else:
                e.control.bgcolor = e.control.data["original_bg"]
            e.control.update()

    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=16),
            ft.Text(text, weight=ft.FontWeight.W_500)
        ], tight=True, spacing=8),
        bgcolor=colors[button_type]["bg"],
        padding=ft.Padding(16, 12, 16, 12),
        border_radius=8,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        on_click=on_click,
        on_hover=handle_hover,
        data={"original_bg": colors[button_type]["bg"], "hover_bg": colors[button_type]["hover"]}
    )


def create_interactive_table_row(cells: List[ft.Control], on_click: Optional[Callable] = None) -> ft.Container:
    """
    Enhanced table rows with hover effects using Flet's built-in animation system.

    Features:
    - Smooth hover transitions
    - Proper spacing and padding
    - Built-in click handling
    - Accessibility support with hover feedback
    """

    def handle_hover(e):
        """Handle row hover state for visual feedback."""
        if e.data == "true":
            e.control.bgcolor = ft.Colors.SURFACE
        else:
            e.control.bgcolor = ft.Colors.TRANSPARENT
        e.control.update()

    return ft.Container(
        content=ft.Row(cells, spacing=20),
        padding=ft.Padding(16, 12, 16, 12),
        animate=ft.Animation(120),
        on_click=on_click,
        border_radius=4,
        on_hover=handle_hover
    )


# ==============================================================================
# PHASE 3: ENHANCED STATUS INDICATORS - Modern Status Chips with Icons
# ==============================================================================

def create_status_chip(status: str, size: str = "medium") -> ft.Container:
    """
    Enhanced status indicators with icons, shadows, and vibrant theme colors.

    Features:
    - Comprehensive status configuration with appropriate icons
    - Size variants (small, medium, large)
    - Enhanced shadows for depth
    - Vibrant brand colors from theme system
    - Smooth transitions with improved animation
    - Consistent visual language across the app
    """
    # Use Material 3 theme colors
    try:
        status_config = {
            "Connected": {"color": ft.Colors.TERTIARY, "icon": ft.Icons.CHECK_CIRCLE},
            "Registered": {"color": ft.Colors.PRIMARY, "icon": ft.Icons.VERIFIED},
            "Error": {"color": ft.Colors.ERROR, "icon": ft.Icons.ERROR},
            "Offline": {"color": ft.Colors.GREY, "icon": ft.Icons.CIRCLE_OUTLINED},
            "Uploading": {"color": ft.Colors.SECONDARY, "icon": ft.Icons.UPLOAD},
            "Failed": {"color": ft.Colors.ERROR, "icon": ft.Icons.ERROR_OUTLINE},
            "Queued": {"color": ft.Colors.OUTLINE, "icon": ft.Icons.SCHEDULE},
            "Complete": {"color": ft.Colors.TERTIARY, "icon": ft.Icons.CHECK_CIRCLE_OUTLINE},
            "Processing": {"color": ft.Colors.PRIMARY, "icon": ft.Icons.AUTORENEW},
            "Pending": {"color": ft.Colors.SECONDARY, "icon": ft.Icons.PENDING},
            "Active": {"color": ft.Colors.TERTIARY, "icon": ft.Icons.PLAY_CIRCLE},
            "Inactive": {"color": ft.Colors.GREY_600, "icon": ft.Icons.PAUSE_CIRCLE},
        }
    except ImportError:
        # Fallback colors if theme not available
        status_config = {
            "Connected": {"color": ft.Colors.GREEN, "icon": ft.Icons.CHECK_CIRCLE},
            "Registered": {"color": ft.Colors.BLUE, "icon": ft.Icons.VERIFIED},
            "Error": {"color": ft.Colors.RED, "icon": ft.Icons.ERROR},
            "Offline": {"color": ft.Colors.GREY, "icon": ft.Icons.CIRCLE_OUTLINED},
            "Uploading": {"color": ft.Colors.ORANGE, "icon": ft.Icons.UPLOAD},
            "Failed": {"color": ft.Colors.RED, "icon": ft.Icons.ERROR_OUTLINE},
            "Queued": {"color": ft.Colors.BLUE_GREY, "icon": ft.Icons.SCHEDULE},
            "Complete": {"color": ft.Colors.GREEN, "icon": ft.Icons.CHECK_CIRCLE_OUTLINE},
            "Processing": {"color": ft.Colors.BLUE, "icon": ft.Icons.AUTORENEW},
            "Pending": {"color": ft.Colors.ORANGE, "icon": ft.Icons.PENDING},
            "Active": {"color": ft.Colors.GREEN, "icon": ft.Icons.PLAY_CIRCLE},
            "Inactive": {"color": ft.Colors.GREY_600, "icon": ft.Icons.PAUSE_CIRCLE},
        }

    config = status_config.get(status, {"color": ft.Colors.GREY, "icon": ft.Icons.HELP})
    sizes = {"small": 10, "medium": 12, "large": 14}
    icon_sizes = {"small": 14, "medium": 16, "large": 18}
    paddings = {"small": ft.Padding(8, 4, 8, 4), "medium": ft.Padding(12, 6, 12, 6), "large": ft.Padding(16, 8, 16, 8)}

    # Enhanced shadow for depth using Material 3 theme
    try:
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            offset=ft.Offset(0, 2),
            color=ft.Colors.with_opacity(0.2, ft.Colors.SHADOW)
        )
    except ImportError:
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            offset=ft.Offset(0, 2),
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK)
        )

    return ft.Container(
        content=ft.Row([
            ft.Icon(
                config["icon"],
                size=icon_sizes[size],
                color=ft.Colors.WHITE
            ),
            ft.Text(
                status,
                size=sizes[size],
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD
            )
        ], spacing=6, tight=True),
        bgcolor=config["color"],
        border_radius=16,
        padding=paddings[size],
        shadow=shadow,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)  # Smoother animation
    )


# ==============================================================================
# PHASE 4: RESPONSIVE LAYOUT ENHANCEMENTS - Dashboard & Metric Cards
# ==============================================================================

def create_dashboard_layout(clients_count: int, transfer_count: int, storage_used: str, uptime: str) -> ft.ResponsiveRow:
    """
    Enhanced dashboard cards with responsive design using Flet's ResponsiveRow.

    Features:
    - Responsive sizing: sm=12, md=6, lg=3 (stack on mobile, 2x2 on tablet, 4x1 on desktop)
    - Consistent metric card styling
    - Proper spacing and alignment
    - Professional color-coded icons
    """
    return ft.ResponsiveRow([
        # Server status cards with responsive breakpoints
        ft.Column([
            create_enhanced_metric_card("Active Clients", clients_count, ft.Icons.PEOPLE, ft.Colors.BLUE)
        ], col={"sm": 12, "md": 6, "lg": 3}),

        ft.Column([
            create_enhanced_metric_card("Total Transfers", transfer_count, ft.Icons.SWAP_HORIZ, ft.Colors.GREEN)
        ], col={"sm": 12, "md": 6, "lg": 3}),

        ft.Column([
            create_enhanced_metric_card("Storage Used", storage_used, ft.Icons.STORAGE, ft.Colors.PURPLE)
        ], col={"sm": 12, "md": 6, "lg": 3}),

        ft.Column([
            create_enhanced_metric_card("Server Uptime", uptime, ft.Icons.TIMER, ft.Colors.ORANGE)
        ], col={"sm": 12, "md": 6, "lg": 3})
    ], spacing=16)


def create_enhanced_metric_card(title: str, value, icon: str, accent_color: str) -> ft.Container:
    """
    Enhanced metric cards with sophisticated styling and premium visual design.

    Features:
    - Color-coded icons for quick recognition
    - Enhanced Material 3 styling with sophisticated shadows
    - Modern typography hierarchy and spacing
    - Smooth hover animations with premium effects
    - Consistent padding and elevation using theme system
    """
    # Enhanced shadow for depth using Material 3 theme
    try:
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            offset=ft.Offset(0, 4),
            color=ft.Colors.with_opacity(0.15, ft.Colors.SHADOW)
        )
        # Use Material 3 surface color
        bg_color = ft.Colors.SURFACE
    except ImportError:
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            offset=ft.Offset(0, 4),
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK)
        )
        bg_color = ft.Colors.SURFACE

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=28, color=ft.Colors.WHITE),
                    bgcolor=accent_color,
                    border_radius=12,
                    padding=ft.Padding(8, 8, 8, 8)
                ),
                ft.Text(title, style=ft.TextThemeStyle.LABEL_LARGE, weight=ft.FontWeight.W500)
            ], spacing=12, alignment=ft.MainAxisAlignment.START),
            ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color=accent_color)
        ], spacing=12),
        bgcolor=bg_color,
        border_radius=16,  # Enhanced border radius
        padding=24,  # Enhanced padding
        shadow=shadow,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)  # Smoother animation
    )


# ==============================================================================
# PHASE 5: FILE TYPE ICONS & VISUAL ENHANCEMENT - File Management UI
# ==============================================================================

def get_file_type_icon(filename: str) -> str:
    """
    File type icon mapping using Flet's built-in Icons for comprehensive file type recognition.

    Features:
    - Comprehensive file type coverage
    - Semantic icon selection for easy recognition
    - Fallback icon for unknown file types
    - Consistent visual language
    """
    file_icons = {
        # Document files
        '.pdf': ft.Icons.PICTURE_AS_PDF,
        '.doc': ft.Icons.DESCRIPTION, '.docx': ft.Icons.DESCRIPTION,
        '.txt': ft.Icons.TEXT_SNIPPET,
        '.rtf': ft.Icons.DESCRIPTION,
        '.odt': ft.Icons.DESCRIPTION,

        # Spreadsheet files
        '.xls': ft.Icons.TABLE_CHART, '.xlsx': ft.Icons.TABLE_CHART,
        '.csv': ft.Icons.TABLE_CHART,
        '.ods': ft.Icons.TABLE_CHART,

        # Presentation files
        '.ppt': ft.Icons.SLIDESHOW, '.pptx': ft.Icons.SLIDESHOW,
        '.odp': ft.Icons.SLIDESHOW,

        # Image files
        '.jpg': ft.Icons.IMAGE, '.jpeg': ft.Icons.IMAGE, '.png': ft.Icons.IMAGE,
        '.gif': ft.Icons.IMAGE, '.bmp': ft.Icons.IMAGE, '.svg': ft.Icons.IMAGE,
        '.webp': ft.Icons.IMAGE, '.tiff': ft.Icons.IMAGE,

        # Video files
        '.mp4': ft.Icons.VIDEO_FILE, '.avi': ft.Icons.VIDEO_FILE,
        '.mov': ft.Icons.VIDEO_FILE, '.mkv': ft.Icons.VIDEO_FILE,
        '.wmv': ft.Icons.VIDEO_FILE, '.flv': ft.Icons.VIDEO_FILE,
        '.webm': ft.Icons.VIDEO_FILE,

        # Audio files
        '.mp3': ft.Icons.AUDIO_FILE, '.wav': ft.Icons.AUDIO_FILE,
        '.flac': ft.Icons.AUDIO_FILE, '.aac': ft.Icons.AUDIO_FILE,
        '.ogg': ft.Icons.AUDIO_FILE,

        # Archive files
        '.zip': ft.Icons.FOLDER_ZIP, '.rar': ft.Icons.FOLDER_ZIP,
        '.7z': ft.Icons.FOLDER_ZIP, '.tar': ft.Icons.FOLDER_ZIP,
        '.gz': ft.Icons.FOLDER_ZIP,

        # Code files
        '.py': ft.Icons.CODE, '.js': ft.Icons.CODE, '.html': ft.Icons.CODE,
        '.css': ft.Icons.CODE, '.cpp': ft.Icons.CODE, '.java': ft.Icons.CODE,
        '.php': ft.Icons.CODE, '.json': ft.Icons.CODE, '.xml': ft.Icons.CODE,

        # System files
        '.exe': ft.Icons.SETTINGS_APPLICATIONS,
        '.msi': ft.Icons.SETTINGS_APPLICATIONS,
        '.deb': ft.Icons.SETTINGS_APPLICATIONS,
        '.dmg': ft.Icons.SETTINGS_APPLICATIONS,
    }

    extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    return file_icons.get(extension, ft.Icons.INSERT_DRIVE_FILE)


def create_file_row(file_info: Dict[str, Any]) -> ft.Container:
    """
    Enhanced file list row with file type icons, status indicators, and actions.

    Features:
    - File type recognition with appropriate icons
    - Integrated status chip display
    - Action buttons for file operations
    - Hover effects for interactive feedback
    - Professional spacing and alignment

    Args:
        file_info: Dictionary with keys: 'name', 'status', 'size', etc.
    """

    def handle_hover(e):
        """Handle file row hover state for visual feedback."""
        if e.data == "true":
            e.control.bgcolor = ft.Colors.SURFACE
        else:
            e.control.bgcolor = ft.Colors.TRANSPARENT
        e.control.update()

    return ft.Container(
        content=ft.Row([
            ft.Icon(get_file_type_icon(file_info["name"]), size=20),
            ft.Text(file_info["name"], expand=True),
            create_status_chip(file_info["status"], "small"),
            ft.IconButton(ft.Icons.MORE_VERT, tooltip="Actions")
        ], spacing=12),
        padding=ft.Padding(12, 8, 12, 8),
        animate=ft.Animation(120),
        on_hover=handle_hover
    )


# ==============================================================================
# TABLE ENHANCEMENT UTILITIES - Premium Desktop Styling Support
# ==============================================================================

def get_premium_table_styling() -> Dict[str, Any]:
    """
    Return sophisticated styling configurations for premium DataTable appearance.

    Returns a dictionary with consistent styling options for DataTables across
    the application, leveraging Material 3 theme system colors and effects.
    """
    try:
        return {
            "heading_row_color": ft.Colors.with_opacity(0.06, ft.Colors.SURFACE),
            "border_color": ft.Colors.OUTLINE,
            "border_width": 1,
            "border_radius": 20,
            "column_spacing_desktop": 55,
            "column_spacing_tablet": 45,
            "column_spacing_mobile": 35,
            "data_row_min_height": 70,
            "heading_row_height": 65,
            "shadow": ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                offset=ft.Offset(0, 4),
                color=ft.Colors.with_opacity(0.12, ft.Colors.SHADOW)
            ),
            "data_row_hover_color": ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
            "divider_color": ft.Colors.with_opacity(0.14, ft.Colors.OUTLINE),
            "header_text_color": ft.Colors.ON_SURFACE,
            "cell_text_size": 14,
            "header_text_weight": ft.FontWeight.BOLD
        }
    except ImportError:
        # Fallback styling if theme not available
        return {
            "heading_row_color": ft.Colors.BLUE_50,
            "border_color": ft.Colors.BLUE_300,
            "border_width": 2,
            "border_radius": 20,
            "column_spacing_desktop": 55,
            "column_spacing_tablet": 45,
            "column_spacing_mobile": 35,
            "data_row_min_height": 70,
            "heading_row_height": 65,
            "shadow": ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                offset=ft.Offset(0, 6),
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK)
            ),
            "data_row_hover_color": ft.Colors.with_opacity(0.08, ft.Colors.BLUE),
            "divider_color": ft.Colors.with_opacity(0.2, ft.Colors.BLUE),
            "header_text_color": ft.Colors.BLUE_800,
            "cell_text_size": 14,
            "header_text_weight": ft.FontWeight.BOLD
        }


def apply_advanced_table_effects(data_table: ft.DataTable, container_elevation: str = "elevated") -> ft.Container:
    """
    Apply consistent premium styling effects to any DataTable component.

    Args:
        data_table: The DataTable component to enhance
        container_elevation: Shadow elevation level from theme system

    Returns:
        ft.Container: Enhanced table container with sophisticated styling
    """
    styling = get_premium_table_styling()

    # Apply styling to the DataTable
    data_table.heading_row_color = styling["heading_row_color"]
    data_table.border = ft.border.all(styling["border_width"], styling["border_color"])
    data_table.border_radius = styling["border_radius"]
    data_table.column_spacing = styling["column_spacing_desktop"]
    data_table.data_row_min_height = styling["data_row_min_height"]
    data_table.heading_row_height = styling["heading_row_height"]
    data_table.data_row_color = {
        ft.ControlState.HOVERED: styling["data_row_hover_color"],
        ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT
    }
    data_table.horizontal_lines = ft.BorderSide(1, styling["divider_color"])

    # Ensure table expands and allow horizontal scrolling to avoid overflow
    data_table.expand = True
    scrollable = ft.Container(
        content=data_table,
        expand=True,
        alignment=ft.alignment.top_left,
        scroll=ft.ScrollMode.AUTO
    )

    # Wrap in enhanced container
    return create_modern_card(
        content=scrollable,
        elevation=container_elevation,
        padding=32,
        return_type="container"
    )


def create_enhanced_table_header(
    title: str,
    search_placeholder: str = "Search...",
    action_buttons: Optional[List[ft.Control]] = None
) -> ft.Container:
    """
    Create a sophisticated table header with search and action controls.

    Args:
        title: Header title text
        search_placeholder: Placeholder text for search field
        action_buttons: Optional list of action button controls

    Returns:
        ft.Container: Enhanced header container with premium styling
    """
    try:
        primary_color = ft.Colors.PRIMARY
        secondary_color = ft.Colors.SECONDARY
    except ImportError:
        primary_color = ft.Colors.BLUE_600
        secondary_color = ft.Colors.PURPLE_600

    header_controls = [
        ft.Text(
            title,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=primary_color
        ),
        ft.Container(expand=True),  # Spacer
    ]

    # Add search field
    search_field = ft.TextField(
        hint_text=search_placeholder,
        prefix_icon=ft.Icons.SEARCH,
        width=300,
    border_color=ft.Colors.OUTLINE,
    focused_border_color=primary_color
    )
    header_controls.append(search_field)

    # Add action buttons if provided
    if action_buttons:
        header_controls.append(ft.Container(width=16))  # Spacing
        action_row = ft.Row(action_buttons, spacing=12)
        header_controls.append(action_row)

    return create_modern_card(
        content=ft.Row(header_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        elevation="soft",
        padding=32,
        return_type="container"
    )
