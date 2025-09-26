import importlib
import sys

mods = ['flet','flask','requests','psutil','httpx','aiosqlite','emoji','python_server','shared']
print('Python:', sys.version)
failed = []
for m in mods:
    try:
        importlib.import_module(m)
        print('OK', m)
    except Exception as e:
        failed.append((m, str(e)))
        print('FAIL', m, e)
print('\nSummary:')
print('  OK:', len(mods) - len(failed))
print('  FAIL:', len(failed))
if failed:
    for m, err in failed:
        print('   -', m, '->', err)
