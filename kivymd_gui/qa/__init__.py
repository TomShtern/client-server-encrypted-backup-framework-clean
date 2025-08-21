"""
Material Design 3 Automated QA Module
Automated compliance checking for M3 design specifications
"""

from .accessibility_checker import AccessibilityChecker, run_accessibility_checks, ContrastCalculator
from .qa_runner import (
    QARunner, run_full_qa_suite, QAResult,
    TouchTargetValidator, SpacingValidator, MotionValidator, 
    ComponentValidator, TokenValidator
)

__all__ = [
    # Main QA system
    'QARunner', 'run_full_qa_suite', 'QAResult',
    
    # Accessibility checking
    'AccessibilityChecker', 'run_accessibility_checks', 'ContrastCalculator',
    
    # Individual validators
    'TouchTargetValidator', 'SpacingValidator', 'MotionValidator', 
    'ComponentValidator', 'TokenValidator'
]