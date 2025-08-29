#!/usr/bin/env python3
"""
Script to identify and manage redundant theme files that can be archived
"""

import os
import shutil
from datetime import datetime

def identify_redundant_theme_files():
    """Identify redundant theme files that can be archived"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flet_gui_dir = os.path.join(project_root, 'flet_server_gui')
    
    # Files that are redundant and can be archived
    redundant_files = [
        os.path.join(flet_gui_dir, 'core', 'theme_system.py'),
        os.path.join(flet_gui_dir, 'utils', 'theme_manager.py'),
        os.path.join(flet_gui_dir, 'utils', 'theme_utils.py'),
    ]
    
    # Check which files actually exist
    existing_redundant_files = [f for f in redundant_files if os.path.exists(f)]
    
    return existing_redundant_files

def create_archive_directory():
    """Create archive directory for redundant files"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    archive_dir = os.path.join(project_root, 'archived_theme_files')
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print("Created archive directory: " + archive_dir)
    
    return archive_dir

def archive_redundant_files():
    """Archive redundant theme files"""
    redundant_files = identify_redundant_theme_files()
    
    if not redundant_files:
        print("No redundant theme files found to archive")
        return
    
    archive_dir = create_archive_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_subdir = os.path.join(archive_dir, "theme_system_" + timestamp)
    os.makedirs(archive_subdir)
    
    archived_count = 0
    for file_path in redundant_files:
        try:
            filename = os.path.basename(file_path)
            destination = os.path.join(archive_subdir, filename)
            shutil.copy2(file_path, destination)
            print("Archived: " + file_path + " -> " + destination)
            archived_count += 1
        except Exception as e:
            print("Failed to archive " + file_path + ": " + str(e))
    
    print("\nArchived " + str(archived_count) + " redundant theme files to: " + archive_subdir)
    print("These files can now be safely removed from the main codebase")

def main():
    """Main function"""
    print("=== Theme System Consolidation Report ===\n")
    
    redundant_files = identify_redundant_theme_files()
    
    if redundant_files:
        print("Redundant theme files found:")
        for file_path in redundant_files:
            print("  - " + file_path)
        
        print("\nRecommendation: Archive these files to clean up the codebase")
        print("Run 'archive_redundant_files()' to move them to an archive directory")
    else:
        print("No redundant theme files found. Codebase is clean!")

if __name__ == "__main__":
    main()