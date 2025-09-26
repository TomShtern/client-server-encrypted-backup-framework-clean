#!/usr/bin/env python3
"""
Test script to check database view import
"""

import os
import sys

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:5]}")

try:
    import importlib
    module_path = "flet_server_gui.views.database"
    print(f"Attempting to import module: {module_path}")
    module = importlib.import_module(module_path)
    print(f"Module imported successfully: {module}")

    class_name = "DatabaseView"
    print(f"Attempting to get class: {class_name}")
    view_class = getattr(module, class_name)
    print(f"Class found successfully: {view_class}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
