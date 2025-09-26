#!/usr/bin/env python3
import os
import tempfile

# Create a 66KB test file for CRC testing
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_66KB_CRC_test.txt') as f:
    content = 'Y' * 67584  # 66KB of 'Y' characters
    f.write(content)
    test_file = f.name

print(f"Created 66KB test file: {test_file}")
print(f"Size: {os.path.getsize(test_file)} bytes")
print("Please upload this file through the web GUI to test the CRC fix!")
print("Expected: CRC values should now match between client and server")
