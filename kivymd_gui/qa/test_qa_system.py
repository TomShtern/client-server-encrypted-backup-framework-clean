"""
Test script for Material Design 3 QA system
Demonstrates how to run automated compliance checks
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa import run_full_qa_suite, run_accessibility_checks


def create_sample_components():
    """Create sample component data for testing"""
    return [
        {
            'id': 'primary_button',
            'type': 'button',
            'widget_type': 'MD3Button',  # Using adapter (good)
            'interactive': True,
            'size': {'width': 120, 'height': 40},  # Good size
            'margin': {'top': 16, 'bottom': 16},  # 8dp aligned (good)
            'padding': {'left': 24, 'right': 24},  # 8dp aligned (good)
            'location': 'dashboard.py:1109',
            'label': 'Start Server'
        },
        {
            'id': 'small_icon_button',
            'type': 'icon_button', 
            'widget_type': 'MDIconButton',  # Raw KivyMD (bad)
            'interactive': True,
            'size': {'width': 32, 'height': 32},  # Too small (bad)
            'margin': {'top': 5, 'bottom': 5},  # Not grid aligned (bad)
            'location': 'dashboard.py:285',
            'label': None  # Missing label (bad)
        },
        {
            'id': 'server_status_card',
            'type': 'card',
            'widget_type': 'MD3Card',  # Using adapter (good)
            'interactive': False,
            'size': {'width': 300, 'height': 180},
            'margin': {'all': 24},  # 8dp aligned (good)
            'padding': {'all': 24},  # 8dp aligned (good)
            'location': 'dashboard.py:485'
        },
        {
            'id': 'port_textfield',
            'type': 'textfield',
            'widget_type': 'MD3TextField',  # Using adapter (good)
            'interactive': True,
            'size': {'width': 200, 'height': 56},  # Good size
            'margin': {'top': 8, 'bottom': 8},  # 8dp aligned (good)
            'location': 'settings.py:120',
            'hint_text': 'Port number'  # Has hint text (good)
        }
    ]


def create_sample_animations():
    """Create sample animation data for testing"""
    return [
        {
            'id': 'button_ripple',
            'type': 'micro',
            'duration': 150,  # Good for micro-interaction
            'location': 'md3_button.py:85'
        },
        {
            'id': 'card_hover',
            'type': 'micro', 
            'duration': 300,  # Too long for micro-interaction (bad)
            'location': 'dashboard.py:1727'
        },
        {
            'id': 'screen_transition',
            'type': 'standard',
            'duration': 250,  # Good for standard animation
            'location': 'main.py:285'
        },
        {
            'id': 'dialog_appear',
            'type': 'standard',
            'duration': 500,  # Too long for standard animation (bad) 
            'location': 'dialogs.py:45'
        }
    ]


def test_accessibility_only():
    """Test just the accessibility checker"""
    print("Testing Accessibility Checker...")
    print("=" * 50)
    
    components = create_sample_components()
    report = run_accessibility_checks(components, save_report=False)
    
    print(f"Accessibility Score: {report['summary']['compliance_score']}/100")
    print(f"Issues Found: {report['summary']['total_issues']}")
    print(f"  - Errors: {report['summary']['errors']}")
    print(f"  - Warnings: {report['summary']['warnings']}")
    
    if report['recommendations']:
        print("\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    return report


def test_full_qa_suite():
    """Test the complete QA suite"""
    print("\nTesting Complete QA Suite...")
    print("=" * 50)
    
    components = create_sample_components() 
    animations = create_sample_animations()
    
    # Run full QA suite
    report = run_full_qa_suite(
        components=components,
        animations=animations, 
        save_report=False
    )
    
    return report


def test_token_validation():
    """Test token system validation"""
    print("\nTesting Token System...")
    print("=" * 50)
    
    try:
        from components.token_loader import TokenLoader
        loader = TokenLoader()
        tokens = loader.tokens
        
        print(f"SUCCESS: Tokens loaded successfully")
        print(f"SUCCESS: Token version: {tokens.get('version', 'unknown')}")
        print(f"SUCCESS: Token categories: {list(tokens.keys())}")
        
        # Test specific token access
        primary_color = tokens['palette']['primary']
        print(f"SUCCESS: Primary color: {primary_color}")
        
        corner_radius = tokens['shape']['corner_medium']
        print(f"SUCCESS: Corner radius: {corner_radius}dp")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Token system error: {e}")
        return False


def main():
    """Run all QA tests"""
    print("Material Design 3 QA System Test")
    print("=" * 60)
    
    # Test 1: Token validation
    token_ok = test_token_validation()
    
    # Test 2: Accessibility only
    accessibility_report = test_accessibility_only()
    
    # Test 3: Full QA suite
    if token_ok:
        full_report = test_full_qa_suite()
        
        print(f"\nFINAL RESULTS:")
        print(f"   Overall Score: {full_report['summary']['overall_score']}/100")
        print(f"   Compliance: {full_report['summary']['compliance_level']}")
        print(f"   Tests Passed: {full_report['summary']['passed_tests']}/{full_report['summary']['total_tests']}")
    
    print(f"\nSUCCESS: QA system test complete!")
    

if __name__ == "__main__":
    main()