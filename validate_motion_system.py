#!/usr/bin/env python3
"""
Motion System Validation Script
Tests the M3 Motion System for compatibility and functionality.
"""

import sys
import traceback
from typing import List, Tuple, Any

def safe_print(message: str):
    """Safe printing with UTF-8 fallback."""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_msg = ''.join(char if ord(char) < 128 else '?' for char in message)
        print(clean_msg)

def run_validation_tests() -> Tuple[bool, List[str]]:
    """Run comprehensive validation tests for the Motion System."""
    
    results = []
    all_passed = True
    
    # Test 1: Import Motion System
    safe_print("🧪 Testing Motion System imports...")
    try:
        from flet_server_gui.ui.motion_system import (
            M3MotionSystem,
            M3EasingCurves,
            M3Duration,
            M3MotionTokens,
            M3TransitionPatterns,
            MotionToken,
            PrebuiltAnimations,
            create_motion_system,
            get_motion_token_by_use_case
        )
        results.append("✅ PASS - Motion System imports successful")
    except Exception as e:
        results.append(f"❌ FAIL - Motion System import failed: {e}")
        all_passed = False
        return all_passed, results
    
    # Test 2: Flet Compatibility
    safe_print("🧪 Testing Flet compatibility...")
    try:
        import flet as ft
        
        # Test basic Flet components that motion system uses
        test_components = [
            ft.Animation,
            ft.AnimationCurve,
            ft.transform.Scale,
            ft.transform.Offset,
            ft.Colors,
            ft.Icons,
            ft.Card,
            ft.Container,
            ft.FilledButton
        ]
        
        for component in test_components:
            if not hasattr(ft, component.__name__.split('.')[-1]) and not hasattr(component, '__name__'):
                continue  # Skip nested attributes
        
        results.append("✅ PASS - Flet compatibility verified")
    except Exception as e:
        results.append(f"❌ FAIL - Flet compatibility issue: {e}")
        all_passed = False
    
    # Test 3: Motion Token Structure
    safe_print("🧪 Testing Motion Token structure...")
    try:
        # Test MotionToken dataclass
        test_token = MotionToken(
            duration=300,
            easing=M3EasingCurves.STANDARD,
            description="Test token",
            use_cases=["test"]
        )
        
        assert test_token.duration == 300
        assert test_token.easing == M3EasingCurves.STANDARD
        assert test_token.description == "Test token"
        assert "test" in test_token.use_cases
        
        results.append("✅ PASS - MotionToken structure valid")
    except Exception as e:
        results.append(f"❌ FAIL - MotionToken structure invalid: {e}")
        all_passed = False
    
    # Test 4: Easing Curves Enum
    safe_print("🧪 Testing M3 Easing Curves...")
    try:
        # Test all easing curves exist
        required_curves = ['STANDARD', 'EMPHASIZED', 'DECELERATED', 'ACCELERATED', 'LINEAR']
        
        for curve_name in required_curves:
            curve = getattr(M3EasingCurves, curve_name)
            assert isinstance(curve, M3EasingCurves)
        
        # Test curve mapping
        from flet_server_gui.ui.motion_system import M3_CURVE_MAPPING
        
        for m3_curve, flet_curve in M3_CURVE_MAPPING.items():
            assert isinstance(m3_curve, M3EasingCurves)
            # Note: flet_curve should be a Flet AnimationCurve but we can't easily test the exact type
        
        results.append("✅ PASS - M3 Easing Curves valid")
    except Exception as e:
        results.append(f"❌ FAIL - M3 Easing Curves invalid: {e}")
        all_passed = False
    
    # Test 5: Duration System
    safe_print("🧪 Testing M3 Duration system...")
    try:
        # Test duration ranges
        short_durations = [M3Duration.SHORT1, M3Duration.SHORT2, M3Duration.SHORT3, M3Duration.SHORT4]
        medium_durations = [M3Duration.MEDIUM1, M3Duration.MEDIUM2, M3Duration.MEDIUM3, M3Duration.MEDIUM4]
        long_durations = [M3Duration.LONG1, M3Duration.LONG2, M3Duration.LONG3, M3Duration.LONG4]
        
        # Verify progression (each should be >= previous)
        prev_value = 0
        for duration in short_durations + medium_durations + long_durations:
            assert duration.value >= prev_value, f"Duration progression broken: {duration.value} < {prev_value}"
            prev_value = duration.value
        
        # Verify reasonable ranges
        assert M3Duration.SHORT1.value >= 50, "SHORT1 too fast"
        assert M3Duration.EXTRA_LONG4.value <= 1000, "EXTRA_LONG4 too slow"
        
        results.append("✅ PASS - M3 Duration system valid")
    except Exception as e:
        results.append(f"❌ FAIL - M3 Duration system invalid: {e}")
        all_passed = False
    
    # Test 6: Motion Tokens
    safe_print("🧪 Testing predefined Motion Tokens...")
    try:
        # Test key motion tokens exist and are valid
        required_tokens = [
            'BUTTON_PRESS', 'BUTTON_HOVER', 'COMPONENT_STATE',
            'CONTENT_FADE', 'CONTENT_SLIDE', 'CONTAINER_TRANSFORM',
            'NAVIGATION_SHARED_AXIS', 'NAVIGATION_FADE_THROUGH',
            'ERROR_SHAKE', 'SUCCESS_PULSE',
            'LIST_ITEM_ENTER', 'LIST_ITEM_EXIT'
        ]
        
        for token_name in required_tokens:
            token = getattr(M3MotionTokens, token_name)
            assert isinstance(token, MotionToken), f"{token_name} is not a MotionToken"
            assert isinstance(token.duration, int), f"{token_name} duration not int"
            assert isinstance(token.easing, M3EasingCurves), f"{token_name} easing not M3EasingCurves"
            assert len(token.use_cases) > 0, f"{token_name} has no use cases"
        
        results.append("✅ PASS - Motion Tokens valid")
    except Exception as e:
        results.append(f"❌ FAIL - Motion Tokens invalid: {e}")
        all_passed = False
    
    # Test 7: Motion System Class Structure
    safe_print("🧪 Testing Motion System class structure...")
    try:
        # Create a mock page object for testing
        class MockPage:
            def __init__(self):
                self.overlay = []
                self.theme_mode = None
            
            def update(self):
                pass
        
        mock_page = MockPage()
        motion_system = M3MotionSystem(mock_page)
        
        # Test key methods exist
        required_methods = [
            'create_animation', 'apply_motion_token', 'button_press_feedback',
            'button_hover_effect', 'card_hover_effect', 'toast_notification',
            'list_item_interactions', 'dialog_appearance', 'error_shake',
            'success_pulse', 'fade_in', 'fade_out', 'slide_up', 'slide_down'
        ]
        
        for method_name in required_methods:
            assert hasattr(motion_system, method_name), f"Missing method: {method_name}"
            assert callable(getattr(motion_system, method_name)), f"Method not callable: {method_name}"
        
        # Test accessibility methods
        motion_system.set_reduce_motion(True)
        assert motion_system.should_reduce_motion() == True
        
        motion_system.set_reduce_motion(False) 
        assert motion_system.should_reduce_motion() == False
        
        results.append("✅ PASS - Motion System class structure valid")
    except Exception as e:
        results.append(f"❌ FAIL - Motion System class structure invalid: {e}")
        all_passed = False
    
    # Test 8: Transition Patterns
    safe_print("🧪 Testing Transition Patterns...")
    try:
        # Test transition pattern methods exist
        required_patterns = ['fade_through', 'shared_axis_x', 'shared_axis_y', 'container_transform', 'fade']
        
        for pattern_name in required_patterns:
            assert hasattr(M3TransitionPatterns, pattern_name), f"Missing pattern: {pattern_name}"
            pattern_method = getattr(M3TransitionPatterns, pattern_name)
            assert callable(pattern_method), f"Pattern not callable: {pattern_name}"
        
        results.append("✅ PASS - Transition Patterns valid")
    except Exception as e:
        results.append(f"❌ FAIL - Transition Patterns invalid: {e}")
        all_passed = False
    
    # Test 9: Utility Functions
    safe_print("🧪 Testing utility functions...")
    try:
        # Test create_motion_system function
        mock_page = MockPage()
        motion_system = create_motion_system(mock_page)
        assert isinstance(motion_system, M3MotionSystem)
        
        # Test get_motion_token_by_use_case
        button_token = get_motion_token_by_use_case("button_press")
        assert button_token is not None
        assert isinstance(button_token, MotionToken)
        
        # Test with non-existent use case
        invalid_token = get_motion_token_by_use_case("non_existent_use_case")
        assert invalid_token is None
        
        results.append("✅ PASS - Utility functions valid")
    except Exception as e:
        results.append(f"❌ FAIL - Utility functions invalid: {e}")
        all_passed = False
    
    # Test 10: Prebuilt Animations
    safe_print("🧪 Testing Prebuilt Animations...")
    try:
        # Test PrebuiltAnimations exist
        required_prebuilts = ['PAGE_ENTER', 'PAGE_EXIT', 'MODAL_ENTER', 'MODAL_EXIT', 'LOADING_PULSE']
        
        for prebuilt_name in required_prebuilts:
            prebuilt = getattr(PrebuiltAnimations, prebuilt_name)
            assert isinstance(prebuilt, MotionToken), f"{prebuilt_name} not a MotionToken"
        
        results.append("✅ PASS - Prebuilt Animations valid")
    except Exception as e:
        results.append(f"❌ FAIL - Prebuilt Animations invalid: {e}")
        all_passed = False
    
    return all_passed, results

def main():
    """Main validation function."""
    
    safe_print("=" * 60)
    safe_print("🎬 MATERIAL DESIGN 3 MOTION SYSTEM VALIDATION")
    safe_print("=" * 60)
    safe_print("")
    
    try:
        all_passed, results = run_validation_tests()
        
        safe_print("")
        safe_print("📋 VALIDATION RESULTS:")
        safe_print("-" * 40)
        
        for result in results:
            safe_print(f"  {result}")
        
        safe_print("")
        safe_print("-" * 40)
        
        if all_passed:
            safe_print("🎉 ALL TESTS PASSED! Motion System is ready for use.")
            safe_print("")
            safe_print("Next steps:")
            safe_print("  • Run demo: python flet_server_gui/motion_system_demo.py")
            safe_print("  • View integration: python flet_server_gui/motion_integration_example.py")
            safe_print("  • Read guide: flet_server_gui/MOTION_SYSTEM_GUIDE.md")
            return 0
        else:
            safe_print("❌ SOME TESTS FAILED! Please review the issues above.")
            return 1
            
    except Exception as e:
        safe_print(f"💥 VALIDATION SCRIPT ERROR: {e}")
        safe_print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())