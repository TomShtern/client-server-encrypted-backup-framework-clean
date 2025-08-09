#!/usr/bin/env python3
import tempfile
import os
import random

# Create a 66KB test file for CRC testing with unique username
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_66KB_CRC_test.txt') as f:
    content = 'Y' * 67584  # 66KB of 'Y' characters
    f.write(content)
    test_file = f.name

# Generate unique username
unique_id = random.randint(1000, 9999)
username = f"TestCRC{unique_id}"

print(f"Created 66KB test file: {test_file}")
print(f"Size: {os.path.getsize(test_file)} bytes")
print(f"Username: {username}")

# Update transfer.info
with open('transfer.info', 'w') as f:
    f.write("127.0.0.1:1256\n")
    f.write(f"{username}\n")
    f.write(f"{test_file}\n")

print("Updated transfer.info")
print("Expected: CRC values should now match between client and server")
