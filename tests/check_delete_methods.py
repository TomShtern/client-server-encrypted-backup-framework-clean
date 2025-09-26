#!/usr/bin/env python3
"""
Check if delete_client method exists in client_actions.py
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_delete_client_method():
    """Check if delete_client method exists in client_actions.py"""
    print("Checking for delete_client method in client_actions.py...")

    try:
        with open("flet_server_gui/actions/client_actions.py", encoding="utf-8") as f:
            content = f.read()

        # Check for delete_client method
        if "def delete_client" in content:
            print("[PASS] delete_client method found in client_actions.py")
            # Find the line number
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "def delete_client" in line:
                    print(f"[INFO] delete_client method found at line {i+1}: {line.strip()}")
        else:
            print("[FAIL] delete_client method not found in client_actions.py")

        # Check for delete_multiple_clients method
        if "def delete_multiple_clients" in content:
            print("[PASS] delete_multiple_clients method found in client_actions.py")
            # Find the line number
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "def delete_multiple_clients" in line:
                    print(f"[INFO] delete_multiple_clients method found at line {i+1}: {line.strip()}")
        else:
            print("[FAIL] delete_multiple_clients method not found in client_actions.py")

    except Exception as e:
        print(f"[ERROR] Failed to check client_actions.py: {e}")

if __name__ == "__main__":
    check_delete_client_method()
