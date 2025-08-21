"""
Material Design 3 QA Test Runner
Comprehensive automated testing suite for M3 compliance
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .accessibility_checker import AccessibilityChecker, run_accessibility_checks
from components.token_loader import TokenLoader, get_token_value


@dataclass
class QAResult:
    """Results from a QA test run"""
    test_name: str
    passed: bool
    score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    execution_time_ms: float


class TouchTargetValidator:
    """Validate touch target sizes according to M3 specifications"""
    
    @staticmethod
    def validate_touch_targets(components: List[Dict[str, Any]]) -> QAResult:
        """Validate that all interactive components meet minimum touch target size"""
        start_time = datetime.now()
        
        min_size = get_token_value('accessibility.touch_target_min', 48)
        issues = []
        
        for component in components:
            if component.get('interactive', False):
                size = component.get('size', {})
                width = size.get('width', 0)
                height = size.get('height', 0)
                
                # At least one dimension must be >=48dp
                if width < min_size and height < min_size:
                    issues.append({
                        'component_id': component.get('id', 'unknown'),
                        'current_size': f"{width}x{height}dp",
                        'required_size': f">={min_size}dp in at least one dimension",
                        'location': component.get('location', 'unknown')
                    })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QAResult(
            test_name="Touch Target Size Validation",
            passed=len(issues) == 0,
            score=100.0 if len(issues) == 0 else max(0, 100 - (len(issues) * 20)),
            issues=issues,
            recommendations=[
                "Ensure all interactive elements are at least 48dp in one dimension",
                "Add padding around small interactive elements to increase touch area"
            ] if issues else [],
            execution_time_ms=execution_time
        )


class SpacingValidator:
    """Validate spacing grid compliance according to M3 specifications"""
    
    @staticmethod
    def validate_spacing_grid(components: List[Dict[str, Any]]) -> QAResult:
        """Validate that components follow 8dp baseline grid"""
        start_time = datetime.now()
        
        base_grid = get_token_value('spacing.grid', 8)
        issues = []
        
        for component in components:
            # Check margins and padding for grid compliance
            margin = component.get('margin', {})
            padding = component.get('padding', {})
            position = component.get('position', {})
            
            # Validate margin values
            for direction, value in margin.items():
                if value % base_grid != 0 and value % 4 != 0:  # Allow 4dp increments
                    issues.append({
                        'component_id': component.get('id', 'unknown'),
                        'property': f"margin_{direction}",
                        'current_value': f"{value}dp",
                        'issue': "Not aligned to 4dp/8dp grid",
                        'location': component.get('location', 'unknown')
                    })
            
            # Validate padding values
            for direction, value in padding.items():
                if value % base_grid != 0 and value % 4 != 0:
                    issues.append({
                        'component_id': component.get('id', 'unknown'),
                        'property': f"padding_{direction}",
                        'current_value': f"{value}dp",
                        'issue': "Not aligned to 4dp/8dp grid",
                        'location': component.get('location', 'unknown')
                    })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QAResult(
            test_name="Spacing Grid Compliance",
            passed=len(issues) == 0,
            score=100.0 if len(issues) == 0 else max(0, 100 - (len(issues) * 10)),
            issues=issues,
            recommendations=[
                "Align all spacing values to the 8dp baseline grid",
                "Use 4dp increments for fine adjustments when necessary",
                "Consider using spacing tokens instead of hardcoded values"
            ] if issues else [],
            execution_time_ms=execution_time
        )


class MotionValidator:
    """Validate motion and animation compliance according to M3 specifications"""
    
    @staticmethod
    def validate_motion_compliance(animations: List[Dict[str, Any]]) -> QAResult:
        """Validate that animations follow M3 motion guidelines"""
        start_time = datetime.now()
        
        motion_tokens = get_token_value('motion', {})
        max_micro_duration = motion_tokens.get('standard', 250)
        max_standard_duration = motion_tokens.get('emphasized', 400)
        
        issues = []
        
        for animation in animations:
            duration = animation.get('duration', 0)
            animation_type = animation.get('type', 'micro')
            
            if animation_type == 'micro' and duration > max_micro_duration:
                issues.append({
                    'animation_id': animation.get('id', 'unknown'),
                    'current_duration': f"{duration}ms",
                    'max_duration': f"{max_micro_duration}ms",
                    'issue': "Micro-interaction duration too long",
                    'location': animation.get('location', 'unknown')
                })
            elif animation_type == 'standard' and duration > max_standard_duration:
                issues.append({
                    'animation_id': animation.get('id', 'unknown'),
                    'current_duration': f"{duration}ms",
                    'max_duration': f"{max_standard_duration}ms",
                    'issue': "Standard animation duration too long",
                    'location': animation.get('location', 'unknown')
                })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QAResult(
            test_name="Motion Compliance",
            passed=len(issues) == 0,
            score=100.0 if len(issues) == 0 else max(0, 100 - (len(issues) * 15)),
            issues=issues,
            recommendations=[
                "Keep micro-interactions under 250ms for responsiveness",
                "Use motion tokens instead of hardcoded duration values",
                "Consider user preference for reduced motion"
            ] if issues else [],
            execution_time_ms=execution_time
        )


class ComponentValidator:
    """Validate that components use the adapter layer instead of raw KivyMD"""
    
    @staticmethod
    def validate_component_compliance(components: List[Dict[str, Any]]) -> QAResult:
        """Validate that components use M3 adapters instead of raw KivyMD widgets"""
        start_time = datetime.now()
        
        # List of raw KivyMD widgets that should be replaced with adapters
        raw_widgets = {
            'MDRaisedButton': 'MD3Button',
            'MDRectangleFlatButton': 'MD3Button',
            'MDCard': 'MD3Card',
            'MDTextField': 'MD3TextField',
            'MDIconButton': 'MD3IconButton'
        }
        
        issues = []
        
        for component in components:
            widget_type = component.get('widget_type', '')
            
            if widget_type in raw_widgets:
                issues.append({
                    'component_id': component.get('id', 'unknown'),
                    'current_widget': widget_type,
                    'recommended_adapter': raw_widgets[widget_type],
                    'issue': "Using raw KivyMD widget instead of M3 adapter",
                    'location': component.get('location', 'unknown')
                })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QAResult(
            test_name="Component Adapter Compliance",
            passed=len(issues) == 0,
            score=100.0 if len(issues) == 0 else max(0, 100 - (len(issues) * 25)),
            issues=issues,
            recommendations=[
                "Replace raw KivyMD widgets with M3 adapter components",
                "Use factory functions (create_md3_button, etc.) for consistency",
                "Ensure all components read styling from design tokens"
            ] if issues else [],
            execution_time_ms=execution_time
        )


class TokenValidator:
    """Validate design token usage and completeness"""
    
    @staticmethod
    def validate_token_usage() -> QAResult:
        """Validate that design tokens are complete and properly structured"""
        start_time = datetime.now()
        
        loader = TokenLoader()
        tokens = loader.tokens
        
        # Required token categories
        required_categories = [
            'palette', 'shape', 'elevation', 'typography', 
            'motion', 'spacing', 'component_tokens'
        ]
        
        issues = []
        
        # Check for missing categories
        for category in required_categories:
            if category not in tokens:
                issues.append({
                    'token_category': category,
                    'issue': "Missing required token category",
                    'impact': "Components may fall back to hardcoded values"
                })
        
        # Validate palette completeness
        palette = tokens.get('palette', {})
        required_colors = [
            'primary', 'on_primary', 'primary_container', 'on_primary_container',
            'secondary', 'on_secondary', 'secondary_container', 'on_secondary_container',
            'surface', 'on_surface', 'background', 'on_background', 'error', 'on_error'
        ]
        
        for color in required_colors:
            if color not in palette:
                issues.append({
                    'token_path': f"palette.{color}",
                    'issue': "Missing required color token",
                    'impact': "Color contrast validation may fail"
                })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QAResult(
            test_name="Design Token Validation",
            passed=len(issues) == 0,
            score=100.0 if len(issues) == 0 else max(0, 100 - (len(issues) * 20)),
            issues=issues,
            recommendations=[
                "Ensure all required token categories are present in tokens.json",
                "Complete the color palette with all M3 color roles",
                "Validate token values against M3 specifications"
            ] if issues else [],
            execution_time_ms=execution_time
        )


class QARunner:
    """Main QA test runner for comprehensive M3 compliance checking"""
    
    def __init__(self):
        self.results: List[QAResult] = []
    
    def run_full_qa_suite(self, components: List[Dict[str, Any]] = None,
                         animations: List[Dict[str, Any]] = None,
                         save_report: bool = True) -> Dict[str, Any]:
        """
        Run the complete QA suite for M3 compliance
        
        Args:
            components: List of component data for validation
            animations: List of animation data for validation
            save_report: Whether to save the report to file
            
        Returns:
            Comprehensive QA report
        """
        components = components or []
        animations = animations or []
        
        print("[INFO] Running M3 compliance QA suite...")
        
        # Run all validators
        results = []
        
        # 1. Token validation
        print("  * Validating design tokens...")
        results.append(TokenValidator.validate_token_usage())
        
        # 2. Accessibility checks
        print("  * Running accessibility checks...")
        accessibility_report = run_accessibility_checks(components, save_report=False)
        results.append(QAResult(
            test_name="Accessibility Compliance",
            passed=accessibility_report['summary']['errors'] == 0,
            score=accessibility_report['summary']['compliance_score'],
            issues=accessibility_report['issues']['errors'] + accessibility_report['issues']['warnings'],
            recommendations=accessibility_report['recommendations'],
            execution_time_ms=0  # Not tracked for accessibility
        ))
        
        # 3. Touch target validation
        print("  * Validating touch targets...")
        results.append(TouchTargetValidator.validate_touch_targets(components))
        
        # 4. Spacing grid validation
        print("  * Validating spacing grid...")
        results.append(SpacingValidator.validate_spacing_grid(components))
        
        # 5. Motion compliance
        print("  * Validating motion compliance...")
        results.append(MotionValidator.validate_motion_compliance(animations))
        
        # 6. Component adapter compliance
        print("  * Validating component adapters...")
        results.append(ComponentValidator.validate_component_compliance(components))
        
        # Calculate overall score
        total_score = sum(result.score for result in results) / len(results)
        total_issues = sum(len(result.issues) for result in results)
        passed_tests = sum(1 for result in results if result.passed)
        
        # Generate comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(results),
                'passed_tests': passed_tests,
                'failed_tests': len(results) - passed_tests,
                'overall_score': round(total_score, 1),
                'total_issues': total_issues,
                'compliance_level': self._get_compliance_level(total_score)
            },
            'test_results': [
                {
                    'test_name': result.test_name,
                    'passed': result.passed,
                    'score': result.score,
                    'issues_count': len(result.issues),
                    'execution_time_ms': result.execution_time_ms,
                    'issues': result.issues,
                    'recommendations': result.recommendations
                }
                for result in results
            ],
            'overall_recommendations': self._generate_overall_recommendations(results)
        }
        
        if save_report:
            self._save_report(report)
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _get_compliance_level(self, score: float) -> str:
        """Get compliance level based on score"""
        if score >= 95:
            return "EXCELLENT"
        elif score >= 85:
            return "GOOD"
        elif score >= 70:
            return "FAIR"
        elif score >= 50:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _generate_overall_recommendations(self, results: List[QAResult]) -> List[str]:
        """Generate high-level recommendations based on all test results"""
        recommendations = []
        
        failed_tests = [result for result in results if not result.passed]
        
        if any("Accessibility" in result.test_name for result in failed_tests):
            recommendations.append(
                "Priority 1: Address accessibility issues to ensure WCAG compliance"
            )
        
        if any("Token" in result.test_name for result in failed_tests):
            recommendations.append(
                "Priority 2: Complete design token implementation for consistency"
            )
        
        if any("Touch Target" in result.test_name for result in failed_tests):
            recommendations.append(
                "Priority 3: Increase touch target sizes for better usability"
            )
        
        if any("Component" in result.test_name for result in failed_tests):
            recommendations.append(
                "Priority 4: Migrate to M3 adapter components for token enforcement"
            )
        
        return recommendations
    
    def _save_report(self, report: Dict[str, Any]) -> None:
        """Save QA report to file"""
        os.makedirs('kivymd_gui/qa/reports', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f'kivymd_gui/qa/reports/qa_report_{timestamp}.json'
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[INFO] QA report saved to {report_path}")
    
    def _print_summary(self, report: Dict[str, Any]) -> None:
        """Print QA summary to console"""
        summary = report['summary']
        
        print(f"\n{'='*60}")
        print(f"MATERIAL DESIGN 3 QA REPORT")
        print(f"{'='*60}")
        print(f"Overall Score: {summary['overall_score']}/100 ({summary['compliance_level']})")
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"Total Issues: {summary['total_issues']}")
        print(f"{'='*60}")
        
        for test_result in report['test_results']:
            status = "PASS" if test_result['passed'] else "FAIL"
            print(f"{status} {test_result['test_name']} ({test_result['score']}/100)")
        
        if report['overall_recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(report['overall_recommendations'], 1):
                print(f"  {i}. {rec}")


def run_full_qa_suite(components: List[Dict[str, Any]] = None,
                     animations: List[Dict[str, Any]] = None,
                     save_report: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run the full QA suite
    
    Args:
        components: Component data for validation
        animations: Animation data for validation  
        save_report: Whether to save report
        
    Returns:
        QA report dictionary
    """
    runner = QARunner()
    return runner.run_full_qa_suite(components, animations, save_report)