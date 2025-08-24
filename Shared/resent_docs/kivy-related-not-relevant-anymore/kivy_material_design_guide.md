# KivyMD Material Design 3 Guide

A comprehensive guide for creating beautiful KivyMD applications that follow Google's Material Design 3 guidelines.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Material Design 3 Principles](#material-design-3-principles)
5. [KivyMD Components](#kivymd-components)
6. [Working with Themes](#working-with-themes)
7. [Navigation Patterns](#navigation-patterns)
8. [Responsive Design](#responsive-design)
9. [Best Practices](#best-practices)
10. [Common Patterns](#common-patterns)
11. [Performance Tips](#performance-tips)
12. [Testing & Debugging](#testing--debugging)

## Introduction

KivyMD is a collection of Material Design compliant widgets for use with Kivy, a Python framework for developing multitouch applications. This guide focuses on implementing Material Design 3 (latest version) principles in your Kivy applications.

## Installation

```bash
# Install KivyMD
pip install kivymd

# For development version
pip install git+https://github.com/kivymd/KivyMD.git
```

## Core Concepts

### Basic App Structure

```python
from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
MDScreen:
    MDLabel:
        text: "Hello, KivyMD!"
        halign: "center"
'''

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"  # Or "Light"
        self.theme_cls.primary_palette = "Orange"  # Primary color
        return Builder.load_string(KV)

MainApp().run()
```

### Key Imports

```python
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import MDNavigationDrawer
```

## Material Design 3 Principles

### Color System

Material Design 3 uses a dynamic color system:

1. **Primary** - Main brand color
2. **Secondary** - Supporting color
3. **Tertiary** - Decorative color
4. **Surface** - Background colors
5. **Error** - Color for errors and warnings

```python
# Theme configuration
self.theme_cls.theme_style = "Light"  # or "Dark"
self.theme_cls.primary_palette = "Blue"  # Primary color
self.theme_cls.accent_palette = "Amber"  # Secondary color
```

### Typography

Material Design 3 typography hierarchy:

1. **Display** - Largest text for headers
2. **Headline** - Section headings
3. **Title** - Subheadings
4. **Body** - Paragraph text
5. **Label** - UI element labels

```kv
MDLabel:
    text: "Display Large"
    theme_text_color: "Primary"
    font_style: "Display"
    role: "large"
```

### Elevation & Shadows

Material Design uses elevation to show depth:

```python
from kivymd.uix.card import MDCard

card = MDCard(
    elevation=4,
    shadow_offset=(0, 2),
    radius=[18]
)
```

## KivyMD Components

### Buttons

#### Elevated Button
```kv
MDFillRoundFlatButton:
    text: "Elevated Button"
    icon: "plus"
```

#### Filled Button
```kv
MDFillRoundFlatIconButton:
    text: "Filled Button"
    icon: "content-save"
```

#### Outlined Button
```kv
MDOutlinedButton:
    text: "Outlined Button"
```

#### Text Button
```kv
MDTextButton:
    text: "Text Button"
```

### Text Fields

```kv
MDTextField:
    hint_text: "Enter text"
    helper_text: "This is helper text"
    helper_text_mode: "on_focus"
    mode: "rectangle"
```

### Cards

```kv
MDCard:
    orientation: "vertical"
    size_hint: None, None
    size: "200dp", "150dp"
    elevation: 4
    
    MDLabel:
        text: "Card Title"
        theme_text_color: "Primary"
        
    MDLabel:
        text: "Card content"
        theme_text_color: "Secondary"
```

### Dialogs

```python
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

dialog = MDDialog(
    title="Dialog Title",
    text="Dialog content",
    buttons=[
        MDFlatButton(text="CANCEL"),
        MDFlatButton(text="OK")
    ]
)
dialog.open()
```

### Navigation

#### Bottom Navigation
```kv
MDBottomNavigation:
    
    MDBottomNavigationItem:
        name: "screen1"
        text: "Home"
        icon: "home"
        
        MDLabel:
            text: "Screen 1"
            halign: "center"
            
    MDBottomNavigationItem:
        name: "screen2"
        text: "Account"
        icon: "account"
        
        MDLabel:
            text: "Screen 2"
            halign: "center"
```

#### Navigation Drawer
```kv
MDNavigationDrawer:
    orientation: "vertical"
    
    MDNavigationDrawerMenu:
        
        MDNavigationDrawerHeader:
            title: "Navigation Drawer"
            
        MDNavigationDrawerItem:
            text: "Home"
            icon: "home"
            
        MDNavigationDrawerItem:
            text: "About"
            icon: "information"
```

## Working with Themes

### Dynamic Theming

```python
from kivymd.theming import ThemeManager

class MainApp(MDApp):
    def build(self):
        self.theme_cls = ThemeManager()
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)
        
    def switch_theme_style(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
```

### Custom Colors

```python
self.theme_cls.colors["Yellow"]["500"] = "#FFFF00"
```

## Navigation Patterns

### Screen Manager with Toolbar

```kv
MDScreen:
    
    MDTopAppBar:
        title: "My App"
        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
        
    MDNavigationDrawer:
        id: nav_drawer
        
        MDNavigationDrawerMenu:
            MDNavigationDrawerItem:
                text: "Home"
                icon: "home"
                
    MDScreenManager:
        id: screen_manager
        
        MDScreen:
            name: "home"
```

## Responsive Design

### Adaptive Layouts

```kv
MDBoxLayout:
    orientation: "vertical" if root.width < 600 else "horizontal"
    
    MDLabel:
        text: "Content 1"
        
    MDLabel:
        text: "Content 2"
```

### Size Classes

```python
from kivy.metrics import dp

class ResponsiveWidget(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.width < dp(600):
            self.orientation = "vertical"
        else:
            self.orientation = "horizontal"
```

## Best Practices

### 1. Use KV Language for UI

Separate your UI code from logic:

```python
# main.py
from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
MDScreen:
    MDLabel:
        text: "Hello"
        halign: "center"
'''

class MainApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

MainApp().run()
```

### 2. Efficient Resource Management

```python
# Reuse widgets instead of recreating them
class MainApp(MDApp):
    dialog = None
    
    def show_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(...)
        self.dialog.open()
```

### 3. Follow Material Guidelines

- Use appropriate spacing (8dp grid)
- Maintain color contrast ratios
- Implement proper touch targets (minimum 48dp)
- Apply elevation appropriately

## Common Patterns

### Login Screen

```kv
MDScreen:
    MDBoxLayout:
        orientation: "vertical"
        padding: "50dp"
        spacing: "20dp"
        
        MDTextField:
            hint_text: "Username"
            
        MDTextField:
            hint_text: "Password"
            password: True
            
        MDFillRoundFlatButton:
            text: "Login"
            size_hint_x: 1
```

### List with Items

```kv
MDScreen:
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "My List"
            
        ScrollView:
            MDList:
                id: container
                
<CustomListItem>
    OneLineAvatarListItem:
        text: root.text
        ImageLeftWidget:
            source: root.avatar
```

### Form with Validation

```python
class FormScreen(MDScreen):
    def validate_form(self):
        email = self.ids.email_field.text
        if "@" not in email:
            self.ids.email_field.error = True
            return False
        return True
```

## Performance Tips

### 1. Lazy Loading

```python
# Load heavy components only when needed
class MainApp(MDApp):
    heavy_component = None
    
    def get_heavy_component(self):
        if not self.heavy_component:
            self.heavy_component = HeavyComponent()
        return self.heavy_component
```

### 2. RecycleView for Large Lists

```kv
RecycleView:
    viewclass: "CustomListItem"
    
    RecycleBoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: self.minimum_height
```

### 3. Image Optimization

```python
# Use appropriate image sizes and formats
AsyncImage:
    source: "image.jpg"
    size_hint: None, None
    size: "200dp", "200dp"
    allow_stretch: True
    keep_ratio: True
```

## Testing & Debugging

### Unit Testing

```python
import unittest
from kivy.tests.common import GraphicUnitTest
from kivymd.app import MDApp

class TestApp(GraphicUnitTest):
    def test_button_click(self):
        app = MDApp()
        # Test implementation
```

### Debug Tips

1. Use Kivy Inspector: `python main.py -m inspector`
2. Enable logging: Set `Config.set('kivy', 'log_level', 'debug')`
3. Check for widget lifecycle issues
4. Profile performance with `Clock.schedule_interval` counters

## Conclusion

This guide provides a foundation for building beautiful, Material Design-compliant applications with KivyMD. Remember to:

- Follow Material Design 3 guidelines for consistency
- Use appropriate components for your use cases
- Implement responsive design for multiple screen sizes
- Optimize performance for smooth user experiences
- Test thoroughly across devices and platforms

For the latest information, refer to:
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Material Design 3 Guidelines](https://m3.material.io/)

Happy coding with KivyMD!