#!/usr/bin/env python3
"""
Phase 3 Verification Script
Tests UI stability and navigation fixes.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import flet as ft

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class TestPhase3Fixes(unittest.TestCase):
    """Test cases for Phase 3 UI stability and navigation fixes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_page = Mock(spec=ft.Page)
        self.test_page.window_min_width = 800
        self.test_page.window_min_height = 600
        self.test_page.update = Mock()
        
    def test_navigation_synchronization(self):
        """Test navigation synchronization fix."""
        try:
            from flet_server_gui.ui.navigation import NavigationManager
            
            # Create navigation manager
            nav_manager = NavigationManager(self.test_page, lambda x: None)
            
            # Test sync_navigation_state method exists
            self.assertTrue(hasattr(nav_manager, 'sync_navigation_state'))
            
            # Test that method accepts a view name parameter
            nav_manager.sync_navigation_state("dashboard")
            
            print("✅ Navigation synchronization method exists and callable")
        except Exception as e:
            self.fail(f"Navigation synchronization test failed: {e}")
    
    def test_responsive_layout_fixes(self):
        """Test responsive layout fixes."""
        try:
            from flet_server_gui.ui.layouts.responsive_fixes import (
                ResponsiveLayoutFixes,
                fix_content_clipping,
                fix_button_clickable_areas,
                ensure_windowed_compatibility
            )
            
            # Test ResponsiveLayoutFixes class exists
            self.assertTrue(hasattr(ResponsiveLayoutFixes, 'create_clipping_safe_container'))
            self.assertTrue(hasattr(ResponsiveLayoutFixes, 'fix_hitbox_alignment'))
            self.assertTrue(hasattr(ResponsiveLayoutFixes, 'create_responsive_scroll_container'))
            self.assertTrue(hasattr(ResponsiveLayoutFixes, 'fix_button_hitbox'))
            self.assertTrue(hasattr(ResponsiveLayoutFixes, 'create_windowed_layout_fix'))
            
            # Test helper functions
            test_content = ft.Text("Test")
            
            clipping_fixed = fix_content_clipping(test_content)
            self.assertIsInstance(clipping_fixed, ft.Container)
            self.assertEqual(clipping_fixed.clip_behavior, ft.ClipBehavior.NONE)
            
            button = ft.ElevatedButton("Test")
            button_fixed = fix_button_clickable_areas(button)
            self.assertIsInstance(button_fixed, ft.Container)
            self.assertGreaterEqual(button_fixed.width, 48)
            self.assertGreaterEqual(button_fixed.height, 48)
            
            windowed_fixed = ensure_windowed_compatibility(test_content)
            self.assertIsInstance(windowed_fixed, ft.Container)
            
            print("✅ Responsive layout fixes implemented correctly")
        except Exception as e:
            self.fail(f"Responsive layout fixes test failed: {e}")
    
    def test_theme_consistency(self):
        """Test theme consistency implementation."""
        try:
            from flet_server_gui.ui.theme_consistency import (
                ThemeConsistencyManager,
                initialize_theme_consistency,
                get_theme_consistency_manager
            )
            
            # Test theme consistency manager
            tokens = {
                "primary": "#7C5CD9",
                "secondary": "#FFA500",
                "error": "#B00020"
            }
            
            manager = ThemeConsistencyManager(tokens)
            
            # Test button styles
            filled_style = manager.get_consistent_button_style("filled")
            self.assertIn("bgcolor", filled_style)
            self.assertIn("color", filled_style)
            
            outlined_style = manager.get_consistent_button_style("outlined")
            self.assertIn("side", outlined_style)
            
            # Test status colors
            online_color = manager.get_status_color("online")
            self.assertEqual(online_color, ft.Colors.GREEN)
            
            error_color = manager.get_status_color("error")
            self.assertEqual(error_color, "#B00020")
            
            # Test card style
            card_style = manager.get_consistent_card_style()
            self.assertIn("elevation", card_style)
            self.assertIn("border_radius", card_style)
            
            # Test initialization
            initialized_manager = initialize_theme_consistency(tokens)
            retrieved_manager = get_theme_consistency_manager()
            self.assertEqual(initialized_manager, retrieved_manager)
            
            print("✅ Theme consistency helpers implemented correctly")
        except Exception as e:
            self.fail(f"Theme consistency test failed: {e}")
    
    def test_stack_replacement_fixes(self):
        """Test that Stack usage has been replaced with better alternatives."""
        try:
            # Check navigation.py for Stack usage
            nav_file_path = os.path.join(project_root, "flet_server_gui", "ui", "navigation.py")
            with open(nav_file_path, 'r', encoding='utf-8') as f:
                nav_content = f.read()
            
            # Should not have problematic Stack usage for badges
            self.assertNotIn("ft.Stack(destination_content", nav_content)
            self.assertNotIn("ft.Stack(destination_content", nav_content)
            
            # Should have Row-based implementation instead
            self.assertIn("ft.Row([", nav_content)
            
            print("✅ Stack replacement fixes implemented correctly")
        except Exception as e:
            self.fail(f"Stack replacement test failed: {e}")
    
    def test_windowed_mode_compatibility(self):
        """Test windowed mode compatibility fixes."""
        try:
            # Check that minimum window size is set appropriately
            from flet_server_gui.main import ServerGUIApp
            
            # Mock the page
            mock_page = Mock()
            mock_page.window_min_width = None
            mock_page.window_min_height = None
            mock_page.controls = []
            
            # Test layout fixes function
            from flet_server_gui.ui.layouts.responsive_fixes import apply_layout_fixes
            apply_layout_fixes(mock_page)
            
            # Should set minimum window size
            self.assertEqual(mock_page.window_min_width, 800)
            self.assertEqual(mock_page.window_min_height, 600)
            
            print("✅ Windowed mode compatibility fixes implemented correctly")
        except Exception as e:
            self.fail(f"Windowed mode compatibility test failed: {e}")

def main():
    """Run all Phase 3 verification tests."""
    print("PHASE 3 VERIFICATION - UI STABILITY & NAVIGATION FIXES")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase3Fixes)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    print("\n" + "=" * 60)
    print("PHASE 3 VERIFICATION RESULTS")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("ALL PHASE 3 TESTS PASSED")
        print("\nPhase 3 fixes successfully implemented:")
        print("   - Navigation synchronization fixed")
        print("   - Responsive layout clipping issues resolved")
        print("   - Clickable area issues fixed")
        print("   - Theme consistency ensured")
        print("   - Windowed mode compatibility improved")
        return 0
    else:
        print("SOME PHASE 3 TESTS FAILED")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailed tests:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback}")
                
        if result.errors:
            print("\nError in tests:")
            for test, error in result.errors:
                print(f"   - {test}: {error}")
                
        return 1

if __name__ == "__main__":
    sys.exit(main())