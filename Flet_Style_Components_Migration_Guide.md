# Migration Guide: Enhanced Components to Flet-Style Components

## Overview
This guide helps developers migrate from the original enhanced components to the new Flet-style components that follow Flet's recommended best practices.

## Why Migrate?
1. **Better Integration**: Flet-style components integrate more seamlessly with Flet's ecosystem
2. **Improved Developer Experience**: More intuitive API for developers familiar with Flet
3. **Easier Maintenance**: Simpler codebase that's easier to maintain and extend
4. **Better Performance**: Leverages Flet's optimized implementations
5. **Consistent Behavior**: Components behave consistently with other Flet controls

## Migration Path

### Buttons

#### Original EnhancedButton Usage
```python
from flet_server_gui.ui.widgets.enhanced_buttons import EnhancedButton, EnhancedButtonConfig

config = EnhancedButtonConfig(
    text="Click Me",
    variant="filled",
    size="medium"
)
button = EnhancedButton(page, config)
```

#### New Flet-Style Usage
```python
from flet_server_gui.ui.widgets import EnhancedFilledButton

button = EnhancedFilledButton(
    text="Click Me",
    size="medium"
)
```

#### Migration Table
| Original Component | New Flet-Style Component | Notes |
|-------------------|-------------------------|-------|
| EnhancedButton with variant="filled" | EnhancedFilledButton | Direct replacement |
| EnhancedButton with variant="tonal" | EnhancedFilledButton (use style customization) | Use ButtonStyle for tonal appearance |
| EnhancedButton with variant="outlined" | EnhancedOutlinedButton | Direct replacement |
| EnhancedButton with variant="text" | EnhancedTextButton | Direct replacement |
| EnhancedButton with variant="icon" | EnhancedIconButton | Direct replacement |
| EnhancedButton with variant="fab" | EnhancedFloatingActionButton | Direct replacement |

#### Convenience Functions
| Original Function | New Flet-Style Function |
|------------------|------------------------|
| create_primary_button | create_flet_style_primary_button |
| create_secondary_button | create_flet_style_secondary_button |
| create_outline_button | create_flet_style_text_button |
| create_text_button | create_flet_style_icon_button |
| create_icon_button | create_flet_style_fab_button |

### Cards

#### Original EnhancedCard Usage
```python
from flet_server_gui.ui.widgets.enhanced_cards import EnhancedCard, EnhancedCardConfig

config = EnhancedCardConfig(
    title="Card Title",
    content="Card content",
    size="medium"
)
card = EnhancedCard(page, config)
```

#### New Flet-Style Usage
```python
from flet_server_gui.ui.widgets import FletStyleEnhancedCard

card = FletStyleEnhancedCard(
    title="Card Title",
    content="Card content",
    size="medium"
)
```

#### Migration Table
| Original Component | New Flet-Style Component |
|-------------------|-------------------------|
| EnhancedCard | FletStyleEnhancedCard |
| StatCard | FletStyleStatCard |
| DataCard | FletStyleDataCard |

### Dialogs

#### Original EnhancedDialog Usage
```python
from flet_server_gui.ui.widgets.enhanced_dialogs import EnhancedDialog, DialogConfig

config = DialogConfig(
    title="Dialog Title",
    content="Dialog content",
    dialog_type="info"
)
dialog = EnhancedDialog(page, config)
```

#### New Flet-Style Usage
```python
from flet_server_gui.ui.widgets import FletStyleEnhancedDialog

dialog = FletStyleEnhancedDialog(
    title="Dialog Title",
    content="Dialog content",
    dialog_type="info"
)
```

#### Migration Table
| Original Component | New Flet-Style Component |
|-------------------|-------------------------|
| EnhancedDialog | FletStyleEnhancedDialog |
| EnhancedAlertDialog | FletStyleEnhancedAlertDialog |

## Code Changes Required

### 1. Import Statements
Change from:
```python
from flet_server_gui.ui.widgets.enhanced_buttons import EnhancedButton
from flet_server_gui.ui.widgets.enhanced_cards import EnhancedCard
from flet_server_gui.ui.widgets.enhanced_dialogs import EnhancedDialog
```

To:
```python
from flet_server_gui.ui.widgets import EnhancedFilledButton, FletStyleEnhancedCard, FletStyleEnhancedDialog
```

### 2. Instantiation
Change from:
```python
config = EnhancedButtonConfig(text="Click Me", variant="filled")
button = EnhancedButton(page, config)
```

To:
```python
button = EnhancedFilledButton(text="Click Me")
```

### 3. Method Calls
Most methods remain the same, but some may have slight differences:
- `set_state()` - Available in both
- `set_text()` - Available in both
- `get_control()` - Not needed in Flet-style components (they ARE Flet controls)

## Backward Compatibility
The original enhanced components are still available and working, so you can migrate gradually:
- Existing code continues to work without changes
- New code can use the Flet-style components
- Both can coexist in the same application

## Benefits of Migration

### 1. Simpler Code
```python
# Before (3 lines)
config = EnhancedButtonConfig(text="Click Me", variant="filled")
button = EnhancedButton(page, config)
flet_control = button.get_control()

# After (1 line)
button = EnhancedFilledButton(text="Click Me")
```

### 2. Better Flet Integration
Flet-style components ARE Flet controls, so they work seamlessly with Flet's layout and event systems.

### 3. Improved Performance
Leverages Flet's optimized implementations rather than wrapper classes.

### 4. Easier Debugging
Fewer layers of abstraction make it easier to debug issues.

## Testing Migration
1. Start by migrating simple components like buttons
2. Test each migrated component individually
3. Gradually migrate more complex components
4. Run existing tests to ensure no regressions
5. Test new functionality with Flet-style components

## Support
If you encounter any issues during migration, refer to:
1. The Flet documentation for the base components
2. The Flet-Style Components Documentation
3. The original enhanced components as reference

The Flet-style components maintain the same functionality while following Flet's best practices, so migration should be straightforward.