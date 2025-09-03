# Material Design 3 QA & Accessibility Guide

Comprehensive guide for automated quality assurance and accessibility compliance validation.

## Overview

The M3 QA system provides automated validation of Material Design 3 compliance across multiple dimensions:

- **Accessibility** (WCAG AA compliance)
- **Design Token Usage** (consistency enforcement)
- **Touch Target Validation** (usability standards)
- **Spacing Grid Compliance** (layout consistency)
- **Motion Standards** (animation guidelines)
- **Component Adapter Usage** (architectural compliance)

## Quick Start

### Running Complete QA Suite

```bash
# Activate KivyMD environment
.\kivy_venv_new\Scripts\activate

# Run comprehensive QA validation
kivy_venv_new/Scripts/python.exe kivymd_gui/qa/test_qa_system.py
```

### Expected Output

```
Material Design 3 QA System Test
============================================================
Testing Token System...
✅ Tokens loaded successfully
✅ Token version: 1.0.0
✅ Token categories: ['palette', 'shape', 'elevation', 'typography', 'motion', 'spacing']

Testing Accessibility Checker...
Accessibility Score: 85.2/100
Issues Found: 3
  - Errors: 1
  - Warnings: 2

🎯 FINAL RESULTS:
   Overall Score: 87.3/100
   Compliance: GOOD
   Tests Passed: 5/6
✅ QA system test complete!
```

## Accessibility Compliance (WCAG AA)

### Color Contrast Validation

The system automatically validates all color token combinations against WCAG AA standards:

```python
from kivymd_gui.qa import run_accessibility_checks

# Validates these critical combinations:
# - primary + on_primary (buttons, app bars)
# - surface + on_surface (body text)
# - background + on_background (main content)
# - error + on_error (error states)

report = run_accessibility_checks()
```

### WCAG AA Requirements

| Text Type | Minimum Contrast Ratio | Token Validation |
|-----------|------------------------|------------------|
| Normal text | 4.5:1 | `surface` + `on_surface` |
| Large text | 3.0:1 | `primary_container` + `on_primary_container` |
| UI components | 3.0:1 | `outline` + `surface` |

### Touch Target Validation

Ensures all interactive elements meet minimum touch target sizes:

```python
# Minimum requirements (automatically validated)
TOUCH_TARGET_MINIMUM = 48  # dp (from tokens.accessibility.touch_target_min)

# Components validated:
# - Buttons, IconButtons, Switches, Checkboxes
# - Text fields, Search fields
# - Navigation items, Menu items
# - Any component marked as interactive=True
```

### Focus Indicators

Validates keyboard navigation support:

- **Focus visibility**: 2dp minimum indicator width
- **Focus order**: Logical tab sequence
- **Focus contrast**: Sufficient contrast for focus indicators

## Design Token Compliance

### Token Usage Validation

Ensures components use design tokens instead of hardcoded values:

```python
# ✅ COMPLIANT: Token-driven styling
component.radius = [get_token_value('shape.corner_medium')]
component.padding = get_token_value('spacing.gutter')

# ❌ NON-COMPLIANT: Hardcoded values
component.radius = [12]  # Detected as violation
component.padding = 16   # Detected as violation
```

### Component Adapter Enforcement

Validates use of M3 adapters instead of raw KivyMD widgets:

```python
# ✅ COMPLIANT: M3 adapter usage
button = create_md3_button("Save", variant="filled")

# ❌ NON-COMPLIANT: Raw KivyMD widget
button = MDRaisedButton(text="Save")  # Detected as violation
```

## Spacing Grid Validation

### 8dp Baseline Grid

Validates alignment to Material Design's 8dp baseline grid:

```python
# ✅ COMPLIANT: Grid-aligned values
margin = 16  # 8dp × 2
padding = 24  # 8dp × 3
spacing = 8   # Base grid unit

# ❌ NON-COMPLIANT: Non-grid values
margin = 15   # Not divisible by 8 or 4
padding = 22  # Not aligned to grid
```

### Acceptable Values

- **Primary grid**: Multiples of 8dp (8, 16, 24, 32, 40, 48...)
- **Secondary grid**: Multiples of 4dp for fine adjustments (4, 12, 20, 28...)
- **Exception**: Values <4dp allowed for borders, dividers

## Motion Compliance

### Animation Duration Limits

Validates animation durations against M3 motion tokens:

```python
# Motion token limits (from tokens.json)
MOTION_LIMITS = {
    'micro': 100,     # Micro-interactions (hover, focus)
    'short': 160,     # Brief transitions
    'standard': 250,  # Standard transitions
    'emphasized': 400 # Complex transitions
}

# ✅ COMPLIANT: Within limits
hover_animation = 80   # < 100ms (micro)
transition = 200       # < 250ms (standard)

# ❌ NON-COMPLIANT: Exceeds limits
slow_animation = 600   # > 400ms (too slow)
```

### Animation Best Practices

- **Micro-interactions**: <100ms (hover, ripple, focus)
- **Standard transitions**: <250ms (screen changes, dialog appear)
- **Emphasized motion**: <400ms (complex choreography)
- **No animation**: >400ms is generally too slow

## QA Report Structure

### Sample Report Output

```json
{
  "timestamp": "2025-08-21T10:30:00",
  "summary": {
    "total_tests": 6,
    "passed_tests": 5,
    "failed_tests": 1,
    "overall_score": 87.3,
    "total_issues": 3,
    "compliance_level": "GOOD"
  },
  "test_results": [
    {
      "test_name": "Design Token Validation",
      "passed": true,
      "score": 100.0,
      "issues_count": 0
    },
    {
      "test_name": "Accessibility Compliance",
      "passed": false,
      "score": 85.2,
      "issues_count": 3,
      "issues": [
        {
          "component_id": "secondary_on_secondary",
          "issue_type": "contrast",
          "severity": "warning",
          "description": "Insufficient contrast for Button text on secondary background",
          "current_value": "4.2:1",
          "required_value": "4.5:1 (WCAG AA)"
        }
      ]
    }
  ]
}
```

### Compliance Levels

| Score Range | Level | Description |
|-------------|-------|-------------|
| 95-100 | EXCELLENT | Professional M3 compliance |
| 85-94 | GOOD | Minor issues, production ready |
| 70-84 | FAIR | Needs improvement |
| 50-69 | POOR | Significant issues |
| <50 | CRITICAL | Must address before release |

## Integration with Development Workflow

### Pre-Commit Validation

```bash
# Add to git pre-commit hook
#!/bin/bash
echo "Running M3 compliance checks..."
kivy_venv_new/Scripts/python.exe kivymd_gui/qa/test_qa_system.py

if [ $? -ne 0 ]; then
    echo "❌ M3 compliance check failed. Please fix issues before committing."
    exit 1
fi
echo "✅ M3 compliance check passed."
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: M3 Compliance Check
on: [push, pull_request]

jobs:
  qa:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install KivyMD
        run: pip install git+https://github.com/kivymd/KivyMD.git@d2f7740
      - name: Run M3 QA Suite
        run: python kivymd_gui/qa/test_qa_system.py
```

## Troubleshooting QA Issues

### Common Accessibility Failures

```bash
# Issue: Color contrast too low
# Solution: Adjust color tokens or use higher contrast combinations
"primary": "#1976D2",      # Instead of light blue
"on_primary": "#FFFFFF"    # White text for sufficient contrast

# Issue: Touch targets too small
# Solution: Use M3 adapters with automatic sizing
create_md3_button("Text")  # Automatically ≥48dp

# Issue: Missing focus indicators
# Solution: Ensure focusable elements have visible focus states
```

### Component Migration Issues

```python
# Issue: Raw KivyMD widget detected
# Problem: button = MDRaisedButton(text="Save")
# Solution: Migrate to M3 adapter
button = create_md3_button("Save", variant="filled", tone="primary")

# Issue: Hardcoded styling detected
# Problem: card.radius = [12]
# Solution: Use token-driven styling
card.radius = [get_token_value('shape.corner_medium')]
```

### Performance Optimization

```python
# Cache token loader for performance
from kivymd_gui.components import token_loader

# Single token access
primary = token_loader.tokens['palette']['primary']

# Batch token access for complex components
tokens = token_loader.tokens
palette = tokens['palette']
spacing = tokens['spacing']
```

## Advanced QA Customization

### Custom Validation Rules

```python
from kivymd_gui.qa import QARunner

class CustomValidator:
    @staticmethod
    def validate_brand_compliance(components):
        """Custom validation for brand-specific requirements"""
        issues = []
        for component in components:
            # Custom brand validation logic
            pass
        return issues

# Extend QA runner with custom validators
qa_runner = QARunner()
qa_runner.add_custom_validator(CustomValidator)
```

### Accessibility Testing Integration

```python
# Integration with accessibility testing tools
from kivymd_gui.qa import AccessibilityChecker

checker = AccessibilityChecker()

# Custom contrast validation
def validate_brand_colors():
    brand_colors = [
        ('#FF5722', '#FFFFFF', 'Brand primary on white'),
        ('#4CAF50', '#000000', 'Success green on black')
    ]
    
    for bg, fg, description in brand_colors:
        ratio = checker.contrast_calculator.calculate_contrast_ratio(bg, fg)
        if ratio < 4.5:
            print(f"❌ {description}: {ratio:.2f}:1 (needs ≥4.5:1)")
        else:
            print(f"✅ {description}: {ratio:.2f}:1")
```

## Continuous Improvement

### Monitoring Compliance Trends

```python
# Track compliance scores over time
import json
from datetime import datetime

def log_compliance_score(score):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'score': score,
        'commit_hash': get_git_commit_hash()
    }
    
    with open('qa_history.json', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

### Automated Improvement Suggestions

The QA system provides actionable recommendations:

1. **High-Impact**: Address accessibility errors first
2. **Medium-Impact**: Migrate to M3 adapters for consistency  
3. **Low-Impact**: Fine-tune spacing and motion for polish
4. **Optimization**: Batch token access for performance

This comprehensive QA system ensures professional Material Design 3 compliance while maintaining development velocity and code quality.