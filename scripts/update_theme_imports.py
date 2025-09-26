#!/usr/bin/env python3
"""
Script to update theme imports from old systems to the new unified theme system
"""

import os
import re


def update_imports_in_file(file_path):
    """Update theme imports in a single file"""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Patterns to replace
        patterns = [
            # Core theme system imports
            (r'from core\.theme_system import ThemeMode, get_theme_system',
             'from flet_server_gui.ui.unified_theme_system import ThemeMode, get_theme_system'),
            (r'from flet_server_gui\.core\.theme_system import get_theme_system, ThemeMode',
             'from flet_server_gui.ui.unified_theme_system import get_theme_system, ThemeMode'),
            (r'from \.\.core\.theme_system import get_theme_system, ThemeMode',
             'from flet_server_gui.ui.unified_theme_system import get_theme_system, ThemeMode'),
            (r'from core\.theme_system import ThemeMode',
             'from flet_server_gui.ui.unified_theme_system import ThemeMode'),
            (r'from core\.theme_system import MaterialDesign3ThemeSystem, theme_system, get_theme_system',
             'from flet_server_gui.ui.unified_theme_system import MaterialDesign3ThemeSystem, theme_system, get_theme_system'),

            # Utils theme imports (if any)
            (r'from utils\.theme_manager import',
             'from flet_server_gui.ui.unified_theme_system import'),
        ]

        original_content = content
        for old_pattern, new_pattern in patterns:
            content = re.sub(old_pattern, new_pattern, content)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated imports in " + file_path)
            return True
        else:
            print("No changes needed in " + file_path)
            return False

    except Exception as e:
        print("Error updating " + file_path + ": " + str(e))
        return False

def main():
    """Main function to update all theme-related files"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flet_gui_dir = os.path.join(project_root, 'flet_server_gui')

    # Files that might need import updates
    files_to_update = [
        os.path.join(flet_gui_dir, 'demo_m3_components.py'),
        os.path.join(flet_gui_dir, 'ui', 'm3_components.py'),
        os.path.join(flet_gui_dir, 'validate_m3_factory.py'),
        os.path.join(flet_gui_dir, 'validate_phase4_foundation.py'),
    ]

    updated_count = 0
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if update_imports_in_file(file_path):
                updated_count += 1

    print("\nSummary: Updated " + str(updated_count) + " files with new theme imports")

if __name__ == "__main__":
    main()
