# Material Design 3 Implementation Guide

Complete reference for the token-driven M3 architecture implemented in the KivyMD GUI.

## Architecture Overview

The implementation follows Google's Material Design 3 specifications with a **token-driven architecture** that ensures consistency, accessibility, and maintainability.

### Key Components

1. **Design Tokens (`tokens.json`)** - Canonical source of truth for all visual decisions
2. **Adapter Layer** - Components that enforce M3 specifications via tokens
3. **Automated QA** - Comprehensive compliance validation system
4. **Theme Integration** - Seamless integration with existing KivyMD theming

## Design Tokens System

### Token Categories

```json
{
  "palette": {           // M3 color system
    "primary": "#1976D2",
    "on_primary": "#FFFFFF",
    "primary_container": "#D1E4FF",
    // ... complete M3 color roles
  },
  "shape": {             // Corner radius tokens
    "corner_small": 6,
    "corner_medium": 12,
    "corner_large": 16
  },
  "elevation": {         // Shadow levels
    "level0": 0,
    "level1": 1,
    "level2": 3
  },
  "typography": {        // Text styles
    "body_medium": {
      "size": 14,
      "line_height": 20,
      "weight": "regular"
    }
  },
  "motion": {            // Animation durations
    "micro": 100,
    "short": 160,
    "standard": 250
  },
  "spacing": {           // Layout grid
    "grid": 8,
    "gutter": 16
  }
}
```

### Token Usage

```python
from kivymd_gui.components import get_token_value

# Access any token using dot notation
primary_color = get_token_value('palette.primary')
card_radius = get_token_value('shape.corner_medium')
button_height = get_token_value('component_tokens.button.height')
```

## M3 Adapter Components

### MD3Button

```python
from kivymd_gui.components import create_md3_button

# Semantic variants
primary_button = create_md3_button("Save", variant="filled", tone="primary")
secondary_button = create_md3_button("Cancel", variant="outlined", tone="secondary")
text_button = create_md3_button("Learn More", variant="text", tone="primary")

# Automatic token enforcement:
# - Radius from tokens.component_tokens.button.radius
# - Height from tokens.component_tokens.button.height
# - Colors from tokens.palette based on tone
# - Touch target ≥48dp validation
```

### MD3Card

```python
from kivymd_gui.components import create_md3_card

# Surface variants
surface_card = create_md3_card(variant="surface")      # elevation=0
elevated_card = create_md3_card(variant="elevated")    # elevation=1
outlined_card = create_md3_card(variant="outlined")    # with border

# Automatic token enforcement:
# - Radius from tokens.component_tokens.card.radius
# - Padding from tokens.component_tokens.card.padding
# - Colors from tokens.palette
# - Responsive adjustments based on screen size
```

### MD3TextField

```python
from kivymd_gui.components import create_md3_textfield

# Field modes
outlined_field = create_md3_textfield("Enter name", field_mode="outlined")
filled_field = create_md3_textfield("Search...", field_mode="filled")

# Specialized fields
search_field = create_search_field("Search items...")
number_field = create_number_field("Port", min_value=1, max_value=65535)

# Automatic token enforcement:
# - Height from tokens.component_tokens.text_field.height
# - Typography from tokens.typography.body_large
# - Colors from tokens.palette
# - Error state styling
```

## Migration Guide

### From Raw KivyMD to M3 Adapters

```python
# ❌ OLD: Raw KivyMD widgets
button = MDRaisedButton(
    text="Save",
    md_bg_color="#1976D2",
    radius=[20],
    height=dp(40)
)

# ✅ NEW: M3 adapter with automatic token compliance
button = create_md3_button("Save", variant="filled", tone="primary")
```

### Component Replacement Map

| Raw KivyMD Widget | M3 Adapter | Benefits |
|-------------------|------------|----------|
| `MDRaisedButton` | `MD3Button` | Token-driven styling, semantic variants |
| `MDCard` | `MD3Card` | Responsive design, elevation tokens |
| `MDTextField` | `MD3TextField` | Typography tokens, error handling |
| `MDIconButton` | `MD3IconButton` | Touch target validation, color tokens |

## Best Practices

### 1. Token-First Development

```python
# ✅ CORRECT: Read from tokens
radius = get_token_value('shape.corner_medium')
self.radius = [radius]

# ❌ INCORRECT: Hardcoded values
self.radius = [12]  # This bypasses the design system
```

### 2. Semantic Component Usage

```python
# ✅ CORRECT: Use semantic variants
primary_action = create_md3_button("Save", variant="filled", tone="primary")
secondary_action = create_md3_button("Cancel", variant="outlined")

# ❌ INCORRECT: Manual color assignment
button.md_bg_color = "#1976D2"  # Bypasses semantic color system
```

### 3. Responsive Design

```python
# ✅ CORRECT: Components automatically adjust to screen size
card = create_md3_card(variant="elevated")
# Radius and padding scale automatically for mobile/tablet/desktop

# ❌ INCORRECT: Fixed sizing
card.radius = [12]  # No responsiveness
```

## Accessibility Compliance

### WCAG AA Standards

- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Touch Targets**: Minimum 48dp in at least one dimension
- **Focus Indicators**: Visible keyboard navigation support
- **Semantic Structure**: Proper labels and hints for screen readers

### Automated Validation

```python
from kivymd_gui.qa import run_accessibility_checks

# Run accessibility validation
report = run_accessibility_checks(components)
print(f"Compliance Score: {report['summary']['compliance_score']}/100")

# Check specific issues
for error in report['issues']['errors']:
    print(f"❌ {error['description']}")
```

## Quality Assurance

### Running QA Checks

```bash
# Complete M3 compliance validation
kivy_venv_new/Scripts/python.exe kivymd_gui/qa/test_qa_system.py

# Individual checks
python -c "from kivymd_gui.qa import run_accessibility_checks; run_accessibility_checks()"
```

### QA Validation Areas

1. **Design Token Usage** - Ensures components use tokens, not hardcoded values
2. **Color Contrast** - WCAG AA compliance for all text/background combinations
3. **Touch Targets** - Minimum 48dp interactive element validation
4. **Spacing Grid** - 8dp baseline grid alignment checking
5. **Motion Compliance** - Animation duration limits (<300ms for micro-interactions)
6. **Component Adapter Usage** - Prevents raw KivyMD widget usage

### Compliance Scoring

- **95-100**: Excellent M3 compliance
- **85-94**: Good compliance, minor issues
- **70-84**: Fair compliance, needs improvement
- **50-69**: Poor compliance, significant issues
- **<50**: Critical compliance problems

## Troubleshooting

### Common Issues

```python
# Issue: Import errors with KivyMD 2.0.x
# Solution: Use correct import paths for adapters
from kivymd_gui.components import MD3Button  # ✅ Correct

# Issue: Token not found
# Solution: Check token path exists in tokens.json
value = get_token_value('palette.primary', fallback="#1976D2")

# Issue: Accessibility failures
# Solution: Use M3 adapters instead of raw widgets
button = create_md3_button("Text", variant="filled")  # Auto-compliant
```

### Validation Failures

```bash
# If QA checks fail:
1. Review the generated report in kivymd_gui/qa/reports/
2. Address high-priority accessibility issues first
3. Migrate raw KivyMD widgets to M3 adapters
4. Verify token usage in custom components
5. Re-run validation until score ≥85
```

## Integration with Existing Code

### Gradual Migration Strategy

1. **Phase 1**: Implement token system and core adapters (✅ Complete)
2. **Phase 2**: Migrate critical components (buttons, cards)
3. **Phase 3**: Full screen migration to M3 adapters
4. **Phase 4**: Custom component migration and optimization

### Backward Compatibility

- Legacy components remain functional during migration
- M3 adapters can coexist with existing KivyMD widgets
- Gradual adoption without breaking existing functionality