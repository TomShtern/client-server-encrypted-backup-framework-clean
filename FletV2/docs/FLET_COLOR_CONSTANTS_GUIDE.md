# Flet 0.28.3 Valid Color Constants Guide

**Date**: January 2025
**Purpose**: Reference guide for valid color constants in Flet 0.28.3 to avoid AttributeError issues

## ✅ Valid Color Constants

### Semantic Colors (Material Design 3)
These colors adapt to the app's theme:

```python
ft.Colors.PRIMARY          # Primary brand color
ft.Colors.SURFACE          # Surface background color
ft.Colors.ON_SURFACE       # Text on surface
ft.Colors.ON_SURFACE_VARIANT  # Muted text on surface (valid!)
ft.Colors.ERROR            # Error state color
ft.Colors.OUTLINE          # Border/outline color
ft.Colors.SURFACE_TINT     # Tinted surface color
```

### Named Colors
Basic color names:

```python
ft.Colors.WHITE
ft.Colors.BLACK
ft.Colors.RED
ft.Colors.GREEN
ft.Colors.BLUE
ft.Colors.YELLOW
ft.Colors.ORANGE
ft.Colors.PURPLE
ft.Colors.GREY
```

### Material Color Shades
Colors with numeric intensity (50-900):

```python
ft.Colors.BLUE_50          # Lightest blue
ft.Colors.BLUE_200         # Light blue
ft.Colors.BLUE_500         # Standard blue
ft.Colors.BLUE_700         # Dark blue
ft.Colors.BLUE_900         # Darkest blue

# Accent variants
ft.Colors.BLUE_ACCENT_100
ft.Colors.BLUE_ACCENT_400
ft.Colors.BLUE_ACCENT_700
```

### Control State Colors
For interactive elements:

```python
ft.ControlState.DEFAULT
ft.ControlState.HOVERED
ft.ControlState.FOCUSED
ft.ControlState.PRESSED
ft.ControlState.SELECTED
```

## ❌ Invalid Color Constants

**DO NOT USE** - These will cause `AttributeError`:

```python
# ❌ WRONG - Don't exist in Flet 0.28.3
ft.Colors.SURFACE_VARIANT         # Use ft.Colors.SURFACE instead
ft.Colors.SURFACE_CONTAINER_LOW   # Use ft.Colors.SURFACE instead
ft.Colors.BACKGROUND              # Use ft.Colors.SURFACE instead
ft.Colors.ON_BACKGROUND           # Use ft.Colors.ON_SURFACE instead
```

## 🎨 Recommended Patterns

### 1. Background Colors
```python
# For card/container backgrounds
bgcolor=ft.Colors.SURFACE

# For subtle background variation
bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE)

# For elevated surfaces
bgcolor=ft.Colors.SURFACE_TINT
```

### 2. Text Colors
```python
# Primary text
color=ft.Colors.ON_SURFACE

# Secondary/muted text
color=ft.Colors.ON_SURFACE_VARIANT  # ✅ This is VALID!

# Disabled text
color=ft.Colors.with_opacity(0.38, ft.Colors.ON_SURFACE)
```

### 3. Interactive Elements
```python
# Hover states
data_row_color={
    ft.ControlState.HOVERED: ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY)
}

# Button states
style=ft.ButtonStyle(
    bgcolor={
        ft.ControlState.DEFAULT: ft.Colors.PRIMARY,
        ft.ControlState.HOVERED: ft.Colors.with_opacity(0.9, ft.Colors.PRIMARY),
    }
)
```

### 4. Borders and Dividers
```python
# Standard borders
border=ft.border.all(1, ft.Colors.OUTLINE)

# Subtle dividers
border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE))
```

## 🔧 Using Opacity

The `with_opacity()` method creates subtle color variations:

```python
# Syntax: ft.Colors.with_opacity(opacity_value, base_color)
ft.Colors.with_opacity(0.5, ft.Colors.RED)    # 50% transparent red
ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY) # Very subtle primary tint

# Also works with hex colors
ft.Colors.with_opacity(0.3, "#FF0000")        # 30% transparent red
```

## 🎭 Theme Integration

### Define Theme Color Scheme
```python
page.theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.Colors.BLUE,
        surface=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
        error=ft.Colors.RED,
    )
)
```

### Use Theme Colors
```python
# These adapt automatically to light/dark theme
ft.Container(bgcolor=ft.Colors.SURFACE)
ft.Text("Hello", color=ft.Colors.ON_SURFACE)
```

## 🚨 Migration Quick Reference

If you encounter these errors, use these replacements:

| Error | Fix |
|-------|-----|
| `ft.Colors.SURFACE_VARIANT` | `ft.Colors.SURFACE` |
| `ft.Colors.SURFACE_CONTAINER_LOW` | `ft.Colors.SURFACE` |
| `ft.Colors.BACKGROUND` | `ft.Colors.SURFACE` |
| `ft.Colors.ON_BACKGROUND` | `ft.Colors.ON_SURFACE` |
| Need subtle variation | `ft.Colors.with_opacity(0.05, ft.Colors.SURFACE)` |

## 📚 References

- **Official Flet Docs**: https://flet.dev/docs/
- **Material Design 3 Colors**: https://m3.material.io/styles/color
- **This Fix Applied**: January 2025 - Fixed all SURFACE_VARIANT references

## 🔍 Verification Command

Check for invalid color constants in your codebase:

```bash
# Search for problematic patterns
rg "SURFACE_VARIANT|SURFACE_CONTAINER_LOW|Colors\.BACKGROUND" FletV2/
```

---

**Key Takeaway**: Always use `ft.Colors.SURFACE` for backgrounds and `ft.Colors.ON_SURFACE` for text. Use `with_opacity()` for subtle variations. The `ON_SURFACE_VARIANT` constant IS valid for muted text colors.
