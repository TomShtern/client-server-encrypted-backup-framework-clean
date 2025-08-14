import importlib, sys
from pathlib import Path
# Ensure project root is on sys.path so package imports like 'api_server' resolve
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
mods=[('api_server.cyberbackup_api_server','app')]
ok=True
for m, attr in mods:
    try:
        mod=importlib.import_module(m)
        got=getattr(mod, attr, None)
        print(f"IMPORT OK: {m}, has {attr}={bool(got)}")
    except Exception as e:
        ok=False
        print(f"IMPORT FAIL: {m}: {e}")
        import traceback; traceback.print_exc()
print("SMOKE:", "PASS" if ok else "FAIL")
