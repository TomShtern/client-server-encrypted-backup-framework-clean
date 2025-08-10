#!/usr/bin/env python3
"""
Deep analysis script to find all errors in the project
"""

import sys
import os
import ast
import traceback
from typing import List, Dict, Any

# Add server directory to path
server_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'python_server', 'server')
sys.path.insert(0, server_dir)

def analyze_python_file(filepath: str) -> Dict[str, Any]:
    """Analyze a Python file for various issues"""
    results = {
        'file': filepath,
        'syntax_errors': [],
        'import_errors': [],
        'incomplete_methods': [],
        'runtime_errors': [],
        'missing_imports': []
    }
    
    try:
        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check syntax
        try:
            tree = ast.parse(content)
            
            # Find incomplete methods
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for methods with minimal implementation
                    if len(node.body) == 1:
                        first_stmt = node.body[0]
                        if isinstance(first_stmt, ast.Pass):
                            results['incomplete_methods'].append(f"Line {node.lineno}: {node.name} - Only pass statement")
                        elif isinstance(first_stmt, ast.Expr):
                            if isinstance(first_stmt.value, ast.Constant):
                                if first_stmt.value.value == Ellipsis or first_stmt.value.value == "...":
                                    results['incomplete_methods'].append(f"Line {node.lineno}: {node.name} - Only ellipsis")
                            elif isinstance(first_stmt.value, ast.Str):
                                if first_stmt.value.s in ["...", "TODO", "FIXME"]:
                                    results['incomplete_methods'].append(f"Line {node.lineno}: {node.name} - Placeholder: {first_stmt.value.s}")
                    
                    # Check for empty methods
                    elif len(node.body) == 0:
                        results['incomplete_methods'].append(f"Line {node.lineno}: {node.name} - Empty method body")
                        
        except SyntaxError as e:
            results['syntax_errors'].append(f"Line {e.lineno}: {e.msg}")
        
        # Test imports
        try:
            # Extract import statements
            import_names = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    import_names.append(line)
            
            # Test key imports for ServerGUI.py
            if 'ServerGUI.py' in filepath:
                test_imports = [
                    'import tkinter as tk',
                    'from tkinter import ttk, messagebox, filedialog',
                    'import threading',
                    'import queue',
                    'from datetime import datetime',
                    'from typing import Dict, List, Optional, Any, Union, Tuple',
                    'from collections import deque'
                ]
                
                for imp in test_imports:
                    if imp not in content:
                        results['missing_imports'].append(f"Missing: {imp}")
                        
        except Exception as e:
            results['import_errors'].append(f"Import analysis error: {e}")
            
    except Exception as e:
        results['runtime_errors'].append(f"File analysis error: {e}")
    
    return results

def test_functionality():
    """Test actual functionality"""
    results = []
    
    print("Testing ServerGUI functionality...")
    try:
        from ServerGUI import ServerGUI, ModernCard, ModernProgressBar, ModernStatusIndicator
        
        # Test basic instantiation
        gui = ServerGUI()
        results.append("✓ ServerGUI instantiation works")
        
        # Test widget creation
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        try:
            card = ModernCard(root, title="Test")
            results.append("✓ ModernCard creation works")
        except Exception as e:
            results.append(f"✗ ModernCard error: {e}")
        
        try:
            progress = ModernProgressBar(root)
            progress.set_progress(50)
            results.append("✓ ModernProgressBar works")
        except Exception as e:
            results.append(f"✗ ModernProgressBar error: {e}")
        
        try:
            status = ModernStatusIndicator(root)
            status.set_status("online")
            results.append("✓ ModernStatusIndicator works")
        except Exception as e:
            results.append(f"✗ ModernStatusIndicator error: {e}")
        
        root.destroy()
        
        # Test GUI methods
        try:
            gui.update_server_status(True, "127.0.0.1", 1256)
            gui.update_client_stats(5, 10, 2)
            gui.update_transfer_stats(1024, "now")
            gui.show_error("test error")
            gui.show_success("test success")
            gui.show_info("test info")
            results.append("✓ All GUI methods work")
        except Exception as e:
            results.append(f"✗ GUI method error: {e}")
            
    except Exception as e:
        results.append(f"✗ Major functionality error: {e}")
        traceback.print_exc()
    
    return results

def main():
    print("🔍 DEEP ERROR ANALYSIS")
    print("=" * 60)
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    
    # Analyze each file
    all_issues = []
    for filepath in python_files:
        if '__pycache__' in filepath or '.git' in filepath:
            continue
            
        print(f"\nAnalyzing: {filepath}")
        results = analyze_python_file(filepath)
        
        issues_found = sum(len(results[key]) for key in results if key != 'file')
        if issues_found > 0:
            all_issues.append(results)
            print(f"  Issues found: {issues_found}")
        else:
            print("  ✓ No issues")
    
    # Test functionality
    print(f"\n{'='*60}")
    print("FUNCTIONALITY TESTING")
    print("=" * 60)
    
    func_results = test_functionality()
    for result in func_results:
        print(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)
    
    if all_issues:
        print(f"❌ Found issues in {len(all_issues)} files:")
        for issue in all_issues:
            print(f"\n📁 {issue['file']}:")
            for category, problems in issue.items():
                if category != 'file' and problems:
                    print(f"  {category}: {len(problems)} issues")
                    for problem in problems[:3]:  # Show first 3
                        print(f"    • {problem}")
                    if len(problems) > 3:
                        print(f"    • ... and {len(problems) - 3} more")
    else:
        print("✅ No static analysis issues found")
    
    print(f"\nFunctionality test results: {len([r for r in func_results if r.startswith('✓')])} passed, {len([r for r in func_results if r.startswith('✗')])} failed")

if __name__ == "__main__":
    main()
