#!/usr/bin/env python3
"""
Material Design 3 Motion System
Comprehensive motion system implementing Material Design 3 motion principles
with easing curves, durations, and transition patterns.

Based on: https://m3.material.io/styles/motion/overview
"""

import flet as ft
import asyncio
from enum import Enum
from typing import Optional, Dict, Any, Union, Callable, List, Tuple
from dataclasses import dataclass


# ============================================================================
# MATERIAL DESIGN 3 EASING CURVES
# ============================================================================

class M3EasingCurves(Enum):
    """Material Design 3 standard easing curves with cubic bezier values."""
    
    # Standard easing: Natural and balanced motion
    STANDARD = "standard"  # (0.4, 0.0, 0.2, 1.0)
    
    # Emphasized easing: Expressive motion with subtle bounce
    EMPHASIZED = "emphasized"  # (0.4, 0.0, 0.2, 1.0) with overshoot
    
    # Decelerated easing: Fast out, slow in
    DECELERATED = "decelerated"  # (0.0, 0.0, 0.2, 1.0)
    
    # Accelerated easing: Slow out, linear in
    ACCELERATED = "accelerated"  # (0.4, 0.0, 1.0, 1.0)
    
    # Linear easing: Constant speed
    LINEAR = "linear"  # (0.0, 0.0, 1.0, 1.0)


# Map M3 curves to Flet AnimationCurves
M3_CURVE_MAPPING = {
    M3EasingCurves.STANDARD: ft.AnimationCurve.EASE_OUT,
    M3EasingCurves.EMPHASIZED: ft.AnimationCurve.BOUNCE_OUT,
    M3EasingCurves.DECELERATED: ft.AnimationCurve.EASE_OUT,
    M3EasingCurves.ACCELERATED: ft.AnimationCurve.EASE_IN,
    M3EasingCurves.LINEAR: ft.AnimationCurve.LINEAR,
}


# ============================================================================
# MATERIAL DESIGN 3 DURATION SYSTEM
# ============================================================================

class M3Duration(Enum):
    """Material Design 3 standard duration tokens."""
    
    # Short: Small component transitions (buttons, switches)
    SHORT1 = 50    # Extra short for micro-interactions
    SHORT2 = 100   # Short for small components  
    SHORT3 = 150   # Short for small element transitions
    SHORT4 = 200   # Short duration cap
    
    # Medium: Standard transitions (expanding/collapsing)
    MEDIUM1 = 250  # Medium start
    MEDIUM2 = 300  # Standard medium duration
    MEDIUM3 = 350  # Medium+ 
    MEDIUM4 = 400  # Medium duration cap
    
    # Long: Large area transitions
    LONG1 = 450    # Long start
    LONG2 = 500    # Standard long duration
    LONG3 = 550    # Long+
    LONG4 = 600    # Long duration cap
    
    # Extra Long: Page/view transitions
    EXTRA_LONG1 = 700  # Extra long start
    EXTRA_LONG2 = 800  # Standard extra long
    EXTRA_LONG3 = 900  # Extra long+
    EXTRA_LONG4 = 1000 # Extra long duration cap


# ============================================================================
# MOTION TOKEN SYSTEM
# ============================================================================

@dataclass
class MotionToken:
    """A motion token containing duration, easing, and metadata."""
    duration: int
    easing: M3EasingCurves
    description: str
    use_cases: List[str]


class M3MotionTokens:
    """Material Design 3 motion tokens for consistent animation patterns."""
    
    # Button interactions
    BUTTON_PRESS = MotionToken(
        duration=M3Duration.SHORT1.value,
        easing=M3EasingCurves.STANDARD,
        description="Button press feedback",
        use_cases=["button_press", "tap_feedback"]
    )
    
    BUTTON_HOVER = MotionToken(
        duration=M3Duration.SHORT2.value,
        easing=M3EasingCurves.STANDARD,
        description="Button hover state",
        use_cases=["hover_enter", "hover_exit"]
    )
    
    # Component state changes
    COMPONENT_STATE = MotionToken(
        duration=M3Duration.SHORT3.value,
        easing=M3EasingCurves.STANDARD,
        description="Component state transitions",
        use_cases=["switch_toggle", "checkbox_check", "radio_select"]
    )
    
    # Content transitions
    CONTENT_FADE = MotionToken(
        duration=M3Duration.MEDIUM2.value,
        easing=M3EasingCurves.STANDARD,
        description="Content fade in/out",
        use_cases=["dialog_appear", "tooltip_show", "toast_notification"]
    )
    
    CONTENT_SLIDE = MotionToken(
        duration=M3Duration.MEDIUM2.value,
        easing=M3EasingCurves.DECELERATED,
        description="Content sliding motion",
        use_cases=["drawer_open", "sheet_expand", "tab_transition"]
    )
    
    # Container transformations
    CONTAINER_TRANSFORM = MotionToken(
        duration=M3Duration.LONG2.value,
        easing=M3EasingCurves.EMPHASIZED,
        description="Container shape/size transformation",
        use_cases=["card_expand", "fab_transform", "container_morph"]
    )
    
    # Navigation transitions
    NAVIGATION_SHARED_AXIS = MotionToken(
        duration=M3Duration.LONG2.value,
        easing=M3EasingCurves.DECELERATED,
        description="Navigation with spatial relationship",
        use_cases=["page_forward", "page_back", "tab_switch"]
    )
    
    NAVIGATION_FADE_THROUGH = MotionToken(
        duration=M3Duration.MEDIUM4.value,
        easing=M3EasingCurves.STANDARD,
        description="Content replacement with fade",
        use_cases=["content_replace", "view_switch"]
    )
    
    # Error and success states
    ERROR_SHAKE = MotionToken(
        duration=M3Duration.MEDIUM1.value,
        easing=M3EasingCurves.EMPHASIZED,
        description="Error indication with shake",
        use_cases=["form_error", "validation_failure"]
    )
    
    SUCCESS_PULSE = MotionToken(
        duration=M3Duration.LONG1.value,
        easing=M3EasingCurves.EMPHASIZED,
        description="Success indication with pulse",
        use_cases=["form_success", "action_complete"]
    )
    
    # List and grid animations
    LIST_ITEM_ENTER = MotionToken(
        duration=M3Duration.MEDIUM1.value,
        easing=M3EasingCurves.DECELERATED,
        description="List item entrance",
        use_cases=["list_add", "search_results", "load_more"]
    )
    
    LIST_ITEM_EXIT = MotionToken(
        duration=M3Duration.SHORT4.value,
        easing=M3EasingCurves.ACCELERATED,
        description="List item removal",
        use_cases=["list_remove", "swipe_dismiss"]
    )


# ============================================================================
# MATERIAL DESIGN 3 TRANSITION PATTERNS
# ============================================================================

class M3TransitionPatterns:
    """Material Design 3 transition pattern implementations."""
    
    @staticmethod
    def fade_through(
        old_content: ft.Control,
        new_content: ft.Control,
        duration: Optional[int] = None,
        on_complete: Optional[Callable] = None
    ) -> None:
        """
        Fade Through: Content replacement with cross-fade.
        Best for: Content that has no spatial or navigational relationship.
        """
        motion_token = M3MotionTokens.NAVIGATION_FADE_THROUGH
        duration = duration or motion_token.duration
        easing = M3_CURVE_MAPPING[motion_token.easing]
        
        # Configure animations
        old_content.animate_opacity = ft.Animation(duration, easing)
        new_content.animate_opacity = ft.Animation(duration, easing)
        
        # Start with new content hidden
        new_content.opacity = 0
        
        async def execute_fade_through():
            try:
                # Phase 1: Fade out old content
                old_content.opacity = 0
                old_content.update()
                
                # Wait for fade out to complete (midpoint)
                await asyncio.sleep((duration / 2) / 1000.0)
                
                # Phase 2: Fade in new content
                new_content.opacity = 1
                new_content.update()
                
                # Wait for fade in to complete
                await asyncio.sleep((duration / 2) / 1000.0)
                
                if on_complete:
                    on_complete()
                    
            except Exception as e:
                print(f"[ERROR] Fade through animation failed: {e}")
        
        asyncio.create_task(execute_fade_through())
    
    @staticmethod
    def shared_axis_x(
        control: ft.Control,
        direction: str = "forward",
        duration: Optional[int] = None,
        distance: float = 0.3,
        on_complete: Optional[Callable] = None
    ) -> None:
        """
        Shared Axis X: Horizontal spatial transitions.
        Best for: Navigation between pages with spatial relationship.
        
        Args:
            direction: "forward" (left to right) or "backward" (right to left)
        """
        motion_token = M3MotionTokens.NAVIGATION_SHARED_AXIS
        duration = duration or motion_token.duration
        easing = M3_CURVE_MAPPING[motion_token.easing]
        
        control.animate_offset = ft.Animation(duration, easing)
        
        # Determine start and end positions
        start_x = distance if direction == "forward" else -distance
        
        async def execute_shared_axis():
            try:
                # Start positioned off-screen
                control.offset = ft.transform.Offset(start_x, 0)
                control.update()
                
                # Small delay to ensure initial position is set
                await asyncio.sleep(0.05)
                
                # Animate to center
                control.offset = ft.transform.Offset(0, 0)
                control.update()
                
                # Wait for animation to complete
                await asyncio.sleep(duration / 1000.0)
                
                if on_complete:
                    on_complete()
                    
            except Exception as e:
                print(f"[ERROR] Shared axis animation failed: {e}")
        
        asyncio.create_task(execute_shared_axis())
    
    @staticmethod
    def shared_axis_y(
        control: ft.Control,
        direction: str = "up",
        duration: Optional[int] = None,
        distance: float = 0.3,
        on_complete: Optional[Callable] = None
    ) -> None:
        """
        Shared Axis Y: Vertical spatial transitions.
        Best for: Hierarchical navigation (parent-child relationships).
        
        Args:
            direction: "up" (bottom to top) or "down" (top to bottom)
        """
        motion_token = M3MotionTokens.NAVIGATION_SHARED_AXIS
        duration = duration or motion_token.duration
        easing = M3_CURVE_MAPPING[motion_token.easing]
        
        control.animate_offset = ft.Animation(duration, easing)
        
        # Determine start position
        start_y = distance if direction == "up" else -distance
        
        async def execute_shared_axis_y():
            try:
                control.offset = ft.transform.Offset(0, start_y)
                control.update()
                
                await asyncio.sleep(0.05)
                
                control.offset = ft.transform.Offset(0, 0)
                control.update()
                
                await asyncio.sleep(duration / 1000.0)
                
                if on_complete:
                    on_complete()
                    
            except Exception as e:
                print(f"[ERROR] Shared axis Y animation failed: {e}")
        
        asyncio.create_task(execute_shared_axis_y())
    
    @staticmethod
    def container_transform(
        from_control: ft.Control,
        to_control: ft.Control,
        duration: Optional[int] = None,
        on_complete: Optional[Callable] = None
    ) -> None:
        """
        Container Transform: Morphing between UI elements.
        Best for: Element that transforms into another (FAB to sheet, card to details).
        """
        motion_token = M3MotionTokens.CONTAINER_TRANSFORM
        duration = duration or motion_token.duration
        easing = M3_CURVE_MAPPING[motion_token.easing]
        
        # Configure animations for both controls
        from_control.animate_scale = ft.Animation(duration, easing)
        from_control.animate_opacity = ft.Animation(duration, easing)
        to_control.animate_scale = ft.Animation(duration, easing)
        to_control.animate_opacity = ft.Animation(duration, easing)
        
        async def execute_container_transform():
            try:
                # Initial state
                to_control.opacity = 0
                to_control.scale = ft.transform.Scale(0.8)
                
                # Start transformation
                from_control.scale = ft.transform.Scale(1.1)
                from_control.opacity = 0.5
                from_control.update()
                
                await asyncio.sleep((duration * 0.3) / 1000.0)
                
                # Midpoint: Start showing new control
                to_control.opacity = 1
                to_control.scale = ft.transform.Scale(1.0)
                to_control.update()
                
                # Continue fading out old control
                from_control.opacity = 0
                from_control.update()
                
                await asyncio.sleep((duration * 0.7) / 1000.0)
                
                if on_complete:
                    on_complete()
                    
            except Exception as e:
                print(f"[ERROR] Container transform animation failed: {e}")
        
        asyncio.create_task(execute_container_transform())
    
    @staticmethod
    def fade(
        control: ft.Control,
        fade_in: bool = True,
        duration: Optional[int] = None,
        on_complete: Optional[Callable] = None
    ) -> None:
        """
        Fade: Simple appear/disappear transition.
        Best for: Simple show/hide without spatial context.
        """
        motion_token = M3MotionTokens.CONTENT_FADE
        duration = duration or motion_token.duration
        easing = M3_CURVE_MAPPING[motion_token.easing]
        
        control.animate_opacity = ft.Animation(duration, easing)
        
        async def execute_fade():
            try:
                if fade_in:
                    control.opacity = 0
                    control.update()
                    await asyncio.sleep(0.05)
                    control.opacity = 1
                else:
                    control.opacity = 1
                    control.update()
                    await asyncio.sleep(0.05)
                    control.opacity = 0
                
                control.update()
                await asyncio.sleep(duration / 1000.0)
                
                if on_complete:
                    on_complete()
                    
            except Exception as e:
                print(f"[ERROR] Fade animation failed: {e}")
        
        asyncio.create_task(execute_fade())


# ============================================================================
# MAIN MOTION SYSTEM CLASS
# ============================================================================

class M3MotionSystem:
    """
    Material Design 3 Motion System
    Main interface for implementing M3 motion patterns and animations.
    """
    
    def __init__(self, page: ft.Page):
        """Initialize the motion system with a page reference."""
        self.page = page
        self._motion_preferences = {"reduce_motion": False}  # Accessibility
    
    # ========================================================================
    # CORE ANIMATION UTILITIES
    # ========================================================================
    
    @staticmethod
    def create_animation(
        duration: Union[int, M3Duration] = M3Duration.MEDIUM2,
        easing: M3EasingCurves = M3EasingCurves.STANDARD
    ) -> ft.Animation:
        """Create a standardized Material Design 3 animation."""
        duration_ms = duration.value if isinstance(duration, M3Duration) else duration
        curve = M3_CURVE_MAPPING.get(easing, ft.AnimationCurve.EASE_OUT)
        return ft.Animation(duration_ms, curve)
    
    def apply_motion_token(self, control: ft.Control, token: MotionToken) -> None:
        """Apply a motion token's properties to a control."""
        animation = self.create_animation(token.duration, token.easing)
        
        # Apply common animation properties
        if hasattr(control, 'animate_opacity'):
            control.animate_opacity = animation
        if hasattr(control, 'animate_offset'):
            control.animate_offset = animation
        if hasattr(control, 'animate_scale'):
            control.animate_scale = animation
    
    # ========================================================================
    # COMMON UI PATTERNS
    # ========================================================================
    
    def button_press_feedback(self, button: ft.Control) -> None:
        """Apply Material Design 3 button press feedback."""
        token = M3MotionTokens.BUTTON_PRESS
        
        button.animate_scale = self.create_animation(token.duration, token.easing)
        
        async def press_feedback():
            try:
                # Press down (subtle scale reduction)
                button.scale = ft.transform.Scale(0.95)
                button.update()
                
                # Quick return to normal
                await asyncio.sleep(token.duration / 1000.0)
                button.scale = ft.transform.Scale(1.0)
                button.update()
                
            except Exception as e:
                print(f"[ERROR] Button press feedback failed: {e}")
        
        # Store the original click handler
        original_click = getattr(button, 'on_click', None)
        
        def enhanced_click(e):
            asyncio.create_task(press_feedback())
            if original_click:
                original_click(e)
        
        button.on_click = enhanced_click
    
    def button_hover_effect(
        self,
        button: ft.Control,
        scale_factor: float = 1.02,
        elevation_increase: int = 1
    ) -> None:
        """Apply Material Design 3 button hover effect."""
        token = M3MotionTokens.BUTTON_HOVER
        
        button.animate_scale = self.create_animation(token.duration, token.easing)
        if hasattr(button, 'animate_elevation'):
            button.animate_elevation = self.create_animation(token.duration, token.easing)
        
        # Store original values
        original_scale = getattr(button, 'scale', ft.transform.Scale(1.0))
        original_elevation = getattr(button, 'elevation', 0)
        
        def on_hover(e):
            try:
                if e.data == "true":
                    # Hover enter
                    button.scale = ft.transform.Scale(scale_factor)
                    if hasattr(button, 'elevation'):
                        button.elevation = original_elevation + elevation_increase
                else:
                    # Hover exit
                    button.scale = original_scale
                    if hasattr(button, 'elevation'):
                        button.elevation = original_elevation
                button.update()
            except Exception as ex:
                print(f"[ERROR] Button hover effect failed: {ex}")
        
        button.on_hover = on_hover
    
    def card_hover_effect(
        self,
        card: ft.Control,
        elevation_increase: int = 2,
        scale_factor: float = 1.01
    ) -> None:
        """Apply Material Design 3 card hover effect."""
        token = M3MotionTokens.BUTTON_HOVER  # Same timing for cards
        
        card.animate_scale = self.create_animation(token.duration, token.easing)
        if hasattr(card, 'animate_elevation'):
            card.animate_elevation = self.create_animation(token.duration, token.easing)
        
        original_scale = getattr(card, 'scale', ft.transform.Scale(1.0))
        original_elevation = getattr(card, 'elevation', 1)
        
        def on_hover(e):
            try:
                if e.data == "true":
                    card.scale = ft.transform.Scale(scale_factor)
                    if hasattr(card, 'elevation'):
                        card.elevation = original_elevation + elevation_increase
                else:
                    card.scale = original_scale
                    if hasattr(card, 'elevation'):
                        card.elevation = original_elevation
                card.update()
            except Exception as ex:
                print(f"[ERROR] Card hover effect failed: {ex}")
        
        card.on_hover = on_hover
    
    def toast_notification(
        self,
        control: ft.Control,
        slide_from: str = "bottom",
        duration: Optional[int] = None,
        auto_dismiss_after: float = 3.0,
        on_dismiss: Optional[Callable] = None
    ) -> None:
        """
        Show a toast notification with proper Material Design 3 motion.
        
        Args:
            slide_from: "bottom", "top", or "side"
            auto_dismiss_after: Seconds before auto-dismissal (0 = no auto-dismiss)
        """
        token = M3MotionTokens.CONTENT_SLIDE
        duration = duration or token.duration
        
        control.animate_offset = self.create_animation(duration, token.easing)
        control.animate_opacity = self.create_animation(duration, M3EasingCurves.STANDARD)
        
        async def show_toast():
            try:
                # Initial position (off-screen)
                if slide_from == "bottom":
                    control.offset = ft.transform.Offset(0, 1.0)
                elif slide_from == "top":
                    control.offset = ft.transform.Offset(0, -1.0)
                else:  # side
                    control.offset = ft.transform.Offset(1.0, 0)
                
                control.opacity = 0
                control.update()
                
                await asyncio.sleep(0.05)
                
                # Animate in
                control.offset = ft.transform.Offset(0, 0)
                control.opacity = 1
                control.update()
                
                # Auto-dismiss
                if auto_dismiss_after > 0:
                    await asyncio.sleep(auto_dismiss_after)
                    
                    # Animate out
                    if slide_from == "bottom":
                        control.offset = ft.transform.Offset(0, 1.0)
                    elif slide_from == "top":
                        control.offset = ft.transform.Offset(0, -1.0)
                    else:  # side
                        control.offset = ft.transform.Offset(1.0, 0)
                    
                    control.opacity = 0
                    control.update()
                    
                    await asyncio.sleep(duration / 1000.0)
                    
                    if on_dismiss:
                        on_dismiss()
                
            except Exception as e:
                print(f"[ERROR] Toast notification failed: {e}")
        
        asyncio.create_task(show_toast())
    
    def list_item_interactions(
        self,
        items: List[ft.Control],
        stagger_delay: int = 50,
        entrance_direction: str = "up"
    ) -> None:
        """Apply staggered entrance animations to list items."""
        token = M3MotionTokens.LIST_ITEM_ENTER
        
        for i, item in enumerate(items):
            item.animate_opacity = self.create_animation(token.duration, token.easing)
            item.animate_offset = self.create_animation(token.duration, token.easing)
            
            # Initial state
            item.opacity = 0
            if entrance_direction == "up":
                item.offset = ft.transform.Offset(0, 0.5)
            elif entrance_direction == "down":
                item.offset = ft.transform.Offset(0, -0.5)
            else:  # side
                item.offset = ft.transform.Offset(0.5, 0)
            
            async def animate_item(control: ft.Control, delay: int):
                try:
                    await asyncio.sleep(delay / 1000.0)
                    control.opacity = 1
                    control.offset = ft.transform.Offset(0, 0)
                    control.update()
                except Exception as e:
                    print(f"[ERROR] List item animation failed: {e}")
            
            asyncio.create_task(animate_item(item, i * stagger_delay))
    
    def dialog_appearance(
        self,
        dialog: ft.Control,
        entrance_style: str = "scale_fade"
    ) -> None:
        """Animate dialog appearance with Material Design 3 patterns."""
        token = M3MotionTokens.CONTENT_FADE
        
        if entrance_style == "scale_fade":
            dialog.animate_scale = self.create_animation(token.duration, M3EasingCurves.EMPHASIZED)
            dialog.animate_opacity = self.create_animation(token.duration, M3EasingCurves.STANDARD)
            
            async def animate_dialog():
                try:
                    dialog.opacity = 0
                    dialog.scale = ft.transform.Scale(0.8)
                    dialog.update()
                    
                    await asyncio.sleep(0.05)
                    
                    dialog.opacity = 1
                    dialog.scale = ft.transform.Scale(1.0)
                    dialog.update()
                except Exception as e:
                    print(f"[ERROR] Dialog animation failed: {e}")
            
            asyncio.create_task(animate_dialog())
        
        elif entrance_style == "slide_up":
            self.shared_axis_y(dialog, direction="up", duration=token.duration)
    
    # ========================================================================
    # ERROR AND SUCCESS FEEDBACK
    # ========================================================================
    
    def error_shake(self, control: ft.Control) -> None:
        """Apply error shake animation to a control."""
        token = M3MotionTokens.ERROR_SHAKE
        
        control.animate_offset = self.create_animation(token.duration, token.easing)
        
        async def shake_animation():
            try:
                # Shake sequence: left, right, left, center
                positions = [
                    ft.transform.Offset(-0.05, 0),
                    ft.transform.Offset(0.05, 0),
                    ft.transform.Offset(-0.03, 0),
                    ft.transform.Offset(0, 0)
                ]
                
                for position in positions:
                    control.offset = position
                    control.update()
                    await asyncio.sleep((token.duration / 4) / 1000.0)
                    
            except Exception as e:
                print(f"[ERROR] Shake animation failed: {e}")
        
        asyncio.create_task(shake_animation())
    
    def success_pulse(self, control: ft.Control) -> None:
        """Apply success pulse animation to a control."""
        token = M3MotionTokens.SUCCESS_PULSE
        
        control.animate_scale = self.create_animation(token.duration, token.easing)
        
        async def pulse_animation():
            try:
                original_scale = getattr(control, 'scale', ft.transform.Scale(1.0))
                
                # Pulse sequence: grow, shrink, normal
                control.scale = ft.transform.Scale(1.1)
                control.update()
                
                await asyncio.sleep((token.duration / 3) / 1000.0)
                
                control.scale = ft.transform.Scale(0.95)
                control.update()
                
                await asyncio.sleep((token.duration / 3) / 1000.0)
                
                control.scale = original_scale
                control.update()
                
            except Exception as e:
                print(f"[ERROR] Pulse animation failed: {e}")
        
        asyncio.create_task(pulse_animation())
    
    # ========================================================================
    # TRANSITION PATTERN SHORTCUTS
    # ========================================================================
    
    def fade_in(
        self,
        control: ft.Control,
        duration: Union[int, M3Duration] = M3Duration.MEDIUM2,
        easing: M3EasingCurves = M3EasingCurves.STANDARD
    ) -> None:
        """Fade in a control."""
        M3TransitionPatterns.fade(control, fade_in=True, duration=duration.value if isinstance(duration, M3Duration) else duration)
    
    def fade_out(
        self,
        control: ft.Control,
        duration: Union[int, M3Duration] = M3Duration.MEDIUM2,
        easing: M3EasingCurves = M3EasingCurves.STANDARD
    ) -> None:
        """Fade out a control."""
        M3TransitionPatterns.fade(control, fade_in=False, duration=duration.value if isinstance(duration, M3Duration) else duration)
    
    def slide_up(
        self,
        control: ft.Control,
        distance: float = 0.3,
        duration: Union[int, M3Duration] = M3Duration.MEDIUM2
    ) -> None:
        """Slide control up from bottom."""
        M3TransitionPatterns.shared_axis_y(
            control,
            direction="up",
            duration=duration.value if isinstance(duration, M3Duration) else duration,
            distance=distance
        )
    
    def slide_down(
        self,
        control: ft.Control,
        distance: float = 0.3,
        duration: Union[int, M3Duration] = M3Duration.MEDIUM2
    ) -> None:
        """Slide control down from top."""
        M3TransitionPatterns.shared_axis_y(
            control,
            direction="down",
            duration=duration.value if isinstance(duration, M3Duration) else duration,
            distance=distance
        )
    
    def slide_in_from_right(
        self,
        control: ft.Control,
        distance: float = 0.3,
        duration: Union[int, M3Duration] = M3Duration.MEDIUM2
    ) -> None:
        """Slide control in from right side."""
        M3TransitionPatterns.shared_axis_x(
            control,
            direction="forward",
            duration=duration.value if isinstance(duration, M3Duration) else duration,
            distance=distance
        )
    
    def slide_in_from_left(
        self,
        control: ft.Control,
        distance: float = 0.3,
        duration: Union[int, M3Duration] = M3Duration.MEDIUM2
    ) -> None:
        """Slide control in from left side."""
        M3TransitionPatterns.shared_axis_x(
            control,
            direction="backward",
            duration=duration.value if isinstance(duration, M3Duration) else duration,
            distance=distance
        )
    
    # ========================================================================
    # ACCESSIBILITY & PREFERENCES
    # ========================================================================
    
    def set_reduce_motion(self, reduce: bool = True) -> None:
        """Set motion reduction preference for accessibility."""
        self._motion_preferences["reduce_motion"] = reduce
    
    def should_reduce_motion(self) -> bool:
        """Check if motion should be reduced for accessibility."""
        return self._motion_preferences.get("reduce_motion", False)
    
    def get_accessible_duration(self, duration: Union[int, M3Duration]) -> int:
        """Get duration adjusted for accessibility preferences."""
        base_duration = duration.value if isinstance(duration, M3Duration) else duration
        
        if self.should_reduce_motion():
            # Reduce animation durations by 50% for accessibility
            return int(base_duration * 0.5)
        
        return base_duration


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_motion_system(page: ft.Page) -> M3MotionSystem:
    """Create and initialize a Material Design 3 motion system."""
    return M3MotionSystem(page)


def get_motion_token_by_use_case(use_case: str) -> Optional[MotionToken]:
    """Get a motion token by its use case."""
    for token in M3MotionTokens.__dict__.values():
        if isinstance(token, MotionToken) and use_case in token.use_cases:
            return token
    return None


# ============================================================================
# PREDEFINED ANIMATION SETS
# ============================================================================

class PrebuiltAnimations:
    """Collection of common animation configurations."""
    
    # Page transitions
    PAGE_ENTER = M3MotionTokens.NAVIGATION_SHARED_AXIS
    PAGE_EXIT = MotionToken(
        duration=M3Duration.MEDIUM1.value,
        easing=M3EasingCurves.ACCELERATED,
        description="Page exit transition",
        use_cases=["page_exit", "navigation_back"]
    )
    
    # Modal interactions
    MODAL_ENTER = M3MotionTokens.CONTENT_FADE
    MODAL_EXIT = MotionToken(
        duration=M3Duration.SHORT4.value,
        easing=M3EasingCurves.ACCELERATED,
        description="Modal dismissal",
        use_cases=["modal_close", "dialog_dismiss"]
    )
    
    # Loading states
    LOADING_PULSE = MotionToken(
        duration=M3Duration.LONG2.value,
        easing=M3EasingCurves.LINEAR,
        description="Loading indicator pulse",
        use_cases=["loading_spinner", "progress_indicator"]
    )


# Export the main class and key components
__all__ = [
    'M3MotionSystem',
    'M3EasingCurves',
    'M3Duration',
    'M3MotionTokens',
    'M3TransitionPatterns',
    'MotionToken',
    'PrebuiltAnimations',
    'create_motion_system',
    'get_motion_token_by_use_case'
]