#!/usr/bin/env python3
import tempfile
import os

# Create a test file with a simple name (no special characters)
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_simple_66KB.txt') as f:
    content = 'W' * 67584  # 66KB of 'W' characters
    f.write(content)
    test_file = f.name

print(f"Created simple test file: {test_file}")
print(f"Size: {os.path.getsize(test_file)} bytes")
print(f"File name: {os.path.basename(test_file)}")

# Test if the path length is the issue
print(f"Path length: {len(test_file)} characters")

# Manually create transfer.info in build/Release to test
transfer_info_path = "build/Release/transfer.info"
with open(transfer_info_path, 'w') as f:
    f.write("127.0.0.1:1256\n")
    f.write("TestWebGUIFix\n")
    f.write(f"{os.path.abspath(test_file)}\n")

print(f"Created transfer.info at: {transfer_info_path}")
print("Now test this file through the web GUI to see if it works")

# Also verify the transfer.info was written correctly
with open(transfer_info_path, 'r') as f:
    content = f.read()
    print(f"transfer.info content:\n{content}")
    print(f"Content length: {len(content)} characters")
