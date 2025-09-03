#!/usr/bin/env python3
"""
Theme Consistency Validation Script
Validates that all hardcoded color references have been replaced with theme tokens.
"""

import sys
import os
import re
from pathlib import Path

def find_hardcoded_colors(directory):
    """Find all hardcoded color references in Python files."""
    hardcoded_patterns = [
        r'ft\.Colors\.',
        r'ft\.colors\.(?!with_opacity)',
        r'ft\.Color\.',
        r'TokenRole\.PRIMARY:',
        r'TokenRole\.SECONDARY:',
        r'TokenRole\.ERROR:',
    ]
    
    files_with_hardcoded_colors = []
    
    # Walk through all Python files
    for py_file in Path(directory).rglob("*.py"):
        # Skip design token and semantic color definition files
        if any(skip in str(py_file) for skip in [
            "design_tokens.py", 
            "semantic_colors.py", 
            "m3_components.py",
            "theme_consistency.py",
            "theme_m3.py"
        ]):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for hardcoded color patterns
            for pattern in hardcoded_patterns:
                if re.search(pattern, content):
                    # Get line numbers
                    lines = content.split('\n')
                    matching_lines = []
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            matching_lines.append((i, line.strip()))
                    
                    if matching_lines:
                        files_with_hardcoded_colors.append({
                            'file': str(py_file.relative_to(directory)),
                            'pattern': pattern,
                            'lines': matching_lines
                        })
                    break  # Move to next file after first match
                    
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return files_with_hardcoded_colors

def validate_theme_tokens(directory):
    """Validate that theme tokens are properly used."""
    print("Validating theme token usage...")
    
    # Find files with hardcoded colors
    files_with_issues = find_hardcoded_colors(directory)
    
    if files_with_issues:
        print("")
        print("Found hardcoded color references:")
        for issue in files_with_issues:
            print("")
            print(f"  File: {issue['file']}")
            print(f"  Pattern: {issue['pattern']}")
            print("  Lines:")
            for line_num, line_content in issue['lines'][:3]:  # Show first 3 matches
                print(f"    {line_num}: {line_content}")
            if len(issue['lines']) > 3:
                print(f"    ... and {len(issue['lines']) - 3} more lines")
        return False
    else:
        print("All hardcoded color references have been replaced with theme tokens!")
        return True

def main():
    """Main validation function."""
    print("Phase 4 Theme Consistency Validation")
    print("==================================================")
    
    # Get the project directory
    project_dir = Path(__file__).parent.absolute()
    flet_gui_dir = project_dir / "flet_server_gui"
    
    if not flet_gui_dir.exists():
        print(f"flet_server_gui directory not found at {flet_gui_dir}")
        return False
    
    print(f"Checking directory: {flet_gui_dir}")
    
    # Validate theme tokens
    token_validation_passed = validate_theme_tokens(flet_gui_dir)
    
    # Summary
    print("")
    print("==================================================")
    if token_validation_passed:
        print("PHASE 4 THEME CONSISTENCY VALIDATION PASSED")
        print("All hardcoded color references have been successfully")
        print("replaced with theme-aware TOKENS system.")
        return True
    else:
        print("PHASE 4 THEME CONSISTENCY VALIDATION FAILED")
        print("Hardcoded color references still exist in the codebase.")
        print("Please replace them with TOKENS['color_role'] references.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)