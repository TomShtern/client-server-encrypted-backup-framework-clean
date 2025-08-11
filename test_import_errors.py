#!/usr/bin/env python3
"""
Comprehensive Python Import Error Scanner
Scans all project Python files for actual import failures.
"""

import os
import sys
import importlib.util
import traceback
from pathlib import Path

def test_import_file(filepath):
    """
    Attempt to import a Python file and return import status.
    
    Args:
        filepath: Path to the Python file to test
        
    Returns:
        dict: {'success': bool, 'error': str, 'error_type': str, 'module_name': str}
    """
    try:
        # Convert file path to module name
        relative_path = os.path.relpath(filepath, '.')
        module_name = relative_path.replace(os.sep, '.').replace('.py', '')
        
        # Handle __init__.py files
        if module_name.endswith('.__init__'):
            module_name = module_name.replace('.__init__', '')
        
        # Try to load the module using importlib
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec is None:
            return {
                'success': False,
                'error': 'Could not create module spec',
                'error_type': 'SpecError',
                'module_name': module_name
            }
        
        module = importlib.util.module_from_spec(spec)
        
        # Add to sys.modules temporarily to handle relative imports
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
            return {
                'success': True,
                'error': None,
                'error_type': None,
                'module_name': module_name
            }
        except Exception as e:
            # Remove from sys.modules on failure
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            error_type = type(e).__name__
            error_msg = str(e)
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': error_type,
                'module_name': module_name,
                'traceback': traceback.format_exc()
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'module_name': module_name if 'module_name' in locals() else 'unknown',
            'traceback': traceback.format_exc()
        }

def categorize_error(result):
    """Categorize the type of import error."""
    if result['success']:
        return 'SUCCESS'
    
    error_type = result['error_type']
    error_msg = result['error'].lower()
    
    if error_type in ['ImportError', 'ModuleNotFoundError']:
        if 'no module named' in error_msg:
            return 'MISSING_DEPENDENCY'
        elif 'cannot import name' in error_msg:
            return 'IMPORT_NAME_ERROR'
        else:
            return 'IMPORT_ERROR'
    elif error_type == 'SyntaxError':
        return 'SYNTAX_ERROR'
    elif error_type == 'NameError':
        return 'NAME_ERROR'
    elif error_type in ['FileNotFoundError', 'OSError']:
        return 'FILE_ERROR'
    else:
        return 'OTHER_ERROR'

def main():
    print("Comprehensive Python Import Error Scanner")
    print("=" * 60)
    
    # Get all Python files
    python_files = [
        './api_server/__init__.py',
        './api_server/cyberbackup_api_server.py', 
        './api_server/real_backup_executor.py',
        './Database/database_manager.py',
        './Database/database_monitor.py',
        './launch_server_gui.py',
        './python_server/server/client_manager.py',
        './python_server/server/config.py',
        './python_server/server/connection_health.py',
        './python_server/server/database.py',
        './python_server/server/database_migrations.py',
        './python_server/server/exceptions.py',
        './python_server/server/file_receipt_monitor.py',
        './python_server/server/file_transfer.py',
        './python_server/server/gui_integration.py',
        './python_server/server/health_api.py',
        './python_server/server/network_server.py',
        './python_server/server/protocol.py',
        './python_server/server/request_handlers.py',
        './python_server/server/server.py',
        './python_server/server/server_singleton.py',
        './python_server/server_gui/ServerGUI.py',
        './scripts/check_dependencies.py',
        './scripts/create_test_file.py',
        './scripts/debugging/deep_error_analysis.py',
        './scripts/debugging/find_gui_errors.py',
        './scripts/debugging/targeted_error_finder.py',
        './scripts/fix_vcpkg_issues.py',
        './scripts/launch_gui.py',
        './scripts/minimal_backup_server.py',
        './scripts/monitor_logs.py',
        './scripts/one_click_build_and_run.py',
        './scripts/one_click_build_and_run_debug.py',
        './scripts/security/key-generation/create_working_keys.py',
        './scripts/security/key-generation/generate_me_info.py',
        './scripts/security/key-generation/generate_rsa_keys.py',
        './scripts/security/key-generation/generate_valid_rsa_key.py',
        './scripts/start_backup_server.py',
        './scripts/test_emoji_support.py',
        './scripts/test_one_click_dry_run.py',
        './scripts/test_one_click_fixes.py',
        './scripts/testing/master_test_suite.py',
        './scripts/testing/quick_validation.py',
        './scripts/testing/validate_null_check_fixes.py',
        './scripts/testing/validate_server_gui.py',
        './scripts/utilities/fix_emojis.py',
        './scripts/utilities/fix_me_info_encoding.py',
        './Shared/__init__.py',
        './Shared/canonicalize.py',
        './Shared/config.py',
        './Shared/config_manager.py',
        './Shared/crc.py',
        './Shared/filename_validator.py',
        './Shared/logging_utils.py',
        './Shared/observability.py',
        './Shared/observability_middleware.py',
        './Shared/path_utils.py',
        './Shared/sentry_config.py',
        './Shared/utils/__init__.py',
        './Shared/utils/error_handler.py',
        './Shared/utils/file_lifecycle.py',
        './Shared/utils/performance_monitor.py',
        './Shared/utils/process_monitor.py',
        './Shared/utils/process_monitor_gui.py',
        './Shared/utils/unified_config.py'
    ]
    
    # Also include test files for completeness
    test_files = [
        './tests/comprehensive_boundary_test.py',
        './tests/debug_boundary_issue.py',
        './tests/debug_boundary_simple.py',
        './tests/debug_buffer_calculation.py',
        './tests/debug_file_transfer.py',
        './tests/debug_process_registry.py',
        './tests/debug_stage6_failure.py',
        './tests/debug_transfer_step_by_step.py',
        './tests/focused_boundary_test.py',
        './tests/simple_boundary_test.py',
        './tests/simple_test.py',
        './tests/simple_test_cpp.py',
        './tests/test_64kb_vs_66kb.py',
        './tests/test_66kb_debug.py',
        './tests/test_api.py',
        './tests/test_api_connection.py',
        './tests/test_api_error.py',
        './tests/test_client.py',
        './tests/test_cpp_client_manual.py',
        './tests/test_crc_fix.py',
        './tests/test_crc_fix_unique.py',
        './tests/test_critical_fixes.py',
        './tests/test_demo_scenarios.py',
        './tests/test_direct_executor.py',
        './tests/test_fixes_validation.py',
        './tests/test_gui_filename_acceptance.py',
        './tests/test_gui_join.py',
        './tests/test_gui_query.py',
        './tests/test_gui_upload.py',
        './tests/test_high_priority_fixes.py',
        './tests/test_larger_upload.py',
        './tests/test_progress_monitoring.py',
        './tests/test_progress_reporting.py',
        './tests/test_server_gui.py',
        './tests/test_simple_transfer.py',
        './tests/test_singleton.py',
        './tests/test_small_file.py',
        './tests/test_socket_issue.py',
        './tests/test_transfer_debug.py',
        './tests/test_upload.py',
        './tests/test_upload_debug.py',
        './tests/test_uuid_fix.py',
        './tests/test_uuid_fix_simple.py',
        './tests/test_web_gui_fix.py',
        './tests/integration/run_integration_tests.py',
        './tests/integration/test_complete_flow.py',
        './tests/integration/test_error_scenarios.py',
        './tests/integration/test_performance_flow.py'
    ]
    
    all_files = python_files + test_files
    
    # Track results
    results = []
    categories = {
        'SUCCESS': [],
        'MISSING_DEPENDENCY': [],
        'IMPORT_NAME_ERROR': [],
        'IMPORT_ERROR': [], 
        'SYNTAX_ERROR': [],
        'NAME_ERROR': [],
        'FILE_ERROR': [],
        'OTHER_ERROR': []
    }
    
    print(f"Testing {len(all_files)} Python files...")
    print()
    
    for i, filepath in enumerate(all_files, 1):
        # Skip files that don't exist
        if not os.path.exists(filepath):
            print(f"SKIP [{i:3d}/{len(all_files)}] {filepath} (file not found)")
            continue
            
        result = test_import_file(filepath)
        results.append((filepath, result))
        
        category = categorize_error(result)
        categories[category].append((filepath, result))
        
        if result['success']:
            print(f"OK  [{i:3d}/{len(all_files)}] {filepath}")
        else:
            print(f"ERR [{i:3d}/{len(all_files)}] {filepath}")
            print(f"   Error: {result['error_type']}: {result['error']}")
    
    # Summary Report
    print("\n" + "="*60)
    print("IMPORT ANALYSIS SUMMARY")
    print("="*60)
    
    total_files = len([r for r in results if r])
    successful = len(categories['SUCCESS'])
    failed = total_files - successful
    
    print(f"Total files tested: {total_files}")
    print(f"Successful imports: {successful}")
    print(f"Failed imports: {failed}")
    print(f"Success rate: {successful/total_files*100:.1f}%" if total_files > 0 else "N/A")
    
    # Detailed failure analysis
    for category, items in categories.items():
        if category == 'SUCCESS' or not items:
            continue
            
        print(f"\n{category.replace('_', ' ')} ({len(items)} files):")
        print("-" * 50)
        
        for filepath, result in items:
            print(f"  * {filepath}")
            print(f"    Error: {result['error']}")
            
            # Show common missing dependencies
            if category == 'MISSING_DEPENDENCY':
                error_msg = result['error'].lower()
                if 'flask' in error_msg:
                    print("    Fix: pip install flask flask-cors flask-socketio")
                elif 'sentry_sdk' in error_msg:
                    print("    Fix: pip install sentry-sdk") 
                elif 'watchdog' in error_msg:
                    print("    Fix: pip install watchdog")
                elif 'tkinter' in error_msg:
                    print("    Fix: Install Python with tkinter support")
                elif any(pkg in error_msg for pkg in ['cryptography', 'crypto']):
                    print("    Fix: pip install cryptography pycryptodome")
            print()
    
    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 50)
    
    if categories['MISSING_DEPENDENCY']:
        print("* Install missing dependencies with pip")
        print("* Check requirements.txt for complete dependency list")
    
    if categories['SYNTAX_ERROR']:
        print("* Review syntax errors in failed files") 
        print("* Consider if files are Python version specific")
    
    if categories['IMPORT_NAME_ERROR'] or categories['IMPORT_ERROR']:
        print("* Check for circular imports or incorrect relative imports")
        print("* Verify module structure and __init__.py files")
    
    if categories['FILE_ERROR']:
        print("* Verify file paths and permissions")
        print("* Check for missing files or directories")
        
    print("\nScan complete!")
    
if __name__ == "__main__":
    main()