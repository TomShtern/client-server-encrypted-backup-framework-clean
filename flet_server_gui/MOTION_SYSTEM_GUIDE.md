# Material Design 3 Motion System Guide

## Overview

The **Material Design 3 Motion System** (`flet_server_gui/ui/motion_system.py`) provides a comprehensive implementation of Google's Material Design 3 motion principles for Flet applications. It offers standardized animations, easing curves, durations, and transition patterns that create cohesive and intuitive user experiences.

## Key Features

### ✅ **Material Design 3 Compliance**
- Official M3 easing curves and duration tokens
- Standardized transition patterns (Fade Through, Shared Axis, Container Transform, Fade)
- Accessibility support with motion reduction preferences

### ✅ **Comprehensive Animation Library**
- **40+ Animation Types**: Button interactions, card hovers, page transitions, list animations
- **Performance Optimized**: Lightweight implementation with minimal overhead
- **Async/Threading Safe**: Proper async handling for Flet's threading model

### ✅ **Easy Integration**
- Drop-in enhancement for existing components
- Clean API with sensible defaults
- Seamless integration with existing Flet GUI components

## Quick Start

### 1. Basic Setup

```python
import flet as ft
from flet_server_gui.ui.motion_system import M3MotionSystem, create_motion_system

def main(page: ft.Page):
    # Create motion system
    motion_system = create_motion_system(page)
    
    # Create a button with motion effects
    button = ft.FilledButton(text="Click me!", on_click=lambda e: None)
    
    # Apply motion effects
    motion_system.button_press_feedback(button)
    motion_system.button_hover_effect(button)
    
    page.add(button)

ft.app(target=main)
```

### 2. Card Interactions

```python
# Create a card with hover effects
card = ft.Card(content=ft.Text("Hover over me!"))

# Apply hover animation
motion_system.card_hover_effect(
    card,
    elevation_increase=3,
    scale_factor=1.02
)
```

### 3. Toast Notifications

```python
# Create toast container
toast = ft.Container(
    content=ft.Text("Success!", color=ft.Colors.WHITE),
    bgcolor=ft.Colors.GREEN,
    border_radius=8,
    padding=16
)

# Show with animation
motion_system.toast_notification(
    toast,
    slide_from="bottom",
    auto_dismiss_after=3.0
)
```

## Material Design 3 Components

### Easing Curves

The system implements official M3 easing curves:

```python
from flet_server_gui.ui.motion_system import M3EasingCurves

# Standard: Balanced, natural motion (most common)
M3EasingCurves.STANDARD

# Emphasized: Expressive motion with subtle bounce
M3EasingCurves.EMPHASIZED  

# Decelerated: Fast start, slow end (entering elements)
M3EasingCurves.DECELERATED

# Accelerated: Slow start, fast end (exiting elements)  
M3EasingCurves.ACCELERATED

# Linear: Constant speed (progress indicators)
M3EasingCurves.LINEAR
```

### Duration Tokens

Standardized duration system following M3 guidelines:

```python
from flet_server_gui.ui.motion_system import M3Duration

# Short durations (50-200ms) - micro-interactions
M3Duration.SHORT1  # 50ms  - button press
M3Duration.SHORT2  # 100ms - hover effects
M3Duration.SHORT3  # 150ms - small transitions
M3Duration.SHORT4  # 200ms - component state changes

# Medium durations (250-400ms) - standard transitions
M3Duration.MEDIUM1 # 250ms - content fade
M3Duration.MEDIUM2 # 300ms - most common duration
M3Duration.MEDIUM3 # 350ms - modal transitions
M3Duration.MEDIUM4 # 400ms - complex content changes

# Long durations (450-600ms) - large area transitions
M3Duration.LONG1   # 450ms - container transforms
M3Duration.LONG2   # 500ms - page transitions
M3Duration.LONG3   # 550ms - complex animations
M3Duration.LONG4   # 600ms - full screen transitions

# Extra Long durations (700-1000ms) - major view changes
M3Duration.EXTRA_LONG1 # 700ms - view transitions
M3Duration.EXTRA_LONG2 # 800ms - complex layouts
M3Duration.EXTRA_LONG3 # 900ms - data loading
M3Duration.EXTRA_LONG4 # 1000ms - maximum duration
```

### Motion Tokens

Pre-configured animation settings for common use cases:

```python
from flet_server_gui.ui.motion_system import M3MotionTokens

# Button interactions
M3MotionTokens.BUTTON_PRESS    # 50ms, standard easing
M3MotionTokens.BUTTON_HOVER    # 100ms, standard easing

# Content transitions  
M3MotionTokens.CONTENT_FADE    # 300ms, standard easing
M3MotionTokens.CONTENT_SLIDE   # 300ms, decelerated easing

# Container transformations
M3MotionTokens.CONTAINER_TRANSFORM # 500ms, emphasized easing

# Navigation transitions
M3MotionTokens.NAVIGATION_SHARED_AXIS  # 500ms, decelerated easing
M3MotionTokens.NAVIGATION_FADE_THROUGH # 400ms, standard easing

# Feedback animations
M3MotionTokens.ERROR_SHAKE     # 250ms, emphasized easing  
M3MotionTokens.SUCCESS_PULSE   # 450ms, emphasized easing

# List animations
M3MotionTokens.LIST_ITEM_ENTER # 250ms, decelerated easing
M3MotionTokens.LIST_ITEM_EXIT  # 200ms, accelerated easing
```

## Transition Patterns

### 1. Fade Through
For content that has no spatial relationship:

```python
from flet_server_gui.ui.motion_system import M3TransitionPatterns

# Replace content with cross-fade
M3TransitionPatterns.fade_through(
    old_content=current_view,
    new_content=next_view,
    duration=400,  # Optional, uses token default
    on_complete=lambda: print("Transition complete")
)
```

### 2. Shared Axis
For content with spatial or navigational relationships:

```python
# Horizontal navigation (forward/backward)
M3TransitionPatterns.shared_axis_x(
    control=next_page,
    direction="forward",  # or "backward"
    duration=500,
    distance=0.3  # Slide distance (30% of width)
)

# Vertical navigation (parent/child)
M3TransitionPatterns.shared_axis_y(
    control=detail_view,
    direction="up",  # or "down" 
    duration=500,
    distance=0.3
)
```

### 3. Container Transform
For elements that transform into other elements:

```python
# Transform FAB to dialog, card to detail view, etc.
M3TransitionPatterns.container_transform(
    from_control=fab_button,
    to_control=expanded_dialog,
    duration=500,
    on_complete=lambda: print("Transform complete")
)
```

### 4. Simple Fade
For basic show/hide without spatial context:

```python
# Fade in
M3TransitionPatterns.fade(
    control=modal_overlay,
    fade_in=True,
    duration=300
)

# Fade out
M3TransitionPatterns.fade(
    control=modal_overlay, 
    fade_in=False,
    duration=300
)
```

## Motion System API

### Core Methods

```python
motion_system = M3MotionSystem(page)

# Basic animations
motion_system.fade_in(control, duration=M3Duration.MEDIUM2)
motion_system.fade_out(control, duration=M3Duration.MEDIUM2)
motion_system.slide_up(control, distance=0.3)
motion_system.slide_down(control, distance=0.3)
motion_system.slide_in_from_right(control, distance=0.3)
motion_system.slide_in_from_left(control, distance=0.3)

# Interactive feedback
motion_system.button_press_feedback(button)
motion_system.button_hover_effect(button, scale_factor=1.05)
motion_system.card_hover_effect(card, elevation_increase=2)

# Toast notifications
motion_system.toast_notification(
    toast_container,
    slide_from="bottom",  # "top", "bottom", "side"
    auto_dismiss_after=3.0,
    on_dismiss=cleanup_function
)

# List animations
motion_system.list_item_interactions(
    items=[item1, item2, item3],
    stagger_delay=50,  # ms between each item
    entrance_direction="up"  # "up", "down", "side"
)

# Dialog animations
motion_system.dialog_appearance(
    dialog,
    entrance_style="scale_fade"  # "scale_fade", "slide_up"
)

# Error/Success feedback
motion_system.error_shake(form_field)
motion_system.success_pulse(success_icon)
```

### Accessibility Support

```python
# Enable motion reduction for accessibility
motion_system.set_reduce_motion(True)

# Check motion preferences
if motion_system.should_reduce_motion():
    # Skip complex animations
    pass

# Get accessibility-adjusted durations
accessible_duration = motion_system.get_accessible_duration(M3Duration.MEDIUM2)
```

## Integration Examples

### Dashboard Enhancement

```python
class EnhancedDashboard:
    def __init__(self, page: ft.Page):
        self.motion_system = create_motion_system(page)
    
    def create_status_cards(self):
        cards = [self.create_server_card(), self.create_client_card()]
        
        # Apply hover effects
        for card in cards:
            self.motion_system.card_hover_effect(card)
        
        # Staggered entrance
        self.motion_system.list_item_interactions(cards, stagger_delay=100)
        
        return ft.Row(cards)
    
    def show_notification(self, message: str, level: str = "info"):
        toast = self.create_toast(message, level)
        
        # Add to page and animate
        self.page.overlay.append(toast)
        self.motion_system.toast_notification(
            toast,
            auto_dismiss_after=3.0,
            on_dismiss=lambda: self.page.overlay.remove(toast)
        )
```

### Form Validation with Motion

```python
def validate_form(self, form_field: ft.TextField):
    if not form_field.value:
        # Shake the field and show error
        self.motion_system.error_shake(form_field)
        self.show_error_toast("Field is required")
    else:
        # Success pulse
        self.motion_system.success_pulse(form_field)
        self.show_success_toast("Validation passed")
```

### Navigation with Transitions

```python
def navigate_to_page(self, new_page: ft.Control, direction: str = "forward"):
    """Navigate with shared axis transition."""
    current_page = self.get_current_page()
    
    # Hide current page
    current_page.visible = False
    new_page.visible = True
    self.page.update()
    
    # Animate new page in
    M3TransitionPatterns.shared_axis_x(
        new_page,
        direction=direction,
        duration=M3Duration.LONG2.value
    )
```

## Best Practices

### 1. **Choose Appropriate Durations**
- **Short (50-200ms)**: Micro-interactions, hover states
- **Medium (250-400ms)**: Standard content transitions
- **Long (450-600ms)**: Large area transitions, page changes
- **Extra Long (700-1000ms)**: Major view changes only

### 2. **Match Easing to Context**
- **Standard**: Most common, balanced motion
- **Decelerated**: Elements entering the screen
- **Accelerated**: Elements leaving the screen  
- **Emphasized**: Special moments, success/error states
- **Linear**: Progress indicators, loading states

### 3. **Respect Accessibility**
```python
# Always check motion preferences
if motion_system.should_reduce_motion():
    # Use instant transitions or very short durations
    duration = M3Duration.SHORT1
else:
    # Use full animation
    duration = M3Duration.MEDIUM2
```

### 4. **Layer Animations Appropriately**
```python
# Don't stack too many simultaneous animations
async def complex_transition():
    # Step 1: Fade out old content
    motion_system.fade_out(old_content)
    await asyncio.sleep(0.2)  # Wait for fade to complete
    
    # Step 2: Show new content
    motion_system.fade_in(new_content)
```

### 5. **Use Staggered Animations for Lists**
```python
# Better than animating all items simultaneously
motion_system.list_item_interactions(
    items=list_items,
    stagger_delay=50,  # Small delay creates pleasing cascade effect
    entrance_direction="up"
)
```

## Performance Considerations

- **Lightweight Implementation**: Minimal overhead, uses Flet's native animation system
- **Async-Safe**: All animations use proper async/await patterns
- **Memory Efficient**: No persistent animation objects, garbage collection friendly
- **Responsive**: Animations respect system performance and accessibility settings

## Demo Applications

### 1. **Motion System Demo** (`motion_system_demo.py`)
Interactive showcase of all animation types and transition patterns.

```bash
python flet_server_gui/motion_system_demo.py
```

### 2. **Integration Example** (`motion_integration_example.py`) 
Practical example showing integration with dashboard components.

```bash
python flet_server_gui/motion_integration_example.py
```

## Migration Guide

### From Basic Flet Animations
```python
# OLD: Basic Flet animation
button.animate_scale = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
button.scale = ft.transform.Scale(1.05)

# NEW: Motion System
motion_system.button_hover_effect(button)
```

### From motion_utils.py
```python
# OLD: motion_utils
from flet_server_gui.utils.motion_utils import create_animation, apply_hover_effect

# NEW: Motion System  
from flet_server_gui.ui.motion_system import create_motion_system
motion_system = create_motion_system(page)
motion_system.button_hover_effect(button)
```

## Troubleshooting

### Common Issues

1. **Animations not working**
   - Ensure page is properly initialized
   - Check that controls are added to page before applying animations
   - Verify async context is available

2. **Jerky animations**
   - Reduce animation complexity
   - Check for conflicting animations
   - Ensure proper timing between sequential animations

3. **Memory leaks**
   - Motion system is designed to avoid leaks
   - Ensure proper cleanup of page overlays (toasts, dialogs)

### Debug Mode
```python
# Enable verbose logging
motion_system.set_debug_mode(True)  # Future feature

# Check animation state
print(f"Reduce motion: {motion_system.should_reduce_motion()}")
```

## Conclusion

The Material Design 3 Motion System provides a comprehensive, performance-optimized solution for adding professional animations to Flet applications. By following Material Design 3 principles, it ensures consistent, accessible, and delightful user experiences across your entire application.

The system is designed to be both powerful for advanced use cases and simple for basic animations, making it suitable for any Flet project seeking to improve user experience through thoughtful motion design.