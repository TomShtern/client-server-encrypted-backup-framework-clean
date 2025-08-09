#!/usr/bin/env python3
"""
DEPRECATED: Standalone Backup Server Launcher

This file is DEPRECATED and should not be used.
Use the official server entry point instead:

    python -m src.server.server

Or use the one-click launcher:

    python one_click_build_and_run.py

This file will be removed in a future version.
"""

import sys
import os

# Add the project root to Python path to fix import issues
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """DEPRECATED: Use official server entry point instead"""
    print("=" * 60)
    print("⚠️  DEPRECATION WARNING")
    print("=" * 60)
    print("This script (start_backup_server.py) is DEPRECATED.")
    print()
    print("Please use the official server entry point instead:")
    print("  python -m src.server.server")
    print()
    print("Or use the one-click launcher:")
    print("  python one_click_build_and_run.py")
    print()
    print("This file will be removed in a future version.")
    print("=" * 60)

    # Ask user if they want to continue anyway
    try:
        response = input("\nDo you want to start the official server instead? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("\nStarting official server...")
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "src.server.server"])
            return 0
        else:
            print("Exiting. Please use the official server entry point.")
            return 1
    except KeyboardInterrupt:
        print("\nExiting.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
