# Theme Customization Guide

## How to Easily Change Colors Throughout the Application

The theme system is fully parameterized, meaning you can change any color in one place and it will automatically update throughout the entire application.

## Theme File Location

All theme customization is done in:
`flet_server_gui/ui/theme_m3.py`

## Color Tokens Dictionary

The `TOKENS` dictionary at the top of the file contains all customizable colors:

```python
TOKENS = {
    # Primary: blue → purple gradient
    "primary_gradient": ["#A8CBF3", "#7C5CD9"],  # light blue to purple
    "primary": "#7C5CD9",  # fallback solid primary (purple)
    "on_primary": "#FFFFFF",
    
    # Secondary: orange
    "secondary": "#FCA651",
    "on_secondary": "#000000",
    
    # Tertiary: pink-ish
    "tertiary": "#AB6DA4",
    "on_tertiary": "#FFFFFF",
    
    # Containers (teal for the "file page" background)
    "container": "#38A298",
    "on_container": "#FFFFFF",
    
    # Surface tones
    "surface": "#F6F8FB",            # main surface (light)
    "surface_variant": "#E7EDF7",    # subtle variant
    "surface_dark": "#0F1720",       # main dark surface
    "background": "#FFFFFF",
    "on_background": "#000000",
    "outline": "#666666",
    
    # Error
    "error": "#B00020",
    "on_error": "#FFFFFF"
}
```

## How to Change Colors

### 1. Open the Theme File
Navigate to `flet_server_gui/ui/theme_m3.py`

### 2. Edit the TOKENS Dictionary
Change any hex color value to your desired color:

For example, to change the secondary color from orange to green:
```python
# Before:
"secondary": "#FCA651",

# After:
"secondary": "#4CAF50",  # Green 500
```

### 3. Save and Restart
Save the file and restart the application. All components using that color will automatically update.

## Color Usage in Components

Components access theme colors through:
1. `page.theme.color_scheme.[color_name]` - For automatic Material Design 3 colors
2. `TOKENS.[color_name]` - For direct token access when needed
3. Theme utility functions - For consistent styling

## Examples of Automatic Updates

When you change a token, these components automatically update:

- **Secondary Color (`#FCA651` → `#4CAF50`)**:
  - Stop button turns from orange to green when server is running
  - Any other component using secondary color updates automatically

- **Tertiary Color (`#AB6DA4` → `#2196F3`)**:
  - Warning messages in logs turn from pinkish-red to blue
  - Active transfers count turns from pinkish-red to blue

- **Container Color (`#38A298` → `#FF9800`)**:
  - Database size card background turns from teal to orange
  - Any other container using this color updates automatically

## Best Practices

1. **Maintain Contrast**: Ensure text colors (`on_[color]`) have sufficient contrast with their backgrounds
2. **Consistent Palette**: Keep colors harmonious with your overall design system
3. **Test Changes**: Always test color changes to ensure readability and accessibility
4. **Document Changes**: Comment significant color changes for future reference

## Example: Complete Theme Makeover

To change the entire application to a red/black theme:

```python
TOKENS = {
    # Primary: red gradient
    "primary_gradient": ["#FF8A80", "#D32F2F"],  # light red to dark red
    "primary": "#D32F2F",  # dark red
    "on_primary": "#FFFFFF",
    
    # Secondary: black
    "secondary": "#212121",  # dark grey/black
    "on_secondary": "#FFFFFF",
    
    # Tertiary: white
    "tertiary": "#FFFFFF",
    "on_tertiary": "#000000",
    
    # Containers (dark grey)
    "container": "#424242",
    "on_container": "#FFFFFF",
    
    # Surface tones (black theme)
    "surface": "#121212",            # dark surface
    "surface_variant": "#1E1E1E",    # slightly lighter variant
    "surface_dark": "#000000",       # pure black
    "background": "#000000",
    "on_background": "#FFFFFF",
    "outline": "#757575",
    
    # Error (keeping red for errors)
    "error": "#B00020",
    "on_error": "#FFFFFF"
}
```

This single change will transform the entire application's color scheme!

## Components That Use Each Color

### Primary (`#7C5CD9`)
- Online status indicator
- Success messages
- Primary action buttons
- Active navigation items

### Secondary (`#FCA651`)
- Stop button when server is running
- Important action buttons
- Highlighted UI elements

### Tertiary (`#AB6DA4`)
- Warning messages
- Special status indicators
- Accent elements

### Container (`#38A298`)
- Database size card background
- Special container backgrounds
- Section headers

### Surface Colors
- Main backgrounds
- Cards
- Dialogs
- Text surfaces

Any change to these tokens will instantly propagate throughout the entire application!