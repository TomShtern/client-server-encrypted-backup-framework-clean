#!/usr/bin/env python3
"""
Modern UI Components for FletV2
Enhanced 2025 design polish with sophisticated visual elements and accessibility.

Provides polished, reusable components following 2025 UI/UX best practices.
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any


def create_modern_card(
    title: str, 
    content: ft.Control, 
    icon: Optional[str] = None,
    actions: Optional[List[ft.Control]] = None,
    elevation: int = 3,
    width: Optional[float] = None,
    animate_on_hover: bool = True
) -> ft.Card:
    """
    Create a modern card with 2025 design standards.
    
    Features:
    - Rounded corners (20px)
    - Subtle shadows with hover animation
    - Modern typography
    - Optional icon and actions
    - Accessibility support
    """
    
    # Title row with optional icon
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
    
    title_controls.append(
        ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE,
            style=ft.TextThemeStyle.TITLE_MEDIUM
        )
    )
    
    # Build card content
    card_content = [
        ft.Row(
            controls=title_controls,
            alignment=ft.MainAxisAlignment.START
        ),
        ft.Container(height=16),  # Spacing
        content
    ]
    
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
    
    card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=card_content,
                spacing=0,
                tight=True
            ),
            padding=ft.Padding(24, 20, 24, 20),
            border_radius=ft.BorderRadius(20, 20, 20, 20)
        ),
        elevation=elevation,
        margin=ft.Margin(8, 8, 8, 8),
        width=width
    )
    
    # Add hover animation
    if animate_on_hover:
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
                color=ft.Colors.ON_SURFACE_VARIANT,
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
    size: str = "medium",  # "small", "medium", "large"
    disabled: bool = False,
    loading: bool = False
) -> ft.Control:
    """
    Create a modern button with 2025 design standards.
    
    Features:
    - Multiple variants (filled, outlined, elevated, text)
    - Size variants with proper padding
    - Loading states
    - Icon support
    - Proper accessibility
    """
    
    # Size configurations
    size_configs = {
        "small": {"padding": ft.Padding(16, 8, 16, 8), "text_size": 14, "icon_size": 18},
        "medium": {"padding": ft.Padding(24, 12, 24, 12), "text_size": 16, "icon_size": 20},
        "large": {"padding": ft.Padding(32, 16, 32, 16), "text_size": 18, "icon_size": 22}
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
    
    # Create button based on variant
    button_style = ft.ButtonStyle(
        padding=config["padding"],
        shape=ft.RoundedRectangleBorder(radius=16),
        animation_duration=200
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
            color=ft.Colors.ON_SURFACE_VARIANT,
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
        border=ft.Border.all(1, color) if variant == "outlined" else None,
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
        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.SURFACE),
        border_radius=ft.BorderRadius(20, 20, 20, 20),
        padding=ft.Padding(24, 24, 24, 24),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
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
        "secondary": {"bg": ft.Colors.SURFACE_VARIANT, "hover": ft.Colors.SECONDARY_CONTAINER},
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
        animate=ft.animation.Animation(150, ft.AnimationCurve.EASE_OUT),
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
            e.control.bgcolor = ft.Colors.SURFACE_VARIANT
        else:
            e.control.bgcolor = ft.Colors.TRANSPARENT
        e.control.update()
    
    return ft.Container(
        content=ft.Row(cells, spacing=20),
        padding=ft.Padding(16, 12, 16, 12),
        animate=ft.animation.Animation(120),
        on_click=on_click,
        border_radius=4,
        on_hover=handle_hover
    )


# ==============================================================================
# PHASE 3: ENHANCED STATUS INDICATORS - Modern Status Chips with Icons
# ==============================================================================

def create_status_chip(status: str, size: str = "medium") -> ft.Container:
    """
    Enhanced status indicators with icons and better contrast using Material 3 design.
    
    Features:
    - Comprehensive status configuration with appropriate icons
    - Size variants (small, medium, large)
    - High contrast design for accessibility
    - Smooth transitions with animation
    - Consistent visual language across the app
    """
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
                weight=ft.FontWeight.W_500
            )
        ], spacing=4, tight=True),
        bgcolor=config["color"],
        border_radius=16,
        padding=ft.Padding(12, 6, 12, 6),
        animate=ft.Animation(150)
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
    Enhanced metric cards with modern styling and better visual hierarchy.
    
    Features:
    - Color-coded icons for quick recognition
    - Modern Material 3 styling with rounded corners
    - Proper spacing and typography hierarchy
    - Smooth hover animations
    - Consistent padding and elevation
    """
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, size=24, color=accent_color),
                ft.Text(title, style=ft.TextThemeStyle.LABEL_MEDIUM)
            ], spacing=8),
            ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD)
        ], spacing=8),
        bgcolor=ft.Colors.SURFACE_VARIANT,
        border_radius=12,
        padding=20,
        animate=ft.animation.Animation(150)
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
            e.control.bgcolor = ft.Colors.SURFACE_VARIANT
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
        animate=ft.animation.Animation(120),
        on_hover=handle_hover
    )
