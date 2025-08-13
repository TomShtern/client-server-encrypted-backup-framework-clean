#!/usr/bin/env python3
"""
Targeted Import Test - Test specific files that might have issues
"""

import sys
import importlib.util
import os
from typing import List, Tuple

def test_single_import(filepath: str, module_name: str) -> bool:
    """Test importing a single file and return result."""
    print(f"Testing: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  SKIP: File not found")
        return False
        
    try:
        # Use importlib to load the module
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec is None or spec.loader is None:
            print(f"  ERROR: Could not create spec for {module_name}")
            return False
            
        module = importlib.util.module_from_spec(spec)
        
        # Add to sys.modules to handle imports
        old_module = sys.modules.get(module_name)
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
            print(f"  OK: Import successful")
            return True
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            if "No module named" in str(e):
                print(f"  CAUSE: Missing dependency")
            return False
        finally:
            # Restore old module or remove
            if old_module:
                sys.modules[module_name] = old_module
            elif module_name in sys.modules:
                del sys.modules[module_name]
                
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        return False

def main() -> None:
    print("Targeted Python Import Test")
    print("=" * 40)
    
    # Test specific files that might have issues
    test_cases: List[Tuple[str, str]] = [
        # Files from the interrupted scan that showed errors
        ('scripts/one_click_build_and_run_debug.py', 'one_click_build_and_run_debug'),
        ('scripts/test_emoji_support.py', 'test_emoji_support'), 
        ('scripts/test_one_click_dry_run.py', 'test_one_click_dry_run'),
        ('scripts/test_one_click_fixes.py', 'test_one_click_fixes'),
        
        # Test files that might be broken
        ('tests/test_api_error.py', 'test_api_error'),
        ('tests/test_crc_fix.py', 'test_crc_fix'),
        ('tests/test_uuid_fix.py', 'test_uuid_fix'),
        
        # Scripts that might have missing deps
        ('scripts/debugging/deep_error_analysis.py', 'deep_error_analysis'),
        ('scripts/utilities/fix_emojis.py', 'fix_emojis'),
        ('scripts/utilities/fix_me_info_encoding.py', 'fix_me_info_encoding'),
        
        # GUI files that might need tkinter
        ('python_server/server_gui/ServerGUI.py', 'ServerGUI'),
        ('launch_server_gui.py', 'launch_server_gui'),
    ]
    
    failed_files: List[str] = []
    
    print(f"\nTesting {len(test_cases)} potentially problematic files...\n")
    
    for filepath, module_name in test_cases:
        success = test_single_import(filepath, module_name)
        if not success:
            failed_files.append(filepath)
        print()
    
    # Summary
    print("=" * 40)
    print("RESULTS SUMMARY")
    print("=" * 40)
    
    total_tested = len([tc for tc in test_cases if os.path.exists(tc[0])])
    successful = total_tested - len(failed_files)
    
    print(f"Files tested: {total_tested}")
    print(f"Successful imports: {successful}")
    print(f"Failed imports: {len(failed_files)}")
    
    if failed_files:
        print(f"\nFAILED FILES ({len(failed_files)}):")
        for filepath in failed_files:
            print(f"  * {filepath}")
        
        print("\nNOTE: Failed files may be:")
        print("  - Test files with broken imports (safe to ignore/fix)")
        print("  - Debug scripts with missing dependencies")
        print("  - Files that import missing modules")
        print("  - Files meant to be run as scripts, not imported")
    else:
        print("\nAll tested files imported successfully!")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()
