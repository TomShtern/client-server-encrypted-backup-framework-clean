#!/usr/bin/env python3
import os
import sys

# Set UTF-8 environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Configure Windows console if available
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        if kernel32.GetConsoleCP() != 65001:
            kernel32.SetConsoleCP(65001)
        if kernel32.GetConsoleOutputCP() != 65001:
            kernel32.SetConsoleOutputCP(65001)
    except:
        pass
