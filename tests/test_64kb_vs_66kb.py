#!/usr/bin/env python3
"""
Test script to verify the 64KB vs 66KB file transfer issue.
Creates test files of exactly 64KB and 66KB to test the transfer.
"""

import os
import tempfile


def create_test_file(size_bytes, name):
    """Create a test file of exact size with clean filename."""
    # Create content that's exactly the specified size
    content = "A" * size_bytes

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{name}.txt') as f:
        f.write(content)
        temp_path = f.name

    print(f"Created {name} file: {temp_path}")
    print(f"File size: {os.path.getsize(temp_path)} bytes")
    return temp_path

def main():
    print("Creating test files for 64KB vs 66KB transfer test...")

    # Create exactly 64KB file (should work)
    file_64kb = create_test_file(64 * 1024, "64KB")

    # Create exactly 66KB file (should fail)
    file_66kb = create_test_file(66 * 1024, "66KB")

    print("\nTest files created:")
    print(f"64KB file: {file_64kb}")
    print(f"66KB file: {file_66kb}")
    print("\nNow test these files through the web GUI to verify the issue.")
    print("Expected: 64KB file works, 66KB file fails")

if __name__ == "__main__":
    main()
