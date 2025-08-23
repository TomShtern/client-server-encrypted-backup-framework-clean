#!/usr/bin/env python3
"""
Motion & Animation Utilities for Flet GUI
Provides helper functions for implementing Material Design 3 motion principles.
"""

import flet as ft
from enum import Enum
from typing import Optional, Union, Tuple

class MotionDuration(Enum):
    """Standard motion durations following Material Design 3 guidelines"""
    XS = 50      # Extra small - micro-interactions
    S = 100      # Small - button presses, toggles
    M = 200      # Medium - expand/collapse, small movements
    L = 300      # Large - page transitions, major movements
    XL = 500     # Extra large - complex transitions

class MotionEasing(Enum):
    """Standard easing curves following Material Design 3 guidelines"""
    STANDARD = ft.AnimationCurve.EASE_OUT  # Default for most animations
    DECELERATE = ft.AnimationCurve.EASE_OUT  # Slowing down (most common)
    ACCELERATE = ft.AnimationCurve.EASE_IN   # Speeding up
    EMPHASIZED = ft.AnimationCurve.ELASTIC_OUT  # Spring-like (special cases)
    LINEAR = ft.AnimationCurve.LINEAR  # Constant speed

def create_animation(duration: Union[int, MotionDuration] = MotionDuration.M, 
                    curve: MotionEasing = MotionEasing.DECELERATE) -> ft.Animation:
    """
    Create a standardized animation with proper duration and easing.
    
    Args:
        duration: Animation duration in milliseconds or MotionDuration enum
        curve: Easing curve or MotionEasing enum
        
    Returns:
        ft.Animation: Configured animation object
    """
    duration_ms = duration.value if isinstance(duration, MotionDuration) else duration
    curve_value = curve.value if isinstance(curve, MotionEasing) else curve
    return ft.Animation(duration_ms, curve_value)

def apply_hover_effect(control: ft.Control, 
                      scale_factor: float = 1.05,
                      elevation_increase: int = 2) -> None:
    """
    Apply a subtle hover effect to a control.
    
    Args:
        control: Flet control to apply hover effect to
        scale_factor: Scale multiplier on hover (1.05 = 5% increase)
        elevation_increase: Elevation increase on hover
    """
    # Store original values
    original_scale = getattr(control, 'scale', ft.transform.Scale(1))
    original_elevation = getattr(control, 'elevation', 0)
    
    def on_hover(e):
        if e.data == "true":
            # Hover enter
            control.scale = ft.transform.Scale(scale_factor)
            if hasattr(control, 'elevation'):
                control.elevation = original_elevation + elevation_increase
        else:
            # Hover exit
            control.scale = original_scale
            if hasattr(control, 'elevation'):
                control.elevation = original_elevation
        control.page.update()
    
    control.on_hover = on_hover
    control.animate_scale = create_animation(MotionDuration.XS)
    if hasattr(control, 'animate_elevation'):
        control.animate_elevation = create_animation(MotionDuration.XS)

def create_staggered_animation(controls: list, 
                              base_delay: int = 50,
                              duration: Union[int, MotionDuration] = MotionDuration.M) -> None:
    """
    Create a staggered entrance animation for a list of controls.
    
    Args:
        controls: List of controls to animate
        base_delay: Delay between each control's animation
        duration: Duration of each animation
    """
    duration_ms = duration.value if isinstance(duration, MotionDuration) else duration
    
    for i, control in enumerate(controls):
        # Set initial hidden state
        control.opacity = 0
        control.offset = ft.transform.Offset(0, 0.5)  # Start slightly below
        
        # Apply animation with delay
        control.animate_opacity = ft.Animation(duration_ms, ft.AnimationCurve.EASE_OUT)
        control.animate_offset = ft.Animation(duration_ms, ft.AnimationCurve.EASE_OUT)
        
        # Schedule animation with delay
        def animate_with_delay(ctrl, delay):
            import asyncio
            async def delayed_animation():
                await asyncio.sleep(delay / 1000.0)  # Convert ms to seconds
                ctrl.opacity = 1
                ctrl.offset = ft.transform.Offset(0, 0)
                ctrl.page.update()
            
            if hasattr(ctrl.page, 'session'):
                asyncio.create_task(delayed_animation())
        
        animate_with_delay(control, i * base_delay)

def create_page_transition(old_content: ft.Control, 
                          new_content: ft.Control,
                          page: ft.Page,
                          transition_type: str = "fade") -> None:
    """
    Create a smooth page transition between content.
    
    Args:
        old_content: Current content to transition from
        new_content: New content to transition to
        page: Page object
        transition_type: Type of transition ("fade", "slide", "scale")
    """
    if transition_type == "fade":
        # Fade transition
        old_content.opacity = 1
        old_content.animate_opacity = create_animation(MotionDuration.M)
        
        def fade_transition():
            old_content.opacity = 0
            page.update()
            import time
            time.sleep(0.2)  # Brief pause
            # Replace content
            # This would typically be handled by the page structure
            new_content.opacity = 0
            new_content.animate_opacity = create_animation(MotionDuration.M)
            new_content.opacity = 1
            page.update()
            
    elif transition_type == "slide":
        # Slide transition
        old_content.offset = ft.transform.Offset(0, 0)
        old_content.animate_offset = create_animation(MotionDuration.L)
        
        def slide_transition():
            old_content.offset = ft.transform.Offset(-1, 0)  # Slide left
            page.update()
            # Replace and slide in new content
            new_content.offset = ft.transform.Offset(1, 0)  # Start from right
            new_content.animate_offset = create_animation(MotionDuration.L)
            new_content.offset = ft.transform.Offset(0, 0)  # Slide to center
            page.update()

def apply_button_press_effect(button: ft.Control) -> None:
    """
    Apply a subtle press effect to a button.
    
    Args:
        button: Button control to apply effect to
    """
    original_scale = getattr(button, 'scale', ft.transform.Scale(1))
    
    def on_press_down(e):
        button.scale = ft.transform.Scale(0.95)
        button.page.update()
    
    def on_press_up(e):
        button.scale = original_scale
        button.page.update()
    
    button.on_click = lambda e: None  # Ensure click handler exists
    # Note: Flet doesn't have direct press down/up events, so we simulate
    # This would be implemented in the button's click handler

def create_spring_animation(control: ft.Control, 
                           intensity: float = 0.1,
                           duration: Union[int, MotionDuration] = MotionDuration.M) -> None:
    """
    Create a spring-like animation effect (simulated with bounce easing).
    
    Args:
        control: Control to apply spring animation to
        intensity: Spring intensity (0.1 = subtle, 0.3 = pronounced)
        duration: Animation duration
    """
    duration_ms = duration.value if isinstance(duration, MotionDuration) else duration
    
    # Use elastic easing for spring effect
    control.animate_scale = ft.Animation(duration_ms, ft.AnimationCurve.ELASTIC_OUT)
    
    # Store original scale
    original_scale = getattr(control, 'scale', ft.transform.Scale(1))
    
    # Apply spring effect
    control.scale = ft.transform.Scale(1 + intensity)
    
    def reset_scale():
        import asyncio
        async def delayed_reset():
            await asyncio.sleep(duration_ms / 1000.0)
            control.scale = original_scale
            control.page.update()
        
        if hasattr(control.page, 'session'):
            asyncio.create_task(delayed_reset())
    
    reset_scale()

# Predefined animation templates for common use cases
PAGE_TRANSITION = create_animation(MotionDuration.L)
BUTTON_HOVER = create_animation(MotionDuration.XS)
CONTENT_REVEAL = create_animation(MotionDuration.M)
LIST_ITEM_APPEAR = create_animation(MotionDuration.S)
ERROR_SHAKE = create_animation(MotionDuration.S, MotionEasing.EMPHASIZED)
SUCCESS_PULSE = create_animation(MotionDuration.M, MotionEasing.EMPHASIZED)