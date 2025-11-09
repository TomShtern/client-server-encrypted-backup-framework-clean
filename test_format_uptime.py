#!/usr/bin/env python3
"""Test format_uptime function to see if it's causing the freeze."""

import sys

sys.path.insert(0, 'FletV2')

from FletV2.utils.formatters import format_uptime

# Test with the exact value from the logs
display_uptime_seconds = 16.544944524765015

print(f"Testing format_uptime with value: {display_uptime_seconds}")
result = format_uptime(display_uptime_seconds)
print(f"Result: {result}")
print("SUCCESS - format_uptime works fine")
