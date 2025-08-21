"""
Material Design 3 Accessibility Checker
WCAG compliance validation for color contrast, touch targets, and accessibility requirements
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
import os
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.token_loader import TokenLoader, get_token_value


@dataclass
class AccessibilityIssue:
    """Represents an accessibility compliance issue"""
    component_id: str
    issue_type: str  # 'contrast', 'touch_target', 'focus', 'semantic'
    severity: str  # 'error', 'warning', 'info'
    description: str
    current_value: Any
    required_value: Any
    location: Optional[str] = None


class ContrastCalculator:
    """Calculate color contrast ratios according to WCAG guidelines"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to RGB values (0-1 range)"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b)
        except (ValueError, IndexError):
            return (0.0, 0.0, 0.0)
    
    @staticmethod
    def get_relative_luminance(rgb: Tuple[float, float, float]) -> float:
        """Calculate relative luminance according to WCAG formula"""
        def linearize(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return pow((c + 0.055) / 1.055, 2.4)
        
        r, g, b = rgb
        r_lin = linearize(r)
        g_lin = linearize(g)
        b_lin = linearize(b)
        
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    
    @classmethod
    def calculate_contrast_ratio(cls, color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors
        
        Args:
            color1: First color in hex format
            color2: Second color in hex format
            
        Returns:
            Contrast ratio (1-21 range)
        """
        rgb1 = cls.hex_to_rgb(color1)
        rgb2 = cls.hex_to_rgb(color2)
        
        lum1 = cls.get_relative_luminance(rgb1)
        lum2 = cls.get_relative_luminance(rgb2)
        
        # Ensure lighter color is numerator
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)


class AccessibilityChecker:
    """Main accessibility checker for M3 compliance"""
    
    def __init__(self):
        self.tokens = TokenLoader().tokens
        self.issues: List[AccessibilityIssue] = []
        self.contrast_calculator = ContrastCalculator()
    
    def check_color_contrast(self) -> List[AccessibilityIssue]:
        """Check color contrast compliance for all token color pairs"""
        issues = []
        palette = get_token_value('palette', {})
        
        # Define critical color pair combinations that must meet WCAG AA
        critical_pairs = [
            ('primary', 'on_primary', 'Button text on primary background'),
            ('secondary', 'on_secondary', 'Button text on secondary background'),
            ('surface', 'on_surface', 'Body text on surface background'),
            ('background', 'on_background', 'Text on background'),
            ('error', 'on_error', 'Error text on error background'),
            ('primary_container', 'on_primary_container', 'Text on primary container'),
            ('secondary_container', 'on_secondary_container', 'Text on secondary container'),
            ('surface_variant', 'on_surface_variant', 'Text on surface variant'),
        ]
        
        for bg_token, fg_token, description in critical_pairs:
            bg_color = palette.get(bg_token)
            fg_color = palette.get(fg_token)
            
            if not bg_color or not fg_color:
                issues.append(AccessibilityIssue(
                    component_id=f"{bg_token}_{fg_token}",
                    issue_type="contrast",
                    severity="error",
                    description=f"Missing color tokens: {bg_token} or {fg_token}",
                    current_value=None,
                    required_value="Both colors must be defined"
                ))
                continue
            
            contrast_ratio = self.contrast_calculator.calculate_contrast_ratio(bg_color, fg_color)
            
            # WCAG AA requirements
            min_contrast_normal = get_token_value('accessibility.contrast_ratio_normal', 4.5)
            min_contrast_large = get_token_value('accessibility.contrast_ratio_large', 3.0)
            
            # Check normal text contrast (4.5:1)
            if contrast_ratio < min_contrast_normal:
                severity = "error" if contrast_ratio < 3.0 else "warning"
                issues.append(AccessibilityIssue(
                    component_id=f"{bg_token}_{fg_token}",
                    issue_type="contrast",
                    severity=severity,
                    description=f"Insufficient contrast for {description}",
                    current_value=f"{contrast_ratio:.2f}:1",
                    required_value=f"{min_contrast_normal}:1 (WCAG AA)",
                    location=f"tokens.palette.{bg_token} + {fg_token}"
                ))
        
        return issues
    
    def check_touch_targets(self, components: List[Dict[str, Any]]) -> List[AccessibilityIssue]:
        """Check touch target size compliance"""
        issues = []
        min_touch_target = get_token_value('accessibility.touch_target_min', 48)
        
        for component in components:
            component_type = component.get('type', 'unknown')
            size = component.get('size', {})
            
            # Check if component is interactive
            if component_type in ['button', 'icon_button', 'switch', 'checkbox', 'radio']:
                width = size.get('width', 0)
                height = size.get('height', 0)
                
                # Check minimum touch target in at least one dimension
                if width < min_touch_target and height < min_touch_target:
                    issues.append(AccessibilityIssue(
                        component_id=component.get('id', 'unknown'),
                        issue_type="touch_target",
                        severity="error",
                        description=f"Touch target too small for {component_type}",
                        current_value=f"{width}×{height}dp",
                        required_value=f"≥{min_touch_target}dp in at least one dimension",
                        location=component.get('location', 'unknown')
                    ))
        
        return issues
    
    def check_focus_indicators(self, components: List[Dict[str, Any]]) -> List[AccessibilityIssue]:
        """Check focus indicator compliance for keyboard navigation"""
        issues = []
        min_focus_width = get_token_value('accessibility.focus_indicator_width', 2)
        
        for component in components:
            if component.get('focusable', False):
                focus_indicator = component.get('focus_indicator', {})
                
                if not focus_indicator:
                    issues.append(AccessibilityIssue(
                        component_id=component.get('id', 'unknown'),
                        issue_type="focus",
                        severity="warning",
                        description="Missing focus indicator for keyboard navigation",
                        current_value="None",
                        required_value="Visible focus indicator required",
                        location=component.get('location', 'unknown')
                    ))
                else:
                    indicator_width = focus_indicator.get('width', 0)
                    if indicator_width < min_focus_width:
                        issues.append(AccessibilityIssue(
                            component_id=component.get('id', 'unknown'),
                            issue_type="focus",
                            severity="warning",
                            description="Focus indicator too thin",
                            current_value=f"{indicator_width}dp",
                            required_value=f"≥{min_focus_width}dp",
                            location=component.get('location', 'unknown')
                        ))
        
        return issues
    
    def check_semantic_structure(self, components: List[Dict[str, Any]]) -> List[AccessibilityIssue]:
        """Check semantic structure and labeling"""
        issues = []
        
        for component in components:
            component_type = component.get('type', 'unknown')
            
            # Check for missing labels on interactive components
            if component_type in ['button', 'textfield', 'switch']:
                if not component.get('label') and not component.get('hint_text'):
                    issues.append(AccessibilityIssue(
                        component_id=component.get('id', 'unknown'),
                        issue_type="semantic",
                        severity="warning",
                        description=f"Missing label or hint text for {component_type}",
                        current_value="No label",
                        required_value="Descriptive label required for screen readers",
                        location=component.get('location', 'unknown')
                    ))
        
        return issues
    
    def run_full_check(self, components: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run complete accessibility check and return comprehensive report"""
        components = components or []
        
        # Run all checks
        contrast_issues = self.check_color_contrast()
        touch_target_issues = self.check_touch_targets(components)
        focus_issues = self.check_focus_indicators(components)
        semantic_issues = self.check_semantic_structure(components)
        
        all_issues = contrast_issues + touch_target_issues + focus_issues + semantic_issues
        
        # Categorize by severity
        errors = [issue for issue in all_issues if issue.severity == 'error']
        warnings = [issue for issue in all_issues if issue.severity == 'warning']
        info_items = [issue for issue in all_issues if issue.severity == 'info']
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(all_issues),
                'errors': len(errors),
                'warnings': len(warnings),
                'info': len(info_items),
                'compliance_score': self._calculate_compliance_score(all_issues)
            },
            'issues': {
                'errors': [self._issue_to_dict(issue) for issue in errors],
                'warnings': [self._issue_to_dict(issue) for issue in warnings],
                'info': [self._issue_to_dict(issue) for issue in info_items]
            },
            'recommendations': self._generate_recommendations(all_issues)
        }
        
        return report
    
    def _issue_to_dict(self, issue: AccessibilityIssue) -> Dict[str, Any]:
        """Convert AccessibilityIssue to dictionary for JSON serialization"""
        return {
            'component_id': issue.component_id,
            'issue_type': issue.issue_type,
            'severity': issue.severity,
            'description': issue.description,
            'current_value': issue.current_value,
            'required_value': issue.required_value,
            'location': issue.location
        }
    
    def _calculate_compliance_score(self, issues: List[AccessibilityIssue]) -> float:
        """Calculate overall compliance score (0-100)"""
        if not issues:
            return 100.0
        
        # Weight errors more heavily than warnings
        error_weight = 10
        warning_weight = 3
        info_weight = 1
        
        total_weight = 0
        for issue in issues:
            if issue.severity == 'error':
                total_weight += error_weight
            elif issue.severity == 'warning':
                total_weight += warning_weight
            else:
                total_weight += info_weight
        
        # Calculate score (assuming max possible weight of 100 for full fail)
        max_weight = 100
        score = max(0, 100 - (total_weight * 100 / max_weight))
        return round(score, 1)
    
    def _generate_recommendations(self, issues: List[AccessibilityIssue]) -> List[str]:
        """Generate actionable recommendations based on issues found"""
        recommendations = []
        
        contrast_issues = [i for i in issues if i.issue_type == 'contrast']
        if contrast_issues:
            recommendations.append(
                "Review color palette contrast ratios. Consider using darker text colors "
                "or lighter background colors to meet WCAG AA standards."
            )
        
        touch_issues = [i for i in issues if i.issue_type == 'touch_target']
        if touch_issues:
            recommendations.append(
                "Increase touch target sizes to at least 48dp in one dimension. "
                "Consider adding padding around interactive elements."
            )
        
        focus_issues = [i for i in issues if i.issue_type == 'focus']
        if focus_issues:
            recommendations.append(
                "Add visible focus indicators for keyboard navigation. "
                "Ensure focus indicators have sufficient contrast and width."
            )
        
        semantic_issues = [i for i in issues if i.issue_type == 'semantic']
        if semantic_issues:
            recommendations.append(
                "Add descriptive labels and hint text for interactive components. "
                "Ensure proper semantic structure for screen readers."
            )
        
        return recommendations


def run_accessibility_checks(components: List[Dict[str, Any]] = None, 
                           save_report: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run accessibility checks
    
    Args:
        components: List of component dictionaries to check
        save_report: Whether to save report to file
        
    Returns:
        Accessibility report dictionary
    """
    checker = AccessibilityChecker()
    report = checker.run_full_check(components)
    
    if save_report:
        os.makedirs('kivymd_gui/qa/reports', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f'kivymd_gui/qa/reports/accessibility_report_{timestamp}.json'
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[INFO] Accessibility report saved to {report_path}")
    
    return report