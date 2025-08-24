# KivyMD Reference Documentation

**Status**: Legacy GUI framework (replaced by Flet)
**Purpose**: Reference documentation for historical KivyMD implementation

## KivyMD 2.0.x API Reference

### Key Version Information
- **KivyMD Version**: Commit `d2f7740` (stable, prevents animation crashes)
- **Kivy Version**: 2.3.1 (tested compatibility)
- **Material Design**: Version 3 specification compliance
- **Font System**: Supports Display, Headline, Title, Body, Label styles only

### Critical Import Path Changes
```python
# ✅ CORRECT 2.0.x imports:
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarLeadingButtonContainer, MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem, MDNavigationRailItemIcon, MDNavigationRailItemLabel
from kivymd.uix.selectioncontrol import MDSwitch  # NOT kivymd.uix.switch
from kivymd.uix.textfield import MDTextField, MDTextFieldSupportingText
```

### Component Migration Patterns

#### MDTopAppBar (Component-Based Architecture)
```python
# ❌ OLD (1.x): 
MDTopAppBar(title="My Title", left_action_items=[...])

# ✅ NEW (2.0.x):
MDTopAppBar(
    MDTopAppBarLeadingButtonContainer(
        MDActionTopAppBarButton(icon="menu", on_release=callback)
    ),
    MDTopAppBarTitle(text="My Title"),
    MDTopAppBarTrailingButtonContainer(
        MDActionTopAppBarButton(icon="refresh", on_release=callback)
    ),
    type="small"  # Options: "small", "medium", "large"
)
```

#### MDNavigationRail (Component-Based Navigation)
```python
# ❌ OLD (1.x): 
MDNavigationRailItem(icon="dashboard", text="Dashboard", on_release=callback)

# ✅ NEW (2.0.x):
nav_item = MDNavigationRailItem(
    MDNavigationRailItemIcon(icon="dashboard"),
    MDNavigationRailItemLabel(text="Dashboard")
)
nav_item.bind(active=lambda instance, value, screen="dashboard": navigate_to_screen(screen) if value else None)
```

#### MDTextField (Component-Based Supporting Text)
```python
# ❌ OLD (1.x): 
MDTextField(helper_text="Default: 1256", ...)

# ✅ NEW (2.0.x):
MDTextField(
    MDTextFieldSupportingText(text="Default: 1256"),
    mode="outlined",
    hint_text="Port number"
)
```

### Critical Text Rendering Fix (BREAKTHROUGH)
**Root Cause**: KivyMD's default `text_size=(self.width, None)` and invalid `role` properties cause vertical character stacking
**Solution**: MD3Label component with proper text_size handling:

```python
# CRITICAL FIX in MD3Label
if 'text_size' not in kwargs:
    self.text_size = (None, None)
    Clock.schedule_once(lambda dt: setattr(self, 'text_size', (None, None)), 0.1)
```

**CRITICAL RULE**: Never use `role` properties on KivyMD labels - they break text rendering

### Dynamic Updates (2.0.x Compatible)
```python
# Update MDTopAppBarTitle text dynamically
for child in self.top_bar.children:
    if hasattr(child, 'text') and 'Title' in child.__class__.__name__:
        child.text = "New Title"
        break

# Update MDTextFieldSupportingText dynamically
for child in textfield.children:
    if hasattr(child, 'text') and 'SupportingText' in child.__class__.__name__:
        child.text = "New supporting text"
        break
```

### Unicode & Font Support
```python
# ✅ CORRECT: Use MD3Label with Unicode support
from kivymd_gui.components.md3_label import MD3Label, create_hebrew_label, create_emoji_label

hebrew_label = create_hebrew_label("שלום עולם")  # Hebrew support
emoji_label = create_emoji_label("🎉 ✅ ❌")     # Emoji support  
mixed_label = create_md3_label("✅ Server | שרת 🎉")  # Auto font selection
```

### Material Design 3 Token System
```python
# Token-driven component creation
from kivymd_gui.components import create_md3_button, create_md3_card, get_token_value

button = create_md3_button("Start Server", variant="filled", tone="primary")
card = create_md3_card(variant="elevated")
primary_color = get_token_value('palette.primary')  # "#1976D2"
```

### Setup Commands
```bash
# CRITICAL: Must use kivy_venv_new virtual environment
python -m venv kivy_venv_new
.\kivy_venv_new\Scripts\activate

# Install stable KivyMD commit
pip install git+https://github.com/kivymd/KivyMD.git@d2f7740
pip install psutil==7.0.0 materialyoucolor==2.0.10 kivy==2.3.1

# Run KivyMD GUI
python kivymd_gui\main.py
```

### Common Errors & Solutions
```bash
# Error: "No module named 'kivymd.uix.topappbar'"
# Solution: Update import to kivymd.uix.appbar

# Error: Text rendering vertically (character-by-character)
# Solution: Remove ALL role properties from KivyMD labels

# Error: NavigationRail animation crashes
# Solution: Use stable commit d2f7740

# Emergency Recovery
.\kivy_venv_new\Scripts\activate
pip uninstall kivymd -y
pip install git+https://github.com/kivymd/KivyMD.git@d2f7740
```

### VS Code Type Stub Solution
```json
{
    "python.analysis.stubPath": "./stubs",
    "python.defaultInterpreterPath": "./kivy_venv_new/Scripts/python.exe"
}
```

### Key Migration Insights
1. **Import Path Migration**: All major components moved in 2.0.x
2. **Component Architecture**: Shift from parameter-based to component-based design
3. **Property Cleanup**: Many legacy properties removed
4. **Event Handling**: Changed from direct callbacks to binding patterns
5. **Text Rendering**: Requires custom MD3Label component to prevent vertical stacking
6. **No Role Properties**: Invalid role properties break text rendering completely