import sys

print('Python executable:', sys.executable)
print('In virtual environment:', sys.prefix != sys.base_prefix)
print('Site packages location:', sys.executable.replace('python.exe', 'site-packages'))
