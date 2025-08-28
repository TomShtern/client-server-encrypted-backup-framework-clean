# Material Design 3 Component Factory

A comprehensive factory for creating Material Design 3 compliant components with proper theme integration, state layers, and responsive design.

## 🎯 Overview

The M3 Component Factory provides a unified interface for creating Material Design 3 components that seamlessly integrate with your existing Flet Server GUI theme system. All components follow Material Design 3 specifications and support responsive design out of the box.

## ✨ Features

### Component Types
- **Buttons**: Filled, Outlined, Text, Elevated, Tonal
- **Cards**: Elevated, Filled, Outlined
- **Input Components**: TextField, DropDown, Checkbox, Switch
- **Data Display**: DataTable, ListTile
- **Navigation**: NavigationRail (planned)

### Material Design 3 Compliance
- ✅ State layers for interactive feedback
- ✅ Proper elevation system (0-12dp)
- ✅ M3 color roles integration
- ✅ Typography scale compliance
- ✅ Corner radius specifications
- ✅ Responsive design support

### Theme Integration
- ✅ Automatic integration with existing theme system
- ✅ Light/dark theme support
- ✅ Color role resolution
- ✅ Typography token application
- ✅ Fallback mode for standalone usage

## 🚀 Quick Start

### Basic Usage

```python
import flet as ft
from ui.m3_components import get_m3_factory

def main(page: ft.Page):
    # Get the global M3 factory instance
    factory = get_m3_factory()
    
    # Create M3 compliant buttons
    filled_button = factory.create_button("filled", "Primary Action", icon=ft.Icons.STAR)
    outlined_button = factory.create_button("outlined", "Secondary Action")
    
    # Create M3 compliant cards
    card = factory.create_card(
        style="elevated",
        title="Card Title",
        subtitle="Card subtitle",
        content=ft.Text("Card content here...")
    )
    
    # Create M3 compliant inputs
    text_field = factory.create_text_field("Enter your name", hint_text="Full name")
    
    page.add(ft.Column([filled_button, outlined_button, card, text_field]))

ft.app(target=main)
```

### Convenience Functions

```python
from ui.m3_components import create_m3_button, create_m3_card, create_m3_text_field

# Quick component creation
button = create_m3_button("filled", "Click Me", icon=ft.Icons.THUMB_UP)
card = create_m3_card("elevated", content=ft.Text("Hello World"))
field = create_m3_text_field("Email Address", hint_text="user@example.com")
```

## 📚 API Reference

### M3ComponentFactory

The main factory class for creating Material Design 3 components.

#### Methods

##### `create_button(style, text="", icon=None, on_click=None, config=None, **kwargs)`

Create a Material Design 3 compliant button.

**Parameters:**
- `style` (str|ComponentStyle): Button style - "filled", "outlined", "text", "elevated", "tonal"
- `text` (str): Button text
- `icon` (str): Button icon (ft.Icons constant)
- `on_click` (callable): Click event handler
- `config` (M3ButtonConfig): Advanced button configuration
- `**kwargs`: Additional Flet button properties

**Returns:** `ft.Control` - M3 compliant button

**Example:**
```python
# Simple button
button = factory.create_button("filled", "Save Document", icon=ft.Icons.SAVE)

# Advanced configuration
config = M3ButtonConfig(
    style=ComponentStyle.FILLED,
    text="Upload File",
    icon=ft.Icons.UPLOAD,
    size="large",
    full_width=True
)
button = factory.create_button("filled", config=config)
```

##### `create_card(style, content=None, title=None, config=None, **kwargs)`

Create a Material Design 3 compliant card.

**Parameters:**
- `style` (str|ComponentStyle): Card style - "elevated", "filled", "outlined"
- `content` (ft.Control): Card content control
- `title` (str): Optional card title
- `config` (M3CardConfig): Advanced card configuration
- `**kwargs`: Additional Flet card properties

**Returns:** `ft.Control` - M3 compliant card

**Example:**
```python
# Simple card
card = factory.create_card(
    style="elevated",
    title="User Profile",
    content=ft.Text("Profile information here...")
)

# Advanced configuration
config = M3CardConfig(
    style=ComponentStyle.ELEVATED_CARD,
    title="Settings",
    subtitle="Application preferences",
    clickable=True,
    actions=[
        factory.create_button("text", "Cancel"),
        factory.create_button("text", "Save")
    ]
)
card = factory.create_card("elevated", config=config)
```

##### `create_text_field(label, hint_text=None, value=None, **kwargs)`

Create a Material Design 3 compliant text field.

**Parameters:**
- `label` (str): Field label
- `hint_text` (str): Placeholder text
- `value` (str): Initial value
- `**kwargs`: Additional Flet TextField properties

**Returns:** `ft.TextField` - M3 compliant text field

##### `create_dropdown(label, options, value=None, **kwargs)`

Create a Material Design 3 compliant dropdown.

**Parameters:**
- `label` (str): Dropdown label
- `options` (List[ft.dropdown.Option]): Dropdown options
- `value` (str): Selected value
- `**kwargs`: Additional Flet Dropdown properties

**Returns:** `ft.Dropdown` - M3 compliant dropdown

##### `create_checkbox(label=None, value=None, **kwargs)`

Create a Material Design 3 compliant checkbox.

**Parameters:**
- `label` (str): Optional checkbox label
- `value` (bool): Initial checked state
- `**kwargs`: Additional Flet Checkbox properties

**Returns:** `ft.Control` - M3 compliant checkbox (with label if provided)

##### `create_switch(label=None, value=None, **kwargs)`

Create a Material Design 3 compliant switch.

**Parameters:**
- `label` (str): Optional switch label
- `value` (bool): Initial state
- `**kwargs`: Additional Flet Switch properties

**Returns:** `ft.Control` - M3 compliant switch (with label if provided)

##### `create_data_table(columns, rows, **kwargs)`

Create a Material Design 3 compliant data table.

**Parameters:**
- `columns` (List[ft.DataColumn]): Table columns
- `rows` (List[ft.DataRow]): Table rows
- `**kwargs`: Additional Flet DataTable properties

**Returns:** `ft.DataTable` - M3 compliant data table

### Configuration Classes

#### M3ButtonConfig

Extended configuration for M3 buttons.

```python
@dataclass
class M3ButtonConfig(M3ComponentConfig):
    text: str = ""
    icon: Optional[str] = None
    icon_placement: str = "leading"  # "leading" or "trailing"
    size: str = "medium"  # "small", "medium", "large"
    full_width: bool = False
    on_click: Optional[Callable] = None
    disabled: bool = False
    loading: bool = False
    custom_colors: Optional[Dict[str, str]] = None
```

#### M3CardConfig

Extended configuration for M3 cards.

```python
@dataclass
class M3CardConfig(M3ComponentConfig):
    content: Optional[ft.Control] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    actions: Optional[List[ft.Control]] = None
    padding: Optional[int] = None
    content_padding: Optional[int] = None
    clickable: bool = False
    on_click: Optional[Callable] = None
```

## 🎨 Theme Integration

### Automatic Theme Resolution

The M3 Component Factory automatically integrates with your existing theme system:

```python
# The factory automatically uses your current theme
factory = get_m3_factory()

# Colors are resolved from your theme system
# Light mode: Uses light color tokens
# Dark mode: Uses dark color tokens

# Typography follows your typography scale
# Spacing uses your spacing tokens
# Elevation follows your elevation system
```

### Color Roles

The factory uses Material Design 3 color roles:

- **Primary**: Main brand color
- **Secondary**: Secondary brand color  
- **Tertiary**: Accent color
- **Surface**: Background surfaces
- **Error**: Error states
- **Outline**: Borders and dividers

### Fallback Mode

If the theme system is not available, the factory provides sensible fallbacks:

```python
# Automatic fallback colors and styling
# Still provides M3 compliant components
# Works standalone without theme system
```

## 🔧 Advanced Usage

### Custom Component Styling

```python
# Apply custom elevation
factory.apply_m3_elevation(component, level="level3")

# Apply custom shape
factory.apply_m3_shape(component, corner_radius="lg")

# Create custom component theme
theme = factory.create_component_theme(base_color="#FF6B35")
```

### Responsive Design

All components support responsive design by default:

```python
# Components automatically adapt to container size
# Use expand=True for full-width components
# Responsive breakpoints handled automatically

button = factory.create_button(
    style="filled",
    text="Responsive Button",
    config=M3ButtonConfig(
        full_width=True,  # Expands to container width
        responsive=True   # Enables responsive behavior
    )
)
```

### Integration with Existing Components

```python
# Mix M3 components with existing components
from ui.widgets.buttons import ActionButtonFactory

def create_mixed_interface():
    # Use M3 for new components
    m3_factory = get_m3_factory()
    save_button = m3_factory.create_button("filled", "Save")
    
    # Keep existing components working
    action_factory = ActionButtonFactory()
    existing_button = action_factory.create_button("client_export")
    
    return ft.Row([save_button, existing_button])
```

## 🧪 Testing & Validation

### Run Validation Tests

```bash
# Validate M3 factory integration
python flet_server_gui/validate_m3_factory.py

# Run integration demo
python flet_server_gui/integration_example_m3.py

# Run full component demo
python flet_server_gui/demo_m3_components.py
```

### Expected Output

```
✅ ALL TESTS PASSED! M3 Component Factory is ready for use.

Integration Notes:
• Use get_m3_factory() to get the global factory instance
• Use convenience functions (create_m3_button, etc.) for quick component creation
• Factory automatically integrates with existing theme system
• All components follow Material Design 3 specifications
• Responsive design is enabled by default
```

## 📖 Examples

### Complete Button Showcase

```python
def create_button_showcase():
    factory = get_m3_factory()
    
    return ft.Column([
        # All button variants
        factory.create_button("filled", "Filled Button", icon=ft.Icons.STAR),
        factory.create_button("outlined", "Outlined Button", icon=ft.Icons.FAVORITE),
        factory.create_button("text", "Text Button", icon=ft.Icons.SETTINGS),
        factory.create_button("elevated", "Elevated Button", icon=ft.Icons.THUMB_UP),
        factory.create_button("tonal", "Tonal Button", icon=ft.Icons.PALETTE),
    ])
```

### Card Layout Example

```python
def create_card_layout():
    factory = get_m3_factory()
    
    return ft.ResponsiveRow([
        ft.Column([
            factory.create_card(
                style="elevated",
                title="Statistics",
                content=ft.Column([
                    ft.Text("Active Users: 1,234"),
                    ft.Text("Total Files: 5,678"),
                ])
            )
        ], col={"sm": 12, "md": 6}),
        
        ft.Column([
            factory.create_card(
                style="filled", 
                title="Recent Activity",
                content=ft.Text("Last backup: 2 hours ago")
            )
        ], col={"sm": 12, "md": 6}),
    ])
```

### Form Components Example

```python
def create_form():
    factory = get_m3_factory()
    
    return ft.Column([
        factory.create_text_field("Full Name", hint_text="Enter your full name"),
        factory.create_text_field("Email", hint_text="user@example.com"),
        factory.create_dropdown(
            label="Country",
            options=[
                ft.dropdown.Option("United States"),
                ft.dropdown.Option("Canada"),
                ft.dropdown.Option("United Kingdom"),
            ]
        ),
        factory.create_checkbox(label="Subscribe to newsletter", value=True),
        factory.create_switch(label="Enable notifications", value=False),
        ft.Row([
            factory.create_button("text", "Cancel"),
            factory.create_button("filled", "Submit", icon=ft.Icons.SEND),
        ], alignment=ft.MainAxisAlignment.END)
    ], spacing=16)
```

## 🔄 Migration Guide

### From Standard Flet Components

```python
# Before (Standard Flet)
button = ft.FilledButton("Click Me", icon=ft.Icons.STAR, on_click=handler)
card = ft.Card(content=ft.Text("Content"))

# After (M3 Factory)
factory = get_m3_factory()
button = factory.create_button("filled", "Click Me", icon=ft.Icons.STAR, on_click=handler)
card = factory.create_card("elevated", content=ft.Text("Content"))
```

### From Existing Button Factory

```python
# Before (ActionButtonFactory)
from ui.widgets.buttons import ActionButtonFactory
factory = ActionButtonFactory()
button = factory.create_action_button("client_export")

# After (Combined Usage)
from ui.m3_components import get_m3_factory
m3_factory = get_m3_factory()
action_factory = ActionButtonFactory()

# Use M3 for new UI components
ui_button = m3_factory.create_button("filled", "New Feature")

# Keep action buttons for business logic
action_button = action_factory.create_action_button("client_export")
```

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
```python
# If you get import errors, the factory has robust fallbacks
# It will work even without the theme system
# Check validation output for specific issues
```

**Theme Not Applied**
```python
# Ensure theme system is properly initialized
from core.theme_system import get_theme_system
theme_system = get_theme_system()

# Factory will use fallbacks if theme system unavailable
factory = get_m3_factory()
```

**Component Styling Issues**
```python
# Factory uses current Flet API compatibility
# Some advanced MaterialState features may use simplified versions
# All components are tested for compatibility
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Factory will log debug information
# Including theme integration status
# And fallback usage
```

## 📄 License

This M3 Component Factory is part of the Client-Server Encrypted Backup Framework and follows the same licensing terms as the main project.

---

**🎨 Material Design 3 Component Factory - Production Ready**  
**✅ Fully integrated with existing theme system**  
**🔧 Backward compatible with existing components**  
**📱 Responsive design by default**  
**🎯 100% Material Design 3 compliant**