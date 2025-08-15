#!/usr/bin/env python3
"""
Test Enhanced Output System
Demonstrates the emoji and color functionality across the project.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_output():
    """Test the enhanced output system with emojis and colors."""
    
    try:
        # Test enhanced output module
        from Shared.utils.enhanced_output import (
            EmojiLogger, Emojis, Colors,
            success_print, error_print, warning_print, 
            info_print, startup_print, network_print
        )
        
        print("=" * 60)
        startup_print("Enhanced Output System Test", "TEST")
        print("=" * 60)
        
        # Test direct emoji usage
        print(f"\n{Emojis.TARGET} Direct Emoji Usage:")
        print(f"  {Emojis.SUCCESS} Success operation")
        print(f"  {Emojis.ERROR} Error operation") 
        print(f"  {Emojis.WARNING} Warning operation")
        print(f"  {Emojis.FILE} File operation")
        print(f"  {Emojis.NETWORK} Network operation")
        print(f"  {Emojis.ROCKET} Startup operation")
        
        # Test color output
        print(f"\n{Emojis.TARGET} Color Output Test:")
        print(f"  {Colors.success('Success message', bold=True)}")
        print(f"  {Colors.error('Error message', bold=True)}")
        print(f"  {Colors.warning('Warning message')}")
        print(f"  {Colors.info('Info message')}")
        print(f"  {Colors.debug('Debug message')}")
        
        # Test enhanced print functions
        print(f"\n{Emojis.TARGET} Enhanced Print Functions:")
        success_print("Operation completed successfully", "TEST")
        error_print("Something went wrong", "TEST")
        warning_print("This is a warning", "TEST")
        info_print("This is informational", "TEST")
        startup_print("System starting up", "TEST")
        network_print("Network connection established", "TEST")
        
        # Test enhanced logger
        print(f"\n{Emojis.TARGET} Enhanced Logger Test:")
        logger = EmojiLogger.get_logger("test-system")
        logger.info("Regular info message")
        logger.success("Success with enhanced logger")
        logger.failure("Error with enhanced logger")
        logger.network("Network operation")
        logger.file_op("File operation")
        logger.security("Security operation")
        
        success_print("Enhanced Output System test completed successfully!", "TEST")
        
    except ImportError as e:
        print(f"❌ ERROR: Could not import enhanced output: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Test failed: {e}")
        return False
    
    return True

def test_utf8_integration():
    """Test UTF-8 integration with enhanced output."""
    
    try:
        from Shared.utils.utf8_solution import enhanced_safe_print
        from Shared.utils.enhanced_output import success_print
        
        print(f"\n{'='*60}")
        print("🎯 UTF-8 Integration Test")
        print("="*60)
        
        # Test UTF-8 with emojis
        enhanced_safe_print("Hebrew text: שלום עולם")
        enhanced_safe_print("Emoji test: 🚀🎉✅❌⚠️🔧📁🌐")
        enhanced_safe_print("Mixed: Hebrew שלום + Emojis 🎉 + English Hello")
        
        success_print("UTF-8 integration test completed!", "UTF8")
        
    except ImportError as e:
        print(f"❌ ERROR: Could not test UTF-8 integration: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: UTF-8 test failed: {e}")
        return False
    
    return True

def test_logging_integration():
    """Test integration with existing logging infrastructure."""
    
    try:
        from Shared.logging_utils import setup_dual_logging
        from Shared.utils.enhanced_output import success_print
        
        print(f"\n{'='*60}")
        print("🔧 Logging Integration Test")
        print("="*60)
        
        # Test enhanced logging setup
        logger, log_file = setup_dual_logging(
            logger_name="test-enhanced",
            server_type="test-server",
            enable_enhanced_output=True
        )
        
        logger.info("Testing enhanced logging integration")
        logger.warning("This is a warning with emoji support")
        logger.error("This is an error with color support")
        
        success_print(f"Logging integration test completed! Log file: {log_file}", "LOG")
        
    except ImportError as e:
        print(f"❌ ERROR: Could not test logging integration: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Logging test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Starting Enhanced Output System Tests...")
    
    # Run all tests
    tests = [
        ("Enhanced Output", test_enhanced_output),
        ("UTF-8 Integration", test_utf8_integration), 
        ("Logging Integration", test_logging_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name} test...")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print(f"\n{'='*60}")
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("Enhanced Output System is ready for use across the project!")
    else:
        print(f"⚠️ SOME TESTS FAILED ({passed}/{total})")
        print("Please check the errors above.")
    print("="*60)
