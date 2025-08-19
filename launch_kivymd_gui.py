#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
launch_kivymd_gui.py - Launcher for KivyMD Encrypted Backup Server GUI
Simple launcher script for the new Material Design interface
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the KivyMD GUI"""
    try:
        from kivymd_gui.main import main as kivymd_main
        print("[INFO] Launching KivyMD Encrypted Backup Server GUI...")
        kivymd_main()
    except ImportError as e:
        print(f"[ERROR] Could not import KivyMD GUI: {e}")
        print("Please ensure KivyMD is installed: pip install kivymd==2.0.0")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to launch GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()