#!/usr/bin/env python3
"""
Quick Python Import Error Scanner - Fast version without executing modules
"""

import ast
import os
from typing import Any


def check_imports_in_file(filepath: str) -> dict[str, Any]:
    """
    Parse a Python file and check for import statements without executing it.
    
    Args:
        filepath: Path to the Python file to check
        
    Returns:
        dict with imports and potential issues
    """
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()

        # Parse AST to find import statements
        tree = ast.parse(content, filename=filepath)
        imports: list[dict[str, Any]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'line': node.lineno
                    })

        return {
            'success': True,
            'imports': imports,
            'error': None
        }

    except SyntaxError as e:
        return {
            'success': False,
            'imports': [],
            'error': f"Syntax Error: {e}",
            'error_type': 'SyntaxError'
        }
    except Exception as e:
        return {
            'success': False,
            'imports': [],
            'error': str(e),
            'error_type': type(e).__name__
        }

def check_module_availability(module_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False
    except Exception:
        return False

def main() -> None:
    print("Quick Python Import Error Scanner")
    print("=" * 50)

    # Core project files to check
    core_files = [
        './api_server/cyberbackup_api_server.py',
        './api_server/real_backup_executor.py',
        './python_server/server/server.py',
        './python_server/server/request_handlers.py',
        './python_server/server/file_transfer.py',
        './python_server/server_gui/ServerGUI.py',
        './scripts/one_click_build_and_run.py',
        './scripts/one_click_build_and_run_debug.py',
        './scripts/launch_gui.py',
        './Shared/observability.py',
        './Shared/sentry_config.py'
    ]

    # Track problematic imports
    missing_modules: set[str] = set()
    syntax_errors: list[Any] = []
    problematic_files: list[str] = []

    print(f"\nScanning {len(core_files)} core files for import issues...\n")

    for filepath in core_files:
        if not os.path.exists(filepath):
            print(f"MISSING: {filepath}")
            continue

        result = check_imports_in_file(filepath)

        if not result['success']:
            syntax_errors.append((filepath, result['error']))
            print(f"SYNTAX ERR: {filepath}")
            print(f"  {result['error']}")
            continue

        print(f"PARSING: {filepath}")

        # Check each import
        file_missing_imports: list[str] = []
        if result['imports']:
            for imp in result['imports']:
                if imp['type'] == 'import':
                    module = imp['module']
                else:
                    module = imp['module']

                # Skip relative imports and standard library
                if module.startswith('.') or not module:
                    continue

                # Check common third-party modules
                if module in ['flask', 'sentry_sdk', 'watchdog', 'tkinter', 'pystray', 'PIL', 'matplotlib']:
                    if not check_module_availability(module):
                        missing_modules.add(module)
                        file_missing_imports.append(f"  Line {imp['line']}: {module}")

        if file_missing_imports:
            problematic_files.append(filepath)
            for missing in file_missing_imports:
                print(missing)

    # Summary
    print("\n" + "=" * 50)
    print("IMPORT ANALYSIS SUMMARY")
    print("=" * 50)

    if syntax_errors:
        print(f"\nSYNTAX ERRORS ({len(syntax_errors)} files):")
        for filepath, error in syntax_errors:
            print(f"  * {filepath}")
            print(f"    {error}")

    if missing_modules:
        print(f"\nMISSING DEPENDENCIES ({len(missing_modules)} modules):")
        for module in sorted(missing_modules):
            print(f"  * {module}")

            # Suggest fixes
            if module == 'flask':
                print("    Fix: pip install flask flask-cors flask-socketio")
            elif module == 'sentry_sdk':
                print("    Fix: pip install sentry-sdk")
            elif module == 'watchdog':
                print("    Fix: pip install watchdog")
            elif module in ['pystray', 'PIL']:
                print("    Fix: pip install Pillow pystray")
            elif module == 'matplotlib':
                print("    Fix: pip install matplotlib")
            elif module == 'tkinter':
                print("    Fix: Install Python with tkinter support")

    if problematic_files:
        print(f"\nFILES WITH MISSING IMPORTS ({len(problematic_files)} files):")
        for filepath in problematic_files:
            print(f"  * {filepath}")

    # Recommendations
    if not syntax_errors and not missing_modules:
        print("\nGOOD NEWS: No obvious import issues found in core files!")
        print("All required modules appear to be available.")
    else:
        print("\nRECOMMENDATIONS:")
        if syntax_errors:
            print("* Fix syntax errors in the listed files")
        if missing_modules:
            print("* Install missing dependencies with the suggested pip commands")
            print("* Check if requirements.txt exists and run: pip install -r requirements.txt")

    print("\nScan complete!")

if __name__ == "__main__":
    main()
