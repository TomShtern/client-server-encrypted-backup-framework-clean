#!/usr/bin/env python3
import tempfile
import os

# Create a 66KB test file
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_66KB_debug.txt') as f:
    content = 'X' * 67584  # 66KB
    f.write(content)
    test_file = f.name

print(f"Created test file: {test_file}")
print(f"Size: {os.path.getsize(test_file)} bytes")

# Update transfer.info
with open('transfer.info', 'w') as f:
    f.write("127.0.0.1:1256\n")
    f.write("TestDebugQuick\n")
    f.write(f"{test_file}\n")

print("Updated transfer.info")
