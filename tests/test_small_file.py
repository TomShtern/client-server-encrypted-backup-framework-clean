#!/usr/bin/env python3
import os
import tempfile

# Create a small 1KB test file to see if basic transfer works
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_1KB_test.txt') as f:
    content = 'Z' * 1024  # 1KB of 'Z' characters
    f.write(content)
    test_file = f.name

print(f"Created 1KB test file: {test_file}")
print(f"Size: {os.path.getsize(test_file)} bytes")

# Update transfer.info for direct client test
with open('transfer.info', 'w') as f:
    f.write("127.0.0.1:1256\n")
    f.write("TestSmallFile\n")
    f.write(f"{test_file}\n")

print("Updated transfer.info for 1KB test")
print("This should work if the basic client functionality is working")
