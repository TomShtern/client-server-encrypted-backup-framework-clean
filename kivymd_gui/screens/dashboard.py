# -*- coding: utf-8 -*-
"""
Enhanced Dashboard screen for the KivyMD Encrypted Backup Server GUI

Comprehensive server monitoring dashboard with Material Design 3 styling featuring:
- 6-card grid layout with server status, client stats, transfer monitoring
- Live performance charts with real-time CPU/Memory tracking  
- Professional control panel with colorful action buttons
- Activity logging with proper text constraints and scrolling
"""

from __future__ import annotations
import sys
import os
from pathlib import Path

# Ensure UTF-8 solution is available
try:
    import Shared.utils.utf8_solution
except ImportError:
    # Try adding project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    try:
        import Shared.utils.utf8_solution
    except ImportError:
        pass  # Continue without UTF-8 solution

import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import psutil

# Import deque separately to avoid potential import issues
try:
    from collections import deque
    DEQUE_AVAILABLE = True
except ImportError:
    DEQUE_AVAILABLE = False
    # Fallback implementation
    class deque:
        def __init__(self, iterable=None, maxlen=None):
            self.data = list(iterable) if iterable else []
            self.maxlen = maxlen
        
        def append(self, item):
            self.data.append(item)
            if self.maxlen and len(self.data) > self.maxlen:
                self.data.pop(0)
        
        def __len__(self):
            return len(self.data)
        
        def __iter__(self):
            return iter(self.data)

# Critical KivyMD imports (required)
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd_gui.components.md3_label import MD3Label, create_md3_label
from kivymd.uix.button import MDButton, MDIconButton
from kivymd_gui.components.md3_button import create_md3_icon_button
from kivymd.uix.button import MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.divider import MDDivider
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.list import MDList, MDListItem
from kivymd.uix.list import MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.badge import MDBadge
from kivymd.uix.tooltip import MDTooltip

# Critical Kivy imports (required)
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation

# Optional KivyMD components
try:
    from kivymd.uix.spinner import MDSpinner
    SPINNER_AVAILABLE = True
except ImportError:
    SPINNER_AVAILABLE = False

# Optional matplotlib imports
try:
    from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Matplotlib not available: {e}")
    MATPLOTLIB_AVAILABLE = False

KIVYMD_AVAILABLE = True

# Local imports
if KIVYMD_AVAILABLE:
    from ..utils.server_integration import ServerStatus, ServerIntegrationBridge
    from ..models.data_models import ServerStats


# Loading and Empty State Components
class MDSkeletonLoader(MDCard):
    """
    Material Design 3 skeleton loader with shimmer effect
    
    Creates placeholder content that mimics the actual layout while loading,
    providing visual continuity and reducing perceived loading time.
    """
    
    def __init__(self, skeleton_type="text", height=None, **kwargs):
        super().__init__(**kwargs)
        
        self.skeleton_type = skeleton_type
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceVariantColor
        self.elevation = 0
        self.radius = [dp(8)]
        self.size_hint_y = None
        self.height = height or dp(24)
        
        # Shimmer animation properties
        self._shimmer_opacity = 0.3
        self._animation = None
        
        self._start_shimmer_animation()
    
    def _start_shimmer_animation(self):
        """Start subtle shimmer animation following MD3 motion principles"""
        try:
            # MD3 emphasized easing with gentle shimmer
            shimmer_anim = Animation(
                opacity=0.6, 
                duration=1.2,
                t='out_cubic'
            ) + Animation(
                opacity=0.3, 
                duration=1.2,
                t='in_cubic'
            )
            shimmer_anim.repeat = True
            shimmer_anim.start(self)
            self._animation = shimmer_anim
        except Exception as e:
            print(f"[ERROR] Shimmer animation failed: {e}")
    
    def stop_shimmer(self):
        """Stop shimmer animation when content loads"""
        try:
            if self._animation:
                self._animation.stop(self)
                self._animation = None
        except Exception as e:
            print(f"[ERROR] Stop shimmer failed: {e}")


class MDLoadingCard(MDCard):
    """
    Enhanced loading card with skeleton screen and progress indicators
    
    Features:
    - Skeleton placeholders that match actual content layout
    - Progressive loading with smooth transitions
    - Error state handling with retry mechanisms
    - Accessibility support for screen readers
    """
    
    def __init__(self, card_title="Loading...", loading_type="skeleton", **kwargs):
        super().__init__(card_type="elevated", **kwargs)
        
        self.card_title = card_title
        self.loading_type = loading_type  # "skeleton", "spinner", "progress"
        self.current_state = "loading"  # "loading", "loaded", "error", "empty"
        
        # Animation references
        self._fade_animation = None
        self._skeleton_elements = []
        
        self._build_loading_ui()
    
    def _build_loading_ui(self):
        """Build loading state UI with skeleton elements"""
        self.main_layout = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(16),
            padding=[dp(20), dp(16), dp(20), dp(16)]
        )
        
        # Header with loading indicator
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Title skeleton or text
        self.title_element = MD3Label(
            text=self.card_title,
            theme_text_color="Secondary",
            font_style="Title",
            adaptive_height=True
        )
        header.add_widget(self.title_element)
        
        # Loading indicator based on type
        if self.loading_type == "spinner":
            spinner = MDCircularProgressIndicator(
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                line_width=dp(3)
            )
            header.add_widget(spinner)
        
        self.main_layout.add_widget(header)
        self.main_layout.add_widget(MDDivider())
        
        # Content area with skeletons
        self.content_area = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16)
        )
        
        self._create_skeleton_content()
        self.main_layout.add_widget(self.content_area)
        self.add_widget(self.main_layout)
    
    def _create_skeleton_content(self):
        """Create skeleton placeholder content"""
        try:
            # Create various skeleton elements
            skeletons = [
                MDSkeletonLoader(skeleton_type="text", height=dp(16), size_hint_x=0.8),
                MDSkeletonLoader(skeleton_type="text", height=dp(16), size_hint_x=0.6),
                MDSkeletonLoader(skeleton_type="text", height=dp(24), size_hint_x=0.9),
                MDSkeletonLoader(skeleton_type="text", height=dp(16), size_hint_x=0.7)
            ]
            
            for skeleton in skeletons:
                self.content_area.add_widget(skeleton)
                self._skeleton_elements.append(skeleton)
                
        except Exception as e:
            print(f"[ERROR] Skeleton creation failed: {e}")
    
    def transition_to_content(self, content_widget, duration=0.25):
        """
        Smooth transition from loading state to actual content
        
        Uses MD3 motion principles for seamless user experience
        """
        try:
            if self.current_state != "loading":
                return
            
            # Stop skeleton animations
            for skeleton in self._skeleton_elements:
                skeleton.stop_shimmer()
            
            # Create fade transition
            fade_out = Animation(opacity=0, duration=duration/2, t='out_cubic')
            
            def on_fade_complete(animation, widget):
                # Replace content
                self.clear_widgets()
                self.add_widget(content_widget)
                
                # Fade in new content
                content_widget.opacity = 0
                fade_in = Animation(opacity=1, duration=duration/2, t='in_cubic')
                fade_in.start(content_widget)
                
                self.current_state = "loaded"
            
            fade_out.bind(on_complete=on_fade_complete)
            fade_out.start(self)
            
        except Exception as e:
            print(f"[ERROR] Content transition failed: {e}")
    
    def show_error_state(self, error_message="Failed to load", retry_callback=None):
        """
        Display error state with retry mechanism
        """
        try:
            self.current_state = "error"
            
            # Stop skeleton animations
            for skeleton in self._skeleton_elements:
                skeleton.stop_shimmer()
            
            # Clear and rebuild for error state
            self.content_area.clear_widgets()
            
            # Error icon and message
            error_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(16),
                adaptive_height=True,
                size_hint_y=None
            )
            
            error_icon = create_md3_icon_button(
                icon="alert-circle",
                tone="error",
                disabled=True
            )
            error_layout.add_widget(error_icon)
            
            error_label = MD3Label(
                text=error_message,
                theme_text_color="Error",
                font_style="Body",
                    halign="center",
                adaptive_height=True
            )
            error_layout.add_widget(error_label)
            
            # Retry button if callback provided
            if retry_callback:
                retry_button = MDButton(
                    MDButtonText(text="Retry"),
                    style="outlined",
                    theme_line_color="Custom",
                    line_color=self.theme_cls.primaryColor,
                    size_hint=(None, None),
                    size=(dp(120), dp(40)),
                    pos_hint={"center_x": 0.5}
                )
                retry_button.bind(on_release=lambda x: retry_callback())
                error_layout.add_widget(retry_button)
            
            self.content_area.add_widget(error_layout)
            
        except Exception as e:
            print(f"[ERROR] Error state display failed: {e}")


class MDEmptyState(MDCard):
    """
    Material Design 3 empty state component with contextual guidance
    
    Provides users with clear messaging and actionable next steps
    when no data is available, following MD3 empty state patterns.
    """
    
    def __init__(self, 
                 title="No data available",
                 description="",
                 icon="inbox",
                 action_text=None,
                 action_callback=None,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.theme_bg_color = "Custom"
        self.md_bg_color = self.theme_cls.surfaceColor
        self.elevation = 0
        self.adaptive_height = True
        self.size_hint_y = None
        
        self._build_empty_state(
            title=title,
            description=description,
            icon=icon,
            action_text=action_text,
            action_callback=action_callback
        )
    
    def _build_empty_state(self, title, description, icon, action_text, action_callback):
        """Build empty state UI with proper MD3 spacing and hierarchy"""
        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(24),  # 3 units on 8dp grid
            padding=[dp(32), dp(40), dp(32), dp(40)],  # Generous padding for empty states
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Icon with proper MD3 sizing
        icon_widget = create_md3_icon_button(
            icon=icon,
            tone="secondary",
            size=(dp(64), dp(64)),  # Large icon for empty states
            disabled=True,  # Decorative only
            pos_hint={"center_x": 0.5}
        )
        layout.add_widget(icon_widget)
        
        # Title with proper MD3 typography
        title_label = MD3Label(
            text=title,
            font_style="Headline",
            # MD3 Headline Medium for empty state titles
            theme_text_color="Primary",
            halign="center",
            adaptive_height=True
        )
        layout.add_widget(title_label)
        
        # Description if provided
        if description:
            desc_label = MD3Label(
                text=description,
                font_style="Body",
                # MD3 Body Large for descriptions
                theme_text_color="Secondary",
                halign="center",
                adaptive_height=True
                # REMOVED: text_size=(None, None) - This was causing vertical text rendering
                # MD3Label handles proper text wrapping automatically
            )
            layout.add_widget(desc_label)
        
        # Action button if provided
        if action_text and action_callback:
            action_button = MDButton(
                MDButtonText(text=action_text),
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=self.theme_cls.primaryColor,
                size_hint=(None, None),
                size=(dp(160), dp(40)),
                pos_hint={"center_x": 0.5}
            )
            action_button.bind(on_release=lambda x: action_callback())
            layout.add_widget(action_button)
        
        self.add_widget(layout)
    
    def update_content(self, title=None, description=None, icon=None):
        """Update empty state content dynamically"""
        try:
            # Find and update children
            layout = self.children[0] if self.children else None
            if not layout:
                return
            
            for child in layout.children:
                if hasattr(child, 'icon') and icon:
                    child.icon = icon
                elif hasattr(child, 'text'):
                    if child.font_style == "Headline" and title:
                        child.text = title
                    elif child.font_style == "Body" and description:
                        child.text = description
                        
        except Exception as e:
            print(f"[ERROR] Empty state update failed: {e}")


class ResponsiveCard(MDCard):
    """
    Enhanced Material Design 3 card with responsive design support
    
    Features:
    - Proper elevation and surface treatment following MD3 specifications
    - Responsive padding and sizing based on screen breakpoints
    - Adaptive touch targets for mobile, tablet, and desktop
    - Smart constraint management for optimal layout behavior
    """
    
    def __init__(self, card_type="elevated", **kwargs):
        super().__init__(**kwargs)
        
        # Store card type for responsive adjustments
        self.card_type = card_type
        
        # MD3 Card Types: filled, elevated, outlined
        self._apply_card_type_styling(card_type)
        
        # Create content layout that child classes expect
        self._content_layout = MDBoxLayout(orientation="vertical")
        self.add_widget(self._content_layout)
        
        # MD3 specifications with responsive defaults
        self.radius = [dp(12)]  # MD3 standard card radius (responsive adjustments applied later)
        self.padding = [dp(24), dp(20), dp(24), dp(20)]  # MD3 card padding (responsive adjustments applied later)
        self.adaptive_height = True
        self.size_hint_y = None
        self.minimum_height = dp(120)  # Ensure minimum touch target (responsive adjustments applied later)
        
        # Responsive state tracking
        self._current_breakpoint = None
        self._responsive_constraints_applied = False
    
    def _apply_card_type_styling(self, card_type):
        """Apply MD3 styling based on card type"""
        if card_type == "elevated":
            self.theme_bg_color = "Custom"
            self.md_bg_color = self.theme_cls.surfaceContainerHighColor
            self.elevation = 3  # MD3 elevated card elevation
            self.shadow_radius = dp(8)
            self.shadow_offset = (0, dp(2))
        elif card_type == "filled":
            self.theme_bg_color = "Custom" 
            self.md_bg_color = self.theme_cls.surfaceContainerHighestColor
            self.elevation = 0
        else:  # outlined
            self.theme_bg_color = "Custom"
            self.md_bg_color = self.theme_cls.surfaceColor
            self.elevation = 0
            # TODO: Add outline property when available in KivyMD 2.0.x
    
    def apply_responsive_constraints(self, available_width, cols):
        """
        Apply responsive constraints for optimal layout behavior
        
        This method is called by the dashboard's responsive layout system
        to ensure cards adapt properly to different screen sizes and layouts
        """
        try:
            # Determine current breakpoint
            MOBILE_MAX = dp(768)
            TABLET_MAX = dp(1200)
            
            if available_width <= MOBILE_MAX:
                breakpoint = "mobile"
            elif available_width <= TABLET_MAX:
                breakpoint = "tablet"
            else:
                breakpoint = "desktop"
            
            # Only update if breakpoint changed to avoid unnecessary layout updates
            if self._current_breakpoint != breakpoint:
                self._current_breakpoint = breakpoint
                self._apply_breakpoint_constraints(breakpoint, cols, available_width)
                self._responsive_constraints_applied = True
            
            # Apply text rendering protection to all child MD3Labels
            self._protect_child_labels_text_rendering()
        
        except Exception as e:
            print(f"[ERROR] Failed to apply responsive constraints to card: {e}")
    
    def _protect_child_labels_text_rendering(self):
        """Protect all child MD3Label instances from text rendering issues"""
        try:
            def protect_labels_recursive(widget):
                # Protect MD3Label instances
                if hasattr(widget, '__class__') and 'MD3Label' in widget.__class__.__name__:
                    self._protect_label_text_rendering(widget)
                
                # Recursively protect children
                if hasattr(widget, 'children'):
                    for child in widget.children:
                        protect_labels_recursive(child)
            
            # Start from content layout
            if hasattr(self, '_content_layout'):
                protect_labels_recursive(self._content_layout)
        except Exception as e:
            print(f"[ERROR] Failed to protect child labels: {e}")
    
    def _protect_label_text_rendering(self, label):
        """FINAL LAYOUT VALIDATION: Protect a label from text rendering issues with optimized spacing"""
        try:
            # FINAL VALIDATION: Ensure label has optimized width for text rendering
            if hasattr(label, 'width') and label.width < dp(120):
                label.size_hint_x = None
                label.width = dp(120)  # Optimized width for better space utilization
            
            # FINAL VALIDATION: Ensure text_size is properly set for text wrapping 
            if hasattr(label, 'text_size'):
                # Use the label's width for text wrapping to prevent overlapping
                if hasattr(label, 'width') and label.width > dp(80):
                    label.text_size = (label.width, None)
                else:
                    label.text_size = (dp(120), None)  # Optimized text size
                
            # FINAL VALIDATION: Ensure proper text alignment
            if not hasattr(label, 'halign') or not label.halign:
                label.halign = 'left'
                
            # FINAL VALIDATION: Ensure adaptive height to prevent text overlapping
            if not hasattr(label, 'adaptive_height') or not label.adaptive_height:
                label.adaptive_height = True
                
            # FINAL VALIDATION: Apply minimum height to prevent text stacking
            if hasattr(label, 'height') and label.height < dp(20):
                label.size_hint_y = None
                label.height = dp(20)  # Optimized minimum height
                
            # FINAL VALIDATION: Ensure adequate padding for text rendering
            if hasattr(label, 'padding') and not label.padding:
                label.padding = [dp(3), dp(2), dp(3), dp(2)]  # Optimized padding
                
        except Exception as e:
            print(f"[ERROR] Failed to protect label: {e}")
    
    def add_widget(self, widget, index=0):
        """Override add_widget to ensure proper text rendering for labels"""
        # Apply text rendering protection to MD3Label children
        if hasattr(widget, '__class__') and 'MD3Label' in widget.__class__.__name__:
            self._protect_label_text_rendering(widget)
        
        super().add_widget(widget, index)
    
    def _apply_breakpoint_constraints(self, breakpoint, cols, available_width):
        """Apply breakpoint-specific constraints to the card"""
        if breakpoint == "mobile":
            # Mobile: Optimize for single-hand operation
            self.padding = [dp(20), dp(16), dp(20), dp(16)]  # Reduced padding
            self.minimum_height = dp(140)  # Larger touch targets
            self.radius = [dp(16)]  # Slightly larger radius for easier touch
            
        elif breakpoint == "tablet":
            # Tablet: Balanced for two-hand operation
            self.padding = [dp(22), dp(18), dp(22), dp(18)]  # Moderate padding
            self.minimum_height = dp(130)  # Standard touch targets
            self.radius = [dp(14)]  # Standard MD3 radius
            
        else:  # desktop
            # Desktop: Optimal for precision input
            self.padding = [dp(24), dp(20), dp(24), dp(20)]  # Full MD3 padding
            self.minimum_height = dp(120)  # Compact for data density
            self.radius = [dp(12)]  # Standard MD3 radius
        
        # Ensure proper size constraints
        self.size_hint_x = None if cols > 1 else 1
        self.adaptive_height = True
        
        # FINAL SPACE OPTIMIZATION: Apply balanced width constraints for optimal space utilization
        min_card_width = dp(380)  # Optimized minimum width for better space utilization
        if cols == 1 and available_width > min_card_width:
            self.size_hint_x = None
            self.width = max(min_card_width, min(dp(520), available_width - dp(40)))  # Optimized max width
        elif cols > 1:
            # For multi-column layouts, ensure adequate width for text rendering
            self.size_hint_x = None
            current_width = getattr(self, 'width', 0)
            if current_width < min_card_width:
                self.width = min_card_width
        
        # Force card layout update to apply new constraints
        self._trigger_layout()


class ServerStatusCard(ResponsiveCard):
    """Enhanced server status card with comprehensive monitoring and MD3 design"""
    
    def __init__(self, **kwargs):
        super().__init__(card_type="elevated", **kwargs)
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(20),  # Increased spacing to prevent text overlap
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Header with status indicator - standard Material Design spacing
        header = MDBoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(40),  # Standard header height
            spacing=dp(16),  # Standard MD3 spacing (2 units)
            adaptive_height=True
        )
        
        title = MD3Label(
            text="Server Status",
            theme_text_color="Primary",
            font_style="Title",  # MD3 Title Large
            adaptive_height=True
        )
        header.add_widget(title)
        
        # Simplified status chip container
        status_container = MDBoxLayout(
            size_hint_x=None, 
            width=dp(100),  # Standard width
            pos_hint={'center_y': 0.5}
        )
        
        # Simplified MD3 chip container
        self.status_chip = MDCard(
            size_hint=(None, None),
            size=(dp(90), dp(28)),  # Slightly smaller for better fit
            radius=[dp(14)],
            elevation=0,
            theme_bg_color="Custom",
            md_bg_color=self.theme_cls.errorColor,
            pos_hint={'center_x': 0.5}
        )
        
        # Simplified chip content - remove conflicting constraints
        chip_content = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(4),
            size_hint=(1, 1)
        )
        
        # Status indicator dot with proper positioning
        self.status_dot = create_md3_icon_button(
            icon="circle",
            tone="error",
            size=(dp(6), dp(6)),  # Smaller dot for better proportions
            disabled=True,  # Decorative only
            pos_hint={'center_y': 0.5}  # Center dot vertically
        )
        
        # Simplified status text - remove conflicting constraints  
        self.status_text = MD3Label(
            text="OFFLINE",
            font_style="Label",
            theme_text_color="Custom",
            text_color=self.theme_cls.onErrorColor,
            halign="center",
            adaptive_height=True
        )
        
        chip_content.add_widget(self.status_dot)
        chip_content.add_widget(self.status_text)
        self.status_chip.add_widget(chip_content)
        status_container.add_widget(self.status_chip)
        header.add_widget(status_container)
        
        self._content_layout.add_widget(header)
        
        # MD3 Divider with proper spacing
        self._content_layout.add_widget(MDDivider(height=dp(1)))
        
        # Status information with standard MD3 spacing
        info_container = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(16),  # Standard MD3 spacing
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Status details - remove conflicting height constraints
        self.status_label = MD3Label(
            text="Status: Stopped", 
            font_style="Body", 
            theme_text_color="Primary",
            adaptive_height=True
        )
        self.address_label = MD3Label(
            text="Address: N/A", 
            font_style="Body", 
            theme_text_color="Secondary",
            adaptive_height=True
        )
        self.uptime_label = MD3Label(
            text="Uptime: 00:00:00", 
            font_style="Body", 
            theme_text_color="Secondary",
            adaptive_height=True
        )
        
        info_container.add_widget(self.status_label)
        info_container.add_widget(self.address_label) 
        info_container.add_widget(self.uptime_label)
        
        self._content_layout.add_widget(info_container)
    
    def update_status(self, status: ServerStatus):
        """Update server status display with MD3 color semantics"""
        try:
            if status.running:
                # STRUCTURAL FIX: Update chip for online status with proper text centering
                self.status_text.text = "ONLINE"
                self.status_chip.md_bg_color = self.theme_cls.primaryColor
                self.status_text.text_color = self.theme_cls.onPrimaryColor
                self.status_dot.icon_color = self.theme_cls.onPrimaryColor
                # Text centering handled by halign property
                
                # Add subtle success animation
                try:
                    from kivy.animation import Animation
                    success_anim = Animation(opacity=0.7, duration=0.15) + Animation(opacity=1.0, duration=0.15)
                    success_anim.start(self.status_chip)
                except Exception:
                    pass  # Graceful fallback if animation fails
                self.status_label.text = "Status: Running"
                self.status_label.theme_text_color = "Primary"
                self.address_label.text = f"Address: {status.host}:{status.port}"
            else:
                # STRUCTURAL FIX: Update chip for offline status with proper text centering
                self.status_text.text = "OFFLINE"
                self.status_chip.md_bg_color = self.theme_cls.errorColor
                self.status_text.text_color = self.theme_cls.onErrorColor
                self.status_dot.icon_color = self.theme_cls.onErrorColor
                # Text centering handled by halign property
                self.status_label.text = "Status: Stopped"
                self.status_label.theme_text_color = "Error"
                self.address_label.text = "Address: N/A"
            
            # Format uptime with enhanced display
            if status.uptime_seconds > 0:
                hours = int(status.uptime_seconds // 3600)
                minutes = int((status.uptime_seconds % 3600) // 60)
                seconds = int(status.uptime_seconds % 60)
                self.uptime_label.text = f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
                self.uptime_label.theme_text_color = "Primary"
            else:
                self.uptime_label.text = "Uptime: 00:00:00"
                self.uptime_label.theme_text_color = "Secondary"
                
        except Exception as e:
            print(f"[ERROR] Failed to update server status: {e}")


class ClientStatsCard(ResponsiveCard):
    """Material Design 3 client statistics card with proper data visualization"""
    
    def __init__(self, **kwargs):
        super().__init__(card_type="filled", **kwargs)
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(16))
        
        # Header with icon and title
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # 2 units on 8dp grid
            size_hint_y=None,
            height=dp(40)
        )
        
        # Icon for visual hierarchy
        icon = create_md3_icon_button(
            icon="account-group",
            tone="primary",
            size=(dp(32), dp(32))
        )
        header.add_widget(icon)
        
        title = MD3Label(
            text="Client Statistics",
            theme_text_color="Primary",
            font_style="Title",
            adaptive_height=True
        )
        header.add_widget(title)
        
        self._content_layout.add_widget(header)
        self._content_layout.add_widget(MDDivider(height=dp(1)))
        
        # Stats with enhanced MD3 data presentation and spacing
        stats_container = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(24),  # Increased spacing to 3 units (24dp) to prevent overlap
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Connected clients with emphasis and better spacing
        connected_row = MDBoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(48),  # Keep height at dp(48)
            spacing=dp(16),  # Increased horizontal spacing from dp(12) to dp(16)
            adaptive_height=True
        )
        self.connected_value = MD3Label(
            text="0",
            font_style="Display",
            # Large number display
            theme_text_color="Primary",
            size_hint_x=None,
            width=dp(80),  # Increased width to accommodate Display font style
            adaptive_height=True
        )
        connected_label = MD3Label(
            text="Connected Clients",
            font_style="Body",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        connected_row.add_widget(self.connected_value)
        connected_row.add_widget(connected_label)
        
        # Total clients with enhanced spacing
        total_row = MDBoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(44),  # Keep height at dp(44)
            spacing=dp(16),  # Increased horizontal spacing from dp(12) to dp(16)
            adaptive_height=True
        )
        self.total_value = MD3Label(
            text="0",
            font_style="Headline",
            theme_text_color="Primary", 
            size_hint_x=None,
            width=dp(80),  # Increased width to accommodate Headline font style
            adaptive_height=True
        )
        total_label = MD3Label(
            text="Total Registered",
            font_style="Body", 
            theme_text_color="Secondary",
            adaptive_height=True
        )
        total_row.add_widget(self.total_value)
        total_row.add_widget(total_label)
        
        # Active transfers with enhanced spacing
        transfers_row = MDBoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height=dp(44),  # Keep height at dp(44)
            spacing=dp(16),  # Increased horizontal spacing from dp(12) to dp(16)
            adaptive_height=True
        )
        self.transfers_value = MD3Label(
            text="0",
            font_style="Headline",
            theme_text_color="Primary",
            size_hint_x=None,
            width=dp(80),  # Increased width to accommodate Headline font style
            adaptive_height=True
        )
        transfers_label = MD3Label(
            text="Active Transfers",
            font_style="Body",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        transfers_row.add_widget(self.transfers_value)
        transfers_row.add_widget(transfers_label)
        
        stats_container.add_widget(connected_row)
        stats_container.add_widget(total_row)
        stats_container.add_widget(transfers_row)
        
        self._content_layout.add_widget(stats_container)
    
    def update_stats(self, connected: int = 0, total: int = 0, active_transfers: int = 0):
        """Update client statistics with MD3 visual feedback"""
        try:
            self.connected_value.text = str(connected)
            self.total_value.text = str(total)
            self.transfers_value.text = str(active_transfers)
            
            # Apply color coding for visual feedback
            if connected > 0:
                self.connected_value.theme_text_color = "Primary"
            else:
                self.connected_value.theme_text_color = "Secondary"
                
            if active_transfers > 0:
                self.transfers_value.theme_text_color = "Primary" 
            else:
                self.transfers_value.theme_text_color = "Secondary"
                
        except Exception as e:
            print(f"[ERROR] Failed to update client stats: {e}")


class TransferStatsCard(ResponsiveCard):
    """Material Design 3 transfer statistics card with enhanced data presentation"""
    
    def __init__(self, **kwargs):
        super().__init__(card_type="filled", **kwargs)
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(16))
        
        # Header with icon for visual hierarchy
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # 2 units on 8dp grid
            size_hint_y=None,
            height=dp(40)
        )
        
        icon = create_md3_icon_button(
            icon="transfer",
            tone="secondary",
            size=(dp(32), dp(32))
        )
        header.add_widget(icon)
        
        title = MD3Label(
            text="Transfer Statistics",
            theme_text_color="Primary",
            font_style="Title",
            adaptive_height=True
        )
        header.add_widget(title)
        
        self._content_layout.add_widget(header)
        self._content_layout.add_widget(MDDivider(height=dp(1)))
        
        # Transfer metrics with prominent display
        metrics_container = MDBoxLayout(orientation="vertical", spacing=dp(16))  # 2 units on 8dp grid
        
        # Total transferred - primary metric
        total_row = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(56))
        self.total_value = MD3Label(
            text="0",
            font_style="Display",
            # Large number for primary metric
            theme_text_color="Primary",
            halign="left",
            adaptive_height=True
        )
        total_unit = MD3Label(
            text="MB Transferred",
            font_style="Body",
            theme_text_color="Secondary",
            halign="left",
            adaptive_height=True
        )
        total_row.add_widget(self.total_value)
        total_row.add_widget(total_unit)
        
        # Transfer rate - secondary metric
        rate_row = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(48))
        self.rate_value = MD3Label(
            text="0.0",
            font_style="Headline",
            theme_text_color="Primary",
            halign="left",
            adaptive_height=True
        )
        rate_unit = MD3Label(
            text="KB/s Current Rate",
            font_style="Body",
            theme_text_color="Secondary",
            halign="left",
            adaptive_height=True
        )
        rate_row.add_widget(self.rate_value)
        rate_row.add_widget(rate_unit)
        
        metrics_container.add_widget(total_row)
        metrics_container.add_widget(rate_row)
        
        self._content_layout.add_widget(metrics_container)
    
    def update_stats(self, total_mb: float = 0, rate_kbs: float = 0):
        """Update transfer statistics with enhanced formatting"""
        try:
            # Format total with appropriate units
            if total_mb >= 1024:
                self.total_value.text = f"{total_mb/1024:.1f}"
                # Update unit label if needed - could be dynamic
            else:
                self.total_value.text = f"{total_mb:.1f}"
            
            # Format rate with visual feedback
            self.rate_value.text = f"{rate_kbs:.1f}"
            
            # Apply color coding for active transfers
            if rate_kbs > 0:
                self.rate_value.theme_text_color = "Primary"
            else:
                self.rate_value.theme_text_color = "Secondary"
                
        except Exception as e:
            print(f"[ERROR] Failed to update transfer stats: {e}")


class MaintenanceCard(ResponsiveCard):
    """Material Design 3 maintenance card with system health indicators"""
    
    def __init__(self, **kwargs):
        super().__init__(card_type="outlined", **kwargs)
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(16))
        
        # Header with maintenance icon
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(16),  # 2 units on 8dp grid
            size_hint_y=None,
            height=dp(40)
        )
        
        icon = create_md3_icon_button(
            icon="wrench",
            tone="tertiary",
            size=(dp(32), dp(32))
        )
        header.add_widget(icon)
        
        title = MD3Label(
            text="System Maintenance",
            theme_text_color="Primary",
            font_style="Title",
            adaptive_height=True
        )
        header.add_widget(title)
        
        self._content_layout.add_widget(header)
        self._content_layout.add_widget(MDDivider(height=dp(1)))
        
        # Maintenance metrics
        maintenance_container = MDBoxLayout(orientation="vertical", spacing=dp(16))  # 2 units on 8dp grid
        
        # Last cleanup time
        cleanup_row = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(40))
        cleanup_label = MD3Label(
            text="Last System Cleanup",
            font_style="Body",
            theme_text_color="Primary",
            adaptive_height=True
        )
        self.cleanup_value = MD3Label(
            text="Never",
            font_style="Body",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        cleanup_row.add_widget(cleanup_label)
        cleanup_row.add_widget(self.cleanup_value)
        
        # Files cleaned count
        files_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36), spacing=dp(8))
        self.files_count = MD3Label(
            text="0",
            font_style="Headline",
            theme_text_color="Primary",
            size_hint_x=None,
            width=dp(80),  # Increased width to accommodate Headline font style
            adaptive_height=True
        )
        files_label = MD3Label(
            text="Files Cleaned Total",
            font_style="Body",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        files_row.add_widget(self.files_count)
        files_row.add_widget(files_label)
        
        maintenance_container.add_widget(cleanup_row)
        maintenance_container.add_widget(files_row)
        
        self._content_layout.add_widget(maintenance_container)
    
    def update_maintenance(self, last_cleanup: str = "Never", files_cleaned: int = 0):
        """Update maintenance information with visual feedback"""
        try:
            self.cleanup_value.text = last_cleanup
            self.files_count.text = str(files_cleaned)
            
            # Visual feedback for maintenance status
            if last_cleanup == "Never":
                self.cleanup_value.theme_text_color = "Error"
            else:
                self.cleanup_value.theme_text_color = "Secondary"
                
            if files_cleaned > 0:
                self.files_count.theme_text_color = "Primary"
            else:
                self.files_count.theme_text_color = "Secondary"
                
        except Exception as e:
            print(f"[ERROR] Failed to update maintenance info: {e}")


class ControlPanelCard(ResponsiveCard):
    """Material Design 3 control panel with proper button hierarchy"""
    
    def __init__(self, dashboard_screen, **kwargs):
        super().__init__(card_type="elevated", **kwargs)
        self.dashboard_screen = dashboard_screen
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(
            orientation="vertical", 
            spacing=dp(20),  # Increased spacing to prevent text overlap
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Header with proper MD3 typography and spacing
        title = MD3Label(
            text="Control Panel",
            theme_text_color="Primary",
            font_style="Title",  # MD3 Title Large
            size_hint_y=None,
            height=dp(36),  # Keep height at dp(36)
            adaptive_height=True,
            padding=[dp(8), dp(6), dp(8), dp(6)]  # Increased padding from [0, dp(4), 0, dp(4)]
        )
        layout.add_widget(title)
        layout.add_widget(MDDivider(height=dp(1)))
        
        # Primary actions - following MD3 button hierarchy with enhanced spacing
        primary_actions = MDBoxLayout(
            orientation="horizontal", 
            spacing=dp(20),  # Keep spacing at dp(20) - already optimal
            size_hint_y=None,
            height=dp(60),  # Increased height from dp(56) to dp(60) for better spacing
            adaptive_height=True
        )
        
        # Start button - Primary Filled (highest emphasis)
        self.start_button = MDButton(
            MDButtonText(text="Start Server"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=self.theme_cls.primaryColor,
            size_hint_y=None,
            height=dp(40),  # MD3 button height
            radius=[dp(20)]  # MD3 fully rounded buttons
        )
        self.start_button.bind(on_release=self.dashboard_screen.start_server)
        
        # Stop button - Error Filled (destructive action)
        self.stop_button = MDButton(
            MDButtonText(text="Stop Server"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=self.theme_cls.errorColor,
            size_hint_y=None,
            height=dp(40),
            radius=[dp(20)]
        )
        self.stop_button.bind(on_release=self.dashboard_screen.stop_server)
        
        primary_actions.add_widget(self.start_button)
        primary_actions.add_widget(self.stop_button)
        layout.add_widget(primary_actions)
        
        # Secondary actions - using outlined buttons with enhanced spacing
        secondary_actions = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),  # Keep spacing at dp(20) - already optimal
            size_hint_y=None,
            height=dp(60),  # Increased height from dp(56) to dp(60) for better spacing
            adaptive_height=True
        )
        
        # Restart button - Secondary Outlined
        self.restart_button = MDButton(
            MDButtonText(text="Restart"),
            style="outlined",
            theme_line_color="Custom",
            line_color=self.theme_cls.primaryColor,
            size_hint_y=None,
            height=dp(40),
            radius=[dp(20)]
        )
        self.restart_button.bind(on_release=self.dashboard_screen.restart_server)
        
        # Backup button - Tertiary Outlined  
        self.backup_button = MDButton(
            MDButtonText(text="Backup Database"),
            style="outlined",
            theme_line_color="Custom", 
            line_color=self.theme_cls.secondaryColor,
            size_hint_y=None,
            height=dp(40),
            radius=[dp(20)]
        )
        self.backup_button.bind(on_release=self.on_backup_db)
        
        secondary_actions.add_widget(self.restart_button)
        secondary_actions.add_widget(self.backup_button)
        layout.add_widget(secondary_actions)
        
        self._content_layout.add_widget(layout)
    
    def on_backup_db(self, *args):
        """Handle backup database button"""
        print("[INFO] Backup DB requested")
        # TODO: Implement database backup functionality
    
    def update_button_states(self, server_running: bool):
        """Update button states with MD3 visual feedback"""
        try:
            # Update enabled/disabled states
            self.start_button.disabled = server_running
            self.stop_button.disabled = not server_running  
            self.restart_button.disabled = not server_running
            
            # Update visual styling based on state
            if server_running:
                # Server running - emphasize stop/restart
                self.stop_button.md_bg_color = self.theme_cls.errorColor
                self.restart_button.line_color = self.theme_cls.primaryColor
                # Dim start button
                self.start_button.md_bg_color = self.theme_cls.surfaceVariantColor
            else:
                # Server stopped - emphasize start
                self.start_button.md_bg_color = self.theme_cls.primaryColor
                # Dim stop/restart buttons
                self.stop_button.md_bg_color = self.theme_cls.surfaceVariantColor
                self.restart_button.line_color = self.theme_cls.outlineVariantColor
                
        except Exception as e:
            print(f"[ERROR] Failed to update button states: {e}")


class PerformanceChartCard(ResponsiveCard):
    """Live system performance chart with CPU and Memory monitoring"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Performance data
        self.cpu_data = deque(maxlen=60)  # Last 60 readings
        self.memory_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        
        self._build_ui()
        
        # Schedule performance updates
        Clock.schedule_interval(self.update_performance_data, 1.0)
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(16))
        
        # Header
        title = MD3Label(
            text="Live System Performance",
            theme_text_color="Primary",
            font_style="Headline",
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(title)
        layout.add_widget(MDDivider())
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure
            self.fig, self.ax = plt.subplots(figsize=(8, 4))
            self.fig.patch.set_facecolor('#2E2E2E')  # Dark background
            self.ax.set_facecolor('#2E2E2E')
            
            # Initialize empty lines
            self.cpu_line, = self.ax.plot([], [], 'g-', label='CPU %', linewidth=2)
            self.memory_line, = self.ax.plot([], [], 'b-', label='Memory %', linewidth=2)
            
            self.ax.set_xlim(0, 60)
            self.ax.set_ylim(0, 100)
            self.ax.set_xlabel('Time (seconds ago)', color='white')
            self.ax.set_ylabel('Usage (%)', color='white')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            self.ax.tick_params(colors='white')
            
            # Add to layout
            canvas = FigureCanvasKivyAgg(self.fig)
            layout.add_widget(canvas)
        else:
            # Fallback if matplotlib not available
            fallback_label = MD3Label(
                text="Performance chart unavailable\n(matplotlib not installed)",
                theme_text_color="Secondary",
                halign="center"
            )
            layout.add_widget(fallback_label)
        
        self._content_layout.add_widget(layout)
    
    def update_performance_data(self, dt):
        """Update performance data and chart"""
        try:
            if not MATPLOTLIB_AVAILABLE:
                return
            
            # Get current system stats
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Add to data queues
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory_percent)
            self.time_data.append(len(self.cpu_data))
            
            # Update chart
            if len(self.cpu_data) > 1:
                x_data = list(range(len(self.cpu_data)))
                self.cpu_line.set_data(x_data, list(self.cpu_data))
                self.memory_line.set_data(x_data, list(self.memory_data))
                
                # Adjust x-axis
                self.ax.set_xlim(max(0, len(self.cpu_data) - 60), max(60, len(self.cpu_data)))
                
                # Redraw
                self.fig.canvas.draw()
                
        except Exception as e:
            print(f"[ERROR] Failed to update performance data: {e}")


class ActivityLogCard(ResponsiveCard):
    """Enhanced activity log with proper text constraints"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(16))
        
        # Header with clear button
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
        
        title = MD3Label(
            text="Activity Log",
            theme_text_color="Primary",
            font_style="Headline",
            adaptive_height=True
        )
        header.add_widget(title)
        
        clear_button = create_md3_icon_button(
            icon="delete",
            tone="secondary",
            on_release=self.clear_log,
            size=(dp(32), dp(32))
        )
        header.add_widget(clear_button)
        
        self._content_layout.add_widget(header)
        self._content_layout.add_widget(MDDivider())
        
        # Scrollable log
        scroll = MDScrollView()
        self.log_list = MDList()
        scroll.add_widget(self.log_list)
        layout.add_widget(scroll)
        
        self._content_layout.add_widget(layout)
        
        # Add initial message
        self.add_log_entry("System", "Enhanced dashboard initialized")
    
    def add_log_entry(self, source: str, message: str, level: str = "INFO"):
        """Add log entry with proper text constraints"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Create properly constrained list item
            item = MDListItem(
                size_hint_y=None,
                height=dp(56),
                spacing=dp(8)
            )
            
            # Headline with source and timestamp
            headline = MDListItemHeadlineText(
                text=f"[{timestamp}] {source}",
                adaptive_width=True,
                shorten=True,
                max_lines=1
            )
            
            # Supporting text with message
            supporting = MDListItemSupportingText(
                text=message,
                adaptive_width=True,
                shorten=True,
                max_lines=1
            )
            
            # Apply color coding
            if level == "ERROR":
                headline.text_color = supporting.text_color = self.theme_cls.errorColor
            elif level == "WARNING":
                headline.text_color = supporting.text_color = self.theme_cls.tertiaryColor
            else:
                headline.theme_text_color = "Primary"
                supporting.theme_text_color = "Secondary"
            
            item.add_widget(headline)
            item.add_widget(supporting)
            
            self.log_list.add_widget(item, index=0)
            
            # Keep only last 100 entries
            if len(self.log_list.children) > 100:
                self.log_list.remove_widget(self.log_list.children[-1])
                
        except Exception as e:
            print(f"[ERROR] Failed to add log entry: {e}")
    
    def clear_log(self, *args):
        """Clear activity log"""
        try:
            self.log_list.clear_widgets()
            self.add_log_entry("System", "Activity log cleared")
        except Exception as e:
            print(f"[ERROR] Failed to clear log: {e}")


class DashboardScreen(MDScreen):
    """
    Enhanced dashboard with comprehensive 6-card layout
    
    Features:
    - Responsive 3-column grid layout
    - Real-time performance monitoring with charts
    - Professional control panel with colorful buttons
    - Enhanced activity logging with proper constraints
    - Material Design 3 styling throughout
    """
    
    def __init__(self, server_bridge: Optional[ServerIntegrationBridge] = None,
                 config: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        
        self.server_bridge = server_bridge
        self.config = config or {}
        
        # Card references
        self.server_status_card: Optional[ServerStatusCard] = None
        self.client_stats_card: Optional[ClientStatsCard] = None
        self.transfer_stats_card: Optional[TransferStatsCard] = None
        self.control_panel_card: Optional[ControlPanelCard] = None
        self.maintenance_card: Optional[MaintenanceCard] = None
        self.performance_card: Optional[PerformanceChartCard] = None
        self.activity_card: Optional[ActivityLogCard] = None
        
        # State tracking
        self.last_status: Optional[ServerStatus] = None
        self.update_event = None
        
        self.build_ui()
        Clock.schedule_once(self.initial_load, 0.5)
    
    def build_ui(self):
        """Build responsive dashboard with adaptive layout structure"""
        try:
            # Create main responsive container
            self.main_container = self._create_main_container()
            
            # Build card sections with proper hierarchy
            self._build_primary_section()
            self._build_secondary_section() 
            self._build_analytics_section()
            
            # Add to screen
            self.add_widget(self.main_container)
            
        except Exception as e:
            print(f"[ERROR] Failed to build responsive dashboard: {e}")
            traceback.print_exc()
    
    def _create_main_container(self):
        """Create the main responsive scroll container"""
        scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(4),
            scroll_type=['bars']
        )
        
        # FINAL SPACE OPTIMIZATION: Main vertical layout with optimized spacing for better space utilization
        self.main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(32),  # Optimized spacing for better space utilization
            padding=[dp(20), dp(24), dp(20), dp(24)],  # Reduced padding for better space usage
            adaptive_height=True,
            size_hint_y=None
        )
        
        scroll.add_widget(self.main_layout)
        return scroll
    
    def _build_primary_section(self):
        """Build primary monitoring section with status and controls"""
        
        # Section header with proper MD3 typography and spacing
        primary_header = MD3Label(
            text="Server Overview",
            font_style="Display",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(48),
            size_hint_x=1
        )
        # Remove the width binding that was causing vertical text rendering
        # primary_header.bind(width=lambda *x: primary_header.setter('text_size')(primary_header, (primary_header.width, None)))
        self.main_layout.add_widget(primary_header)
        
        # Responsive card container for primary cards
        primary_container = self._create_card_container(
            cards_data=[
                ("server_status_card", ServerStatusCard),
                ("control_panel_card", lambda: ControlPanelCard(self))
            ],
            min_card_width=dp(340),
            max_cards_per_row=2,
            section_spacing=dp(24)  # Increased internal spacing from dp(16) to dp(24)
        )
        
        self.main_layout.add_widget(primary_container)
    
    def _build_secondary_section(self):
        """Build secondary statistics section"""
        # Section header with proper 8dp grid spacing
        self.main_layout.add_widget(MD3Label(size_hint_y=None, height=dp(24)))  # 3 units spacer
        
        secondary_header = MD3Label(
            text="System Statistics",
            font_style="Headline",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40)  # 5 units on 8dp grid
        )
        # Remove the width binding that was causing vertical text rendering
        # secondary_header.bind(width=lambda *x: secondary_header.setter('text_size')(secondary_header, (secondary_header.width, None)))
        self.main_layout.add_widget(secondary_header)
        
        # Stats cards container
        stats_container = self._create_card_container(
            cards_data=[
                ("client_stats_card", ClientStatsCard),
                ("transfer_stats_card", TransferStatsCard),
                ("maintenance_card", MaintenanceCard)
            ],
            min_card_width=dp(280),
            max_cards_per_row=3,
            section_spacing=dp(24)  # Increased internal spacing from dp(16) to dp(24)
        )
        
        self.main_layout.add_widget(stats_container)
    
    def _build_analytics_section(self):
        """Build analytics and monitoring section"""
        # Section header with proper 8dp grid spacing
        self.main_layout.add_widget(MD3Label(size_hint_y=None, height=dp(24)))  # 3 units spacer
        
        analytics_header = MD3Label(
            text="Live Monitoring",
            font_style="Headline",
            # MD3 Headline Large for subsections 
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40)  # 5 units on 8dp grid
            # REMOVED: padding=[0, 0, 0, dp(8)] - MDLabel doesn't support padding property
        )
        # Remove the width binding that was causing vertical text rendering
        # analytics_header.bind(width=lambda *x: analytics_header.setter('text_size')(analytics_header, (analytics_header.width, None)))
        self.main_layout.add_widget(analytics_header)
        
        # Analytics cards with larger heights
        analytics_container = self._create_card_container(
            cards_data=[
                ("performance_card", PerformanceChartCard),
                ("activity_card", ActivityLogCard)
            ],
            min_card_width=dp(400),
            max_cards_per_row=2,
            section_spacing=dp(24),  # Increased internal spacing from dp(16) to dp(24)
            card_height=dp(300)  # Optimized height for charts and logs
        )
        
        self.main_layout.add_widget(analytics_container)
    
    def _create_card_container(self, cards_data, min_card_width=None, 
                              max_cards_per_row=3, section_spacing=None, 
                              card_height=None):
        """
        Create sophisticated responsive card container with MD3 breakpoints
        
        Material Design 3 Breakpoint System:
        - Desktop (>1200px): 3-column layout for optimal data density
        - Tablet (768-1200px): 2-column layout with enhanced spacing
        - Mobile (<768px): Single column with optimized touch targets
        """
        # FINAL SPACE OPTIMIZATION: Set optimized defaults for better space utilization
        if min_card_width is None:
            min_card_width = dp(380)  # Optimized minimum width for better space utilization
        if section_spacing is None:
            section_spacing = dp(20)  # Optimized spacing for better space usage
        
        # MD3 Breakpoint detection with proper spacing calculations
        screen_width = Window.width
        available_width = screen_width - dp(48)  # Account for screen padding
        
        # Calculate columns using MD3 breakpoint system
        optimal_cols, card_spacing, container_padding = self._calculate_responsive_layout(
            available_width, min_card_width, max_cards_per_row, section_spacing
        )
        
        # Create responsive grid container with adaptive sizing
        container = MDGridLayout(
            cols=optimal_cols,
            spacing=card_spacing,
            adaptive_height=True,
            size_hint_y=None,
            row_default_height=card_height or dp(160),  # Reduced for better space utilization
            col_default_width=self._calculate_optimal_card_width(available_width, optimal_cols, card_spacing),
            padding=container_padding
        )
        
        # Store layout parameters for responsive updates
        container._layout_params = {
            'cards_data': cards_data,
            'min_card_width': min_card_width,
            'max_cards_per_row': max_cards_per_row,
            'section_spacing': section_spacing,
            'card_height': card_height
        }
        
        # Bind to window resize for smooth responsive behavior
        Window.bind(on_resize=lambda *args: self._update_container_layout_responsive(container))
        
        # Create and add cards with proper constraints
        for card_attr, card_class in cards_data:
            card = card_class()
            
            # Apply responsive card constraints
            self._apply_card_responsive_constraints(card, available_width, optimal_cols)
            
            # Apply enhanced card constraints for text rendering
            self._apply_enhanced_card_constraints(card, available_width, optimal_cols)
            
            setattr(self, card_attr, card)
            container.add_widget(card)
        
        # FINAL SPACE OPTIMIZATION: Calculate and set optimized container height
        rows_needed = (len(cards_data) + optimal_cols - 1) // optimal_cols
        total_height = (card_height or dp(160)) * rows_needed + card_spacing * (rows_needed - 1)
        container.height = total_height
        
        return container
    
    def _calculate_responsive_layout(self, available_width, min_card_width, max_cards_per_row, base_spacing):
        """
        Calculate responsive layout parameters using MD3 breakpoint system
        
        Returns:
            tuple: (optimal_cols, card_spacing, container_padding)
        """
        try:
            # MD3 Breakpoint thresholds (converted from CSS pixels to dp)
            MOBILE_MAX = dp(768)
            TABLET_MAX = dp(1200)
            
            # Determine breakpoint and adjust layout accordingly
            if available_width <= MOBILE_MAX:
                # Mobile: Single column with optimized spacing
                optimal_cols = 1
                card_spacing = dp(16)  # 2 units on 8dp grid
                container_padding = [dp(8), dp(16), dp(8), dp(16)]  # Reduced horizontal padding
                
            elif available_width <= TABLET_MAX:
                # Tablet: 2-column layout with enhanced spacing
                optimal_cols = min(2, max_cards_per_row)
                card_spacing = dp(20)  # 2.5 units on 8dp grid
                container_padding = [dp(16), dp(20), dp(16), dp(20)]  # Balanced padding
                
            else:  # desktop
                # Desktop: 3-column layout for optimal data density
                # Calculate optimal columns based on available space and constraints
                max_possible_cols = int(available_width // min_card_width)
                optimal_cols = min(max_cards_per_row, max(1, max_possible_cols))
                card_spacing = base_spacing  # Use provided spacing
                container_padding = [dp(24), dp(24), dp(24), dp(24)]  # Full padding
            
            # Ensure minimum column count
            optimal_cols = max(1, optimal_cols)
            
            return optimal_cols, card_spacing, container_padding
            
        except Exception as e:
            print(f"[ERROR] Responsive layout calculation failed: {e}")
            # Fallback to safe defaults
            return 1, dp(16), [dp(16), dp(16), dp(16), dp(16)]
    
    def _calculate_optimal_card_width(self, available_width, cols, spacing):
        """
        Calculate optimal card width based on available space and column count
        
        Ensures cards maintain proper aspect ratios and readability
        """
        try:
            # Account for spacing between cards and container padding
            total_spacing = spacing * (cols - 1)
            container_padding_horizontal = dp(48)  # Total left + right padding
            
            # Calculate width per card
            usable_width = available_width - total_spacing - container_padding_horizontal
            card_width = usable_width / cols
            
            # FINAL SPACE OPTIMIZATION: Enhanced constraints for optimal text rendering and space utilization
            min_width = dp(380)  # Optimized for better space utilization while maintaining text readability
            max_width = dp(520)  # Balanced max width for optimal space usage
            
            # Clamp to reasonable bounds with improved space utilization
            optimal_width = max(min_width, min(card_width, max_width))
            
            return optimal_width
            
        except Exception as e:
            print(f"[ERROR] Card width calculation failed: {e}")
            return dp(380)  # Safe fallback optimized for space utilization
    
    def _apply_card_responsive_constraints(self, card, available_width, cols):
        """
        Apply responsive constraints to individual cards for optimal layout
        
        Ensures touch targets remain accessible across all screen sizes
        Uses the card's built-in responsive system if available
        """
        try:
            # Use the card's built-in responsive system if it's a ResponsiveCard
            if hasattr(card, 'apply_responsive_constraints'):
                card.apply_responsive_constraints(available_width, cols)
            else:
                # Fallback for non-ResponsiveCard instances
                self._apply_legacy_card_constraints(card, available_width, cols)
            
        except Exception as e:
            print(f"[ERROR] Card constraint application failed: {e}")
    
    def _apply_enhanced_card_constraints(self, card, available_width, cols):
        """
        Apply enhanced constraints that prevent text rendering issues
        """
        try:
            # FINAL SPACE OPTIMIZATION: Ensure minimum width for proper text rendering with better space usage
            min_card_width = dp(380)  # Optimized minimum width for balanced text rendering and space utilization
            
            # Apply size constraints
            card.size_hint_x = None if cols > 1 else 1
            card.adaptive_height = True
            
            # Ensure adequate width for text rendering
            if cols == 1 and available_width > min_card_width:
                card.size_hint_x = None
                card.width = max(min_card_width, min(dp(520), available_width - dp(40)))
            elif cols > 1:
                # For multi-column layouts, ensure adequate width
                card.size_hint_x = None
                current_width = getattr(card, 'width', 0)
                if current_width < min_card_width:
                    card.width = min_card_width
                    
        except Exception as e:
            print(f"[ERROR] Enhanced card constraint application failed: {e}")

    def _apply_legacy_card_constraints(self, card, available_width, cols):
        """
        Legacy constraint application for non-ResponsiveCard instances
        
        Maintains compatibility with standard MDCard instances
        """
        try:
            # MD3 Breakpoint-specific card adjustments
            MOBILE_MAX = dp(768)
            TABLET_MAX = dp(1200)
            
            if available_width <= MOBILE_MAX:
                # Mobile: Optimize for single-hand operation
                if hasattr(card, 'padding'):
                    card.padding = [dp(20), dp(16), dp(20), dp(16)]
                if hasattr(card, 'minimum_height'):
                    card.minimum_height = dp(140)
                if hasattr(card, 'radius'):
                    card.radius = [dp(16)]
                    
            elif available_width <= TABLET_MAX:
                # Tablet: Balanced for two-hand operation
                if hasattr(card, 'padding'):
                    card.padding = [dp(22), dp(18), dp(22), dp(18)]
                if hasattr(card, 'minimum_height'):
                    card.minimum_height = dp(130)
                if hasattr(card, 'radius'):
                    card.radius = [dp(14)]
                    
            else:  # desktop
                # Desktop: Optimal for precision input
                if hasattr(card, 'padding'):
                    card.padding = [dp(24), dp(20), dp(24), dp(20)]
                if hasattr(card, 'minimum_height'):
                    card.minimum_height = dp(120)
                if hasattr(card, 'radius'):
                    card.radius = [dp(12)]
            
            # Ensure proper size constraints
            card.size_hint_x = None if cols > 1 else 1
            card.adaptive_height = True
            
            # FINAL SPACE OPTIMIZATION: Apply balanced width constraints for optimal space usage
            min_card_width = dp(380)  # Optimized minimum width for better space utilization
            if cols == 1 and available_width > min_card_width:
                card.size_hint_x = None
                card.width = max(min_card_width, min(dp(520), available_width - dp(40)))
            elif cols > 1:
                # For multi-column layouts, ensure adequate width
                card.size_hint_x = None
                current_width = getattr(card, 'width', 0)
                if current_width < min_card_width:
                    card.width = min_card_width
            
        except Exception as e:
            print(f"[ERROR] Legacy card constraint application failed: {e}")
    
    def _update_container_layout_responsive(self, container):
        """
        Enhanced responsive layout update with smooth transitions
        
        Handles window resize events with proper layout recalculation
        """
        try:
            if not hasattr(container, '_layout_params'):
                return
            
            params = container._layout_params
            available_width = Window.width - dp(48)
            
            # Recalculate layout using MD3 breakpoints
            optimal_cols, card_spacing, container_padding = self._calculate_responsive_layout(
                available_width, 
                params['min_card_width'], 
                params['max_cards_per_row'], 
                params['section_spacing']
            )
            
            # Update container properties smoothly
            container.cols = optimal_cols
            container.spacing = card_spacing
            container.padding = container_padding
            container.col_default_width = self._calculate_optimal_card_width(available_width, optimal_cols, card_spacing)
            
            # Update card constraints for all children
            for card in container.children:
                self._apply_card_responsive_constraints(card, available_width, optimal_cols)
            
            # FINAL SPACE OPTIMIZATION: Recalculate container height with optimized sizing
            rows_needed = (len(params['cards_data']) + optimal_cols - 1) // optimal_cols
            card_height = params['card_height'] or dp(160)
            total_height = card_height * rows_needed + card_spacing * (rows_needed - 1)
            container.height = total_height
            
            # Force layout update
            container._trigger_layout()
            
        except Exception as e:
            print(f"[ERROR] Responsive layout update failed: {e}")
    
    def _update_container_layout(self, container, cards_data, min_card_width, max_cards_per_row):
        """Legacy method - redirects to enhanced responsive layout"""
        try:
            self._update_container_layout_responsive(container)
        except Exception as e:
            print(f"[ERROR] Layout update failed: {e}")
    
    def get_responsive_layout_info(self):
        """
        Get current responsive layout information for debugging and testing
        
        Returns:
            dict: Current layout state including breakpoint, screen size, and card layout
        """
        try:
            screen_width = Window.width
            available_width = screen_width - dp(48)
            
            # Determine current breakpoint
            MOBILE_MAX = dp(768)
            TABLET_MAX = dp(1200)
            
            if available_width <= MOBILE_MAX:
                breakpoint = "mobile"
                expected_cols = 1
            elif available_width <= TABLET_MAX:
                breakpoint = "tablet" 
                expected_cols = 2
            else:
                breakpoint = "desktop"
                expected_cols = 3
            
            return {
                "screen_width": screen_width,
                "available_width": available_width,
                "breakpoint": breakpoint,
                "expected_columns": expected_cols,
                "mobile_threshold": MOBILE_MAX,
                "tablet_threshold": TABLET_MAX,
                "responsive_system_active": True
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get layout info: {e}")
            return {
                "error": str(e),
                "responsive_system_active": False
            }
    
    def force_responsive_layout_update(self):
        """
        Force a complete responsive layout update
        
        Useful for testing or recovering from layout issues
        """
        try:
            # Find all containers with layout parameters
            containers_updated = 0
            
            def find_containers(widget):
                nonlocal containers_updated
                if hasattr(widget, '_layout_params'):
                    self._update_container_layout_responsive(widget)
                    containers_updated += 1
                
                # Recursively check children
                if hasattr(widget, 'children'):
                    for child in widget.children:
                        find_containers(child)
            
            # Start search from main layout
            if hasattr(self, 'main_layout'):
                find_containers(self.main_layout)
            
            if self.activity_card:
                self.activity_card.add_log_entry(
                    "System", 
                    f"Forced layout update: {containers_updated} containers updated"
                )
            
            return containers_updated
            
        except Exception as e:
            print(f"[ERROR] Force layout update failed: {e}")
            if self.activity_card:
                self.activity_card.add_log_entry(
                    "System", 
                    f"Layout update failed: {str(e)}", 
                    "ERROR"
                )
            return 0
    
    def initial_load(self, dt):
        """Initial data loading and setup"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Loading comprehensive dashboard...")
            
            self.refresh_all_data()
            self.schedule_updates()
            
        except Exception as e:
            print(f"[ERROR] Initial load failed: {e}")
    
    def schedule_updates(self):
        """Schedule periodic updates"""
        try:
            self.stop_updates()
            update_interval = self.config.get("ui", {}).get("auto_refresh_interval", 2.0)
            self.update_event = Clock.schedule_interval(self.periodic_update, update_interval)
        except Exception as e:
            print(f"[ERROR] Failed to schedule updates: {e}")
    
    def stop_updates(self):
        """Stop periodic updates"""
        try:
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
        except Exception as e:
            print(f"[ERROR] Failed to stop updates: {e}")
    
    def periodic_update(self, dt):
        """Periodic data refresh"""
        try:
            if self.server_bridge:
                status = self.server_bridge.get_latest_status()
                if status:
                    self.update_server_status(status)
        except Exception as e:
            print(f"[ERROR] Periodic update failed: {e}")
    
    def refresh_all_data(self):
        """Refresh all dashboard data"""
        try:
            # Update client stats (mock data for now)
            if self.client_stats_card:
                self.client_stats_card.update_stats(connected=0, total=0, active_transfers=0)
            
            # Update transfer stats (mock data for now)
            if self.transfer_stats_card:
                self.transfer_stats_card.update_stats(total_mb=0, rate_kbs=0)
            
            # Update maintenance info (mock data for now)
            if self.maintenance_card:
                self.maintenance_card.update_maintenance(last_cleanup="Never", files_cleaned=0)
            
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Dashboard data refreshed")
                
        except Exception as e:
            print(f"[ERROR] Data refresh failed: {e}")
    
    def update_server_status(self, status: ServerStatus):
        """Update server status across all cards"""
        try:
            if self.server_status_card:
                self.server_status_card.update_status(status)
            
            if self.control_panel_card:
                self.control_panel_card.update_button_states(status.running)
            
            # Log status changes
            if self.last_status is None or self.last_status.running != status.running:
                if self.activity_card:
                    msg = "Server started" if status.running else "Server stopped"
                    self.activity_card.add_log_entry("Server", msg)
            
            self.last_status = status
            
        except Exception as e:
            print(f"[ERROR] Status update failed: {e}")
    
    def start_server(self, *args):
        """Start the server"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Starting server...")
            
            if self.server_bridge:
                self.server_bridge.start_server_async()
                Clock.schedule_once(self.check_command_response, 2.0)
        except Exception as e:
            print(f"[ERROR] Start server failed: {e}")
    
    def stop_server(self, *args):
        """Stop the server"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Stopping server...")
            
            if self.server_bridge:
                self.server_bridge.stop_server_async()
                Clock.schedule_once(self.check_command_response, 2.0)
        except Exception as e:
            print(f"[ERROR] Stop server failed: {e}")
    
    def restart_server(self, *args):
        """Restart the server"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("User", "Restarting server...")
            
            if self.server_bridge:
                self.server_bridge.restart_server_async()
                Clock.schedule_once(self.check_command_response, 5.0)
        except Exception as e:
            print(f"[ERROR] Restart server failed: {e}")
    
    def check_command_response(self, dt):
        """Check server command response"""
        try:
            if self.server_bridge and self.activity_card:
                response = self.server_bridge.get_command_response()
                if response:
                    command = response.get('command', 'unknown')
                    success = response.get('success', False)
                    message = response.get('message', 'No message')
                    level = "INFO" if success else "ERROR"
                    self.activity_card.add_log_entry("Server", f"{command}: {message}", level)
        except Exception as e:
            print(f"[ERROR] Command response check failed: {e}")
    
    def on_enter(self):
        """Screen entered"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Enhanced dashboard entered")
            self.schedule_updates()
            self.refresh_all_data()
            
            # FINAL LAYOUT VALIDATION: Run comprehensive layout validation
            Clock.schedule_once(lambda dt: self.validate_final_layout(), 1.0)
            
            # Optional: Demonstrate micro-interactions (remove in production)
            # Clock.schedule_once(lambda dt: self.demonstrate_micro_interactions(), 3.0)
        except Exception as e:
            print(f"[ERROR] Dashboard on_enter failed: {e}")
    
    def validate_final_layout(self):
        """FINAL LAYOUT VALIDATION: Comprehensive validation of all layout constraints"""
        try:
            validation_issues = []
            
            # Validate responsive container constraints
            layout_info = self.get_responsive_layout_info()
            if not layout_info.get('responsive_system_active', False):
                validation_issues.append("Responsive system not active")
            
            # Validate card sizing constraints
            cards_to_validate = [
                ('server_status_card', self.server_status_card),
                ('client_stats_card', self.client_stats_card), 
                ('transfer_stats_card', self.transfer_stats_card),
                ('control_panel_card', self.control_panel_card),
                ('maintenance_card', self.maintenance_card),
                ('performance_card', self.performance_card),
                ('activity_card', self.activity_card)
            ]
            
            for card_name, card in cards_to_validate:
                if card is None:
                    validation_issues.append(f"{card_name} is None")
                    continue
                    
                # Check minimum width constraint
                if hasattr(card, 'width') and card.width < dp(380):
                    validation_issues.append(f"{card_name} width {card.width} below minimum dp(380)")
                    
                # Check adaptive height setting
                if not getattr(card, 'adaptive_height', False):
                    validation_issues.append(f"{card_name} missing adaptive_height=True")
                    
                # Check responsive constraints application
                if hasattr(card, '_responsive_constraints_applied'):
                    if not card._responsive_constraints_applied:
                        validation_issues.append(f"{card_name} responsive constraints not applied")
            
            # Validate status chip positioning (critical fix)
            if self.server_status_card and hasattr(self.server_status_card, 'status_text'):
                status_text = self.server_status_card.status_text
                if not hasattr(status_text, 'text_size') or status_text.text_size != (dp(60), dp(24)):
                    validation_issues.append("Status chip text sizing not properly configured")
                    
                if not hasattr(status_text, 'halign') or status_text.halign != 'center':
                    validation_issues.append("Status chip text alignment not centered")
            
            # Log validation results
            if self.activity_card:
                if validation_issues:
                    for issue in validation_issues[:3]:  # Limit to first 3 issues
                        self.activity_card.add_log_entry("Validation", f"Issue: {issue}", "WARNING")
                else:
                    self.activity_card.add_log_entry("Validation", "All layout constraints validated successfully", "INFO")
            
            return len(validation_issues) == 0, validation_issues
            
        except Exception as e:
            print(f"[ERROR] Layout validation failed: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def on_leave(self):
        """Screen left"""
        try:
            if self.activity_card:
                self.activity_card.add_log_entry("System", "Dashboard left")
            self.stop_updates()
        except Exception as e:
            print(f"[ERROR] Dashboard on_leave failed: {e}")
